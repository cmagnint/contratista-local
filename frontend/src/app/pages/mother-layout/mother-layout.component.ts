import { Component, Inject, OnInit, PLATFORM_ID, ViewChild, HostListener } from '@angular/core';
import { MatSidenav } from '@angular/material/sidenav';
import { isPlatformBrowser, CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { ContratistaApiService } from '../../services/contratista-api.service';
import { ReactiveFormsModule } from '@angular/forms';
import { MatIconModule } from '@angular/material/icon';
import { MatDrawer } from '@angular/material/sidenav';
import { MatDrawerContainer } from '@angular/material/sidenav';
import { MatDrawerContent } from '@angular/material/sidenav';
import { RouterModule } from '@angular/router';
import { JwtService } from '../../services/jwt.service';
import { SociedadGlobalService } from '../../services/sociedad-global.service';


@Component({
  selector: 'app-mother-layout',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatIconModule,
    MatDrawer,
    MatDrawerContainer,
    MatDrawerContent,
    RouterModule,
  ],
  templateUrl: './mother-layout.component.html',
  styleUrl: './mother-layout.component.css'
})
export class MotherLayoutComponent implements OnInit {
  @ViewChild('leftSidenav') leftSidenav!: MatSidenav;
  @ViewChild('rightSidenav') rightSidenav!: MatSidenav;

  mostrarBotonAdministrarPerfiles: boolean = true;

  constructor(
    private router: Router,
    private jwtService: JwtService,
    private sociedadGlobalService: SociedadGlobalService,
    @Inject(PLATFORM_ID) private platformId: Object,
    private apiService: ContratistaApiService
  ) {}


  public modulos: {[key:string]:boolean} = {
    'administrar_perfiles': true,
    'administrar_usuarios': true,
    'administrar_clientes': true,
    'administrar_trabajadores': true,
    'administrar_transportes': true,
    'administrar_area_cargos': true,
  };

  public modals: { [key: string]: boolean } = {
    seleccionInicial: false,
    sociedadesModal: false,
    sucursalesModal: false,
  };

  // Nueva variable
sociedadesDisponibles: Array<{ id: number; nombre: string }> = [];
sociedadActual: { id: number; nombre: string } | null = null;
dropdownSociedadGlobal: boolean = false;
  
  public oneSociedadSected: boolean = false;
  public oneCampoSelected: boolean = false;
  public modulosArray: any[] = [];
  public is_admin:boolean = false;
  public nombre_user: string | null = null;
  public nombre_holding: string | null = null;
  public holding: string | null = null;
  public todasSeleccionadas: boolean = false;
  public sucursalesCargadas: any[] = [];
  selectedSucursales: any[] = [];
  public submodulosWeb: any;
  public selectedSociedadId: number | null = null;
  public selectedSociedadName: string | null = null;
  public selectedSucursalId: number | null = null;
  public selectedSucursalName: string | null = null;
  
  // Variables para sociedades del usuario
  public sociedadesUsuario: any[] = [];
  public usuario_id: number | null = null;
  
  // Variables para la sociedad de trabajo actual
  public sociedadTrabajoActual: any = null;
  public dropdownOpenSociedadTrabajo: boolean = false;

  // ============================================
  // ✅ MÉTODOS PARA OBTENER DATOS DESDE JWT
  // REEMPLAZANDO COMPLETAMENTE LOCALSTORAGE
  // ============================================

  /**
   * ✅ OBTENER NOMBRE USUARIO desde JWT
   */
  private getNombreUsuarioFromJWT(): string {
    try {
      if (!isPlatformBrowser(this.platformId)) {
        return '';
      }

      const userInfo = this.jwtService.getUserInfo();
      const nombre = userInfo?.nombre;
      
      
      return nombre || '';
    } catch (error) {
      return '';
    }
  }

  

  /**
   * ✅ OBTENER USER ID desde JWT
   */
  private getUserIdFromJWT(): number | null {
    try {
      if (!isPlatformBrowser(this.platformId)) {
        return null;
      }

      const userInfo = this.jwtService.getUserInfo();
      const userId = userInfo?.user_id;
      
      
      return userId || null;
    } catch (error) {
      return null;
    }
  }

