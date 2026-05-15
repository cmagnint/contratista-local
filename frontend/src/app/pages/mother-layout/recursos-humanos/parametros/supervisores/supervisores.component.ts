import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ContratistaApiService } from '../../../../../services/contratista-api.service';

interface Supervisor {
  id: number;
  holding: number;
  usuario: number;
  usuario_nombre: string;
  usuario_rut: string;
  trabajadores_count: { directos: number; total: number };
  trabajadores_detail: { id: number; nombre: string; rut: string }[];
  firma: string | null;
  huella: string | null;
}

interface UsuarioOption {
  id: number;
  rut: string;
  nombre: string;
}

interface FormState {
  id: number;
  usuario: number;
  firmaFile: File | null;
  firmaPreview: string | null;
  firmaExistente: string | null;
  firmaClear: boolean;
  huellaFile: File | null;
  huellaPreview: string | null;
  huellaExistente: string | null;
  huellaClear: boolean;
}

interface CharlaContrato {
  id: number;
  fecha_inicio_contrato: string;
  fecha_termino_contrato: string | null;
  nombre_documento: string | null;
  nombre_cliente: string | null;
  nombre_fundo: string | null;
  estado_contrato: string | null;
  registro_charla_id: number | null;
  supervisor_id: number | null;
  supervisor_nombre: string | null;
}

interface CharlaTrabajadorGrupo {
  trabajador_id: number;
  trabajador_nombre: string;
  trabajador_rut: string | null;
  contratos: CharlaContrato[];
}

interface CharlaSupervisorGrupo {
  supervisor_id: number | null;
  supervisor_nombre: string;
  total_trabajadores: number;
  total_contratos: number;
  trabajadores: CharlaTrabajadorGrupo[];
}

interface CharlaResumen {
  total_contratos: number;
  con_charla: number;
  sin_charla: number;
}

interface RegistroCharlasResponse {
  grupos: CharlaSupervisorGrupo[];
  supervisores: Supervisor[];
  resumen: CharlaResumen;
}

const emptyForm = (): FormState => ({
  id: 0,
  usuario: 0,
  firmaFile: null,
  firmaPreview: null,
  firmaExistente: null,
  firmaClear: false,
  huellaFile: null,
  huellaPreview: null,
  huellaExistente: null,
  huellaClear: false,
});

@Component({
  selector: 'app-supervisores',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './supervisores.component.html',
  styleUrl: './supervisores.component.css'
})
export class SupervisoresComponent implements OnInit {
  supervisores: Supervisor[] = [];
  usuarios: UsuarioOption[] = [];
  supervisorSeleccionado: Supervisor | null = null;

  holdingId = 0;
  loading = false;
  submitting = false;
  error = '';

  showModal = false;
  editMode = false;
  form: FormState = emptyForm();

  // Modal imagen
  showImageModal = false;
  imagenModalUrl = '';
  imagenModalTipo = '';

  // Modales de estado
  showSuccessModal = false;
  showErrorModal = false;

  // Modal asignar charla
  showCharlaModal = false;
  loadingCharlas = false;
  savingCharlas = false;
  charlaError = '';
  charlaSuccess = '';

  filtrosCharla = {
    fechaInicio: '',
    fechaFin: '',
    trabajador: '',
    supervisor: '',
  };

  supervisorAsignacion = 0;
  charlaGrupos: CharlaSupervisorGrupo[] = [];
  resumenCharlas: CharlaResumen = {
    total_contratos: 0,
    con_charla: 0,
    sin_charla: 0,
  };

  contratosSeleccionados = new Set<number>();
  gruposExpandidos = new Set<string>();
  trabajadoresExpandidos = new Set<string>();

  // Filtros client-side aplicados sobre el árbol ya cargado.
  filtroSupervisorLocal = '';
  filtroTrabajadorLocal = '';

  constructor(private api: ContratistaApiService) {}

  ngOnInit(): void {
    this.holdingId = Number(localStorage.getItem('holding_id') || 0);
    this.cargarSupervisores();
  }

  cargarSupervisores(): void {
    if (!this.holdingId) return;
    this.loading = true;

    this.api.get(`api_supervisores/${this.holdingId}/`).subscribe({
      next: (data: any) => {
        this.supervisores = Array.isArray(data) ? data : [];
        this.loading = false;
        this.cargarUsuarios();
      },
      error: () => {
        this.supervisores = [];
        this.loading = false;
        this.cargarUsuarios();
      }
    });
  }

