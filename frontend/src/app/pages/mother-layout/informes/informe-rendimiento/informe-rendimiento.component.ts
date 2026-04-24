import { Component, OnInit, PLATFORM_ID, Inject, AfterViewChecked, NgZone } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatButtonModule } from '@angular/material/button';
import { MatNativeDateModule, provideNativeDateAdapter } from '@angular/material/core';
import { Chart } from 'chart.js';
import { registerables } from 'chart.js';
import { ContratistaApiService } from '../../../../services/contratista-api.service';

Chart.register(...registerables);

interface FilaRanking {
  pos: number;
  nombre: string;
  uc: number;
  dias: number;
  promDia: number;
}

interface BloqueUC {
  uc: string;
  totalTrabajadores: number;
  totalProd: number;
  promProd: number;
  topTrabajador: string;
  top10: FilaRanking[];
  bottom10: FilaRanking[];
  barId: string;
  donaId: string;
  laborSel: string | null;   // labor activa en el filtro (click dona)
}

@Component({
  selector: 'app-informe-rendimiento',
  standalone: true,
  imports: [
    CommonModule, ReactiveFormsModule,
    MatFormFieldModule, MatInputModule, MatSelectModule,
    MatDatepickerModule, MatButtonModule, MatNativeDateModule
  ],
  providers: [provideNativeDateAdapter()],
  templateUrl: './informe-rendimiento.component.html',
  styleUrl: './informe-rendimiento.component.css'
})
export class InformeRendimientoComponent implements OnInit, AfterViewChecked {

  filtroForm: FormGroup;
  clientes:     any[] = [];
  supervisores: any[] = [];
  labores:      any[] = [];

  produccionData:     any[] = [];
  produccionFiltrada: any[] = [];

  bloquesUC: BloqueUC[] = [];
  charts: Chart[] = [];
  pendingRender = false;

  holding       = '';
  infoMessage   = '';
  errorMessage  = '';
  filtrosVisible= true;
  buscando      = false;

  totalTrabajadoresGlobal = 0;
  totalLabores            = 0;
  totalUCs                = 0;

  constructor(
    private fb: FormBuilder,
    private api: ContratistaApiService,
    private zone: NgZone,
    @Inject(PLATFORM_ID) private pid: Object
  ) {
    this.filtroForm = this.fb.group({
      fecha_inicio:  ['', Validators.required],
      fecha_fin:     ['', Validators.required],
      cliente_id:    [''],
      supervisor_id: [''],
      labor_id:      ['']
    });
  }

  ngOnInit() {
    if (!isPlatformBrowser(this.pid)) return;
    this.holding = localStorage.getItem('holding_id') || '';
    if (!this.holding) { this.errorMessage = 'Holding no encontrado'; return; }
    this.cargarDropdowns();

    this.filtroForm.get('labor_id')!.valueChanges.subscribe(() => {
      if (this.produccionData.length > 0) this.aplicarFiltroLocal();
    });
  }

  ngAfterViewChecked() {
    if (this.pendingRender && this.bloquesUC.length > 0) {
      this.pendingRender = false;
      this.renderCharts();
    }
  }

  cargarDropdowns() {
    this.api.get(`api_clientes/?holding=${this.holding}`).subscribe({
      next: r => this.clientes = r.filter((c: any) => c.estado !== false),
      error: () => {}
    });
    this.api.get(`api_supervisores/${this.holding}`).subscribe({
      next: r => this.supervisores = r.map((s: any) => ({
        id: s.id, nombre: s.usuario_nombre || 'Sin nombre'
      })),
      error: () => {}
    });
    this.api.get(`labores_comercial/?holding=${this.holding}`).subscribe({
      next: r => this.labores = r.filter((l: any) => l.estado !== false),
      error: () => {}
    });
  }

  buscarDatos() {
    if (!this.filtroForm.valid) { this.errorMessage = 'Fechas requeridas'; return; }
    this.infoMessage  = '';
    this.errorMessage = '';
    this.buscando     = true;

    const v    = this.filtroForm.value;
    const body = {
      ...v,
      fecha_inicio: this.fmt(v.fecha_inicio),
      fecha_fin:    this.fmt(v.fecha_fin),
      holding:      this.holding
    };

    this.api.post('informe-rendimiento/', body).subscribe({
      next: res => {
        this.buscando = false;
        if (res?.length) {
          this.produccionData = res;
          this.aplicarFiltroLocal();
        } else {
          this.produccionData     = [];
          this.produccionFiltrada = [];
          this.infoMessage        = 'Sin datos para los filtros seleccionados';
          this.resetAll();
        }
      },
      error: () => {
        this.buscando     = false;
        this.errorMessage = 'Error al obtener datos';
      }
    });
  }

