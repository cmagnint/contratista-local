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
  selector: 'app-archivo-previred',
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
  templateUrl: './archivo-previred.component.html',
  styleUrls: ['./archivo-previred.component.css'],
  providers: [DatePipe]
})
export class ArchivoPreviredComponent implements OnInit {
  filtroForm: FormGroup;
  periodoForm: FormGroup;
  
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
  
  // Estado del archivo generado
  archivoGenerado: boolean = false;
  nombreArchivo: string = '';
  
  // Datos para los meses
  meses: any[] = [
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
  
  // Años disponibles (10 años hacia atrás y 1 año adelante)
  anos: number[] = [];
  
  // ID del holding actual
  holding: string = '';
  
  // Columnas para la tabla de trabajadores
  displayedColumns: string[] = ['seleccionar', 'nombre', 'rut', 'nacionalidad', 'afp', 'acciones'];
  
  constructor(
    private fb: FormBuilder,
    private apiService: ContratistaApiService,
    private snackBar: MatSnackBar,
    private datePipe: DatePipe,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {
    // Inicializar formulario de filtros
    this.filtroForm = this.fb.group({
      sociedad_id: ['', Validators.required],
      cliente_id: [''],
      fundo_id: [{value: '', disabled: true}], // Inicialmente deshabilitado
      casa_id: ['']
    });
    
    // Inicializar formulario de periodo
    const fechaActual = new Date();
    this.periodoForm = this.fb.group({
      mes: [fechaActual.getMonth() + 1, Validators.required], // Mes actual
      ano: [fechaActual.getFullYear(), Validators.required]  // Año actual
    });
    
    // Generar años disponibles
    const anoActual = fechaActual.getFullYear();
    for (let i = anoActual - 10; i <= anoActual + 1; i++) {
      this.anos.push(i);
    }
    
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
    this.archivoGenerado = false;
    
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
      // Agregar a seleccionados
      this.trabajadoresSeleccionados.push(trabajador);
    } else {
      // Quitar de seleccionados
      this.trabajadoresSeleccionados = this.trabajadoresSeleccionados.filter(
        t => t.id !== trabajador.id
      );
    }
  }
  
  seleccionarTodos(evento: any): void {
    const seleccionado = evento.checked;
    
    if (seleccionado) {
      // Seleccionar todos los trabajadores
      this.trabajadoresSeleccionados = [...this.trabajadores];
    } else {
      // Deseleccionar todos
      this.trabajadoresSeleccionados = [];
    }
  }
  
  estaSeleccionado(trabajador: any): boolean {
    return this.trabajadoresSeleccionados.some(t => t.id === trabajador.id);
  }
  
  estanTodosSeleccionados(): boolean {
    return this.trabajadores.length > 0 && 
           this.trabajadoresSeleccionados.length === this.trabajadores.length;
  }
  
  generarArchivoPrevired(): void {
    if (this.trabajadoresSeleccionados.length === 0) {
      this.snackBar.open(
        'Debe seleccionar al menos un trabajador',
        'Cerrar',
        { duration: 3000 }
      );
      return;
    }
    
    if (this.periodoForm.invalid) {
      this.snackBar.open(
        'Debe seleccionar un mes y año válidos',
        'Cerrar',
        { duration: 3000 }
      );
      return;
    }
    
    this.cargando = true;
    this.mensajeError = '';
    this.archivoGenerado = false;
    
    // Obtener datos del periodo
    const periodo = this.periodoForm.value;
    
    // Preparar IDs de trabajadores seleccionados
    const trabajadorIds = this.trabajadoresSeleccionados.map(t => t.id);
    
    const requestData = {
      trabajador_ids: trabajadorIds,
      mes: periodo.mes,
      ano: periodo.ano
    };
    
    // Llamar al endpoint para generar el archivo
    this.apiService.postBlob('generar-archivo-previred/', requestData).subscribe({
      next: (response) => {
        this.cargando = false;
        this.archivoGenerado = true;
        
        // Crear nombre de archivo
        const mesTexto = this.meses.find(m => m.valor === periodo.mes)?.nombre || periodo.mes;
        this.nombreArchivo = `Previred_${mesTexto}_${periodo.ano}.txt`;
        
        // Descargar el archivo
        this.descargarArchivo(response);
        
        this.snackBar.open(
          'Archivo Previred generado exitosamente',
          'Cerrar',
          { duration: 3000 }
        );
      },
      error: (error) => {
        this.cargando = false;
        console.error('Error al generar archivo Previred:', error);
        this.mensajeError = error.error?.error || 'Error al generar archivo Previred';
      }
    });
  }
  
  descargarArchivo(blob: Blob): void {
    // Crear una URL para el blob
    const url = window.URL.createObjectURL(blob);
    
    // Crear un elemento de enlace para descargar
    const a = document.createElement('a');
    a.href = url;
    a.download = this.nombreArchivo;
    
    // Anexar a documento, hacer clic y limpiar
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    
    // Liberar la URL
    window.URL.revokeObjectURL(url);
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
    this.archivoGenerado = false;
  }
  
  // Helper method to extract name from trabajador object
  getNombreTrabajador(trabajador: any): string {
    return trabajador.nombre_completo || `${trabajador.nombres || ''} ${trabajador.apellidos || ''}`.trim();
  }
}