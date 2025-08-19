// reprocesar-pago.component.ts

import { Component, OnInit, TemplateRef, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBarModule, MatSnackBar } from '@angular/material/snack-bar';
import { MatTableModule } from '@angular/material/table';
import { MatCardModule } from '@angular/material/card';
import { MatDialogModule, MatDialog } from '@angular/material/dialog';
import { MatTooltipModule } from '@angular/material/tooltip';
import { ContratistaApiService } from '../../../../services/contratista-api.service';

// Interfaces para un mejor tipado de datos
interface Folio {
  id: number;
  nombre_cliente: string;  // Changed from cliente.nombre
  valor_pago_trabajador: number;
  estado?: boolean;  // Made optional since it's not in the API response
  // Add other fields if needed
  fecha_inicio_contrato: string;
  fecha_termino_contrato: string;
}


interface ReprocesoResultado {
  trabajador: string;
  montoOriginal: number;
  montoNuevo: number;
  diferencia: number;
  estado: string;
  saldoNuevo?: number;
}

interface DialogData {
  folio: Folio;
  nuevoValor: number;
}

@Component({
  selector: 'app-reprocesar-pago',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatDatepickerModule,
    MatNativeDateModule,
    MatSelectModule,
    MatButtonModule,
    MatProgressSpinnerModule,
    MatSnackBarModule,
    MatTableModule,
    MatCardModule,
    MatDialogModule,
    MatTooltipModule,
  ],
  templateUrl: './reprocesar-pago.component.html',
  styleUrl: './reprocesar-pago.component.css'
})
export class ReprocesarPagoComponent implements OnInit {
  // Referencia al template del diálogo
  @ViewChild('dialogTemplate') dialogTemplate!: TemplateRef<any>;

  // Propiedades del componente
  reprocesarForm: FormGroup;
  isLoading = false;
  folios: Folio[] = [];
  selectedFolio: Folio | null = null;
  resultados: ReprocesoResultado[] = [];
  displayedColumns: string[] = ['trabajador', 'montoOriginal', 'montoNuevo', 'diferencia', 'saldoNuevo', 'estado'];
  holdingId: number;
  dialogData: DialogData | null = null;

  constructor(
    private fb: FormBuilder,
    private snackBar: MatSnackBar,
    private dialog: MatDialog,
    private apiService: ContratistaApiService
  ) {
    this.holdingId = Number(localStorage.getItem('holding_id'));
    
    // Inicialización del formulario con validadores
    this.reprocesarForm = this.fb.group({
      fechaInicio: ['', [Validators.required]],
      fechaFin: ['', [Validators.required]],
      folioId: ['', [Validators.required]],
      nuevoValorPago: ['', [Validators.required, Validators.min(1)]]
    }, { validators: this.fechaRangeValidator });

    // Suscripción a cambios en el folio seleccionado
    this.reprocesarForm.get('folioId')?.valueChanges.subscribe(folioId => {
      this.onFolioSelected(folioId);
    });
  }

  ngOnInit(): void {
    this.cargarFoliosComerciales();
  }

  private fechaRangeValidator(group: FormGroup) {
    const inicio = group.get('fechaInicio')?.value;
    const fin = group.get('fechaFin')?.value;
    
    if (inicio && fin && inicio > fin) {
      return { fechaInvalida: true };
    }
    return null;
  }

  private cargarFoliosComerciales(): void {
    this.isLoading = true;
    this.apiService.get(`folio_comercial/${this.holdingId}/`).subscribe({
      next: (response: any[]) => {
        // Map the API response to match our expected format
        this.folios = response.map(folio => ({
          id: folio.id,
          nombre_cliente: folio.nombre_cliente,
          valor_pago_trabajador: folio.valor_pago_trabajador,
          fecha_inicio_contrato: folio.fecha_inicio_contrato,
          fecha_termino_contrato: folio.fecha_termino_contrato,
          estado: true  // Since we're receiving active folios
        })).sort((a, b) => 
          a.nombre_cliente.localeCompare(b.nombre_cliente));
        
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error al cargar folios:', error);
        this.mostrarError('Error al cargar los folios comerciales');
        this.isLoading = false;
      }
    });
  }


