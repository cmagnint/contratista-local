# Mapa de comportamiento — contratista

**Sistema:** SaaS para contratistas agrícolas  
**Stack:** Angular + Django/DRF + PostgreSQL · Multi-tenant por holding → sociedades

---

## A. Capa de acceso

### Login

- **Frontend:** `LoginComponent` en `/login` → `POST /contratista_test_api/api_login/`
- **Fuentes:** `login.component.ts:148-224`, `services/contratista-api.service.ts:23-36`
- **Backend:** `views/auth.py:283-402` → `LoginSerializer (serializers.py:77)` → `Usuarios` → tabla `usuarios`
- **Reglas:** RUT se normaliza a dígitos. Superadmin entra con usuario Django; admin general como `Usuarios`. JWT incluye `user_type`, `holding_id`, `sociedades`, `perfil`, `permissions`, `allowed_routes`, `is_superuser`, `is_admin`.
- **Redirección:** superadmin → `/super-admin` · resto → `/fs/home`
- **JWT:** `services/jwt_service.py:68-193`
- ⚠ La validación revisa `perfil.estado`, no `Usuarios.estado` (`auth.py:309-314`).
- ⚠ Mapa de rutas JWT no cubre todas las rutas reales y contiene `/fs/produccion-trabajador` que no está en `app.routes.ts` (`jwt_service.py:207-248`, `frontend/services/jwt.service.ts:458-490`).

---

### Recuperación de contraseña

- **Frontend:** `LoginComponent` → `POST /contratista_test_api/password-reset/` (acciones `check_user`, `generate_code`, `verify_code`)
- **Fuentes:** `login.component.ts:278-372`
- **Backend:** `PasswordResetAPIView (views/auth.py:33-199)` → `Usuarios` → tabla `usuarios`
- **Reglas:** busca por RUT o correo; genera código de 6 dígitos con expiración; envía email vía `send_mail`.
- ⚠ No se observó throttling ni bloqueo por intentos.

---

### Cambio de contraseña

- **Frontend:** `ChangePassword` en `/change-password` → `POST /contratista_test_api/password-reset/` (acción `change_password`)
- **Fuentes:** `change-password.component.ts:58-108`
- **Backend:** `PasswordResetAPIView (views/auth.py:171-199)` → `Usuarios.set_password()` → tabla `usuarios`
- **Reglas:** exige RUT, código y nueva contraseña; limpia código tras cambio.
- ⚠ Validación de fortaleza de contraseña: no queda clara en la lectura.

---

## B. Superadmin

> Acceso restringido por guard: bloquea `/fs` para superadmin y `/super-admin` para usuarios normales (`auth-guard/contratista-auth.guard.ts:78-104`).

---

### Holdings

- **Frontend:** `SuperadminComponent` en `/super-admin` → `GET/POST/PATCH /api_holding/`
- **Fuentes:** `superadmin.component.ts:152-257`
- **Backend:** `HoldingAPIView (views/admin.py:44-245)` → `HoldingSerializer` → `Holding` → tabla `holding`
- **Datos:** al crear holding, backend inicializa perfiles, módulos web/móvil, AFP y Salud base.

---

### Sociedades

- **Frontend:** `SuperadminComponent` → `GET/POST/PATCH /api_sociedad/` con filtro `?holding=`
- **Fuentes:** `superadmin.component.ts:282-412`
- **Backend:** `SociedadAPIView (views/admin.py:251-329)` → `SociedadSerializer` → `Sociedad` → tabla `sociedad`
- **Datos:** RUT, razón social, giro, dirección, comuna/región, holding.
- **Acoplamientos:** alimenta todos los módulos operativos por filtro de sociedad global.

---

### Administradores principales

- **Frontend:** `SuperadminComponent` → `GET/POST/PATCH /api_admin/`
- **Fuentes:** `superadmin.component.ts:459-584`
- **Backend:** `AdminAPIView (views/admin.py:382-555)` → crea `PersonalTrabajadores` + `Usuarios`
- **Tablas:** `usuarios`, `personal`, `perfiles` + M2M con `sociedad`
- **Reglas:** solo un administrador principal por holding; se le asignan todos los módulos web/submódulos.

---

## C. Módulos operativos

---

### Administración › Personal

- **Qué hace:** mantiene ficha base de trabajadores/personas usadas por usuarios, contratos, pagos, producción y leyes sociales.
- **Frontend:** `PersonalComponent` en `/fs/personal-empresas`
- **Fuentes:** `pages/personal/personal.component.ts:261-452`
- **Endpoints:**
  - `GET/POST/PUT/DELETE /api_personal/` → `views/personal.py:PersonalAPIView`
  - `PATCH/GET /api_personal_documentos/{id}/`
  - Catálogos: `api_sociedad/`, `api_areas_administracion/`, `api_cargos_administracion/`, `api_afp_trabajadores/`, `api_salud_trabajadores/`, `api_bancos/`
