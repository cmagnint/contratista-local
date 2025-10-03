import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ContratistaApiService } from '../../../../services/contratista-api.service';

interface ArchivoTxt {
  nombre: string;
  contenido: string;
  numero_archivo: number;
  total_lineas: number;
}

@Component({
  selector: 'app-generar-txt-banco',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './generar-txt-banco.component.html',
  styleUrl: './generar-txt-banco.component.css'
})
export class GenerarTxtBancoComponent {
  archivoSeleccionado: File | null = null;
  nombreArchivoSeleccionado: string = '';
  archivosGenerados: ArchivoTxt[] = [];
  procesando: boolean = false;
  errorMensaje: string = '';
  exitoMensaje: string = '';
  
  // Información del CSV cargado
  totalRegistros: number = 0;
  totalArchivos: number = 0;
  
  // Modales
  modals: { [key: string]: boolean } = {
    errorModal: false,
    exitoModal: false,
    infoModal: false
  };

  constructor(private apiService: ContratistaApiService) {}

  /**
   * Maneja la selección del archivo CSV
   */
  onFileSelect(event: any): void {
    const file = event.target.files[0];
    
    if (file) {
      // Validar que sea un archivo CSV
      if (!file.name.toLowerCase().endsWith('.csv')) {
        this.mostrarError('Por favor seleccione un archivo CSV válido');
        this.limpiarArchivo();
        return;
      }
      
      // Validar tamaño del archivo (máximo 5MB)
      if (file.size > 5 * 1024 * 1024) {
        this.mostrarError('El archivo es demasiado grande. Máximo 5MB');
        this.limpiarArchivo();
        return;
      }
      
      this.archivoSeleccionado = file;
      this.nombreArchivoSeleccionado = file.name;
      this.errorMensaje = '';
      
      console.log('Archivo CSV seleccionado:', file.name);
    }
  }

  /**
   * Limpia el archivo seleccionado
   */
  limpiarArchivo(): void {
    this.archivoSeleccionado = null;
    this.nombreArchivoSeleccionado = '';
    this.archivosGenerados = [];
    this.totalRegistros = 0;
    this.totalArchivos = 0;
    
    // Limpiar input file
    const fileInput = document.getElementById('csvFileInput') as HTMLInputElement;
    if (fileInput) {
      fileInput.value = '';
    }
  }

  /**
   * Procesa el archivo CSV y genera los TXT
   */
  async procesarArchivo(): Promise<void> {
    if (!this.archivoSeleccionado) {
      this.mostrarError('Por favor seleccione un archivo CSV');
      return;
    }

    this.procesando = true;
    this.errorMensaje = '';
    this.archivosGenerados = [];

    try {
      // Crear FormData para enviar el archivo
      const formData = new FormData();
      formData.append('csv_file', this.archivoSeleccionado);
      formData.append('action', 'generar_txt_banco');

      console.log('Enviando archivo al backend...');

      // Enviar al backend usando el servicio
      const response = await this.apiService.postFormData('generar_txt_banco/', formData).toPromise();

      console.log('Respuesta del backend:', response);

      if (response.success) {
        // Procesar respuesta exitosa
        this.archivosGenerados = response.archivos;
        this.totalRegistros = response.total_registros;
        this.totalArchivos = response.total_archivos;
        
        this.exitoMensaje = `Se generaron ${this.totalArchivos} archivo(s) TXT con ${this.totalRegistros} registro(s) total(es)`;
        this.openModal('exitoModal');
        
        console.log('Archivos generados:', this.archivosGenerados);
      } else {
        this.mostrarError(response.message || 'Error al procesar el archivo');
      }
    } catch (error: any) {
      console.error('Error al procesar archivo:', error);
      this.mostrarError(error.error?.message || 'Error al comunicarse con el servidor');
    } finally {
      this.procesando = false;
    }
  }

  /**
   * Descarga un archivo TXT específico
   */
  descargarArchivo(archivo: ArchivoTxt): void {
    try {
      // Crear blob con el contenido del archivo
      const blob = new Blob([archivo.contenido], { type: 'text/plain;charset=utf-8' });
      
      // Crear URL del blob
      const url = window.URL.createObjectURL(blob);
      
      // Crear elemento <a> temporal para descargar
      const link = document.createElement('a');
      link.href = url;
      link.download = archivo.nombre;
      
      // Simular click para descargar
      document.body.appendChild(link);
      link.click();
      
      // Limpiar
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      console.log('Archivo descargado:', archivo.nombre);
    } catch (error) {
      console.error('Error al descargar archivo:', error);
      this.mostrarError('Error al descargar el archivo');
    }
  }

  /**
   * Descarga todos los archivos generados
   */
  descargarTodos(): void {
    if (this.archivosGenerados.length === 0) {
      this.mostrarError('No hay archivos para descargar');
      return;
    }

    // Descargar cada archivo con un pequeño delay para no saturar el navegador
    this.archivosGenerados.forEach((archivo, index) => {
      setTimeout(() => {
        this.descargarArchivo(archivo);
      }, index * 300); // 300ms de delay entre cada descarga
    });
  }

  /**
   * Muestra modal de error
   */
  mostrarError(mensaje: string): void {
    this.errorMensaje = mensaje;
    this.openModal('errorModal');
  }

  /**
   * Abre un modal
   */
  openModal(modalName: string): void {
    this.modals[modalName] = true;
  }

  /**
   * Cierra un modal
   */
  closeModal(modalName: string): void {
    this.modals[modalName] = false;
    
    // Limpiar mensajes al cerrar
    if (modalName === 'errorModal') {
      this.errorMensaje = '';
    }
    if (modalName === 'exitoModal') {
      this.exitoMensaje = '';
    }
  }

  /**
   * Muestra información del formato
   */
  mostrarInfoFormato(): void {
    this.openModal('infoModal');
  }

  /**
   * Verifica si hay archivos generados
   */
  hayArchivosGenerados(): boolean {
    return this.archivosGenerados.length > 0;
  }

  /**
   * Obtiene el tamaño del archivo en formato legible
   */
  obtenerTamanoArchivo(): string {
    if (!this.archivoSeleccionado) return '';
    
    const bytes = this.archivoSeleccionado.size;
    const kb = bytes / 1024;
    const mb = kb / 1024;
    
    if (mb >= 1) {
      return `${mb.toFixed(2)} MB`;
    } else {
      return `${kb.toFixed(2)} KB`;
    }
  }
}