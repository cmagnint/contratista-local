import { Component, Inject, OnInit, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser, CommonModule } from '@angular/common';
import { ContratistaApiService } from '../../../../../services/contratista-api.service';
import { FormsModule } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';


@Component({
  selector: 'app-casas',
  standalone: true,
  imports: [
    MatTableModule,
    FormsModule,
    CommonModule,
  ],
  templateUrl: './casas.component.html',
  styleUrl: './casas.component.css'
})
export class CasasComponent implements OnInit {
  //VARIABLES

  constructor(
    private apiService: ContratistaApiService,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {}

  // Booleanos para abrir o cerrar ventanas
  public modals: { [key: string]: boolean } = {
    exitoModal: false,
    errorModal: false,
    crearCasa: false,
    modificarCasa: false,
    confirmacionModal: false,
  };

  //Perfil seleccionado

  public CasasSeleccionada: any = {
    id_casa_seleccionada : 0,
    nombre_casa_seleccionada : '',
    estado_casa_seleccionada: false,
  }

  public holding: string = ''; //Variable para guardar el ID del holding al cual pertenece al adminitrador
  public nombreCasa: string = '';

  
  public nombreCasaNew: string = '';
  

  errorMessage!: string; //Variable usada para mostrar los mensajes de error de la API
  selectedRows: any[] = []; //Array usado para guardar las filas seleccionadas
  dropdownOpen: boolean = false; //Booleano usado para abrir los dropdownmenus 

  public todasSeleccionadas: boolean = false; //Booleano para seleccionar todas/ninguna casilla

  public casasCargadas: any[] = [];

  columnasDesplegadas = ['codigo','nombre','estado'];
  
  public deletedRow: any[] = [];
  //TESTING 

  //------------------------------------------------------------//

 
  public selectedCasaId: number | null = null;

  //FUNCIONES
  
  ngOnInit(): void {
    if (isPlatformBrowser(this.platformId)) {
      this.holding = localStorage.getItem('holding_id') || '';
      this.cargarCasas();
    }
  }

  //FUNCIONES CRUD

  crearCasa():void{
    let data = {
      holding: this.holding,
      nombre : this.nombreCasa,
    }
    this.apiService.post('api_casas_trabajadores/', data).subscribe({
      next: (response) => {
        console.log(response);
        this.closeModal('crearAfp');
        this.cargarCasas();
        this.openModal('exitoModal');
        
      }, error:(error) => {
        this.openModal('errorModal');
      }
    })
  }

  cargarCasas():void{
    this.apiService.get(`api_casas_trabajadores/?holding=${this.holding}`).subscribe({
      next: (response) => {
        this.casasCargadas = response;
      },
      error: (error) => {
        console.error('Error al recibir las sociedades:', error);
      }
    });
  }

  modificarCasa():void{
    let data = {
      holding: this.holding,
      id : this.selectedCasaId,
      nombre: this.nombreCasaNew,
      estado: this.estadoCasaNew,
    }
    this.apiService.put('api_casas_trabajadores/', data).subscribe({
      next:(response) => {
        this.closeModal('modificarAfp');
        this.cargarCasas();
        this.openModal('exitoModal');
      }, error:(error) => {
        console.log(error);
        this.openModal('errorModal');
      }
    })
  }
  
  eliminarCasasSeleccionadas(): void {
    if (this.deletedRow.length > 0) {
        const idsToDelete = this.deletedRow.map(row => row.id);
        this.apiService.delete('api_casas_trabajadores/', {ids: idsToDelete}).subscribe({
            next: () => {
                this.closeModal('confirmacionModal')
                this.cargarCasas();
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

  //------------------------------------------------------------------------------//

  estadoCasaNew: boolean = true; // Inicializa el estado

  toggleEstado() {
    this.estadoCasaNew = !this.estadoCasaNew;
  }

  toggleSelection(casaId: number): void {
    if (this.selectedCasaId === casaId) {
      this.selectedCasaId = null;  // Deseleccionar si el mismo perfil es clickeado nuevamente
    } else {
      this.selectedCasaId = casaId;  // Seleccionar el nuevo perfil
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
        this.CasasSeleccionada = {
          id_casa_seleccionada : lastSelectedRow.id,
          nombre_casa_seleccionada : lastSelectedRow.nombre,
          estado_casa_seleccionada: lastSelectedRow.estado,
        };
        this.selectedCasaId = this.CasasSeleccionada.id_casa_seleccionada;
        this.nombreCasaNew = this.CasasSeleccionada.nombre_casa_seleccionada;
        this.estadoCasaNew = this.CasasSeleccionada.estado_casa_seleccionada  
    } else {
      this.CasasSeleccionada = {
        id_casa_seleccionada : 0,
        nombre_casa_seleccionada : '',
        estado_casa_seleccionada: false,
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
      this.cargarCasas();  
    }
  }

  checkValue():void{
    
    
  }
}


