import { Component, OnInit, PLATFORM_ID, Inject } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { FormGroup, FormBuilder, Validators } from '@angular/forms';
import { ContratistaApiService } from '../../../../services/contratista-api.service';

// Interface definitions for strong typing
interface Fundo {
  id: number;
  nombre_campo: string;
}

interface Supervisor {
  id: number;
  nombre: string;
}

interface Casa {
  id: number;
  nombre: string;
}

interface Produccion {
  nombre_labor: string;
  cantidad: number;
  unidad_medida: string;
  valor_total: number;
}

interface ProduccionCSV {
  nombre_trabajador: string;
  rut_trabajador: string;
  fecha_produccion: string;
  valor_dia: number;
}

interface InformeResumen {
  total_pago: number;
  total_registros: number;
}

@Component({
  selector: 'app-informe-pago',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule],
  templateUrl: './informe-pago.component.html',
  styleUrl: './informe-pago.component.css'
})
export class InformePagoComponent implements OnInit {
  filterForm: FormGroup;
  fundos: Fundo[] = [];
  supervisores: Supervisor[] = [];
  casas: Casa[] = [];
  producciones: Produccion[] = [];
  resumen: InformeResumen | null = null;
  isLoading: boolean = false;
  hasError: boolean = false;
  errorMessage: string = '';
  showResults: boolean = false;
  
  constructor(
    private fb: FormBuilder,
    @Inject(PLATFORM_ID) private platformId: Object,
    private contratistaApi: ContratistaApiService
  ) {    
    // Initialize form with required date fields
    this.filterForm = this.fb.group({
      fechaDesde: ['', Validators.required],
      fechaHasta: ['', Validators.required],
      fundoId: [''],
      supervisorId: [''],
      casaId: ['']
    });
  }

  ngOnInit() {
    if(isPlatformBrowser(this.platformId)) {
      const holdingId = localStorage.getItem('holding_id');
      if (holdingId) {
        this.loadDropdownData(holdingId);
      }
    }
  }

  loadDropdownData(holdingId: string) {
    this.isLoading = true;
    this.contratistaApi.get(`variables-dropdown-informe-pago/?holding=${holdingId}`).subscribe({
      next: (response) => {
        this.fundos = response.fundos;
        this.supervisores = response.supervisores;
        this.casas = response.casas;
        this.isLoading = false;
      },
      error: (error) => {
        this.handleError('Error al cargar los datos iniciales');
        this.isLoading = false;
      }
    });
  }

  generateReport() {
    this.showResults = false;
    this.producciones = [];
    this.resumen = null;
    
    if (!this.filterForm.get('fechaDesde')?.valid || !this.filterForm.get('fechaHasta')?.valid) {
      this.handleError('Por favor seleccione un rango de fechas válido');
      return;
    }

    const holdingId = localStorage.getItem('holding_id');
    if (!holdingId) {
      this.handleError('No se encontró el ID del holding');
      return;
    }

    const filters = this.filterForm.value;
    this.isLoading = true;
    
    const requestBody = {
      holding: holdingId,
      fecha_inicio: filters.fechaDesde,
      fecha_fin: filters.fechaHasta,
      fundo_id: filters.fundoId || null,
      supervisor_id: filters.supervisorId || null,
      casa_id: filters.casaId || null
    };

    this.contratistaApi.post('informe-pago/generar/', requestBody).subscribe({
      next: (response) => {
        this.producciones = response.producciones;
        this.resumen = response.resumen;
        this.isLoading = false;
        this.showResults = true;
      },
      error: (error) => {
        this.handleError('Error al generar el informe');
        this.isLoading = false;
      }
    });
  }

