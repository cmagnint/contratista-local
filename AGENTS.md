# AGENTS.md

## Objetivo del repositorio
SaaS para contratistas agrícolas chilenos. Multi-tenant: holding → sociedades → trabajadores compartidos por holding. Stack: PostgreSQL + Django/DRF + Angular (web admin) + Flutter (móvil supervisor). En producción con datos reales; en rediseño Spec-Driven.

## Documentos vivos (fuente de verdad, en este orden)
1. `spec_dominio_v1.1.md` — dominio. Si el código la contradice, el código está mal.
2. `flujo_contratista.md` — mapa actual frontend ↔ backend ↔ BD (descriptivo, no prescriptivo).
3. `schema_prod.sql`, `indices.txt`, `tablas_tamano.txt` — estado real de la BD.
4. `frontend/src/app/app.routes.ts` — única fuente de rutas Angular.

Si dos documentos discrepan: gana la spec. Reporta la discrepancia, no la silencies.

## Orden de construcción (inviolable)
PostgreSQL → Django → Angular. No se escribe código de una capa hasta que la anterior está especificada y validada. Si la tarea pide saltarse el orden, pedir confirmación explícita antes de avanzar.

## Reglas duras
- **No inventar.** Rutas, tablas, modelos, endpoints, campos, librerías, versiones: si no se puede verificar leyendo el archivo, marcar `needs_verification` y decir qué falta.
- **No asumir.** Si falta un dato necesario, hacer una pregunta concreta. "No sé X, necesito Y" > respuesta especulativa.
- **Solo lectura por defecto en auditorías.** No crear, modificar ni borrar archivos salvo que la tarea lo pida explícitamente.
- **Cambios quirúrgicos.** Modificar lo mínimo. No reformatear ni "limpiar" código ajeno al cambio.
- **Falla rápido.** Lanzar errores cuando precondiciones fallan. Sin fallbacks "por si acaso".
- **Token-aware.** Respuestas cortas, citar `path:lineas`, no pegar código fuente.
- **No renombrar ni mover archivos** salvo que la tarea lo pida.

## Spec-Driven Development (flujo obligatorio)
1. **Spec primero.** Antes de código, redactar o confirmar spec en 5–10 líneas: entradas, salidas, invariantes, errores. Esperar confirmación.
2. **Spec = única fuente de verdad.** Si el código la contradice, el código está mal.
3. **Trazabilidad.** Cada cambio cita la sección de la spec que lo exige (`§X.Y`). Sin spec que lo respalde, no entra.
4. **Tests desde la spec.** Verifican comportamiento, no detalles de implementación.

## Modo Detective (obligatorio para bugs)
Orden estricto:
1. **Teoría.** 1–3 frases: función, entrada y estado concretos.
2. **Evidencia.** Antes de tocar código, definir qué confirmaría o refutaría la teoría (log puntual, valor a inspeccionar, test mínimo, sección a leer). Ejecutarlo.
3. **Veredicto.** Si confirma → fix. Si refuta → nueva teoría, descartando la anterior. No acumular teorías abiertas.
4. **Fix.** Quirúrgico, sobre la causa raíz. Nada más.

Teoría sin evidencia = adivinanza. Prohibido aplicar fixes "elegantes" basados solo en teoría.

## Reglas por capa

### PostgreSQL
- Normalizar por defecto (3FN). Desnormalizar solo con justificación medible.
- Tipos estrictos: `uuid`/`bigint`, `timestamptz`, `numeric(p,s)` para dinero, `text` (no `varchar(n)` salvo razón concreta), `citext` si aplica.
- Constraints en BD: `NOT NULL`, `CHECK`, `UNIQUE`, `FOREIGN KEY` con `ON DELETE` explícito.
- Cada índice se justifica con la query que sirve.
- Migraciones versionadas, idempotentes, reversibles cuando sea posible.
- Sin lógica de negocio en triggers salvo invariantes de integridad.

### Django
- Modelos = espejo del esquema. La BD manda; el ORM la refleja.
- Views/serializers delgados. Lógica de dominio en servicios o managers.
- Validación en dos niveles (Django + BD) coherentes.
- Querysets explícitos: `select_related`/`prefetch_related` donde haya N+1, no por defecto.
- Errores tipados. HTTP coherente con la spec.
- Sin signals para flujo principal.

### Angular (frontend)
- Tipos derivados del contrato del backend. Un solo tipo por entidad.
- No inventar rutas: la fuente es `app.routes.ts`.
- `mother-layout.component.*` y `pages/mother-layout/` ayudan a detectar módulos pero no confirman la ruta final.
- Estado mínimo en cliente. Server state ≠ client state.
- Sin librerías "por costumbre".

## Convenciones de citas
- Toda afirmación sobre el código debe citar `path/al/archivo.ext:linea` o `path:inicio-fin`.
- Toda afirmación sobre la spec cita `spec_dominio_v1.1.md §X.Y`.
- Si la cita no se puede dar: `needs_verification` + qué archivo abrir.

## Catálogo de módulos (chatbot interno)
Cuando la tarea sea generar catálogo:
- JSON o fixture Django.
- Por módulo: `codigo`, `nombre`, `area`, `frontend_path`, `ruta_angular`, `estado_ruta`, `descripcion`, `palabras_clave`.
- `estado_ruta = "verified"` solo si la ruta está confirmada en `app.routes.ts`.
- `estado_ruta = "needs_verification"` si se infiere por carpeta o nombre de componente.

## Cierre obligatorio de toda tarea
Antes de dar por terminado, listar:
1. Archivos leídos (paths exactos).
2. Supuestos que quedan pendientes.
3. Preguntas abiertas que requieren decisión del usuario.

Sin este cierre, la tarea no está terminada.

## Criterio de terminado
- Resultado auditable: cada afirmación tiene evidencia citable.
- Cero rutas, tablas o campos inventados presentados como definitivos.
- Cero código pegado innecesariamente.
- Cierre obligatorio presente.