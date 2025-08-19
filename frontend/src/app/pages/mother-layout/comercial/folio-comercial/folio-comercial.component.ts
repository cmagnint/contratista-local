//folio-comercial.component.ts
import { Component, Inject, OnInit, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser, CommonModule } from '@angular/common';
import { ContratistaApiService } from '../../../../services/contratista-api.service';
import { ReactiveFormsModule } from '@angular/forms';
import { FormsModule } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';
import { JwtService } from '../../../../services/jwt.service';

@Component({
  selector: 'app-folio-comercial',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatTableModule,
    FormsModule
  ],
  templateUrl: './folio-comercial.component.html',
  styleUrl: './folio-comercial.component.css'
})
export class FolioComercialComponent implements OnInit {
  public modals: { [key: string]: boolean } = {
    exitoModal: false,
    errorModal: false,
    crearFolio: false,
    modificarFolio: false,
    confirmacionModal: false,
    clienteModal: false,
    fundosModal: false,
    laboresModal: false,
    transportistasModal: false,
    vehiculosModal: false,
  };

  public holding: string = ''; 

  public folioSeleccionado: any = {
    id_folio_seleccionadoNew: 0,
    id_cliente_seleccionadoNew: 0,
    ids_labores_seleccionadasNew: [],
    ids_fundos_seleccionadosNew: [],
    ids_transportistas_seleccionadosNew: [],
    ids_vehiculos_seleccionadosNew: [],
    fecha_inicio_contratoNew: new Date(),
    fecha_termino_contratoNew: new Date(),
    valor_pago_trabajadorNew: 0,
    valor_facturacionNew: 0,
    estado_folio_seleccionado: true,
  }

  selectedClienteId: number | null = null;
  selectedFundosNew: any[] = [];
  selectedLaboresNew: any[] = [];
  selectedTransportistasNew: any[] = [];
  selectedVehiculosNew: any[] = [];

  errorMessage!: string;
  selectedRows: any[] = [];
  dropdownOpen: boolean = false;
  dropdownOpenLabores: boolean = false;
  dropdownOpenTransportistas: boolean = false;
  dropdownOpenVehiculos: boolean = false;
  public todasSeleccionadas: boolean = false;
  public dropdownOpenCliente: boolean = false;

  public foliosCargados: any[] = [];
  public clientesCargados: any[] = [];
  public fundosCargados: any[] = [];
  public laboresCargadas: any[] = [];
  public transportistasCargados: any[] = [];
  public vehiculosCargados: any[] = [];
  public choferesCargados: any[] = [];

  columnasDesplegadas = ['codigo','cliente', 'fundos', 'labores', 'transportistas', 'vehiculos', 'fecha_inicio_contrato', 
  'fecha_termino_contrato', 'valor_pago_trabajador', 'valor_facturacion','estado'];
  
  public deletedRow: any[] = [];

