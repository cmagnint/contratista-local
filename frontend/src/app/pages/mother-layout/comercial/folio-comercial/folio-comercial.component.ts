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
    horariosModal: false,
  };

  public holding: string = ''; 

  public folioSeleccionado: any = {
    id_folio_seleccionadoNew: 0,
    id_cliente_seleccionadoNew: 0,
    ids_labores_seleccionadasNew: [],
    ids_fundos_seleccionadosNew: [],
    ids_transportistas_seleccionadosNew: [],
    ids_vehiculos_seleccionadosNew: [],
    ids_horarios_seleccionadosNew: [],
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
  selectedHorariosNew: any[] = [];
  laboresValores: { [key: number]: { valor_pago_trabajador: number, valor_facturacion: number } } = {};
  public tableExpansionState: { [key: string]: boolean } = {};

  errorMessage!: string;
  selectedRows: any[] = [];
  dropdownOpen: boolean = false;
  dropdownOpenLabores: boolean = false;
  dropdownOpenTransportistas: boolean = false;
  dropdownOpenVehiculos: boolean = false;
  dropdownOpenHorarios: boolean = false;
  public todasSeleccionadas: boolean = false;
  public dropdownOpenCliente: boolean = false;

  public foliosCargados: any[] = [];
  public clientesCargados: any[] = [];
  public fundosCargados: any[] = [];
  public laboresCargadas: any[] = [];
  public transportistasCargados: any[] = [];
  public vehiculosCargados: any[] = [];
  public choferesCargados: any[] = [];
  public horariosCargados: any[] = [];

  columnasDesplegadas = ['codigo','cliente', 'fundos', 'labores', 'transportistas', 'vehiculos',  'horarios','fecha_inicio_contrato', 
  'fecha_termino_contrato','estado'];
  
  public deletedRow: any[] = [];

  constructor(
    private apiService: ContratistaApiService,
    private jwtService: JwtService,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {}

  ngOnInit(): void {
    if (isPlatformBrowser(this.platformId)) {
      this.holding = this.getHoldingIdFromJWT();
      console.log('HOLDING:', this.holding);
      this.cargarFolio();
      this.cargarClientes();
      this.cargarFundos();
      this.cargarLabores();
      this.cargarEmpresas();
      this.cargarChoferes();
      this.cargarVehiculos();
      this.cargarHorarios();
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

  isLaborSelected(laborId: number): boolean {
    return this.selectedLaboresNew.includes(laborId);
  }


  toggleLaborSelection(labor: any): void {
    const index = this.selectedLaboresNew.indexOf(labor.id);
    if (index > -1) {
      this.selectedLaboresNew.splice(index, 1);
      delete this.laboresValores[labor.id];
    } else {
      this.selectedLaboresNew.push(labor.id);
      this.laboresValores[labor.id] = {
        valor_pago_trabajador: 0,
        valor_facturacion: 0
      };
    }
  }

  crearFolio(): void {
    const laboresData = this.selectedLaboresNew.map(laborId => ({
      id: laborId,
      valor_pago_trabajador: this.laboresValores[laborId]?.valor_pago_trabajador || 0,
      valor_facturacion: this.laboresValores[laborId]?.valor_facturacion || 0
    }));

    const transportistasData = this.selectedTransportistasNew.map(transportistaId => {
      const vehiculos = this.selectedVehiculosNew
        .filter(vehiculoId => {
          const empresa = this.vehiculosCargados.find(e => 
            e.vehiculos.some((v: { id: any; }) => v.id === vehiculoId)
          );
          return empresa?.vehiculos.find((v: { id: any; empresa_id: any; }) => v.id === vehiculoId)?.empresa_id === transportistaId;
        })
        .map(vehiculoId => ({ id: vehiculoId }));
      
      return { id: transportistaId, vehiculos };
    });

    const payload = {
      holding: parseInt(this.holding),
      cliente: this.selectedClienteId,
      fundos_ids: this.selectedFundosNew,
      labores_data: laboresData,
      horarios_ids: this.selectedHorariosNew,
      transportistas_data: transportistasData,
      fecha_inicio_contrato: this.folioSeleccionado.fecha_inicio_contratoNew,
      fecha_termino_contrato: this.folioSeleccionado.fecha_termino_contratoNew
    };

    this.apiService.post('folio_comercial/', payload).subscribe({
      next: () => {
        this.openModal('exitoModal');
        this.cargarFolio();
        this.closeModal('crearFolio');
        this.resetForm();
      },
      error: (error) => {
        this.errorMessage = error.error?.message || 'Error al crear el folio';
        this.openModal('errorModal');
      }
    });
  }

  cargarFolio(): void {
    this.apiService.get(`folio_comercial/?holding=${this.holding}`).subscribe({
      next: (response) => {
        console.log('📦 Folios recibidos del backend:', response);
        
        // Debug: verificar estructura del primer folio
        if (response.length > 0) {
          console.log('🔍 Estructura del primer folio:', response[0]);
          console.log('🔍 ¿Tiene labores_detalle?', response[0].labores_detalle);
          console.log('🔍 ¿Tipo de labores_detalle?', typeof response[0].labores_detalle);
          console.log('🔍 nombres_labores:', response[0].nombres_labores);
        }
        
        this.foliosCargados = response;
      },
      error: (error) => {
        console.error('Error al recibir los folios:', error);
      }
    });
  }

  /**
 * ✅ PARSEAR LABORES DESDE STRING
 */
parseLaboresFromString(folio: any): any[] {
  // Si ya existe labores_detalle, usarlo
  if (folio.labores_detalle && folio.labores_detalle.length > 0) {
    return folio.labores_detalle;
  }
  
  // Si no hay nombres_labores, retornar array vacío
  if (!folio.nombres_labores) return [];
  
  const laboresArray: any[] = [];
  
  // Split por comas para separar múltiples labores
  const laboresStrings = folio.nombres_labores.split(/,(?![^()]*\))/);
  
  laboresStrings.forEach((laborString: string, index: number) => {
    // Regex para extraer: NOMBRE (Pago: $XXXX, Fact: $YYYY)
    const match = laborString.trim().match(/^(.+?)\s*\(Pago:\s*\$(\d+),\s*Fact:\s*\$(\d+)\)$/);
    
    if (match) {
      laboresArray.push({
        id: `${folio.id}_labor_${index}`, // ID único combinando folio + índice
        nombre: match[1].trim(),
        valor_pago_trabajador: parseInt(match[2]),
        valor_facturacion: parseInt(match[3])
      });
    }
  });
  
  console.log(`🔍 Labores parseadas para folio ${folio.id}:`, laboresArray);
  
  return laboresArray;
}


  modificarFolio(): void {
  const laboresData = this.selectedLaboresNew.map(laborId => ({
    id: laborId,
    valor_pago_trabajador: this.laboresValores[laborId]?.valor_pago_trabajador || 0,
    valor_facturacion: this.laboresValores[laborId]?.valor_facturacion || 0
  }));

  const transportistasData = this.selectedTransportistasNew.map(transportistaId => {
    const vehiculos = this.selectedVehiculosNew
      .filter(vehiculoId => {
        const empresa = this.vehiculosCargados.find(e => 
          e.vehiculos.some((v: { id: any; }) => v.id === vehiculoId)
        );
        return empresa?.vehiculos.find((v: { id: any; empresa_id: any; }) => v.id === vehiculoId)?.empresa_id === transportistaId;
      })
      .map(vehiculoId => ({ id: vehiculoId }));
    
    return { id: transportistaId, vehiculos };
  });

  const payload = {
    id: this.folioSeleccionado.id_folio_seleccionadoNew,
    holding: parseInt(this.holding),
    cliente: this.selectedClienteId,
    fundos_ids: this.selectedFundosNew,
    labores_data: laboresData,
    horarios_ids: this.selectedHorariosNew,
    transportistas_data: transportistasData,
    fecha_inicio_contrato: this.folioSeleccionado.fecha_inicio_contratoNew,
    fecha_termino_contrato: this.folioSeleccionado.fecha_termino_contratoNew
  };

  this.apiService.put('folio_comercial/', payload).subscribe({
    next: () => {
      this.openModal('exitoModal');
      this.cargarFolio();
      this.closeModal('modificarFolio');
      this.resetForm();
    },
    error: (error) => {
      this.errorMessage = error.error?.message || 'Error al modificar el folio';
      this.openModal('errorModal');
    }
  });
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
    console.log('🔍 Fila seleccionada:', lastSelectedRow);
    
    this.selectedClienteId = lastSelectedRow.cliente;
    this.selectedFundosNew = lastSelectedRow.fundos ? lastSelectedRow.fundos.map((fundo: any) => fundo.id) : [];
    this.selectedHorariosNew = lastSelectedRow.horarios ? lastSelectedRow.horarios.map((horario: any) => horario.id) : [];
    
    // ✅ NUEVO: Usar parseLaboresFromString para obtener los valores correctos
    const laboresParsed = this.parseLaboresFromString(lastSelectedRow);
    console.log('🔍 Labores parseadas para modificar:', laboresParsed);
    
    if (laboresParsed.length > 0) {
      this.selectedLaboresNew = [];
      this.laboresValores = {};
      
      // Buscar el ID real de cada labor comparando con laboresCargadas
      laboresParsed.forEach((laborParsed: any) => {
        const laborReal = this.laboresCargadas.find(l => l.nombre === laborParsed.nombre);
        
        if (laborReal) {
          this.selectedLaboresNew.push(laborReal.id);
          this.laboresValores[laborReal.id] = {
            valor_pago_trabajador: laborParsed.valor_pago_trabajador,
            valor_facturacion: laborParsed.valor_facturacion
          };
          
          console.log(`✅ Labor "${laborReal.nombre}" cargada:`, {
            id: laborReal.id,
            pago: laborParsed.valor_pago_trabajador,
            fact: laborParsed.valor_facturacion
          });
        } else {
          console.warn(`⚠️ No se encontró la labor "${laborParsed.nombre}" en laboresCargadas`);
        }
      });
    } else {
      this.selectedLaboresNew = [];
      this.laboresValores = {};
    }
    
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
        .filter((v: { modelo: any; }) => vehiculosModelos.some((modelo: string | any[]) => modelo.includes(v.modelo)))
        .map((v: { id: any; }) => v.id);
    } else {
      this.selectedVehiculosNew = [];
    }
    
    this.folioSeleccionado = {
      id_folio_seleccionadoNew: lastSelectedRow.id,
      id_cliente_seleccionadoNew: lastSelectedRow.cliente,
      ids_fundos_seleccionadosNew: this.selectedFundosNew,
      ids_labores_seleccionadasNew: this.selectedLaboresNew,
      ids_transportistas_seleccionadosNew: this.selectedTransportistasNew,
      ids_vehiculos_seleccionadosNew: this.selectedVehiculosNew,
      ids_horarios_seleccionadosNew: this.selectedHorariosNew,
      fecha_inicio_contratoNew: lastSelectedRow.fecha_inicio_contrato,
      fecha_termino_contratoNew: lastSelectedRow.fecha_termino_contrato,
      estado_folio_seleccionado: lastSelectedRow.estado
    };
    
    console.log('✅ Estado final después de seleccionar:', {
      laboresSeleccionadas: this.selectedLaboresNew,
      valoresLabores: this.laboresValores
    });
  } else {
    this.resetForm();
  }
}

/**
 * ✅ VERIFICAR SI UNA LABOR ESTÁ EXPANDIDA EN TABLA
 */
isLaborExpandedInTable(folioId: number, laborId: number): boolean {
  const key = `folio_${folioId}_labor_${laborId}`;
  return this.tableExpansionState[key] || false;
}

/**
 * ✅ TOGGLE EXPANSIÓN DE LABOR EN TABLA
 */
toggleLaborInTable(folioId: number, laborId: number, event: Event): void {
  event.stopPropagation();
  const key = `folio_${folioId}_labor_${laborId}`;
  this.tableExpansionState[key] = !this.tableExpansionState[key];
}

/**
 * ✅ FORMATEAR MONEDA
 */
formatCurrency(value: number): string {
  if (!value && value !== 0) return '0';
  return value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
}


resetForm(): void {
  this.selectedClienteId = null;
  this.selectedFundosNew = [];
  this.selectedLaboresNew = [];
  this.selectedTransportistasNew = [];
  this.selectedVehiculosNew = [];
  this.selectedHorariosNew = [];
  this.laboresValores = {};
  
  this.folioSeleccionado = {
    id_folio_seleccionadoNew: 0,
    id_cliente_seleccionadoNew: 0,
    ids_labores_seleccionadasNew: [],
    ids_fundos_seleccionadosNew: [],
    ids_transportistas_seleccionadosNew: [],
    ids_vehiculos_seleccionadosNew: [],
    ids_horarios_seleccionadosNew: [],
    fecha_inicio_contratoNew: new Date(),
    fecha_termino_contratoNew: new Date(),
    estado_folio_seleccionado: true,
  };

  this.dropdownOpen = false;
  this.dropdownOpenCliente = false;
  this.dropdownOpenLabores = false;
  this.dropdownOpenTransportistas = false;
  this.dropdownOpenVehiculos = false;
  this.dropdownOpenHorarios = false;
  this.todasSeleccionadas = false;
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

  cargarHorarios(): void {
  this.apiService.get(`horarios/?holding=${this.holding}`).subscribe({
    next: (response) => {
      this.horariosCargados = response.map((horario: any) => ({
        id: horario.id,
        nombre: horario.nombre,
        jornada: horario.jornada
      }));
    },
    error: (error) => {
      console.error('Error al recibir los horarios:', error);
    }
  });
}

  isSelected(row: any): boolean {
    return this.selectedRows.some(r => r.id === row.id);
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

  toggleDropdownHorarios() {
    this.dropdownOpenHorarios = !this.dropdownOpenHorarios;
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

  /**
   * ✅ OBTENER ICONO PARA EXPANSIÓN
   */
  getExpansionIcon(isExpanded: boolean): string {
    return isExpanded ? '▼' : '▶';
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
