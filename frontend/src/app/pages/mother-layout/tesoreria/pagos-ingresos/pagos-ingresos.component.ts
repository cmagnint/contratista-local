// pagos-ingresos.component.ts - VERSIÓN FLEXIBLE PARA DISTRIBUCIÓN MÚLTIPLE
import { Component, OnInit, Inject, PLATFORM_ID } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ContratistaApiService } from '../../../../services/contratista-api.service';

interface Banco {
  codigo_sbif: string;
  nombre: string;
}

interface CuentaOrigen {
  id: number;
  numero_cuenta: string;
  tipo_cuenta: string;
  banco_info: {
    id: number;
    nombre: string;
    codigo_sbif: string;
  };
}

interface MovimientoConSaldo {
  id: number;
  fecha: string;
  numero_operacion: string;
  descripcion: string;
  monto_original: number;
  monto_distribuido: number;
  saldo_disponible: number;
  porcentaje_usado: number;
  completamente_usado: boolean;
  saldo: number;
}

interface FacturaVenta {
  id: number;
  numero: string;
  fecha_emision: string;
  neto: number;
  iva: number;
  total: number;
  estado: string;
  saldo_pendiente: number;
}

interface EstadoFactura {
  factura: {
    id: number;
    folio: string;
    fecha_emision: string;
    cliente_nombre: string;
    monto_total: number;
    monto_neto: number;
    monto_iva: number;
  };
  cobertura: {
    neto_cubierto: number;
    iva_cubierto: number;
    total_cubierto: number;
    neto_pendiente: number;
    iva_pendiente: number;
    total_pendiente: number;
    porcentaje_cubierto: number;
    completamente_pagada: boolean;
  };
  historial_pagos: Array<{
    fecha: string;
    monto_distribuido: number;
    monto_neto_cubierto: number;
    monto_iva_cubierto: number;
  }>;
}

interface DistribucionPendiente {
  movimiento: MovimientoConSaldo;
  factura: FacturaVenta;
  monto_a_distribuir: number;
  porcentaje_neto: number;
  porcentaje_iva: number;
  monto_neto: number;
  monto_iva: number;
}

@Component({
  selector: 'app-pagos-ingresos',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule],
  templateUrl: './pagos-ingresos.component.html',
  styleUrl: './pagos-ingresos.component.css'
})
export class PagosIngresosComponent implements OnInit {
  
  // Formularios reactivos
  seleccionForm: FormGroup;
  distribucionForm: FormGroup;
  
  // Estados del proceso
  pasoActual = 1;
  cargando = false;
  error = '';
  exito = '';
  
  // Datos para selects
  bancos: Banco[] = [];
  cuentasOrigen: CuentaOrigen[] = [];
  movimientosConSaldo: MovimientoConSaldo[] = [];
  facturasDisponibles: FacturaVenta[] = [];
  
  // Archivo PDF seleccionado
  archivoPdfSeleccionado: File | null = null;
  
  // Datos seleccionados
  bancoSeleccionado: Banco | null = null;
  cuentaSeleccionada: CuentaOrigen | null = null;
  movimientoSeleccionado: MovimientoConSaldo | null = null;
  facturaSeleccionada: FacturaVenta | null = null;
  
  // Información extraída de la cartola
  fechaCartola: string | null = null;
  periodoCartola: { inicio: string; fin: string } | null = null;
  
  // NUEVOS CAMPOS PARA DISTRIBUCIÓN FLEXIBLE
  estadoFacturaActual: EstadoFactura | null = null;
  distribucionesPendientes: DistribucionPendiente[] = [];
  modoDistribucionMultiple = false;
  
  // Debug y monitoreo
  ultimaRespuestaProcesamiento: any = null;
  filtrosAplicados: any = null;
  
  constructor(
    private apiService: ContratistaApiService,
    private fb: FormBuilder,
    @Inject(PLATFORM_ID) private platformId: Object,
  ) {
    // Inicializar formularios
    this.seleccionForm = this.fb.group({
      banco: ['', Validators.required]
    });
    
    this.distribucionForm = this.fb.group({
      movimiento: ['', Validators.required],
      factura: ['', Validators.required],
      montoDistribuir: ['', [Validators.required, Validators.min(0)]],
      montoNeto: ['0', [Validators.required, Validators.min(0)]],
      montoIva: ['0', [Validators.required, Validators.min(0)]]
    });
  }

