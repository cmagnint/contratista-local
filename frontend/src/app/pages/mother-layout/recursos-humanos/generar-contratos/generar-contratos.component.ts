import { Component, OnInit, Inject, PLATFORM_ID } from '@angular/core';
import { CommonModule, DatePipe, isPlatformBrowser } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatTableModule } from '@angular/material/table';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatSortModule } from '@angular/material/sort';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatSnackBarModule, MatSnackBar } from '@angular/material/snack-bar';
import { ContratistaApiService } from '../../../../services/contratista-api.service';

@Component({
  selector: 'app-generar-contratos',
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
    MatCheckboxModule,
    MatTableModule,
    MatPaginatorModule,
    MatSortModule,
    MatProgressSpinnerModule,
    MatIconModule,
    MatTooltipModule,
    MatSnackBarModule
  ],
  templateUrl: './generar-contratos.component.html',
  styleUrl: './generar-contratos.component.css',
  providers: [DatePipe]
})
export class GenerarContratosComponent implements OnInit {
  filtroForm: FormGroup;
  
  // Datos para los dropdowns
  sociedades: any[] = [];
  clientes: any[] = [];
  fundos: any[] = [];
  casas: any[] = [];
  
  // Estado de carga
  cargando: boolean = false;
  cargandoFundos: boolean = false;
  cargandoTrabajadores: boolean = false;
  mensajeError: string = '';
  
  // Lista de trabajadores y selección
  trabajadores: any[] = [];
  trabajadoresSeleccionados: any[] = [];
  
  // Formatos de contrato disponibles
  formatosDisponibles: any[] = [];
  formatoSeleccionado: any = null;
  
  // Estado de los contratos generados
  contratosGenerados: boolean = false;
  urlsContratos: string[] = [];
  
  // ID del holding actual
  holding: string = '';
  
  // Columnas para la tabla de trabajadores
  displayedColumns: string[] = ['seleccionar', 'nombre', 'rut', 'nacionalidad', 'acciones'];
  
