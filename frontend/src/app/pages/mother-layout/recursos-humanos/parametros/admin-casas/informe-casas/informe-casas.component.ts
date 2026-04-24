import { Component, Inject, OnInit, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser, CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ContratistaApiService } from '../../../../../../services/contratista-api.service';

interface Ocupante {
  id: number;
  nombres: string;
  apellidos: string;
  rut: string;
  fecha_inicio: string;
  fecha_fin: string | null;
}

interface Casa {
  casa_id: number | null;
  casa_nombre: string;
  total: number;
  ocupantes: Ocupante[];
}

@Component({
  selector: 'app-informe-casas',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './informe-casas.component.html',
  styleUrl: './informe-casas.component.css'
})
export class InformeCasasComponent implements OnInit {

  public holding: string = '';
  public fecha: string = new Date().toISOString().substring(0, 10);
  public casas: Casa[] = [];
  public cargando: boolean = false;
  public filtro: string = '';
  public expandidas: Set<number | string> = new Set();

  constructor(
    private apiService: ContratistaApiService,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {}

  ngOnInit(): void {
    if (isPlatformBrowser(this.platformId)) {
      this.holding = localStorage.getItem('holding_id') || '';
      this.cargar();
    }
  }

  cargar(): void {
    if (!this.holding) return;
    this.cargando = true;
    this.apiService.get(`informe-casas/?holding=${this.holding}&fecha=${this.fecha}`).subscribe({
      next: (response) => {
        this.casas = response.casas || [];
        this.cargando = false;
      },
      error: (error) => {
        console.error('Error al cargar informe de casas:', error);
        this.cargando = false;
      }
    });
  }

  toggle(id: number | string | null): void {
    const key = id ?? 'sin';
    if (this.expandidas.has(key)) {
      this.expandidas.delete(key);
    } else {
      this.expandidas.add(key);
    }
  }

  abierta(id: number | string | null): boolean {
    return this.expandidas.has(id ?? 'sin');
  }

  get casasFiltradas(): Casa[] {
    if (!this.filtro.trim()) return this.casas;
    const f = this.filtro.toLowerCase();
    return this.casas
      .map(c => ({
        ...c,
        ocupantes: c.ocupantes.filter(o =>
          (o.nombres || '').toLowerCase().includes(f) ||
          (o.apellidos || '').toLowerCase().includes(f) ||
          (o.rut || '').toLowerCase().includes(f) ||
          c.casa_nombre.toLowerCase().includes(f)
        )
      }))
      .filter(c => c.ocupantes.length > 0 || c.casa_nombre.toLowerCase().includes(f));
  }

  totalPersonas(): number {
    return this.casas.reduce((s, c) => s + c.total, 0);
  }

  exportarCSV(): void {
    const filas = [['Casa', 'Nombres', 'Apellidos', 'RUT', 'Fecha Inicio', 'Fecha Fin']];
    this.casas.forEach(c => c.ocupantes.forEach(o => {
      filas.push([
        c.casa_nombre,
        o.nombres || '',
        o.apellidos || '',
        o.rut || '',
        o.fecha_inicio,
        o.fecha_fin || 'vigente'
      ]);
    }));
    const csv = filas.map(f => f.map(x => `"${x}"`).join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `informe_casas_${this.fecha}.csv`;
    a.click();
  }
}