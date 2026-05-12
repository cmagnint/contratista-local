# Iteration 01 — Variable `timbre_empleador` en formatos de contrato

## Objetivo
Incorporar `timbre_empleador` como variable imprimible en formatos de contrato, análoga a `firma_empleador`, con CRUD propio de la imagen sobre `Holding`.

## Alcance
- Backend: nueva `APIView` para gestionar `Holding.timbre_empleador` (GET/POST/PUT/DELETE).
- Backend: validación dura al guardar `ContratoVariables` cuando la variable `timbre_empleador` está colocada.
- Frontend (`recursos-humanos/generacion-contratos/formatos`): nueva entrada "Timbre Empleador" en el menú lateral de variables, uploader de imagen y render de ejemplo (mismo patrón que `firma_empleador`).
- Frontend (`recursos-humanos/generacion-contratos/generar-contratos`): impresión de la imagen del timbre en el PDF en la posición guardada.

Fuera de alcance: cualquier otra variable, refactor de variables existentes, cambios en otros formatos, retroactividad sobre contratos ya emitidos.

## Modelo de datos
- `Holding.timbre_empleador: ImageField` ya existe (migración `0006_holding_timbre_empleador`). No se altera.
- `ContratoVariables.variables: JSONField` ya existe. Las posiciones de `timbre_empleador` se almacenan dentro del mismo JSON, bajo la misma estructura usada por `firma_empleador`. No se crean tablas ni columnas nuevas.

## Contrato backend

### Endpoint nuevo: `HoldingTimbreEmpleadorView` (APIView)
Ruta: `/api/holding/<int:holding_id>/timbre-empleador/`

Métodos:
- `GET`: devuelve la URL de la imagen actual. 404 si no hay imagen.
- `POST`: sube imagen cuando no existe. 409 si ya existe.
- `PUT`: reemplaza la imagen existente. 404 si no existe.
- `DELETE`: elimina la imagen y deja el campo en `NULL`. 404 si no existe.

Entradas (POST/PUT): `multipart/form-data` con campo `imagen` (archivo).
Salidas (GET/POST/PUT): `{ "timbre_empleador": "<url>" }`.
Errores: 400 (archivo inválido), 404 (holding o imagen no existe), 409 (POST sobre existente).

### Validación en guardado de formato
Al crear/actualizar `ContratoVariables`, si el JSON `variables` contiene la clave `timbre_empleador` con posición asignada y `Holding.timbre_empleador` es `NULL`, rechazar con 400 y mensaje explícito. La regla vive en backend; el frontend solo refleja el error.

### Render del contrato
En la vista que genera el PDF en `generar-contratos`, leer `Holding.timbre_empleador` y estamparla en la posición indicada por `ContratoVariables.variables['timbre_empleador']`, replicando el mismo mecanismo que `firma_empleador`.

## Contrato frontend
- `formatos`: añadir "Timbre Empleador" al menú izquierdo de variables; añadir uploader (mismo patrón que firma); usar la imagen subida como preview al colocar la variable; si no hay imagen, bloquear el drop de la variable y solicitar subirla.
- `generar-contratos`: sin lógica nueva; el backend resuelve la impresión. El frontend solo dispara la generación.

## Invariantes
- Una sola imagen `timbre_empleador` por `Holding`.
- No se puede activar la variable `timbre_empleador` en un formato sin imagen cargada.
- El procesamiento (composición del PDF, validaciones) ocurre exclusivamente en backend.

## Trazabilidad
- Endpoint CRUD → punto 4 del requerimiento.
- Menú lateral + uploader + preview + bloqueo → punto 2.
- Persistencia de posiciones en `ContratoVariables.variables` → punto 3.
- Estampado en PDF al generar contrato → punto 4.

## Tests mínimos (desde la spec)
1. POST imagen cuando no existe → 201 + URL.
2. POST cuando ya existe → 409.
3. PUT cuando existe → 200 + nueva URL; archivo previo reemplazado.
4. PUT cuando no existe → 404.
5. DELETE cuando existe → 204; campo queda `NULL`.
6. GET sin imagen → 404.
7. Guardar `ContratoVariables` con `timbre_empleador` posicionado y holding sin imagen → 400.
8. Generar contrato con variable activa → PDF contiene la imagen en la posición esperada.
