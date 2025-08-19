import { Component, OnInit, Inject, PLATFORM_ID } from '@angular/core';
import { CommonModule, DatePipe, isPlatformBrowser } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatTableModule } from '@angular/material/table';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatSortModule } from '@angular/material/sort';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { ContratistaApiService } from '../../../../services/contratista-api.service';
@Component({
  selector: 'app-liquidaciones',
  standalone: true,
  imports: [
    CommonModule, 
    FormsModule,
    ReactiveFormsModule,
    MatCardModule,
    MatButtonModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatDatepickerModule,
    MatNativeDateModule,
    MatTableModule,
    MatPaginatorModule,
    MatSortModule,
    MatProgressSpinnerModule,
    MatIconModule,
    MatTooltipModule
  ],
  templateUrl: './liquidaciones.component.html',
  styleUrls: ['./liquidaciones.component.css'],
  providers: [DatePipe]
})
export class LiquidacionesComponent implements OnInit {
  filtroForm: FormGroup;
  
  // Datos para los dropdowns
  sociedades: any[] = [];
  clientes: any[] = [];
  fundos: any[] = [];
  casas: any[] = [];
  
  // Estado de carga
  cargando: boolean = false;
  cargandoFundos: boolean = false;
  mensajeError: string = '';
  liquidacionesGeneradas: boolean = false;
  
  // Opciones de meses y años para los selectores
  meses = [
    { valor: 1, nombre: 'Enero' },
    { valor: 2, nombre: 'Febrero' },
    { valor: 3, nombre: 'Marzo' },
    { valor: 4, nombre: 'Abril' },
    { valor: 5, nombre: 'Mayo' },
    { valor: 6, nombre: 'Junio' },
    { valor: 7, nombre: 'Julio' },
    { valor: 8, nombre: 'Agosto' },
    { valor: 9, nombre: 'Septiembre' },
    { valor: 10, nombre: 'Octubre' },
    { valor: 11, nombre: 'Noviembre' },
    { valor: 12, nombre: 'Diciembre' }
  ];
  
  years: number[] = [];
  
  // ID del holding actual
  holding: string = '';
  
