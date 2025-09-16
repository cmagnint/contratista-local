import { Component, Inject, OnInit, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser, CommonModule } from '@angular/common';
import { ContratistaApiService } from '../../../../../services/contratista-api.service';
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
    imageViewModal: false, // NUEVO: Modal para ver imágenes
  };

  public choferSeleccionado: any = {
    nombre_chofer_seleccionado : '',
    rut_chofer_seleccionado : '',
    licencia_chofer_seleccionado : '',
    id_empresa_chofer_seleccionado: 0,
    id_chofer_seleccionada : 0,
    vehiculo_chofer_seleccionado: 0, // AGREGADO: ID del vehículo
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
  public vehiculosDisponibles: any[] = []; // AGREGADO: Lista completa de vehículos

  // MODIFICADO: Agregar columnas de imágenes y documentos
  columnasDesplegadas = ['empresa','modelo','nombre','rut','licencia','imagenes','documentos'];
  
  public nombreChoferNew: string = '';
  public rutChoferNew: string = '';
  public licenciaChoferNew: string = '';

  public deletedRow: any[] = [];

  public selectedChoferId: number | null = null;
  public selectedEmpresaId: number | null = null;
  public selectedVehiculoId: number | null = null;

  // PROPIEDADES PARA ARCHIVOS
  public imagenes: { [key: string]: File | null } = {
    foto_perfil: null,
    foto_licencia_frontal: null,
    foto_licencia_trasera: null,
    foto_cedula_frontal: null,
    foto_cedula_trasera: null
  };

  public imagenesModificar: { [key: string]: File | null } = {
    foto_perfil: null,
    foto_licencia_frontal: null,
    foto_licencia_trasera: null,
    foto_cedula_frontal: null,
    foto_cedula_trasera: null
  };

  public documentos: File[] = [];
  public documentosModificar: File[] = [];
  public previewImagenes: { [key: string]: string } = {};
  public previewImagenesModificar: { [key: string]: string } = {};

  // NUEVO: Para manejar imágenes existentes del chofer
  public imagenesExistentesChofer: { [key: string]: string } = {};
  public documentosExistentesChofer: string[] = [];
  
  // NUEVO: Para modal de visualización de imagen
  public imagenEnVisualizacion: string = '';
  public tipoImagenEnVisualizacion: string = '';

  // NUEVO: Método para obtener las claves de un objeto (soluciona el error de Object.keys)
  getObjectKeys(obj: any): string[] {
    return Object.keys(obj || {});
  }

  ngOnInit(): void {
    if (isPlatformBrowser(this.platformId)) {
      this.holding = localStorage.getItem('holding_id') || '';
      this.cargarChoferes();
      this.cargarEmpresas();
      this.cargarVehiculos();
    }
  }

  // NUEVOS MÉTODOS PARA ARCHIVOS
  onImageSelect(event: Event, tipo: string): void {
    const target = event.target as HTMLInputElement;
    if (target.files && target.files[0]) {
      const file = target.files[0];
      
      // Validar formato de imagen
      const validFormats = ['jpg', 'jpeg', 'png', 'gif', 'webp'];
      const extension = file.name.toLowerCase().split('.').pop();
      
      if (!validFormats.includes(extension || '')) {
        this.errorMessage = 'Solo se permiten imágenes: JPG, PNG, GIF, WEBP';
        this.openModal('errorModal');
        return;
      }

      this.imagenes[tipo] = file;
      
      // Preview de imagen
      const reader = new FileReader();
      reader.onload = (e) => {
        this.previewImagenes[tipo] = e.target?.result as string;
      };
      reader.readAsDataURL(file);
    }
  }

  onImageSelectModificar(event: Event, tipo: string): void {
    const target = event.target as HTMLInputElement;
    if (target.files && target.files[0]) {
      const file = target.files[0];
      
      // Validar formato de imagen
      const validFormats = ['jpg', 'jpeg', 'png', 'gif', 'webp'];
      const extension = file.name.toLowerCase().split('.').pop();
      
      if (!validFormats.includes(extension || '')) {
        this.errorMessage = 'Solo se permiten imágenes: JPG, PNG, GIF, WEBP';
        this.openModal('errorModal');
        return;
      }

      this.imagenesModificar[tipo] = file;
      
      // Preview de imagen
      const reader = new FileReader();
      reader.onload = (e) => {
        this.previewImagenesModificar[tipo] = e.target?.result as string;
      };
      reader.readAsDataURL(file);
    }
  }

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

  removeImage(tipo: string): void {
    this.imagenes[tipo] = null;
    delete this.previewImagenes[tipo];
  }

  removeImageModificar(tipo: string): void {
    this.imagenesModificar[tipo] = null;
    delete this.previewImagenesModificar[tipo];
  }

  crearChoferes(): void {
    const formData = new FormData();
    
    // Datos básicos del chofer
    formData.append('holding', this.holding);
    formData.append('empresa', this.selectedEmpresaId?.toString() || '');
    formData.append('nombre', this.nombreChofer);
    formData.append('rut', this.rutChofer);
    formData.append('licencia', this.licenciaChofer);
    formData.append('vehiculo', this.selectedVehiculoId?.toString() || '');

    // Agregar imágenes
    Object.keys(this.imagenes).forEach(tipo => {
      if (this.imagenes[tipo]) {
        formData.append(`imagen_${tipo}`, this.imagenes[tipo]!);
      }
    });

    // Agregar documentos
    this.documentos.forEach((doc, index) => {
      formData.append(`documento_${index}`, doc);
    });

    this.apiService.postFormData('api_choferes_transportes/', formData).subscribe({
      next: (response) => {
        console.log(response);
        this.closeModal('crearChofer');
        this.cargarChoferes();
        this.openModal('exitoModal');
        this.limpiarFormulario();
      },
      error: (error) => {
        console.log(error);
        this.openModal('errorModal');
      }
    });
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
        console.log('Choferes cargados:', this.choferesCargados); // AGREGADO: Para debug
      },
      error: (error) => {
        console.error('Error al recibir los choferes:', error);
      }
    });
  }

  cargarVehiculos():void{
    this.apiService.get(`api_vehiculos_transportes/?holding=${this.holding}`).subscribe({
      next: (response) => {
        console.log('vehiculos cargados',response)
        this.vehiculosDisponibles = response; // AGREGADO: Guardar lista completa
        
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

  modificarChoferes(): void {
    const formData = new FormData();
    
    // Datos básicos del chofer
    formData.append('holding', this.holding);
    formData.append('empresa', this.selectedEmpresaId?.toString() || '');
    formData.append('nombre', this.nombreChoferNew);
    formData.append('rut', this.rutChoferNew);
    formData.append('licencia', this.licenciaChoferNew);
    formData.append('id', this.selectedChoferId?.toString() || '');
    formData.append('vehiculo', this.selectedVehiculoId?.toString() || '');

    // Agregar imágenes modificadas
    Object.keys(this.imagenesModificar).forEach(tipo => {
      if (this.imagenesModificar[tipo]) {
        formData.append(`imagen_${tipo}`, this.imagenesModificar[tipo]!);
      }
    });

    // Agregar documentos modificados
    this.documentosModificar.forEach((doc, index) => {
      formData.append(`documento_${index}`, doc);
    });

    this.apiService.putFormData('api_choferes_transportes/', formData).subscribe({
      next: (response) => {
        this.closeModal('modificarChofer');
        this.cargarChoferes();
        this.openModal('exitoModal');
        this.limpiarFormularioModificar();
      },
      error: (error) => {
        console.log(error);
        this.openModal('errorModal');
      }
    });
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

  limpiarFormulario(): void {
    this.nombreChofer = '';
    this.rutChofer = '';
    this.licenciaChofer = '';
    this.selectedEmpresaId = null;
    this.selectedVehiculoId = null;
    this.imagenes = {
      foto_perfil: null,
      foto_licencia_frontal: null,
      foto_licencia_trasera: null,
      foto_cedula_frontal: null,
      foto_cedula_trasera: null
    };
    this.documentos = [];
    this.previewImagenes = {};
  }

  limpiarFormularioModificar(): void {
    this.imagenesModificar = {
      foto_perfil: null,
      foto_licencia_frontal: null,
      foto_licencia_trasera: null,
      foto_cedula_frontal: null,
      foto_cedula_trasera: null
    };
    this.documentosModificar = [];
    this.previewImagenesModificar = {};
    this.imagenesExistentesChofer = {}; // AGREGADO: Limpiar imágenes existentes
    this.documentosExistentesChofer = []; // AGREGADO: Limpiar documentos existentes
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

  // MODIFICADO: Cargar información completa del chofer incluyendo imágenes y documentos
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
        id_empresa_chofer_seleccionado: lastSelectedRow.empresa,
        vehiculo_chofer_seleccionado: lastSelectedRow.vehiculo // AGREGADO: Guardar ID del vehículo
      };
      this.nombreChoferNew = this.choferSeleccionado.nombre_chofer_seleccionado
      this.rutChoferNew = this.choferSeleccionado.rut_chofer_seleccionado
      this.licenciaChoferNew = this.choferSeleccionado.licencia_chofer_seleccionado
      this.selectedChoferId = this.choferSeleccionado.id_chofer_seleccionada;
      this.selectedEmpresaId = this.choferSeleccionado.id_empresa_chofer_seleccionado;
      this.selectedVehiculoId = this.choferSeleccionado.vehiculo_chofer_seleccionado; // AGREGADO: Asignar vehículo seleccionado

      // AGREGADO: Cargar imágenes y documentos existentes del chofer
      this.cargarArchivosChoferSeleccionado(lastSelectedRow);

    } else {
      this.choferSeleccionado = {
        nombre_chofer_seleccionado : '',
        rut_chofer_seleccionado : '',
        licencia_chofer_seleccionado : '',
        id_empresa_chofer_seleccionado: 0,
        id_chofer_seleccionada : 0,
        vehiculo_chofer_seleccionado: 0 // AGREGADO
      }
      // AGREGADO: Limpiar archivos cuando no hay selección
      this.imagenesExistentesChofer = {};
      this.documentosExistentesChofer = [];
    }
  }

  // NUEVO: Método para cargar archivos del chofer seleccionado
  cargarArchivosChoferSeleccionado(chofer: any): void {
    // Cargar imágenes existentes
    if (chofer.imagenes_urls) {
      this.imagenesExistentesChofer = chofer.imagenes_urls;
    } else {
      this.imagenesExistentesChofer = {};
    }

    // Cargar documentos existentes
    if (chofer.documentos_urls && Array.isArray(chofer.documentos_urls)) {
      this.documentosExistentesChofer = chofer.documentos_urls;
    } else {
      this.documentosExistentesChofer = [];
    }
  }

  getEmpresaName(id: number): string {
    const empresa = this.empresasCargadas.find(e => e.id === id);
    return empresa ? empresa.nombre : 'No seleccionado';
  }

  // CORREGIDO: Método para obtener el nombre del vehículo por ID
  getVehiculoName(id: number): string {
    const vehiculo = this.vehiculosDisponibles.find(v => v.id === id);
    return vehiculo ? vehiculo.modelo : 'No seleccionado';
  }

  // NUEVO: Métodos para manejar imágenes y documentos en la tabla
  hasImages(chofer: any): boolean {
    return chofer.imagenes_urls && Object.values(chofer.imagenes_urls).some((url: any) => url !== null);
  }

  hasDocuments(chofer: any): boolean {
    return chofer.documentos_urls && Array.isArray(chofer.documentos_urls) && chofer.documentos_urls.length > 0;
  }

  // NUEVO: Abrir imagen en modal
  abrirImagenEnModal(url: string, tipo: string): void {
    this.imagenEnVisualizacion = url;
    this.tipoImagenEnVisualizacion = tipo;
    this.openModal('imageViewModal');
  }

  // NUEVO: Descargar documento
  descargarDocumento(url: string, nombreArchivo?: string): void {
    // Crear un enlace temporal para descargar
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
    if (key === 'crearChofer') {
      this.limpiarFormulario();
    }
    if (key === 'modificarChofer') {
      this.limpiarFormularioModificar();
    }
    // AGREGADO: Limpiar modal de imagen
    if (key === 'imageViewModal') {
      this.imagenEnVisualizacion = '';
      this.tipoImagenEnVisualizacion = '';
    }
  }
}