  ngOnInit(): void {
    if(isPlatformBrowser(this.platformId)){
      this.cargarDatosIniciales();
    }
  }
  
  // ============================================================================
  // MÉTODOS PARA CARGAR DATOS INICIALES
  // ============================================================================
  
  async cargarDatosIniciales(): Promise<void> {
    this.cargando = true;
    try {
      console.log('=== INICIANDO CARGA DE DATOS ===');
      await this.cargarBancos();
      console.log('=== CARGA COMPLETADA ===');
    } catch (error) {
      console.error('Error en carga inicial:', error);
      this.mostrarError('Error cargando datos iniciales');
    } finally {
      this.cargando = false;
    }
  }
  
  async cargarBancos(): Promise<void> {
    try {
      const response = await this.apiService.get('api_bancos/').toPromise();
      this.bancos = response || [];
      console.log(`✅ Cargados ${this.bancos.length} bancos`);
    } catch (error) {
      console.error('Error cargando bancos:', error);
      throw new Error('Error cargando bancos');
    }
  }
  
  // ============================================================================
  // MÉTODOS DE NAVEGACIÓN ENTRE PASOS
  // ============================================================================
  
  async siguientePaso(): Promise<void> {
    if (this.pasoActual === 1) {
      if (this.bancoSeleccionado && this.seleccionForm.valid) {
        await this.cargarCuentasOrigen();
        this.pasoActual = 2;
      } else {
        this.mostrarError('Por favor seleccione un banco');
      }
    } else if (this.pasoActual === 2) {
      if (this.archivoPdfSeleccionado && this.cuentaSeleccionada) {
        await this.procesarCartolaPDF();
        this.pasoActual = 3;
      } else {
        this.mostrarError('Por favor seleccione una cuenta y suba el archivo PDF');
      }
    } else if (this.pasoActual === 3) {
      // En el nuevo flujo, pasamos al paso 4 sin seleccionar UN movimiento específico
      if (this.movimientosConSaldo.length > 0) {
        await this.cargarFacturasDisponibles();
        this.pasoActual = 4;
      } else {
        this.mostrarError('No hay movimientos disponibles para distribuir');
      }
    } else if (this.pasoActual === 4) {
      // Procesar distribución actual
      await this.procesarDistribucionActual();
    }
  }
  
  pasoAnterior(): void {
    if (this.pasoActual > 1) {
      this.pasoActual--;
      this.limpiarError();
    }
  }
  
  // ============================================================================
  // MÉTODOS PARA MANEJAR SELECCIONES
  // ============================================================================
  
  onBancoSeleccionado(event: Event): void {
    const target = event.target as HTMLSelectElement;
    const codigoSbif = target.value;
    
    this.bancoSeleccionado = this.bancos.find(b => b.codigo_sbif === codigoSbif) || null;
    this.seleccionForm.patchValue({ banco: codigoSbif });
    
    // Limpiar selecciones posteriores
    this.cuentaSeleccionada = null;
    this.cuentasOrigen = [];
  }
  
  onCuentaSeleccionada(event: Event): void {
    const target = event.target as HTMLSelectElement;
    const cuentaId = parseInt(target.value);
    this.cuentaSeleccionada = this.cuentasOrigen.find(c => c.id === cuentaId) || null;
    
    // Limpiar selecciones posteriores
    this.archivoPdfSeleccionado = null;
    this.movimientosConSaldo = [];
  }
  
  onMovimientoSeleccionado(movimiento: MovimientoConSaldo): void {
    this.movimientoSeleccionado = movimiento;
    
    // Resetear los montos de distribución
    this.distribucionForm.patchValue({
      movimiento: movimiento.id,
      montoNeto: '0',
      montoIva: '0',
      montoDistribuir: '0'
    });
    
    console.log('💰 Movimiento seleccionado:', movimiento);
    console.log('💰 Saldo disponible:', movimiento.saldo_disponible);
  }
  
