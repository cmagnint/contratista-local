//formatos.component.ts
import { Component, Inject, NgZone, OnInit, PLATFORM_ID, ViewChild } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ContratistaApiService } from '../../../../../services/contratista-api.service';

// Interfaz para una ubicación específica de una variable
interface Ubicacion {
  pagina: number;
  posX: number;
  posY: number;
  id: string;
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
  
  // Store the original File object
  originalPdfFile: File | null = null;
  
  // Modal properties
  mostrarModal = false;
  nombreFormato = '';
  tipoContrato = 'CHILENO';
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
  
  // Variables de documento con array de ubicaciones
  variables: VariableDocumento[] = [
    { nombre: 'nombre', valor: '', posX: 0, posY: 0, pagina: 1, colocada: false, ubicaciones: [] },
    { nombre: 'rut', valor: '', posX: 0, posY: 0, pagina: 1, colocada: false, ubicaciones: [] },
    { nombre: 'dni', valor: '', posX: 0, posY: 0, pagina: 1, colocada: false, ubicaciones: [] },
    { nombre: 'f_inicio', valor: '', posX: 0, posY: 0, pagina: 1, colocada: false, ubicaciones: [] },
    { nombre: 'f_ingreso', valor: '', posX: 0, posY: 0, pagina: 1, colocada: false, ubicaciones: [] },
    { nombre: 'f_termino', valor: '', posX: 0, posY: 0, pagina: 1, colocada: false, ubicaciones: [] },
    { nombre: 'nacionalidad', valor: '', posX: 0, posY: 0, pagina: 1, colocada: false, ubicaciones: [] },
    { nombre: 'f_nacmnto', valor: '', posX: 0, posY: 0, pagina: 1, colocada: false, ubicaciones: [] },
    { nombre: 'e_civil', valor: '', posX: 0, posY: 0, pagina: 1, colocada: false, ubicaciones: [] },
    { nombre: 'domicilio', valor: '', posX: 0, posY: 0, pagina: 1, colocada: false, ubicaciones: [] },
    { nombre: 'campo_cliente', valor: '', posX: 0, posY: 0, pagina: 1, colocada: false, ubicaciones: [] },
    { nombre: 'banco', valor: '', posX: 0, posY: 0, pagina: 1, colocada: false, ubicaciones: [] },
    { nombre: 'cuenta', valor: '', posX: 0, posY: 0, pagina: 1, colocada: false, ubicaciones: [] },
    { nombre: 'firma_empleador', valor: '', posX: 0, posY: 0, pagina: 1, colocada: false, ubicaciones: [] },
    { nombre: 'afp', valor: '', posX: 0, posY: 0, pagina: 1, colocada: false, ubicaciones: [] },
    { nombre: 'salud', valor: '', posX: 0, posY: 0, pagina: 1, colocada: false, ubicaciones: [] },
    { nombre: 'telefono', valor: '', posX: 0, posY: 0, pagina: 1, colocada: false, ubicaciones: [] },
    { nombre: 'correo', valor: '', posX: 0, posY: 0, pagina: 1, colocada: false, ubicaciones: [] }
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
    private apiService: ContratistaApiService
  ) {
    this.isBrowser = isPlatformBrowser(this.platformId);
  }

  ngOnInit(): void {
    if (this.isBrowser) {
      document.addEventListener('mousemove', this.handleMouseMove.bind(this));
      document.addEventListener('mouseup', this.handleMouseUp.bind(this));
    }
    
    this.documentoSeleccionado = null;
    this.modoModificacion = false;
  }

  /**
   * Obtener valor de ejemplo realista para cada variable
   */
  obtenerValorEjemplo(nombreVariable: string): string {
    const ejemplos: {[key: string]: string} = {
      'nombre': 'Juan Pérez González',
      'rut': '12.345.678-9', 
      'dni': '12.345.678-9',
      'f_inicio': '15/03/2024',
      'f_ingreso': '15/03/2024', 
      'f_termino': '14/03/2025',
      'nacionalidad': 'Chilena',
      'f_nacmnto': '25/08/1990',
      'e_civil': 'Soltero(a)',
      'domicilio': 'Av. Las Condes 123, Santiago',
      'campo_cliente': 'Campo Específico Cliente',
      'banco': 'Banco de Chile',
      'cuenta': '123456789',
      'firma_empleador': '[Firma Digital]',
      'afp': 'AFP Capital',
      'salud': 'Fonasa',
      'telefono': '+56 9 1234 5678',
      'correo': 'trabajador@empresa.cl'
    };
    
    return ejemplos[nombreVariable] || nombreVariable;
  }

