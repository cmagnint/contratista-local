// sociedad.component.ts
import { Component, OnInit, Inject, PLATFORM_ID } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ContratistaApiService } from '../../../../services/contratista-api.service';
import { JwtService } from '../../../../services/jwt.service';
// Interfaces for type safety
interface Banco {
  codigo_sbif: string;
  nombre: string;
}

interface CuentaOrigen {
  id?: number;
  sociedad: number;
  banco: string;
  banco_nombre?: string;
  tipo_cuenta: string;
  numero_cuenta: string;
}

interface Sociedad {
  id: number;
  holding: number;
  rol_sociedad: string;
  nombre: string;
  nombre_representante: string;
  rut_representante: string;
  comuna: string;
  ciudad: string;
  calle: string;
  cuentas_origen: CuentaOrigen[];
}

interface TipoCuenta {
  valor: string;
  etiqueta: string;
}

interface OpcionesBanco {
  [key: string]: TipoCuenta[];
}

@Component({
  selector: 'app-sociedad',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule],
  templateUrl: './sociedad.component.html',
  styleUrls: ['./sociedad.component.css']
})
export class SociedadComponent implements OnInit {
  // Data arrays
  sociedades: Sociedad[] = [];
  bancos: Banco[] = [];
  
  // UI state management
  selectedSociedad?: Sociedad;
  isLoading = false;
  showCuentaForm = false;
  errorMessage = '';
  successMessage = '';

  showEditCuentaForm = false;
  selectedCuenta?: CuentaOrigen;
  
  // Form groups
  sociedadForm: FormGroup;
  cuentaForm: FormGroup;

  public holdingId: string = '';

  // Tipos de cuenta por banco
  tiposCuentaPorBanco: OpcionesBanco = {
    '012': [ // Banco Estado
      { valor: 'CCT', etiqueta: 'Cuenta Corriente (CCT)' },
      { valor: 'CTV', etiqueta: 'Chequera Electrónica (CTV)' }
    ],
    'default': [
      { valor: 'CTE', etiqueta: 'Cuenta Corriente' },
      { valor: 'VIS', etiqueta: 'Cuenta Vista' },
      { valor: 'AHO', etiqueta: 'Cuenta Ahorro' }
    ]
  };

  tiposCuentaActuales: TipoCuenta[] = [];

  constructor(
    private api: ContratistaApiService,
    private jwtService: JwtService,
    @Inject(PLATFORM_ID) private platformId: Object,
    private fb: FormBuilder
  ) {
    // Initialize sociedad form with validators
    this.sociedadForm = this.fb.group({
      nombre_representante: ['', [Validators.required, Validators.minLength(3)]],
      rut_representante: ['', [Validators.required, Validators.pattern(/^\d{1,2}\.\d{3}\.\d{3}[-][0-9kK]{1}$/)]],
      comuna: ['', Validators.required],
      ciudad: ['', Validators.required],
      calle: ['', Validators.required]
    });

    // Initialize cuenta form with validators
    this.cuentaForm = this.fb.group({
      banco: ['', Validators.required],
      tipo_cuenta: ['', Validators.required],
      numero_cuenta: ['', [Validators.required, Validators.pattern(/^\d+$/)]]
    });

    // Listener para cambios en el banco seleccionado
    this.cuentaForm.get('banco')?.valueChanges.subscribe(bancoSeleccionado => {
      this.actualizarTiposCuenta(bancoSeleccionado);
    });
  }

  editCuenta(cuenta: CuentaOrigen) {
    this.selectedCuenta = cuenta;
    this.showEditCuentaForm = true;
    this.showCuentaForm = false;
  
    // Actualizar los tipos de cuenta según el banco
    this.actualizarTiposCuenta(cuenta.banco);
    
    this.cuentaForm.patchValue({
      banco: cuenta.banco,
      tipo_cuenta: cuenta.tipo_cuenta,
      numero_cuenta: cuenta.numero_cuenta
    });
  }

  updateCuenta() {
    if (!this.selectedSociedad || !this.selectedCuenta || !this.cuentaForm.valid) return;
  
    this.isLoading = true;
    this.api.patch(
      `api_cuentas_origen/${this.selectedSociedad.id}/${this.selectedCuenta.id}/`, 
      this.cuentaForm.value
    ).subscribe({
      next: (data: CuentaOrigen) => {
        const index = this.selectedSociedad!.cuentas_origen.findIndex(
          c => c.id === this.selectedCuenta!.id
        );
        if (index !== -1) {
          this.selectedSociedad!.cuentas_origen[index] = data;
        }
        this.cuentaForm.reset();
        this.showEditCuentaForm = false;
        this.selectedCuenta = undefined;
        this.successMessage = 'Cuenta bancaria actualizada exitosamente';
        this.isLoading = false;
      },
      error: (error) => {
        this.errorMessage = 'Error al actualizar cuenta: ' + error.message;
        this.isLoading = false;
      }
    });
  }

  // Funciones de utilidad para manejo de RUT
  private formatRutDisplay(rut: string): string {
    if (!rut) return '';
    
    let rutLimpio = rut.toString().replace(/[^0-9kK]/g, '');
    
    if (rutLimpio.length < 2) return rutLimpio;
    
    const dv = rutLimpio.slice(-1);
    const rutNumeros = rutLimpio.slice(0, -1);
    
    let rutFormateado = '';
    let i = rutNumeros.length;
    
    while (i > 0) {
      if (rutFormateado) rutFormateado = '.' + rutFormateado;
      rutFormateado = rutNumeros.slice(Math.max(0, i-3), i) + rutFormateado;
      i -= 3;
    }
    
    return rutFormateado + '-' + dv;
  }

