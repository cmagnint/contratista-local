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
  //VARIABLES

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

  // Booleanos para abrir o cerrar ventanas
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
  };

  //Perfil seleccionado
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

  public holding: string = ''; //Variable para guardar el ID del holding al cual pertenece al adminitrador
  public nombresTrabajador: string | null = null;
  public apellidosTrabajador:  string | null = null;
  public rutTrabajador: string | null = null;
  public correoTrabajador: string | null = null;
  public direccionTrabajador: string | null = null;
  public fechaTrabajador : Date | null = null;
  public sexoTrabajador: string = 'Hombre';
  public telefonoTrabajador: string | null = null;
  public metodoPago: string = 'Sin Pago';
  public banco: string | null = null;
  public tipoCuenta: string | null = null;
  public numeroCuenta: string | null = null;

  // Variables para modificación
  correoTrabajadorNew: string = '';
  direccionTrabajadorNew: string = '';
  sexoTrabajadorNew: string = '';
  telefonoTrabajadorNew: string = '';
  fechaIngresoNew: string = '';
  metodoPagoNew: string = '';
  bancoNew: string = '';
  tipoCuentaNew: string = '';
  numeroCuentaNew: string = '';
  public nacionalidadTrabajador: string = 'CHILENA';
  public nacionalidadTrabajadorNew: string = 'CHILENA';

  //SOCIEDADES CARGADAS
  public sociedadesCargadas: any[] = []
  public selectedSociedadId: number | null = null;
  
  //AREAS CARGADAS
  public areasCargadas: any[] = []
  public selectedAreaId: number | null = null;

  //CARGOS CARGADOS
  public cargosCargados: any[] = []
  public selectedCargoId: number | null = null;

  //AFP CARGADOS
  public afpCargadas: any[] = []
  public selectedAfpId: number | null = null;

  //SALUD CARGADOS
  public saludCargadas: any[] = []
  public selectedSaludId: number | null = null;

  //BANCOS CARGADOS
  public bancosCargados: any[] = []
  public selectedBancoId: number | null = null;
  
  public fechaIngreso: string | null = null;

  errorMessage!: string; //Variable usada para mostrar los mensajes de error de la API
  selectedRows: any[] = []; //Array usado para guardar las filas seleccionadas
  
  public dropdownStates = {
    sociedades: false,
    areas: false,
    cargos: false,
    afps: false,
    salud: false,
    bancos: false,
  };

  public todasSeleccionadas: boolean = false; //Booleano para seleccionar todas/ninguna casilla
  public trabajadoresCargados: any[] = [];
  columnasDesplegadas = ['codigo','sociedad','area','cargo','nombre','rut','direccion',
    'sexo','telefono','nacionalidad','correo','fecha_ingreso','afp','salud','metodo_pago', 'estado'];
  
  public nombreTrabajadorNew: string = '';
  public rutTrabajadorNew: string = '';
  public emailTrabajadorNew: string = '';
  public deletedRow: any[] = [];
  
  //TESTING 

  //------------------------------------------------------------//
  public selectedTrabajadorId: number | null = null; //GUARDA EL ID DEL TRABAJADOR DE LA FILA SELECCIONADA

  //FUNCIONES
  
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

  //CARGAR SOCIEDADES
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
        console.log(this.areasCargadas);
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
        console.log('Bancos cargados:', this.bancosCargados);
      },
      error: (error) => {
        console.error('Error al cargar bancos:', error);
        this.openModal('errorModal');
      }
    });
  }

