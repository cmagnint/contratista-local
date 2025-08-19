// facturas-venta-automatizada.component.ts - ACTUALIZADO CON MEJORAS BOLETA MANUAL

import { Component, OnInit, OnDestroy, Inject, PLATFORM_ID } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ContratistaApiService } from '../../../../../../services/contratista-api.service';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatIconModule } from '@angular/material/icon';
import { MatDividerModule } from '@angular/material/divider';
import { MatSelectModule } from '@angular/material/select';
import { MatTableModule } from '@angular/material/table';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatDialogModule, MatDialog } from '@angular/material/dialog';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatChipsModule } from '@angular/material/chips';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatMenuModule } from '@angular/material/menu';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { Subscription, interval, firstValueFrom } from 'rxjs';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatRadioModule } from '@angular/material/radio';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';

// ==================== INTERFACES ACTUALIZADAS ====================

interface FacturaDistribucion {
  id: number;
  nro?: string;
  tipo_doc: string;
  tipo_compra: string;
  rut_receptor: string;
  razon_social: string;
  folio: string;
  fecha_docto: string;
  fecha_recepcion: string;
  fecha_acuse?: string;
  
  // Montos
  monto_total: number;
  monto_neto: number;
  monto_exento: number;
  monto_iva_recuperable: number;
  monto_iva_no_recuperable?: number;
  codigo_iva_no_rec?: string;
  monto_neto_activo_fijo?: number;
  iva_activo_fijo?: number;
  iva_uso_comun?: number;
  impto_sin_derecho_credito?: number;
  iva_no_retenido?: number;
  tabacos_puros?: number;
  tabacos_cigarrillos?: number;
  tabacos_elaborados?: number;
  nce_nde_fact_compra?: number;
  codigo_otro_impuesto?: string;
  valor_otro_impuesto?: number;
  tasa_otro_impuesto?: number;
  
  fecha_encontrada: string;
  
  // CAMPOS DE DISTRIBUCIÓN MÚLTIPLE
  monto_distribuido: number;
  monto_pendiente: number;
  porcentaje_distribuido: number;
  porcentaje_pendiente: number;
  completamente_distribuida: boolean;
  distribuciones_count: number;
  distribuciones: DistribucionExistente[];
  
  // PDF
  pdf_disponible: boolean;
  pdf_url?: string;
  pdf_descargado: boolean;
  fecha_descarga_pdf?: string;
  error_descarga_pdf?: string;
  intentos_descarga_pdf?: number;
  codigo_sii?: string;
  
  procesada: boolean;
  selected: boolean; // Para selección múltiple
  holding?: number;
  
  // CAMPOS PARA IDENTIFICAR FACTURAS MANUALES
  es_manual?: boolean;
  descripcion?: string;
}

interface DistribucionExistente {
  id: number;
  cliente: {
    id: number;
    nombre: string;
    rut: string;
  };
  fundo?: {
    id: number;
    nombre: string;
  };
  labor?: {
    id: number;
    nombre: string;
  };
  cuenta?: {
    id: number;
    nombre: string;
    codigo: string;
  };
  monto_distribuido: number;
  porcentaje_distribuido: number;
  tipo_distribucion: string;
  fecha_distribucion: string;
  observaciones?: string;
  usuario_distribuyente?: {
    id: number;
    nombre: string;
    rut: string;
  };
}

interface EstadisticasPDF {
  total_facturas: number;
  facturas_con_pdf: number;
  facturas_sin_pdf: number;
  facturas_error_pdf: number;
  porcentaje_con_pdf: number;
  porcentaje_sin_pdf: number;
  porcentaje_error_pdf: number;
  facturas_0_intentos?: number;
  facturas_1_2_intentos?: number;
  facturas_3_mas_intentos?: number;
  fecha_actualizacion?: string;
}

interface EstadisticasDistribucion {
  total_facturas: number;
  facturas_sin_distribuir: number;
  facturas_parcialmente_distribuidas: number;
  facturas_con_alguna_distribucion: number;
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
  comuna_campo: string;
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
  activa: boolean;
}

interface ProcesoAutomaticoStatus {
  estado: 'inactivo' | 'ejecutando' | 'completado' | 'error';
  ultima_ejecucion?: string;
  proxima_ejecucion?: string;
  facturas_encontradas: number;
  mensaje?: string;
  configuracion_activa?: boolean;
  periodo_configurado?: string;
}

// Interface para distribución múltiple
interface DistribucionMultiple {
  facturas: FacturaDistribucion[];
  tipo_distribucion_multiple: 'INDIVIDUAL' | 'GRUPAL';
  monto_total_disponible: number;
  monto_minimo_por_factura: number;
}

// Interface para factura manual ACTUALIZADA
interface FacturaManual {
  tipo_doc: string;
  rut_receptor: string;
  razon_social_receptor: string;
  folio?: string; // Ya no es requerido, será automático
  fecha_emision: string;
  monto_total: number;
  monto_neto: number;
  // Eliminado monto_exento y monto_iva (no hay IVA en boletas)
  descripcion?: string;
  observaciones?: string;
}

@Component({
  selector: 'app-facturas-venta-automatizada',
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
    MatDividerModule,
    MatSelectModule,
    MatTableModule,
    MatCheckboxModule,
    MatDialogModule,
    MatProgressSpinnerModule,
    MatChipsModule,
    MatTooltipModule,
    MatMenuModule,
    MatSlideToggleModule,
    MatPaginatorModule,
    MatRadioModule,
    MatDatepickerModule,
    MatNativeDateModule,
  ],
  templateUrl: './facturas-venta-automatizada.component.html',
  styleUrl: './facturas-venta-automatizada.component.css'
})
export class FacturasVentaAutomatizadaComponent implements OnInit, OnDestroy {
  
  // ==================== FORMULARIOS ====================
  
  distribucionForm: FormGroup;
  periodoForm: FormGroup;
  facturaManualForm: FormGroup;

  // ==================== ESTADOS DE LA APLICACIÓN ====================
  
  loading = false;
  loadingFacturas = false;
  loadingDistribucion = false;
  loadingFundos = false;
  loadingPdfSearch = false;
  loadingCrearFactura = false;
  error: string | null = null;
  success: string | null = null;
  public holding: string = '';
  
  // ==================== DATOS ====================
  
  facturas: FacturaDistribucion[] = [];
  facturasFiltradas: FacturaDistribucion[] = [];
  clientes: Cliente[] = [];
  fundos: Fundo[] = [];
  labores: Labor[] = [];
  cuentas: Cuenta[] = [];
  
  // ==================== SELECCIÓN MÚLTIPLE ====================
  
  facturaSeleccionada: FacturaDistribucion | null = null;
  facturasSeleccionadas: FacturaDistribucion[] = [];
  distribucionMultiple: DistribucionMultiple | null = null;
  modoDistribucionMultiple = false;
  
  // ==================== ESTADOS DE UI ====================
  
  mostrarDialogoDistribucion = false;
  mostrarDialogoDistribuciones = false;
  mostrarDialogoFacturaManual = false;
  
  // ==================== FILTROS ====================
  
  filtroEstado = 'todos';
  filtroTexto = '';
  filtroTipo = 'todos'; // todos, sii, manual
  
