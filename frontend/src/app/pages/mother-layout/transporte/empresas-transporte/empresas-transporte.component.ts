import { Component, Inject, OnInit, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser, CommonModule } from '@angular/common';
import { ContratistaApiService } from '../../../../services/contratista-api.service';
import { ReactiveFormsModule } from '@angular/forms';
import { FormsModule } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';

@Component({
  selector: 'app-empresas-transporte',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatTableModule,
    FormsModule
  ],
  templateUrl: './empresas-transporte.component.html',
  styleUrl: './empresas-transporte.component.css'
})
export class EmpresasTransporteComponent implements OnInit {
  // VARIABLES BÁSICAS
  public holding: string = '';
  public errorMessage!: string;
  public selectedRows: any[] = [];
  public dropdownOpen: boolean = false;
  public todasSeleccionadas: boolean = false;
  public empresasCargadas: any[] = [];
  public deletedRow: any[] = [];
  public selectedEmpresaId: number | null = null;

  // VARIABLES PARA FOLIOS
  public foliosTransporte: any[] = [];
  public folioTransportistaId: number | null = null;

  // VARIABLES PARA EMPRESA
  public nombreEmpresa: string = '';
  public rutEmpresa: string = '';
  public direccionEmpresa: string = '';
  public nombreEmpresaNew: string = '';
  public rutEmpresaNew: string = '';
  public direccionEmpresaNew: string = '';

  // COLUMNAS DE LA TABLA
  columnasDesplegadas = ['nombre', 'rut', 'direccion', 'folio_transportista'];

  // MODALES
  public modals: { [key: string]: boolean } = {
    exitoModal: false,
    errorModal: false,
    crearEmpresa: false,
    modificarEmpresa: false,
    confirmacionModal: false,
  };

  // EMPRESA SELECCIONADA
  public empresaSeleccionada: any = {
    id_empresa_seleccionada: 0,
    nombre_empresa_seleccionada: '',
    rut_empresa_seleccionada: '',
    direccion_empresa_seleccionada: '',
    folio_transportista: null
  };

