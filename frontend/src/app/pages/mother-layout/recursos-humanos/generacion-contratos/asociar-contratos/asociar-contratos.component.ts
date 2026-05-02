import { Component, Inject, OnInit, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser, CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatIconModule } from '@angular/material/icon';
import { MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { ContratistaApiService } from '../../../../../services/contratista-api.service';

@Component({
  selector: 'app-asociar-contratos',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatIconModule,
    MatSelectModule,
    MatFormFieldModule,
    MatInputModule,
  ],
  templateUrl: './asociar-contratos.component.html',
  styleUrl: './asociar-contratos.component.css'
})
export class AsociarContratosComponent implements OnInit {

  constructor(
    private apiService: ContratistaApiService,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {}

  // ─── Estado ───────────────────────────────────────────
  holding = '';
  filtroBusqueda = '';

  trabajadores: any[] = [];
  trabajadoresFiltrados: any[] = [];
  trabajadorSeleccionado: any = null;

  parametros: any[] = [];
  asociaciones: any[] = [];

  // Upload
  parametroParaSubir: number | null = null;
  archivoSeleccionado: File | null = null;
  subiendoArchivo = false;

  // UI
  modals: { [key: string]: boolean } = { error: false, exito: false, confirmarEliminar: false };
  errorMessage = '';
  exitoMessage = '';
  asociacionAEliminar: number | null = null;

  // ─── Lifecycle ────────────────────────────────────────
  ngOnInit(): void {
    if (!isPlatformBrowser(this.platformId)) return;
    this.holding = localStorage.getItem('holding_id') || '';
    this.cargarTrabajadores();
    this.cargarParametros();
  }

  // ─── Carga ────────────────────────────────────────────
  cargarTrabajadores(): void {
    this.apiService.get(`api_personal/?holding=${this.holding}`).subscribe({
      
      next: (res) => {
        this.trabajadores = res.filter((t: any) => t.estado);
        this.aplicarFiltro();
      },
      error: () => this.mostrarError('Error al cargar trabajadores'),
    });
  }

  cargarParametros(): void {
    this.apiService.get('api_parametros/').subscribe({
      next: (res) => { this.parametros = res; },
      error: () => this.mostrarError('Error al cargar parámetros'),
    });
  }

  cargarAsociaciones(): void {
    if (!this.trabajadorSeleccionado) return;
    this.apiService
      .get(`api_contratos_asociados/?trabajador_id=${this.trabajadorSeleccionado.id}`)
      .subscribe({
        next: (res) => { this.asociaciones = res; },
        error: () => this.mostrarError('Error al cargar asociaciones'),
      });
  }

  // ─── Filtro ───────────────────────────────────────────
  aplicarFiltro(): void {
    const termino = this.filtroBusqueda.toLowerCase().trim();
    this.trabajadoresFiltrados = termino
      ? this.trabajadores.filter(t =>
          `${t.nombres} ${t.apellidos}`.toLowerCase().includes(termino) ||
          (t.rut || '').toLowerCase().includes(termino)
        )
      : [...this.trabajadores];
  }

  // ─── Selección de trabajador ──────────────────────────
  seleccionarTrabajador(trabajador: any): void {
    this.trabajadorSeleccionado = trabajador;
    this.asociaciones = [];
    this.parametroParaSubir = null;
    this.archivoSeleccionado = null;
    this.cargarAsociaciones();
  }

  // ─── Upload ───────────────────────────────────────────
  onArchivoSeleccionado(event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0] ?? null;
    if (file && file.type !== 'application/pdf') {
      this.mostrarError('Solo se permiten archivos PDF');
      input.value = '';
      return;
    }
    this.archivoSeleccionado = file;
  }

  subirPDF(): void {
    if (!this.parametroParaSubir || !this.archivoSeleccionado || !this.trabajadorSeleccionado) {
      this.mostrarError('Selecciona un parámetro y un archivo PDF');
      return;
    }

    const formData = new FormData();
    formData.append('trabajador_id', String(this.trabajadorSeleccionado.id));
    formData.append('parametro_id', String(this.parametroParaSubir));
    formData.append('archivo_pdf', this.archivoSeleccionado);

    this.subiendoArchivo = true;
    this.apiService.postFormData('api_contratos_asociados/', formData).subscribe({
      next: (res) => {
        this.asociaciones.push(res);
        this.archivoSeleccionado = null;
        this.parametroParaSubir = null;
        this.subiendoArchivo = false;
        this.exitoMessage = 'PDF asociado exitosamente';
        this.modals['exito'] = true;
      },
      error: (err) => {
        this.subiendoArchivo = false;
        this.mostrarError(err?.error?.error || 'Error al subir PDF');
      },
    });
  }

  // ─── Eliminar ─────────────────────────────────────────
  confirmarEliminar(id: number): void {
    this.asociacionAEliminar = id;
    this.modals['confirmarEliminar'] = true;
  }

  eliminarAsociacion(): void {
    if (!this.asociacionAEliminar) return;
    this.apiService.delete(`api_contratos_asociados/${this.asociacionAEliminar}/`, {}).subscribe({
      next: () => {
        this.asociaciones = this.asociaciones.filter(a => a.id !== this.asociacionAEliminar);
        this.asociacionAEliminar = null;
        this.modals['confirmarEliminar'] = false;
      },
      error: () => this.mostrarError('Error al eliminar asociación'),
    });
  }

  // ─── Helpers UI ───────────────────────────────────────
  agrupadoPorParametro(): { parametro: string; items: any[] }[] {
    const mapa: { [key: string]: any[] } = {};
    for (const a of this.asociaciones) {
      if (!mapa[a.parametro_nombre]) mapa[a.parametro_nombre] = [];
      mapa[a.parametro_nombre].push(a);
    }
    return Object.entries(mapa).map(([parametro, items]) => ({ parametro, items }));
  }

  abrirPDF(url: string): void {
    window.open(url, '_blank');
  }

  mostrarError(msg: string): void {
    this.errorMessage = msg;
    this.modals['error'] = true;
  }

  closeModal(key: string): void {
    this.modals[key] = false;
  }
}