  // ==================== ESTADÍSTICAS ====================
  
  estadisticasPdf: EstadisticasPDF = {
    total_facturas: 0,
    facturas_con_pdf: 0,
    facturas_sin_pdf: 0,
    facturas_error_pdf: 0,
    porcentaje_con_pdf: 0,
    porcentaje_sin_pdf: 0,
    porcentaje_error_pdf: 0,
    facturas_0_intentos: 0,
    facturas_1_2_intentos: 0,
    facturas_3_mas_intentos: 0,
    fecha_actualizacion: ''
  };
  
  estadisticasDistribucion: EstadisticasDistribucion = {
    total_facturas: 0,
    facturas_sin_distribuir: 0,
    facturas_parcialmente_distribuidas: 0,
    facturas_con_alguna_distribucion: 0
  };
  
  mostrarEstadisticasPdf = true;
  
  // ==================== PROCESO AUTOMÁTICO ====================
  
  procesoStatus: ProcesoAutomaticoStatus = {
    estado: 'inactivo',
    facturas_encontradas: 0,
    configuracion_activa: false
  };
  
  // ==================== CONFIGURACIÓN ====================
  
  mesesOptions = [
    { value: 1, label: 'Enero' },
    { value: 2, label: 'Febrero' },
    { value: 3, label: 'Marzo' },
    { value: 4, label: 'Abril' },
    { value: 5, label: 'Mayo' },
    { value: 6, label: 'Junio' },
    { value: 7, label: 'Julio' },
    { value: 8, label: 'Agosto' },
    { value: 9, label: 'Septiembre' },
    { value: 10, label: 'Octubre' },
    { value: 11, label: 'Noviembre' },
    { value: 12, label: 'Diciembre' }
  ];

  yearOptions: number[] = [];
  configuracionCargada = false;
  
  // ==================== FOLIO AUTOMÁTICO ====================
  
  proximoFolio: number = 1; // Próximo folio automático
  
  // ==================== TABLA CON SELECCIÓN ====================
  
  displayedColumns: string[] = ['select', 'folio', 'proveedor', 'montos', 'progreso', 'pdf', 'acciones'];
  
  // ==================== SUBSCRIPCIONES ====================
  
  statusSubscription: Subscription | null = null;
  
  constructor(
    private fb: FormBuilder,
    private apiService: ContratistaApiService,
    private snackBar: MatSnackBar,
    private dialog: MatDialog,
    @Inject(PLATFORM_ID) private platformId: Object,
  ) {
    // Inicializar arrays
    this.facturas = [];
    this.facturasFiltradas = [];
    this.clientes = [];
    this.fundos = [];
    this.labores = [];
    this.cuentas = [];
    this.facturasSeleccionadas = [];

    // Generar opciones de años
    const currentYear = new Date().getFullYear();
    for (let year = 2020; year <= currentYear + 2; year++) {
      this.yearOptions.push(year);
    }

    // Formulario para período
    this.periodoForm = this.fb.group({
      mes: [new Date().getMonth() + 1, [Validators.required, Validators.min(1), Validators.max(12)]],
      year: [new Date().getFullYear(), [Validators.required, Validators.min(2020)]]
    });

    // Formulario para distribución (simple y múltiple)
    this.distribucionForm = this.fb.group({
      tipo_distribucion: ['MONTO', Validators.required],
      tipo_distribucion_multiple: ['INDIVIDUAL'], // INDIVIDUAL o GRUPAL
      monto_a_distribuir: [null],
      porcentaje_a_distribuir: [null],
      cliente_id: [null, Validators.required],
      fundo_id: [null],
      labor_id: [null],
      cuenta_id: [null],
      observaciones: ['']
    });

    // Formulario para factura manual ACTUALIZADO - SIMPLIFICADO
    this.facturaManualForm = this.fb.group({
      // tipo_doc eliminado - siempre será 'BOLETA_MANUAL'
      rut_receptor: ['', [Validators.required, Validators.pattern(/^\d{1,8}-[\dkK]$/)]],
      razon_social_receptor: ['', [Validators.required, Validators.minLength(3)]],
      // folio eliminado - será automático
      fecha_emision: [new Date(), Validators.required],
      monto_total: [0, [Validators.required, Validators.min(1)]],
      monto_neto: [0, [Validators.required, Validators.min(0)]],
      // monto_exento y monto_iva eliminados
      descripcion: ['', [Validators.required, Validators.minLength(5)]],
      observaciones: ['']
    });

    if (isPlatformBrowser(this.platformId)) {
      this.holding = localStorage.getItem('holding') || '';
    }
  }

  ngOnInit(): void {
    if (isPlatformBrowser(this.platformId)) {
      this.cargarDatosIniciales();
      this.iniciarMonitoreoStatus();
    }
  }

  ngOnDestroy(): void {
    if (this.statusSubscription) {
      this.statusSubscription.unsubscribe();
    }
  }

  onFiltroTextoChange(event: Event): void {
    const target = event.target as HTMLInputElement;
    this.filtroTexto = target.value;
    this.aplicarFiltros();
  }

  // ==================== CARGA INICIAL ====================

  async cargarDatosIniciales(): Promise<void> {
    await Promise.all([
      this.cargarConfiguracionPeriodo(),
      this.cargarFacturas(),
      this.cargarDatosDistribucion(),
      this.cargarProximoFolio() // NUEVO: Cargar próximo folio
    ]);
  }

  async cargarConfiguracionPeriodo(): Promise<void> {
    try {
      const response = await firstValueFrom(this.apiService.post('facturas_venta_automatico/', {
        action: 'get_automatic_configuration'
      }));
      
      if (response?.status === 'success' && response.data) {
        const config = response.data;
        
        this.periodoForm.patchValue({
          mes: config.mes || new Date().getMonth() + 1,
          year: config.year || new Date().getFullYear()
        });
        
        this.configuracionCargada = true;
        console.log('Período cargado:', `${config.mes}/${config.year}`);
      } else {
        console.log('No hay configuración de período guardada');
        this.configuracionCargada = false;
      }
    } catch (error: any) {
      console.error('Error cargando configuración de período:', error);
      this.configuracionCargada = false;
    }
  }

  // NUEVO: Cargar próximo folio automático
  async cargarProximoFolio(): Promise<void> {
    try {
      const response = await firstValueFrom(this.apiService.post('facturas_venta_automatico/', {
        action: 'get_next_folio'
      }));
      
      if (response?.status === 'success') {
        this.proximoFolio = response.next_folio || 1;
        console.log('Próximo folio automático:', this.proximoFolio);
      } else {
        this.proximoFolio = 1;
        console.log('No se pudo obtener próximo folio, usando 1 por defecto');
      }
    } catch (error: any) {
      console.error('Error cargando próximo folio:', error);
      this.proximoFolio = 1;
    }
  }