  onFacturaSeleccionada(event: Event): void {
    const target = event.target as HTMLSelectElement;
    const facturaId = parseInt(target.value);
    this.facturaSeleccionada = this.facturasDisponibles.find(f => f.id === facturaId) || null;
    
    if (this.facturaSeleccionada) {
      // Cargar estado detallado de la factura
      this.cargarEstadoFactura(this.facturaSeleccionada.id);
      
      this.distribucionForm.patchValue({
        factura: facturaId,
        montoNeto: '0',
        montoIva: '0'
      });
      
      // No validar automáticamente, dejar que el usuario ingrese los montos manualmente
      setTimeout(() => this.validarMontosDistribucion(), 100);
    }
  }
  
  // ============================================================================
  // MÉTODOS PARA MANEJO DE ARCHIVOS
  // ============================================================================
  
  onArchivoSeleccionado(event: Event): void {
    const target = event.target as HTMLInputElement;
    const files = target.files;
    
    if (files && files.length > 0) {
      const archivo = files[0];
      
      if (archivo.type !== 'application/pdf') {
        this.mostrarError('Por favor seleccione un archivo PDF válido');
        return;
      }
      
      if (archivo.size > 10 * 1024 * 1024) {
        this.mostrarError('El archivo es demasiado grande (máximo 10MB)');
        return;
      }
      
      this.archivoPdfSeleccionado = archivo;
      this.limpiarError();
    }
  }
  
  // ============================================================================
  // MÉTODOS DE API - VERSIÓN FLEXIBLE
  // ============================================================================
  
  async cargarCuentasOrigen(): Promise<void> {
    if (!this.bancoSeleccionado) return;
    
    this.cargando = true;
    try {
      const response = await this.apiService.get(`tesoreria/cuentas-origen/banco/${this.bancoSeleccionado.codigo_sbif}/`).toPromise();
      this.cuentasOrigen = response?.cuentas || [];
      
      if (this.cuentasOrigen.length === 0) {
        this.mostrarError('No se encontraron cuentas origen para este banco');
      }
    } catch (error) {
      this.mostrarError('Error cargando cuentas origen');
    } finally {
      this.cargando = false;
    }
  }
  
  async procesarCartolaPDF(): Promise<void> {
    if (!this.archivoPdfSeleccionado || !this.cuentaSeleccionada) return;
    
    this.cargando = true;
    try {
      const formData = new FormData();
      formData.append('cartola_pdf', this.archivoPdfSeleccionado);
      formData.append('cuenta_origen_id', this.cuentaSeleccionada.id.toString());
      
      const response = await this.apiService.postFormData('tesoreria/procesar-cartola/', formData).toPromise();
      
      this.ultimaRespuestaProcesamiento = response;
      
      if (response.fecha_cartola) {
        this.fechaCartola = response.fecha_cartola;
      }
      if (response.periodo_cartola) {
        this.periodoCartola = response.periodo_cartola;
      }
      
      // Cargar movimientos con saldos
      await this.cargarMovimientosConSaldo();
      
      this.mostrarExito(`Cartola procesada exitosamente. Total ingresos: ${response.total_ingresos_detectados}`);
      
    } catch (error) {
      this.mostrarError('Error procesando la cartola PDF');
    } finally {
      this.cargando = false;
    }
  }
  
  async cargarMovimientosConSaldo(): Promise<void> {
    if (!this.cuentaSeleccionada || !this.periodoCartola) return;
    
    try {
      const params = {
        cuenta_origen_id: this.cuentaSeleccionada.id.toString(),
        fecha_inicio: this.periodoCartola.inicio,
        fecha_fin: this.periodoCartola.fin
      };
      
      const queryString = new URLSearchParams(params).toString();
      const response = await this.apiService.get(`tesoreria/movimientos-saldos/?${queryString}`).toPromise();
      
      this.movimientosConSaldo = response?.movimientos || [];
      
      console.log(`✅ Movimientos con saldo cargados: ${this.movimientosConSaldo.length}`);
      
      // ORDENAR POR FECHA (más reciente primero), luego por monto
      this.movimientosConSaldo.sort((a, b) => {
        const fechaA = new Date(a.fecha).getTime();
        const fechaB = new Date(b.fecha).getTime();
        if (fechaA !== fechaB) {
          return fechaB - fechaA; // Más reciente primero
        }
        return b.monto_original - a.monto_original; // Si misma fecha, mayor monto primero
      });
      
      // Filtrar solo los que tienen saldo disponible
      this.movimientosConSaldo = this.movimientosConSaldo.filter(mov => mov.saldo_disponible > 0);
      
      if (this.movimientosConSaldo.length === 0) {
        this.mostrarError('No hay movimientos con saldo disponible para distribuir');
      }
      
    } catch (error) {
      this.mostrarError('Error cargando movimientos con saldo');
    }
  }
  
