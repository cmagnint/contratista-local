//formatos.component.ts
import { Component, Inject, NgZone, OnDestroy, OnInit, PLATFORM_ID, ViewChild } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ContratistaApiService } from '../../../../../services/contratista-api.service';
import { JwtService } from '../../../../../services/jwt.service';

// Interfaz para una ubicación específica de una variable
interface Ubicacion {
  pagina: number;
  posX: number;
  posY: number;
  id: string;
  pageWidth: number;
  pageHeight: number;
  width?: number;
  height?: number;
  valor?: string;
  fontSize?: number;
}

interface VariableDocumento {
  nombre: string;
  valor: string;
  posX: number;
  posY: number;
  pagina: number;
  colocada: boolean;
  ubicaciones: Ubicacion[];
}

// Interfaz para el mapa interno de variables colocadas
interface VariablePosicionada {
  nombre: string;
  posX: number;
  posY: number;
  elementId: string;
  variableIndex: number;
}

// Interfaz para variables con datos de prueba
interface VariableConDatos {
  nombre: string;
  tipo: string;
  valorPredeterminado: string;
  valorPrueba: string;
}


interface ElementoSeguridadOption {
  id: number;
  elemento: string;
  cantidad: string | null;
}

interface PdfParteInfo {
  indice: number;
  tipo: 'ORIGINAL' | 'ANEXO';
  etiqueta: string;
  nombreArchivo: string;
  paginas: number;
  paginaInicio: number;
  paginaFin: number;
  color: string;
}

@Component({
  selector: 'app-formatos',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule
  ],
  templateUrl: './formatos.component.html',
  styleUrl: './formatos.component.css'
})
export class FormatosComponent implements OnInit, OnDestroy {
  pdfSrc: string | ArrayBuffer | null = null;
  isLoading = false;
  isBrowser: boolean;
  errorMessage: string | null = null;
  public holding: string = '';
  private readonly PDF_DISPLAY_MULTIPLIER = 1.4;
  private readonly PDF_TEXT_FONT_SIZE_PT = 9;
  private readonly PDF_TEXT_ASCENT_RATIO = 0.74;
  private readonly IMAGE_VARIABLES = [
    'firma_empleador',
    'timbre_empleador',
    'firma',
    'huella',
    'firma_supervisor',
    'huella_supervisor'
  ];

  panelVariablesContraido = false;
  vistaFinalPDF = false;
  mostrarDebugCoordenadas = false;
  zoomPDF = 1;
  mostrarControlesCargaPDF = true;

  variableSeleccionadaParaPropiedades: {
    nombre: string;
    pagina: number;
    posX: number;
    posY: number;
    width?: number;
    height?: number;
    fontSize?: number;
    elementId: string;
    variableIndex: number;
  } | null = null;

  // Store the original File object
  originalPdfFile: File | null = null;
  // Array para almacenar múltiples PDFs
  pdfDocuments: any[] = [];
  pdfBuffers: ArrayBuffer[] = [];
  pdfFiles: File[] = [];
  totalPages: number = 0;
  pdfPages: any[] = [];
  totalPagesAcumuladas: number[] = []; // Páginas acumuladas por cada PDF


  // Identificación visual y administración de PDF original/anexos
  pdfPartesInfo: PdfParteInfo[] = [];
  seccionPDFActiva: PdfParteInfo | null = null;
  paginaPDFActiva: number = 1;
  private pdfScrollObserver: IntersectionObserver | null = null;
  private readonly PDF_ORIGINAL_COLOR = '#00E5FF';
  private readonly PDF_ANEXO_COLORS = [
    '#39FF14',
    '#FFEA00',
    '#FF4FD8',
    '#00FFC6',
    '#FF7A00',
    '#B967FF',
    '#00B7FF',
    '#FF3864'
  ];

  // Modal properties
  mostrarModal = false;
  nombreFormato = '';
  tipoContrato = 'CHILENO';
  mostrarModalTipoContrato = false;

  documentoGuardadoId: number | null = null;

  // Modal para datos de prueba
  mostrarModalDatosPrueba = false;
  variablesConDatos: VariableConDatos[] = [];
  pdfPreviewUrl: string | null = null;

  // Nuevas propiedades para modo documento existente
  modoDocumentoExistente: boolean = false;
  documentosCargados: any[] = [];
  documentoSeleccionado: any = null;

  // Propiedades para dimensiones nativas del PDF
  pdfNativeWidth: number = 0;
  pdfNativeHeight: number = 0;

  // Propiedades Elemento Seguridad
  elementosSeguridad: ElementoSeguridadOption[] = [];
  mostrarModalElementoSeguridad: boolean = false;
  elementoSeleccionadoTemp: ElementoSeguridadOption | null = null;
  elementoSeguridadPendiente: ElementoSeguridadOption | null = null;
  variableBuscada: string = '';
  filtroDocumentoBuscado: string = '';
  filtroDocumentoTipo: string = '';
  filtroDocumentoFecha: string = '';
  documentoEditandoNombreId: number | null = null;
  nombreDocumentoEditado: string = '';
  documentosFiltradosCache: any[] = [];
  documentosAgrupadosCache: { tipo: string; documentos: any[] }[] = [];
  documentosEliminandoIds = new Set<number>();

  readonly TEXTO_LIBRE_VARIABLE = 'texto_libre';
  readonly TEXTOS_LIBRES_CONTAINER = 'textos_libres';
  mostrarModalTextoLibre: boolean = false;
  textoLibreTemp: string = '';
  textoLibrePendiente: string = '';

  // ⭐ PROPIEDADES PARA FIRMA EMPLEADOR
  firmaEmpleadorDisponible: boolean = false;
  firmaEmpleadorUrl: string | null = null;
  mostrarModalFirmaEmpleador: boolean = false;

  // Propiedades para timbre empleador
  timbreEmpleadorDisponible: boolean = false;
  timbreEmpleadorUrl: string | null = null;
  mostrarModalTimbreEmpleador: boolean = false;

  // ⭐ PROPIEDADES PARA FIRMA TRABAJADOR (PLACEHOLDER)
  readonly FIRMA_TRABAJADOR_PLACEHOLDER = 'assets/images/firma_trabajador_placeholder.png';
  readonly FIRMA_TRABAJADOR_WIDTH = 150;
  readonly FIRMA_TRABAJADOR_HEIGHT = 50;

  // ⭐ NUEVO: PROPIEDADES PARA HUELLA TRABAJADOR (PLACEHOLDER)
  readonly HUELLA_TRABAJADOR_PLACEHOLDER = 'assets/images/huella_trabajador_placeholder.png';
  readonly HUELLA_TRABAJADOR_WIDTH = 80;
  readonly HUELLA_TRABAJADOR_HEIGHT = 100;

  // ⭐ NUEVO: PROPIEDADES PARA SUPERVISOR (PLACEHOLDER)
  readonly FIRMA_SUPERVISOR_PLACEHOLDER = 'assets/images/firma_trabajador_placeholder.png';
  readonly FIRMA_SUPERVISOR_WIDTH = 150;
  readonly FIRMA_SUPERVISOR_HEIGHT = 50;
  readonly HUELLA_SUPERVISOR_PLACEHOLDER = 'assets/images/huella_trabajador_placeholder.png';
  readonly HUELLA_SUPERVISOR_WIDTH = 80;
  readonly HUELLA_SUPERVISOR_HEIGHT = 100;

  // Control de redimensionamiento de imagen
  imagenFirmaEnEdicion: {
    element: HTMLElement;
    originalWidth: number;
    originalHeight: number;
    minWidth: number;
    minHeight: number;
  } | null = null;

  // Variables de documento con array de ubicaciones
  variables: VariableDocumento[] = [
    { nombre: 'fecha_emision', valor: '', posX: 0, posY: 0, pagina: 1, colocada: false, ubicaciones: [] },
    { nombre: 'fecha_ingreso', valor: '', posX: 0, posY: 0, pagina: 1, colocada: false, ubicaciones: [] },
    { nombre: 'fecha_inicio_contrato', valor: '', posX: 0, posY: 0, pagina: 1, colocada: false, ubicaciones: [] },
    { nombre: 'fecha_termino', valor: '', posX: 0, posY: 0, pagina: 1, colocada: false, ubicaciones: [] },
    { nombre: 'nombre_completo', valor: '', posX: 0, posY: 0, pagina: 1, colocada: false, ubicaciones: [] },
    { nombre: 'rut', valor: '', posX: 0, posY: 0, pagina: 1, colocada: false, ubicaciones: [] },
    { nombre: 'dni', valor: '', posX: 0, posY: 0, pagina: 1, colocada: false, ubicaciones: [] },
    { nombre: 'nic', valor: '', posX: 0, posY: 0, pagina: 1, colocada: false, ubicaciones: [] },
    { nombre: 'sociedad', valor: '', posX: 0, posY: 0, pagina: 1, colocada: false, ubicaciones: [] },
    { nombre: 'nombre_cliente', valor: '', posX: 0, posY: 0, pagina: 1, colocada: false, ubicaciones: [] },
    { nombre: 'nombre_campo', valor: '', posX: 0, posY: 0, pagina: 1, colocada: false, ubicaciones: [] },
    { nombre: 'nacionalidad', valor: '', posX: 0, posY: 0, pagina: 1, colocada: false, ubicaciones: [] },
    { nombre: 'fecha_nacimiento', valor: '', posX: 0, posY: 0, pagina: 1, colocada: false, ubicaciones: [] },
    { nombre: 'estado_civil', valor: '', posX: 0, posY: 0, pagina: 1, colocada: false, ubicaciones: [] },
    { nombre: 'domicilio', valor: '', posX: 0, posY: 0, pagina: 1, colocada: false, ubicaciones: [] },
    { nombre: 'horario', valor: '', posX: 0, posY: 0, pagina: 1, colocada: false, ubicaciones: [] },
    { nombre: 'lugar_trabajo', valor: '', posX: 0, posY: 0, pagina: 1, colocada: false, ubicaciones: [] },
    { nombre: 'afp', valor: '', posX: 0, posY: 0, pagina: 1, colocada: false, ubicaciones: [] },
    { nombre: 'salud', valor: '', posX: 0, posY: 0, pagina: 1, colocada: false, ubicaciones: [] },
    { nombre: 'telefono', valor: '', posX: 0, posY: 0, pagina: 1, colocada: false, ubicaciones: [] },
    { nombre: 'correo', valor: '', posX: 0, posY: 0, pagina: 1, colocada: false, ubicaciones: [] },
    { nombre: 'tipo_pago', valor: '', posX: 0, posY: 0, pagina: 1, colocada: false, ubicaciones: [] },
    { nombre: 'banco', valor: '', posX: 0, posY: 0, pagina: 1, colocada: false, ubicaciones: [] },
    { nombre: 'tipo_cuenta', valor: '', posX: 0, posY: 0, pagina: 1, colocada: false, ubicaciones: [] },
    { nombre: 'numero_cuenta', valor: '', posX: 0, posY: 0, pagina: 1, colocada: false, ubicaciones: [] },
    { nombre: 'cargo', valor: '', posX: 0, posY: 0, pagina: 1, colocada: false, ubicaciones: [] },
    { nombre: 'area', valor: '', posX: 0, posY: 0, pagina: 1, colocada: false, ubicaciones: [] },
    { nombre: 'contacto_emergencia_nombre', valor: '', posX: 0, posY: 0, pagina: 1, colocada: false, ubicaciones: [] },
    { nombre: 'contacto_emergencia_telefono', valor: '', posX: 0, posY: 0, pagina: 1, colocada: false, ubicaciones: [] },
    { nombre: 'firma_empleador', valor: '', posX: 0, posY: 0, pagina: 1, colocada: false, ubicaciones: [] },
    { nombre: 'timbre_empleador', valor: '', posX: 0, posY: 0, pagina: 1, colocada: false, ubicaciones: [] },
    { nombre: 'firma', valor: '', posX: 0, posY: 0, pagina: 1, colocada: false, ubicaciones: [] },
    { nombre: 'huella', valor: '', posX: 0, posY: 0, pagina: 1, colocada: false, ubicaciones: [] },
    { nombre: 'elemento_seguridad', valor: '', posX: 0, posY: 0, pagina: 1, colocada: false, ubicaciones: [] },
    { nombre: 'cantidad_seguridad', valor: '', posX: 0, posY: 0, pagina: 1, colocada: false, ubicaciones: [] },
    { nombre: 'texto_libre', valor: '', posX: 0, posY: 0, pagina: 1, colocada: false, ubicaciones: [] },
    { nombre: 'nombre_supervisor', valor: '', posX: 0, posY: 0, pagina: 1, colocada: false, ubicaciones: [] },
    { nombre: 'firma_supervisor', valor: '', posX: 0, posY: 0, pagina: 1, colocada: false, ubicaciones: [] },
    { nombre: 'huella_supervisor', valor: '', posX: 0, posY: 0, pagina: 1, colocada: false, ubicaciones: [] },
  ];

  // Track variables placed on each page
  variablesPorPagina: Map<number, VariablePosicionada[]> = new Map();

  // Variable seleccionada actualmente
  variableSeleccionada: VariableDocumento | null = null;

  // Estado para modo de posicionamiento
  modoColocacion: boolean = false;

  // Variables para el arrastre
  variableArrastrandose: VariablePosicionada | null = null;
  elementoArrastrandose: HTMLElement | null = null;
  offsetX: number = 0;
  offsetY: number = 0;
  paginaActualArrastre: HTMLElement | null = null;
  paginaNumeroArrastre: number = 0;

  // Guardar referencia al documento PDF para reutilizarlo
  private pdfDocument: any = null;

  // Nueva propiedad para el modo de modificación
  modoModificacion: boolean = false;

  // Control de cambios pendientes
  haycambiosPendientes: boolean = false;

  constructor(
    @Inject(PLATFORM_ID) private platformId: Object,
    private ngZone: NgZone,
    private apiService: ContratistaApiService,
    private jwtService: JwtService,
  ) {
    this.isBrowser = isPlatformBrowser(this.platformId);
  }

  ngOnInit(): void {
    if (this.isBrowser) {
      document.addEventListener('mousemove', this.handleMouseMove.bind(this));
      document.addEventListener('mouseup', this.handleMouseUp.bind(this));

      this.holding = this.getHoldingIdFromJWT();
    }

    this.documentoSeleccionado = null;
    this.modoModificacion = false;

    if (this.holding) {
      this.cargarFirmaEmpleador();
      this.cargarTimbreEmpleador();
      this.cargarElementosSeguridad();
    }
  }


  ngOnDestroy(): void {
    if (this.pdfScrollObserver) {
      this.pdfScrollObserver.disconnect();
      this.pdfScrollObserver = null;
    }
  }

  onFiltroDocumentoChange(): void {
    this.recalcularDocumentosExistentes();
  }

  recalcularDocumentosExistentes(): void {
    this.documentosFiltradosCache = this.filtrarDocumentos(this.documentosCargados);
    this.documentosAgrupadosCache = this.agruparDocumentosPorTipo(this.documentosFiltradosCache);
  }

  private filtrarDocumentos(documentos: any[]): any[] {
    const busqueda = this.normalizarTexto(this.filtroDocumentoBuscado);
    const tipo = this.normalizarTexto(this.filtroDocumentoTipo);
    const fecha = this.filtroDocumentoFecha;

    return (documentos || []).filter((doc: any) => {
      const nombreDoc = this.normalizarTexto(doc.nombre);
      const tipoDoc = this.normalizarTexto(doc.tipo);
      const fechaDoc = doc.fecha_creacion ? new Date(doc.fecha_creacion) : null;

      const coincideNombre =
        !busqueda ||
        nombreDoc.includes(busqueda) ||
        tipoDoc.includes(busqueda) ||
        (doc.fecha_creacion || '').toString().includes(busqueda);

      const coincideTipo =
        !tipo ||
        tipoDoc === tipo;

      const coincideFecha =
        !fecha ||
        (
          fechaDoc &&
          fechaDoc.toISOString().slice(0, 10) === fecha
        );

      return coincideNombre && coincideTipo && coincideFecha;
    });
  }