  /**
   * ✅ OBTENER HOLDING ID desde JWT (ya existía, mejorado)
   */
  private getHoldingIdFromJWT(): string {
    try {
      if (!isPlatformBrowser(this.platformId)) {
        return '';
      }

      const userInfo = this.jwtService.getUserInfo();
      const holdingId = userInfo?.holding_id;
      
      
      if (holdingId && holdingId !== null) {
        return holdingId.toString();
      } else {
        return '';
      }
    } catch (error) {
      return '';
    }
  }

  /**
   * ✅ VERIFICAR SI ES ADMIN desde JWT
   */
  private getIsAdminFromJWT(): boolean {
    try {
      if (!isPlatformBrowser(this.platformId)) {
        return false;
      }

      const payload = this.jwtService.decodeToken();
      const isAdmin = payload?.is_admin || payload?.user_type === 'ADMIN_HOLDING';
      
      
      return isAdmin || false;
    } catch (error) {
      return false;
    }
  }

  /**
   * ✅ OBTENER TODA LA INFORMACIÓN DEL USUARIO desde JWT
   */
  private initializeUserDataFromJWT(): void {
    if (!isPlatformBrowser(this.platformId)) {
      return;
    }

    try {
      // ✅ REEMPLAZAR LOCALSTORAGE CON JWT
      this.nombre_user = this.getNombreUsuarioFromJWT();
      this.nombre_holding = this.getNombreHoldingFromJWT(); // ✅ AGREGAR ESTA LÍNEA
      this.holding = this.getHoldingIdFromJWT();
      this.usuario_id = this.getUserIdFromJWT();
      this.is_admin = this.getIsAdminFromJWT();
      
    } catch (error) {
      
    }
  }

  /**
 * ✅ OBTENER NOMBRE HOLDING desde JWT
 */
private getNombreHoldingFromJWT(): string {
  try {
    if (!isPlatformBrowser(this.platformId)) {
      return '';
    }

    const userInfo = this.jwtService.getUserInfo();
    const nombreHolding = userInfo?.nombre_holding;
    console.log('el nombre del holding es: ', nombreHolding)
    return nombreHolding || '';
  } catch (error) {
    return '';
  }
}

  

  /**
   * ✅ VERIFICAR SI HAY DATOS VÁLIDOS
   */
  private hasValidUserData(): boolean {
    return !!(this.nombre_user && this.holding && this.usuario_id);
  }

  /**
   * ✅ SYNC CON LOCALSTORAGE: Solo para compatibilidad con código legacy
   */
  private syncWithLocalStorage(): void {
    try {
      // Solo sincronizar si tenemos datos válidos del JWT
      if (this.hasValidUserData()) {
        
        localStorage.setItem('nombre_user', this.nombre_user || '');
        localStorage.setItem('nombre_holding', this.nombre_holding || '');
        localStorage.setItem('holding_id', this.holding || '');
        localStorage.setItem('usuario_id', this.usuario_id?.toString() || '');
        localStorage.setItem('is_admin', this.is_admin.toString());
        
      }
    } catch (error) {
    }
  }

