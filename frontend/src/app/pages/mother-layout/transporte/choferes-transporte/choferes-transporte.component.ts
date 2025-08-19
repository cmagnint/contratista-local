import { Component, Inject, OnInit, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser, CommonModule } from '@angular/common';
import { ContratistaApiService } from '../../../../services/contratista-api.service';
import { ReactiveFormsModule } from '@angular/forms';
import { FormsModule } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';

@Component({
  selector: 'app-choferes-transporte',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatTableModule,
    FormsModule
  ],
  templateUrl: './choferes-transporte.component.html',
  styleUrl: './choferes-transporte.component.css'
})
export class ChoferesTransporteComponent implements OnInit {
  constructor(
    private apiService: ContratistaApiService,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {}

  public modals: { [key: string]: boolean } = {
    exitoModal: false,
    errorModal: false,
    crearChofer: false,
    modificarChofer: false,
    confirmacionModal: false,
    empresasModal: false,
    vehiculoModal: false,
  };

  public choferSeleccionado: any = {
    nombre_chofer_seleccionado : '',
    rut_chofer_seleccionado : '',
    licencia_chofer_seleccionado : '',
    id_empresa_chofer_seleccionado: 0,
    id_chofer_seleccionada : 0,
  }

  public holding: string = ''; 
  public nombreEmpresa: string = '';
  public nombreChofer: string = '';
  public rutChofer: string = '';
  public licenciaChofer: string = '';

  errorMessage!: string;
  selectedRows: any[] = [];
  dropdownOpen: boolean = false;
  dropdownOpenVehiculos: boolean = false;

  public todasSeleccionadas: boolean = false;

  public choferesCargados: any[] = [];
  public empresasCargadas: any[] = [];
  public vehiculosAgrupados: any[] = [];

  columnasDesplegadas = ['empresa','modelo','nombre','rut','licencia'];
  
  public nombreChoferNew: string = '';
  public rutChoferNew: string = '';
  public licenciaChoferNew: string = '';

  public deletedRow: any[] = [];

  public selectedChoferId: number | null = null;
  public selectedEmpresaId: number | null = null;
  public selectedVehiculoId: number | null = null;

  ngOnInit(): void {
    if (isPlatformBrowser(this.platformId)) {
      this.holding = localStorage.getItem('holding_id') || '';
      this.cargarChoferes();
      this.cargarEmpresas();
      this.cargarVehiculos();
    }
  }

  crearChoferes():void{
    let data = {
      holding: this.holding,
      empresa: this.selectedEmpresaId,
      nombre: this.nombreChofer,
      rut: this.rutChofer,
      licencia: this.licenciaChofer,
      vehiculo: this.selectedVehiculoId
    }
    this.apiService.post('api_choferes_transportes/', data).subscribe({
      next: (response) => {
        console.log(response);
        this.closeModal('crearChofer');
        this.cargarChoferes();
        this.openModal('exitoModal');
      }, error:(error) => {
        this.openModal('errorModal');
      }
    })
  }

  cargarEmpresas():void{
    this.apiService.get(`api_empresa_transportes/?holding=${this.holding}`).subscribe({
      next: (response) => {
        this.empresasCargadas = response;
        console.log(this.empresasCargadas);
      },
      error: (error) => {
        console.error('Error al recibir las sociedades:', error);
      }
    });
  }

  cargarChoferes():void{
    this.apiService.get(`api_choferes_transportes/?holding=${this.holding}`).subscribe({
      next: (response) => {
        this.choferesCargados = response;
      },
      error: (error) => {
        console.error('Error al recibir las sociedades:', error);
      }
    });
  }

  cargarVehiculos():void{
    this.apiService.get(`api_vehiculos_transportes/?holding=${this.holding}`).subscribe({
      next: (response) => {
        console.log('vehiculos cargados',response)
        const vehiculosPorEmpresa: { [key: string]: any[] } = {};
        response.forEach((vehiculo: any) => {
          if (!vehiculosPorEmpresa[vehiculo.nombre_empresa]) {
            vehiculosPorEmpresa[vehiculo.nombre_empresa] = [];
          }
          vehiculosPorEmpresa[vehiculo.nombre_empresa].push({
            id: vehiculo.id,
            modelo: vehiculo.modelo,
            empresa_id: vehiculo.empresa,
            
          });
        });
        this.vehiculosAgrupados = Object.keys(vehiculosPorEmpresa).map(empresaId => ({
          nombre: this.empresasCargadas.find(empresa => empresa.id.toString() === empresaId)?.nombre || empresaId,
          vehiculos: vehiculosPorEmpresa[empresaId]
        }));
      },
      error: (error) => {
        console.error('Error al recibir los vehículos:', error);
      }
    });
  }

  modificarChoferes():void{
    let data = {
      holding: this.holding,
      empresa: this.selectedEmpresaId,
      nombre: this.nombreChoferNew,
      rut: this.rutChoferNew,
      licencia: this.licenciaChoferNew,
      id: this.selectedChoferId,
      vehiculo: this.selectedVehiculoId
    }
    this.apiService.put('api_choferes_transportes/', data).subscribe({
      next:(response) => {
        this.closeModal('modificarChofer');
        this.cargarChoferes();
        this.openModal('exitoModal');
      }, error:(error) => {
        console.log(error);
        this.openModal('errorModal');
      }
    })
  }
  
  eliminarChoferesSeleccionados(): void {
    if (this.deletedRow.length > 0) {
        const idsToDelete = this.deletedRow.map(row => row.id);
        this.apiService.delete('api_choferes_transportes/', {ids: idsToDelete}).subscribe({
            next: () => {
                this.closeModal('confirmacionModal')
                this.cargarChoferes();
                this.openModal('exitoModal');
                this.deletedRow = []; // Limpiar la selección después de eliminar
            },
            error: (error) => {
                this.openModal('errorModal');
                console.error('Error al eliminar perfiles:', error);
            }
        });
    }
  }

  toggleSelection(empresaId: number): void {
    if (this.selectedEmpresaId === empresaId) {
      this.selectedEmpresaId = null; 
    } else {
      this.selectedEmpresaId = empresaId; 
    }
  }

  selectVehiculo(vehiculoId: number): void {
    this.selectedVehiculoId = vehiculoId;
  }

  isSelected(row: any): boolean {
    return this.selectedRows.some(r => r.id === row.id);
  }

  selectRow(row: any): void {
    const index = this.selectedRows.findIndex(selectedRow => selectedRow.id === row.id);
    if (index > -1) {
        this.selectedRows.splice(index, 1);
    } else {
        this.selectedRows.push(row);
    }

    if (this.selectedRows.length > 0){
        const lastSelectedRow = this.selectedRows[this.selectedRows.length - 1];
        this.choferSeleccionado = {
        nombre_chofer_seleccionado: lastSelectedRow.nombre,
        rut_chofer_seleccionado: lastSelectedRow.rut,
        licencia_chofer_seleccionado: lastSelectedRow.licencia,
        id_chofer_seleccionada : lastSelectedRow.id,
        id_empresa_chofer_seleccionado: lastSelectedRow.empresa
      };
      this.nombreChoferNew = this.choferSeleccionado.nombre_chofer_seleccionado
      this.rutChoferNew = this.choferSeleccionado.rut_chofer_seleccionado
      this.licenciaChoferNew = this.choferSeleccionado.licencia_chofer_seleccionado
      this.selectedChoferId = this.choferSeleccionado.id_chofer_seleccionada;
      this.selectedEmpresaId = this.choferSeleccionado.id_empresa_chofer_seleccionado;

    } else {
      this.choferSeleccionado = {
        nombre_chofer_seleccionado : '',
        rut_chofer_seleccionado : '',
        licencia_chofer_seleccionado : '',
        id_empresa_chofer_seleccionado: 0,
        id_chofer_seleccionada : 0,
      }
    }
  }

  formatNumber(event: Event): void{
    const target = event.target as HTMLInputElement; 
    if (!target) return;
    let rut = target.value.replace(/\D/g, '');
  }

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

  toggleDropdown() {
    this.dropdownOpen = !this.dropdownOpen;
  }

  toggleDropdownVehiculos() {
    this.dropdownOpenVehiculos = !this.dropdownOpenVehiculos;
  }

  deseleccionarFila(event: MouseEvent) {
    this.selectedRows = [];
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
      this.cargarEmpresas();  
    }
  }
}