  async cargarFacturasDisponibles(): Promise<void> {
    if (!this.periodoCartola) return;
    
    this.cargando = true;
    try {
      const params = {
        fecha_inicio: this.periodoCartola.inicio,
        fecha_fin: this.periodoCartola.fin
      };
      
      const queryString = new URLSearchParams(params).toString();
      const response = await this.apiService.get(`tesoreria/facturas-distribuidas/?${queryString}`).toPromise();
      this.facturasDisponibles = response?.facturas || [];
      
      if (this.facturasDisponibles.length === 0) {
        this.mostrarError(`No se encontraron facturas distribuidas en el período`);
      }
      
    } catch (error) {
      this.mostrarError('Error cargando facturas disponibles');
    } finally {
      this.cargando = false;
    }
  }
  
  async cargarEstadoFactura(facturaId: number): Promise<void> {
    try {
      this.estadoFacturaActual = await this.apiService.get(`tesoreria/factura-estado/${facturaId}/`).toPromise();
    } catch (error) {
      console.error('Error cargando estado de factura:', error);
    }
  }
  
  async procesarDistribucionActual(): Promise<void> {
    if (!this.movimientoSeleccionado || !this.facturaSeleccionada) return;
    
    if (!this.distribucionForm.valid) {
      this.mostrarError('Por favor complete correctamente todos los campos');
      return;
    }
    
    const montos = this.calcularMontos();
    
    if (montos.total <= 0) {
      this.mostrarError('Debe especificar al menos un monto para neto o IVA');
      return;
    }
    
    this.cargando = true;
    try {
      const datos = {
        movimiento_id: this.movimientoSeleccionado.id,
        factura_id: this.facturaSeleccionada.id,
        monto_distribuido: montos.total,
        // Calcular porcentajes dinámicamente para el backend
        porcentaje_neto: montos.total > 0 ? (montos.neto / montos.total) * 100 : 0,
        porcentaje_iva: montos.total > 0 ? (montos.iva / montos.total) * 100 : 0
      };
      
      console.log('📊 Enviando distribución:', {
        movimiento: this.movimientoSeleccionado.numero_operacion,
        factura: this.facturaSeleccionada.numero,
        monto_neto: montos.neto,
        monto_iva: montos.iva,
        total: montos.total
      });
      
      const response = await this.apiService.post('tesoreria/registrar-ingreso/', datos).toPromise();
      
      this.mostrarExito(`Distribución registrada: ${this.formatearMonto(montos.neto)} al neto, ${this.formatearMonto(montos.iva)} al IVA`);
      
      // Recargar datos para mostrar nuevos saldos
      await this.cargarMovimientosConSaldo();
      if (this.facturaSeleccionada) {
        await this.cargarEstadoFactura(this.facturaSeleccionada.id);
      }
      
      // Activar modo distribución múltiple
      this.modoDistribucionMultiple = true;
      
    } catch (error: any) {
      console.error('Error:', error);
      const errorMsg = error?.error?.error || 'Error registrando la distribución';
      this.mostrarError(errorMsg);
    } finally {
      this.cargando = false;
    }
  }
  
  // ============================================================================
  // MÉTODOS PARA DISTRIBUCIÓN MÚLTIPLE
  // ============================================================================
  
  agregarOtraDistribucion(): void {
    // Limpiar selecciones para permitir nueva distribución
    this.movimientoSeleccionado = null;
    this.facturaSeleccionada = null;
    this.estadoFacturaActual = null;
    
    this.distribucionForm.reset({
      montoNeto: '0',
      montoIva: '0',
      montoDistribuir: '0'
    });
    
    this.limpiarError();
  }
  
