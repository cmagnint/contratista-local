import { Component, Inject, OnInit, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser, CommonModule } from '@angular/common';
import { ContratistaApiService } from '../../../../services/contratista-api.service';
import { ReactiveFormsModule } from '@angular/forms';
import { FormsModule } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';
import { JwtService } from '../../../../services/jwt.service';
@Component({
  selector: 'app-administrar-clientes',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatTableModule,
    FormsModule
  ],
  templateUrl: './administrar-clientes.component.html',
  styleUrl: './administrar-clientes.component.css'
})
export class AdministrarClientesComponent implements OnInit {
  public modals: { [key: string]: boolean } = {
    exitoModal: false,
    errorModal: false,
    crearCliente: false,
    modificarCliente: false,
    confirmacionModal: false,
  };

  public clienteSeleccionado: any = {
    nombre_cliente_seleccionado: '',
    rut_cliente_seleccionado: '',
    direccion_cliente_seleccionado: '',
    giro_cliente_seleccionado: '',
    id_cliente_seleccionado: 0,
  };

  public usuarioIdNew = 0;
  public holding: string = '';
  public nombreCliente: string = '';
  public rutCliente: string = '';
  public direccionCliente: string = '';
  public giroCliente: string = '';
  public nombreRepresentanteLegal: string = '';
  public RUTRepresentanteLegal: string = '';
  public direccionRepresentanteLegal: string = '';
  public nuevoCampo: { nombre: string, direccion: string, comuna: string } = { nombre: '', direccion: '', comuna: '' };
  public campos: { nombre: string, direccion: string, comuna: string }[] = [];
  public camposNew: { id: number, nombre_campo: string, direccion_campo: string, comuna_campo: string }[] = [];

  errorMessage!: string;
  selectedRows: any[] = [];
  dropdownOpen: boolean = false;
  public todasSeleccionadas: boolean = false;
  public clientesCargados: any[] = [];
  columnasDesplegadas = ['rut', 'nombre', 'direccion', 'giro', 'campos_personalizados','nombre_rep','rut_rep'];

  public nombreClienteNew: string = '';
  public rutClienteNew: string = '';
  public direccionClienteNew: string = '';
  public giroClienteNew: string = '';
  public deletedRow: any[] = [];

  public selectedClienteId: number | null = null;

