# Iteration 02 — Renombrar formatos y textos libres imprimibles

## Estado de la iteración
La iteration-01 (timbre_empleador) ya está implementada y funcional.
Esta iteración tiene dos partes. La parte 1 (renombrar) está implementada
en el frontend (formatos.component.ts: `iniciarEdicionNombreDocumento`,
`guardarNombreDocumento`) y en el backend (`_actualizar_documento` soporta
`nombre` y `variables` de forma independiente). No se toca.

La parte 2 (textos libres) tiene 5 bugs confirmados que impiden su
funcionamiento. Este documento los describe con precisión para que el agente
los corrija sin tocar nada más.

---

## Bugs confirmados (textos libres)

### Bug 1 — Frontend: `texto_libre` no guarda su contenido en la ubicación

**Archivo:** `formatos.component.ts` → método `handlePdfClick`

El bloque que construye el objeto y lo pasa a `variableActual.ubicaciones.push()`
solo incluye `valor` para `elemento_seguridad` y `cantidad_seguridad`:

```typescript
...(
  ['elemento_seguridad', 'cantidad_seguridad'].includes(variableActual.nombre)
    ? { valor: valorEspecial }
    : {}
)
```

Para `texto_libre`, `textoLibrePendiente` se setea en `confirmarTextoLibre`
pero nunca entra en la ubicación. La ubicación queda sin `valor`.

**Fix:** agregar `texto_libre` a esa lista y pasar `this.textoLibrePendiente`:

```typescript
...(
  ['elemento_seguridad', 'cantidad_seguridad'].includes(variableActual.nombre)
    ? { valor: valorEspecial }
    : variableActual.nombre === this.TEXTO_LIBRE_VARIABLE
      ? { valor: this.textoLibrePendiente }
      : {}
)
```

Resetear `textoLibrePendiente = ''` al final del bloque de `texto_libre`
(análogo al reset de `elementoSeguridadPendiente`).

---

### Bug 2 — Frontend: preview en PDF muestra `'texto_libre'` en lugar del contenido

**Archivo:** `formatos.component.ts` → método `mostrarVariableEnPdf` → CASO 6

El código para calcular `textoMostrar` solo acepta `ubicacion.valor` para
`elemento_seguridad` y `cantidad_seguridad`:

```typescript
const textoMostrar = (
  ['elemento_seguridad', 'cantidad_seguridad'].includes(variable.nombre) &&
  ubicacion?.valor
)
  ? ubicacion.valor
  : this.obtenerValorEjemplo(variable.nombre);
```

`texto_libre` cae al branch `obtenerValorEjemplo` que devuelve la string
literal `'texto_libre'`.

**Fix:** extender la condición para incluir `texto_libre`:

```typescript
const textoMostrar = (
  [..., 'texto_libre'].includes(variable.nombre) && ubicacion?.valor
)
  ? ubicacion.valor
  : this.obtenerValorEjemplo(variable.nombre);
```

---

### Bug 3 — Frontend: formato de serialización no coincide con el contrato del backend

**Archivos:** `confirmarGuardado` y `guardarCambiosDocumento` /
`guardarPosicionesModificadas` en `formatos.component.ts`

Los tres métodos serializan todas las variables de la misma forma:

```typescript
const variables = this.variables
  .filter(v => v.ubicaciones.length > 0)
  .map(variable => ({
    nombre: variable.nombre,
    ubicaciones: variable.ubicaciones
  }));
```

Para `texto_libre` esto produce:

```json
{ "nombre": "texto_libre", "ubicaciones": [{ "valor": "ESTIMADO", "posX": 100, ... }] }
```

El backend espera (ver `validar_textos_libres_para_formato` y
`agregar_textos_libres_por_pagina` en `views/contratos.py`):

```json
{ "nombre": "textos_libres", "textos_libres": [{ "texto": "ESTIMADO", "posX": 100, ... }] }
```