  finalizarDistribuciones(): void {
    this.resetearFormulario();
  }
  
  // ============================================================================
  // MÉTODOS DE VALIDACIÓN
  // ============================================================================
  
  // ============================================================================
  // MÉTODOS DE VALIDACIÓN - VERSIÓN CON MONTOS ABSOLUTOS
  // ============================================================================
  
  validarMontosDistribucion(): void {
    const montoNeto = parseFloat(this.distribucionForm.get('montoNeto')?.value || '0');
    const montoIva = parseFloat(this.distribucionForm.get('montoIva')?.value || '0');
    const saldoDisponible = this.movimientoSeleccionado?.saldo_disponible || 0;
    const totalDistribucion = montoNeto + montoIva;
    
    // Validar que no exceda el saldo disponible del movimiento
    if (totalDistribucion > saldoDisponible) {
      this.distribucionForm.get('montoNeto')?.setErrors({ excedeMovimiento: true });
      this.distribucionForm.get('montoIva')?.setErrors({ excedeMovimiento: true });
    } else {
      // Validar límites individuales si hay estado de factura
      if (this.estadoFacturaActual) {
        const netoDisponibleFactura = this.estadoFacturaActual.cobertura.neto_pendiente;
        const ivaDisponibleFactura = this.estadoFacturaActual.cobertura.iva_pendiente;
        
        // Validar neto
        if (montoNeto > netoDisponibleFactura) {
          this.distribucionForm.get('montoNeto')?.setErrors({ 
            excedeFacturaNeto: true,
            maximoDisponible: netoDisponibleFactura 
          });
        } else {
          this.distribucionForm.get('montoNeto')?.setErrors(null);
        }
        
        // Validar IVA
        if (montoIva > ivaDisponibleFactura) {
          this.distribucionForm.get('montoIva')?.setErrors({ 
            excedeFacturaIva: true,
            maximoDisponible: ivaDisponibleFactura 
          });
        } else {
          this.distribucionForm.get('montoIva')?.setErrors(null);
        }
      } else {
        this.distribucionForm.get('montoNeto')?.setErrors(null);
        this.distribucionForm.get('montoIva')?.setErrors(null);
      }
    }
    
    // Actualizar el monto total a distribuir
    this.distribucionForm.patchValue({ montoDistribuir: totalDistribucion }, { emitEvent: false });
  }
  
  validarMontoDistribuir(): void {
    const monto = parseFloat(this.distribucionForm.get('montoDistribuir')?.value || '0');
    const saldoDisponible = this.movimientoSeleccionado?.saldo_disponible || 0;
    
    if (monto > saldoDisponible) {
      this.distribucionForm.get('montoDistribuir')?.setErrors({ 
        montoExcesivo: true,
        montoMaximo: saldoDisponible 
      });
    } else if (monto <= 0) {
      this.distribucionForm.get('montoDistribuir')?.setErrors({ montoInvalido: true });
    } else {
      this.distribucionForm.get('montoDistribuir')?.setErrors(null);
    }
  }
  
  // ============================================================================
  // MÉTODOS DE UTILIDAD ACTUALIZADOS
  // ============================================================================
  
  obtenerErrorMontoNeto(): string | null {
    const control = this.distribucionForm.get('montoNeto');
    if (control?.errors) {
      if (control.errors['excedeFacturaNeto']) {
        return `Excede el neto pendiente: ${this.formatearMonto(control.errors['maximoDisponible'])}`;
      }
      if (control.errors['excedeMovimiento']) {
        return 'El total (neto + IVA) excede el saldo del movimiento';
      }
      if (control.errors['required']) {
        return 'El monto neto es requerido';
      }
    }
    return null;
  }
  
  obtenerErrorMontoIva(): string | null {
    const control = this.distribucionForm.get('montoIva');
    if (control?.errors) {
      if (control.errors['excedeFacturaIva']) {
        return `Excede el IVA pendiente: ${this.formatearMonto(control.errors['maximoDisponible'])}`;
      }
      if (control.errors['excedeMovimiento']) {
        return 'El total (neto + IVA) excede el saldo del movimiento';
      }
      if (control.errors['required']) {
        return 'El monto IVA es requerido';
      }
    }
    return null;
  }
  
