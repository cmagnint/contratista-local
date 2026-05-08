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

  constructor(private api: ContratistaApiService) {}

  cargarSupervisores(): void {
  if (!this.holdingId) return;
  this.loading = true;

  this.api.get(`api_supervisores/${this.holdingId}/`).subscribe({
    next: (data: any) => {
      this.supervisores = Array.isArray(data) ? data : [];
      this.loading = false;
      this.cargarUsuarios(); // garantiza orden
    },
    error: () => {
      this.supervisores = [];
      this.loading = false;
      this.cargarUsuarios();
    }
  });
}

ngOnInit(): void {
  this.holdingId = Number(localStorage.getItem('holding_id') || 0);
  this.cargarSupervisores(); // usuarios se carga dentro
}

  cargarUsuarios(): void {
    if (!this.holdingId) return;

    this.api.get(`api_usuarios/${this.holdingId}/`).subscribe({
      next: (data: any) => {
        const raw: any[] = Array.isArray(data) ? data : (data.results ?? []);
        
        // IDs de usuarios que ya son supervisores en este holding
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

    // Inyectar el usuario del supervisor en la lista si no está (fue filtrado por ya ser supervisor)
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
}