- **Modelos / tablas:** `PersonalTrabajadores/personal`, `AreasAdministracion/areas_administracion`, `CargosAdministracion/cargos_admnistracion`, `AFP/afp`, `Salud/salud`, `Banco/banco`
- **Entrada:** identificación, contacto, sociedad, cargo/área, previsión, banco, documentos.
- **Salida:** JSON de personas, blob/documentos.
- **Procesos:** carga/descarga documental. No Celery observado.
- **Lee de:** Sociedades, AFP, Salud, áreas/cargos, bancos.
- **Escribe para:** Usuarios, Contratos, Producción, Pagos, Leyes Sociales, Transporte.

---

### Administración › Usuarios

- **Qué hace:** administra cuentas operativas, perfil, sociedades asignadas, supervisor/persona asociada.
- **Frontend:** `UsuariosComponent` en `/fs/administrar-usuarios`
- **Fuentes:** `pages/usuarios/usuarios.component.ts:133-363`
- **Endpoints:**
  - `GET/POST/PUT/DELETE /api_usuarios/` → `views/admin.py:UsuariosAPIView`
  - `GET /api_perfil/{holding}/`, `/api_personal_for_users/{holding}/`, `/api_supervisores/{holding}/`, `/api_sociedad/?holding=`
- **Modelos / tablas:** `Usuarios/usuarios`, `Perfiles/perfiles`, `PersonalTrabajadores/personal`, `Supervisores/supervisores`, `Sociedad/sociedad`
- **Entrada:** RUT/email, perfil, sociedades, supervisor/persona.
- **Salida:** JSON de usuarios con perfil y permisos.
- **Lee de:** Personal, Perfiles, Sociedades, Supervisores.
- **Escribe para:** acceso consumido por guard, JWT y menú.

---

### Administración › Parámetros › Sociedades

- **Qué hace:** edición operativa de datos de sociedades del holding.
- **Frontend:** `SociedadComponent` en `/fs/admin-sociedad`
- **Fuentes:** `pages/sociedad/sociedad.component.ts:135-328`
- **Endpoints:** `GET/PATCH/POST /api_sociedades_modify/{holdingId}` → `SociedadDetailAPIView`; `GET /api_bancos/`
- **Modelos / tablas:** `Sociedad/sociedad`, `Banco/banco`
- **Escribe para:** datos base usados por contratos, pagos, leyes sociales y tesorería.

---

### Administración › Parámetros › AFP

- **Qué hace:** mantiene instituciones AFP y tasas.
- **Frontend:** `AfpComponent` en `/fs/r-h-afp`
- **Fuentes:** `pages/afp/afp.component.ts:77-99`
- **Endpoints:** `GET/PUT /api_afp_trabajadores/` → `views/personal.py:AFPAPIView`
- **Modelos / tablas:** `AFP/afp`
- **Escribe para:** Personal, Contratos, Liquidaciones, Previred.

---

### Administración › Parámetros › Salud

- **Qué hace:** mantiene instituciones de salud.
- **Frontend:** `SaludComponent` en `/fs/r-h-salud`
- **Fuentes:** `pages/salud/salud.component.ts:68-97`
- **Endpoints:** `GET/PUT /api_salud_trabajadores/` → `views/personal.py:SaludAPIView`
- **Modelos / tablas:** `Salud/salud`
- **Escribe para:** Personal, Contratos, Liquidaciones, Previred.

---

### Administración › Parámetros › Áreas / Cargos

- **Qué hace:** define estructura interna administrativa para fichas de trabajadores.
- **Frontend:** `AreasCargosAdministracionComponent` en `/fs/areas-cargos-administracion`
- **Fuentes:** `pages/areas-cargos-administracion/areas-cargos-administracion.component.ts:114-272`
- **Endpoints:**
  - `GET/POST/PUT/DELETE /api_areas_administracion/`, `/api_cargos_administracion/`
  - → `views/admin.py:AreaAdministracionAPIView:704-758`, `CargoAdministracionAPIView:764-820`
- **Modelos / tablas:** `AreasAdministracion/areas_administracion`, `CargosAdministracion/cargos_admnistracion`
- **Escribe para:** Personal y Enrolamiento.

---

### Administración › Parámetros › Perfiles

- **Qué hace:** define permisos web/móvil por módulo y submódulo.
- **Frontend:** `PerfilesComponent` en `/fs/administrar-perfiles`
- **Fuentes:** `pages/perfiles/perfiles.component.ts:217-535`
- **Endpoints:**
  - `GET/POST/PUT/DELETE /api_perfil/{holding}/`
  - `GET /api_modulos_web/{holding}/`, `/api_submodulos_web/{holding}/`, `/api_modulos_movil/{holding}/`, `/api_submodulos_movil/{holding}/`
  - → `views/admin.py:591-699, 560-585`
- **Modelos / tablas:** `Perfiles/perfiles`, `ModulosWeb/modulos_web`, `SubModulosWeb/sub_modulos_web`, `ModulosMovil/modulos_movil`, `SubModulosMovil/sub_modulos_movil`
- **Escribe para:** Login/JWT, AuthGuard y menú.

---

### Clientes › Administrar

