import { Component, Inject, NgZone, OnInit, PLATFORM_ID } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ContratistaApiService } from '../../../../../services/contratista-api.service';
import { JwtService } from '../../../../../services/jwt.service';

interface Ubicacion {
  pagina: number;
  posX: number;
  posY: number;
  id: string;
  pageWidth: number;
  pageHeight: number;
  width?: number;
  height?: number;
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

interface VariablePosicionada {
  nombre: string;
  posX: number;
  posY: number;
  elementId: string;
  variableIndex: number;
}

interface VariableConDatos {
  nombre: string;
  tipo: string;
  valorPredeterminado: string;
  valorPrueba: string;
}

interface FirmaOrganizacion {
  id: number;
  tipo: 'firma' | 'huella';
  nombre: string;
  key: string;
  imagen_url: string;
}

@Component({
  selector: 'app-formatos',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './formatos.component.html',
  styleUrl: './formatos.component.css'
})
export class FormatosComponent implements OnInit {
  pdfSrc: string | ArrayBuffer | null = null;
  isLoading = false;
  isBrowser: boolean;
  errorMessage: string | null = null;
  public holding: string = '';

  originalPdfFile: File | null = null;
  pdfDocuments: any[] = [];
  pdfBuffers: ArrayBuffer[] = [];
  pdfFiles: File[] = [];
  totalPages: number = 0;
  pdfPages: any[] = [];
  totalPagesAcumuladas: number[] = [];

  mostrarModal = false;
  nombreFormato = '';
  tipoContrato = 'CHILENO';
  mostrarModalTipoContrato = false;

  documentoGuardadoId: number | null = null;

  mostrarModalDatosPrueba = false;
  variablesConDatos: VariableConDatos[] = [];
  pdfPreviewUrl: string | null = null;

  modoDocumentoExistente: boolean = false;
  documentosCargados: any[] = [];
  documentoSeleccionado: any = null;

  pdfNativeWidth: number = 0;
  pdfNativeHeight: number = 0;

  // ⭐ FIRMAS Y HUELLAS DE ORGANIZACIÓN (dinámicas)
  firmasOrganizacion: FirmaOrganizacion[] = [];
  mostrarModalNuevaFirmaOrg = false;
  nuevaFirmaOrgTipo: 'firma' | 'huella' = 'firma';
  nuevaFirmaOrgNombre = '';
  nuevaFirmaOrgArchivo: File | null = null;

  // ⭐ FIRMA Y HUELLA TRABAJADOR (placeholders estáticos)
  readonly FIRMA_TRABAJADOR_PLACEHOLDER = 'assets/images/firma_trabajador_placeholder.png';
  readonly FIRMA_TRABAJADOR_WIDTH = 150;
  readonly FIRMA_TRABAJADOR_HEIGHT = 50;

  readonly HUELLA_TRABAJADOR_PLACEHOLDER = 'assets/images/huella_trabajador_placeholder.png';
  readonly HUELLA_TRABAJADOR_WIDTH = 80;
  readonly HUELLA_TRABAJADOR_HEIGHT = 100;

  imagenFirmaEnEdicion: {
    element: HTMLElement;
    originalWidth: number;
    originalHeight: number;
    minWidth: number;
    minHeight: number;
  } | null = null;

  // Variables estáticas — firma_empleador ya NO está aquí, es dinámica
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
    { nombre: 'elementos_proteccion', valor: '', posX: 0, posY: 0, pagina: 1, colocada: false, ubicaciones: [] },
    { nombre: 'contacto_emergencia_nombre', valor: '', posX: 0, posY: 0, pagina: 1, colocada: false, ubicaciones: [] },
    { nombre: 'contacto_emergencia_telefono', valor: '', posX: 0, posY: 0, pagina: 1, colocada: false, ubicaciones: [] },
    // Firma y huella del TRABAJADOR (siempre disponibles con placeholder)
    { nombre: 'firma', valor: '', posX: 0, posY: 0, pagina: 1, colocada: false, ubicaciones: [] },
    { nombre: 'huella', valor: '', posX: 0, posY: 0, pagina: 1, colocada: false, ubicaciones: [] }
    // Las firmas/huellas de organización se agregan dinámicamente desde cargarFirmasOrganizacion()
  ];

  variablesPorPagina: Map<number, VariablePosicionada[]> = new Map();
  variableSeleccionada: VariableDocumento | null = null;
  modoColocacion: boolean = false;

  variableArrastrandose: VariablePosicionada | null = null;
  elementoArrastrandose: HTMLElement | null = null;
  offsetX: number = 0;
  offsetY: number = 0;
  paginaActualArrastre: HTMLElement | null = null;
  paginaNumeroArrastre: number = 0;

