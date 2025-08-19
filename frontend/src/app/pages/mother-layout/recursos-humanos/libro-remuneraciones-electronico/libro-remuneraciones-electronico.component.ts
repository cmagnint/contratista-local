import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatDividerModule } from '@angular/material/divider';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatInputModule } from '@angular/material/input';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ContratistaApiService } from '../../../../services/contratista-api.service';
import { HttpEventType } from '@angular/common/http';
import { saveAs } from 'file-saver';

@Component({
  selector: 'app-libro-remuneraciones-electronico',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    MatFormFieldModule,
    MatSelectModule,
    MatButtonModule,
    MatProgressBarModule,
    MatSnackBarModule,
    MatCardModule,
    MatIconModule,
    MatDividerModule,
    MatDatepickerModule,
    MatNativeDateModule,
    MatInputModule
  ],
  templateUrl: './libro-remuneraciones-electronico.component.html',
  styleUrls: ['./libro-remuneraciones-electronico.component.css']
})
export class LibroRemuneracionesElectronicoComponent implements OnInit {
  remuneracionesForm: FormGroup;
  sociedades: any[] = [];
  meses: any[] = [
    { valor: 1, nombre: 'Enero' },
    { valor: 2, nombre: 'Febrero' },
    { valor: 3, nombre: 'Marzo' },
    { valor: 4, nombre: 'Abril' },
    { valor: 5, nombre: 'Mayo' },
    { valor: 6, nombre: 'Junio' },
    { valor: 7, nombre: 'Julio' },
    { valor: 8, nombre: 'Agosto' },
    { valor: 9, nombre: 'Septiembre' },
    { valor: 10, nombre: 'Octubre' },
    { valor: 11, nombre: 'Noviembre' },
    { valor: 12, nombre: 'Diciembre' }
  ];
  anios: number[] = [];
  holdingId: number;
  isGenerating: boolean = false;
  progressValue: number = 0;

  constructor(
    private fb: FormBuilder,
    private apiService: ContratistaApiService,
    private snackBar: MatSnackBar
  ) {
    this.holdingId = Number(localStorage.getItem('holding_id'));

    // Generar años (año actual y 5 años anteriores)
    const currentYear = new Date().getFullYear();
    for (let i = 0; i < 6; i++) {
      this.anios.push(currentYear - i);
    }

    this.remuneracionesForm = this.fb.group({
      sociedad: ['', Validators.required],
      mes: ['', Validators.required],
      anio: [currentYear, Validators.required]
    });
  }

  ngOnInit(): void {
    this.cargarSociedades();
  }

  cargarSociedades() {
    this.apiService.get(`api_sociedades_modify/${this.holdingId}/`).subscribe({
      next: (data) => {
        this.sociedades = data;
      },
      error: (error) => {
        console.error('Error al cargar las sociedades:', error);
        this.snackBar.open('Error al cargar las sociedades', 'Cerrar', {
          duration: 3000
        });
      }
    });
  }

  generarLibroRemuneraciones() {
    if (this.remuneracionesForm.invalid) {
      this.snackBar.open('Por favor complete todos los campos requeridos', 'Cerrar', {
        duration: 3000
      });
      return;
    }

    const formData = this.remuneracionesForm.value;
    
    this.isGenerating = true;
    this.progressValue = 15; // Iniciamos con un 15% para mostrar que está en proceso

    // Build the query string with all required parameters
    const queryString = `?holding_id=${this.holdingId}&sociedad_id=${formData.sociedad}&mes=${formData.mes}&anio=${formData.anio}`;
    
    // Log the complete URL for debugging
    console.log(`Making request to: generar-libro-remuneraciones/${queryString}`);
    
    // Use the existing getFile method with the constructed URL
    this.apiService.getFile(`generar-libro-remuneraciones/${queryString}`).subscribe({
      next: (event) => {
        if (event.type === HttpEventType.DownloadProgress && event.total) {
          // Actualizar la barra de progreso
          this.progressValue = Math.round(100 * event.loaded / event.total);
        } else if (event.type === HttpEventType.Response) {
          // Descarga completada
          this.progressValue = 100;
          
          // Generar nombre de archivo
          const sociedadNombre = this.sociedades.find(s => s.id === formData.sociedad)?.nombre || 'Sociedad';
          const mesNombre = this.meses.find(m => m.valor === formData.mes)?.nombre || formData.mes;
          const fileName = `Libro_Remuneraciones_${sociedadNombre}_${mesNombre}_${formData.anio}.csv`;
          
          // Guardar el archivo
          const file = new Blob([event.body as Blob], { type: 'text/csv' });
          saveAs(file, fileName);
          
          // Notificar al usuario
          this.snackBar.open('Libro de remuneraciones generado con éxito', 'Cerrar', {
            duration: 5000
          });
          
          setTimeout(() => {
            this.isGenerating = false;
            this.progressValue = 0;
          }, 1000);
        }
      },
      error: (error) => {
        console.error('Error al generar el libro de remuneraciones:', error);
        
        // Intentar leer el mensaje de error del servidor si está disponible
        if (error.error instanceof Blob) {
          const reader = new FileReader();
          reader.onload = () => {
            try {
              const errorText = reader.result as string;
              console.error('Error response content:', errorText);
              
              // Intentar parsear como JSON
              try {
                const errorJson = JSON.parse(errorText);
                this.snackBar.open(`Error: ${errorJson.error || 'Desconocido'}`, 'Cerrar', {
                  duration: 5000
                });
              } catch (e) {
                // Si no es JSON, mostrar el texto tal cual
                this.snackBar.open(`Error: ${errorText.substring(0, 100)}`, 'Cerrar', {
                  duration: 5000
                });
              }
            } catch (e) {
              this.snackBar.open('Error al generar el libro de remuneraciones', 'Cerrar', {
                duration: 5000
              });
            }
          };
          reader.readAsText(error.error);
        } else {
          this.snackBar.open('Error al generar el libro de remuneraciones', 'Cerrar', {
            duration: 5000
          });
        }
        
        this.isGenerating = false;
        this.progressValue = 0;
      }
    });
  }
}