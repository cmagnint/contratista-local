// haberes-descuentos.component.ts
import { Component, Inject, OnInit, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser, CommonModule } from '@angular/common';
import { ContratistaApiService } from '../../../../services/contratista-api.service';
import { ReactiveFormsModule } from '@angular/forms';
import { FormsModule } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';

@Component({
  selector: 'app-haberes-descuentos',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatTableModule,
    FormsModule
  ],
  templateUrl: './haberes-descuentos.component.html',
  styleUrl: './haberes-descuentos.component.css'
})
export class HaberesDescuentosComponent implements OnInit {
  // VARIABLES
  constructor(
    private apiService: ContratistaApiService,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {}

  // Booleanos para abrir o cerrar ventanas
  public modals: { [key: string]: boolean } = {
    exitoModal: false,
    errorModal: false,
    crearHaber: false,
    modificarHaber: false,
    crearDescuento: false,
    modificarDescuento: false,
    confirmacionModal: false,
  };

  // VARIABLES PARA HABERES
  public haberSeleccionado: any = {
    nombre_haber_seleccionado: '',
    id_haber_seleccionado: 0,
    imponible_haber_seleccionado: false,
    orden_haber_seleccionado: 0,
    tipo_valor_haber_seleccionado: '',
    cuenta_contable_1_haber_seleccionado: '',
    cuenta_contable_2_haber_seleccionado: '',
    ubicacion_liquidacion_haber_seleccionado: '',
  };

  public nuevoHaber: any = {
    nombre: '',
    imponible: false,
    orden: 0,
    tipo_valor: 'MONTO',
    cuenta_contable_1: '',
    cuenta_contable_2: '',
    ubicacion_liquidacion: '',
  };

  public haberesCargados: any[] = [];
  public selectedHaberRows: any[] = [];
  public selectedHaberId: number | null = null;
  
  // VARIABLES PARA DESCUENTOS
  public descuentoSeleccionado: any = {
    nombre_descuento_seleccionado: '',
    id_descuento_seleccionado: 0,
    orden_descuento_seleccionado: 0,
    cuota_descuento_seleccionado: false,
    cuenta_contable_descuento_seleccionado: '',
  };

  public nuevoDescuento: any = {
    nombre: '',
    orden: 0,
    cuota: false,
    cuenta_contable: '',
  };

  public descuentosCargados: any[] = [];
  public selectedDescuentoRows: any[] = [];
  public selectedDescuentoId: number | null = null;

  public errorMessage!: string;
  public holding: string = '';
  public tipoEliminacion: string = ''; // 'haber' o 'descuento'
  public deleteItems: any[] = [];

  // COLUMNAS PARA TABLAS
  columnasDesplegadasHaberes = ['id', 'nombre', 'imponible', 'tipo_valor', 'orden'];
  columnasDesplegadasDescuentos = ['id', 'nombre', 'cuota', 'orden'];

  // FUNCIONES
  ngOnInit(): void {
    if (isPlatformBrowser(this.platformId)) {
      this.holding = localStorage.getItem('holding_id') || '';
      this.cargarHaberes();
      this.cargarDescuentos();
    }
  }

  // FUNCIONES CRUD PARA HABERES
  crearHaberes(): void {
    let data = {
      holding: this.holding,
      ...this.nuevoHaber
    };
    
    this.apiService.post('api_haberes/', data).subscribe({
      next: (response) => {
        this.closeModal('crearHaber');
        this.cargarHaberes();
        this.openModal('exitoModal');
        // Reiniciar el formulario
        this.nuevoHaber = {
          nombre: '',
          imponible: false,
          orden: 0,
          tipo_valor: 'MONTO',
          cuenta_contable_1: '',
          cuenta_contable_2: '',
          ubicacion_liquidacion: '',
        };
      },
      error: (error) => {
        this.errorMessage = error.error?.message || "Error al crear el haber";
        this.openModal('errorModal');
      },
    });
  }

  cargarHaberes(): void {
    this.apiService.get(`api_haberes/?holding=${this.holding}`).subscribe({
      next: (response) => {
        // Ordenar los haberes por el campo orden
        this.haberesCargados = response.sort((a: { orden: number; }, b: { orden: number; }) => a.orden - b.orden);
      },
      error: (error) => {
        console.error('Error al recibir los haberes:', error);
      },
    });
  }

  modificarHaberes(): void {
    if (!this.selectedHaberId) return;
    
    let data = {
      holding: this.holding,
      id: this.selectedHaberId,
      ...this.haberSeleccionado
    };
    
    // Eliminar propiedades con prefijo
    Object.keys(data).forEach(key => {
      if (key.includes('_seleccionado')) {
        const newKey = key.replace('_haber_seleccionado', '');
        data[newKey] = data[key];
        delete data[key];
      }
    });

    this.apiService.put('api_haberes/', data).subscribe({
      next: (response) => {
        this.closeModal('modificarHaber');
        this.cargarHaberes();
        this.openModal('exitoModal');
      },
      error: (error) => {
        this.errorMessage = error.error?.message || "Error al modificar el haber";
        this.openModal('errorModal');
      },
    });
  }

  eliminarHaberesSeleccionados(): void {
    if (this.deleteItems.length > 0) {
      const idsToDelete = this.deleteItems.map((row) => row.id);
      this.apiService.delete('api_haberes/', { ids: idsToDelete }).subscribe({
        next: () => {
          this.closeModal('confirmacionModal');
          this.cargarHaberes();
          this.openModal('exitoModal');
          this.deleteItems = []; // Limpiar la selección después de eliminar
          this.selectedHaberRows = [];
        },
        error: (error) => {
          this.errorMessage = error.error?.message || "Error al eliminar haberes";
          this.openModal('errorModal');
        },
      });
    }
  }

  // FUNCIONES CRUD PARA DESCUENTOS
  crearDescuentos(): void {
    let data = {
      holding: this.holding,
      ...this.nuevoDescuento
    };
    
    this.apiService.post('api_descuentos/', data).subscribe({
      next: (response) => {
        this.closeModal('crearDescuento');
        this.cargarDescuentos();
        this.openModal('exitoModal');
        // Reiniciar el formulario
        this.nuevoDescuento = {
          nombre: '',
          orden: 0,
          cuota: false,
          cuenta_contable: '',
        };
      },
      error: (error) => {
        this.errorMessage = error.error?.message || "Error al crear el descuento";
        this.openModal('errorModal');
      },
    });
  }

  cargarDescuentos(): void {
    this.apiService.get(`api_descuentos/?holding=${this.holding}`).subscribe({
      next: (response) => {
        // Ordenar los descuentos por el campo orden
        this.descuentosCargados = response.sort((a: { orden: number; }, b: { orden: number; }) => a.orden - b.orden);
      },
      error: (error) => {
        console.error('Error al recibir los descuentos:', error);
      },
    });
  }

  modificarDescuentos(): void {
    if (!this.selectedDescuentoId) return;
    
    let data = {
      holding: this.holding,
      id: this.selectedDescuentoId,
      ...this.descuentoSeleccionado
    };
    
    // Eliminar propiedades con prefijo
    Object.keys(data).forEach(key => {
      if (key.includes('_seleccionado')) {
        const newKey = key.replace('_descuento_seleccionado', '');
        data[newKey] = data[key];
        delete data[key];
      }
    });

    this.apiService.put('api_descuentos/', data).subscribe({
      next: (response) => {
        this.closeModal('modificarDescuento');
        this.cargarDescuentos();
        this.openModal('exitoModal');
      },
      error: (error) => {
        this.errorMessage = error.error?.message || "Error al modificar el descuento";
        this.openModal('errorModal');
      },
    });
  }

  eliminarDescuentosSeleccionados(): void {
    if (this.deleteItems.length > 0) {
      const idsToDelete = this.deleteItems.map((row) => row.id);
      this.apiService.delete('api_descuentos/', { ids: idsToDelete }).subscribe({
        next: () => {
          this.closeModal('confirmacionModal');
          this.cargarDescuentos();
          this.openModal('exitoModal');
          this.deleteItems = []; // Limpiar la selección después de eliminar
          this.selectedDescuentoRows = [];
        },
        error: (error) => {
          this.errorMessage = error.error?.message || "Error al eliminar descuentos";
          this.openModal('errorModal');
        },
      });
    }
  }

  // FUNCIONES COMUNES
  isHaberSelected(row: any): boolean {
    return this.selectedHaberRows.some((r) => r.id === row.id);
  }

  isDescuentoSelected(row: any): boolean {
    return this.selectedDescuentoRows.some((r) => r.id === row.id);
  }

  selectHaberRow(row: any): void {
    const index = this.selectedHaberRows.findIndex((selectedRow) => selectedRow.id === row.id);
    if (index > -1) {
      // Si la fila ya está seleccionada, deseleccionarla
      this.selectedHaberRows.splice(index, 1);
      this.selectedHaberId = null;
    } else {
      // Agregar fila a las seleccionadas (limpiando selección previa)
      this.selectedHaberRows = [row];
      this.selectedHaberId = row.id;
      
      // Actualizar datos del haber seleccionado
      this.haberSeleccionado = {
        nombre_haber_seleccionado: row.nombre,
        imponible_haber_seleccionado: row.imponible,
        orden_haber_seleccionado: row.orden,
        tipo_valor_haber_seleccionado: row.tipo_valor,
        cuenta_contable_1_haber_seleccionado: row.cuenta_contable_1,
        cuenta_contable_2_haber_seleccionado: row.cuenta_contable_2,
        ubicacion_liquidacion_haber_seleccionado: row.ubicacion_liquidacion,
      };
    }
  }

  selectDescuentoRow(row: any): void {
    const index = this.selectedDescuentoRows.findIndex((selectedRow) => selectedRow.id === row.id);
    if (index > -1) {
      // Si la fila ya está seleccionada, deseleccionarla
      this.selectedDescuentoRows.splice(index, 1);
      this.selectedDescuentoId = null;
    } else {
      // Agregar fila a las seleccionadas (limpiando selección previa)
      this.selectedDescuentoRows = [row];
      this.selectedDescuentoId = row.id;
      
      // Actualizar datos del descuento seleccionado
      this.descuentoSeleccionado = {
        nombre_descuento_seleccionado: row.nombre,
        orden_descuento_seleccionado: row.orden,
        cuota_descuento_seleccionado: row.cuota,
        cuenta_contable_descuento_seleccionado: row.cuenta_contable,
      };
    }
  }

  deselectHaberRows(event: MouseEvent) {
    this.selectedHaberRows = []; // Deselecciona todas las filas
    this.selectedHaberId = null;
  }

  deselectDescuentoRows(event: MouseEvent) {
    this.selectedDescuentoRows = []; // Deselecciona todas las filas
    this.selectedDescuentoId = null;
  }

  openModal(key: string, tipo?: string): void {
    this.modals[key] = true;
    if (key === 'confirmacionModal') {
      this.tipoEliminacion = tipo || '';
      if (tipo === 'haber') {
        this.deleteItems = this.selectedHaberRows;
      } else if (tipo === 'descuento') {
        this.deleteItems = this.selectedDescuentoRows;
      }
    }
  }

  closeModal(key: string): void {
    this.modals[key] = false;
    if (key === 'exitoModal') {
      this.cargarHaberes();
      this.cargarDescuentos();
    }
  }

  getTipoValorText(tipo: string): string {
    const opciones: { [key: string]: string } = {
      'CANTIDAD': 'Por Cantidad',
      'MONTO': 'Monto Fijo'
    };
    return opciones[tipo] || tipo;
  }
}