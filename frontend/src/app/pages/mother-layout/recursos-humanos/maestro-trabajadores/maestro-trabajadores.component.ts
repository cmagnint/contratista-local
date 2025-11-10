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
    @Inject(PLATFORM_ID) private platformId: Object
  ) {}

  // Variables existentes
  public holding: string = '';
  public contratos: any[] = [];
  public contratosFiltrados: any[] = [];
  public filtroEstado: string = 'vigente'; // ✅ CAMBIO: ahora por defecto es 'vigente'
  public selectedRows: any[] = [];
  public contratoSeleccionado: any = null;
  
  // ✅ NUEVAS VARIABLES PARA CREAR CONTRATO
  public sociedades: any[] = [];
  public folios: any[] = [];
  public fundos: any[] = [];
  public labores: any[] = [];
  public casas: any[] = [];
  public horarios: any[] = [];
  public trabajadores: any[] = [];
  public documentos: any[] = [];
  public isCreatingContract: boolean = false; // ← AGREGAR variable

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
    fecha_termino: ''
  };
  
  // Columnas de la tabla
  displayedColumns: string[] = [
    'id',
    'trabajador',
    'rut',
    'sociedad',
    'cliente',
    'fundo',
    'documento',
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
    crearContratoModal: false // ✅ NUEVO
  };
  
  public errorMessage: string = '';

  ngOnInit(): void {
    if (isPlatformBrowser(this.platformId)) {
      this.holding = localStorage.getItem('holding_id') || '';
      this.cargarContratos();
      this.cargarSociedades(); // ✅ Carga sociedades Y folios juntos
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

  // ✅ MÉTODOS PARA CARGAR DATOS - USANDO ENDPOINT UNIFICADO
  cargarSociedades(): void {
    // Cargar sociedades y folios iniciales
    this.apiService.get(`api_crear_contrato_web/?holding=${this.holding}`).subscribe({
      next: (response) => {
        this.sociedades = response.sociedades;
        this.folios = response.folios;
        console.log('✅ Sociedades cargadas:', this.sociedades.length);
        console.log('✅ Folios cargados:', this.folios.length);
      },
      error: (error) => {
        console.error('❌ Error al cargar datos iniciales:', error);
      }
    });
  }

  cargarDocumentos(): void {
    // Los documentos ahora vienen en el segundo llamado con sociedad y folio
    // No es necesario cargarlos por separado inicialmente
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
    
    // Cargar trabajadores disponibles y datos del folio
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
    if (event) event.stopPropagation(); // ← AGREGAR ESTO
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

  // ✅ NUEVO MÉTODO PARA ABRIR MODAL CREAR CONTRATO
  abrirModalCrearContrato(): void {
    this.limpiarFormularioContrato();
    this.openModal('crearContratoModal');
  }

  // ✅ NUEVO MÉTODO PARA CREAR CONTRATO
  crearContrato(): void {
    if (this.isCreatingContract) return; // ← PREVENIR doble click
    
    if (!this.nuevoContrato.sociedad_id || !this.nuevoContrato.folio_id || 
        !this.nuevoContrato.fundo_id || !this.nuevoContrato.labor_id || 
        !this.nuevoContrato.horario_id || 
        !this.nuevoContrato.trabajador_id || !this.nuevoContrato.fecha_inicio) {
      this.errorMessage = 'Complete todos los campos obligatorios';
      this.openModal('errorModal');
      return;
    }

    this.isCreatingContract = true; // ← BLOQUEAR

    const body = {
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

    this.apiService.post('api_crear_contrato_web/', body).subscribe({
      next: (response) => {
        console.log('✅ Contrato creado:', response);
        this.isCreatingContract = false; // ← DESBLOQUEAR
        this.closeModal('crearContratoModal');
        this.cargarContratos();
        this.openModal('exitoModal');
      },
      error: (error) => {
        console.error('❌ Error al crear contrato:', error);
        this.isCreatingContract = false; // ← DESBLOQUEAR
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
      fecha_termino: ''
    };
    this.fundos = [];
    this.labores = [];
    this.horarios = [];
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