  /**
   * Determinar si una variable debería estar centrada
   */
  esCampocentrado(nombreVariable: string): boolean {
    const camposCentrados = ['rut', 'dni', 'e_civil', 'f_nacmnto', 'f_inicio', 'nacionalidad', 'f_ingreso', 'f_termino'];
    return camposCentrados.includes(nombreVariable);
  }

  /**
   * ⭐ NUEVO: Inicializa las dimensiones nativas del PDF sin renderizarlo
   * Esto es necesario para calcular correctamente las posiciones cuando se carga un documento existente
   * CORRECCIÓN: Clonar el buffer internamente para evitar detachment
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
        
        // ⭐ Crear una copia del buffer para esta operación
        const bufferCopy = pdfArrayBuffer.slice(0);
        
        const loadingTask = pdfjsLib.getDocument({ data: bufferCopy });
        const pdf = await loadingTask.promise;
        
        // Obtener dimensiones de la primera página
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
            
            // ⭐ DEBUG: Verificar qué se cargó
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
   * ⭐ MODIFICADO: Carga el PDF desde una URL e inicializa dimensiones SIEMPRE
   * CORRECCIÓN: Crear copias separadas del ArrayBuffer para evitar detachment
   */
  cargarPDFDesdeURL(pdfUrl: string): void {
    if (!pdfUrl) {
      this.errorMessage = 'No se encontró la URL del PDF';
      return;
    }
    
    this.isLoading = true;
    
    fetch(pdfUrl)
      .then(response => {
        if (!response.ok) {
          throw new Error(`Error HTTP: ${response.status}`);
        }
        return response.arrayBuffer();
      })
      .then(async arrayBuffer => {
        // ⭐ CORRECCIÓN CRÍTICA: Crear COPIAS SEPARADAS del ArrayBuffer
        // PDF.js puede "detach" el buffer, por lo que necesitamos copias independientes
        const bufferParaDimensiones = arrayBuffer.slice(0);  // Copia 1: para inicializar dimensiones
        const bufferParaRender = arrayBuffer.slice(0);       // Copia 2: para renderizar
        
        this.pdfSrc = bufferParaRender;
        
        // ⭐ Usar la copia 1 para inicializar dimensiones (puede quedar detached)
        await this.inicializarDimensionesPDF(bufferParaDimensiones);
        
        if (!this.modoDocumentoExistente || this.modoModificacion) {
          // ⭐ this.pdfSrc (copia 2) está intacta para renderizar
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

  onFileSelected(event: Event): void {
    if (!this.isBrowser) return;
    
    const input = event.target as HTMLInputElement;
    
    if (input.files && input.files[0]) {
      const file = input.files[0];
      this.originalPdfFile = file;
      console.log('File selected:', file.name, 'size:', file.size, 'bytes');
      
      this.isLoading = true;
      this.errorMessage = null;
      
      const reader = new FileReader();
      reader.onload = () => {
        // ⭐ CORRECCIÓN: Crear copia del buffer para almacenamiento
        const originalBuffer = reader.result as ArrayBuffer;
        this.pdfSrc = originalBuffer.slice(0);
        
        console.log('PDF cargado como ArrayBuffer, tamaño:', (this.pdfSrc as ArrayBuffer).byteLength);
        this.renderPdf();
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
    
    // Coordenadas en píxeles del elemento visual
    const pixelX = clientX - pageRect.left;
    const pixelY = clientY - pageRect.top;
    
    // Convertir a coordenadas nativas del PDF usando las dimensiones reales
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
    
    // Convertir a coordenadas nativas
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
          
          // ⭐ CORRECCIÓN: Crear una copia del buffer para renderizar
          const bufferForRender = (this.pdfSrc as ArrayBuffer).slice(0);
          
          const loadingTask = pdfjsLib.getDocument({
            data: bufferForRender,
            cMapUrl: 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.4.120/cmaps/',
            cMapPacked: true
          });
          
          const pdf = await loadingTask.promise;
          this.pdfDocument = pdf;
          console.log('PDF cargado con éxito. Páginas:', pdf.numPages);
          
          // Obtener dimensiones nativas del PDF desde la primera página
          const firstPage = await pdf.getPage(1);
          const nativeViewport = firstPage.getViewport({ scale: 1.0 });
          this.pdfNativeWidth = nativeViewport.width;
          this.pdfNativeHeight = nativeViewport.height;
          
          console.log(`Dimensiones nativas del PDF: ${this.pdfNativeWidth} x ${this.pdfNativeHeight}`);
          
          this.createPdfControls(container, pdf.numPages);
          await this.renderPdfPages(1, Math.min(pdf.numPages, 3));
          
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
      
      pageContentDiv.appendChild(canvas);
      pageDiv.appendChild(pageContentDiv);
      pagesContainer.appendChild(pageDiv);
      
      await page.render({
        canvasContext: context,
        viewport: scaledViewport,
        renderInteractiveForms: true
      }).promise;
      
      console.log(`✅ Canvas de página ${pageNum} renderizado`);
      
      // ⭐ CRÍTICO: Esperar a que el DOM se actualice completamente
      await new Promise(resolve => setTimeout(resolve, 50));
      
      // ⭐ Verificar dimensiones del pageElement antes de renderizar variables
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
      
      this.variableSeleccionada.ubicaciones.push({
        pagina: pageNumber,
        posX: coords.posX,
        posY: coords.posY,
        id: elementId
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
   * ⭐ MODIFICADO: Validaciones mejoradas y debugging completo
   */
  mostrarVariableEnPdf(variable: VariablePosicionada, pageElement: HTMLElement): void {
    console.log(`🔄 Intentando renderizar variable "${variable.nombre}"...`);
    
    // ⭐ VALIDACIÓN CRÍTICA: Verificar dimensiones nativas
    if (this.pdfNativeWidth === 0 || this.pdfNativeHeight === 0) {
      console.error('❌ ERROR: Dimensiones nativas no inicializadas. No se puede renderizar la variable.');
      console.error('pdfNativeWidth:', this.pdfNativeWidth, 'pdfNativeHeight:', this.pdfNativeHeight);
      return;
    }
    
    // ⭐ VALIDACIÓN: Verificar que el pageElement tiene dimensiones
    const pageRect = pageElement.getBoundingClientRect();
    if (pageRect.width === 0 || pageRect.height === 0) {
      console.error(`❌ ERROR: pageElement no tiene dimensiones válidas:`, pageRect);
      console.error('Esperando a que el elemento tenga dimensiones...');
      
      // Reintentar después de un breve delay
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
    
    // Mostrar valor de ejemplo en lugar del nombre de variable
    variableElement.textContent = this.obtenerValorEjemplo(variable.nombre);
    
    variableElement.id = variable.elementId;
    variableElement.setAttribute('data-variable', variable.nombre);
    variableElement.setAttribute('data-variable-index', variable.variableIndex.toString());
    variableElement.style.position = 'absolute';
    
    // Convertir coordenadas nativas a píxeles para mostrar en pantalla
    const scaleX = pageRect.width / this.pdfNativeWidth;
    const scaleY = pageRect.height / this.pdfNativeHeight;
    
    const displayX = variable.posX * scaleX;
    const displayY = variable.posY * scaleY;
    
    // 🐛 DEBUG COMPLETO: Log para verificar todo el proceso
    console.log(`📍 Variable "${variable.nombre}" - COMPLETO:`, {
      '1_coordenadas_nativas': { x: variable.posX, y: variable.posY },
      '2_dimensiones_pdf': { width: this.pdfNativeWidth, height: this.pdfNativeHeight },
      '3_dimensiones_page': { width: pageRect.width, height: pageRect.height },
      '4_scale': { scaleX: scaleX, scaleY: scaleY },
      '5_coordenadas_display': { x: displayX, y: displayY },
      '6_modo_modificacion': this.modoModificacion
    });
    
    // ⭐ VALIDACIÓN: Verificar que las coordenadas calculadas son válidas
    if (isNaN(displayX) || isNaN(displayY) || !isFinite(displayX) || !isFinite(displayY)) {
      console.error(`❌ ERROR: Coordenadas display inválidas para "${variable.nombre}":`, { displayX, displayY });
      return;
    }
    
    variableElement.style.left = `${displayX}px`;
    variableElement.style.top = `${displayY}px`;
    
    // ⭐ ESTILOS SINCRONIZADOS Y COMPACTOS
    variableElement.style.fontFamily = 'Arial, sans-serif';
    variableElement.style.fontSize = '12px';
    variableElement.style.fontWeight = 'normal';
    variableElement.style.padding = '3px 6px'; // ✅ REDUCIDO: más compacto
    variableElement.style.backgroundColor = 'rgba(74, 128, 245, 0.08)';
    variableElement.style.border = `1px dashed #4a80f5`; // ✅ REDUCIDO: 1px
    variableElement.style.borderRadius = `3px`;
    variableElement.style.zIndex = '100';
    variableElement.style.whiteSpace = 'nowrap';
    variableElement.style.maxWidth = 'none';
    
    // Aplicar alineación según el tipo de campo
    if (this.esCampocentrado(variable.nombre)) {
      variableElement.style.textAlign = 'center';
      variableElement.style.transform = 'translateX(-50%)';
    } else {
      variableElement.style.textAlign = 'left';
      variableElement.style.transform = 'none'; // ⭐ Asegurar sin transform si no es centrado
    }
    
    variableElement.style.pointerEvents = 'all';
    variableElement.style.cursor = 'move';
    
    pageElement.style.position = 'relative';
    pageElement.appendChild(variableElement);
    
    console.log(`✅ Variable "${variable.nombre}" renderizada exitosamente en (${displayX}, ${displayY})`);
    
    variableElement.addEventListener('mousedown', (event) => {
      this.handleVariableMouseDown(event, variable, variableElement, pageElement);
    });
    
    // ⭐ CRÍTICO: Botón de eliminar SIEMPRE disponible (en creación y modificación)
    console.log(`🔘 Creando botón de eliminar para "${variable.nombre}"...`);
    
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
    console.log(`✅ Botón de eliminar agregado para "${variable.nombre}"`);
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
          console.error('Se alcanzó el número máximo de reintentos. No se pudieron encontrar variables.');
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
   * ⭐ MODIFICADO: Mejor manejo del estado y limpieza
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
    
    // Cambiar modos
    this.modoDocumentoExistente = false;
    this.modoModificacion = true;
    
    // ⭐ Limpiar el contenedor para evitar duplicados
    const pdfContainer = document.getElementById('pdf-container');
    if (pdfContainer) {
      pdfContainer.innerHTML = '';
    }
    
    // Pequeño delay para que Angular actualice el DOM
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
    
    const nombreArchivo = this.nombreFormato.toLowerCase().replace(/\s+/g, '_') + '.pdf';
    const renamedFile = new File([this.originalPdfFile], nombreArchivo, { type: 'application/pdf' });
    
    console.log('Enviando archivo original:', renamedFile.name, 'size:', renamedFile.size, 'bytes');
    formData.append('archivo_pdf', renamedFile);
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
          alert('Formato guardado exitosamente con coordenadas nativas');
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
        console.log('Tamaño del blob:', blob.size, 'bytes');
        console.log('Tipo:', blob.type);
        
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
        alert('Posiciones guardadas. Ahora el PDF de prueba usará las nuevas posiciones.');
      },
      error: (error) => {
        console.error('Error al sincronizar posiciones:', error);
        alert(`Error: ${error.error?.error || 'No se pudieron guardar las posiciones'}`);
        this.isLoading = false;
      }
    });
  }
}