  ngOnInit(): void {
    if (isPlatformBrowser(this.platformId)) {
      
      // ✅ CARGAR DATOS DESDE JWT (reemplazando localStorage)
      this.initializeUserDataFromJWT();
      
      // ✅ Verificar que tenemos datos válidos
      if (!this.hasValidUserData()) {
        // Opcional: redirigir al login si no hay datos válidos
        // this.router.navigate(['/login']);
        // return;
      }
      
      // ✅ Sincronizar con localStorage para compatibilidad con código legacy
      this.syncWithLocalStorage();
      
    
      
      // ✅ CARGAR SOCIEDADES DEL USUARIO
      if (this.usuario_id) {
        this.cargarSociedadesUsuario();
      } else {
      }
      
      // ✅ CARGAR SOCIEDAD DE TRABAJO ACTUAL
      const sociedadTrabajoGuardada = localStorage.getItem('sociedad_trabajo_actual');
      if (sociedadTrabajoGuardada) {
        try {
          this.sociedadTrabajoActual = JSON.parse(sociedadTrabajoGuardada);
        } catch (error) {
          localStorage.removeItem('sociedad_trabajo_actual');
        }
      }
      
      // ✅ NUEVO: Cargar sociedades disponibles desde localStorage para dropdown global
      const sociedadesStr = localStorage.getItem('sociedades');
      if (sociedadesStr) {
        this.sociedadesDisponibles = JSON.parse(sociedadesStr);
        
        // Cargar sociedad guardada o seleccionar la primera
        this.sociedadGlobalService.cargarSociedadGuardada();
        this.sociedadActual = this.sociedadGlobalService.getSociedad();
        
        // Si no hay sociedad seleccionada y hay disponibles, seleccionar la primera
        if (!this.sociedadActual && this.sociedadesDisponibles.length > 0) {
          this.seleccionarSociedad(this.sociedadesDisponibles[0]);
        }
      }
      
      // ✅ NUEVO: Suscribirse a cambios de sociedad global
      this.sociedadGlobalService.sociedadSeleccionada$.subscribe(sociedad => {
        this.sociedadActual = sociedad;
      });
      
      // ✅ CARGAR DATOS ADICIONALES
      this.cargarSubmodulosWeb(); // Mantener por compatibilidad legacy
      
      if (this.holding) {
        this.cargarSociedades();
      } else {
      }
      
    } else {
      // ✅ SSR: Solo log mínimo
    }
  }

  // ✅ NUEVO: Métodos para el dropdown
toggleDropdownSociedadGlobal(): void {
  this.dropdownSociedadGlobal = !this.dropdownSociedadGlobal;
}

seleccionarSociedad(sociedad: { id: number; nombre: string }): void {
  this.sociedadGlobalService.setSociedad(sociedad);
  this.dropdownSociedadGlobal = false;
}

   /**
   * 🎯 NUEVO MÉTODO: Extrae holding_id del JWT
   */


  cargarSociedadesUsuario(): void {
    if (this.usuario_id) {
      this.apiService.get(`api_sociedades_usuario/${this.usuario_id}/`).subscribe({
        next: (response) => {
          this.sociedadesUsuario = response.sociedades;
          
          // Si solo hay una sociedad, seleccionarla automáticamente
          if (this.sociedadesUsuario.length === 1) {
            this.seleccionarSociedadTrabajo(this.sociedadesUsuario[0]);
          }
          // Si no hay sociedad seleccionada pero hay sociedades disponibles
          else if (!this.sociedadTrabajoActual && this.sociedadesUsuario.length > 0) {
            // Verificar si la sociedad guardada sigue siendo válida
            const sociedadGuardada = localStorage.getItem('sociedad_trabajo_actual');
            if (sociedadGuardada) {
              const sociedad = JSON.parse(sociedadGuardada);
              const sociedadValida = this.sociedadesUsuario.find(s => s.id === sociedad.id);
              if (sociedadValida) {
                this.sociedadTrabajoActual = sociedadValida;
              } else {
                // Si la sociedad guardada ya no es válida, seleccionar la primera
                this.seleccionarSociedadTrabajo(this.sociedadesUsuario[0]);
              }
            } else {
              // Si no hay sociedad guardada, seleccionar la primera
              this.seleccionarSociedadTrabajo(this.sociedadesUsuario[0]);
            }
          }
        },
        error: (error) => {
        }
      });
    }
  }

  toggleDropdownSociedadTrabajo(): void {
    this.dropdownOpenSociedadTrabajo = !this.dropdownOpenSociedadTrabajo;
  }

  seleccionarSociedadTrabajo(sociedad: any): void {
    this.sociedadTrabajoActual = sociedad;
    localStorage.setItem('sociedad_trabajo_actual', JSON.stringify(sociedad));
    this.dropdownOpenSociedadTrabajo = false;
    
    // Opcional: Recargar datos relacionados con la sociedad seleccionada
    
    // Puedes emitir un evento o recargar componentes si es necesario
    // this.recargarDatosSociedad();
  }

  @HostListener('document:click', ['$event'])
  onDocumentClick(event: MouseEvent): void {
    const target = event.target as HTMLElement;
    if (!target.closest('.dropdown-sociedad-trabajo')) {
      this.dropdownOpenSociedadTrabajo = false;
    }
  }