  async cargarFacturas(): Promise<void> {
    this.loadingFacturas = true;
    
    try {
      const response = await firstValueFrom(this.apiService.post('facturas_venta_automatico/', {
        action: 'get_automatic_invoices'
      }));
      
      if (response?.status === 'success') {
        // Mapear los datos del backend a la estructura del frontend
        this.facturas = (response.facturas || []).map((facturaRaw: any) => {
          const factura: FacturaDistribucion = {
            // Campos básicos
            id: facturaRaw.id,
            nro: facturaRaw.nro || facturaRaw.id?.toString() || '',
            tipo_doc: facturaRaw.tipo_doc || '',
            tipo_compra: facturaRaw.tipo_compra || '',
            rut_receptor: facturaRaw.rut_receptor || '',
            razon_social: facturaRaw.razon_social_receptor || facturaRaw.razon_social || '',
            folio: facturaRaw.folio || '',
            fecha_docto: facturaRaw.fecha_emision || facturaRaw.fecha_docto || '',
            fecha_recepcion: facturaRaw.fecha_recepcion || '',
            fecha_acuse: facturaRaw.fecha_acuse || '',
            
            // Montos - mapeo correcto desde el backend
            monto_total: Number(facturaRaw.monto_total) || 0,
            monto_neto: Number(facturaRaw.monto_neto) || 0,
            monto_exento: Number(facturaRaw.monto_exento) || 0,
            monto_iva_recuperable: Number(facturaRaw.monto_iva) || Number(facturaRaw.monto_iva_recuperable) || 0,
            monto_iva_no_recuperable: Number(facturaRaw.monto_iva_no_recuperable) || 0,
            codigo_iva_no_rec: facturaRaw.codigo_iva_no_rec || '',
            monto_neto_activo_fijo: Number(facturaRaw.monto_neto_activo_fijo) || 0,
            iva_activo_fijo: Number(facturaRaw.iva_activo_fijo) || 0,
            iva_uso_comun: Number(facturaRaw.iva_uso_comun) || 0,
            impto_sin_derecho_credito: Number(facturaRaw.impto_sin_derecho_credito) || 0,
            iva_no_retenido: Number(facturaRaw.iva_no_retenido) || 0,
            tabacos_puros: Number(facturaRaw.tabacos_puros) || 0,
            tabacos_cigarrillos: Number(facturaRaw.tabacos_cigarrillos) || 0,
            tabacos_elaborados: Number(facturaRaw.tabacos_elaborados) || 0,
            nce_nde_fact_compra: Number(facturaRaw.nce_nde_fact_compra) || 0,
            codigo_otro_impuesto: facturaRaw.codigo_otro_impuesto || '',
            valor_otro_impuesto: Number(facturaRaw.valor_otro_impuesto) || 0,
            tasa_otro_impuesto: Number(facturaRaw.tasa_otro_impuesto) || 0,
            
            fecha_encontrada: facturaRaw.fecha_encontrada || '',
            
            // CAMPOS DE DISTRIBUCIÓN MÚLTIPLE
            monto_distribuido: Number(facturaRaw.monto_distribuido) || 0,
            monto_pendiente: Number(facturaRaw.monto_pendiente) || Number(facturaRaw.monto_total) || 0,
            porcentaje_distribuido: Number(facturaRaw.porcentaje_distribuido) || 0,
            porcentaje_pendiente: Number(facturaRaw.porcentaje_pendiente) || 100,
            completamente_distribuida: Boolean(facturaRaw.completamente_distribuida) || false,
            distribuciones_count: Number(facturaRaw.distribuciones_count) || 0,
            distribuciones: this.mapearDistribuciones(facturaRaw.distribuciones || []),
            
            // CAMPOS DE PDF
            pdf_disponible: Boolean(facturaRaw.pdf_disponible) || Boolean(facturaRaw.pdf_descargado) || false,
            pdf_url: facturaRaw.pdf_url || null,
            pdf_descargado: Boolean(facturaRaw.pdf_descargado) || false,
            fecha_descarga_pdf: facturaRaw.fecha_descarga_pdf || '',
            error_descarga_pdf: facturaRaw.error_descarga_pdf || '',
            intentos_descarga_pdf: Number(facturaRaw.intentos_descarga_pdf) || 0,
            codigo_sii: facturaRaw.codigo_sii || '',
            
            // Campos de control
            procesada: Boolean(facturaRaw.procesada) || false,
            selected: false, // Para selección múltiple
            holding: facturaRaw.holding,
            
            // CAMPOS PARA IDENTIFICAR FACTURAS MANUALES
            es_manual: this.esFacturaManual(facturaRaw.tipo_doc),
            descripcion: facturaRaw.descripcion || ''
          };
          
          return factura;
        });
        
        // Actualizar estadísticas
        if (response.estadisticas) {
          this.estadisticasPdf = {
            total_facturas: Number(response.estadisticas.total_facturas) || 0,
            facturas_con_pdf: Number(response.estadisticas.facturas_con_pdf) || 0,
            facturas_sin_pdf: Number(response.estadisticas.facturas_sin_pdf) || 0,
            facturas_error_pdf: Number(response.estadisticas.facturas_error_pdf) || 0,
            porcentaje_con_pdf: Number(response.estadisticas.porcentaje_con_pdf) || 0,
            porcentaje_sin_pdf: Number(response.estadisticas.porcentaje_sin_pdf) || 0,
            porcentaje_error_pdf: Number(response.estadisticas.porcentaje_error_pdf) || 0,
            facturas_0_intentos: Number(response.estadisticas.facturas_0_intentos) || 0,
            facturas_1_2_intentos: Number(response.estadisticas.facturas_1_2_intentos) || 0,
            facturas_3_mas_intentos: Number(response.estadisticas.facturas_3_mas_intentos) || 0,
            fecha_actualizacion: response.estadisticas.fecha_actualizacion || new Date().toISOString()
          };
          
          this.estadisticasDistribucion = {
            total_facturas: Number(response.estadisticas.total_facturas) || 0,
            facturas_sin_distribuir: Number(response.estadisticas.facturas_sin_distribuir) || 0,
            facturas_parcialmente_distribuidas: Number(response.estadisticas.facturas_parcialmente_distribuidas) || 0,
            facturas_con_alguna_distribucion: Number(response.estadisticas.facturas_con_alguna_distribucion) || 0
          };
        }
        
        this.aplicarFiltros();
        console.log(`Facturas cargadas y mapeadas: ${this.facturas.length}`, this.facturas);
      } else {
        this.facturas = [];
        this.facturasFiltradas = [];
        console.warn('No se recibieron facturas del backend:', response);
      }
    } catch (error: any) {
      console.error('Error cargando facturas:', error);
      this.mostrarError('Error al cargar facturas: ' + (error.error?.message || error.message));
      this.facturas = [];
      this.facturasFiltradas = [];
    } finally {
      this.loadingFacturas = false;
    }
  }