  cargarUsuarios(): void {
    if (!this.holdingId) return;

    this.api.get(`api_usuarios/${this.holdingId}/`).subscribe({
      next: (data: any) => {
        const raw: any[] = Array.isArray(data) ? data : (data.results ?? []);
        const idsYaSupervisores = new Set(this.supervisores.map(s => s.usuario));

        this.usuarios = raw
          .filter(u => !idsYaSupervisores.has(u.id))
          .map(u => ({
            id: u.id,
            rut: u.rut,
            nombre: u.nombre_persona ?? u.rut,
          }));
      },
      error: () => {}
    });
  }

  seleccionarFila(sup: Supervisor, event: Event): void {
    event.stopPropagation();
    this.supervisorSeleccionado = this.supervisorSeleccionado?.id === sup.id ? null : sup;
  }

  deseleccionarFila(event: Event): void {
    this.supervisorSeleccionado = null;
  }

  isSelected(sup: Supervisor): boolean {
    return this.supervisorSeleccionado?.id === sup.id;
  }

  abrirCrear(): void {
    this.editMode = false;
    this.form = emptyForm();
    this.error = '';
    this.showModal = true;
  }

  abrirEditar(sup: Supervisor): void {
    this.editMode = true;
    this.form = {
      ...emptyForm(),
      id: sup.id,
      usuario: sup.usuario,
      firmaExistente: sup.firma,
      huellaExistente: sup.huella,
    };

    if (!this.usuarios.find(u => u.id === sup.usuario)) {
      this.usuarios = [
        { id: sup.usuario, rut: sup.usuario_rut, nombre: sup.usuario_nombre },
        ...this.usuarios
      ];
    }

    this.error = '';
    this.showModal = true;
  }

  cerrarModal(): void {
    this.showModal = false;
    this.form = emptyForm();
    this.error = '';
  }

  abrirImagenModal(url: string, tipo: string): void {
    this.imagenModalUrl = url;
    this.imagenModalTipo = tipo;
    this.showImageModal = true;
  }

  cerrarImagenModal(): void {
    this.showImageModal = false;
    this.imagenModalUrl = '';
    this.imagenModalTipo = '';
  }

  onFirmaSelected(event: Event): void {
    const file = (event.target as HTMLInputElement).files?.[0];
    if (!file) return;
    this.form.firmaFile = file;
    this.form.firmaClear = false;
    this.leerPreview(file, url => this.form.firmaPreview = url);
  }

  onHuellaSelected(event: Event): void {
    const file = (event.target as HTMLInputElement).files?.[0];
    if (!file) return;
    this.form.huellaFile = file;
    this.form.huellaClear = false;
    this.leerPreview(file, url => this.form.huellaPreview = url);
  }

  private leerPreview(file: File, cb: (url: string) => void): void {
    const reader = new FileReader();
    reader.onload = e => cb(e.target?.result as string);
    reader.readAsDataURL(file);
  }

  quitarFirma(): void {
    this.form.firmaFile = null;
    this.form.firmaPreview = null;
    this.form.firmaExistente = null;
    this.form.firmaClear = true;
  }

  quitarHuella(): void {
    this.form.huellaFile = null;
    this.form.huellaPreview = null;
    this.form.huellaExistente = null;
    this.form.huellaClear = true;
  }

  firmaActiva(): string | null {
    return this.form.firmaPreview ?? this.form.firmaExistente;
  }

  huellaActiva(): string | null {
    return this.form.huellaPreview ?? this.form.huellaExistente;
  }