- **Qué hace:** mantiene clientes agrícolas y sus campos.
- **Frontend:** `ClientesComponent` en `/fs/administrar-clientes`
- **Fuentes:** `pages/clientes/clientes.component.ts:506-644`
- **Endpoints:**
  - `GET/POST/PUT/DELETE /api_clientes/`, `/api_campos_clientes/`
  - → `views/clientes.py:ClienteAPIView:33`, `CamposClientesAPIView:118`
- **Modelos / tablas:** `Clientes/clientes`, `CamposClientes/campos_clientes`
- **Escribe para:** Comercial, Producción, Informes, Costos, Leyes Sociales.

---

### Clientes › Áreas / Cargos

- **Qué hace:** define áreas y cargos asociados al cliente.
- **Frontend:** `AreasCargosClientesComponent` en `/fs/administrar-area-cargos-cliente`
- **Fuentes:** `pages/areas-cargos-clientes/areas-cargos-clientes.component.ts:114-272`
- **Endpoints:** `GET/POST/PUT/DELETE /api_areas_cliente/`, `/api_cargos_cliente/` → `views/clientes.py:183-310`
- **Modelos / tablas:** `AreasCliente/areas_clientes`, `CargosCliente/cargos_clientes`
- **Lee de:** Clientes.
- **Escribe para:** Contactos y acuerdos comerciales.

---

### Clientes › Contactos

- **Qué hace:** mantiene contactos por cliente, área y cargo.
- **Frontend:** `ContactosClientesComponent` en `/fs/administrar-contactos-clientes`
- **Fuentes:** `pages/contactos-clientes/contactos-clientes.component.ts:106-232`
- **Endpoints:**
  - `GET/POST/PUT/DELETE /api_contactos_clientes/`
  - Lee: `api_clientes/`, `api_areas_cliente/`, `api_cargos_cliente/`
  - → `views/clientes.py:ContactoClienteAPIView:312`
- **Modelos / tablas:** `ContactosClientes/contactos_clientes`, `Clientes`, `AreasCliente`, `CargosCliente`

---

### Comercial › Folio / Acuerdo Comercial

- **Qué hace:** configura acuerdos comerciales por cliente/campo/labor, con pagos, supervisores y datos de transporte.
- **Frontend:** `FolioComercialComponent` en `/fs/folio-comercial`
- **Fuentes:** `pages/folio-comercial/folio-comercial.component.ts:185-739`
- **Endpoints:**
  - `GET/POST/PUT/DELETE /folio_comercial/` → `views/produccion.py:FolioComercialAPIView:1087-1167`
  - Lee: `api_clientes/`, `api_campos_clientes/`, `labores_comercial/`, `api_empresa_transportes/`, `api_vehiculos_transportes/`, `api_choferes_transportes/`, `horarios/`
- **Modelos / tablas:** `FolioComercial/folio_comercial`, `FolioComercialLabor/fc_labor_pago`, `HistorialCambioFolio/historial_cambios_folio`
- **Entrada:** cliente, campo, labores, valores, vigencias, transporte.
- **Salida:** JSON.
- **Lee de:** Clientes, Labores, Transporte, Horarios.
- **Escribe para:** Producción, Pagos, Informes, Transporte.

---

### Comercial › Labores

- **Qué hace:** mantiene labores productivas cobrables/pagables.
- **Frontend:** `LaboresComercialComponent` en `/fs/labores-comercial`
- **Fuentes:** `pages/labores-comercial/labores-comercial.component.ts:112-172`
- **Endpoints:** `GET/POST/PUT/DELETE /labores_comercial/`; lee `unidad_control_comercial/` → `views/produccion.py:LaboresAPIView:1030-1085`
- **Modelos / tablas:** `Labores/labores`, `UnidadControl/unidad_control`
- **Escribe para:** Folio Comercial, Producción, Informes.

---

### Comercial › Unidad de Control

- **Qué hace:** define unidades de medida/control para labores.
- **Frontend:** `UnidadControlComercialComponent` en `/fs/unidad-control-comercial`
- **Fuentes:** `pages/unidad-control-comercial/unidad-control-comercial.component.ts:107-154`
- **Endpoints:** `GET/POST/PUT/DELETE /unidad_control_comercial/` → `views/produccion.py:UnidadControlAPIView:973-1028`
- **Modelos / tablas:** `UnidadControl/unidad_control`
- **Escribe para:** Labores y Folio Comercial.

---

### Costos › Cuentas

- **Qué hace:** administra cuentas contables para distribuir facturas.
- **Frontend:** `CuentasComponent` en `/fs/cuentas`
- **Fuentes:** `pages/cuentas/cuentas.component.ts:74-165`
- **Endpoints:** `GET/POST /api_cuentas/`, `PUT /api_cuentas/update/{id}/`, `DELETE /api_cuentas/delete/{id}/` → `views/sii.py:CuentasAPIView:77`
- **Modelos / tablas:** `Cuenta/cuentas`
- **Escribe para:** facturas compra/venta distribuidas y reportes de costos.

---

### Costos › Parámetros Factura Compra / Venta