  private mapearDistribuciones(distribucionesRaw: any[]): DistribucionExistente[] {
    if (!Array.isArray(distribucionesRaw)) {
      return [];
    }
    
    return distribucionesRaw.map((distRaw: any) => {
      const distribucion: DistribucionExistente = {
        id: distRaw.id || 0,
        cliente: {
          id: distRaw.cliente?.id || distRaw.cliente_id || 0,
          nombre: distRaw.cliente?.nombre || distRaw.cliente_nombre || '',
          rut: distRaw.cliente?.rut || distRaw.cliente_rut || ''
        },
        fundo: distRaw.fundo ? {
          id: distRaw.fundo.id || distRaw.fundo_id || 0,
          nombre: distRaw.fundo.nombre || distRaw.fundo_nombre || ''
        } : undefined,
        labor: distRaw.labor ? {
          id: distRaw.labor.id || distRaw.labor_id || 0,
          nombre: distRaw.labor.nombre || distRaw.labor_nombre || ''
        } : undefined,
        cuenta: distRaw.cuenta ? {
          id: distRaw.cuenta.id || distRaw.cuenta_id || 0,
          nombre: distRaw.cuenta.nombre || distRaw.cuenta_nombre || '',
          codigo: distRaw.cuenta.codigo || distRaw.cuenta_codigo || ''
        } : undefined,
        monto_distribuido: Number(distRaw.monto_distribuido) || 0,
        porcentaje_distribuido: Number(distRaw.porcentaje_distribuido) || 0,
        tipo_distribucion: distRaw.tipo_distribucion || 'MONTO',
        fecha_distribucion: distRaw.fecha_distribucion || '',
        observaciones: distRaw.observaciones || '',
        usuario_distribuyente: distRaw.usuario_distribuyente ? {
          id: distRaw.usuario_distribuyente.id || 0,
          nombre: distRaw.usuario_distribuyente.nombre || '',
          rut: distRaw.usuario_distribuyente.rut || ''
        } : undefined
      };
      
      return distribucion;
    });
  }

  async cargarDatosDistribucion(): Promise<void> {
    try {
      const response = await firstValueFrom(this.apiService.obtenerDatosDistribucion());
      if (response?.status === 'success') {
        const data = response.data;
        this.clientes = data.clientes || [];
        this.labores = data.labores || [];
        this.cuentas = data.cuentas || [];
        console.log('Datos de distribución cargados:', data);
      }
    } catch (error: any) {
      console.error('Error al cargar datos de distribución:', error);
      this.mostrarError('Error al cargar datos de distribución');
    }
  }

  // ==================== FACTURAS MANUALES ACTUALIZADO ====================

  abrirDialogoFacturaManual(): void {
    this.mostrarDialogoFacturaManual = true;
    this.resetearFormularioManual();
    // Cargar el próximo folio al abrir el diálogo
    this.cargarProximoFolio();
  }

  cerrarDialogoFacturaManual(): void {
    this.mostrarDialogoFacturaManual = false;
    this.facturaManualForm.reset();
  }

  async confirmarCrearFacturaManual(): Promise<void> {
    if (this.facturaManualForm.invalid) {
      this.mostrarError('Por favor complete todos los campos requeridos');
      return;
    }

    this.loadingCrearFactura = true;

    try {
      const formData = this.facturaManualForm.value;
      
      // Formatear fecha de emisión
      const fechaEmision = formData.fecha_emision instanceof Date 
        ? formData.fecha_emision.toISOString().split('T')[0]
        : formData.fecha_emision;
      
      const facturaManual: FacturaManual = {
        tipo_doc: 'BOLETA_MANUAL', // FIJO: Siempre boleta manual
        rut_receptor: formData.rut_receptor,
        razon_social_receptor: formData.razon_social_receptor,
        // folio: se omite - será automático en el backend
        fecha_emision: fechaEmision,
        monto_total: Number(formData.monto_total),
        monto_neto: Number(formData.monto_neto),
        // monto_exento y monto_iva eliminados
        descripcion: formData.descripcion,
        observaciones: formData.observaciones
      };

      const response = await firstValueFrom(this.apiService.post('facturas_venta_automatico/', {
        action: 'create_manual_invoice',
        ...facturaManual
      }));

      if (response?.status === 'success') {
        this.mostrarExito('Boleta de venta creada exitosamente');
        this.cerrarDialogoFacturaManual();
        await this.cargarFacturas();
        await this.cargarProximoFolio(); // Actualizar próximo folio
      } else {
        this.mostrarError(response?.message || 'Error al crear la boleta de venta');
      }
    } catch (error: any) {
      console.error('Error al crear factura manual:', error);
      this.mostrarError('Error al crear boleta de venta: ' + (error.error?.message || error.message));
    } finally {
      this.loadingCrearFactura = false;
    }
  }

  resetearFormularioManual(): void {
    this.facturaManualForm.reset({
      // tipo_doc eliminado - siempre será 'BOLETA_MANUAL'
      fecha_emision: new Date(),
      monto_total: 0,
      monto_neto: 0
      // monto_exento y monto_iva eliminados
    });
  }

  // ACTUALIZADO: Cálculo simplificado sin IVA
  onMontoTotalChange(): void {
    const montoTotal = this.facturaManualForm.get('monto_total')?.value || 0;
    
    // SIMPLIFICADO: Para boletas manuales, total = neto (sin IVA)
    this.facturaManualForm.patchValue({
      monto_neto: montoTotal
    });
  }

  // ELIMINADO: onTipoDocumentoChange() - ya no es necesario

  esFacturaManual(tipoDoc: string): boolean {
    return ['BOLETA_MANUAL', 'FACTURA_MANUAL', 'NOTA_VENTA', 'COMPROBANTE'].includes(tipoDoc);
  }

  // ==================== SELECCIÓN MÚLTIPLE ====================

  toggleSeleccionFactura(factura: FacturaDistribucion): void {
    factura.selected = !factura.selected;
    this.actualizarFacturasSeleccionadas();
  }

  seleccionarTodasVisibles(): void {
    const todasSeleccionadas = this.facturasFiltradas.every(f => f.selected);
    this.facturasFiltradas.forEach(factura => {
      if (!factura.completamente_distribuida) {
        factura.selected = !todasSeleccionadas;
      }
    });
    this.actualizarFacturasSeleccionadas();
  }

  private actualizarFacturasSeleccionadas(): void {
    this.facturasSeleccionadas = this.facturas.filter(f => f.selected);
    
    if (this.facturasSeleccionadas.length > 1) {
      this.prepararDistribucionMultiple();
    } else {
      this.distribucionMultiple = null;
      this.modoDistribucionMultiple = false;
    }
  }

  private prepararDistribucionMultiple(): void {
    const facturas = this.facturasSeleccionadas;
    const montosPendientes = facturas.map(f => f.monto_pendiente);
    const montoMinimo = Math.min(...montosPendientes);
    const montoTotal = montosPendientes.reduce((sum, monto) => sum + monto, 0);

    this.distribucionMultiple = {
      facturas: facturas,
      tipo_distribucion_multiple: 'INDIVIDUAL',
      monto_total_disponible: montoTotal,
      monto_minimo_por_factura: montoMinimo
    };

    this.modoDistribucionMultiple = true;
  }

  limpiarSeleccion(): void {
    this.facturas.forEach(f => f.selected = false);
    this.facturasSeleccionadas = [];
    this.distribucionMultiple = null;
    this.modoDistribucionMultiple = false;
  }

  abrirDialogoDistribucionMultiple(): void {
    if (this.facturasSeleccionadas.length === 0) {
      this.mostrarError('Debe seleccionar al menos una factura');
      return;
    }

    if (this.facturasSeleccionadas.length === 1) {
      // Distribución simple
      this.abrirDialogoDistribucion(this.facturasSeleccionadas[0]);
    } else {
      // Distribución múltiple
      this.facturaSeleccionada = null;
      this.mostrarDialogoDistribucion = true;
      this.resetearFormulario();
      this.configurarFormularioMultiple();
    }
  }