  private agruparDocumentosPorTipo(documentos: any[]): { tipo: string; documentos: any[] }[] {
    const ordenTipos = ['CHILENO', 'EXTRANJERO'];
    const grupos: { [key: string]: any[] } = {};

    documentos.forEach((doc: any) => {
      const tipo = (doc.tipo || 'SIN TIPO').toUpperCase();
      if (!grupos[tipo]) grupos[tipo] = [];
      grupos[tipo].push(doc);
    });

    return Object.keys(grupos)
      .sort((a, b) => {
        const ia = ordenTipos.indexOf(a);
        const ib = ordenTipos.indexOf(b);

        if (ia !== -1 && ib !== -1) return ia - ib;
        if (ia !== -1) return -1;
        if (ib !== -1) return 1;
        return a.localeCompare(b);
      })
      .map(tipo => ({
        tipo,
        documentos: [...grupos[tipo]].sort((a, b) => {
          const fa = a.fecha_creacion ? new Date(a.fecha_creacion).getTime() : 0;
          const fb = b.fecha_creacion ? new Date(b.fecha_creacion).getTime() : 0;
          return fb - fa;
        })
      }));
  }

  trackByGrupoTipo(index: number, grupo: { tipo: string; documentos: any[] }): string {
    return grupo.tipo;
  }

  trackByDocumentoId(index: number, documento: any): number {
    return documento.id;
  }

  private getHoldingIdFromJWT(): string {
    try {
      const userInfo = this.jwtService.getUserInfo();
      const holdingId = userInfo?.holding_id;

      console.log('🔍 Holding ID del JWT:', holdingId);

      if (holdingId && holdingId !== null) {
        return holdingId.toString();
      } else {
        console.warn('⚠️ Holding ID no encontrado en JWT o es null');
        return '';
      }
    } catch (error) {
      console.error('❌ Error extrayendo holding_id del JWT:', error);
      return '';
    }
  }

  /**
   * Cargar firma del empleador desde backend
   */
  cargarFirmaEmpleador(): void {
    if (!this.holding) {
      console.warn('⚠️ No se puede cargar firma: holding no disponible');
      return;
    }

    this.apiService.get(`api_firma_empleador/?holding_id=${this.holding}`)
      .subscribe({
        next: (response: any) => {
          this.firmaEmpleadorDisponible = response.firma_disponible;
          this.firmaEmpleadorUrl = response.firma_url || null;

          console.log('✅ Estado firma empleador:', {
            disponible: this.firmaEmpleadorDisponible,
            url: this.firmaEmpleadorUrl
          });
        },
        error: (error) => {
          console.error('Error al cargar firma empleador:', error);
          this.firmaEmpleadorDisponible = false;
        }
      });
  }

  cargarTimbreEmpleador(): void {
    if (!this.holding) {
      console.warn('No se puede cargar timbre: holding no disponible');
      return;
    }

    this.apiService.get(`api/holding/${this.holding}/timbre-empleador/`)
      .subscribe({
        next: (response: any) => {
          this.timbreEmpleadorDisponible = true;
          this.timbreEmpleadorUrl = response.timbre_empleador || null;
        },
        error: (error) => {
          if (error.status !== 404) {
            console.error('Error al cargar timbre empleador:', error);
          }
          this.timbreEmpleadorDisponible = false;
          this.timbreEmpleadorUrl = null;
        }
      });
  }

  cargarElementosSeguridad(): void {
    if (!this.holding) {
      console.warn('No se puede cargar elementos de seguridad: holding no disponible');
      return;
    }

    this.apiService.get(`api_elemento_seguridad/?holding=${this.holding}`)
      .subscribe({
        next: (response: any) => {
          this.elementosSeguridad = Array.isArray(response) ? response : [];
        },
        error: (error) => {
          console.error('Error al cargar elementos de seguridad:', error);
          this.elementosSeguridad = [];
        }
      });
  }

  confirmarElementoSeguridad(): void {
    if (!this.elementoSeleccionadoTemp) return;

    const variableElemento = this.variables.find(v => v.nombre === 'elemento_seguridad');

    if (!variableElemento) {
      alert('No existe la variable elemento_seguridad');
      return;
    }

    this.elementoSeguridadPendiente = this.elementoSeleccionadoTemp;
    this.mostrarModalElementoSeguridad = false;

    this.iniciarColocacionVariable(variableElemento);
  }

  /**
   * Abrir modal para subir firma
   */
  abrirModalFirmaEmpleador(): void {
    this.mostrarModalFirmaEmpleador = true;
  }

  /**
   * Cerrar modal
   */
  cerrarModalFirmaEmpleador(): void {
    this.mostrarModalFirmaEmpleador = false;
  }

  abrirModalTimbreEmpleador(): void {
    this.mostrarModalTimbreEmpleador = true;
  }

  cerrarModalTimbreEmpleador(): void {
    this.mostrarModalTimbreEmpleador = false;
  }

  /**
   * Subir firma del empleador
   */
  onFirmaEmpleadorSelected(event: Event): void {
    const input = event.target as HTMLInputElement;

    if (input.files && input.files[0]) {
      const file = input.files[0];

      // Validar tipo
      const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif'];
      if (!allowedTypes.includes(file.type)) {
        alert('Formato no válido. Use JPG, PNG o GIF');
        return;
      }

      // Validar tamaño (5MB)
      if (file.size > 5 * 1024 * 1024) {
        alert('La imagen es demasiado grande. Máximo 5MB');
        return;
      }

      // Subir al backend
      const formData = new FormData();
      formData.append('firma_empleador', file);
      formData.append('holding_id', this.holding);

      this.isLoading = true;

      this.apiService.postFormData('api_firma_empleador/', formData)
        .subscribe({
          next: (response: any) => {
            console.log('✅ Firma subida:', response);
            this.firmaEmpleadorDisponible = true;
            this.firmaEmpleadorUrl = response.firma_url;
            this.isLoading = false;
            this.cerrarModalFirmaEmpleador();
            alert('Firma del empleador actualizada exitosamente');
          },
          error: (error) => {
            console.error('Error al subir firma:', error);
            alert(`Error: ${error.error?.error || 'No se pudo subir la firma'}`);
            this.isLoading = false;
          }
        });
    }
  }

  onTimbreEmpleadorSelected(event: Event): void {
    const input = event.target as HTMLInputElement;

    if (input.files && input.files[0]) {
      const file = input.files[0];
      const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif'];
      if (!allowedTypes.includes(file.type)) {
        alert('Formato no válido. Use JPG, PNG o GIF');
        return;
      }

      if (file.size > 5 * 1024 * 1024) {
        alert('La imagen es demasiado grande. Máximo 5MB');
        return;
      }

      const formData = new FormData();
      formData.append('imagen', file);

      this.isLoading = true;
      const request$ = this.timbreEmpleadorDisponible
        ? this.apiService.putFormData(`api/holding/${this.holding}/timbre-empleador/`, formData)
        : this.apiService.postFormData(`api/holding/${this.holding}/timbre-empleador/`, formData);

      request$.subscribe({
        next: (response: any) => {
          this.timbreEmpleadorDisponible = true;
          this.timbreEmpleadorUrl = response.timbre_empleador;
          this.isLoading = false;
          this.cerrarModalTimbreEmpleador();
          alert('Timbre del empleador actualizado exitosamente');
        },
        error: (error) => {
          console.error('Error al subir timbre:', error);
          alert(`Error: ${error.error?.error || 'No se pudo subir el timbre'}`);
          this.isLoading = false;
        }
      });
    }
  }

  iniciarColocacionVariable(variable: VariableDocumento): void {
    this.variableSeleccionada = variable;
    this.modoColocacion = true;

    const pdfContainer = document.getElementById('pdf-container');

    if (pdfContainer) {
      pdfContainer.style.cursor = 'crosshair';
      pdfContainer.addEventListener('click', this.handlePdfClick.bind(this), { once: true });
    }
  }

  /**
   * Eliminar firma del empleador
   */
  eliminarFirmaEmpleador(): void {
    if (!confirm('¿Está seguro de eliminar la firma del empleador?')) {
      return;
    }

    this.isLoading = true;

    this.apiService.delete(`api_firma_empleador/?holding_id=${this.holding}`, {})
      .subscribe({
        next: (response: any) => {
          console.log('✅ Firma eliminada:', response);
          this.firmaEmpleadorDisponible = false;
          this.firmaEmpleadorUrl = null;
          this.isLoading = false;
          alert('Firma del empleador eliminada');
        },
        error: (error) => {
          console.error('Error al eliminar firma:', error);
          alert('No se pudo eliminar la firma');
          this.isLoading = false;
        }
      });
  }

  eliminarTimbreEmpleador(): void {
    if (!confirm('¿Está seguro de eliminar el timbre del empleador?')) {
      return;
    }

    this.isLoading = true;

    this.apiService.delete(`api/holding/${this.holding}/timbre-empleador/`, {})
      .subscribe({
        next: () => {
          this.timbreEmpleadorDisponible = false;
          this.timbreEmpleadorUrl = null;
          this.isLoading = false;
          alert('Timbre del empleador eliminado');
        },
        error: (error) => {
          console.error('Error al eliminar timbre:', error);
          alert('No se pudo eliminar el timbre');
          this.isLoading = false;
        }
      });
  }

  /**
   * Verificar si variable está disponible
   */
  variableEstaDisponible(variable: VariableDocumento): boolean {
    if (variable.nombre === 'firma_empleador') {
      return this.firmaEmpleadorDisponible;
    }
    if (variable.nombre === 'timbre_empleador') {
      return this.timbreEmpleadorDisponible;
    }
    // ⭐ FIRMA Y HUELLA TRABAJADOR: siempre disponibles (son placeholders)
    return true;
  }

  /**
   * Obtener valor de ejemplo realista para cada variable
   */
  obtenerValorEjemplo(nombreVariable: string): string {
    const ejemplos: { [key: string]: string } = {
      'fecha_emision': '05/11/2025',
      'fecha_ingreso': '15/03/2024',
      'fecha_inicio_contrato': '15/03/2024',
      'fecha_termino': '14/03/2025',
      'nombre_completo': 'Juan Pérez González',
      'rut': '12.345.678-9',
      'dni': '45.678.901',
      'nic': 'NIC123456789',
      'sociedad': 'Agrícola El Valle Limitada',
      'nombre_cliente': 'Cliente Agricola SPA',
      'nombre_campo': 'Fundo Las Camelias',
      'nacionalidad': 'Chilena',
      'fecha_nacimiento': '25/08/1990',
      'estado_civil': 'Soltero(a)',
      'domicilio': 'Av. Las Condes 123, Santiago',
      'horario': 'Jornada Completa',
      'lugar_trabajo': 'Fundo Los Pinos',
      'afp': 'AFP Capital',
      'salud': 'Fonasa',
      'telefono': '+56 9 1234 5678',
      'correo': 'trabajador@empresa.cl',
      'tipo_pago': 'Transferencia bancaria',
      'banco': 'Banco de Chile',
      'tipo_cuenta': 'Cuenta corriente',
      'numero_cuenta': '123456789',
      'cargo': 'Operario Agrícola',
      'area': 'Producción',
      'contacto_emergencia_nombre': 'María González',
      'contacto_emergencia_telefono': '+56 9 8765 4321',
      'firma_empleador': '[Firma Empleador]',
      'timbre_empleador': '[Timbre Empleador]',
      'firma': '[Firma Trabajador]',
      'huella': '[Huella Digital]',
      'elemento_seguridad': '[Elemento de Seguridad]',
      'cantidad_seguridad': '[Cantidad del Elemento]',
      'nombre_supervisor': 'Carlos Rodríguez Díaz',
      'firma_supervisor': '[Firma Supervisor]',
      'huella_supervisor': '[Huella Supervisor]',
      'texto_libre': '[Texto Libre]',


    };

    return ejemplos[nombreVariable] || nombreVariable;
  }

  /**
   * Determinar si una variable debería estar centrada
   */
  esCampocentrado(nombreVariable: string): boolean {
    const camposCentrados = ['rut', 'dni', 'nic', 'estado_civil', 'fecha_nacimiento', 'fecha_emision', 'fecha_ingreso', 'fecha_inicio_contrato', 'fecha_termino'];
    return camposCentrados.includes(nombreVariable);
  }

  /**
   * Inicializa las dimensiones nativas del PDF sin renderizarlo
   */
  private async inicializarDimensionesPDF(pdfArrayBuffer: ArrayBuffer): Promise<void> {
    return new Promise(async (resolve, reject) => {
      try {
        if (!(window as any).pdfjsLib) {
          await this.loadPdfJsScript();
        }

        const pdfjsLib = (window as any).pdfjsLib;
        const workerUrl = `https://cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjsLib.version}/pdf.worker.min.js`;
        pdfjsLib.GlobalWorkerOptions.workerSrc = workerUrl;

        const bufferCopy = pdfArrayBuffer.slice(0);

        const loadingTask = pdfjsLib.getDocument({ data: bufferCopy });
        const pdf = await loadingTask.promise;

        const firstPage = await pdf.getPage(1);
        const nativeViewport = firstPage.getViewport({ scale: 1.0 });

        this.pdfNativeWidth = nativeViewport.width;
        this.pdfNativeHeight = nativeViewport.height;

        console.log(`✅ Dimensiones nativas inicializadas: ${this.pdfNativeWidth} x ${this.pdfNativeHeight}`);

        resolve();
      } catch (error) {
        console.error('Error al inicializar dimensiones del PDF:', error);
        reject(error);
      }
    });
  }

  /**
   * Cargar lista de documentos existentes desde el backend
   */
  cargarDocumentosExistentes(): void {
    this.modoDocumentoExistente = true;
    this.isLoading = true;
    this.documentosCargados = [];
    this.documentosFiltradosCache = [];
    this.documentosAgrupadosCache = [];
    this.documentoSeleccionado = null;
    this.modoModificacion = false;

    this.apiService.get('api_documento_nativo/')
      .subscribe({
        next: (response: any) => {
          this.documentosCargados = Array.isArray(response) ? response : [];
          this.recalcularDocumentosExistentes();
          this.isLoading = false;
        },
        error: (error) => {
          console.error('Error al cargar documentos:', error);
          this.errorMessage = 'No se pudieron cargar los documentos existentes.';
          this.isLoading = false;
        }
      });
  }


  private obtenerEtiquetaPartePDF(indice: number): string {
    return indice === 0 ? 'O' : `A${indice}`;
  }

  private obtenerColorPartePDF(indice: number): string {
    if (indice === 0) return this.PDF_ORIGINAL_COLOR;
    return this.PDF_ANEXO_COLORS[(indice - 1) % this.PDF_ANEXO_COLORS.length];
  }

  private recalcularTotalPagesAcumuladas(): void {
    let acumulado = 0;
    this.totalPagesAcumuladas = [];

    this.pdfDocuments.forEach(doc => {
      acumulado += Number(doc?.numPages || 0);
      this.totalPagesAcumuladas.push(acumulado);
    });

    this.totalPages = acumulado;
  }

