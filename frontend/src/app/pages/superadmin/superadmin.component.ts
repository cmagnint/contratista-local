import { Component, OnInit, Inject, PLATFORM_ID } from '@angular/core';
import { ContratistaApiService } from '../../services/contratista-api.service';
import { JwtService } from '../../services/jwt.service';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
interface Holding {
  id: number;
  nombre: string;
  estado: boolean;
  expanded?: boolean;
}

interface Sociedad {
  id: number;
  holding: number;
  holding_nombre?: string;
  nombre: string;
  rol_sociedad: string;
  nombre_representante: string;
  rut_representante: string;
  comuna: string;
  ciudad: string;
  calle: string;
  estado: boolean;
  expanded?: boolean;
}

interface AdminPrincipal {
  id: number;
  holding: number;
  holding_nombre?: string;
  nombre: string;
  rut: string;
  email: string;
  estado: boolean;
}

@Component({
  selector: 'app-superadmin',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './superadmin.component.html',
  styleUrl: './superadmin.component.css'
})
export class SuperadminComponent implements OnInit {

  // ==================== ESTADO DEL MENÚ ====================
  sidebarOpen = false;
  activeSection: 'holdings' | 'sociedades' | 'administradores' | null = null;
  selectedHoldingId: number | null = null;

  // ==================== DATOS ====================
  holdings: Holding[] = [];
  sociedades: Sociedad[] = [];
  administradores: AdminPrincipal[] = [];

  // ==================== MODALES ====================
  modals = {
    createHolding: false,
    editHolding: false,
    createSociedad: false,
    editSociedad: false,
    createAdmin: false,
    editAdmin: false,
    confirmAction: false,
    success: false,
    error: false
  };

  // ==================== FORMULARIOS ====================
  holdingForm = {
    id: null as number | null,
    nombre: '',
    estado: true
  };

  sociedadForm = {
    id: null as number | null,
    holding: null as number | null,
    nombre: '',
    rol_sociedad: '',
    nombre_representante: '',
    rut_representante: '',
    comuna: '',
    ciudad: '',
    calle: '',
    estado: true
  };

  adminForm = {
    id: null as number | null,
    holding: null as number | null,
    nombre: '',
    rut: '',
    email: '',
    password: '',
    estado: true
  };

  // ==================== VARIABLES DE CONTROL ====================
  isLoading = false;
  errorMessage = '';
  successMessage = '';
  confirmAction: { type: string; item: any; message: string } | null = null;

  constructor(
    private contratistaApiService: ContratistaApiService,
    @Inject(PLATFORM_ID) private platformId: Object,
    private jwtService: JwtService,
    private router: Router
  ) {}

  ngOnInit(): void {
    if(isPlatformBrowser(this.platformId)){
      this.loadHoldings();
    }
  }

  // ==================== FUNCIONES DE MENÚ ====================
  toggleSidebar(): void {
    this.sidebarOpen = !this.sidebarOpen;
  }

  closeSidebar(): void {
    this.sidebarOpen = false;
  }

  setActiveSection(section: 'holdings' | 'sociedades' | 'administradores'): void {
    this.activeSection = section;
    this.selectedHoldingId = null;
    this.closeSidebar(); // Cerrar sidebar al seleccionar una opción
    
    // Cargar datos según la sección
    switch (section) {
      case 'holdings':
        this.loadHoldings();
        break;
      case 'sociedades':
        this.sociedades = [];
        break;
      case 'administradores':
        this.administradores = [];
        break;
    }
  }

  // ==================== GESTIÓN DE HOLDINGS ====================
  async loadHoldings(): Promise<void> {
    try {
      this.isLoading = true;
      const response = await this.contratistaApiService.get('api_holding/').toPromise();
      this.holdings = response.map((h: any) => ({
        ...h,
        estado: h.estado !== undefined ? h.estado : true,
        expanded: false
      }));
    } catch (error) {
      console.error('Error al cargar holdings:', error);
      this.showError('Error al cargar holdings');
    } finally {
      this.isLoading = false;
    }
  }

  toggleHoldingExpansion(holding: Holding): void {
    holding.expanded = !holding.expanded;
  }

  editHolding(holding: Holding): void {
    this.holdingForm = {
      id: holding.id,
      nombre: holding.nombre,
      estado: holding.estado
    };
    this.openModal('editHolding');
  }

  confirmToggleHolding(holding: Holding): void {
    const action = holding.estado ? 'desactivar' : 'activar';
    this.confirmAction = {
      type: 'toggleHolding',
      item: holding,
      message: `¿Está seguro que desea ${action} el holding "${holding.nombre}"?`
    };
    this.openModal('confirmAction');
  }

