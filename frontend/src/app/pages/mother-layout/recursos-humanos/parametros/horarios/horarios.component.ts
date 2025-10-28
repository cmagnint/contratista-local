// horarios.component.ts - VERSIÓN MODIFICADA CON CAMPO NOMBRE

import { Component, Inject, OnInit, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser, CommonModule } from '@angular/common';
import { ContratistaApiService } from '../../../../../services/contratista-api.service';
import { FormsModule } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';


@Component({
  selector: 'app-horarios',
  standalone: true,
  imports: [
    MatTableModule,
    FormsModule,
    CommonModule,
  ],
  templateUrl: './horarios.component.html',
  styleUrl: './horarios.component.css'
})
export class HorariosComponent implements OnInit {
  //VARIABLES

  constructor(
    private apiService: ContratistaApiService,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {}

  // Booleanos para abrir o cerrar ventanas
  public modals: { [key: string]: boolean } = {
    exitoModal: false,
    errorModal: false,
    crearHorario: false,
    modificarHorario: false,
    confirmacionModal: false,
    eliminarModal: false,
  };

  //Horario seleccionado
  public horarioSeleccionado: any = {
    id_horario_seleccionado: 0,
    nombre_horario_seleccionado: '',  // ✅ NUEVO
    jornada_horario_seleccionado: 0.0,
  }

  
  public holding: string = ''; //Variable para guardar el ID del holding
  public nombreHorario: string = '';  // ✅ NUEVO
  public jornadaHorario: number | null = null;
 
  errorMessage!: string;
  selectedRows: any[] = [];
  dropdownOpen: boolean = false;

  public todasSeleccionadas: boolean = false;

  public horariosCargados: any[] = [];

  columnasDesplegadas = ['codigo', 'nombre', 'jornada'];  // ✅ AGREGADA COLUMNA 'nombre'
  
  public deletedRow: any[] = [];

  public selectedHorarioId: number | null = null;
  public nombreHorarioNew: string = '';  // ✅ NUEVO
  public jornadaHorarioNew: number | null = null;
  
  //FUNCIONES
  
  ngOnInit(): void {
    if (isPlatformBrowser(this.platformId)) {
      this.holding = localStorage.getItem('holding_id') || '';
      this.cargarHorarios();
    }
  }

  //FUNCIONES CRUD

  crearHorario(): void {
    let data = {
      holding: this.holding,
      nombre: this.nombreHorario,  // ✅ NUEVO
      jornada: this.jornadaHorario,
    }
    this.apiService.post('horarios/', data).subscribe({
      next: (response) => {
        console.log(response);
        this.closeModal('crearHorario');
        this.cargarHorarios();
        this.openModal('exitoModal');
        
      }, error: (error) => {
        this.openModal('errorModal');
      }
    })
  }

  cargarHorarios(): void {
    this.apiService.get(`horarios/?holding=${this.holding}`).subscribe({
      next: (response) => {
        this.horariosCargados = response;
      },
      error: (error) => {
        console.error('Error al recibir los horarios:', error);
      }
    });
  }

  modificarHorario(): void {
    let data = {
      holding: this.holding,
      id: this.selectedHorarioId,
      nombre: this.nombreHorarioNew,  // ✅ NUEVO
      jornada: this.jornadaHorarioNew,
    }
    this.apiService.put('horarios/', data).subscribe({
      next: (response) => {
        this.closeModal('modificarHorario');
        this.cargarHorarios();
        this.openModal('exitoModal');
      }, error: (error) => {
        console.log(error);
        this.openModal('errorModal');
      }
    })
  }
  
  eliminarHorariosSeleccionadas(): void {
    if (this.deletedRow.length > 0) {
      const idsToDelete = this.deletedRow.map(row => row.id);
      this.apiService.delete('horarios/', {ids: idsToDelete}).subscribe({
        next: () => {
          this.closeModal('confirmacionModal')
          this.cargarHorarios();
          this.openModal('exitoModal');
          this.deletedRow = [];
        },
        error: (error) => {
          this.openModal('errorModal');
          console.error('Error al eliminar horarios:', error);
        }
      });
    }
  }

  //------------------------------------------------------------------------------//

  toggleSelection(horarioId: number): void {
    if (this.selectedHorarioId === horarioId) {
      this.selectedHorarioId = null;
    } else {
      this.selectedHorarioId = horarioId;
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

    if (this.selectedRows.length > 0) {
      const lastSelectedRow = this.selectedRows[this.selectedRows.length - 1];
      this.horarioSeleccionado = {
        id_horario_seleccionado: lastSelectedRow.id,
        nombre_horario_seleccionado: lastSelectedRow.nombre,  // ✅ NUEVO
        jornada_horario_seleccionado: lastSelectedRow.jornada,
      };
      this.selectedHorarioId = this.horarioSeleccionado.id_horario_seleccionado;
      this.nombreHorarioNew = this.horarioSeleccionado.nombre_horario_seleccionado;  // ✅ NUEVO
      this.jornadaHorarioNew = this.horarioSeleccionado.jornada_horario_seleccionado;
    } else {
      this.horarioSeleccionado = {
        id_horario_seleccionado: 0,
        nombre_horario_seleccionado: '',  // ✅ NUEVO
        jornada_horario_seleccionado: 0.0,
      }
    }
  }

  toggleDropdown() {
    this.dropdownOpen = !this.dropdownOpen;
  }

  deseleccionarFila(event: MouseEvent) {
    this.selectedRows = [];
  }

  openModal(key: string): void {
    this.modals[key] = true;
    if (key == 'confirmacionModal') {
      this.deletedRow = this.selectedRows;
      console.log(this.deletedRow);
    }
  }

  closeModal(key: string): void {
    this.modals[key] = false;
    if (key === 'exitoModal') {
      this.cargarHorarios();  
    }
  }
}