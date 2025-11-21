import { Component, OnInit, AfterViewInit, PLATFORM_ID, Inject } from '@angular/core';
import { isPlatformBrowser, CommonModule } from '@angular/common';
import { ContratistaApiService } from '../../../../services/contratista-api.service';
import { ReactiveFormsModule, FormsModule } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';
import { MatIconModule } from '@angular/material/icon';
import { JwtService } from '../../../../services/jwt.service';

@Component({
  selector: 'app-enrolamiento',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    FormsModule,
    MatTableModule,
    MatIconModule,
  ],
  templateUrl: './enrolamiento.component.html',
  styleUrl: './enrolamiento.component.css'
})
export class EnrolamientoComponent implements OnInit {

  modals: any = {
    loadingModal: false
  };

  // CONTROL DE FLUJO
  pasoActual: number = 1;
  holding: string = '';
  
  // PASO 1: SOCIEDAD
  sociedadesCargadas: any[] = [];
  selectedSociedadId: number | null = null;
  
  // PASO 2: PRE-CONTRATACIÓN
  foliosCargados: any[] = [];
  fundosCargados: any[] = [];
  laboresCargadas: any[] = [];
  horariosCargados: any[] = [];
  transportistasCargados: any[] = [];
  vehiculosCargados: any[] = [];
  casasCargadas: any[] = [];
  supervisoresCargados: any[] = [];
  jefesCuadrillaCargados: any[] = [];
  
  selectedFolioId: number | null = null;
  selectedFundoId: number | null = null;
  selectedLaborId: number | null = null;
  selectedHorarioId: number | null = null;
  selectedTransportistaId: number | null = null;
  selectedVehiculoId: number | null = null;
  selectedCasaId: number | null = null;
  selectedSupervisorId: number | null = null;
  selectedJefeCuadrillaId: number | null = null;
  jefesCuadrillaFiltrados: any[] = [];
  
  // PASO 3: CONTRATACIÓN
  tipoDocumento: string = 'CEDULA_CHILENA';
  
  // Datos del trabajador
  nombres: string = '';
  apellidos: string = '';
  rut: string = '';
  dni: string = '';
  nic: string = '';
  sexo: string = '';
  estadoCivil: string = 'SOLTERO(A)';
  nacionalidad: string = 'CHILENA';
  telefonoPrefijo: string = '+56';
  telefonoNumero: string = '';
  correoUsuario: string = '';
  correoDominio: string = 'gmail.com';
  direccion: string = '';
  fechaNacimiento: string = '';
  
  nacionalidades: string[] = [
    'CHILENA', 'BOLIVIANA', 'ARGENTINA', 'PERUANA', 
    'VENEZOLANA', 'HAITIANA', 'PARAGUAYA', 'URUGUAYA', 'BRASILEÑA'
  ];
  
  // Datos bancarios
  metodoPago: string = 'EFECTIVO';
  banco: string = '';
  tipoCuenta: string = 'CUENTA RUT';
  numeroCuenta: string = '';
  
  bancosCargados: any[] = [];
  
  // Imágenes
  imagenCarnetFrente: File | null = null;
  imagenCarnetReverso: File | null = null;
  previewCarnetFrente: string | null = null;
  previewCarnetReverso: string | null = null;
  

  
  // Estados
  cargandoOCR: boolean = false;
  guardando: boolean = false;
  
  // Dropdowns
  dropdownStates: any = {
    sociedades: false,
    folios: false,
    fundos: false,
    labores: false,
    horarios: false,
    transportistas: false,
    vehiculos: false,
    casas: false,
    supervisores: false,
    jefes: false,
    bancos: false,
    nacionalidades: false
  };