  constructor(
    private fb: FormBuilder,
    private apiService: ContratistaApiService,
    private snackBar: MatSnackBar,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {
    // Inicializar formulario
    this.filtroForm = this.fb.group({
      sociedad_id: ['', Validators.required],
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
  
  buscarTrabajadores(): void {
    if (this.filtroForm.invalid) {
      return;
    }
    
    this.cargandoTrabajadores = true;
    this.mensajeError = '';
    this.trabajadores = [];
    this.trabajadoresSeleccionados = [];
    this.formatosDisponibles = [];
    this.formatoSeleccionado = null;
    this.contratosGenerados = false;
    this.urlsContratos = [];
    
    const formValues = this.filtroForm.getRawValue();
    let params: any = {
      holding: this.holding
    };
    
    // Agregar solo los filtros que tienen valor
    if (formValues.sociedad_id) params.sociedad_id = formValues.sociedad_id;
    if (formValues.cliente_id) params.cliente_id = formValues.cliente_id;
    if (formValues.fundo_id) params.fundo_id = formValues.fundo_id;
    if (formValues.casa_id) params.casa_id = formValues.casa_id;
    
    // Convertir params a query string
    const queryParams = Object.keys(params)
      .map(key => `${key}=${params[key]}`)
      .join('&');
    
    this.apiService.get(`api_personal_filtrado/?${queryParams}`).subscribe({
      next: (response) => {
        this.trabajadores = response;
        this.cargandoTrabajadores = false;
        console.log('Trabajadores cargados:', this.trabajadores.length);
      },
      error: (error) => {
        this.cargandoTrabajadores = false;
        console.error('Error al cargar trabajadores:', error);
        this.mensajeError = error.error?.error || 'Error al cargar trabajadores';
      }
    });
  }
  
  seleccionarTrabajador(trabajador: any, evento: any): void {
    const seleccionado = evento.checked;
    
    if (seleccionado) {
      // Verificar que no se mezclen nacionalidades
      if (this.trabajadoresSeleccionados.length > 0) {
        const nacionalidadPrimero = this.trabajadoresSeleccionados[0].nacionalidad;
        
        if (trabajador.nacionalidad !== nacionalidadPrimero) {
          this.snackBar.open(
            'No se pueden seleccionar trabajadores de diferentes nacionalidades',
            'Cerrar',
            { duration: 3000 }
          );
          evento.source.checked = false;
          return;
        }
      }
      
      // Agregar a seleccionados
      this.trabajadoresSeleccionados.push(trabajador);
    } else {
      // Quitar de seleccionados
      this.trabajadoresSeleccionados = this.trabajadoresSeleccionados.filter(
        t => t.id !== trabajador.id
      );
    }
    
    // Si hay trabajadores seleccionados, cargar formatos disponibles
    if (this.trabajadoresSeleccionados.length > 0) {
      this.cargarFormatosDisponibles();
    } else {
      this.formatosDisponibles = [];
      this.formatoSeleccionado = null;
    }
  }
  
  cargarFormatosDisponibles(): void {
    // Determinar el tipo de contrato basado en la nacionalidad
    const nacionalidad = this.trabajadoresSeleccionados[0].nacionalidad?.toUpperCase();
    const tipoContrato = nacionalidad === 'CHILENA' || nacionalidad === 'CHILENO' ? 'CHILENO' : 'EXTRANJERO';
    
    this.apiService.get(`api_listar-documentos/?tipo=${tipoContrato}`).subscribe({
      next: (response) => {
        this.formatosDisponibles = response;
        console.log('Formatos disponibles:', this.formatosDisponibles.length);
        
        if (this.formatosDisponibles.length === 0) {
          this.snackBar.open(
            `No hay formatos de contrato disponibles para nacionalidad ${nacionalidad}`,
            'Cerrar',
            { duration: 3000 }
          );
        } else if (this.formatosDisponibles.length === 1) {
          // Seleccionar automáticamente si solo hay un formato
          this.formatoSeleccionado = this.formatosDisponibles[0];
        }
      },
      error: (error) => {
        console.error('Error al cargar formatos:', error);
        this.mensajeError = 'Error al cargar formatos de contrato disponibles';
      }
    });
  }
  
  seleccionarFormato(formato: any): void {
    this.formatoSeleccionado = formato;
  }
  
  generarContratos(): void {
    if (!this.formatoSeleccionado || this.trabajadoresSeleccionados.length === 0) {
      this.snackBar.open(
        'Debe seleccionar trabajadores y un formato de contrato',
        'Cerrar',
        { duration: 3000 }
      );
      return;
    }
    
    this.cargando = true;
    this.mensajeError = '';
    this.contratosGenerados = false;
    this.urlsContratos = [];
    
    // Preparar IDs de trabajadores seleccionados
    const trabajadorIds = this.trabajadoresSeleccionados.map(t => t.id);
    
    const requestData = {
      documento_id: this.formatoSeleccionado.id,
      trabajador_ids: trabajadorIds
    };
    
    this.apiService.post('api_generar-documentos-masivo/', requestData).subscribe({
      next: (response) => {
        this.cargando = false;
        this.contratosGenerados = true;
        
        // Guardar URLs de los contratos generados
        if (response.urls && Array.isArray(response.urls)) {
          this.urlsContratos = response.urls;
        }
        
        this.snackBar.open(
          `Se generaron ${this.urlsContratos.length} contratos exitosamente`,
          'Cerrar',
          { duration: 3000 }
        );
      },
      error: (error) => {
        this.cargando = false;
        console.error('Error al generar contratos:', error);
        this.mensajeError = error.error?.error || 'Error al generar contratos';
      }
    });
  }
  
  descargarContrato(url: string, indice: number): void {
    const a = document.createElement('a');
    a.href = url;
    a.download = `contrato_${this.trabajadoresSeleccionados[indice]?.nombre_completo || indice}.pdf`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  }
  
  descargarTodos(): void {
    // Si hay muchos contratos, hacer esto secuencialmente para evitar bloqueos
    if (this.urlsContratos.length > 0) {
      let index = 0;
      
      const descargaSiguiente = () => {
        if (index < this.urlsContratos.length) {
          this.descargarContrato(this.urlsContratos[index], index);
          index++;
          setTimeout(descargaSiguiente, 300); // Esperar 300ms entre descargas
        }
      };
      
      descargaSiguiente();
    }
  }
  
  limpiarFiltros(): void {
    this.filtroForm.reset({
      sociedad_id: '',
      cliente_id: '',
      casa_id: ''
    });
    
    // El control de fundo debe manejarse de manera especial porque está deshabilitado
    this.filtroForm.get('fundo_id')?.setValue('');
    this.filtroForm.get('fundo_id')?.disable();
    
    this.trabajadores = [];
    this.trabajadoresSeleccionados = [];
    this.formatosDisponibles = [];
    this.formatoSeleccionado = null;
    this.contratosGenerados = false;
    this.urlsContratos = [];
  }
  
  estaSeleccionado(trabajador: any): boolean {
    return this.trabajadoresSeleccionados.some(t => t.id === trabajador.id);
  }
  
  // Helper method to extract name from trabajador object
  getNombreTrabajador(trabajador: any): string {
    return trabajador.nombre_completo || `${trabajador.nombres || ''} ${trabajador.apellidos || ''}`.trim();
  }
}