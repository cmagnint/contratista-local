import { Component, Inject, OnInit, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser, CommonModule } from '@angular/common';
import { ContratistaApiService } from '../../../../services/contratista-api.service';
import { ReactiveFormsModule } from '@angular/forms';
import { FormsModule } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';
import { MatIconModule } from '@angular/material/icon';
import { JwtService } from '../../../../services/jwt.service';

@Component({
  selector: 'app-personal',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    FormsModule,
    MatTableModule,
    MatIconModule,
  ],
  templateUrl: './personal.component.html',
  styleUrl: './personal.component.css'
})
export class PersonalComponent implements OnInit {
  
  constructor(
    private contratistaApiService: ContratistaApiService,
    private jwtService : JwtService,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {}

  public nacionalidadesFiltradas: string[] = [];
  public todasLasNacionalidades: string[] = [
      'AFGANA', 'ALBANESA', 'ALEMANA', 'ANDORRANA', 'ANGOLEÑA', 'ANTIGUANA', 'ÁRABE', 
      'ARGELINA', 'ARGENTINA', 'ARMENIA', 'AUSTRALIANA', 'AUSTRIACA', 'AZERBAIYANA', 
      'BAHAMEÑA', 'BANGLADESÍ', 'BARBADENSE', 'BAREINÍ', 'BELGA', 'BELICEÑA', 'BENINESA', 
      'BIELORRUSA', 'BIRMANA', 'BOLIVIANA', 'BOSNIA', 'BOTSWANA', 'BRASILEÑA', 'BRUNEANA', 
      'BÚLGARA', 'BURKINESA', 'BURUNDESA', 'BUTANESA', 'CABOVERDIANA', 'CAMBOYANA', 
      'CAMERUNESA', 'CANADIENSE', 'CHADIANA', 'CHILENA', 'CHINA', 'CHIPRIOTA', 'COLOMBIANA', 
      'COMORENSE', 'CONGOLEÑA', 'COSTARRICENSE', 'CROATA', 'CUBANA', 'DANESA', 'DOMINICANA',
      'ECUATORIANA', 'EGIPCIA', 'EMIRATÍ', 'ERITREA', 'ESLOVACA', 'ESLOVENA', 'ESPAÑOLA', 
      'ESTADOUNIDENSE', 'ESTONIA', 'ETÍOPE', 'FILIPINA', 'FINLANDESA', 'FRANCESA', 
      'GABONESA', 'GAMBIANA', 'GEORGIANA', 'GHANESA', 'GRANADINA', 'GRIEGA', 'GUATEMALTECA', 
      'GUINEANA', 'GUYANESA', 'HAITIANA', 'HONDUREÑA', 'HÚNGARA', 'INDIA', 'INDONESIA', 
      'IRANÍ', 'IRAQUÍ', 'IRLANDESA', 'ISLANDESA', 'ISRAELÍ', 'ITALIANA', 'JAMAICANA', 
      'JAPONESA', 'JORDANA', 'KAZAJA', 'KENIANA', 'KIRGUISA', 'KUWAITÍ', 'LAOSIANA', 
      'LESOTENSE', 'LETONA', 'LIBANESA', 'LIBERIANA', 'LIBIA', 'LIECHTENSTEINIANA', 
      'LITUANA', 'LUXEMBURGUESA', 'MACEDONIA', 'MALASIA', 'MALAVÍ', 'MALDIVA', 'MALIENSE', 
      'MALTESA', 'MARROQUÍ', 'MAURICIANA', 'MAURITANA', 'MEXICANA', 'MOLDAVA', 'MONEGASCA', 
      'MONGOLA', 'MONTENEGRINA', 'MOZAMBIQUEÑA', 'NAMIBIA', 'NEPALÍ', 'NICARAGÜENSE', 
      'NIGERINA', 'NIGERIANA', 'NORUEGA', 'NEOZELANDESA', 'OMÁNÍ', 'NEERLANDESA', 
      'PAKISTANÍ', 'PANAMEÑA', 'PAPÚ', 'PARAGUAYA', 'PERUANA', 'POLACA', 'PORTUGUESA', 
      'QATARÍ', 'RUANDESA', 'RUMANA', 'RUSA', 'SAMOANA', 'SALVADOREÑA', 'SANMARINENSE', 
      'SAUDÍ', 'SENEGALESA', 'SERBIA', 'SEYCHELLENSE', 'SIERRALEONESA', 'SINGAPURENSE', 
      'SIRIA', 'SOMALÍ', 'SUAZI', 'SUDAFRICANA', 'SUDANESA', 'SUECA', 'SUIZA', 'SURINAMESA', 
      'TAILANDESA', 'TAIWANESA', 'TANZANA', 'TAYIKA', 'TIMORENSE', 'TOGOLESA', 'TONGANA', 
      'TRINITENSE', 'TUNECINA', 'TURCA', 'TURKMÉNA', 'UCRANIANA', 'UGANDESA', 'URUGUAYA', 
      'UZBEKA', 'VANUATUENSE', 'VATICANA', 'VENEZOLANA', 'VIETNAMITA', 'YEMENÍ', 'YIBUTIANA', 
      'ZAMBIANA', 'ZIMBABUENSE'
  ];

  public modals: { [key: string]: boolean } = {
    exitoModal: false,
    errorModal: false,
    crearTrabajador: false,
    modificarTrabajador: false,
    holdingModal: false,
    sociedadesModal: false,
    camposModal: false,
    areasModal: false,
    cargosModal: false,
    afpModal: false,
    saludModal: false,
    bancosModal: false,
    confirmacionModal: false,
    bancoInfoModal: false,
    documentosModal: false,
  };

  public trabajadorSeleccionado: any = {
    nombre_trabajador_seleccionado : '',
    rut_trabajador_seleccionado : '',
    direccion_trabajador_seleccionado : '',
    fecha_ingreso_trabajador_seleccionado : Date,
    id_trabajador_seleccionado : 0,
    id_sociedad_trabajador_seleccionado : 0,
    id_cargo_trabajador_seleccionado : 0,
    id_area_trabajador_seleccionado : 0 ,
    id_salud_trabajador_seleccionado : 0,
    id_afp_trabajador_seleccionado : 0,
  }

  public holding: string = '';
  public nombresTrabajador: string | null = null;
  public apellidosTrabajador:  string | null = null;
  public rutTrabajador: string | null = null;
  public correoTrabajador: string | null = null;
  public direccionTrabajador: string | null = null;
  public fechaTrabajador : Date | null = null;
  public sexoTrabajador: string = '';
  public telefonoTrabajador: string | null = null;
  public metodoPago: string | null = null;;
  public banco: string | null = null;
  public tipoCuenta: string | null = null;
  public numeroCuenta: string | null = null;
  public nacionalidadTrabajador: string = 'CHILENA';
  public fechaIngreso: string | null = null;
  public fechaNacimiento: string | null = null;
  public estadoCivil: string = 'SOLTERO(A)';

  public correoTrabajadorNew: string = '';
  public direccionTrabajadorNew: string = '';
  public sexoTrabajadorNew: string = '';
  public telefonoTrabajadorNew: string = '';
  public fechaIngresoNew: string = '';
  public metodoPagoNew: string | null = null;
  public bancoNew: string = '';
  public tipoCuentaNew: string = '';
  public numeroCuentaNew: string = '';
  public nacionalidadTrabajadorNew: string = 'CHILENA';
  public fechaNacimientoNew: string | null = null;
  public estadoCivilNew: string = '';

  public sociedadesCargadas: any[] = []
  public selectedSociedadId: number | null = null;
  
  public areasCargadas: any[] = []
  public selectedAreaId: number | null = null;

  public cargosCargados: any[] = []
  public selectedCargoId: number | null = null;

  public afpCargadas: any[] = []
  public selectedAfpId: number | null = null;

  public saludCargadas: any[] = []
  public selectedSaludId: number | null = null;

  public bancosCargados: any[] = []
  public selectedBancoId: number | null = null;

  public trabajadorSeleccionadoBanco: any = null;
  public trabajadorSeleccionadoDocs: any = null;

  public dniTrabajador: string | null = null;
  public nicTrabajador: string | null = null;
  public dniTrabajadorNew: string = '';
  public nicTrabajadorNew: string = '';

  // Nuevas propiedades para subir documentos
  public archivoCarnetFrontal: File | null = null;
  public archivoCarnetTrasero: File | null = null;
  public archivoFirma: File | null = null;
  
  public nombreArchivoFrontal: string = '';
  public nombreArchivoTrasero: string = '';
  public nombreArchivoFirma: string = '';

  errorMessage!: string;
  selectedRows: any[] = [];
  
  public dropdownStates = {
    sociedades: false,
    areas: false,
    cargos: false,
    afps: false,
    salud: false,
    bancos: false,
    casas: false,
    fundos: false,
  };

  public todasSeleccionadas: boolean = false;
  public trabajadoresCargados: any[] = [];
  columnasDesplegadas = [
    'codigo', 'sociedad', 'area', 'cargo', 'nombre', 'apellidos', 'rut', 'dni', 'nic',
    'direccion', 'sexo', 'telefono', 'nacionalidad', 'correo', 
    'fecha_ingreso', 'fecha_nacimiento', 'estado_civil', 'afp', 'salud', 
    'metodo_pago', 'banco_info', 'documentos', 'estado'
  ];
  
  public nombreTrabajadorNew: string = '';
  public rutTrabajadorNew: string = '';
  public emailTrabajadorNew: string = '';
  public deletedRow: any[] = [];
  public selectedTrabajadorId: number | null = null;

  ngOnInit():void {
    if (isPlatformBrowser(this.platformId)) {
      this.holding = this.getHoldingIdFromJWT(); 
      this.cargarTrabajadores();
      this.cargarSociedades();
      this.cargarAreas();
      this.cargarCargos();
      this.cargaAfp();
      this.cargarSalud();
      this.cargarBancos();
      this.setDefaultFechaCelebracion();
      this.nacionalidadesFiltradas = [...this.todasLasNacionalidades];
    }
  }

  tieneImagenReal(path: string): boolean {
    if (!path) return false;
    if (path.includes('dni.jpg')) return false;
    return true;
  }
  
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

  setDefaultFechaCelebracion(): void {
    const today = new Date();
    const day = String(today.getDate()).padStart(2, '0');
    const month = String(today.getMonth() + 1).padStart(2, '0');
    const year = today.getFullYear();
    this.fechaIngreso = `${year}-${month}-${day}`;
  }

  cargarSociedades(): void {
    this.contratistaApiService.get(`api_sociedad/?holding=${this.holding}`).subscribe({
      next: (response) => {
        if(response.length > 0) {
          this.sociedadesCargadas = response;
        } else {
          console.log('No se encontraron sociedades');
        }
      }, 
      error: (error) => {
        console.error('Error al recibir las sociedades:', error);
      }
    });
  }

  cargarAreas():void{
    this.contratistaApiService.get(`api_areas_administracion/?holding=${this.holding}`).subscribe({
      next: (response) => {
        this.areasCargadas = response;
      },
      error: (error) => {
        console.error('Error al recibir las areas:', error);
      }
    });
  }

  cargarCargos(): void {
    this.contratistaApiService.get(`api_cargos_administracion/?holding=${this.holding}`).subscribe({
      next: (response) => {
        this.cargosCargados = response; 
        if (response.length === 0) {
          this.selectedRows = [];
        }
      },
      error: (error) => {
        this.openModal('errorModal');
      }
    });
  }

  cargaAfp(): void {
    this.contratistaApiService.get(`api_afp_trabajadores/?holding=${this.holding}`).subscribe({
      next: (response) => {
        this.afpCargadas = response;
        if (response.length === 0) {
          this.selectedRows = [];
        }
      },
      error: (error) => {
        this.openModal('errorModal');
      }
    });
  }

  cargarSalud(): void {
    this.contratistaApiService.get(`api_salud_trabajadores/?holding=${this.holding}`).subscribe({
      next: (response) => {
        this.saludCargadas = response;
        if (response.length === 0) {
          this.selectedRows = [];
        }
      },
      error: (error) => {
        this.openModal('errorModal');
      }
    });
  }

  cargarBancos(): void {
    this.contratistaApiService.get('api_bancos/').subscribe({
      next: (response) => {
        this.bancosCargados = response;
      },
      error: (error) => {
        console.error('Error al cargar bancos:', error);
        this.openModal('errorModal');
      }
    });
  }

  cargarTrabajadores():void{
  this.contratistaApiService.get(`api_personal/?holding=${this.holding}`).subscribe({
    next: (response) => {
      this.trabajadoresCargados = response.sort((a: any, b: any) => {
        const apellidoA = (a.apellidos || '').toUpperCase();
        const apellidoB = (b.apellidos || '').toUpperCase();
        
        if (apellidoA < apellidoB) return -1;
        if (apellidoA > apellidoB) return 1;
        
        const nombreA = (a.nombres || '').toUpperCase();
        const nombreB = (b.nombres || '').toUpperCase();
        
        if (nombreA < nombreB) return -1;
        if (nombreA > nombreB) return 1;
        
        return 0;
      });
      
      console.log('Trabajadores cargados y ordenados:', this.trabajadoresCargados);
    },
    error: (error) => {
      console.error('Error al recibir los trabajadores:', error);
    }
  });
}

  crearTrabajador(): void {
    let data = {
      holding: this.holding,
      nombres: this.nombresTrabajador,
      apellidos: this.apellidosTrabajador,
      rut: this.rutTrabajador!.replace(/[\.\-]/g, ''),
      dni: this.dniTrabajador,
      nic: this.nicTrabajador,
      correo: this.correoTrabajador,
      direccion: this.direccionTrabajador,
      sexo: this.sexoTrabajador,
      telefono: this.telefonoTrabajador,
      nacionalidad: this.nacionalidadTrabajador,
      sociedad: this.selectedSociedadId,
      area: this.selectedAreaId,
      cargo: this.selectedCargoId,
      afp: this.selectedAfpId,
      salud: this.selectedSaludId,
      metodo_pago: this.metodoPago,
      fecha_ingreso: this.fechaIngreso,
      banco: this.selectedBancoId,
      tipo_cuenta_bancaria: this.tipoCuenta,
      numero_cuenta: this.numeroCuenta,
      fecha_nacimiento: this.fechaNacimiento,
      estado_civil: this.estadoCivil
    }
    
    this.contratistaApiService.post('api_personal/', data).subscribe({
      next: (response) => {
        this.closeModal('crearTrabajador');
        this.cargarTrabajadores();
        this.limpiarFormularioCreacion();
        this.openModal('exitoModal');
      }, 
      error: (error) => {
        this.openModal('errorModal')
      }
    });
  }

  modificarTrabajador(): void {
    const data = {
      id: this.selectedTrabajadorId,
      holding: this.holding,
      nombres: this.nombreTrabajadorNew,
      rut: this.rutTrabajadorNew.replace(/[\.\-]/g, ''),
      dni: this.dniTrabajadorNew,
      nic: this.nicTrabajadorNew,
      correo: this.correoTrabajadorNew,
      direccion: this.direccionTrabajadorNew,
      sexo: this.sexoTrabajadorNew,
      telefono: this.telefonoTrabajadorNew,
      nacionalidad: this.nacionalidadTrabajadorNew,
      sociedad: this.selectedSociedadId,
      area: this.selectedAreaId,
      cargo: this.selectedCargoId,
      afp: this.selectedAfpId,
      salud: this.selectedSaludId,
      fecha_ingreso: this.fechaIngresoNew,
      metodo_pago: this.metodoPagoNew,
      banco: this.selectedBancoId,
      tipo_cuenta_bancaria: this.tipoCuentaNew,
      numero_cuenta: this.numeroCuentaNew,
      fecha_nacimiento: this.fechaNacimientoNew,
      estado_civil: this.estadoCivilNew
    };
  
    this.contratistaApiService.put('api_personal/', data).subscribe({
      next: (response) => {
        this.closeModal('modificarTrabajador');
        this.cargarTrabajadores();
        this.openModal('exitoModal');
        this.limpiarFormularioModificacion();
      },
      error: (error) => {
        console.error('Error:', error);
        this.openModal('errorModal');
      }
    });
  }

  eliminarTrabajadoresSeleccionados(): void {
    if (this.deletedRow.length > 0) {
        const idsToDelete = this.deletedRow.map(row => row.id);
        this.contratistaApiService.delete('api_personal/', {ids: idsToDelete}).subscribe({
            next: () => {
                this.closeModal('confirmacionModal')
                this.cargarTrabajadores();
                this.openModal('exitoModal');
                this.deletedRow = [];
            },
            error: (error) => {
                this.openModal('errorModal');
                console.error('Error al eliminar trabajadores:', error);
            }
        });
    }
  }

  // NUEVOS MÉTODOS PARA SUBIR DOCUMENTOS
  onFileSelected(event: Event, tipo: 'frontal' | 'trasero' | 'firma'): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      const file = input.files[0];
      
      // Validar tipo de archivo
      const tiposPermitidos = ['image/jpeg', 'image/jpg', 'image/png'];
      if (!tiposPermitidos.includes(file.type)) {
        alert('Solo se permiten archivos JPG, JPEG o PNG');
        input.value = '';
        return;
      }
      
      // Validar tamaño (máx 5MB)
      if (file.size > 5 * 1024 * 1024) {
        alert('El archivo no debe superar 5MB');
        input.value = '';
        return;
      }
      
      switch(tipo) {
        case 'frontal':
          this.archivoCarnetFrontal = file;
          this.nombreArchivoFrontal = file.name;
          break;
        case 'trasero':
          this.archivoCarnetTrasero = file;
          this.nombreArchivoTrasero = file.name;
          break;
        case 'firma':
          this.archivoFirma = file;
          this.nombreArchivoFirma = file.name;
          break;
      }
    }
  }

  subirDocumentos(): void {
    if (!this.trabajadorSeleccionadoDocs) {
      alert('No hay trabajador seleccionado');
      return;
    }

    if (!this.archivoCarnetFrontal && !this.archivoCarnetTrasero && !this.archivoFirma) {
      alert('Debe seleccionar al menos un documento');
      return;
    }

    console.log('📤 Iniciando subida de documentos...');
    console.log('👤 Trabajador ID:', this.trabajadorSeleccionadoDocs.id);

    const formData = new FormData();
    
    if (this.archivoCarnetFrontal) {
      console.log('✅ Agregando carnet frontal:', this.archivoCarnetFrontal.name);
      formData.append('carnet_front_image', this.archivoCarnetFrontal, this.archivoCarnetFrontal.name);
    }
    if (this.archivoCarnetTrasero) {
      console.log('✅ Agregando carnet trasero:', this.archivoCarnetTrasero.name);
      formData.append('carnet_back_image', this.archivoCarnetTrasero, this.archivoCarnetTrasero.name);
    }
    if (this.archivoFirma) {
      console.log('✅ Agregando firma:', this.archivoFirma.name);
      formData.append('firma', this.archivoFirma, this.archivoFirma.name);
    }

    console.log('📦 Enviando FormData...');

    this.contratistaApiService.patchFormData(
      `api_personal_documentos/${this.trabajadorSeleccionadoDocs.id}/`,
      formData
    ).subscribe({
      next: (response: any) => {
        console.log('✅ Respuesta exitosa:', response);
        this.cargarTrabajadores();
        this.trabajadorSeleccionadoDocs = response;
        this.limpiarArchivosSeleccionados();
        this.closeModal('documentosModal');
        this.openModal('exitoModal');
      },
      error: (error) => {
        console.error('❌ Error completo:', error);
        console.error('❌ Status:', error.status);
        console.error('❌ Detalle:', error.error);
        
        this.errorMessage = error.error?.detail || error.error?.error || 'Error al subir documentos';
        this.openModal('errorModal');
      }
    });
  }

  limpiarArchivosSeleccionados(): void {
    this.archivoCarnetFrontal = null;
    this.archivoCarnetTrasero = null;
    this.archivoFirma = null;
    this.nombreArchivoFrontal = '';
    this.nombreArchivoTrasero = '';
    this.nombreArchivoFirma = '';
  }
  // FIN NUEVOS MÉTODOS

  toggleSelection(id: number, list: number[], total: any[]): void {
    const index = list.indexOf(id);
    if (index > -1) {
      list.splice(index, 1);
    } else {
      list.push(id);
    }
    if (list.length === total.length) {
      this.todasSeleccionadas = true;
    } else {
      this.todasSeleccionadas = false;
    }
  }

  toggleSelectionSociedad(sociedadId: number): void {
    if (this.selectedSociedadId === sociedadId) {
      this.selectedSociedadId = null;
    } else {
      this.selectedSociedadId = sociedadId;
    }
  }

  toggleSelectionArea(areaId: number): void {
    if (this.selectedAreaId === areaId) {
      this.selectedAreaId = null;
    } else {
      this.selectedAreaId = areaId;
    }
  }

  toggleSelectionCargo(cargoId: number): void {
    if (this.selectedCargoId === cargoId) {
      this.selectedCargoId = null;
    } else {
      this.selectedCargoId = cargoId;
    }
  }

  toggleSelectionAFP(afpId: number): void {
    if (this.selectedAfpId === afpId) {
      this.selectedAfpId = null;
    } else {
      this.selectedAfpId = afpId;
    }
  }

  toggleSelectionSalud(saludId: number): void {
    if (this.selectedSaludId === saludId) {
      this.selectedSaludId = null;
    } else {
      this.selectedSaludId = saludId;
    }
  }

  toggleSelectionBanco(bancoId: number): void {
    if (this.selectedBancoId === bancoId) {
      this.selectedBancoId = null;
    } else {
      this.selectedBancoId = bancoId;
    }
  }

  getNombreSociedadSeleccionada(): string {
    if (this.selectedSociedadId) {
      const sociedad = this.sociedadesCargadas.find(s => s.id === this.selectedSociedadId);
      return sociedad ? sociedad.nombre : '';
    }
    return '';
  }

  getNombreAreaSeleccionada(): string {
    if (this.selectedAreaId) {
      const area = this.areasCargadas.find(a => a.id === this.selectedAreaId);
      return area ? area.nombre : '';
    }
    return '';
  }

  getNombreCargoSeleccionado(): string {
    if (this.selectedCargoId) {
      const cargo = this.cargosCargados.find(c => c.id === this.selectedCargoId);
      return cargo ? cargo.nombre : '';
    }
    return '';
  }

  getNombreAfpSeleccionada(): string {
    if (this.selectedAfpId) {
      const afp = this.afpCargadas.find(a => a.id === this.selectedAfpId);
      return afp ? afp.nombre : '';
    }
    return '';
  }

  getNombreSaludSeleccionada(): string {
    if (this.selectedSaludId) {
      const salud = this.saludCargadas.find(s => s.id === this.selectedSaludId);
      return salud ? salud.nombre : '';
    }
    return '';
  }

  getNombreBancoSeleccionado(): string {
    if (this.selectedBancoId) {
      const banco = this.bancosCargados.find(b => b.id === this.selectedBancoId);
      return banco ? `${banco.nombre} (${banco.codigo_sbif})` : '';
    }
    return '';
  }

  isSelected(row: any): boolean {
    return this.selectedRows.some(r => r.id === row.id);
  }

  formatRUT(event: Event): void {
    const target = event.target as HTMLInputElement;
    if (!target) return;

    // ✅ Permite K/k además de números
    let rut = target.value.replace(/[^0-9kK]/g, '').toUpperCase();
    
    if (rut.length === 0) {
      target.value = '';
      return;
    }
    
    const verifier = rut.slice(-1);
    let body = rut.slice(0, -1);
    
    if (body.length === 0) {
      target.value = verifier;
      return;
    }
    
    const parts: string[] = [];
    while (body.length > 3) {
      parts.unshift(body.slice(-3));
      body = body.slice(0, -3);
    }
    if (body.length > 0) {
      parts.unshift(body);
    }
    
    target.value = parts.join('.') + '-' + verifier;
  }

  validateNumber(event: KeyboardEvent) {
    const pattern = /[0-9]/;
    const inputChar = String.fromCharCode(event.charCode);

    if (!pattern.test(inputChar)) {
      event.preventDefault();
    }
  }
  
  formatRUTString(value: string): string {
    let rut = value.replace(/\D/g, '');
    let parts = [];
    const verifier = rut.slice(-1);
    rut = rut.slice(0, -1);
    while (rut.length > 3) {
        parts.unshift(rut.slice(-3));
        rut = rut.slice(0, -3);
    }
    parts.unshift(rut);
    return parts.join('.') + '-' + verifier;
  }

  toggleDropdown(dropdownName: string) {
    Object.keys(this.dropdownStates).forEach(key => {
      if (key !== dropdownName) {
        this.dropdownStates[key as keyof typeof this.dropdownStates] = false;
      }
    });
    this.dropdownStates[dropdownName as keyof typeof this.dropdownStates] = 
      !this.dropdownStates[dropdownName as keyof typeof this.dropdownStates];
  }

  deseleccionarFila(event: MouseEvent) {
    this.selectedRows = [];
  }

  onMetodoPagoChange(event: Event): void {
    const selectElement = event.target as HTMLSelectElement;
    this.metodoPago = selectElement.value;
  }

  onMetodoPagoChangeModificar(event: Event): void {
    const selectElement = event.target as HTMLSelectElement;
    this.metodoPagoNew = selectElement.value;
  }

  openModal(key: string): void {
    this.modals[key] = true;
    if(key== 'confirmacionModal'){
      this.deletedRow = this.selectedRows;
    }
  }

  closeModal(key: string): void {
    this.modals[key] = false;
    if (key === 'exitoModal') {
      this.cargarTrabajadores();  
    }
    if (key === 'documentosModal') {
      this.limpiarArchivosSeleccionados();
    }
  }

  abrirModalBanco(trabajador: any): void {
    this.trabajadorSeleccionadoBanco = trabajador;
    this.openModal('bancoInfoModal');
  }

  abrirModalDocumentos(trabajador: any): void {
    this.trabajadorSeleccionadoDocs = trabajador;
    console.log('Documentos del trabajador:', {
      carnet_front: trabajador.carnet_front_image,
      carnet_back: trabajador.carnet_back_image,
      firma: trabajador.firma
    });
    this.openModal('documentosModal');
  }

  descargarDocumento(url: string, nombreArchivo: string): void {
    if (!url) {
      alert('No hay documento disponible');
      return;
    }
    
    const link = document.createElement('a');
    link.href = url;
    link.download = nombreArchivo;
    link.target = '_blank';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }
  //IMPORTANTE, Para contratista-docker-cloud usar baseUrl : http://contratista.terramobile.cl
  //Para contratista usar http://localhost
  
  getUrlCompleta(path: string): string {
    if (!path) return '';
    
    if (path.startsWith('http')) {
      return path;
    }
    
    const baseUrl = 'http://localhost:8182';
    return `${baseUrl}${path}`;
  }

  onImageError(event: any): void {
    event.target.src = 'assets/no-image.png';
    console.error('Error cargando imagen');
  }

  selectRow(row: any): void {
    const index = this.selectedRows.findIndex(selectedRow => selectedRow.id === row.id);
    if (index > -1) {
      this.selectedRows.splice(index, 1);
    } else {
      this.selectedRows.push(row);
    }

    if (this.selectedRows.length === 1) {
      const selectedRow = this.selectedRows[0];
      this.selectedTrabajadorId = selectedRow.id;
      
      this.nombreTrabajadorNew = selectedRow.nombres;
      this.rutTrabajadorNew = this.formatRUTString(selectedRow.rut);
      this.dniTrabajadorNew = selectedRow.dni || '';
      this.nicTrabajadorNew = selectedRow.nic || '';
      this.correoTrabajadorNew = selectedRow.correo;
      this.direccionTrabajadorNew = selectedRow.direccion;
      this.sexoTrabajadorNew = selectedRow.sexo;
      this.telefonoTrabajadorNew = selectedRow.telefono;
      this.nacionalidadTrabajadorNew = selectedRow.nacionalidad;
      this.fechaIngresoNew = selectedRow.fecha_ingreso;
      this.fechaNacimientoNew = selectedRow.fecha_nacimiento;
      this.estadoCivilNew = selectedRow.estado_civil;
      
      this.metodoPagoNew = selectedRow.metodo_pago;
      this.tipoCuentaNew = selectedRow.tipo_cuenta_bancaria;
      this.numeroCuentaNew = selectedRow.numero_cuenta;
      
      this.selectedSociedadId = selectedRow.sociedad;
      this.selectedAreaId = selectedRow.area;
      this.selectedCargoId = selectedRow.cargo;
      this.selectedAfpId = selectedRow.afp;
      this.selectedSaludId = selectedRow.salud;
      this.selectedBancoId = selectedRow.banco;
      // Normalizar método de pago
      if (this.metodoPagoNew?.toUpperCase() === 'TRANSFERENCIA') {
        this.metodoPagoNew = 'Transferencia';
      } else if (this.metodoPagoNew?.toUpperCase() === 'EFECTIVO') {
        this.metodoPagoNew = 'Efectivo';
      } else if (this.metodoPagoNew?.toUpperCase() === 'SIN PAGO') {
        this.metodoPagoNew = 'Sin Pago';
      }
    }
  }

  limpiarFormularioModificacion(): void {
    this.nombreTrabajadorNew = '';
    this.rutTrabajadorNew = '';
    this.dniTrabajadorNew = '';
    this.nicTrabajadorNew = '';
    this.correoTrabajadorNew = '';
    this.direccionTrabajadorNew = '';
    this.sexoTrabajadorNew = '';
    this.telefonoTrabajadorNew = '';
    this.nacionalidadTrabajadorNew = 'CHILENA';
    this.fechaIngresoNew = '';
    this.fechaNacimientoNew = '';
    this.estadoCivilNew = '';
    this.metodoPagoNew = '';
    this.tipoCuentaNew = '';
    this.numeroCuentaNew = '';
    
    this.selectedSociedadId = null;
    this.selectedAreaId = null;
    this.selectedCargoId = null;
    this.selectedAfpId = null;
    this.selectedSaludId = null;
    this.selectedBancoId = null;
    
    Object.keys(this.dropdownStates).forEach(key => {
      this.dropdownStates[key as keyof typeof this.dropdownStates] = false;
    });
  }

  limpiarFormularioCreacion(): void {
    this.nombresTrabajador = null;
    this.apellidosTrabajador = null;
    this.rutTrabajador = null;
    this.dniTrabajador = null;
    this.nicTrabajador = null;
    this.correoTrabajador = null;
    this.direccionTrabajador = null;
    this.sexoTrabajador = 'H';
    this.telefonoTrabajador = null;
    this.nacionalidadTrabajador = 'CHILENA';
    this.fechaNacimiento = null;
    this.estadoCivil = 'SOLTERO(A)';
    this.selectedSociedadId = null;
    this.selectedAreaId = null;
    this.selectedCargoId = null;
    this.selectedAfpId = null;
    this.selectedSaludId = null;
    this.selectedBancoId = null;
    this.metodoPago = 'Sin Pago';
    this.banco = null;
    this.tipoCuenta = null;
    this.numeroCuenta = null;
    
    this.setDefaultFechaCelebracion();
    
    Object.keys(this.dropdownStates).forEach(key => {
      this.dropdownStates[key as keyof typeof this.dropdownStates] = false;
    });
  }
}