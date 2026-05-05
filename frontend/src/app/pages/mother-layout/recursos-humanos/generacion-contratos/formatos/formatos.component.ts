//formatos.component.ts
import { Component, Inject, NgZone, OnInit, PLATFORM_ID, ViewChild } from '@angular/core';
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
export class FormatosComponent implements OnInit {
  pdfSrc: string | ArrayBuffer | null = null;
  isLoading = false;
  isBrowser: boolean;
  errorMessage: string | null = null;
  public holding: string = '';

  // Store the original File object
  originalPdfFile: File | null = null;
  // Array para almacenar múltiples PDFs
  pdfDocuments: any[] = [];
  pdfBuffers: ArrayBuffer[] = [];
  pdfFiles: File[] = [];
  totalPages: number = 0;
  pdfPages: any[] = [];
  totalPagesAcumuladas: number[] = []; // Páginas acumuladas por cada PDF
  
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
  
  //Propiedades Elemento Seguridad
  elementosSeguridad: string[] = [];
  mostrarModalElementoSeguridad: boolean = false;
  elementoSeleccionadoTemp: string = '';
  variableBuscada: string = '';

  // ⭐ PROPIEDADES PARA FIRMA EMPLEADOR
  firmaEmpleadorDisponible: boolean = false;
  firmaEmpleadorUrl: string | null = null;
  mostrarModalFirmaEmpleador: boolean = false;
  
  // ⭐ PROPIEDADES PARA FIRMA TRABAJADOR (PLACEHOLDER)
  readonly FIRMA_TRABAJADOR_PLACEHOLDER = 'assets/images/firma_trabajador_placeholder.png';
  readonly FIRMA_TRABAJADOR_WIDTH = 150;
  readonly FIRMA_TRABAJADOR_HEIGHT = 50;
  
