import { Component, OnInit, Inject, PLATFORM_ID } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ContratistaApiService } from '../../../../services/contratista-api.service';

// Basic data interfaces
interface InformeData {
  clientes: Cliente[];
  transportistas: Transportista[];
}

interface Cliente {
  id: number;
  nombre: string;
}

interface Transportista {
  id: number;
  nombre: string;
  vehiculos: Vehiculo[];
}

interface Vehiculo {
  id: number;
  ppu: string;
  modelo: string;
}

// Interface for API response data
interface RegistroTransportista {
  fecha_inicio: string;
  fecha_fin: string;
  cliente: string;
  transportista: string;
  vehiculo: string;
  valor_pago: number;
  valor_facturacion: number;
}

@Component({
  selector: 'app-informe-transportista',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './informe-transportista.component.html',
  styleUrl: './informe-transportista.component.css'
})
export class InformeTransportistaComponent implements OnInit {
  // Date range fields
  startDate: string = '';
  endDate: string = '';

  // Selected IDs arrays for multiple selection
  selectedClienteIds: number[] = [];
  selectedTransportistaIds: number[] = [];
  selectedVehiculoIds: number[] = [];

  // Data arrays for checkboxes
  clientes: Cliente[] = [];
  transportistas: Transportista[] = [];
  vehiculos: Vehiculo[] = [];

  // Select all states
  allClientesSelected: boolean = false;
  allTransportistasSelected: boolean = false;
  allVehiculosSelected: boolean = false;

  // State management
  isLoading: boolean = false;
  holding: string = '';
  errorMessage: string = '';

