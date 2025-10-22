import { Component, Inject, OnInit, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser, CommonModule } from '@angular/common';
import { ContratistaApiService } from '../../../../services/contratista-api.service';
import { ReactiveFormsModule, FormsModule } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';
import { JwtService } from '../../../../services/jwt.service';

@Component({
  selector: 'app-usuarios',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatTableModule,
    FormsModule,
  ],
  templateUrl: './usuarios.component.html',
  styleUrl: './usuarios.component.css'
})
export class UsuariosComponent implements OnInit {
  // Booleanos para abrir o cerrar ventanas
  public modals: { [key: string]: boolean } = {
    exitoModal: false,
    errorModal: false,
    loadingModal: false,
    crearUsuario: false,
    modificarUsuario: false,
    confirmacionModal: false,
    seleccionInicial: false,
  };

  //Perfil seleccionado
  public usuarioSeleccionado: any = {
    nombre_usuario_seleccionado: '',
    rut_usuario_seleccionado: '',
    email_usuario_seleccionado: '',
    id_perfil_usuario_seleccionado: 0,
    id_usuario_seleccionado: 0,
  }

  public usuarioIdNew = 0;
  public personalDisponible: any[] = [];
  public selectedPersonalId: string = '';

  modulosDisponibles = [
    { id: 1, name: 'Administrar Perfiles' },
    { id: 2, name: 'Administrar Usuarios' },
    { id: 3, name: 'Administrar Clientes' },
    { id: 4, name: 'Admin. Trabajadores' },
    { id: 5, name: 'Administrar Transportes' },
    { id: 6, name: 'Administrar Area/Cargos' },
  ];

  public sociedadesCargadas: any[] = [];
  public supervisoresCargados: any[] = [];
  public selectedSociedades: any[] = [];
  public selectedSociedadesNew: any[] = [];
  public holding: string = '';
  public nombreUsuario: string = '';
  public rutUsuario: string = '';
  public emailUsuario: string = '';
  public errorMessage!: string;
  public selectedRows: any[] = [];
  
  public dropdownOpenPerfiles: boolean = false;
  public dropdownOpenSociedades: boolean = false;
  
  public todasSeleccionadas: boolean = false;
  public usuariosCargados: any[] = [];
  public columnasDesplegadas = ['codigo', 'perfil', 'sociedad', 'rut', 'nombre', 'email', 'estado'];
  public nombreUsuarioNew: string = '';
  public rutUsuarioNew: string = '';
  public emailUsuarioNew: string = '';
  public deletedRow: any[] = [];
  public sociedad_actual_id = 0;
  public sucursal_actual_id = 0;
  public perfilesCargados: any[] = [];
  public selectedPerfilId: number | null = null;
  public selectedUserId: number = 0;
  public selectedAllSucursales: boolean = false;
  public selectedAllSucursalesNew: boolean = false;
  public selectedSupervisorId: number | null = null;


