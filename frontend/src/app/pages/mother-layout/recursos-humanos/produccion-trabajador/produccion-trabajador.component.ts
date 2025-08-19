import { Component, Inject, OnInit, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser, CommonModule } from '@angular/common';
import { ContratistaApiService } from '../../../../services/contratista-api.service';
import { ReactiveFormsModule } from '@angular/forms';
import { FormsModule } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';

@Component({
  selector: 'app-produccion-trabajador',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatTableModule,
    FormsModule
  ],
  templateUrl: './produccion-trabajador.component.html',
  styleUrl: './produccion-trabajador.component.css'
})
export class ProduccionTrabajadorComponent implements OnInit {
  //VARIABLES

  constructor(
    private apiService: ContratistaApiService,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {}

 

  // Booleanos para abrir o cerrar ventanas
  public modals: { [key: string]: boolean } = {
    exitoModal: false,
    errorModal: false,
    crearTrabajador: false,
    modificarTrabajador: false,
    holdingModal: false,
    sociedadesModal: false,
    clientesModal: false,
    camposModal: false,
    areasModal: false,
    cargosModal: false,
    afpModal: false,
    saludModal: false,
    confirmacionModal: false,
  };

  //Perfil seleccionado
  public trabajadorSeleccionado: any = {
    nombre_trabajador_seleccionado : '',
    rut_trabajador_seleccionado : '',
    direccion_trabajador_seleccionado : '',
    fecha_ingreso_trabajador_seleccionado : Date,
    id_trabajador_seleccionado : 0,
    id_sociedad_trabajador_seleccionado : 0,
    id_cargo_trabajador_seleccionado : 0,
    id_area_trabajador_seleccionado : 0 ,
    id_salud_trabajador_seleccionado : 0,
    id_afp_trabajador_seleccionado : 0,
  }

  public holding: string = ''; //Variable para guardar el ID del holding al cual pertenece al adminitrador
  public nombreTrabajador: string | null = null;
  public rutTrabajador: string | null = null;
  public correoTrabajador: string | null = null;
  public direccionTrabajador: string | null = null;
  public fechaTrabajador : Date | null = null;
  public sexoTrabajador: string = 'Hombre';
  public telefonoTrabajador: string | null = null;
  public metodoPago: string = 'Sin Pago';
  public banco: string | null = null;
  public tipoCuenta: string | null = null;
  public numeroCuenta: string | null = null;

  //SOCIEDADES CARGADAS
  public sociedadesCargadas: any[] = []
  public selectedSociedadId: number | null = null;
  
  //CLIENTES CARGADOS
  public clientesCargados:  any[] = []
  public selectedClienteId: number | null = null;

  //AREAS CARGADAS
  public areasCargadas: any[] = []
  public selectedAreaId: number | null = null;

  //CARGOS CARGADOS
  public cargosCargados: any[] = []
  public selectedCargoId: number | null = null;

  //AFP CARGADOS
  public afpCargadas: any[] = []
  public selectedAfpId: number | null = null;

  //SALUD CARGADOS
  public saludCargadas: any[] = []
  public selectedSaludId: number | null = null;
  
  //CAMPOS CARGADOS
  public camposCargados: any[] = [];
  public selectedCampoId: number | null = null;

  public fechaIngreso: string | null = null;

  errorMessage!: string; //Variable usada para mostrar los mensajes de error de la API
  selectedRows: any[] = []; //Array usado para guardar las filas seleccionadas
  dropdownOpen: boolean = false; //Booleano usado para abrir los dropdownmenus 

  public todasSeleccionadas: boolean = false; //Booleano para seleccionar todas/ninguna casilla
  public produccionesCargadas: any[] = [];
  columnasDesplegadas = ['codigo','sociedad','supervisor','nombre_trabajador','nombre_labor','nombre_unidad_control',
    'folio','valor_pago_trabajador','horas','fecha_ingreso_produccion'];
  
  public nombreTrabajadorNew: string = '';
  public rutTrabajadorNew: string = '';
  public emailTrabajadorNew: string = '';
  public deletedRow: any[] = [];
  //TESTING 

  //------------------------------------------------------------//
  public selectedTrabajadorId: number | null = null; //GUARDA EL ID DEL TRABAJADOR DE LA FILA SELECCIONADA

  //FUNCIONES
  
  ngOnInit():void {
    if (isPlatformBrowser(this.platformId)) {
      this.holding = localStorage.getItem('holding_id') || '';
      this.cargarProduccion();
      this.cargarSociedades();
      this.cargarAreas();
      this.cargarCargos();
      this.cargaAfp();
      this.cargarSalud();
      this.cargarClientes();
      this.cargarCampos();
      this.setDefaultFechaCelebracion();
    }
  }

  setDefaultFechaCelebracion(): void {
    const today = new Date();
    const day = String(today.getDate()).padStart(2, '0');
    const month = String(today.getMonth() + 1).padStart(2, '0');
    const year = today.getFullYear();
    this.fechaIngreso = `${year}-${month}-${day}`;
  }

  //CARGAR SOCIEDADES
  cargarSociedades(): void {
    this.apiService.get(`api_sociedad/?holding=${this.holding}`).subscribe({
      next: (response) => {
        if(response.length > 0) {
          this.sociedadesCargadas = response;
        } else {
          console.log('No se encontraron sociedades');
        }
      }, 
      error: (error) => {
        console.error('Error al recibir las sociedades:', error);
      }
    });
  }

  //CARGAR CLIENTES
  cargarClientes(): void {
    this.apiService.get(`api_clientes/?holding=${this.holding}`).subscribe({
      next: (response) => {
        if(response.length > 0) {
          this.clientesCargados = response;
        } else {
          console.log('No se encontraron clientes');
        }
      }, 
      error: (error) => {
        console.error('Error al recibir los clientes:', error);
      }
    });
  }
  
  cargarAreas():void{
    this.apiService.get(`api_areas_administracion/?holding=${this.holding}`).subscribe({
      next: (response) => {
        this.areasCargadas = response;
        console.log(this.areasCargadas);
      },
      error: (error) => {
        console.error('Error al recibir las sociedades:', error);
      }
    });
  }

  cargarCargos(): void {
    this.apiService.get(`api_cargos_administracion/?holding=${this.holding}`).subscribe({
      next: (response) => {
        this.cargosCargados = response; 
        if (response.length === 0) {
          this.selectedRows = [];
        }
      },
      error: (error) => {
        this.openModal('errorModal');
      }
    });
  }

  cargaAfp(): void {
    this.apiService.get(`api_afp_trabajadores/?holding=${this.holding}`).subscribe({
      next: (response) => {
        this.afpCargadas = response; // Asegurar que el dataSource se actualiza completamente
        if (response.length === 0) {
          // Si no hay perfiles, asegurarse de limpiar cualquier selección
          this.selectedRows = [];
        }
      },
      error: (error) => {
        this.openModal('errorModal');
      }
    });
  }

  cargarSalud(): void {
    this.apiService.get(`api_salud_trabajadores/?holding=${this.holding}`).subscribe({
      next: (response) => {
        this.saludCargadas = response; // Asegurar que el dataSource se actualiza completamente
        if (response.length === 0) {
          // Si no hay perfiles, asegurarse de limpiar cualquier selección
          this.selectedRows = [];
        }
      },
      error: (error) => {
        this.openModal('errorModal');
      }
    });
  }

  cargarCampos(): void {
    this.apiService.get(`api_campos_clientes/?holding_id=${this.holding}`).subscribe({
      next: (response) => {
        if (response.length > 0) {
          this.camposCargados = response;
          
        } else {
          console.log('No se encontraron campos');
        }
      }, 
      error: (error) => {
        console.error('Error al recibir los campos:', error);
      }
    });
  }


//----------------------------------------------------------------------------//

  //FUNCIONES CRUD DEL MODULO

  crearTrabajador():void{
    let data = {
      holding: this.holding,
      nombre: this.nombreTrabajador,
      rut: this.rutTrabajador!.replace(/[\.\-]/g, ''),
      correo: this.correoTrabajador,
      direccion: this.direccionTrabajador,
      sexo: this.sexoTrabajador,
      telefono: this.telefonoTrabajador,
      sociedad: this.selectedSociedadId,
      cliente: this.selectedClienteId,
      fundo: this.selectedCampoId,
      area: this.selectedAreaId,
      cargo: this.selectedCargoId,
      afp: this.selectedAfpId,
      salud: this.selectedSaludId,
      metodo_pago: this.metodoPago,
      fecha_ingreso: this.fechaIngreso,
      banco:  this.banco,
      tipo_cuenta_bancaria: this.tipoCuenta, 
      numero_cuenta: this.numeroCuenta,
      nacionalidad: 'CHILENA'

    }
    this.apiService.post('api_personal/', data).subscribe({
      next: (response) => {
        this.closeModal('crearUsuario');
        this.cargarProduccion();
        this.openModal('exitoModal');
        
      }, error:(error) => {
        this.openModal('errorModal')
      }
    })
  }

  onMetodoPagoChange(event: Event): void {
    const selectElement = event.target as HTMLSelectElement;
    this.metodoPago = selectElement.value;
  }

  cargarProduccion():void{
    this.apiService.get(`produccion-trabajador/?holding=${this.holding}`).subscribe({
      next: (response) => {
        this.produccionesCargadas = response;
        
      },
      error: (error) => {
        console.error('Error al recibir las sociedades:', error);
        
      }
    });
  }

  modificarTrabajadores():void{
    let data = {
      id : this.selectedTrabajadorId,
      nombre: this.nombreTrabajadorNew,
      rut: this.rutTrabajadorNew,
      usuario: this.rutTrabajadorNew,
      email: this.emailTrabajadorNew,
      //perfil: this.selectedPerfilId,
    }
    this.apiService.put('api_personal/', data).subscribe({
      next:(response) => {
        console.log('Usuario actualizado:', response);
        this.closeModal('modificarUsuario');
        this.cargarProduccion();
        this.openModal('exitoModal');
      }, error:(error) => {
        console.log(error);
        this.openModal('errorModal');
      }
    })
  }
  
  eliminarTrabajadoresSeleccionados(): void {
    if (this.deletedRow.length > 0) {
        const idsToDelete = this.deletedRow.map(row => row.id);
        this.apiService.delete('api_personal/', {ids: idsToDelete}).subscribe({
            next: () => {
                this.closeModal('confirmacionModal')
                this.cargarProduccion();
                this.openModal('exitoModal');
                this.deletedRow = []; // Limpiar la selección después de eliminar
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
      list.splice(index, 1); // Deseleccionar
    } else {
      list.push(id); // Seleccionar
    }
    // Esta parte comprueba si todas las opciones están seleccionadas para ajustar la casilla "Seleccionar Todas"
    if (list.length === total.length) {
      // Si todas las opciones individuales están seleccionadas
      this.todasSeleccionadas = true;
    } else {
      // Si al menos una opción individual no está seleccionada
      this.todasSeleccionadas = false;
    }
  }

  toggleSelectionSociedad(sociedadId: number): void {
    if (this.selectedSociedadId === sociedadId) {
      this.selectedSociedadId = null;  // Deseleccionar si el mismo perfil es clickeado nuevamente
    } else {
      this.selectedSociedadId = sociedadId;  // Seleccionar el nuevo perfil
    }
  }

  toggleSelectionCliente(clienteId: number): void {
    if (this.selectedClienteId === clienteId) {
      this.selectedClienteId = null;  // Deseleccionar si el mismo perfil es clickeado nuevamente
    } else {
      this.selectedClienteId = clienteId;  // Seleccionar el nuevo perfil
    }
  }

  toggleSelectionCampo(campoId: number): void {
    if (this.selectedCampoId === campoId) {
      this.selectedCampoId = null;  // Deseleccionar si el mismo perfil es clickeado nuevamente
    } else {
      this.selectedCampoId = campoId;  // Seleccionar el nuevo perfil
    }
  }

  toggleSelectionArea(areaId: number): void {
    if (this.selectedAreaId === areaId) {
      this.selectedAreaId = null;  // Deseleccionar si el mismo perfil es clickeado nuevamente
    } else {
      this.selectedAreaId = areaId;  // Seleccionar el nuevo perfil
    }
  }

  toggleSelectionCargo(cargoId: number): void {
    if (this.selectedCargoId === cargoId) {
      this.selectedCargoId = null;  // Deseleccionar si el mismo perfil es clickeado nuevamente
    } else {
      this.selectedCargoId = cargoId;  // Seleccionar el nuevo perfil
    }
  }

  toggleSelectionAFP(afpId: number): void {
    if (this.selectedAfpId === afpId) {
      this.selectedAfpId = null;  // Deseleccionar si el mismo perfil es clickeado nuevamente
    } else {
      this.selectedAfpId = afpId;  // Seleccionar el nuevo perfil
    }
  }

  toggleSelectionSalud(saludId: number): void {
    if (this.selectedSaludId === saludId) {
      this.selectedSaludId = null;  // Deseleccionar si el mismo perfil es clickeado nuevamente
    } else {
      this.selectedSaludId = saludId;  // Seleccionar el nuevo perfil
    }
  }

  isSelected(row: any): boolean {
    return this.selectedRows.some(r => r.id === row.id);
  }

  selectRow(row: any): void {
    const index = this.selectedRows.findIndex(selectedRow => selectedRow.id === row.id);
    if (index > -1) {
        // Si la fila ya está seleccionada, deseleccionarla
        this.selectedRows.splice(index, 1);
    } else {
        // Agregar fila a las seleccionadas
        this.selectedRows.push(row);
    }

    if (this.selectedRows.length > 0){
        const lastSelectedRow = this.selectedRows[this.selectedRows.length - 1];
        this.trabajadorSeleccionado = {
        nombre_usuario_seleccionado : lastSelectedRow.nombre,
        rut_usuario_seleccionado : lastSelectedRow.rut ,
        email_usuario_seleccionado : lastSelectedRow.email ,
        id_perfil_usuario_seleccionado : lastSelectedRow.perfil,
        id_usuario_seleccionado : lastSelectedRow.id,
        
      };
      this.selectedTrabajadorId = this.trabajadorSeleccionado.id_perfil_usuario_seleccionado;
      this.nombreTrabajadorNew = this.trabajadorSeleccionado.nombre_usuario_seleccionado;
      this.rutTrabajadorNew = this.formatRUTString(this.trabajadorSeleccionado.rut_usuario_seleccionado);
      this.emailTrabajadorNew = this.trabajadorSeleccionado.email_usuario_seleccionado;
      //this.selectedUserId = this.trabajadorSeleccionado.id_usuario_seleccionado;
    } else {
      // Limpiar perfilSeleccionado si no hay filas seleccionadas
      this.trabajadorSeleccionado = {
        nombre_usuario_seleccionado : '',
        rut_usuario_seleccionado : ''  ,
        email_usuario_seleccionado : ''  ,
      }
    }
  }

  formatRUT(event: Event): void {
    const target = event.target as HTMLInputElement; // Casting seguro
    if (!target) return; // Verificar que realmente existe un target

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

  validateNumber(event: KeyboardEvent) {
    const pattern = /[0-9]/;
    const inputChar = String.fromCharCode(event.charCode);

    if (!pattern.test(inputChar)) {
      // Invalid character, prevent input
      event.preventDefault();
    }
  }
  
  formatRUTString(value: string): string {
    let rut = value.replace(/\D/g, '');
    let parts = [];
    const verifier = rut.slice(-1);
    rut = rut.slice(0, -1);
    while (rut.length > 3) {
        parts.unshift(rut.slice(-3));
        rut = rut.slice(0, -3);
    }
    parts.unshift(rut);
    return parts.join('.') + '-' + verifier;
  }

  toggleDropdown() {
    this.dropdownOpen = !this.dropdownOpen;
  }

  

  deseleccionarFila(event: MouseEvent) {
    this.selectedRows = [];  // Deselecciona todas las filas
  }

  openModal(key: string): void {
    this.modals[key] = true;
    if(key== 'confirmacionModal'){
      this.deletedRow = this.selectedRows;
      console.log(this.deletedRow);
    }

   
  }

  closeModal(key: string): void {
    this.modals[key] = false;
    if (key === 'exitoModal') {
      this.cargarProduccion();  
    }
  }

  checkValue():void{
    
    
  }
}

