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
import { MatTabsModule } from '@angular/material/tabs';
import { MatBadgeModule } from '@angular/material/badge';

@Component({
  selector: 'app-asignacion-haberes-dialog',
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
    MatTabsModule,
    MatBadgeModule
  ],
  templateUrl: './asignacion-haberes-dialog.component.html',
  styleUrls: ['./asignacion-haberes-dialog.component.css']
})
export class AsignacionHaberesDialogComponent implements OnInit {
  // Formulario para la asignación de haberes
  asignacionForm: FormGroup;
  
  // Control para asignar el mismo valor a todos los trabajadores
  usarMismoValor: boolean = true;
  
  // Mapeo de IDs de trabajadores a sus nombres para el UI
  trabajadoresMap: {[key: number]: string} = {};
  
  // Contenedor para mostrar haberes asignados en modo visualización
  haberesAsignados: any[] = [];
  
  // Lista de haberes disponibles
  haberesDisponibles: any[] = [];
  
  // Haber seleccionado actualmente
  haberSeleccionado: any = null;
  
  constructor(
    private fb: FormBuilder,
    public dialogRef: MatDialogRef<AsignacionHaberesDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any
  ) {
    // Inicializar el formulario con los campos necesarios
    this.asignacionForm = this.fb.group({
      haberes_asignaciones: this.fb.array([])
    });
    
    // Guardar la lista de haberes disponibles
    this.haberesDisponibles = this.data.haberes || [];
    
    // Construir el mapa de IDs de trabajadores a nombres
    if (this.data.trabajadores) {
      this.data.trabajadores.forEach((t: any) => {
        this.trabajadoresMap[t.id] = t.nombre_completo || `${t.nombres} ${t.apellidos || ''}`.trim();
      });
    }
  }
  
  ngOnInit(): void {
    // Si estamos en modo visualización, preparar datos para mostrar
    if (this.data.modoVisualizacion) {
      this.prepararDatosVisualizacion();
    }
  }
  
  // Preparar datos para modo visualización
  prepararDatosVisualizacion(): void {
    const trabajador = this.data.trabajadores[0];
    this.haberesAsignados = [];
    
    // Verificar si tenemos haberes asignados a través de la nueva relación
    if (trabajador.haberes_asignados && trabajador.haberes_asignados.length > 0) {
      this.haberesAsignados = trabajador.haberes_asignados.map((asignacion: any) => ({
        ...asignacion.haber,
        valor: asignacion.valor
      }));
    }
    // Si no, usar la vieja relación directa
    else if (trabajador.haberes && trabajador.haberes.length > 0) {
      this.haberesAsignados = trabajador.haberes;
    }
  }
  
  // Getter para acceder fácilmente al array de haberes
  get haberesAsignaciones() {
    return this.asignacionForm.get('haberes_asignaciones') as FormArray;
  }
  
  // Seleccionar un haber para asignar
  seleccionarHaber(haber: any): void {
    // Guardar el haber seleccionado
    this.haberSeleccionado = haber;
    
    // Limpiar el FormArray anterior
    while (this.haberesAsignaciones.length > 0) {
      this.haberesAsignaciones.removeAt(0);
    }
    
    // Crear grupo de formulario para el haber
    const haberGroup = this.fb.group({
      haber_id: [haber.id],
      haber_nombre: [haber.nombre],
      tipo_valor: [haber.tipo_valor],
      imponible: [haber.imponible],
      // Este será el valor único si se usa el mismo para todos
      valor_comun: [0],
      // Valores específicos por trabajador (solo se usarán si usarMismoValor = false)
      valores_por_trabajador: this.fb.array([])
    });
    
    // Agregar valores por trabajador
    const valoresPorTrabajadorArray = haberGroup.get('valores_por_trabajador') as FormArray;
    
    this.data.trabajadores.forEach((trabajador: any) => {
      // Buscar si este trabajador ya tiene asignado este haber
      let valorExistente = 0;
      
      // Primero verificamos haberes_asignados (relación TrabajadorHaber)
      if (trabajador.haberes_asignados) {
        const asignacionExistente = trabajador.haberes_asignados.find((h: any) => 
          h.haber.id === haber.id
        );
        if (asignacionExistente) {
          valorExistente = asignacionExistente.valor;
        }
      }
      // Si no, verificamos si existe en la lista de haberes directa (vieja relación)
      else if (trabajador.haberes) {
        const asignacionExistente = trabajador.haberes.find((h: any) => h.id === haber.id);
        if (asignacionExistente) {
          valorExistente = asignacionExistente.valor || 0;
        }
      }
      
      valoresPorTrabajadorArray.push(this.fb.group({
        trabajador_id: [trabajador.id],
        valor: [valorExistente]
      }));
    });
    
    // Añadir el grupo al array principal
    this.haberesAsignaciones.push(haberGroup);
  }
  