  private pdfDocument: any = null;
  modoModificacion: boolean = false;
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
      this.cargarFirmasOrganizacion();
    }
  }

  private getHoldingIdFromJWT(): string {
    try {
      const userInfo = this.jwtService.getUserInfo();
      const holdingId = userInfo?.holding_id;
      if (holdingId && holdingId !== null) {
        return holdingId.toString();
      }
      return '';
    } catch (error) {
      console.error('❌ Error extrayendo holding_id del JWT:', error);
      return '';
    }
  }

  // ============================================================
  // FIRMAS Y HUELLAS DE ORGANIZACIÓN
  // ============================================================

  getFirmaOrg(key: string): FirmaOrganizacion | undefined {
    return this.firmasOrganizacion.find(f => f.key === key);
  }

  cargarFirmasOrganizacion(): void {
    if (!this.holding) return;

    this.apiService.get(`api_firma_organizacion/?holding_id=${this.holding}`)
      .subscribe({
        next: (response: any) => {
          const lista: FirmaOrganizacion[] = response;
          this.firmasOrganizacion = lista;

          // Agregar al array de variables si no existe ya
          lista.forEach(f => {
            if (!this.variables.find(v => v.nombre === f.key)) {
              this.variables.push({
                nombre: f.key,
                valor: '', posX: 0, posY: 0, pagina: 1,
                colocada: false, ubicaciones: []
              });
            }
          });
        },
        error: (error) => {
          console.error('Error al cargar firmas de organización:', error);
        }
      });
  }

  onNuevaFirmaOrgFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files[0]) {
      this.nuevaFirmaOrgArchivo = input.files[0];
    }
  }

  agregarFirmaOrganizacion(): void {
    if (!this.nuevaFirmaOrgNombre.trim()) {
      alert('El nombre es obligatorio');
      return;
    }
    if (!this.nuevaFirmaOrgArchivo) {
      alert('Seleccione una imagen');
      return;
    }

    const formData = new FormData();
    formData.append('holding_id', this.holding);
    formData.append('tipo', this.nuevaFirmaOrgTipo);
    formData.append('nombre', this.nuevaFirmaOrgNombre.trim());
    formData.append('imagen', this.nuevaFirmaOrgArchivo);

    this.isLoading = true;
    this.apiService.postFormData('api_firma_organizacion/', formData)
      .subscribe({
        next: () => {
          this.mostrarModalNuevaFirmaOrg = false;
          this.nuevaFirmaOrgNombre = '';
          this.nuevaFirmaOrgArchivo = null;
          this.nuevaFirmaOrgTipo = 'firma';
          this.isLoading = false;
          this.cargarFirmasOrganizacion();
        },
        error: (error) => {
          console.error('Error al agregar firma:', error);
          alert(`Error: ${error.error?.error || 'No se pudo guardar'}`);
          this.isLoading = false;
        }
      });
  }

  eliminarFirmaOrganizacion(id: number, key: string): void {
    if (!confirm('¿Eliminar esta firma/huella?')) return;

    this.isLoading = true;
    this.apiService.delete(`api_firma_organizacion/?id=${id}`, {})
      .subscribe({
        next: () => {
          this.variables = this.variables.filter(v => v.nombre !== key);
          this.isLoading = false;
          this.cargarFirmasOrganizacion();
        },
        error: (error) => {
          console.error('Error al eliminar firma:', error);
          alert('No se pudo eliminar');
          this.isLoading = false;
        }
      });
  }

  // ============================================================
  // HELPERS
  // ============================================================

  variableEstaDisponible(variable: VariableDocumento): boolean {
    if (this.getFirmaOrg(variable.nombre)) return true;
    return true; // firma/huella trabajador siempre disponibles (placeholder)
  }

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
      'elementos_proteccion': 'Casco, guantes, zapatos de seguridad',
      'contacto_emergencia_nombre': 'María González',
      'contacto_emergencia_telefono': '+56 9 8765 4321',
      'firma': '[Firma Trabajador]',
      'huella': '[Huella Digital]'
    };

    if (ejemplos[nombreVariable]) return ejemplos[nombreVariable];

    const firmaOrg = this.getFirmaOrg(nombreVariable);
    if (firmaOrg) {
      return firmaOrg.tipo === 'firma'
        ? `[Firma: ${firmaOrg.nombre}]`
        : `[Huella: ${firmaOrg.nombre}]`;
    }

    return nombreVariable;
  }

  esCampocentrado(nombreVariable: string): boolean {
    const camposCentrados = ['rut', 'dni', 'nic', 'estado_civil', 'fecha_nacimiento', 'fecha_emision', 'fecha_ingreso', 'fecha_inicio_contrato', 'fecha_termino'];
    return camposCentrados.includes(nombreVariable);
  }

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
        resolve();
      } catch (error) {
        reject(error);
      }
    });
  }

  cargarDocumentosExistentes(): void {
    this.modoDocumentoExistente = true;
    this.isLoading = true;
    this.documentosCargados = [];
    this.documentoSeleccionado = null;
    this.modoModificacion = false;

    this.apiService.get('api_documento_nativo/')
      .subscribe({
        next: (response: any) => {
          if (Array.isArray(response)) {
            this.documentosCargados = response;
          }
          this.isLoading = false;
        },
        error: (error) => {
          console.error('Error al cargar documentos:', error);
          this.errorMessage = 'No se pudieron cargar los documentos existentes.';
          this.isLoading = false;
        }
      });
  }

  async anexarPDFDirecto(): Promise<void> {
    if (!this.isBrowser) return;

    this.ngZone.runOutsideAngular(async () => {
      try {
        const pdfjsLib = (window as any)['pdfjs-dist/build/pdf'];
        if (!pdfjsLib) {
          this.errorMessage = 'Error al cargar la librería PDF.js';
          this.isLoading = false;
          return;
        }
        const ultimoBuffer = this.pdfBuffers[this.pdfBuffers.length - 1];
        const loadingTask = pdfjsLib.getDocument({ data: ultimoBuffer });
        const pdfDoc = await loadingTask.promise;
        this.pdfDocuments.push(pdfDoc);

        let acumulado = 0;
        this.totalPagesAcumuladas = [];
        this.pdfDocuments.forEach(doc => {
          acumulado += doc.numPages;
          this.totalPagesAcumuladas.push(acumulado);
        });
        this.totalPages = acumulado;

        await this.renderizarTodasLasPaginas();
        this.ngZone.run(() => { this.isLoading = false; });
      } catch (error) {
        this.ngZone.run(() => {
          this.errorMessage = 'Error al anexar el PDF.';
          this.isLoading = false;
        });
      }
    });
  }

  async renderizarTodasLasPaginas(): Promise<void> {
    if (!this.isBrowser) return;

    const pagesContainer = document.getElementById('pdf-pages');
    if (!pagesContainer) return;

    pagesContainer.innerHTML = '';
    this.pdfPages = [];

    const containerWidth = pagesContainer.clientWidth || 800;
    const pixelRatio = window.devicePixelRatio || 1;

    for (let docIndex = 0; docIndex < this.pdfDocuments.length; docIndex++) {
      const pdfDoc = this.pdfDocuments[docIndex];
      const paginasAnteriores = docIndex > 0 ? this.totalPagesAcumuladas[docIndex - 1] : 0;

      for (let pageNum = 1; pageNum <= pdfDoc.numPages; pageNum++) {
        try {
          const pageNumGlobal = paginasAnteriores + pageNum;
          const page = await pdfDoc.getPage(pageNum);
          const viewport = page.getViewport({ scale: 1.0 });
          const scale = (containerWidth * 0.9) / viewport.width;
          const scaledViewport = page.getViewport({ scale: scale * 1.4 * pixelRatio });

          const pageDiv = document.createElement('div');
          pageDiv.className = 'pdf-page-container';

          const pageHeader = document.createElement('div');
          pageHeader.className = 'pdf-page-header';
          pageHeader.textContent = `PÁGINA ${pageNumGlobal}`;

          const pageContentDiv = document.createElement('div');
          pageContentDiv.className = 'pdf-page';
          pageContentDiv.setAttribute('data-page', pageNumGlobal.toString());
          pageContentDiv.style.width = `${scaledViewport.width / pixelRatio}px`;
          pageContentDiv.style.height = `${scaledViewport.height / pixelRatio}px`;

          const canvas = document.createElement('canvas');
          canvas.className = 'pdf-canvas';
          canvas.width = scaledViewport.width;
          canvas.height = scaledViewport.height;
          canvas.style.width = `${scaledViewport.width / pixelRatio}px`;
          canvas.style.height = `${scaledViewport.height / pixelRatio}px`;

          const context = canvas.getContext('2d', { alpha: false, willReadFrequently: true });
          if (!context) continue;

          await page.render({ canvasContext: context, viewport: scaledViewport, renderInteractiveForms: true }).promise;

          const pageFooter = document.createElement('div');
          pageFooter.className = 'pdf-page-footer';
          pageFooter.textContent = 'Haga clic para posicionar variables | Arrastre para mover';

          pageContentDiv.appendChild(canvas);
          pageDiv.appendChild(pageHeader);
          pageDiv.appendChild(pageContentDiv);
          pageDiv.appendChild(pageFooter);
          pagesContainer.appendChild(pageDiv);

          const nativeViewport = page.getViewport({ scale: 1.0 });
          this.pdfPages.push({
            pageNumber: pageNumGlobal,
            nativeWidth: nativeViewport.width,
            nativeHeight: nativeViewport.height,
            canvas, viewport: scaledViewport,
            container: pageContentDiv
          });
        } catch (error) {
          console.error(`Error al renderizar página ${pageNum}:`, error);
        }
      }
    }

    if (this.pdfDocuments.length > 0) {
      const firstPage = await this.pdfDocuments[0].getPage(1);
      const nativeViewport = firstPage.getViewport({ scale: 1.0 });
      this.pdfNativeWidth = nativeViewport.width;
      this.pdfNativeHeight = nativeViewport.height;
    }

    await new Promise(resolve => setTimeout(resolve, 100));

    this.ngZone.run(() => {
      setTimeout(() => {
        this.redibujarTodasLasVariables();
      }, 150);
    });
  }

  redibujarTodasLasVariables(): void {
    this.variablesPorPagina.forEach((variables, pageNum) => {
      const pageElement = document.querySelector(`[data-page="${pageNum}"]`) as HTMLElement;
      if (pageElement) {
        pageElement.querySelectorAll('.pdf-variable').forEach(el => el.remove());
        variables.forEach(variable => {
          this.mostrarVariableEnPdf(variable, pageElement);
        });
      }
    });
  }

  seleccionarDocumentoExistente(documento: any): void {
    this.documentoSeleccionado = documento;
    this.documentoGuardadoId = documento.id;
    this.isLoading = true;

    this.apiService.get(`api_documento_nativo/${documento.id}/`)
      .subscribe({
        next: (response: any) => {
          this.documentoSeleccionado = response;
          if (response.variables && Array.isArray(response.variables)) {
            this.cargarVariablesDesdeDocumento(response.variables);
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

  cargarVariablesDesdeDocumento(variablesDocumento: any[]): void {
    if (!variablesDocumento || variablesDocumento.length === 0) return;

    this.resetearVariables();

    variablesDocumento.forEach(varDoc => {
      // Asegurarse que la variable dinámica exista en el array
      let varIndex = this.variables.findIndex(v => v.nombre === varDoc.nombre);
      if (varIndex < 0) {
        // Puede ser una firma de organización no cargada aún; agregar
        this.variables.push({
          nombre: varDoc.nombre,
          valor: '', posX: 0, posY: 0, pagina: 1,
          colocada: false, ubicaciones: []
        });
        varIndex = this.variables.length - 1;
      }

      this.variables[varIndex].colocada = true;
      this.variables[varIndex].posX = varDoc.posX || 0;
      this.variables[varIndex].posY = varDoc.posY || 0;
      this.variables[varIndex].pagina = varDoc.pagina || 1;

      if (varDoc.ubicaciones && Array.isArray(varDoc.ubicaciones)) {
        this.variables[varIndex].ubicaciones = [...varDoc.ubicaciones];

        varDoc.ubicaciones.forEach((ubicacion: any) => {
          if (!this.variablesPorPagina.has(ubicacion.pagina)) {
            this.variablesPorPagina.set(ubicacion.pagina, []);
          }
          this.variablesPorPagina.get(ubicacion.pagina)?.push({
            nombre: varDoc.nombre,
            posX: ubicacion.posX,
            posY: ubicacion.posY,
            elementId: ubicacion.id || `var-${varDoc.nombre}-${Date.now()}`,
            variableIndex: varIndex
          });
        });
      }
    });
  }

  cargarPDFDesdeURL(pdfUrl: string): void {
    if (!pdfUrl) {
      this.errorMessage = 'No se encontró la URL del PDF';
      return;
    }

    this.isLoading = true;

    fetch(pdfUrl)
      .then(response => {
        if (!response.ok) throw new Error(`Error HTTP: ${response.status}`);
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
              this.actualizarInterfazModoModificacion();
            }
          });
        } else {
          this.isLoading = false;
        }
      })
      .catch(error => {
        this.errorMessage = `Error al cargar el PDF: ${error.message}`;
        this.isLoading = false;
      });
  }

  getNumeroVariables(): number {
    return this.variables.filter(v => v.colocada).length;
  }

  onFileSelected(event: Event, esAnexo: boolean = false): void {
    if (!this.isBrowser) return;

    const input = event.target as HTMLInputElement;
    if (input.files && input.files[0]) {
      const file = input.files[0];
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
          this.totalPagesAcumuladas = [];
          this.mostrarModalTipoContrato = true;
        } else {
          this.pdfBuffers.push(originalBuffer.slice(0));
          this.pdfFiles.push(file);
          this.anexarPDFDirecto();
        }
      };
      reader.onerror = () => {
        this.isLoading = false;
        this.errorMessage = 'Error al leer el archivo PDF.';
      };
      reader.readAsArrayBuffer(file);
    }
  }

  seleccionarVariable(variable: VariableDocumento): void {
    this.variableSeleccionada = variable;
    this.modoColocacion = true;

    const pdfContainer = document.getElementById('pdf-container');
    if (pdfContainer) {
      pdfContainer.style.cursor = 'crosshair';
      pdfContainer.addEventListener('click', this.handlePdfClick.bind(this), { once: true });
    }
  }

  calcularCoordenadasNativas(pageElement: HTMLElement, clientX: number, clientY: number): { posX: number, posY: number } {
    const pageRect = pageElement.getBoundingClientRect();
    const pixelX = clientX - pageRect.left;
    const pixelY = clientY - pageRect.top;
    const scaleX = this.pdfNativeWidth / pageRect.width;
    const scaleY = this.pdfNativeHeight / pageRect.height;
    return { posX: pixelX * scaleX, posY: pixelY * scaleY };
  }

  findClickedPage(event: MouseEvent): HTMLElement | null {
    const elements = document.elementsFromPoint(event.clientX, event.clientY);
    for (const element of elements) {
      if (element.classList.contains('pdf-page')) return element as HTMLElement;
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
    if (!this.variableArrastrandose || !this.elementoArrastrandose || !this.paginaActualArrastre) return;

    const finalX = parseInt(this.elementoArrastrandose.style.left);
    const finalY = parseInt(this.elementoArrastrandose.style.top);

    const coords = this.calcularCoordenadasNativas(
      this.paginaActualArrastre,
      finalX + this.paginaActualArrastre.getBoundingClientRect().left,
      finalY + this.paginaActualArrastre.getBoundingClientRect().top
    );

    const variablesList = this.variablesPorPagina.get(this.paginaNumeroArrastre) || [];
    const variableIndex = variablesList.findIndex(v => v.elementId === this.variableArrastrandose?.elementId);

    if (variableIndex !== -1) {
      variablesList[variableIndex].posX = coords.posX;
      variablesList[variableIndex].posY = coords.posY;

      const mainVarIndex = variablesList[variableIndex].variableIndex;
      if (mainVarIndex >= 0 && mainVarIndex < this.variables.length) {
        const variable = this.variables[mainVarIndex];
        const ubicacionIndex = variable.ubicaciones.findIndex(u => u.id === this.variableArrastrandose?.elementId);

        if (ubicacionIndex !== -1) {
          variable.ubicaciones[ubicacionIndex].posX = coords.posX;
          variable.ubicaciones[ubicacionIndex].posY = coords.posY;

          // Guardar dimensiones para imágenes (org firmas + trabajador)
          const esImagen = this.getFirmaOrg(variable.nombre) || variable.nombre === 'firma' || variable.nombre === 'huella';
          if (esImagen) {
            const elementRect = this.elementoArrastrandose!.getBoundingClientRect();
            const pageRect = this.paginaActualArrastre!.getBoundingClientRect();
            const scaleX = this.pdfNativeWidth / pageRect.width;
            const scaleY = this.pdfNativeHeight / pageRect.height;
            variable.ubicaciones[ubicacionIndex].width = elementRect.width * scaleX;
            variable.ubicaciones[ubicacionIndex].height = elementRect.height * scaleY;
          }
        }

        if (variable.ubicaciones.length > 0 && ubicacionIndex === variable.ubicaciones.length - 1) {
          variable.posX = coords.posX;
          variable.posY = coords.posY;
        }
      }
      this.haycambiosPendientes = true;
    }

    this.elementoArrastrandose.classList.remove('dragging');
    document.body.style.cursor = 'auto';
    this.variableArrastrandose = null;
    this.elementoArrastrandose = null;
    this.paginaActualArrastre = null;
    this.paginaNumeroArrastre = 0;
  }

  resetearVariables(): void {
    // Mantener solo variables estáticas; eliminar las dinámicas de org
    const nombresOrg = this.firmasOrganizacion.map(f => f.key);
    this.variables = this.variables.filter(v => !nombresOrg.includes(v.nombre));

    this.variables.forEach(variable => {
      variable.posX = 0;
      variable.posY = 0;
      variable.pagina = 1;
      variable.colocada = false;
      variable.ubicaciones = [];
    });

    this.variablesPorPagina.clear();
    document.querySelectorAll('.pdf-variable').forEach(el => el.remove());

    // Volver a agregar las dinámicas limpias
    this.firmasOrganizacion.forEach(f => {
      this.variables.push({
        nombre: f.key, valor: '', posX: 0, posY: 0,
        pagina: 1, colocada: false, ubicaciones: []
      });
    });
  }

  exportarPosiciones(): void {
    const posiciones: any[] = [];
    this.variables.forEach(variable => {
      variable.ubicaciones.forEach(ubicacion => {
        posiciones.push({
          variable: variable.nombre,
          posicion: { x: ubicacion.posX, y: ubicacion.posY, pagina: ubicacion.pagina }
        });
      });
    });
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
          if (!(window as any).pdfjsLib) {
            await this.loadPdfJsScript();
          }

          const pdfjsLib = (window as any).pdfjsLib;
          if (!pdfjsLib) throw new Error('No se pudo cargar PDF.js');

          const workerUrl = `https://cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjsLib.version}/pdf.worker.min.js`;
          pdfjsLib.GlobalWorkerOptions.workerSrc = workerUrl;

          const container = document.getElementById('pdf-container');
          if (!container) throw new Error('No se encontró #pdf-container');
          container.innerHTML = '';

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

          const firstPage = await pdf.getPage(1);
          const nativeViewport = firstPage.getViewport({ scale: 1.0 });
          this.pdfNativeWidth = nativeViewport.width;
          this.pdfNativeHeight = nativeViewport.height;

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

    for (let pageNum = startPage; pageNum <= endPage; pageNum++) {
      const pageDiv = document.createElement('div');
      pageDiv.className = 'pdf-page-container';

      const pageHeader = document.createElement('div');
      pageHeader.className = 'pdf-page-header';
      pageHeader.textContent = `PÁGINA ${pageNum}`;
      pageDiv.appendChild(pageHeader);

      const pageContentDiv = document.createElement('div');
      pageContentDiv.className = 'pdf-page';
      pageContentDiv.setAttribute('data-page', pageNum.toString());

      const page = await pdfDoc.getPage(pageNum);
      const viewport = page.getViewport({ scale: 1.0 });
      const scale = (containerWidth * 0.9) / viewport.width;
      const scaledViewport = page.getViewport({ scale: scale * 1.4 * pixelRatio });

      pageContentDiv.style.width = `${viewport.width / pixelRatio}px`;
      pageContentDiv.style.height = `${viewport.height / pixelRatio}px`;

      const canvas = document.createElement('canvas');
      canvas.className = 'pdf-canvas';
      canvas.width = scaledViewport.width;
      canvas.height = scaledViewport.height;
      canvas.style.width = `${scaledViewport.width / pixelRatio}px`;
      canvas.style.height = `${scaledViewport.height / pixelRatio}px`;

      const context = canvas.getContext('2d', { alpha: false, willReadFrequently: true });
      if (!context) continue;

      pageContentDiv.appendChild(canvas);
      pageDiv.appendChild(pageContentDiv);
      pagesContainer.appendChild(pageDiv);

      await page.render({ canvasContext: context, viewport: scaledViewport, renderInteractiveForms: true }).promise;
      await new Promise(resolve => setTimeout(resolve, 50));

      this.ngZone.run(() => {
        const variables = this.variablesPorPagina.get(pageNum) || [];
        variables.forEach(variable => {
          this.mostrarVariableEnPdf(variable, pageContentDiv);
        });
      });
    }
  }

  private loadPdfJsScript(): Promise<void> {
    return new Promise((resolve, reject) => {
      const pdfJsVersion = '3.4.120';
      const scriptSrc = `https://cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfJsVersion}/pdf.min.js`;
      if (document.querySelector(`script[src="${scriptSrc}"]`)) { resolve(); return; }
      const script = document.createElement('script');
      script.src = scriptSrc;
      script.onload = () => resolve();
      script.onerror = (e) => reject(new Error(`Error al cargar PDF.js: ${e}`));
      document.head.appendChild(script);
    });
  }

  handlePdfClick(event: MouseEvent): void {
    if (!this.variableSeleccionada || !this.modoColocacion) return;

    const clickedPage = this.findClickedPage(event);
    if (!clickedPage) return;

    const pageNumber = parseInt(clickedPage.getAttribute('data-page') || '0');
    if (pageNumber <= 0) return;

    const coords = this.calcularCoordenadasNativas(clickedPage, event.clientX, event.clientY);
    const variableIndex = this.variables.findIndex(v => v === this.variableSeleccionada);
    const elementId = `var-${this.variableSeleccionada.nombre}-${Date.now()}`;

    this.variableSeleccionada.posX = coords.posX;
    this.variableSeleccionada.posY = coords.posY;
    this.variableSeleccionada.pagina = pageNumber;
    this.variableSeleccionada.colocada = true;

    const pageData = this.pdfPages.find(p => p.pageNumber === pageNumber);
    this.variableSeleccionada.ubicaciones.push({
      pagina: pageNumber,
      posX: coords.posX,
      posY: coords.posY,
      id: elementId,
      pageWidth: pageData?.nativeWidth || this.pdfNativeWidth,
      pageHeight: pageData?.nativeHeight || this.pdfNativeHeight
    });

    if (!this.variablesPorPagina.has(pageNumber)) {
      this.variablesPorPagina.set(pageNumber, []);
    }
    this.variablesPorPagina.get(pageNumber)?.push({
      nombre: this.variableSeleccionada.nombre,
      posX: coords.posX,
      posY: coords.posY,
      elementId,
      variableIndex
    });

    this.mostrarVariableEnPdf({
      nombre: this.variableSeleccionada.nombre,
      posX: coords.posX,
      posY: coords.posY,
      elementId,
      variableIndex
    }, clickedPage);

    this.modoColocacion = false;
    document.getElementById('pdf-container')!.style.cursor = 'default';
    this.variableSeleccionada = null;

    if (this.modoModificacion) {
      this.actualizarInterfazModoModificacion();
    }
  }

  mostrarVariableEnPdf(variable: VariablePosicionada, pageElement: HTMLElement): void {
    if (this.pdfNativeWidth === 0 || this.pdfNativeHeight === 0) return;

    const pageRect = pageElement.getBoundingClientRect();
    if (pageRect.width === 0 || pageRect.height === 0) {
      setTimeout(() => this.mostrarVariableEnPdf(variable, pageElement), 100);
      return;
    }

    const scaleX = pageRect.width / this.pdfNativeWidth;
    const scaleY = pageRect.height / this.pdfNativeHeight;
    const displayX = variable.posX * scaleX;
    const displayY = variable.posY * scaleY;

    if (isNaN(displayX) || isNaN(displayY) || !isFinite(displayX) || !isFinite(displayY)) return;

    const variableElement = document.createElement('div');
    variableElement.className = 'pdf-variable';
    if (this.modoModificacion) variableElement.classList.add('edit-mode');

    const firmaOrg = this.getFirmaOrg(variable.nombre);
    const esFirmaTrabajador = variable.nombre === 'firma';
    const esHuellaTrabajador = variable.nombre === 'huella';

    const mainVariable = this.variables[variable.variableIndex];
    const ubicacion = mainVariable?.ubicaciones.find(u => u.id === variable.elementId);

    if (firmaOrg) {
      // ⭐ FIRMA O HUELLA DE ORGANIZACIÓN (dinámica)
      variableElement.classList.add(firmaOrg.tipo === 'firma' ? 'firma-org-imagen' : 'huella-org-imagen');

      let displayWidth = firmaOrg.tipo === 'firma' ? 150 : 80;
      let displayHeight = firmaOrg.tipo === 'firma' ? 50 : 100;

      if (ubicacion?.width && ubicacion?.height) {
        displayWidth = ubicacion.width * scaleX;
        displayHeight = ubicacion.height * scaleY;
      }

      const img = document.createElement('img');
      img.src = firmaOrg.imagen_url;
      img.style.width = `${displayWidth}px`;
      img.style.height = `${displayHeight}px`;
      img.style.objectFit = 'contain';
      img.style.display = 'block';
      img.style.pointerEvents = 'none';
      variableElement.appendChild(img);

      variableElement.style.backgroundColor = firmaOrg.tipo === 'firma'
        ? 'rgba(40, 167, 69, 0.08)' : 'rgba(59, 130, 246, 0.08)';
      variableElement.style.border = firmaOrg.tipo === 'firma'
        ? '2px dashed #28a745' : '2px dashed #3b82f6';

    } else if (esFirmaTrabajador) {
      // ⭐ FIRMA TRABAJADOR (placeholder)
      variableElement.classList.add('firma-trabajador-imagen');

      let displayWidth = this.FIRMA_TRABAJADOR_WIDTH;
      let displayHeight = this.FIRMA_TRABAJADOR_HEIGHT;
      if (ubicacion?.width && ubicacion?.height) {
        displayWidth = ubicacion.width * scaleX;
        displayHeight = ubicacion.height * scaleY;
      }

      const img = document.createElement('img');
      img.src = this.FIRMA_TRABAJADOR_PLACEHOLDER;
      img.style.width = `${displayWidth}px`;
      img.style.height = `${displayHeight}px`;
      img.style.objectFit = 'contain';
      img.style.display = 'block';
      img.style.pointerEvents = 'none';
      variableElement.appendChild(img);

      variableElement.style.backgroundColor = 'rgba(255, 152, 0, 0.08)';
      variableElement.style.border = '2px dashed #ff9800';

    } else if (esHuellaTrabajador) {
      // ⭐ HUELLA TRABAJADOR (placeholder)
      variableElement.classList.add('huella-trabajador-imagen');

      let displayWidth = this.HUELLA_TRABAJADOR_WIDTH;
      let displayHeight = this.HUELLA_TRABAJADOR_HEIGHT;
      if (ubicacion?.width && ubicacion?.height) {
        displayWidth = ubicacion.width * scaleX;
        displayHeight = ubicacion.height * scaleY;
      }

      const img = document.createElement('img');
      img.src = this.HUELLA_TRABAJADOR_PLACEHOLDER;
      img.style.width = `${displayWidth}px`;
      img.style.height = `${displayHeight}px`;
      img.style.objectFit = 'contain';
      img.style.display = 'block';
      img.style.pointerEvents = 'none';
      variableElement.appendChild(img);

      variableElement.style.backgroundColor = 'rgba(59, 130, 246, 0.08)';
      variableElement.style.border = '2px dashed #3b82f6';

    } else {
      // ⭐ VARIABLE DE TEXTO
      const textSpan = document.createElement('span');
      textSpan.textContent = this.obtenerValorEjemplo(variable.nombre);
      textSpan.style.pointerEvents = 'none';
      variableElement.appendChild(textSpan);

      variableElement.style.backgroundColor = 'rgba(74, 128, 245, 0.08)';
      variableElement.style.border = '1px dashed #4a80f5';
    }

    variableElement.id = variable.elementId;
    variableElement.setAttribute('data-variable', variable.nombre);
    variableElement.setAttribute('data-variable-index', variable.variableIndex.toString());
    variableElement.style.position = 'absolute';
    variableElement.style.left = `${displayX}px`;
    variableElement.style.top = `${displayY}px`;
    variableElement.style.fontFamily = 'Arial, sans-serif';
    variableElement.style.fontSize = '12px';
    variableElement.style.fontWeight = 'normal';
    variableElement.style.padding = '3px 6px';
    variableElement.style.borderRadius = '3px';
    variableElement.style.zIndex = '100';
    variableElement.style.whiteSpace = 'nowrap';
    variableElement.style.maxWidth = 'none';
    variableElement.style.pointerEvents = 'all';
    variableElement.style.cursor = 'move';

    // Centrado solo para variables de texto
    const esImagen = firmaOrg || esFirmaTrabajador || esHuellaTrabajador;
    if (!esImagen && this.esCampocentrado(variable.nombre)) {
      variableElement.style.textAlign = 'center';
      variableElement.style.transform = 'translateX(-50%)';
    } else {
      variableElement.style.textAlign = 'left';
      variableElement.style.transform = 'none';
    }

    pageElement.style.position = 'relative';
    pageElement.appendChild(variableElement);

    variableElement.addEventListener('mousedown', (event) => {
      this.handleVariableMouseDown(event, variable, variableElement, pageElement);
    });

    // Handles de redimensionamiento para imágenes
    if (esImagen) {
      this.agregarHandlesRedimension(variableElement, variable, pageElement);
    }

    // Botón eliminar
    const deleteBtn = document.createElement('div');
    deleteBtn.className = 'delete-btn';
    deleteBtn.innerHTML = '×';
    deleteBtn.title = 'Eliminar variable';
    deleteBtn.style.cssText = `
      position: absolute !important;
      top: -6px !important;
      right: -6px !important;
      width: 16px !important;
      height: 16px !important;
      background-color: #dc3545 !important;
      color: white !important;
      border: none !important;
      border-radius: 50% !important;
      cursor: pointer !important;
      font-size: 11px !important;
      line-height: 16px !important;
      display: flex !important;
      align-items: center !important;
      justify-content: center !important;
      z-index: 101 !important;
      box-shadow: 0 1px 3px rgba(0,0,0,0.3) !important;
      opacity: 0.9 !important;
    `;
    deleteBtn.addEventListener('click', (event) => {
      event.stopPropagation();
      this.eliminarVariable(variable.elementId, variable.variableIndex);
    });
    variableElement.appendChild(deleteBtn);
  }

  agregarHandlesRedimension(element: HTMLElement, variable: VariablePosicionada, pageElement: HTMLElement): void {
    const positions = ['top-left', 'top-right', 'bottom-left', 'bottom-right', 'top', 'right', 'bottom', 'left'];
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

  posicionarHandle(handle: HTMLElement, position: string): void {
    switch (position) {
      case 'top-left': handle.style.top = '-4px'; handle.style.left = '-4px'; break;
      case 'top-right': handle.style.top = '-4px'; handle.style.right = '-4px'; break;
      case 'bottom-left': handle.style.bottom = '-4px'; handle.style.left = '-4px'; break;
      case 'bottom-right': handle.style.bottom = '-4px'; handle.style.right = '-4px'; break;
      case 'top': handle.style.top = '-4px'; handle.style.left = 'calc(50% - 4px)'; break;
      case 'right': handle.style.right = '-4px'; handle.style.top = 'calc(50% - 4px)'; break;
      case 'bottom': handle.style.bottom = '-4px'; handle.style.left = 'calc(50% - 4px)'; break;
      case 'left': handle.style.left = '-4px'; handle.style.top = 'calc(50% - 4px)'; break;
    }
  }

  getCursorForHandle(position: string): string {
    const cursors: { [key: string]: string } = {
      'top-left': 'nwse-resize', 'top-right': 'nesw-resize',
      'bottom-left': 'nesw-resize', 'bottom-right': 'nwse-resize',
      'top': 'ns-resize', 'right': 'ew-resize',
      'bottom': 'ns-resize', 'left': 'ew-resize'
    };
    return cursors[position] || 'default';
  }

  iniciarRedimension(event: MouseEvent, element: HTMLElement, variable: VariablePosicionada, pageElement: HTMLElement, handlePosition: string): void {
    event.preventDefault();

    const startX = event.clientX;
    const startY = event.clientY;
    const startWidth = element.offsetWidth;
    const startHeight = element.offsetHeight;
    const startLeft = element.offsetLeft;
    const startTop = element.offsetTop;

    this.imagenFirmaEnEdicion = { element, originalWidth: startWidth, originalHeight: startHeight, minWidth: 50, minHeight: 20 };

    const onMouseMove = (e: MouseEvent) => {
      const deltaX = e.clientX - startX;
      const deltaY = e.clientY - startY;
      let newWidth = startWidth, newHeight = startHeight, newLeft = startLeft, newTop = startTop;

      switch (handlePosition) {
        case 'bottom-right': newWidth = Math.max(this.imagenFirmaEnEdicion!.minWidth, startWidth + deltaX); newHeight = Math.max(this.imagenFirmaEnEdicion!.minHeight, startHeight + deltaY); break;
        case 'bottom-left': newWidth = Math.max(this.imagenFirmaEnEdicion!.minWidth, startWidth - deltaX); newHeight = Math.max(this.imagenFirmaEnEdicion!.minHeight, startHeight + deltaY); newLeft = startLeft + (startWidth - newWidth); break;
        case 'top-right': newWidth = Math.max(this.imagenFirmaEnEdicion!.minWidth, startWidth + deltaX); newHeight = Math.max(this.imagenFirmaEnEdicion!.minHeight, startHeight - deltaY); newTop = startTop + (startHeight - newHeight); break;
        case 'top-left': newWidth = Math.max(this.imagenFirmaEnEdicion!.minWidth, startWidth - deltaX); newHeight = Math.max(this.imagenFirmaEnEdicion!.minHeight, startHeight - deltaY); newLeft = startLeft + (startWidth - newWidth); newTop = startTop + (startHeight - newHeight); break;
        case 'right': newWidth = Math.max(this.imagenFirmaEnEdicion!.minWidth, startWidth + deltaX); break;
        case 'left': newWidth = Math.max(this.imagenFirmaEnEdicion!.minWidth, startWidth - deltaX); newLeft = startLeft + (startWidth - newWidth); break;
        case 'bottom': newHeight = Math.max(this.imagenFirmaEnEdicion!.minHeight, startHeight + deltaY); break;
        case 'top': newHeight = Math.max(this.imagenFirmaEnEdicion!.minHeight, startHeight - deltaY); newTop = startTop + (startHeight - newHeight); break;
      }

      element.style.width = `${newWidth}px`;
      element.style.height = `${newHeight}px`;
      element.style.left = `${newLeft}px`;
      element.style.top = `${newTop}px`;
      const img = element.querySelector('img') as HTMLImageElement;
      if (img) { img.style.width = `${newWidth}px`; img.style.height = `${newHeight}px`; }
    };

    const onMouseUp = () => {
      document.removeEventListener('mousemove', onMouseMove);
      document.removeEventListener('mouseup', onMouseUp);

      const pageRect = pageElement.getBoundingClientRect();
      const scaleX = this.pdfNativeWidth / pageRect.width;
      const scaleY = this.pdfNativeHeight / pageRect.height;

      const nativeWidth = element.offsetWidth * scaleX;
      const nativeHeight = element.offsetHeight * scaleY;
      const nativeX = element.offsetLeft * scaleX;
      const nativeY = element.offsetTop * scaleY;

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
            mainVariable.ubicaciones[ubicacionIndex].width = nativeWidth;
            mainVariable.ubicaciones[ubicacionIndex].height = nativeHeight;
          }
        }
        this.haycambiosPendientes = true;
      }

      this.imagenFirmaEnEdicion = null;
    };

    document.addEventListener('mousemove', onMouseMove);
    document.addEventListener('mouseup', onMouseUp);
  }

  actualizarInterfazModoModificacion(): void {
    this.currentRetry = 0;
    this.intentarActualizarVariables();
  }

  private maxRetries = 5;
  private currentRetry = 0;

  private intentarActualizarVariables(): void {
    setTimeout(() => {
      const variables = document.querySelectorAll('.pdf-variable');
      if (variables.length === 0) {
        this.currentRetry++;
        if (this.currentRetry < this.maxRetries) this.intentarActualizarVariables();
        return;
      }

      variables.forEach(el => {
        el.classList.add('edit-mode');
        if (!el.querySelector('.delete-btn')) {
          const deleteBtn = document.createElement('div');
          deleteBtn.className = 'delete-btn';
          deleteBtn.innerHTML = '×';
          const variableId = el.id;
          const variableIndex = el.getAttribute('data-variable-index');
          deleteBtn.addEventListener('click', (event) => {
            event.stopPropagation();
            if (variableIndex !== null) this.eliminarVariable(variableId, parseInt(variableIndex));
          });
          el.appendChild(deleteBtn);
        }
      });
    }, 500 + (this.currentRetry * 300));
  }

  eliminarVariable(elementId: string, variableIndex: number): void {
    let paginaEncontrada = -1;

    this.variablesPorPagina.forEach((variables, pagina) => {
      if (variables.findIndex(v => v.elementId === elementId) !== -1) {
        paginaEncontrada = pagina;
      }
    });

    if (paginaEncontrada !== -1) {
      const variableElement = document.getElementById(elementId);
      if (variableElement) variableElement.remove();

      const variablesList = this.variablesPorPagina.get(paginaEncontrada);
      if (variablesList) {
        const indexInPage = variablesList.findIndex(v => v.elementId === elementId);
        if (indexInPage !== -1) variablesList.splice(indexInPage, 1);
      }

      if (variableIndex >= 0 && variableIndex < this.variables.length) {
        const variable = this.variables[variableIndex];
        const ubicacionIndex = variable.ubicaciones.findIndex(u => u.id === elementId);
        if (ubicacionIndex !== -1) variable.ubicaciones.splice(ubicacionIndex, 1);
        if (variable.ubicaciones.length === 0) variable.colocada = false;
      }

      this.haycambiosPendientes = true;
    }
  }

  modificarDocumentoSeleccionado(): void {
    if (!this.documentoSeleccionado || !this.documentoGuardadoId) {
      this.errorMessage = 'No hay un documento seleccionado para modificar';
      return;
    }

    const pdfUrl = this.documentoSeleccionado.archivo_pdf_url;
    this.modoDocumentoExistente = false;
    this.modoModificacion = true;

    const pdfContainer = document.getElementById('pdf-container');
    if (pdfContainer) pdfContainer.innerHTML = '';

    setTimeout(() => this.cargarPDFDesdeURL(pdfUrl), 100);
  }

  guardarCambiosDocumento(): void {
    if (!this.documentoGuardadoId) {
      alert('No se puede identificar el documento a modificar');
      return;
    }

    const variables = this.variables.filter(v => v.ubicaciones.length > 0).map(variable => ({
      nombre: variable.nombre,
      ubicaciones: variable.ubicaciones
    }));

    this.isLoading = true;
    this.apiService.put(`api_documento_nativo/${this.documentoGuardadoId}/`, { variables })
      .subscribe({
        next: () => {
          this.isLoading = false;
          this.modoModificacion = false;
          this.modoDocumentoExistente = true;
          this.haycambiosPendientes = false;
          alert('Documento actualizado exitosamente');
        },
        error: (error) => {
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
    if (this.documentoSeleccionado) this.seleccionarDocumentoExistente(this.documentoSeleccionado);
  }

  guardarFormato(): void {
    if (!this.originalPdfFile) { alert('Por favor, seleccione un archivo PDF primero'); return; }
    if (!this.variables.some(v => v.ubicaciones.length > 0)) {
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
    if (!this.nombreFormato.trim()) { alert('El nombre del formato es obligatorio'); return; }
    if (!this.originalPdfFile) { alert('No se encontró el archivo PDF original'); return; }

    const variables = this.variables.filter(v => v.ubicaciones.length > 0).map(variable => ({
      nombre: variable.nombre,
      ubicaciones: variable.ubicaciones
    }));

    const formData = new FormData();

    if (this.pdfFiles.length > 1) {
      this.pdfFiles.forEach((file, index) => formData.append(`pdf_parte_${index}`, file));
      formData.append('num_partes', this.pdfFiles.length.toString());
      formData.append('requiere_merge', 'true');
    } else {
      const nombreArchivo = this.nombreFormato.toLowerCase().replace(/\s+/g, '_') + '.pdf';
      const renamedFile = new File([this.originalPdfFile!], nombreArchivo, { type: 'application/pdf' });
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
          this.documentoGuardadoId = response.id;
          this.isLoading = false;
          this.haycambiosPendientes = false;
          alert('Formato guardado exitosamente');
          this.cerrarModal();
        },
        error: (error) => {
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
      const esImagen = this.getFirmaOrg(variable.nombre) || variable.nombre === 'firma' || variable.nombre === 'huella';
      if (esImagen) return; // Las imágenes no necesitan datos de prueba

      let tipo = 'normal';
      if (variable.nombre.includes('fecha')) tipo = 'fecha';

      this.variablesConDatos.push({
        nombre: variable.nombre,
        tipo,
        valorPredeterminado: this.obtenerValorEjemplo(variable.nombre),
        valorPrueba: this.obtenerValorEjemplo(variable.nombre)
      });
    });

    if (this.variablesConDatos.length > 0) {
      this.mostrarModalDatosPrueba = true;
    } else {
      alert('No hay variables de texto colocadas en el documento');
    }
  }

  get variablesFiltradas(): VariableDocumento[] {
    if (this.tipoContrato === 'CHILENO') {
      return this.variables.filter(v => v.nombre !== 'dni' && v.nombre !== 'nic');
    } else {
      return this.variables.filter(v => v.nombre !== 'rut');
    }
  }

  confirmarTipoContrato(): void {
    this.mostrarModalTipoContrato = false;
    this.renderPdf();
  }

  cerrarModalTipoContrato(): void {
    this.mostrarModalTipoContrato = false;
    this.pdfSrc = null;
    this.originalPdfFile = null;
  }

  cerrarModalDatosPrueba(): void {
    this.mostrarModalDatosPrueba = false;
  }

  confirmarGenerarPDF(): void {
    if (!this.documentoGuardadoId) { alert('No se encontró el ID del documento'); return; }

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
        const blobUrl = URL.createObjectURL(blob);
        this.pdfPreviewUrl = blobUrl;
        window.open(blobUrl, '_blank');
        this.isLoading = false;
        this.mostrarModalDatosPrueba = false;
        setTimeout(() => URL.revokeObjectURL(blobUrl), 60000);
      },
      error: () => {
        alert('Error: No se pudo generar el PDF');
        this.isLoading = false;
      }
    });
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
    if (!this.documentoGuardadoId) { alert('No se puede identificar el documento'); return; }

    const variables = this.variables.filter(v => v.ubicaciones.length > 0).map(variable => ({
      nombre: variable.nombre,
      ubicaciones: variable.ubicaciones
    }));

    this.isLoading = true;
    this.apiService.put(`api_documento_nativo/${this.documentoGuardadoId}/`, { variables })
      .subscribe({
        next: () => {
          this.isLoading = false;
          this.haycambiosPendientes = false;
          alert('Posiciones guardadas.');
        },
        error: (error) => {
          alert(`Error: ${error.error?.error || 'No se pudieron guardar las posiciones'}`);
          this.isLoading = false;
        }
      });
  }
}