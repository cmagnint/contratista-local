import { Component, Inject, OnInit, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser, CommonModule } from '@angular/common';
import { ContratistaApiService } from '../../../../../services/contratista-api.service';
import { FormsModule } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';

@Component({
  selector: 'app-afp',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatTableModule,
  ],
  templateUrl: './afp.component.html',
  styleUrl: './afp.component.css'
})
export class AfpComponent implements OnInit {
  //VARIABLES

  constructor(
    private apiService: ContratistaApiService,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {}

  // Booleanos para abrir o cerrar ventanas
  public modals: { [key: string]: boolean } = {
    exitoModal: false,
    errorModal: false,
    crearAfp: false,
    modificarAfp: false,
    confirmacionModal: false,
  };

  //Perfil seleccionado
  public afpSeleccionada: any = {
    nombre_afp_seleccionada: '',
    id_afp_seleccionada: 0,
    porcentaje_descuento_seleccionado: 10.0,
  }

  public holding: string = ''; //Variable para guardar el ID del holding al cual pertenece al adminitrador
  public nombreAfp: string = '';
  public porcentajeDescuento: number = 10.0; // Default value

  errorMessage!: string; //Variable usada para mostrar los mensajes de error de la API
  selectedRows: any[] = []; //Array usado para guardar las filas seleccionadas
  dropdownOpen: boolean = false; //Booleano usado para abrir los dropdownmenus 

  public todasSeleccionadas: boolean = false; //Booleano para seleccionar todas/ninguna casilla

  public afpsCargadas: any[] = [];

  columnasDesplegadas = ['codigo', 'nombre', 'porcentaje']; // Added porcentaje
  
  public nombreAFpNew: string = '';
  public porcentajeDescuentoNew: number = 10.0;

  public deletedRow: any[] = [];
  
  public selectedAfpId: number | null = null;

  //FUNCIONES
  ngOnInit(): void {
    if (isPlatformBrowser(this.platformId)) {
      this.holding = localStorage.getItem('holding_id') || '';
      this.cargarAfps();
    }
  }

  //FUNCIONES CRUD
  crearAfps(): void {
    let data = {
      holding: this.holding,
      nombre: this.nombreAfp,
      porcentaje_descuento: this.porcentajeDescuento
    }
    this.apiService.post('api_afp_trabajadores/', data).subscribe({
      next: (response) => {
        console.log(response);
        this.closeModal('crearAfp');
        this.cargarAfps();
        this.openModal('exitoModal');
      }, 
      error: (error) => {
        this.errorMessage = error.error?.message || 'Error al crear AFP';
        this.openModal('errorModal');
      }
    })
  }

  cargarAfps(): void {
    this.apiService.get(`api_afp_trabajadores/?holding=${this.holding}`).subscribe({
      next: (response) => {
        this.afpsCargadas = response;
      },
      error: (error) => {
        console.error('Error al recibir las afps:', error);
        this.errorMessage = 'Error al cargar AFPs';
        this.openModal('errorModal');
      }
    });
  }

  modificarAfps(): void {
    let data = {
      holding: this.holding,
      id: this.selectedAfpId,
      nombre: this.nombreAFpNew,
      porcentaje_descuento: this.porcentajeDescuentoNew
    }
    this.apiService.put('api_afp_trabajadores/', data).subscribe({
      next: (response) => {
        this.closeModal('modificarAfp');
        this.cargarAfps();
        this.openModal('exitoModal');
      }, 
      error: (error) => {
        console.log(error);
        this.errorMessage = error.error?.message || 'Error al modificar AFP';
        this.openModal('errorModal');
      }
    })
  }
  
  eliminarAfpSeleccionadas(): void {
    if (this.deletedRow.length > 0) {
      const idsToDelete = this.deletedRow.map(row => row.id);
      this.apiService.delete('api_afp_trabajadores/', {ids: idsToDelete}).subscribe({
        next: () => {
          this.closeModal('confirmacionModal')
          this.cargarAfps();
          this.openModal('exitoModal');
          this.deletedRow = []; // Limpiar la selección después de eliminar
        },
        error: (error) => {
          this.errorMessage = error.error?.message || 'Error al eliminar AFPs';
          this.openModal('errorModal');
          console.error('Error al eliminar AFPs:', error);
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
      this.afpSeleccionada = {
        nombre_afp_seleccionada: lastSelectedRow.nombre,
        id_afp_seleccionada: lastSelectedRow.id,
        porcentaje_descuento_seleccionado: lastSelectedRow.porcentaje_descuento,
      };
      this.selectedAfpId = this.afpSeleccionada.id_afp_seleccionada;
      this.nombreAFpNew = this.afpSeleccionada.nombre_afp_seleccionada;
      this.porcentajeDescuentoNew = this.afpSeleccionada.porcentaje_descuento_seleccionado;
    } else {
      // Limpiar afpSeleccionada si no hay filas seleccionadas
      this.afpSeleccionada = {
        nombre_afp_seleccionada: '',
        id_afp_seleccionada: 0,
        porcentaje_descuento_seleccionado: 10.0,
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
      this.cargarAfps();  
    }
  }
}