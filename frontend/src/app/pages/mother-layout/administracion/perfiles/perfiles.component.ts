// src/app/pages/mother-layout/administracion/perfiles/perfiles.component.ts - VERSIÓN SIMPLIFICADA
import { Component, Inject, OnInit, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { ContratistaApiService } from '../../../../services/contratista-api.service';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { JwtService } from '../../../../services/jwt.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-perfiles',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatTableModule,
    MatSlideToggleModule
  ],
  templateUrl: './perfiles.component.html',
  styleUrl: './perfiles.component.css'
})
export class PerfilesComponent implements OnInit {
  
  // ✅ PERMISOS SIMPLES
  canCreatePerfiles = false;
  canEditPerfiles = false;
  canDeletePerfiles = false;
  isAdmin = false;

  // Variables existentes (sin cambios)
  public holding: string = '';
  public is_admin: string = '';
  public is_admin_bool: boolean = false;
  public perfiles: any[] = [];
  public modulos_web: any[] = [];
  public submodulos_web: any[] = [];
  public modulos_movil: any[] = [];
  public submodulos_movil: any[] = [];
  public selectedModulos: any[] = [];
  public selectedSubmodulos: any[] = [];
  public nombrePerfil: string = '';
  public tipoPerfil: string = 'WEB';
  public estado: boolean = true;
  public selectedRows: any[] = [];
  public errorMessage: string = '';
  public selectedModulosWeb: any[] = [];
  public selectedModulosMovil: any[] = [];
  public selectedSubmodulosWeb: number[] = [];
  public selectedSubmodulosMovil: number[] = [];
  public openDropdowns: { [key: string]: boolean } = {};
  
  private readonly RESTRICTED_NAME_PROFILES = ['SUPERVISOR', 'JEFE DE CUADRILLA', 'ADMINISTRADOR PRINCIPAL'];
  private readonly RESTRICTED_DELETE_PROFILES = ['SUPERVISOR', 'JEFE DE CUADRILLA', 'ADMINISTRADOR PRINCIPAL'];

  public modals: { [key: string]: boolean } = {
    crearPerfil: false,
    modificarPerfil: false,
    confirmacionModal: false,
    exitoModal: false,
    errorModal: false,
  };

  columnasDesplegadas = ['codigo_perfil', 'nombre_perfiles', 'tipo', 'modulos', 'estado'];
  
  public tipoOptions = [
    { value: 'WEB', label: 'Web' },
    { value: 'MOVIL', label: 'Móvil' },
    { value: 'AMBOS', label: 'Ambos' }
  ];

