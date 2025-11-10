// horarios.component.ts - VERSIÓN CON HORAS POR DÍA

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

  // Horario seleccionado
  public horarioSeleccionado: any = {
    id_horario_seleccionado: 0,
    nombre_horario_seleccionado: '',
    jornada_horario_seleccionado: 0.0,
  }

  public holding: string = '';
  public nombreHorario: string = '';
  
  // Horas por día para CREAR
  public horasLunes: number = 9.0;
  public horasMartes: number = 9.0;
  public horasMiercoles: number = 9.0;
  public horasJueves: number = 9.0;
  public horasViernes: number = 9.0;
  public horasSabado: number = 0.0;
  public horasDomingo: number = 0.0;
 
  errorMessage!: string;
  selectedRows: any[] = [];
  dropdownOpen: boolean = false;
  public todasSeleccionadas: boolean = false;
  public horariosCargados: any[] = [];
  columnasDesplegadas = ['codigo', 'nombre', 'lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo'];
  public deletedRow: any[] = [];
  public selectedHorarioId: number | null = null;
  
  // Variables para MODIFICAR
  public nombreHorarioNew: string = '';
  public horasLunesNew: number = 9.0;
  public horasMartesNew: number = 9.0;
  public horasMiercolesNew: number = 9.0;
  public horasJuevesNew: number = 9.0;
  public horasViernesNew: number = 9.0;
  public horasSabadoNew: number = 0.0;
  public horasDomingoNew: number = 0.0;
  
  ngOnInit(): void {
    if (isPlatformBrowser(this.platformId)) {
      this.holding = localStorage.getItem('holding_id') || '';
      this.cargarHorarios();
    }
  }

  crearHorario(): void {
    let data = {
      holding: this.holding,
      nombre: this.nombreHorario,
      jornada: 9.0, // Mantener por compatibilidad
      horas_lunes: this.horasLunes,
      horas_martes: this.horasMartes,
      horas_miercoles: this.horasMiercoles,
      horas_jueves: this.horasJueves,
      horas_viernes: this.horasViernes,
      horas_sabado: this.horasSabado,
      horas_domingo: this.horasDomingo
    }
    
    this.apiService.post('horarios/', data).subscribe({
      next: (response) => {
        console.log(response);
        this.closeModal('crearHorario');
        this.cargarHorarios();
        this.openModal('exitoModal');
        // Resetear campos
        this.nombreHorario = '';
        this.horasLunes = 9.0;
        this.horasMartes = 9.0;
        this.horasMiercoles = 9.0;
        this.horasJueves = 9.0;
        this.horasViernes = 9.0;
        this.horasSabado = 0.0;
        this.horasDomingo = 0.0;
      }, 
      error: (error) => {
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
      nombre: this.nombreHorarioNew,
      jornada: 9.0, // Mantener por compatibilidad
      horas_lunes: this.horasLunesNew,
      horas_martes: this.horasMartesNew,
      horas_miercoles: this.horasMiercolesNew,
      horas_jueves: this.horasJuevesNew,
      horas_viernes: this.horasViernesNew,
      horas_sabado: this.horasSabadoNew,
      horas_domingo: this.horasDomingoNew
    }
    
    this.apiService.put('horarios/', data).subscribe({
      next: (response) => {
        this.closeModal('modificarHorario');
        this.cargarHorarios();
        this.openModal('exitoModal');
      }, 
      error: (error) => {
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
        nombre_horario_seleccionado: lastSelectedRow.nombre,
        jornada_horario_seleccionado: lastSelectedRow.jornada,
      };
      this.selectedHorarioId = this.horarioSeleccionado.id_horario_seleccionado;
      this.nombreHorarioNew = this.horarioSeleccionado.nombre_horario_seleccionado;
      
      // Cargar horas por día
      this.horasLunesNew = lastSelectedRow.horas_lunes || 9.0;
      this.horasMartesNew = lastSelectedRow.horas_martes || 9.0;
      this.horasMiercolesNew = lastSelectedRow.horas_miercoles || 9.0;
      this.horasJuevesNew = lastSelectedRow.horas_jueves || 9.0;
      this.horasViernesNew = lastSelectedRow.horas_viernes || 9.0;
      this.horasSabadoNew = lastSelectedRow.horas_sabado || 0.0;
      this.horasDomingoNew = lastSelectedRow.horas_domingo || 0.0;
    } else {
      this.horarioSeleccionado = {
        id_horario_seleccionado: 0,
        nombre_horario_seleccionado: '',
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