  async createHolding(): Promise<void> {
    if (!this.holdingForm.nombre.trim()) {
      this.showError('El nombre del holding es requerido');
      return;
    }

    try {
      this.isLoading = true;
      const data = { nombre: this.holdingForm.nombre.trim().toUpperCase() };
      const response = await this.contratistaApiService.post('api_holding/', data).toPromise();
      
      this.holdings.push({
        ...response,
        estado: true,
        expanded: false
      });

      this.showSuccess('Holding creado exitosamente');
      this.closeModal('createHolding');
      this.resetHoldingForm();
    } catch (error) {
      console.error('Error al crear holding:', error);
      this.showError('Error al crear holding');
    } finally {
      this.isLoading = false;
    }
  }

  async updateHolding(): Promise<void> {
    if (!this.holdingForm.id || !this.holdingForm.nombre.trim()) {
      this.showError('Datos incompletos para actualizar');
      return;
    }

    try {
      this.isLoading = true;
      const data = {
        id: this.holdingForm.id,
        nombre: this.holdingForm.nombre.trim().toUpperCase(),
        estado: this.holdingForm.estado
      };

      const response = await this.contratistaApiService.patch('api_holding/', data).toPromise();
      
      const index = this.holdings.findIndex(h => h.id === this.holdingForm.id);
      if (index !== -1) {
        this.holdings[index] = { ...response, expanded: false };
      }

      this.showSuccess('Holding actualizado exitosamente');
      this.closeModal('editHolding');
      this.resetHoldingForm();
    } catch (error) {
      console.error('Error al actualizar holding:', error);
      this.showError('Error al actualizar holding');
    } finally {
      this.isLoading = false;
    }
  }

  async toggleHoldingStatus(holding: Holding): Promise<void> {
    try {
      this.isLoading = true;
      const data = {
        id: holding.id,
        estado: !holding.estado
      };

      await this.contratistaApiService.patch('api_holding/', data).toPromise();
      holding.estado = !holding.estado;
      
      this.showSuccess(`Holding ${holding.estado ? 'activado' : 'desactivado'} exitosamente`);
    } catch (error) {
      console.error('Error al cambiar estado del holding:', error);
      this.showError('Error al cambiar estado del holding');
    } finally {
      this.isLoading = false;
    }
  }

  resetHoldingForm(): void {
    this.holdingForm = { id: null, nombre: '', estado: true };
  }

  // ==================== GESTIÓN DE SOCIEDADES ====================
  selectHoldingForSociedades(holdingId: number): void {
    this.selectedHoldingId = holdingId;
    this.loadSociedades(holdingId);
  }

  async loadSociedades(holdingId: number): Promise<void> {
    try {
      this.isLoading = true;
      const response = await this.contratistaApiService.get(`api_sociedad/?holding=${holdingId}`).toPromise();
      
      this.sociedades = response.map((s: any) => ({
        ...s,
        estado: s.estado !== undefined ? s.estado : true,
        expanded: false,
        holding_nombre: this.getHoldingName(s.holding)
      }));
    } catch (error) {
      console.error('Error al cargar sociedades:', error);
      this.showError('Error al cargar sociedades');
    } finally {
      this.isLoading = false;
    }
  }

  toggleSociedadExpansion(sociedad: Sociedad): void {
    sociedad.expanded = !sociedad.expanded;
  }

  editSociedad(sociedad: Sociedad): void {
    this.sociedadForm = {
      id: sociedad.id,
      holding: sociedad.holding,
      nombre: sociedad.nombre,
      rol_sociedad: this.formatRUTString(sociedad.rol_sociedad),
      nombre_representante: sociedad.nombre_representante,
      rut_representante: this.formatRUTString(sociedad.rut_representante),
      comuna: sociedad.comuna,
      ciudad: sociedad.ciudad,
      calle: sociedad.calle,
      estado: sociedad.estado
    };
    this.openModal('editSociedad');
  }

  confirmToggleSociedad(sociedad: Sociedad): void {
    const action = sociedad.estado ? 'desactivar' : 'activar';
    this.confirmAction = {
      type: 'toggleSociedad',
      item: sociedad,
      message: `¿Está seguro que desea ${action} la sociedad "${sociedad.nombre}"?`
    };
    this.openModal('confirmAction');
  }

