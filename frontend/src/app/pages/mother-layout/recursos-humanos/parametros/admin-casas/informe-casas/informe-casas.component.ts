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

  // Selección y modal
  public seleccionados: Set<number> = new Set();
  public modalAbierto: boolean = false;
  public nuevaCasaId: number = -1;
  public guardando: boolean = false;

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
        this.casas = this.ordenarCasas(response.casas || []);
        this.seleccionados = new Set();
        this.cargando = false;
      },
      error: (error) => {
        console.error('Error al cargar informe de casas:', error);
        this.cargando = false;
      }
    });
  }

  // ── Ordenamiento ──────────────────────────────────────────────────────────

  private compararTexto(a: string | null | undefined, b: string | null | undefined): number {
    return (a || '').localeCompare(b || '', 'es', {
      sensitivity: 'base',
      numeric: true
    });
  }

  private ordenarOcupantes(ocupantes: Ocupante[]): Ocupante[] {
    return [...(ocupantes || [])].sort((a, b) => {
      const nombreA = `${a.nombres || ''} ${a.apellidos || ''}`.trim();
      const nombreB = `${b.nombres || ''} ${b.apellidos || ''}`.trim();

      return this.compararTexto(nombreA, nombreB);
    });
  }

  private ordenarCasas(casas: Casa[]): Casa[] {
    return [...(casas || [])]
      .map(casa => ({
        ...casa,
        ocupantes: this.ordenarOcupantes(casa.ocupantes || [])
      }))
      .sort((a, b) => this.compararTexto(a.casa_nombre, b.casa_nombre));
  }

  // ── Acordeón ──────────────────────────────────────────────────────────────

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

  // ── Filtro ────────────────────────────────────────────────────────────────

  get casasFiltradas(): Casa[] {
    if (!this.filtro.trim()) {
      return this.ordenarCasas(this.casas);
    }

    const f = this.filtro.toLowerCase();

    const filtradas = this.casas
      .map(c => ({
        ...c,
        ocupantes: this.ordenarOcupantes(
          (c.ocupantes || []).filter(o =>
            (o.nombres || '').toLowerCase().includes(f) ||
            (o.apellidos || '').toLowerCase().includes(f) ||
            (o.rut || '').toLowerCase().includes(f) ||
            (c.casa_nombre || '').toLowerCase().includes(f)
          )
        )
      }))
      .filter(c =>
        c.ocupantes.length > 0 ||
        (c.casa_nombre || '').toLowerCase().includes(f)
      );

    return this.ordenarCasas(filtradas);
  }

  totalPersonas(): number {
    return this.casas.reduce((s, c) => s + c.total, 0);
  }

  // ── Selección ─────────────────────────────────────────────────────────────

  toggleSeleccion(id: number, event: Event): void {
    event.stopPropagation();

    const next = new Set(this.seleccionados);

    next.has(id) ? next.delete(id) : next.add(id);

    this.seleccionados = next;
  }

  estaSeleccionado(id: number): boolean {
    return this.seleccionados.has(id);
  }

  toggleCasa(casa: Casa, event: Event): void {
    event.stopPropagation();

    const next = new Set(this.seleccionados);

    if (this.todaCasaSeleccionada(casa)) {
      casa.ocupantes.forEach(o => next.delete(o.id));
    } else {
      casa.ocupantes.forEach(o => next.add(o.id));
    }

    this.seleccionados = next;
  }

  todaCasaSeleccionada(casa: Casa): boolean {
    return casa.ocupantes.length > 0 && casa.ocupantes.every(o => this.seleccionados.has(o.id));
  }

  algunoEnCasa(casa: Casa): boolean {
    return casa.ocupantes.some(o => this.seleccionados.has(o.id)) && !this.todaCasaSeleccionada(casa);
  }

  limpiarSeleccion(): void {
    this.seleccionados = new Set();
  }

  // ── Modal migración ───────────────────────────────────────────────────────

  /** Selecciona un único trabajador y abre el modal directamente */
  abrirCambioIndividual(ocupante: Ocupante, event: Event): void {
    event.stopPropagation();

    this.seleccionados = new Set([ocupante.id]);
    this.abrirModal();
  }

  abrirModal(): void {
    if (this.seleccionados.size === 0) return;

    const primera = this.casasDisponibles[0];

    this.nuevaCasaId = primera?.casa_id ?? -1;
    this.modalAbierto = true;
  }

  cerrarModal(): void {
    this.modalAbierto = false;
    this.guardando = false;
  }

  get casasDisponibles(): Casa[] {
    return this.ordenarCasas(
      this.casas.filter(c => c.casa_id !== null)
    );
  }

  get trabajadoresSeleccionados(): Ocupante[] {
    const todos = this.casas.flatMap(c => c.ocupantes || []);

    return this.ordenarOcupantes(
      todos.filter(o => this.seleccionados.has(o.id))
    );
  }

  confirmarCambio(): void {
    if (this.seleccionados.size === 0 || this.guardando) return;

    this.guardando = true;

    const body = {
      trabajador_ids: Array.from(this.seleccionados),
      nueva_casa_id: this.nuevaCasaId === -1 ? null : this.nuevaCasaId,
      holding_id: this.holding
    };

    this.apiService.post('informe-casas/cambiar-casa/', body).subscribe({
      next: () => {
        this.cerrarModal();
        this.seleccionados = new Set();
        this.cargar();
      },
      error: (error) => {
        console.error('Error al migrar trabajadores:', error);
        this.guardando = false;
      }
    });
  }

  // ── Exportar ──────────────────────────────────────────────────────────────

  exportarCSV(): void {
    const filas = [['Casa', 'Nombres', 'Apellidos', 'RUT', 'Fecha Inicio', 'Fecha Fin']];

    this.ordenarCasas(this.casas).forEach(c => {
      c.ocupantes.forEach(o => {
        filas.push([
          c.casa_nombre,
          o.nombres || '',
          o.apellidos || '',
          o.rut || '',
          o.fecha_inicio,
          o.fecha_fin || 'vigente'
        ]);
      });
    });

    const csv = filas.map(f => f.map(x => `"${x}"`).join(',')).join('\n');

    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const a = document.createElement('a');

    a.href = URL.createObjectURL(blob);
    a.download = `informe_casas_${this.fecha}.csv`;
    a.click();
  }
}