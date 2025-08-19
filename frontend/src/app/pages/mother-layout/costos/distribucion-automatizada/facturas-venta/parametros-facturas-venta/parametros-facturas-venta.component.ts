// parametros-facturas-venta.component.ts
import { Component, OnInit, Inject, PLATFORM_ID } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ContratistaApiService } from '../../../../../../services/contratista-api.service';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatIconModule } from '@angular/material/icon';
import { MatSelectModule } from '@angular/material/select';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatDividerModule } from '@angular/material/divider';
import { MatTooltipModule } from '@angular/material/tooltip';

interface ConfiguracionSII {
  id?: number;
  rut_sii: string;
  password_sii: string;
  empresa_rut: string;
  empresa_nombre: string;
  hora_ejecucion: string;
  mes: number;
  year: number;
  periodo_texto?: string;
  activo: boolean;
  created_at?: string;
  updated_at?: string;
}

@Component({
  selector: 'app-parametros-facturas-venta',
  standalone: true,
  imports: [
      CommonModule,
      ReactiveFormsModule,
      MatButtonModule,
      MatCardModule,
      MatFormFieldModule,
      MatInputModule,
      MatIconModule,
      MatSelectModule,
      MatSlideToggleModule,
      MatProgressSpinnerModule,
      MatDividerModule,
      MatTooltipModule
    ],
  templateUrl: './parametros-facturas-venta.component.html',
  styleUrl: './parametros-facturas-venta.component.css'
})
export class ParametrosFacturasVentaComponent implements OnInit {
  
  configuracionForm: FormGroup;
  loading = false;
  guardando = false;
  probandoConexion = false;
  configuracionExistente: ConfiguracionSII | null = null;
  mostrarPassword = false;

  // Información de la empresa actual
  sociedadTrabajoActual: any = null;

