//posicionar-variable-contrato.component.ts
import { Component, Inject, NgZone, OnInit, PLATFORM_ID, ViewChild } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ContratistaApiService } from '../../../../services/contratista-api.service';
import { CalibrarVariableComponent } from './calibrar-variable/calibrar-variable.component';

// Interfaz para una ubicación específica de una variable
interface Ubicacion {
  pagina: number;
  posX: number;
  posY: number;
  id: string; // ID único para cada colocación
}

interface VariableDocumento {
  nombre: string;
  valor: string;
  posX: number;
  posY: number;
  pagina: number;
  colocada: boolean;
  ubicaciones: Ubicacion[]; // Array de todas las ubicaciones donde se ha colocado esta variable
}

// Interfaz para el mapa interno de variables colocadas
interface VariablePosicionada {
  nombre: string;
  posX: number;
  posY: number;
  elementId: string;
  variableIndex: number; // Índice de la variable en el array principal
}

// Interfaz para variables con datos de prueba
interface VariableConDatos {
  nombre: string;
  tipo: string; // normal, fecha, numero, etc.
  valorPredeterminado: string;
  valorPrueba: string;
}

@Component({
  selector: 'app-posicionar-variable-contrato',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    CalibrarVariableComponent
  ],
  templateUrl: './posicionar-variable-contrato.component.html',
  styleUrls: ['./posicionar-variable-contrato.component.css']
})
export class PosicionarVariableContratoComponent implements OnInit {
  pdfSrc: string | ArrayBuffer | null = null;
  isLoading = false;
  isBrowser: boolean;
  pdfViewer: any = null;
  errorMessage: string | null = null;
  
  // Store the original File object
  originalPdfFile: File | null = null;
  
  // Modal properties
  mostrarModal = false;
  nombreFormato = '';
  tipoContrato = 'CHILENO'; // Default value
  documentoGuardadoId: number | null = null;

  // Modal para datos de prueba
  mostrarModalDatosPrueba = false;
  variablesConDatos: VariableConDatos[] = [];
  pdfPreviewUrl: string | null = null;

  // Nuevas propiedades para modo documento existente
  modoDocumentoExistente: boolean = false;
  documentosCargados: any[] = [];
  documentoSeleccionado: any = null;

  // Factor de escala fijo al 150%
  readonly scaleFactor: number = 1.4;
  
  // Variables de documento con array de ubicaciones - ACTUALIZADO
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
  
  // Track variables placed on each page - key is page number, value is array of placed variables
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
  
  // NUEVAS PROPIEDADES PARA CALIBRACIÓN
  modoCalibration: boolean = false;
  variableParaCalibrar: VariableDocumento | null = null;
  
  constructor(
    @Inject(PLATFORM_ID) private platformId: Object,
    private ngZone: NgZone,
    private apiService: ContratistaApiService
  ) {
    // Verificamos si estamos en el navegador
    this.isBrowser = isPlatformBrowser(this.platformId);
  }

  ngOnInit(): void {
    // Añadimos listeners globales para el arrastre
    if (this.isBrowser) {
      document.addEventListener('mousemove', this.handleMouseMove.bind(this));
      document.addEventListener('mouseup', this.handleMouseUp.bind(this));
    }
    
    // Asegurarnos que documentoSeleccionado no es null al iniciar
    this.documentoSeleccionado = null;
    this.modoModificacion = false;
  }

