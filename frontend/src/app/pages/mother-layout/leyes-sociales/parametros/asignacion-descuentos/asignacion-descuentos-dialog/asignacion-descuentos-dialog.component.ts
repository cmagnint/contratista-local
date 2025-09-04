import { Component, Inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup, FormArray } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA, MatDialogModule } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatDividerModule } from '@angular/material/divider';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatChipsModule } from '@angular/material/chips';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';

interface DescuentoAsignado {
  id: number;
  valor: number;
  num_cuotas: number;
  es_cuota: boolean;
}

@Component({
  selector: 'app-asignacion-descuentos-dialog',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    MatDialogModule,
    MatButtonModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatCheckboxModule,
    MatDividerModule,
    MatIconModule,
    MatTooltipModule,
    MatExpansionModule,
    MatChipsModule,
    MatSlideToggleModule
  ],
  templateUrl: './asignacion-descuentos-dialog.component.html',
  styleUrls: ['./asignacion-descuentos-dialog.component.css']
})
export class AsignacionDescuentosDialogComponent implements OnInit {
  // Formulario para la asignación de descuentos
  asignacionForm: FormGroup;
  descuentoSeleccionado: number | null = null;
  descuentosAsignados: DescuentoAsignado[] = [];
  
  constructor(
    private fb: FormBuilder,
    public dialogRef: MatDialogRef<AsignacionDescuentosDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any
  ) {
    // Inicializar el formulario con los campos necesarios
    this.asignacionForm = this.fb.group({
      descuento_id: [null],
      valor_descuento: [null],
      es_cuota: [false],
      num_cuotas: [{value: 1, disabled: true}],
      descuentos: this.fb.array([])
    });

    // Observador para cambio en el campo es_cuota
    this.asignacionForm.get('es_cuota')?.valueChanges.subscribe(esCuota => {
      if (esCuota) {
        this.asignacionForm.get('num_cuotas')?.enable();
      } else {
        this.asignacionForm.get('num_cuotas')?.disable();
        this.asignacionForm.get('num_cuotas')?.setValue(1);
      }
    });

    // Observador para cambio de descuento seleccionado
    this.asignacionForm.get('descuento_id')?.valueChanges.subscribe(descuentoId => {
      if (descuentoId) {
        const descuento = this.obtenerDescuentoPorId(descuentoId);
        if (descuento) {
          // Si el descuento tiene la propiedad cuota, actualizar el campo es_cuota
          this.asignacionForm.get('es_cuota')?.setValue(descuento.cuota || false);
        }
      }
    });
  }
  
  ngOnInit(): void {
    // Si estamos en modo visualización, cargamos los descuentos existentes
    if (this.data.modoVisualizacion && this.data.trabajadores.length === 1) {
      const trabajador = this.data.trabajadores[0];
      if (trabajador.descuentos && trabajador.descuentos.length > 0) {
        // Convertir los descuentos existentes al formato del formulario
        this.descuentosAsignados = trabajador.descuentos.map((d: any) => ({
          id: d.id,
          valor: d.valor,
          num_cuotas: d.num_cuotas || 1,
          es_cuota: !!d.num_cuotas && d.num_cuotas > 1
        }));
      }
    }
  }

  // Getter para acceder al FormArray de descuentos
  get descuentosFormArray() {
    return this.asignacionForm.get('descuentos') as FormArray;
  }
  
  // Agregar un descuento a la lista de asignados
  agregarDescuento(): void {
    const descuentoId = this.asignacionForm.get('descuento_id')?.value;
    const valor = this.asignacionForm.get('valor_descuento')?.value;
    const esCuota = this.asignacionForm.get('es_cuota')?.value;
    const numCuotas = esCuota ? this.asignacionForm.get('num_cuotas')?.value : 1;

    if (!descuentoId || valor === null) {
      return;
    }

    // Verificar si el descuento ya está asignado
    const descuentoExistente = this.descuentosAsignados.find(d => d.id === descuentoId);
    if (descuentoExistente) {
      alert('Este descuento ya ha sido asignado');
      return;
    }

    // Agregar a la lista de descuentos asignados
    this.descuentosAsignados.push({
      id: descuentoId,
      valor: valor,
      num_cuotas: numCuotas,
      es_cuota: esCuota
    });

    // Limpiar campos del formulario
    this.asignacionForm.patchValue({
      descuento_id: null,
      valor_descuento: null,
      es_cuota: false,
      num_cuotas: 1
    });
  }

  // Eliminar un descuento de la lista de asignados
  eliminarDescuento(index: number): void {
    this.descuentosAsignados.splice(index, 1);
  }
  
  // Obtener descuento por ID
  obtenerDescuentoPorId(id: number): any {
    return this.data.descuentos.find((d: any) => d.id === id);
  }
  
  // Obtener nombre de un descuento por su ID
  obtenerNombreDescuento(descuentoId: number): string {
    const descuento = this.obtenerDescuentoPorId(descuentoId);
    return descuento ? descuento.nombre : 'Desconocido';
  }
  
  // Obtener tipo de un descuento
  obtenerTipoDescuento(descuentoId: number): string {
    const descuento = this.obtenerDescuentoPorId(descuentoId);
    if (!descuento) return 'Desconocido';
    
    switch (descuento.tipo) {
      case 'AFP': return 'AFP';
      case 'SALUD': return 'Salud';
      case 'OTRO': return 'Otro Descuento';
      default: return descuento.tipo;
    }
  }
  
  // Obtener tipo de valor de un descuento
  obtenerTipoValorDescuento(descuentoId: number): string {
    const descuento = this.obtenerDescuentoPorId(descuentoId);
    if (!descuento) return 'Desconocido';
    
    return descuento.tipo_valor === 'PORCENTAJE' ? 'Porcentaje' : 'Monto Fijo';
  }
  
  // Formatear un valor como moneda
  formatearValor(valor: number | undefined | null): string {
    if (valor === undefined || valor === null) {
      return 'No asignado';
    }
    return new Intl.NumberFormat('es-CL', { style: 'currency', currency: 'CLP' }).format(valor);
  }
  
  // Formatear un valor como porcentaje
  formatearPorcentaje(valor: number | undefined | null): string {
    if (valor === undefined || valor === null) {
      return 'No asignado';
    }
    return `${valor}%`;
  }
  
  // Verificar si hay alguna asignación seleccionada
  tieneAsignaciones(): boolean {
    return this.descuentosAsignados.length > 0;
  }
  
  // Cerrar el diálogo sin guardar cambios
  onCancel(): void {
    this.dialogRef.close();
  }
  
  // Guardar los cambios y cerrar el diálogo
  onSubmit(): void {
    if (this.tieneAsignaciones()) {
      this.dialogRef.close({
        descuentos: this.descuentosAsignados
      });
    }
  }
}