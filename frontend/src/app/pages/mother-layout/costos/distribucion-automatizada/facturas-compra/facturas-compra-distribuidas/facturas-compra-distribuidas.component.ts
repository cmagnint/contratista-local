import { Component, OnInit, Inject, PLATFORM_ID } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup } from '@angular/forms';
import { ContratistaApiService } from '../../../../../../services/contratista-api.service';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatIconModule } from '@angular/material/icon';
import { MatSelectModule } from '@angular/material/select';
import { MatTableModule } from '@angular/material/table';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatPaginatorModule, PageEvent } from '@angular/material/paginator';
import { MatSortModule, Sort } from '@angular/material/sort';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatChipsModule } from '@angular/material/chips';


interface FacturaCompraDistribuida {
  id: number;
  folio: string;
  tipo_doc: string;
  tipo_compra: string;
  rut_proveedor: string;
  razon_social: string;
  fecha_docto: string;
  fecha_recepcion: string;
  fecha_acuse: string;
  monto_exento: number;
  monto_neto: number;
  monto_iva_recuperable: number;
  monto_iva_no_recuperable: number;
  codigo_iva_no_rec: string;
  monto_total: number;
  monto_neto_activo_fijo: number;
  iva_activo_fijo: number;
  iva_uso_comun: number;
  impto_sin_derecho_credito: number;
  iva_no_retenido: number;
  tabacos_puros: number;
  tabacos_cigarrillos: number;
  tabacos_elaborados: number;
  nce_nde_fact_compra: number;
  codigo_otro_impuesto: string;
  valor_otro_impuesto: number;
  tasa_otro_impuesto: number;
  cliente_nombre: string;
  cliente_rut: string;
  fundo_nombre: string;
  labor_nombre: string;
  cuenta_nombre: string;
  cuenta_codigo: string;
  usuario_nombre: string;
  fecha_distribucion: string;
  observaciones: string;
  selected: boolean;
}

interface FacturaAgrupada {
  folio: string;
  tipo_doc: string;
  rut_proveedor: string;
  razon_social: string;
  fecha_docto: string;
  monto_total_original: number;
  monto_total_distribuido: number;
  cantidad_distribuciones: number;
  distribuciones: FacturaCompraDistribuida[];
  expanded: boolean;
  selected: boolean;
  fecha_primera_distribucion: string;
}

interface Cliente {
  id: number;
  nombre: string;
  rut: string;
}

interface Fundo {
  id: number;
  nombre_campo: string;
  direccion_campo: string;
}

interface Labor {
  id: number;
  nombre: string;
  especie: string;
}

interface Cuenta {
  id: number;
  nombre_cuenta: string;
  cuenta_contable: string;
}
@Component({
  selector: 'app-facturas-compra-distribuidas',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatProgressBarModule,
    MatButtonModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatIconModule,
    MatSelectModule,
    MatTableModule,
    MatCheckboxModule,
    MatProgressSpinnerModule,
    MatPaginatorModule,
    MatSortModule,
    MatTooltipModule,
    MatChipsModule
  ],
  templateUrl: './facturas-compra-distribuidas.component.html',
  styleUrl: './facturas-compra-distribuidas.component.css'
})
export class FacturasCompraDistribuidasComponent implements OnInit {

  // Variables de estado
  loading = false;
  loadingExport = false;
  error: string | null = null;
  holding: string = '';

  // Formulario de filtros
  filtrosForm: FormGroup;

  // Datos para filtros
  clientes: Cliente[] = [];
  fundos: Fundo[] = [];
  labores: Labor[] = [];
  cuentas: Cuenta[] = [];

  // Datos de facturas
  facturasOriginales: FacturaCompraDistribuida[] = [];
  facturasAgrupadas: FacturaAgrupada[] = [];
  facturasParaMostrar: FacturaAgrupada[] = [];

  // Configuración de tabla
  displayedColumns: string[] = [
    'select',
    'expand',
    'folio',
    'tipo_doc',
    'fecha_docto',
    'razon_social',
    'monto_total_original',
    'monto_total_distribuido',
    'cantidad_distribuciones',
    'fecha_primera_distribucion',
    'acciones'
  ];

  // Paginación
  pageSize = 25;
  pageSizeOptions = [10, 25, 50, 100];
  totalItems = 0;
  currentPage = 0;

  // Ordenamiento
  currentSort: Sort = { active: 'fecha_primera_distribucion', direction: 'desc' };

  // Selección
  allSelected = false;
  someSelected = false;