  private cleanRut(rut: string): string {
    if (!rut) return '';
    return rut.toString().replace(/[^0-9kK]/g, '').toUpperCase();
  }

  onRutInput(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (!input) return;
    
    const rutLimpio = this.cleanRut(input.value);
    const rutFormateado = this.formatRutDisplay(rutLimpio);
    
    this.sociedadForm.patchValue({ rut_representante: rutFormateado }, { emitEvent: false });
  }

  actualizarTiposCuenta(codigoBanco: string) {
    this.tiposCuentaActuales = this.tiposCuentaPorBanco[codigoBanco] || 
                              this.tiposCuentaPorBanco['default'];
    this.cuentaForm.patchValue({ tipo_cuenta: '' });
  }

  ngOnInit() {
    if (isPlatformBrowser(this.platformId)) {
      this.holdingId = this.getHoldingIdFromJWT();
    this.loadInitialData();
    }
  }

   /**
   * 🎯 NUEVO MÉTODO: Extrae holding_id del JWT
   */
  private getHoldingIdFromJWT(): string {
    try {
      const userInfo = this.jwtService.getUserInfo();
      const holdingId = userInfo?.holding_id;
      
      console.log('🔍 Holding ID del JWT:', holdingId);
      
      if (holdingId && holdingId !== null ) {
        return holdingId.toString();
      } else {
        console.warn('⚠️ Holding ID no encontrado en JWT o es null');
        return '';
      }
    } catch (error) {
      console.error('❌ Error extrayendo holding_id del JWT:', error);
      return '';
    }
  }

  loadInitialData() {
    this.isLoading = true;
    this.loadSociedades();
    this.loadBancos();
  }

  loadSociedades() {
    
    if (!this.holdingId) {
      this.errorMessage = 'No se encontró el ID del holding';
      this.isLoading = false;
      return;
    }

    this.api.get(`api_sociedades_modify/${this.holdingId}`).subscribe({
      next: (data: Sociedad[]) => {
        this.sociedades = data.map(sociedad => ({
          ...sociedad,
          rut_representante: this.formatRutDisplay(sociedad.rut_representante)
        }));
        this.isLoading = false;
      },
      error: (error) => {
        this.errorMessage = 'Error al cargar sociedades: ' + error.message;
        this.isLoading = false;
      }
    });
  }

  loadBancos() {
    this.api.get('api_bancos').subscribe({
      next: (data: Banco[]) => {
        this.bancos = data;
      },
      error: (error) => {
        this.errorMessage = 'Error al cargar bancos: ' + error.message;
      }
    });
  }

  selectSociedad(sociedad: Sociedad) {
    this.selectedSociedad = sociedad;
    this.sociedadForm.patchValue({
      nombre_representante: sociedad.nombre_representante,
      rut_representante: this.formatRutDisplay(sociedad.rut_representante),
      comuna: sociedad.comuna,
      ciudad: sociedad.ciudad,
      calle: sociedad.calle
    });
    this.errorMessage = '';
    this.successMessage = '';
  }

  updateSociedad() {
    if (!this.selectedSociedad || !this.sociedadForm.valid) return;
    
    
    if (!this.holdingId) {
      this.errorMessage = 'No se encontró el ID del holding';
      return;
    }

    this.isLoading = true;

    const formData = {
      ...this.sociedadForm.value,
      rut_representante: this.cleanRut(this.sociedadForm.get('rut_representante')?.value)
    };

    this.api.patch(
      `api_sociedades_modify/${this.holdingId}/${this.selectedSociedad.id}/`, 
      formData
    ).subscribe({
      next: (data: Sociedad) => {
        const index = this.sociedades.findIndex(s => s.id === data.id);
        if (index !== -1) {
          this.sociedades[index] = {
            ...data,
            rut_representante: this.formatRutDisplay(data.rut_representante)
          };
        }
        this.selectedSociedad = this.sociedades[index];
        this.successMessage = 'Sociedad actualizada exitosamente';
        this.isLoading = false;
      },
      error: (error) => {
        this.errorMessage = 'Error al actualizar sociedad: ' + error.message;
        this.isLoading = false;
      }
    });
  }

  addCuenta() {
    if (!this.selectedSociedad || !this.cuentaForm.valid) return;

    this.isLoading = true;
    this.api.post(
      `api_cuentas_origen/${this.selectedSociedad.id}/`, 
      this.cuentaForm.value
    ).subscribe({
      next: (data: CuentaOrigen) => {
        if (this.selectedSociedad) {
          this.selectedSociedad.cuentas_origen.push(data);
        }
        this.cuentaForm.reset();
        this.showCuentaForm = false;
        this.successMessage = 'Cuenta bancaria agregada exitosamente';
        this.isLoading = false;
      },
      error: (error) => {
        this.errorMessage = 'Error al agregar cuenta: ' + error.message;
        this.isLoading = false;
      }
    });
  }

  getTipoCuentaDisplay(tipo: string): string {
    const opcionBancoEstado = this.tiposCuentaPorBanco['012']
      .find(t => t.valor === tipo);
    if (opcionBancoEstado) return opcionBancoEstado.etiqueta;

    const opcionDefault = this.tiposCuentaPorBanco['default']
      .find(t => t.valor === tipo);
    return opcionDefault ? opcionDefault.etiqueta : tipo;
  }

  toggleCuentaForm() {
    this.showCuentaForm = !this.showCuentaForm;
    if (this.showCuentaForm) {
      this.showEditCuentaForm = false;
      this.selectedCuenta = undefined;
    }
    this.errorMessage = '';
    this.successMessage = '';
    if (!this.showCuentaForm) {
      this.cuentaForm.reset();
    }
  }
}