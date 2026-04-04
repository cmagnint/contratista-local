import { Component, Inject, OnInit, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser, CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { ContratistaApiService } from '../../../../services/contratista-api.service';
import { JwtService } from '../../../../services/jwt.service';

@Component({
  selector: 'app-traspaso-trabajadores',
  standalone: true,
  imports: [
    CommonModule, FormsModule,
    MatTableModule, MatButtonModule,
    MatSelectModule, MatFormFieldModule, MatIconModule
  ],
  templateUrl: './traspaso-trabajadores.component.html',
  styleUrl: './traspaso-trabajadores.component.css'
})
export class TraspasoTrabajadoresComponent implements OnInit {

  constructor(
    private apiService: ContratistaApiService,
    private jwtService: JwtService,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {}

  holding = '';
  supervisores: any[] = [];
  supervisorOrigenId = '';
  supervisorDestinoId = '';
  trabajadoresOrigen: any[] = [];
  selectedTrabajadores: any[] = [];
  isTransferring = false;
  resultadoTransferencia: any = null;
  errorMessage = '';

  modals: { [key: string]: boolean } = {
    confirmacionModal: false,
    resultadoModal: false,
    errorModal: false,
  };

  displayedColumns = ['select', 'nombres', 'apellidos', 'rut'];

  ngOnInit(): void {
    if (isPlatformBrowser(this.platformId)) {
      this.holding = this.jwtService.getUserInfo()?.holding_id?.toString() || '';
      this.cargarSupervisores();
    }
  }

  cargarSupervisores(): void {
    this.apiService.get(`api_traspaso_trabajadores/?holding=${this.holding}`).subscribe({
      next: (res) => { this.supervisores = res; },
      error: () => {
        this.errorMessage = 'Error al cargar supervisores';
        this.openModal('errorModal');
      }
    });
  }

  get supervisoresDestino(): any[] {
    return this.supervisores.filter(s => s.id.toString() !== this.supervisorOrigenId);
  }

  onOrigenChange(): void {
    this.supervisorDestinoId = '';
    this.selectedTrabajadores = [];
    const sup = this.supervisores.find(s => s.id.toString() === this.supervisorOrigenId);
    this.trabajadoresOrigen = sup ? sup.trabajadores : [];
  }

  toggleSeleccion(t: any): void {
    const idx = this.selectedTrabajadores.findIndex(x => x.id === t.id);
    idx > -1 ? this.selectedTrabajadores.splice(idx, 1) : this.selectedTrabajadores.push(t);
  }

  isSelected(t: any): boolean {
    return this.selectedTrabajadores.some(x => x.id === t.id);
  }

  get allSelected(): boolean {
    return this.trabajadoresOrigen.length > 0 &&
      this.selectedTrabajadores.length === this.trabajadoresOrigen.length;
  }

  toggleAll(checked: boolean): void {
    this.selectedTrabajadores = checked ? [...this.trabajadoresOrigen] : [];
  }

  confirmarTraspaso(): void {
    if (!this.supervisorOrigenId || !this.supervisorDestinoId || !this.selectedTrabajadores.length) {
      this.errorMessage = 'Seleccione supervisor origen, destino y al menos un trabajador';
      this.openModal('errorModal');
      return;
    }
    this.openModal('confirmacionModal');
  }

  ejecutarTraspaso(): void {
    this.isTransferring = true;
    this.closeModal('confirmacionModal');

    this.apiService.post('api_traspaso_trabajadores/', {
      holding: this.holding,
      supervisor_origen_id: this.supervisorOrigenId,
      supervisor_destino_id: this.supervisorDestinoId,
      trabajadores_ids: this.selectedTrabajadores.map(t => t.id)
    }).subscribe({
      next: (res) => {
        this.isTransferring = false;
        this.resultadoTransferencia = res;
        this.cargarSupervisores();
        this.onOrigenChange();
        this.openModal('resultadoModal');
      },
      error: (err) => {
        this.isTransferring = false;
        this.errorMessage = err.error?.error || 'Error al realizar el traspaso';
        this.openModal('errorModal');
      }
    });
  }

  formatRut(rut: string): string {
    if (!rut) return 'N/A';
    const clean = rut.replace(/\./g, '').replace(/-/g, '').toUpperCase();
    const dv = clean.slice(-1);
    const body = clean.slice(0, -1).replace(/\B(?=(\d{3})+(?!\d))/g, '.');
    return `${body}-${dv}`;
  }

  openModal(key: string): void { this.modals[key] = true; }
  closeModal(key: string): void { this.modals[key] = false; }
}