  abrirMenuIzquierdo() {
    this.leftSidenav.toggle();
  }

  abrirMenuDerecho() {
    this.rightSidenav.toggle();
  }

  //========================================================
  //============== ADMINISTRACION ==========================
  //========================================================

  navigateToAdministrarSociedad() {
    this.router.navigate(['/fs/admin-sociedad']);
    this.leftSidenav.close();
  }

  navigateToAdministrarPerfiles() {
    this.router.navigate(['/fs/administrar-perfiles']);
    this.leftSidenav.close();
  } 

  navigateToAdministrarPersonal() {
    this.router.navigate(['/fs/personal-empresas']);
    this.leftSidenav.close();
  }

  navigateToAdministrarUsuarios() {
    this.router.navigate(['/fs/administrar-usuarios']);
    this.leftSidenav.close();
  }

  navigateToAdministrarClientes() {
    this.router.navigate(['/fs/administrar-clientes']);
    this.leftSidenav.close();
  }

  navigateToAdministrarContactos() {
    this.router.navigate(['/fs/administrar-contactos-clientes']);
    this.leftSidenav.close();
  }

  navigateToAdministrarAreaCargos() {
    this.router.navigate(['/administrar-area-cargos']);
    this.leftSidenav.close();
  }

  navigateToAdministrarTransporte() {
    this.router.navigate(['/administrar-transportes']);
    this.leftSidenav.close();
  }

  navigateToAdministrarTrabajadores() {
    this.router.navigate(['/administrar-trabajadores']);
    this.leftSidenav.close();
  }

  navigateToPersonal() {
    this.router.navigate(['/administrar-trabajadores-personal']);
    this.leftSidenav.close();
  }

  navigateToAFPS() {
    this.router.navigate(['/fs/r-h-afp']);
    this.leftSidenav.close();
  }

  navigateToSaluds() {
    this.router.navigate(['/fs/r-h-salud']);
    this.leftSidenav.close();
  }

  navigateToCasas() {
    this.router.navigate(['/fs/r-h-casas']);
    this.leftSidenav.close();
  }

  navigateToHorario() {
    this.router.navigate(['/fs/r-h-horarios']);
    this.leftSidenav.close();
  }

  navigateToAdministrarArea() {
    this.router.navigate(['/administrar-area']);
    this.leftSidenav.close();
  }

  navigateToAdministrarCargos() {
    this.router.navigate(['/fs/administrar-area-cargos-cliente']);
    this.leftSidenav.close();
  }

  navigateToAdministrarAreaCargosAdmin() {
    this.router.navigate(['/fs/areas-cargos-administracion']);
    this.leftSidenav.close();
  }

  navigateToChoferes() {
    this.router.navigate(['/fs/choferes-transporte']);
    this.leftSidenav.close();
  }

  navigateToTramos() {
    this.router.navigate(['/fs/tramos']);
    this.leftSidenav.close();
  }
  
  navigateToEmpresasTransporte() {
    this.router.navigate(['/fs/empresas-transporte']);
    this.leftSidenav.close();
  }

  navigateToVehiculos() {
    this.router.navigate(['/fs/vehiculos-transporte']);
    this.leftSidenav.close();
  }

  navigateToUnidadControlComercial() {
    this.router.navigate(['/fs/unidad-control-comercial']);
    this.leftSidenav.close();
  }

  navigateToLaboresComercial() {
    this.router.navigate(['/fs/labores-comercial']);
    this.leftSidenav.close();
  }

  navigateToFolioComercial() {
    this.router.navigate(['/fs/folio-comercial']);
    this.leftSidenav.close();
  }

  navigateToFolioTransporte() {
    this.router.navigate(['/fs/folio-transporte']);
    this.leftSidenav.close();
  }

  navigateToPagoTransporte() {
    this.router.navigate(['/fs/pagos-transporte']);
    this.leftSidenav.close();
  }

  navigateToProformaTransporte() {
    this.router.navigate(['/fs/proforma-transporte']);
    this.leftSidenav.close();
  }

  navigateToGenerarQR() {
    this.router.navigate(['/fs/generar-qr']);
    this.leftSidenav.close();
  }

