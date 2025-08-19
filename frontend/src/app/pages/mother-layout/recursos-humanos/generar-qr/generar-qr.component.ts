// generar-qr.component.ts
import { Component, OnInit, Inject, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser, CommonModule } from '@angular/common';
import { QRCodeModule, QRCodeElementType } from 'angularx-qrcode';
import { ContratistaApiService } from '../../../../services/contratista-api.service';
import { saveAs } from 'file-saver';
import JSZip from 'jszip';
import { SafeUrl } from '@angular/platform-browser';

interface Trabajador {
  nombres: string;
  apellidos: string;
  rut: string;
  
}

@Component({
  selector: 'app-generar-qr',
  standalone: true,
  imports: [CommonModule, QRCodeModule],
  templateUrl: './generar-qr.component.html',
  styleUrls: ['./generar-qr.component.css']
})
export class GenerarQrComponent implements OnInit {
  trabajadores: Trabajador[] = [];
  cargando = false;
  error = '';
  qrType: QRCodeElementType = 'img';

  constructor(
    private apiService: ContratistaApiService,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {}

  ngOnInit() {
    if (isPlatformBrowser(this.platformId)) {
      this.cargarTrabajadores();
    }
  }

  cargarTrabajadores() {
    this.cargando = true;
    this.apiService.get('api_trabajadores_cosecha/').subscribe({
      next: (response) => {
        this.trabajadores = response;
        this.cargando = false;
      },
      error: (error) => {
        this.error = 'Error al cargar trabajadores: ' + error.message;
        this.cargando = false;
      }
    });
  }

  async descargarQRs() {
    try {
      const zip = new JSZip();

      const createImageFromQR = async (qrElement: HTMLElement, trabajador: Trabajador): Promise<string> => {
        return new Promise((resolve) => {
          const canvas = document.createElement('canvas');
          const ctx = canvas.getContext('2d');
          const img = new Image();
          
          // Obtener la imagen del QR
          const qrImg = qrElement.querySelector('img');
          if (!qrImg) {
            throw new Error('No se pudo encontrar la imagen QR');
          }

          img.onload = () => {
            if (ctx) {
              // Configurar el tamaño del canvas
              canvas.width = 300;
              canvas.height = 300;

              // Fondo blanco
              ctx.fillStyle = 'white';
              ctx.fillRect(0, 0, canvas.width, canvas.height);

              // Dibujar el QR
              ctx.drawImage(img, 50, 20, 200, 200);

              // Configurar el texto
              ctx.fillStyle = 'black';
              ctx.textAlign = 'center';
              
              // Nombre
              ctx.font = 'bold 16px Arial';
              ctx.fillText(trabajador.nombres, canvas.width/2, canvas.height - 60);
              
              // Apellidos
              ctx.font = 'bold 16px Arial';
              ctx.fillText(trabajador.apellidos, canvas.width/2, canvas.height - 40);

              // RUT
              ctx.font = '14px Arial';
              ctx.fillText(this.formatRUT(trabajador.rut), canvas.width/2, canvas.height - 20);
              
              resolve(canvas.toDataURL('image/png').split(',')[1]);
            }
          };

          img.src = qrImg.src;
        });
      };

      for (let i = 0; i < this.trabajadores.length; i++) {
        const trabajador = this.trabajadores[i];
        const qrElement = document.getElementById(`qr-${i}`);
        
        if (qrElement) {
          try {
            const imageData = await createImageFromQR(qrElement, trabajador);
            zip.file(`${trabajador.rut}_${trabajador.nombres}.png`, imageData, {base64: true});
          } catch (error) {
            console.error(`Error procesando QR para ${trabajador.nombres}:`, error);
          }
        }
      }

      const content = await zip.generateAsync({type: 'blob'});
      saveAs(content, 'codigos_qr_cosecha.zip');
    } catch (error) {
      console.error('Error al generar ZIP:', error);
      this.error = 'Error al generar el archivo ZIP';
    }
  }

  formatRUT(rut: string): string {
    let valor = rut.replace(/\./g, '').replace('-', '');
    valor = valor.substring(0, valor.length - 1) + '-' + valor.charAt(valor.length - 1);
    return valor.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
  }

  generarContenidoQR(trabajador: Trabajador): string {
    return JSON.stringify({
      nombre: trabajador.nombres,
      apellidos: trabajador.apellidos,
      rut: trabajador.rut,
      
    });
  }
}