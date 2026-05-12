# Spec del dominio — contratista (v1.1)

> Fuente única de verdad para el rediseño. Cualquier código que la contradiga, está mal.

> Cambios v1.0 → v1.1:
> - Cerrado modelo de producción: dos tablas, misma medida (cantidad de unidades de control), distinta granularidad temporal.
> - Eliminada la noción de "pago por hora": el pago siempre es `cantidad × precio`. Las horas en mano de obra son informativas.
> - Etiquetado `Labor.modalidad` (mano_obra vs cosecha): una labor pertenece a exactamente una modalidad.
> - Sociedad del trabajador se deriva del contrato vigente. `personal.sociedad_id` deja de ser fuente de verdad.
> - SII: distribución parcial permitida explícitamente; cuenta bancaria pertenece a sociedad, no a holding.
> - Pago a transportista: combinación folio + tramo + trabajadores transportados, mediado por folio de transporte.

---

## 1. Producto

SaaS para contratistas agrícolas chilenos. Un contratista provee mano de obra y servicios a empresas agrícolas (clientes), gestiona a los trabajadores que despliega en terreno, registra la producción de esos trabajadores, les paga, cumple obligaciones laborales chilenas (liquidaciones, Previred, LRE) y lleva la contabilidad básica de compras y ventas (SII, cartolas).

Stack: Angular (web admin) + Flutter (móvil supervisor) + Django/DRF + PostgreSQL.

---

## 2. Actores

| Actor | Acceso | Rol |
|---|---|---|
| Superadmin | Web `/super-admin` | Crea holdings, sociedades y al admin general del holding. No entra a módulos operativos. |
| Admin general | Web `/fs/*` | Único administrador de su holding. Acceso completo a todos los módulos del holding. |
| Usuario operativo | Web `/fs/*` con perfil restringido | Subset del admin general según perfil asignado. |
| Supervisor | App móvil Flutter | Registra producción en terreno (mano de obra y cosecha) contra trabajadores del holding. |
| Trabajador | App móvil (autoregistro / QR / APK link) | Se enrola, no opera el sistema. |

Regla: **un holding tiene exactamente un admin general**.

---

## 3. Modelo de tenancy

```
Holding 1 ──── 1 Admin general
   │
   ├── N Sociedades       (entidades jurídicas que facturan y emplean)
   ├── N Trabajadores     (personal del contratista, compartido entre sociedades)
   ├── N Clientes         (empresas agrícolas a las que se presta servicio)
   └── N Cuentas SII por sociedad (credenciales SII a nivel sociedad)
        └── N Cuentas bancarias y cartolas por sociedad
```

**Reglas de aislación:**
- Toda fila de negocio pertenece a exactamente un holding (`holding_id` obligatorio o derivable).
- Un trabajador pertenece al holding, no a la sociedad. Puede rotar entre sociedades del mismo holding sin duplicarse.
- Un contrato laboral asocia trabajador con sociedad: la sociedad es el empleador legal en ese período.
- Un mismo trabajador puede tener contratos sucesivos con distintas sociedades del mismo holding.
- Cuentas SII y cartolas bancarias se manejan **a nivel sociedad** (porque facturan por sociedad).

---

## 4. Entidades núcleo

### 4.1 Personas y accesos

- **Trabajador (`personal`)**: persona natural enrolada por el contratista. Pertenece al holding. Datos: identificación (RUT/extranjero), contacto, AFP, salud, banco. No tiene credenciales web.
- **Usuario (`usuarios`)**: cuenta web. Puede estar asociada a un trabajador (caso admin general). Tiene perfil que define permisos.
- **Supervisor (`supervisores`)**: figura operativa que registra producción en terreno desde la app móvil. Tiene credenciales propias.
- **Perfil (`perfiles`)**: conjunto de módulos web/móvil habilitados.

### 4.2 Estructura comercial

- **Cliente (`clientes`)**: empresa agrícola contratante. Tiene `N` campos.
- **Campo (`campos_clientes`)**: ubicación física donde se ejecuta el trabajo.
- **Folio comercial (`folio_comercial`)**: acuerdo entre el holding y un cliente, con vigencia, asociado a un campo y a un conjunto de labores con sus precios.
- **Labor (`labores`)**: tipo de trabajo. Tiene `modalidad` y `unidad_pago`.
- **FolioComercialLabor (`fc_labor_pago`)**: precio acordado en ese folio para esa labor. La unidad del precio debe coincidir con `labor.unidad_pago`.