  guardar(): void {
    if (!this.form.usuario) {
      this.error = 'Selecciona un usuario.';
      return;
    }
    this.submitting = true;
    this.error = '';

    const fd = new FormData();
    fd.append('holding', String(this.holdingId));
    fd.append('usuario', String(this.form.usuario));
    if (this.editMode) fd.append('id', String(this.form.id));

    if (this.form.firmaFile) {
      fd.append('firma', this.form.firmaFile);
    } else if (this.form.firmaClear) {
      fd.append('firma_clear', '1');
    }

    if (this.form.huellaFile) {
      fd.append('huella', this.form.huellaFile);
    } else if (this.form.huellaClear) {
      fd.append('huella_clear', '1');
    }

    const op$ = this.editMode
      ? this.api.putFormData('api_supervisores/', fd)
      : this.api.postFormData('api_supervisores/', fd);

    op$.subscribe({
      next: () => {
        this.cerrarModal();
        this.supervisorSeleccionado = null;
        this.cargarSupervisores();
        this.submitting = false;
        this.showSuccessModal = true;
      },
      error: () => {
        this.error = 'Error al guardar. Verifica los datos.';
        this.submitting = false;
        this.showErrorModal = true;
      }
    });
  }

  // ========================================================================
  // ASIGNACIÓN DE CHARLAS A CONTRATOS
  // ========================================================================

  abrirAsignarCharla(): void {
    this.resetFiltrosCharlas();
    this.contratosSeleccionados.clear();
    this.supervisorAsignacion = 0;
    this.charlaError = '';
    this.charlaSuccess = '';
    this.filtroSupervisorLocal = '';
    this.filtroTrabajadorLocal = '';
    this.showCharlaModal = true;
    this.cargarCharlas();
  }

  cerrarCharlaModal(): void {
    this.showCharlaModal = false;
    this.charlaGrupos = [];
    this.contratosSeleccionados.clear();
    this.gruposExpandidos.clear();
    this.trabajadoresExpandidos.clear();
    this.charlaError = '';
    this.charlaSuccess = '';
    this.filtroSupervisorLocal = '';
    this.filtroTrabajadorLocal = '';
  }

  resetFiltrosCharlas(): void {
    const hoy = this.fechaHoyISO();
    this.filtrosCharla = {
      fechaInicio: hoy,
      fechaFin: hoy,
      trabajador: '',
      supervisor: '',
    };
  }

  limpiarFiltrosCharlas(): void {
    this.resetFiltrosCharlas();
    this.cargarCharlas();
  }

  cargarCharlas(): void {
    if (!this.holdingId) return;
    if (!this.filtrosCharla.fechaInicio || !this.filtrosCharla.fechaFin) {
      this.charlaError = 'Debes seleccionar fecha inicio y fecha fin.';
      return;
    }

    if (this.filtrosCharla.fechaInicio > this.filtrosCharla.fechaFin) {
      this.charlaError = 'La fecha inicio no puede ser mayor que la fecha fin.';
      return;
    }

    this.loadingCharlas = true;
    this.charlaError = '';
    this.charlaSuccess = '';
    this.contratosSeleccionados.clear();
    this.filtroSupervisorLocal = '';
    this.filtroTrabajadorLocal = '';

    const params = new URLSearchParams();
    params.set('fecha_inicio', this.filtrosCharla.fechaInicio);
    params.set('fecha_fin', this.filtrosCharla.fechaFin);

    if (this.filtrosCharla.trabajador.trim()) {
      params.set('trabajador', this.filtrosCharla.trabajador.trim());
    }

    if (this.filtrosCharla.supervisor !== '') {
      params.set('supervisor', String(this.filtrosCharla.supervisor));
    }

    this.api.get(`api_registro_charlas/${this.holdingId}/?${params.toString()}`).subscribe({
      next: (data: RegistroCharlasResponse) => {
        this.charlaGrupos = Array.isArray(data.grupos) ? data.grupos : [];
        this.resumenCharlas = data.resumen ?? {
          total_contratos: 0,
          con_charla: 0,
          sin_charla: 0,
        };

        if (Array.isArray(data.supervisores) && data.supervisores.length > 0) {
          this.supervisores = data.supervisores;
        }

        this.expandirGruposIniciales();
        this.loadingCharlas = false;
      },
      error: (err: any) => {
        this.charlaGrupos = [];
        this.loadingCharlas = false;
        this.charlaError = err?.error?.message || err?.error?.error || 'Error al cargar registros de charla.';
      }
    });
  }