  async createSociedad(): Promise<void> {
    if (!this.validateSociedadForm()) return;

    try {
      this.isLoading = true;
      const data = {
        holding: this.selectedHoldingId,
        nombre: this.sociedadForm.nombre.trim().toUpperCase(),
        rol_sociedad: this.sociedadForm.rol_sociedad.replace(/[^0-9kK]/g, ''),
        nombre_representante: this.sociedadForm.nombre_representante.trim().toUpperCase(),
        rut_representante: this.sociedadForm.rut_representante.replace(/[^0-9kK]/g, ''),
        comuna: this.sociedadForm.comuna.trim().toUpperCase(),
        ciudad: this.sociedadForm.ciudad.trim().toUpperCase(),
        calle: this.sociedadForm.calle.trim().toUpperCase()
      };

      const response = await this.contratistaApiService.post('api_sociedad/', data).toPromise();
      
      this.sociedades.push({
        ...response,
        estado: true,
        expanded: false,
        holding_nombre: this.getHoldingName(response.holding)
      });

      this.showSuccess('Sociedad creada exitosamente');
      this.closeModal('createSociedad');
      this.resetSociedadForm();
    } catch (error) {
      console.error('Error al crear sociedad:', error);
      this.showError('Error al crear sociedad');
    } finally {
      this.isLoading = false;
    }
  }

  async updateSociedad(): Promise<void> {
    if (!this.sociedadForm.id || !this.validateSociedadForm()) return;

    try {
      this.isLoading = true;
      const data = {
        id: this.sociedadForm.id,
        holding: this.sociedadForm.holding,
        nombre: this.sociedadForm.nombre.trim().toUpperCase(),
        rol_sociedad: this.sociedadForm.rol_sociedad.replace(/[^0-9kK]/g, ''),
        nombre_representante: this.sociedadForm.nombre_representante.trim().toUpperCase(),
        rut_representante: this.sociedadForm.rut_representante.replace(/[^0-9kK]/g, ''),
        comuna: this.sociedadForm.comuna.trim().toUpperCase(),
        ciudad: this.sociedadForm.ciudad.trim().toUpperCase(),
        calle: this.sociedadForm.calle.trim().toUpperCase(),
        estado: this.sociedadForm.estado
      };

      const response = await this.contratistaApiService.patch('api_sociedad/', data).toPromise();
      
      const index = this.sociedades.findIndex(s => s.id === this.sociedadForm.id);
      if (index !== -1) {
        this.sociedades[index] = {
          ...response,
          expanded: false,
          holding_nombre: this.getHoldingName(response.holding)
        };
      }

      this.showSuccess('Sociedad actualizada exitosamente');
      this.closeModal('editSociedad');
      this.resetSociedadForm();
    } catch (error) {
      console.error('Error al actualizar sociedad:', error);
      this.showError('Error al actualizar sociedad');
    } finally {
      this.isLoading = false;
    }
  }

  async toggleSociedadStatus(sociedad: Sociedad): Promise<void> {
    try {
      this.isLoading = true;
      const data = {
        id: sociedad.id,
        estado: !sociedad.estado
      };

      await this.contratistaApiService.patch('api_sociedad/', data).toPromise();
      sociedad.estado = !sociedad.estado;
      
      this.showSuccess(`Sociedad ${sociedad.estado ? 'activada' : 'desactivada'} exitosamente`);
    } catch (error) {
      console.error('Error al cambiar estado de la sociedad:', error);
      this.showError('Error al cambiar estado de la sociedad');
    } finally {
      this.isLoading = false;
    }
  }

  validateSociedadForm(): boolean {
    const form = this.sociedadForm;
    if (!form.nombre.trim() || !form.rol_sociedad.trim() || 
        !form.nombre_representante.trim() || !form.rut_representante.trim() ||
        !form.comuna.trim() || !form.ciudad.trim() || !form.calle.trim()) {
      this.showError('Todos los campos son requeridos');
      return false;
    }
    return true;
  }

  resetSociedadForm(): void {
    this.sociedadForm = {
      id: null,
      holding: null,
      nombre: '',
      rol_sociedad: '',
      nombre_representante: '',
      rut_representante: '',
      comuna: '',
      ciudad: '',
      calle: '',
      estado: true
    };
  }

  // ==================== GESTIÓN DE ADMINISTRADORES ====================
  selectHoldingForAdmins(holdingId: number): void {
    this.selectedHoldingId = holdingId;
    this.loadAdministradores(holdingId);
  }

  async loadAdministradores(holdingId: number): Promise<void> {
    try {
      this.isLoading = true;
      const response = await this.contratistaApiService.get('api_admin/').toPromise();
      
      console.log('Respuesta administradores:', response);
      console.log('Holding ID a filtrar:', holdingId, typeof holdingId);
      
      this.administradores = response
        .filter((admin: any) => {
          console.log('Admin holding:', admin.holding, typeof admin.holding);
          return Number(admin.holding) === Number(holdingId);
        })
        .map((admin: any) => ({
          ...admin,
          holding_nombre: this.getHoldingName(admin.holding),
          estado: admin.estado !== undefined ? admin.estado : true
        }));
        
      console.log('Administradores filtrados:', this.administradores);
    } catch (error) {
      console.error('Error al cargar administradores:', error);
      this.showError('Error al cargar administradores');
    } finally {
      this.isLoading = false;
    }
  }