  private recalcularPdfPartesInfo(): void {
    let paginaInicio = 1;

    this.pdfPartesInfo = this.pdfDocuments.map((doc: any, index: number) => {
      const paginas = Number(doc?.numPages || 0);
      const paginaFin = paginas > 0 ? paginaInicio + paginas - 1 : paginaInicio;
      const etiqueta = this.obtenerEtiquetaPartePDF(index);
      const tipo = index === 0 ? 'ORIGINAL' : 'ANEXO';
      const nombreArchivo =
        this.pdfFiles[index]?.name ||
        (index === 0 ? this.originalPdfFile?.name : '') ||
        (index === 0 ? this.documentoSeleccionado?.nombre : '') ||
        `${tipo === 'ORIGINAL' ? 'PDF original' : 'Anexo'} ${etiqueta}`;

      const parte: PdfParteInfo = {
        indice: index,
        tipo,
        etiqueta,
        nombreArchivo,
        paginas,
        paginaInicio,
        paginaFin,
        color: this.obtenerColorPartePDF(index)
      };

      paginaInicio = paginaFin + 1;
      return parte;
    });

    if (!this.seccionPDFActiva && this.pdfPartesInfo.length > 0) {
      this.seccionPDFActiva = this.pdfPartesInfo[0];
      this.paginaPDFActiva = this.pdfPartesInfo[0].paginaInicio;
    } else if (this.seccionPDFActiva) {
      const parteActualizada = this.pdfPartesInfo.find(p => p.indice === this.seccionPDFActiva?.indice);
      this.seccionPDFActiva = parteActualizada || this.pdfPartesInfo[0] || null;
      this.paginaPDFActiva = this.seccionPDFActiva?.paginaInicio || 1;
    }
  }

  get totalAnexosPDF(): number {
    return Math.max(0, this.pdfPartesInfo.length - 1);
  }

  getPdfParteDePagina(pageNum: number): PdfParteInfo | null {
    return this.pdfPartesInfo.find(parte => pageNum >= parte.paginaInicio && pageNum <= parte.paginaFin) || null;
  }

  scrollAPdfParte(parte: PdfParteInfo): void {
    if (!this.isBrowser || !parte) return;

    const pageElement = document.querySelector(`[data-page="${parte.paginaInicio}"]`) as HTMLElement | null;
    pageElement?.scrollIntoView({ behavior: 'smooth', block: 'start', inline: 'nearest' });
    this.actualizarSeccionActivaDesdePagina(parte.paginaInicio);
  }

  private actualizarSeccionActivaDesdePagina(pageNum: number): void {
    const parte = this.getPdfParteDePagina(pageNum);
    if (!parte) return;

    this.paginaPDFActiva = pageNum;
    this.seccionPDFActiva = parte;

    document.querySelectorAll('.pdf-page-container.active-pdf-section')
      .forEach(el => el.classList.remove('active-pdf-section'));

    const pageElement = document.querySelector(`[data-page-global="${pageNum}"]`) as HTMLElement | null;
    pageElement?.classList.add('active-pdf-section');
  }

  private observarSeccionPDFActiva(): void {
    if (!this.isBrowser) return;

    if (this.pdfScrollObserver) {
      this.pdfScrollObserver.disconnect();
      this.pdfScrollObserver = null;
    }

    const pageElements = Array.from(document.querySelectorAll('.pdf-page-container[data-page-global]')) as HTMLElement[];
    if (pageElements.length === 0) return;

    const root = document.querySelector('.pdf-viewer-wrapper') as HTMLElement | null;

    this.pdfScrollObserver = new IntersectionObserver((entries) => {
      const visibles = entries
        .filter(entry => entry.isIntersecting)
        .sort((a, b) => {
          const aTop = Math.abs(a.boundingClientRect.top - (root?.getBoundingClientRect().top || 0));
          const bTop = Math.abs(b.boundingClientRect.top - (root?.getBoundingClientRect().top || 0));
          return aTop - bTop;
        });

      const visible = visibles[0];
      if (!visible) return;

      const pageNum = Number((visible.target as HTMLElement).getAttribute('data-page-global') || 0);
      if (!pageNum) return;

      this.ngZone.run(() => this.actualizarSeccionActivaDesdePagina(pageNum));
    }, {
      root,
      threshold: [0.12, 0.25, 0.5, 0.75],
      rootMargin: '-12% 0px -55% 0px'
    });

    pageElements.forEach(page => this.pdfScrollObserver?.observe(page));
    this.actualizarSeccionActivaDesdePagina(this.paginaPDFActiva || 1);
  }

  private construirHeaderPaginaPDF(
    pageHeader: HTMLElement,
    parteInfo: PdfParteInfo | null,
    pageNumGlobal: number,
    pageNumDentroParte: number
  ): void {
    pageHeader.textContent = '';

    const badge = document.createElement('span');
    badge.className = 'pdf-section-badge';
    badge.textContent = parteInfo?.etiqueta || 'O';

    const title = document.createElement('span');
    title.className = 'pdf-page-title';
    title.textContent = `PÁGINA ${pageNumGlobal}`;

    const section = document.createElement('span');
    section.className = 'pdf-page-section-name';
    section.textContent = parteInfo
      ? `${parteInfo.tipo === 'ORIGINAL' ? 'Original' : 'Anexo'} · ${pageNumDentroParte}/${parteInfo.paginas}`
      : 'Original';

    pageHeader.appendChild(badge);
    pageHeader.appendChild(title);
    pageHeader.appendChild(section);
  }

  private eliminarYReordenarVariablesPorAnexo(paginaInicio: number, paginaFin: number, paginasEliminadas: number): void {
    const nuevasVariablesPorPagina: Map<number, VariablePosicionada[]> = new Map();

    this.variables.forEach(variable => {
      const ubicacionesActualizadas = variable.ubicaciones
        .filter(ubicacion => ubicacion.pagina < paginaInicio || ubicacion.pagina > paginaFin)
        .map(ubicacion => ({
          ...ubicacion,
          pagina: ubicacion.pagina > paginaFin ? ubicacion.pagina - paginasEliminadas : ubicacion.pagina
        }));

      variable.ubicaciones = ubicacionesActualizadas;
      variable.colocada = ubicacionesActualizadas.length > 0;

      if (ubicacionesActualizadas.length > 0) {
        const ultima = ubicacionesActualizadas[ubicacionesActualizadas.length - 1];
        variable.pagina = ultima.pagina;
        variable.posX = ultima.posX;
        variable.posY = ultima.posY;
      } else {
        variable.pagina = 1;
        variable.posX = 0;
        variable.posY = 0;
      }
    });

    this.variablesPorPagina.forEach((variables, pagina) => {
      if (pagina >= paginaInicio && pagina <= paginaFin) return;

      const nuevaPagina = pagina > paginaFin ? pagina - paginasEliminadas : pagina;
      const variablesActualizadas = variables.map(variable => ({ ...variable }));
      nuevasVariablesPorPagina.set(nuevaPagina, [
        ...(nuevasVariablesPorPagina.get(nuevaPagina) || []),
        ...variablesActualizadas
      ]);
    });

    this.variablesPorPagina = nuevasVariablesPorPagina;

    if (this.variableSeleccionadaParaPropiedades) {
      const paginaSeleccionada = this.variableSeleccionadaParaPropiedades.pagina;

      if (paginaSeleccionada >= paginaInicio && paginaSeleccionada <= paginaFin) {
        this.variableSeleccionadaParaPropiedades = null;
      } else if (paginaSeleccionada > paginaFin) {
        this.variableSeleccionadaParaPropiedades = {
          ...this.variableSeleccionadaParaPropiedades,
          pagina: paginaSeleccionada - paginasEliminadas
        };
      }
    }
  }

  async eliminarAnexoPDF(parte: PdfParteInfo, event?: Event): Promise<void> {
    if (event) {
      event.preventDefault();
      event.stopPropagation();
    }

    if (!parte || parte.tipo !== 'ANEXO' || parte.indice <= 0) {
      alert('Solo se pueden eliminar anexos. El PDF original no se puede eliminar desde esta acción.');
      return;
    }

    const confirmar = confirm(
      `¿Eliminar el anexo ${parte.etiqueta}?\n\n` +
      `${parte.nombreArchivo}\n` +
      `Páginas ${parte.paginaInicio} a ${parte.paginaFin}.\n\n` +
      `También se quitarán las variables colocadas dentro de esas páginas.`
    );

    if (!confirmar) return;

    this.isLoading = true;

    try {
      const paginasEliminadas = parte.paginaFin - parte.paginaInicio + 1;

      this.pdfBuffers.splice(parte.indice, 1);
      this.pdfFiles.splice(parte.indice, 1);
      this.pdfDocuments.splice(parte.indice, 1);

      this.eliminarYReordenarVariablesPorAnexo(parte.paginaInicio, parte.paginaFin, paginasEliminadas);
      this.recalcularTotalPagesAcumuladas();
      this.seccionPDFActiva = null;
      this.recalcularPdfPartesInfo();

      await this.renderizarTodasLasPaginas();

      this.haycambiosPendientes = true;
    } catch (error) {
      console.error('Error al eliminar anexo:', error);
      this.errorMessage = 'No se pudo eliminar el anexo del PDF.';
    } finally {
      this.isLoading = false;
    }
  }

  async anexarPDFDirecto(): Promise<void> {
    if (!this.isBrowser) return;

    this.ngZone.runOutsideAngular(async () => {
      try {
        const pdfjsLib = (window as any)['pdfjs-dist/build/pdf'] || (window as any).pdfjsLib;

        if (!pdfjsLib) {
          console.error('PDF.js no está disponible');
          this.ngZone.run(() => {
            this.errorMessage = 'Error al cargar la librería PDF.js';
            this.isLoading = false;
          });
          return;
        }

        const ultimoBuffer = this.pdfBuffers[this.pdfBuffers.length - 1];
        const loadingTask = pdfjsLib.getDocument({ data: ultimoBuffer.slice(0) });
        const pdfDoc = await loadingTask.promise;

        console.log(`✅ PDF anexado cargado - ${pdfDoc.numPages} páginas`);

        this.pdfDocuments.push(pdfDoc);
        this.recalcularTotalPagesAcumuladas();
        this.recalcularPdfPartesInfo();

        await this.renderizarTodasLasPaginas();

        this.ngZone.run(() => {
          this.isLoading = false;
          this.haycambiosPendientes = true;
          console.log('✅ PDF anexado renderizado correctamente');
        });

      } catch (error) {
        console.error('Error al anexar PDF:', error);
        this.ngZone.run(() => {
          this.errorMessage = 'Error al anexar el PDF. Verifique que el archivo sea válido.';
          this.isLoading = false;
        });
      }
    });
  }

  async renderizarTodasLasPaginas(): Promise<void> {
    if (!this.isBrowser) return;

    const pagesContainer = document.getElementById('pdf-pages');
    if (!pagesContainer) {
      console.error('❌ No se encontró #pdf-pages');
      return;
    }

    pagesContainer.innerHTML = '';
    this.pdfPages = [];

    this.recalcularTotalPagesAcumuladas();
    this.recalcularPdfPartesInfo();

    const containerWidth = pagesContainer.clientWidth || 800;
    const pixelRatio = window.devicePixelRatio || 1;

    console.log(`📄 Renderizando ${this.pdfDocuments.length} documentos...`);

    for (let docIndex = 0; docIndex < this.pdfDocuments.length; docIndex++) {
      const pdfDoc = this.pdfDocuments[docIndex];
      const paginasAnteriores = docIndex > 0 ? this.totalPagesAcumuladas[docIndex - 1] : 0;
      const parteInfo = this.pdfPartesInfo[docIndex] || null;

      for (let pageNum = 1; pageNum <= pdfDoc.numPages; pageNum++) {
        try {
          const pageNumGlobal = paginasAnteriores + pageNum;
          const page = await pdfDoc.getPage(pageNum);

          const nativeViewport = page.getViewport({ scale: 1.0 });

          const nativeWidth = nativeViewport.width;
          const nativeHeight = nativeViewport.height;

          const baseScale = (containerWidth * 0.9) / nativeWidth;
          const visualScale = baseScale * this.PDF_DISPLAY_MULTIPLIER * this.zoomPDF;

          const renderViewport = page.getViewport({
            scale: visualScale * pixelRatio
          });

          const displayWidth = nativeWidth * visualScale;
          const displayHeight = nativeHeight * visualScale;

          const pageDiv = document.createElement('div');
          pageDiv.className = `pdf-page-container ${docIndex === 0 ? 'pdf-original-page' : 'pdf-anexo-page'}`;
          pageDiv.setAttribute('data-page-global', pageNumGlobal.toString());
          pageDiv.setAttribute('data-pdf-part-index', docIndex.toString());
          pageDiv.setAttribute('data-pdf-section', parteInfo?.etiqueta || 'O');
          pageDiv.style.setProperty('--pdf-part-color', parteInfo?.color || this.PDF_ORIGINAL_COLOR);

          const pageMarker = document.createElement('div');
          pageMarker.className = 'pdf-page-section-marker';
          pageMarker.textContent = parteInfo?.etiqueta || 'O';

          const pageHeader = document.createElement('div');
          pageHeader.className = 'pdf-page-header';
          this.construirHeaderPaginaPDF(pageHeader, parteInfo, pageNumGlobal, pageNum);

          const pageContentDiv = document.createElement('div');
          pageContentDiv.className = 'pdf-page';
          pageContentDiv.setAttribute('data-page', pageNumGlobal.toString());
          pageContentDiv.setAttribute('data-pdf-section', parteInfo?.etiqueta || 'O');
          pageContentDiv.setAttribute('data-pdf-part-index', docIndex.toString());

          // ✅ Datos por página. No dependemos de this.pdfNativeWidth global.
          pageContentDiv.setAttribute('data-native-width', nativeWidth.toString());
          pageContentDiv.setAttribute('data-native-height', nativeHeight.toString());
          pageContentDiv.setAttribute('data-visual-scale', visualScale.toString());

          pageContentDiv.style.width = `${displayWidth}px`;
          pageContentDiv.style.height = `${displayHeight}px`;

          const canvas = document.createElement('canvas');
          canvas.className = 'pdf-canvas';

          canvas.width = renderViewport.width;
          canvas.height = renderViewport.height;

          canvas.style.width = `${displayWidth}px`;
          canvas.style.height = `${displayHeight}px`;

          const context = canvas.getContext('2d', {
            alpha: false,
            willReadFrequently: true
          });

          if (!context) continue;

          await page.render({
            canvasContext: context,
            viewport: renderViewport,
            renderInteractiveForms: true
          }).promise;

          const pageFooter = document.createElement('div');
          pageFooter.className = 'pdf-page-footer';
          pageFooter.textContent = `${parteInfo?.etiqueta || 'O'} · ${parteInfo?.tipo === 'ANEXO' ? 'Anexo' : 'Original'} · Haga clic para posicionar variables | Arrastre para mover`;

          pageContentDiv.appendChild(canvas);
          pageDiv.appendChild(pageMarker);
          pageDiv.appendChild(pageHeader);
          pageDiv.appendChild(pageContentDiv);
          pageDiv.appendChild(pageFooter);

          pagesContainer.appendChild(pageDiv);

          this.pdfPages.push({
            pageNumber: pageNumGlobal,
            nativeWidth,
            nativeHeight,
            canvas,
            viewport: renderViewport,
            container: pageContentDiv,
            pdfPartIndex: docIndex,
            pdfPartLabel: parteInfo?.etiqueta || 'O'
          });

          console.log(`✅ Página ${pageNumGlobal} renderizada`, {
            parte: parteInfo?.etiqueta || 'O',
            nativeWidth,
            nativeHeight,
            displayWidth,
            displayHeight,
            visualScale
          });

        } catch (error) {
          console.error(`Error al renderizar página ${pageNum} del documento ${docIndex + 1}:`, error);
        }
      }
    }

    if (this.pdfPages.length > 0) {
      this.pdfNativeWidth = this.pdfPages[0].nativeWidth;
      this.pdfNativeHeight = this.pdfPages[0].nativeHeight;
    }

    await new Promise(resolve => setTimeout(resolve, 100));

    this.ngZone.run(() => {
      setTimeout(() => {
        this.redibujarTodasLasVariables();
        this.actualizarEstadoVisualPDF();
        this.observarSeccionPDFActiva();
        console.log(`✅ ${this.pdfPages.length} páginas totales renderizadas`);
      }, 150);
    });
  }