  // ========================================================================
  // FILTROS CLIENT-SIDE SOBRE EL ÁRBOL CARGADO
  // ========================================================================
  // Aplica `filtroSupervisorLocal` y `filtroTrabajadorLocal` sobre
  // `charlaGrupos` sin volver a llamar al backend. Ambos campos
  // matchean nombre o RUT, case-insensitive. Si un grupo queda sin
  // trabajadores tras el filtro, se omite.
  get gruposFiltrados(): CharlaSupervisorGrupo[] {
    const fSup = this.filtroSupervisorLocal.trim().toLowerCase();
    const fTrab = this.filtroTrabajadorLocal.trim().toLowerCase();

    if (!fSup && !fTrab) return this.charlaGrupos;

    return this.charlaGrupos
      .filter(grupo => {
        if (!fSup) return true;
        const nombre = (grupo.supervisor_nombre || '').toLowerCase();
        const rut = grupo.supervisor_id
          ? (this.supervisores.find(s => s.id === grupo.supervisor_id)?.usuario_rut || '').toLowerCase()
          : '';
        return nombre.includes(fSup) || rut.includes(fSup);
      })
      .map(grupo => {
        if (!fTrab) return grupo;
        const trabajadores = grupo.trabajadores.filter(t => {
          const nombre = (t.trabajador_nombre || '').toLowerCase();
          const rut = (t.trabajador_rut || '').toLowerCase();
          return nombre.includes(fTrab) || rut.includes(fTrab);
        });
        return { ...grupo, trabajadores };
      })
      .filter(grupo => grupo.trabajadores.length > 0);
  }

  asignarCharlas(): void {
    const contratoIds = Array.from(this.contratosSeleccionados);

    if (!this.supervisorAsignacion) {
      this.charlaError = 'Debes seleccionar el supervisor que realizó la charla.';
      return;
    }

    if (contratoIds.length === 0) {
      this.charlaError = 'Selecciona al menos un contrato.';
      return;
    }

    this.savingCharlas = true;
    this.charlaError = '';
    this.charlaSuccess = '';

    const payload = {
      holding: this.holdingId,
      supervisor: this.supervisorAsignacion,
      contrato_ids: contratoIds,
    };

    this.api.post('api_registro_charlas/', payload).subscribe({
      next: (resp: any) => {
        const actualizados = resp?.actualizados ?? contratoIds.length;
        this.charlaSuccess = `Se asignaron ${actualizados} contrato(s) correctamente.`;
        this.savingCharlas = false;
        this.supervisorAsignacion = 0;
        this.cargarCharlas();
      },
      error: (err: any) => {
        this.savingCharlas = false;
        this.charlaError = err?.error?.message || err?.error?.error || 'Error al asignar charla.';
      }
    });
  }

  quitarCharlasSeleccionadas(): void {
    const contratoIds = Array.from(this.contratosSeleccionados);

    if (contratoIds.length === 0) {
      this.charlaError = 'Selecciona al menos un contrato para quitar su charla.';
      return;
    }

    this.savingCharlas = true;
    this.charlaError = '';
    this.charlaSuccess = '';

    const payload = {
      holding: this.holdingId,
      contrato_ids: contratoIds,
      supervisor: null,
      accion: 'quitar',
    };

    this.api.post('api_registro_charlas/', payload).subscribe({
      next: (resp: any) => {
        const eliminados = resp?.eliminados ?? contratoIds.length;
        this.charlaSuccess = `Se quitaron ${eliminados} registro(s) de charla.`;
        this.savingCharlas = false;
        this.cargarCharlas();
      },
      error: (err: any) => {
        this.savingCharlas = false;
        this.charlaError = err?.error?.message || err?.error?.error || 'Error al quitar charla.';
      }
    });
  }

  toggleContratoSeleccion(contratoId: number, event: Event): void {
    event.stopPropagation();
    const checked = (event.target as HTMLInputElement).checked;

    if (checked) {
      this.contratosSeleccionados.add(contratoId);
    } else {
      this.contratosSeleccionados.delete(contratoId);
    }
  }

  toggleTrabajadorSeleccion(trabajador: CharlaTrabajadorGrupo, event: Event): void {
    event.stopPropagation();
    const checked = (event.target as HTMLInputElement).checked;

    trabajador.contratos.forEach(c => {
      if (checked) {
        this.contratosSeleccionados.add(c.id);
      } else {
        this.contratosSeleccionados.delete(c.id);
      }
    });
  }