  // ⭐ NUEVO: PROPIEDADES PARA HUELLA TRABAJADOR (PLACEHOLDER)
  readonly HUELLA_TRABAJADOR_PLACEHOLDER = 'assets/images/huella_trabajador_placeholder.png';
  readonly HUELLA_TRABAJADOR_WIDTH = 80;
  readonly HUELLA_TRABAJADOR_HEIGHT = 100;
  
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
    { nombre: 'nombre_cliente', valor:'', posX: 0, posY: 0, pagina: 1, colocada: false, ubicaciones: [] },
    { nombre: 'nombre_campo', valor:'', posX: 0, posY: 0, pagina: 1, colocada: false, ubicaciones: [] },
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
    { nombre: 'firma_empleador', valor: '', posX: 0, posY: 0, pagina: 1, colocada: false, ubicaciones: [] },
    { nombre: 'firma', valor: '', posX: 0, posY: 0, pagina: 1, colocada: false, ubicaciones: [] },
    { nombre: 'huella', valor: '', posX: 0, posY: 0, pagina: 1, colocada: false, ubicaciones: [] },
    { nombre: 'elemento_seguridad', valor: '', posX: 0, posY: 0, pagina: 1, colocada: false, ubicaciones: [] },

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
      this.cargarElementosSeguridad();
    }
  }

   private getHoldingIdFromJWT(): string {
    try {
      const userInfo = this.jwtService.getUserInfo();
      const holdingId = userInfo?.holding_id;
      
      console.log('🔍 Holding ID del JWT:', holdingId);
      
      if (holdingId && holdingId !== null ) {
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

  cargarElementosSeguridad(): void {
    this.apiService.get('api_elemento_seguridad/')
      .subscribe({
        next: (response: any) => {
          this.elementosSeguridad = Array.isArray(response) ? response : [];
        },
        error: (error) => {
          console.error('Error al cargar elementos de seguridad:', error);
        }
      });
  }

  confirmarElementoSeguridad(): void {
    if (!this.elementoSeleccionadoTemp) return;
    this.mostrarModalElementoSeguridad = false;
    this.modoColocacion = true;
    const pdfContainer = document.getElementById('pdf-container');
    if (pdfContainer) {
      pdfContainer.style.cursor = 'crosshair';
      pdfContainer.addEventListener('click', this.handlePdfClick.bind(this), { once: true });
    }
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
  
  /**
   * Verificar si variable está disponible
   */
  variableEstaDisponible(variable: VariableDocumento): boolean {
    if (variable.nombre === 'firma_empleador') {
      return this.firmaEmpleadorDisponible;
    }
    // ⭐ FIRMA Y HUELLA TRABAJADOR: siempre disponibles (son placeholders)
    return true;
  }

  /**
   * Obtener valor de ejemplo realista para cada variable
   */
  obtenerValorEjemplo(nombreVariable: string): string {
    const ejemplos: {[key: string]: string} = {
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
      'firma_empleador': '[Firma Empleador]',
      'firma': '[Firma Trabajador]',
      'huella': '[Huella Digital]',
      'elemento_seguridad': '[Elemento de Seguridad]',

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
          console.error('PDF.js no está disponible');
          this.errorMessage = 'Error al cargar la librería PDF.js';
          this.isLoading = false;
          return;
        }

        const ultimoBuffer = this.pdfBuffers[this.pdfBuffers.length - 1];
        const loadingTask = pdfjsLib.getDocument({ data: ultimoBuffer });
        const pdfDoc = await loadingTask.promise;
        
        console.log(`✅ PDF anexado cargado - ${pdfDoc.numPages} páginas`);
        
        this.pdfDocuments.push(pdfDoc);
        
        let acumulado = 0;
        this.totalPagesAcumuladas = [];
        this.pdfDocuments.forEach(doc => {
          acumulado += doc.numPages;
          this.totalPagesAcumuladas.push(acumulado);
        });
        
        this.totalPages = acumulado;
        
        await this.renderizarTodasLasPaginas();
        
        this.ngZone.run(() => {
          this.isLoading = false;
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
    
    const containerWidth = pagesContainer.clientWidth || 800;
    const pixelRatio = window.devicePixelRatio || 1;
    
    console.log(`📄 Renderizando ${this.pdfDocuments.length} documentos...`);

    for (let docIndex = 0; docIndex < this.pdfDocuments.length; docIndex++) {
      const pdfDoc = this.pdfDocuments[docIndex];
      const paginasAnteriores = docIndex > 0 ? this.totalPagesAcumuladas[docIndex - 1] : 0;
      
      console.log(`📘 Documento ${docIndex + 1}: ${pdfDoc.numPages} páginas (offset: ${paginasAnteriores})`);
      
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
          
          await page.render({
            canvasContext: context,
            viewport: scaledViewport,
            renderInteractiveForms: true
          }).promise;
          
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
            canvas: canvas,
            viewport: scaledViewport,
            container: pageContentDiv
          });
          
          console.log(`✅ Página ${pageNumGlobal} renderizada (Doc ${docIndex + 1}, Pág ${pageNum})`);
          
        } catch (error) {
          console.error(`Error al renderizar página ${pageNum} del documento ${docIndex + 1}:`, error);
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
      const varIndex = this.variables.findIndex(v => v.nombre === varDoc.nombre);
      
      if (varIndex >= 0) {
        this.variables[varIndex].colocada = true;
        this.variables[varIndex].posX = varDoc.posX || 0;
        this.variables[varIndex].posY = varDoc.posY || 0;
        this.variables[varIndex].pagina = varDoc.pagina || 1;
        
        if (varDoc.ubicaciones && Array.isArray(varDoc.ubicaciones)) {
          this.variables[varIndex].ubicaciones = [...varDoc.ubicaciones];
          
          varDoc.ubicaciones.forEach((ubicacion: { pagina: number; posX: any; posY: any; id: any; }) => {
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
      }
    });
  }

  /**
   * Carga el PDF desde una URL e inicializa dimensiones SIEMPRE
   */
  cargarPDFDesdeURL(pdfUrl: string): void {
    if (!pdfUrl) {
      this.errorMessage = 'No se encontró la URL del PDF';
      return;
    }

    pdfUrl = pdfUrl.replace('http://', 'https://');
    
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
      reader.onerror = (error) => {
        console.error('Error al leer el archivo:', error);
        this.isLoading = false;
        this.errorMessage = 'Error al leer el archivo PDF.';
      };
      reader.readAsArrayBuffer(file);
    }
  }

  seleccionarVariable(variable: VariableDocumento): void {
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

    this.variableSeleccionada = variable;
    this.modoColocacion = true;
    const pdfContainer = document.getElementById('pdf-container');
    if (pdfContainer) {
      pdfContainer.style.cursor = 'crosshair';
      pdfContainer.addEventListener('click', this.handlePdfClick.bind(this), { once: true });
    }
  }

  /**
   * Calcular coordenadas nativas del PDF (sin escalado)
   */
  calcularCoordenadasNativas(pageElement: HTMLElement, clientX: number, clientY: number): {posX: number, posY: number} {
    const pageRect = pageElement.getBoundingClientRect();
    
    const pixelX = clientX - pageRect.left;
    const pixelY = clientY - pageRect.top;
    
    const scaleX = this.pdfNativeWidth / pageRect.width;
    const scaleY = this.pdfNativeHeight / pageRect.height;
    
    const nativeX = pixelX * scaleX;
    const nativeY = pixelY * scaleY;
    
    console.log(`Coordenadas nativas: (${nativeX}, ${nativeY}) desde píxeles (${pixelX}, ${pixelY})`);
    
    return {
      posX: nativeX,
      posY: nativeY
    };
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
    if (!this.variableArrastrandose || !this.elementoArrastrandose || !this.paginaActualArrastre) return;
    
    const finalX = parseInt(this.elementoArrastrandose.style.left);
    const finalY = parseInt(this.elementoArrastrandose.style.top);
    
    const coords = this.calcularCoordenadasNativas(this.paginaActualArrastre, 
      finalX + this.paginaActualArrastre.getBoundingClientRect().left, 
      finalY + this.paginaActualArrastre.getBoundingClientRect().top);
    
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
          
          // ⭐ Guardar dimensiones para firma_empleador, firma Y huella
          if (variable.nombre === 'firma_empleador' || variable.nombre === 'firma' || variable.nombre === 'huella') {
            const elementRect = this.elementoArrastrandose!.getBoundingClientRect();
            const pageRect = this.paginaActualArrastre!.getBoundingClientRect();
            
            const scaleX = this.pdfNativeWidth / pageRect.width;
            const scaleY = this.pdfNativeHeight / pageRect.height;
            
            const nativeWidth = elementRect.width * scaleX;
            const nativeHeight = elementRect.height * scaleY;
            
            variable.ubicaciones[ubicacionIndex].width = nativeWidth;
            variable.ubicaciones[ubicacionIndex].height = nativeHeight;
            
            console.log(`✅ Dimensiones guardadas al arrastrar ${variable.nombre}: ${nativeWidth}x${nativeHeight}`);
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
    this.variables.forEach(variable => {
      variable.posX = 0;
      variable.posY = 0;
      variable.pagina = 1;
      variable.colocada = false;
      variable.ubicaciones = [];
    });
    
    this.variablesPorPagina.clear();
    
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
    if (this.variableSeleccionada && this.modoColocacion) {
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
        pageHeight: pageData?.nativeHeight || this.pdfNativeHeight,
        ...(this.variableSeleccionada.nombre === 'elemento_seguridad' && { valor: this.elementoSeleccionadoTemp })
      });
      
      if (!this.variablesPorPagina.has(pageNumber)) {
        this.variablesPorPagina.set(pageNumber, []);
      }
      
      this.variablesPorPagina.get(pageNumber)?.push({
        nombre: this.variableSeleccionada.nombre,
        posX: coords.posX, 
        posY: coords.posY,
        elementId: elementId,
        variableIndex: variableIndex
      });
      
      this.mostrarVariableEnPdf({
        nombre: this.variableSeleccionada.nombre,
        posX: coords.posX,
        posY: coords.posY,
        elementId: elementId,
        variableIndex: variableIndex
      }, clickedPage);
      
      this.modoColocacion = false;
      document.getElementById('pdf-container')!.style.cursor = 'default';
      this.variableSeleccionada = null;
      
      if (this.modoModificacion) {
        this.actualizarInterfazModoModificacion();
      }
    }
  }

  /**
   * ⭐ MODIFICADO: Mostrar variable en PDF (soporta firma_empleador, firma Y huella como imágenes)
   */
  mostrarVariableEnPdf(variable: VariablePosicionada, pageElement: HTMLElement): void {
    
    console.log(`🔄 Intentando renderizar variable "${variable.nombre}"...`);
    
    if (this.pdfNativeWidth === 0 || this.pdfNativeHeight === 0) {
      console.error('❌ ERROR: Dimensiones nativas no inicializadas');
      return;
    }
    
    const pageRect = pageElement.getBoundingClientRect();
    if (pageRect.width === 0 || pageRect.height === 0) {
      console.error(`❌ ERROR: pageElement no tiene dimensiones válidas`);
      setTimeout(() => {
        console.log(`🔁 Reintentando renderizar "${variable.nombre}"...`);
        this.mostrarVariableEnPdf(variable, pageElement);
      }, 100);
      return;
    }
    
    const variableElement = document.createElement('div');
    variableElement.className = 'pdf-variable';
    if (this.modoModificacion) {
      variableElement.classList.add('edit-mode');
    }
    
    // ⭐ CASO 1: firma_empleador es IMAGEN
    if (variable.nombre === 'firma_empleador') {
      if (!this.firmaEmpleadorDisponible || !this.firmaEmpleadorUrl) {
        console.warn('⚠️ firma_empleador no disponible');
        return;
      }
      
      variableElement.classList.add('firma-empleador-imagen');
      
      const img = document.createElement('img');
      img.src = this.firmaEmpleadorUrl;
      
      const mainVarIndex = variable.variableIndex;
      const mainVariable = this.variables[mainVarIndex];
      const ubicacion = mainVariable.ubicaciones.find(u => u.id === variable.elementId);
      
      const scaleX = pageRect.width / this.pdfNativeWidth;
      const scaleY = pageRect.height / this.pdfNativeHeight;
      
      let displayWidth = 150;
      let displayHeight = 50;
      
      if (ubicacion && ubicacion.width && ubicacion.height) {
        displayWidth = ubicacion.width * scaleX;
        displayHeight = ubicacion.height * scaleY;
        console.log(`✅ Usando dimensiones guardadas firma_empleador: ${displayWidth.toFixed(1)}x${displayHeight.toFixed(1)}px`);
      }
      
      img.style.width = `${displayWidth}px`;
      img.style.height = `${displayHeight}px`;
      img.style.objectFit = 'contain';
      img.style.display = 'block';
      img.style.pointerEvents = 'none';
      
      img.onerror = () => {
        console.error('❌ Error al cargar imagen firma_empleador');
        img.alt = '[Error: No se pudo cargar la firma]';
        img.style.border = '2px solid red';
      };
      
      img.onload = () => {
        console.log('✅ Imagen firma_empleador cargada');
      };
      
      variableElement.appendChild(img);
      
    } 
    // ⭐ CASO 2: firma trabajador es IMAGEN PLACEHOLDER
    else if (variable.nombre === 'firma') {
      variableElement.classList.add('firma-trabajador-imagen');
      
      const img = document.createElement('img');
      img.src = this.FIRMA_TRABAJADOR_PLACEHOLDER;
      
      const mainVarIndex = variable.variableIndex;
      const mainVariable = this.variables[mainVarIndex];
      const ubicacion = mainVariable.ubicaciones.find(u => u.id === variable.elementId);
      
      const scaleX = pageRect.width / this.pdfNativeWidth;
      const scaleY = pageRect.height / this.pdfNativeHeight;
      
      let displayWidth = this.FIRMA_TRABAJADOR_WIDTH;
      let displayHeight = this.FIRMA_TRABAJADOR_HEIGHT;
      
      if (ubicacion && ubicacion.width && ubicacion.height) {
        displayWidth = ubicacion.width * scaleX;
        displayHeight = ubicacion.height * scaleY;
        console.log(`✅ Usando dimensiones guardadas firma: ${displayWidth.toFixed(1)}x${displayHeight.toFixed(1)}px`);
      }
      
      img.style.width = `${displayWidth}px`;
      img.style.height = `${displayHeight}px`;
      img.style.objectFit = 'contain';
      img.style.display = 'block';
      img.style.pointerEvents = 'none';
      
      img.onerror = () => {
        console.error('❌ Error al cargar imagen placeholder firma');
        img.alt = '[Error: No se pudo cargar placeholder]';
        img.style.border = '2px solid red';
      };
      
      img.onload = () => {
        console.log('✅ Imagen placeholder firma cargada');
      };
      
      variableElement.appendChild(img);
      
    }
    // ⭐ NUEVO CASO 3: huella trabajador es IMAGEN PLACEHOLDER
    else if (variable.nombre === 'huella') {
      variableElement.classList.add('huella-trabajador-imagen');
      
      const img = document.createElement('img');
      img.src = this.HUELLA_TRABAJADOR_PLACEHOLDER;
      
      const mainVarIndex = variable.variableIndex;
      const mainVariable = this.variables[mainVarIndex];
      const ubicacion = mainVariable.ubicaciones.find(u => u.id === variable.elementId);
      
      const scaleX = pageRect.width / this.pdfNativeWidth;
      const scaleY = pageRect.height / this.pdfNativeHeight;
      
      let displayWidth = this.HUELLA_TRABAJADOR_WIDTH;
      let displayHeight = this.HUELLA_TRABAJADOR_HEIGHT;
      
      if (ubicacion && ubicacion.width && ubicacion.height) {
        displayWidth = ubicacion.width * scaleX;
        displayHeight = ubicacion.height * scaleY;
        console.log(`✅ Usando dimensiones guardadas huella: ${displayWidth.toFixed(1)}x${displayHeight.toFixed(1)}px`);
      }
      
      img.style.width = `${displayWidth}px`;
      img.style.height = `${displayHeight}px`;
      img.style.objectFit = 'contain';
      img.style.display = 'block';
      img.style.pointerEvents = 'none';
      
      img.onerror = () => {
        console.error('❌ Error al cargar imagen placeholder huella');
        img.alt = '[Error: No se pudo cargar placeholder]';
        img.style.border = '2px solid red';
      };
      
      img.onload = () => {
        console.log('✅ Imagen placeholder huella cargada');
      };
      
      variableElement.appendChild(img);
      
    } else {
      const ubicacion = this.variables[variable.variableIndex]?.ubicaciones.find(u => u.id === variable.elementId);
      const textoMostrar = (variable.nombre === 'elemento_seguridad' && ubicacion?.valor)
        ? ubicacion.valor
        : this.obtenerValorEjemplo(variable.nombre);
      const textSpan = document.createElement('span');
      textSpan.textContent = textoMostrar;
      textSpan.style.pointerEvents = 'none';
      variableElement.appendChild(textSpan);
    }
    
    variableElement.id = variable.elementId;
    variableElement.setAttribute('data-variable', variable.nombre);
    variableElement.setAttribute('data-variable-index', variable.variableIndex.toString());
    variableElement.style.position = 'absolute';
    
    const scaleX = pageRect.width / this.pdfNativeWidth;
    const scaleY = pageRect.height / this.pdfNativeHeight;
    
    const displayX = variable.posX * scaleX;
    const displayY = variable.posY * scaleY;
    
    console.log(`📍 Variable "${variable.nombre}" - Posición:`, {
      nativas: { x: variable.posX, y: variable.posY },
      display: { x: displayX, y: displayY },
      escala: { scaleX, scaleY }
    });
    
    if (isNaN(displayX) || isNaN(displayY) || !isFinite(displayX) || !isFinite(displayY)) {
      console.error(`❌ ERROR: Coordenadas display inválidas`);
      return;
    }
    
    variableElement.style.left = `${displayX}px`;
    variableElement.style.top = `${displayY}px`;
    
    // ⭐ ESTILOS BASE
    variableElement.style.fontFamily = 'Arial, sans-serif';
    variableElement.style.fontSize = '12px';
    variableElement.style.fontWeight = 'normal';
    variableElement.style.padding = '3px 6px';
    
    // ⭐ COLORES DIFERENTES PARA CADA TIPO
    if (variable.nombre === 'firma_empleador') {
      variableElement.style.backgroundColor = 'rgba(40, 167, 69, 0.08)';
      variableElement.style.border = '2px dashed #28a745';
    } else if (variable.nombre === 'firma') {
      variableElement.style.backgroundColor = 'rgba(255, 152, 0, 0.08)';
      variableElement.style.border = '2px dashed #ff9800';
    } else if (variable.nombre === 'huella') {
      variableElement.style.backgroundColor = 'rgba(59, 130, 246, 0.08)';
      variableElement.style.border = '2px dashed #3b82f6';
    } else {
      variableElement.style.backgroundColor = 'rgba(74, 128, 245, 0.08)';
      variableElement.style.border = '1px dashed #4a80f5';
    }
    
    variableElement.style.borderRadius = '3px';
    variableElement.style.zIndex = '100';
    variableElement.style.whiteSpace = 'nowrap';
    variableElement.style.maxWidth = 'none';
    
    if (this.esCampocentrado(variable.nombre) && variable.nombre !== 'firma_empleador' && variable.nombre !== 'firma' && variable.nombre !== 'huella') {
      variableElement.style.textAlign = 'center';
      variableElement.style.transform = 'translateX(-50%)';
    } else {
      variableElement.style.textAlign = 'left';
      variableElement.style.transform = 'none';
    }
    
    variableElement.style.pointerEvents = 'all';
    variableElement.style.cursor = 'move';
    
    pageElement.style.position = 'relative';
    pageElement.appendChild(variableElement);
    
    console.log(`✅ Variable "${variable.nombre}" renderizada exitosamente`);
    
    variableElement.addEventListener('mousedown', (event) => {
      this.handleVariableMouseDown(event, variable, variableElement, pageElement);
    });
    
    // ⭐ Agregar handles de redimensionamiento SOLO para firma_empleador, firma Y huella
    if (variable.nombre === 'firma_empleador' || variable.nombre === 'firma' || variable.nombre === 'huella') {
      this.agregarHandlesRedimension(variableElement, variable, pageElement);
    }
    
    // ⭐ Botón de eliminar
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
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3) !important;
      opacity: 0.9 !important;
    `;
    
    deleteBtn.addEventListener('click', (event) => {
      event.stopPropagation();
      console.log(`🗑️ Eliminando variable "${variable.nombre}"...`);
      this.eliminarVariable(variable.elementId, variable.variableIndex);
    });
    
    variableElement.appendChild(deleteBtn);
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
    switch(position) {
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
  
  /**
   * Obtener cursor apropiado
   */
  getCursorForHandle(position: string): string {
    const cursors: {[key: string]: string} = {
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
      
      switch(handlePosition) {
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
      
      const pageRect = pageElement.getBoundingClientRect();
      const scaleX = this.pdfNativeWidth / pageRect.width;
      const scaleY = this.pdfNativeHeight / pageRect.height;
      
      const finalWidth = element.offsetWidth;
      const finalHeight = element.offsetHeight;
      const finalLeft = element.offsetLeft;
      const finalTop = element.offsetTop;
      
      const nativeWidth = finalWidth * scaleX;
      const nativeHeight = finalHeight * scaleY;
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
            mainVariable.ubicaciones[ubicacionIndex].width = nativeWidth;
            mainVariable.ubicaciones[ubicacionIndex].height = nativeHeight;
          }
        }
        
        this.haycambiosPendientes = true;
      }
      
      console.log(`✅ ${variable.nombre} redimensionada: ${nativeWidth}x${nativeHeight} en (${nativeX}, ${nativeY})`);
      
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
    let variableEncontrada = null;
    
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
    
    if (this.variablesPorPagina.size === 0) {
      this.errorMessage = 'El documento no tiene variables para modificar';
      return;
    }
    
    console.log('📝 Iniciando modificación de documento:', this.documentoSeleccionado.nombre);
    console.log('Variables cargadas en memoria:', this.variablesPorPagina.size, 'páginas');
    
    const pdfUrl = this.documentoSeleccionado.archivo_pdf_url;
    
    this.modoDocumentoExistente = false;
    this.modoModificacion = true;
    
    const pdfContainer = document.getElementById('pdf-container');
    if (pdfContainer) {
      pdfContainer.innerHTML = '';
    }
    
    setTimeout(() => {
      console.log('🔄 Cargando PDF para modificación...');
      this.cargarPDFDesdeURL(pdfUrl);
    }, 100);
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
    
    const variables = this.variables.filter(v => v.ubicaciones.length > 0).map(variable => ({
      nombre: variable.nombre,
      ubicaciones: variable.ubicaciones
    }));
    
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
    } else {
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
  }
  
  cerrarModalDatosPrueba(): void {
    this.mostrarModalDatosPrueba = false;
  }
  
  confirmarGenerarPDF(): void {
    if (!this.documentoGuardadoId) {
      alert('No se encontró el ID del documento');
      return;
    }
    
    const datosVariables: {[key: string]: string} = {};
    
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
    
    const variables = this.variables.filter(v => v.ubicaciones.length > 0).map(variable => ({
      nombre: variable.nombre,
      ubicaciones: variable.ubicaciones
    }));
    
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