### 4.3 Modelo de Labor

```
Labor:
  - nombre
  - modalidad ∈ {mano_obra, cosecha}
  - unidad_pago ∈ {bandeja, kilo, caja, bin, ...}   (catálogo extensible)
```

**Regla:** una labor pertenece a exactamente una modalidad. Las labores de mano de obra y las de cosecha se crean por separado en el catálogo, aunque puedan tener el mismo nombre coloquial ("cosecha de manzana mano de obra" vs "cosecha de manzana cosecha").

### 4.4 Producción

Producción es lo que un trabajador hace en un día contra un folio y una labor. **El pago siempre es `cantidad × precio del folio para esa labor`**, sin excepción. Hay dos tablas porque la granularidad temporal del registro es distinta:

#### Tabla `produccion_mano_obra`

Una fila por `(trabajador, folio, labor, fecha)`. Se registra al cierre del día.

```
produccion_mano_obra:
  - trabajador_id      FK personal
  - folio_id           FK folio_comercial
  - labor_id           FK labores  (constraint: labor.modalidad = 'mano_obra')
  - fecha              date
  - cantidad           numeric  (lo que paga: bandejas, kilos, etc.)
  - horas              numeric  (informativa, no entra al cálculo de pago)
  - supervisor_id      FK supervisores
  - creado_at, creado_por
  - UNIQUE (trabajador_id, folio_id, labor_id, fecha)
```

#### Tabla `produccion_cosecha`

N filas por `(trabajador, folio, labor, fecha)`. Cada fila es un incremento inmutable registrado en tiempo real desde la app móvil.

```
produccion_cosecha:
  - trabajador_id      FK personal
  - folio_id           FK folio_comercial
  - labor_id           FK labores  (constraint: labor.modalidad = 'cosecha')
  - fecha              date
  - hora_registro      timestamptz  (momento exacto del incremento)
  - cantidad           numeric  (incremento de este registro)
  - supervisor_id      FK supervisores
  - creado_at
  - INMUTABLE: sin updates ni deletes lógicos.
```

#### Cálculo de pago (regla única)

```
pago_mano_obra(t, f, l, d) = cantidad × FolioComercialLabor.precio
pago_cosecha(t, f, l, d)   = SUM(cantidad sobre las N filas del día) × FolioComercialLabor.precio
```

Las horas registradas en mano de obra **no entran al cálculo de pago**, son informativas (productividad, control horario, reportes).

### 4.5 Contratos laborales

- **ContratoTrabajador (`contratos_trabajadores`)**: vincula trabajador con sociedad. Define inicio, fin, AFP, salud, horario.
- **ContratoHorarioSnapshot**: copia inmutable del horario al momento de contratar.
- Un trabajador puede tener varios contratos a lo largo del tiempo, con la misma o distinta sociedad del holding.
- A lo más un contrato vigente por trabajador-sociedad en una fecha dada.
- **La sociedad del trabajador en un período se deriva del contrato vigente, no de un campo en `personal`**.

### 4.6 Pagos al trabajador

- **RegistroPagoTransferencia / RegistroPagoEfectivo**: cada uno consolida un conjunto de filas de producción pagadas por una vía.
- **Días trabajados aprobados (`dias_trabajados_aprobados`)**: cuántos días del mes laboró cada trabajador, derivado de producción + asistencia + casa.
- **MesCerrado (`meses_cerrados`)**: marca un mes como cerrado por holding. Cierra solo la edición de días trabajados. El admin general puede reabrir.
- **Liquidación / Previred / LRE**: archivos legales generados a partir de contrato vigente + días trabajados + haberes/descuentos + AFP/salud. Pueden generarse antes del cierre como vista preliminar.

### 4.7 Comercial financiero

- **Cuenta contable (`cuentas`)**: por holding. Sirve para distribuir facturas.
- **Factura compra/venta SII**: descargada por scraping del SII (Selenium + Celery) para cada sociedad. Pasa por estados: por distribuir → distribuida (asignada a cuentas con porcentajes).
- **Distribución**: puede ser parcial. Una factura distribuida al 60% sigue siendo válida; el 40% restante puede distribuirse después.
- **Cartola bancaria**: archivo subido por el usuario, asociada a una cuenta bancaria de una sociedad. Sus movimientos se concilian con facturas distribuidas para registrar ingresos y egresos.

