import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { ContratistaApiService } from '../../../../../services/contratista-api.service';

interface ElementoSeguridad {
  id: number;
  holding: number;
  elemento: string;
}

@Component({
  selector: 'app-elementos-seguridad',
  standalone: true,
  imports: [CommonModule, FormsModule, MatTableModule, MatButtonModule],
  templateUrl: './elementos-seguridad.component.html',
  styleUrl: './elementos-seguridad.component.css'
})
export class ElementosSeguridadComponent implements OnInit {

  elementosCargados: ElementoSeguridad[] = [];
  selectedRows: ElementoSeguridad[] = [];

  modals: Record<string, boolean> = {
    crearElemento: false,
    modificarElemento: false,
    confirmacionModal: false,
    exitoModal: false,
    errorModal: false,
  };

  codigo: string = '';
  elemento: string = '';
  codigoNew: string = '';
  elementoNew: string = '';

  errorMessage: string = '';
  holdingId: number | null = null;

  columnasDesplegadas: string[] = ['id', 'elemento'];

  constructor(private api: ContratistaApiService) {}

  ngOnInit(): void {
    const stored = localStorage.getItem('holding_id');
    if (stored) {
      this.holdingId = parseInt(stored, 10);
      this.cargarElementos();
    }
  }

  cargarElementos(): void {
    this.api.get(`elementos_seguridad/?holding=${this.holdingId}`).subscribe({
      next: (data: ElementoSeguridad[]) => {
        this.elementosCargados = data;
      },
      error: () => {
        this.errorMessage = 'Error al cargar elementos de seguridad.';
        this.openModal('errorModal');
      }
    });
  }

  openModal(modalName: string): void {
    if (modalName === 'modificarElemento' && this.selectedRows.length === 1) {
  this.elementoNew = this.selectedRows[0].elemento;
}
    this.modals[modalName] = true;
  }

  closeModal(modalName: string): void {
    this.modals[modalName] = false;
    if (modalName === 'crearElemento') {
      this.codigo = '';
      this.elemento = '';
    }
    if (modalName === 'modificarElemento') {
      this.codigoNew = '';
      this.elementoNew = '';
    }
  }

  selectRow(row: ElementoSeguridad): void {
    const idx = this.selectedRows.findIndex(r => r.id === row.id);
    if (idx >= 0) {
      this.selectedRows.splice(idx, 1);
    } else {
      this.selectedRows.push(row);
    }
  }

  isSelected(row: ElementoSeguridad): boolean {
    return this.selectedRows.some(r => r.id === row.id);
  }

  deseleccionarFila(event: Event): void {
    this.selectedRows = [];
  }

  crearElemento(): void {
    if (!this.codigo.trim() || !this.elemento.trim()) {
      this.errorMessage = 'Todos los campos son obligatorios.';
      this.openModal('errorModal');
      return;
    }
    this.api.post('elementos_seguridad/', {
      holding: this.holdingId,
      elemento: this.elemento
    }).subscribe({
      next: () => {
        this.closeModal('crearElemento');
        this.cargarElementos();
        this.openModal('exitoModal');
      },
      error: () => {
        this.errorMessage = 'Error al crear el elemento de seguridad.';
        this.openModal('errorModal');
      }
    });
  }

  modificarElemento(): void {
    if (!this.codigoNew.trim() || !this.elementoNew.trim()) {
      this.errorMessage = 'Todos los campos son obligatorios.';
      this.openModal('errorModal');
      return;
    }
    this.api.patch('elementos_seguridad/', {
      id: this.selectedRows[0].id,
      elemento: this.elementoNew
    }).subscribe({
      next: () => {
        this.closeModal('modificarElemento');
        this.selectedRows = [];
        this.cargarElementos();
        this.openModal('exitoModal');
      },
      error: () => {
        this.errorMessage = 'Error al modificar el elemento de seguridad.';
        this.openModal('errorModal');
      }
    });
  }

  eliminarElementosSeleccionados(): void {
    const ids = this.selectedRows.map(r => r.id);
    this.api.delete('elementos_seguridad/', { ids }).subscribe({
      next: () => {
        this.closeModal('confirmacionModal');
        this.selectedRows = [];
        this.cargarElementos();
        this.openModal('exitoModal');
      },
      error: () => {
        this.errorMessage = 'Error al eliminar los elementos de seguridad.';
        this.openModal('errorModal');
      }
    });
  }
}