  /**
   * Cargar lista de documentos existentes desde el backend
   */
  cargarDocumentosExistentes(): void {
    this.modoDocumentoExistente = true;
    this.isLoading = true;
    this.documentosCargados = [];
    this.documentoSeleccionado = null; // Explícitamente asignar null aquí
    this.modoModificacion = false; // Asegurarnos que no estamos en modo modificación
    
    this.apiService.get('api_listar-documentos/')
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
    this.documentoSeleccionado = documento;
    this.documentoGuardadoId = documento.id;
    
    // Cargar los detalles completos del documento
    this.isLoading = true;
    this.apiService.get(`api_obtener-documento/${documento.id}/`)
      .subscribe({
        next: (response: any) => {
          // Actualizar con la información completa
          this.documentoSeleccionado = response;
          
          // Cargar variables del documento
          if (response.variables && Array.isArray(response.variables)) {
            this.cargarVariablesDesdeDocumento(response.variables);
          }
          
          // Cargar el PDF
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
    
    // Resetear las variables actuales
    this.resetearVariables();
    
    // Recorrer las variables del documento para actualizar las existentes
    variablesDocumento.forEach(varDoc => {
      const varIndex = this.variables.findIndex(v => v.nombre === varDoc.nombre);
      
      if (varIndex >= 0) {
        // Actualizar posiciones principales
        this.variables[varIndex].colocada = true;
        this.variables[varIndex].posX = varDoc.posX || 0;
        this.variables[varIndex].posY = varDoc.posY || 0;
        this.variables[varIndex].pagina = varDoc.pagina || 1;
        
        // Actualizar ubicaciones
        if (varDoc.ubicaciones && Array.isArray(varDoc.ubicaciones)) {
          this.variables[varIndex].ubicaciones = [...varDoc.ubicaciones];
          
          // Agregar cada ubicación al mapa de variables por página
          varDoc.ubicaciones.forEach((ubicacion: { pagina: number; posX: any; posY: any; id: any; }) => {
            // Asegurarnos que la página existe en el mapa
            if (!this.variablesPorPagina.has(ubicacion.pagina)) {
              this.variablesPorPagina.set(ubicacion.pagina, []);
            }
            
            // Añadir la variable posicionada al mapa
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
   * Carga el PDF desde una URL
   */
  // Modificar método cargarPDFDesdeURL para que actualice la interfaz de edición
  cargarPDFDesdeURL(pdfUrl: string): void {
    if (!pdfUrl) {
      this.errorMessage = 'No se encontró la URL del PDF';
      return;
    }
    
    this.isLoading = true;
    
    // Descargar el PDF usando fetch
    fetch(pdfUrl)
      .then(response => {
        if (!response.ok) {
          throw new Error(`Error HTTP: ${response.status}`);
        }
        return response.arrayBuffer();
      })
      .then(arrayBuffer => {
        // Clonar el ArrayBuffer para evitar problemas de desconexión
        const clonedBuffer = arrayBuffer.slice(0);
        
        // Establecer el PDF y renderizarlo solo si no estamos en modo documento existente
        // o si estamos en modo modificación
        this.pdfSrc = clonedBuffer;
        
        if (!this.modoDocumentoExistente || this.modoModificacion) {
          this.renderPdf().then(() => {
            // Si estamos en modo modificación, actualizar la interfaz
            if (this.modoModificacion) {
              console.log('PDF renderizado, actualizando interfaz de modificación...');
              this.actualizarInterfazModoModificacion();
            }
          });
        } else {
          // Si estamos en modo documento existente y no en modificación,
          // simplemente marcar como cargado sin renderizar
          this.isLoading = false;
        }
      })
      .catch(error => {
        console.error('Error al cargar el PDF:', error);
        this.errorMessage = `Error al cargar el PDF del documento: ${error.message}`;
        this.isLoading = false;
      });
  }

  /**
   * Ir directamente al modo de calibración para el documento seleccionado
   */
  calibrarDocumentoSeleccionado(): void {
    if (!this.documentoSeleccionado || !this.documentoGuardadoId) {
      this.errorMessage = 'No hay un documento seleccionado para calibrar';
      return;
    }
    
    // Asegurarnos que todas las variables están cargadas
    if (this.variablesPorPagina.size === 0) {
      this.errorMessage = 'El documento no tiene variables colocadas';
      return;
    }
    
    // Iniciar modo de calibración
    this.modoCalibration = true;
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
      // Store the original file for later use
      this.originalPdfFile = file;
      console.log('File selected:', file.name, 'size:', file.size, 'bytes');
      
      this.isLoading = true;
      this.errorMessage = null;
      
      const reader = new FileReader();
      reader.onload = () => {
        this.pdfSrc = reader.result;
        console.log('PDF cargado como ArrayBuffer, tamaño:', (this.pdfSrc as ArrayBuffer).byteLength);
        this.renderPdf();
      };
      reader.onerror = (error) => {
        console.error('Error al leer el archivo:', error);
        this.isLoading = false;
        this.errorMessage = 'Error al leer el archivo PDF.';
      };
      
      // Leemos el archivo como ArrayBuffer para compatibilidad con el visor
      reader.readAsArrayBuffer(file);
    }
  }

  // Método para iniciar la colocación de una variable
  seleccionarVariable(variable: VariableDocumento): void {
    this.variableSeleccionada = variable;
    this.modoColocacion = true;
    
    // Añadimos el cursor "crosshair" al contenedor PDF
    const pdfContainer = document.getElementById('pdf-container');
    if (pdfContainer) {
      pdfContainer.style.cursor = 'crosshair';
      
      // Añadimos un listener de clic para posicionar la variable
      pdfContainer.addEventListener('click', this.handlePdfClick.bind(this), { once: true });
    }
  }

  calcularCoordenadasRelativas(pageElement: HTMLElement, clientX: number, clientY: number): {posX: number, posY: number} {
    // Obtener el rectángulo del contenedor de la página
    const pageRect = pageElement.getBoundingClientRect();
    
    // Obtener el contenedor del PDF
    const pdfContainer = document.getElementById('pdf-container');
    if (!pdfContainer) {
      return {posX: 0, posY: 0};
    }
    
    // Obtener el documento PDF
    const pdfCanvas = pageElement.querySelector('canvas.pdf-canvas');
    if (!pdfCanvas) {
      return {posX: 0, posY: 0};
    }
    
    // Calcular posición en píxeles relativa a la página
    const pixelX = clientX - pageRect.left;
    const pixelY = clientY - pageRect.top;
    
    // Las coordenadas ORIGINALES sin procesar
    // Estas serán las que guardaremos para máxima precisión
    return {
      posX: pixelX,
      posY: pixelY
    };
  }
  

  
  // Encuentra el elemento de página que fue clickeado
  findClickedPage(event: MouseEvent): HTMLElement | null {
    const elements = document.elementsFromPoint(event.clientX, event.clientY);
    for (const element of elements) {
      if (element.classList.contains('pdf-page')) {
        return element as HTMLElement;
      }
    }
    return null;
  }
  
 
  
  // Manejador del inicio de arrastre de una variable
  handleVariableMouseDown(event: MouseEvent, variable: VariablePosicionada, element: HTMLElement, pageElement: HTMLElement): void {
    // Prevenimos comportamiento predeterminado y propagación
    event.preventDefault();
    event.stopPropagation();
    
    // Obtenemos el número de página
    const pageNumber = parseInt(pageElement.getAttribute('data-page') || '0');
    if (pageNumber <= 0) return;
    
    // Guardamos la variable que estamos arrastrando
    this.variableArrastrandose = variable;
    this.elementoArrastrandose = element;
    this.paginaActualArrastre = pageElement;
    this.paginaNumeroArrastre = pageNumber;
    
    // Calculamos la posición del clic dentro del elemento
    const rect = element.getBoundingClientRect();
    this.offsetX = event.clientX - rect.left;
    this.offsetY = event.clientY - rect.top;
    
    // Añadimos clases de estilo para indicar que estamos arrastrando
    element.classList.add('dragging');
    document.body.style.cursor = 'move';
  }
  
  // Manejador del movimiento durante el arrastre
  handleMouseMove(event: MouseEvent): void {
    if (!this.variableArrastrandose || !this.elementoArrastrandose || !this.paginaActualArrastre) return;
    
    // Calculamos la nueva posición basada en la posición del mouse y el offset
    const pageRect = this.paginaActualArrastre.getBoundingClientRect();
    
    // Restringimos la posición dentro de los límites de la página
    let newX = event.clientX - pageRect.left - this.offsetX;
    let newY = event.clientY - pageRect.top - this.offsetY;
    
    // Prevenimos que la variable se salga de los límites de la página
    newX = Math.max(0, Math.min(newX, pageRect.width - this.elementoArrastrandose.offsetWidth));
    newY = Math.max(0, Math.min(newY, pageRect.height - this.elementoArrastrandose.offsetHeight));
    
    // Actualizamos la posición visual del elemento
    this.elementoArrastrandose.style.left = `${newX}px`;
    this.elementoArrastrandose.style.top = `${newY}px`;
  }
  
  // Manejador del fin del arrastre
  handleMouseUp(event: MouseEvent): void {
    if (!this.variableArrastrandose || !this.elementoArrastrandose || !this.paginaActualArrastre) return;
    
    // Calculamos las coordenadas finales normalizadas (sin escala)
    const finalX = parseInt(this.elementoArrastrandose.style.left);
    const finalY = parseInt(this.elementoArrastrandose.style.top);
    
    // Convertimos las coordenadas a valores normalizados sin escala
    const normalizedX = finalX;
    const normalizedY = finalY;
    
    // Actualizamos las coordenadas de la variable en el mapa
    const variablesList = this.variablesPorPagina.get(this.paginaNumeroArrastre) || [];
    const variableIndex = variablesList.findIndex(v => v.elementId === this.variableArrastrandose?.elementId);
    
    if (variableIndex !== -1) {
      variablesList[variableIndex].posX = normalizedX;
      variablesList[variableIndex].posY = normalizedY;
      
      // Actualizamos también la ubicación correspondiente en el array de ubicaciones de la variable principal
      const mainVarIndex = variablesList[variableIndex].variableIndex;
      if (mainVarIndex >= 0 && mainVarIndex < this.variables.length) {
        const variable = this.variables[mainVarIndex];
        
        // Buscamos la ubicación correspondiente por el ID del elemento
        const ubicacionIndex = variable.ubicaciones.findIndex(u => u.id === this.variableArrastrandose?.elementId);
        if (ubicacionIndex !== -1) {
          variable.ubicaciones[ubicacionIndex].posX = normalizedX;
          variable.ubicaciones[ubicacionIndex].posY = normalizedY;
        }
        
        // Si es la ubicación más reciente, actualizamos también la posición principal
        if (variable.ubicaciones.length > 0 && ubicacionIndex === variable.ubicaciones.length - 1) {
          variable.posX = normalizedX;
          variable.posY = normalizedY;
        }
      }
    }
    
    // NUEVO: Actualizar el elemento de depuración asociado
    const debugInfo = this.paginaActualArrastre.querySelector(
      `.debug-info[data-for="${this.variableArrastrandose.elementId}"]`
    ) as HTMLElement; // Cast a HTMLElement para tener acceso a style
    
    if (debugInfo) {
      // Actualizamos la posición del indicador de depuración
      debugInfo.style.left = `${finalX + 2}px`;
      debugInfo.style.top = `${finalY + 30}px`;
      // Actualizamos el texto con las nuevas coordenadas
      debugInfo.textContent = `(${Math.round(finalX)},${Math.round(finalY)})`;
    }
    
    // Quitamos clases de estilo de arrastre
    this.elementoArrastrandose.classList.remove('dragging');
    document.body.style.cursor = 'auto';
    
    // Limpiamos las referencias
    this.variableArrastrandose = null;
    this.elementoArrastrandose = null;
    this.paginaActualArrastre = null;
    this.paginaNumeroArrastre = 0;
  }
  
  // Resetea todas las variables a su estado inicial
  resetearVariables(): void {
    this.variables.forEach(variable => {
      variable.posX = 0;
      variable.posY = 0;
      variable.pagina = 1;
      variable.colocada = false;
      variable.ubicaciones = []; // Limpiamos todas las ubicaciones
    });
    
    // Limpiamos el mapa de variables por página
    this.variablesPorPagina.clear();
    
    // Eliminamos todas las variables del PDF
    document.querySelectorAll('.pdf-variable').forEach(el => el.remove());
    document.querySelectorAll('.debug-info').forEach(el => el.remove());
  }
  
  // Genera JSON con las posiciones de las variables
  exportarPosiciones(): void {
    const posiciones: { variable: string; posicion: { x: number; y: number; pagina: number; }; }[] = [];
    
    // Exportamos todas las ubicaciones de todas las variables
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
    
    console.log('Posiciones de variables:', JSON.stringify(posiciones, null, 2));
    // Ejemplo de descarga del JSON
    this.descargarJSON(posiciones, 'posiciones_variables.json');
  }
  
  // Método auxiliar para descargar el JSON
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

  // Modificamos renderPdf para retornar una promesa que se resuelve cuando termina
  async renderPdf(): Promise<void> {
    if (!this.isBrowser || !this.pdfSrc) {
      this.isLoading = false;
      return Promise.resolve(); // Retorna una promesa resuelta si no hay nada que renderizar
    }

    return new Promise((resolve, reject) => {
      this.ngZone.runOutsideAngular(async () => {
        try {
          console.log('Iniciando renderizado de PDF...');
          
          // Cargamos la librería PDF.js
          if (!(window as any).pdfjsLib) {
            console.log('Cargando PDF.js desde CDN...');
            await this.loadPdfJsScript();
          }
          
          const pdfjsLib = (window as any).pdfjsLib;
          if (!pdfjsLib) {
            throw new Error('No se pudo cargar PDF.js');
          }
          
          // Configuramos el worker de PDF.js
          const workerUrl = `https://cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjsLib.version}/pdf.worker.min.js`;
          pdfjsLib.GlobalWorkerOptions.workerSrc = workerUrl;

          // Obtenemos el elemento contenedor
          const container = document.getElementById('pdf-container');
          if (!container) {
            throw new Error('No se encontró el contenedor #pdf-container');
          }
          
          // Limpiamos el contenedor
          container.innerHTML = '';

          // Verificamos que pdfSrc no sea null antes de procesarlo
          if (this.pdfSrc === null) {
            throw new Error('No se ha cargado ningún PDF');
          }

          console.log('Cargando documento PDF...');
          // Cargamos el documento PDF
          const loadingTask = pdfjsLib.getDocument({
            data: this.pdfSrc,
            cMapUrl: 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.4.120/cmaps/',
            cMapPacked: true
          });
          
          const pdf = await loadingTask.promise;
          this.pdfDocument = pdf;
          console.log('PDF cargado con éxito. Páginas:', pdf.numPages);
          
          // Creamos los controles de navegación y el contenedor para el PDF
          this.createPdfControls(container, pdf.numPages);
          
          // Renderizamos las primeras páginas
          await this.renderPdfPages(1, Math.min(pdf.numPages, 3));
          
          this.ngZone.run(() => {
            this.isLoading = false;
            resolve(); // Resolvemos la promesa cuando el renderizado está completo
          });
        } catch (error) {
          console.error('Error al renderizar el PDF:', error);
          
          this.ngZone.run(() => {
            this.isLoading = false;
            this.errorMessage = `Error al renderizar el PDF: ${error instanceof Error ? error.message : 'Error desconocido'}`;
            reject(error); // Rechazamos la promesa si hay un error
          });
        }
      });
    });
  }
  
  // Método para crear los controles del PDF y el contenedor
  private createPdfControls(container: HTMLElement, numPages: number): void {
    // Creamos los controles
    const controlsContainer = document.createElement('div');
    controlsContainer.className = 'pdf-controls';
    
    // Botones de navegación
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
    
    // Creamos el contenedor de páginas
    const pagesContainer = document.createElement('div');
    pagesContainer.id = 'pdf-pages';
    pagesContainer.className = 'pdf-pages';
    
    container.appendChild(controlsContainer);
    container.appendChild(pagesContainer);
    
    // Variables para controlar la navegación
    let currentPage = 1;
    const pagesToShow = 3;
    
    // Evento para botón anterior
    prevButton.addEventListener('click', () => {
      const newStartPage = Math.max(1, currentPage - pagesToShow);
      const newEndPage = Math.min(newStartPage + pagesToShow - 1, numPages);
      
      this.renderPdfPages(newStartPage, newEndPage);
      
      currentPage = newStartPage;
      pageInfo.textContent = `Página ${newStartPage}-${newEndPage} de ${numPages}`;
      prevButton.disabled = newStartPage === 1;
      nextButton.disabled = newEndPage === numPages;
    });
    
    // Evento para botón siguiente
    nextButton.addEventListener('click', () => {
      const newStartPage = Math.min(currentPage + pagesToShow, numPages);
      const newEndPage = Math.min(newStartPage + pagesToShow - 1, numPages);
      
      this.renderPdfPages(newStartPage, newEndPage);
      
      currentPage = newStartPage;
      pageInfo.textContent = `Página ${newStartPage}-${newEndPage} de ${numPages}`;
      prevButton.disabled = newStartPage === 1;
      nextButton.disabled = newEndPage === numPages;
    });
    
    // Guardamos referencias
    this.currentPage = currentPage;
    this.pageInfo = pageInfo;
    this.prevButton = prevButton;
    this.nextButton = nextButton;
  }
  
  // Variables para controlar el estado
  private currentPage: number = 1;
  private pageInfo: HTMLElement | null = null;
  private prevButton: HTMLButtonElement | null = null;
  private nextButton: HTMLButtonElement | null = null;
  
  // Método para renderizar páginas del PDF
  private async renderPdfPages(startPage: number, endPage: number): Promise<void> {
    if (!this.pdfDocument) return;
    
    const pdfDoc = this.pdfDocument;
    const numPages = pdfDoc.numPages;
    
    // Aseguramos que los valores estén dentro de los límites
    startPage = Math.max(1, Math.min(startPage, numPages));
    endPage = Math.min(Math.max(startPage, endPage), numPages);
    
    // Obtenemos el contenedor de páginas
    const pagesContainer = document.getElementById('pdf-pages');
    if (!pagesContainer) return;
    
    // Limpiamos el contenedor
    pagesContainer.innerHTML = '';
    
    // Obtenemos el ancho del contenedor para escalar adecuadamente
    const containerWidth = pagesContainer.clientWidth || 800;
    const pixelRatio = window.devicePixelRatio || 1;
    
    // Renderizamos cada página
    for (let pageNum = startPage; pageNum <= endPage; pageNum++) {
      // Creamos un contenedor para la página actual
      const pageDiv = document.createElement('div');
      pageDiv.className = 'pdf-page-container';
      
      // Añadimos el encabezado de la página
      const pageHeader = document.createElement('div');
      pageHeader.className = 'pdf-page-header';
      pageHeader.textContent = `PÁGINA ${pageNum}`;
      pageDiv.appendChild(pageHeader);
      
      // Contenedor para la página del PDF
      const pageContentDiv = document.createElement('div');
      pageContentDiv.className = 'pdf-page';
      pageContentDiv.setAttribute('data-page', pageNum.toString());
      
      // Cargamos la página del PDF
      const page = await pdfDoc.getPage(pageNum);
      
      // Calculamos la escala apropiada
      const viewport = page.getViewport({ scale: 1.0 });
      const scale = (containerWidth * 0.9) / viewport.width;
      const scaledViewport = page.getViewport({ scale: scale * this.scaleFactor * pixelRatio });
      
      // Configuramos el tamaño del contenedor
      pageContentDiv.style.width = `${scaledViewport.width / pixelRatio}px`;
      pageContentDiv.style.height = `${scaledViewport.height / pixelRatio}px`;
      
      // Creamos el canvas para renderizar la página
      const canvas = document.createElement('canvas');
      canvas.className = 'pdf-canvas';
      canvas.width = scaledViewport.width;
      canvas.height = scaledViewport.height;
      canvas.style.width = `${scaledViewport.width / pixelRatio}px`;
      canvas.style.height = `${scaledViewport.height / pixelRatio}px`;
      
      const context = canvas.getContext('2d', { alpha: false, willReadFrequently: true });
      if (!context) continue;
      
      // Añadimos el canvas al contenedor
      pageContentDiv.appendChild(canvas);
      pageDiv.appendChild(pageContentDiv);
      
      // Añadimos la página al contenedor principal
      pagesContainer.appendChild(pageDiv);
      
      // Renderizamos la página
      await page.render({
        canvasContext: context,
        viewport: scaledViewport,
        renderInteractiveForms: true
      }).promise;
      
      // Re-aplicamos las variables que estén en esta página
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
  
  // Opens the save format modal
  guardarFormato(): void {
    if (!this.originalPdfFile) {
      alert('Por favor, seleccione un archivo PDF primero');
      return;
    }
    
    // Check if any variables have positions
    const hayVariablesColocadas = this.variables.some(v => v.ubicaciones.length > 0);
    if (!hayVariablesColocadas) {
      alert('Debe colocar al menos una variable en el documento');
      return;
    }
    
    this.mostrarModal = true;
  }

  // Close the modal
  cerrarModal(): void {
    this.mostrarModal = false;
    this.nombreFormato = '';
    this.tipoContrato = 'CHILENO';
  }

  // Save format to backend
  confirmarGuardado(): void {
    if (!this.nombreFormato.trim()) {
      alert('El nombre del formato es obligatorio');
      return;
    }
    
    if (!this.originalPdfFile) {
      alert('No se encontró el archivo PDF original');
      return;
    }
    
    // Collect variables with their positions
    const variables = this.variables.filter(v => v.ubicaciones.length > 0).map(variable => ({
      nombre: variable.nombre,
      ubicaciones: variable.ubicaciones
    }));
    
    // Create FormData for multipart/form-data submission
    const formData = new FormData();
    
    // Use the original file with a new name
    const nombreArchivo = this.nombreFormato.toLowerCase().replace(/\s+/g, '_') + '.pdf';
    const renamedFile = new File([this.originalPdfFile], nombreArchivo, { type: 'application/pdf' });
    
    console.log('Sending original file:', renamedFile.name, 'size:', renamedFile.size, 'bytes');
    formData.append('archivo_pdf', renamedFile);
    
    // Add form data
    formData.append('nombre', this.nombreFormato);
    formData.append('tipo', this.tipoContrato);
    formData.append('variables', JSON.stringify(variables));
    
    // Send to backend using the API service
    this.isLoading = true;
    this.apiService.postFormData('api_guardar-documento-variables/', formData)
      .subscribe({
        next: (response: any) => {
          console.log('Formato guardado exitosamente', response);
          this.documentoGuardadoId = response.id;
          this.isLoading = false;
          
          // Preguntar si desea calibrar el documento
          const calibrarAhora = confirm('Documento guardado exitosamente. ¿Deseas calibrar las posiciones de las variables?');
          
          if (calibrarAhora) {
            this.iniciarCalibracion();
          } else {
            alert('Formato guardado exitosamente');
            this.cerrarModal();
          }
        },
        error: (error) => {
          console.error('Error al guardar el formato:', error);
          alert(`Error: ${error.error?.error || 'No se pudo guardar el formato'}`);
          this.isLoading = false;
        }
      });
  }

  /**
   * NUEVOS MÉTODOS PARA CALIBRACIÓN
   */
  
  // Método para iniciar la calibración
  iniciarCalibracion(): void {
    if (!this.documentoGuardadoId) {
      alert('Primero debes guardar el documento para poder calibrarlo');
      return;
    }
    
    // Activamos el modo de calibración
    this.modoCalibration = true;
    
    // Si solo tenemos una variable colocada, la seleccionamos automáticamente
    const variablesColocadas = this.variables.filter(v => v.colocada);
    if (variablesColocadas.length === 1) {
      this.variableParaCalibrar = variablesColocadas[0];
    }
  }
  
  // Método para calibrar una variable específica
  calibrarVariable(variable: VariableDocumento): void {
    if (!this.documentoGuardadoId) {
      alert('Primero debes guardar el documento para poder calibrarlo');
      return;
    }
    
    // Activamos el modo de calibración y seleccionamos la variable
    this.modoCalibration = true;
    this.variableParaCalibrar = variable;
  }
  
  // Método para salir del modo calibración
  cerrarCalibracion(): void {
    this.modoCalibration = false;
    this.variableParaCalibrar = null;
  }
  
  // Método para manejar la finalización de la calibración
  onCalibracionCompletada(resultado: any): void {
    console.log('Calibración completada:', resultado);
    
    // Actualizamos las variables si el resultado incluye cambios
    if (resultado.variables) {
      this.variables = resultado.variables;
      
      // Reconstruimos el mapa de variables por página
      this.variablesPorPagina.clear();
      this.variables.forEach((variable, variableIndex) => {
        variable.ubicaciones.forEach(ubicacion => {
          if (!this.variablesPorPagina.has(ubicacion.pagina)) {
            this.variablesPorPagina.set(ubicacion.pagina, []);
          }
          
          this.variablesPorPagina.get(ubicacion.pagina)?.push({
            nombre: variable.nombre,
            posX: ubicacion.posX,
            posY: ubicacion.posY,
            elementId: ubicacion.id,
            variableIndex: variableIndex
          });
        });
      });
      
      // Volvemos a renderizar las variables en el PDF
      this.renderPdfPages(this.currentPage, Math.min(this.currentPage + 2, this.pdfDocument?.numPages || 3));
    }
    
    // Salimos del modo calibración
    this.modoCalibration = false;
    this.variableParaCalibrar = null;
  }
  
  // Método para generar un PDF de calibración
  generarPDFCalibracion(): void {
    if (!this.documentoGuardadoId) {
      alert('Primero debes guardar el documento para poder calibrarlo');
      return;
    }
    
    this.isLoading = true;
    this.apiService.post('api_calibracion-pdf/', { documento_id: this.documentoGuardadoId })
      .subscribe({
        next: (response: any) => {
          console.log('PDF de calibración generado:', response);
          
          // Abre el PDF en una nueva ventana
          window.open(response.url, '_blank');
          
          this.isLoading = false;
          alert('PDF de calibración generado. Por favor, revisa el PDF y ajusta los parámetros de transformación según las instrucciones.');
        },
        error: (error) => {
          console.error('Error al generar PDF de calibración:', error);
          alert(`Error: ${error.error?.error || 'No se pudo generar el PDF de calibración'}`);
          this.isLoading = false;
        }
      });
  }

  /**
   * NUEVOS MÉTODOS PARA GENERAR PDF DE PRUEBA
   */

  // Método para preparar y mostrar modal de datos de prueba
  generarPDFPrueba(): void {
    if (!this.documentoGuardadoId) {
      alert('Primero debes guardar el documento para poder generar un PDF');
      return;
    }

    // Preparamos datos de prueba para las variables colocadas
    this.variablesConDatos = [];
    const variablesColocadas = this.variables.filter(v => v.colocada);
    
    variablesColocadas.forEach(variable => {
      let tipo = 'normal';
      let valorPredeterminado = '';
      
      // Determinar tipo y valor predeterminado según el nombre de la variable
      if (variable.nombre.includes('fecha') || 
          variable.nombre.includes('f_inicio') || 
          variable.nombre.includes('f_nacmnto') || 
          variable.nombre.includes('f_ingreso') || 
          variable.nombre.includes('f_termino')) {
        tipo = 'fecha';
        valorPredeterminado = '01/01/2023';
      } else if (variable.nombre === 'rut' || variable.nombre === 'dni') {
        valorPredeterminado = '12.345.678-9';
      } else if (variable.nombre === 'nombre') {
        valorPredeterminado = 'Juan Pérez López';
      } else if (variable.nombre === 'nacionalidad') {
        valorPredeterminado = 'Chilena';
      } else if (variable.nombre === 'e_civil') {
        valorPredeterminado = 'Soltero';
      } else if (variable.nombre === 'domicilio') {
        valorPredeterminado = 'Av. Ejemplo 123, Santiago';
      } else if (variable.nombre === 'telefono') {
        valorPredeterminado = '+56 9 1234 5678';
      } else if (variable.nombre === 'correo') {
        valorPredeterminado = 'ejemplo@correo.com';
      } else {
        valorPredeterminado = `Valor de prueba para ${variable.nombre}`;
      }
      
      this.variablesConDatos.push({
        nombre: variable.nombre,
        tipo: tipo,
        valorPredeterminado: valorPredeterminado,
        valorPrueba: valorPredeterminado // Inicializamos con el valor predeterminado
      });
    });
    
    // Mostramos el modal si hay variables colocadas
    if (this.variablesConDatos.length > 0) {
      this.mostrarModalDatosPrueba = true;
    } else {
      alert('No hay variables colocadas en el documento');
    }
  }
  
  // Cerrar modal de datos de prueba
  cerrarModalDatosPrueba(): void {
    this.mostrarModalDatosPrueba = false;
  }
  
  // Generar PDF con datos de prueba
  confirmarGenerarPDF(): void {
    if (!this.documentoGuardadoId) {
      alert('No se encontró el ID del documento');
      return;
    }
    
    // Preparar datos para enviar al backend
    const datosVariables: {[key: string]: string} = {};
    
    this.variablesConDatos.forEach(variable => {
      datosVariables[variable.nombre] = variable.valorPrueba || variable.valorPredeterminado;
    });
    
    // Enviar solicitud al backend
    this.isLoading = true;
    this.apiService.post('api_ajustar_calibracion/', {
      documento_id: this.documentoGuardadoId,
      datos_variables: datosVariables
    }).subscribe({
      next: (response: any) => {
        console.log('PDF generado con éxito:', response);
        
        // Guardar URL del PDF generado
        this.pdfPreviewUrl = response.url;
        
        // Abrir PDF en nueva ventana
        window.open(response.url, '_blank');
        
        this.isLoading = false;
        this.mostrarModalDatosPrueba = false;
      },
      error: (error) => {
        console.error('Error al generar PDF:', error);
        alert(`Error: ${error.error?.error || 'No se pudo generar el PDF'}`);
        this.isLoading = false;
      }
    });
  }
  
  // Descargar PDF generado
  descargarPDF(): void {
    if (!this.pdfPreviewUrl) return;
    
    // Crear un enlace para descargar el PDF
    const a = document.createElement('a');
    a.href = this.pdfPreviewUrl;
    a.download = `documento_${this.documentoGuardadoId}_${Date.now()}.pdf`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  }

  // Nueva propiedad para el modo de modificación
  modoModificacion: boolean = false;

  // Método para entrar en modo de modificación de documento
  modificarDocumentoSeleccionado(): void {
    if (!this.documentoSeleccionado || !this.documentoGuardadoId) {
      this.errorMessage = 'No hay un documento seleccionado para modificar';
      return;
    }
    
    // Asegurarnos que todas las variables están cargadas
    if (this.variablesPorPagina.size === 0) {
      this.errorMessage = 'El documento no tiene variables para modificar';
      return;
    }
    
    // Importante: vamos a guardar la URL del PDF en lugar de mantener el ArrayBuffer
    const pdfUrl = this.documentoSeleccionado.archivo_pdf_url;
    
    // Salir del modo existente y entrar en modo modificación
    this.modoDocumentoExistente = false;
    this.modoModificacion = true;
    
    // En lugar de volver a renderizar el PDF, vamos a cargarlo de nuevo desde la URL
    setTimeout(() => {
      // Cargar el PDF fresco, en lugar de intentar usar el ArrayBuffer existente
      this.cargarPDFDesdeURL(pdfUrl);
      
      // La actualización de la interfaz la haremos después de que el PDF se cargue
      // (esto sucede en el callback de éxito de cargarPDFDesdeURL)
    }, 100);
  }

  // Método para actualizar la interfaz en modo modificación
  private maxRetries = 5;
  private currentRetry = 0;

  // Método para actualizar la interfaz en modo modificación
  actualizarInterfazModoModificacion(): void {
    console.log('Actualizando interfaz en modo modificación...');
    
    // Reiniciamos el contador de reintentos
    this.currentRetry = 0;
    
    // Llamamos a la función que intentará actualizar las variables
    this.intentarActualizarVariables();
  }

  // Método para intentar actualizar variables con reintentos
  private intentarActualizarVariables(): void {
    setTimeout(() => {
      // Verificamos que hay elementos variables para actualizar
      const variables = document.querySelectorAll('.pdf-variable');
      console.log(`Encontradas ${variables.length} variables para actualizar (intento ${this.currentRetry + 1}/${this.maxRetries})`);
      
      if (variables.length === 0) {
        this.currentRetry++;
        
        if (this.currentRetry < this.maxRetries) {
          console.warn('No se encontraron variables en el PDF, intentando de nuevo...');
          // Aumentamos el tiempo de espera con cada reintento
          this.intentarActualizarVariables();
        } else {
          console.error('Se alcanzó el número máximo de reintentos. No se pudieron encontrar variables.');
        }
        return;
      }
      
      // Añadir botones de eliminación a todas las variables
      variables.forEach(el => {
        // Añadir clase para marcar que estamos en modo edición
        el.classList.add('edit-mode');
        
        // Si no tiene botón de eliminar, añadirlo
        if (!el.querySelector('.delete-btn')) {
          const deleteBtn = document.createElement('div');
          deleteBtn.className = 'delete-btn';
          deleteBtn.innerHTML = '×';
          deleteBtn.title = 'Eliminar variable';
          
          // Obtener el ID de la variable
          const variableId = el.id;
          const variableIndex = el.getAttribute('data-variable-index');
          
          // Evento para eliminar la variable
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
    }, 500 + (this.currentRetry * 300)); // Aumentamos el tiempo con cada reintento
  }

  // Método para eliminar una variable
  eliminarVariable(elementId: string, variableIndex: number): void {
    // Encontrar la página y la variable
    let paginaEncontrada = -1;
    let variableEncontrada = null;
    
    // Buscar la variable en todas las páginas
    this.variablesPorPagina.forEach((variables, pagina) => {
      const index = variables.findIndex(v => v.elementId === elementId);
      if (index !== -1) {
        paginaEncontrada = pagina;
        variableEncontrada = variables[index];
      }
    });
    
    if (paginaEncontrada !== -1 && variableEncontrada) {
      // Eliminar el elemento del DOM
      const variableElement = document.getElementById(elementId);
      if (variableElement) {
        variableElement.remove();
        
        // También eliminar el elemento de depuración asociado
        const debugInfo = document.querySelector(`.debug-info[data-for="${elementId}"]`);
        if (debugInfo) {
          debugInfo.remove();
        }
      }
      
      // Eliminar la variable del array de variables por página
      const variablesList = this.variablesPorPagina.get(paginaEncontrada);
      if (variablesList) {
        const indexInPage = variablesList.findIndex(v => v.elementId === elementId);
        if (indexInPage !== -1) {
          variablesList.splice(indexInPage, 1);
        }
      }
      
      // Actualizar la variable principal
      if (variableIndex >= 0 && variableIndex < this.variables.length) {
        const variable = this.variables[variableIndex];
        
        // Buscar y eliminar la ubicación
        const ubicacionIndex = variable.ubicaciones.findIndex(u => u.id === elementId);
        if (ubicacionIndex !== -1) {
          variable.ubicaciones.splice(ubicacionIndex, 1);
        }
        
        // Si no quedan ubicaciones, marcar como no colocada
        if (variable.ubicaciones.length === 0) {
          variable.colocada = false;
        }
      }
    }
  }

  // Método para guardar los cambios del documento modificado
  guardarCambiosDocumento(): void {
    if (!this.documentoGuardadoId) {
      alert('No se puede identificar el documento a modificar');
      return;
    }
    
    // Recopilar las variables actualizadas
    const variables = this.variables.filter(v => v.ubicaciones.length > 0).map(variable => ({
      nombre: variable.nombre,
      ubicaciones: variable.ubicaciones
    }));
    
    // Preparar datos para enviar al backend
    const datosActualizados = {
      id: this.documentoGuardadoId,
      variables: variables
    };
    
    this.isLoading = true;
    
    // Llamar al API para actualizar el documento
    this.apiService.put(`api_obtener-documento/${this.documentoGuardadoId}/`, datosActualizados)
      .subscribe({
        next: (response: any) => {
          console.log('Documento actualizado exitosamente', response);
          this.isLoading = false;
          
          // Salir del modo modificación y volver al modo documento existente
          this.modoModificacion = false;
          this.modoDocumentoExistente = true;
          alert('Documento actualizado exitosamente');
        },
        error: (error) => {
          console.error('Error al actualizar el documento:', error);
          alert(`Error: ${error.error?.error || 'No se pudo actualizar el documento'}`);
          this.isLoading = false;
        }
      });
  }

  // Sobrescribir el método handlePdfClick para que funcione también en modo modificación
  handlePdfClick(event: MouseEvent): void {
    // Mantener el comportamiento original para el modo colocación
    if (this.variableSeleccionada && this.modoColocacion) {
      // Código original aquí (el que ya tienes)
      if (!this.variableSeleccionada || !this.modoColocacion) return;
      
      // Obtenemos el elemento de página que fue clickeado
      const clickedPage = this.findClickedPage(event);
      if (!clickedPage) return;
      
      // Obtenemos el número de página del atributo data-page
      const pageNumber = parseInt(clickedPage.getAttribute('data-page') || '0');
      if (pageNumber <= 0) return;
      
      // Obtenemos coordenadas relativas
      const coords = this.calcularCoordenadasRelativas(clickedPage, event.clientX, event.clientY);
      
      // Guardamos las coordenadas ORIGINALES sin procesar
      // Esto es crucial: no dividimos por el factor de escala
      const posX = coords.posX;
      const posY = coords.posY;
      
      // Encontrar el índice de la variable seleccionada en el array
      const variableIndex = this.variables.findIndex(v => v === this.variableSeleccionada);
      
      // Creamos un ID único para el elemento DOM
      const elementId = `var-${this.variableSeleccionada.nombre}-${Date.now()}`;
      
      // Actualizamos la información de la variable
      this.variableSeleccionada.posX = posX;
      this.variableSeleccionada.posY = posY;
      this.variableSeleccionada.pagina = pageNumber;
      this.variableSeleccionada.colocada = true;
      
      // Añadimos esta ubicación al array de ubicaciones de la variable
      this.variableSeleccionada.ubicaciones.push({
        pagina: pageNumber,
        posX: posX,
        posY: posY,
        id: elementId
      });
      
      // Añadimos la variable al mapa de variables por página
      if (!this.variablesPorPagina.has(pageNumber)) {
        this.variablesPorPagina.set(pageNumber, []);
      }
      
      this.variablesPorPagina.get(pageNumber)?.push({
        nombre: this.variableSeleccionada.nombre,
        posX: posX, 
        posY: posY,
        elementId: elementId,
        variableIndex: variableIndex
      });
      
      // Mostramos la variable en el PDF
      this.mostrarVariableEnPdf({
        nombre: this.variableSeleccionada.nombre,
        posX: posX,
        posY: posY,
        elementId: elementId,
        variableIndex: variableIndex
      }, clickedPage);
      
      // Reseteamos el modo de colocación
      this.modoColocacion = false;
      document.getElementById('pdf-container')!.style.cursor = 'default';
      this.variableSeleccionada = null;
      
      // Si estamos en modo modificación, actualizar la interfaz
      if (this.modoModificacion) {
        this.actualizarInterfazModoModificacion();
      }
    }
  }

  // Modificar el método mostrarVariableEnPdf para añadir botón de eliminar en modo modificación
  mostrarVariableEnPdf(variable: VariablePosicionada, pageElement: HTMLElement): void {
    // Creamos un elemento para mostrar la variable
    const variableElement = document.createElement('div');
    variableElement.className = 'pdf-variable';
    if (this.modoModificacion) {
      variableElement.classList.add('edit-mode');
    }
    variableElement.textContent = variable.nombre;
    variableElement.id = variable.elementId;
    variableElement.setAttribute('data-variable', variable.nombre);
    variableElement.setAttribute('data-variable-index', variable.variableIndex.toString());
    variableElement.style.position = 'absolute';
    
    // Aplicamos directamente las coordenadas en píxeles
    variableElement.style.left = `${variable.posX}px`;
    variableElement.style.top = `${variable.posY}px`;
    
    // Estilo para el elemento visual
    variableElement.style.fontSize = `${12}px`;
    variableElement.style.padding = `${4}px ${8}px`;
    variableElement.style.backgroundColor = 'rgba(74, 128, 245, 0.1)';
    variableElement.style.border = `1px dashed #4a80f5`;
    variableElement.style.borderRadius = `3px`;
    variableElement.style.zIndex = '100';
    
    // Permitimos eventos de puntero y agregamos cursor de arrastre
    variableElement.style.pointerEvents = 'all';
    variableElement.style.cursor = 'move';
    
    // Añadimos el elemento al contenedor de la página
    pageElement.style.position = 'relative';
    pageElement.appendChild(variableElement);
    
    // Añadimos evento de mousedown para iniciar el arrastre
    variableElement.addEventListener('mousedown', (event) => {
      this.handleVariableMouseDown(event, variable, variableElement, pageElement);
    });
    
    // Si estamos en modo modificación, añadir botón de eliminar
    if (this.modoModificacion) {
      const deleteBtn = document.createElement('div');
      deleteBtn.className = 'delete-btn';
      deleteBtn.innerHTML = '×';
      deleteBtn.title = 'Eliminar variable';
      
      // Evento para eliminar la variable
      deleteBtn.addEventListener('click', (event) => {
        event.stopPropagation();
        this.eliminarVariable(variable.elementId, variable.variableIndex);
      });
      
      variableElement.appendChild(deleteBtn);
    }
    
    // INFORMACIÓN DE DIAGNÓSTICO - POSICIONADA SIEMPRE DEBAJO DEL RECTÁNGULO
    // Importante: Esta parte se cambia para asegurar que las coordenadas aparezcan siempre
    // debajo del rectángulo y no dentro de él, independientemente del modo
    if (true) { // Cambiar a "false" para ocultar durante la producción
      // Crear el elemento de depuración
      const debugInfo = document.createElement('div');
      debugInfo.className = 'debug-info';
      debugInfo.style.position = 'absolute';
      
      // IMPORTANTE: Asegurarnos que las coordenadas siempre aparezcan debajo del rectángulo
      // y no dentro de él
      const rect = variableElement.getBoundingClientRect();
      const elementHeight = 24; // Altura aproximada del elemento variable
      
      // Posicionamos debajo del rectángulo, no dentro
      debugInfo.style.left = `${variable.posX + 2}px`;
      debugInfo.style.top = `${variable.posY + elementHeight + 4}px`; // Siempre debajo del rectángulo
      
      debugInfo.style.fontSize = '8px';
      debugInfo.style.color = 'red';
      debugInfo.style.zIndex = '101';
      debugInfo.textContent = `(${Math.round(variable.posX)},${Math.round(variable.posY)})`;
      
      // Vincula el elemento de depuración con la variable
      debugInfo.setAttribute('data-for', variable.elementId);
      
      pageElement.appendChild(debugInfo);
    }
  }

  // Modificar el método para salir del modo modificación
  cerrarModificacion(): void {
    // Confirmar si hay cambios pendientes
    if (this.modoModificacion) {
      const confirmar = confirm('¿Desea guardar los cambios antes de salir?');
      if (confirmar && this.documentoSeleccionado) {
        this.guardarCambiosDocumento();
      }
    }
    
    this.modoModificacion = false;
    this.modoDocumentoExistente = true;
    
    // Recargar el documento para mostrar el estado original
    if (this.documentoSeleccionado) {
      this.seleccionarDocumentoExistente(this.documentoSeleccionado);
    }
  }
}