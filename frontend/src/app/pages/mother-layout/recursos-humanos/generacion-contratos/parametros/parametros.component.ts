import { Component, Inject, OnInit, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser, CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatIconModule } from '@angular/material/icon';
import { ContratistaApiService } from '../../../../../services/contratista-api.service';

@Component({
  selector: 'app-parametros',
  standalone: true,
  imports: [CommonModule, FormsModule, MatIconModule],
  templateUrl: './parametros.component.html',
  styleUrl: './parametros.component.css'
})
export class ParametrosComponent implements OnInit {

  constructor(
    private apiService: ContratistaApiService,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {}

  // ─── Estado ───────────────────────────────────────────
  holding = '';
  parametros: any[] = [];
  formatos: any[] = [];

  // Formulario crear
  nuevoNombre = '';
  creando = false;

  // Edición inline
  editandoId: number | null = null;
  editNombre = '';
  editFormatoId: number | null = null;
  guardando = false;

  // Eliminar
  parametroAEliminar: any = null;

  // UI
  modals: { [key: string]: boolean } = {
    crear: false,
    confirmarEliminar: false,
    error: false,
    exito: false,
  };
  errorMessage = '';
  exitoMessage = '';

  // ─── Lifecycle ────────────────────────────────────────
  ngOnInit(): void {
    if (!isPlatformBrowser(this.platformId)) return;
    this.holding = localStorage.getItem('holding_id') || '';
    this.cargarParametros();
    this.cargarFormatos();
  }

  // ─── Carga ────────────────────────────────────────────
  cargarParametros(): void {
    this.apiService.get('api_parametros/').subscribe({
      next: (res) => { this.parametros = res; },
      error: () => this.mostrarError('Error al cargar parámetros'),
    });
  }

  cargarFormatos(): void {
    this.apiService.get('api_documento_nativo/').subscribe({
      next: (res) => { this.formatos = res; },
      error: () => this.mostrarError('Error al cargar formatos'),
    });
  }

  // ─── Crear ────────────────────────────────────────────
  abrirModalCrear(): void {
    this.nuevoNombre = '';
    this.modals['crear'] = true;
  }

  crearParametro(): void {
    const nombre = this.nuevoNombre.trim();
    if (!nombre) {
      this.mostrarError('El nombre es requerido');
      return;
    }
    this.creando = true;
    this.apiService.post('api_parametros/', { nombre }).subscribe({
      next: (res) => {
        this.parametros.push(res);
        this.creando = false;
        this.closeModal('crear');
        this.mostrarExito(`Parámetro "${res.nombre}" creado`);
      },
      error: (err) => {
        this.creando = false;
        this.mostrarError(err?.error?.error || 'Error al crear parámetro');
      },
    });
  }

  // ─── Edición inline ───────────────────────────────────
  iniciarEdicion(p: any): void {
    this.editandoId = p.id;
    this.editNombre = p.nombre;
    this.editFormatoId = p.formato_id ?? null;
  }

  cancelarEdicion(): void {
    this.editandoId = null;
  }

  guardarEdicion(p: any): void {
    const nombre = this.editNombre.trim();
    if (!nombre) {
      this.mostrarError('El nombre no puede estar vacío');
      return;
    }
    this.guardando = true;
    const payload: any = { nombre };
    // Siempre enviar formato_id (puede ser null para desasignar)
    payload.formato_id = this.editFormatoId ?? null;

    this.apiService.put(`api_parametros/${p.id}/`, payload).subscribe({
      next: (res) => {
        const idx = this.parametros.findIndex(x => x.id === p.id);
        if (idx !== -1) this.parametros[idx] = res;
        this.guardando = false;
        this.editandoId = null;
        this.mostrarExito('Parámetro actualizado');
      },
      error: (err) => {
        this.guardando = false;
        this.mostrarError(err?.error?.error || 'Error al guardar');
      },
    });
  }

  // ─── Eliminar ─────────────────────────────────────────
  confirmarEliminar(p: any): void {
    this.parametroAEliminar = p;
    this.modals['confirmarEliminar'] = true;
  }

  eliminarParametro(): void {
    if (!this.parametroAEliminar) return;
    const id = this.parametroAEliminar.id;
    const nombre = this.parametroAEliminar.nombre;
    this.apiService.delete(`api_parametros/${id}/`, {}).subscribe({
      next: () => {
        this.parametros = this.parametros.filter(p => p.id !== id);
        this.parametroAEliminar = null;
        this.closeModal('confirmarEliminar');
        this.mostrarExito(`Parámetro "${nombre}" eliminado`);
      },
      error: (err) => {
        this.closeModal('confirmarEliminar');
        this.mostrarError(err?.error?.error || 'Error al eliminar');
      },
    });
  }

  // ─── Helpers ──────────────────────────────────────────
  getNombreFormato(formatoId: number | null): string {
    if (!formatoId) return '—';
    const f = this.formatos.find(x => x.id === formatoId);
    return f ? f.nombre : '—';
  }

  get totalConFormato(): number {
    return this.parametros.filter(p => p.formato_id).length;
  }

  mostrarError(msg: string): void {
    this.errorMessage = msg;
    this.modals['error'] = true;
  }

  mostrarExito(msg: string): void {
    this.exitoMessage = msg;
    this.modals['exito'] = true;
  }

  closeModal(key: string): void {
    this.modals[key] = false;
  }
}