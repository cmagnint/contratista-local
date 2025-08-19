import { Component, Inject, OnInit, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser, CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';
import { ContratistaApiService } from '../../../../services/contratista-api.service';
import { MatIconModule } from '@angular/material/icon';

interface Tramo {
  id?: number;
  origen: string;
  destino: string;
  comentario: string;
  unidad_pago: 'PASAJERO' | 'VIAJE';
}

@Component({
  selector: 'app-tramos',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatTableModule,
    MatIconModule
  ],
  templateUrl: './tramos.component.html',
  styleUrl: './tramos.component.css'
})
export class TramosComponent implements OnInit {
  // Variables principales
  public holding: string = '';
  public tramos: Tramo[] = [];
  public selectedRows: Tramo[] = [];
  public displayedColumns: string[] = ['id', 'origen', 'destino', 'comentario', 'unidad_pago'];
  
  // Modal states
  public modals: { [key: string]: boolean } = {
    exitoModal: false,
    errorModal: false,
    crearTramo: false,
    modificarTramo: false
  };

  // Form models
  public newTramo: Tramo = {
    origen: '',
    destino: '',
    comentario: '',
    unidad_pago: 'PASAJERO'
  };

  public selectedTramo: Tramo = {
    origen: '',
    destino: '',
    comentario: '',
    unidad_pago: 'PASAJERO'
  };

  public errorMessage: string = '';

  constructor(
    private contratistaApiService: ContratistaApiService,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {}

  ngOnInit(): void {
    if (isPlatformBrowser(this.platformId)) {
      this.holding = localStorage.getItem('holding_id') || '';
      this.loadTramos();
    }
  }

  // Carga inicial de tramos
  loadTramos(): void {
    this.contratistaApiService.get(`api_tramos/?holding=${this.holding}`).subscribe({
      next: (response) => {
        this.tramos = response;
      },
      error: (error) => {
        this.errorMessage = 'Error al cargar los tramos';
        this.openModal('errorModal');
      }
    });
  }

  // Crear nuevo tramo
  createTramo(): void {
    const data = {
      holding: this.holding,
      ...this.newTramo
    };

    this.contratistaApiService.post('api_tramos/', data).subscribe({
      next: (response) => {
        this.closeModal('crearTramo');
        this.loadTramos();
        this.openModal('exitoModal');
        this.resetNewTramo();
      },
      error: (error) => {
        this.errorMessage = 'Error al crear el tramo';
        this.openModal('errorModal');
      }
    });
  }

  // Actualizar tramo existente
  updateTramo(): void {
    const data = {
      id: this.selectedTramo.id,
      holding: this.holding,
      ...this.selectedTramo
    };

    this.contratistaApiService.put('api_tramos/', data).subscribe({
      next: (response) => {
        this.closeModal('modificarTramo');
        this.loadTramos();
        this.openModal('exitoModal');
      },
      error: (error) => {
        this.errorMessage = 'Error al modificar el tramo';
        this.openModal('errorModal');
      }
    });
  }

  // Eliminar tramos seleccionados
  eliminarTramosSeleccionados(): void {
    if (this.selectedRows.length === 0) return;

    const idsToDelete = this.selectedRows.map(row => row.id);
    
    this.contratistaApiService.delete('api_tramos/', { ids: idsToDelete }).subscribe({
      next: () => {
        this.loadTramos();
        this.selectedRows = [];
        this.openModal('exitoModal');
      },
      error: (error) => {
        this.errorMessage = 'Error al eliminar los tramos';
        this.openModal('errorModal');
      }
    });
  }

  // Helpers para la selección de filas
  isSelected(row: Tramo): boolean {
    return this.selectedRows.some(r => r.id === row.id);
  }

  selectRow(row: Tramo): void {
    const index = this.selectedRows.findIndex(r => r.id === row.id);
    if (index > -1) {
      this.selectedRows.splice(index, 1);
    } else {
      this.selectedRows.push(row);
    }

    if (this.selectedRows.length === 1) {
      this.selectedTramo = { ...this.selectedRows[0] };
    }
  }

  deseleccionarFila(event: MouseEvent): void {
    this.selectedRows = [];
  }

  // Modal handlers
  openModal(key: string): void {
    this.modals[key] = true;
  }

  closeModal(key: string): void {
    this.modals[key] = false;
  }

  // Reset form helpers
  resetNewTramo(): void {
    this.newTramo = {
      origen: '',
      destino: '',
      comentario: '',
      unidad_pago: 'PASAJERO'
    };
  }
}