### 4.8 Transporte

- **EmpresaTransporte / Vehículo / Chofer / Tramo**: maestros de transporte por holding.
- **FolioTransportista**: acuerdo con una empresa de transporte, vinculado a vehículo(s) y tramo(s), con precio.
- **TrabajadorTransporteHistorial**: registra qué trabajadores movió cada vehículo cada día (insumo de cálculo).
- **PagoTransportista / Proforma**: el pago combina folio de transporte + tramo recorrido + trabajadores efectivamente transportados. Se materializa contra un folio de transporte; sin folio no hay pago.

---

## 5. Flujos críticos

### 5.1 Onboarding
1. Superadmin crea **Holding**.
2. Superadmin crea **Sociedades** del holding.
3. Superadmin crea **Admin general** (uno solo por holding) y le asigna todas las sociedades.
4. Admin general entra y configura: perfiles, parámetros (AFP, salud, áreas/cargos, casas, horarios, elementos de seguridad), clientes y campos.
5. Admin enrola trabajadores (manual, autoregistro web, autoregistro por enlace, app móvil con OCR de carnet).
6. Admin genera contratos laborales asociando trabajador con sociedad.

**Invariantes:**
- Holding sin admin general → no operable.
- Admin general sin sociedad asignada → no operable.

### 5.2 Ciclo productivo

1. Admin define **labores** (separadas por modalidad: mano_obra y cosecha) y **unidades de control**.
2. Admin firma un **folio comercial** con un cliente: campo, vigencia, conjunto de labores con su precio por unidad.
3. Supervisor en terreno (app móvil) registra producción día a día contra ese folio:
   - Si la labor es de mano de obra → al cierre del día registra cantidad producida (bandejas, kilos…) y horas trabajadas (informativa).
   - Si la labor es de cosecha → registra incrementos en tiempo real durante el día. Cada incremento es una fila inmutable.
4. Admin filtra producción no pagada y procesa pago (transferencia o efectivo).
5. Sistema calcula `pago = cantidad × precio` (en cosecha, sumando los incrementos del día) y registra el pago.
6. Cierre de mes consolida días trabajados.
7. Liquidaciones, Previred y LRE consumen contrato vigente + días trabajados + haberes/descuentos.

**Invariantes:**
- No se puede registrar producción contra un folio fuera de vigencia.
- No se puede registrar producción de mano de obra contra una labor de cosecha (y viceversa).
- No se puede registrar producción para un trabajador sin contrato vigente con alguna sociedad del holding en esa fecha.
- No se puede pagar dos veces la misma fila de producción (mano de obra) ni el mismo conjunto de incrementos (cosecha).
- Mes cerrado bloquea edición de días trabajados; sí permite generar liquidaciones preliminares.
- En mano de obra, `(trabajador, folio, labor, fecha)` es único.

### 5.3 Ciclo SII / costos
1. Admin guarda credenciales SII por sociedad.
2. Tarea Celery + Selenium descarga periódicamente facturas de compra y venta del SII de cada sociedad.
3. Las facturas quedan en estado **por distribuir**.
4. Admin asigna cada factura a una o más cuentas contables del holding con porcentajes. La distribución puede ser parcial; mientras quede saldo sin distribuir, la factura permanece en estado distribuible.
5. Admin sube cartolas bancarias por cuenta bancaria de una sociedad.
6. Sistema concilia movimientos de cartola con facturas distribuidas → registra ingresos y egresos.

**Invariantes:**
- La distribución de una factura no puede exceder 100%.
- Una factura distribuida al 100% queda cerrada para nuevas distribuciones.
- Cartola pertenece a una cuenta bancaria de una sociedad del holding.
- Procesar una cartola que no pertenezca a una sociedad del holding del usuario → error.

### 5.4 Ciclo transporte
1. Admin mantiene maestros: empresas de transporte, vehículos, choferes, tramos.
2. Admin registra **folios de transporte** vinculados a empresa + vehículo(s) + tramo(s) con precio.
3. Supervisor registra qué trabajadores se transportaron en qué vehículo cada día.
4. Sistema calcula pago al transportista combinando: folio de transporte + tramo recorrido + trabajadores transportados.
5. Admin confirma pago y/o emite proforma.

**Invariante:** sin folio de transporte vigente, no hay pago al transportista.