  navigateToGenerarContratos() {
    this.router.navigate(['/fs/generar-contrato']);
    this.leftSidenav.close();
  }

  navigateToMaestroTrabajadores() {
    this.router.navigate(['/fs/maestro-trabajadores']);
    this.leftSidenav.close();
  }
  
  navigateToEnrolamiento() {
    this.router.navigate(['/fs/enrolamiento']);
    this.leftSidenav.close();
  }
  
  navigateToAutoRegistro() {
    this.router.navigate(['/fs/autoregistro-personal']);
    this.leftSidenav.close();
  }

  navigateToFormatos() {
    this.router.navigate(['/fs/formatos']);
    this.leftSidenav.close();
  }

  navigateToLRE() {
    this.router.navigate(['/fs/lre']);
    this.leftSidenav.close();
  }

  navigateToDescargarFacturas() {
    this.router.navigate(['/fs/descargar-facturas']);
    this.leftSidenav.close();
  }

  navigateToFacturasCompraAutomatizado() {
    this.router.navigate(['/fs/facturas-compra-automatizado']);
    this.leftSidenav.close();
  }

  navigateToFacturasVentaAutomatizado() {
    this.router.navigate(['/fs/facturas-venta-automatizado']);
    this.leftSidenav.close();
  }

  navigateToParametrosFacturaVenta() {
    this.router.navigate(['/fs/parametros-factura-venta']);
    this.leftSidenav.close();
  }

  navigateToFacturasCompraDistribuidas() {
    this.router.navigate(['/fs/facturas-compra-distribuidas']);
    this.leftSidenav.close();
  }

  navigateToFacturasVentaDistribuidas() {
    this.router.navigate(['/fs/facturas-venta-distribuidas']);
    this.leftSidenav.close();
  }

  navigateToCuentas() {
    this.router.navigate(['/fs/cuentas']);
    this.leftSidenav.close();
  }

  navigateToParametrosFacturaCompra(){
    this.router.navigate(['/fs/parametros-factura-compra']);
    this.leftSidenav.close();
  }

  

  // RUTAS DE PAGO

  navigateToTxtBanco() {
    this.router.navigate(['/fs/txt-banco']);
    this.leftSidenav.close();
  }

  navigateToPagoTransferencia() {
    this.router.navigate(['/fs/pago-transf']);
    this.leftSidenav.close();
  }

  navigateToTransferenciaRealizada() {
    this.router.navigate(['/fs/transf-rlzda']);
    this.leftSidenav.close();
  }

  navigateToPagoEfectivo() {
    this.router.navigate(['/fs/pago-efect']);
    this.leftSidenav.close();
  }

  navigateToReprocesar() {
    this.router.navigate(['/fs/reprcs-pago']);
    this.leftSidenav.close();
  }

  // RUTAS DE INFORMES
  navigateToInformeRendimiento() {
    this.router.navigate(['/fs/informe-rendimiento']);
    this.leftSidenav.close();
  }

  navigateToInformePago() {
    this.router.navigate(['/fs/informe-pago']);
    this.leftSidenav.close();
  }

  navigateToInformeTransportista() {
    this.router.navigate(['/fs/informe-transportista']);
    this.leftSidenav.close();
  }
  
  //LEYES SOCIALES RUTA
  navigateToInformeDiasTrabajados() {
    this.router.navigate(['/fs/informe-dias-trab']);
    this.leftSidenav.close();
  }

  navigateToHaberesDescuentos() {
    this.router.navigate(['/fs/haberes-descuentos']);
    this.leftSidenav.close();
  }

  navigateToArchivoPrevired() {
    this.router.navigate(['/fs/arch-previred']);
    this.leftSidenav.close();
  }

  navigateToLiquidaciones() {
    this.router.navigate(['/fs/liquidaciones']);
    this.leftSidenav.close();
  }

  navigateToAsignacionHaberes() {
    this.router.navigate(['/fs/asignacion-haberes']);
    this.leftSidenav.close();
  }

  navigateToAsignacionDescuentos() {
    this.router.navigate(['/fs/asignacion-descuentos']);
    this.leftSidenav.close();
  }

