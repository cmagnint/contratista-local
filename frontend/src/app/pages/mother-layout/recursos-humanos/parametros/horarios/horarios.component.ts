import { Component, Inject, OnInit, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser, CommonModule } from '@angular/common';
import { ContratistaApiService } from '../../../../../services/contratista-api.service';
import { FormsModule } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';


@Component({
  selector: 'app-horarios',
  standalone: true,
  imports: [
    MatTableModule,
    FormsModule,
    CommonModule,
  ],
  templateUrl: './horarios.component.html',
  styleUrl: './horarios.component.css'
})
export class HorariosComponent implements OnInit {
  //VARIABLES

  constructor(
    private apiService: ContratistaApiService,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {}

  // Booleanos para abrir o cerrar ventanas
  public modals: { [key: string]: boolean } = {
    exitoModal: false,
    errorModal: false,
    crearHorario: false,
    modificarHorario: false,
    confirmacionModal: false,
    eliminarModal: false,
  };

  //Unidad Contrl  seleccionado

  public horarioSeleccionado: any = {
    id_horario_seleccionado : 0,
    jornada_horario_seleccionado : 0.0,
  }

  
  public holding: string = ''; //Variable para guardar el ID del holding al cual pertenece al adminitrador
  public jornadaHorario: number | null = null;
 
  errorMessage!: string; //Variable usada para mostrar los mensajes de error de la API
  selectedRows: any[] = []; //Array usado para guardar las filas seleccionadas
  dropdownOpen: boolean = false; //Booleano usado para abrir los dropdownmenus 

  public todasSeleccionadas: boolean = false; //Booleano para seleccionar todas/ninguna casilla

  public horariosCargados: any[] = [];

  columnasDesplegadas = ['codigo','jornada'];
  
  public deletedRow: any[] = [];
  //TESTING 

  //------------------------------------------------------------//

  public selectedHorarioId: number | null = null;
  public jornadaHorarioNew: number | null = null;
  //FUNCIONES
  
  ngOnInit(): void {
    if (isPlatformBrowser(this.platformId)) {
      this.holding = localStorage.getItem('holding_id') || '';
      this.cargarHorarios();
    }
  }
  //FUNCIONES CRUD

  crearHorario():void{
    let data = {
      holding: this.holding,
      jornada: this.jornadaHorario,
    }
    this.apiService.post('horarios/', data).subscribe({
      next: (response) => {
        console.log(response);
        this.closeModal('crearHorario');
        this.cargarHorarios();
        this.openModal('exitoModal');
        
      }, error:(error) => {
        this.openModal('errorModal');
      }
    })
  }

  cargarHorarios():void{
    this.apiService.get(`horarios/?holding=${this.holding}`).subscribe({
      next: (response) => {
        this.horariosCargados = response;
      },
      error: (error) => {
        console.error('Error al recibir las sociedades:', error);
      }
    });
  }

  modificarHorario():void{
    let data = {
      holding: this.holding,
      id : this.selectedHorarioId,
      jornada: this.jornadaHorarioNew,
    }
    this.apiService.put('horarios/', data).subscribe({
      next:(response) => {
        this.closeModal('modificarHorario');
        this.cargarHorarios();
        this.openModal('exitoModal');
      }, error:(error) => {
        console.log(error);
        this.openModal('errorModal');
      }
    })
  }
  
  eliminarHorariosSeleccionadas(): void {
    if (this.deletedRow.length > 0) {
        const idsToDelete = this.deletedRow.map(row => row.id);
        this.apiService.delete('horarios/', {ids: idsToDelete}).subscribe({
            next: () => {
                this.closeModal('confirmacionModal')
                this.cargarHorarios();
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

  toggleSelection(horarioId: number): void {
    if (this.selectedHorarioId === horarioId) {
      this.selectedHorarioId = null;  // Deseleccionar si el mismo perfil es clickeado nuevamente
    } else {
      this.selectedHorarioId = horarioId;  // Seleccionar el nuevo perfil
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
        this.horarioSeleccionado = {
        id_horario_seleccionado : lastSelectedRow.id,
        jornada_horario_seleccionado : lastSelectedRow.jornada,
      };
      this.selectedHorarioId = this.horarioSeleccionado.id_horario_seleccionado;
      this.jornadaHorarioNew = this.horarioSeleccionado.jornada_horario_seleccionado;
    } else {
      // Limpiar perfilSeleccionado si no hay filas seleccionadas
      this.horarioSeleccionado = {
        id_horario_seleccionado : 0,
        jornada_horario_seleccionado : 0.0,
      }
    }
  }

  estadoUnidadControl: boolean = true; // Inicializa el estado

  toggleEstadoUnidadControl() {
    this.estadoUnidadControl = !this.estadoUnidadControl;
  }

  formatNumber(event: Event): void {
    const target = event.target as HTMLInputElement; // Casting seguro
    if (!target) return; // Verificar que realmente existe un target

    // Mantener solo caracteres numéricos
    target.value = target.value.replace(/[^\d]/g, '');
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
      this.cargarHorarios();  
    }
  }

  checkValue():void{
    
    
  }
}