  // Función para obtener el array de valores por trabajador
  getValoresPorTrabajador() {
    if (this.haberesAsignaciones.length === 0) return [];
    return (this.haberesAsignaciones.at(0).get('valores_por_trabajador') as FormArray).controls;
  }
  
  // Cambiar entre modo de asignación único o individual
  toggleModoAsignacion() {
    this.usarMismoValor = !this.usarMismoValor;
  }
  
  // Verificar si hay alguna asignación seleccionada
  tieneAsignaciones(): boolean {
    if (!this.haberSeleccionado) return false;
    
    const tieneHaberesAsignados = this.haberesAsignaciones.controls.some(control => {
      if (this.usarMismoValor) {
        return control.get('valor_comun')?.value > 0;
      } else {
        const valoresPorTrabajador = control.get('valores_por_trabajador') as FormArray;
        return valoresPorTrabajador.controls.some(valorControl => 
          valorControl.get('valor')?.value > 0
        );
      }
    });
    
    return tieneHaberesAsignados;
  }
  
  // Formatear un valor como moneda
  formatearValor(valor: number | undefined | null): string {
    if (valor === undefined || valor === null) {
      return 'No asignado';
    }
    return new Intl.NumberFormat('es-CL', { style: 'currency', currency: 'CLP' }).format(valor);
  }
  
  // Obtener el texto de tipo de valor para visualización
  getTipoValorText(tipo: string): string {
    return tipo === 'CANTIDAD' ? 'Por Cantidad' : 'Monto Fijo';
  }
  
  // Cerrar el diálogo sin guardar cambios
  onCancel(): void {
    this.dialogRef.close();
  }
  
  // Guardar los cambios y cerrar el diálogo
  onSubmit(): void {
    if (this.tieneAsignaciones()) {
      // Construir el objeto de datos a enviar al backend
      const formValue = this.asignacionForm.value;
      const result: any = {
        haberes_asignaciones: []
      };
      
      // Procesar haberes asignados
      formValue.haberes_asignaciones.forEach((haberData: any) => {
        // Si el valor común es mayor que 0 (en modo valor común)
        if (this.usarMismoValor && haberData.valor_comun > 0) {
          // Añadir una asignación para cada trabajador con el mismo valor
          this.data.trabajadores.forEach((trabajador: any) => {
            result.haberes_asignaciones.push({
              trabajador_id: trabajador.id,
              haber_id: haberData.haber_id,
              valor: haberData.valor_comun
            });
          });
        } 
        // En modo individual, añadir solo las asignaciones con valor > 0
        else if (!this.usarMismoValor) {
          haberData.valores_por_trabajador.forEach((valorTrabajador: any) => {
            if (valorTrabajador.valor > 0) {
              result.haberes_asignaciones.push({
                trabajador_id: valorTrabajador.trabajador_id,
                haber_id: haberData.haber_id,
                valor: valorTrabajador.valor
              });
            }
          });
        }
      });
      
      this.dialogRef.close(result);
    }
  }
}