import { Routes } from '@angular/router';
import { LoginComponent } from './pages/login/login.component';
import { SmartPreloadComponent } from './services/smart-preload.component';
import { MotherLayoutComponent } from './pages/mother-layout/mother-layout.component';
import { HomeComponent } from './pages/mother-layout/home/home.component';
import { SuperadminComponent } from './pages/superadmin/superadmin.component';
import { PersonalComponent } from './pages/mother-layout/administracion/personal/personal.component';
import { PerfilesComponent } from './pages/mother-layout/administracion/parametros/perfiles/perfiles.component';
import { contratistaAuthGuard } from './auth-guard/contratista-auth.guard';
import { UsuariosComponent } from './pages/mother-layout/administracion/usuarios/usuarios.component';
import { AreasCargosAdministracionComponent } from './pages/mother-layout/administracion/parametros/areas-cargos-administracion/areas-cargos-administracion.component';
import { AdministrarClientesComponent } from './pages/mother-layout/clientes/administrar-clientes/administrar-clientes.component';
import { AreasCargosClientesComponent } from './pages/mother-layout/clientes/parametros/areas-cargos-clientes/areas-cargos-clientes.component';
import { ContactosClientesComponent } from './pages/mother-layout/clientes/parametros/contactos-clientes/contactos-clientes.component';
import { FolioComercialComponent } from './pages/mother-layout/comercial/folio-comercial/folio-comercial.component';
import { EmpresasTransporteComponent } from './pages/mother-layout/transporte/administrar-transportes/empresas-transporte/empresas-transporte.component';
import { VehiculosTransporteComponent } from './pages/mother-layout/transporte/administrar-transportes/vehiculos-transporte/vehiculos-transporte.component';
import { ChoferesTransporteComponent } from './pages/mother-layout/transporte/administrar-transportes/choferes-transporte/choferes-transporte.component';
import { LaboresComercialComponent } from './pages/mother-layout/comercial/parametros/labores-comercial/labores-comercial.component';
import { UnidadControlComercialComponent } from './pages/mother-layout/comercial/parametros/unidad-control-comercial/unidad-control-comercial.component';
import { AfpComponent } from './pages/mother-layout/administracion/parametros/afp/afp.component';
import { SaludComponent } from './pages/mother-layout/administracion/parametros/salud/salud.component';
import { CasasComponent } from './pages/mother-layout/recursos-humanos/parametros/admin-casas/casas/casas.component';
import { HorariosComponent } from './pages/mother-layout/recursos-humanos/parametros/horarios/horarios.component';
import { GenerarQrComponent } from './pages/mother-layout/recursos-humanos/generar-qr/generar-qr.component';
import { AutoRegistroComponent } from './pages/mother-layout/recursos-humanos/auto-registro/auto-registro.component';
import { AutoRegistroLinkComponent } from './pages/mother-layout/recursos-humanos/auto-registro-link/auto-registro-link.component';
import { ApkLinkComponent } from './pages/mother-layout/recursos-humanos/apk-link/apk-link.component';
import { InformeRendimientoComponent } from './pages/mother-layout/informes/informe-rendimiento/informe-rendimiento.component';
import { InformePagoComponent } from './pages/mother-layout/informes/informe-pago/informe-pago.component';
import { SociedadComponent } from './pages/mother-layout/administracion/parametros/sociedad/sociedad.component';
import { PagoEfectivoComponent } from './pages/mother-layout/pagos/pago-efectivo/pago-efectivo.component';
import { PagoTransferenciaComponent } from './pages/mother-layout/pagos/pago-transferencia/pago-transferencia.component';
import { TransferenciasRealizadasComponent } from './pages/mother-layout/pagos/transferencias-realizadas/transferencias-realizadas.component';
import { ReprocesarPagoComponent } from './pages/mother-layout/pagos/reprocesar-pago/reprocesar-pago.component';
import { FolioTransportistaComponent } from './pages/mother-layout/transporte/folio-transportista/folio-transportista.component';
import { TramosComponent } from './pages/mother-layout/transporte/parametros/tramos/tramos.component';
import { PagosTransportistaComponent } from './pages/mother-layout/transporte/pagos-transportista/pagos-transportista.component';
import { InformeTransportistaComponent } from './pages/mother-layout/informes/informe-transportista/informe-transportista.component';
import { ProformasTransportistaComponent } from './pages/mother-layout/transporte/proformas-transportista/proformas-transportista.component';
import { InformeDiasTrabajadosComponent } from './pages/mother-layout/leyes-sociales/informe-dias-trabajados/informe-dias-trabajados.component';
import { HaberesDescuentosComponent } from './pages/mother-layout/leyes-sociales/haberes-descuentos/haberes-descuentos.component';
import { ArchivoPreviredComponent } from './pages/mother-layout/leyes-sociales/archivo-previred/archivo-previred.component';
import { LiquidacionesComponent } from './pages/mother-layout/leyes-sociales/liquidaciones/liquidaciones.component';
import { AsignacionHaberesComponent } from './pages/mother-layout/leyes-sociales/parametros/asignacion-haberes/asignacion-haberes.component';
import { AsignacionDescuentosComponent } from './pages/mother-layout/leyes-sociales/parametros/asignacion-descuentos/asignacion-descuentos.component';
import { LibroRemuneracionesElectronicoComponent } from './pages/mother-layout/leyes-sociales/libro-remuneraciones-electronico/libro-remuneraciones-electronico.component';
import { GenerarContratosComponent } from './pages/mother-layout/recursos-humanos/generacion-contratos/generar-contratos/generar-contratos.component';
import { CuentasComponent } from './pages/mother-layout/costos/cuentas/cuentas.component';
import { FacturasCompraAutomatizadaComponent } from './pages/mother-layout/costos/distribucion-automatizada/facturas-compra/facturas-compra-automatizada/facturas-compra-automatizada.component';
import { FacturasCompraDistribuidasComponent } from './pages/mother-layout/costos/distribucion-automatizada/facturas-compra/facturas-compra-distribuidas/facturas-compra-distribuidas.component';
import { ParametrosFacturasCompraComponent } from './pages/mother-layout/costos/distribucion-automatizada/facturas-compra/parametros-facturas-compra/parametros-facturas-compra.component';
import { FacturasVentaAutomatizadaComponent } from './pages/mother-layout/costos/distribucion-automatizada/facturas-venta/facturas-venta-automatizada/facturas-venta-automatizada.component';
import { ParametrosFacturasVentaComponent } from './pages/mother-layout/costos/distribucion-automatizada/facturas-venta/parametros-facturas-venta/parametros-facturas-venta.component';
import { FacturasVentaDistribuidasComponent } from './pages/mother-layout/costos/distribucion-automatizada/facturas-venta/facturas-venta-distribuidas/facturas-venta-distribuidas.component';
import { PagosIngresosComponent } from './pages/mother-layout/tesoreria/pagos-ingresos/pagos-ingresos.component';
import { PagosEgresosComponent } from './pages/mother-layout/tesoreria/pagos-egresos/pagos-egresos.component';
import { HistorialPagosComponent } from './pages/mother-layout/tesoreria/historial-pagos/historial-pagos.component';
import { ChangePasswordComponent } from './pages/change-password/change-password.component';
import { MaestroTrabajadoresComponent } from './pages/mother-layout/recursos-humanos/maestro-trabajadores/maestro-trabajadores.component';
import { FormatosComponent } from './pages/mother-layout/recursos-humanos/generacion-contratos/formatos/formatos.component';
import { GenerarTxtBancoComponent } from './pages/mother-layout/pagos/generar-txt-banco/generar-txt-banco.component';
import { EnrolamientoComponent } from './pages/mother-layout/recursos-humanos/enrolamiento/enrolamiento.component';
import { TraspasoTrabajadoresComponent } from './pages/mother-layout/recursos-humanos/traspaso-trabajadores/traspaso-trabajadores.component';
import { InformeCasasComponent } from './pages/mother-layout/recursos-humanos/parametros/admin-casas/informe-casas/informe-casas.component';