  constructor(
    private contratistaApiService: ContratistaApiService,
    private jwtService: JwtService,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {}

  ngOnInit(): void {
    if (isPlatformBrowser(this.platformId)) {
      this.holding = this.getHoldingIdFromJWT();
      this.cargarSociedades();
    }
  }

  private getHoldingIdFromJWT(): string {
    try {
      const userInfo = this.jwtService.getUserInfo();
      const holdingId = userInfo?.holding_id;
      
      if (holdingId && holdingId !== null) {
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

  // ==================== PASO 1: SOCIEDAD ====================
  
  cargarSociedades(): void {
    this.contratistaApiService.get(`api_sociedad/${this.holding}/`).subscribe({
      next: (response) => {
        this.sociedadesCargadas = response;
        if (response.length === 1) {
          this.selectedSociedadId = response[0].id;
        }
      },
      error: (error) => {
        console.error('Error cargando sociedades:', error);
      }
    });
  }

  get jefeSeleccionadoNombre(): string {
    if (!this.selectedJefeCuadrillaId) return 'SELECCIONAR JEFE CUADRILLA (Opcional)';
    return this.jefesCuadrillaFiltrados.find(j => j.id === this.selectedJefeCuadrillaId)?.nombre || 'SELECCIONAR JEFE CUADRILLA (Opcional)';
  }

  toggleSelectionSupervisor(id: number): void {
    this.selectedSupervisorId = this.selectedSupervisorId === id ? null : id;
    this.selectedJefeCuadrillaId = null;
    this.actualizarJefesCuadrilla();
  }

  actualizarJefesCuadrilla(): void {
    if (!this.selectedSupervisorId) {
      this.jefesCuadrillaFiltrados = [];
      return;
    }
    const supervisor = this.supervisoresCargados.find(s => s.id === this.selectedSupervisorId);
    this.jefesCuadrillaFiltrados = supervisor?.jefes_cuadrilla || [];
    
    if (this.jefesCuadrillaFiltrados.length === 1) {
      this.selectedJefeCuadrillaId = this.jefesCuadrillaFiltrados[0].id;
    }
  }

  toggleSelectionSociedad(id: number): void {
    this.selectedSociedadId = this.selectedSociedadId === id ? null : id;
  }

  siguientePreContratacion(): void {
    if (!this.selectedSociedadId) {
      alert('Debe seleccionar una sociedad');
      return;
    }
    this.pasoActual = 2;
    this.cargarDatosPreContratacion();
  }

  // ==================== PASO 2: PRE-CONTRATACIÓN ====================

  cargarDatosPreContratacion(): void {
    this.contratistaApiService.get(`folio_comercial/${this.holding}/`).subscribe({
      next: (response) => {
        this.foliosCargados = response;
        if (response.length === 1) {
          this.selectedFolioId = response[0].id;
          this.onFolioChange();
        }
      },
      error: (error) => console.error('Error cargando folios:', error)
    });
    
    this.contratistaApiService.get(`api_supervisores/${this.holding}/`).subscribe({
      next: (response) => {
        this.supervisoresCargados = response;
        if (response.length === 1) {
          this.selectedSupervisorId = response[0].id;
          this.actualizarJefesCuadrilla();
        }
      },
      error: (error) => console.error('Error cargando supervisores:', error)
    });

    this.contratistaApiService.get(`api_casas_trabajadores/?holding=${this.holding}`).subscribe({
      next: (response) => {
        this.casasCargadas = response;
        if (response.length === 1) this.selectedCasaId = response[0].id;
      },
      error: (error) => console.error('Error cargando casas:', error)
    });
  }

  onFolioChange(): void {
    if (!this.selectedFolioId) return;
    
    const folio = this.foliosCargados.find(f => f.id === this.selectedFolioId);
    if (folio) {
      this.fundosCargados = folio.fundos || [];
      this.laboresCargadas = folio.labores || [];
      this.horariosCargados = folio.horarios || [];
      this.transportistasCargados = folio.transportistas || [];
      
      if (this.fundosCargados.length === 1) this.selectedFundoId = this.fundosCargados[0].id;
      if (this.laboresCargadas.length === 1) this.selectedLaborId = this.laboresCargadas[0].id;
      if (this.horariosCargados.length === 1) this.selectedHorarioId = this.horariosCargados[0].id;
      if (this.transportistasCargados.length === 1) {
        this.selectedTransportistaId = this.transportistasCargados[0].id;
        this.onTransportistaChange();
      }
    }
  }

  onTransportistaChange(): void {
    if (!this.selectedTransportistaId) return;
    
    this.contratistaApiService.get(`api_vehiculos_transportes/?holding=${this.holding}`).subscribe({
      next: (response) => {
        this.vehiculosCargados = response.filter(
          (v: any) => v.empresa === this.selectedTransportistaId
        );
        
        if (this.vehiculosCargados.length === 1) {
          this.selectedVehiculoId = this.vehiculosCargados[0].id;
        }
      },
      error: (error) => console.error('Error cargando vehículos:', error)
    });
  }

  toggleSelectionFolio(id: number): void {
    this.selectedFolioId = this.selectedFolioId === id ? null : id;
    this.onFolioChange();
  }

  toggleSelectionFundo(id: number): void {
    this.selectedFundoId = this.selectedFundoId === id ? null : id;
  }

  toggleSelectionLabor(id: number): void {
    this.selectedLaborId = this.selectedLaborId === id ? null : id;
  }

  toggleSelectionHorario(id: number): void {
    this.selectedHorarioId = this.selectedHorarioId === id ? null : id;
  }

  toggleSelectionTransportista(id: number): void {
    this.selectedTransportistaId = this.selectedTransportistaId === id ? null : id;
    this.onTransportistaChange();
  }

  toggleSelectionVehiculo(id: number): void {
    this.selectedVehiculoId = this.selectedVehiculoId === id ? null : id;
  }

  toggleSelectionCasa(id: number): void {
    this.selectedCasaId = this.selectedCasaId === id ? null : id;
  }

  toggleSelectionJefeCuadrilla(id: number): void {
    this.selectedJefeCuadrillaId = this.selectedJefeCuadrillaId === id ? null : id;
  }

  siguienteContratacion(): void {
    if (!this.validarPreContratacion()) {
      alert('Debe completar todos los campos de pre-contratación');
      return;
    }
    this.pasoActual = 3;
    this.cargarBancos();
  }

  validarPreContratacion(): boolean {
    return !!(
      this.selectedFolioId &&
      this.selectedFundoId &&
      this.selectedLaborId &&
      this.selectedHorarioId &&
      this.selectedCasaId &&
      this.selectedSupervisorId
    );
  }

  volverPreContratacion(): void {
    this.pasoActual = 2;
  }

  // ==================== PASO 3: CONTRATACIÓN ====================

  cargarBancos(): void {
    this.contratistaApiService.get('api_bancos/').subscribe({
      next: (response) => {
        this.bancosCargados = response;
      },
      error: (error) => console.error('Error cargando bancos:', error)
    });
  }

  onFileSelected(event: any, tipo: 'frente' | 'reverso'): void {
    const file = event.target.files[0];
    if (!file) return;

    if (tipo === 'frente') {
      this.imagenCarnetFrente = file;
      this.previewImage(file, 'frente');
      this.procesarOCR(file, 'frente');
    } else {
    // ⬇️ ESTE ES EL ÚNICO CAMBIO
    if (file.type === 'application/pdf') {
      // Si es PDF, convertir primero
      this.convertirPDFaImagen(file, 'reverso');
    } else {
        // Si es imagen, funciona como antes
        this.imagenCarnetReverso = file;
        this.previewImage(file, 'reverso');
      }
    }
  }

  // MÉTODO NUEVO - Agregar después de onFileSelected
  convertirPDFaImagen(file: File, tipo: 'reverso'): void {
    this.modals['loadingModal'] = true;
    const formData = new FormData();
    formData.append('image', file);
    
    this.contratistaApiService.postFormData('api_convert_pdf_to_image/', formData).subscribe({
      next: (response) => {
        if (response.success && response.imagen_convertida) {
          this.reemplazarConImagenConvertida(response.imagen_convertida, tipo);
        }
        this.modals['loadingModal'] = false;
      },
      error: (error) => {
        console.error('Error convirtiendo PDF:', error);
        this.modals['loadingModal'] = false;
        alert('Error al convertir PDF.');
      }
    });
  }

  previewImage(file: File, tipo: 'frente' | 'reverso'): void {
    const reader = new FileReader();
    reader.onload = (e: any) => {
      if (tipo === 'frente') {
        this.previewCarnetFrente = e.target.result;
      } else {
        this.previewCarnetReverso = e.target.result;
      }
    };
    reader.readAsDataURL(file);
  }

  procesarOCR(file: File, tipo: 'frente' | 'reverso'): void {
    this.modals['loadingModal'] = true; // ✅ Mostrar loading
    const formData = new FormData();
    formData.append('image', file);
    
    this.contratistaApiService.postFormData('api_ocr_carnet/', formData).subscribe({
      next: (response) => {
        if (response.success && response.datos) {
          this.rellenarDatosOCR(response.datos);
          // Si el backend convirtió PDF a imagen
          if (response.imagen_convertida) {
            this.reemplazarConImagenConvertida(response.imagen_convertida, tipo);
          }
        }
        this.modals['loadingModal'] = false;
      },
      error: (error) => {
        console.error('Error en OCR:', error);
        this.modals['loadingModal'] = false;
        alert('Error al procesar el carnet. Complete los datos manualmente.');
      }
    });
  }

  reemplazarConImagenConvertida(base64Image: string, tipo: 'frente' | 'reverso'): void {
    // Convertir base64 a Blob
    const byteString = atob(base64Image);
    const ab = new ArrayBuffer(byteString.length);
    const ia = new Uint8Array(ab);
    for (let i = 0; i < byteString.length; i++) {
      ia[i] = byteString.charCodeAt(i);
    }
    const blob = new Blob([ab], { type: 'image/png' });
    
    // Convertir Blob a File
    const nombreArchivo = tipo === 'frente' ? 'carnet_frente.png' : 'carnet_reverso.png';
    const archivoConvertido = new File([blob], nombreArchivo, { type: 'image/png' });
    
    // Reemplazar archivo original
    if (tipo === 'frente') {
      this.imagenCarnetFrente = archivoConvertido;
      this.previewCarnetFrente = `data:image/png;base64,${base64Image}`;
    } else {
      this.imagenCarnetReverso = archivoConvertido;
      this.previewCarnetReverso = `data:image/png;base64,${base64Image}`;
    }
  }

  rellenarDatosOCR(datos: any): void {
    if (datos.nombres) this.nombres = datos.nombres;
    if (datos.apellidos) this.apellidos = datos.apellidos;
    if (datos.rut) {
      const rutLimpio = datos.rut.replace(/\./g, '').replace(/-/g, '');
      this.rut = this.formatearRUT(rutLimpio);
    }
    if (datos.sexo) {
      console.log('🔍 Sexo del OCR:', datos.sexo); // DEBUG
      this.sexo = datos.sexo;
    }
    if (datos.fecha_nacimiento) this.fechaNacimiento = datos.fecha_nacimiento;
    if (datos.nacionalidad) this.nacionalidad = datos.nacionalidad;
    
    console.log('🔍 Estado final - Sexo:', this.sexo); // DEBUG
  }

  formatearRUT(rut: string): string {
    // Eliminar puntos y guiones
    let rutLimpio = rut.replace(/\./g, '').replace(/-/g, '');
    
    if (rutLimpio.length > 1) {
      const body = rutLimpio.slice(0, -1);
      const dv = rutLimpio.slice(-1);
      
      // Agregar puntos cada 3 dígitos
      const bodyFormateado = body.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
      return `${bodyFormateado}-${dv}`;
    }
    return rutLimpio;
  }

  // Modificar onMetodoPagoChange():
  onMetodoPagoChange(): void {
    if (this.metodoPago === 'TRANSFERENCIA') {
      const bancoEstado = this.bancosCargados.find(b => 
        b.nombre.toUpperCase().includes('ESTADO')
      );
      
      if (bancoEstado) {
        this.banco = bancoEstado.id.toString();
      }
      
      this.tipoCuenta = 'CUENTA RUT'; // Cambiar a CUENTA RUT
      
      // Cuenta RUT = RUT sin guion, puntos NI dígito verificador
      if (this.rut) {
        const rutLimpio = this.rut.replace(/\./g, '').replace(/-/g, '');
        this.numeroCuenta = rutLimpio.slice(0, -1); // Quitar último dígito
      }
    }
  }

  onRutChange(): void {
    if (this.metodoPago === 'TRANSFERENCIA') {
      const rutLimpio = this.rut.replace(/\./g, '').replace(/-/g, '');
      this.numeroCuenta = rutLimpio.slice(0, -1); // Quitar último dígito
    }
  }







  get sociedadSeleccionadaNombre(): string {
    if (!this.selectedSociedadId) return 'SELECCIONAR SOCIEDAD';
    return this.sociedadesCargadas.find(s => s.id === this.selectedSociedadId)?.nombre || 'SELECCIONAR SOCIEDAD';
  }

  get folioSeleccionadoNombre(): string {
    if (!this.selectedFolioId) return 'SELECCIONAR FOLIO';
    return this.foliosCargados.find(s => s.id === this.selectedFolioId)?.nombre_cliente || 'SELECCIONAR FOLIO';
  }

  get fundoSeleccionadoNombre(): string {
    if (!this.selectedFundoId) return 'SELECCIONAR FUNDO';
    return this.fundosCargados.find(s => s.id === this.selectedFundoId)?.nombre || 'SELECCIONAR FUNDO';
  }

  get laborSeleccionadaNombre(): string {
    if (!this.selectedLaborId) return 'SELECCIONAR LABOR';
    return this.laboresCargadas.find(s => s.id === this.selectedLaborId)?.nombre || 'SELECCIONAR LABOR';
  }

  get horarioSeleccionadoNombre(): string {
    if (!this.selectedHorarioId) return 'SELECCIONAR HORARIO';
    return this.horariosCargados.find(s => s.id === this.selectedHorarioId)?.nombre || 'SELECCIONAR HORARIO';
  }

  get transportistaSeleccionadoNombre(): string {
    if (!this.selectedTransportistaId) return 'SELECCIONAR EMPRESA TRANSPORTISTA';
    return this.transportistasCargados.find(s => s.id === this.selectedTransportistaId)?.nombre || 'SELECCIONAR EMPRESA TRANSPORTISTA';
  }

  get vehiculoSeleccionadoNombre(): string {
    if (!this.selectedVehiculoId) return 'SELECCIONAR VEHÍCULO (Opcional)';
    const vehiculo = this.vehiculosCargados.find(v => v.id === this.selectedVehiculoId);
    return vehiculo ? `${vehiculo.ppu} - ${vehiculo.modelo}` : 'SELECCIONAR VEHÍCULO (Opcional)';
  }

  get casaSeleccionadaNombre(): string {
    if (!this.selectedCasaId) return 'SELECCIONAR CASA';
    return this.casasCargadas.find(s => s.id === this.selectedCasaId)?.nombre || 'SELECCIONAR CASA';
  }

  get supervisorSeleccionadoNombre(): string {
    if (!this.selectedSupervisorId) return 'SELECCIONAR SUPERVISOR';
    return this.supervisoresCargados.find(s => s.id === this.selectedSupervisorId)?.usuario_nombre || 'SELECCIONAR SUPERVISOR';
  }
  
  get bancoSeleccionadoNombre(): string {
  if (!this.banco) return 'SELECCIONAR BANCO';
  const bancoEncontrado = this.bancosCargados.find(b => b.id.toString() === this.banco);
  return bancoEncontrado?.nombre || 'SELECCIONAR BANCO';
}

  // Cambiar URL del endpoint:
  guardarTrabajador(): void {
    if (!this.validarFormulario()) {
      alert('Complete todos los campos obligatorios');
      return;
    }

    this.guardando = true;

    const formData = new FormData();
    
    formData.append('holding', this.holding.toString());
    formData.append('sociedad', this.selectedSociedadId!.toString());
    formData.append('folio', this.selectedFolioId!.toString());
    formData.append('fundo', this.selectedFundoId!.toString());
    formData.append('labor', this.selectedLaborId!.toString());
    formData.append('horario', this.selectedHorarioId!.toString());
    formData.append('casa', this.selectedCasaId!.toString());
    formData.append('codigo_supervisor', this.selectedSupervisorId!.toString());
    
    if (this.selectedTransportistaId) {
      formData.append('transportista', this.selectedTransportistaId.toString());
    }
    if (this.selectedVehiculoId) {
      formData.append('vehiculo', this.selectedVehiculoId.toString());
    }
    if (this.selectedJefeCuadrillaId) {
      formData.append('jefe_cuadrilla', this.selectedJefeCuadrillaId.toString());
    }
    
    formData.append('nombres', this.nombres.toUpperCase());
    formData.append('apellidos', this.apellidos.toUpperCase());
    
    if (this.tipoDocumento === 'CEDULA_CHILENA') {
      // Limpiar RUT: quitar puntos y guión
      const rutLimpio = this.rut.replace(/\./g, '').replace(/-/g, '');
      formData.append('rut', rutLimpio);
    } else {
      formData.append('dni', this.dni);
    }
    
    if (this.nic) formData.append('nic', this.nic);
    formData.append('sexo', this.sexo);
    formData.append('estado_civil', this.estadoCivil);
    formData.append('nacionalidad', this.nacionalidad.toUpperCase());
    
    const telefonoCompleto = `${this.telefonoPrefijo}${this.telefonoNumero}`;
    formData.append('telefono', telefonoCompleto);
    
    const correoCompleto = `${this.correoUsuario}@${this.correoDominio}`;
    formData.append('correo', correoCompleto.toLowerCase());
    
    formData.append('direccion', this.direccion.toUpperCase());
    formData.append('fecha_nacimiento', this.fechaNacimiento);
    
    formData.append('metodo_pago', this.metodoPago);
    if (this.metodoPago !== 'EFECTIVO') {
      formData.append('banco', this.banco);
      formData.append('tipo_cuenta_bancaria', this.tipoCuenta);
      formData.append('numero_cuenta', this.numeroCuenta);
    }
    
    formData.append('estado', 'true');
    
    if (this.imagenCarnetFrente) {
      formData.append('carnet_front_image', this.imagenCarnetFrente);
    }
    if (this.imagenCarnetReverso) {
      formData.append('carnet_back_image', this.imagenCarnetReverso);
    }

    this.contratistaApiService.postFormData('personal_trabajadores_mobile/', formData).subscribe({
      next: (response) => {
        alert('Trabajador enrolado exitosamente');
        this.resetearFormulario();
        this.pasoActual = 1;
        this.guardando = false;
      },
      error: (error) => {
        console.error('Error guardando trabajador:', error);
        alert('Error al guardar. Verifique los datos e intente nuevamente.');
        this.guardando = false;
      }
    });
  }

  validarFormulario(): boolean {
    return !!(
      this.nombres &&
      this.apellidos &&
      (this.rut || this.dni) &&
      this.sexo &&
      this.nacionalidad &&
      this.fechaNacimiento &&
      this.imagenCarnetFrente
    );
  }

  base64ToBlob(base64: string): Blob {
    const byteString = atob(base64.split(',')[1]);
    const mimeString = base64.split(',')[0].split(':')[1].split(';')[0];
    const ab = new ArrayBuffer(byteString.length);
    const ia = new Uint8Array(ab);
    for (let i = 0; i < byteString.length; i++) {
      ia[i] = byteString.charCodeAt(i);
    }
    return new Blob([ab], { type: mimeString });
  }

  resetearFormulario(): void {
    this.selectedSociedadId = null;
    this.selectedFolioId = null;
    this.selectedFundoId = null;
    this.selectedLaborId = null;
    this.selectedHorarioId = null;
    this.selectedTransportistaId = null;
    this.selectedVehiculoId = null;
    this.selectedCasaId = null;
    this.selectedSupervisorId = null;
    this.selectedJefeCuadrillaId = null;
    
    this.nombres = '';
    this.apellidos = '';
    this.rut = '';
    this.dni = '';
    this.nic = '';
    this.sexo = '';
    this.estadoCivil = 'SOLTERO(A)';
    this.nacionalidad = 'CHILENA';
    this.telefonoNumero = '';
    this.correoUsuario = '';
    this.correoDominio = 'gmail.com';
    this.direccion = '';
    this.fechaNacimiento = '';
    this.metodoPago = 'EFECTIVO';
    this.banco = '';
    this.tipoCuenta = '';
    this.numeroCuenta = '';
    this.imagenCarnetFrente = null;
    this.imagenCarnetReverso = null;
    this.previewCarnetFrente = null;
    this.previewCarnetReverso = null;
  }

  toggleDropdown(dropdown: string): void {
    this.dropdownStates[dropdown] = !this.dropdownStates[dropdown];
  }

  formatRUT(event: any): void {
    this.rut = this.formatearRUT(event.target.value);
    this.onRutChange();
  }

  volverSociedad(): void {
    this.pasoActual = 1;
  }
}