  toggleGrupoSeleccion(grupo: CharlaSupervisorGrupo, event: Event): void {
    event.stopPropagation();
    const checked = (event.target as HTMLInputElement).checked;

    grupo.trabajadores.forEach(t => {
      t.contratos.forEach(c => {
        if (checked) {
          this.contratosSeleccionados.add(c.id);
        } else {
          this.contratosSeleccionados.delete(c.id);
        }
      });
    });
  }

  isContratoSeleccionado(contratoId: number): boolean {
    return this.contratosSeleccionados.has(contratoId);
  }

  todosContratosTrabajadorSeleccionados(trabajador: CharlaTrabajadorGrupo): boolean {
    return trabajador.contratos.length > 0 && trabajador.contratos.every(c => this.contratosSeleccionados.has(c.id));
  }

  algunosContratosTrabajadorSeleccionados(trabajador: CharlaTrabajadorGrupo): boolean {
    const seleccionados = trabajador.contratos.filter(c => this.contratosSeleccionados.has(c.id)).length;
    return seleccionados > 0 && seleccionados < trabajador.contratos.length;
  }

  todosContratosGrupoSeleccionados(grupo: CharlaSupervisorGrupo): boolean {
    const contratos = grupo.trabajadores.flatMap(t => t.contratos);
    return contratos.length > 0 && contratos.every(c => this.contratosSeleccionados.has(c.id));
  }

  algunosContratosGrupoSeleccionados(grupo: CharlaSupervisorGrupo): boolean {
    const contratos = grupo.trabajadores.flatMap(t => t.contratos);
    const seleccionados = contratos.filter(c => this.contratosSeleccionados.has(c.id)).length;
    return seleccionados > 0 && seleccionados < contratos.length;
  }

  cantidadSeleccionados(): number {
    return this.contratosSeleccionados.size;
  }

  toggleGrupo(grupo: CharlaSupervisorGrupo): void {
    const key = this.grupoKey(grupo);
    if (this.gruposExpandidos.has(key)) {
      this.gruposExpandidos.delete(key);
    } else {
      this.gruposExpandidos.add(key);
    }
  }

  grupoExpandido(grupo: CharlaSupervisorGrupo): boolean {
    return this.gruposExpandidos.has(this.grupoKey(grupo));
  }

  toggleTrabajador(grupo: CharlaSupervisorGrupo, trabajador: CharlaTrabajadorGrupo): void {
    const key = this.trabajadorKey(grupo, trabajador);
    if (this.trabajadoresExpandidos.has(key)) {
      this.trabajadoresExpandidos.delete(key);
    } else {
      this.trabajadoresExpandidos.add(key);
    }
  }

  trabajadorExpandido(grupo: CharlaSupervisorGrupo, trabajador: CharlaTrabajadorGrupo): boolean {
    return this.trabajadoresExpandidos.has(this.trabajadorKey(grupo, trabajador));
  }

  supervisorNombre(sup: Supervisor): string {
    return `${sup.usuario_nombre || 'Sin nombre'} — ${sup.usuario_rut || 'Sin RUT'}`;
  }

  formatearFecha(fecha: string | null): string {
    if (!fecha) return '—';
    const partes = fecha.split('-');
    if (partes.length !== 3) return fecha;
    return `${partes[2]}-${partes[1]}-${partes[0]}`;
  }

  private fechaHoyISO(): string {
    const hoy = new Date();
    const yyyy = hoy.getFullYear();
    const mm = String(hoy.getMonth() + 1).padStart(2, '0');
    const dd = String(hoy.getDate()).padStart(2, '0');
    return `${yyyy}-${mm}-${dd}`;
  }

  private expandirGruposIniciales(): void {
    this.gruposExpandidos.clear();
    this.trabajadoresExpandidos.clear();

    this.charlaGrupos.forEach(grupo => {
      this.gruposExpandidos.add(this.grupoKey(grupo));
      grupo.trabajadores.forEach(trabajador => {
        this.trabajadoresExpandidos.add(this.trabajadorKey(grupo, trabajador));
      });
    });
  }

  private grupoKey(grupo: CharlaSupervisorGrupo): string {
    return String(grupo.supervisor_id ?? 'sin-charla');
  }

  private trabajadorKey(grupo: CharlaSupervisorGrupo, trabajador: CharlaTrabajadorGrupo): string {
    return `${this.grupoKey(grupo)}-${trabajador.trabajador_id}`;
  }
}