  constructor(
    private apiService: ContratistaApiService,
    private jwtService: JwtService,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {}

  ngOnInit() {
    if (isPlatformBrowser(this.platformId)) {
      this.holding = this.getHoldingIdFromJWT();
      this.cargarSociedades();
      this.cargarPerfiles();
      this.cargarUsuarios();
      this.cargarSupervisores();
      this.cargarPersonalDisponible();
    }
  }

  private getHoldingIdFromJWT(): string {
    try {
      const userInfo = this.jwtService.getUserInfo();
      const holdingId = userInfo?.holding_id;
      
      console.log('🔍 Holding ID del JWT:', holdingId);
      
      if (holdingId && holdingId !== null ) {
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

  isJefeCuadrilla(): boolean {
    const selectedPerfil = this.perfilesCargados.find(p => p.id === this.selectedPerfilId);
    return selectedPerfil?.nombre_perfil === 'JEFE DE CUADRILLA';
  }

  cargarSupervisores():void{
    this.apiService.get(`api_supervisores/${this.holding}/`).subscribe({
      next: (response) => {
        this.supervisoresCargados = response;
        console.log('Supervisores cargados:', this.supervisoresCargados);
      },
      error: (error) => {
        console.log('No hay supervisores disponibles');
        this.supervisoresCargados = [];
      }
    })
  }

  cargarPersonalDisponible(): void {
    this.apiService.get(`api_personal_for_users/${this.holding}/`).subscribe({
        next: (response) => {
            this.personalDisponible = response;
            console.log('Personal disponible cargado:', this.personalDisponible);
        },
        error: (error) => {
            if (error.status === 404) {
                this.personalDisponible = [];
                console.log('No se encontró personal disponible, cargando lista vacía');
            } else {
                this.openErrorModal('Error al cargar personal: ' + error.error.message);
            }
        }
    });
  }

  onPersonalSelected(personalId: string | number): void {
    const id = typeof personalId === 'string' ? parseInt(personalId) : personalId;
    const personalSeleccionado = this.personalDisponible.find(p => p.id === id);
    
    if (personalSeleccionado) {
        this.nombreUsuario = personalSeleccionado.nombre_completo;
        this.rutUsuario = this.formatRUTString(personalSeleccionado.rut);
        this.emailUsuario = personalSeleccionado.correo || '';
        this.selectedPersonalId = personalId.toString();
        
        console.log('Personal seleccionado:', personalSeleccionado);
        console.log('Campos actualizados:', {
            nombre: this.nombreUsuario,
            rut: this.rutUsuario,
            email: this.emailUsuario
        });
    } else {
        this.nombreUsuario = '';
        this.rutUsuario = '';
        this.emailUsuario = '';
        this.selectedPersonalId = '';
    }
  }

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

  cargarPerfiles(): void {
    const url = `api_perfil/${this.holding}/`;
    this.apiService.get(url).subscribe({
      next: (response) => {
        this.perfilesCargados = response;
        if (response.length === 0) {
          this.selectedRows = [];
        }
      },
      error: (error) => {
        // Error silencioso
      }
    });
  }

  /**
   * 🧹 Limpia el RUT removiendo puntos y guiones
   */
  limpiarRUT(rut: string): string {
    if (!rut) return '';
    
    return rut
      .replace(/[.\-\s]/g, '')
      .toUpperCase()
      .trim();
  }

  /**
   * ✅ Crear usuario con RUT limpio
   */
  crearUsuario(): void {
    if (!this.selectedPersonalId) {
      this.openModal('errorModal');
      this.errorMessage = 'Por favor, seleccione una persona antes de crear el usuario.';
      return;
    }

    if (!this.nombreUsuario || !this.rutUsuario || !this.emailUsuario || !this.selectedPerfilId) {
      this.openModal('errorModal');
      this.errorMessage = 'Por favor, complete todos los campos antes de crear un usuario.';
      return;
    }

    const selectedPerfil = this.perfilesCargados.find(p => p.id === this.selectedPerfilId);
    if (selectedPerfil?.nombre_perfil === 'JEFE DE CUADRILLA' && !this.selectedSupervisorId) {
      this.openModal('errorModal');
      this.errorMessage = 'Debe seleccionar un supervisor para el Jefe de Cuadrilla.';
      return;
    }

    this.openModal('loadingModal');

    let data = {
      holding: this.holding,
      empresas_asignadas: this.selectedSociedades,
      persona: this.selectedPersonalId,
      nombre: this.nombreUsuario,
      rut: this.limpiarRUT(this.rutUsuario),
      email: this.emailUsuario,
      perfil: this.selectedPerfilId,
      supervisor: this.selectedSupervisorId,
    }
    
    console.log('📤 Datos enviados al API:', data);
    console.log('🧹 RUT limpio enviado:', data.rut);
    
    this.apiService.post('api_usuarios/', data).subscribe({
      next: (response) => {
        console.log('✅ Usuario creado exitosamente:', response);
        this.closeModal('loadingModal');
        this.closeModal('crearUsuario');
        this.cargarUsuarios();
        this.openModal('exitoModal');
      },
      error: (error) => {
        console.error('❌ Error al crear usuario:', error);
        this.closeModal('loadingModal');
        this.openModal('errorModal')
        this.errorMessage = 'Error al crear usuario: ' + error.error.message;
      }
    })
  }

  /**
   * ✅ Modificar usuario con RUT limpio
   */
  modificarUsuario(): void {
    if (!this.selectedSociedadesNew || this.selectedSociedadesNew.length === 0) {
      this.openModal('errorModal');
      this.errorMessage = 'Debe seleccionar al menos una sociedad';
      return;
    }

    let data = {
      id: this.selectedUserId,
      nombre: this.nombreUsuarioNew,
      rut: this.limpiarRUT(this.rutUsuarioNew),
      usuario: this.limpiarRUT(this.rutUsuarioNew),
      email: this.emailUsuarioNew,
      perfil: this.selectedPerfilId,
      empresas_asignadas: this.selectedSociedadesNew
    }

    console.log('📤 Datos de modificación enviados:', data);
    console.log('🧹 RUT limpio enviado:', data.rut);

    this.apiService.put('api_usuarios/', data).subscribe({
      next: (response) => {
        console.log('✅ Usuario modificado exitosamente:', response);
        this.closeModal('modificarUsuario');
        this.cargarUsuarios();
        this.openModal('exitoModal');
      },
      error: (error) => {
        console.error('❌ Error al modificar usuario:', error);
        this.openModal('errorModal');
        this.errorMessage = error.error.message || 'Error al modificar usuario';
      }
    });
  }

  cargarUsuarios(): void {
    const url = `api_usuarios/${this.holding}/`;
    this.apiService.get(url).subscribe({
      next: (response) => {
        console.log('Usuarios disponibles: ', response);
        this.usuariosCargados = response;
      },
      error: (error) => {
        if (error.status !== 404) {
          this.openErrorModal('Error al cargar usuarios: ' + error.error.message);
        } else {
          this.usuariosCargados = [];
          console.log('No se encontraron usuarios, cargando lista vacía');
        }
      }
    });
  }

  eliminarUsuariosSeleccionados(): void {
    console.log(this.deletedRow.length);
    if (this.deletedRow.length > 0) {
      const idsToDelete = this.deletedRow.map(row => row.id);
      this.apiService.delete('api_usuarios/', { ids: idsToDelete }).subscribe({
        next: () => {
          this.closeModal('confirmacionModal')
          this.cargarUsuarios();
          this.openModal('exitoModal');
          this.deletedRow = [];
        },
        error: (error) => {
          this.openModal('errorModal');
          console.error('Error al eliminar perfiles:', error);
        }
      });
    }
  }

  toggleSelection(id: number, list: number[], total: any[]): void {
    const index = list.indexOf(id);
    if (index > -1) {
      list.splice(index, 1);
    } else {
      list.push(id);
    }
    this.todasSeleccionadas = list.length === total.length;
  }

  selectAllSociedades(isChecked: boolean): void {
    this.selectedSociedades = isChecked ? this.sociedadesCargadas.map(s => s.id) : [];
  }

  selectAllSociedadesNew(isChecked: boolean): void {
    this.selectedSociedadesNew = isChecked ? this.sociedadesCargadas.map(s => s.id) : [];
  }

  toggleSelectionPerfil(perfilId: number): void {
    if (this.selectedPerfilId === perfilId) {
      this.selectedPerfilId = null;
    } else {
      this.selectedPerfilId = perfilId;
    }
  }

  toggleDropdownPerfiles(): void {
    this.dropdownOpenPerfiles = !this.dropdownOpenPerfiles;
    if (this.dropdownOpenPerfiles) {
      this.dropdownOpenSociedades = false;
    }
  }

  toggleDropdownSociedades(): void {
    this.dropdownOpenSociedades = !this.dropdownOpenSociedades;
    if (this.dropdownOpenSociedades) {
      this.dropdownOpenPerfiles = false;
    }
  }

  getSelectedPerfilName(): string {
    if (this.selectedPerfilId) {
      const perfil = this.perfilesCargados.find(p => p.id === this.selectedPerfilId);
      return perfil?.nombre_perfil || 'SELECCIONAR PERFIL';
    }
    return 'SELECCIONAR PERFIL';
  }

  isPerfilDisabled(perfil: any): boolean {
    return perfil.nombre_perfil === 'JEFE DE CUADRILLA' && (!this.supervisoresCargados || this.supervisoresCargados.length === 0);
  }

  isSelected(row: any): boolean {
    return this.selectedRows.some(r => r.id === row.id);
  }

  /**
   * ✅ CORREGIDO: Seleccionar fila con campos correctos del API
   */
  selectRow(row: any): void {
    const index = this.selectedRows.findIndex(selectedRow => selectedRow.id === row.id);
    if (index > -1) {
      this.selectedRows.splice(index, 1);
    } else {
      this.selectedRows.push(row);
    }

    if (this.selectedRows.length > 0) {
      const lastSelectedRow = this.selectedRows[this.selectedRows.length - 1];
      
      console.log('👤 Usuario seleccionado:', lastSelectedRow);
      
      // ✅ Usar campos correctos del API
      this.selectedSociedadesNew = lastSelectedRow.empresas_asignadas || [];
      this.usuarioSeleccionado = {
        nombre_usuario_seleccionado: lastSelectedRow.nombre_persona || lastSelectedRow.nombre,
        rut_usuario_seleccionado: lastSelectedRow.rut,
        email_usuario_seleccionado: lastSelectedRow.email,
        id_perfil_usuario_seleccionado: lastSelectedRow.perfil,
        id_usuario_seleccionado: lastSelectedRow.id,
      };
      
      // ✅ Asignar a variables New
      this.selectedPerfilId = this.usuarioSeleccionado.id_perfil_usuario_seleccionado;
      this.nombreUsuarioNew = this.usuarioSeleccionado.nombre_usuario_seleccionado;
      this.rutUsuarioNew = this.formatRUTString(this.usuarioSeleccionado.rut_usuario_seleccionado);
      this.emailUsuarioNew = this.usuarioSeleccionado.email_usuario_seleccionado;
      this.selectedUserId = this.usuarioSeleccionado.id_usuario_seleccionado;
      
      console.log('📝 Campos asignados para modificar:');
      console.log('   Nombre:', this.nombreUsuarioNew);
      console.log('   RUT:', this.rutUsuarioNew);
      console.log('   Email:', this.emailUsuarioNew);
      console.log('   Perfil ID:', this.selectedPerfilId);
    } else {
      this.usuarioSeleccionado = {
        nombre_usuario_seleccionado: '',
        rut_usuario_seleccionado: '',
        email_usuario_seleccionado: '',
      }
      // Limpiar también las variables New
      this.nombreUsuarioNew = '';
      this.rutUsuarioNew = '';
      this.emailUsuarioNew = '';
      this.selectedPerfilId = null;
    }
  }

  /**
   * Formatea RUT en el input mientras el usuario escribe
   */
  formatRUT(event: Event): void {
    const target = event.target as HTMLInputElement;
    if (!target) return;

    let valor = target.value.replace(/[.\-\s]/g, '').toUpperCase();
    const verificador = valor.slice(-1);
    let rutNumeros = valor.slice(0, -1);
    
    if (rutNumeros.length === 0) {
      target.value = '';
      return;
    }
    
    let parts = [];
    while (rutNumeros.length > 3) {
      parts.unshift(rutNumeros.slice(-3));
      rutNumeros = rutNumeros.slice(0, -3);
    }
    parts.unshift(rutNumeros);
    
    target.value = parts.join('.') + '-' + verificador;
  }

  /**
   * Formatea un string de RUT para mostrar
   */
  formatRUTString(value: string): string {
    if (!value) return '';

    const rutLimpio = this.limpiarRUT(value);
    const verificador = rutLimpio.slice(-1);
    let rutNumeros = rutLimpio.slice(0, -1);
    
    if (rutNumeros.length === 0) return '';
    
    let parts = [];
    while (rutNumeros.length > 3) {
      parts.unshift(rutNumeros.slice(-3));
      rutNumeros = rutNumeros.slice(0, -3);
    }
    parts.unshift(rutNumeros);
    
    return parts.join('.') + '-' + verificador;
  }

  deseleccionarFila(event: MouseEvent) {
    this.selectedRows = [];
    this.dropdownOpenPerfiles = false;
    this.dropdownOpenSociedades = false;
  }

  openModal(key: string): void {
    this.modals[key] = true;
    if (key == 'confirmacionModal') {
      this.deletedRow = this.selectedRows;
    }
    if (key === 'crearUsuario') {
      this.resetearCamposCrearUsuario();
    }
  }

  resetearCamposCrearUsuario(): void {
    this.selectedPersonalId = '';
    this.nombreUsuario = '';
    this.rutUsuario = '';
    this.emailUsuario = '';
    this.selectedPerfilId = null;
    this.selectedSociedades = [];
    this.selectedSupervisorId = null;
    this.dropdownOpenPerfiles = false;
    this.dropdownOpenSociedades = false;
  }

  closeModal(key: string): void {
    this.modals[key] = false;
    if (key === 'exitoModal') {
      this.cargarPerfiles();
    }
    if (key === 'crearUsuario' || key === 'modificarUsuario') {
      this.dropdownOpenPerfiles = false;
      this.dropdownOpenSociedades = false;
    }
  }

  openErrorModal(message: string): void {
    this.modals['errorModal'] = true;
    this.errorMessage = message;
  }
}