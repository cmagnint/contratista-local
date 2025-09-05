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
    nombre_rep_legal_seleccionado: '',
    direccion_rep_legal_seleccionado: '',
  };

  public usuarioIdNew = 0;
  public holding: string = '';
  public nombreCliente: string = '';
  public rutCliente: string = '';
  public direccionCliente: string = '';
  public giroCliente: string = '';
  public nombreRepresentanteLegal: string = '';
  public direccionRepresentanteLegal: string = '';
  public nuevoCampo: { nombre: string, direccion: string, comuna: string } = { nombre: '', direccion: '', comuna: '' };
  public campos: { nombre: string, direccion: string, comuna: string }[] = [];
  public camposNew: { id: number, nombre_campo: string, direccion_campo: string, comuna_campo: string }[] = [];

  errorMessage!: string;
  selectedRows: any[] = [];
  dropdownOpen: boolean = false;
  public todasSeleccionadas: boolean = false;
  public clientesCargados: any[] = [];
  columnasDesplegadas = ['rut', 'nombre', 'direccion', 'giro', 'campos_personalizados','nombre_rep'];

  public nombreClienteNew: string = '';
  public rutClienteNew: string = '';
  public direccionClienteNew: string = '';
  public giroClienteNew: string = '';
  // 🆕 NUEVAS VARIABLES PARA REPRESENTANTE LEGAL EN MODIFICACIÓN
  public nombreRepresentanteLegalNew: string = '';
  public direccionRepresentanteLegalNew: string = '';
  
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
      nombre_rep_legal: this.nombreRepresentanteLegal,
      direccion_rep_legal: this.direccionRepresentanteLegal ,
    };
    this.apiService.post('api_clientes/', data).subscribe({
      next: (response) => {
        this.crearCampos(response.id);
        this.cargarClientes();
        this.closeModal('crearCliente');
        this.openModal('exitoModal');
        // Limpiar formulario después de crear
        this.limpiarFormularioCrear();
      },
      error: (error) => {
        this.openModal('errorModal');
      }
    });
  }

  // 🆕 MÉTODO PARA LIMPIAR FORMULARIO DE CREAR
  limpiarFormularioCrear(): void {
    this.nombreCliente = '';
    this.rutCliente = '';
    this.direccionCliente = '';
    this.giroCliente = '';
    this.nombreRepresentanteLegal = '';
    this.direccionRepresentanteLegal = '';
    this.campos = [];
    this.nuevoCampo = { nombre: '', direccion: '', comuna: '' };
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
    this.campos = [];
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

  // 🆕 MÉTODO MODIFICAR CLIENTE ACTUALIZADO PARA INCLUIR REPRESENTANTE LEGAL
  modificarCliente(): void {
    let data = {
      holding: this.holding,
      id: this.selectedClienteId,
      nombre: this.nombreClienteNew,
      rut: this.rutClienteNew.replace(/[\.\-]/g, ''), // Limpiar formato RUT
      direccion: this.direccionClienteNew,
      giro: this.giroClienteNew,
      nombre_rep_legal: this.nombreRepresentanteLegalNew, // 🆕 Incluir nombre rep legal
      direccion_rep_legal: this.direccionRepresentanteLegalNew, // 🆕 Incluir dirección rep legal
      camposPersonalizados: this.camposNew
    };
    
    console.log('🔄 Datos a enviar para modificar:', data);
    
    this.apiService.put('api_clientes/', data).subscribe({
      next: (response) => {
        console.log('✅ Cliente actualizado:', response);
        this.closeModal('modificarCliente');
        this.cargarClientes();
        this.openModal('exitoModal');
      },
      error: (error) => {
        console.error('❌ Error al modificar cliente:', error);
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

  // 🆕 MÉTODO SELECT ROW ACTUALIZADO PARA INCLUIR DATOS DE REPRESENTANTE LEGAL
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
        nombre_rep_legal_seleccionado: lastSelectedRow.nombre_rep_legal || '', // 🆕 Agregar rep legal
        direccion_rep_legal_seleccionado: lastSelectedRow.direccion_rep_legal || '', // 🆕 Agregar dirección rep legal
      };
      
      // Actualizar variables para el formulario de modificación
      this.selectedClienteId = this.clienteSeleccionado.id_cliente_seleccionado;
      this.nombreClienteNew = this.clienteSeleccionado.nombre_cliente_seleccionado;
      this.rutClienteNew = this.formatRUTString(this.clienteSeleccionado.rut_cliente_seleccionado);
      this.direccionClienteNew = this.clienteSeleccionado.direccion_cliente_seleccionado;
      this.giroClienteNew = this.clienteSeleccionado.giro_cliente_seleccionado;
      // 🆕 ACTUALIZAR VARIABLES DE REPRESENTANTE LEGAL
      this.nombreRepresentanteLegalNew = this.clienteSeleccionado.nombre_rep_legal_seleccionado;
      this.direccionRepresentanteLegalNew = this.clienteSeleccionado.direccion_rep_legal_seleccionado;

      this.cargarCampos(this.selectedClienteId!);
    } else {
      this.clienteSeleccionado = {
        nombre_cliente_seleccionado: '',
        rut_cliente_seleccionado: '',
        direccion_cliente_seleccionado: '',
        giro_cliente_seleccionado: '',
        nombre_rep_legal_seleccionado: '',
        direccion_rep_legal_seleccionado: '',
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