- **Qué hace:** guarda credenciales/configuración SII automática por holding para compras y ventas.
- **Frontend:** `/fs/parametros-factura-compra`, `/fs/parametros-factura-venta`
- **Fuentes:** `parametros-factura-compra.component.ts:276-433`, `parametros-factura-venta.component.ts:277-434`
- **Endpoints:**
  - `POST /facturas_compra_automatico/`, `POST /facturas_venta_automatico/` con acciones `get_automatic_configuration`, `save_automatic_configuration`
  - → `views/sii.py:368-428, 3851`
- **Modelos / tablas:** `ConfiguracionSIIAutomaticaCompra/configuracion_sii_automatica`, `ConfiguracionSIIAutomaticaVenta/configuracion_sii_automatica_venta`
- **Procesos:** Selenium/SII y Celery (`services/tasks.py:41-187, 1972-2113`)

---

### Costos › Facturas Compra Automatizado / Distribuidas

- **Qué hace:** descarga, crea manualmente, distribuye y exporta facturas de compra SII.
- **Frontend:** `/fs/facturas-compra-automatizado`, `/fs/facturas-compra-distribuidas`
- **Fuentes:** `facturas-compra-automatizado.component.ts:441-1423`, `facturas-compra-distribuidas.component.ts:210-519`
- **Endpoints:**
  - `POST /facturas_compra_automatico/`
  - `GET /facturas_sii_pdf/{id}/`
  - `POST /facturas_sii_compra_distribuidas/`
  - → `views/sii.py:368-428, 2287, 2465`
- **Modelos / tablas:** `FacturaCompraSIIPorDistribuir/facturas_sii_por_distribuir`, `FacturaCompraSIIDistribuida/facturas_sii_distribuidas`, `Cuenta/cuentas`
- **Salida:** JSON, PDF, CSV.
- **Procesos:** scraping SII, descarga PDF, Celery (`services/tasks.py:653-749, 1078-1539`)
- **Escribe para:** Tesorería Egresos y Costos.

---

### Costos › Facturas Venta Automatizado / Distribuidas

- **Qué hace:** descarga, crea, distribuye y exporta facturas de venta SII.
- **Frontend:** `/fs/facturas-venta-automatizado`, `/fs/facturas-venta-distribuidas`
- **Fuentes:** `facturas-venta-automatizado.component.ts:440-1425`, `facturas-venta-distribuidas.component.ts:210-519`
- **Endpoints:**
  - `POST /facturas_venta_automatico/`
  - `GET /facturas_venta_sii_pdf/{id}/`
  - `POST /facturas_sii_venta_distribuidas/`
  - → `views/sii.py:3851, 5756, 5877-6115`
- **Modelos / tablas:** `FacturaVentaSIIPorDistribuir/facturas_venta_sii_por_distribuir`, `FacturaVentaSIIDistribuida/facturas_venta_sii_distribuidas`, `Cuenta/cuentas`
- **Procesos:** Selenium/SII, CSV/PDF, Celery (`services/tasks.py:2752-2888, 2968-3719`)
- **Escribe para:** Tesorería Ingresos.

---

### Recursos Humanos › Maestro Trabajadores

- **Qué hace:** administra contratos vigentes/históricos del trabajador y retroactividad.
- **Frontend:** `MaestroTrabajadoresComponent` en `/fs/maestro-trabajadores`
- **Fuentes:** `pages/maestro-trabajadores/maestro-trabajadores.component.ts:215-612`
- **Endpoints:**
  - `GET/PATCH/DELETE /api_contratos_trabajadores/`
  - `GET /api_crear_contrato_web/`
  - `POST /api_contrato_retroactivo/`
  - → `views/contratos.py:1149, 1375, 1716`
- **Modelos / tablas:** `ContratoTrabajador/contratos_trabajadores`, `PersonalTrabajadores/personal`, `ContratoHorarioSnapshot/contrato_horario`
- **Lee de:** Personal, Sociedades, Horarios.
- **Escribe para:** Liquidaciones, Previred, Pagos, documentos.

---

### Recursos Humanos › Enrolamiento

- **Qué hace:** registra trabajadores desde web con OCR/documentos y datos laborales.
- **Frontend:** `EnrolamientoComponent` en `/fs/enrolamiento`
- **Fuentes:** `pages/enrolamiento/enrolamiento.component.ts:155-668`
- **Endpoints:**
  - Catálogos: `api_sociedad/{holding}/`, `folio_comercial/`, `api_supervisores/`, `api_casas_trabajadores/`, `api_areas_administracion/`, `api_vehiculos_transportes/`, `api_cargos_administracion/`, `api_bancos/`
  - `POST /api_convert_pdf_to_image/`, `/api_ocr_carnet/`, `/personal_trabajadores_mobile/`
  - → `views/personal.py:PersonalTrabajadoresMobileAPIView:334`; `views/docs.py:CarnetOCRAPIView:21`, `PDFToImageAPIView:124`
- **Modelos / tablas:** `PersonalTrabajadores/personal` y catálogos asociados.
- **Procesos:** OCR de cédula, conversión PDF↔imagen.
- **Lee de:** Comercial, Supervisores, Casas, Transporte y catálogos.
- **Escribe para:** Personal/Trabajadores.

