import { Component, Inject, OnInit, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser, CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';
import { ContratistaApiService } from '../../../../services/contratista-api.service';
import { MatIconModule } from '@angular/material/icon';

interface FolioTransportista {
  id?: number;
  holding: number;
  folio_comercial: number;
  nombre_folio_comercial?: string;
  valor_pago_transportista: number;
  valor_facturacion_transportista: number;
  tramo: number;
  nombre_tramo?: string;
}

@Component({
  selector: 'app-folio-transportista',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatTableModule,
    MatIconModule
  ],
  templateUrl: './folio-transportista.component.html',
  styleUrl: './folio-transportista.component.css'
})
export class FolioTransportistaComponent implements OnInit {
  // Variables principales
  public holding: string = '';
  public folios: FolioTransportista[] = [];
  public selectedRows: FolioTransportista[] = [];
  public foliosComerciales: any[] = [];
  public tramos: any[] = [];
  public errorMessage: string = '';

  // Columns para la tabla
  public displayedColumns: string[] = [
    'id', 
    'nombre_folio_comercial',
    'valor_pago_transportista',
    'valor_facturacion_transportista',
    'nombre_tramo'
  ];

  // Estados de los modales
  public modals: { [key: string]: boolean } = {
    exitoModal: false,
    errorModal: false,
    crearFolio: false,
    modificarFolio: false,
    confirmacionModal: false
  };

  // Modelos para formularios
  public newFolio: FolioTransportista = {
    holding: 0,
    folio_comercial: 0,
    valor_pago_transportista: 0,
    valor_facturacion_transportista: 0,
    tramo: 0
  };

  public selectedFolio: FolioTransportista = {
    holding: 0,
    folio_comercial: 0,
    valor_pago_transportista: 0,
    valor_facturacion_transportista: 0,
    tramo: 0
  };

  public deletedRow: FolioTransportista[] = [];

  constructor(
    private contratistaApiService: ContratistaApiService,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {}

  ngOnInit(): void {
    if (isPlatformBrowser(this.platformId)) {
      this.holding = localStorage.getItem('holding_id') || '';
      this.cargarDatos();
    }
  }

  cargarDatos(): void {
    this.cargarFolios();
    this.cargarFoliosComerciales();
    this.cargarTramos();
  }

  cargarFolios(): void {
    this.contratistaApiService.get(`api_folio_transportista/?holding=${this.holding}`).subscribe({
      next: (response) => {
        this.folios = response;
      },
      error: (error) => {
        this.errorMessage = 'Error al cargar los folios';
        this.openModal('errorModal');
      }
    });
  }

  cargarFoliosComerciales(): void {
    this.contratistaApiService.get(`folio_comercial/?holding=${this.holding}`).subscribe({
      next: (response) => {
        this.foliosComerciales = response;
      },
      error: (error) => {
        console.error('Error al cargar folios comerciales:', error);
      }
    });
  }

  cargarTramos(): void {
    this.contratistaApiService.get(`api_tramos/?holding=${this.holding}`).subscribe({
      next: (response) => {
        this.tramos = response;
      },
      error: (error) => {
        console.error('Error al cargar tramos:', error);
      }
    });
  }

  crearFolio(): void {
    const data = {
      holding: parseInt(this.holding), // Convertimos el holding a número
      folio_comercial: this.newFolio.folio_comercial,
      valor_pago_transportista: this.newFolio.valor_pago_transportista,
      valor_facturacion_transportista: this.newFolio.valor_facturacion_transportista,
      tramo: this.newFolio.tramo
    };
  
    this.contratistaApiService.post('api_folio_transportista/', data).subscribe({
      next: (response) => {
        this.closeModal('crearFolio');
        this.cargarFolios();
        this.openModal('exitoModal');
        this.resetNewFolio();
      },
      error: (error) => {
        this.errorMessage = 'Error al crear el folio';
        this.openModal('errorModal');
      }
    });
  }

  modificarFolio(): void {
    const data = {
      id: this.selectedFolio.id,
      holding: parseInt(this.holding), // Convertimos el holding a número
      folio_comercial: this.selectedFolio.folio_comercial,
      valor_pago_transportista: this.selectedFolio.valor_pago_transportista,
      valor_facturacion_transportista: this.selectedFolio.valor_facturacion_transportista,
      tramo: this.selectedFolio.tramo
    };
  
    this.contratistaApiService.put('api_folio_transportista/', data).subscribe({
      next: (response) => {
        this.closeModal('modificarFolio');
        this.cargarFolios();
        this.openModal('exitoModal');
      },
      error: (error) => {
        this.errorMessage = 'Error al modificar el folio';
        this.openModal('errorModal');
      }
    });
  }
  eliminarFoliosSeleccionados(): void {
    if (this.deletedRow.length > 0) {
      const idsToDelete = this.deletedRow.map(row => row.id);
      
      this.contratistaApiService.delete('api_folio_transportista/', { ids: idsToDelete }).subscribe({
        next: () => {
          this.closeModal('confirmacionModal');
          this.cargarFolios();
          this.openModal('exitoModal');
          this.deletedRow = [];
        },
        error: (error) => {
          this.errorMessage = 'Error al eliminar los folios';
          this.openModal('errorModal');
        }
      });
    }
  }

  // Helpers de selección
  isSelected(row: FolioTransportista): boolean {
    return this.selectedRows.some(r => r.id === row.id);
  }

  selectRow(row: FolioTransportista): void {
    const index = this.selectedRows.findIndex(r => r.id === row.id);
    if (index > -1) {
      this.selectedRows.splice(index, 1);
    } else {
      this.selectedRows.push(row);
    }

    if (this.selectedRows.length === 1) {
      this.selectedFolio = { ...this.selectedRows[0] };
    }
  }

  deseleccionarFila(event: MouseEvent): void {
    this.selectedRows = [];
  }

  // Manejo de modales
  openModal(key: string): void {
    this.modals[key] = true;
    if (key === 'confirmacionModal') {
      this.deletedRow = this.selectedRows;
    }
  }

  closeModal(key: string): void {
    this.modals[key] = false;
    if (key === 'exitoModal') {
      this.cargarFolios();
    }
  }

  // Reset de formularios
  resetNewFolio(): void {
    this.newFolio = {
      holding: 0,
      folio_comercial: 0,
      valor_pago_transportista: 0,
      valor_facturacion_transportista: 0,
      tramo: 0
    };
  }
}