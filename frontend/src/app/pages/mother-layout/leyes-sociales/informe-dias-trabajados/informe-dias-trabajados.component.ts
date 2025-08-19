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
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatDialogModule, MatDialog } from '@angular/material/dialog';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatBadgeModule } from '@angular/material/badge';
import { ContratistaApiService } from '../../../../services/contratista-api.service';
import { ReduccionDialogComponent } from './reduccion-dialog/reduccion-dialog.component';

interface TrabajadorDataExtendido {
  id?: number;
  nombres: string;
  apellidos?: string;
  rut: string;
  fecha_ingreso?: string;
  dias_por_cliente: { [key: string]: number };
  client_totals?: { [key: string]: number };
  dias_totales: number;
  // Campos adicionales para la edición y aprobación
  dias_originales?: { [key: string]: number };
  aprobado?: boolean;
  fecha_aprobacion?: Date;
  // Campos para mantener los valores editados
  valores_editados?: { [key: string]: number };
  // Campos para las reducciones
  reducciones_aplicadas: { [clienteNombre: string]: { porcentaje: number, diasOriginales: number, manual?: boolean } };
  // Flag para saber si ya estaba guardado en la base de datos
  registrado_en_db?: boolean;
}

// Nueva interfaz para datos de mes cerrado
interface MesCerradoData {
  id?: number;
  holding?: number;
  mes: number;
  year: number;
  is_closed: boolean;
  fecha_cierre?: string;
  usuario_cierre?: number;
  usuario_cierre_nombre?: string;
  motivo?: string;
}

@Component({
  selector: 'app-informe-dias-trabajados',
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
    MatCheckboxModule,
    MatDialogModule,
    MatTooltipModule,
    MatBadgeModule,
  ],
  templateUrl: './informe-dias-trabajados.component.html',
  styleUrls: ['./informe-dias-trabajados.component.css'],
  providers: [DatePipe]
})
export class InformeDiasTrabajadosComponent implements OnInit {
  filtroForm: FormGroup;
  
  // Datos para los dropdowns
  clientes: any[] = [];
  fundos: any[] = [];
  casas: any[] = [];
  
  // Estado de carga para fundos
  cargandoFundos: boolean = false;
  
  // Datos del informe
  informeCargado: boolean = false;
  cargando: boolean = false;
  trabajadoresData: TrabajadorDataExtendido[] = [];
  clientesData: any[] = [];
  mensajeError: string = '';
  
  // Columnas para la tabla
  displayedColumns: string[] = [];
  
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
  
  // Para almacenar los registros aprobados cargados desde la base de datos
  registrosAprobadosExistentes: any[] = [];
  
  // Nuevas propiedades para control de mes cerrado
  mesCerrado: boolean = false;
  mesCerradoData: MesCerradoData | null = null;
  permisoCerrarMes: boolean = false;
  
  // Contador para trabajadores con días reducidos
  numTrabajadoresReducidos: number = 0;
  
  constructor(
    private fb: FormBuilder,
    private apiService: ContratistaApiService,
    private datePipe: DatePipe,
    private dialog: MatDialog,
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
      mes: [hoy.getMonth() + 1, Validators.required],
      year: [hoy.getFullYear(), Validators.required],
      trabajador_id: [''],
      cliente_id: [''],
      fundo_id: [{value: '', disabled: true}], // Inicialmente deshabilitado
      supervisor_id: [''],
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
    
    // Observar cambios en mes y año para verificar si están cerrados
    this.filtroForm.get('mes')?.valueChanges.subscribe(mes => {
      const year = this.filtroForm.get('year')?.value;
      if (mes && year) {
        this.checkMesCerrado(mes, year);
      }
    });
    
    this.filtroForm.get('year')?.valueChanges.subscribe(year => {
      const mes = this.filtroForm.get('mes')?.value;
      if (mes && year) {
        this.checkMesCerrado(mes, year);
      }
    });
  }
  
