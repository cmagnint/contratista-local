import { Component, Inject, OnInit, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser, CommonModule } from '@angular/common';
import { ContratistaApiService } from '../../../../services/contratista-api.service';
import { ReactiveFormsModule } from '@angular/forms';
import { FormsModule } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';
import { JwtService } from '../../../../services/jwt.service';
@Component({
  selector: 'app-contactos-clientes',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatTableModule,
    FormsModule
  ],
  templateUrl: './contactos-clientes.component.html',
  styleUrl: './contactos-clientes.component.css'
})
export class ContactosClientesComponent implements OnInit {
  public modals: { [key: string]: boolean } = {
    exitoModal: false,
    errorModal: false,
    crearContacto: false,
    modificarContacto: false,
    confirmacionModal: false,
  };

  public nuevoContacto: any = {
    nombre_contacto: '',
    rut_contacto: '',
    telefono: '',
    correo: '',
    cliente: null,
    campo_cliente: null,
    area_cliente: null,
    cargo_cliente: null
  };

  public contactoSeleccionado: any = {
    nombre_contacto: '',
    rut_contacto: '',
    telefono: '',
    correo: '',
    cliente: null,
    campo_cliente: null,
    area_cliente: null,
    cargo_cliente: null
  };

  public campoPorCliente: any = {
    idCliente: 0,
    campos: [],
  }

  public dropdownOpenCliente: boolean = false;
  public dropdownOpenAreaCliente: boolean = false;
  public dropdownOpenCargoCliente: boolean = false;
  public dropdownOpenCampoCliente: boolean = false;
  public camposClientes: any[] = [];
  public areasCargadas: any[] = [];
  public cargosClientes: any[] = [];
  public contactosCargados: any[] = [];
  public clientesCargados: any[] = [];
  public holding: string = '';
  public selectedRows: any[] = [];
  public errorMessage!: string;
  public deletedRow: any[] = [];
  columnasDesplegadasContactos = ['nombre_contacto', 'rut_contacto', 
  'telefono', 'correo', 'cliente', 'campo_cliente', 'area_cliente', 'cargo_cliente'];