  // RUTAS TESORERIA

  navigateToPagosIngresos(){
    this.router.navigate(['/fs/pagos-ingresos']);
    this.leftSidenav.close();
  }

  navigateToPagosIngresosEgresos(){
    this.router.navigate(['/fs/pagos-egresos']);
    this.leftSidenav.close();
  }


  navigateToHistorialPagos(){
    this.router.navigate(['/fs/historial-pagos']);
    this.leftSidenav.close();
  }

  navigateToTraspasoTrabajadores(){
    this.router.navigate(['/fs/traspaso-trabajadores']);
    this.leftSidenav.close();
  }

  

  //======================================================================================================
  
  cargarSubmodulosWeb() {
    const submodulosWebString = localStorage.getItem('submodulos_web');
    if (submodulosWebString) {
      this.submodulosWeb = JSON.parse(submodulosWebString);

    }
  }

  tieneSubmodulo(modulo: string, submodulo: string): boolean {
    if (this.submodulosWeb && this.submodulosWeb[modulo]) {
      return this.submodulosWeb[modulo].some((sub: any) => sub.nombre === submodulo);
    }
    return false;
  }

  dropdownOpenSociedad: boolean = false;
  toggleDropdownSociedad() {
    this.dropdownOpenSociedad = !this.dropdownOpenSociedad;
  }

  dropdownOpenSucursal: boolean = false;
  toggleDropdownSucursal() {
    this.dropdownOpenSucursal = !this.dropdownOpenSucursal;
  }

  public sociedadesCargadas: any[] = [];
  public selectedSociedad: any[] = [];

  cargarSociedades(): void {
    this.apiService.get(`api_sociedad/?holding=${this.holding}`).subscribe({
      next: (response) => {
        if (response.length > 0) {
          this.sociedadesCargadas = response.map((sociedad: any) => ({
            id: sociedad.id,
            name: sociedad.nombre
          }));
        } else {
          console.log('No se encontraron sociedades');
        }
      },
      error: (error) => {
        console.error('Error al recibir las sociedades:', error);
      }
    });
  }

  toggleSelectionSucursal(sucursalId: number, sucursalName: string): void {
    if (this.selectedSucursalId === sucursalId) {
      this.selectedSucursalId = null;
    } else {
      this.selectedSucursalId = sucursalId;
      this.selectedSucursalName = sucursalName;
    }
  }

  toggleSelectionSociedades(sociedadId: number, sociedadName: string): void {
    if (this.selectedSociedadId === sociedadId) {
      this.selectedSociedadId = null;
    } else {
      this.selectedSociedadId = sociedadId;
      this.selectedSociedadName = sociedadName;
    }
  }

  saveSelection() {
    localStorage.setItem('sociedad_actual_name', this.selectedSociedadName!);
    localStorage.setItem('sociedad_actual_id', String(this.selectedSociedadId));
    localStorage.setItem('campo_actual_name', this.selectedSucursalName!);
    localStorage.setItem('campo_actual_id',String(this.selectedSucursalId));
    this.closeModal('seleccionInicial');
  }

  validateSelection() {
    this.errorSociedad = !this.selectedSociedadId;
    this.errorCampo = !this.selectedSucursalId;

    if (this.selectedSociedadId && this.selectedSucursalId) {
      this.saveSelection();
      location.reload();
    }
  }

  errorSociedad = false;
  errorCampo = false;

  openGroups: { [key: string]: boolean } = {};

  toggleGroup(group: string): void {
    this.openGroups[group] = !this.openGroups[group];
  }

  isGroupOpen(group: string): boolean {
    return this.openGroups[group];
  }

  openModal(key: string): void {
    this.modals[key] = true;
  }

  closeModal(key: string): void {
    this.modals[key] = false;
  }

  dropdownOpen: boolean = false;

  toggleDropdown() {
    this.dropdownOpen = !this.dropdownOpen;
  }

  confirmLogout(): void {
  
  try {
    // Limpiar todos los tokens JWT
    this.jwtService.clearTokens();
    
    
    // Redirigir al login
    this.router.navigate(['/login']);
    
    
  } catch (error) {
    // En caso de error, forzar redirección
    this.router.navigate(['/login']);
  }
}