  ngOnInit(): void {
    if (isPlatformBrowser(this.platformId)) {
      // Usar localStorage solo si estamos en el navegador
      this.holding = localStorage.getItem('holding_id') || '';
      if (this.holding) {
        this.cargarDatosIniciales();
        this.checkPermisosCerrarMes();
        
        // Verificar si el mes actual está cerrado
        const mes = this.filtroForm.get('mes')?.value;
        const year = this.filtroForm.get('year')?.value;
        if (mes && year) {
          this.checkMesCerrado(mes, year);
        }
      } else {
        this.mensajeError = 'No se pudo determinar el ID del holding';
      }
    }
  }
  
  // Verificar si el usuario tiene permisos para cerrar meses
  checkPermisosCerrarMes(): void {
    // Aquí puedes implementar la lógica para verificar permisos
    // Por ahora, asumimos que el usuario tiene permisos
    this.permisoCerrarMes = true;
  }
  
  // Verificar si un mes está cerrado
  checkMesCerrado(mes: number, year: number): void {
    this.apiService.get(`meses-cerrados/?holding_id=${this.holding}&mes=${mes}&year=${year}`)
      .subscribe({
        next: (response) => {
          this.mesCerrado = response.is_closed;
          if (this.mesCerrado) {
            this.mesCerradoData = response;
          } else {
            this.mesCerradoData = null;
          }
        },
        error: (error) => {
          console.error('Error al verificar el estado del mes:', error);
          this.mensajeError = 'Error al verificar si el mes está cerrado';
        }
      });
  }
  
  // Método para cerrar un mes
  cerrarMes(): void {
    const mes = this.filtroForm.get('mes')?.value;
    const year = this.filtroForm.get('year')?.value;
    
    if (!confirm(`¿Está seguro que desea cerrar el mes ${this.getNombreMes()} ${year}?\n\nUna vez cerrado, no se podrán realizar modificaciones a los días trabajados de este mes.`)) {
      return;
    }
    
    const motivo = prompt('Motivo del cierre (opcional):');
    
    const data = {
      holding_id: this.holding,
      mes: mes,
      year: year,
      motivo: motivo || ''
    };
    
    this.apiService.post('meses-cerrados/', data)
      .subscribe({
        next: (response) => {
          this.mesCerrado = true;
          this.mesCerradoData = response;
          alert('Mes cerrado correctamente');
        },
        error: (error) => {
          console.error('Error al cerrar el mes:', error);
          this.mensajeError = error.error?.error || 'Error al cerrar el mes';
        }
      });
  }
  
  // Método para abrir un mes previamente cerrado
  abrirMes(): void {
    const mes = this.filtroForm.get('mes')?.value;
    const year = this.filtroForm.get('year')?.value;
    
    if (!confirm(`¿Está seguro que desea abrir el mes ${this.getNombreMes()} ${year}?\n\nEsto permitirá realizar modificaciones a los días trabajados de este mes.`)) {
      return;
    }
    
    const data = {
      holding_id: this.holding,
      mes: mes,
      year: year
    };
    
    this.apiService.delete('meses-cerrados/', data)
      .subscribe({
        next: (response) => {
          this.mesCerrado = false;
          this.mesCerradoData = null;
          alert('Mes abierto correctamente');
        },
        error: (error) => {
          console.error('Error al abrir el mes:', error);
          this.mensajeError = error.error?.error || 'Error al abrir el mes';
        }
      });
  }

  // Nuevo método para eliminar todos los registros de un mes
  eliminarRegistrosMes(): void {
    const mes = this.filtroForm.get('mes')?.value;
    const year = this.filtroForm.get('year')?.value;
    
    if (!confirm(`¿Está seguro que desea ELIMINAR TODOS LOS REGISTROS del mes ${this.getNombreMes()} ${year}?\n\nEsta acción no se puede deshacer y eliminará todos los días trabajados aprobados para este mes.`)) {
      return;
    }
    
    this.cargando = true;
    const data = {
      holding_id: this.holding,
      mes: mes,
      year: year
    };
    
    this.apiService.delete('dias-trabajados-aprobados/', data)
      .subscribe({
        next: (response) => {
          this.cargando = false;
          alert(response.mensaje);
          // Refrescar el informe para mostrar los cambios
          this.generarInforme();
        },
        error: (error) => {
          this.cargando = false;
          console.error('Error al eliminar registros:', error);
          this.mensajeError = error.error?.error || 'Error al eliminar los registros del mes';
        }
      });
  }
  
