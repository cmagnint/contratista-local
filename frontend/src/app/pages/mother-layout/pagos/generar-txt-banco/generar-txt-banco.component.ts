import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
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
  imports: [CommonModule, FormsModule],
  templateUrl: './generar-txt-banco.component.html',
  styleUrl: './generar-txt-banco.component.css'
})
export class GenerarTxtBancoComponent {
  archivoSeleccionado: File | null = null;
  nombreArchivoSeleccionado: string = '';
  nombreArchivoBase: string = '';
  archivosGenerados: ArchivoTxt[] = [];
  procesando: boolean = false;
  errorMensaje: string = '';
  exitoMensaje: string = '';
  
  totalRegistros: number = 0;
  totalArchivos: number = 0;
  
  modals: { [key: string]: boolean } = {
    errorModal: false,
    exitoModal: false,
    infoModal: false
  };

  constructor(private apiService: ContratistaApiService) {}

  onFileSelect(event: any): void {
    const file = event.target.files[0];
    
    if (file) {
      if (!file.name.toLowerCase().endsWith('.csv')) {
        this.mostrarError('Por favor seleccione un archivo CSV válido');
        this.limpiarArchivo();
        return;
      }
      
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

  limpiarArchivo(): void {
    this.archivoSeleccionado = null;
    this.nombreArchivoSeleccionado = '';
    this.archivosGenerados = [];
    this.totalRegistros = 0;
    this.totalArchivos = 0;
    
    const fileInput = document.getElementById('csvFileInput') as HTMLInputElement;
    if (fileInput) {
      fileInput.value = '';
    }
  }

  async procesarArchivo(): Promise<void> {
    if (!this.archivoSeleccionado) {
      this.mostrarError('Por favor seleccione un archivo CSV');
      return;
    }

    if (!this.nombreArchivoBase.trim()) {
      this.mostrarError('Por favor ingrese un nombre para los archivos');
      return;
    }

    this.procesando = true;
    this.errorMensaje = '';
    this.archivosGenerados = [];

    try {
      const formData = new FormData();
      formData.append('csv_file', this.archivoSeleccionado);
      formData.append('nombre_archivo', this.nombreArchivoBase.trim());
      formData.append('action', 'generar_txt_banco');

      console.log('Enviando archivo al backend...');

      const response = await this.apiService.postFormData('generar_txt_banco/', formData).toPromise();

      console.log('Respuesta del backend:', response);

      if (response.success) {
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

  descargarArchivo(archivo: ArchivoTxt): void {
    try {
      const blob = new Blob([archivo.contenido], { type: 'text/plain;charset=utf-8' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = archivo.nombre;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      console.log('Archivo descargado:', archivo.nombre);
    } catch (error) {
      console.error('Error al descargar archivo:', error);
      this.mostrarError('Error al descargar el archivo');
    }
  }

  descargarTodos(): void {
    if (this.archivosGenerados.length === 0) {
      this.mostrarError('No hay archivos para descargar');
      return;
    }

    this.archivosGenerados.forEach((archivo, index) => {
      setTimeout(() => {
        this.descargarArchivo(archivo);
      }, index * 300);
    });
  }

  mostrarError(mensaje: string): void {
    this.errorMensaje = mensaje;
    this.openModal('errorModal');
  }

  openModal(modalName: string): void {
    this.modals[modalName] = true;
  }

  closeModal(modalName: string): void {
    this.modals[modalName] = false;
    
    if (modalName === 'errorModal') {
      this.errorMensaje = '';
    }
    if (modalName === 'exitoModal') {
      this.exitoMensaje = '';
    }
  }

  mostrarInfoFormato(): void {
    this.openModal('infoModal');
  }

  hayArchivosGenerados(): boolean {
    return this.archivosGenerados.length > 0;
  }

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