  private configurarFormularioMultiple(): void {
    // Configurar el formulario para distribución múltiple
    this.distribucionForm.patchValue({
      tipo_distribucion_multiple: 'INDIVIDUAL'
    });

    // Configurar validaciones específicas para múltiple
    this.onTipoDistribucionChange();
  }

  // ==================== PERÍODO ====================

  async actualizarPeriodo(): Promise<void> {
    if (this.periodoForm.invalid) {
      this.mostrarError('Por favor seleccione un mes y año válidos');
      return;
    }

    const mes = this.periodoForm.get('mes')?.value;
    const year = this.periodoForm.get('year')?.value;

    if (!this.validarPeriodoSeleccionado(mes, year)) {
      return;
    }

    this.loading = true;
    
    try {
      const configActual = await firstValueFrom(this.apiService.post('facturas_venta_automatico/', {
        action: 'get_automatic_configuration'
      }));
      
      if (configActual?.status === 'success' && configActual.data) {
        const configActualizada = {
          ...configActual.data,
          mes: mes,
          year: year
        };
        
        const response = await firstValueFrom(this.apiService.post('facturas_venta_automatico/', {
          action: 'save_automatic_configuration',
          ...configActualizada
        }));
        
        if (response?.status === 'success') {
          this.mostrarExito(`Período actualizado: ${this.getNombreMes(mes)} ${year}`);
          this.verificarStatusProceso();
          this.mostrarInfoPeriodoPdfs(mes, year);
          this.cargarFacturas();
        } else {
          this.mostrarError(response?.message || 'Error al actualizar período');
        }
      } else {
        this.mostrarError('No se encontró configuración existente. Configure las credenciales primero.');
      }
    } catch (error: any) {
      console.error('Error actualizando período:', error);
      this.mostrarError('Error al actualizar período: ' + (error.error?.message || error.message));
    } finally {
      this.loading = false;
    }
  }

  validarPeriodoSeleccionado(mes: number, year: number): boolean {
    const fechaActual = new Date();
    const fechaPeriodo = new Date(year, mes - 1, 1);
    
    const fechaLimite = new Date(fechaActual);
    fechaLimite.setMonth(fechaLimite.getMonth() + 3);
    
    if (fechaPeriodo > fechaLimite) {
      this.mostrarError(
        `El período ${this.getNombreMes(mes)} ${year} está muy en el futuro. ` +
        `Máximo permitido: ${this.getNombreMes(fechaLimite.getMonth() + 1)} ${fechaLimite.getFullYear()}`
      );
      return false;
    }
    
    const fechaMinima = new Date(2020, 0, 1);
    if (fechaPeriodo < fechaMinima) {
      this.mostrarError('El período no puede ser anterior a enero 2020');
      return false;
    }
    
    return true;
  }

  mostrarInfoPeriodoPdfs(mes: number, year: number): void {
    const fechaInicioPeriodo = new Date(year, mes - 1, 1);
    const fechaInicioPdfs = new Date(fechaInicioPeriodo);
    fechaInicioPdfs.setDate(fechaInicioPdfs.getDate() - 8);
    
    const fechaFinPdfs = new Date(year, mes, 0);
    
    const rangoInfo = `Los PDFs se buscarán desde el ${fechaInicioPdfs.toLocaleDateString('es-CL')} hasta el ${fechaFinPdfs.toLocaleDateString('es-CL')}`;
    
    this.snackBar.open(rangoInfo, 'Entendido', {
      duration: 8000,
      panelClass: ['info-snackbar']
    });
  }

  // ==================== FILTROS ====================

  aplicarFiltros(): void {
    let facturasFiltradas = [...this.facturas];
    
    // Filtro por estado
    if (this.filtroEstado !== 'todos') {
      facturasFiltradas = facturasFiltradas.filter(f => {
        switch (this.filtroEstado) {
          case 'sin_distribuir':
            return f.porcentaje_distribuido === 0;
          case 'parcialmente_distribuidas':
            return f.porcentaje_distribuido > 0 && f.porcentaje_distribuido < 100;
          case 'con_distribucion':
            return f.porcentaje_distribuido > 0;
          default:
            return true;
        }
      });
    }
    
    // Filtro por tipo (SII vs Manual)
    if (this.filtroTipo !== 'todos') {
      facturasFiltradas = facturasFiltradas.filter(f => {
        switch (this.filtroTipo) {
          case 'sii':
            return !f.es_manual;
          case 'manual':
            return f.es_manual;
          default:
            return true;
        }
      });
    }
    
    // Filtro por texto
    if (this.filtroTexto.trim()) {
      const texto = this.filtroTexto.toLowerCase().trim();
      facturasFiltradas = facturasFiltradas.filter(f =>
        f.folio.toLowerCase().includes(texto) ||
        f.razon_social.toLowerCase().includes(texto) ||
        f.rut_receptor.includes(texto) ||
        (f.descripcion && f.descripcion.toLowerCase().includes(texto))
      );
    }
    
    this.facturasFiltradas = facturasFiltradas;
  }

  // ==================== DISTRIBUCIÓN ====================

  abrirDialogoDistribucion(factura?: FacturaDistribucion): void {
    if (factura) {
      // Distribución simple
      this.facturaSeleccionada = factura;
      this.modoDistribucionMultiple = false;
    } else if (this.facturasSeleccionadas.length > 1) {
      // Distribución múltiple
      this.facturaSeleccionada = null;
      this.modoDistribucionMultiple = true;
    } else {
      this.mostrarError('Debe seleccionar al menos una factura');
      return;
    }
    
    this.mostrarDialogoDistribucion = true;
    this.resetearFormulario();
  }

  cerrarDialogoDistribucion(): void {
    this.mostrarDialogoDistribucion = false;
    this.facturaSeleccionada = null;
    this.modoDistribucionMultiple = false;
    this.distribucionForm.reset();
    this.fundos = [];
  }

  async confirmarDistribucion(): Promise<void> {
    if (this.distribucionForm.invalid) {
      this.mostrarError('Por favor complete todos los campos requeridos');
      return;
    }

    this.loadingDistribucion = true;

    try {
      if (this.modoDistribucionMultiple) {
        await this.confirmarDistribucionMultiple();
      } else {
        await this.confirmarDistribucionSimple();
      }
    } catch (error: any) {
      console.error('Error al distribuir:', error);
      this.mostrarError('Error al distribuir: ' + (error.error?.message || error.message));
    } finally {
      this.loadingDistribucion = false;
    }
  }

  private async confirmarDistribucionSimple(): Promise<void> {
    if (!this.facturaSeleccionada) return;

    const formData = {
      action: 'distribute_invoice_multiple',
      factura_id: this.facturaSeleccionada.id,
      ...this.distribucionForm.value
    };

    const response = await firstValueFrom(this.apiService.post('facturas_venta_automatico/', formData));

    if (response?.status === 'success') {
      this.mostrarExito(response.message);
      this.cerrarDialogoDistribucion();
      await this.cargarFacturas();
    } else {
      this.mostrarError(response?.message || 'Error al distribuir factura');
    }
  }