  calcularTotalSaldoDisponible(): number {
    return this.movimientosConSaldo.reduce((sum, mov) => sum + mov.saldo_disponible, 0);
  }
  
  calcularMontos(): { neto: number, iva: number, total: number } {
    const neto = parseFloat(this.distribucionForm.get('montoNeto')?.value || '0');
    const iva = parseFloat(this.distribucionForm.get('montoIva')?.value || '0');
    
    return {
      neto: neto,
      iva: iva,
      total: neto + iva
    };
  }
  
  sugerirDistribucionProporcional(): void {
    if (!this.movimientoSeleccionado || !this.estadoFacturaActual) return;
    
    const saldoDisponible = this.movimientoSeleccionado.saldo_disponible;
    const facturaTotal = this.estadoFacturaActual.factura.monto_total;
    const facturaNeto = this.estadoFacturaActual.factura.monto_neto;
    const facturaIva = this.estadoFacturaActual.factura.monto_iva;
    
    // Calcular proporción original de la factura
    const proporcionNeto = facturaNeto / facturaTotal;
    const proporcionIva = facturaIva / facturaTotal;
    
    // Aplicar proporción al saldo disponible
    const netoSugerido = saldoDisponible * proporcionNeto;
    const ivaSugerido = saldoDisponible * proporcionIva;
    
    // Limitar por lo pendiente en la factura
    const netoFinal = Math.min(netoSugerido, this.estadoFacturaActual.cobertura.neto_pendiente);
    const ivaFinal = Math.min(ivaSugerido, this.estadoFacturaActual.cobertura.iva_pendiente);
    
    this.distribucionForm.patchValue({
      montoNeto: netoFinal.toFixed(0),
      montoIva: ivaFinal.toFixed(0)
    });
    
    this.validarMontosDistribucion();
  }
  
  formatearMonto(monto: number): string {
    return new Intl.NumberFormat('es-CL', {
      style: 'currency',
      currency: 'CLP',
      minimumFractionDigits: 0
    }).format(monto);
  }
  
  calcularPorcentajeUso(saldoDisponible: number, montoOriginal: number): number {
    if (montoOriginal === 0) return 0;
    return ((montoOriginal - saldoDisponible) / montoOriginal) * 100;
  }
  
  mostrarError(mensaje: string): void {
    this.error = mensaje;
    this.exito = '';
    setTimeout(() => this.limpiarError(), 8000);
  }
  
  mostrarExito(mensaje: string): void {
    this.exito = mensaje;
    this.error = '';
    setTimeout(() => this.exito = '', 8000);
  }
  
  limpiarError(): void {
    this.error = '';
  }
  
  resetearFormulario(): void {
    this.pasoActual = 1;
    this.seleccionForm.reset();
    this.distribucionForm.reset({
      montoNeto: '0',
      montoIva: '0',
      montoDistribuir: '0'
    });
    this.archivoPdfSeleccionado = null;
    this.bancoSeleccionado = null;
    this.cuentaSeleccionada = null;
    this.movimientoSeleccionado = null;
    this.facturaSeleccionada = null;
    this.fechaCartola = null;
    this.periodoCartola = null;
    this.movimientosConSaldo = [];
    this.facturasDisponibles = [];
    this.cuentasOrigen = [];
    this.estadoFacturaActual = null;
    this.modoDistribucionMultiple = false;
    this.ultimaRespuestaProcesamiento = null;
    this.filtrosAplicados = null;
    this.limpiarError();
  }
  
  // ============================================================================
  // MÉTODOS DE TRACKING PARA ANGULAR
  // ============================================================================
  
  trackByMovimientoId(index: number, movimiento: MovimientoConSaldo): number {
    return movimiento.id;
  }
  
  trackByFacturaId(index: number, factura: FacturaVenta): number {
    return factura.id;
  }
  
  trackByBancoId(index: number, banco: Banco): string {
    return banco.codigo_sbif;
  }
  
  trackByCuentaId(index: number, cuenta: CuentaOrigen): number {
    return cuenta.id;
  }
}