---

### Recursos Humanos › Autoregistro / APK Link / Generar QR

- **Qué hace:** genera enlaces externos para registro o APK y QR de trabajadores cosecha.
- **Frontend:** `/fs/autoregistro-personal`, `/apk-link/:token/:id`, `/arl/:token/:id`, `/fs/generar-qr` (`app.routes.ts:80-87, 110-111`)
- **Endpoints:**
  - `GET/POST /enlaces-auto-registro/`
  - `GET /validar-enlace/{token}/{id}/`
  - `POST /personal-web/`
  - `GET/POST /link_apk/{holding_id}/`
  - `GET /validate_apk/{token}/{id}/`, `/download_apk/{token}/{id}/`
  - `GET /api_trabajadores_cosecha/`
  - → `views/personal.py:986-1120, 568, 950`
- **Modelos / tablas:** `EnlaceAutoRegistro/enlaces_auto_registro`, `APKLink/apk_links`, `CodigoQR/asociacion_codigo_qr`, `PersonalTrabajadores/personal`
- **Salida:** enlaces, APK, QR/datos de trabajadores.
- **Escribe para:** Personal y datos de acceso móvil.

---

### Recursos Humanos › Traspaso Trabajadores

- **Qué hace:** registra cambios de casa/transporte/asignación operativa de trabajadores.
- **Frontend:** `TraspasoTrabajadoresComponent` en `/fs/traspaso-trabajadores`
- **Fuentes:** `pages/traspaso-trabajadores/traspaso-trabajadores.component.ts:57-108`
- **Endpoints:** `GET/POST /api_traspaso_trabajadores/` → `views/personal.py:TraspasoTrabajadoresAPIView:2579`
- **Modelos / tablas:** `RegistroCasaTrabajador/registro_casa_trabajador`, `TrabajadorTransporteHistorial/trabajador_transporte_historial`, `PersonalTrabajadores/personal`
- **Lee de:** Personal, Casas, Transporte.
- **Escribe para:** historial consumido por Informes y Transporte.

---

### Recursos Humanos › Generación de Contratos

- **Qué hace:** administra formatos, parámetros, asociación y generación masiva de documentos contractuales.
- **Frontend:** `/fs/formatos`, `/fs/generar-contrato`, `/fs/asoc-cont`, `/fs/par-cont`
- **Fuentes:** `formatos.component.ts:268-2735`, `generar-contratos.component.ts:101-305`, `asociar-contratos.component.ts:63-158`, `parametros-contratos.component.ts:59-146`
- **Endpoints:**
  - `GET/POST/DELETE /api_firma_empleador/`
  - `GET/POST/PUT/DELETE /api_documento_nativo/`
  - `GET/POST /api_generar-documentos-masivo/`
  - `GET /api_listar-documentos/`
  - `GET/POST/PUT/DELETE /api_parametros/`
  - `GET /api_trabajadores_por_parametro/`
  - `POST /api_generar-documentos-por-parametro/`
  - `POST/DELETE /api_contratos_asociados/`
  - → `views/contratos.py:54, 698, 1117, 1645, 1874, 2033, 2086`
- **Modelos / tablas:** `ContratoVariables/documentos_variables`, `FirmaOrganizacion/firmas_organizacion`, `Parametro/parametros_contrato`, `ContratoAsociadoTrabajador/contratos_asociados_trabajador`, `ContratoTrabajador/contratos_trabajadores`
- **Salida:** PDF/documentos generados, JSON de plantillas/parámetros.
- **Lee de:** Personal, Sociedades, Contratos, Elementos de Seguridad.
- **Escribe para:** documentos para Maestro Trabajadores.

---

### Recursos Humanos › Parámetros RH (Casas, Horarios, Elementos de Seguridad, Supervisores)

- **Qué hace:** mantiene casas, horarios, elementos de seguridad y supervisores.
- **Frontend:** `/fs/r-h-casas`, `/fs/inf-casas`, `/fs/r-h-horarios`, `/fs/elem-seg`, `/fs/superv`
- **Fuentes:** `casas.component.ts:69-121`, `informe-casas.component.ts:59-185`, `horarios.component.ts:179-277`, `elementos-seguridad.component.ts:58-162`, `supervisores.component.ts:86-258`
- **Endpoints:**
  - `GET/POST/PUT/DELETE /api_casas_trabajadores/`, `/horarios/`, `/elementos_seguridad/`, `/api_supervisores/`
  - `GET /informe-casas/`, `POST /informe-casas/cambiar-casa/`
  - → `views/produccion.py:CasasTrabajadoresAPIView:144`, `HorarioAPIView:1185`, `InformeCasasAPIView:202`, `CambiarCasaAPIView:268`; `views/personal.py:SupervisorAPIView:778`; `views/parametros.py:ElementoSeguridadAPIView:22`
- **Modelos / tablas:** `CasasTrabajadores/casas`, `Horarios/horarios`, `ElementoSeguridad/elemento_seguridad`, `Supervisores/supervisores`, `RegistroCasaTrabajador/registro_casa_trabajador`
- **Escribe para:** Enrolamiento, Contratos, Producción, Informes, Leyes Sociales.