  constructor(
    private apiService: ContratistaApiService,
    private jwtService: JwtService,
    private router: Router,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {}

  ngOnInit(): void {
    if (!isPlatformBrowser(this.platformId)) {
      return;
    }

    console.log('🔍 PerfilesComponent: Iniciando...');

    // ✅ VERIFICACIÓN SIMPLE DE AUTENTICACIÓN
    if (!this.jwtService.isAuthenticated()) {
      console.log('❌ Usuario no autenticado, redirigiendo...');
      this.router.navigate(['/login']);
      return;
    }

    // ✅ VERIFICACIÓN SIMPLE DE PERMISOS
    if (!this.jwtService.canAccessSubmodule('ADMINISTRACION', 'PERFILES')) {
      console.log('❌ Sin acceso al submódulo PERFILES, redirigiendo...');
      this.router.navigate(['/fs/home']);
      return;
    }

    // ✅ ESTABLECER PERMISOS SIMPLES
    this.setUserPermissions();

    // ✅ INICIALIZAR COMPONENTE
    this.initializeComponent();
  }

  /**
   * ✅ ESTABLECER PERMISOS DEL USUARIO
   */
  private setUserPermissions(): void {
    const payload = this.jwtService.decodeToken();
    
    if (payload) {
      this.isAdmin = payload.is_admin || payload.is_superuser;
      
      // Puede ver perfiles si tiene acceso al submódulo
      const canViewPerfiles = this.jwtService.canAccessSubmodule('ADMINISTRACION', 'PERFILES');
      
      // Para crear/editar/eliminar, necesita ser admin
      this.canCreatePerfiles = canViewPerfiles && this.isAdmin;
      this.canEditPerfiles = canViewPerfiles && this.isAdmin;
      this.canDeletePerfiles = canViewPerfiles && this.isAdmin;

      console.log('🔑 Permisos establecidos:', {
        canView: canViewPerfiles,
        canCreate: this.canCreatePerfiles,
        canEdit: this.canEditPerfiles,
        canDelete: this.canDeletePerfiles,
        isAdmin: this.isAdmin
      });
    }
  }

  /**
   * ✅ INICIALIZACIÓN DEL COMPONENTE
   */
  private initializeComponent(): void {
    console.log('✅ PerfilesComponent: Inicializando componente...');
    
    // Obtener holding desde JWT
    this.holding = this.getHoldingIdFromJWT();
    
    // Compatibilidad con código legacy
    this.is_admin = this.isAdmin ? 'true' : 'false';
    this.is_admin_bool = this.isAdmin;
    
    // Cargar datos
    this.cargarPerfiles();
    this.cargarModulosWeb();
    this.cargarSubmodulosWeb();
    this.cargarModulosMovil();
    this.cargarSubmodulosMovil();

    console.log('✅ PerfilesComponent: Componente inicializado');
  }

  /**
   * ✅ MÉTODO ACTUALIZADO: Extrae holding_id del JWT
   */
  private getHoldingIdFromJWT(): string {
    try {
      const userInfo = this.jwtService.getUserInfo();
      const holdingId = userInfo?.holding_id;
      
      console.log('🔍 Holding ID del JWT:', holdingId);
      
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
   * ✅ MÉTODO CON VERIFICACIÓN SIMPLE: Agregar perfil
   */
  agregarPerfil(): void {
    console.log('🔧 Intentando crear perfil...');
    
    // ✅ Verificación simple
    if (!this.canCreatePerfiles) {
      console.log('❌ Sin permisos para crear perfiles');
      this.openErrorModal('No tiene permisos para crear perfiles');
      return;
    }

    if (!this.validarSeleccionModulos()) {
      return;
    }

    let data = {
      holding: parseInt(this.holding, 10),
      nombre_perfil: this.nombrePerfil,
      tipo: this.tipoPerfil,
      estado: this.estado,
      modulos_web: this.tipoPerfil !== 'MOVIL' ? this.selectedModulosWeb : [],
      submodulos_web: this.tipoPerfil !== 'MOVIL' ? this.selectedSubmodulosWeb : [],
      modulos_movil: this.tipoPerfil !== 'WEB' ? this.selectedModulosMovil : [],
      submodulos_movil: this.tipoPerfil !== 'WEB' ? this.selectedSubmodulosMovil : []
    };

    console.log('📤 Enviando data para crear perfil:', data);

    this.apiService.post(`api_perfil/${this.holding}/`, data).subscribe({
      next: (response) => {
        console.log('✅ Perfil creado exitosamente:', response);
        this.openSuccessModal();
        this.closeModal('crearPerfil');
        this.cargarPerfiles();
      },
      error: (error) => {
        console.error('❌ Error creando perfil:', error);
        this.openErrorModal('Error al crear perfil: ' + (error.error?.message || 'Ocurrió un error desconocido'));
      }
    });
  }

  /**
   * ✅ MÉTODO CON VERIFICACIÓN SIMPLE: Modificar perfil
   */
  modificarPerfil(): void {
    console.log('🔧 Intentando modificar perfil...');
    
    // ✅ Verificación simple
    if (!this.canEditPerfiles) {
      console.log('❌ Sin permisos para modificar perfiles');
      this.openErrorModal('No tiene permisos para modificar perfiles');
      return;
    }

    if (this.selectedRows.length !== 1) {
      this.openErrorModal('Seleccione un solo perfil para modificar');
      return;
    }

    if (!this.validarSeleccionModulos()) {
      return;
    }

    const perfilSeleccionado = this.selectedRows[0];
    
    let data: any = {
      id: perfilSeleccionado.id,
      tipo: this.tipoPerfil,
      estado: this.estado,
      modulos_web_ids: this.tipoPerfil !== 'MOVIL' ? this.selectedModulosWeb.filter(item => typeof item === 'number') : [],
      submodulos_web_ids: this.tipoPerfil !== 'MOVIL' ? this.selectedSubmodulosWeb.filter(item => typeof item === 'number') : [],
      modulos_movil_ids: this.tipoPerfil !== 'WEB' ? this.selectedModulosMovil.filter(item => typeof item === 'number') : [],
      submodulos_movil_ids: this.tipoPerfil !== 'WEB' ? this.selectedSubmodulosMovil.filter(item => typeof item === 'number') : []
    };

    if (!this.isRestrictedNameProfile(perfilSeleccionado)) {
      data.nombre_perfil = this.nombrePerfil;
    }

    console.log('📤 Enviando data para modificar perfil:', data);

    this.apiService.put(`api_perfil/${this.holding}/`, data).subscribe({
      next: () => {
        console.log('✅ Perfil modificado exitosamente');
        this.openSuccessModal();
        this.closeModal('modificarPerfil');
        this.cargarPerfiles();
      },
      error: (error) => {
        console.error('❌ Error modificando perfil:', error);
        this.openErrorModal('Error al modificar el perfil: ' + (error.error?.message || 'Ocurrió un error desconocido'));
      }
    });
  }

  /**
   * ✅ MÉTODO CON VERIFICACIÓN SIMPLE: Eliminar perfiles
   */
  eliminarPerfilesSeleccionados(): void {
    console.log('🗑️ Intentando eliminar perfiles...');
    
    // ✅ Verificación simple
    if (!this.canDeletePerfiles) {
      console.log('❌ Sin permisos para eliminar perfiles');
      this.openErrorModal('No tiene permisos para eliminar perfiles');
      return;
    }

    if (this.selectedRows.length === 0 || this.selectedRows.some(row => this.isAdminPrincipal(row))) {
      this.openErrorModal('No se pueden eliminar los perfiles seleccionados');
      return;
    }

    const idsToDelete = this.selectedRows.map(row => row.id);
    
    console.log('📤 Eliminando perfiles con IDs:', idsToDelete);

    this.apiService.delete(`api_perfil/${this.holding}/`, {ids: idsToDelete}).subscribe({
      next: () => {
        console.log('✅ Perfiles eliminados exitosamente');
        this.cargarPerfiles();
        this.openSuccessModal();
        this.selectedRows = [];
      },
      error: (error) => {
        console.error('❌ Error eliminando perfiles:', error);
        this.openErrorModal('Error al eliminar perfiles');
      }
    });
  }

  /**
   * ✅ MÉTODO CON VERIFICACIÓN SIMPLE: Toggle estado
   */
  toggleEstado(perfil: any): void {
    console.log('🔄 Intentando cambiar estado del perfil:', perfil.id);
    
    // ✅ Verificación simple
    if (!this.canEditPerfiles) {
      console.log('❌ Sin permisos para cambiar estado de perfiles');
      return; // No mostrar error, solo no hacer nada
    }

    if (this.isRestrictedNameProfile(perfil)) {
      return;
    }
    
    const data = {
      id: perfil.id,
      estado: !perfil.estado
    };
    
    this.apiService.put(`api_perfil/${this.holding}/`, data).subscribe({
      next: () => {
        console.log('✅ Estado cambiado exitosamente');
        this.cargarPerfiles();
      },
      error: (error) => {
        console.error('❌ Error cambiando estado:', error);
        this.openErrorModal('Error al cambiar el estado del perfil');
      }
    });
  }

  /**
   * ✅ MÉTODO ACTUALIZADO: Verificar si botón de eliminar debe estar deshabilitado
   */
  isDeleteButtonDisabled(): boolean {
    // ✅ Verificar permisos primero
    if (!this.canDeletePerfiles) {
      return true;
    }

    return this.selectedRows.length === 0 || 
           this.selectedRows.some(row => this.isAdminPrincipal(row)) ||
           this.selectedRows.some(row => this.isRestrictedDeleteProfile(row));
  }

  /**
   * ✅ MÉTODO ACTUALIZADO: Abrir modal con verificación simple
   */
  openModal(key: string): void {
    // ✅ Verificación simple según el tipo de modal
    if (key === 'crearPerfil' && !this.canCreatePerfiles) {
      this.openErrorModal('No tiene permisos para crear perfiles');
      return;
    }
    
    if (key === 'modificarPerfil' && !this.canEditPerfiles) {
      this.openErrorModal('No tiene permisos para modificar perfiles');
      return;
    }

    // ✅ TU CÓDIGO ORIGINAL SIN CAMBIOS
    this.modals[key] = true;
    if (key === 'crearPerfil') {
      this.resetForm();
    }
    if (key === 'modificarPerfil' && this.selectedRows.length === 1) {
      const perfilSeleccionado = this.selectedRows[0];
      console.log('Perfil seleccionado:', perfilSeleccionado);

      this.nombrePerfil = perfilSeleccionado.nombre_perfil;
      this.tipoPerfil = perfilSeleccionado.tipo;
      this.estado = perfilSeleccionado.estado;
      
      // Reiniciar las selecciones
      this.selectedModulosWeb = [];
      this.selectedModulosMovil = [];
      this.selectedSubmodulosWeb = [];
      this.selectedSubmodulosMovil = [];

      if (this.tipoPerfil === 'WEB' || this.tipoPerfil === 'AMBOS') {
        // Encontrar los IDs de los módulos web basados en sus nombres
        this.selectedModulosWeb = this.modulos_web
          .filter(modulo => perfilSeleccionado.modulos_web.includes(modulo.nombre))
          .map(modulo => modulo.id);

        // Encontrar los IDs de los submódulos web basados en sus nombres
        this.selectedSubmodulosWeb = this.submodulos_web
          .filter(submodulo => perfilSeleccionado.submodulos_web.includes(submodulo.nombre))
          .map(submodulo => submodulo.id);
        
        console.log('Módulos Web seleccionados:', this.selectedModulosWeb);
        console.log('Submódulos Web seleccionados:', this.selectedSubmodulosWeb);
      }

      if (this.tipoPerfil === 'MOVIL' || this.tipoPerfil === 'AMBOS') {
        // Encontrar los IDs de los módulos móvil basados en sus nombres
        this.selectedModulosMovil = this.modulos_movil
          .filter(modulo => perfilSeleccionado.modulos_movil.includes(modulo.nombre))
          .map(modulo => modulo.id);

        // Encontrar los IDs de los submódulos móvil basados en sus nombres
        this.selectedSubmodulosMovil = this.submodulos_movil
          .filter(submodulo => perfilSeleccionado.submodulos_movil.includes(submodulo.nombre))
          .map(submodulo => submodulo.id);
        
        console.log('Módulos Móvil seleccionados:', this.selectedModulosMovil);
        console.log('Submódulos Móvil seleccionados:', this.selectedSubmodulosMovil);
      }

      // Actualizar el estado de los dropdowns
      this.updateDropdownStates();
    }
  }

  /**
   * ✅ MÉTODO PARA DEBUG DE PERMISOS
   */
  debugPermisos(): void {
    if (!isPlatformBrowser(this.platformId)) {
      return;
    }

    console.log('=== 🔍 DEBUG PERMISOS PERFILES ===');
    
    const payload = this.jwtService.decodeToken();
    if (payload) {
      console.log('👤 Usuario:', payload.nombre_completo);
      console.log('🏢 Holding:', payload.holding_id);
      console.log('👑 Es Superuser:', payload.is_superuser);
      console.log('🔑 Es Admin:', payload.is_admin);
      console.log('📋 Perfil:', payload.perfil);
      
      console.log('--- PERMISOS WEB ---');
      const webPermissions = payload.permissions.web || {};
      Object.keys(webPermissions).forEach(modulo => {
        console.log(`📦 ${modulo}:`, webPermissions[modulo]);
      });
      
      console.log('--- VERIFICACIONES ESPECÍFICAS ---');
      console.log('¿Puede acceder a ADMINISTRACION?', this.jwtService.canAccessModule('ADMINISTRACION'));
      console.log('¿Puede acceder a PERFILES?', this.jwtService.canAccessSubmodule('ADMINISTRACION', 'PERFILES'));
      
      console.log('--- PERMISOS COMPONENTE ---');
      console.log('canCreatePerfiles:', this.canCreatePerfiles);
      console.log('canEditPerfiles:', this.canEditPerfiles);
      console.log('canDeletePerfiles:', this.canDeletePerfiles);
      console.log('isAdmin:', this.isAdmin);
    }
    
    console.log('=== 🔍 FIN DEBUG PERMISOS ===');
  }

  // ============================================
  // ✅ RESTO DE MÉTODOS SIN CAMBIOS
  // ============================================

  isRestrictedDeleteProfile(perfil: any): boolean {
    return this.RESTRICTED_DELETE_PROFILES.includes(perfil.nombre_perfil);
  }

  cargarPerfiles(): void {
    this.apiService.get(`api_perfil/${this.holding}/`).subscribe({
      next: (response) => {
        console.log('Perfiles recibidos:', response);
        this.perfiles = response;
      },
      error: (error) => {
        this.openErrorModal('Error al cargar perfiles: ' + error.error.message);
      }
    });
  }

  cargarModulosWeb(): void {
    this.apiService.get(`api_modulos_web/${this.holding}/`).subscribe({
      next: (response) => {
        this.modulos_web = response;
      },
      error: (error) => {
        console.error('Error al cargar módulos web:', error);
      }
    });
  }
  
  cargarSubmodulosWeb(): void {
    this.apiService.get(`api_submodulos_web/${this.holding}/`).subscribe({
      next: (response) => {
        this.submodulos_web = response;
        console.log('Submódulos Web cargados:', this.submodulos_web);
      },
      error: (error) => {
        console.error('Error al cargar submódulos web:', error);
      }
    });
  }

  cargarModulosMovil(): void {
    this.apiService.get(`api_modulos_movil/${this.holding}/`).subscribe({
      next: (response) => {
        this.modulos_movil = response;
      },
      error: (error) => {
        console.error('Error al cargar módulos móvil:', error);
      }
    });
  }

  cargarSubmodulosMovil(): void {
    this.apiService.get(`api_submodulos_movil/${this.holding}/`).subscribe({
      next: (response) => {
        this.submodulos_movil = response;
        console.log('Submódulos Móvil cargados:', this.submodulos_movil);
      },
      error: (error) => {
        console.error('Error al cargar submódulos móvil:', error);
      }
    });
  }

  validarSeleccionModulos(): boolean {
    if (this.tipoPerfil === 'AMBOS') {
      const tieneModulosWeb = this.selectedModulosWeb.length > 0 || this.selectedSubmodulosWeb.length > 0;
      const tieneModulosMovil = this.selectedModulosMovil.length > 0 || this.selectedSubmodulosMovil.length > 0;

      if (!tieneModulosWeb || !tieneModulosMovil) {
        const tipoFaltante = !tieneModulosWeb ? 'Web' : 'Móvil';
        this.openErrorModal(`Debe seleccionar al menos un módulo o submódulo ${tipoFaltante} cuando el tipo de perfil es 'Ambos'.`);
        return false;
      }
    }
    return true;
  }

  isAdminPrincipal(perfil: any): boolean {
    return perfil.nombre_perfil === 'ADMINISTRADOR PRINCIPAL';
  }

  isRestrictedNameProfile(perfil: any): boolean {
    return this.RESTRICTED_NAME_PROFILES.includes(perfil.nombre_perfil);
  }

  selectRow(row: any): void {
    if (this.isAdminPrincipal(row)) {
      return;
    }
    const index = this.selectedRows.findIndex(selectedRow => selectedRow.id === row.id);
    if (index > -1) {
      this.selectedRows.splice(index, 1);
    } else {
      this.selectedRows.push(row);
    }
  }

  isSelected(row: any): boolean {
    return !this.isAdminPrincipal(row) && this.selectedRows.some(r => r.id === row.id);
  }

  closeModal(key: string): void {
    this.modals[key] = false;
    if (key === 'exitoModal') {
      this.cargarPerfiles();
    }
  }

  openErrorModal(message: string): void {
    this.modals['errorModal'] = true;
    this.errorMessage = message;
  }

  openSuccessModal(): void {
    this.modals['exitoModal'] = true;
  }

  resetForm(): void {
    this.nombrePerfil = '';
    this.tipoPerfil = 'WEB';
    this.estado = true;
    this.selectedModulos = [];
    this.selectedSubmodulos = [];
  }

  onTipoPerfilChange(): void {
    this.selectedModulos = [];
    this.selectedSubmodulos = [];
  }

  isModuloSelected(moduloId: number, tipo: 'WEB' | 'MOVIL'): boolean {
    return tipo === 'WEB' 
      ? this.selectedModulosWeb.includes(moduloId)
      : this.selectedModulosMovil.includes(moduloId);
  }

  toggleDropdown(moduloId: number, tipo: 'WEB' | 'MOVIL'): void {
    const key = `${tipo}_${moduloId}`;
    this.openDropdowns[key] = !this.openDropdowns[key];
  }

  isDropdownOpen(moduloId: number, tipo: 'WEB' | 'MOVIL'): boolean {
    const key = `${tipo}_${moduloId}`;
    return this.openDropdowns[key] || false;
  }
  
  getSubmodulos(moduloId: number, tipo: 'WEB' | 'MOVIL'): any[] {
    const submodulos = tipo === 'WEB' 
      ? this.submodulos_web.filter(sm => sm.modulo === moduloId)
      : this.submodulos_movil.filter(sm => sm.modulo === moduloId);

    console.log(`Submódulos para módulo ${moduloId} (${tipo}):`, submodulos);
    return submodulos;
  }
  
  toggleModuloSelection(moduloId: number, tipo: 'WEB' | 'MOVIL'): void {
    const selectedModulos = tipo === 'WEB' ? this.selectedModulosWeb : this.selectedModulosMovil;
    const selectedSubmodulos = tipo === 'WEB' ? this.selectedSubmodulosWeb : this.selectedSubmodulosMovil;
    const index = selectedModulos.indexOf(moduloId);
    
    if (index > -1) {
      selectedModulos.splice(index, 1);
      // Deseleccionar todos los submódulos asociados
      const submodulos = this.getSubmodulos(moduloId, tipo);
      submodulos.forEach(sm => {
        const subIndex = selectedSubmodulos.indexOf(sm.id);
        if (subIndex > -1) {
          selectedSubmodulos.splice(subIndex, 1);
        }
      });
    } else {
      selectedModulos.push(moduloId);
      // Seleccionar todos los submódulos
      const submodulos = this.getSubmodulos(moduloId, tipo);
      submodulos.forEach(sm => {
        if (!selectedSubmodulos.includes(sm.id)) {
          selectedSubmodulos.push(sm.id);
        }
      });
    }

    if (tipo === 'WEB') {
      this.selectedModulosWeb = [...selectedModulos];
      this.selectedSubmodulosWeb = [...selectedSubmodulos];
    } else {
      this.selectedModulosMovil = [...selectedModulos];
      this.selectedSubmodulosMovil = [...selectedSubmodulos];
    }
    
    // Actualizar el estado del dropdown
    this.openDropdowns[`${tipo}_${moduloId}` as string] = selectedSubmodulos.length > 0;
  }
  
  toggleSubmoduloSelection(submoduloId: number, moduloId: number, tipo: 'WEB' | 'MOVIL'): void {
    const selectedModulos = tipo === 'WEB' ? this.selectedModulosWeb : this.selectedModulosMovil;
    const selectedSubmodulos = tipo === 'WEB' ? this.selectedSubmodulosWeb : this.selectedSubmodulosMovil;
    const index = selectedSubmodulos.indexOf(submoduloId);
    
    if (index > -1) {
      selectedSubmodulos.splice(index, 1);
    } else {
      selectedSubmodulos.push(submoduloId);
    }

    // Verificar si algún submódulo está seleccionado
    const submodulos = this.getSubmodulos(moduloId, tipo);
    const algunoSeleccionado = submodulos.some(sm => selectedSubmodulos.includes(sm.id));
    
    if (algunoSeleccionado) {
      if (!selectedModulos.includes(moduloId)) {
        selectedModulos.push(moduloId);
      }
    } else {
      const index = selectedModulos.indexOf(moduloId);
      if (index > -1) {
        selectedModulos.splice(index, 1);
      }
    }

    if (tipo === 'WEB') {
      this.selectedModulosWeb = [...selectedModulos];
      this.selectedSubmodulosWeb = [...selectedSubmodulos];
    } else {
      this.selectedModulosMovil = [...selectedModulos];
      this.selectedSubmodulosMovil = [...selectedSubmodulos];
    }
    
    // Actualizar el estado del dropdown
    this.openDropdowns[`${tipo}_${moduloId}` as string] = selectedSubmodulos.length > 0;
  }

  updateDropdownStates(): void {
    this.openDropdowns = {};
    
    if (this.tipoPerfil === 'WEB' || this.tipoPerfil === 'AMBOS') {
      this.selectedModulosWeb.forEach(moduloId => {
        this.openDropdowns[`WEB_${moduloId}`] = true;
      });
    }
    
    if (this.tipoPerfil === 'MOVIL' || this.tipoPerfil === 'AMBOS') {
      this.selectedModulosMovil.forEach(moduloId => {
        this.openDropdowns[`MOVIL_${moduloId}`] = true;
      });
    }

    console.log('Estado de los dropdowns:', this.openDropdowns);
  }

  getModulosDisplay(perfil: any): string {
    let display = '';

    const processModulos = (modulos: string[], submodulos: string[], tipo: 'WEB' | 'MOVIL') => {
      if (modulos.length === 0 && submodulos.length === 0) return;

      display += `${tipo}: [\n`;
      modulos.forEach(modulo => {
        const moduloSubmodulos = this.getSubmodulosForModulo(modulo, submodulos, tipo);
        display += `  ${modulo}: [${moduloSubmodulos.join(', ')}],\n`;
      });
      display += ']\n';
    };

    if (perfil.tipo === 'WEB' || perfil.tipo === 'AMBOS') {
      processModulos(perfil.modulos_web, perfil.submodulos_web, 'WEB');
    }
    
    if (perfil.tipo === 'MOVIL' || perfil.tipo === 'AMBOS') {
      if (perfil.tipo === 'AMBOS' && perfil.modulos_web.length > 0) display += '\n';
      processModulos(perfil.modulos_movil, perfil.submodulos_movil, 'MOVIL');
    }

    return display || 'No hay módulos disponibles';
  }
  
  getSubmodulosForModulo(modulo: string, submodulos: string[], tipo: 'WEB' | 'MOVIL'): string[] {
    const allSubmodulos = tipo === 'WEB' ? this.submodulos_web : this.submodulos_movil;
    const moduloObj = (tipo === 'WEB' ? this.modulos_web : this.modulos_movil).find(m => m.nombre === modulo);
    
    if (!moduloObj) return [];

    return submodulos.filter(submodulo => 
      allSubmodulos.some(sm => sm.nombre === submodulo && sm.modulo === moduloObj.id)
    );
  }
  
  actualizarVista(): void {
    if (this.selectedRows.length === 1) {
      const perfilSeleccionado = this.selectedRows[0];
      perfilSeleccionado.modulos_web = this.modulos_web
        .filter(modulo => this.selectedModulosWeb.includes(modulo.id))
        .map(modulo => modulo.nombre);
      perfilSeleccionado.submodulos_web = this.submodulos_web
        .filter(submodulo => this.selectedSubmodulosWeb.includes(submodulo.id))
        .map(submodulo => submodulo.nombre);
      perfilSeleccionado.modulos_movil = this.modulos_movil
        .filter(modulo => this.selectedModulosMovil.includes(modulo.id))
        .map(modulo => modulo.nombre);
      perfilSeleccionado.submodulos_movil = this.submodulos_movil
        .filter(submodulo => this.selectedSubmodulosMovil.includes(submodulo.id))
        .map(submodulo => submodulo.nombre);
      
      // Forzar la actualización de la vista
      this.perfiles = [...this.perfiles];
    }
  }

  getSubmoduloIdByNombre(nombre: string, tipo: string): number | undefined {
    const submodulos = tipo === 'WEB' ? this.submodulos_web : this.submodulos_movil;
    const submodulo = submodulos.find(sm => sm.nombre === nombre);
    return submodulo ? submodulo.id : undefined;
  }
}