  aplicarFiltroLocal() {
    const laborId = this.filtroForm.get('labor_id')!.value;
    this.produccionFiltrada = laborId
      ? this.produccionData.filter(i => String(i.labor_id) === String(laborId))
      : [...this.produccionData];

    if (!this.produccionFiltrada.length) {
      this.infoMessage = 'Sin datos para la labor seleccionada';
      this.resetAll();
      return;
    }
    this.infoMessage = '';
    this.construirBloquesUC();
    this.pendingRender = true;
  }

  construirBloquesUC() {
    this.destruirCharts();

    const porUC: Record<string, any[]> = {};
    this.produccionFiltrada.forEach(i => {
      const uc = i.nombre_unidad_control || 'Sin UC';
      (porUC[uc] ??= []).push(i);
    });

    const trabajadoresGlobal = new Set<string>();
    const laboresGlobal      = new Set<string>();
    this.produccionFiltrada.forEach(i => {
      trabajadoresGlobal.add(i.nombre_trabajador || 'Sin nombre');
      laboresGlobal.add(i.nombre_labor || 'Sin labor');
    });
    this.totalTrabajadoresGlobal = trabajadoresGlobal.size;
    this.totalLabores            = laboresGlobal.size;
    this.totalUCs                = Object.keys(porUC).length;

    this.bloquesUC = Object.entries(porUC).map(([uc, _], idx) => ({
      uc,
      totalTrabajadores: 0,
      totalProd: 0,
      promProd: 0,
      topTrabajador: '-',
      top10: [],
      bottom10: [],
      barId:  `bar-${idx}`,
      donaId: `dona-${idx}`,
      laborSel: null
    }));

    // calcular stats iniciales (sin filtro labor)
    this.bloquesUC.forEach(b => this.recalcStatsBloque(b));
  }

  // recalcula stats/rankings del bloque considerando b.laborSel
  recalcStatsBloque(b: BloqueUC) {
    const regs = this.produccionFiltrada.filter(i =>
      (i.nombre_unidad_control || 'Sin UC') === b.uc
      && (!b.laborSel || i.nombre_labor === b.laborSel)
    );

    const byW: Record<string, { uc: number; dias: Set<string> }> = {};
    regs.forEach(i => {
      const n = i.nombre_trabajador || 'Sin nombre';
      if (!byW[n]) byW[n] = { uc: 0, dias: new Set() };
      byW[n].uc += +(i.unidades_control || 0);
      if (i.fecha) byW[n].dias.add(i.fecha);
    });
    const entradas = Object.entries(byW)
      .map(([nombre, v]) => ({
        nombre, uc: v.uc,
        dias: v.dias.size || 1,
        promDia: v.uc / (v.dias.size || 1)
      }))
      .sort((a, b) => b.uc - a.uc);

    b.totalTrabajadores = entradas.length;
    b.totalProd         = entradas.reduce((s, e) => s + e.uc, 0);
    b.promProd          = entradas.length ? b.totalProd / entradas.length : 0;
    b.topTrabajador     = entradas[0]?.nombre ?? '-';
    b.top10             = entradas.slice(0, 10).map((e, i) => ({ pos: i + 1, ...e }));
    b.bottom10          = [...entradas].reverse().slice(0, 10)
                          .map((e, i) => ({ pos: entradas.length - i, ...e }));
  }

  renderCharts() {
    this.destruirCharts();
    this.bloquesUC.forEach(b => {
      this.crearBarra(b);
      this.crearDona(b);
    });
  }

  // click en labor de la dona → toggle filtro en barra + rankings
  onLaborClick(b: BloqueUC, labor: string) {
    this.zone.run(() => {
      b.laborSel = (b.laborSel === labor) ? null : labor;
      this.recalcStatsBloque(b);
      // redibujar ambos charts del bloque
      this.charts = this.charts.filter(c => {
        if (c.canvas?.id === b.barId || c.canvas?.id === b.donaId) {
          c.destroy(); return false;
        }
        return true;
      });
      this.crearBarra(b);
      this.crearDona(b);
    });
  }

  limpiarLabor(b: BloqueUC) {
    if (b.laborSel) this.onLaborClick(b, b.laborSel);
  }