  cargarDatosIniciales(): void {
    // Cargar clientes
    this.apiService.get(`api_clientes/?holding=${this.holding}`).subscribe({
      next: (response) => {
        this.clientes = response;
      },
      error: (error) => {
        console.error('Error al recibir las sociedades:', error);
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
  
  generarInforme(): void {
    if (this.filtroForm.invalid) {
      return;
    }
    
    this.cargando = true;
    this.informeCargado = false;
    this.mensajeError = '';
    this.numTrabajadoresReducidos = 0;
    
    // Importante: cuando usamos controles deshabilitados, debemos usar getRawValue() 
    // en lugar de value para obtener todos los valores incluyendo los deshabilitados
    const formValues = this.filtroForm.getRawValue();
    const params = {
      holding_id: this.holding,
      mes: formValues.mes,
      year: formValues.year,
      trabajador_id: formValues.trabajador_id || null,
      cliente_id: formValues.cliente_id || null,
      fundo_id: formValues.fundo_id || null,
      supervisor_id: formValues.supervisor_id || null,
      casa_id: formValues.casa_id || null
    };
    
    console.log('Enviando parámetros de informe:', params);
    
    // Verificar si el mes está cerrado
    this.checkMesCerrado(params.mes, params.year);
    
    // Primero obtener registros aprobados para este período
    this.apiService.get(`dias-trabajados-aprobados/?holding_id=${this.holding}&mes=${params.mes}&year=${params.year}`)
      .subscribe({
        next: (registrosAprobados) => {
          // Guardar los registros aprobados para usarlos después
          this.registrosAprobadosExistentes = registrosAprobados;
          
          // Continuar con la generación del informe
          this.apiService.post('informe-dias-trabajados/', params).subscribe({
            next: (data) => {
              console.log('Datos recibidos:', data);
              
              // Procesar los datos recibidos
              this.procesarDatosInforme(data);
              
              // Marcar como aprobados los trabajadores que ya tengan registro
              this.marcarTrabajadoresAprobados();
              
              // Configurar columnas para la tabla
              this.configureColumns();
              
              this.informeCargado = true;
              this.cargando = false;
            },
            error: (error) => {
              console.error('Error al generar informe:', error);
              this.mensajeError = error.error?.error || 'Error al generar el informe';
              this.cargando = false;
            }
          });
        },
        error: (error) => {
          console.error('Error al obtener registros aprobados:', error);
          
          // Si hay error consultando registros, generamos el informe sin ellos
          this.apiService.post('informe-dias-trabajados/', params).subscribe({
            next: (data) => {
              this.procesarDatosInforme(data);
              this.configureColumns();
              this.informeCargado = true;
              this.cargando = false;
            },
            error: (error) => {
              this.mensajeError = error.error?.error || 'Error al generar el informe';
              this.cargando = false;
            }
          });
        }
      });
  }
  
  procesarDatosInforme(data: any): void {
    // Extraer información de los clientes del JSON
    this.clientesData = data.clientes.map((cliente: any) => ({
      id: cliente.id,
      nombre: cliente.nombre
    }));
    
    // Procesar los datos de trabajadores y añadir propiedades para la edición
    this.trabajadoresData = data.trabajadores.map((trabajador: any) => {
      // Transformar client_totals a dias_por_cliente con nombres como claves
      const dias_por_cliente: { [key: string]: number } = {};
      const dias_originales: { [key: string]: number } = {};
      
      if (trabajador.client_totals) {
        for (const clientId in trabajador.client_totals) {
          const clienteEncontrado = this.clientesData.find(c => c.id.toString() === clientId);
          if (clienteEncontrado) {
            dias_por_cliente[clienteEncontrado.nombre] = trabajador.client_totals[clientId];
            dias_originales[clienteEncontrado.nombre] = trabajador.client_totals[clientId];
          }
        }
      }
      
      // Crear objeto trabajador extendido
      return {
        ...trabajador,
        dias_por_cliente,
        dias_originales,
        valores_editados: {},
        aprobado: false,
        reducciones_aplicadas: {},
        registrado_en_db: false
      };
    });
    
    console.log('Datos procesados:', this.trabajadoresData);
  }
  
  // Método para marcar trabajadores que ya tienen registros aprobados
  marcarTrabajadoresAprobados(): void {
    if (!this.registrosAprobadosExistentes || this.registrosAprobadosExistentes.length === 0) {
      return;
    }
    
    this.numTrabajadoresReducidos = 0;
    
    // Para cada registro aprobado existente, encontrar el trabajador correspondiente
    this.registrosAprobadosExistentes.forEach(registro => {
      const trabajador = this.trabajadoresData.find(t => t.id === registro.trabajador_id);
      if (trabajador) {
        // Marcar como aprobado y registrado en DB
        trabajador.aprobado = true;
        trabajador.registrado_en_db = true;
        trabajador.fecha_aprobacion = new Date(registro.fecha_aprobacion);
        
        // Actualizar los días por cliente desde el registro guardado
        if (registro.dias_por_cliente) {
          trabajador.dias_por_cliente = {}; // Reiniciamos para asegurarnos que solo tenemos los datos guardados
          
          this.clientesData.forEach(cliente => {
            const clienteId = cliente.id.toString();
            if (registro.dias_por_cliente[clienteId] !== undefined) {
              trabajador.dias_por_cliente[cliente.nombre] = registro.dias_por_cliente[clienteId];
            }
          });
        }
        
        // Actualizar las reducciones aplicadas
        if (registro.reducciones_aplicadas) {
          // Asegurarse de que reducciones_aplicadas exista en trabajador
          trabajador.reducciones_aplicadas = {};
          let tieneReducciones = false;
          
          this.clientesData.forEach(cliente => {
            const clienteId = cliente.id.toString();
            if (registro.reducciones_aplicadas[clienteId]) {
              trabajador.reducciones_aplicadas[cliente.nombre] = registro.reducciones_aplicadas[clienteId];
              tieneReducciones = true;
            }
          });
          
          // Incrementar contador de trabajadores con reducciones
          if (tieneReducciones) {
            this.numTrabajadoresReducidos++;
          }
        }
        
        // Actualizar el total de días
        trabajador.dias_totales = registro.dias_totales;
        
        // Guardar los valores originales para comparaciones futuras
        if (trabajador.dias_por_cliente) {
          trabajador.dias_originales = { ...trabajador.dias_por_cliente };
        }
      }
    });
    
    // Ordenar los trabajadores para que los aprobados aparezcan al principio
    this.ordenarTrabajadoresPorAprobacion();
  }
  
  // Devuelve true si algún cliente tiene una reducción aplicada
  trabajadorTieneReducciones(trabajador: TrabajadorDataExtendido): boolean {
    if (!trabajador.reducciones_aplicadas) return false;
    return Object.keys(trabajador.reducciones_aplicadas).length > 0;
  }
  
  configureColumns(): void {
    // Columnas básicas
    this.displayedColumns = ['trabajador', 'rut', 'fecha_ingreso'];
    
    // Añadir columnas por cliente
    for (const cliente of this.clientesData) {
      this.displayedColumns.push(`cliente_${cliente.id}`);
    }
    
    // Añadir columna total
    this.displayedColumns.push('total');
    
    // Añadir columna para el checkbox de aprobación
    this.displayedColumns.push('aprobado');
    
    console.log('Columnas configuradas:', this.displayedColumns);
  }
  
  limpiarFiltros(): void {
    const hoy = new Date();
    
    // Reseteamos los controles estándar
    this.filtroForm.patchValue({
      mes: hoy.getMonth() + 1,
      year: hoy.getFullYear(),
      trabajador_id: '',
      cliente_id: '',
      supervisor_id: '',
      casa_id: ''
    });
    
    // El control de fundo debe manejarse de manera especial porque está deshabilitado
    this.filtroForm.get('fundo_id')?.setValue('');
    this.filtroForm.get('fundo_id')?.disable();
    
    this.informeCargado = false;
  }
  
  // Obtener el nombre del mes seleccionado
  getNombreMes(): string {
    const mes = this.filtroForm.get('mes')?.value;
    return this.meses.find(m => m.valor === mes)?.nombre || '';
  }
  
  // Método para formatear la fecha de ingreso
  formatFechaIngreso(fechaStr: string | null): string {
    if (!fechaStr) return 'N/A';
    
    const fecha = new Date(fechaStr);
    return this.datePipe.transform(fecha, 'dd/MM/yyyy') || 'N/A';
  }
  
  // Obtener los días trabajados por trabajador y cliente
  getDiasPorCliente(trabajador: TrabajadorDataExtendido, clienteId: number): number {
    const clienteEncontrado = this.clientesData.find(c => c.id === clienteId);
    if (clienteEncontrado && trabajador.dias_por_cliente) {
      return trabajador.dias_por_cliente[clienteEncontrado.nombre] || 0;
    }
    return 0;
  }
  
  // Obtener el valor original de días trabajados
  getValorOriginal(trabajador: TrabajadorDataExtendido, clienteId: number): number | null {
    const clienteEncontrado = this.clientesData.find(c => c.id === clienteId);
    if (!clienteEncontrado) return null;
    
    const clienteNombre = clienteEncontrado.nombre;
    
    // Primero intentar obtener el valor original de las reducciones aplicadas
    if (trabajador.reducciones_aplicadas && 
        trabajador.reducciones_aplicadas[clienteNombre] && 
        trabajador.reducciones_aplicadas[clienteNombre].diasOriginales !== undefined) {
      return trabajador.reducciones_aplicadas[clienteNombre].diasOriginales;
    }
    
    // Si no hay reducciones, intentar obtener del objeto dias_originales
    if (trabajador.dias_originales) {
      return trabajador.dias_originales[clienteNombre] || null;
    }
    
    return null;
  }
  
  // Verificar si un valor ha sido editado
  isValorEditado(trabajador: TrabajadorDataExtendido, clienteId: number): boolean {
    const clienteEncontrado = this.clientesData.find(c => c.id === clienteId);
    if (!clienteEncontrado) return false;
    
    const clienteNombre = clienteEncontrado.nombre;
    
    // Comprobar si tiene reducciones aplicadas para este cliente
    if (trabajador.reducciones_aplicadas && trabajador.reducciones_aplicadas[clienteNombre]) {
      return true; // Si hay reducciones, siempre mostrar el valor original
    }
    
    // Comprobar diferencias entre valor original y actual
    if (trabajador.dias_originales && trabajador.dias_por_cliente) {
      const valorOriginal = trabajador.dias_originales[clienteNombre] || 0;
      const valorActual = trabajador.dias_por_cliente[clienteNombre] || 0;
      return valorOriginal !== valorActual;
    }
    
    return false;
  }
  
  
  // Verificar si un valor ha sido reducido
  isValorReducido(trabajador: TrabajadorDataExtendido, clienteId: number): boolean {
    const clienteEncontrado = this.clientesData.find(c => c.id === clienteId);
    if (clienteEncontrado && trabajador.reducciones_aplicadas) {
      return !!trabajador.reducciones_aplicadas[clienteEncontrado.nombre];
    }
    return false;
  }
  
  // Obtener el porcentaje de reducción aplicado
  getPorcentajeReduccion(trabajador: TrabajadorDataExtendido, clienteId: number): number | null {
    const clienteEncontrado = this.clientesData.find(c => c.id === clienteId);
    if (clienteEncontrado && trabajador.reducciones_aplicadas && trabajador.reducciones_aplicadas[clienteEncontrado.nombre]) {
      return trabajador.reducciones_aplicadas[clienteEncontrado.nombre].porcentaje;
    }
    return null;
  }
  
  // Verificar si la reducción fue manual o automática
  isReduccionManual(trabajador: TrabajadorDataExtendido, clienteId: number): boolean {
    const clienteEncontrado = this.clientesData.find(c => c.id === clienteId);
    if (clienteEncontrado && trabajador.reducciones_aplicadas && trabajador.reducciones_aplicadas[clienteEncontrado.nombre]) {
      return !!trabajador.reducciones_aplicadas[clienteEncontrado.nombre].manual;
    }
    return false;
  }
  
  // Manejar cambios en los días trabajados
  onDiasChange(trabajador: TrabajadorDataExtendido, clienteId: number, nuevoValor: number): void {
    // Verificar si el mes está cerrado
    if (this.mesCerrado) {
      alert('El mes está cerrado. No se pueden realizar modificaciones.');
      return; // Prevenir cualquier cambio
    }
    
    const clienteEncontrado = this.clientesData.find(c => c.id === clienteId);
    if (clienteEncontrado && trabajador.dias_por_cliente) {
      // Guardar el valor original si aún no existe
      if (!trabajador.dias_originales) {
        trabajador.dias_originales = {...trabajador.dias_por_cliente};
      }
      
      // Obtener el valor original de referencia
      const valorOriginal = trabajador.dias_originales[clienteEncontrado.nombre];
      
      // Actualizar el valor en dias_por_cliente
      trabajador.dias_por_cliente[clienteEncontrado.nombre] = nuevoValor;
      
      // Actualizar valores_editados para seguimiento
      if (!trabajador.valores_editados) {
        trabajador.valores_editados = {};
      }
      trabajador.valores_editados[clienteEncontrado.nombre] = nuevoValor;
      
      // Inicializar objeto de reducciones si no existe
      if (!trabajador.reducciones_aplicadas) {
        trabajador.reducciones_aplicadas = {};
      }
      
      // Calcular y aplicar la reducción manual si el nuevo valor es menor que el original
      if (nuevoValor < valorOriginal) {
        // Calcular el porcentaje de reducción
        const porcentajeReduccion = Math.round((1 - (nuevoValor / valorOriginal)) * 100);
        
        // Guardar la información de la reducción
        trabajador.reducciones_aplicadas[clienteEncontrado.nombre] = {
          porcentaje: porcentajeReduccion,
          diasOriginales: valorOriginal,
          manual: true
        };
      } else if (trabajador.reducciones_aplicadas && trabajador.reducciones_aplicadas[clienteEncontrado.nombre]) {
        // Si el valor es igual o mayor al original, eliminar la reducción si existía
        delete trabajador.reducciones_aplicadas[clienteEncontrado.nombre];
      }
      
      // Recalcular el total de días
      this.recalcularTotalDias(trabajador);
      
      // Actualizar el contador de trabajadores con reducciones
      this.actualizarContadorReducidos();
    }
  }
  
  // Actualizar el contador de trabajadores con reducciones
  actualizarContadorReducidos(): void {
    this.numTrabajadoresReducidos = this.trabajadoresData.filter(t => this.trabajadorTieneReducciones(t)).length;
  }
  
  // Recalcular el total de días trabajados para un trabajador
  recalcularTotalDias(trabajador: TrabajadorDataExtendido): void {
    let total = 0;
    for (const clienteNombre in trabajador.dias_por_cliente) {
      total += trabajador.dias_por_cliente[clienteNombre] || 0;
    }
    trabajador.dias_totales = total;
  }
  
  // Obtener el total de días trabajados por un trabajador
  getDiasTotales(trabajador: TrabajadorDataExtendido): number {
    return trabajador.dias_totales || 0;
  }
  
  // Obtener el nombre completo del trabajador
  getNombreTrabajador(trabajador: TrabajadorDataExtendido): string {
    return `${trabajador.nombres} ${trabajador.apellidos || ''}`.trim();
  }
  
  // Manejar el cambio en el checkbox de aprobación
  onAprobadoChange(trabajador: TrabajadorDataExtendido): void {
    // Verificar si el mes está cerrado
    if (this.mesCerrado) {
      alert('El mes está cerrado. No se pueden realizar modificaciones.');
      return; // Prevenir cualquier cambio
    }
    
    // Verificar si el trabajador ya tiene un registro guardado en la base de datos
    const tieneRegistroExistente = this.registrosAprobadosExistentes.some(
      r => r.trabajador_id === trabajador.id
    );
    
    if (tieneRegistroExistente && !trabajador.aprobado) {
      // Si está intentando desaprobar un registro ya guardado, mostrar advertencia
      if (!confirm('Este registro ya ha sido guardado en el sistema. ¿Desea desaprobarlo para modificarlo?')) {
        return; // Si el usuario cancela, no hacer nada
      }
      // Si confirma, se permitirá desaprobarlo pero se tendrá que guardar nuevamente
    }
    
    trabajador.aprobado = !trabajador.aprobado;
    
    if (trabajador.aprobado) {
      // Si se aprueba, registrar la fecha y hora de aprobación
      trabajador.fecha_aprobacion = new Date();
    } else {
      // Si se desaprueba, eliminar la fecha de aprobación
      trabajador.fecha_aprobacion = undefined;
    }
    
    // Ordenar la lista para que los aprobados aparezcan al principio
    this.ordenarTrabajadoresPorAprobacion();
  }
  
  // Ordenar trabajadores para que los aprobados aparezcan al principio
  ordenarTrabajadoresPorAprobacion(): void {
    this.trabajadoresData.sort((a, b) => {
      // Primero ordenar por estado de aprobación (aprobados primero)
      if (a.aprobado && !b.aprobado) return -1;
      if (!a.aprobado && b.aprobado) return 1;
      
      // Si ambos están aprobados, ordenar por fecha de aprobación (más reciente primero)
      if (a.aprobado && b.aprobado) {
        return (b.fecha_aprobacion?.getTime() || 0) - (a.fecha_aprobacion?.getTime() || 0);
      }
      
      // Para los no aprobados, mantener el orden original
      return 0;
    });
  }
  
  // Obtener estilo para una fila según su estado de aprobación y si tiene reducciones
  getFilaEstilo(trabajador: TrabajadorDataExtendido): {[key: string]: string} {
    if (trabajador.aprobado) {
      if (this.trabajadorTieneReducciones(trabajador)) {
        return {'background-color': '#fff8e1'}; // Color para aprobados con reducciones
      }
      return {'background-color': '#e8f5e9'}; // Color para aprobados normales
    }
    return {}; // Sin estilo especial para no aprobados
  }
  
  // Obtener estilo para una celda que ha sido reducida
  getCeldaEstiloReducida(trabajador: TrabajadorDataExtendido, clienteId: number): {[key: string]: string} {
    if (this.isValorReducido(trabajador, clienteId)) {
      // Si la reducción es manual, usar un color diferente
      if (this.isReduccionManual(trabajador, clienteId)) {
        return {'background-color': '#ffcdd2', 'position': 'relative'};
      }
      return {'background-color': '#ffe0b2', 'position': 'relative'};
    }
    return {};
  }
  
  // Abrir diálogo para aplicar reducción por cliente
  abrirDialogoReduccion(): void {
    // Verificar si el mes está cerrado
    if (this.mesCerrado) {
      alert('El mes está cerrado. No se pueden realizar modificaciones.');
      return; // Prevenir cualquier cambio
    }
    
    if (!this.informeCargado || this.clientesData.length === 0) {
      this.mensajeError = 'Debe generar un informe primero para aplicar reducciones';
      return;
    }
    
    const dialogRef = this.dialog.open(ReduccionDialogComponent, {
      width: '500px',
      data: {
        clientes: this.clientesData,
        porcentajeReduccion: 10,
        clientesSeleccionados: []
      }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.aplicarReduccionPorCliente(result.clientesSeleccionados, result.porcentajeReduccion);
      }
    });
  }
  
  // Aplicar reducción a los días trabajados para clientes seleccionados
  aplicarReduccionPorCliente(clienteIds: number[], porcentajeReduccion: number): void {
    // Verificar que los parámetros son válidos
    if (!clienteIds.length || porcentajeReduccion < 1 || porcentajeReduccion > 100) {
      this.mensajeError = 'Parámetros de reducción inválidos';
      return;
    }
    
    // Mapear IDs de clientes a sus nombres para más fácil referencia
    const clientesNombres = clienteIds.map(id => {
      const cliente = this.clientesData.find(c => c.id === id);
      return cliente ? cliente.nombre : null;
    }).filter(nombre => nombre !== null) as string[];
    
    // Aplicar reducción a cada trabajador
    this.trabajadoresData.forEach(trabajador => {
      // No aplicar reducción a trabajadores ya aprobados
      if (trabajador.aprobado) {
        return;
      }
      
      // Inicializar objeto de reducciones si no existe
      if (!trabajador.reducciones_aplicadas) {
        trabajador.reducciones_aplicadas = {};
      }
      
      // Aplicar reducción para cada cliente seleccionado
      clientesNombres.forEach(clienteNombre => {
        if (trabajador.dias_por_cliente[clienteNombre] !== undefined) {
          // Asegurar que dias_originales existe y contiene los valores correctos
          if (!trabajador.dias_originales) {
            trabajador.dias_originales = {};
          }
          
          // Importante: asegurar que el valor original se guarda correctamente antes de modificar
          if (trabajador.dias_originales[clienteNombre] === undefined) {
            trabajador.dias_originales[clienteNombre] = trabajador.dias_por_cliente[clienteNombre];
          }
          
          const diasOriginales = trabajador.dias_originales[clienteNombre];
          
          // Calcular nuevo valor con reducción
          const factorReduccion = (100 - porcentajeReduccion) / 100;
          const nuevoValorExacto = diasOriginales * factorReduccion;
          const nuevoValor = Math.round(nuevoValorExacto);
          
          // Actualizar días por cliente
          trabajador.dias_por_cliente[clienteNombre] = nuevoValor;
          
          // Guardar la información de la reducción con el valor original
          trabajador.reducciones_aplicadas[clienteNombre] = {
            porcentaje: porcentajeReduccion,
            diasOriginales: diasOriginales
          };
        }
      });
      
      // Recalcular total de días
      this.recalcularTotalDias(trabajador);
    });
    
    // Actualizar contador de trabajadores con reducciones
    this.actualizarContadorReducidos();
    
    // Mostrar mensaje de éxito
    alert(`Reducción del ${porcentajeReduccion}% aplicada a ${clientesNombres.length} cliente(s)`);
  }
  
  // Verificar si hay al menos un registro aprobado
  hayRegistrosAprobados(): boolean {
    return this.trabajadoresData.some(t => t.aprobado);
  }

  // Guardar los registros aprobados
  guardarRegistrosAprobados(): void {
    // Verificar si el mes está cerrado
    if (this.mesCerrado) {
      alert('El mes está cerrado. No se pueden realizar modificaciones.');
      return; // Prevenir guardar
    }
    
    // Filtrar solo los trabajadores aprobados
    const registrosAprobados = this.trabajadoresData.filter(t => t.aprobado);
    
    if (registrosAprobados.length === 0) {
      this.mensajeError = 'No hay registros aprobados para guardar';
      return;
    }
    
    this.cargando = true;
    
    // Preparar los registros para enviar al backend
    const promises = registrosAprobados.map(trabajador => {
      // Convertir dias_por_cliente a formato {cliente_id: dias}
      const diasPorCliente: {[key: string]: number} = {};
      this.clientesData.forEach(cliente => {
        diasPorCliente[cliente.id] = this.getDiasPorCliente(trabajador, cliente.id);
      });
      
      // Convertir reducciones_aplicadas a formato {cliente_id: reduccion}
      const reduccionesAplicadas: {[key: string]: any} = {};
      if (trabajador.reducciones_aplicadas) {
        this.clientesData.forEach(cliente => {
          const clienteNombre = cliente.nombre;
          if (trabajador.reducciones_aplicadas?.[clienteNombre]) {
            reduccionesAplicadas[cliente.id] = trabajador.reducciones_aplicadas[clienteNombre];
          }
        });
      }
      
      // Preparar datos para el registro
      const registroData = {
        holding_id: this.holding,
        trabajador_id: trabajador.id,
        mes: this.filtroForm.get('mes')?.value,
        year: this.filtroForm.get('year')?.value,
        dias_por_cliente: diasPorCliente,
        reducciones_aplicadas: reduccionesAplicadas,
        dias_totales: trabajador.dias_totales
      };
      
      // Enviar al backend
      return this.apiService.post('dias-trabajados-aprobados/', registroData).toPromise();
    });
    
    // Procesar todas las peticiones en paralelo
    Promise.all(promises)
      .then(responses => {
        this.cargando = false;
        
        // Marcar los trabajadores como registrados en DB
        registrosAprobados.forEach(t => {
          t.registrado_en_db = true;
        });
        
        // Actualizar la lista de registros existentes
        this.generarInforme();
        
        // Mostrar mensaje de éxito
        alert(`Se han guardado ${registrosAprobados.length} registros correctamente`);
      })
      .catch(error => {
        this.cargando = false;
        this.mensajeError = 'Error al guardar los registros aprobados';
        console.error('Error guardando registros:', error);
      });
  }
}