  constructor(
    private fb: FormBuilder,
    private apiService: ContratistaApiService,
    private snackBar: MatSnackBar,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {
    this.filtrosForm = this.fb.group({
      cliente_id: [''],
      fundo_id: [{ value: '', disabled: true }], // Inicialmente deshabilitado
      labor_id: [''],
      cuenta_id: [''],
      fecha_desde: [''],
      fecha_hasta: [''],
      folio: [''],
      razon_social: ['']
    });
  }

  ngOnInit(): void {
    if (isPlatformBrowser(this.platformId)) {
      this.holding = localStorage.getItem('holding_id') || '';
      this.inicializarComponente();
    }
  }

  async inicializarComponente(): Promise<void> {
    await Promise.all([
      this.cargarDatosDistribucion(),
      this.cargarFacturasDistribuidas()
    ]);
  }

  // ==================== CARGA DE DATOS ====================

  cargarDatosDistribucion(): Promise<void> {
    return new Promise((resolve, reject) => {
      this.apiService.post('facturas_sii_compra_distribuidas/', {
        action: 'get_distribution_data'
      }).subscribe({
        next: (response) => {
          if (response.status === 'success') {
            const data = response.data;
            this.clientes = data.clientes || [];
            this.labores = data.labores || [];
            this.cuentas = data.cuentas || [];
            console.log('Datos de distribución cargados');
            resolve();
          } else {
            this.error = 'Error al cargar datos de distribución';
            reject();
          }
        },
        error: (error) => {
          console.error('Error al cargar datos de distribución:', error);
          this.error = 'Error al cargar datos de distribución';
          reject();
        }
      });
    });
  }

  cargarFacturasDistribuidas(): void {
    this.loading = true;
    this.error = null;

    // Preparar filtros
    const filtros = this.obtenerFiltrosActivos();

    this.apiService.post('facturas_sii_compra_distribuidas/', {
      action: 'list_distributed_invoices',
      holding_id: this.holding,
      filtros: filtros
    }).subscribe({
      next: (response) => {
        this.loading = false;
        if (response.status === 'success') {
          this.facturasOriginales = response.data.facturas || [];
          this.agruparFacturas();
          this.aplicarFiltrosYOrdenamiento();
          console.log(`Facturas distribuidas cargadas: ${this.facturasOriginales.length} -> ${this.facturasAgrupadas.length} agrupadas`);
        } else {
          this.error = response.message || 'Error al cargar facturas distribuidas';
          this.facturasOriginales = [];
          this.facturasAgrupadas = [];
          this.facturasParaMostrar = [];
        }
      },
      error: (error) => {
        this.loading = false;
        console.error('Error al cargar facturas:', error);
        this.error = 'Error al cargar facturas distribuidas';
        this.facturasOriginales = [];
        this.facturasAgrupadas = [];
        this.facturasParaMostrar = [];
      }
    });
  }

  // ==================== AGRUPACIÓN DE FACTURAS ====================

  agruparFacturas(): void {
    const facturasPorFolio = new Map<string, FacturaCompraDistribuida[]>();

    // Agrupar facturas por folio
    this.facturasOriginales.forEach(factura => {
      const key = `${factura.folio}-${factura.tipo_doc}-${factura.rut_proveedor}`;
      if (!facturasPorFolio.has(key)) {
        facturasPorFolio.set(key, []);
      }
      facturasPorFolio.get(key)!.push(factura);
    });

    // Crear objetos de facturas agrupadas
    this.facturasAgrupadas = Array.from(facturasPorFolio.entries()).map(([key, distribuciones]) => {
      const primera = distribuciones[0];
      
      // Calcular monto total distribuido
      const montoTotalDistribuido = distribuciones.reduce((sum, d) => sum + d.monto_total, 0);
      
      // Encontrar la fecha de primera distribución
      const fechaPrimeraDistribucion = distribuciones
        .map(d => new Date(d.fecha_distribucion))
        .sort((a, b) => a.getTime() - b.getTime())[0];

      // Para el monto original, usamos el monto total distribuido como referencia
      const montoTotalOriginal = montoTotalDistribuido;

      return {
        folio: primera.folio,
        tipo_doc: primera.tipo_doc,
        rut_proveedor: primera.rut_proveedor,
        razon_social: primera.razon_social,
        fecha_docto: primera.fecha_docto,
        monto_total_original: montoTotalOriginal,
        monto_total_distribuido: montoTotalDistribuido,
        cantidad_distribuciones: distribuciones.length,
        distribuciones: distribuciones.sort((a, b) => 
          new Date(a.fecha_distribucion).getTime() - new Date(b.fecha_distribucion).getTime()
        ),
        expanded: false,
        selected: false,
        fecha_primera_distribucion: fechaPrimeraDistribucion.toISOString()
      };
    });
  }

  // ==================== EXPANSIÓN/COLAPSO ====================

  toggleExpansion(factura: FacturaAgrupada): void {
    if (factura.cantidad_distribuciones > 1) {
      factura.expanded = !factura.expanded;
    }
  }

  expandirTodas(): void {
    this.facturasParaMostrar.forEach(f => {
      if (f.cantidad_distribuciones > 1) {
        f.expanded = true;
      }
    });
  }

  colapsarTodas(): void {
    this.facturasParaMostrar.forEach(f => f.expanded = false);
  }

  // ==================== FILTROS ====================

  onClienteSeleccionado(): void {
    const clienteId = this.filtrosForm.get('cliente_id')?.value;
    const fundoControl = this.filtrosForm.get('fundo_id');
    
    if (!clienteId) {
      this.fundos = [];
      fundoControl?.setValue('');
      fundoControl?.disable(); // Deshabilitar cuando no hay cliente seleccionado
      return;
    }

    // Habilitar el control de fundo cuando hay cliente seleccionado
    fundoControl?.enable();

    // Cargar fundos del cliente seleccionado
    this.apiService.get(`api_campos_clientes/${clienteId}/`).subscribe({
      next: (response) => {
        this.fundos = response || [];
        fundoControl?.setValue('');
      },
      error: (error) => {
        console.error('Error al cargar fundos:', error);
        this.fundos = [];
        fundoControl?.setValue('');
      }
    });
  }

  aplicarFiltros(): void {
    this.cargarFacturasDistribuidas();
  }

  limpiarFiltros(): void {
    this.filtrosForm.reset();
    this.fundos = [];
    
    // Deshabilitar el control de fundo al limpiar filtros
    const fundoControl = this.filtrosForm.get('fundo_id');
    fundoControl?.setValue('');
    fundoControl?.disable();
    
    this.cargarFacturasDistribuidas();
  }

  obtenerFiltrosActivos(): any {
    // Usar getRawValue() para incluir valores de controles deshabilitados
    const formValue = this.filtrosForm.getRawValue();
    const filtros: any = {};

    // Solo incluir filtros que tengan valor
    Object.keys(formValue).forEach(key => {
      if (formValue[key] && formValue[key] !== '') {
        filtros[key] = formValue[key];
      }
    });

    return filtros;
  }

  // ==================== TABLA Y PAGINACIÓN ====================

  aplicarFiltrosYOrdenamiento(): void {
    // Para filtros locales adicionales se pueden agregar aquí
    let facturasFiltradas = [...this.facturasAgrupadas];

    // Aplicar ordenamiento
    this.aplicarOrdenamiento(facturasFiltradas);

    // Actualizar paginación
    this.totalItems = facturasFiltradas.length;
    this.currentPage = 0;
    this.actualizarPagina(facturasFiltradas);
  }

  aplicarOrdenamiento(facturas: FacturaAgrupada[]): void {
    if (!this.currentSort.active || this.currentSort.direction === '') {
      return;
    }

    facturas.sort((a, b) => {
      const isAsc = this.currentSort.direction === 'asc';
      const valueA = this.getPropertyValue(a, this.currentSort.active);
      const valueB = this.getPropertyValue(b, this.currentSort.active);

      // Comparación para números
      if (typeof valueA === 'number' && typeof valueB === 'number') {
        return (valueA - valueB) * (isAsc ? 1 : -1);
      }

      // Comparación para fechas
      if (this.currentSort.active.includes('fecha')) {
        const dateA = new Date(valueA).getTime();
        const dateB = new Date(valueB).getTime();
        return (dateA - dateB) * (isAsc ? 1 : -1);
      }

      // Comparación para strings
      const stringA = (valueA || '').toString().toLowerCase();
      const stringB = (valueB || '').toString().toLowerCase();
      return stringA.localeCompare(stringB) * (isAsc ? 1 : -1);
    });
  }

  getPropertyValue(obj: any, property: string): any {
    return property.split('.').reduce((o, p) => o && o[p], obj);
  }

  onSortChange(sort: Sort): void {
    this.currentSort = sort;
    this.aplicarFiltrosYOrdenamiento();
  }

  onPageChange(event: PageEvent): void {
    this.currentPage = event.pageIndex;
    this.pageSize = event.pageSize;
    this.actualizarPagina();
  }

  actualizarPagina(facturasFiltradas?: FacturaAgrupada[]): void {
    const facturas = facturasFiltradas || this.facturasAgrupadas;
    const startIndex = this.currentPage * this.pageSize;
    const endIndex = startIndex + this.pageSize;
    this.facturasParaMostrar = facturas.slice(startIndex, endIndex);
    
    // Reinicializar selección después de cambio de página
    this.facturasParaMostrar.forEach(factura => factura.selected = false);
    this.actualizarEstadoSeleccion();
  }

  // ==================== SELECCIÓN ====================

  onFacturaSeleccionada(factura: FacturaAgrupada): void {
    factura.selected = !factura.selected;
    this.actualizarEstadoSeleccion();
  }

  onSelectAll(): void {
    const newState = !this.allSelected;
    this.facturasParaMostrar.forEach(factura => {
      factura.selected = newState;
    });
    this.actualizarEstadoSeleccion();
  }

  actualizarEstadoSeleccion(): void {
    const seleccionadas = this.facturasParaMostrar.filter(f => f.selected);
    this.allSelected = seleccionadas.length === this.facturasParaMostrar.length && this.facturasParaMostrar.length > 0;
    this.someSelected = seleccionadas.length > 0 && seleccionadas.length < this.facturasParaMostrar.length;
  }

  getFacturasSeleccionadas(): FacturaAgrupada[] {
    return this.facturasAgrupadas.filter(f => f.selected);
  }

  // ==================== EXPORTAR CSV ====================

  descargarCSV(): void {
    const facturasSeleccionadas = this.getFacturasSeleccionadas();
    
    if (facturasSeleccionadas.length === 0) {
      this.snackBar.open('Debe seleccionar al menos una factura para descargar', 'Cerrar', {
        duration: 5000,
        panelClass: ['warning-snackbar']
      });
      return;
    }

    this.loadingExport = true;

    // Obtener todos los IDs de las distribuciones de las facturas seleccionadas
    const distribucionIds: number[] = [];
    facturasSeleccionadas.forEach(factura => {
      factura.distribuciones.forEach(distribucion => {
        distribucionIds.push(distribucion.id);
      });
    });

    this.apiService.post('facturas_sii_compra_distribuidas/', {
      action: 'export_distributed_invoices_csv',
      holding_id: this.holding,
      factura_ids: distribucionIds
    }).subscribe({
      next: (response) => {
        this.loadingExport = false;
        
        if (response.status === 'success') {
          // Crear y descargar archivo CSV
          const blob = new Blob([response.data.csv_content], { type: 'text/csv;charset=utf-8;' });
          const link = document.createElement('a');
          
          if (link.download !== undefined) {
            const url = URL.createObjectURL(blob);
            link.setAttribute('href', url);
            link.setAttribute('download', response.data.filename);
            link.style.visibility = 'hidden';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
          }

          const totalDistribuciones = distribucionIds.length;
          this.snackBar.open(`CSV descargado: ${facturasSeleccionadas.length} facturas (${totalDistribuciones} distribuciones)`, 'Cerrar', {
            duration: 5000,
            panelClass: ['success-snackbar']
          });

          // Deseleccionar facturas
          facturasSeleccionadas.forEach(f => f.selected = false);
          this.actualizarEstadoSeleccion();

        } else {
          this.snackBar.open('Error al generar CSV: ' + response.message, 'Cerrar', {
            duration: 7000,
            panelClass: ['error-snackbar']
          });
        }
      },
      error: (error) => {
        this.loadingExport = false;
        console.error('Error al descargar CSV:', error);
        this.snackBar.open('Error al descargar CSV', 'Cerrar', {
          duration: 7000,
          panelClass: ['error-snackbar']
        });
      }
    });
  }

  // ==================== MÉTODOS AUXILIARES ====================

  formatearMonto(monto: number): string {
    return new Intl.NumberFormat('es-CL', {
      style: 'currency',
      currency: 'CLP',
      minimumFractionDigits: 0
    }).format(monto);
  }

  formatearFecha(fecha: string): string {
    if (!fecha) return '';
    try {
      return new Date(fecha).toLocaleDateString('es-CL');
    } catch {
      return fecha;
    }
  }

  getTotalSeleccionado(): number {
    return this.getFacturasSeleccionadas().reduce((sum, factura) => sum + factura.monto_total_distribuido, 0);
  }

  getCantidadSeleccionada(): number {
    return this.getFacturasSeleccionadas().length;
  }

  getTotalDistribucionesSeleccionadas(): number {
    return this.getFacturasSeleccionadas().reduce((sum, factura) => sum + factura.cantidad_distribuciones, 0);
  }

  // ==================== MÉTODOS DE UTILIDAD ====================

  getDistribucionesUnicas(): string[] {
    const facturas = this.getFacturasSeleccionadas();
    const clientes = new Set<string>();
    
    facturas.forEach(factura => {
      factura.distribuciones.forEach(dist => {
        if (dist.cliente_nombre) {
          clientes.add(dist.cliente_nombre);
        }
      });
    });
    
    return Array.from(clientes);
  }
}
