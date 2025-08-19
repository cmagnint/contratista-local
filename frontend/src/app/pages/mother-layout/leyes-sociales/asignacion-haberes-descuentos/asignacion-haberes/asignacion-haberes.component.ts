import { Component, OnInit, Inject, PLATFORM_ID } from '@angular/core';
import { CommonModule, DatePipe, isPlatformBrowser } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatTableModule } from '@angular/material/table';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatSortModule } from '@angular/material/sort';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatIconModule } from '@angular/material/icon';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatDialogModule, MatDialog } from '@angular/material/dialog';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatChipsModule } from '@angular/material/chips';
import { ContratistaApiService } from '../../../../../services/contratista-api.service';
import { AsignacionHaberesDialogComponent } from './asignacion-haberes-dialog/asignacion-haberes-dialog.component';

// Interfaces para manejo de datos
interface Trabajador {
  id: number;
  nombre_completo: string;
  rut: string;
  haberes: Haber[];
  haberes_asignados?: TrabajadorHaber[];
  seleccionado?: boolean;
}

interface Haber {
  id: number;
  nombre: string;
  tipo_valor: string;
  imponible: boolean;
}

interface TrabajadorHaber {
  haber: Haber;
  valor: number;
}

@Component({
  selector: 'app-asignacion-haberes',
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
    MatTableModule,
    MatPaginatorModule,
    MatSortModule,
    MatProgressSpinnerModule,
    MatIconModule,
    MatCheckboxModule,
    MatDialogModule,
    MatTooltipModule,
    MatChipsModule
  ],
  templateUrl: './asignacion-haberes.component.html',
  styleUrls: ['./asignacion-haberes.component.css'],
  providers: [DatePipe]
})
export class AsignacionHaberesComponent implements OnInit {
  filtroForm: FormGroup;
  
  // Datos para los filtros
  sociedades: any[] = [];
  clientes: any[] = [];
  fundos: any[] = [];
  casas: any[] = [];
  
  // Estado de carga para fundos
  cargandoFundos: boolean = false;
  
  // Datos para asignación
  haberes: Haber[] = [];
  
  // Datos de trabajadores
  trabajadores: Trabajador[] = [];
  trabajadoresSeleccionados: Trabajador[] = [];
  
  // Estados de la UI
  cargando: boolean = false;
  mensajeError: string = '';
  resultadosExisten: boolean = false;
  
  // Columnas para la tabla - Removemos 'sueldo_base'
  displayedColumns: string[] = ['seleccionar', 'trabajador', 'rut', 'haberes', 'acciones'];
  
  // ID del holding actual
  holding: string = '';
  
