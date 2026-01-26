import { Component, Inject, OnInit, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser, CommonModule } from '@angular/common';
import { ContratistaApiService } from '../../../../../services/contratista-api.service';
import { FormsModule } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';
import { JwtService } from '../../../../../services/jwt.service';

interface Turno {
  id?: number;
  dia_semana: number;
  nombre_turno: string;
  hora_inicio: string;
  hora_fin: string;
  tiene_colacion: boolean;
  minutos_colacion: number;
  orden: number;
}

@Component({
  selector: 'app-horarios',
  standalone: true,
  imports: [MatTableModule, FormsModule, CommonModule],
  templateUrl: './horarios.component.html',
  styleUrl: './horarios.component.css'
})
export class HorariosComponent implements OnInit {
  
  constructor(
    private apiService: ContratistaApiService,
    private jwtService: JwtService,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {}

  public modals: { [key: string]: boolean } = {
    exitoModal: false,
    errorModal: false,
    crearHorario: false,
    modificarHorario: false,
    confirmacionModal: false,
  };

  public holding: string = '';
  public nombreHorario: string = '';
  public nombreHorarioNew: string = '';
  
  errorMessage!: string;
  selectedRows: any[] = [];
  public horariosCargados: any[] = [];
  public deletedRow: any[] = [];
  public selectedHorarioId: number | null = null;

  public diasSemana = [
    { valor: 0, nombre: 'Lunes' },
    { valor: 1, nombre: 'Martes' },
    { valor: 2, nombre: 'Miércoles' },
    { valor: 3, nombre: 'Jueves' },
    { valor: 4, nombre: 'Viernes' },
    { valor: 5, nombre: 'Sábado' },
    { valor: 6, nombre: 'Domingo' }
  ];

  // Para crear
  public turnosCrear: Turno[] = [];
  
  // Para modificar
  public turnosModificar: Turno[] = [];

  ngOnInit(): void {
    if (isPlatformBrowser(this.platformId)) {
      this.holding = this.getHoldingIdFromJWT(); 
      this.cargarHorarios();
    }
  }

  private getHoldingIdFromJWT(): string {
    try {
      const userInfo = this.jwtService.getUserInfo();
      const holdingId = userInfo?.holding_id;
      return holdingId ? holdingId.toString() : '';
    } catch (error) {
      console.error('Error extrayendo holding_id:', error);
      return '';
    }
  }

  agregarTurnoCrear(dia: number): void {
    const orden = this.turnosCrear.filter(t => t.dia_semana === dia).length;
    this.turnosCrear.push({
      dia_semana: dia,
      nombre_turno: '',
      hora_inicio: '08:00',
      hora_fin: '17:00',
      tiene_colacion: false,
      minutos_colacion: 0,
      orden: orden
    });
  }

  eliminarTurnoCrear(index: number): void {
    this.turnosCrear.splice(index, 1);
  }

  agregarTurnoModificar(dia: number): void {
    const orden = this.turnosModificar.filter(t => t.dia_semana === dia).length;
    this.turnosModificar.push({
      dia_semana: dia,
      nombre_turno: '',
      hora_inicio: '08:00',
      hora_fin: '17:00',
      tiene_colacion: false,
      minutos_colacion: 0,
      orden: orden
    });
  }

  eliminarTurnoModificar(index: number): void {
    this.turnosModificar.splice(index, 1);
  }

  getTurnosPorDia(turnos: Turno[], dia: number): Turno[] {
    return turnos.filter(t => t.dia_semana === dia).sort((a, b) => a.orden - b.orden);
  }

  getNombreDia(dia: number): string {
    return this.diasSemana.find(d => d.valor === dia)?.nombre || '';
  }

  crearHorario(): void {
    if (!this.nombreHorario) {
      this.errorMessage = 'Debe ingresar un nombre para el horario';
      this.openModal('errorModal');
      return;
    }

    if (this.turnosCrear.length === 0) {
      this.errorMessage = 'Debe crear al menos un turno';
      this.openModal('errorModal');
      return;
    }

    const data: any = {
      holding: this.holding,
      nombre: this.nombreHorario,
      turnos: this.turnosCrear
    };
    
    this.apiService.post('horarios/', data).subscribe({
      next: (response) => {
        this.closeModal('crearHorario');
        this.cargarHorarios();
        this.openModal('exitoModal');
        this.resetCrear();
      }, 
      error: (error) => {
        this.errorMessage = 'Error al crear el horario';
        this.openModal('errorModal');
      }
    });
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
    if (!this.nombreHorarioNew) {
      this.errorMessage = 'Debe ingresar un nombre para el horario';
      this.openModal('errorModal');
      return;
    }

    if (this.turnosModificar.length === 0) {
      this.errorMessage = 'Debe crear al menos un turno';
      this.openModal('errorModal');
      return;
    }

    const data: any = {
      holding: this.holding,
      id: this.selectedHorarioId,
      nombre: this.nombreHorarioNew,
      turnos: this.turnosModificar
    };
    
    this.apiService.put('horarios/', data).subscribe({
      next: (response) => {
        this.closeModal('modificarHorario');
        this.cargarHorarios();
        this.openModal('exitoModal');
        this.resetModificar();
      }, 
      error: (error) => {
        this.errorMessage = 'Error al modificar el horario';
        this.openModal('errorModal');
      }
    });
  }
  
  eliminarHorariosSeleccionadas(): void {
    if (this.deletedRow.length > 0) {
      const idsToDelete = this.deletedRow.map(row => row.id);
      this.apiService.delete('horarios/', {ids: idsToDelete}).subscribe({
        next: () => {
          this.closeModal('confirmacionModal');
          this.cargarHorarios();
          this.openModal('exitoModal');
          this.deletedRow = [];
        },
        error: (error) => {
          this.errorMessage = 'Error al eliminar horarios';
          this.openModal('errorModal');
        }
      });
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
      this.selectedRows = [row];
    }

    if (this.selectedRows.length > 0) {
      const lastSelectedRow = this.selectedRows[0];
      this.selectedHorarioId = lastSelectedRow.id;
      this.nombreHorarioNew = lastSelectedRow.nombre;
      this.turnosModificar = JSON.parse(JSON.stringify(lastSelectedRow.turnos || []));
    }
  }

  deseleccionarFila(event: MouseEvent): void {
    this.selectedRows = [];
  }

  openModal(key: string): void {
    this.modals[key] = true;
    if (key === 'confirmacionModal') {
      this.deletedRow = this.selectedRows;
    }
  }

  closeModal(key: string): void {
    this.modals[key] = false;
    if (key === 'exitoModal') {
      this.cargarHorarios();  
    }
  }

  resetCrear(): void {
    this.nombreHorario = '';
    this.turnosCrear = [];
  }

  resetModificar(): void {
    this.nombreHorarioNew = '';
    this.turnosModificar = [];
  }

  verDetalleHorario(horario: any): void {
    this.selectRow(horario);
  }
}