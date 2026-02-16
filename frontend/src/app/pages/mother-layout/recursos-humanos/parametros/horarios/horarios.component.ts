import { Component, Inject, OnInit, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser, CommonModule } from '@angular/common';
import { ContratistaApiService } from '../../../../../services/contratista-api.service';
import { FormsModule } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';
import { JwtService } from '../../../../../services/jwt.service';
import { SociedadGlobalService } from '../../../../../services/sociedad-global.service';

interface DiaHorario {
  inicio: string;
  fin: string;
  colacion: boolean;
  minutos_colacion: number;
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
    private sociedadGlobalService: SociedadGlobalService,
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

  // Sociedades
  public sociedadesDisponibles: Array<{ id: number; nombre: string }> = [];
  public sociedadSeleccionada: { id: number; nombre: string } | null = null;
  public sociedadSeleccionadaModificar: { id: number; nombre: string } | null = null;

  public diasSemana = [
    { key: 'lunes', nombre: 'Lunes' },
    { key: 'martes', nombre: 'Martes' },
    { key: 'miercoles', nombre: 'Miércoles' },
    { key: 'jueves', nombre: 'Jueves' },
    { key: 'viernes', nombre: 'Viernes' },
    { key: 'sabado', nombre: 'Sábado' },
    { key: 'domingo', nombre: 'Domingo' }
  ];

  // Para crear
  public horariosCrear: { [key: string]: DiaHorario } = {
    lunes: { inicio: '08:00', fin: '17:00', colacion: true, minutos_colacion: 60 },
    martes: { inicio: '08:00', fin: '17:00', colacion: true, minutos_colacion: 60 },
    miercoles: { inicio: '08:00', fin: '17:00', colacion: true, minutos_colacion: 60 },
    jueves: { inicio: '08:00', fin: '17:00', colacion: true, minutos_colacion: 60 },
    viernes: { inicio: '08:00', fin: '17:00', colacion: true, minutos_colacion: 60 },
    sabado: { inicio: '', fin: '', colacion: false, minutos_colacion: 0 },
    domingo: { inicio: '', fin: '', colacion: false, minutos_colacion: 0 }
  };

  // Para modificar
  public horariosModificar: { [key: string]: DiaHorario } = {
    lunes: { inicio: '', fin: '', colacion: false, minutos_colacion: 0 },
    martes: { inicio: '', fin: '', colacion: false, minutos_colacion: 0 },
    miercoles: { inicio: '', fin: '', colacion: false, minutos_colacion: 0 },
    jueves: { inicio: '', fin: '', colacion: false, minutos_colacion: 0 },
    viernes: { inicio: '', fin: '', colacion: false, minutos_colacion: 0 },
    sabado: { inicio: '', fin: '', colacion: false, minutos_colacion: 0 },
    domingo: { inicio: '', fin: '', colacion: false, minutos_colacion: 0 }
  };