  // ============================================
  // ✅ MÉTODOS JWT COMPATIBLES CON SSR
  // ============================================

  /**
   * ✅ VERIFICAR MÓDULO: Compatible con SSR
   * CORREGIDO: Admins y Superadmins tienen acceso total + SSR compatible
   */
  public puedeAccederModulo(nombreModulo: string): boolean {
    try {
      // ✅ SSR COMPATIBILITY: En servidor, permitir acceso para evitar layouts vacíos
      if (!isPlatformBrowser(this.platformId)) {
        return true; // Se verificará en browser
      }

      // ✅ BROWSER: Verificación real de permisos
      const payload = this.jwtService.decodeToken();
      if (!payload) {
        return false;
      }

      // ✅ SUPERADMINS: Acceso total al sistema
      if (payload.is_superuser) {
        return true;
      }

      // ✅ ADMINS: Acceso total a su holding
      if (payload.is_admin || payload.user_type === 'ADMIN_HOLDING') {
        return true;
      }

      // ✅ USUARIOS NORMALES: Verificar permisos específicos
      const tieneAcceso = this.jwtService.canAccessModule(nombreModulo, 'web');
      return tieneAcceso;

    } catch (error) {
      // En caso de error y estamos en browser, denegar acceso
      return !isPlatformBrowser(this.platformId);
    }
  }

  /**
   * ✅ VERIFICAR SUBMÓDULO: Compatible con SSR
   * CORREGIDO: Admins y Superadmins tienen acceso total + SSR compatible
   */
  public puedeAccederSubmodulo(nombreModulo: string, nombreSubmodulo: string): boolean {
    try {
      // ✅ SSR COMPATIBILITY: En servidor, permitir acceso para evitar layouts vacíos
      if (!isPlatformBrowser(this.platformId)) {
        return true; // Se verificará en browser
      }

      // ✅ BROWSER: Verificación real de permisos
      const payload = this.jwtService.decodeToken();
      if (!payload) {
        return false;
      }

      // ✅ SUPERADMINS: Acceso total al sistema
      if (payload.is_superuser) {
        return true;
      }

      // ✅ ADMINS: Acceso total a su holding
      if (payload.is_admin || payload.user_type === 'ADMIN_HOLDING') {
        return true;
      }

      // ✅ USUARIOS NORMALES: Verificar permisos específicos
      const tieneAcceso = this.jwtService.canAccessSubmodule(nombreModulo, nombreSubmodulo, 'web');
      return tieneAcceso;

    } catch (error) {
      // En caso de error y estamos en browser, denegar acceso
      return !isPlatformBrowser(this.platformId);
    }
  }

  /**
   * ✅ MÉTODO LEGACY ACTUALIZADO: Compatible con SSR
   */
  public tieneSubmoduloJWT(modulo: string, submodulo: string): boolean {
    return this.puedeAccederSubmodulo(modulo, submodulo);
  }

  /**
   * ✅ VERIFICAR SI ES ADMIN: Compatible con SSR
   */
  public esAdminOSuperadmin(): boolean {
    try {
      // ✅ SSR COMPATIBILITY: En servidor, devolver false
      if (!isPlatformBrowser(this.platformId)) {
        return false;
      }

      const payload = this.jwtService.decodeToken();
      if (!payload) return false;

      return payload.is_superuser || payload.is_admin || payload.user_type === 'ADMIN_HOLDING';
    } catch (error) {
      return false;
    }
  }

  /**
   * ✅ OBTENER TIPO USUARIO: Compatible con SSR
   */
  public obtenerTipoUsuario(): string {
    try {
      // ✅ SSR COMPATIBILITY: En servidor, devolver UNKNOWN
      if (!isPlatformBrowser(this.platformId)) {
        return 'SSR';
      }

      const payload = this.jwtService.decodeToken();
      if (!payload) return 'UNKNOWN';

      if (payload.is_superuser) return 'SUPERADMIN';
      if (payload.is_admin || payload.user_type === 'ADMIN_HOLDING') return 'ADMIN';
      return 'USER';
    } catch (error) {
      return 'ERROR';
    }
  }
}