  // Opciones para meses
  mesesDisponibles = [
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

  // Opciones para años (últimos 3 años y próximos 2)
  anosDisponibles: number[] = [];

  constructor(
    private fb: FormBuilder,
    private contratistaApi: ContratistaApiService,
    private snackBar: MatSnackBar,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {
    this.configuracionForm = this.createForm();
    this.generateAnosDisponibles();
  }

  ngOnInit(): void {
    if (isPlatformBrowser(this.platformId)) {
      this.cargarSociedadTrabajoActual();
      this.cargarConfiguracion();
    }
  }

  private createForm(): FormGroup {
    const fechaActual = new Date();
    const mesActual = fechaActual.getMonth() + 1; // getMonth() retorna 0-11
    const anoActual = fechaActual.getFullYear();

    return this.fb.group({
      rut_sii: ['', [Validators.required]],
      password_sii: ['', [Validators.required, Validators.minLength(6)]],
      hora_ejecucion: ['08:00', [Validators.required, Validators.pattern(/^([01]?[0-9]|2[0-3]):[0-5][0-9]$/)]],
      mes: [mesActual, [Validators.required, Validators.min(1), Validators.max(12)]],
      year: [anoActual, [Validators.required, Validators.min(2020), Validators.max(2030)]],
      activo: [true]
    });
  }

  private generateAnosDisponibles(): void {
    const fechaActual = new Date();
    const anoActual = fechaActual.getFullYear();
    
    // Generar desde 3 años atrás hasta 2 años adelante
    for (let i = anoActual - 3; i <= anoActual + 2; i++) {
      this.anosDisponibles.push(i);
    }
  }

  // ==================== SOCIEDAD DE TRABAJO ====================

  cargarSociedadTrabajoActual(): void {
    const sociedadGuardada = localStorage.getItem('sociedad_trabajo_actual');
    if (sociedadGuardada) {
      try {
        this.sociedadTrabajoActual = JSON.parse(sociedadGuardada);
        console.log('Sociedad de trabajo cargada:', this.sociedadTrabajoActual);
      } catch (error) {
        console.error('Error al parsear sociedad_trabajo_actual:', error);
        this.mostrarMensaje('Error al cargar la sociedad de trabajo actual', 'error');
      }
    } else {
      console.warn('No se encontró sociedad_trabajo_actual en localStorage');
      this.mostrarMensaje('No se ha seleccionado una empresa. Por favor, seleccione una empresa primero.', 'error');
    }
  }

  // ==================== FUNCIONES DE FORMATEO DE RUT ====================

  /**
   * Limpia el RUT removiendo puntos, guiones y espacios, dejando solo números y K
   * @param rut - El RUT a limpiar
   * @returns RUT limpio con solo números y K
   */
  private limpiarRut(rut: string): string {
    if (!rut) return '';
    return rut.toString().replace(/[^0-9Kk]/g, '').toUpperCase();
  }

  /**
   * Formatea un RUT agregando puntos y guión
   * Ejemplo: 182850045 -> 18.285.004-5
   * @param rut - El RUT a formatear (puede estar limpio o ya formateado)
   * @returns RUT formateado con puntos y guión
   */
  private formatearRut(rut: string): string {
    if (!rut) return '';
    
    // Limpiar el RUT primero
    const rutLimpio = this.limpiarRut(rut);
    
    if (rutLimpio.length < 2) return rutLimpio;
    
    // Separar el dígito verificador
    const digitoVerificador = rutLimpio.slice(-1);
    const numeroRut = rutLimpio.slice(0, -1);
    
    if (numeroRut.length === 0) return rutLimpio;
    
    // Formatear el número con puntos
    const numeroFormateado = numeroRut.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
    
    return `${numeroFormateado}-${digitoVerificador}`;
  }

  /**
   * Valida el formato del RUT y calcula si el dígito verificador es correcto
   * @param rut - El RUT a validar
   * @returns true si el RUT es válido, false en caso contrario
   */
  private validarRut(rut: string): boolean {
    if (!rut) return false;
    
    const rutLimpio = this.limpiarRut(rut);
    
    if (rutLimpio.length < 2) return false;
    
    const digitoVerificador = rutLimpio.slice(-1);
    const numeroRut = rutLimpio.slice(0, -1);
    
    // Verificar que el número contenga solo dígitos
    if (!/^\d+$/.test(numeroRut)) return false;
    
    // Calcular dígito verificador
    let suma = 0;
    let multiplicador = 2;
    
    for (let i = numeroRut.length - 1; i >= 0; i--) {
      suma += parseInt(numeroRut[i]) * multiplicador;
      multiplicador = multiplicador === 7 ? 2 : multiplicador + 1;
    }
    
    const resto = suma % 11;
    const digitoCalculado = resto < 2 ? resto.toString() : resto === 10 ? 'K' : (11 - resto).toString();
    
    return digitoVerificador === digitoCalculado;
  }

  /**
   * Maneja el evento de input para el campo de RUT SII
   * Formatea automáticamente mientras el usuario escribe
   * @param event - El evento de input
   */
  onRutInput(event: any): void {
    const valor = event.target.value;
    const rutFormateado = this.formatearRut(valor);
    
    // Actualizar el valor del campo en el formulario
    this.configuracionForm.patchValue({
      rut_sii: rutFormateado
    });
    
    // Actualizar el valor del input directamente para evitar problemas de cursor
    event.target.value = rutFormateado;
  }

  /**
   * Valida el RUT cuando el usuario sale del campo (blur)
   */
  onRutBlur(): void {
    const control = this.configuracionForm.get('rut_sii');
    if (control && control.value) {
      const rutFormateado = this.formatearRut(control.value);
      control.setValue(rutFormateado);
      
      // Validar el RUT
      if (!this.validarRut(rutFormateado)) {
        control.setErrors({ rutInvalido: true });
      } else {
        // Remover el error de RUT inválido si existe, pero mantener otros errores
        const erroresActuales = control.errors;
        if (erroresActuales) {
          delete erroresActuales['rutInvalido'];
          control.setErrors(Object.keys(erroresActuales).length > 0 ? erroresActuales : null);
        }
      }
    }
  }

  /**
   * Permite solo caracteres válidos para RUT (números y K)
   * @param event - El evento de teclado
   */
  onRutKeyPress(event: KeyboardEvent): void {
    const char = event.key;
    const isNumber = /[0-9]/.test(char);
    const isK = char.toUpperCase() === 'K';
    const isControlKey = ['Backspace', 'Delete', 'Tab', 'Enter', 'ArrowLeft', 'ArrowRight'].includes(event.key);
    
    if (!isNumber && !isK && !isControlKey) {
      event.preventDefault();
    }
  }

  // ==================== MÉTODOS DE CONFIGURACIÓN ====================

  async cargarConfiguracion(): Promise<void> {
  this.loading = true;
  
  const payload = {
    action: 'get_automatic_configuration'
  };

  try {
    const response = await this.contratistaApi.post('facturas_venta_automatico/', payload).toPromise();
    
    if (response?.data) {
      this.configuracionExistente = response.data;
      this.configuracionForm.patchValue({
        rut_sii: this.formatearRut(response.data.rut_sii),
        password_sii: response.data.password_sii || '', // CARGAR LA CONTRASEÑA DESDE EL BACKEND
        hora_ejecucion: response.data.hora_ejecucion,
        mes: response.data.mes,
        year: response.data.year,
        activo: response.data.activo
      });
      
      this.mostrarMensaje('Configuración cargada correctamente', 'success');
    }
  } catch (error) {
    console.error('Error al cargar configuración:', error);
    // Si no existe configuración, no mostramos error
    if (error && (error as any).status !== 404) {
      this.mostrarMensaje('Error al cargar la configuración', 'error');
    }
  } finally {
    this.loading = false;
  }
}

  async guardarConfiguracion(): Promise<void> {
    if (!this.sociedadTrabajoActual) {
      this.mostrarMensaje('No se ha seleccionado una empresa. Por favor, seleccione una empresa primero.', 'error');
      return;
    }

    if (this.configuracionForm.invalid) {
      this.marcarCamposInvalidos();
      this.mostrarMensaje('Por favor, complete todos los campos requeridos', 'error');
      return;
    }

    // Validar RUT SII antes de enviar
    const rutSii = this.configuracionForm.get('rut_sii')?.value;
    
    if (!this.validarRut(rutSii)) {
      this.mostrarMensaje('El RUT del usuario SII es inválido', 'error');
      return;
    }

    // Validar mes y año
    const mes = this.configuracionForm.get('mes')?.value;
    const year = this.configuracionForm.get('year')?.value;
    
    if (!mes || mes < 1 || mes > 12) {
      this.mostrarMensaje('Seleccione un mes válido', 'error');
      return;
    }

    if (!year || year < 2020 || year > 2030) {
      this.mostrarMensaje('Seleccione un año válido', 'error');
      return;
    }

    this.guardando = true;
    
    try {
      const formData = this.configuracionForm.value;
      
      // Limpiar RUT antes de enviar (remover formato)
      formData.rut_sii = this.limpiarRut(formData.rut_sii);
      
      // Agregar datos de la empresa desde localStorage
      formData.empresa_rut = this.limpiarRut(this.sociedadTrabajoActual.rut);
      formData.empresa_nombre = this.sociedadTrabajoActual.nombre;
      
      // Si el password está vacío y existe configuración, no enviarlo
      if (!formData.password_sii && this.configuracionExistente) {
        delete formData.password_sii;
      }

      const payload = {
        action: 'save_automatic_configuration',
        ...formData
      };

      const response = await this.contratistaApi.post('facturas_venta_automatico/', payload).toPromise();
      
      if (response?.status === 'success') {
        this.configuracionExistente = response.data;
        this.mostrarMensaje('Configuración guardada exitosamente', 'success');
        
        // Limpiar password del formulario por seguridad y reformatear RUT
        this.configuracionForm.patchValue({ 
          password_sii: '',
          rut_sii: this.formatearRut(formData.rut_sii)
        });
      } else {
        this.mostrarMensaje(response?.message || 'Error al guardar la configuración', 'error');
      }
      
    } catch (error) {
      console.error('Error al guardar configuración:', error);
      const mensaje = (error as any)?.error?.message || 'Error al guardar la configuración';
      this.mostrarMensaje(mensaje, 'error');
    } finally {
      this.guardando = false;
    }
  }

  async probarConexion(): Promise<void> {
    if (!this.sociedadTrabajoActual) {
      this.mostrarMensaje('No se ha seleccionado una empresa. Por favor, seleccione una empresa primero.', 'error');
      return;
    }

    if (!this.configuracionForm.get('rut_sii')?.value || !this.configuracionForm.get('password_sii')?.value) {
      this.mostrarMensaje('Ingrese RUT y contraseña para probar la conexión', 'error');
      return;
    }

    // Validar RUT antes de probar
    const rutSii = this.configuracionForm.get('rut_sii')?.value;
    if (!this.validarRut(rutSii)) {
      this.mostrarMensaje('El RUT del usuario SII es inválido', 'error');
      return;
    }

    this.probandoConexion = true;
    
    try {
      const rutSiiLimpio = this.limpiarRut(rutSii);
      const rutEmpresaLimpio = this.limpiarRut(this.sociedadTrabajoActual.rut);
      
      // Primero intentamos guardar una configuración temporal para test
      const payload = {
        action: 'save_automatic_configuration',
        rut_sii: rutSiiLimpio,
        password_sii: this.configuracionForm.get('password_sii')?.value,
        empresa_rut: rutEmpresaLimpio,
        empresa_nombre: this.sociedadTrabajoActual.nombre,
        hora_ejecucion: this.configuracionForm.get('hora_ejecucion')?.value || '08:00',
        mes: this.configuracionForm.get('mes')?.value,
        year: this.configuracionForm.get('year')?.value,
        activo: false, // Desactivado para el test
        test_mode: true // Indicar que es un test
      };

      const response = await this.contratistaApi.post('facturas_venta_automatico/', payload).toPromise();
      
      if (response?.status === 'success') {
        // Ahora intentamos ejecutar el proceso de test
        const testPayload = {
          action: 'execute_automatic_process_manual',
          test_mode: true
        };
        
        const testResponse = await this.contratistaApi.post('facturas_venta_automatico/', testPayload).toPromise();
        
        if (testResponse?.status === 'success') {
          this.mostrarMensaje('✅ Conexión exitosa con el SII', 'success');
        } else {
          this.mostrarMensaje('❌ Error en las credenciales del SII: ' + (testResponse?.message || 'Error desconocido'), 'error');
        }
      } else {
        this.mostrarMensaje('❌ Error al configurar el test: ' + (response?.message || 'Error desconocido'), 'error');
      }
      
    } catch (error) {
      console.error('Error al probar conexión:', error);
      const errorMsg = (error as any)?.error?.message || (error as any)?.message || 'Error desconocido';
      this.mostrarMensaje('❌ Error al probar la conexión con el SII: ' + errorMsg, 'error');
    } finally {
      this.probandoConexion = false;
    }
  }

  toggleMostrarPassword(): void {
    this.mostrarPassword = !this.mostrarPassword;
  }

  limpiarFormulario(): void {
    const fechaActual = new Date();
    const mesActual = fechaActual.getMonth() + 1;
    const anoActual = fechaActual.getFullYear();

    this.configuracionForm.reset({
      rut_sii: '',
      password_sii: '',
      hora_ejecucion: '08:00',
      mes: mesActual,
      year: anoActual,
      activo: true
    });
    this.configuracionExistente = null;
    this.mostrarMensaje('Formulario limpiado', 'info');
  }

  private marcarCamposInvalidos(): void {
    Object.keys(this.configuracionForm.controls).forEach(key => {
      const control = this.configuracionForm.get(key);
      if (control && control.invalid) {
        control.markAsTouched();
      }
    });
  }

  private mostrarMensaje(mensaje: string, tipo: 'success' | 'error' | 'info'): void {
    const config = {
      duration: tipo === 'error' ? 5000 : 3000,
      panelClass: [`snackbar-${tipo}`]
    };
    
    this.snackBar.open(mensaje, 'Cerrar', config);
  }

  // ==================== MÉTODOS AUXILIARES PARA PERÍODO ====================

  /**
   * Obtiene el texto del período actual seleccionado
   */
  getPeriodoTexto(): string {
    const mes = this.configuracionForm.get('mes')?.value;
    const year = this.configuracionForm.get('year')?.value;
    
    if (!mes || !year) return 'Período no definido';
    
    const mesTexto = this.mesesDisponibles.find(m => m.value === mes)?.label || 'Mes desconocido';
    return `${mesTexto} ${year}`;
  }

  // ==================== GETTERS PARA VALIDACIONES ====================

  get rutSiiInvalido(): boolean {
    const control = this.configuracionForm.get('rut_sii');
    return !!(control && control.invalid && control.touched);
  }

  get passwordInvalido(): boolean {
    const control = this.configuracionForm.get('password_sii');
    return !!(control && control.invalid && control.touched);
  }

  get horaInvalida(): boolean {
    const control = this.configuracionForm.get('hora_ejecucion');
    return !!(control && control.invalid && control.touched);
  }

  get mesInvalido(): boolean {
    const control = this.configuracionForm.get('mes');
    return !!(control && control.invalid && control.touched);
  }

  get yearInvalido(): boolean {
    const control = this.configuracionForm.get('year');
    return !!(control && control.invalid && control.touched);
  }

  // ==================== GETTER PARA EMPRESA ACTUAL ====================

  get empresaActualInfo(): string {
    if (this.sociedadTrabajoActual) {
      return `${this.sociedadTrabajoActual.nombre} (${this.formatearRut(this.sociedadTrabajoActual.rut)})`;
    }
    return 'No se ha seleccionado empresa';
  }

  // ==================== GETTER PARA CONFIGURACIÓN EXISTENTE ====================

  get configuracionExistenteInfo(): string {
    if (this.configuracionExistente && this.configuracionExistente.periodo_texto) {
      return this.configuracionExistente.periodo_texto;
    }
    return this.getPeriodoTexto();
  }
}