  constructor(
    private apiService: ContratistaApiService,
    private jwtService: JwtService,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {}

  ngOnInit(): void {
    if (isPlatformBrowser(this.platformId)) {
      this.holding = this.getHoldingIdFromJWT();
      this.cargarFolio();
      this.cargarClientes();
      this.cargarFundos();
      this.cargarLabores();
      this.cargarEmpresas();
      this.cargarChoferes();
      this.cargarVehiculos();
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

  crearFolio(): void {
    let data = {
      holding: parseInt(this.holding),
      cliente: this.selectedClienteId,
      fundos_ids: this.selectedFundosNew,   // Changed from fundos
      labores_ids: this.selectedLaboresNew, // Changed from labores
      
      // Format transportistas data properly
      transportistas_data: this.selectedTransportistasNew.map(transportistaId => ({
        id: transportistaId,
        vehiculos: this.selectedVehiculosNew
          .filter(vehiculoId => {
            const vehiculo = this.vehiculosCargados
              .flatMap(empresa => empresa.vehiculos)
              .find(v => v.id === vehiculoId);
            return vehiculo && this.selectedTransportistasNew.includes(vehiculo.empresa_id);
          })
          .map(vehiculoId => ({ id: vehiculoId }))
      })),
      
      fecha_inicio_contrato: this.folioSeleccionado.fecha_inicio_contratoNew,
      fecha_termino_contrato: this.folioSeleccionado.fecha_termino_contratoNew,
      valor_pago_trabajador: this.folioSeleccionado.valor_pago_trabajadorNew,
      valor_facturacion: this.folioSeleccionado.valor_facturacionNew
    }
    
    this.apiService.post('folio_comercial/', data).subscribe({
      next: (response) => {
        console.log(response);
        this.closeModal('crearFolio');
        this.cargarFolio();
        this.openModal('exitoModal');
      }, error: (error) => {
        this.openModal('errorModal');
      }
    })
  }

  cargarFolio(): void {
    this.apiService.get(`folio_comercial/?holding=${this.holding}`).subscribe({
      next: (response) => {
        this.foliosCargados = response;
      },
      error: (error) => {
        console.error('Error al recibir los folios:', error);
      }
    });
  }

  modificarFolio(): void {
    // Crear el objeto con la estructura correcta
    const data = {
      id: this.folioSeleccionado.id_folio_seleccionadoNew,
      cliente: this.selectedClienteId, // Asegúrate de que este es el ID del cliente
      fundos_ids: this.selectedFundosNew,
      labores_ids: this.selectedLaboresNew,
      transportistas_data: this.selectedTransportistasNew.map(transportistaId => ({
        id: transportistaId,
        vehiculos: this.selectedVehiculosNew
          .filter(vehiculoId => {
            const vehiculo = this.vehiculosCargados
              .flatMap(empresa => empresa.vehiculos)
              .find(v => v.id === vehiculoId);
            return vehiculo && this.selectedTransportistasNew.includes(vehiculo.empresa_id);
          })
          .map(vehiculoId => ({ id: vehiculoId }))
      })),
      fecha_inicio_contrato: this.folioSeleccionado.fecha_inicio_contratoNew,
      fecha_termino_contrato: this.folioSeleccionado.fecha_termino_contratoNew,
      valor_pago_trabajador: this.folioSeleccionado.valor_pago_trabajadorNew,
      valor_facturacion: this.folioSeleccionado.valor_facturacionNew
    };
  
    console.log('Datos a enviar:', data); // Para depuración
  
    this.apiService.put('folio_comercial/', data).subscribe({
      next: (response) => {
        console.log('Respuesta exitosa:', response);
        this.closeModal('modificarFolio');
        this.cargarFolio();
        this.openModal('exitoModal');
      },
      error: (error) => {
        console.log('Error completo:', error);
        this.errorMessage = error.error?.message || 'Error al modificar el folio';
        this.openModal('errorModal');
      }
    });
  }

  eliminarFolioSeleccionados(): void {
    if (this.deletedRow.length > 0) {
      const idsToDelete = this.deletedRow.map(row => row.id);
      this.apiService.delete('folio_comercial/', { ids: idsToDelete }).subscribe({
        next: () => {
          this.closeModal('confirmacionModal');
          this.cargarFolio();
          this.openModal('exitoModal');
          this.deletedRow = []; // Limpiar la selección después de eliminar
        },
        error: (error) => {
          this.openModal('errorModal');
          console.error('Error al eliminar folios:', error);
        }
      });
    }
  }

  cargarClientes(): void {
    this.apiService.get(`api_clientes/?holding=${this.holding}`).subscribe({
      next: (response) => {
        if (response.length > 0) {
          this.clientesCargados = response.map((cliente: any) => ({
            id: cliente.id,
            name: cliente.nombre
          }));
        }
      },
      error: (error) => {
        console.error('Error al recibir los clientes:', error);
      }
    });
  }

  cargarFundos(): void {
    this.apiService.get(`api_campos_clientes/?holding_id=${this.holding}`).subscribe({
      next: (response) => {
        if (response.length > 0) {
          const fundosPorCliente: { [key: string]: any[] } = {};
          response.forEach((fundo: any) => {
            if (!fundosPorCliente[fundo.nombre_cliente]) {
              fundosPorCliente[fundo.nombre_cliente] = [];
            }
            fundosPorCliente[fundo.nombre_cliente].push({
              cliente_id: fundo.cliente,
              id: fundo.id,
              nombre: fundo.nombre_campo
            });
          });
          this.fundosCargados = Object.keys(fundosPorCliente).map(clienteId => ({
            nombre: this.clientesCargados.find(cliente => cliente.id.toString() === clienteId)?.name || clienteId,
            fundos: fundosPorCliente[clienteId],
          }));
        }
      },
      error: (error) => {
        console.error('Error al cargar fundos:', error);
      }
    });
  }

  cargarLabores(): void {
    this.apiService.get(`labores_comercial/?holding=${this.holding}`).subscribe({
      next: (response) => {
        this.laboresCargadas = response.map((labor: any) => ({
          id: labor.id,
          nombre: labor.nombre,
          holding: labor.holding,
          estado: labor.estado
        }));
      },
      error: (error) => {
        console.error('Error al recibir las labores:', error);
      }
    });
  }

  cargarEmpresas(): void {
    this.apiService.get(`api_empresa_transportes/?holding=${this.holding}`).subscribe({
      next: (response) => {
        this.transportistasCargados = response;
      },
      error: (error) => {
        console.error('Error al recibir las empresas de transporte:', error);
      }
    });
  }

  cargarVehiculos(): void {
    this.apiService.get(`api_vehiculos_transportes/?holding=${this.holding}`).subscribe({
      next: (response) => {
        const vehiculosPorEmpresa: { [key: string]: any[] } = {};
        response.forEach((vehiculo: any) => {
          if (!vehiculosPorEmpresa[vehiculo.empresa]) {
            vehiculosPorEmpresa[vehiculo.empresa] = [];
          }
          vehiculosPorEmpresa[vehiculo.empresa].push({
            empresa_id: vehiculo.empresa,
            id: vehiculo.id,
            ppu: vehiculo.ppu,
            modelo: vehiculo.modelo,
            chofer: this.choferesCargados.find(chofer => chofer.vehiculo == vehiculo.id)?.nombre || 'SIN CHOFER'
          });
        });
        this.vehiculosCargados = Object.keys(vehiculosPorEmpresa).map(empresaId => ({
          nombre: this.transportistasCargados.find(empresa => empresa.id.toString() === empresaId)?.nombre || empresaId,
          vehiculos: vehiculosPorEmpresa[empresaId],
        }));
      },
      error: (error) => {
        console.error('Error al recibir los vehículos:', error);
      }
    });
  }

  cargarChoferes(): void {
    this.apiService.get(`api_choferes_transportes/?holding=${this.holding}`).subscribe({
      next: (response) => {
        this.choferesCargados = response.map((chofer: any) => ({
          id: chofer.id,
          nombre: chofer.nombre,
          empresa: chofer.empresa,
          vehiculo: chofer.vehiculo
        }));
      },
      error: (error) => {
        console.error('Error al recibir los choferes:', error);
      }
    });
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
        console.log(lastSelectedRow);
        
        // Actualizar cliente seleccionado
        this.selectedClienteId = lastSelectedRow.cliente;
        
        // Actualizar fundos seleccionados
        this.selectedFundosNew = lastSelectedRow.fundos ? lastSelectedRow.fundos.map((fundo: any) => fundo.id) : [];
        
        // Actualizar labores seleccionadas
        this.selectedLaboresNew = lastSelectedRow.labores ? lastSelectedRow.labores.map((labor: any) => labor.id) : [];
        
        // Actualizar transportistas y vehículos seleccionados
        // Aquí necesitamos buscar los IDs basados en los nombres
        if (lastSelectedRow.nombres_transportistas) {
            const transportistasNames = lastSelectedRow.nombres_transportistas.split(',').map((name: string) => name.trim());
            this.selectedTransportistasNew = this.transportistasCargados
                .filter(t => transportistasNames.includes(t.nombre))
                .map(t => t.id);
        } else {
            this.selectedTransportistasNew = [];
        }

        if (lastSelectedRow.nombres_vehiculos) {
            const vehiculosModelos = lastSelectedRow.nombres_vehiculos.split(',').map((name: string) => name.trim());
            this.selectedVehiculosNew = this.vehiculosCargados
                .flatMap(empresa => empresa.vehiculos)
                .filter(v => vehiculosModelos.some((modelo: string | any[]) => modelo.includes(v.modelo)))
                .map(v => v.id);
        } else {
            this.selectedVehiculosNew = [];
        }
        
        // Actualizar el resto de datos del folio
        this.folioSeleccionado = {
            id_folio_seleccionadoNew: lastSelectedRow.id,
            id_cliente_seleccionadoNew: lastSelectedRow.cliente,
            ids_fundos_seleccionadosNew: this.selectedFundosNew,
            ids_labores_seleccionadasNew: this.selectedLaboresNew,
            ids_transportistas_seleccionadosNew: this.selectedTransportistasNew,
            ids_vehiculos_seleccionadosNew: this.selectedVehiculosNew,
            fecha_inicio_contratoNew: lastSelectedRow.fecha_inicio_contrato,
            fecha_termino_contratoNew: lastSelectedRow.fecha_termino_contrato,
            valor_pago_trabajadorNew: lastSelectedRow.valor_pago_trabajador,
            valor_facturacionNew: lastSelectedRow.valor_facturacion,
            estado_folio_seleccionado: lastSelectedRow.estado
        };
    } else {
        this.resetForm();
    }
}
  resetForm(): void {
    // Reset selected IDs
    this.selectedClienteId = null;
    this.selectedFundosNew = [];
    this.selectedLaboresNew = [];
    this.selectedTransportistasNew = [];
    this.selectedVehiculosNew = [];
    
    // Reset folio selection object
    this.folioSeleccionado = {
        id_folio_seleccionadoNew: 0,
        id_cliente_seleccionadoNew: 0,
        ids_labores_seleccionadasNew: [],
        ids_fundos_seleccionadosNew: [],
        ids_transportistas_seleccionadosNew: [],
        ids_vehiculos_seleccionadosNew: [],
        fecha_inicio_contratoNew: new Date(),
        fecha_termino_contratoNew: new Date(),
        valor_pago_trabajadorNew: 0,
        valor_facturacionNew: 0,
        estado_folio_seleccionado: true,
    };

    // Reset all dropdown states
    this.dropdownOpen = false;
    this.dropdownOpenCliente = false;
    this.dropdownOpenLabores = false;
    this.dropdownOpenTransportistas = false;
    this.dropdownOpenVehiculos = false;
    
    // Reset any selection flags
    this.todasSeleccionadas = false;
}

  toggleSelectionCliente(clienteId: number): void {
    if (this.selectedClienteId === clienteId) {
      this.selectedClienteId = null;
    } else {
      this.selectedClienteId = clienteId;
    }
  }

  toggleSelection(id: number, list: number[], total: any[]): void {
    const index = list.indexOf(id);
    if (index > -1) {
      list.splice(index, 1);
    } else {
      list.push(id);
    }
    this.todasSeleccionadas = list.length === total.length;
  }

  toggleDropdownCliente() {
    this.dropdownOpenCliente = !this.dropdownOpenCliente;
  }

  toggleDropdownLabores() {
    this.dropdownOpenLabores = !this.dropdownOpenLabores;
  }

  toggleDropdownTransportistas() {
    this.dropdownOpenTransportistas = !this.dropdownOpenTransportistas;
  }

  toggleDropdownVehiculos() {
    this.dropdownOpenVehiculos = !this.dropdownOpenVehiculos;
  }

  formatNumber(event: Event): void {
    const target = event.target as HTMLInputElement;
    if (!target) return;
    target.value = target.value.replace(/[^\d]/g, '');
  }

  toggleDropdown() {
    this.dropdownOpen = !this.dropdownOpen;
  }

  deseleccionarFila(event: MouseEvent) {
    this.selectedRows = [];
  }

  openModal(key: string): void {
    this.modals[key] = true;
    if (key === 'confirmacionModal') {
      this.deletedRow = this.selectedRows;
    }
    if (key === 'crearFolio'){
      this.resetForm();
    }
  }

  closeModal(key: string): void {
    this.modals[key] = false;
    if (key === 'exitoModal') {
      this.cargarFolio();
    }
  }
}