  constructor(
    private apiService: ContratistaApiService,
    private jwtService: JwtService,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {}

  ngOnInit(): void {
    if (isPlatformBrowser(this.platformId)) {
      this.holding = this.getHoldingIdFromJWT();
      this.cargarClientes();
      this.cargarAreas();
      this.cargarCargosClientes();
      this.cargarContactos();
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


  cargarClientes(): void {
    this.apiService.get(`api_clientes/?holding=${this.holding}`).subscribe({
      next: (response) => {
        this.clientesCargados = response;
      },
      error: (error) => {
        console.error('Error al recibir los clientes:', error);
      },
    });
  }

  cargarAreas(): void {
    this.apiService.get(`api_areas_cliente/?holding=${this.holding}`).subscribe({
      next: (response) => {
        this.areasCargadas = response;
      },
      error: (error) => {
        console.error('Error al recibir las áreas:', error);
      },
    });
  }

  cargarCargosClientes(): void {
    this.apiService.get(`api_cargos_cliente/?holding=${this.holding}`).subscribe({
      next: (response) => {
        if(response.length > 0) {
          const cargosPorArea: { [key: string]: any[] } = {};
          response.forEach((cargo: any) => {
            if (!cargosPorArea[cargo.area]) {
              cargosPorArea[cargo.area] = [];
            }
            cargosPorArea[cargo.area].push({
              area_id: cargo.area,
              id: cargo.id,
              name: cargo.nombre,
              isAvailable: false,
            });
          });
          this.cargosClientes = Object.keys(cargosPorArea).map(areaId => ({
            area_id: parseInt(areaId, 10),
            cargos: cargosPorArea[areaId],
          }));
        } else {
          console.log('No se encontraron cargos');
        }
      }, 
      error: (error) => {
        console.error('Error al recibir los cargos:', error);
      }
    });
  }

  cargarContactos(): void {
    this.apiService.get(`api_contactos_clientes/?holding=${this.holding}`).subscribe({
      next: (response) => {
        this.contactosCargados = response;
      },
      error: (error) => {
        console.error('Error al recibir los contactos de clientes:', error);
      },
    });
  }

  crearContacto(): void {
    let data = {
      holding: this.holding,
      cliente: this.nuevoContacto.cliente,
      campo_cliente: this.nuevoContacto.campo_cliente,
      area_cliente: this.nuevoContacto.area_cliente,
      cargo_cliente: this.nuevoContacto.cargo_cliente,
      nombre_contacto:  this.nuevoContacto.nombre_contacto,
      rut_contacto: this.nuevoContacto.rut_contacto.replace(/\D/g, ''),
      telefono: this.nuevoContacto.telefono,
      correo: this.nuevoContacto.correo,
    }
    this.apiService.post('api_contactos_clientes/', data).subscribe({
      next: (response) => {
        this.closeModal('crearContacto');
        this.cargarContactos();
        this.openModal('exitoModal');
      },
      error: (error) => {
        this.openModal('errorModal');
      },
    });
  }

  modificarContacto(): void {
    this.apiService.put('api_contactos_clientes/', this.contactoSeleccionado).subscribe({
      next: (response) => {
        this.closeModal('modificarContacto');
        this.cargarContactos();
        this.openModal('exitoModal');
      },
      error: (error) => {
        this.openModal('errorModal');
      },
    });
  }

  eliminarContactosSeleccionados(): void {
    if (this.deletedRow.length > 0) {
      const idsToDelete = this.deletedRow.map((row) => row.id);
      this.apiService.delete('api_contactos_clientes/', { ids: idsToDelete }).subscribe({
        next: () => {
          this.closeModal('confirmacionModal');
          this.cargarContactos();
          this.openModal('exitoModal');
          this.deletedRow = []; // Limpiar la selección después de eliminar
        },
        error: (error) => {
          this.openModal('errorModal');
          console.error('Error al eliminar contactos:', error);
        },
      });
    }
  }

  toggleSelection(contactoId: number): void {
    if (this.contactoSeleccionado.id === contactoId) {
      this.contactoSeleccionado.id = null; // Deseleccionar si el mismo contacto es clickeado nuevamente
    } else {
      this.contactoSeleccionado.id = contactoId; // Seleccionar el nuevo contacto
    }
  }

  toggleDropdownCliente() {
    this.dropdownOpenCliente = !this.dropdownOpenCliente;
  }

  toggleDropdownAreaCliente() {
    this.dropdownOpenAreaCliente = !this.dropdownOpenAreaCliente;
  }

  toggleDropdownCargoCliente() {
    this.dropdownOpenCargoCliente = !this.dropdownOpenCargoCliente;
  }

  toggleDropdownCampoCliente() {
    this.dropdownOpenCampoCliente = !this.dropdownOpenCampoCliente;
  }

  toggleSelectionCliente(clienteId: number): void {
    if (this.nuevoContacto.cliente === clienteId) {
      this.nuevoContacto.cliente = null;  // Deseleccionar si el mismo cliente es clickeado nuevamente
    } else {
      this.nuevoContacto.cliente = clienteId;  // Seleccionar el nuevo cliente
    }
    this.nuevoContacto.campo_cliente = null;  // Reset campo cuando se cambia el cliente
  }

  toggleSelectionArea(areaId: number): void {
    if (this.nuevoContacto.area_cliente === areaId) {
      this.nuevoContacto.area_cliente = null;  // Deseleccionar si el mismo área es clickeado nuevamente
    } else {
      this.nuevoContacto.area_cliente = areaId;  // Seleccionar el nuevo área
    }
    this.nuevoContacto.cargo_cliente = null;  // Reset cargo cuando se cambia el área
  }

  toggleSelectionCargo(cargoId: number): void {
    if (this.nuevoContacto.cargo_cliente === cargoId) {
      this.nuevoContacto.cargo_cliente = null;  // Deseleccionar si el mismo cargo es clickeado nuevamente
    } else {
      this.nuevoContacto.cargo_cliente = cargoId;  // Seleccionar el nuevo cargo
    }
  }

  isSelected(row: any): boolean {
    return this.selectedRows.some((r) => r.id === row.id);
  }

  selectRow(row: any): void {
    const index = this.selectedRows.findIndex((selectedRow) => selectedRow.id === row.id);
    if (index > -1) {
      this.selectedRows.splice(index, 1); // Si la fila ya está seleccionada, deseleccionarla
    } else {
      this.selectedRows.push(row); // Agregar fila a las seleccionadas
    }

    if (this.selectedRows.length > 0) {
      const lastSelectedRow = this.selectedRows[this.selectedRows.length - 1];
      this.contactoSeleccionado = lastSelectedRow;
    } else {
      this.contactoSeleccionado = {
        nombre_contacto: '',
        rut_contacto: '',
        telefono: '',
        correo: '',
        cliente: null,
        campo_cliente: null,
        area_cliente: null,
        cargo_cliente: null
      };
    }
  }

  deseleccionarFila(event: MouseEvent) {
    this.selectedRows = []; // Deselecciona todas las filas
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
      this.cargarContactos();
    }
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

  checkValue(): void {}
}