---

### Leyes Sociales › Días Trabajados

- **Qué hace:** calcula, revisa y aprueba días trabajados por periodo.
- **Frontend:** `InformeDiasTrabajadosComponent` en `/fs/informe-dias-trab`
- **Fuentes:** `pages/informe-dias-trabajados/informe-dias-trabajados.component.ts:223-1000`
- **Endpoints:**
  - `GET/POST /meses-cerrados/`, `/dias-trabajados-aprobados/`
  - `POST /informe-dias-trabajados/`
  - → `views/rrhh.py:InformeDiasTrabajadosAPIView:318-433`, `DiasTrabajadosAprobadosAPIView:440-602`, `MesCerradoAPIView:608-681`
- **Modelos / tablas:** `DiasTrabajadosAprobados/dias_trabajados_aprobados`, `MesCerrado/meses_cerrados`, `ProduccionTrabajador/produccion`
- **Lee de:** Producción, Personal, Clientes/Campos/Casas.
- **Escribe para:** Liquidaciones, Previred, LRE.

---

### Leyes Sociales › Haberes / Descuentos / Asignaciones

- **Qué hace:** define conceptos y los asigna a trabajadores.
- **Frontend:** `/fs/haberes-descuentos`, `/fs/asignacion-haberes`, `/fs/asignacion-descuentos`
- **Fuentes:** `haberes-descuentos.component.ts:110-268`, `asignacion-haberes.component.ts:141-314`, `asignacion-descuentos.component.ts:141-314`
- **Endpoints:**
  - `GET/POST/PUT/DELETE /api_haberes/`, `/api_descuentos/`
  - `POST /api_asignar_haberes/`, `/api_asignar_descuentos/`
  - → `views/rrhh.py:688-842`
- **Modelos / tablas:** `Haberes/haberes`, `Descuentos/descuentos`, `TrabajadorHaber/trabajador_haber`, `TrabajadorDescuento/trabajador_descuento`
- **Lee de:** Personal y filtros de cliente/casa.
- **Escribe para:** Liquidaciones, Previred, LRE.

---

### Leyes Sociales › Liquidaciones / Previred / LRE

- **Qué hace:** genera archivos legales/remuneracionales a partir de trabajadores, contratos, días y conceptos.
- **Frontend:** `/fs/liquidaciones`, `/fs/arch-previred`, `/fs/lre`
- **Fuentes:** `liquidaciones.component.ts:207`, `previred.component.ts:152-312`, `lre.component.ts:89-122`
- **Endpoints:**
  - `POST /generar-liquidaciones/`
  - `POST /generar-archivo-previred/`
  - `GET /generar-libro-remuneraciones/`
  - → `views/rrhh.py:GenerarLiquidacionesAPIView:909`, `GenerarArchivoPreviewAPIView:1557-1688`, `LibroRemuneracionesElectronicoAPIView:1226`
- **Modelos / tablas:** `PersonalTrabajadores`, `ContratoTrabajador`, `DiasTrabajadosAprobados`, `Haberes`, `Descuentos`, `AFP`, `Salud`, `Sociedad`
- **Salida:** blob de liquidaciones, TXT Previred, archivo LRE.
- **Procesos:** generación de archivos.
- **Lee de:** Personal, Contratos, Días Trabajados, Haberes/Descuentos.
- **Escribe para:** archivos legales externos.

---

### Pagos › Transferencia / Efectivo

- **Qué hace:** filtra producción pendiente, procesa pagos y genera planillas.
- **Frontend:** `/fs/pago-transf`, `/fs/pago-efect`
- **Fuentes:** `pago-transferencia.component.ts:109-411`, `pago-efectivo.component.ts:123-364`
- **Endpoints:**
  - `GET /produccion-filtrada-transferencia/`, `POST /procesar-pago/`, `GET /generar-planilla-transferencia/`
  - equivalentes para efectivo
  - → `views/produccion.py:160-508, 560-960`
- **Modelos / tablas:** `ProduccionTrabajador/produccion`, `RegistroPagoTransferencia/registro_pagos_transferencia`, `RegistroPagoEfectivo/registro_pagos_efectivo`, `HistorialCambioPago/historial_cambios_pago`
- **Salida:** JSON de producción/pagos, PDF de planilla.
- **Lee de:** Producción, Trabajadores, Sociedades, Cuentas de origen.
- **Escribe para:** Informes de pago e historial.

---

### Pagos › TXT Banco / Informes / Reproceso

- **Qué hace:** genera archivo bancario, consulta pagos realizados y reporta pagos.
- **Frontend:** `/fs/txt-banco`, `/fs/transf-rlzda`, `/fs/reprcs-pago`, `/fs/informe-pago`
- **Fuentes:** `txt-banco.component.ts:100`, `transferencias-realizadas.component.ts:94`, `reprocesar-pago.component.ts:198`
- **Endpoints:**
  - `POST /generar_txt_banco/` → `views/contratos.py:GenerarTxtBancoAPIView:551`
  - `GET /pagos-realizados/` → `views/produccion.py:PagosRealizadosAPIView:514`
  - `GET /variables-dropdown-informe-pago/`, `POST /informe-pago/generar/`, `GET /informe-pago/csv/` → `views/produccion.py:1348-1419`
