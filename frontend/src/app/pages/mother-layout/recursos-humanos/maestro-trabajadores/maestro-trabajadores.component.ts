import { Component, Inject, OnInit, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser, CommonModule } from '@angular/common';
import { ContratistaApiService } from '../../../../services/contratista-api.service';
import { FormsModule } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';

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
    MatIconModule
  ],
  templateUrl: './maestro-trabajadores.component.html',
  styleUrl: './maestro-trabajadores.component.css'
})
export class MaestroTrabajadoresComponent implements OnInit {
  
  constructor(
    private apiService: ContratistaApiService,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {}

  // Variables
  public holding: string = '';
  public contratos: any[] = [];
  public contratosFiltrados: any[] = [];
  public filtroEstado: string = 'todos'; // todos | vigente | vencido
  public selectedRows: any[] = [];
  public contratoSeleccionado: any = null;
  
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
    detalleContratoModal: false
  };
  
  public errorMessage: string = '';

  ngOnInit(): void {
    if (isPlatformBrowser(this.platformId)) {
      this.holding = localStorage.getItem('holding_id') || '';
      this.cargarContratos();
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

  cambiarFiltro(filtro: string): void {
    this.filtroEstado = filtro;
    this.selectedRows = []; // Limpiar selección al cambiar filtro
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

  eliminarContratosSeleccionados(): void {
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
  }

  deseleccionarFila(event: MouseEvent): void {
    this.selectedRows = [];
  }
}