Hay dos diferencias: (a) `nombre` debe ser `'textos_libres'` no `'texto_libre'`,
y (b) cada item usa `texto` no `valor`.

**Fix:** antes de enviar, transformar la variable `texto_libre` en el formato
esperado. Esta transformación va en un método privado llamado
`_serializarVariablesParaBackend()` que centraliza la serialización para los
tres métodos de guardado:

```typescript
private _serializarVariablesParaBackend(): any[] {
  const textoLibreVar = this.variables.find(
    v => v.nombre === this.TEXTO_LIBRE_VARIABLE && v.ubicaciones.length > 0
  );

  const variablesNormales = this.variables
    .filter(v => v.ubicaciones.length > 0 && v.nombre !== this.TEXTO_LIBRE_VARIABLE)
    .map(v => ({ nombre: v.nombre, ubicaciones: v.ubicaciones }));

  if (textoLibreVar && textoLibreVar.ubicaciones.length > 0) {
    const textosLibres = textoLibreVar.ubicaciones.map(u => ({
      id: u.id,
      texto: u.valor || '',
      pagina: u.pagina,
      posX: u.posX,
      posY: u.posY,
      pageWidth: u.pageWidth,
      pageHeight: u.pageHeight,
      width: u.width ?? undefined,
      height: u.height ?? undefined,
      fontSize: u.fontSize ?? undefined,
    }));
    variablesNormales.push({
      nombre: this.TEXTOS_LIBRES_CONTAINER,  // 'textos_libres'
      textos_libres: textosLibres
    });
  }

  return variablesNormales;
}
```

Reemplazar los tres `.filter(...).map(...)` de `confirmarGuardado`,
`guardarCambiosDocumento` y `guardarPosicionesModificadas` con
`this._serializarVariablesParaBackend()`.

---

### Bug 4 — Backend: `validar_variables_formato` rechaza entradas sin `ubicaciones`

**Archivo:** `views/contratos.py` → función `validar_variables_formato`

El loop valida que toda entrada de la lista tenga la clave `ubicaciones`:

```python
if 'ubicaciones' not in variable:
    return 'Todas las variables deben tener ubicaciones'
```

La entrada `textos_libres` usa la clave `textos_libres`, no `ubicaciones`.
Con el fix del Bug 3 el frontend ya envía el formato correcto, pero el backend
sigue rechazando esta entrada.

**Fix:** omitir el chequeo de `ubicaciones` para la entrada `textos_libres`:

```python
if variable.get('nombre') != TEXTOS_LIBRES_CONTAINER:
    if 'ubicaciones' not in variable:
        return 'Todas las variables deben tener ubicaciones'
```

Este es el único cambio en backend para esta iteración.

---

### Bug 5 — Consecuencia de los bugs 3+4: los textos libres nunca llegan a `ContratoVariables`

Con los bugs 3 y 4 presentes, ningún guardado persiste los textos libres.
Al resolverlos, los textos libres quedan almacenados en
`ContratoVariables.variables` (JSONField) bajo la clave `textos_libres`,
que es la única fuente de verdad. No se crea tabla ni columna nueva.

---

## Formato de datos (contrato definitivo)

### Representación interna en Angular (en memoria)

Variable `texto_libre` dentro del array `this.variables`, con sus ubicaciones:

```typescript
{
  nombre: 'texto_libre',
  colocada: true,
  ubicaciones: [
    {
      id: 'var-texto_libre-1700000000000',
      pagina: 1,
      posX: 120,
      posY: 340,
      pageWidth: 595,
      pageHeight: 842,
      width: undefined,
      height: undefined,
      valor: 'ESTIMADO',   // contenido del texto libre
      fontSize: undefined,
    }
  ]
}
```

### Wire format enviado al backend (resultado de `_serializarVariablesParaBackend`)

