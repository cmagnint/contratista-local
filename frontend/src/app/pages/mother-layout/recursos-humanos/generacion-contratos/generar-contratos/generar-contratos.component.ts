import { Component, Inject, OnInit, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser, CommonModule } from '@angular/common';
import { ContratistaApiService } from '../../../../../services/contratista-api.service';
import { FormsModule } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatInputModule } from '@angular/material/input';
import { SelectionModel } from '@angular/cdk/collections';

@Component({
  selector: 'app-generar-contratos',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatTableModule,
    MatButtonModule,
    MatSelectModule,
    MatFormFieldModule,
    MatIconModule,
    MatCheckboxModule,
    MatInputModule,
  ],
  templateUrl: './generar-contratos.component.html',
  styleUrl: './generar-contratos.component.css'
})
export class GenerarContratosComponent implements OnInit {

  constructor(
    private apiService: ContratistaApiService,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {}

  // ─── Compartido ───────────────────────────────────
  holding     = '';
  sociedad    = '';
  sociedades: any[] = [];
  fechaEmision = '';
  contratosGenerados: any[] = [];
  mostrarContratos = false;
  marcarComoGenerado = false;

  modals: { [key: string]: boolean } = {
    exitoModal: false,
    errorModal: false,
    confirmacionRegenerarModal: false,
    decisionEstadoModal: false,
  };
  errorMessage  = '';
  confirmMessage = '';

  // ─── Modo ─────────────────────────────────────────
  // 'CLASICO' | 'PARAMETRO'
  modoGeneracion: string = '';

  // ─── Modo clásico ─────────────────────────────────
  trabajadores: any[] = [];
  documentos: any[]   = [];
  documentoSeleccionado: number | null = null;
  filtroContrato = 'sin_contrato';
  tipoFormato    = '';
  selection      = new SelectionModel<any>(true, []);
  selectedRows: any[] = [];

  displayedColumns: string[] = [
    'select', 'id', 'nombres', 'apellidos', 'rut', 'estado_contrato', 'cargo', 'fecha_ingreso'
  ];

  // ─── Modo parámetro ───────────────────────────────
  parametros: any[]          = [];
  parametroSeleccionado: number | null = null;
  trabajadoresParametro: any[] = [];  // [{trabajador_id, nombres, apellidos, rut, cargo, pdfs[], pdfSeleccionadoId}]
  selectionParam = new SelectionModel<any>(true, []);
  selectedRowsParam: any[]   = [];

  displayedColumnsParam: string[] = [
    'select', 'nombres', 'rut', 'pdf_selector'
  ];

  // ─── Lifecycle ────────────────────────────────────
  ngOnInit(): void {
    if (!isPlatformBrowser(this.platformId)) return;
    this.holding     = localStorage.getItem('holding_id') || '';
    this.fechaEmision = new Date().toISOString().split('T')[0];
    this.cargarSociedades();

    this.selection.changed.subscribe(() => {
      this.selectedRows = this.selection.selected;
    });
    this.selectionParam.changed.subscribe(() => {
      this.selectedRowsParam = this.selectionParam.selected;
    });
  }

  // ─── Sociedad ─────────────────────────────────────
  cargarSociedades(): void {
    this.apiService.get(`api_sociedades_modify/${this.holding}/`).subscribe({
      next: (res) => { this.sociedades = res; },
      error: () => this.mostrarError('Error al cargar sociedades'),
    });
  }

  onSociedadChange(): void {
    this.resetModo();
    this.modoGeneracion = '';
  }

  // ─── Modo ─────────────────────────────────────────
  seleccionarModo(modo: string): void {
    this.modoGeneracion = modo;
    this.resetModo();

    if (modo === 'CLASICO') {
      this.cargarTrabajadores();
    } else {
      this.cargarParametros();
    }
  }

  resetModo(): void {
    // clásico
    this.trabajadores         = [];
    this.documentos           = [];
    this.documentoSeleccionado = null;
    this.tipoFormato          = '';
    this.selection.clear();
    this.selectedRows         = [];
    // parámetro
    this.parametros           = [];
    this.parametroSeleccionado = null;
    this.trabajadoresParametro = [];
    this.selectionParam.clear();
    this.selectedRowsParam    = [];
    // compartido
    this.contratosGenerados   = [];
    this.mostrarContratos     = false;
  }

  // ─── Modo CLÁSICO ─────────────────────────────────
  cargarTrabajadores(): void {
    if (!this.sociedad) return;
    const params = `holding=${this.holding}&sociedad_id=${this.sociedad}&filtro_contrato=${this.filtroContrato}`;
    this.apiService.get(`api_personal_filtrado/?${params}`).subscribe({
      next: (res) => {
        this.trabajadores = res;
        this.selection.clear();
      },
      error: () => this.mostrarError('Error al cargar trabajadores'),
    });
  }

  cambiarFiltroContrato(filtro: string): void {
    this.filtroContrato        = filtro;
    this.tipoFormato           = '';
    this.documentos            = [];
    this.documentoSeleccionado = null;
    this.selection.clear();
    this.cargarTrabajadores();
  }

  cambiarTipoFormato(tipo: string): void {
    this.tipoFormato = tipo;
    this.cargarDocumentos();
  }

  cargarDocumentos(): void {
    if (!this.tipoFormato) { this.documentos = []; return; }
    this.apiService.get(`api_listar-documentos/?tipo=${this.tipoFormato}&holding=${this.holding}`).subscribe({
      next: (res) => {
        this.documentos           = res;
        this.documentoSeleccionado = null;
      },
      error: () => this.mostrarError('Error al cargar documentos'),
    });
  }

  isAllSelected(): boolean {
    return this.selection.selected.length === this.trabajadores.length;
  }

  toggleAllRows(): void {
    if (this.isAllSelected()) {
      this.selection.clear();
    } else {
      this.trabajadores.forEach(r => this.selection.select(r));
    }
  }

  generarContratosClasico(): void {
    if (!this.selectedRows.length) { this.mostrarError('Selecciona al menos un trabajador'); return; }
    if (!this.documentoSeleccionado)   { this.mostrarError('Selecciona un tipo de documento'); return; }
    if (!this.fechaEmision)             { this.mostrarError('Selecciona una fecha de emisión'); return; }

    const conContrato = this.selectedRows.filter(t => t.tiene_contrato);
    if (conContrato.length > 0 && this.filtroContrato !== 'con_contrato') {
      this.confirmMessage = `${conContrato.length} trabajador(es) ya tienen contrato generado. ¿Desea regenerarlo?`;
      this.openModal('confirmacionRegenerarModal');
      return;
    }
    this.openModal('decisionEstadoModal');
  }

  procederGeneracion(marcarGenerado: boolean): void {
    this.marcarComoGenerado = marcarGenerado;
    this.closeModal('decisionEstadoModal');
    this.confirmarGeneracionClasica();
  }

  confirmarGeneracionClasica(): void {
    const payload = {
      documento_id:         this.documentoSeleccionado,
      trabajador_ids:       this.selectedRows.map(t => t.id),
      fecha_emision:        this.fechaEmision,
      sociedad_id:          this.sociedad,
      marcar_como_generado: this.marcarComoGenerado,
    };
    this.apiService.post('api_generar-documentos-masivo/', payload).subscribe({
      next: (res) => {
        this.contratosGenerados = res.contratos || [];
        this.mostrarContratos   = true;
        this.closeModal('confirmacionRegenerarModal');
        this.selection.clear();
        this.selectedRows = [];
        this.cargarTrabajadores();
        this.openModal('exitoModal');
      },
      error: (err) => {
        this.closeModal('confirmacionRegenerarModal');
        this.mostrarError(err.error?.error || 'Error al generar contratos');
      },
    });
  }

  // ─── Modo PARÁMETRO ───────────────────────────────
  cargarParametros(): void {
    this.apiService.get('api_parametros/?con_formato=true').subscribe({
      next: (res) => { this.parametros = res; },
      error: () => this.mostrarError('Error al cargar parámetros'),
    });
  }

  onParametroChange(): void {
    this.trabajadoresParametro = [];
    this.selectionParam.clear();
    if (!this.parametroSeleccionado) return;

    const params = `parametro_id=${this.parametroSeleccionado}&sociedad_id=${this.sociedad}`;
    this.apiService.get(`api_trabajadores_por_parametro/?${params}`).subscribe({
      next: (res) => {
        // Agregar pdfSeleccionadoId = primer pdf (menor orden)
        this.trabajadoresParametro = res.map((t: any) => ({
          ...t,
          pdfSeleccionadoId: t.pdfs?.[0]?.id ?? null,
        }));
      },
      error: () => this.mostrarError('Error al cargar trabajadores del parámetro'),
    });
  }

  isAllSelectedParam(): boolean {
    return this.selectionParam.selected.length === this.trabajadoresParametro.length;
  }

  toggleAllRowsParam(): void {
    if (this.isAllSelectedParam()) {
      this.selectionParam.clear();
    } else {
      this.trabajadoresParametro.forEach(r => this.selectionParam.select(r));
    }
  }

  generarContratosPorParametro(): void {
    if (!this.selectedRowsParam.length) { this.mostrarError('Selecciona al menos un trabajador'); return; }
    if (!this.fechaEmision)              { this.mostrarError('Selecciona una fecha de emisión'); return; }

    const payload = {
      parametro_id:   this.parametroSeleccionado,
      sociedad_id:    this.sociedad,
      fecha_emision:  this.fechaEmision,
      trabajadores:   this.selectedRowsParam.map(t => ({
        trabajador_id:        t.trabajador_id,
        contrato_asociado_id: t.pdfSeleccionadoId,
      })),
    };

    this.apiService.post('api_generar-documentos-por-parametro/', payload).subscribe({
      next: (res) => {
        this.contratosGenerados = res.contratos || [];
        this.mostrarContratos   = true;
        this.selectionParam.clear();
        this.selectedRowsParam  = [];
        this.openModal('exitoModal');
      },
      error: (err) => {
        this.mostrarError(err.error?.error || 'Error al generar contratos');
      },
    });
  }

  // ─── Descargas ────────────────────────────────────
  descargarContrato(url: string): void {
    window.open(url, '_blank');
  }

  descargarTodosContratos(): void {
    if (this.contratosGenerados.length === 1) {
      this.descargarContrato(this.contratosGenerados[0].url);
      return;
    }
    import('jszip').then(JSZip => {
      const zip = new JSZip.default();
      let completados = 0;
      this.contratosGenerados.forEach(contrato => {
        fetch(contrato.url)
          .then(r => r.blob())
          .then(blob => {
            zip.file(`contrato_${contrato.trabajador_nombre.replace(/\s+/g, '_')}.pdf`, blob);
            completados++;
            if (completados === this.contratosGenerados.length) {
              zip.generateAsync({ type: 'blob' }).then(content => {
                const a = document.createElement('a');
                a.href = URL.createObjectURL(content);
                a.download = `contratos_${this.fechaEmision}.zip`;
                a.click();
              });
            }
          })
          .catch(() => { completados++; });
      });
    });
  }

  cerrarPanelContratos(): void {
    this.contratosGenerados = [];
    this.mostrarContratos   = false;
  }

  // ─── Modales ──────────────────────────────────────
  openModal(key: string): void  { this.modals[key] = true;  }
  closeModal(key: string): void {
    this.modals[key] = false;
    if (key === 'errorModal')               this.errorMessage   = '';
    if (key === 'confirmacionRegenerarModal') this.confirmMessage = '';
  }

  mostrarError(msg: string): void {
    this.errorMessage = msg;
    this.openModal('errorModal');
  }
}