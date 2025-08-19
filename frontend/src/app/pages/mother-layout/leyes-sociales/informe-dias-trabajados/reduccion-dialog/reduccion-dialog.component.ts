import { Component, Inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatSliderModule } from '@angular/material/slider';

export interface DialogData {
  clientes: any[];
  porcentajeReduccion: number;
  clientesSeleccionados: number[];
}

@Component({
  selector: 'app-reduccion-dialog',
  templateUrl: './reduccion-dialog.component.html',
  styleUrls: ['./reduccion-dialog.component.css'],
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatDialogModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatCheckboxModule,
    MatSliderModule
  ]
})
export class ReduccionDialogComponent {
  clientesSeleccionadosMap: {[key: number]: boolean} = {};

  constructor(
    public dialogRef: MatDialogRef<ReduccionDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: DialogData
  ) {
    // Inicializar mapa de selección
    this.data.clientes.forEach(cliente => {
      this.clientesSeleccionadosMap[cliente.id] = false;
    });
  }

  // Método para actualizar el porcentaje desde el slider
  updatePorcentaje(event: any): void {
    this.data.porcentajeReduccion = event.value;
  }

  getResult(): any {
    // Convertir mapa a array de IDs
    const clientesSeleccionados = Object.keys(this.clientesSeleccionadosMap)
      .filter(id => this.clientesSeleccionadosMap[Number(id)])
      .map(id => Number(id));
    
    return {
      clientesSeleccionados,
      porcentajeReduccion: this.data.porcentajeReduccion
    };
  }

  hayClientesSeleccionados(): boolean {
    return Object.values(this.clientesSeleccionadosMap).some(value => value);
  }
}