  editAdmin(admin: AdminPrincipal): void {
    this.adminForm = {
      id: admin.id,
      holding: admin.holding,
      nombre: admin.nombre,
      rut: this.formatRUTString(admin.rut),
      email: admin.email,
      password: '',
      estado: admin.estado
    };
    this.openModal('editAdmin');
  }

  confirmToggleAdmin(admin: AdminPrincipal): void {
    const action = admin.estado ? 'desactivar' : 'activar';
    this.confirmAction = {
      type: 'toggleAdmin',
      item: admin,
      message: `¿Está seguro que desea ${action} el administrador "${admin.nombre}"?`
    };
    this.openModal('confirmAction');
  }

  async createAdmin(): Promise<void> {
    if (!this.validateAdminForm()) return;

    try {
      this.isLoading = true;
      const data = {
        holding: this.selectedHoldingId,
        nombre: this.adminForm.nombre.trim(),
        rut: this.adminForm.rut.replace(/[^0-9kK]/g, ''),
        email: this.adminForm.email.trim(),
        password: this.adminForm.password
      };

      const response = await this.contratistaApiService.post('api_admin/', data).toPromise();
      
      this.administradores.push({
        ...response,
        holding_nombre: this.getHoldingName(response.holding),
        estado: true
      });

      this.showSuccess('Administrador creado exitosamente');
      this.closeModal('createAdmin');
      this.resetAdminForm();
    } catch (error) {
      console.error('Error al crear administrador:', error);
      this.showError('Error al crear administrador');
    } finally {
      this.isLoading = false;
    }
  }

  async updateAdmin(): Promise<void> {
    if (!this.adminForm.id || !this.validateAdminForm(false)) return;

    try {
      this.isLoading = true;
      const data: any = {
        id: this.adminForm.id,
        nombre: this.adminForm.nombre.trim(),
        email: this.adminForm.email.trim(),
        estado: this.adminForm.estado
      };

      if (this.adminForm.password.trim()) {
        data.password = this.adminForm.password;
      }

      const response = await this.contratistaApiService.patch('api_admin/', data).toPromise();
      
      const index = this.administradores.findIndex(a => a.id === this.adminForm.id);
      if (index !== -1) {
        this.administradores[index] = {
          ...response,
          holding_nombre: this.getHoldingName(response.holding)
        };
      }

      this.showSuccess('Administrador actualizado exitosamente');
      this.closeModal('editAdmin');
      this.resetAdminForm();
    } catch (error) {
      console.error('Error al actualizar administrador:', error);
      this.showError('Error al actualizar administrador');
    } finally {
      this.isLoading = false;
    }
  }

  async toggleAdminStatus(admin: AdminPrincipal): Promise<void> {
    try {
      this.isLoading = true;
      const data = {
        id: admin.id,
        estado: !admin.estado
      };

      await this.contratistaApiService.patch('api_admin/', data).toPromise();
      admin.estado = !admin.estado;
      
      this.showSuccess(`Administrador ${admin.estado ? 'activado' : 'desactivado'} exitosamente`);
    } catch (error) {
      console.error('Error al cambiar estado del administrador:', error);
      this.showError('Error al cambiar estado del administrador');
    } finally {
      this.isLoading = false;
    }
  }

  validateAdminForm(checkPassword: boolean = true): boolean {
    const form = this.adminForm;
    if (!form.nombre.trim() || !form.rut.trim() || !form.email.trim()) {
      this.showError('Nombre, RUT y email son requeridos');
      return false;
    }
    if (checkPassword && !form.password.trim()) {
      this.showError('La contraseña es requerida');
      return false;
    }
    return true;
  }

  resetAdminForm(): void {
    this.adminForm = {
      id: null,
      holding: null,
      nombre: '',
      rut: '',
      email: '',
      password: '',
      estado: true
    };
  }

  // ==================== UTILIDADES ====================
  formatRUT(event: Event): void {
    const target = event.target as HTMLInputElement;
    if (!target) return;

    let rut = target.value.replace(/[^0-9kK]/g, '');
    if (rut.length > 1) {
      const parts = [];
      const verifier = rut.slice(-1);
      rut = rut.slice(0, -1);
      
      while (rut.length > 3) {
        parts.unshift(rut.slice(-3));
        rut = rut.slice(0, -3);
      }
      parts.unshift(rut);
      target.value = parts.join('.') + '-' + verifier;
    }
    
    if (target.value === '-') {
      target.value = '';
    }
  }