- **Modelos / tablas:** pagos transferencia/efectivo, producción, personal, banco/cuenta.
- **Salida:** TXT banco, JSON, CSV.
- **Lee de:** Pagos procesados y Producción.
- ⚠ Frontend usa `POST /reprocesar-pagos/` pero no aparece ruta backend en `urls.py:183-405`.

---

### Tesorería › Ingresos / Egresos / Historial

- **Qué hace:** procesa cartolas bancarias, concilia movimientos con facturas distribuidas y registra ingresos/egresos.
- **Frontend:** `/fs/pagos-ingresos`, `/fs/pagos-egresos`, `/fs/historial-pagos`
- **Fuentes:** `pagos-ingresos.component.ts:177-473`, `pagos-egresos.component.ts:176-472`
- **Endpoints:**
  - `GET /tesoreria/cuentas-origen/banco/{codigo}/`
  - `POST /tesoreria/procesar-cartola/`
  - `GET /tesoreria/movimientos-saldos/`, `/tesoreria/facturas-distribuidas/`
  - `POST /tesoreria/registrar-ingreso/`
  - Equivalentes para egreso: `procesar-cartola-egreso`, `movimientos-egreso-saldos`, `facturas-compra-distribuidas`, `registrar-egreso`
  - Historial: `GET /tesoreria/historial/{tipo}/{estado}/`, `/csv/`
  - → `views/sii.py:6202-6985, 7295-7852, 8474-8678`
- **Modelos / tablas:** `CuentaOrigen/cuenta_origen`, `CartolaMovimiento/cartola_movimiento`, `FacturaVentaSIIDistribuida`, `FacturaCompraSIIDistribuida`, `RegistroIngreso/registro_ingreso`, `RegistroEgreso/registro_egreso`
- **Salida:** JSON de movimientos/saldos, CSV historial.
- **Procesos:** lectura de cartola subida por usuario.
- **Lee de:** facturas de Costos/SII.
- **Escribe para:** conciliación financiera e historial.

---

### Transporte › Transportistas / Vehículos / Choferes / Tramos

- **Qué hace:** mantiene maestros de transporte.
- **Frontend:** `/fs/empresas-transporte`, `/fs/vehiculos-transporte`, `/fs/choferes-transporte`, `/fs/tramos`
- **Fuentes:** `empresas-transporte.component.ts:520-608`, `vehiculos-transporte.component.ts:121-197`, `choferes-transporte.component.ts:255-363`, `tramos.component.ts:95-155`
- **Endpoints:** `GET/POST/PUT/DELETE /api_empresa_transportes/`, `/api_vehiculos_transportes/`, `/api_choferes_transportes/`, `/api_tramos/` → `views/transporte.py:61-465`
- **Modelos / tablas:** `EmpresasTransporte/empresas_transporte`, `VehiculosTransporte/vehiculos_transporte`, `DocumentosVehiculo/documentos_vehiculo`, `ChoferesTransporte/choferes`, `DocumentosChofer/documentos_chofer`, `Tramos/tramos_transportista`
- **Entrada:** datos legales, bancarios, documentos, vehículos, choferes, tramos.
- **Salida:** JSON/FormData.
- **Escribe para:** Folio Comercial, Folio Transporte, Pagos Transportista, Enrolamiento.

---

### Transporte › Folio / Pago / Proforma

- **Qué hace:** crea folios de transporte, calcula pago transportista y genera proformas.
- **Frontend:** `/fs/folio-transporte`, `/fs/pagos-transporte`, `/fs/proforma-transporte`
- **Fuentes:** `folio-transportista.component.ts:92-172`, `pagos-transportista.component.ts:111-405`, `proformas-transportista.component.ts:98-368`
- **Endpoints:**
  - `GET/POST/PUT/DELETE /api_folio_transportista/`
  - `GET /calculo-pago-transportista/`
  - `POST /confirmar-pago-transportista/`
  - `GET/POST/PUT/DELETE /generar-proformas/`
  - `GET /generar-proformas/{id}/pdf/`
  - → `views/transporte.py:471-767, 905-1080`
- **Modelos / tablas:** `FolioTransportista/folios_transportes`, `PagoTransportista/pagos_transportista`, `DetallePagoTransportista/detalle_pagos_transportista`, `ProformaTransportista/proformas_transportista`, `TrabajadorTransporteHistorial/trabajador_transporte_historial`
- **Salida:** JSON de cálculo/pago, PDF de proforma, TXT banco.
- **Lee de:** Comercial, Producción, Transportistas, Tramos, historial trabajador-transporte.
- **Escribe para:** pagos/proformas.
- ⚠ `ConfirmarPagoTransportista` existe como URL pero la clase leída no define métodos (`views/transporte.py:562-564`).

---

### Informes › Pagos / Rendimiento / Transportista