  async downloadCSV() {
    try {
      this.isLoading = true;
      
      // Validate form and get date range
      const filters = this.filterForm.value;
      if (!filters.fechaDesde || !filters.fechaHasta) {
        this.handleError('Por favor seleccione un rango de fechas válido');
        return;
      }

      // Get holding ID from localStorage
      const holdingId = localStorage.getItem('holding_id');
      if (!holdingId) {
        this.handleError('No se encontró el ID del holding');
        return;
      }

      // Prepare request body with all filters
      const requestBody = {
        holding: holdingId,
        fecha_inicio: filters.fechaDesde,
        fecha_fin: filters.fechaHasta,
        fundo_id: filters.fundoId || null,
        supervisor_id: filters.supervisorId || null,
        casa_id: filters.casaId || null
      };

      // Get the CSV data from our specialized endpoint
      const response = await this.contratistaApi.post('informe-pago/csv/', requestBody).toPromise();
      
      // Generate CSV content from the response data
      const csvContent = this.generateCSVContent(
        response.producciones,
        response.fecha_inicio,
        response.fecha_fin
      );
      
      // Create and trigger download
      const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' });
      const link = document.createElement('a');
      const filename = `informe_pago_${filters.fechaDesde}_${filters.fechaHasta}.csv`;
      
      // Check for IE/Edge browsers using type assertion
      const nav = navigator as any;
      if (nav.msSaveBlob) { // IE10+
        nav.msSaveBlob(blob, filename);
      } else {
        link.href = URL.createObjectURL(blob);
        link.setAttribute('download', filename);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      }

      this.isLoading = false;
    } catch (error) {
      this.handleError('Error al generar el archivo CSV');
      this.isLoading = false;
    }
  }

  private generateCSVContent(producciones: ProduccionCSV[], fechaInicio: string, fechaFin: string): string {
    // Group productions by worker
    const workerProductions: {
      [key: string]: {
        nombre: string;
        rut: string;
        dailyEarnings: { [key: string]: number };
        totalEarnings: number;
      };
    } = {};
    
    // Create date range array
    const dateRange = this.generateDateRange(new Date(fechaInicio), new Date(fechaFin));

    // Process production data
    producciones.forEach(prod => {
      const workerId = prod.rut_trabajador;
      
      // Initialize worker data if not exists
      if (!workerProductions[workerId]) {
        workerProductions[workerId] = {
          nombre: prod.nombre_trabajador,
          rut: prod.rut_trabajador,
          dailyEarnings: {},
          totalEarnings: 0
        };
        
        // Initialize all dates with 0
        dateRange.forEach(date => {
          const dateKey = date.toISOString().split('T')[0];
          workerProductions[workerId].dailyEarnings[dateKey] = 0;
        });
      }

      // Add daily earnings
      const dateKey = prod.fecha_produccion;
      workerProductions[workerId].dailyEarnings[dateKey] = 
        (workerProductions[workerId].dailyEarnings[dateKey] || 0) + prod.valor_dia;
      workerProductions[workerId].totalEarnings += prod.valor_dia;
    });

    // Generate headers
    const headers = [
      'Nombre Trabajador',
      'RUT Trabajador',
      ...dateRange.map(date => {
        const formattedDate = date.toISOString().split('T')[0];
        return `${formattedDate} (Monto)`;
      }),
      'Pago Total'
    ];

    // Generate rows
    const rows = Object.values(workerProductions).map(worker => {
      const dailyValues = dateRange.map(date => {
        const dateKey = date.toISOString().split('T')[0];
        return worker.dailyEarnings[dateKey] || 0;
      });

      return [
        worker.nombre,
        worker.rut,
        ...dailyValues,
        worker.totalEarnings
      ];
    });

    // Combine and format
    const csvRows = [headers, ...rows];
    return csvRows.map(row => 
      row.map(value => {
        if (typeof value === 'string') {
          // Escape quotes and wrap strings in quotes
          return `"${value.replace(/"/g, '""')}"`;
        } else if (typeof value === 'number') {
          // Format numbers with Chilean format
          return value.toLocaleString('es-CL', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
          });
        }
        return value;
      }).join(',')
    ).join('\n');
  }

  private generateDateRange(startDate: Date, endDate: Date): Date[] {
    const dates: Date[] = [];
    const currentDate = new Date(startDate);

    // Generate array of dates between start and end
    while (currentDate <= endDate) {
      dates.push(new Date(currentDate));
      currentDate.setDate(currentDate.getDate() + 1);
    }

    return dates;
  }

  private handleError(message: string) {
    this.hasError = true;
    this.errorMessage = message;
    setTimeout(() => {
      this.hasError = false;
      this.errorMessage = '';
    }, 5000);
  }
}