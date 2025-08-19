import { Component, Inject, OnInit, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser, CommonModule } from '@angular/common';
import { ContratistaApiService } from '../../../../services/contratista-api.service';
import { ReactiveFormsModule } from '@angular/forms';
import { FormsModule } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';
import { JwtService } from '../../../../services/jwt.service';

@Component({
  selector: 'app-areas-cargos-administracion',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatTableModule,
    FormsModule
  ],
  templateUrl: './areas-cargos-administracion.component.html',
  styleUrl: './areas-cargos-administracion.component.css'
})
export class AreasCargosAdministracionComponent implements OnInit {
  // VARIABLES
  constructor(
    private apiService: ContratistaApiService,
    private jwtService: JwtService,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {}

  // Booleanos para abrir o cerrar ventanas
  public modals: { [key: string]: boolean } = {
    exitoModal: false,
    errorModal: false,
    crearArea: false,
    modificarArea: false,
    crearCargo: false,
    modificarCargo: false,
    confirmacionModal: false,
    areasModal: false,
    clientesModal: false,
  };

  // VARIABLES PARA ÁREAS
  public areaSeleccionada: any = {
    nombre_area_seleccionada: '',
    id_area_seleccionada: 0,
  };

  public nombreArea: string = '';
  public nombreAreaNew: string = '';
  selectedRows: any[] = [];
  public areasCargadas: any[] = [];
  
  // ✅ SEPARAMOS LAS VARIABLES DE SELECCIÓN
  public selectedAreaIdForTable: number | null = null; // Para selección en tabla
  public selectedAreaIdForCargo: number | null = null; // Para crear/modificar cargos

  // VARIABLES PARA CARGOS
  public cargoSeleccionado: any = {
    nombre_cargo_seleccionado: '',
    id_cargo_seleccionado: 0,
    id_area_cargo_seleccionado: 0,
  };

  
  public nombreCargo: string = '';
  public nombreCargoNew: string = '';
  public cargosCargados: any[] = [];
  public selectedCargoId: number | null = null;
  public errorMessage!: string;
  public holding: string = '';
  public dropdownOpen: boolean = false;
  public deletedRow: any[] = [];
  

   // COLUMNAS PARA TABLAS
  columnasDesplegadas = ['nombre'];
  columnasDesplegadasCargos = ['nombre', 'area'];

  // FUNCIONES
  ngOnInit(): void {
    if (isPlatformBrowser(this.platformId)) {
      this.holding = this.getHoldingIdFromJWT();
      this.cargarAreas();
      this.cargarCargos();
      
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

  // FUNCIONES CRUD PARA ÁREAS
  crearAreas(): void {
    let data = {
      holding: this.holding,
      nombre: this.nombreArea,
      
    };
    this.apiService.post('api_areas_administracion/', data).subscribe({
      next: (response) => {
        this.closeModal('crearArea');
        this.nombreArea = ''; // ✅ Limpiar campo
        this.cargarAreas();
        this.openModal('exitoModal');
      },
      error: (error) => {
        this.openModal('errorModal');
      },
    });
  }

  cargarAreas(): void {
    this.apiService.get(`api_areas_administracion/?holding=${this.holding}`).subscribe({
      next: (response) => {
        this.areasCargadas = response;
      },
      error: (error) => {
        console.error('Error al recibir las áreas:', error);
      },
    });
  }

  modificarAreas(): void {
    let data = {
      holding: this.holding,
      id: this.selectedAreaIdForTable,
      nombre: this.nombreAreaNew,
    };
    this.apiService.put('api_areas_administracion/', data).subscribe({
      next: (response) => {
        this.closeModal('modificarArea');
        this.nombreAreaNew = ''; // ✅ Limpiar campo
        this.cargarAreas();
        this.openModal('exitoModal');
      },
      error: (error) => {
        console.log(error);
        this.openModal('errorModal');
      },
    });
  }

  eliminarAreasSeleccionadas(): void {
    if (this.deletedRow.length > 0) {
      const idsToDelete = this.deletedRow.map((row) => row.id);
      this.apiService.delete('api_areas_administracion/', { ids: idsToDelete }).subscribe({
        next: () => {
          this.closeModal('confirmacionModal');
          this.cargarAreas();
          this.openModal('exitoModal');
          this.deletedRow = []; // Limpiar la selección después de eliminar
        },
        error: (error) => {
          this.openModal('errorModal');
          console.error('Error al eliminar áreas:', error);
        },
      });
    }
  }

  // FUNCIONES CRUD PARA CARGOS
  crearCargos(): void {
    let data = {
      holding: this.holding,
      nombre: this.nombreCargo,
      area: this.selectedAreaIdForCargo,
    };
    this.apiService.post('api_cargos_administracion/', data).subscribe({
      next: (response) => {
        console.log(response);
        this.closeModal('crearCargo');
        this.nombreCargo = ''; // ✅ Limpiar campo
        this.selectedAreaIdForCargo = null; // ✅ Limpiar selección de área
        this.cargarCargos();
        this.openModal('exitoModal');
      },
      error: (error) => {
        this.openModal('errorModal');
      },
    });
  }

  cargarCargos(): void {
    this.apiService.get(`api_cargos_administracion/?holding=${this.holding}`).subscribe({
      next: (response) => {
        this.cargosCargados = response;
      },
      error: (error) => {
        console.error('Error al recibir los cargos:', error);
      },
    });
  }

  modificarCargos(): void {
    let data = {
      holding: this.holding,
      id: this.selectedCargoId,
      nombre: this.nombreCargoNew,
      area: this.selectedAreaIdForCargo,
    };
    this.apiService.put('api_cargos_administracion/', data).subscribe({
      next: (response) => {
        this.closeModal('modificarCargo');
        this.nombreCargoNew = ''; // ✅ Limpiar campo
        this.selectedAreaIdForCargo = null; // ✅ Limpiar selección de área
        this.cargarCargos();
        this.openModal('exitoModal');
      },
      error: (error) => {
        console.log(error);
        this.openModal('errorModal');
      },
    });
  }

  eliminarCargosSeleccionados(): void {
    if (this.deletedRow.length > 0) {
      const idsToDelete = this.deletedRow.map((row) => row.id);
      this.apiService.delete('api_cargos_administracion/', { ids: idsToDelete }).subscribe({
        next: () => {
          this.closeModal('confirmacionModal');
          this.cargarCargos();
          this.openModal('exitoModal');
          this.deletedRow = []; // Limpiar la selección después de eliminar
        },
        error: (error) => {
          this.openModal('errorModal');
          console.error('Error al eliminar cargos:', error);
        },
      });
    }
  }

  // FUNCIONES COMUNES
  // ✅ FUNCIÓN CORREGIDA PARA SELECCIÓN DE ÁREA EN CARGOS
  toggleSelection(areaId: number): void {
    if (this.selectedAreaIdForCargo === areaId) {
      this.selectedAreaIdForCargo = null; // Deseleccionar si el mismo área es clickeada nuevamente
    } else {
      this.selectedAreaIdForCargo = areaId; // Seleccionar el nuevo área
    }
  }

  isSelected(row: any): boolean {
    return this.selectedRows.some((r) => r.id === row.id);
  }

  // ✅ FUNCIÓN CORREGIDA PARA SELECCIÓN DE FILAS EN TABLA
  selectRow(row: any): void {
    const index = this.selectedRows.findIndex((selectedRow) => selectedRow.id === row.id);
    if (index > -1) {
      // Si la fila ya está seleccionada, deseleccionarla
      this.selectedRows.splice(index, 1);
    } else {
      // Agregar fila a las seleccionadas
      this.selectedRows.push(row);
    }

    if (this.selectedRows.length > 0) {
      const lastSelectedRow = this.selectedRows[this.selectedRows.length - 1];
      this.areaSeleccionada = {
        nombre_area_seleccionada: lastSelectedRow.nombre,
        id_area_seleccionada: lastSelectedRow.id,
      };
      this.selectedAreaIdForTable = this.areaSeleccionada.id_area_seleccionada; // ✅ Usar variable específica para tabla
      this.nombreAreaNew = this.areaSeleccionada.nombre_area_seleccionada;

      this.cargoSeleccionado = {
        nombre_cargo_seleccionada: lastSelectedRow.nombre,
        id_cargo_seleccionado: lastSelectedRow.id,
        id_area_cargo_seleccionado: lastSelectedRow.area,
      };
      this.selectedCargoId = this.cargoSeleccionado.id_cargo_seleccionado;
      this.nombreCargoNew = this.cargoSeleccionado.nombre_cargo_seleccionada;
      this.selectedAreaIdForCargo = this.cargoSeleccionado.id_area_cargo_seleccionado; // ✅ Solo para cargos

    } else {
      // Limpiar perfilSeleccionado si no hay filas seleccionadas
      this.areaSeleccionada = {
        nombre_cliente_seleccionado: '',
      };
      this.selectedAreaIdForTable = null; // ✅ Limpiar selección de tabla
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
    this.selectedRows = []; // Deselecciona todas las filas
    this.selectedAreaIdForTable = null; // ✅ Limpiar selección de tabla
  }

  openModal(key: string): void {
    this.modals[key] = true;
    if (key == 'confirmacionModal') {
      this.deletedRow = this.selectedRows;
      console.log(this.deletedRow);
    }
    // ✅ Limpiar selección de área para cargos al abrir modales de creación
    if (key === 'crearCargo') {
      this.selectedAreaIdForCargo = null;
    }
  }

  closeModal(key: string): void {
    this.modals[key] = false;
    if (key === 'exitoModal') {
      this.cargarAreas();
      this.cargarCargos();
    }
    // ✅ Limpiar selección al cerrar modal de áreas
    if (key === 'areasModal') {
      this.dropdownOpen = false;
    }
  }

  checkValue(): void {}
}