  private async confirmarDistribucionMultiple(): Promise<void> {
    const tipoMultiple = this.distribucionForm.get('tipo_distribucion_multiple')?.value;
    const formData = this.distribucionForm.value;

    let distribucionesExitosas = 0;
    const errores: string[] = [];

    for (const factura of this.facturasSeleccionadas) {
      try {
        let montoParaEstaFactura = 0;
        let porcentajeParaEstaFactura = 0;

        if (tipoMultiple === 'INDIVIDUAL') {
          // Cada factura recibe el monto/porcentaje especificado
          if (formData.tipo_distribucion === 'MONTO') {
            montoParaEstaFactura = Math.min(formData.monto_a_distribuir, factura.monto_pendiente);
          } else {
            porcentajeParaEstaFactura = Math.min(formData.porcentaje_a_distribuir, factura.porcentaje_pendiente);
          }
        } else {
          // Distribución grupal proporcional
          const proporcion = factura.monto_pendiente / this.distribucionMultiple!.monto_total_disponible;
          if (formData.tipo_distribucion === 'MONTO') {
            montoParaEstaFactura = formData.monto_a_distribuir * proporcion;
          } else {
            porcentajeParaEstaFactura = formData.porcentaje_a_distribuir * proporcion;
          }
        }

        const dataFactura = {
          action: 'distribute_invoice_multiple',
          factura_id: factura.id,
          tipo_distribucion: formData.tipo_distribucion,
          monto_a_distribuir: montoParaEstaFactura || null,
          porcentaje_a_distribuir: porcentajeParaEstaFactura || null,
          cliente_id: formData.cliente_id,
          fundo_id: formData.fundo_id,
          labor_id: formData.labor_id,
          cuenta_id: formData.cuenta_id,
          observaciones: `${formData.observaciones} (Distribución múltiple)`
        };

        const response = await firstValueFrom(this.apiService.post('facturas_venta_automatico/', dataFactura));

        if (response?.status === 'success') {
          distribucionesExitosas++;
        } else {
          errores.push(`Factura ${factura.folio}: ${response?.message || 'Error desconocido'}`);
        }
      } catch (error: any) {
        errores.push(`Factura ${factura.folio}: ${error.message || 'Error de comunicación'}`);
      }
    }

    // Mostrar resultados
    if (distribucionesExitosas > 0) {
      this.mostrarExito(`Se distribuyeron ${distribucionesExitosas} de ${this.facturasSeleccionadas.length} facturas exitosamente`);
    }

    if (errores.length > 0) {
      console.error('Errores en distribución múltiple:', errores);
      this.mostrarError(`${errores.length} facturas tuvieron errores. Ver consola para detalles.`);
    }

    this.cerrarDialogoDistribucion();
    this.limpiarSeleccion();
    await this.cargarFacturas();
  }

  // ==================== VER DISTRIBUCIONES ====================

  verDistribuciones(factura: FacturaDistribucion): void {
    this.facturaSeleccionada = factura;
    this.mostrarDialogoDistribuciones = true;
  }

  cerrarDialogoDistribuciones(): void {
    this.mostrarDialogoDistribuciones = false;
    this.facturaSeleccionada = null;
  }

  async eliminarDistribucion(distribucion: DistribucionExistente): Promise<void> {
    if (!confirm('¿Está seguro de eliminar esta distribución?')) {
      return;
    }
    
    try {
      const response = await firstValueFrom(this.apiService.post('facturas_venta_automatico/', {
        action: 'delete_distribution',
        distribucion_id: distribucion.id
      }));
      
      if (response?.status === 'success') {
        this.mostrarExito('Distribución eliminada exitosamente');
        await this.cargarFacturas();
        
        // Actualizar factura seleccionada
        if (this.facturaSeleccionada) {
          const facturaActualizada = this.facturas.find(f => f.id === this.facturaSeleccionada!.id);
          if (facturaActualizada) {
            this.facturaSeleccionada = facturaActualizada;
          }
        }
      } else {
        this.mostrarError(response?.message || 'Error al eliminar distribución');
      }
    } catch (error: any) {
      console.error('Error al eliminar distribución:', error);
      this.mostrarError('Error al eliminar distribución: ' + (error.error?.message || error.message));
    }
  }

  // ==================== EVENTOS DEL FORMULARIO ====================

  onTipoDistribucionChange(): void {
    this.distribucionForm.patchValue({
      monto_a_distribuir: null,
      porcentaje_a_distribuir: null
    });
    
    const tipo = this.distribucionForm.get('tipo_distribucion')?.value;
    const montoControl = this.distribucionForm.get('monto_a_distribuir');
    const porcentajeControl = this.distribucionForm.get('porcentaje_a_distribuir');
    
    if (tipo === 'MONTO') {
      montoControl?.setValidators([Validators.required, Validators.min(0.01)]);
      porcentajeControl?.clearValidators();
      
      if (this.modoDistribucionMultiple && this.distribucionMultiple) {
        montoControl?.setValidators([
          Validators.required, 
          Validators.min(0.01),
          Validators.max(this.distribucionMultiple.monto_minimo_por_factura)
        ]);
      } else if (this.facturaSeleccionada) {
        montoControl?.setValidators([
          Validators.required, 
          Validators.min(0.01),
          Validators.max(this.facturaSeleccionada.monto_pendiente)
        ]);
      }
    } else {
      porcentajeControl?.setValidators([Validators.required, Validators.min(0.01), Validators.max(100)]);
      montoControl?.clearValidators();
    }
    
    montoControl?.updateValueAndValidity();
    porcentajeControl?.updateValueAndValidity();
  }

  async onClienteSeleccionado(): Promise<void> {
    const clienteId = this.distribucionForm.get('cliente_id')?.value;
    if (clienteId) {
      this.loadingFundos = true;
      try {
        const response = await firstValueFrom(this.apiService.get(`api_campos_clientes/${clienteId}/`));
        this.fundos = response || [];
      } catch (error) {
        console.error('Error cargando fundos:', error);
        this.fundos = [];
      } finally {
        this.loadingFundos = false;
      }
    } else {
      this.fundos = [];
    }
    
    this.distribucionForm.patchValue({ fundo_id: null });
  }

  // ==================== UTILIDADES DEL FORMULARIO ====================

  distribuirResto(): void {
    if (this.modoDistribucionMultiple && this.distribucionMultiple) {
      const tipo = this.distribucionForm.get('tipo_distribucion')?.value;
      if (tipo === 'MONTO') {
        this.distribucionForm.patchValue({
          monto_a_distribuir: this.distribucionMultiple.monto_minimo_por_factura
        });
      } else {
        this.distribucionForm.patchValue({
          porcentaje_a_distribuir: 100
        });
      }
    } else if (this.facturaSeleccionada) {
      const tipo = this.distribucionForm.get('tipo_distribucion')?.value;
      if (tipo === 'MONTO') {
        this.distribucionForm.patchValue({
          monto_a_distribuir: this.facturaSeleccionada.monto_pendiente
        });
      } else {
        this.distribucionForm.patchValue({
          porcentaje_a_distribuir: this.facturaSeleccionada.porcentaje_pendiente
        });
      }
    }
  }

