import { Component, Inject, OnInit, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser, CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup, FormArray, Validators } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatCardModule } from '@angular/material/card';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { ContratistaApiService } from '../../../../services/contratista-api.service';

// Interfaz para el enlace APK que refleja la estructura exacta de la respuesta del backend
export interface ApkLink {
  id: number;
  url: string;
  token: string;
  fecha_expiracion: string;
  activo: boolean;
  tiempo_restante: number;
}

@Component({
  selector: 'app-auto-registro',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatButtonModule,
    MatIconModule,
    MatCardModule,
    MatCheckboxModule,
    MatTooltipModule,
    MatSnackBarModule
  ],
  templateUrl: './auto-registro.component.html',
  styleUrls: ['./auto-registro.component.css']
})
export class AutoRegistroComponent implements OnInit {
  // Formularios y estados principales
  enlaceForm: FormGroup;
  apkForm: FormGroup;
  
  // Datos y estados
  perfiles: any[] = [];
  enlaces: any[] = [];
  enlaceGenerado: any = null;
  apkLink: ApkLink | null = null;
  holding: string | undefined;

  constructor(
    private fb: FormBuilder,
    private contratistaApi: ContratistaApiService,
    private snackBar: MatSnackBar,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {
    // Inicialización del formulario de auto-registro
    this.enlaceForm = this.fb.group({
      perfil: ['', Validators.required],
      duracion_horas: [24, [Validators.required, Validators.min(1)]],
      restringirRuts: [false],
      generarContrato: [false],
      ruts: this.fb.array([])
    });

    // Inicialización del formulario de APK con validación de duración máxima
    this.apkForm = this.fb.group({
      duracion_horas: [24, [
        Validators.required,
        Validators.min(1),
        Validators.max(168) // Máximo 7 días
      ]]
    });
  }

  // Getter para acceder fácilmente al FormArray de RUTs
  get rutsArray() {
    return this.enlaceForm.get('ruts') as FormArray;
  }

  ngOnInit(): void {
    if (isPlatformBrowser(this.platformId)) {
      this.holding = localStorage.getItem('holding_id') || '';
      if (this.holding) {
        this.cargarPerfiles();
        this.cargarEnlaces();
        this.cargarEnlaceApk();
      } else {
        this.mostrarError('No se pudo determinar el holding');
      }
    }
  }

  // Métodos relacionados con el enlace APK
  cargarEnlaceApk() {
    if (!this.holding) return;
    
    this.contratistaApi.get(`link_apk/${this.holding}/`).subscribe({
      next: (response) => {
        this.apkLink = Array.isArray(response) && response.length === 0 ? null : response;
      },
      error: (error) => {
        console.error('Error al cargar enlace APK:', error);
        this.mostrarError('Error al cargar el enlace APK');
      }
    });
  }

  generarEnlaceApk() {
    if (this.apkForm.valid && this.holding) {
      const formData = {
        holding: this.holding,
        duracion_horas: this.apkForm.value.duracion_horas
      };

      this.contratistaApi.post(`link_apk/${this.holding}/`, formData).subscribe({
        next: (response) => {
          this.apkLink = response;
          this.mostrarExito('Enlace APK generado exitosamente');
          this.apkForm.reset({ duracion_horas: 24 });
        },
        error: (error) => {
          console.error('Error al generar enlace APK:', error);
          this.mostrarError('Error al generar el enlace APK');
        }
      });
    }
  }

  eliminarEnlaceApk() {
    if (this.apkLink && this.holding) {
      this.contratistaApi.delete(`link_apk/${this.holding}/`, {
        id: this.apkLink.id,
        holding: this.holding
      }).subscribe({
        next: () => {
          this.apkLink = null;
          this.mostrarExito('Enlace APK eliminado exitosamente');
        },
        error: (error) => {
          console.error('Error al eliminar enlace APK:', error);
          this.mostrarError('Error al eliminar el enlace APK');
        }
      });
    }
  }

  // Métodos existentes para auto-registro
  cargarPerfiles() {
    this.contratistaApi.get(`api_perfil/${this.holding}/`).subscribe({
      next: (data) => {
        this.perfiles = data;
      },
      error: (error) => {
        console.error('Error al cargar perfiles:', error);
        this.mostrarError('Error al cargar los perfiles');
      }
    });
  }

  cargarEnlaces() {
    this.contratistaApi.get(`enlaces-auto-registro/?holding=${this.holding}`).subscribe({
      next: (response) => {
        this.enlaces = response;
      },
      error: (error) => {
        console.error('Error al cargar enlaces:', error);
        this.mostrarError('Error al cargar los enlaces existentes');
      }
    });
  }

  agregarRut() {
    this.rutsArray.push(this.fb.control('', Validators.required));
  }

  eliminarRut(index: number) {
    this.rutsArray.removeAt(index);
  }

  generarEnlace() {
    if (this.enlaceForm.valid) {
      const formData = this.enlaceForm.value;
      const data = {
        holding: this.holding,
        perfil: formData.perfil,
        duracion_horas: formData.duracion_horas,
        generar_contrato: formData.generarContrato,
        ruts_permitidos: formData.restringirRuts ? formData.ruts.filter((rut: string) => rut.trim() !== '') : null
      };

      this.contratistaApi.post('enlaces-auto-registro/', data).subscribe({
        next: (response) => {
          this.enlaceGenerado = response;
          this.mostrarExito('Enlace generado exitosamente');
          this.cargarEnlaces();
        },
        error: (error) => {
          console.error('Error al generar enlace:', error);
          this.mostrarError(error.error?.message || 'Error al generar el enlace');
        }
      });
    }
  }

  desactivarEnlace(id: number) {
    this.contratistaApi.delete('enlaces-auto-registro/', {
      ids: [id],
      holding: this.holding
    }).subscribe({
      next: () => {
        this.mostrarExito('Enlace desactivado exitosamente');
        this.cargarEnlaces();
      },
      error: (error) => {
        console.error('Error al desactivar enlace:', error);
        this.mostrarError('Error al desactivar el enlace');
      }
    });
  }

  // Métodos de utilidad
  copiarEnlace(url: string) {
    navigator.clipboard.writeText(url).then(() => {
      this.mostrarExito('Enlace copiado al portapapeles');
    }).catch(() => {
      this.mostrarError('Error al copiar el enlace');
    });
  }

  isEnlaceExpirado(fecha_expiracion: string): boolean {
    return new Date(fecha_expiracion) < new Date();
  }

  private mostrarExito(mensaje: string) {
    this.snackBar.open(mensaje, 'Cerrar', {
      duration: 3000,
      panelClass: ['success-snackbar']
    });
  }

  private mostrarError(mensaje: string) {
    this.snackBar.open(mensaje, 'Cerrar', {
      duration: 5000,
      panelClass: ['error-snackbar']
    });
  }
}