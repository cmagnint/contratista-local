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

  constructor(private router: Router,
              private jwtService: JwtService,
              @Inject(PLATFORM_ID) private platformId: Object,
              private apiService: ContratistaApiService) {}

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
      
      console.log('👤 Nombre usuario desde JWT:', nombre);
      
      return nombre || '';
    } catch (error) {
      console.error('❌ Error obteniendo nombre de usuario del JWT:', error);
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
      
      console.log('🆔 User ID desde JWT:', userId);
      
      return userId || null;
    } catch (error) {
      console.error('❌ Error obteniendo user ID del JWT:', error);
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
      
      console.log('🔍 Holding ID desde JWT:', holdingId);
      
      if (holdingId && holdingId !== null) {
        return holdingId.toString();
      } else {
        console.warn('⚠️ Holding ID no encontrado en JWT o es null');
        return '';
      }
    } catch (error) {
      console.error('❌ Error extrayendo holding_id del JWT:', error);
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
      
      console.log('🔑 Is Admin desde JWT:', isAdmin);
      
      return isAdmin || false;
    } catch (error) {
      console.error('❌ Error obteniendo is_admin del JWT:', error);
      return false;
    }
  }

  /**
   * ✅ OBTENER TODA LA INFORMACIÓN DEL USUARIO desde JWT
   */
  private initializeUserDataFromJWT(): void {
    if (!isPlatformBrowser(this.platformId)) {
      console.log('🖥️ SSR: Saltando inicialización de datos JWT');
      return;
    }

    try {
      console.log('🔄 Inicializando datos del usuario desde JWT...');
      
      // ✅ REEMPLAZAR LOCALSTORAGE CON JWT
      this.nombre_user = this.getNombreUsuarioFromJWT();
      this.holding = this.getHoldingIdFromJWT();
      this.usuario_id = this.getUserIdFromJWT();
      this.is_admin = this.getIsAdminFromJWT();
      
      console.log('✅ Datos del usuario cargados desde JWT:', {
        nombre_user: this.nombre_user,
        nombre_holding: this.nombre_holding,
        holding: this.holding,
        usuario_id: this.usuario_id,
        is_admin: this.is_admin
      });
      
    } catch (error) {
      console.error('❌ Error inicializando datos del usuario desde JWT:', error);
      
      // ✅ FALLBACK: Si falla JWT, intentar localStorage como respaldo
      console.log('⚠️ Fallback: Intentando cargar desde localStorage...');
      this.initializeUserDataFromLocalStorage();
    }
  }

  /**
   * ✅ FALLBACK: Cargar desde localStorage solo si JWT falla
   */
  private initializeUserDataFromLocalStorage(): void {
    console.log('📦 Cargando datos desde localStorage (fallback)...');
    
    this.nombre_user = localStorage.getItem('nombre_user');
    this.nombre_holding = localStorage.getItem('nombre_holding');
    this.holding = localStorage.getItem('holding_id');
    
    const usuarioId = localStorage.getItem('usuario_id');
    this.usuario_id = usuarioId ? parseInt(usuarioId) : null;
    
    this.is_admin = localStorage.getItem('is_admin') === 'true';
    
    console.log('⚠️ Datos cargados desde localStorage:', {
      nombre_user: this.nombre_user,
      nombre_holding: this.nombre_holding,
      holding: this.holding,
      usuario_id: this.usuario_id,
      is_admin: this.is_admin
    });
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
        console.log('🔄 Sincronizando datos JWT con localStorage para compatibilidad...');
        
        localStorage.setItem('nombre_user', this.nombre_user || '');
        localStorage.setItem('nombre_holding', this.nombre_holding || '');
        localStorage.setItem('holding_id', this.holding || '');
        localStorage.setItem('usuario_id', this.usuario_id?.toString() || '');
        localStorage.setItem('is_admin', this.is_admin.toString());
        
        console.log('✅ Sincronización con localStorage completada');
      }
    } catch (error) {
      console.error('❌ Error sincronizando con localStorage:', error);
    }
  }

  ngOnInit(): void {
    if (isPlatformBrowser(this.platformId)) {
      console.log('🌐 Mother Layout: Inicializando en browser...');
      
      // ✅ CARGAR DATOS DESDE JWT (reemplazando localStorage)
      this.initializeUserDataFromJWT();
      
      // ✅ Verificar que tenemos datos válidos
      if (!this.hasValidUserData()) {
        console.warn('⚠️ No se pudieron cargar datos válidos del usuario');
        // Opcional: redirigir al login si no hay datos válidos
        // this.router.navigate(['/login']);
        // return;
      }
      
      // ✅ Sincronizar con localStorage para compatibilidad con código legacy
      this.syncWithLocalStorage();
      
      // ✅ DEBUG: Solo en browser, no en SSR
      console.log('🔍 Tipo de usuario detectado:', this.obtenerTipoUsuario());
      console.log('🔑 Es admin o superadmin:', this.esAdminOSuperadmin());
      
      // ✅ CARGAR SOCIEDADES DEL USUARIO
      if (this.usuario_id) {
        console.log('👥 Cargando sociedades para usuario:', this.usuario_id);
        this.cargarSociedadesUsuario();
      } else {
        console.warn('⚠️ No se pudo obtener usuario_id, no se cargarán sociedades');
      }
      
      // ✅ CARGAR SOCIEDAD DE TRABAJO ACTUAL
      const sociedadTrabajoGuardada = localStorage.getItem('sociedad_trabajo_actual');
      if (sociedadTrabajoGuardada) {
        try {
          this.sociedadTrabajoActual = JSON.parse(sociedadTrabajoGuardada);
          console.log('🏢 Sociedad de trabajo cargada:', this.sociedadTrabajoActual?.nombre);
        } catch (error) {
          console.error('❌ Error parseando sociedad de trabajo:', error);
          localStorage.removeItem('sociedad_trabajo_actual');
        }
      }
      
      // ✅ CARGAR DATOS ADICIONALES
      this.cargarSubmodulosWeb(); // Mantener por compatibilidad legacy
      
      if (this.holding) {
        console.log('🏢 Cargando sociedades para holding:', this.holding);
        this.cargarSociedades();
      } else {
        console.warn('⚠️ No se pudo obtener holding_id, no se cargarán sociedades');
      }
      
    } else {
      // ✅ SSR: Solo log mínimo
      console.log('🖥️ Mother Layout: Ejecutándose en servidor (SSR)');
    }
  }

   /**
   * 🎯 NUEVO MÉTODO: Extrae holding_id del JWT
   */


  cargarSociedadesUsuario(): void {
    if (this.usuario_id) {
      this.apiService.get(`api_sociedades_usuario/${this.usuario_id}/`).subscribe({
        next: (response) => {
          this.sociedadesUsuario = response.sociedades;
          console.log('Sociedades del usuario:', this.sociedadesUsuario);
          
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
          console.error('Error al cargar sociedades del usuario:', error);
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
    console.log('Sociedad de trabajo seleccionada:', sociedad);
    
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

  navigateToProduccion() {
    this.router.navigate(['/fs/produccion-trabajador']);
    this.leftSidenav.close();
  }

  navigateToAutoRegistro() {
    this.router.navigate(['/fs/autoregistro-personal']);
    this.leftSidenav.close();
  }

  navigateToPosVarContrato() {
    this.router.navigate(['/fs/pos-var-contrato']);
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

  //======================================================================================================
  
  cargarSubmodulosWeb() {
    const submodulosWebString = localStorage.getItem('submodulos_web');
    if (submodulosWebString) {
      this.submodulosWeb = JSON.parse(submodulosWebString);
      console.log(this.submodulosWeb)
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
  console.log('🚪 Logout desde mother layout...');
  
  try {
    // Limpiar todos los tokens JWT
    this.jwtService.clearTokens();
    
    console.log('✅ Tokens JWT eliminados');
    
    // Redirigir al login
    this.router.navigate(['/login']);
    
    console.log('✅ Redirección al login completada');
    
  } catch (error) {
    console.error('❌ Error durante logout:', error);
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
        console.log('❌ No se pudo decodificar el JWT');
        return false;
      }

      // ✅ SUPERADMINS: Acceso total al sistema
      if (payload.is_superuser) {
        console.log('👑 Usuario SUPERADMIN - Acceso total al módulo:', nombreModulo);
        return true;
      }

      // ✅ ADMINS: Acceso total a su holding
      if (payload.is_admin || payload.user_type === 'ADMIN_HOLDING') {
        console.log('🔑 Usuario ADMIN - Acceso total al módulo:', nombreModulo);
        return true;
      }

      // ✅ USUARIOS NORMALES: Verificar permisos específicos
      const tieneAcceso = this.jwtService.canAccessModule(nombreModulo, 'web');
      console.log(`👤 Usuario normal - Acceso al módulo '${nombreModulo}':`, tieneAcceso);
      return tieneAcceso;

    } catch (error) {
      console.error('❌ Error verificando acceso al módulo:', error);
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
        console.log('❌ No se pudo decodificar el JWT');
        return false;
      }

      // ✅ SUPERADMINS: Acceso total al sistema
      if (payload.is_superuser) {
        console.log(`👑 Usuario SUPERADMIN - Acceso total al submódulo: ${nombreModulo}/${nombreSubmodulo}`);
        return true;
      }

      // ✅ ADMINS: Acceso total a su holding
      if (payload.is_admin || payload.user_type === 'ADMIN_HOLDING') {
        console.log(`🔑 Usuario ADMIN - Acceso total al submódulo: ${nombreModulo}/${nombreSubmodulo}`);
        return true;
      }

      // ✅ USUARIOS NORMALES: Verificar permisos específicos
      const tieneAcceso = this.jwtService.canAccessSubmodule(nombreModulo, nombreSubmodulo, 'web');
      console.log(`👤 Usuario normal - Acceso al submódulo '${nombreModulo}/${nombreSubmodulo}':`, tieneAcceso);
      return tieneAcceso;

    } catch (error) {
      console.error('❌ Error verificando acceso al submódulo:', error);
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
      console.error('❌ Error verificando si es admin:', error);
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
      console.error('❌ Error obteniendo tipo de usuario:', error);
      return 'ERROR';
    }
  }
}