  distribuirMitad(): void {
    if (this.modoDistribucionMultiple && this.distribucionMultiple) {
      const tipo = this.distribucionForm.get('tipo_distribucion')?.value;
      if (tipo === 'MONTO') {
        this.distribucionForm.patchValue({
          monto_a_distribuir: this.distribucionMultiple.monto_minimo_por_factura / 2
        });
      } else {
        this.distribucionForm.patchValue({
          porcentaje_a_distribuir: 50
        });
      }
    } else if (this.facturaSeleccionada) {
      const tipo = this.distribucionForm.get('tipo_distribucion')?.value;
      if (tipo === 'MONTO') {
        this.distribucionForm.patchValue({
          monto_a_distribuir: this.facturaSeleccionada.monto_pendiente / 2
        });
      } else {
        this.distribucionForm.patchValue({
          porcentaje_a_distribuir: Math.min(50, this.facturaSeleccionada.porcentaje_pendiente)
        });
      }
    }
  }

  resetearFormulario(): void {
    this.distribucionForm.reset({
      tipo_distribucion: 'MONTO',
      tipo_distribucion_multiple: 'INDIVIDUAL'
    });
    this.onTipoDistribucionChange();
  }

  // ==================== PDFs ====================

  async cargarEstadisticasPdf(): Promise<void> {
    try {
      const response = await firstValueFrom(this.apiService.post('facturas_venta_automatico/', {
        action: 'get_pdf_search_status'
      }));
      
      if (response?.status === 'success') {
        this.estadisticasPdf = response.estadisticas_pdf;
        console.log('Estadísticas PDF actualizadas:', this.estadisticasPdf);
      }
    } catch (error: any) {
      console.error('Error cargando estadísticas PDF:', error);
    }
  }

  async buscarPdfsFacturasExistentes(): Promise<void> {
    if (this.loadingPdfSearch) return;
    
    this.loadingPdfSearch = true;
    
    try {
      const response = await firstValueFrom(this.apiService.post('facturas_venta_automatico/', {
        action: 'search_pdfs_for_existing_invoices'
      }));
      
      if (response?.status === 'success') {
        this.mostrarExito(response.message);
        
        if (response.facturas_sin_pdf > 0) {
          this.snackBar.open(
            `Búsqueda iniciada para ${response.facturas_sin_pdf} facturas. El proceso continuará en segundo plano.`, 
            'Entendido', 
            { duration: 8000, panelClass: ['info-snackbar'] }
          );
        }
        
        this.iniciarActualizacionAutomaticaPdfs();
      } else {
        this.mostrarError(response?.message || 'Error al iniciar búsqueda de PDFs');
      }
    } catch (error: any) {
      console.error('Error buscando PDFs:', error);
      this.mostrarError('Error al buscar PDFs: ' + (error.error?.message || error.message));
    } finally {
      this.loadingPdfSearch = false;
    }
  }

  private iniciarActualizacionAutomaticaPdfs(): void {
    let contador = 0;
    const maxActualizaciones = 10;
    
    const interval = setInterval(() => {
      contador++;
      this.cargarEstadisticasPdf();
      this.cargarFacturas();
      
      if (contador >= maxActualizaciones) {
        clearInterval(interval);
        console.log('Finalizadas actualizaciones automáticas de PDFs');
      }
    }, 30000);
  }

  async visualizarPdfFactura(factura: FacturaDistribucion): Promise<void> {
    if (!factura.pdf_disponible) {
      this.snackBar.open('Esta factura no tiene PDF disponible', 'Cerrar', {
        duration: 3000,
        panelClass: ['warning-snackbar']
      });
      return;
    }

    try {
      const loadingRef = this.snackBar.open('Cargando PDF...', '', {
        duration: 0,
        panelClass: ['info-snackbar']
      });

      const pdfBlob = await firstValueFrom(this.apiService.getPDF(`facturas_venta_sii_pdf/${factura.id}/`));
      
      loadingRef.dismiss();
      
      const pdfUrl = window.URL.createObjectURL(pdfBlob!);
      
      const ventanaPdf = window.open(
        pdfUrl, 
        '_blank',
        'width=1000,height=800,scrollbars=yes,resizable=yes,toolbar=yes,menubar=yes'
      );
      
      if (!ventanaPdf) {
        const link = document.createElement('a');
        link.href = pdfUrl;
        link.target = '_blank';
        link.style.display = 'none';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        this.snackBar.open('PDF abierto en nueva pestaña', 'Cerrar', {
          duration: 3000,
          panelClass: ['success-snackbar']
        });
      } else {
        ventanaPdf.focus();
        
        setTimeout(() => {
          window.URL.revokeObjectURL(pdfUrl);
        }, 10000);
      }
      
    } catch (error: any) {
      console.error('Error abriendo PDF:', error);
      this.mostrarError('Error al abrir PDF: ' + (error.error?.message || error.message));
    }
  }

  // ==================== PROCESO AUTOMÁTICO ====================

  iniciarMonitoreoStatus(): void {
    this.statusSubscription = interval(30000).subscribe(() => {
      this.verificarStatusProceso();
    });
    
    this.verificarStatusProceso();
  }

  async verificarStatusProceso(): Promise<void> {
    try {
      const response = await firstValueFrom(this.apiService.post('facturas_venta_automatico/', {
        action: 'get_automatic_process_status'
      }));
      
      if (response?.status_data) {
        this.procesoStatus = response.status_data;
      }
    } catch (error: any) {
      console.error('Error verificando status del proceso:', error);
    }
  }

  async ejecutarProcesoManual(): Promise<void> {
    if (!this.configuracionValida) {
      this.mostrarError('Debe configurar las credenciales y el período primero');
      return;
    }

    this.loading = true;
    
    try {
      const response = await firstValueFrom(this.apiService.post('facturas_venta_automatico/', {
        action: 'execute_automatic_process_manual'
      }));
      
      if (response?.status === 'success') {
        const periodo = this.periodoConfigurado;
        this.mostrarExito(`Proceso ejecutado exitosamente para ${periodo}`);
        this.cargarFacturas();
        this.verificarStatusProceso();
      } else {
        this.mostrarError(response?.message || 'Error al ejecutar el proceso');
      }
    } catch (error: any) {
      console.error('Error ejecutando proceso manual:', error);
      
      if (error.status === 400 && error.error?.message) {
        this.mostrarError(error.error.message);
      } else if (error.status === 404) {
        this.mostrarError('No se encontró configuración. Por favor, configure las credenciales y período primero.');
      } else {
        this.mostrarError('Error al ejecutar el proceso manual: ' + (error.error?.message || error.message));
      }
    } finally {
      this.loading = false;
    }
  }

  // ==================== GETTERS ====================

  get periodoConfigurado(): string {
    return this.procesoStatus.periodo_configurado || this.getPeriodoTextoFormulario();
  }

  get configuracionValida(): boolean {
    return this.configuracionCargada && this.configuracionActiva;
  }

  get configuracionActiva(): boolean {
    return this.procesoStatus.configuracion_activa === true;
  }