  constructor(
    private fb: FormBuilder,
    private apiService: ContratistaApiService,
    private dialog: MatDialog,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {
    // Inicializar formulario
    this.filtroForm = this.fb.group({
      sociedad_id: [''],
      cliente_id: [''],
      fundo_id: [{value: '', disabled: true}], // Inicialmente deshabilitado
      casa_id: ['']
    });
    
    // Observador para cambios en cliente_id
    this.filtroForm.get('cliente_id')?.valueChanges.subscribe(clienteId => {
      if (clienteId) {
        this.cargandoFundos = true;
        this.filtroForm.get('fundo_id')?.enable();
        this.cargarFundosPorCliente(clienteId);
      } else {
        this.fundos = [];
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
        console.error('Error al cargar sociedades:', error);
        this.mensajeError = 'Error al cargar datos de sociedades';
      }
    });
    
    // Cargar clientes
    this.apiService.get(`api_clientes/?holding=${this.holding}`).subscribe({
      next: (response) => {
        this.clientes = response;
      },
      error: (error) => {
        console.error('Error al cargar clientes:', error);
        this.mensajeError = 'Error al cargar datos de clientes';
      }
    });
    
    // Cargar casas
    this.apiService.get(`api_casas_trabajadores/?holding=${this.holding}`).subscribe({
      next: (data) => {
        this.casas = data;
      },
      error: (err) => {
        console.error('Error al cargar casas:', err);
        this.mensajeError = 'Error al cargar datos de casas';
      }
    });
    
    // Cargar haberes
    this.apiService.get(`api_haberes/?holding=${this.holding}`).subscribe({
      next: (data) => {
        this.haberes = data;
      },
      error: (err) => {
        console.error('Error al cargar haberes:', err);
        this.mensajeError = 'Error al cargar datos de haberes';
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
        console.error('Error al cargar fundos:', err);
        this.mensajeError = 'Error al cargar datos de fundos';
        this.cargandoFundos = false;
      }
    });
  }
  
  buscarTrabajadores(): void {
    this.cargando = true;
    this.resultadosExisten = false;
    this.mensajeError = '';
    this.trabajadores = [];
    this.trabajadoresSeleccionados = [];
    
    // Construir parámetros de búsqueda
    const formValues = this.filtroForm.getRawValue();
    let params = new URLSearchParams();
    
    params.append('holding', this.holding);
    
    if (formValues.sociedad_id) {
      params.append('sociedad_id', formValues.sociedad_id);
    }
    
    if (formValues.cliente_id) {
      params.append('cliente_id', formValues.cliente_id);
    }
    
    if (formValues.fundo_id) {
      params.append('fundo_id', formValues.fundo_id);
    }
    
    if (formValues.casa_id) {
      params.append('casa_id', formValues.casa_id);
    }
    
    this.apiService.get(`api_personal_filtrado/?${params}`).subscribe({
      next: (data) => {
        this.trabajadores = data.map((t: any) => ({
          ...t,
          seleccionado: false
        }));
        this.resultadosExisten = this.trabajadores.length > 0;
        this.cargando = false;
      },
      error: (error) => {
        console.error('Error al buscar trabajadores:', error);
        this.mensajeError = error.error?.error || 'Error al buscar trabajadores';
        this.cargando = false;
      }
    });
  }
  
  limpiarFiltros(): void {
    this.filtroForm.patchValue({
      sociedad_id: '',
      cliente_id: '',
      casa_id: ''
    });
    
    // El control de fundo debe manejarse especialmente
    this.filtroForm.get('fundo_id')?.setValue('');
    this.filtroForm.get('fundo_id')?.disable();
    
    this.trabajadores = [];
    this.trabajadoresSeleccionados = [];
    this.resultadosExisten = false;
  }
  
  seleccionarTodos(event: any): void {
    const seleccionados = event.checked;
    
    this.trabajadores.forEach(t => {
      t.seleccionado = seleccionados;
    });
    
    this.actualizarSeleccionados();
  }
  
  toggleSeleccion(trabajador: Trabajador): void {
    trabajador.seleccionado = !trabajador.seleccionado;
    this.actualizarSeleccionados();
  }
  
  actualizarSeleccionados(): void {
    this.trabajadoresSeleccionados = this.trabajadores.filter(t => t.seleccionado);
  }
  
  abrirDialogoAsignacion(): void {
    if (!this.trabajadoresSeleccionados.length) {
      this.mensajeError = 'Debe seleccionar al menos un trabajador';
      return;
    }
    
    const dialogRef = this.dialog.open(AsignacionHaberesDialogComponent, {
      width: '600px',
      data: {
        trabajadores: this.trabajadoresSeleccionados,
        haberes: this.haberes
      }
    });
    
    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.asignarHaberes(result);
      }
    });
  }
  
  asignarHaberes(datosAsignacion: any): void {
    const trabajadorIds = this.trabajadoresSeleccionados.map(t => t.id);
    
    const payload = {
      holding_id: this.holding,
      trabajador_ids: trabajadorIds,
      haberes_asignaciones: datosAsignacion.haberes_asignaciones || []
    };
    
    this.cargando = true;
    
    this.apiService.post('api_asignar_haberes/', payload).subscribe({
      next: (response) => {
        // Actualizar los datos de los trabajadores con la respuesta
        this.actualizarTrabajadoresConRespuesta(response);
        this.cargando = false;
        
        // Mostrar mensaje de éxito
        alert(`Se han asignado correctamente los haberes a ${trabajadorIds.length} trabajador(es)`);
      },
      error: (error) => {
        console.error('Error al asignar haberes:', error);
        this.mensajeError = error.error?.error || 'Error al asignar haberes';
        this.cargando = false;
      }
    });
  }
  
  actualizarTrabajadoresConRespuesta(trabajadoresActualizados: any[]): void {
    // Actualizar los datos de trabajadores con la respuesta del servidor
    trabajadoresActualizados.forEach(trabajadorActualizado => {
      const index = this.trabajadores.findIndex(t => t.id === trabajadorActualizado.id);
      if (index !== -1) {
        // Mantener el estado de selección
        const seleccionado = this.trabajadores[index].seleccionado;
        this.trabajadores[index] = { 
          ...trabajadorActualizado, 
          seleccionado 
        };
      }
    });
    
    // Actualizar la lista de seleccionados
    this.actualizarSeleccionados();
  }
  
  verDetallesTrabajador(trabajador: Trabajador): void {
    const dialogRef = this.dialog.open(AsignacionHaberesDialogComponent, {
      width: '600px',
      data: {
        trabajadores: [trabajador],
        haberes: this.haberes,
        modoVisualizacion: true
      }
    });
    
    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        // Si hay cambios desde el modo visualización, asignarlos
        this.asignarHaberes(result);
      }
    });
  }
  
  // Métodos auxiliares
  getTotalHaberes(trabajador: Trabajador): number {
    // Contar primero de haberes_asignados (nueva relación) y como backup usar haberes (antigua relación)
    return trabajador.haberes_asignados?.length || trabajador.haberes?.length || 0;
  }
  
  formatearValor(valor: number | undefined): string {
    if (valor === undefined || valor === null) {
      return 'No asignado';
    }
    return new Intl.NumberFormat('es-CL', { style: 'currency', currency: 'CLP' }).format(valor);
  }
  
  // Método para obtener información sobre el tipo de valor del haber
  getTipoValorHaber(haber: any): string {
    return haber.tipo_valor === 'CANTIDAD' ? 'Por Cantidad' : 'Monto Fijo';
  }
}