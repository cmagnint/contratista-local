import { Component, OnInit, ViewChild, ElementRef, PLATFORM_ID, Inject } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatButtonModule } from '@angular/material/button';
import { MatNativeDateModule, provideNativeDateAdapter } from '@angular/material/core';
import { Chart, ChartConfiguration } from 'chart.js';
import { registerables } from 'chart.js';
import { ContratistaApiService } from '../../../../services/contratista-api.service';

// Register Chart.js components
Chart.register(...registerables);

@Component({
  selector: 'app-informe-rendimiento',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatDatepickerModule,
    MatButtonModule,
    MatNativeDateModule
  ],
  providers: [
    provideNativeDateAdapter()
  ],
  templateUrl: './informe-rendimiento.component.html',
  styleUrl: './informe-rendimiento.component.css'
})
export class InformeRendimientoComponent implements OnInit {
  @ViewChild('rendimientoChart') private chartRef!: ElementRef;
  
  filtroForm: FormGroup;
  clientes: any[] = [];
  supervisores: any[] = [];
  jefesCuadrilla: any[] = [];
  labores: any[] = [];
  chart: Chart | null = null;
  produccionData: any[] = [];
  holding: string = '';
  infoMessage: string = '';
  errorMessage: string = '';

  constructor(
    private fb: FormBuilder,
    private apiService: ContratistaApiService,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {
    // Initialize form with required validators
    this.filtroForm = this.fb.group({
      fecha_inicio: ['', Validators.required],
      fecha_fin: ['', Validators.required],
      cliente_id: [''],
      supervisor_id: [''],
      jefe_cuadrilla_id: [''],
      labor_id: ['']
    });
  }

  ngOnInit() {
    // Check browser environment before localStorage access
    if (isPlatformBrowser(this.platformId)) {
      this.holding = localStorage.getItem('holding_id') || '';
      if (!this.holding) {
        this.errorMessage = 'No se ha encontrado un holding válido';
        return;
      }
      this.cargarDatosIniciales();
    }
  }

  cargarDatosIniciales() {
    // Load initial data for dropdowns with error handling
    this.apiService.get(`api_clientes/?holding=${this.holding}`).subscribe({
      next: (response) => {
        console.log('Clientes: ',response)
        this.clientes = response.filter((cliente: any) => cliente.estado !== false);
      },
      error: (error) => {
        console.error('Error cargando clientes:', error);
        this.errorMessage = 'Error al cargar lista de clientes';
      }
    });

    this.apiService.get(`api_supervisores/${this.holding}`).subscribe({
      next: (response) => {
        console.log('Supervisores: ', response);
        this.supervisores = response.map((supervisor: any) => ({
          id: supervisor.id,
          nombre: supervisor.usuario_nombre || 'Sin nombre',
          rut: supervisor.usuario_rut
        }));
      },
      error: (error) => {
        console.error('Error cargando supervisores:', error);
        this.errorMessage = 'Error al cargar lista de supervisores';
      }
    });

    this.apiService.get(`api_jefes_cuadrilla/${this.holding}`).subscribe({
      next: (response) => {
        console.log('Jefes de Cuadrilla: ', response);
        this.jefesCuadrilla = response.map((jefe: any) => ({
          id: jefe.id,
          nombre: jefe.usuario_nombre || 'Sin nombre',
          rut: jefe.usuario_rut,
          supervisor_nombre: jefe.supervisor_nombre
        }));
      },
      error: (error) => {
        console.error('Error cargando jefes de cuadrilla:', error);
        this.errorMessage = 'Error al cargar lista de jefes de cuadrilla';
      }
    });

    this.apiService.get(`labores_comercial/?holding=${this.holding}`).subscribe({
      next: (response) => {
        this.labores = response.filter((labor: any) => labor.estado !== false);
      },
      error: (error) => {
        console.error('Error cargando labores:', error);
        this.errorMessage = 'Error al cargar lista de labores';
      }
    });
  }

  buscarDatos() {
    if (this.filtroForm.valid) {
      this.infoMessage = '';
      this.errorMessage = '';

      // Format dates and prepare form data
      const formData = {
        ...this.filtroForm.value,
        fecha_inicio: this.formatDate(this.filtroForm.value.fecha_inicio),
        fecha_fin: this.formatDate(this.filtroForm.value.fecha_fin),
        holding: this.holding
      };

      this.apiService.post('informe-rendimiento/', formData).subscribe({
        next: (response) => {
          if (response && response.length > 0) {
            this.produccionData = response;
            this.actualizarGrafico();
          } else {
            this.infoMessage = 'No se encontraron datos para los filtros seleccionados';
            if (this.chart) {
              this.chart.destroy();
              this.chart = null;
            }
          }
        },
        error: (error) => {
          console.error('Error en la búsqueda:', error);
          this.errorMessage = 'Error al obtener los datos de producción';
        }
      });
    } else {
      this.errorMessage = 'Por favor, complete todos los campos requeridos';
    }
  }

  private formatDate(date: Date): string {
    if (!date) return '';
    const d = new Date(date);
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }

  actualizarGrafico() {
    if (this.chart) {
      this.chart.destroy();
    }

    const ctx = this.chartRef.nativeElement.getContext('2d');
    
    const config: ChartConfiguration = {
      type: 'bar',
      data: {
        labels: this.produccionData.map(item => item.trabajador_nombre),
        datasets: [{
          label: 'Producción',
          data: this.produccionData.map(item => item.unidades_control),
          backgroundColor: 'rgba(75, 192, 192, 0.2)',
          borderColor: 'rgba(75, 192, 192, 1)',
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: 'Unidades de Control'
            }
          },
          x: {
            title: {
              display: true,
              text: 'Trabajadores'
            },
            ticks: {
              maxRotation: 45,
              minRotation: 45
            }
          }
        },
        plugins: {
          title: {
            display: true,
            text: 'Informe de Rendimiento por Trabajador',
            font: {
              size: 16
            }
          },
          legend: {
            position: 'top'
          },
          tooltip: {
            callbacks: {
              label: function(context) {
                let label = context.dataset.label || '';
                if (label) {
                  label += ': ';
                }
                if (context.parsed.y !== null) {
                  label += context.parsed.y.toFixed(2);
                }
                return label;
              }
            }
          }
        }
      }
    };

    this.chart = new Chart(ctx, config);
  }

  limpiarFiltros() {
    this.filtroForm.reset();
    if (this.chart) {
      this.chart.destroy();
      this.chart = null;
    }
    this.produccionData = [];
    this.infoMessage = '';
    this.errorMessage = '';
  }
}