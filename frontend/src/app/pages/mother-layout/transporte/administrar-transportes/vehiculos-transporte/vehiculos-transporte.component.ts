import { Component, Inject, OnInit, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser, CommonModule } from '@angular/common';
import { ContratistaApiService } from '../../../../../services/contratista-api.service';
import { ReactiveFormsModule } from '@angular/forms';
import { FormsModule } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';

@Component({
  selector: 'app-vehiculos-transporte',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatTableModule,
    FormsModule
  ],
  templateUrl: './vehiculos-transporte.component.html',
  styleUrl: './vehiculos-transporte.component.css'
})
export class VehiculosTransporteComponent implements OnInit {
  //VARIABLES

  constructor(
    private apiService: ContratistaApiService,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {}

  // Booleanos para abrir o cerrar ventanas
  public modals: { [key: string]: boolean } = {
    exitoModal: false,
    errorModal: false,
    crearVehiculo: false,
    modificarVehiculo: false,
    confirmacionModal: false,
    empresasModal: false,
  };

  //Perfil seleccionado
  public vehiculoSeleccionado: any = {
    ppu_vehiculo_seleccionado: '',
    modelo_vehiculo_seleccionado: '',
    year_vehiculo_seleccionado: 0,
    color_vehiculo_seleccionado: '',
    numero_pasajeros_vehiculo_seleccionado: 0,
    marca_vehiculo_seleccionado: '',
    id_empresa_vehiculo_seleccionado: 0,
    id_vehiculo_seleccionada: 0,
  }

  public holding: string = ''; 
  public nombreEmpresa: string = '';
  public ppuVehiculo: string = '';
  public modeloVehiculo: string = '';
  public tipoVehiculo: string = '';
  public yearVehiculo: number = 0;
  public colorVehiculo: string = '';
  public numeroPasajerosVehiculo: number = 0;
  public marcaVehiculo: string = '';

  errorMessage!: string; 
  selectedRows: any[] = []; 
  dropdownOpen: boolean = false; 

  public todasSeleccionadas: boolean = false;

  public vehiculosCargados: any[] = [];
  public empresasCargadas: any[] = [];

  // AGREGAR NUEVA COLUMNA DE DOCUMENTOS
  columnasDesplegadas = ['empresa','ppu','modelo','tipo','year','color','numero_pasajeros','marca','documentos'];
  
  public ppuVehiculoNew: string = '';
  public modeloVehiculoNew: string = '';
  public tipoVehiculoNew: string = '';
  public yearVehiculoNew: number | null = null;
  public colorVehiculoNew: string = '';
  public numeroPasajerosVehiculoNew: number | null = null;
  public marcaVehiculoNew: string = '';

  public deletedRow: any[] = [];

  public selectedVehiculoId: number | null = null;
  public selectedEmpresaId: number | null = null;

  // NUEVAS PROPIEDADES PARA DOCUMENTOS
  public documentos: File[] = [];
  public documentosModificar: File[] = [];
  public documentosExistentesVehiculo: string[] = [];

  //FUNCIONES
  
  ngOnInit(): void {
    if (isPlatformBrowser(this.platformId)) {
      this.holding = localStorage.getItem('holding_id') || '';
      this.cargarVehiculos();
      this.cargarEmpresas();
    }
  }

  //FUNCIONES CRUD

  crearVehiculos(): void {
    const formData = new FormData();
    
    // Datos básicos del vehículo
    formData.append('holding', this.holding);
    formData.append('empresa', this.selectedEmpresaId?.toString() || '');
    formData.append('ppu', this.ppuVehiculo);
    formData.append('modelo', this.modeloVehiculo);
    formData.append('year', this.yearVehiculo.toString());
    formData.append('color', this.colorVehiculo);
    formData.append('num_pasajeros', this.numeroPasajerosVehiculo.toString());
    formData.append('marca', this.marcaVehiculo);
    formData.append('tipo', this.tipoVehiculo);

    // Agregar documentos
    this.documentos.forEach((doc, index) => {
      formData.append(`documento_${index}`, doc);
    });

    this.apiService.postFormData('api_vehiculos_transportes/', formData).subscribe({
      next: (response) => {
        console.log(response);
        this.closeModal('crearVehiculo');
        this.cargarVehiculos();
        this.openModal('exitoModal');
        this.limpiarFormulario();
      },
      error: (error) => {
        console.log(error);
        this.openModal('errorModal');
      }
    });
  }

  cargarEmpresas(): void {
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

  cargarVehiculos(): void {
    this.apiService.get(`api_vehiculos_transportes/?holding=${this.holding}`).subscribe({
      next: (response) => {
        this.vehiculosCargados = response;
        console.log('Vehículos cargados:', this.vehiculosCargados);
      },
      error: (error) => {
        console.error('Error al recibir las sociedades:', error);
      }
    });
  }

  modificarVehiculos(): void {
    const formData = new FormData();
    
    // Datos básicos del vehículo
    formData.append('holding', this.holding);
    formData.append('id', this.selectedVehiculoId?.toString() || '');
    formData.append('empresa', this.selectedEmpresaId?.toString() || '');
    formData.append('ppu', this.ppuVehiculoNew);
    formData.append('modelo', this.modeloVehiculoNew);
    formData.append('year', this.yearVehiculoNew?.toString() || '');
    formData.append('color', this.colorVehiculoNew);
    formData.append('num_pasajeros', this.numeroPasajerosVehiculoNew?.toString() || '');
    formData.append('marca', this.marcaVehiculoNew);
    formData.append('tipo', this.tipoVehiculoNew);

    // Agregar documentos modificados
    this.documentosModificar.forEach((doc, index) => {
      formData.append(`documento_${index}`, doc);
    });

    this.apiService.putFormData('api_vehiculos_transportes/', formData).subscribe({
      next: (response) => {
        this.closeModal('modificarVehiculo');
        this.cargarVehiculos();
        this.openModal('exitoModal');
        this.limpiarFormularioModificar();
      },
      error: (error) => {
        console.log(error);
        this.openModal('errorModal');
      }
    });
  }
  
  eliminarVehiculosSeleccionados(): void {
    if (this.deletedRow.length > 0) {
      const idsToDelete = this.deletedRow.map(row => row.id);
      this.apiService.delete('api_vehiculos_transportes/', {ids: idsToDelete}).subscribe({
        next: () => {
          this.closeModal('confirmacionModal')
          this.cargarVehiculos();
          this.openModal('exitoModal');
          this.deletedRow = []; 
        },
        error: (error) => {
          this.openModal('errorModal');
          console.error('Error al eliminar perfiles:', error);
        }
      });
    }
  }

  // NUEVOS MÉTODOS PARA MANEJO DE DOCUMENTOS
  onDocumentSelect(event: Event): void {
    const target = event.target as HTMLInputElement;
    if (target.files) {
      const validFormats = ['pdf', 'xlsx', 'xls', 'doc', 'docx', 'txt'];
      
      for (let i = 0; i < target.files.length; i++) {
        const file = target.files[i];
        const extension = file.name.toLowerCase().split('.').pop();
        
        if (!validFormats.includes(extension || '')) {
          this.errorMessage = 'Solo se permiten: PDF, Excel, Word, TXT';
          this.openModal('errorModal');
          return;
        }
        
        this.documentos.push(file);
      }
    }
  }

  onDocumentSelectModificar(event: Event): void {
    const target = event.target as HTMLInputElement;
    if (target.files) {
      const validFormats = ['pdf', 'xlsx', 'xls', 'doc', 'docx', 'txt'];
      
      for (let i = 0; i < target.files.length; i++) {
        const file = target.files[i];
        const extension = file.name.toLowerCase().split('.').pop();
        
        if (!validFormats.includes(extension || '')) {
          this.errorMessage = 'Solo se permiten: PDF, Excel, Word, TXT';
          this.openModal('errorModal');
          return;
        }
        
        this.documentosModificar.push(file);
      }
    }
  }

  removeDocument(index: number): void {
    this.documentos.splice(index, 1);
  }

  removeDocumentModificar(index: number): void {
    this.documentosModificar.splice(index, 1);
  }

  // NUEVO: Verificar si el vehículo tiene documentos
  hasDocuments(vehiculo: any): boolean {
    return vehiculo.documentos_urls && Array.isArray(vehiculo.documentos_urls) && vehiculo.documentos_urls.length > 0;
  }

  // NUEVO: Descargar documento
  descargarDocumento(url: string, nombreArchivo?: string): void {
    const link = document.createElement('a');
    link.href = url;
    link.download = nombreArchivo || 'documento';
    link.target = '_blank';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  // NUEVO: Obtener nombre del archivo desde la URL
  getNombreArchivoDesdeUrl(url: string): string {
    return url.split('/').pop()?.split('?')[0] || 'documento';
  }

  limpiarFormulario(): void {
    this.ppuVehiculo = '';
    this.modeloVehiculo = '';
    this.tipoVehiculo = '';
    this.yearVehiculo = 0;
    this.colorVehiculo = '';
    this.numeroPasajerosVehiculo = 0;
    this.marcaVehiculo = '';
    this.selectedEmpresaId = null;
    this.documentos = []; // Limpiar documentos
  }

  limpiarFormularioModificar(): void {
    this.documentosModificar = []; // Limpiar documentos modificados
    this.documentosExistentesVehiculo = []; // Limpiar documentos existentes
  }

  toggleSelection(empresaId: number): void {
    if (this.selectedEmpresaId === empresaId) {
      this.selectedEmpresaId = null; 
    } else {
      this.selectedEmpresaId = empresaId; 
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
      this.vehiculoSeleccionado = {
        ppu_vehiculo_seleccionado: lastSelectedRow.ppu,
        modelo_vehiculo_seleccionado: lastSelectedRow.modelo,
        tipo_vehiculo_seleccionado: lastSelectedRow.tipo,
        year_vehiculo_seleccionado: lastSelectedRow.year,
        color_vehiculo_seleccionado: lastSelectedRow.color,
        numero_pasajeros_vehiculo_seleccionado: lastSelectedRow.num_pasajeros,
        marca_vehiculo_seleccionado: lastSelectedRow.marca,
        id_vehiculo_seleccionado: lastSelectedRow.id,
        id_empresa_vehiculo_seleccionado: lastSelectedRow.empresa
      };
      this.ppuVehiculoNew = this.vehiculoSeleccionado.ppu_vehiculo_seleccionado
      this.modeloVehiculoNew = this.vehiculoSeleccionado.modelo_vehiculo_seleccionado
      this.tipoVehiculoNew = this.vehiculoSeleccionado.tipo_vehiculo_seleccionado
      this.yearVehiculoNew = this.vehiculoSeleccionado.year_vehiculo_seleccionado
      this.colorVehiculoNew = this.vehiculoSeleccionado.color_vehiculo_seleccionado
      this.numeroPasajerosVehiculoNew = this.vehiculoSeleccionado.numero_pasajeros_vehiculo_seleccionado
      this.marcaVehiculoNew = this.vehiculoSeleccionado.marca_vehiculo_seleccionado
      this.selectedVehiculoId = this.vehiculoSeleccionado.id_vehiculo_seleccionado;
      this.selectedEmpresaId = this.vehiculoSeleccionado.id_empresa_vehiculo_seleccionado;

      // NUEVO: Cargar documentos existentes del vehículo
      this.cargarArchivosVehiculoSeleccionado(lastSelectedRow);

    } else {
      this.vehiculoSeleccionado = {
        ppu_vehiculo_seleccionado: '',
        modelo_vehiculo_seleccionado: '',
        tipo_vehiculo_seleccionado: '',
        year_vehiculo_seleccionado: 0,
        color_vehiculo_seleccionado: '',
        numero_pasajeros_vehiculo_seleccionado: 0,
        marca_vehiculo_seleccionado: '',
        id_empresa_vehiculo_seleccionado: 0,
        id_vehiculo_seleccionada: 0,
      }
      // NUEVO: Limpiar archivos cuando no hay selección
      this.documentosExistentesVehiculo = [];
    }
  }

  // NUEVO: Método para cargar archivos del vehículo seleccionado
  cargarArchivosVehiculoSeleccionado(vehiculo: any): void {
    // Cargar documentos existentes
    if (vehiculo.documentos_urls && Array.isArray(vehiculo.documentos_urls)) {
      this.documentosExistentesVehiculo = vehiculo.documentos_urls;
    } else {
      this.documentosExistentesVehiculo = [];
    }
  }

  getEmpresaName(id: number): string {
    const empresa = this.empresasCargadas.find(e => e.id === id);
    return empresa ? empresa.nombre : 'No seleccionado';
  }

  formatNumber(event: Event): void {
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
      this.cargarEmpresas();  
    }
    if (key === 'crearVehiculo') {
      this.limpiarFormulario();
    }
    if (key === 'modificarVehiculo') {
      this.limpiarFormularioModificar();
    }
  }
}