  formatRUTString(value: string): string {
    if (!value) return '';
    
    let rut = value.replace(/[^0-9kK]/g, '');
    if (rut.length > 1) {
      const parts = [];
      const verifier = rut.slice(-1);
      rut = rut.slice(0, -1);
      
      while (rut.length > 3) {
        parts.unshift(rut.slice(-3));
        rut = rut.slice(0, -3);
      }
      parts.unshift(rut);
      return parts.join('.') + '-' + verifier;
    }
    return rut;
  }

  getHoldingName(holdingId: number): string {
    const holding = this.holdings.find(h => h.id === holdingId);
    return holding ? holding.nombre : 'Holding no encontrado';
  }

  // ==================== GESTIÓN DE MODALES ====================
  openModal(key: string): void {
    this.modals[key as keyof typeof this.modals] = true;
  }

  closeModal(key: string): void {
    this.modals[key as keyof typeof this.modals] = false;
    
    if (key === 'confirmAction') {
      this.confirmAction = null;
    }
  }

  // ==================== MANEJO DE CONFIRMACIONES ====================
  async executeConfirmedAction(): Promise<void> {
  if (!this.confirmAction) return;

  const { type, item } = this.confirmAction;
  this.closeModal('confirmAction');

  switch (type) {
    case 'toggleHolding':
      await this.toggleHoldingStatus(item);
      break;
    case 'toggleSociedad':
      await this.toggleSociedadStatus(item);
      break;
    case 'toggleAdmin':
      await this.toggleAdminStatus(item);
      break;
    case 'logout':  // ⭐ CASO FALTANTE PARA LOGOUT
      this.doLogout();
      break;
    default:
      console.warn('Acción no reconocida:', type);
  }
}

  // ==================== MANEJO DE MENSAJES ====================
  showSuccess(message: string): void {
    this.successMessage = message;
    this.openModal('success');
    
    setTimeout(() => {
      this.closeModal('success');
      this.successMessage = '';
    }, 3000);
  }

  showError(message: string): void {
    this.errorMessage = message;
    this.openModal('error');
    
    setTimeout(() => {
      this.closeModal('error');
      this.errorMessage = '';
    }, 5000);
  }

  // ==================== LOGOUT ====================
  confirmLogout(): void {
    this.confirmAction = {
      type: 'logout',
      item: null,
      message: '¿Está seguro que desea cerrar la sesión?'
    };
    this.openModal('confirmAction');
  }

  doLogout(): void {
  try {
    console.log('🚪 Iniciando logout...');
    
    // Limpiar tokens
    this.jwtService.clearTokens();
    
    // Limpiar estado local del componente
    this.resetAllForms();
    this.activeSection = null;
    this.selectedHoldingId = null;
    
    // Cerrar sidebar si está abierto
    this.closeSidebar();
    
    console.log('✅ Logout exitoso, redirigiendo...');
    this.router.navigate(['/login']);
    
  } catch (error) {
    console.error('❌ Error durante logout:', error);
    // Incluso si hay error, intentar navegar al login
    this.router.navigate(['/login']);
  }
}

// ==================== MÉTODO AUXILIAR PARA LIMPIAR FORMULARIOS ====================
private resetAllForms(): void {
  this.resetHoldingForm();
  this.resetSociedadForm();
  this.resetAdminForm();
  
  // Limpiar arrays de datos
  this.holdings = [];
  this.sociedades = [];
  this.administradores = [];
}

  // ==================== HANDLERS DE FORMULARIOS ====================
  onCreateHolding(): void {
    this.createHolding();
  }

  onUpdateHolding(): void {
    this.updateHolding();
  }

  onCreateSociedad(): void {
    this.createSociedad();
  }

  onUpdateSociedad(): void {
    this.updateSociedad();
  }

  onCreateAdmin(): void {
    this.createAdmin();
  }

  onUpdateAdmin(): void {
    this.updateAdmin();
  }

  // ==================== GETTERS PARA TEMPLATES ====================
  get activeHoldings(): Holding[] {
    return this.holdings.filter(h => h.estado);
  }

  get selectedHolding(): Holding | null {
    return this.selectedHoldingId 
      ? this.holdings.find(h => h.id === this.selectedHoldingId) || null 
      : null;
  }

  get hasAdminForSelectedHolding(): boolean {
    return this.administradores.length > 0;
  }
}