### 5.5 Cierre y reapertura de mes

- Cierre: el admin general marca un mes como cerrado para el holding. Bloquea edición de días trabajados de ese mes.
- Reapertura: el admin general puede reabrir un mes cerrado para reprocesarlo. La reapertura debe quedar registrada (quién, cuándo, motivo) para auditoría.

---

## 6. Reglas transversales (invariantes)

- **Tenancy**: toda escritura debe poder atribuirse a un holding. Lecturas filtran por holding del usuario autenticado. Sin excepción.
- **Dinero**: todos los montos se almacenan como `numeric(p,s)` con escala fija. Nunca `float` ni `int` para dinero.
- **Tiempo**: toda fecha-hora es `timestamptz`. Zona horaria del negocio: `America/Santiago`.
- **Identificación de personas**: RUT chileno o documento extranjero, normalizado a dígitos para indexar y comparar; formato canónico al exponer.
- **Borrado**: el dominio no permite borrado físico de entidades de negocio (trabajador, contrato, folio, producción, factura, pago). Solo soft-delete con campo `eliminado_at` o estado.
- **Auditoría mínima**: cada tabla operativa lleva `creado_at`, `creado_por`, `modificado_at`, `modificado_por`.
- **Idempotencia**: en mano de obra, registrar producción con la misma `(trabajador, folio, labor, fecha)` debe ser un upsert o un error explícito, nunca duplicar. En cosecha, los incrementos son aditivos por diseño; cada fila es un evento independiente.

---

## 7. Errores que deben fallar rápido

| Caso | Resultado esperado |
|---|---|
| Crear segundo admin general en un holding | Error: ya existe admin general. |
| Registrar producción contra folio fuera de vigencia | Error: folio no vigente. |
| Registrar producción de mano de obra contra labor de cosecha (o viceversa) | Error: modalidad de labor incorrecta. |
| Registrar producción para trabajador sin contrato vigente con alguna sociedad del holding | Error: trabajador sin contrato vigente. |
| Editar días trabajados en mes cerrado | Error: mes cerrado. (Admin puede reabrir.) |
| Distribuir factura excediendo 100% acumulado | Error: distribución supera el monto. |
| Re-pagar producción de mano de obra ya pagada | Error: producción ya pagada. |
| Cargar cartola de cuenta que no pertenece a sociedad del holding | Error: cuenta ajena. |
| Calcular pago al transportista sin folio de transporte vigente | Error: sin folio de transporte. |
| Reabrir mes cerrado sin registrar autor y fecha | Error: reapertura requiere auditoría. |

---

## 8. Decisiones explícitas tomadas en v1.1

- **Producción mide unidades, siempre**. No existe "pago por hora" en este sistema. Las horas en mano de obra son metadata.
- **Una labor, una modalidad**. No existen labores que sean ambas (mano de obra y cosecha). Si el negocio necesita ambas para una misma actividad, se crean dos labores distintas en el catálogo.
- **Cosecha es aditiva**. Cada fila de cosecha es un evento inmutable. El pago suma los eventos del día. Esto permite la app móvil registrar en tiempo real sin race conditions.
- **Sociedad del trabajador = contrato vigente**. `personal.sociedad_id` deja de ser fuente de verdad. Si se mantiene, es solo cache de la sociedad actual y debe regenerarse desde contrato.
- **Distribución SII parcial permitida**. Una factura puede estar 60% distribuida y seguir siendo distribuible.
- **Cuenta bancaria por sociedad, no por holding**. Las cartolas se concilian a nivel sociedad.
- **Pago a transportista exige folio de transporte**. Combinación de folio + tramo + trabajadores transportados.

---

## 9. Lo que esta spec **no** define (decisiones pendientes)

- Granularidad de producción más fina que el día para mano de obra (turnos, lotes específicos): no contemplado.
- Sub-roles dentro del admin general (ej. contador con acceso solo a SII): se modelan como perfiles.
- Reglas de retención y privacidad sobre documentos personales (carnets, firmas): no contemplado.
- Multi-país: el sistema asume Chile (RUT, AFP, Previred, LRE).
- Política exacta de motivo/aprobación para reapertura de mes cerrado.

---

## 10. Trazabilidad

Cada cambio futuro al esquema o al código debe citar la sección de esta spec que lo justifica. Si no la hay, primero se actualiza la spec.

Versión: 1.1 · Fecha: 2026-05-09