  constructor(
    private apiService: ContratistaApiService,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {}

  ngOnInit(): void {
    if (isPlatformBrowser(this.platformId)) {
      this.holding = localStorage.getItem('holding_id') || '';
      this.cargarEmpresas();
      this.cargarFoliosTransporte();
    }
  }

  // CARGA DE DATOS
  cargarEmpresas(): void {
    this.apiService.get(`api_empresa_transportes/?holding=${this.holding}`).subscribe({
      next: (response) => {
        this.empresasCargadas = response;
        console.log('Empresas cargadas:', this.empresasCargadas);
      },
      error: (error) => {
        console.error('Error al recibir las empresas:', error);
      }
    });
  }

  cargarFoliosTransporte(): void {
    this.apiService.get(`api_folio_transportista/?holding=${this.holding}`).subscribe({
      next: (response) => {
        this.foliosTransporte = response;
        console.log('Folios de transporte cargados:', this.foliosTransporte);
      },
      error: (error) => {
        console.error('Error al cargar folios de transporte:', error);
      }
    });
  }

  // OPERACIONES CRUD
  crearEmpresa(): void {
    let data = {
      holding: this.holding,
      nombre: this.nombreEmpresa,
      rut: this.rutEmpresa.replace(/[\.\-]/g, ''),
      direccion: this.direccionEmpresa,
      folio_transportista: this.folioTransportistaId
    }
    this.apiService.post('api_empresa_transportes/', data).subscribe({
      next: (response) => {
        console.log('Empresa creada:', response);
        this.closeModal('crearEmpresa');
        this.cargarEmpresas();
        this.openModal('exitoModal');
        this.limpiarFormulario();
      },
      error: (error) => {
        console.error('Error al crear empresa:', error);
        this.openModal('errorModal');
      }
    });
  }

  modificarEmpresa(): void {
    let data = {
      holding: this.holding,
      id: this.selectedEmpresaId,
      nombre: this.nombreEmpresaNew,
      rut: this.rutEmpresaNew.replace(/[\.\-]/g, ''),
      direccion: this.direccionEmpresaNew,
      folio_transportista: this.folioTransportistaId
    }
    this.apiService.put('api_empresa_transportes/', data).subscribe({
      next: (response) => {
        console.log('Empresa actualizada:', response);
        this.closeModal('modificarEmpresa');
        this.cargarEmpresas();
        this.openModal('exitoModal');
        this.limpiarFormulario();
      },
      error: (error) => {
        console.error('Error al modificar empresa:', error);
        this.openModal('errorModal');
      }
    });
  }

  eliminarEmpresasSeleccionados(): void {
    if (this.deletedRow.length > 0) {
      const idsToDelete = this.deletedRow.map(row => row.id);
      this.apiService.delete('api_empresa_transportes/', { ids: idsToDelete }).subscribe({
        next: () => {
          this.closeModal('confirmacionModal');
          this.cargarEmpresas();
          this.openModal('exitoModal');
          this.deletedRow = [];
        },
        error: (error) => {
          console.error('Error al eliminar empresas:', error);
          this.openModal('errorModal');
        }
      });
    }
  }

  // UTILIDADES
  getFolioInfo(folioId: number): string {
    const folio = this.foliosTransporte.find(f => f.id === folioId);
    return folio ? `${folio.nombre_tramo} - ${folio.valor_pago_transportista}` : 'Sin folio';
  }

  limpiarFormulario(): void {
    this.nombreEmpresa = '';
    this.rutEmpresa = '';
    this.direccionEmpresa = '';
    this.folioTransportistaId = null;
    this.nombreEmpresaNew = '';
    this.rutEmpresaNew = '';
    this.direccionEmpresaNew = '';
  }

  // MANEJO DE SELECCIÓN
  selectRow(row: any): void {
    const index = this.selectedRows.findIndex(selectedRow => selectedRow.id === row.id);
    if (index > -1) {
      this.selectedRows.splice(index, 1);
    } else {
      this.selectedRows.push(row);
    }

    if (this.selectedRows.length > 0) {
      const lastSelectedRow = this.selectedRows[this.selectedRows.length - 1];
      this.empresaSeleccionada = {
        nombre_empresa_seleccionada: lastSelectedRow.nombre,
        rut_empresa_seleccionada: lastSelectedRow.rut,
        direccion_empresa_seleccionada: lastSelectedRow.direccion,
        id_empresa_seleccionada: lastSelectedRow.id,
        folio_transportista: lastSelectedRow.folio_transportista
      };
      this.selectedEmpresaId = this.empresaSeleccionada.id_empresa_seleccionada;
      this.nombreEmpresaNew = this.empresaSeleccionada.nombre_empresa_seleccionada;
      this.rutEmpresaNew = this.formatRUTString(this.empresaSeleccionada.rut_empresa_seleccionada);
      this.direccionEmpresaNew = this.empresaSeleccionada.direccion_empresa_seleccionada;
      this.folioTransportistaId = this.empresaSeleccionada.folio_transportista;
    }
  }

  isSelected(row: any): boolean {
    return this.selectedRows.some(r => r.id === row.id);
  }

  // FORMATO RUT
  formatRUT(event: Event): void {
    const target = event.target as HTMLInputElement;
    if (!target) return;

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

  // MANEJO DE MODALES
  openModal(key: string): void {
    this.modals[key] = true;
    if (key === 'confirmacionModal') {
      this.deletedRow = this.selectedRows;
    }
  }

  getFolioTransportistaInfo(folioId: number | null): string {
    if (!folioId) return 'Sin folio asignado';
    const folio = this.foliosTransporte.find(f => f.id === folioId);
    return folio ? `${folio.nombre_tramo} - $${folio.valor_pago_transportista.toLocaleString()}` : 'Sin folio asignado';
  }

  closeModal(key: string): void {
    this.modals[key] = false;
    if (key === 'exitoModal') {
      this.cargarEmpresas();
    }
  }

  deseleccionarFila(event: MouseEvent): void {
    this.selectedRows = [];
  }
}