//----------------------------------------------------------------------------//

  //FUNCIONES CRUD DEL MODULO

  crearTrabajador(): void {
  let data = {
    holding: this.holding,
    nombres: this.nombresTrabajador,
    apellidos: this.apellidosTrabajador,
    rut: this.rutTrabajador!.replace(/[\.\-]/g, ''),
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
    numero_cuenta: this.numeroCuenta
  }
  
  this.contratistaApiService.post('api_personal/', data).subscribe({
    next: (response) => {
      this.closeModal('crearTrabajador');
      this.cargarTrabajadores();
      this.limpiarFormularioCreacion(); // 🎯 AGREGAMOS LA LIMPIEZA DEL FORMULARIO
      this.openModal('exitoModal');
    }, 
    error: (error) => {
      this.openModal('errorModal')
    }
  });
}

  onMetodoPagoChange(event: Event): void {
    const selectElement = event.target as HTMLSelectElement;
    this.metodoPago = selectElement.value;
  }

  cargarTrabajadores():void{
    this.contratistaApiService.get(`api_personal/?holding=${this.holding}`).subscribe({
      next: (response) => {
        this.trabajadoresCargados = response;
        
      },
      error: (error) => {
        console.error('Error al recibir los trabajadores:', error);
        
      }
    });
  }

  modificarTrabajador(): void {
    const data = {
      id: this.selectedTrabajadorId,
      holding: this.holding,
      nombres: this.nombreTrabajadorNew,
      rut: this.rutTrabajadorNew.replace(/[\.\-]/g, ''),
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
      numero_cuenta: this.numeroCuentaNew
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
                this.deletedRow = []; // Limpiar la selección después de eliminar
            },
            error: (error) => {
                this.openModal('errorModal');
                console.error('Error al eliminar trabajadores:', error);
            }
        });
    }
  }

  toggleSelection(id: number, list: number[], total: any[]): void {
    const index = list.indexOf(id);
    if (index > -1) {
      list.splice(index, 1); // Deseleccionar
    } else {
      list.push(id); // Seleccionar
    }
    // Esta parte comprueba si todas las opciones están seleccionadas para ajustar la casilla "Seleccionar Todas"
    if (list.length === total.length) {
      // Si todas las opciones individuales están seleccionadas
      this.todasSeleccionadas = true;
    } else {
      // Si al menos una opción individual no está seleccionada
      this.todasSeleccionadas = false;
    }
  }

  toggleSelectionSociedad(sociedadId: number): void {
    if (this.selectedSociedadId === sociedadId) {
      this.selectedSociedadId = null;  // Deseleccionar si el mismo perfil es clickeado nuevamente
    } else {
      this.selectedSociedadId = sociedadId;  // Seleccionar el nuevo perfil
    }
  }

  toggleSelectionArea(areaId: number): void {
    if (this.selectedAreaId === areaId) {
      this.selectedAreaId = null;  // Deseleccionar si el mismo perfil es clickeado nuevamente
    } else {
      this.selectedAreaId = areaId;  // Seleccionar el nuevo perfil
    }
  }

  toggleSelectionCargo(cargoId: number): void {
    if (this.selectedCargoId === cargoId) {
      this.selectedCargoId = null;  // Deseleccionar si el mismo perfil es clickeado nuevamente
    } else {
      this.selectedCargoId = cargoId;  // Seleccionar el nuevo perfil
    }
  }

  toggleSelectionAFP(afpId: number): void {
    if (this.selectedAfpId === afpId) {
      this.selectedAfpId = null;  // Deseleccionar si el mismo perfil es clickeado nuevamente
    } else {
      this.selectedAfpId = afpId;  // Seleccionar el nuevo perfil
    }
  }

  toggleSelectionSalud(saludId: number): void {
    if (this.selectedSaludId === saludId) {
      this.selectedSaludId = null;  // Deseleccionar si el mismo perfil es clickeado nuevamente
    } else {
      this.selectedSaludId = saludId;  // Seleccionar el nuevo perfil
    }
  }

  toggleSelectionBanco(bancoId: number): void {
    if (this.selectedBancoId === bancoId) {
      this.selectedBancoId = null;  // Deseleccionar si el mismo banco es clickeado nuevamente
    } else {
      this.selectedBancoId = bancoId;  // Seleccionar el nuevo banco
    }
  }

  isSelected(row: any): boolean {
    return this.selectedRows.some(r => r.id === row.id);
  }


  formatRUT(event: Event): void {
    const target = event.target as HTMLInputElement; // Casting seguro
    if (!target) return; // Verificar que realmente existe un target

    let rut = target.value.replace(/\D/g, '');
    let parts = [];
    const verifier = rut.slice(-1);
    rut = rut.slice(0, -1);
    while (rut.length > 3) {
        parts.unshift(rut.slice(-3));
        rut = rut.slice(0, -3);
    }
    parts.unshift(rut);
    target.value = parts.join('.') + '-' + verifier;
    if (target.value === '-') {
        target.value = '';
    }
  }

  validateNumber(event: KeyboardEvent) {
    const pattern = /[0-9]/;
    const inputChar = String.fromCharCode(event.charCode);

    if (!pattern.test(inputChar)) {
      // Invalid character, prevent input
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
    // Cerrar todos los otros dropdowns
    Object.keys(this.dropdownStates).forEach(key => {
      if (key !== dropdownName) {
        this.dropdownStates[key as keyof typeof this.dropdownStates] = false;
      }
    });
    // Toggle el dropdown seleccionado
    this.dropdownStates[dropdownName as keyof typeof this.dropdownStates] = 
      !this.dropdownStates[dropdownName as keyof typeof this.dropdownStates];
  }

  

  deseleccionarFila(event: MouseEvent) {
    this.selectedRows = [];  // Deselecciona todas las filas
  }

  openModal(key: string): void {
    this.modals[key] = true;
    if(key== 'confirmacionModal'){
      this.deletedRow = this.selectedRows;
      console.log(this.deletedRow);
    }

   
  }

  closeModal(key: string): void {
    this.modals[key] = false;
    if (key === 'exitoModal') {
      this.cargarTrabajadores();  
    }
  }

  // ============================================
  // 🎯 MÉTODOS PARA MOSTRAR NOMBRES EN DROPDOWNS DEL MODAL MODIFICAR
  // ============================================

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

  // ============================================
  // 🎯 MÉTODO PARA CAMBIO DE MÉTODO DE PAGO EN MODIFICAR
  // ============================================

  onMetodoPagoChangeModificar(event: Event): void {
    const selectElement = event.target as HTMLSelectElement;
    this.metodoPagoNew = selectElement.value;
  }

  // ============================================
  // 🎯 MÉTODO SELECTROW ACTUALIZADO PARA INCLUIR APELLIDOS
  // ============================================

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
      
      // Información personal
      this.nombreTrabajadorNew = selectedRow.nombres;
      this.rutTrabajadorNew = this.formatRUTString(selectedRow.rut);
      this.correoTrabajadorNew = selectedRow.correo;
      this.direccionTrabajadorNew = selectedRow.direccion;
      this.sexoTrabajadorNew = selectedRow.sexo;
      this.telefonoTrabajadorNew = selectedRow.telefono;
      this.nacionalidadTrabajadorNew = selectedRow.nacionalidad;
      this.fechaIngresoNew = selectedRow.fecha_ingreso;
      
      // Método de pago
      this.metodoPagoNew = selectedRow.metodo_pago;
      this.tipoCuentaNew = selectedRow.tipo_cuenta_bancaria;
      this.numeroCuentaNew = selectedRow.numero_cuenta;
      
      // IDs para dropdowns - ESTOS SON LOS IMPORTANTES
      this.selectedSociedadId = selectedRow.sociedad;
      this.selectedAreaId = selectedRow.area;
      this.selectedCargoId = selectedRow.cargo;
      this.selectedAfpId = selectedRow.afp;
      this.selectedSaludId = selectedRow.salud;
      this.selectedBancoId = selectedRow.banco;
      
      console.log('🔍 Datos cargados para modificar:', {
        trabajadorId: this.selectedTrabajadorId,
        sociedadId: this.selectedSociedadId,
        areaId: this.selectedAreaId,
        cargoId: this.selectedCargoId,
        afpId: this.selectedAfpId,
        saludId: this.selectedSaludId,
        bancoId: this.selectedBancoId
      });
    }
  }

  // ============================================
  // 🎯 MÉTODO LIMPIAR FORMULARIO MODIFICACIÓN ACTUALIZADO
  // ============================================

  limpiarFormularioModificacion(): void {
    this.nombreTrabajadorNew = '';
    this.rutTrabajadorNew = '';
    this.correoTrabajadorNew = '';
    this.direccionTrabajadorNew = '';
    this.sexoTrabajadorNew = '';
    this.telefonoTrabajadorNew = '';
    this.nacionalidadTrabajadorNew = 'CHILENA';
    this.fechaIngresoNew = '';
    this.metodoPagoNew = '';
    this.tipoCuentaNew = '';
    this.numeroCuentaNew = '';
    
    // Limpiar selecciones de dropdowns
    this.selectedSociedadId = null;
    this.selectedAreaId = null;
    this.selectedCargoId = null;
    this.selectedAfpId = null;
    this.selectedSaludId = null;
    this.selectedBancoId = null;
    
    // Cerrar todos los dropdowns
    Object.keys(this.dropdownStates).forEach(key => {
      this.dropdownStates[key as keyof typeof this.dropdownStates] = false;
    });
  }

  limpiarFormularioCreacion(): void {
    // Limpiar campos de información personal
    this.nombresTrabajador = null;
    this.apellidosTrabajador = null;
    this.rutTrabajador = null;
    this.correoTrabajador = null;
    this.direccionTrabajador = null;
    this.sexoTrabajador = 'Hombre';
    this.telefonoTrabajador = null;
    this.nacionalidadTrabajador = 'CHILENA';
    
    // Limpiar selecciones de dropdowns
    this.selectedSociedadId = null;
    this.selectedAreaId = null;
    this.selectedCargoId = null;
    this.selectedAfpId = null;
    this.selectedSaludId = null;
    this.selectedBancoId = null;
    
    // Limpiar campos de método de pago
    this.metodoPago = 'Sin Pago';
    this.banco = null;
    this.tipoCuenta = null;
    this.numeroCuenta = null;
    
    // Resetear fecha de ingreso a la fecha actual
    this.setDefaultFechaCelebracion();
    
    // Cerrar todos los dropdowns
    Object.keys(this.dropdownStates).forEach(key => {
      this.dropdownStates[key as keyof typeof this.dropdownStates] = false;
    });
  }


  checkValue():void{
    
    
  }
}