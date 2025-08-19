import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { ContratistaApiService } from '../../../../services/contratista-api.service';
import { HttpEventType, HttpResponse } from '@angular/common/http';

@Component({
  selector: 'app-apk-link',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    MatCardModule,
    MatProgressBarModule,
    MatIconModule,
    MatButtonModule,
    MatSnackBarModule,
    MatProgressSpinnerModule
  ],
  templateUrl: './apk-link.component.html',
  styleUrls: ['./apk-link.component.css']
})
export class ApkLinkComponent implements OnInit {
  // Estados y variables principales
  token: string = '';
  id: string = '';
  estado: 'validando' | 'listo' | 'error' = 'validando';
  mensajeError: string = '';
  tiempoRestante: number = 0;
  
  // Variables de descarga
  descargando: boolean = false;
  progreso: number = 0;

  constructor(
    private route: ActivatedRoute,
    private contratistaApi: ContratistaApiService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit() {
    // Obtener token e ID de la URL
    this.token = this.route.snapshot.params['token'];
    this.id = this.route.snapshot.params['id'];
    this.validarToken();
  }

  validarToken() {
    this.contratistaApi.get(`validate_apk/${this.token}/${this.id}/`).subscribe({
      next: (response) => {
        if (response.activo && response.tiempo_restante > 0) {
          this.estado = 'listo';
          this.tiempoRestante = response.tiempo_restante;
        } else {
          this.estado = 'error';
          this.mensajeError = 'El enlace ha expirado';
        }
      },
      error: (error) => {
        this.estado = 'error';
        this.mensajeError = error.error?.message || 'El enlace no es válido o ha expirado';
      }
    });
  }

  iniciarDescarga() {
    this.descargando = true;
    this.progreso = 0;

    this.contratistaApi.getFile(`download_apk/${this.token}/${this.id}/`).subscribe({
      next: (event) => {
        if (event.type === HttpEventType.DownloadProgress && event.total) {
          this.progreso = Math.round(100 * event.loaded / event.total);
        }
        if (event instanceof HttpResponse) {
          this.manejarDescargaCompletada(event.body);
        }
      },
      error: (error) => {
        this.manejarError();
      }
    });
  }

  private manejarDescargaCompletada(data: any) {
    // Crear y descargar el archivo
    const blob = new Blob([data], { type: 'application/vnd.android.package-archive' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'contratista.apk';
    document.body.appendChild(a);
    a.click();
    
    // Limpieza
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
    this.descargando = false;
    
    // Notificar al usuario
    this.snackBar.open('Descarga completada con éxito', 'Cerrar', {
      duration: 3000,
      panelClass: ['success-snackbar']
    });
  }

  private manejarError() {
    this.descargando = false;
    this.snackBar.open('Error al descargar la aplicación', 'Cerrar', {
      duration: 5000,
      panelClass: ['error-snackbar']
    });
  }
}