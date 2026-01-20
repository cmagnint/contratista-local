// casas.component.ts - MODIFICADO

import { Component, Inject, OnInit, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser, CommonModule } from '@angular/common';
import { ContratistaApiService } from '../../../../../services/contratista-api.service';
import { FormsModule } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-casas',
  standalone: true,
  imports: [
    MatTableModule,
    FormsModule,
    CommonModule,
    MatIconModule,
  ],
  templateUrl: './casas.component.html',
  styleUrl: './casas.component.css'
})
export class CasasComponent implements OnInit {
  
  public modals: { [key: string]: boolean } = {
    exitoModal: false,
    errorModal: false,
    crearCasa: false,
    modificarCasa: false,
    confirmacionModal: false,
  };

  public CasasSeleccionada: any = {
    id_casa_seleccionada : 0,
    nombre_casa_seleccionada : '',
    estado_casa_seleccionada: false,
  }

  public holding: string = '';
  public nombreCasa: string = '';
  public nombreCasaNew: string = '';
  public estadoCasaNew: boolean = true;

  errorMessage!: string;
  selectedRows: any[] = [];
  dropdownOpen: boolean = false;
  public todasSeleccionadas: boolean = false;
  public casasCargadas: any[] = [];
  columnasDesplegadas = ['codigo','nombre','estado'];
  public deletedRow: any[] = [];
  public selectedCasaId: number | null = null;

  constructor(
    private apiService: ContratistaApiService,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {}

  ngOnInit(): void {
    if (isPlatformBrowser(this.platformId)) {
      this.holding = localStorage.getItem('holding_id') || '';
      this.cargarCasas();
    }
  }

  crearCasa(): void {
    let data = {
      holding: this.holding,
      nombre : this.nombreCasa,
    }
    this.apiService.post('api_casas_trabajadores/', data).subscribe({
      next: (response) => {
        console.log(response);
        this.closeModal('crearCasa');
        this.cargarCasas();
        this.openModal('exitoModal');
        this.limpiarFormularioCrear();
      }, 
      error:(error) => {
        this.openModal('errorModal');
      }
    })
  }

  limpiarFormularioCrear(): void {
    this.nombreCasa = '';
  }

  cargarCasas(): void {
    this.apiService.get(`api_casas_trabajadores/?holding=${this.holding}`).subscribe({
      next: (response) => {
        this.casasCargadas = response;
      },
      error: (error) => {
        console.error('Error al recibir las casas:', error);
      }
    });
  }

  modificarCasa(): void {
    let data = {
      holding: this.holding,
      id : this.selectedCasaId,
      nombre: this.nombreCasaNew,
      estado: this.estadoCasaNew,
    }
    this.apiService.put('api_casas_trabajadores/', data).subscribe({
      next:(response) => {
        this.closeModal('modificarCasa');
        this.cargarCasas();
        this.openModal('exitoModal');
      }, 
      error:(error) => {
        console.log(error);
        this.openModal('errorModal');
      }
    })
  }
  
  eliminarCasasSeleccionadas(): void {
    if (this.deletedRow.length > 0) {
      const idsToDelete = this.deletedRow.map(row => row.id);
      this.apiService.delete('api_casas_trabajadores/', {ids: idsToDelete}).subscribe({
        next: () => {
          this.closeModal('confirmacionModal')
          this.cargarCasas();
          this.openModal('exitoModal');
          this.deletedRow = [];
        },
        error: (error) => {
          this.openModal('errorModal');
          console.error('Error al eliminar casas:', error);
        }
      });
    }
  }

  toggleEstado() {
    this.estadoCasaNew = !this.estadoCasaNew;
  }

  toggleSelection(casaId: number): void {
    if (this.selectedCasaId === casaId) {
      this.selectedCasaId = null;
    } else {
      this.selectedCasaId = casaId;
    }
  }

  isSelected(row: any): boolean {
    return this.selectedRows.some(r => r.id === row.id);
  }

  selectRow(row: any): void {
    const index = this.selectedRows.findIndex(selectedRow => selectedRow.id === row.id);
    if (index > -1) {
      this.selectedRows.splice(index, 1);
    } else {
      this.selectedRows.push(row);
    }

    if (this.selectedRows.length > 0){
      const lastSelectedRow = this.selectedRows[this.selectedRows.length - 1];
      this.CasasSeleccionada = {
        id_casa_seleccionada : lastSelectedRow.id,
        nombre_casa_seleccionada : lastSelectedRow.nombre,
        estado_casa_seleccionada: lastSelectedRow.estado,
      };
      this.selectedCasaId = this.CasasSeleccionada.id_casa_seleccionada;
      this.nombreCasaNew = this.CasasSeleccionada.nombre_casa_seleccionada;
      this.estadoCasaNew = this.CasasSeleccionada.estado_casa_seleccionada;
    } else {
      this.CasasSeleccionada = {
        id_casa_seleccionada : 0,
        nombre_casa_seleccionada : '',
        estado_casa_seleccionada: false,
      }
    }
  }

  formatRUT(event: Event): void {
    const target = event.target as HTMLInputElement;
    if (!target) return;

    let rut = target.value.replace(/\D/g, '');
    let parts = [];
    const verifier = rut.slice(-1);
    rut = rut.slice(0, -1);
    while (rut.length > 3) {
      parts.unshift(rut.slice(-3));
      rut = rut.slice(0, -3);
    }
    parts.unshift(rut);
    target.value = parts.join('.') + '-' + verifier;
    if (target.value === '-') {
      target.value = '';
    }
  }
  
  formatRUTString(value: string): string {
    let rut = value.replace(/\D/g, '');
    let parts = [];
    const verifier = rut.slice(-1);
    rut = rut.slice(0, -1);
    while (rut.length > 3) {
      parts.unshift(rut.slice(-3));
      rut = rut.slice(0, -3);
    }
    parts.unshift(rut);
    return parts.join('.') + '-' + verifier;
  }

  toggleDropdown() {
    this.dropdownOpen = !this.dropdownOpen;
  }

  deseleccionarFila(event: MouseEvent) {
    this.selectedRows = [];
  }

  openModal(key: string): void {
    this.modals[key] = true;
    if(key == 'confirmacionModal'){
      this.deletedRow = this.selectedRows;
      console.log(this.deletedRow);
    }
  }

  closeModal(key: string): void {
    this.modals[key] = false;
    if (key === 'exitoModal') {
      this.cargarCasas();  
    }
  }

  checkValue(): void {
    
  }
}