  constructor(
    private apiService: ContratistaApiService,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {}

  ngOnInit() {
    if (isPlatformBrowser(this.platformId)) {
      this.holding = localStorage.getItem('holding_id') || '';
      this.loadInitialData();
    }
  }

  /**
   * Loads initial data for all checkboxes from the API
   */
  loadInitialData() {
    const endpoint = `informe-transportista/?holding=${this.holding}`;
    this.isLoading = true;

    this.apiService.get(endpoint).subscribe({
      next: (data: InformeData) => {
        this.clientes = data.clientes;
        this.transportistas = data.transportistas;
        this.updateAvailableVehiculos();
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error al cargar datos:', error);
        this.errorMessage = 'Error al cargar los datos iniciales';
        this.isLoading = false;
      }
    });
  }

  /**
   * Cliente checkbox handlers
   */
  toggleAllClientes() {
    this.allClientesSelected = !this.allClientesSelected;
    this.selectedClienteIds = this.allClientesSelected 
      ? this.clientes.map(c => c.id)
      : [];
  }

  toggleCliente(cliente: Cliente) {
    const index = this.selectedClienteIds.indexOf(cliente.id);
    if (index === -1) {
      this.selectedClienteIds.push(cliente.id);
    } else {
      this.selectedClienteIds.splice(index, 1);
    }
    this.updateClientesSelectAllState();
  }

  /**
   * Transportista checkbox handlers
   */
  toggleAllTransportistas() {
    this.allTransportistasSelected = !this.allTransportistasSelected;
    this.selectedTransportistaIds = this.allTransportistasSelected
      ? this.transportistas.map(t => t.id)
      : [];
    this.updateAvailableVehiculos();
    this.selectedVehiculoIds = []; // Reset vehicle selection
    this.allVehiculosSelected = false;
  }

  toggleTransportista(transportista: Transportista) {
    const index = this.selectedTransportistaIds.indexOf(transportista.id);
    if (index === -1) {
      this.selectedTransportistaIds.push(transportista.id);
    } else {
      this.selectedTransportistaIds.splice(index, 1);
    }
    this.updateTransportistasSelectAllState();
    this.updateAvailableVehiculos();
    this.selectedVehiculoIds = []; // Reset vehicle selection
    this.allVehiculosSelected = false;
  }

  /**
   * Vehiculo checkbox handlers
   */
  toggleAllVehiculos() {
    this.allVehiculosSelected = !this.allVehiculosSelected;
    this.selectedVehiculoIds = this.allVehiculosSelected
      ? this.vehiculos.map(v => v.id)
      : [];
  }

  toggleVehiculo(vehiculo: Vehiculo) {
    const index = this.selectedVehiculoIds.indexOf(vehiculo.id);
    if (index === -1) {
      this.selectedVehiculoIds.push(vehiculo.id);
    } else {
      this.selectedVehiculoIds.splice(index, 1);
    }
    this.updateVehiculosSelectAllState();
  }

  /**
   * Updates "Select All" checkbox states
   */
  private updateClientesSelectAllState() {
    this.allClientesSelected = 
      this.selectedClienteIds.length === this.clientes.length;
  }

  private updateTransportistasSelectAllState() {
    this.allTransportistasSelected = 
      this.selectedTransportistaIds.length === this.transportistas.length;
  }

  private updateVehiculosSelectAllState() {
    this.allVehiculosSelected = 
      this.selectedVehiculoIds.length === this.vehiculos.length && this.vehiculos.length > 0;
  }

  /**
   * Updates available vehicles based on selected transporters
   */
  private updateAvailableVehiculos() {
    if (this.selectedTransportistaIds.length === 0) {
      this.vehiculos = [];
      return;
    }

    this.vehiculos = this.transportistas
      .filter(t => this.selectedTransportistaIds.includes(t.id))
      .flatMap(t => t.vehiculos);
  }

  /**
   * Initiates report download process
   */
  downloadInforme() {
    if (!isPlatformBrowser(this.platformId)) {
      return;
    }

    if (!this.validateDates()) {
      return;
    }

    this.isLoading = true;
    const requestData = this.prepareRequestData();

    this.apiService.post('informe-transportista/', requestData).subscribe({
      next: (response: { registros: RegistroTransportista[], metadata: any }) => {
        this.generateAndDownloadCSV(response.registros);
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error al obtener datos del informe:', error);
        this.errorMessage = 'Error al generar el informe';
        this.isLoading = false;
      }
    });
  }

  /**
   * Validates the date range selection
   */
  private validateDates(): boolean {
    if (!this.startDate || !this.endDate) {
      this.errorMessage = 'Por favor seleccione un rango de fechas válido';
      return false;
    }
    return true;
  }

  /**
   * Prepares request data for the API
   */
  private prepareRequestData() {
    return {
      fecha_inicio: this.startDate,
      fecha_fin: this.endDate,
      cliente_ids: this.selectedClienteIds.length > 0 ? this.selectedClienteIds : null,
      transportista_ids: this.selectedTransportistaIds.length > 0 ? this.selectedTransportistaIds : null,
      vehiculo_ids: this.selectedVehiculoIds.length > 0 ? this.selectedVehiculoIds : null
    };
  }

  /**
   * Generates CSV content and triggers download
   */
  private generateAndDownloadCSV(data: any[]) {
    const headers = [
      'Fecha',
      'Cliente',
      'Empresa de Transporte',
      'Vehículo',
      'Chofer',
      'Cantidad Pasajeros',
      'Valor a Pagar',
      'Total Acumulado',
      'Unidad de Control',
      'Origen',
      'Destino'
    ];
  
    const rows = data.map(registro => [
      registro.fecha,
      registro.cliente,
      registro.empresa_transporte,
      registro.vehiculo,
      registro.chofer,
      registro.cantidad_pasajeros,
      this.formatCurrency(registro.valor_pago),
      this.formatCurrency(registro.total_acumulado),
      registro.unidad_control,
      registro.origen,
      registro.destino
    ]);
  
    const csvContent = [
      headers.join(','),
      ...rows.map(row => 
        row.map(value => 
          typeof value === 'string' ? `"${value.replace(/"/g, '""')}"` : value
        ).join(',')
      )
    ].join('\n');
  
    const blob = new Blob(['\ufeff' + csvContent], { 
      type: 'text/csv;charset=utf-8;' 
    });
    
    this.triggerDownload(blob);
  }

  /**
   * Handles the actual file download process
   */
  private triggerDownload(blob: Blob) {
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    const filename = `informe_transportista_${new Date().toISOString().split('T')[0]}.csv`;
    
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  }

  /**
   * Formats currency values according to Chilean standards
   */
  private formatCurrency(value: number): string {
    return value.toLocaleString('es-CL', {
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    });
  }
}