- **Qué hace:** consolida reportes de producción, pagos y transporte.
- **Frontend:** `/fs/informe-pago`, `/fs/informe-rendimiento`, `/fs/informe-transportista`
- **Fuentes:** `informe-rendimiento.component.ts:107-137`, `informe-transportista.component.ts:91-219`
- **Endpoints:**
  - Pagos: `GET /variables-dropdown-informe-pago/`, `POST /informe-pago/generar/`, `GET /informe-pago/csv/`
  - Rendimiento: `POST /informe-rendimiento/`
  - Transportista: `POST /informe-transportista/`
  - → `views/produccion.py:1157-1419`, `views/transporte.py:774-899`
- **Modelos / tablas:** `ProduccionTrabajador/produccion`, `PersonalTrabajadores/personal`, `Clientes`, `Labores`, `Supervisores`, `EmpresasTransporte`, `PagoTransportista`
- **Salida:** JSON y CSV.
- No se observó escritura operativa.

---

## D. Flujos transversales

### 1. Onboarding

Superadmin crea Holding → crea Sociedad → crea admin principal (`Usuarios` + `PersonalTrabajadores`) → admin mantiene perfiles, sociedades y personal → enrolamiento/autoregistro crean trabajadores → generación de contratos produce documentos y contratos asociados.

### 2. Ciclo productivo

Clientes + Labores + Unidad de Control alimentan Folio Comercial → producción se registra contra folio/labor/trabajador → Pagos filtra producción pendiente → procesa transferencia/efectivo → Informes y Leyes Sociales consumen producción/pagos.

### 3. Ciclo SII / costos

Parámetros SII guardan credenciales/config → Celery/Selenium descarga CSV/PDF → facturas quedan por distribuir → usuario distribuye a cuentas → Tesorería concilia cartolas contra facturas distribuidas → historial exporta JSON/CSV.

### 4. Transporte

Maestros de transportista/vehículo/chofer/tramo → Folio Transporte define reglas → historial trabajador-transporte y producción alimentan cálculo → Pago Transportista y Proforma generan documentos/pagos.

### 5. Ciclo remuneracional

Personal + Contratos + Días Trabajados + Haberes/Descuentos → Liquidaciones/Previred/LRE generan archivos legales. AFP/Salud parametrizan los cálculos.

---

## E. Mapa de acoplamiento

| Módulo | Lee de | Escribe para |
|---|---|---|
| Administración Personal | Sociedades, AFP, Salud, Áreas/Cargos, Bancos | Usuarios, Contratos, Pagos, Leyes Sociales, Producción |
| Usuarios / Perfiles | Personal, Supervisores, Sociedades | Login, JWT, Menú, Guard |
| Clientes | Sociedades | Comercial, Producción, Informes, Leyes Sociales |
| Comercial | Clientes, Labores, Transporte, Horarios | Producción, Pagos, Informes, Transporte |
| Costos / SII | Cuentas, Config SII | Tesorería, Costos distribuidos |
| Recursos Humanos | Personal, Sociedades, Horarios, Casas, Transporte | Contratos, Leyes Sociales, Producción |
| Leyes Sociales | Personal, Contratos, Producción, Haberes/Descuentos | Archivos legales, cierres |
| Pagos | Producción, Personal, Banco/Cuentas | Historial, Informes, TXT banco |
| Tesorería | Facturas distribuidas, Bancos, Cartolas | Historial financiero, conciliación |
| Transporte | Comercial, Producción, Trabajador-transporte | Pagos transportista, Proformas, Informes |
| Informes | Producción, Pagos, Clientes, Transporte | CSV/JSON/PDF de consulta |

---

## F. Huecos detectados durante la lectura

- `POST /reprocesar-pagos/` aparece en frontend pero no en `backend/contratista_test_app/urls.py:183-405`.
- `POST /confirmar-pago-transportista/` está en URLs pero la vista no implementa método (`views/transporte.py:562-564`).
- `PersonalTrabajadores` no muestra campos directos transportista/vehiculo/fundo/casa, aunque vistas/componentes los referencian; existe historial separado (`models/transporte.py:106-117`, `models/produccion.py:137-147`).
- `ProduccionTrabajador.calcular_monto_a_pagar` referencia `folio.valor_pago_trabajador`, pero `FolioComercial` no expone ese campo directo; el valor parece estar en `FolioComercialLabor`.
- Previred referencia `trabajador.afp.porcentaje_descuento`, pero el modelo `AFP` expone `porcentaje_cotizacion_individual`.
- `FacturaCompraEstadoAPIView` aparece duplicada en `views/sii.py`.
- `backend/bot/urls.py` define `consulta/`, pero el include raíz está comentado en `backend/contratista_test/urls.py:28`.
- `mother-layout.component.ts` conserva rutas de navegación no verificadas en `app.routes.ts` (`/administrar-trabajadores`, `/fs/descargar-facturas` y otras).
- `JwtService` frontend contiene mapa de rutas incompleto respecto de `app.routes.ts`.

---

**Cierre:** aprox. 90 archivos leídos entre `frontend/src` y `backend`. Módulos cubiertos: todos los operativos listados. Módulos pendientes: 0.