  /**
   * Redibujar todas las variables en todas las páginas
   */
  redibujarTodasLasVariables(): void {
    console.log('🔄 Redibujando todas las variables...');

    this.variablesPorPagina.forEach((variables, pageNum) => {
      const pageElement = document.querySelector(`[data-page="${pageNum}"]`) as HTMLElement;

      if (pageElement) {
        pageElement.querySelectorAll('.pdf-variable').forEach(el => el.remove());

        variables.forEach(variable => {
          this.mostrarVariableEnPdf(variable, pageElement);
        });

        console.log(`✅ Página ${pageNum} redibujada con ${variables.length} variables`);
      } else {
        console.warn(`⚠️ No se encontró el elemento de página ${pageNum}`);
      }
    });

    console.log('✅ Todas las variables redibujadas');
  }

  /**
   * Seleccionar un documento existente de la lista
   */
  seleccionarDocumentoExistente(documento: any): void {
    console.log('📂 Seleccionando documento:', documento.nombre);

    this.documentoSeleccionado = documento;
    this.documentoGuardadoId = documento.id;

    this.isLoading = true;
    this.apiService.get(`api_documento_nativo/${documento.id}/`)
      .subscribe({
        next: (response: any) => {
          console.log('📦 Respuesta del backend:', response);

          this.documentoSeleccionado = response;
          this.tipoContrato = response.tipo || 'CHILENO';

          if (response.variables && Array.isArray(response.variables)) {
            console.log(`📋 Cargando ${response.variables.length} variables desde el backend...`);
            this.cargarVariablesDesdeDocumento(response.variables);

            console.log('🗂️ Variables en memoria después de cargar:', {
              totalVariablesColocadas: this.variables.filter(v => v.colocada).length,
              variablesPorPagina: Array.from(this.variablesPorPagina.entries()).map(([pagina, vars]) => ({
                pagina,
                cantidad: vars.length,
                variables: vars.map(v => ({ nombre: v.nombre, posX: v.posX, posY: v.posY }))
              }))
            });
          }

          this.cargarPDFDesdeURL(response.archivo_pdf_url);

          this.isLoading = false;
        },
        error: (error) => {
          console.error('Error al cargar detalles del documento:', error);
          this.errorMessage = 'No se pudo cargar el documento seleccionado.';
          this.isLoading = false;
        }
      });
  }

  /**
   * Carga las variables desde un documento existente
   */
  cargarVariablesDesdeDocumento(variablesDocumento: any[]): void {
    if (!variablesDocumento || variablesDocumento.length === 0) return;

    this.resetearVariables();

    variablesDocumento.forEach(varDoc => {
      if (varDoc?.nombre === this.TEXTOS_LIBRES_CONTAINER) {
        this.cargarTextosLibresDesdeDocumento(varDoc);
        return;
      }

      const varIndex = this.variables.findIndex(v => v.nombre === varDoc.nombre);

      if (varIndex < 0) return;

      const ubicaciones = Array.isArray(varDoc.ubicaciones)
        ? varDoc.ubicaciones.map((u: any) => ({
          id: u.id || `var-${varDoc.nombre}-${Date.now()}-${Math.random().toString(36).slice(2)}`,
          pagina: Number(u.pagina || 1),
          posX: Number(u.posX || 0),
          posY: Number(u.posY || 0),
          width: u.width !== undefined ? Number(u.width) : undefined,
          height: u.height !== undefined ? Number(u.height) : undefined,
          valor: u.valor
        }))
        : [];

      this.variables[varIndex].colocada = ubicaciones.length > 0;
      this.variables[varIndex].ubicaciones = ubicaciones;

      if (ubicaciones.length > 0) {
        const ultima = ubicaciones[ubicaciones.length - 1];
        this.variables[varIndex].posX = ultima.posX;
        this.variables[varIndex].posY = ultima.posY;
        this.variables[varIndex].pagina = ultima.pagina;
      }

      ubicaciones.forEach((ubicacion: any) => {
        if (!this.variablesPorPagina.has(ubicacion.pagina)) {
          this.variablesPorPagina.set(ubicacion.pagina, []);
        }

        this.variablesPorPagina.get(ubicacion.pagina)?.push({
          nombre: varDoc.nombre,
          posX: ubicacion.posX,
          posY: ubicacion.posY,
          elementId: ubicacion.id,
          variableIndex: varIndex
        });
      });
    });
  }

  cargarTextosLibresDesdeDocumento(varDoc: any): void {
    const varIndex = this.variables.findIndex(v => v.nombre === this.TEXTO_LIBRE_VARIABLE);
    if (varIndex < 0) return;

    const textosLibres = Array.isArray(varDoc?.textos_libres) ? varDoc.textos_libres : [];
    const ubicaciones = textosLibres
      .filter((textoLibre: any) => textoLibre && typeof textoLibre === 'object')
      .map((textoLibre: any) => ({
        id: textoLibre.id || `texto_libre_${Date.now()}_${Math.random().toString(36).slice(2)}`,
        pagina: Number(textoLibre.pagina || 1),
        posX: Number(textoLibre.posX ?? textoLibre.x ?? 0),
        posY: Number(textoLibre.posY ?? textoLibre.y ?? 0),
        pageWidth: Number(textoLibre.pageWidth || this.pdfNativeWidth || 0),
        pageHeight: Number(textoLibre.pageHeight || this.pdfNativeHeight || 0),
        width: textoLibre.width !== undefined ? Number(textoLibre.width) : undefined,
        height: textoLibre.height !== undefined ? Number(textoLibre.height) : undefined,
        valor: textoLibre.texto || '',
        fontSize: textoLibre.fontSize !== undefined ? Number(textoLibre.fontSize) : 10
      }));

    this.variables[varIndex].colocada = ubicaciones.length > 0;
    this.variables[varIndex].ubicaciones = ubicaciones;

    if (ubicaciones.length > 0) {
      const ultima = ubicaciones[ubicaciones.length - 1];
      this.variables[varIndex].posX = ultima.posX;
      this.variables[varIndex].posY = ultima.posY;
      this.variables[varIndex].pagina = ultima.pagina;
    }

    ubicaciones.forEach((ubicacion: Ubicacion) => {
      if (!this.variablesPorPagina.has(ubicacion.pagina)) {
        this.variablesPorPagina.set(ubicacion.pagina, []);
      }

      this.variablesPorPagina.get(ubicacion.pagina)?.push({
        nombre: this.TEXTO_LIBRE_VARIABLE,
        posX: ubicacion.posX,
        posY: ubicacion.posY,
        elementId: ubicacion.id,
        variableIndex: varIndex
      });
    });
  }

  private _serializarVariablesParaBackend(): any[] {
    const textoLibreVar = this.variables.find(
      v => v.nombre === this.TEXTO_LIBRE_VARIABLE && v.ubicaciones.length > 0
    );

    const variablesNormales: any[] = this.variables
      .filter(v => v.ubicaciones.length > 0 && v.nombre !== this.TEXTO_LIBRE_VARIABLE)
      .map(v => ({ nombre: v.nombre, ubicaciones: v.ubicaciones }));

    if (textoLibreVar && textoLibreVar.ubicaciones.length > 0) {
      const textosLibres = textoLibreVar.ubicaciones.map(u => ({
        id: u.id,
        texto: u.valor || '',
        pagina: u.pagina,
        posX: u.posX,
        posY: u.posY,
        pageWidth: u.pageWidth,
        pageHeight: u.pageHeight,
        width: u.width ?? undefined,
        height: u.height ?? undefined,
        fontSize: u.fontSize ?? undefined,
      }));
      variablesNormales.push({
        nombre: this.TEXTOS_LIBRES_CONTAINER,
        textos_libres: textosLibres
      });
    }

    return variablesNormales;
  }

  private normalizarUrlPdf(pdfUrl: string): string {
    if (!pdfUrl) return '';

    const PRODUCCION_BASE_URL = 'https://contratista.terramobile.cl';

    const protocoloActual = window.location.protocol;
    const hostActual = window.location.hostname;

    const esLocal =
      hostActual === 'localhost' ||
      hostActual === '127.0.0.1' ||
      hostActual === '0.0.0.0';

    // Caso 1: URL relativa, ejemplo: /media/contracts/formats/archivo.pdf
    if (pdfUrl.startsWith('/')) {
      // En localhost, si los PDFs están en el servidor productivo,
      // usar la URL real del backend.
      if (esLocal) {
        return `${PRODUCCION_BASE_URL}${pdfUrl}`;
      }

      // En producción, usar el mismo dominio actual.
      return `${window.location.origin}${pdfUrl}`;
    }

    try {
      const url = new URL(pdfUrl);

      // Caso 2: estamos en localhost
      if (esLocal) {
        // Si el backend devuelve http://contratista.terramobile.cl,
        // lo forzamos a https.
        if (
          url.hostname === 'contratista.terramobile.cl' &&
          url.protocol === 'http:'
        ) {
          url.protocol = 'https:';
        }

        return url.toString();
      }

      // Caso 3: producción con HTTPS.
      // Evita mixed content si el backend devuelve http.
      if (protocoloActual === 'https:' && url.protocol === 'http:') {
        url.protocol = 'https:';
      }

      return url.toString();

    } catch {
      return pdfUrl;
    }
  }

  /**
   * Carga el PDF desde una URL e inicializa dimensiones SIEMPRE
   */
  cargarPDFDesdeURL(pdfUrl: string): void {
    if (!pdfUrl) {
      this.errorMessage = 'No se encontró la URL del PDF';
      return;
    }

    pdfUrl = this.normalizarUrlPdf(pdfUrl);

    console.log('PDF URL:', pdfUrl);

    this.isLoading = true;

    fetch(pdfUrl)
      .then(response => {
        if (!response.ok) {
          throw new Error(`Error HTTP: ${response.status}`);
        }
        return response.arrayBuffer();
      })
      .then(async arrayBuffer => {
        const bufferParaDimensiones = arrayBuffer.slice(0);
        const bufferParaRender = arrayBuffer.slice(0);

        this.pdfSrc = bufferParaRender;

        await this.inicializarDimensionesPDF(bufferParaDimensiones);

        if (!this.modoDocumentoExistente || this.modoModificacion) {
          this.renderPdf().then(() => {
            if (this.modoModificacion) {
              console.log('PDF renderizado, actualizando interfaz de modificación...');
              this.actualizarInterfazModoModificacion();
            }
          });
        } else {
          this.isLoading = false;
          console.log('✅ Documento existente cargado con dimensiones inicializadas');
        }
      })
      .catch(error => {
        console.error('Error al cargar el PDF:', error);
        this.errorMessage = `Error al cargar el PDF del documento: ${error.message}`;
        this.isLoading = false;
      });
  }

  eliminarFormatoDocumento(documento: any, event?: MouseEvent): void {
    if (event) {
      event.preventDefault();
      event.stopPropagation();
    }

    if (!documento?.id) {
      alert('No se pudo identificar el formato a eliminar.');
      return;
    }

    const documentoId = Number(documento.id);

    if (this.documentosEliminandoIds.has(documentoId)) {
      return;
    }

    const confirmar = confirm(
      `¿Está seguro de eliminar el formato "${documento.nombre}"?\n\n` +
      `También se eliminará el PDF asociado.\n\n` +
      `Esta acción no se puede deshacer.`
    );

    if (!confirmar) return;

    this.documentosEliminandoIds.add(documentoId);
    this.isLoading = true;

    this.apiService.delete(`api_documento_nativo/${documentoId}/`, {})
      .subscribe({
        next: (response: any) => {
          console.log('Formato eliminado:', response);

          this.limpiarFormatoEliminadoDeInterfaz(documentoId);

          this.documentosEliminandoIds.delete(documentoId);
          this.isLoading = false;

          alert(response?.mensaje || 'Formato eliminado exitosamente.');
        },
        error: (error) => {
          console.error('Error al eliminar formato:', error);

          /*
            Si el backend responde 404/410, significa que el formato ya no existe.
            Para la interfaz eso debe tratarse como eliminado, no como error visual.
          */
          if (error?.status === 404 || error?.status === 410) {
            this.limpiarFormatoEliminadoDeInterfaz(documentoId);

            this.documentosEliminandoIds.delete(documentoId);
            this.isLoading = false;

            alert('El formato ya no existía en el servidor. Se quitó de la lista.');
            return;
          }

          this.documentosEliminandoIds.delete(documentoId);
          this.isLoading = false;

          alert(
            error?.error?.error ||
            error?.error?.detalle ||
            'No se pudo eliminar el formato.'
          );
        }
      });
  }

  iniciarEdicionNombreDocumento(documento: any, event: Event): void {
    event.preventDefault();
    event.stopPropagation();

    this.documentoEditandoNombreId = documento?.id || null;
    this.nombreDocumentoEditado = documento?.nombre || '';

    setTimeout(() => {
      const input = document.getElementById(`documento-nombre-input-${documento.id}`) as HTMLInputElement | null;
      input?.focus();
      input?.select();
    }, 0);
  }

  cancelarEdicionNombreDocumento(event: Event): void {
    event.preventDefault();
    event.stopPropagation();

    this.documentoEditandoNombreId = null;
    this.nombreDocumentoEditado = '';
  }

  guardarNombreDocumento(documento: any, event: Event): void {
    event.preventDefault();
    event.stopPropagation();

    const nuevoNombre = this.nombreDocumentoEditado.trim();

    if (!nuevoNombre) {
      alert('El nombre del formato no puede estar vacío.');
      return;
    }

    if (nuevoNombre === documento.nombre) {
      this.documentoEditandoNombreId = null;
      this.nombreDocumentoEditado = '';
      return;
    }

    this.isLoading = true;

    this.apiService.patch(`api_documento_nativo/${documento.id}/`, { nombre: nuevoNombre })
      .subscribe({
        next: (response: any) => {
          const nombreActualizado = response?.nombre || nuevoNombre;

          documento.nombre = nombreActualizado;

          const docEnLista = this.documentosCargados.find((doc: any) => doc.id === documento.id);
          if (docEnLista) {
            docEnLista.nombre = nombreActualizado;
          }

          if (this.documentoSeleccionado?.id === documento.id) {
            this.documentoSeleccionado.nombre = nombreActualizado;
          }

          this.documentoEditandoNombreId = null;
          this.nombreDocumentoEditado = '';
          this.recalcularDocumentosExistentes();
          this.isLoading = false;
        },
        error: (error) => {
          console.error('Error al actualizar nombre del formato:', error);
          this.isLoading = false;
          alert(error?.error?.error || 'No se pudo actualizar el nombre del formato.');
        }
      });
  }


  onDocumentoItemClick(doc: any): void {
    if (this.documentoEditandoNombreId !== null) return;
    this.seleccionarDocumentoExistente(doc);
  }
  /**
   * Obtener el número de variables colocadas en el documento
   */
  getNumeroVariables(): number {
    return this.variables.filter(v => v.colocada).length;
  }

  onFileSelected(event: Event, esAnexo: boolean = false): void {
    if (!this.isBrowser) return;

    const input = event.target as HTMLInputElement;

    if (input.files && input.files[0]) {
      const file = input.files[0];
      console.log('File selected:', file.name, 'size:', file.size, 'bytes', 'Es anexo:', esAnexo);

      if (file.type !== 'application/pdf') {
        alert('Solo se permiten archivos PDF.');
        input.value = '';
        return;
      }

      if (esAnexo && !this.pdfSrc) {
        alert('Primero debes seleccionar el PDF original.');
        input.value = '';
        return;
      }

      this.isLoading = true;
      this.errorMessage = null;

      const reader = new FileReader();
      reader.onload = () => {
        const originalBuffer = reader.result as ArrayBuffer;

        if (!esAnexo) {
          this.originalPdfFile = file;
          this.pdfSrc = originalBuffer.slice(0);
          this.pdfBuffers = [originalBuffer.slice(0)];
          this.pdfFiles = [file];
          this.pdfDocuments = [];
          this.pdfPartesInfo = [];
          this.seccionPDFActiva = null;
          this.paginaPDFActiva = 1;
          this.totalPagesAcumuladas = [];
          this.totalPages = 0;
          this.pdfPages = [];

          this.mostrarModalTipoContrato = true;
        } else {
          this.pdfBuffers.push(originalBuffer.slice(0));
          this.pdfFiles.push(file);
          this.anexarPDFDirecto();
        }

        input.value = '';
      };
      reader.onerror = (error) => {
        console.error('Error al leer el archivo:', error);
        this.isLoading = false;
        this.errorMessage = 'Error al leer el archivo PDF.';
        input.value = '';
      };
      reader.readAsArrayBuffer(file);
    }
  }

