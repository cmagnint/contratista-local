import { Component, Inject, OnInit, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser, CommonModule } from '@angular/common';
import { ContratistaApiService } from '../../../../../services/contratista-api.service';
import { FormsModule } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';

@Component({
  selector: 'app-salud',
  standalone: true,
  imports: [
    MatTableModule,
    FormsModule,
    CommonModule,
  ],
  templateUrl: './salud.component.html',
  styleUrl: './salud.component.css'
})
export class SaludComponent implements OnInit {
  //VARIABLES

  constructor(
    private apiService: ContratistaApiService,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {}

  // Booleanos para abrir o cerrar ventanas
  public modals: { [key: string]: boolean } = {
    exitoModal: false,
    errorModal: false,
    crearSalud: false,
    modificarSalud: false,
    confirmacionModal: false,
  };

  //Salud seleccionada
  public saludSeleccionada: any = {
    nombre_salud_seleccionada: '',
    id_salud_seleccionada: 0,
    porcentaje_descuento_seleccionado: 7.0,
  }
  
  public holding: string = ''; //Variable para guardar el ID del holding al cual pertenece al adminitrador
  public nombreSalud: string = '';
  public porcentajeDescuento: number = 7.0; // Default value

  errorMessage!: string; //Variable usada para mostrar los mensajes de error de la API
  selectedRows: any[] = []; //Array usado para guardar las filas seleccionadas
  dropdownOpen: boolean = false; //Booleano usado para abrir los dropdownmenus 

  public todasSeleccionadas: boolean = false; //Booleano para seleccionar todas/ninguna casilla

  public saludCargadas: any[] = [];

  columnasDesplegadas = ['codigo', 'nombre', 'porcentaje']; // Added porcentaje
  
  public nombreSaludNew: string = '';
  public porcentajeDescuentoNew: number = 7.0;

  public deletedRow: any[] = [];
  
  public selectedSaludId: number | null = null;

  //FUNCIONES
  ngOnInit(): void {
    if (isPlatformBrowser(this.platformId)) {
      this.holding = localStorage.getItem('holding_id') || '';
      this.cargarSalud();
    }
  }

  //FUNCIONES CRUD
  crearSalud(): void {
    let data = {
      holding: this.holding,
      nombre: this.nombreSalud,
      porcentaje_descuento: this.porcentajeDescuento
    }
    this.apiService.post('api_salud_trabajadores/', data).subscribe({
      next: (response) => {
        console.log(response);
        this.closeModal('crearSalud');
        this.cargarSalud();
        this.openModal('exitoModal');
      }, 
      error: (error) => {
        this.errorMessage = error.error?.message || 'Error al crear Salud';
        this.openModal('errorModal');
      }
    })
  }

  cargarSalud(): void {
    this.apiService.get(`api_salud_trabajadores/?holding=${this.holding}`).subscribe({
      next: (response) => {
        this.saludCargadas = response;
      },
      error: (error) => {
        console.error('Error al recibir la salud:', error);
        this.errorMessage = 'Error al cargar Salud';
        this.openModal('errorModal');
      }
    });
  }

  modificarSalud(): void {
    let data = {
      holding: this.holding,
      id: this.selectedSaludId,
      nombre: this.nombreSaludNew,
      porcentaje_descuento: this.porcentajeDescuentoNew
    }
    this.apiService.put('api_salud_trabajadores/', data).subscribe({
      next: (response) => {
        this.closeModal('modificarSalud');
        this.cargarSalud();
        this.openModal('exitoModal');
      }, 
      error: (error) => {
        console.log(error);
        this.errorMessage = error.error?.message || 'Error al modificar Salud';
        this.openModal('errorModal');
      }
    })
  }
  
  eliminarSaludSeleccionadas(): void {
    if (this.deletedRow.length > 0) {
      const idsToDelete = this.deletedRow.map(row => row.id);
      this.apiService.delete('api_salud_trabajadores/', {ids: idsToDelete}).subscribe({
        next: () => {
          this.closeModal('confirmacionModal')
          this.cargarSalud();
          this.openModal('exitoModal');
          this.deletedRow = []; // Limpiar la selección después de eliminar
        },
        error: (error) => {
          this.errorMessage = error.error?.message || 'Error al eliminar Salud';
          this.openModal('errorModal');
          console.error('Error al eliminar salud:', error);
        }
      });
    }
  }

  //------------------------------------------------------------------------------//

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

    if (this.selectedRows.length > 0) {
      const lastSelectedRow = this.selectedRows[this.selectedRows.length - 1];
      this.saludSeleccionada = {
        nombre_salud_seleccionada: lastSelectedRow.nombre,
        id_salud_seleccionada: lastSelectedRow.id,
        porcentaje_descuento_seleccionado: lastSelectedRow.porcentaje_descuento,
      };
      this.selectedSaludId = this.saludSeleccionada.id_salud_seleccionada;
      this.nombreSaludNew = this.saludSeleccionada.nombre_salud_seleccionada;
      this.porcentajeDescuentoNew = this.saludSeleccionada.porcentaje_descuento_seleccionado;
    } else {
      // Limpiar saludSeleccionada si no hay filas seleccionadas
      this.saludSeleccionada = {
        nombre_salud_seleccionada: '',
        id_salud_seleccionada: 0,
        porcentaje_descuento_seleccionado: 7.0,
      }
    }
  }

  deseleccionarFila(event: MouseEvent) {
    this.selectedRows = [];  // Deselecciona todas las filas
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
      this.cargarSalud();  
    }
  }
}