  crearBarra(b: BloqueUC) {
    const el = document.getElementById(b.barId) as HTMLCanvasElement | null;
    if (!el) return;

    const regs = this.produccionFiltrada.filter(i =>
      (i.nombre_unidad_control || 'Sin UC') === b.uc
      && (!b.laborSel || i.nombre_labor === b.laborSel)
    );

    const byW: Record<string, number> = {};
    regs.forEach(i => {
      const n = i.nombre_trabajador || 'Sin nombre';
      byW[n] = (byW[n] || 0) + +(i.unidades_control || 0);
    });
    const sorted = Object.entries(byW).sort((a, b) => b[1] - a[1]);
    const labels = sorted.map(e => e[0]);
    const data   = sorted.map(e => e[1]);
    const n      = labels.length || 1;
    const bg     = labels.map((_, i) =>
      `rgba(20,179,92,${(0.35 + (1 - i / n) * 0.65).toFixed(2)})`
    );

    const titulo = b.laborSel
      ? `Producción por Trabajador — ${b.laborSel} (${b.uc})`
      : `Producción por Trabajador (${b.uc})`;

    const chart = new Chart(el.getContext('2d')!, {
      type: 'bar',
      data: {
        labels,
        datasets: [{
          label: b.uc,
          data,
          backgroundColor: bg,
          borderColor: '#0f8a47',
          borderWidth: 1,
          borderRadius: 5
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          title: {
            display: true, text: titulo,
            font: { size: 13, weight: 'bold' },
            color: '#14b35c'
          },
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: ctx => ` ${b.uc}: ${(ctx.parsed.y as number).toFixed(2)}`
            }
          }
        },
        scales: {
          y: { beginAtZero: true, title: { display: true, text: b.uc } },
          x: { ticks: { maxRotation: 50, minRotation: 35, font: { size: 10 } } }
        }
      }
    });
    this.charts.push(chart);
  }

  crearDona(b: BloqueUC) {
    const el = document.getElementById(b.donaId) as HTMLCanvasElement | null;
    if (!el) return;

    const regs = this.produccionFiltrada.filter(i =>
      (i.nombre_unidad_control || 'Sin UC') === b.uc
    );

    const byL: Record<string, number> = {};
    regs.forEach(i => {
      const n = i.nombre_labor || 'Sin labor';
      byL[n] = (byL[n] || 0) + +(i.unidades_control || 0);
    });
    const labels = Object.keys(byL);
    const data   = Object.values(byL);
    const COLORS = [
      '#14b35c','#2196F3','#FF9800','#9C27B0',
      '#f44336','#00BCD4','#FF5722','#795548'
    ];
    // resaltar seleccionada
    const bg = labels.map((lbl, i) => {
      const base = COLORS[i % COLORS.length];
      return b.laborSel && b.laborSel !== lbl ? base + '55' : base;   // alpha si no está sel
    });
    const borderColor = labels.map(lbl =>
      b.laborSel === lbl ? '#222' : '#fff'
    );
    const borderWidth = labels.map(lbl =>
      b.laborSel === lbl ? 3 : 2
    );

    const self = this;
    const chart = new Chart(el.getContext('2d')!, {
      type: 'doughnut',
      data: {
        labels,
        datasets: [{
          data,
          backgroundColor: bg,
          borderColor,
          borderWidth
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        onClick: (_evt, elems) => {
          if (elems.length > 0) {
            const i = elems[0].index;
            self.onLaborClick(b, labels[i]);
          }
        },
        onHover: (evt, elems) => {
          (evt.native?.target as HTMLElement).style.cursor =
            elems.length ? 'pointer' : 'default';
        },
        plugins: {
          title: {
            display: true,
            text: `Distribución Labor (${b.uc}) — click para filtrar`,
            font: { size: 12, weight: 'bold' },
            color: '#14b35c'
          },
          legend: {
            position: 'bottom',
            labels: { font: { size: 11 }, boxWidth: 14 },
            onClick: (_e: any, item: any) => self.onLaborClick(b, item.text)
          },
          tooltip: {
            callbacks: {
              label: ctx => {
                const total = (ctx.dataset.data as number[]).reduce((a, v) => a + v, 0);
                const val = ctx.parsed as number;
                return ` ${ctx.label}: ${val.toFixed(0)} ${b.uc} (${((val/total)*100).toFixed(1)}%)`;
              }
            }
          }
        }
      }
    });
    this.charts.push(chart);
  }

  destruirCharts() {
    this.charts.forEach(c => c.destroy());
    this.charts = [];
  }

  resetAll() {
    this.destruirCharts();
    this.bloquesUC               = [];
    this.totalTrabajadoresGlobal = 0;
    this.totalLabores            = 0;
    this.totalUCs                = 0;
  }

  private fmt(d: Date): string {
    if (!d) return '';
    const dt = new Date(d);
    return `${dt.getFullYear()}-${String(dt.getMonth()+1).padStart(2,'0')}-${String(dt.getDate()).padStart(2,'0')}`;
  }

  limpiarFiltros() {
    this.filtroForm.reset();
    this.produccionData     = [];
    this.produccionFiltrada = [];
    this.infoMessage        = '';
    this.errorMessage       = '';
    this.resetAll();
  }
}