  private onFolioSelected(folioId: number): void {
    this.selectedFolio = this.folios.find(f => f.id === folioId) || null;
    
    if (this.selectedFolio) {
      this.reprocesarForm.patchValue({
        nuevoValorPago: this.selectedFolio.valor_pago_trabajador
      }, { emitEvent: false });
    }
  }

  onSubmit(): void {
    if (this.reprocesarForm.valid && this.selectedFolio) {
      // Preparamos los datos del diálogo antes de abrirlo
      this.dialogData = {
        folio: this.selectedFolio,
        nuevoValor: this.reprocesarForm.get('nuevoValorPago')?.value
      };

      const dialogRef = this.dialog.open(this.dialogTemplate, {
        width: '400px'
      });

      dialogRef.afterClosed().subscribe(confirmed => {
        if (confirmed) {
          this.procesarReproceso();
        }
        // Limpiamos los datos del diálogo después de cerrarlo
        this.dialogData = null;
      });
    }
  }

  // Método helper para acceder a los datos del diálogo desde el template
  getDialogData(): DialogData {
    if (!this.dialogData) {
      throw new Error('Dialog data not initialized');
    }
    return this.dialogData;
  }

  private procesarReproceso(): void {
    if (!this.reprocesarForm.valid) return;

    this.isLoading = true;
    const formValue = this.reprocesarForm.value;
    
    const data = {
      fecha_inicio: this.formatDate(formValue.fechaInicio),
      fecha_fin: this.formatDate(formValue.fechaFin),
      folio_id: formValue.folioId,
      holding_id: this.holdingId,
      nuevo_valor_pago: formValue.nuevoValorPago
    };

    this.apiService.post('reprocesar-pagos/', data).subscribe({
      next: (response) => {
        this.manejarRespuestaExitosa(response);
        this.cargarFoliosComerciales();
      },
      error: (error) => {
        this.manejarError(error);
      }
    });
  }

  private formatDate(date: Date): string {
    return date.toISOString().split('T')[0];
  }

  private manejarRespuestaExitosa(response: any): void {
    this.resultados = response.changes.map((cambio: any) => ({
      trabajador: cambio.trabajador,
      montoOriginal: cambio.monto_original,
      montoNuevo: cambio.monto_nuevo,
      diferencia: cambio.diferencia,
      saldoNuevo: cambio.saldo_nuevo,
      estado: this.determinarEstado(cambio)
    }));
    
    this.snackBar.open('Pagos reprocesados correctamente', 'Cerrar', {
      duration: 3000,
      horizontalPosition: 'right',
      verticalPosition: 'top'
    });
    
    this.isLoading = false;
  }

  private manejarError(error: any): void {
    this.mostrarError(error.error?.message || 'Error al reprocesar pagos');
    this.isLoading = false;
  }

  private determinarEstado(cambio: any): string {
    if (cambio.error) return 'Error';
    if (cambio.diferencia === 0) return 'Sin Cambios';
    return cambio.diferencia > 0 ? 'Ajuste Positivo' : 'Ajuste Negativo';
  }

  private mostrarError(mensaje: string): void {
    this.snackBar.open(mensaje, 'Cerrar', {
      duration: 5000,
      horizontalPosition: 'right',
      verticalPosition: 'top',
      panelClass: ['error-snackbar']
    });
  }

  formatCurrency(value: number): string {
    return new Intl.NumberFormat('es-CL', {
      style: 'currency',
      currency: 'CLP'
    }).format(value);
  }

  getEstadoClass(estado: string): string {
    const clases = {
      'Error': 'estado-error',
      'Sin Cambios': 'estado-neutral',
      'Ajuste Positivo': 'estado-positivo',
      'Ajuste Negativo': 'estado-negativo'
    };
    return clases[estado as keyof typeof clases] || '';
  }

  getEstadoTooltip(estado: string): string {
    const tooltips = {
      'Error': 'Ocurrió un error durante el reproceso',
      'Sin Cambios': 'No hubo cambios en el monto',
      'Ajuste Positivo': 'Se agregó saldo a favor del trabajador',
      'Ajuste Negativo': 'Se descontó saldo del trabajador'
    };
    return tooltips[estado as keyof typeof tooltips] || '';
  }
}