  constructor(
    private apiService: ContratistaApiService,
    private jwtService: JwtService,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {}

  ngOnInit(): void {
    if (isPlatformBrowser(this.platformId)) {
      this.holding = this.getHoldingIdFromJWT();
      this.cargarClientes();
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
  
  crearCliente(): void {
    let data = {
      holding: this.holding,
      nombre: this.nombreCliente,
      rut: this.rutCliente.replace(/[\.\-]/g, ''),
      direccion: this.direccionCliente,
      giro: this.giroCliente,
      rut_rep_legal:  this.RUTRepresentanteLegal.replace(/[\.\-]/g, ''),
      nombre_rep_legal: this.nombreRepresentanteLegal,
      direccion_rep_legal: this.direccionRepresentanteLegal ,
    };
    this.apiService.post('api_clientes/', data).subscribe({
      next: (response) => {
        this.crearCampos(response.id); // Crear los campos personalizados para el cliente creado
        this.cargarClientes();
        this.closeModal('crearCliente');
        this.openModal('exitoModal');
      },
      error: (error) => {
        this.openModal('errorModal');
      }
    });
  }

  crearCampos(clienteId: number): void {
    for (let campo of this.campos) {
      let campoData = {
        holding: this.holding,
        cliente: clienteId,
        nombre_campo: campo.nombre,
        direccion_campo: campo.direccion,
        comuna_campo: campo.comuna
      };
      this.apiService.post('api_campos_clientes/', campoData).subscribe({
        next: (response) => {
          console.log('Campo creado:', response);
        },
        error: (error) => {
          console.error('Error al crear campo:', error);
          this.openModal('errorModal');
        }
      });
    }
    this.campos = []; // Limpiar los campos después de crear
  }

  cargarClientes(): void {
    this.apiService.get(`api_clientes/?holding=${this.holding}`).subscribe({
      next: (response) => {
        
        this.clientesCargados = response;
      },
      error: (error) => {
        console.error('Error al recibir las sociedades:', error);
      }
    });
  }

  cargarCampos(clienteId: number): void {
    this.apiService.get(`api_campos_clientes/${clienteId}`).subscribe({
      next: (response) => {
        console.log(response)
        this.camposNew = response; 
      },
      error: (error) => {
        console.error('Error al cargar campos personalizados:', error);
      }
    });
  }

  modificarCliente(): void {
    let data = {
      holding: this.holding,
      id: this.selectedClienteId,
      nombre: this.nombreClienteNew,
      rut: this.rutClienteNew,
      direccion: this.direccionClienteNew,
      giro: this.giroClienteNew,
      camposPersonalizados: this.camposNew
    };
    this.apiService.put('api_clientes/', data).subscribe({
      next: (response) => {
        console.log('Cliente actualizado:', response);
        this.closeModal('modificarCliente');
        this.cargarClientes();
        this.openModal('exitoModal');
      },
      error: (error) => {
        console.log(error);
        this.openModal('errorModal');
      }
    });
  }

  eliminarClientesSeleccionados(): void {
    if (this.deletedRow.length > 0) {
      const idsToDelete = this.deletedRow.map(row => row.id);
      this.apiService.delete('api_clientes/', { ids: idsToDelete }).subscribe({
        next: () => {
          this.closeModal('confirmacionModal');
          this.cargarClientes();
          this.openModal('exitoModal');
          this.deletedRow = [];
        },
        error: (error) => {
          this.openModal('errorModal');
          console.error('Error al eliminar clientes:', error);
        }
      });
    }
  }

  agregarCampo(): void {
    if (this.nuevoCampo.nombre.trim() && this.nuevoCampo.direccion.trim() && this.nuevoCampo.comuna.trim()) {
      this.campos.push({ ...this.nuevoCampo });
      this.nuevoCampo = { nombre: '', direccion: '', comuna: '' };
    }
  }

  eliminarCampo(index: number): void {
    this.campos.splice(index, 1);
  }

  toggleSelection(clienteId: number): void {
    if (this.selectedClienteId === clienteId) {
      this.selectedClienteId = null;
    } else {
      this.selectedClienteId = clienteId;
    }
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

    if (this.selectedRows.length > 0) {
      const lastSelectedRow = this.selectedRows[this.selectedRows.length - 1];
      this.clienteSeleccionado = {
        nombre_cliente_seleccionado: lastSelectedRow.nombre,
        rut_cliente_seleccionado: lastSelectedRow.rut,
        direccion_cliente_seleccionado: lastSelectedRow.direccion,
        giro_cliente_seleccionado: lastSelectedRow.giro,
        id_cliente_seleccionado: lastSelectedRow.id,
      };
      this.selectedClienteId = this.clienteSeleccionado.id_cliente_seleccionado;
      this.nombreClienteNew = this.clienteSeleccionado.nombre_cliente_seleccionado;
      this.rutClienteNew = this.formatRUTString(this.clienteSeleccionado.rut_cliente_seleccionado);
      this.direccionClienteNew = this.clienteSeleccionado.direccion_cliente_seleccionado;
      this.giroClienteNew = this.clienteSeleccionado.giro_cliente_seleccionado;

      this.cargarCampos(this.selectedClienteId!); // Cargar campos personalizados al seleccionar cliente
    } else {
      this.clienteSeleccionado = {
        nombre_cliente_seleccionado: '',
        rut_cliente_seleccionado: '',
        direccion_cliente_seleccionado: '',
        giro_cliente_seleccionado: '',
      };
    }
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

  deseleccionarFila(event: MouseEvent) {
    this.selectedRows = [];
  }

  openModal(key: string): void {
    this.modals[key] = true;
    if (key == 'confirmacionModal') {
      this.deletedRow = this.selectedRows;
      console.log(this.deletedRow);
    }
  }

  closeModal(key: string): void {
    this.modals[key] = false;
    if (key === 'exitoModal') {
      this.cargarClientes();
    }
  }
}