import { Component, Inject, OnInit, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser, CommonModule } from '@angular/common';
import { ContratistaApiService } from '../../../../../services/contratista-api.service';
import { ReactiveFormsModule } from '@angular/forms';
import { FormsModule } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';
import { JwtService } from '../../../../../services/jwt.service';

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
  // CONSTRUCTOR
  constructor(
    private apiService: ContratistaApiService,
    private jwtService: JwtService,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {}

  // MODALES
  public modals: { [key: string]: boolean } = {
    exitoModal: false,
    errorModal: false,
    crearArea: false,
    modificarArea: false,
    crearCargo: false,
    modificarCargo: false,
    confirmacionModalArea: false,
    confirmacionModalCargo: false,
  };

  // VARIABLES PARA ÁREAS
  public areaSeleccionada: any = {
    nombre_area_seleccionada: '',
    id_area_seleccionada: 0,
  };

  public nombreArea: string = '';
  public nombreAreaNew: string = '';
  public selectedAreaRows: any[] = []; // Filas seleccionadas de la tabla de áreas
  public areasCargadas: any[] = [];
  public selectedAreaForCargo: any = null; // Área seleccionada para crear/modificar cargos
  public deletedAreaRows: any[] = []; // Áreas para eliminar

  // VARIABLES PARA CARGOS
  public cargoSeleccionado: any = {
    nombre_cargo_seleccionado: '',
    id_cargo_seleccionado: 0,
    id_area_cargo_seleccionado: 0,
  };

  public nombreCargo: string = '';
  public nombreCargoNew: string = '';
  public cargosCargados: any[] = [];
  public selectedCargoRows: any[] = []; // Filas seleccionadas de la tabla de cargos
  public selectedCargoId: number | null = null;
  public deletedCargoRows: any[] = []; // Cargos para eliminar

  // VARIABLES GENERALES
  public errorMessage!: string;
  public holding: string = '';

  // COLUMNAS PARA TABLAS
  columnasDesplegadas = ['nombre'];
  columnasDesplegadasCargos = ['nombre', 'area'];

  // INICIALIZACIÓN
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

  // ===================================================
  // FUNCIONES CRUD PARA ÁREAS
  // ===================================================

  crearAreas(): void {
    let data = {
      holding: this.holding,
      nombre: this.nombreArea,
    };
    
    this.apiService.post('api_areas_administracion/', data).subscribe({
      next: (response) => {
        this.closeModal('crearArea');
        this.nombreArea = '';
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
    if (!this.areaSeleccionada.id_area_seleccionada || this.areaSeleccionada.id_area_seleccionada === 0) {
      this.errorMessage = 'No hay área seleccionada para modificar';
      this.openModal('errorModal');
      return;
    }

    let data = {
      holding: this.holding,
      id: this.areaSeleccionada.id_area_seleccionada,
      nombre: this.nombreAreaNew,
    };
    
    this.apiService.put('api_areas_administracion/', data).subscribe({
      next: (response) => {
        this.closeModal('modificarArea');
        this.nombreAreaNew = '';
        this.selectedAreaRows = [];
        this.selectedAreaForCargo = null;
        this.areaSeleccionada = {
          nombre_area_seleccionada: '',
          id_area_seleccionada: 0,
        };
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
    if (this.deletedAreaRows.length > 0) {
      const idsToDelete = this.deletedAreaRows.map((row) => row.id);
      this.apiService.delete('api_areas_administracion/', { ids: idsToDelete }).subscribe({
        next: () => {
          this.closeModal('confirmacionModalArea');
          this.selectedAreaRows = [];
          this.selectedAreaForCargo = null;
          this.cargarAreas();
          this.cargarCargos(); // Recargar cargos porque pueden haberse eliminado por cascada
          this.openModal('exitoModal');
          this.deletedAreaRows = [];
        },
        error: (error) => {
          this.openModal('errorModal');
          console.error('Error al eliminar áreas:', error);
        },
      });
    }
  }

  // ===================================================
  // FUNCIONES CRUD PARA CARGOS
  // ===================================================

  crearCargos(): void {
    if (!this.selectedAreaForCargo) {
      this.errorMessage = 'No hay área seleccionada para crear el cargo';
      this.openModal('errorModal');
      return;
    }

    let data = {
      holding: this.holding,
      nombre: this.nombreCargo,
      area: this.selectedAreaForCargo.id,
    };
    
    this.apiService.post('api_cargos_administracion/', data).subscribe({
      next: (response) => {
        console.log(response);
        this.closeModal('crearCargo');
        this.nombreCargo = '';
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
    if (!this.selectedCargoId || this.selectedCargoId === null) {
      this.errorMessage = 'No hay cargo seleccionado para modificar';
      this.openModal('errorModal');
      return;
    }

    let data = {
      holding: this.holding,
      id: this.selectedCargoId,
      nombre: this.nombreCargoNew,
      area: this.cargoSeleccionado.id_area_cargo_seleccionado, // Mantener el área original
    };
    
    this.apiService.put('api_cargos_administracion/', data).subscribe({
      next: (response) => {
        this.closeModal('modificarCargo');
        this.nombreCargoNew = '';
        this.selectedCargoRows = [];
        this.selectedCargoId = null;
        this.cargoSeleccionado = {
          nombre_cargo_seleccionado: '',
          id_cargo_seleccionado: 0,
          id_area_cargo_seleccionado: 0,
        };
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
    if (this.deletedCargoRows.length > 0) {
      const idsToDelete = this.deletedCargoRows.map((row) => row.id);
      this.apiService.delete('api_cargos_administracion/', { ids: idsToDelete }).subscribe({
        next: () => {
          this.closeModal('confirmacionModalCargo');
          this.selectedCargoRows = [];
          this.cargarCargos();
          this.openModal('exitoModal');
          this.deletedCargoRows = [];
        },
        error: (error) => {
          this.openModal('errorModal');
          console.error('Error al eliminar cargos:', error);
        },
      });
    }
  }

  // ===================================================
  // FUNCIONES DE SELECCIÓN DE FILAS - ÁREAS
  // ===================================================

  isAreaSelected(row: any): boolean {
    return this.selectedAreaRows.some((r) => r.id === row.id);
  }

  selectAreaRow(row: any): void {
    const index = this.selectedAreaRows.findIndex((selectedRow) => selectedRow.id === row.id);
    
    if (index > -1) {
      // Si la fila ya está seleccionada, deseleccionarla
      this.selectedAreaRows.splice(index, 1);
      
      // Si deseleccionamos el área que estaba marcada para cargos, la limpiamos
      if (this.selectedAreaForCargo && this.selectedAreaForCargo.id === row.id) {
        this.selectedAreaForCargo = null;
      }
    } else {
      // Agregar fila a las seleccionadas
      this.selectedAreaRows.push(row);
    }

    // Solo marcar un área para cargos si hay exactamente una seleccionada
    if (this.selectedAreaRows.length === 1) {
      this.selectedAreaForCargo = this.selectedAreaRows[0];
      
      // Actualizar datos para modificación
      this.areaSeleccionada = {
        nombre_area_seleccionada: this.selectedAreaRows[0].nombre,
        id_area_seleccionada: this.selectedAreaRows[0].id,
      };
      this.nombreAreaNew = this.areaSeleccionada.nombre_area_seleccionada;
    } else {
      // Si hay 0 o más de 1 área seleccionada, limpiar área para cargos
      this.selectedAreaForCargo = null;
      
      // Limpiar datos de modificación si no hay exactamente una selección
      this.areaSeleccionada = {
        nombre_area_seleccionada: '',
        id_area_seleccionada: 0,
      };
      this.nombreAreaNew = '';
    }
  }

  deseleccionarFilaAreas(event: MouseEvent): void {
    this.selectedAreaRows = [];
    this.selectedAreaForCargo = null;
    this.areaSeleccionada = {
      nombre_area_seleccionada: '',
      id_area_seleccionada: 0,
    };
    this.nombreAreaNew = '';
  }

  // ===================================================
  // FUNCIONES DE SELECCIÓN DE FILAS - CARGOS
  // ===================================================

  isCargoSelected(row: any): boolean {
    return this.selectedCargoRows.some((r) => r.id === row.id);
  }

  selectCargoRow(row: any): void {
    const index = this.selectedCargoRows.findIndex((selectedRow) => selectedRow.id === row.id);
    
    if (index > -1) {
      // Si la fila ya está seleccionada, deseleccionarla
      this.selectedCargoRows.splice(index, 1);
    } else {
      // Agregar fila a las seleccionadas
      this.selectedCargoRows.push(row);
    }

    // Actualizar datos para modificación si hay un solo cargo seleccionado
    if (this.selectedCargoRows.length === 1) {
      this.cargoSeleccionado = {
        nombre_cargo_seleccionado: this.selectedCargoRows[0].nombre,
        id_cargo_seleccionado: this.selectedCargoRows[0].id,
        id_area_cargo_seleccionado: this.selectedCargoRows[0].area,
      };
      this.selectedCargoId = this.cargoSeleccionado.id_cargo_seleccionado;
      this.nombreCargoNew = this.cargoSeleccionado.nombre_cargo_seleccionado;
    } else {
      // Limpiar si no hay o hay más de una selección
      this.cargoSeleccionado = {
        nombre_cargo_seleccionado: '',
        id_cargo_seleccionado: 0,
        id_area_cargo_seleccionado: 0,
      };
      this.selectedCargoId = null;
      this.nombreCargoNew = '';
    }
  }

  deseleccionarFilaCargos(event: MouseEvent): void {
    this.selectedCargoRows = [];
    this.cargoSeleccionado = {
      nombre_cargo_seleccionado: '',
      id_cargo_seleccionado: 0,
      id_area_cargo_seleccionado: 0,
    };
    this.selectedCargoId = null;
    this.nombreCargoNew = '';
  }

  // ===================================================
  // FUNCIONES DE MODALES
  // ===================================================

  openModal(key: string): void {
    this.modals[key] = true;
    
    if (key === 'confirmacionModalArea') {
      this.deletedAreaRows = [...this.selectedAreaRows];
      console.log('Áreas para eliminar:', this.deletedAreaRows);
    }
    
    if (key === 'confirmacionModalCargo') {
      this.deletedCargoRows = [...this.selectedCargoRows];
      console.log('Cargos para eliminar:', this.deletedCargoRows);
    }
  }

  closeModal(key: string): void {
    this.modals[key] = false;
    
    if (key === 'exitoModal') {
      this.cargarAreas();
      this.cargarCargos();
    }
  }

  // ===================================================
  // FUNCIONES AUXILIARES (MANTENER COMPATIBILIDAD)
  // ===================================================

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

  checkValue(): void {}
}