  ngOnInit(): void {
    if (isPlatformBrowser(this.platformId)) {
      this.holding = this.getHoldingIdFromJWT(); 
      this.cargarSociedadesDisponibles();
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

  cargarSociedadesDisponibles(): void {
    const sociedadesStr = localStorage.getItem('sociedades');
    if (sociedadesStr) {
      this.sociedadesDisponibles = JSON.parse(sociedadesStr);
    }
  }

  calcularHorasDia(dia: DiaHorario): number {
    if (!dia.inicio || !dia.fin) return 0;
    
    const [horaIni, minIni] = dia.inicio.split(':').map(Number);
    const [horaFin, minFin] = dia.fin.split(':').map(Number);
    
    const totalMinutos = (horaFin * 60 + minFin) - (horaIni * 60 + minIni);
    
    return totalMinutos / 60;
  }

  calcularTotalSemanal(horarios: { [key: string]: DiaHorario }): number {
    let total = 0;
    this.diasSemana.forEach(dia => {
      total += this.calcularHorasDia(horarios[dia.key]);
    });
    return total;
  }

  crearHorario(): void {
    if (!this.sociedadSeleccionada) {
      this.errorMessage = 'Debe seleccionar una sociedad';
      this.openModal('errorModal');
      return;
    }

    if (!this.nombreHorario) {
      this.errorMessage = 'Debe ingresar un nombre para el horario';
      this.openModal('errorModal');
      return;
    }

    const data: any = {
      holding: this.holding,
      sociedad: this.sociedadSeleccionada.id,
      nombre: this.nombreHorario,
      lunes_inicio: this.horariosCrear['lunes'].inicio || null,
      lunes_fin: this.horariosCrear['lunes'].fin || null,
      lunes_colacion: this.horariosCrear['lunes'].colacion,
      lunes_minutos_colacion: this.horariosCrear['lunes'].minutos_colacion,
      martes_inicio: this.horariosCrear['martes'].inicio || null,
      martes_fin: this.horariosCrear['martes'].fin || null,
      martes_colacion: this.horariosCrear['martes'].colacion,
      martes_minutos_colacion: this.horariosCrear['martes'].minutos_colacion,
      miercoles_inicio: this.horariosCrear['miercoles'].inicio || null,
      miercoles_fin: this.horariosCrear['miercoles'].fin || null,
      miercoles_colacion: this.horariosCrear['miercoles'].colacion,
      miercoles_minutos_colacion: this.horariosCrear['miercoles'].minutos_colacion,
      jueves_inicio: this.horariosCrear['jueves'].inicio || null,
      jueves_fin: this.horariosCrear['jueves'].fin || null,
      jueves_colacion: this.horariosCrear['jueves'].colacion,
      jueves_minutos_colacion: this.horariosCrear['jueves'].minutos_colacion,
      viernes_inicio: this.horariosCrear['viernes'].inicio || null,
      viernes_fin: this.horariosCrear['viernes'].fin || null,
      viernes_colacion: this.horariosCrear['viernes'].colacion,
      viernes_minutos_colacion: this.horariosCrear['viernes'].minutos_colacion,
      sabado_inicio: this.horariosCrear['sabado'].inicio || null,
      sabado_fin: this.horariosCrear['sabado'].fin || null,
      sabado_colacion: this.horariosCrear['sabado'].colacion,
      sabado_minutos_colacion: this.horariosCrear['sabado'].minutos_colacion,
      domingo_inicio: this.horariosCrear['domingo'].inicio || null,
      domingo_fin: this.horariosCrear['domingo'].fin || null,
      domingo_colacion: this.horariosCrear['domingo'].colacion,
      domingo_minutos_colacion: this.horariosCrear['domingo'].minutos_colacion
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
    let url = `horarios/?holding=${this.holding}`;
    
    // Filtrar por sociedad global si está seleccionada
    const sociedadGlobal = this.sociedadGlobalService.getSociedad();
    if (sociedadGlobal) {
      url += `&sociedad=${sociedadGlobal.id}`;
    }
    
    this.apiService.get(url).subscribe({
      next: (response) => {
        this.horariosCargados = response;
      },
      error: (error) => {
        console.error('Error al recibir los horarios:', error);
      }
    });
  }

  modificarHorario(): void {
    if (!this.sociedadSeleccionadaModificar) {
      this.errorMessage = 'Debe seleccionar una sociedad';
      this.openModal('errorModal');
      return;
    }

    if (!this.nombreHorarioNew) {
      this.errorMessage = 'Debe ingresar un nombre para el horario';
      this.openModal('errorModal');
      return;
    }

    const data: any = {
      holding: this.holding,
      id: this.selectedHorarioId,
      sociedad: this.sociedadSeleccionadaModificar.id,
      nombre: this.nombreHorarioNew,
      lunes_inicio: this.horariosModificar['lunes'].inicio || null,
      lunes_fin: this.horariosModificar['lunes'].fin || null,
      lunes_colacion: this.horariosModificar['lunes'].colacion,
      lunes_minutos_colacion: this.horariosModificar['lunes'].minutos_colacion,
      martes_inicio: this.horariosModificar['martes'].inicio || null,
      martes_fin: this.horariosModificar['martes'].fin || null,
      martes_colacion: this.horariosModificar['martes'].colacion,
      martes_minutos_colacion: this.horariosModificar['martes'].minutos_colacion,
      miercoles_inicio: this.horariosModificar['miercoles'].inicio || null,
      miercoles_fin: this.horariosModificar['miercoles'].fin || null,
      miercoles_colacion: this.horariosModificar['miercoles'].colacion,
      miercoles_minutos_colacion: this.horariosModificar['miercoles'].minutos_colacion,
      jueves_inicio: this.horariosModificar['jueves'].inicio || null,
      jueves_fin: this.horariosModificar['jueves'].fin || null,
      jueves_colacion: this.horariosModificar['jueves'].colacion,
      jueves_minutos_colacion: this.horariosModificar['jueves'].minutos_colacion,
      viernes_inicio: this.horariosModificar['viernes'].inicio || null,
      viernes_fin: this.horariosModificar['viernes'].fin || null,
      viernes_colacion: this.horariosModificar['viernes'].colacion,
      viernes_minutos_colacion: this.horariosModificar['viernes'].minutos_colacion,
      sabado_inicio: this.horariosModificar['sabado'].inicio || null,
      sabado_fin: this.horariosModificar['sabado'].fin || null,
      sabado_colacion: this.horariosModificar['sabado'].colacion,
      sabado_minutos_colacion: this.horariosModificar['sabado'].minutos_colacion,
      domingo_inicio: this.horariosModificar['domingo'].inicio || null,
      domingo_fin: this.horariosModificar['domingo'].fin || null,
      domingo_colacion: this.horariosModificar['domingo'].colacion,
      domingo_minutos_colacion: this.horariosModificar['domingo'].minutos_colacion
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
      
      // Buscar sociedad
      const sociedad = this.sociedadesDisponibles.find(s => s.id === lastSelectedRow.sociedad);
      this.sociedadSeleccionadaModificar = sociedad || null;
      
      // Cargar horarios
      this.diasSemana.forEach(dia => {
        this.horariosModificar[dia.key] = {
          inicio: lastSelectedRow[`${dia.key}_inicio`] || '',
          fin: lastSelectedRow[`${dia.key}_fin`] || '',
          colacion: lastSelectedRow[`${dia.key}_colacion`] || false,
          minutos_colacion: lastSelectedRow[`${dia.key}_minutos_colacion`] || 0
        };
      });
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
    this.sociedadSeleccionada = null;
    this.horariosCrear = {
      lunes: { inicio: '08:00', fin: '17:00', colacion: true, minutos_colacion: 60 },
      martes: { inicio: '08:00', fin: '17:00', colacion: true, minutos_colacion: 60 },
      miercoles: { inicio: '08:00', fin: '17:00', colacion: true, minutos_colacion: 60 },
      jueves: { inicio: '08:00', fin: '17:00', colacion: true, minutos_colacion: 60 },
      viernes: { inicio: '08:00', fin: '17:00', colacion: true, minutos_colacion: 60 },
      sabado: { inicio: '', fin: '', colacion: false, minutos_colacion: 0 },
      domingo: { inicio: '', fin: '', colacion: false, minutos_colacion: 0 }
    };
  }

  resetModificar(): void {
    this.nombreHorarioNew = '';
    this.sociedadSeleccionadaModificar = null;
  }

  getHorasDia(horario: any, dia: string): number {
    const diaData: DiaHorario = {
      inicio: horario[`${dia}_inicio`] || '',
      fin: horario[`${dia}_fin`] || '',
      colacion: horario[`${dia}_colacion`] || false,
      minutos_colacion: horario[`${dia}_minutos_colacion`] || 0
    };
    return this.calcularHorasDia(diaData);
  }

  getTotalSemanal(horario: any): number {
    let total = 0;
    this.diasSemana.forEach(dia => {
      total += this.getHorasDia(horario, dia.key);
    });
    return total;
  }
}