  get hayFacturasPorDistribuir(): boolean {
    return this.facturas.length > 0;
  }

  get facturasSinDistribuir(): number {
    return this.facturas.filter(f => f.porcentaje_distribuido === 0).length;
  }

  get facturasParcialmenteDistribuidas(): number {
    return this.facturas.filter(f => f.porcentaje_distribuido > 0 && f.porcentaje_distribuido < 100).length;
  }

  get facturasConDistribucion(): number {
    return this.facturas.filter(f => f.porcentaje_distribuido > 0).length;
  }

  get facturasConPdf(): number {
    return this.facturas.filter(f => f.pdf_disponible).length;
  }

  get facturasSinPdf(): number {
    return this.facturas.filter(f => !f.pdf_disponible).length;
  }

  get facturasManuales(): number {
    return this.facturas.filter(f => f.es_manual).length;
  }

  get facturasSII(): number {
    return this.facturas.filter(f => !f.es_manual).length;
  }

  get porcentajeConPdf(): number {
    if (this.facturas.length === 0) return 0;
    return Math.round((this.facturasConPdf / this.facturas.length) * 100);
  }

  get algunaFacturaSeleccionada(): boolean {
    return this.facturasSeleccionadas.length > 0;
  }

  get todasLasVisiblesSeleccionadas(): boolean {
    const facturasPuedenSeleccionarse = this.facturasFiltradas.filter(f => !f.completamente_distribuida);
    return facturasPuedenSeleccionarse.length > 0 && 
           facturasPuedenSeleccionarse.every(f => f.selected);
  }

  get algunaVisibleSeleccionada(): boolean {
    return this.facturasFiltradas.some(f => f.selected);
  }

  getPeriodoTextoFormulario(): string {
    const mes = this.periodoForm.get('mes')?.value;
    const year = this.periodoForm.get('year')?.value;
    
    if (mes && year) {
      return `${this.getNombreMes(mes)} ${year}`;
    }
    
    return 'Período no seleccionado';
  }

  getNombreMes(mes: number): string {
    const mesOption = this.mesesOptions.find(m => m.value === mes);
    return mesOption ? mesOption.label : mes.toString();
  }

  getValorDistribucion(): number {
    const tipo = this.distribucionForm.get('tipo_distribucion')?.value;
    
    if (this.modoDistribucionMultiple && this.distribucionMultiple) {
      if (tipo === 'MONTO') {
        const montoIndividual = this.distribucionForm.get('monto_a_distribuir')?.value || 0;
        return montoIndividual * this.facturasSeleccionadas.length;
      } else {
        const porcentaje = this.distribucionForm.get('porcentaje_a_distribuir')?.value || 0;
        return this.distribucionMultiple.monto_total_disponible * (porcentaje / 100);
      }
    } else if (this.facturaSeleccionada) {
      if (tipo === 'MONTO') {
        return this.distribucionForm.get('monto_a_distribuir')?.value || 0;
      } else {
        const porcentaje = this.distribucionForm.get('porcentaje_a_distribuir')?.value || 0;
        return (porcentaje / 100) * this.facturaSeleccionada.monto_total;
      }
    }
    
    return 0;
  }

  getPorcentajeDistribucion(): number {
    const tipo = this.distribucionForm.get('tipo_distribucion')?.value;
    
    if (tipo === 'PORCENTAJE') {
      return this.distribucionForm.get('porcentaje_a_distribuir')?.value || 0;
    } else {
      const monto = this.distribucionForm.get('monto_a_distribuir')?.value || 0;
      if (this.modoDistribucionMultiple && this.distribucionMultiple) {
        return this.distribucionMultiple.monto_total_disponible > 0 ? 
          (monto / this.distribucionMultiple.monto_total_disponible) * 100 : 0;
      } else if (this.facturaSeleccionada) {
        return this.facturaSeleccionada.monto_total > 0 ? 
          (monto / this.facturaSeleccionada.monto_total) * 100 : 0;
      }
    }
    
    return 0;
  }

  getNombreCliente(clienteId: number): string {
    const cliente = this.clientes.find(c => c.id === clienteId);
    return cliente ? cliente.nombre : '';
  }

  getIconoPdf(factura: FacturaDistribucion): string {
    if (factura.es_manual) {
      return 'description'; // Icono para facturas manuales
    } else if (factura.pdf_disponible) {
      return 'picture_as_pdf';
    } else if (factura.error_descarga_pdf) {
      return 'error';
    } else {
      return 'cloud_download';
    }
  }

  getColorIconoPdf(factura: FacturaDistribucion): string {
    if (factura.es_manual) {
      return 'accent'; // Color diferente para facturas manuales
    } else if (factura.pdf_disponible) {
      return 'primary';
    } else if (factura.error_descarga_pdf) {
      return 'warn';
    } else {
      return 'disabled';
    }
  }

  getTooltipPdf(factura: FacturaDistribucion): string {
    if (factura.es_manual) {
      return 'Boleta manual - No requiere PDF del SII';
    } else if (factura.pdf_disponible) {
      const fechaDescarga = factura.fecha_descarga_pdf 
        ? this.formatearFechaHora(factura.fecha_descarga_pdf)
        : '';
      return `PDF disponible${fechaDescarga ? ` - Descargado: ${fechaDescarga}` : ''}`;
    } else if (factura.error_descarga_pdf) {
      return `Error descargando PDF: ${factura.error_descarga_pdf}`;
    } else {
      return 'PDF no disponible - Será descargado automáticamente';
    }
  }

  getEstadoProcesoBadge(): string {
    switch (this.procesoStatus.estado) {
      case 'ejecutando': return 'warn';
      case 'completado': return 'primary';
      case 'error': return 'accent';
      default: return '';
    }
  }

  getEstadoProcesoTexto(): string {
    switch (this.procesoStatus.estado) {
      case 'inactivo': return 'Inactivo';
      case 'ejecutando': return 'Ejecutando...';
      case 'completado': return 'Completado';
      case 'error': return 'Error';
      default: return 'Desconocido';
    }
  }

  // ACTUALIZADO: Eliminar función getTipoDocumentoLabel ya que solo habrá boletas manuales

  // ==================== UTILIDADES ====================

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
      const date = new Date(fecha + 'T00:00:00');
      return date.toLocaleDateString('es-CL');
    } catch {
      return fecha;
    }
  }

  formatearFechaHora(fechaHora: string): string {
    if (!fechaHora) return '';
    
    try {
      const date = new Date(fechaHora);
      return date.toLocaleString('es-CL', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        hour12: false
      });
    } catch {
      return fechaHora;
    }
  }

  private mostrarError(mensaje: string): void {
    this.error = mensaje;
    this.snackBar.open(mensaje, 'Cerrar', {
      duration: 5000,
      panelClass: ['error-snackbar']
    });
    
    setTimeout(() => {
      this.error = null;
    }, 5000);
  }

  private mostrarExito(mensaje: string): void {
    this.success = mensaje;
    this.snackBar.open(mensaje, 'Cerrar', {
      duration: 3000,
      panelClass: ['success-snackbar']
    });
    
    setTimeout(() => {
      this.success = null;
    }, 3000);
  }
}