  seleccionarVariable(variable: VariableDocumento): void {
    if (variable.nombre === 'timbre_empleador' && !this.timbreEmpleadorDisponible) {
      alert('Debes subir el timbre del empleador antes de colocarlo en el formato.');
      return;
    }

    if (variable.nombre === 'cantidad_seguridad') {
      alert('La cantidad se posiciona automáticamente después de posicionar un elemento de seguridad.');
      return;
    }

    if (variable.nombre === 'elemento_seguridad') {
      if (this.elementosSeguridad.length === 0) {
        alert('No hay elementos de seguridad configurados para este holding');
        return;
      }

      this.variableSeleccionada = variable;
      this.elementoSeleccionadoTemp = this.elementosSeguridad[0];
      this.mostrarModalElementoSeguridad = true;
      return;
    }

    if (variable.nombre === this.TEXTO_LIBRE_VARIABLE) {
      this.textoLibreTemp = '';
      this.mostrarModalTextoLibre = true;
      return;
    }

    this.iniciarColocacionVariable(variable);
  }

  cancelarTextoLibre(): void {
    this.mostrarModalTextoLibre = false;
    this.textoLibreTemp = '';
    this.textoLibrePendiente = '';
    this.variableSeleccionada = null;
    this.modoColocacion = false;

    const pdfContainer = document.getElementById('pdf-container');
    if (pdfContainer) {
      pdfContainer.style.cursor = 'default';
    }
  }

  confirmarTextoLibre(): void {
    const texto = this.textoLibreTemp.trim();
    if (!texto) {
      alert('No se puede guardar el formato porque existe un texto libre vacío.');
      return;
    }
    if (texto.length > 200) {
      alert('El texto libre no puede superar los 200 caracteres.');
      return;
    }

    const variableTextoLibre = this.variables.find(v => v.nombre === this.TEXTO_LIBRE_VARIABLE);
    if (!variableTextoLibre) {
      alert('No existe la variable texto_libre');
      return;
    }

    this.textoLibrePendiente = texto;
    this.mostrarModalTextoLibre = false;
    this.iniciarColocacionVariable(variableTextoLibre);
  }

  /**
   * Calcular coordenadas nativas de la página clickeada.
   *
   * Convención única del editor:
   * - posX y posY representan la esquina superior izquierda visual del texto/imagen.
   * - El backend convierte esa misma posición a punto de escritura sin aplicar offsets mágicos.
   * - Las dimensiones se toman desde la página real, no desde una variable global del PDF.
   */
  calcularCoordenadasNativas(pageElement: HTMLElement, clientX: number, clientY: number): { posX: number, posY: number } {
    const pageRect = pageElement.getBoundingClientRect();
    const { nativeWidth, nativeHeight } = this.obtenerDimensionesNativasPagina(pageElement);

    const pixelX = Math.max(0, Math.min(clientX - pageRect.left, pageRect.width));
    const pixelY = Math.max(0, Math.min(clientY - pageRect.top, pageRect.height));

    const scaleX = nativeWidth / pageRect.width;
    const scaleY = nativeHeight / pageRect.height;

    const nativeX = pixelX * scaleX;
    const nativeY = pixelY * scaleY;

    console.log('📍 Coordenadas nativas por página:', {
      pagina: pageElement.getAttribute('data-page'),
      pixel: { x: pixelX, y: pixelY },
      nativas: { x: nativeX, y: nativeY },
      escala: { scaleX, scaleY },
      dimensiones: { nativeWidth, nativeHeight }
    });

    return {
      posX: nativeX,
      posY: nativeY
    };
  }

  obtenerDimensionesNativasPagina(pageElement: HTMLElement): { nativeWidth: number; nativeHeight: number } {
    const nativeWidth = Number(pageElement.getAttribute('data-native-width')) || this.pdfNativeWidth || pageElement.offsetWidth;
    const nativeHeight = Number(pageElement.getAttribute('data-native-height')) || this.pdfNativeHeight || pageElement.offsetHeight;
    return { nativeWidth, nativeHeight };
  }

  obtenerEscalaPagina(pageElement: HTMLElement): { scaleX: number; scaleY: number } {
    const visualScale = Number(pageElement.getAttribute('data-visual-scale'));

    if (visualScale && isFinite(visualScale) && visualScale > 0) {
      return {
        scaleX: visualScale,
        scaleY: visualScale
      };
    }

    const { nativeWidth, nativeHeight } = this.obtenerDimensionesNativasPagina(pageElement);
    const pageRect = pageElement.getBoundingClientRect();

    return {
      scaleX: pageRect.width / nativeWidth,
      scaleY: pageRect.height / nativeHeight
    };
  }

  private convertirPtAPx(fontSizePt: number, pageElement: HTMLElement): number {
    const { scaleY } = this.obtenerEscalaPagina(pageElement);
    return fontSizePt * scaleY;
  }

  private obtenerTopTextoDesdeBaselinePx(baselineYPx: number, fontSizePx: number): number {
    return baselineYPx - (fontSizePx * this.PDF_TEXT_ASCENT_RATIO);
  }

  private obtenerBaselineNativoDesdeTopPx(topPx: number, fontSizePt: number, pageElement: HTMLElement): number {
    const { scaleY } = this.obtenerEscalaPagina(pageElement);
    const topNativo = topPx / scaleY;
    return topNativo + (fontSizePt * this.PDF_TEXT_ASCENT_RATIO);
  }

  private esVariableTexto(nombre: string): boolean {
    return !this.esVariableImagen(nombre);
  }

  private actualizarEstadoVisualPDF(): void {
    const container = document.getElementById('pdf-container');
    if (!container) return;

    container.classList.toggle('vista-final-pdf', this.vistaFinalPDF);
    container.classList.toggle('debug-coordenadas-activo', this.mostrarDebugCoordenadas);
  }

  togglePanelVariables(): void {
    this.panelVariablesContraido = !this.panelVariablesContraido;
  }

  toggleControlesCargaPDF(): void {
    this.mostrarControlesCargaPDF = !this.mostrarControlesCargaPDF;
  }

  toggleVistaFinalPDF(): void {
    this.vistaFinalPDF = !this.vistaFinalPDF;
    this.actualizarEstadoVisualPDF();
  }

  toggleDebugCoordenadas(): void {
    this.mostrarDebugCoordenadas = !this.mostrarDebugCoordenadas;
    this.actualizarEstadoVisualPDF();
    this.redibujarTodasLasVariables();
  }

  async setZoomPDF(zoom: number): Promise<void> {
    this.zoomPDF = zoom;
    if (!this.pdfSrc || this.isLoading) return;
    this.isLoading = true;
    try {
      if (this.pdfDocuments.length > 1) {
        await this.renderizarTodasLasPaginas();
      } else {
        await this.renderPdf();
      }
      this.actualizarEstadoVisualPDF();
    } catch (error) {
      console.error('Error al aplicar zoom:', error);
    } finally {
      this.isLoading = false;
    }
  }

  private seleccionarVariableParaPropiedades(variable: VariablePosicionada): void {
    const pageNumber = this.obtenerPaginaVariable(variable.elementId);
    const ubicacion = this.variables[variable.variableIndex]?.ubicaciones.find(u => u.id === variable.elementId);

    this.variableSeleccionadaParaPropiedades = {
      nombre: variable.nombre,
      pagina: pageNumber,
      posX: ubicacion?.posX ?? variable.posX,
      posY: ubicacion?.posY ?? variable.posY,
      width: ubicacion?.width,
      height: ubicacion?.height,
      fontSize: ubicacion?.fontSize ?? this.PDF_TEXT_FONT_SIZE_PT,
      elementId: variable.elementId,
      variableIndex: variable.variableIndex,
    };
  }

  private obtenerPaginaVariable(elementId: string): number {
    let pagina = 0;
    this.variablesPorPagina.forEach((variables, pageNum) => {
      if (variables.some(v => v.elementId === elementId)) pagina = pageNum;
    });
    return pagina;
  }

  eliminarVariableSeleccionada(): void {
    if (!this.variableSeleccionadaParaPropiedades) return;
    this.eliminarVariable(
      this.variableSeleccionadaParaPropiedades.elementId,
      this.variableSeleccionadaParaPropiedades.variableIndex
    );
    this.variableSeleccionadaParaPropiedades = null;
  }

  private esVariableImagen(nombre: string): boolean {
    return this.IMAGE_VARIABLES.includes(nombre);
  }

  findClickedPage(event: MouseEvent): HTMLElement | null {
    const elements = document.elementsFromPoint(event.clientX, event.clientY);
    for (const element of elements) {
      if (element.classList.contains('pdf-page')) {
        return element as HTMLElement;
      }
    }
    return null;
  }

  handleVariableMouseDown(event: MouseEvent, variable: VariablePosicionada, element: HTMLElement, pageElement: HTMLElement): void {
    event.preventDefault();
    event.stopPropagation();

    const pageNumber = parseInt(pageElement.getAttribute('data-page') || '0');
    if (pageNumber <= 0) return;

    this.variableArrastrandose = variable;
    this.elementoArrastrandose = element;
    this.paginaActualArrastre = pageElement;
    this.paginaNumeroArrastre = pageNumber;

    const rect = element.getBoundingClientRect();
    this.offsetX = event.clientX - rect.left;
    this.offsetY = event.clientY - rect.top;

    element.classList.add('dragging');
    document.body.style.cursor = 'move';
  }

  handleMouseMove(event: MouseEvent): void {
    if (!this.variableArrastrandose || !this.elementoArrastrandose || !this.paginaActualArrastre) return;

    const pageRect = this.paginaActualArrastre.getBoundingClientRect();

    let newX = event.clientX - pageRect.left - this.offsetX;
    let newY = event.clientY - pageRect.top - this.offsetY;

    newX = Math.max(0, Math.min(newX, pageRect.width - this.elementoArrastrandose.offsetWidth));
    newY = Math.max(0, Math.min(newY, pageRect.height - this.elementoArrastrandose.offsetHeight));

    this.elementoArrastrandose.style.left = `${newX}px`;
    this.elementoArrastrandose.style.top = `${newY}px`;
  }

  handleMouseUp(event: MouseEvent): void {
    if (!this.variableArrastrandose || !this.elementoArrastrandose || !this.paginaActualArrastre) {
      return;
    }

    const finalX = parseFloat(this.elementoArrastrandose.style.left || '0');
    const finalTop = parseFloat(this.elementoArrastrandose.style.top || '0');

    const variablesList = this.variablesPorPagina.get(this.paginaNumeroArrastre) || [];
    const variableIndex = variablesList.findIndex(
      v => v.elementId === this.variableArrastrandose?.elementId
    );

    if (variableIndex !== -1) {
      const itemPagina = variablesList[variableIndex];
      const mainVarIndex = itemPagina.variableIndex;

      if (mainVarIndex >= 0 && mainVarIndex < this.variables.length) {
        const variable = this.variables[mainVarIndex];

        const ubicacionIndex = variable.ubicaciones.findIndex(
          u => u.id === this.variableArrastrandose?.elementId
        );

        if (ubicacionIndex !== -1) {
          const { scaleX, scaleY } = this.obtenerEscalaPagina(this.paginaActualArrastre);

          const nativeX = finalX / scaleX;

          let nativeY: number;

          if (this.esVariableImagen(variable.nombre)) {
            nativeY = finalTop / scaleY;
          } else {
            const fontSizePt =
              variable.ubicaciones[ubicacionIndex].fontSize ||
              this.PDF_TEXT_FONT_SIZE_PT;

            nativeY = this.obtenerBaselineNativoDesdeTopPx(
              finalTop,
              fontSizePt,
              this.paginaActualArrastre
            );
          }

          itemPagina.posX = nativeX;
          itemPagina.posY = nativeY;

          variable.ubicaciones[ubicacionIndex].posX = nativeX;
          variable.ubicaciones[ubicacionIndex].posY = nativeY;

          if (this.esVariableImagen(variable.nombre)) {
            const elementRect = this.elementoArrastrandose.getBoundingClientRect();

            const nativeWidth = elementRect.width / scaleX;
            const nativeHeight = elementRect.height / scaleY;

            variable.ubicaciones[ubicacionIndex].width = nativeWidth;
            variable.ubicaciones[ubicacionIndex].height = nativeHeight;
          }

          if (variable.ubicaciones.length > 0 && ubicacionIndex === variable.ubicaciones.length - 1) {
            variable.posX = nativeX;
            variable.posY = nativeY;
          }

          this.haycambiosPendientes = true;
          this.seleccionarVariableParaPropiedades(itemPagina);
        }
      }
    }

    this.elementoArrastrandose.classList.remove('dragging');
    document.body.style.cursor = 'auto';

    this.variableArrastrandose = null;
    this.elementoArrastrandose = null;
    this.paginaActualArrastre = null;
    this.paginaNumeroArrastre = 0;
  }

  resetearVariables(): void {
    this.variables.forEach(variable => {
      variable.posX = 0;
      variable.posY = 0;
      variable.pagina = 1;
      variable.colocada = false;
      variable.ubicaciones = [];
    });

    this.variablesPorPagina.clear();
    this.variableSeleccionadaParaPropiedades = null;

    document.querySelectorAll('.pdf-variable').forEach(el => el.remove());
    document.querySelectorAll('.debug-info').forEach(el => el.remove());
  }

  exportarPosiciones(): void {
    const posiciones: { variable: string; posicion: { x: number; y: number; pagina: number; }; }[] = [];

    this.variables.forEach(variable => {
      variable.ubicaciones.forEach(ubicacion => {
        posiciones.push({
          variable: variable.nombre,
          posicion: {
            x: ubicacion.posX,
            y: ubicacion.posY,
            pagina: ubicacion.pagina
          }
        });
      });
    });

    console.log('Posiciones de variables (coordenadas nativas):', JSON.stringify(posiciones, null, 2));
    this.descargarJSON(posiciones, 'posiciones_variables_nativas.json');
  }