export const routes: Routes = [
  { path: '', component: SmartPreloadComponent, pathMatch: 'full' },
  { path: 'login', component: LoginComponent },
  { path: 'change-password', component: ChangePasswordComponent },
  { 
    path: 'super-admin', 
    component: SuperadminComponent, 
    canActivate: [contratistaAuthGuard] 
  },
  { 
    path: 'arl/:token/:id', 
    component: AutoRegistroLinkComponent,
  },
  {
    path: 'apk-link/:token/:id',
    component: ApkLinkComponent,
  },  
  { 
    path: 'fs',
    component: MotherLayoutComponent,
    canActivate: [contratistaAuthGuard],
    children: [
      //RUTAS ADMINISTRACION
      { path: '', redirectTo: 'home', pathMatch: 'full' },
      { path: 'home', component: HomeComponent },
      { path: 'personal-empresas', component: PersonalComponent },
      { path: 'administrar-perfiles', component: PerfilesComponent },
      { path: 'administrar-usuarios', component: UsuariosComponent },
      { path: 'areas-cargos-administracion', component: AreasCargosAdministracionComponent },
      { path: 'admin-sociedad', component: SociedadComponent },
      //RUTAS RECURSOS HUMANOS
      { path: 'maestro-trabajadores', component: MaestroTrabajadoresComponent },
      { path: 'r-h-afp', component: AfpComponent },
      { path: 'r-h-salud', component: SaludComponent },
      { path: 'r-h-casas', component: CasasComponent },
      { path: 'inf-casas', component: InformeCasasComponent },
      { path: 'r-h-horarios', component: HorariosComponent },
      { path: 'generar-qr', component: GenerarQrComponent },
      { path: 'autoregistro-personal', component: AutoRegistroComponent },
      { path: 'formatos', component: FormatosComponent },
      { path: 'generar-contrato',  component: GenerarContratosComponent },
      { path: 'enrolamiento', component: EnrolamientoComponent },
      { path: 'traspaso-trabajadores', component: TraspasoTrabajadoresComponent },
      // RUTAS DE CLIENTES
      { path: 'administrar-clientes', component: AdministrarClientesComponent },
      { path: 'administrar-area-cargos-cliente', component: AreasCargosClientesComponent },
      { path: 'administrar-contactos-clientes', component: ContactosClientesComponent },
      // RUTAS COMERCIAL
      { path: 'folio-comercial', component: FolioComercialComponent },
      { path: 'labores-comercial', component: LaboresComercialComponent },
      { path: 'unidad-control-comercial', component: UnidadControlComercialComponent },
      { path: 'lre', component: LibroRemuneracionesElectronicoComponent },
      //RUTAS TRANSPORTE
      { path: 'empresas-transporte', component: EmpresasTransporteComponent },
      { path: 'vehiculos-transporte', component: VehiculosTransporteComponent },
      { path: 'choferes-transporte', component: ChoferesTransporteComponent },
      { path: 'folio-transporte', component: FolioTransportistaComponent },
      { path: 'tramos', component: TramosComponent },
      { path: 'pagos-transporte', component: PagosTransportistaComponent },
      { path: 'proforma-transporte', component: ProformasTransportistaComponent },
      //RUTAS PAGO
      { path: 'pago-transf', component: PagoTransferenciaComponent },
      { path: 'pago-efect', component: PagoEfectivoComponent },
      { path: 'transf-rlzda', component: TransferenciasRealizadasComponent },
      { path: 'reprcs-pago', component: ReprocesarPagoComponent }, 
      { path: 'txt-banco', component: GenerarTxtBancoComponent },
      //RUTAS INFORMES
      { path: 'informe-rendimiento', component: InformeRendimientoComponent },
      { path: 'informe-pago', component: InformePagoComponent },
      { path: 'informe-transportista', component: InformeTransportistaComponent },
      //RUTAS LEYES SOCIALES
      { path: 'informe-dias-trab', component: InformeDiasTrabajadosComponent },
      { path: 'haberes-descuentos', component: HaberesDescuentosComponent },
      { path: 'arch-previred', component: ArchivoPreviredComponent },
      { path: 'liquidaciones', component: LiquidacionesComponent },
      { path: 'asignacion-haberes', component:  AsignacionHaberesComponent },
      { path: 'asignacion-descuentos', component: AsignacionDescuentosComponent },
      //RUTAS COSTOS
      { path: 'cuentas', component: CuentasComponent },
      { path: 'facturas-compra-automatizado', component: FacturasCompraAutomatizadaComponent },
      { path: 'facturas-compra-distribuidas', component: FacturasCompraDistribuidasComponent },
      { path: 'facturas-venta-distribuidas', component: FacturasVentaDistribuidasComponent },
      { path: 'parametros-factura-compra', component: ParametrosFacturasCompraComponent },
      { path: 'parametros-factura-venta', component: ParametrosFacturasVentaComponent },
      { path: 'facturas-venta-automatizado', component: FacturasVentaAutomatizadaComponent },
      //RUTAS TESORERIA
      { path: 'pagos-ingresos', component: PagosIngresosComponent },
      { path: 'pagos-egresos', component: PagosEgresosComponent },
      { path: 'historial-pagos', component: HistorialPagosComponent },
    ]
  },
  { path: '', redirectTo: '/login', pathMatch: 'full' },
  { path: '**', redirectTo: '/login' },
];