```json
[
  { "nombre": "rut", "ubicaciones": [...] },
  { "nombre": "firma_empleador", "ubicaciones": [...] },
  {
    "nombre": "textos_libres",
    "textos_libres": [
      {
        "id": "var-texto_libre-1700000000000",
        "texto": "ESTIMADO",
        "pagina": 1,
        "posX": 120,
        "posY": 340,
        "pageWidth": 595,
        "pageHeight": 842
      }
    ]
  }
]
```

### Formato almacenado en `ContratoVariables.variables` (idéntico al wire format)

El backend guarda exactamente lo recibido en el JSONField. No hay
transformación adicional.

### Carga desde backend al frontend (`cargarTextosLibresDesdeDocumento`)

Esta función ya existe y hace la transformación inversa correctamente:
lee `texto` del backend y lo pone como `valor` en la ubicación de Angular.
No requiere cambios.

---

## Archivos a modificar

### Backend

`backend/contratista_test_app/views/contratos.py`

Solo un cambio quirúrgico en `validar_variables_formato`:
agregar el guard `if variable.get('nombre') != TEXTOS_LIBRES_CONTAINER`
antes del chequeo de `'ubicaciones' not in variable`.

### Frontend

`frontend/src/app/pages/mother-layout/recursos-humanos/generacion-contratos/formatos/formatos.component.ts`

Cuatro cambios quirúrgicos:

1. `handlePdfClick`: agregar `valor: this.textoLibrePendiente` en la
   ubicación cuando `variableActual.nombre === this.TEXTO_LIBRE_VARIABLE`.
   Resetear `this.textoLibrePendiente = ''` al finalizar.

2. `mostrarVariableEnPdf` CASO 6: incluir `'texto_libre'` en la lista de
   nombres que leen `ubicacion.valor`.

3. Nuevo método privado `_serializarVariablesParaBackend()`.

4. Reemplazar los bloques de serialización en `confirmarGuardado`,
   `guardarCambiosDocumento` y `guardarPosicionesModificadas` con
   `this._serializarVariablesParaBackend()`.

No se toca `formatos.component.html` ni `formatos.component.css`.
No se toca ninguna otra vista ni modelo.

---

## Invariantes

- Un texto libre sin contenido no puede colocarse (validado en
  `confirmarTextoLibre` en frontend y en `validar_textos_libres_para_formato`
  en backend).
- El procesamiento del PDF ocurre en backend. El frontend solo diseña y
  persiste posiciones y contenido.
- Formatos anteriores sin `textos_libres` siguen funcionando: el backend
  tolera su ausencia en `agregar_textos_libres_por_pagina` y en
  `_generar_documento_coordenadas_nativas`.
- Variables existentes (firma_empleador, timbre_empleador, rut, etc.) no se
  tocan.

---

## Tests mínimos

### Backend

1. `PUT /api_documento_nativo/<id>/` con `variables` que incluya entrada
   `textos_libres` válida → 200, datos persistidos en BD.
2. Mismo payload con `texto` vacío → 400 con mensaje
   `'No se puede guardar el formato porque existe un texto libre vacío.'`
3. Mismo payload con `posX` no numérico → 400 con mensaje de posición inválida.
4. Formato antiguo sin `textos_libres` → 200, sin errores.

### Frontend

1. Clic en "Colocar" de `texto_libre` abre modal de texto.
2. Confirmar con texto `'ESTIMADO'` activa modo colocación.
3. Clic en el PDF crea elemento visible con texto `'ESTIMADO'` (no `'texto_libre'`).
4. El elemento es arrastrable.
5. Al guardar, el payload enviado contiene
   `{ "nombre": "textos_libres", "textos_libres": [{ "texto": "ESTIMADO", ... }] }`.
6. Al reabrir el formato, el texto aparece en la posición guardada con el
   contenido correcto.
7. Al generar PDF de prueba, el texto aparece en la posición indicada.

---

## Fuera de alcance de esta iteración

- Edición del contenido de un texto libre ya colocado (pendiente para iteración futura).
- Estilos tipográficos (negrita, cursiva, color).
- Renombrar formatos (ya implementado, no se toca).