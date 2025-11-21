import { Component, Inject, OnInit, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser, CommonModule } from '@angular/common';
import { ContratistaApiService } from '../../../../services/contratista-api.service';
import { FormsModule } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { JwtService } from '../../../../services/jwt.service';

@Component({
  selector: 'app-maestro-trabajadores',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatTableModule,
    MatButtonModule,
    MatSelectModule,
    MatFormFieldModule,
    MatIconModule,
    MatInputModule,
    MatDatepickerModule,
    MatNativeDateModule
  ],
  templateUrl: './maestro-trabajadores.component.html',
  styleUrl: './maestro-trabajadores.component.css'
})
export class MaestroTrabajadoresComponent implements OnInit {
  
  constructor(
    private apiService: ContratistaApiService,
    private jwtService: JwtService,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {}

  // Variables existentes
  public holding: string = '';
  public contratos: any[] = [];
  public contratosFiltrados: any[] = [];
  public filtroEstado: string = 'vigente';
  public selectedRows: any[] = [];
  public contratoSeleccionado: any = null;
  
  // Variables para crear contrato
  public sociedades: any[] = [];
  public folios: any[] = [];
  public fundos: any[] = [];
  public labores: any[] = [];
  public casas: any[] = [];
  public horarios: any[] = [];
  public trabajadores: any[] = [];
  public documentos: any[] = [];
  
  // NUEVAS VARIABLES para supervisores y transporte
  public supervisores: any[] = [];
  public jefesCuadrilla: any[] = [];
  public jefesCuadrillaFiltrados: any[] = [];
  public transportistas: any[] = [];
  public vehiculosFiltrados: any[] = [];
  public choferesFiltrados: any[] = [];
  
  public isCreatingContract: boolean = false;
  
  public nuevoContrato = {
    sociedad_id: '',
    folio_id: '',
    fundo_id: '',
    labor_id: '',
    casa_id: '',
    horario_id: '',
    trabajador_id: '',
    documento_id: '',
    fecha_inicio: '',
    fecha_termino: '',
    // NUEVOS CAMPOS
    supervisor_id: '',
    jefe_cuadrilla_id: '',
    transportista_id: '',
    vehiculo_id: '',
    chofer_id: ''
  };
  
  // Columnas de la tabla
  displayedColumns: string[] = [
    'id',
    'trabajador',
    'rut',
    'sociedad',
    'cliente',
    'fundo',
    'fecha_inicio',
    'fecha_termino',
    'estado',
    'dias_restantes',
    'acciones'
  ];
  
  // Modal
  public modals: { [key: string]: boolean } = {
    exitoModal: false,
    errorModal: false,
    confirmacionModal: false,
    detalleContratoModal: false,
    crearContratoModal: false
  };
  
  public errorMessage: string = '';

  ngOnInit(): void {
    if (isPlatformBrowser(this.platformId)) {
      this.holding = this.getHoldingIdFromJWT();
      console.log('Holding:', this.holding);
      this.cargarContratos();
      this.cargarSociedadesyFolios();
    }
  }

  private getHoldingIdFromJWT(): string {
    try {
      const userInfo = this.jwtService.getUserInfo();
      const holdingId = userInfo?.holding_id;
      
      console.log('🔍 Holding ID del JWT:', holdingId);
      
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

  cargarContratos(): void {
    const params = `holding=${this.holding}&estado=${this.filtroEstado}`;
    
    this.apiService.get(`api_contratos_trabajadores/?${params}`).subscribe({
      next: (response) => {
        this.contratos = response;
        this.contratosFiltrados = response;
        console.log('✅ Contratos cargados:', this.contratos.length);
      },
      error: (error) => {
        console.error('❌ Error al cargar contratos:', error);
        this.errorMessage = 'Error al cargar contratos';
        this.openModal('errorModal');
      }
    });
  }

  cargarSociedadesyFolios(): void {
    this.apiService.get(`api_crear_contrato_web/?holding=${this.holding}`).subscribe({
      next: (response) => {
        this.sociedades = response.sociedades;
        this.folios = response.folios;
        this.supervisores = response.supervisores;
        this.jefesCuadrilla = response.jefes_cuadrilla;
        this.transportistas = response.transportistas;
        
        console.log('✅ Sociedades cargadas:', this.sociedades.length);
        console.log('✅ Folios cargados:', this.folios.length);
        console.log('✅ Supervisores cargados:', this.supervisores.length);
        console.log('✅ Jefes de cuadrilla cargados:', this.jefesCuadrilla.length);
        console.log('✅ Transportistas cargados:', this.transportistas.length);
      },
      error: (error) => {
        console.error('❌ Error al cargar datos iniciales:', error);
      }
    });
  }

  onSociedadChange(): void {
    if (!this.nuevoContrato.sociedad_id) return;
    
    // Resetear campos dependientes
    this.nuevoContrato.folio_id = '';
    this.trabajadores = [];
    this.fundos = [];
    this.labores = [];
    this.horarios = [];
    this.casas = [];
    this.documentos = [];
  }

  onFolioChange(): void {
    if (!this.nuevoContrato.folio_id || !this.nuevoContrato.sociedad_id) return;
    
    const params = `holding=${this.holding}&sociedad_id=${this.nuevoContrato.sociedad_id}&folio_id=${this.nuevoContrato.folio_id}`;
    
    this.apiService.get(`api_crear_contrato_web/?${params}`).subscribe({
      next: (response) => {
        this.trabajadores = response.trabajadores;
        this.fundos = response.fundos;
        this.labores = response.labores;
        this.horarios = response.horarios;
        this.casas = response.casas;
        this.documentos = response.documentos;
        
        // Auto-llenar fechas desde el folio
        this.nuevoContrato.fecha_inicio = response.folio.fecha_inicio;
        this.nuevoContrato.fecha_termino = response.folio.fecha_termino;
        
        console.log('✅ Trabajadores sin contrato:', this.trabajadores.length);
        console.log('✅ Datos del folio cargados');
      },
      error: (error) => {
        console.error('❌ Error al cargar datos del folio:', error);
        this.errorMessage = 'Error al cargar datos del folio';
        this.openModal('errorModal');
      }
    });
  }

  // NUEVO: Filtrar jefes de cuadrilla por supervisor
  onSupervisorChange(): void {
    if (!this.nuevoContrato.supervisor_id) {
      this.jefesCuadrillaFiltrados = [];
      this.nuevoContrato.jefe_cuadrilla_id = '';
      return;
    }
    
    this.jefesCuadrillaFiltrados = this.jefesCuadrilla.filter(
      jefe => jefe.supervisor_id === parseInt(this.nuevoContrato.supervisor_id)
    );
    
    // Resetear jefe de cuadrilla si no hay opciones
    if (this.jefesCuadrillaFiltrados.length === 0) {
      this.nuevoContrato.jefe_cuadrilla_id = '';
    }
    
    console.log('✅ Jefes de cuadrilla filtrados:', this.jefesCuadrillaFiltrados.length);
  }

  // NUEVO: Filtrar vehículos por transportista
  onTransportistaChange(): void {
    if (!this.nuevoContrato.transportista_id) {
      this.vehiculosFiltrados = [];
      this.choferesFiltrados = [];
      this.nuevoContrato.vehiculo_id = '';
      this.nuevoContrato.chofer_id = '';
      return;
    }
    
    const transportistaSeleccionado = this.transportistas.find(
      t => t.id === parseInt(this.nuevoContrato.transportista_id)
    );
    
    this.vehiculosFiltrados = transportistaSeleccionado?.vehiculos || [];
    this.choferesFiltrados = [];
    this.nuevoContrato.vehiculo_id = '';
    this.nuevoContrato.chofer_id = '';
    
    console.log('✅ Vehículos filtrados:', this.vehiculosFiltrados.length);
  }

  // NUEVO: Filtrar choferes por vehículo
  onVehiculoChange(): void {
    if (!this.nuevoContrato.vehiculo_id) {
      this.choferesFiltrados = [];
      this.nuevoContrato.chofer_id = '';
      return;
    }
    
    const vehiculoSeleccionado = this.vehiculosFiltrados.find(
      v => v.id === parseInt(this.nuevoContrato.vehiculo_id)
    );
    
    this.choferesFiltrados = vehiculoSeleccionado?.choferes || [];
    this.nuevoContrato.chofer_id = '';
    
    console.log('✅ Choferes filtrados:', this.choferesFiltrados.length);
  }

  cambiarFiltro(filtro: string): void {
    this.filtroEstado = filtro;
    this.selectedRows = [];
    this.cargarContratos();
  }

  selectRow(row: any): void {
    const index = this.selectedRows.findIndex(r => r.id === row.id);
    if (index > -1) {
      this.selectedRows.splice(index, 1);
    } else {
      this.selectedRows.push(row);
    }
  }

  isSelected(row: any): boolean {
    return this.selectedRows.some(r => r.id === row.id);
  }

  eliminarContratosSeleccionados(event?: MouseEvent): void {
    if (event) event.stopPropagation();
    if (this.selectedRows.length === 0) return;
    this.openModal('confirmacionModal');
  }

  confirmarEliminacion(): void {
    const ids = this.selectedRows.map(r => r.id);
    
    this.apiService.delete('api_contratos_trabajadores/', { ids }).subscribe({
      next: () => {
        console.log('✅ Contratos eliminados exitosamente');
        this.closeModal('confirmacionModal');
        this.selectedRows = [];
        this.cargarContratos();
        this.openModal('exitoModal');
      },
      error: (error) => {
        console.error('❌ Error al eliminar contratos:', error);
        this.errorMessage = 'Error al eliminar contratos';
        this.openModal('errorModal');
      }
    });
  }

  abrirModalCrearContrato(): void {
    this.limpiarFormularioContrato();
    this.openModal('crearContratoModal');
  }

  crearContrato(): void {
    if (this.isCreatingContract) return;
    
    if (!this.nuevoContrato.sociedad_id || !this.nuevoContrato.folio_id || 
        !this.nuevoContrato.fundo_id || !this.nuevoContrato.labor_id || 
        !this.nuevoContrato.horario_id || 
        !this.nuevoContrato.trabajador_id || !this.nuevoContrato.fecha_inicio) {
      this.errorMessage = 'Complete todos los campos obligatorios';
      this.openModal('errorModal');
      return;
    }

    this.isCreatingContract = true;

    const body: any = {
      holding: this.holding,
      trabajador: this.nuevoContrato.trabajador_id,
      documento: this.nuevoContrato.documento_id || null,
      fecha_inicio_contrato: this.nuevoContrato.fecha_inicio,
      fecha_termino_contrato: this.nuevoContrato.fecha_termino || null,
      labor: this.nuevoContrato.labor_id,
      folio_comercial: this.nuevoContrato.folio_id,
      horario: this.nuevoContrato.horario_id,
      fundo: this.nuevoContrato.fundo_id,
      casa: this.nuevoContrato.casa_id || null
    };

    // AGREGAR CAMPOS OPCIONALES
    if (this.nuevoContrato.supervisor_id) {
      body.supervisor_id = this.nuevoContrato.supervisor_id;
    }
    
    if (this.nuevoContrato.jefe_cuadrilla_id) {
      body.jefe_cuadrilla_id = this.nuevoContrato.jefe_cuadrilla_id;
    }
    
    if (this.nuevoContrato.transportista_id) {
      body.transportista_id = this.nuevoContrato.transportista_id;
    }
    
    if (this.nuevoContrato.vehiculo_id) {
      body.vehiculo_id = this.nuevoContrato.vehiculo_id;
    }
    
    if (this.nuevoContrato.chofer_id) {
      body.chofer_id = this.nuevoContrato.chofer_id;
    }

    this.apiService.post('api_crear_contrato_web/', body).subscribe({
      next: (response) => {
        console.log('✅ Contrato creado:', response);
        this.isCreatingContract = false;
        this.closeModal('crearContratoModal');
        this.cargarContratos();
        this.openModal('exitoModal');
      },
      error: (error) => {
        console.error('❌ Error al crear contrato:', error);
        this.isCreatingContract = false;
        this.errorMessage = error.error?.error || 'Error al crear contrato';
        this.openModal('errorModal');
      }
    });
  }

  limpiarFormularioContrato(): void {
    this.nuevoContrato = {
      sociedad_id: '',
      folio_id: '',
      fundo_id: '',
      labor_id: '',
      casa_id: '',
      horario_id: '',
      trabajador_id: '',
      documento_id: '',
      fecha_inicio: '',
      fecha_termino: '',
      supervisor_id: '',
      jefe_cuadrilla_id: '',
      transportista_id: '',
      vehiculo_id: '',
      chofer_id: ''
    };
    this.fundos = [];
    this.labores = [];
    this.horarios = [];
    this.jefesCuadrillaFiltrados = [];
    this.vehiculosFiltrados = [];
    this.choferesFiltrados = [];
  }

  verDetalleContrato(contrato: any): void {
    this.contratoSeleccionado = contrato;
    this.openModal('detalleContratoModal');
  }

  getEstadoColor(estado: string): string {
    return estado === 'VIGENTE' ? '#90EE90' : '#FFB6C1';
  }

  openModal(key: string): void {
    this.modals[key] = true;
  }

  closeModal(key: string): void {
    this.modals[key] = false;
    
    if (key === 'detalleContratoModal') {
      this.contratoSeleccionado = null;
    }
    if (key === 'crearContratoModal') {
      this.limpiarFormularioContrato();
    }
  }

  deseleccionarFila(event: MouseEvent): void {
    this.selectedRows = [];
  }
}