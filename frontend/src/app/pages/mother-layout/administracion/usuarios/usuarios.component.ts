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
    crearUsuario: false,
    modificarUsuario: false,
    perfilesModal: false,
    confirmacionModal: false,
    seleccionInicial: false,
    sociedadesModal: false
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
  public selectedPersonalId: number | null = null;

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
  public dropdownOpen: boolean = false;
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
      //this.sociedad_actual_id = parseInt(localStorage.getItem('sociedad_actual_id')!);
      //this.sucursal_actual_id = parseInt(localStorage.getItem('campo_actual_id')!);
      this.cargarSociedades();
      this.cargarPerfiles();
      this.cargarUsuarios();
      this.cargarPersonalDisponible();
      this.cargarSupervisores();
    }
  }

   /**
   * 🎯 NUEVO MÉTODO: Extrae holding_id del JWT
   */
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
        this.openErrorModal('No se encontraron supervisores');
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
            this.openErrorModal('Error al cargar personal: ' + error.error.message);
        }
    });
}

  onPersonalSelected(personalId: string | number): void {
    // Convertir a número ya que viene como string desde el select
    const id = typeof personalId === 'string' ? parseInt(personalId) : personalId;
    const personalSeleccionado = this.personalDisponible.find(p => p.id === id);
    
    if (personalSeleccionado) {
        this.nombreUsuario = personalSeleccionado.nombre_completo;
        this.rutUsuario = this.formatRUTString(personalSeleccionado.rut);
        this.emailUsuario = personalSeleccionado.correo || '';
        this.selectedPersonalId = id;
        
        // Para debug
        console.log('Personal seleccionado:', personalSeleccionado);
        console.log('Campos actualizados:', {
            nombre: this.nombreUsuario,
            rut: this.rutUsuario,
            email: this.emailUsuario
        });
    } else {
        // Limpiar los campos si no se selecciona ninguna persona
        this.nombreUsuario = '';
        this.rutUsuario = '';
        this.emailUsuario = '';
        this.selectedPersonalId = null;
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
        //this.openErrorModal('Error al cargar perfiles: ' + error.error.message);
      }
    });
  }

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

    let data = {
      holding: this.holding,
      empresas_asignadas: this.selectedSociedades,
      persona: this.selectedPersonalId,
      nombre: this.nombreUsuario,
      rut: this.rutUsuario.replace(/\D/g, ''),
      email: this.emailUsuario,
      perfil: this.selectedPerfilId,
      supervisor: this.selectedSupervisorId,
    }
    
    this.apiService.post('api_usuarios/', data).subscribe({
      next: (response) => {
        this.closeModal('crearUsuario');
        this.cargarUsuarios();
        this.openModal('exitoModal');
      },
      error: (error) => {
        this.openModal('errorModal')
        this.errorMessage = 'Error al crear usuario: ' + error.error.message;
      }
    })
  }

  cargarUsuarios(): void {
    const url = `api_usuarios/${this.holding}/`;
    this.apiService.get(url).subscribe({
      next: (response) => {
        console.log('Usuarios disponibles: ', response);
        this.usuariosCargados = response;
      },
      error: (error) => {
        this.openErrorModal('Error al cargar usuarios: ' + error.error.message);
      }
    });
  }

  modificarUsuario(): void {
    if (!this.selectedSociedadesNew || this.selectedSociedadesNew.length === 0) {
      this.openModal('errorModal');
      this.errorMessage = 'Debe seleccionar al menos una sociedad';
      return;
    }

    let data = {
      id: this.selectedUserId,
      nombre: this.nombreUsuarioNew,
      rut: this.rutUsuarioNew,
      usuario: this.rutUsuarioNew,
      email: this.emailUsuarioNew,
      perfil: this.selectedPerfilId,
      empresas_asignadas: this.selectedSociedadesNew
    }

    this.apiService.put('api_usuarios/', data).subscribe({
      next: (response) => {
        this.closeModal('modificarUsuario');
        this.cargarUsuarios();
        this.openModal('exitoModal');
      },
      error: (error) => {
        this.openModal('errorModal');
        this.errorMessage = error.error.message || 'Error al modificar usuario';
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

  isSelected(row: any): boolean {
    return this.selectedRows.some(r => r.id === row.id);
  }

  selectRow(row: any): void {
    const index = this.selectedRows.findIndex(selectedRow => selectedRow.id === row.id);
    if (index > -1) {
      this.selectedRows.splice(index, 1);
    } else {
      this.selectedRows.push(row);
    }

    if (this.selectedRows.length > 0) {
      const lastSelectedRow = this.selectedRows[this.selectedRows.length - 1];
      this.selectedSociedadesNew = lastSelectedRow.empresas_asignadas || [];
      this.usuarioSeleccionado = {
        nombre_usuario_seleccionado: lastSelectedRow.nombre,
        rut_usuario_seleccionado: lastSelectedRow.rut,
        email_usuario_seleccionado: lastSelectedRow.email,
        id_perfil_usuario_seleccionado: lastSelectedRow.perfil,
        id_usuario_seleccionado: lastSelectedRow.id,
      };
      this.selectedPerfilId = this.usuarioSeleccionado.id_perfil_usuario_seleccionado;
      this.nombreUsuarioNew = this.usuarioSeleccionado.nombre_usuario_seleccionado;
      this.rutUsuarioNew = this.formatRUTString(this.usuarioSeleccionado.rut_usuario_seleccionado);
      this.emailUsuarioNew = this.usuarioSeleccionado.email_usuario_seleccionado;
      this.selectedUserId = this.usuarioSeleccionado.id_usuario_seleccionado;
    } else {
      this.usuarioSeleccionado = {
        nombre_usuario_seleccionado: '',
        rut_usuario_seleccionado: '',
        email_usuario_seleccionado: '',
      }
    }
  }

  formatRUT(event: Event): void {
    const target = event.target as HTMLInputElement;
    if (!target) return;

    let rut = target.value.replace(/\D/g, '');
    let parts = [];
    const verifier = rut.slice(-1);
    rut = rut.slice(0, -1);
    while (rut.length > 3) {
      parts.unshift(rut.slice(-3));
      rut = rut.slice(0, -3);
    }
    parts.unshift(rut);
    target.value = parts.join('.') + '-' + verifier;
    if (target.value === '-') {
      target.value = '';
    }
  }

  formatRUTString(value: string): string {
    // Si el valor está vacío, retornar cadena vacía
    if (!value) return '';

    // Obtener el último carácter (que podría ser K o k)
    const lastChar = value.slice(-1).toUpperCase();
    
    // Verificar si el último carácter es K
    const isK = lastChar === 'K';
    
    // Obtener solo los números, excluyendo la K si existe
    let rut = value.slice(0, isK ? -1 : undefined).replace(/\D/g, '');
    
    let parts = [];
    // Si es K, usar K como verificador, si no, usar el último número
    const verifier = isK ? 'K' : rut.slice(-1);
    // Si no es K, quitar el último número para procesarlo
    if (!isK) rut = rut.slice(0, -1);
    
    // Formatear los números en grupos de 3
    while (rut.length > 3) {
        parts.unshift(rut.slice(-3));
        rut = rut.slice(0, -3);
    }
    parts.unshift(rut);
    
    // Unir todo con el verificador (número o K)
    return parts.join('.') + '-' + verifier;
}
  toggleDropdown() {
    this.dropdownOpen = !this.dropdownOpen;
  }

  deseleccionarFila(event: MouseEvent) {
    this.selectedRows = [];
  }

  openModal(key: string): void {
    this.modals[key] = true;
    if (key == 'confirmacionModal') {
      this.deletedRow = this.selectedRows;
    }
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
}