  constructor(
    private fb: FormBuilder,
    private apiService: ContratistaApiService,
    private datePipe: DatePipe,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {
    // Generar lista de años (últimos 5 años hasta el actual)
    const yearActual = new Date().getFullYear();
    for (let i = 0; i < 5; i++) {
      this.years.push(yearActual - i);
    }
    
    // Inicializar formulario con mes y año actual
    const hoy = new Date();
    this.filtroForm = this.fb.group({
      sociedad_id: ['', Validators.required],
      mes: [hoy.getMonth() + 1, Validators.required],
      year: [hoy.getFullYear(), Validators.required],
      cliente_id: [''],
      fundo_id: [{value: '', disabled: true}], // Inicialmente deshabilitado
      casa_id: ['']
    });
    
    // Añadir observador al cambio de cliente para cargar fundos
    this.filtroForm.get('cliente_id')?.valueChanges.subscribe(clienteId => {
      if (clienteId) {
        this.cargandoFundos = true;
        // Habilitar el control de fundo cuando hay un cliente seleccionado
        this.filtroForm.get('fundo_id')?.enable();
        
        this.cargarFundosPorCliente(clienteId);
      } else {
        this.fundos = [];
        // Restablecer y deshabilitar el control de fundo cuando no hay cliente
        this.filtroForm.get('fundo_id')?.setValue('');
        this.filtroForm.get('fundo_id')?.disable();
      }
    });
  }
  
  ngOnInit(): void {
    if (isPlatformBrowser(this.platformId)) {
      // Usar localStorage solo si estamos en el navegador
      this.holding = localStorage.getItem('holding_id') || '';
      if (this.holding) {
        this.cargarDatosIniciales();
      } else {
        this.mensajeError = 'No se pudo determinar el ID del holding';
      }
    }
  }
  
  cargarDatosIniciales(): void {
    // Cargar sociedades
    this.apiService.get(`api_sociedad/?holding=${this.holding}`).subscribe({
      next: (response) => {
        this.sociedades = response;
      },
      error: (error) => {
        console.error('Error al recibir las sociedades:', error);
        this.mensajeError = 'Error al cargar las sociedades';
      }
    });
    
    // Cargar clientes
    this.apiService.get(`api_clientes/?holding=${this.holding}`).subscribe({
      next: (response) => {
        this.clientes = response;
      },
      error: (error) => {
        console.error('Error al recibir los clientes:', error);
        this.mensajeError = 'Error al cargar los clientes';
      }
    });
    
    // Cargar casas
    this.apiService.get(`api_casas_trabajadores/?holding=${this.holding}`).subscribe({
      next: (data) => {
        this.casas = data;
        console.log('Casas cargadas:', this.casas.length);
      },
      error: (err) => {
        console.error('Error cargando casas:', err);
        this.mensajeError = 'Error cargando datos de casas';
      }
    });
  }
  
  cargarFundosPorCliente(clienteId: number): void {
    this.fundos = [];
    
    this.apiService.get(`api_campos_clientes/${clienteId}/`).subscribe({
      next: (data) => {
        this.fundos = data;
        this.cargandoFundos = false;
        console.log('Fundos cargados para cliente:', this.fundos.length);
      },
      error: (err) => {
        console.error('Error cargando fundos:', err);
        this.mensajeError = 'Error cargando datos de fundos';
        this.cargandoFundos = false;
      }
    });
  }
  
  generarLiquidaciones(): void {
    if (this.filtroForm.invalid) {
      return;
    }
    
    this.cargando = true;
    this.liquidacionesGeneradas = false;
    this.mensajeError = '';
    
    const formValues = this.filtroForm.getRawValue();
    const params = {
      holding_id: this.holding,
      sociedad_id: formValues.sociedad_id,
      mes: formValues.mes,
      year: formValues.year,
      cliente_id: formValues.cliente_id || null,
      fundo_id: formValues.fundo_id || null,
      casa_id: formValues.casa_id || null
    };
    
    console.log('Enviando parámetros para generar liquidaciones:', params);
    
    // Use postBlob instead of post for file downloads
    this.apiService.postBlob('generar-liquidaciones/', params)
      .subscribe({
        next: (response: Blob) => {
          this.cargando = false;
          this.liquidacionesGeneradas = true;
          
          // Create download link for the zip file
          const url = window.URL.createObjectURL(response);
          const a = document.createElement('a');
          const filename = `liquidaciones_${this.getNombreMes()}_${formValues.year}.zip`;
          
          a.href = url;
          a.download = filename;
          document.body.appendChild(a);
          a.click();
          
          // Clean up
          window.URL.revokeObjectURL(url);
          document.body.removeChild(a);
        },
        error: (error) => {
          this.cargando = false;
          console.error('Error al generar liquidaciones:', error);
          
          // Handle error response
          if (error.error instanceof Blob) {
            // Try to read error message from blob
            const reader = new FileReader();
            reader.onload = () => {
              try {
                const errorJson = JSON.parse(reader.result as string);
                this.mensajeError = errorJson.error || 'Error al generar las liquidaciones';
              } catch (e) {
                this.mensajeError = 'Error al generar las liquidaciones';
              }
            };
            reader.readAsText(error.error);
          } else {
            this.mensajeError = error.error?.error || 'Error al generar las liquidaciones';
          }
        }
      });
  }
  limpiarFiltros(): void {
    const hoy = new Date();
    
    // Reseteamos los controles estándar
    this.filtroForm.patchValue({
      sociedad_id: '',
      mes: hoy.getMonth() + 1,
      year: hoy.getFullYear(),
      cliente_id: '',
      casa_id: ''
    });
    
    // El control de fundo debe manejarse de manera especial porque está deshabilitado
    this.filtroForm.get('fundo_id')?.setValue('');
    this.filtroForm.get('fundo_id')?.disable();
    
    this.liquidacionesGeneradas = false;
  }
  
  // Obtener el nombre del mes seleccionado
  getNombreMes(): string {
    const mes = this.filtroForm.get('mes')?.value;
    return this.meses.find(m => m.valor === mes)?.nombre || '';
  }
}