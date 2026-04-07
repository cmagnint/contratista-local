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

  // ── Estado general ────────────────────────────────────────────────────────
  public holding: string = '';
  public contratos: any[] = [];
  public filtroEstado: string = 'vigente';
  public filtroSupervisor: string = 'todos';
  public selectedRows: any[] = [];
  public contratoSeleccionado: any = null;
  public filtrosVisible: boolean = true;

  // ── Fecha terminación ─────────────────────────────────────────────────────
  public fechaTerminacion: string = '';

  get hoy(): string {
    return new Date().toISOString().split('T')[0];
  }

  // ── Filtros de texto ──────────────────────────────────────────────────────
  filtros = { nombres: '', apellidos: '', rut: '', fecha_inicio: '', nacionalidad: '', cliente: '' };

  get contratosFiltrados(): any[] {
    let base = this.contratos;

    if (this.filtroSupervisor === 'sin_supervisor') {
      base = base.filter(c => !c.supervisor);
    } else if (this.filtroSupervisor !== 'todos') {
      base = base.filter(c => c.supervisor?.id?.toString() === this.filtroSupervisor);
    }

    return base.filter(c =>
      (!this.filtros.nombres      || (c.nombres_trabajador     || '').toUpperCase().includes(this.filtros.nombres.toUpperCase()))      &&
      (!this.filtros.apellidos    || (c.apellidos_trabajador   || '').toUpperCase().includes(this.filtros.apellidos.toUpperCase()))    &&
      (!this.filtros.rut          || (c.rut_trabajador         || '').toUpperCase().includes(this.filtros.rut.toUpperCase()))          &&
      (!this.filtros.fecha_inicio || (c.fecha_inicio_contrato  || '').includes(this.filtros.fecha_inicio))                            &&
      (!this.filtros.nacionalidad || (c.nacionalidad_trabajador || '').toUpperCase().includes(this.filtros.nacionalidad.toUpperCase())) &&
      (!this.filtros.cliente      || (c.nombre_cliente         || '').toUpperCase().includes(this.filtros.cliente.toUpperCase()))
    );
  }

  get uniqueNacionalidades(): string[] {
    return [...new Set(this.contratos.map(c => c.nacionalidad_trabajador).filter(Boolean))] as string[];
  }

  limpiarFiltros(): void {
    this.filtros = { nombres: '', apellidos: '', rut: '', fecha_inicio: '', nacionalidad: '', cliente: '' };
  }

  // ── Datos para crear contrato ─────────────────────────────────────────────
  public sociedades: any[] = [];
  public folios: any[] = [];
  public fundos: any[] = [];
  public labores: any[] = [];
  public casas: any[] = [];
  public horarios: any[] = [];
  public trabajadores: any[] = [];
  public documentos: any[] = [];

  // ── Supervisores y transporte ─────────────────────────────────────────────
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
    supervisor_id: '',
    jefe_cuadrilla_id: '',
    transportista_id: '',
    vehiculo_id: '',
    chofer_id: ''
  };

  // ── Contrato Retroactivo ──────────────────────────────────────────────────
  public nuevoContratoRetroactivo = {
    fecha_consulta:  '',
    historial_id:    '',
    trabajador_id:   '',
    supervisor_id:   '',
    sociedad_id:     '',
    folio_id:        '',
    fundo_id:        '',
    labor_id:        '',
    horario_id:      '',
    documento_id:    '',
    fecha_inicio:    '',
    fecha_termino:   '',
  };
  public historialesDisponibles: any[] = [];
  public historialesFiltrados:   any[] = [];
  public fundosRetroactivo:      any[] = [];
  public laboresRetroactivo:     any[] = [];
  public horariosRetroactivo:    any[] = [];
  public isLoadingHistorial:     boolean = false;
  public isCreatingRetroactivo:  boolean = false;

  // ── Columnas ──────────────────────────────────────────────────────────────
  displayedColumns: string[] = [
    'id', 'trabajador', 'apellidos', 'rut', 'nacionalidad', 'sociedad', 'cliente', 'fundo',
    'supervisor', 'fecha_inicio', 'fecha_termino', 'estado',
    'dias_restantes', 'acciones', 'horario',
  ];

  // ── Modales ───────────────────────────────────────────────────────────────
  public modals: { [key: string]: boolean } = {
    exitoModal:               false,
    errorModal:               false,
    confirmacionModal:        false,
    detalleContratoModal:     false,
    crearContratoModal:       false,
    terminarContratoModal:    false,
    contratoRetroactivoModal: false
  };

  public errorMessage: string = '';

  // ── Lifecycle ─────────────────────────────────────────────────────────────

  ngOnInit(): void {
    if (isPlatformBrowser(this.platformId)) {
      this.holding = this.getHoldingIdFromJWT();
      this.cargarContratos();
      this.cargarSociedadesyFolios();
    }
  }

  private getHoldingIdFromJWT(): string {
    try {
      const userInfo = this.jwtService.getUserInfo();
      const holdingId = userInfo?.holding_id;
      if (holdingId && holdingId !== null) {
        return holdingId.toString();
      }
      return '';
    } catch (error) {
      console.error('Error extrayendo holding_id del JWT:', error);
      return '';
    }
  }

  // ── Carga de datos ────────────────────────────────────────────────────────

  cargarContratos(): void {
    const params = `holding=${this.holding}&estado=${this.filtroEstado}`;
    this.apiService.get(`api_contratos_trabajadores/?${params}`).subscribe({
      next: (response) => {
        this.contratos = response;
      },
      error: (error) => {
        console.error('Error al cargar contratos:', error);
        this.errorMessage = 'Error al cargar contratos';
        this.openModal('errorModal');
      }
    });
  }

  cargarSociedadesyFolios(): void {
    this.apiService.get(`api_crear_contrato_web/?holding=${this.holding}`).subscribe({
      next: (response) => {
        this.sociedades     = response.sociedades;
        this.folios         = response.folios;
        this.supervisores   = response.supervisores;
        this.jefesCuadrilla = response.jefes_cuadrilla;
        this.transportistas = response.transportistas;
      },
      error: (error) => {
        console.error('Error al cargar datos iniciales:', error);
      }
    });
  }

  // ── Filtros ───────────────────────────────────────────────────────────────

  cambiarFiltro(filtro: string): void {
    this.filtroEstado = filtro;
    this.selectedRows = [];
    this.cargarContratos();
  }

  aplicarFiltroSupervisor(): void {
    // Mantenido por compatibilidad; la lógica está en el getter contratosFiltrados
  }

  // ── Selección de filas ────────────────────────────────────────────────────

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

  deseleccionarFila(event: MouseEvent): void {
    this.selectedRows = [];
  }

  // ── Eliminar contratos ────────────────────────────────────────────────────

  eliminarContratosSeleccionados(event?: MouseEvent): void {
    if (event) event.stopPropagation();
    if (this.selectedRows.length === 0) return;
    this.openModal('confirmacionModal');
  }

  confirmarEliminacion(): void {
    const ids = this.selectedRows.map(r => r.id);
    this.apiService.delete('api_contratos_trabajadores/', { ids }).subscribe({
      next: () => {
        this.closeModal('confirmacionModal');
        this.selectedRows = [];
        this.cargarContratos();
        this.openModal('exitoModal');
      },
      error: (error) => {
        console.error('Error al eliminar contratos:', error);
        this.errorMessage = 'Error al eliminar contratos';
        this.openModal('errorModal');
      }
    });
  }

  // ── Crear contrato ────────────────────────────────────────────────────────

  abrirModalCrearContrato(): void {
    this.limpiarFormularioContrato();
    this.openModal('crearContratoModal');
  }

  onSociedadChange(): void {
    if (!this.nuevoContrato.sociedad_id) return;
    this.nuevoContrato.folio_id = '';
    this.trabajadores = [];
    this.fundos  = [];
    this.labores = [];
    this.horarios = [];
    this.casas   = [];
    this.documentos = [];
  }

  onFolioChange(): void {
    if (!this.nuevoContrato.folio_id || !this.nuevoContrato.sociedad_id) return;
    const params = `holding=${this.holding}&sociedad_id=${this.nuevoContrato.sociedad_id}&folio_id=${this.nuevoContrato.folio_id}`;
    this.apiService.get(`api_crear_contrato_web/?${params}`).subscribe({
      next: (response) => {
        this.trabajadores = response.trabajadores;
        this.fundos       = response.fundos;
        this.labores      = response.labores;
        this.horarios     = response.horarios;
        this.casas        = response.casas;
        this.documentos   = response.documentos;
        this.nuevoContrato.fecha_inicio  = response.folio.fecha_inicio;
        this.nuevoContrato.fecha_termino = response.folio.fecha_termino;
      },
      error: (error) => {
        console.error('Error al cargar datos del folio:', error);
        this.errorMessage = 'Error al cargar datos del folio';
        this.openModal('errorModal');
      }
    });
  }

  onSupervisorChange(): void {
    if (!this.nuevoContrato.supervisor_id) {
      this.jefesCuadrillaFiltrados = [];
      this.nuevoContrato.jefe_cuadrilla_id = '';
      return;
    }
    this.jefesCuadrillaFiltrados = this.jefesCuadrilla.filter(
      jefe => jefe.supervisor_id === parseInt(this.nuevoContrato.supervisor_id)
    );
    if (this.jefesCuadrillaFiltrados.length === 0) {
      this.nuevoContrato.jefe_cuadrilla_id = '';
    }
  }

  onTransportistaChange(): void {
    if (!this.nuevoContrato.transportista_id) {
      this.vehiculosFiltrados = [];
      this.choferesFiltrados  = [];
      this.nuevoContrato.vehiculo_id = '';
      this.nuevoContrato.chofer_id   = '';
      return;
    }
    const t = this.transportistas.find(
      t => t.id === parseInt(this.nuevoContrato.transportista_id)
    );
    this.vehiculosFiltrados = t?.vehiculos || [];
    this.choferesFiltrados  = [];
    this.nuevoContrato.vehiculo_id = '';
    this.nuevoContrato.chofer_id   = '';
  }

  onVehiculoChange(): void {
    if (!this.nuevoContrato.vehiculo_id) {
      this.choferesFiltrados = [];
      this.nuevoContrato.chofer_id = '';
      return;
    }
    const v = this.vehiculosFiltrados.find(
      v => v.id === parseInt(this.nuevoContrato.vehiculo_id)
    );
    this.choferesFiltrados       = v?.choferes || [];
    this.nuevoContrato.chofer_id = '';
  }

  crearContrato(): void {
    if (this.isCreatingContract) return;

    if (!this.nuevoContrato.sociedad_id || !this.nuevoContrato.folio_id ||
        !this.nuevoContrato.fundo_id    || !this.nuevoContrato.labor_id  ||
        !this.nuevoContrato.horario_id  || !this.nuevoContrato.trabajador_id ||
        !this.nuevoContrato.fecha_inicio) {
      this.errorMessage = 'Complete todos los campos obligatorios';
      this.openModal('errorModal');
      return;
    }

    this.isCreatingContract = true;

    const body: any = {
      holding:                this.holding,
      trabajador:             this.nuevoContrato.trabajador_id,
      documento:              this.nuevoContrato.documento_id || null,
      fecha_inicio_contrato:  this.nuevoContrato.fecha_inicio,
      fecha_termino_contrato: this.nuevoContrato.fecha_termino || null,
      labor:                  this.nuevoContrato.labor_id,
      folio_comercial:        this.nuevoContrato.folio_id,
      horario:                this.nuevoContrato.horario_id,
      fundo:                  this.nuevoContrato.fundo_id,
      casa:                   this.nuevoContrato.casa_id || null
    };

    if (this.nuevoContrato.supervisor_id)     body.supervisor_id     = this.nuevoContrato.supervisor_id;
    if (this.nuevoContrato.jefe_cuadrilla_id) body.jefe_cuadrilla_id = this.nuevoContrato.jefe_cuadrilla_id;
    if (this.nuevoContrato.transportista_id)  body.transportista_id  = this.nuevoContrato.transportista_id;
    if (this.nuevoContrato.vehiculo_id)       body.vehiculo_id       = this.nuevoContrato.vehiculo_id;
    if (this.nuevoContrato.chofer_id)         body.chofer_id         = this.nuevoContrato.chofer_id;

    this.apiService.post('api_crear_contrato_web/', body).subscribe({
      next: () => {
        this.isCreatingContract = false;
        this.closeModal('crearContratoModal');
        this.cargarContratos();
        this.openModal('exitoModal');
      },
      error: (error) => {
        console.error('Error al crear contrato:', error);
        this.isCreatingContract = false;
        this.errorMessage = error.error?.error || 'Error al crear contrato';
        this.openModal('errorModal');
      }
    });
  }

  limpiarFormularioContrato(): void {
    this.nuevoContrato = {
      sociedad_id: '', folio_id: '', fundo_id: '', labor_id: '',
      casa_id: '', horario_id: '', trabajador_id: '', documento_id: '',
      fecha_inicio: '', fecha_termino: '', supervisor_id: '',
      jefe_cuadrilla_id: '', transportista_id: '', vehiculo_id: '', chofer_id: ''
    };
    this.fundos                  = [];
    this.labores                 = [];
    this.horarios                = [];
    this.jefesCuadrillaFiltrados = [];
    this.vehiculosFiltrados      = [];
    this.choferesFiltrados       = [];
  }

  // ── Terminar contrato ─────────────────────────────────────────────────────

  terminarContrato(contrato: any, event?: MouseEvent): void {
    if (event) event.stopPropagation();
    this.contratoSeleccionado = contrato;
    this.fechaTerminacion = '';
    this.openModal('terminarContratoModal');
  }

  confirmarTerminacion(): void {
    if (!this.contratoSeleccionado || !this.fechaTerminacion) return;
    this.apiService.patch('api_contratos_trabajadores/', {
      id: this.contratoSeleccionado.id,
      fecha_termino_contrato: this.fechaTerminacion
    }).subscribe({
      next: () => {
        this.closeModal('terminarContratoModal');
        this.contratoSeleccionado = null;
        this.fechaTerminacion = '';
        this.cargarContratos();
        this.openModal('exitoModal');
      },
      error: (error) => {
        console.error('Error al terminar contrato:', error);
        this.errorMessage = error.error?.error || 'Error al terminar contrato';
        this.closeModal('terminarContratoModal');
        this.openModal('errorModal');
      }
    });
  }

  // ── Contrato Retroactivo ──────────────────────────────────────────────────

  abrirModalContratoRetroactivo(): void {
    this.limpiarFormularioRetroactivo();
    this.openModal('contratoRetroactivoModal');
  }

  buscarTrabajadoresSinContrato(): void {
    if (!this.nuevoContratoRetroactivo.fecha_consulta) return;

    this.isLoadingHistorial = true;
    this.historialesFiltrados = [];
    this.nuevoContratoRetroactivo.historial_id  = '';
    this.nuevoContratoRetroactivo.trabajador_id = '';
    this.nuevoContratoRetroactivo.supervisor_id = '';
    this.nuevoContratoRetroactivo.fecha_inicio  = '';
    this.nuevoContratoRetroactivo.fecha_termino = '';

    this.apiService.get(
      `api_contrato_retroactivo/?holding=${this.holding}&fecha=${this.nuevoContratoRetroactivo.fecha_consulta}`
    ).subscribe({
      next: (response: any[]) => {
        this.historialesFiltrados = response;
        this.isLoadingHistorial   = false;
      },
      error: (error) => {
        console.error('Error al buscar trabajadores sin contrato:', error);
        this.isLoadingHistorial = false;
        this.errorMessage = error.error?.error || 'Error al obtener trabajadores sin contrato';
        this.openModal('errorModal');
      }
    });
  }

  onTrabajadorRetroactivoChange(): void {
    this.nuevoContratoRetroactivo.fecha_inicio  = this.nuevoContratoRetroactivo.fecha_consulta;
    this.nuevoContratoRetroactivo.fecha_termino = '';
    this.nuevoContratoRetroactivo.supervisor_id = '';
  }

  onSociedadRetroactivoChange(): void {
    this.nuevoContratoRetroactivo.folio_id   = '';
    this.nuevoContratoRetroactivo.fundo_id   = '';
    this.nuevoContratoRetroactivo.labor_id   = '';
    this.nuevoContratoRetroactivo.horario_id = '';
    this.fundosRetroactivo   = [];
    this.laboresRetroactivo  = [];
    this.horariosRetroactivo = [];
  }

  onFolioRetroactivoChange(): void {
    const { sociedad_id, folio_id } = this.nuevoContratoRetroactivo;
    if (!folio_id || !sociedad_id) return;

    const params = `holding=${this.holding}&sociedad_id=${sociedad_id}&folio_id=${folio_id}`;
    this.apiService.get(`api_crear_contrato_web/?${params}`).subscribe({
      next: (response) => {
        this.fundosRetroactivo   = response.fundos;
        this.laboresRetroactivo  = response.labores;
        this.horariosRetroactivo = response.horarios;
      },
      error: (error) => {
        console.error('Error al cargar datos del folio retroactivo:', error);
        this.errorMessage = 'Error al cargar datos del folio';
        this.openModal('errorModal');
      }
    });
  }

  crearContratoRetroactivo(): void {
    if (this.isCreatingRetroactivo) return;

    const r = this.nuevoContratoRetroactivo;

    if (!r.trabajador_id || !r.fecha_inicio || !r.sociedad_id ||
        !r.folio_id || !r.fundo_id || !r.labor_id || !r.horario_id) {
      this.errorMessage = 'Complete todos los campos obligatorios';
      this.openModal('errorModal');
      return;
    }

    this.isCreatingRetroactivo = true;

    const body: any = {
      holding:               this.holding,
      trabajador:            r.trabajador_id,
      fecha_inicio_contrato: r.fecha_inicio,
      labor:                 r.labor_id,
      folio_comercial:       r.folio_id,
      horario:               r.horario_id,
      fundo:                 r.fundo_id,
    };

    if (r.fecha_termino) body.fecha_termino_contrato = r.fecha_termino;
    if (r.documento_id)  body.documento              = r.documento_id;
    if (r.supervisor_id) body.supervisor_id          = r.supervisor_id;

    this.apiService.post('api_contrato_retroactivo/', body).subscribe({
      next: () => {
        this.isCreatingRetroactivo = false;
        this.closeModal('contratoRetroactivoModal');
        this.cargarContratos();
        this.openModal('exitoModal');
      },
      error: (error) => {
        console.error('Error al crear contrato retroactivo:', error);
        this.isCreatingRetroactivo = false;
        this.errorMessage = error.error?.error || 'Error al crear contrato retroactivo';
        this.openModal('errorModal');
      }
    });
  }

  limpiarFormularioRetroactivo(): void {
    this.nuevoContratoRetroactivo = {
      fecha_consulta: '', historial_id: '', trabajador_id: '',
      supervisor_id: '', sociedad_id: '', folio_id: '', fundo_id: '',
      labor_id: '', horario_id: '', documento_id: '',
      fecha_inicio: '', fecha_termino: '',
    };
    this.historialesDisponibles = [];
    this.historialesFiltrados   = [];
    this.fundosRetroactivo      = [];
    this.laboresRetroactivo     = [];
    this.horariosRetroactivo    = [];
    this.isLoadingHistorial     = false;
    this.isCreatingRetroactivo  = false;
  }

  // ── Detalle ───────────────────────────────────────────────────────────────

  verDetalleContrato(contrato: any): void {
    this.contratoSeleccionado = contrato;
    this.openModal('detalleContratoModal');
  }

  formatRut(rut: string): string {
    if (!rut) return 'N/A';
    const clean     = rut.replace(/\./g, '').replace(/-/g, '').toUpperCase();
    const dv        = clean.slice(-1);
    const body      = clean.slice(0, -1);
    const formatted = body.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
    return `${formatted}-${dv}`;
  }

  // ── Modales ───────────────────────────────────────────────────────────────

  openModal(key: string): void {
    this.modals[key] = true;
  }

  closeModal(key: string): void {
    this.modals[key] = false;
    if (key === 'detalleContratoModal')     this.contratoSeleccionado = null;
    if (key === 'crearContratoModal')       this.limpiarFormularioContrato();
    if (key === 'terminarContratoModal')    { this.contratoSeleccionado = null; this.fechaTerminacion = ''; }
    if (key === 'contratoRetroactivoModal') this.limpiarFormularioRetroactivo();
  }
}