  descargarJSON(data: any, filename: string): void {
    if (!this.isBrowser) return;

    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  async renderPdf(): Promise<void> {
    if (!this.isBrowser || !this.pdfSrc) {
      this.isLoading = false;
      return Promise.resolve();
    }

    return new Promise((resolve, reject) => {
      this.ngZone.runOutsideAngular(async () => {
        try {
          console.log('Iniciando renderizado de PDF...');

          if (!(window as any).pdfjsLib) {
            console.log('Cargando PDF.js desde CDN...');
            await this.loadPdfJsScript();
          }

          const pdfjsLib = (window as any).pdfjsLib;
          if (!pdfjsLib) {
            throw new Error('No se pudo cargar PDF.js');
          }

          const workerUrl = `https://cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjsLib.version}/pdf.worker.min.js`;
          pdfjsLib.GlobalWorkerOptions.workerSrc = workerUrl;

          const container = document.getElementById('pdf-container');
          if (!container) {
            throw new Error('No se encontró el contenedor #pdf-container');
          }

          container.innerHTML = '';

          if (this.pdfSrc === null) {
            throw new Error('No se ha cargado ningún PDF');
          }

          console.log('Cargando documento PDF...');

          const bufferForRender = (this.pdfSrc as ArrayBuffer).slice(0);

          const loadingTask = pdfjsLib.getDocument({
            data: bufferForRender,
            cMapUrl: 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.4.120/cmaps/',
            cMapPacked: true
          });

          const pdf = await loadingTask.promise;
          this.pdfDocument = pdf;
          this.pdfDocuments = [pdf];
          this.totalPagesAcumuladas = [pdf.numPages];
          this.totalPages = pdf.numPages;
          this.seccionPDFActiva = null;
          this.recalcularPdfPartesInfo();

          const firstPage = await pdf.getPage(1);
          const nativeViewport = firstPage.getViewport({ scale: 1.0 });
          this.pdfNativeWidth = nativeViewport.width;
          this.pdfNativeHeight = nativeViewport.height;

          console.log(`Dimensiones nativas del PDF: ${this.pdfNativeWidth} x ${this.pdfNativeHeight}`);

          const pagesContainer = document.createElement('div');
          pagesContainer.id = 'pdf-pages';
          pagesContainer.className = 'pdf-pages';
          container.appendChild(pagesContainer);

          await this.renderizarTodasLasPaginas();

          this.ngZone.run(() => {
            this.isLoading = false;
            resolve();
          });
        } catch (error) {
          console.error('Error al renderizar el PDF:', error);

          this.ngZone.run(() => {
            this.isLoading = false;
            this.errorMessage = `Error al renderizar el PDF: ${error instanceof Error ? error.message : 'Error desconocido'}`;
            reject(error);
          });
        }
      });
    });
  }

  private createPdfControls(container: HTMLElement, numPages: number): void {
    const controlsContainer = document.createElement('div');
    controlsContainer.className = 'pdf-controls';

    const prevButton = document.createElement('button');
    prevButton.textContent = 'Anterior';
    prevButton.className = 'pdf-control-btn prev-btn';
    prevButton.disabled = true;

    const pageInfo = document.createElement('span');
    pageInfo.className = 'page-info';
    pageInfo.textContent = `Página 1-3 de ${numPages}`;

    const nextButton = document.createElement('button');
    nextButton.textContent = 'Siguiente';
    nextButton.className = 'pdf-control-btn next-btn';
    nextButton.disabled = numPages <= 3;

    controlsContainer.appendChild(prevButton);
    controlsContainer.appendChild(pageInfo);
    controlsContainer.appendChild(nextButton);

    const pagesContainer = document.createElement('div');
    pagesContainer.id = 'pdf-pages';
    pagesContainer.className = 'pdf-pages';

    container.appendChild(controlsContainer);
    container.appendChild(pagesContainer);

    let currentPage = 1;
    const pagesToShow = 3;

    prevButton.addEventListener('click', () => {
      const newStartPage = Math.max(1, currentPage - pagesToShow);
      const newEndPage = Math.min(newStartPage + pagesToShow - 1, numPages);

      this.renderPdfPages(newStartPage, newEndPage);

      currentPage = newStartPage;
      pageInfo.textContent = `Página ${newStartPage}-${newEndPage} de ${numPages}`;
      prevButton.disabled = newStartPage === 1;
      nextButton.disabled = newEndPage === numPages;
    });

    nextButton.addEventListener('click', () => {
      const newStartPage = Math.min(currentPage + pagesToShow, numPages);
      const newEndPage = Math.min(newStartPage + pagesToShow - 1, numPages);

      this.renderPdfPages(newStartPage, newEndPage);

      currentPage = newStartPage;
      pageInfo.textContent = `Página ${newStartPage}-${newEndPage} de ${numPages}`;
      prevButton.disabled = newStartPage === 1;
      nextButton.disabled = newEndPage === numPages;
    });

    this.currentPage = currentPage;
    this.pageInfo = pageInfo;
    this.prevButton = prevButton;
    this.nextButton = nextButton;
  }

  private currentPage: number = 1;
  private pageInfo: HTMLElement | null = null;
  private prevButton: HTMLButtonElement | null = null;
  private nextButton: HTMLButtonElement | null = null;

  private async renderPdfPages(startPage: number, endPage: number): Promise<void> {
    if (!this.pdfDocument) return;

    const pdfDoc = this.pdfDocument;
    const numPages = pdfDoc.numPages;

    startPage = Math.max(1, Math.min(startPage, numPages));
    endPage = Math.min(Math.max(startPage, endPage), numPages);

    const pagesContainer = document.getElementById('pdf-pages');
    if (!pagesContainer) return;

    pagesContainer.innerHTML = '';

    const containerWidth = pagesContainer.clientWidth || 800;
    const pixelRatio = window.devicePixelRatio || 1;

    console.log(`📄 Renderizando páginas ${startPage}-${endPage}...`);
    console.log(`📐 Dimensiones nativas disponibles: ${this.pdfNativeWidth} x ${this.pdfNativeHeight}`);

    for (let pageNum = startPage; pageNum <= endPage; pageNum++) {
      const parteInfo = this.getPdfParteDePagina(pageNum) || this.pdfPartesInfo[0] || null;

      const pageDiv = document.createElement('div');
      pageDiv.className = `pdf-page-container ${parteInfo?.tipo === 'ANEXO' ? 'pdf-anexo-page' : 'pdf-original-page'}`;
      pageDiv.setAttribute('data-page-global', pageNum.toString());
      pageDiv.setAttribute('data-pdf-section', parteInfo?.etiqueta || 'O');
      pageDiv.style.setProperty('--pdf-part-color', parteInfo?.color || this.PDF_ORIGINAL_COLOR);

      const pageMarker = document.createElement('div');
      pageMarker.className = 'pdf-page-section-marker';
      pageMarker.textContent = parteInfo?.etiqueta || 'O';

      const pageHeader = document.createElement('div');
      pageHeader.className = 'pdf-page-header';
      this.construirHeaderPaginaPDF(pageHeader, parteInfo, pageNum, pageNum);
      pageDiv.appendChild(pageMarker);
      pageDiv.appendChild(pageHeader);

      const pageContentDiv = document.createElement('div');
      pageContentDiv.className = 'pdf-page';
      pageContentDiv.setAttribute('data-page', pageNum.toString());

      const page = await pdfDoc.getPage(pageNum);

      const viewport = page.getViewport({ scale: 1.0 });
      const nativeWidth = viewport.width;
      const nativeHeight = viewport.height;
      const baseScale = (containerWidth * 0.9) / nativeWidth;
      const visualScale = baseScale * this.PDF_DISPLAY_MULTIPLIER * this.zoomPDF;
      const scaledViewport = page.getViewport({ scale: visualScale * pixelRatio });
      const displayWidth = nativeWidth * visualScale;
      const displayHeight = nativeHeight * visualScale;

      pageContentDiv.setAttribute('data-native-width', nativeWidth.toString());
      pageContentDiv.setAttribute('data-native-height', nativeHeight.toString());
      pageContentDiv.setAttribute('data-visual-scale', visualScale.toString());
      pageContentDiv.style.width = `${displayWidth}px`;
      pageContentDiv.style.height = `${displayHeight}px`;

      const canvas = document.createElement('canvas');
      canvas.className = 'pdf-canvas';
      canvas.width = scaledViewport.width;
      canvas.height = scaledViewport.height;
      canvas.style.width = `${displayWidth}px`;
      canvas.style.height = `${displayHeight}px`;

      const context = canvas.getContext('2d', { alpha: false, willReadFrequently: true });
      if (!context) continue;

      pageContentDiv.appendChild(canvas);
      pageDiv.appendChild(pageContentDiv);

      const pageFooter = document.createElement('div');
      pageFooter.className = 'pdf-page-footer';
      pageFooter.textContent = `${parteInfo?.etiqueta || 'O'} · ${parteInfo?.tipo === 'ANEXO' ? 'Anexo' : 'Original'} · Haga clic para posicionar variables | Arrastre para mover`;
      pageDiv.appendChild(pageFooter);

      pagesContainer.appendChild(pageDiv);

      await page.render({
        canvasContext: context,
        viewport: scaledViewport,
        renderInteractiveForms: true
      }).promise;

      console.log(`✅ Canvas de página ${pageNum} renderizado`);

      await new Promise(resolve => setTimeout(resolve, 50));

      const pageRect = pageContentDiv.getBoundingClientRect();
      console.log(`📏 Dimensiones de página ${pageNum} en DOM:`, {
        width: pageRect.width,
        height: pageRect.height,
        left: pageRect.left,
        top: pageRect.top
      });

      this.ngZone.run(() => {
        const variables = this.variablesPorPagina.get(pageNum) || [];
        console.log(`🔍 Página ${pageNum} tiene ${variables.length} variables para renderizar`);

        if (variables.length > 0) {
          console.log(`📋 Variables en página ${pageNum}:`, variables.map(v => ({
            nombre: v.nombre,
            posX: v.posX,
            posY: v.posY
          })));
        }

        variables.forEach(variable => {
          this.mostrarVariableEnPdf(variable, pageContentDiv);
        });
      });
    }

    this.observarSeccionPDFActiva();
    console.log(`✅ Todas las páginas (${startPage}-${endPage}) renderizadas completamente`);
  }

  private loadPdfJsScript(): Promise<void> {
    return new Promise((resolve, reject) => {
      const pdfJsVersion = '3.4.120';
      const scriptSrc = `https://cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfJsVersion}/pdf.min.js`;

      if (document.querySelector(`script[src="${scriptSrc}"]`)) {
        resolve();
        return;
      }

      const script = document.createElement('script');
      script.src = scriptSrc;
      script.onload = () => resolve();
      script.onerror = (e) => reject(new Error(`Error al cargar PDF.js: ${e}`));
      document.head.appendChild(script);
    });
  }

  handlePdfClick(event: MouseEvent): void {
    if (!this.variableSeleccionada || !this.modoColocacion) return;

    if (this.variableSeleccionada.nombre === 'timbre_empleador' && !this.timbreEmpleadorDisponible) {
      alert('Debes subir el timbre del empleador antes de colocarlo en el formato.');
      this.modoColocacion = false;
      this.variableSeleccionada = null;
      const pdfContainer = document.getElementById('pdf-container');
      if (pdfContainer) {
        pdfContainer.style.cursor = 'default';
      }
      return;
    }

    const clickedPage = this.findClickedPage(event);
    if (!clickedPage) return;

    const pageNumber = parseInt(clickedPage.getAttribute('data-page') || '0', 10);
    if (pageNumber <= 0) return;

    const coords = this.calcularCoordenadasNativas(clickedPage, event.clientX, event.clientY);
    const variableActual = this.variableSeleccionada;

    const variableIndex = this.variables.findIndex(v => v === variableActual);
    const elementId = `var-${variableActual.nombre}-${Date.now()}`;

    variableActual.posX = coords.posX;
    variableActual.posY = coords.posY;
    variableActual.pagina = pageNumber;
    variableActual.colocada = true;

    const pageData = this.pdfPages.find(p => p.pageNumber === pageNumber);

    let valorEspecial: string | undefined = undefined;

    if (variableActual.nombre === 'elemento_seguridad') {
      valorEspecial = this.elementoSeguridadPendiente?.elemento || '';
    }

    if (variableActual.nombre === 'cantidad_seguridad') {
      valorEspecial = this.elementoSeguridadPendiente?.cantidad || '';
    }

    variableActual.ubicaciones.push({
      pagina: pageNumber,
      posX: coords.posX,
      posY: coords.posY,
      id: elementId,
      pageWidth: pageData?.nativeWidth || this.pdfNativeWidth,
      pageHeight: pageData?.nativeHeight || this.pdfNativeHeight,
      ...(
        ['elemento_seguridad', 'cantidad_seguridad'].includes(variableActual.nombre)
          ? { valor: valorEspecial }
          : variableActual.nombre === this.TEXTO_LIBRE_VARIABLE
            ? { valor: this.textoLibrePendiente }
            : {}
      )
    });

    if (!this.variablesPorPagina.has(pageNumber)) {
      this.variablesPorPagina.set(pageNumber, []);
    }

    const variablePosicionada: VariablePosicionada = {
      nombre: variableActual.nombre,
      posX: coords.posX,
      posY: coords.posY,
      elementId: elementId,
      variableIndex: variableIndex
    };

    this.variablesPorPagina.get(pageNumber)?.push(variablePosicionada);
    this.seleccionarVariableParaPropiedades(variablePosicionada);
    this.mostrarVariableEnPdf(variablePosicionada, clickedPage);

    if (this.modoModificacion) {
      this.actualizarInterfazModoModificacion();
    }

    /**
     * Si acabamos de posicionar el elemento,
     * ahora se activa automáticamente la posición de la cantidad.
     */
    if (variableActual.nombre === 'elemento_seguridad') {
      const variableCantidad = this.variables.find(v => v.nombre === 'cantidad_seguridad');

      if (variableCantidad) {
        this.variableSeleccionada = variableCantidad;
        this.modoColocacion = true;

        const pdfContainer = document.getElementById('pdf-container');

        if (pdfContainer) {
          pdfContainer.style.cursor = 'crosshair';

          setTimeout(() => {
            pdfContainer.addEventListener('click', this.handlePdfClick.bind(this), { once: true });
          }, 0);
        }

        alert(`Ahora posiciona la cantidad: ${this.elementoSeguridadPendiente?.cantidad || 'Sin cantidad'}`);
        return;
      }
    }

    /**
     * Si acabamos de posicionar la cantidad,
     * se termina el flujo de elemento + cantidad.
     */
    if (variableActual.nombre === 'cantidad_seguridad') {
      this.elementoSeguridadPendiente = null;
      this.elementoSeleccionadoTemp = null;
    }

    if (variableActual.nombre === this.TEXTO_LIBRE_VARIABLE) {
      this.textoLibrePendiente = '';
    }

    this.modoColocacion = false;

    const pdfContainer = document.getElementById('pdf-container');
    if (pdfContainer) {
      pdfContainer.style.cursor = 'default';
    }

    this.variableSeleccionada = null;
  }

  mostrarVariableEnPdf(variable: VariablePosicionada, pageElement: HTMLElement): void {
    if (this.pdfNativeWidth === 0 || this.pdfNativeHeight === 0) {
      console.error('ERROR: Dimensiones nativas no inicializadas');
      return;
    }

    const pageRect = pageElement.getBoundingClientRect();

    if (pageRect.width === 0 || pageRect.height === 0) {
      setTimeout(() => this.mostrarVariableEnPdf(variable, pageElement), 100);
      return;
    }

    const { scaleX, scaleY } = this.obtenerEscalaPagina(pageElement);
    const ubicacion = this.variables[variable.variableIndex]?.ubicaciones.find(
      u => u.id === variable.elementId
    );

    const variableElement = document.createElement('div');
    variableElement.id = variable.elementId;
    variableElement.className = 'pdf-variable';
    variableElement.setAttribute('data-variable', variable.nombre);
    variableElement.setAttribute('data-variable-index', variable.variableIndex.toString());

    if (this.modoModificacion) {
      variableElement.classList.add('edit-mode');
    }

    if (this.variableSeleccionadaParaPropiedades?.elementId === variable.elementId) {
      variableElement.classList.add('selected');
    }

    const displayX = variable.posX * scaleX;
    const baselineYPx = variable.posY * scaleY;

    if (
      isNaN(displayX) ||
      isNaN(baselineYPx) ||
      !isFinite(displayX) ||
      !isFinite(baselineYPx)
    ) {
      console.error('ERROR: Coordenadas display inválidas', {
        variable,
        displayX,
        baselineYPx
      });
      return;
    }

    variableElement.style.position = 'absolute';
    variableElement.style.left = `${displayX}px`;
    variableElement.style.zIndex = '100';
    variableElement.style.whiteSpace = 'nowrap';
    variableElement.style.maxWidth = 'none';
    variableElement.style.cursor = 'move';
    variableElement.style.pointerEvents = 'all';

    const renderImage = (
      src: string,
      fallbackWidth: number,
      fallbackHeight: number,
      className: string
    ): void => {
      variableElement.classList.add(className, 'pdf-variable-image');

      const img = document.createElement('img');
      img.src = src;

      const nativeImgWidth = ubicacion?.width || fallbackWidth;
      const nativeImgHeight = ubicacion?.height || fallbackHeight;

      const displayWidth = nativeImgWidth * scaleX;
      const displayHeight = nativeImgHeight * scaleY;

      variableElement.style.top = `${variable.posY * scaleY}px`;
      variableElement.style.width = `${displayWidth}px`;
      variableElement.style.height = `${displayHeight}px`;

      img.style.width = `${displayWidth}px`;
      img.style.height = `${displayHeight}px`;
      img.style.objectFit = 'contain';
      img.style.display = 'block';
      img.style.pointerEvents = 'none';

      img.onerror = () => {
        console.error(`Error al cargar imagen ${variable.nombre}`);
        img.style.border = '2px solid red';
      };

      variableElement.appendChild(img);
    };

    if (variable.nombre === 'firma_empleador') {
      if (!this.firmaEmpleadorDisponible || !this.firmaEmpleadorUrl) return;
      renderImage(this.firmaEmpleadorUrl, 150, 50, 'firma-empleador-imagen');

    } else if (variable.nombre === 'timbre_empleador') {
      if (!this.timbreEmpleadorDisponible || !this.timbreEmpleadorUrl) return;
      renderImage(this.timbreEmpleadorUrl, 150, 50, 'firma-empleador-imagen');

    } else if (variable.nombre === 'firma') {
      renderImage(
        this.FIRMA_TRABAJADOR_PLACEHOLDER,
        this.FIRMA_TRABAJADOR_WIDTH,
        this.FIRMA_TRABAJADOR_HEIGHT,
        'firma-trabajador-imagen'
      );

    } else if (variable.nombre === 'huella') {
      renderImage(
        this.HUELLA_TRABAJADOR_PLACEHOLDER,
        this.HUELLA_TRABAJADOR_WIDTH,
        this.HUELLA_TRABAJADOR_HEIGHT,
        'huella-trabajador-imagen'
      );

    } else if (variable.nombre === 'firma_supervisor') {
      renderImage(
        this.FIRMA_SUPERVISOR_PLACEHOLDER,
        this.FIRMA_SUPERVISOR_WIDTH,
        this.FIRMA_SUPERVISOR_HEIGHT,
        'firma-supervisor-imagen'
      );

    } else if (variable.nombre === 'huella_supervisor') {
      renderImage(
        this.HUELLA_SUPERVISOR_PLACEHOLDER,
        this.HUELLA_SUPERVISOR_WIDTH,
        this.HUELLA_SUPERVISOR_HEIGHT,
        'huella-supervisor-imagen'
      );

    } else {
      const textoMostrar = (
        ['elemento_seguridad', 'cantidad_seguridad', 'texto_libre'].includes(variable.nombre) &&
        ubicacion?.valor
      )
        ? ubicacion.valor
        : this.obtenerValorEjemplo(variable.nombre);

      const fontSizePt = ubicacion?.fontSize || this.PDF_TEXT_FONT_SIZE_PT;
      const displayFontSize = this.convertirPtAPx(fontSizePt, pageElement);

      const displayTop = this.obtenerTopTextoDesdeBaselinePx(
        baselineYPx,
        displayFontSize
      );

      variableElement.style.top = `${displayTop}px`;
      variableElement.style.height = `${displayFontSize}px`;

      const textSpan = document.createElement('span');
      textSpan.textContent = textoMostrar;
      textSpan.style.pointerEvents = 'none';
      textSpan.style.display = 'block';
      textSpan.style.height = `${displayFontSize}px`;
      textSpan.style.lineHeight = `${displayFontSize}px`;
      textSpan.style.margin = '0';
      textSpan.style.padding = '0';

      variableElement.appendChild(textSpan);

      variableElement.style.setProperty('font-family', 'Helvetica, Arial, sans-serif', 'important');
      variableElement.style.setProperty('font-size', `${displayFontSize}px`, 'important');
      variableElement.style.setProperty('line-height', `${displayFontSize}px`, 'important');
      variableElement.style.setProperty('font-weight', '400', 'important');
      variableElement.style.setProperty('padding', '0', 'important');
      variableElement.style.setProperty('color', '#000000', 'important');

      variableElement.classList.add('pdf-variable-text');
    }

    if (this.esCampocentrado(variable.nombre) && !this.esVariableImagen(variable.nombre)) {
      variableElement.style.textAlign = 'center';
      variableElement.style.transform = 'translateX(-50%)';
      variableElement.classList.add('pdf-variable-centered');
    } else {
      variableElement.style.textAlign = 'left';
      variableElement.style.transform = 'none';
    }

    pageElement.style.position = 'relative';
    pageElement.appendChild(variableElement);

    variableElement.addEventListener('mousedown', (event) => {
      this.seleccionarVariableParaPropiedades(variable);
      this.redibujarEstadoSeleccionado();
      this.handleVariableMouseDown(event, variable, variableElement, pageElement);
    });

    variableElement.addEventListener('click', (event) => {
      event.stopPropagation();
      this.seleccionarVariableParaPropiedades(variable);
      this.redibujarEstadoSeleccionado();
    });

    if (this.esVariableImagen(variable.nombre)) {
      this.agregarHandlesRedimension(variableElement, variable, pageElement);
    }

    const deleteBtn = document.createElement('button');
    deleteBtn.className = 'delete-btn';
    deleteBtn.innerHTML = '✕';
    deleteBtn.title = 'Eliminar variable';
    deleteBtn.type = 'button';

    deleteBtn.addEventListener('mousedown', (event) => {
      event.preventDefault();
      event.stopPropagation();
    });

    deleteBtn.addEventListener('click', (event) => {
      event.preventDefault();
      event.stopPropagation();
      this.eliminarVariable(variable.elementId, variable.variableIndex);
    });

    variableElement.appendChild(deleteBtn);

    if (this.mostrarDebugCoordenadas) {
      const debug = document.createElement('div');
      debug.className = 'debug-info';
      debug.setAttribute('data-for', variable.elementId);
      debug.textContent = `P${this.obtenerPaginaVariable(variable.elementId) || pageElement.getAttribute('data-page')} X:${variable.posX.toFixed(1)} Y:${variable.posY.toFixed(1)}`;
      variableElement.appendChild(debug);
    }

    this.actualizarEstadoVisualPDF();
  }

  private redibujarEstadoSeleccionado(): void {
    document.querySelectorAll('.pdf-variable.selected').forEach(el => el.classList.remove('selected'));
    if (this.variableSeleccionadaParaPropiedades?.elementId) {
      document.getElementById(this.variableSeleccionadaParaPropiedades.elementId)?.classList.add('selected');
    }
  }



  /**
   * Agregar handles de redimensionamiento
   */
  agregarHandlesRedimension(element: HTMLElement, variable: VariablePosicionada, pageElement: HTMLElement): void {
    const positions = [
      'top-left', 'top-right', 'bottom-left', 'bottom-right',
      'top', 'right', 'bottom', 'left'
    ];

    positions.forEach(pos => {
      const handle = document.createElement('div');
      handle.className = `resize-handle resize-handle-${pos}`;
      handle.style.cssText = `
        position: absolute;
        width: 8px;
        height: 8px;
        background-color: #4a80f5;
        border: 1px solid white;
        cursor: ${this.getCursorForHandle(pos)};
        z-index: 102;
      `;

      this.posicionarHandle(handle, pos);

      handle.addEventListener('mousedown', (e) => {
        e.stopPropagation();
        this.iniciarRedimension(e, element, variable, pageElement, pos);
      });

      element.appendChild(handle);
    });
  }

  /**
   * Posicionar handles
   */
  posicionarHandle(handle: HTMLElement, position: string): void {
    switch (position) {
      case 'top-left':
        handle.style.top = '-4px';
        handle.style.left = '-4px';
        break;
      case 'top-right':
        handle.style.top = '-4px';
        handle.style.right = '-4px';
        break;
      case 'bottom-left':
        handle.style.bottom = '-4px';
        handle.style.left = '-4px';
        break;
      case 'bottom-right':
        handle.style.bottom = '-4px';
        handle.style.right = '-4px';
        break;
      case 'top':
        handle.style.top = '-4px';
        handle.style.left = 'calc(50% - 4px)';
        break;
      case 'right':
        handle.style.right = '-4px';
        handle.style.top = 'calc(50% - 4px)';
        break;
      case 'bottom':
        handle.style.bottom = '-4px';
        handle.style.left = 'calc(50% - 4px)';
        break;
      case 'left':
        handle.style.left = '-4px';
        handle.style.top = 'calc(50% - 4px)';
        break;
    }
  }

  normalizarTexto(valor: any): string {
    return (valor || '')
      .toString()
      .toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .trim();
  }

  documentosFiltrados(): any[] {
    const busqueda = this.normalizarTexto(this.filtroDocumentoBuscado);
    const tipo = this.normalizarTexto(this.filtroDocumentoTipo);
    const fecha = this.filtroDocumentoFecha;

    return (this.documentosCargados || []).filter((doc: any) => {
      const nombreDoc = this.normalizarTexto(doc.nombre);
      const tipoDoc = this.normalizarTexto(doc.tipo);
      const fechaDoc = doc.fecha_creacion ? new Date(doc.fecha_creacion) : null;

      const coincideNombre =
        !busqueda ||
        nombreDoc.includes(busqueda) ||
        tipoDoc.includes(busqueda) ||
        (doc.fecha_creacion || '').toString().includes(busqueda);

      const coincideTipo =
        !tipo ||
        tipoDoc === tipo;

      const coincideFecha =
        !fecha ||
        (
          fechaDoc &&
          fechaDoc.toISOString().slice(0, 10) === fecha
        );

      return coincideNombre && coincideTipo && coincideFecha;
    });
  }

  documentosAgrupadosPorTipo(): { tipo: string; documentos: any[] }[] {
    const docs = this.documentosFiltrados();

    const ordenTipos = ['CHILENO', 'EXTRANJERO'];
    const grupos: { [key: string]: any[] } = {};

    docs.forEach((doc: any) => {
      const tipo = (doc.tipo || 'SIN TIPO').toUpperCase();
      if (!grupos[tipo]) grupos[tipo] = [];
      grupos[tipo].push(doc);
    });

    return Object.keys(grupos)
      .sort((a, b) => {
        const ia = ordenTipos.indexOf(a);
        const ib = ordenTipos.indexOf(b);

        if (ia !== -1 && ib !== -1) return ia - ib;
        if (ia !== -1) return -1;
        if (ib !== -1) return 1;
        return a.localeCompare(b);
      })
      .map(tipo => ({
        tipo,
        documentos: grupos[tipo].sort((a, b) => {
          const fa = a.fecha_creacion ? new Date(a.fecha_creacion).getTime() : 0;
          const fb = b.fecha_creacion ? new Date(b.fecha_creacion).getTime() : 0;
          return fb - fa;
        })
      }));
  }

  limpiarFiltrosDocumentos(): void {
    this.filtroDocumentoBuscado = '';
    this.filtroDocumentoTipo = '';
    this.filtroDocumentoFecha = '';
    this.recalcularDocumentosExistentes();
  }

  /**
   * Obtener cursor apropiado
   */
  getCursorForHandle(position: string): string {
    const cursors: { [key: string]: string } = {
      'top-left': 'nwse-resize',
      'top-right': 'nesw-resize',
      'bottom-left': 'nesw-resize',
      'bottom-right': 'nwse-resize',
      'top': 'ns-resize',
      'right': 'ew-resize',
      'bottom': 'ns-resize',
      'left': 'ew-resize'
    };
    return cursors[position] || 'default';
  }

  /**
   * Iniciar redimensionamiento
   */
  iniciarRedimension(
    event: MouseEvent,
    element: HTMLElement,
    variable: VariablePosicionada,
    pageElement: HTMLElement,
    handlePosition: string
  ): void {
    event.preventDefault();

    const startX = event.clientX;
    const startY = event.clientY;
    const startWidth = element.offsetWidth;
    const startHeight = element.offsetHeight;
    const startLeft = element.offsetLeft;
    const startTop = element.offsetTop;

    this.imagenFirmaEnEdicion = {
      element: element,
      originalWidth: startWidth,
      originalHeight: startHeight,
      minWidth: 50,
      minHeight: 20
    };

    const onMouseMove = (e: MouseEvent) => {
      const deltaX = e.clientX - startX;
      const deltaY = e.clientY - startY;

      let newWidth = startWidth;
      let newHeight = startHeight;
      let newLeft = startLeft;
      let newTop = startTop;

      switch (handlePosition) {
        case 'bottom-right':
          newWidth = Math.max(this.imagenFirmaEnEdicion!.minWidth, startWidth + deltaX);
          newHeight = Math.max(this.imagenFirmaEnEdicion!.minHeight, startHeight + deltaY);
          break;
        case 'bottom-left':
          newWidth = Math.max(this.imagenFirmaEnEdicion!.minWidth, startWidth - deltaX);
          newHeight = Math.max(this.imagenFirmaEnEdicion!.minHeight, startHeight + deltaY);
          newLeft = startLeft + (startWidth - newWidth);
          break;
        case 'top-right':
          newWidth = Math.max(this.imagenFirmaEnEdicion!.minWidth, startWidth + deltaX);
          newHeight = Math.max(this.imagenFirmaEnEdicion!.minHeight, startHeight - deltaY);
          newTop = startTop + (startHeight - newHeight);
          break;
        case 'top-left':
          newWidth = Math.max(this.imagenFirmaEnEdicion!.minWidth, startWidth - deltaX);
          newHeight = Math.max(this.imagenFirmaEnEdicion!.minHeight, startHeight - deltaY);
          newLeft = startLeft + (startWidth - newWidth);
          newTop = startTop + (startHeight - newHeight);
          break;
        case 'right':
          newWidth = Math.max(this.imagenFirmaEnEdicion!.minWidth, startWidth + deltaX);
          break;
        case 'left':
          newWidth = Math.max(this.imagenFirmaEnEdicion!.minWidth, startWidth - deltaX);
          newLeft = startLeft + (startWidth - newWidth);
          break;
        case 'bottom':
          newHeight = Math.max(this.imagenFirmaEnEdicion!.minHeight, startHeight + deltaY);
          break;
        case 'top':
          newHeight = Math.max(this.imagenFirmaEnEdicion!.minHeight, startHeight - deltaY);
          newTop = startTop + (startHeight - newHeight);
          break;
      }

      element.style.width = `${newWidth}px`;
      element.style.height = `${newHeight}px`;
      element.style.left = `${newLeft}px`;
      element.style.top = `${newTop}px`;

      const img = element.querySelector('img') as HTMLImageElement;
      if (img) {
        img.style.width = `${newWidth}px`;
        img.style.height = `${newHeight}px`;
      }
    };

    const onMouseUp = () => {
      document.removeEventListener('mousemove', onMouseMove);
      document.removeEventListener('mouseup', onMouseUp);

      const nativeWidth = Number(pageElement.getAttribute('data-native-width')) || this.pdfNativeWidth;
      const nativeHeight = Number(pageElement.getAttribute('data-native-height')) || this.pdfNativeHeight;

      const scaleX = nativeWidth / pageElement.offsetWidth;
      const scaleY = nativeHeight / pageElement.offsetHeight;

      const finalWidth = element.offsetWidth;
      const finalHeight = element.offsetHeight;
      const finalLeft = element.offsetLeft;
      const finalTop = element.offsetTop;

      const nativeX = finalLeft * scaleX;
      const nativeY = finalTop * scaleY;

      const pageNumber = parseInt(pageElement.getAttribute('data-page') || '0');
      const variablesList = this.variablesPorPagina.get(pageNumber) || [];
      const varIndex = variablesList.findIndex(v => v.elementId === variable.elementId);

      if (varIndex !== -1) {
        variablesList[varIndex].posX = nativeX;
        variablesList[varIndex].posY = nativeY;

        const mainVarIndex = variablesList[varIndex].variableIndex;
        if (mainVarIndex >= 0 && mainVarIndex < this.variables.length) {
          const mainVariable = this.variables[mainVarIndex];

          const ubicacionIndex = mainVariable.ubicaciones.findIndex(u => u.id === variable.elementId);
          if (ubicacionIndex !== -1) {
            mainVariable.ubicaciones[ubicacionIndex].posX = nativeX;
            mainVariable.ubicaciones[ubicacionIndex].posY = nativeY;
            mainVariable.ubicaciones[ubicacionIndex].width = finalWidth * scaleX;
            mainVariable.ubicaciones[ubicacionIndex].height = finalHeight * scaleY;
          }
        }

        this.haycambiosPendientes = true;
        this.seleccionarVariableParaPropiedades(variablesList[varIndex]);
      }

      console.log(`✅ ${variable.nombre} redimensionada en (${nativeX}, ${nativeY})`);

      this.imagenFirmaEnEdicion = null;
    };

    document.addEventListener('mousemove', onMouseMove);
    document.addEventListener('mouseup', onMouseUp);
  }

  actualizarInterfazModoModificacion(): void {
    console.log('Actualizando interfaz en modo modificación...');

    this.currentRetry = 0;
    this.intentarActualizarVariables();
  }

  private maxRetries = 5;
  private currentRetry = 0;

  private intentarActualizarVariables(): void {
    setTimeout(() => {
      const variables = document.querySelectorAll('.pdf-variable');
      console.log(`Encontradas ${variables.length} variables para actualizar (intento ${this.currentRetry + 1}/${this.maxRetries})`);

      if (variables.length === 0) {
        this.currentRetry++;

        if (this.currentRetry < this.maxRetries) {
          console.warn('No se encontraron variables en el PDF, intentando de nuevo...');
          this.intentarActualizarVariables();
        } else {
          console.error('Se alcanzó el número máximo de reintentos.');
        }
        return;
      }

      variables.forEach(el => {
        el.classList.add('edit-mode');

        if (!el.querySelector('.delete-btn')) {
          const deleteBtn = document.createElement('div');
          deleteBtn.className = 'delete-btn';
          deleteBtn.innerHTML = '×';
          deleteBtn.title = 'Eliminar variable';

          const variableId = el.id;
          const variableIndex = el.getAttribute('data-variable-index');

          deleteBtn.addEventListener('click', (event) => {
            event.stopPropagation();
            if (variableIndex !== null) {
              this.eliminarVariable(variableId, parseInt(variableIndex));
            }
          });

          el.appendChild(deleteBtn);
        }
      });

      console.log('Interfaz de modo modificación actualizada correctamente');
    }, 500 + (this.currentRetry * 300));
  }

  eliminarVariable(elementId: string, variableIndex: number): void {
    let paginaEncontrada = -1;
    let variableEncontrada: VariablePosicionada | null = null;

    this.variablesPorPagina.forEach((variables, pagina) => {
      const index = variables.findIndex(v => v.elementId === elementId);
      if (index !== -1) {
        paginaEncontrada = pagina;
        variableEncontrada = variables[index];
      }
    });

    if (paginaEncontrada !== -1 && variableEncontrada) {
      const variableElement = document.getElementById(elementId);
      if (variableElement) {
        variableElement.remove();

        const debugInfo = document.querySelector(`.debug-info[data-for="${elementId}"]`);
        if (debugInfo) {
          debugInfo.remove();
        }
      }

      const variablesList = this.variablesPorPagina.get(paginaEncontrada);
      if (variablesList) {
        const indexInPage = variablesList.findIndex(v => v.elementId === elementId);
        if (indexInPage !== -1) {
          variablesList.splice(indexInPage, 1);
        }
      }

      if (variableIndex >= 0 && variableIndex < this.variables.length) {
        const variable = this.variables[variableIndex];

        const ubicacionIndex = variable.ubicaciones.findIndex(u => u.id === elementId);
        if (ubicacionIndex !== -1) {
          variable.ubicaciones.splice(ubicacionIndex, 1);
        }

        if (variable.ubicaciones.length === 0) {
          variable.colocada = false;
        }
      }

      if (this.variableSeleccionadaParaPropiedades?.elementId === elementId) {
        this.variableSeleccionadaParaPropiedades = null;
      }
      this.haycambiosPendientes = true;
    }
  }

  /**
   * Mejor manejo del estado y limpieza
   */
  modificarDocumentoSeleccionado(): void {
    if (!this.documentoSeleccionado || !this.documentoGuardadoId) {
      this.errorMessage = 'No hay un documento seleccionado para modificar';
      return;
    }

    this.modoDocumentoExistente = false;
    this.modoModificacion = true;
    this.isLoading = true;

    setTimeout(() => {
      const pdfContainer = document.getElementById('pdf-container');
      if (pdfContainer) {
        pdfContainer.innerHTML = '';
      }

      if (this.pdfSrc) {
        this.renderPdf()
          .then(() => {
            this.actualizarInterfazModoModificacion();
          })
          .catch(err => {
            console.error('Error al renderizar PDF en modo modificación:', err);
            this.isLoading = false;
            this.errorMessage = 'No se pudo cargar el PDF para modificación.';
          });
      } else {
        const pdfUrl = this.documentoSeleccionado?.archivo_pdf_url;
        if (pdfUrl) {
          this.cargarPDFDesdeURL(pdfUrl);
        } else {
          this.isLoading = false;
          this.errorMessage = 'No se encontró la URL del PDF.';
        }
      }
    }, 150);
  }

  guardarCambiosDocumento(): void {
    if (!this.documentoGuardadoId) {
      alert('No se puede identificar el documento a modificar');
      return;
    }

    const variables = this._serializarVariablesParaBackend();

    const datosActualizados = {
      variables: variables
    };

    this.isLoading = true;

    this.apiService.put(`api_documento_nativo/${this.documentoGuardadoId}/`, datosActualizados)
      .subscribe({
        next: (response: any) => {
          console.log('Documento actualizado exitosamente', response);
          this.isLoading = false;

          this.modoModificacion = false;
          this.modoDocumentoExistente = true;
          this.haycambiosPendientes = false;
          alert('Documento actualizado exitosamente');
        },
        error: (error) => {
          console.error('Error al actualizar el documento:', error);
          alert(`Error: ${error.error?.error || 'No se pudo actualizar el documento'}`);
          this.isLoading = false;
        }
      });
  }

  cerrarModificacion(): void {
    if (this.modoModificacion && this.haycambiosPendientes) {
      const confirmar = confirm('¿Desea guardar los cambios antes de salir?');
      if (confirmar && this.documentoSeleccionado) {
        this.guardarCambiosDocumento();
        return;
      }
    }

    this.modoModificacion = false;
    this.modoDocumentoExistente = true;
    this.haycambiosPendientes = false;

    if (this.documentoSeleccionado) {
      this.seleccionarDocumentoExistente(this.documentoSeleccionado);
    }
  }

  formatearNombreVariable(nombre: string): string {
    if (!nombre) return '';

    const texto = nombre
      .replace(/_/g, ' ')
      .replace(/\s+/g, ' ')
      .trim()
      .toLowerCase();

    return texto.charAt(0).toUpperCase() + texto.slice(1);
  }

  guardarFormato(): void {
    if (!this.originalPdfFile) {
      alert('Por favor, seleccione un archivo PDF primero');
      return;
    }

    const hayVariablesColocadas = this.variables.some(v => v.ubicaciones.length > 0);
    if (!hayVariablesColocadas) {
      alert('Debe colocar al menos una variable en el documento');
      return;
    }

    this.mostrarModal = true;
  }

  cerrarModal(): void {
    this.mostrarModal = false;
    this.nombreFormato = '';
    this.tipoContrato = 'CHILENO';
  }

  confirmarGuardado(): void {
    if (!this.nombreFormato.trim()) {
      alert('El nombre del formato es obligatorio');
      return;
    }

    if (!this.originalPdfFile) {
      alert('No se encontró el archivo PDF original');
      return;
    }

    const variables = this._serializarVariablesParaBackend();

    const formData = new FormData();

    if (this.pdfFiles.length > 1) {
      console.log(`📎 Enviando ${this.pdfFiles.length} PDFs para fusionar...`);

      this.pdfFiles.forEach((file, index) => {
        formData.append(`pdf_parte_${index}`, file);
        console.log(`  - Parte ${index + 1}: ${file.name}, ${(file.size / 1024).toFixed(2)} KB`);
      });

      formData.append('num_partes', this.pdfFiles.length.toString());
      formData.append('requiere_merge', 'true');
    } else {
      const nombreArchivo = this.nombreFormato.toLowerCase().replace(/\s+/g, '_') + '.pdf';
      const renamedFile = new File([this.originalPdfFile!], nombreArchivo, { type: 'application/pdf' });
      console.log('Enviando archivo único:', renamedFile.name);
      formData.append('archivo_pdf', renamedFile);
      formData.append('requiere_merge', 'false');
    }

    formData.append('nombre', this.nombreFormato);
    formData.append('tipo', this.tipoContrato);
    formData.append('variables', JSON.stringify(variables));

    this.isLoading = true;
    this.apiService.postFormData('api_documento_nativo/', formData)
      .subscribe({
        next: (response: any) => {
          console.log('Formato guardado exitosamente', response);
          this.documentoGuardadoId = response.id;
          this.isLoading = false;
          this.haycambiosPendientes = false;
          alert('Formato guardado exitosamente');
          this.cerrarModal();
        },
        error: (error) => {
          console.error('Error al guardar el formato:', error);
          alert(`Error: ${error.error?.error || 'No se pudo guardar el formato'}`);
          this.isLoading = false;
        }
      });
  }

  generarPDFPrueba(): void {
    if (!this.documentoGuardadoId) {
      alert('Primero debes guardar el documento para poder generar un PDF');
      return;
    }

    this.variablesConDatos = [];
    const variablesColocadas = this.variables.filter(v => v.colocada);

    variablesColocadas.forEach(variable => {
      let tipo = 'normal';
      let valorPredeterminado = this.obtenerValorEjemplo(variable.nombre);

      if (variable.nombre.includes('fecha') ||
        variable.nombre.includes('f_inicio') ||
        variable.nombre.includes('f_nacmnto') ||
        variable.nombre.includes('f_ingreso') ||
        variable.nombre.includes('f_termino')) {
        tipo = 'fecha';
      }

      this.variablesConDatos.push({
        nombre: variable.nombre,
        tipo: tipo,
        valorPredeterminado: valorPredeterminado,
        valorPrueba: valorPredeterminado
      });
    });

    if (this.variablesConDatos.length > 0) {
      this.mostrarModalDatosPrueba = true;
    } else {
      alert('No hay variables colocadas en el documento');
    }
  }

  /**
    * Obtener variables filtradas según el tipo de contrato
  */
  get variablesFiltradas(): VariableDocumento[] {
    let vars = this.variables;

    if (this.tipoContrato === 'CHILENO') {
      vars = vars.filter(v => v.nombre !== 'dni' && v.nombre !== 'nic');
    } else if (!this.modoModificacion) {
      vars = vars.filter(v => v.nombre !== 'rut');
    }

    if (this.variableBuscada.trim()) {
      const term = this.variableBuscada.toLowerCase().trim();
      vars = vars.filter(v => v.nombre.toLowerCase().includes(term));
    }

    return [...vars].sort((a, b) => a.nombre.localeCompare(b.nombre, 'es'));
  }

  /**
   * Confirmar tipo de contrato y renderizar PDF
   */
  confirmarTipoContrato(): void {
    this.mostrarModalTipoContrato = false;
    this.renderPdf();
  }

  /**
   * Cerrar modal de tipo de contrato
   */
  cerrarModalTipoContrato(): void {
    this.mostrarModalTipoContrato = false;
    this.pdfSrc = null;
    this.originalPdfFile = null;
    this.pdfBuffers = [];
    this.pdfFiles = [];
    this.pdfDocuments = [];
    this.pdfPartesInfo = [];
    this.seccionPDFActiva = null;
    this.paginaPDFActiva = 1;
    this.totalPagesAcumuladas = [];
    this.totalPages = 0;
  }

  cerrarModalDatosPrueba(): void {
    this.mostrarModalDatosPrueba = false;
  }

  cancelarElementoSeguridad(): void {
    this.mostrarModalElementoSeguridad = false;
    this.elementoSeleccionadoTemp = null;
    this.elementoSeguridadPendiente = null;
    this.variableSeleccionada = null;
    this.modoColocacion = false;

    const pdfContainer = document.getElementById('pdf-container');
    if (pdfContainer) {
      pdfContainer.style.cursor = 'default';
    }
  }

  confirmarGenerarPDF(): void {
    if (!this.documentoGuardadoId) {
      alert('No se encontró el ID del documento');
      return;
    }

    const datosVariables: { [key: string]: string } = {};

    this.variablesConDatos.forEach(variable => {
      datosVariables[variable.nombre] = variable.valorPrueba || variable.valorPredeterminado;
    });

    this.isLoading = true;

    this.apiService.postBlob('api_documento_nativo/', {
      action: 'generar_prueba',
      documento_id: this.documentoGuardadoId,
      datos_variables: datosVariables
    }).subscribe({
      next: (blob: Blob) => {
        console.log('PDF generado con éxito');

        const blobUrl = URL.createObjectURL(blob);
        this.pdfPreviewUrl = blobUrl;

        window.open(blobUrl, '_blank');

        this.isLoading = false;
        this.mostrarModalDatosPrueba = false;

        setTimeout(() => URL.revokeObjectURL(blobUrl), 60000);
      },
      error: (error) => {
        console.error('Error al generar PDF:', error);
        alert(`Error: No se pudo generar el PDF`);
        this.isLoading = false;
      }
    });
  }

  private limpiarFormatoEliminadoDeInterfaz(documentoId: number): void {
    const id = Number(documentoId);

    this.documentosCargados = (this.documentosCargados || []).filter(
      (doc: any) => Number(doc.id) !== id
    );

    this.documentosFiltradosCache = (this.documentosFiltradosCache || []).filter(
      (doc: any) => Number(doc.id) !== id
    );

    this.documentosAgrupadosCache = (this.documentosAgrupadosCache || [])
      .map((grupo: any) => ({
        ...grupo,
        documentos: (grupo.documentos || []).filter(
          (doc: any) => Number(doc.id) !== id
        )
      }))
      .filter((grupo: any) => grupo.documentos.length > 0);

    this.recalcularDocumentosExistentes();

    if (this.documentoSeleccionado?.id && Number(this.documentoSeleccionado.id) === id) {
      this.documentoSeleccionado = null;
      this.documentoGuardadoId = null;
      this.pdfSrc = null;
      this.pdfPreviewUrl = null;
      this.pdfPages = [];
      this.pdfDocuments = [];
      this.pdfBuffers = [];
      this.pdfFiles = [];
      this.pdfPartesInfo = [];
      this.seccionPDFActiva = null;
      this.paginaPDFActiva = 1;
      this.totalPages = 0;
      this.pdfNativeWidth = 0;
      this.pdfNativeHeight = 0;
      this.variableSeleccionadaParaPropiedades = null;
      this.haycambiosPendientes = false;

      this.resetearVariables();

      const pdfContainer = document.getElementById('pdf-container');
      if (pdfContainer) {
        pdfContainer.innerHTML = '';
      }
    }

    if (this.documentoEditandoNombreId && Number(this.documentoEditandoNombreId) === id) {
      this.documentoEditandoNombreId = null;
      this.nombreDocumentoEditado = '';
    }
  }

  descargarPDF(): void {
    if (!this.pdfPreviewUrl) return;

    const a = document.createElement('a');
    a.href = this.pdfPreviewUrl;
    a.download = `documento_${this.documentoGuardadoId}_${Date.now()}.pdf`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  }

  guardarPosicionesModificadas(): void {
    if (!this.documentoGuardadoId) {
      alert('No se puede identificar el documento');
      return;
    }

    const variables = this._serializarVariablesParaBackend();

    this.isLoading = true;

    this.apiService.put(`api_documento_nativo/${this.documentoGuardadoId}/`, {
      variables: variables
    }).subscribe({
      next: (response: any) => {
        console.log('Posiciones sincronizadas con backend', response);
        this.isLoading = false;
        this.haycambiosPendientes = false;
        alert('Posiciones guardadas.');
      },
      error: (error) => {
        console.error('Error al sincronizar posiciones:', error);
        alert(`Error: ${error.error?.error || 'No se pudieron guardar las posiciones'}`);
        this.isLoading = false;
      }
    });
  }
}
