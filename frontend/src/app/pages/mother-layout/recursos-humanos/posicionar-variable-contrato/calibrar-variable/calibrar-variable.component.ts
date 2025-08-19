// calibrar-variable.component.ts
import { Component, EventEmitter, Input, Output, OnInit, ElementRef, ViewChild, OnDestroy, AfterViewInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ContratistaApiService } from '../../../../../services/contratista-api.service';
import { DomSanitizer, SafeUrl } from '@angular/platform-browser';
import { Subscription } from 'rxjs';

// Replicar las interfaces necesarias
interface Ubicacion {
  pagina: number;
  posX: number;
  posY: number;
  id: string;
  // Campos opcionales para coordenadas visuales
  visualX?: number;
  visualY?: number;
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

interface CalibrationSetting {
  id?: number;
  nombre: string;
  escala_x: number;
  escala_y: number;
  offset_x: number;
  offset_y: number;
  invertir_y: boolean;
  activo: boolean;
}

@Component({
  selector: 'app-calibrar-variable',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule
  ],
  templateUrl: './calibrar-variable.component.html',
  styleUrls: ['./calibrar-variable.component.css']
})
export class CalibrarVariableComponent implements OnInit, OnDestroy, AfterViewInit {
  // References to PDF preview elements
  @ViewChild('pdfPreviewContainer') pdfPreviewContainer!: ElementRef;
  @ViewChild('pdfCanvas') pdfCanvas!: ElementRef;
  
  // Propiedades de entrada
  @Input() documentoId: number | null = null;
  @Input() variables: VariableDocumento[] = [];
  
  // Eventos de salida
  @Output() calibracionCompletada = new EventEmitter<any>();
  @Output() cerrarCalibracion = new EventEmitter<void>();
  
  // Estado de la interfaz
  isLoading = false;
  errorMessage: string | null = null;
  successMessage: string | null = null;
  
  // Calibración actual
  calibracionActual: CalibrationSetting = {
    nombre: 'Calibración predeterminada',
    escala_x: 0.72, // Aproximadamente 1.0/1.4
    escala_y: 0.72,
    offset_x: 0,
    offset_y: 0,
    invertir_y: true,
    activo: true
  };
  
  // Lista de calibraciones guardadas
  calibracionesGuardadas: CalibrationSetting[] = [];
  
  // Variable que se está calibrando actualmente
  variableSeleccionada: VariableDocumento | null = null;
  ubicacionSeleccionada: Ubicacion | null = null;
  
  // Control de ajuste
  pixelIncremento: number = 1;
  
  // Historial de PDF generados para calibración
  pdfsGenerados: { url: string, fecha: Date }[] = [];
  
  // Estado del documento
  nombreDocumento: string = '';
  tipoDocumento: string = '';
  
  // Mapa de variables visualizadas en el preview
  variablesMostradas: Map<string, HTMLElement> = new Map();
  
  // PDF viewer properties
  pdfSrc: string | ArrayBuffer | null = null;
  pdfDocument: any = null;
  pdfZoomLevel: number = 1.5;
  currentPage: number = 1;
  pdfPages: any[] = [];
  
  // Preview context
  previewContext: CanvasRenderingContext2D | null = null;
  pdfPreviewLoaded: boolean = false;
  
  // Subscription for API calls
  private subscriptions: Subscription = new Subscription();
  
  // Exponer Math a la plantilla para usar funciones como min/max
  Math = Math;
  
  // Constantes para la calibración del sistema de coordenadas frontend-backend
  COORD_TRANSFORM = {
    // Estos valores deben ajustarse según el comportamiento observado
    // entre el sistema de coordenadas frontend y backend
    SCALE_X: 0.7, // Factor de escala aproximado entre frontend y backend
    SCALE_Y: 0.7,
    OFFSET_X: 0,  // Offset en píxeles
    OFFSET_Y: 0
  };
  
  constructor(
    private apiService: ContratistaApiService,
    private sanitizer: DomSanitizer
  ) {}

  ngOnInit(): void {
    // Cargar documento y calibraciones si hay un ID
    if (this.documentoId) {
      this.cargarDocumento();
      this.cargarCalibraciones();
    }
    
    // Si hay variables, seleccionamos la primera variable colocada
    if (this.variables.length > 0) {
      const variablesColocadas = this.variables.filter(v => v.colocada);
      if (variablesColocadas.length > 0) {
        this.seleccionarVariable(variablesColocadas[0]);
      }
    }
  }
  
  ngOnDestroy(): void {
    this.subscriptions.unsubscribe();
  }

  /**
   * Carga la información del documento desde el backend
   */
  cargarDocumento(): void {
    if (!this.documentoId) return;
    
    this.isLoading = true;
    
    // Usar la nueva URL actualizada
    const subscription = this.apiService.get(`api_obtener-documento/${this.documentoId}/`)
      .subscribe({
        next: (response: any) => {
          this.nombreDocumento = response.nombre;
          this.tipoDocumento = response.tipo;
          
          // Cargar el PDF para la vista previa
          this.pdfSrc = response.archivo_pdf_url;
          
          // Si el documento viene con variables, podemos actualizar nuestra lista
          if (response.variables && Array.isArray(response.variables)) {
            // Solo actualizamos si hay alguna variable nueva o diferente
            const hayCambios = this.actualizarVariablesDesdeBackend(response.variables);
            if (hayCambios) {
              console.log('Variables actualizadas desde backend');
            }
          }
          
          this.isLoading = false;
          
          // Iniciar carga del PDF para la vista previa
          this.cargarPdfParaPreview();
        },
        error: (error) => {
          console.error('Error al cargar documento:', error);
          // No mostramos el error para no interrumpir la experiencia
          // Simplemente continuamos con los datos que ya tenemos
          this.isLoading = false;
        }
      });
      
    this.subscriptions.add(subscription);
  }
  
  /**
   * Actualiza la lista de variables con datos del backend si es necesario
   * @returns true si se realizaron cambios, false si no
   */
  actualizarVariablesDesdeBackend(variablesBackend: any[]): boolean {
    let hayCambios = false;
    
    // Recorremos las variables del backend
    for (const varBackend of variablesBackend) {
      // Buscamos si existe en nuestra lista actual
      const varIndex = this.variables.findIndex(v => v.nombre === varBackend.nombre);
      
      if (varIndex >= 0) {
        // La variable existe, actualizamos sus ubicaciones si hay nuevas
        if (varBackend.ubicaciones && varBackend.ubicaciones.length > 0) {
          // Verificamos si hay ubicaciones nuevas
          for (const ubBackend of varBackend.ubicaciones) {
            const ubExistente = this.variables[varIndex].ubicaciones.find(
              u => u.pagina === ubBackend.pagina && 
                  Math.abs(u.posX - ubBackend.posX) < 5 &&
                  Math.abs(u.posY - ubBackend.posY) < 5
            );
            
            if (!ubExistente) {
              // Es una ubicación nueva, la agregamos
              this.variables[varIndex].ubicaciones.push(ubBackend);
              this.variables[varIndex].colocada = true;
              hayCambios = true;
            }
          }
        }
      }
    }
    
    return hayCambios;
  }
 
  /**
   * Carga todas las páginas del PDF para tenerlas disponibles
   */
  async loadPdfPages(): Promise<void> {
    if (!this.pdfDocument) return;
    
    this.pdfPages = [];
    
    for (let i = 1; i <= this.pdfDocument.numPages; i++) {
      const page = await this.pdfDocument.getPage(i);
      this.pdfPages.push(page);
    }
  }
  
  /**
   * Renderiza la vista previa del PDF en el canvas
   */
  async renderPdfPreview(): Promise<void> {
    if (!this.pdfCanvas || !this.variableSeleccionada || !this.ubicacionSeleccionada) {
      console.log("Faltan elementos necesarios para la vista previa");
      return;
    }
  
    try {
      // Obtener el canvas y su contexto
      const canvas = this.pdfCanvas.nativeElement;
      const ctx = canvas.getContext('2d');
      if (!ctx) return;
  
      // Asegurar que el PDF está cargado
      if (!this.pdfDocument) {
        console.log("PDF no cargado aún");
        return;
      }
  
      // Configurar dimensiones del canvas
      const previewWidth = 400;
      const previewHeight = 300;
      canvas.width = previewWidth;
      canvas.height = previewHeight;
      
      // Limpiar el canvas
      ctx.clearRect(0, 0, canvas.width, canvas.height);
  
      const pageNum = this.ubicacionSeleccionada.pagina;
      
      // Coordenadas frontend de la variable seleccionada
      const frontendX = this.ubicacionSeleccionada.visualX || this.ubicacionSeleccionada.posX;
      const frontendY = this.ubicacionSeleccionada.visualY || this.ubicacionSeleccionada.posY;
      
      // Transformar a coordenadas de backend (estimado según calibración)
      const backendX = frontendX * this.COORD_TRANSFORM.SCALE_X + this.COORD_TRANSFORM.OFFSET_X;
      const backendY = frontendY * this.COORD_TRANSFORM.SCALE_Y + this.COORD_TRANSFORM.OFFSET_Y;
      
      console.log(`Coordenadas frontend: X=${frontendX}, Y=${frontendY}`);
      console.log(`Coordenadas backend estimadas: X=${backendX}, Y=${backendY}`);
      
      // Obtener la página
      const page = await this.pdfDocument.getPage(pageNum);
      
      // Dimensiones originales del PDF
      const originalViewport = page.getViewport({ scale: 1.0 });
      
      // SIMPLIFICACIÓN: Siempre mostrar solo la vista de backend
      
      // Primer paso: renderizar la página completa a escala menor en un canvas temporal
      const tempCanvas = document.createElement('canvas');
      
      // Escala para el canvas temporal
      const tempScale = Math.min(1200 / originalViewport.width, 1800 / originalViewport.height);
      
      // Viewport para la página completa
      const tempViewport = page.getViewport({ scale: tempScale });
      tempCanvas.width = tempViewport.width;
      tempCanvas.height = tempViewport.height;
      
      const tempCtx = tempCanvas.getContext('2d');
      if (!tempCtx) return;
      
      // Renderizar la página completa
      await page.render({
        canvasContext: tempCtx,
        viewport: tempViewport
      }).promise;
      
      // Definir las zonas que queremos mostrar
      const zoomLevel = 0.8; // Zoom más bajo para ver más contexto
      
      // Calcular coordenadas en el canvas temporal
      const tempBackendX = backendX * tempScale;
      const tempBackendY = backendY * tempScale;
      
      // Calcular área a recortar
      const cropWidth = previewWidth / zoomLevel;
      const cropHeight = previewHeight / zoomLevel;
      
      let cropX = tempBackendX - (cropWidth / 2);
      let cropY = tempBackendY - (cropHeight / 2);
      
      // Asegurar que el recorte no se salga del canvas
      cropX = Math.max(0, Math.min(cropX, tempCanvas.width - cropWidth));
      cropY = Math.max(0, Math.min(cropY, tempCanvas.height - cropHeight));
      
      // Dibujar vista
      ctx.drawImage(
        tempCanvas,
        cropX, cropY, cropWidth, cropHeight,
        0, 0, previewWidth, previewHeight
      );
      
      // Calcular posición relativa de la variable en la vista
      const relX = ((tempBackendX - cropX) / cropWidth) * previewWidth;
      const relY = ((tempBackendY - cropY) / cropHeight) * previewHeight;
      
      // Dibujar indicador
      this.drawVariableIndicator(relX, relY, 1, 'rgba(255, 0, 0, 0.8)');
      
      // Mostrar etiqueta de backend
      ctx.fillStyle = 'rgba(0, 0, 0, 0.6)';
      ctx.fillRect(5, 5, 120, 20);
      ctx.font = 'bold 12px Arial';
      ctx.fillStyle = 'white';
      ctx.fillText('Vista del Backend', 15, 20);
      
      // Mostrar información de transformación de coordenadas
      ctx.fillStyle = 'rgba(0, 0, 0, 0.6)';
      ctx.fillRect(5, previewHeight - 25, 240, 20);
      ctx.font = '11px Courier New';
      ctx.fillStyle = 'white';
      ctx.fillText(`Front(${Math.round(frontendX)},${Math.round(frontendY)}) → Back(${Math.round(backendX)},${Math.round(backendY)})`, 10, previewHeight - 10);
      
    } catch (error) {
      console.error("Error al renderizar la vista previa:", error);
      this.errorMessage = `Error`;
    }
  }

  drawClearIndicator(x: number, y: number): void {
    const canvas = this.pdfCanvas.nativeElement;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    // Guardar estado del contexto
    ctx.save();
    
    // Círculo externo con brillo
    ctx.beginPath();
    ctx.arc(x, y, 30, 0, Math.PI * 2);
    ctx.strokeStyle = 'rgba(255, 0, 0, 0.8)';
    ctx.lineWidth = 3;
    ctx.stroke();
    
    // Círculo interno
    ctx.beginPath();
    ctx.arc(x, y, 15, 0, Math.PI * 2);
    ctx.fillStyle = 'rgba(255, 0, 0, 0.3)';
    ctx.fill();
    
    // Cruz centrada
    ctx.beginPath();
    ctx.moveTo(x - 20, y);
    ctx.lineTo(x + 20, y);
    ctx.moveTo(x, y - 20);
    ctx.lineTo(x, y + 20);
    ctx.strokeStyle = 'red';
    ctx.lineWidth = 2;
    ctx.stroke();
    
    // Texto con información de la variable
    ctx.font = 'bold 12px Arial';
    ctx.fillStyle = 'black';
    ctx.fillText(`Variable: ${this.variableSeleccionada?.nombre}`, x - 40, y - 35);
    
    // Coordenadas con fondo para mejor visibilidad
    const coords = `X:${Math.round(this.ubicacionSeleccionada?.posX || 0)}, Y:${Math.round(this.ubicacionSeleccionada?.posY || 0)}`;
    
    const textWidth = ctx.measureText(coords).width;
    ctx.fillStyle = 'rgba(255, 255, 255, 0.7)';
    ctx.fillRect(x - 5, y + 25, textWidth + 10, 20);
    
    ctx.fillStyle = 'red';
    ctx.fillText(coords, x, y + 40);
    
    // Restaurar contexto
    ctx.restore();
  }
  


  async renderFullPageAndCrop(page: any, canvas: HTMLCanvasElement, ctx: CanvasRenderingContext2D,variableX: number, variableY: number): Promise<void> {
    try {
    // Get original viewport
    const originalViewport = page.getViewport({ scale: 1.0 });

    // Calculate an appropriate scale to fit the entire page in a buffer canvas
    const tempCanvas = document.createElement('canvas');
    const fitScale = Math.min(1200 / originalViewport.width, 1800 / originalViewport.height);

    // Create a viewport for the whole page at reduced scale
    const tempViewport = page.getViewport({ scale: fitScale });

    // Set temporary canvas size
    tempCanvas.width = tempViewport.width;
    tempCanvas.height = tempViewport.height;

    // Get context for temp canvas
    const tempCtx = tempCanvas.getContext('2d');
    if (!tempCtx) return;

    // Render the entire page to the temporary canvas
    await page.render({
    canvasContext: tempCtx,
    viewport: tempViewport
    }).promise;

    console.log(`Rendered full page at scale ${fitScale}`);

    // Calculate variable position on the temp canvas
    const tempX = variableX * fitScale;
    const tempY = variableY * fitScale;

    console.log(`Variable on temp canvas: X=${tempX}, Y=${tempY}`);

    // Calculate crop area
    const cropWidth = canvas.width;
    const cropHeight = canvas.height;
    const cropX = Math.max(0, tempX - cropWidth/2);
    const cropY = Math.max(0, tempY - cropHeight/2);

    // Ensure crop area doesn't go outside the page
    const adjustedCropX = Math.min(cropX, tempCanvas.width - cropWidth);
    const adjustedCropY = Math.min(cropY, tempCanvas.height - cropHeight);

    console.log(`Cropping from temp canvas: X=${adjustedCropX}, Y=${adjustedCropY}, W=${cropWidth}, H=${cropHeight}`);

    // Clear the main canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw the cropped area to the main canvas
    ctx.drawImage(
    tempCanvas, 
    adjustedCropX, adjustedCropY, cropWidth, cropHeight,
    0, 0, canvas.width, canvas.height
    );

    // Draw variable indicators
    const finalX = tempX - adjustedCropX;
    const finalY = tempY - adjustedCropY;
    this.drawVariableIndicator(finalX, finalY, 1);

    console.log(`Variable should appear at: X=${finalX}, Y=${finalY}`);
    } catch (error) {
    console.error("Error in renderFullPageAndCrop:", error);
    }
  }

   
  calibrarTransformacionCoordenadas(): void {
    // Esta función podría calcular automáticamente los parámetros de transformación
    // basándose en puntos conocidos en frontend y backend
    
    // Por ahora, implementamos una calibración manual basada en la prueba y error
    
    // Ejemplo: con datos reales de coordenadas frontend y backend equivalentes
    // Frontend: (640, 185) -> Backend: (436, 134)
    
    // Calculamos factores de escala
    const frontendX = 640, frontendY = 185;
    const backendX = 436, backendY = 134;
    
    this.COORD_TRANSFORM.SCALE_X = backendX / frontendX;
    this.COORD_TRANSFORM.SCALE_Y = backendY / frontendY;
    
    // Calculamos offsets si es necesario
    this.COORD_TRANSFORM.OFFSET_X = backendX - (frontendX * this.COORD_TRANSFORM.SCALE_X);
    this.COORD_TRANSFORM.OFFSET_Y = backendY - (frontendY * this.COORD_TRANSFORM.SCALE_Y);
    
    console.log("Calibración de coordenadas:", this.COORD_TRANSFORM);
    
    // Re-renderizar la vista previa con los nuevos parámetros
    setTimeout(() => {
      this.renderPdfPreview();
    }, 0);
  }
  
  
  drawFocusIndicator(x: number, y: number): void {
    if (!this.pdfCanvas) return;
    
    const canvas = this.pdfCanvas.nativeElement;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    // Save current state
    ctx.save();
    
    // Draw crosshair
    ctx.strokeStyle = 'red';
    ctx.lineWidth = 2;
    
    // Horizontal line
    ctx.beginPath();
    ctx.moveTo(x - 15, y);
    ctx.lineTo(x + 15, y);
    ctx.stroke();
    
    // Vertical line
    ctx.beginPath();
    ctx.moveTo(x, y - 15);
    ctx.lineTo(x, y + 15);
    ctx.stroke();
    
    // Draw circle around position
    ctx.beginPath();
    ctx.arc(x, y, 20, 0, Math.PI * 2);
    ctx.strokeStyle = '#4a80f5';
    ctx.lineWidth = 2;
    ctx.stroke();
    
    // Draw variable area rectangle (simulating text area)
    // Use a half-transparent fill
    ctx.fillStyle = 'rgba(74, 128, 245, 0.2)';
    ctx.fillRect(x - 40, y - 10, 80, 20);
    ctx.strokeStyle = '#4a80f5';
    ctx.strokeRect(x - 40, y - 10, 80, 20);
    
    // Add coordinate text
    ctx.fillStyle = 'red';
    ctx.font = '12px Arial';
    ctx.fillText(
      `(${Math.round(this.ubicacionSeleccionada?.posX || 0)},${Math.round(this.ubicacionSeleccionada?.posY || 0)})`,
      x + 25,
      y - 15
    );
    
    // Restore previous state
    ctx.restore();
  }
 
  //
  async cargarPdfParaPreview(): Promise<void> {
  if (!this.pdfSrc) return;
  
  this.isLoading = true;
  this.errorMessage = null;
  
  try {
    console.log("Cargando PDF.js...");
    await this.loadPdfJsScript();
    
    const pdfjsLib = (window as any).pdfjsLib;
    if (!pdfjsLib) {
      throw new Error("PDF.js library not available");
    }
    
    // Configurar worker
    const workerUrl = `https://cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjsLib.version}/pdf.worker.min.js`;
    pdfjsLib.GlobalWorkerOptions.workerSrc = workerUrl;
    
    console.log("Cargando documento PDF...");
    
    // Crear tarea según el tipo de fuente
    let loadingTask;
    if (typeof this.pdfSrc === 'string') {
      console.log("Cargando PDF desde URL", this.pdfSrc);
      loadingTask = pdfjsLib.getDocument({
        url: this.pdfSrc,
        cMapUrl: 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.4.120/cmaps/',
        cMapPacked: true
      });
    } else {
      console.log("Cargando PDF desde datos");
      loadingTask = pdfjsLib.getDocument({
        data: this.pdfSrc,
        cMapUrl: 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.4.120/cmaps/',
        cMapPacked: true
      });
    }
    
    // Cargar el documento
    this.pdfDocument = await loadingTask.promise;
    console.log(`PDF cargado exitosamente con ${this.pdfDocument.numPages} páginas`);
    
    this.pdfPreviewLoaded = true;
    
    // Si hay una variable seleccionada, renderizar la vista previa
    if (this.variableSeleccionada && this.ubicacionSeleccionada) {
      console.log("Renderizando vista previa para la variable seleccionada");
      await this.renderPdfPreview();
    }
  } catch (error) {
    console.error("Error al cargar PDF:", error);
    this.errorMessage = "No se pudo cargar la vista previa del PDF: ";
  } finally {
    this.isLoading = false;
  }
}

  ajustarPosicion(deltaX: number, deltaY: number): void {
    if (!this.ubicacionSeleccionada) return;
    
    // Calcular nueva posición
    const nuevoX = (this.ubicacionSeleccionada.visualX || this.ubicacionSeleccionada.posX) + (deltaX * this.pixelIncremento);
    const nuevoY = (this.ubicacionSeleccionada.visualY || this.ubicacionSeleccionada.posY) + (deltaY * this.pixelIncremento);
    
    // Actualizar posición
    this.ubicacionSeleccionada.visualX = nuevoX;
    this.ubicacionSeleccionada.visualY = nuevoY;
    
    // Actualizar elemento visual
    this.actualizarElementoVisual();
    
    // Actualizar vista previa
    setTimeout(() => {
      this.renderPdfPreview();
    }, 0);
  }

  ajustarTransformacion(param: string, delta: number): void {
    switch(param) {
      case 'SCALE_X':
        this.COORD_TRANSFORM.SCALE_X += delta * 0.01;
        break;
      case 'SCALE_Y':
        this.COORD_TRANSFORM.SCALE_Y += delta * 0.01;
        break;
      case 'OFFSET_X':
        this.COORD_TRANSFORM.OFFSET_X += delta;
        break;
      case 'OFFSET_Y':
        this.COORD_TRANSFORM.OFFSET_Y += delta;
        break;
    }
    
    // Actualizar vista previa
    this.renderPdfPreview();
  }

  establecerPuntoDeCalibración(frontendX: number, frontendY: number, backendX: number, backendY: number): void {
    // Calcular transformación
    this.COORD_TRANSFORM.SCALE_X = backendX / frontendX;
    this.COORD_TRANSFORM.SCALE_Y = backendY / frontendY;
    this.COORD_TRANSFORM.OFFSET_X = 0;
    this.COORD_TRANSFORM.OFFSET_Y = 0;
    
    console.log(`Calibración establecida: ${JSON.stringify(this.COORD_TRANSFORM)}`);
    
    // Actualizar vista previa
    this.renderPdfPreview();
  }
  
  /**
   * NOTA: Para inicializar los valores de transformación correctos, debes
   * llamar a este método cuando tengas una variable correctamente posicionada.
   */
  inicializarTransformacionCoordenadas(): void {
    // Si ya tenemos datos de un par de puntos frontend-backend,
    // podemos inicializar la transformación aquí
    
    // Ejemplo: coordenadas correctas de una variable
    // Frontend: (640, 185) -> Backend: (436, 134)
    this.establecerPuntoDeCalibración(640, 185, 436, 134);
  }

/**
 * Carga el script de PDF.js
 */
private loadPdfJsScript(): Promise<void> {
  return new Promise((resolve, reject) => {
    // Si ya está cargado, resolvemos inmediatamente
    if ((window as any).pdfjsLib) {
      resolve();
      return;
    }
    
    // Cargar versión específica para estabilidad
    const pdfJsVersion = '3.4.120';
    const scriptSrc = `https://cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfJsVersion}/pdf.min.js`;
    
    console.log("Cargando PDF.js desde:", scriptSrc);
    
    const script = document.createElement('script');
    script.src = scriptSrc;
    script.onload = () => {
      console.log("PDF.js cargado exitosamente");
      resolve();
    };
    script.onerror = (e) => {
      console.error("Error al cargar PDF.js:", e);
      reject(new Error('Error al cargar PDF.js'));
    };
    document.head.appendChild(script);
  });
}
  
  // Enhanced variable indicator drawing
  drawVariableIndicator(x: number, y: number, scale: number, color?: string): void {
    if (!this.pdfCanvas) return;
    
    const canvas = this.pdfCanvas.nativeElement;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    // Save current context state
    ctx.save();
    
    // Draw highlighted area for the variable
    ctx.fillStyle = color || 'rgba(74, 128, 245, 0.2)';
    ctx.strokeStyle = '#4a80f5';
    ctx.lineWidth = 2;
    
    // Variable text area dimensions (scaled)
    const width = 80 * scale;
    const height = 20 * scale;
    
    // Draw rectangle (centered on variable position)
    const rectX = x - (width/2);
    const rectY = y - (height/2);
    ctx.fillRect(rectX, rectY, width, height);
    ctx.strokeRect(rectX, rectY, width, height);
    
    // Draw crosshair at exact position
    ctx.strokeStyle = '#ff0000';
    ctx.lineWidth = 1;
    const crossSize = 10 * scale;
    
    // Horizontal line
    ctx.beginPath();
    ctx.moveTo(x - crossSize, y);
    ctx.lineTo(x + crossSize, y);
    ctx.stroke();
    
    // Vertical line
    ctx.beginPath();
    ctx.moveTo(x, y - crossSize);
    ctx.lineTo(x, y + crossSize);
    ctx.stroke();
    
    // Add coordinates text
    ctx.fillStyle = '#ff0000';
    ctx.font = `${10 * scale}px Arial`;
    ctx.fillText(
      `(${Math.round(this.ubicacionSeleccionada?.posX || 0)},${Math.round(this.ubicacionSeleccionada?.posY || 0)})`, 
      x + (15 * scale), 
      y + (15 * scale)
    );
    
    // Restore context
    ctx.restore();
  }
  
  // Add this helper method to get correct page scaling
  getPageScale(page: any): number {
    const viewport = page.getViewport({ scale: 1.0 });
    const containerWidth = 400; // Fixed preview container width
    return containerWidth / viewport.width;
  }
  
  
  // Make sure this is called in ngAfterViewInit
  ngAfterViewInit(): void {
    // Call base implementation if it exists
    if (this.pdfCanvas) {
      console.log("PDF Canvas reference available");
      
      // Initialize canvas context
      const canvas = this.pdfCanvas.nativeElement;
      if (canvas) {
        this.previewContext = canvas.getContext('2d');
        console.log("Canvas context initialized:", !!this.previewContext);
      }
      
      // If PDF source is already available, start loading
      if (this.pdfSrc && !this.pdfPreviewLoaded) {
        console.log("PDF source available, starting load");
        setTimeout(() => {
          this.cargarPdfParaPreview();
        }, 100);
      }
    }
  }
  //

  generarPDFPruebaCompleto(): void {
    if (!this.documentoId) {
      this.errorMessage = 'No se puede generar el PDF: falta ID de documento';
      return;
    }
    
    this.isLoading = true;
    
    // Preparar datos de prueba para todas las variables colocadas
    let datosVariables: { [key: string]: string } = {};
    
    // Variables para las que tenemos valores colocados
    const variablesColocadas = this.variables.filter(v => v.colocada);
    
    variablesColocadas.forEach(v => {
      let valorPrueba = '';
      
      // Determinar un valor de prueba según el tipo de variable
      if (v.nombre.includes('fecha') || v.nombre.includes('f_')) {
        valorPrueba = "01/01/2023";
      } else if (v.nombre === 'rut' || v.nombre === 'dni') {
        valorPrueba = "12.345.678-9";
      } else if (v.nombre === 'nombre') {
        valorPrueba = "Juan Pérez";
      } else if (v.nombre === 'nacionalidad') {
        valorPrueba = "Chilena";
      } else if (v.nombre === 'e_civil') {
        valorPrueba = "Soltero";
      } else if (v.nombre === 'domicilio') {
        valorPrueba = "Av. Ejemplo 123, Santiago";
      } else if (v.nombre === 'telefono') {
        valorPrueba = "+56 9 1234 5678";
      } else if (v.nombre === 'correo') {
        valorPrueba = "ejemplo@correo.com";
      } else {
        valorPrueba = `Prueba-${v.nombre}`;
      }
      
      datosVariables[v.nombre] = valorPrueba;
    });
    
    console.log('Generando PDF completo con calibración:', {
      documento_id: this.documentoId,
      escala_x: this.calibracionActual.escala_x,
      escala_y: this.calibracionActual.escala_y,
      offset_x: this.calibracionActual.offset_x,
      offset_y: this.calibracionActual.offset_y,
      invertir_y: this.calibracionActual.invertir_y,
      datos_variables: datosVariables
    });
    
    // Enviar solicitud al backend para generar el PDF con los parámetros de calibración actuales
    const subscription = this.apiService.post('api_ajustar_calibracion/', {
      documento_id: this.documentoId,
      escala_x: this.calibracionActual.escala_x,
      escala_y: this.calibracionActual.escala_y,
      offset_x: this.calibracionActual.offset_x,
      offset_y: this.calibracionActual.offset_y,
      invertir_y: this.calibracionActual.invertir_y,
      datos_variables: datosVariables
    })
      .subscribe({
        next: (response: any) => {
          // Guardar el PDF generado en el historial
          this.pdfsGenerados.unshift({
            url: response.url,
            fecha: new Date()
          });
          
          // Abrir el PDF en una nueva ventana
          window.open(response.url, '_blank');
          
          this.isLoading = false;
          this.successMessage = 'PDF de prueba generado correctamente';
          
          // Ocultar mensaje después de 3 segundos
          setTimeout(() => {
            this.successMessage = null;
          }, 3000);
        },
        error: (error) => {
          console.error('Error al generar PDF de prueba:', error);
          this.errorMessage = `Error: ${error.error?.error || 'No se pudo generar el PDF de prueba'}`;
          this.isLoading = false;
        }
      });
      
    this.subscriptions.add(subscription);
  }
  
  /**
   * Carga las calibraciones existentes para este documento
   */
  cargarCalibraciones(): void {
    if (!this.documentoId) return;
    
    this.isLoading = true;
    const subscription = this.apiService.get(`api_calibraciones/${this.documentoId}/`)
      .subscribe({
        next: (response: any) => {
          this.isLoading = false;
          if (Array.isArray(response)) {
            this.calibracionesGuardadas = response;
            
            // Si hay una calibración activa, cargarla como actual
            const calibracionActiva = this.calibracionesGuardadas.find(c => c.activo);
            if (calibracionActiva) {
              this.calibracionActual = { ...calibracionActiva };
            }
          }
        },
        error: (error) => {
          console.error('Error al cargar calibraciones:', error);
          this.isLoading = false;
          // No mostramos error ya que podría ser que no haya calibraciones aún
        }
      });
      
    this.subscriptions.add(subscription);
  }
  
  /**
   * Selecciona una variable para calibrar
   */
  seleccionarVariable(variable: VariableDocumento): void {
    this.variableSeleccionada = variable;
    
    // Si la variable tiene ubicaciones, seleccionar la última
    if (variable.ubicaciones && variable.ubicaciones.length > 0) {
      // Clonamos la ubicación para no modificar la original directamente
      this.ubicacionSeleccionada = {...variable.ubicaciones[variable.ubicaciones.length - 1]};
      
      // Inicializamos las coordenadas visuales con las originales
      this.ubicacionSeleccionada.visualX = this.ubicacionSeleccionada.posX;
      this.ubicacionSeleccionada.visualY = this.ubicacionSeleccionada.posY;
      
      // Renderizar la vista previa del PDF
      if (this.pdfPreviewLoaded) {
        setTimeout(() => {
          this.renderPdfPreview();
        }, 0);
      }
    } else {
      this.errorMessage = 'Esta variable no tiene ubicaciones definidas';
      this.variableSeleccionada = null;
    }
  }
  
 
  
  /**
   * Actualiza la representación visual de la variable
   */
  actualizarElementoVisual(): void {
    if (!this.variableSeleccionada || !this.ubicacionSeleccionada) return;
    
    const elementId = `visual-${this.variableSeleccionada.nombre}`;
    const element = document.getElementById(elementId);
    
    if (element) {
      element.style.left = `${this.ubicacionSeleccionada.visualX}px`;
      element.style.top = `${this.ubicacionSeleccionada.visualY}px`;
    }
  }
  
  /**
   * Ajusta parámetros de calibración (escala y offset)
   */
  ajustarParametro(parametro: keyof CalibrationSetting, delta: number): void {
    if (!parametro) return;
    
    // Check if we're dealing with a numeric property
    if (
      parametro === 'escala_x' || 
      parametro === 'escala_y' || 
      parametro === 'offset_x' || 
      parametro === 'offset_y'
    ) {
      const incremento = parametro.includes('escala') ? 0.01 : 1;
      const valorActual = this.calibracionActual[parametro] as number;
      
      if (parametro.includes('escala')) {
        // Para escalas, mantenemos entre 0.01 y 2.0
        this.calibracionActual[parametro] = Math.max(0.01, Math.min(2.0, valorActual + (delta * incremento)));
      } else {
        // Para offsets, actualizamos sin restricciones
        this.calibracionActual[parametro] = valorActual + (delta * incremento);
      }
      
      // Redondeamos a 2 decimales para evitar problemas de precisión
      if (parametro.includes('escala')) {
        this.calibracionActual[parametro] = Math.round((this.calibracionActual[parametro] as number) * 100) / 100;
      }
    }
  }
  
  /**
   * Alterna el valor de invertir_y
   */
  toggleInvertirY(): void {
    this.calibracionActual.invertir_y = !this.calibracionActual.invertir_y;
  }
  
  /**
   * Genera un PDF de prueba con la variable seleccionada y la calibración actual
   */
  generarPDFPrueba(): void {
    if (!this.variableSeleccionada || !this.ubicacionSeleccionada || !this.documentoId) {
      this.errorMessage = 'No se puede generar el PDF: falta información necesaria';
      return;
    }
    
    this.isLoading = true;
    
    // Preparar datos de prueba para la variable seleccionada
    let datosVariables: { [key: string]: string } = {};
    
    // Determinar un valor de prueba según el tipo de variable
    let valorPrueba = '';
    if (this.variableSeleccionada.nombre.includes('fecha') || this.variableSeleccionada.nombre.includes('f_')) {
      valorPrueba = '01/01/2023';
    } else if (this.variableSeleccionada.nombre === 'rut' || this.variableSeleccionada.nombre === 'dni') {
      valorPrueba = '12.345.678-9';
    } else if (this.variableSeleccionada.nombre === 'nombre') {
      valorPrueba = 'Juan Pérez';
    } else {
      valorPrueba = `Prueba-${this.variableSeleccionada.nombre}`;
    }
    
    datosVariables[this.variableSeleccionada.nombre] = valorPrueba;
    
    console.log('Generando PDF con calibración:', {
      documento_id: this.documentoId,
      escala_x: this.calibracionActual.escala_x,
      escala_y: this.calibracionActual.escala_y,
      offset_x: this.calibracionActual.offset_x,
      offset_y: this.calibracionActual.offset_y,
      invertir_y: this.calibracionActual.invertir_y,
      variable_nombre: this.variableSeleccionada.nombre,
      datos_variables: datosVariables
    });
    
    // Enviar solicitud al backend para generar el PDF
    const subscription = this.apiService.post('api_ajustar_calibracion/', {
      documento_id: this.documentoId,
      escala_x: this.calibracionActual.escala_x,
      escala_y: this.calibracionActual.escala_y,
      offset_x: this.calibracionActual.offset_x,
      offset_y: this.calibracionActual.offset_y,
      invertir_y: this.calibracionActual.invertir_y,
      variable_nombre: this.variableSeleccionada.nombre,
      datos_variables: datosVariables
    })
      .subscribe({
        next: (response: any) => {
          // Guardar el PDF generado en el historial
          this.pdfsGenerados.unshift({
            url: response.url,
            fecha: new Date()
          });
          
          // Abrir el PDF en una nueva ventana
          window.open(response.url, '_blank');
          
          this.isLoading = false;
          this.successMessage = 'PDF de calibración generado correctamente';
          
          // Ocultar mensaje después de 3 segundos
          setTimeout(() => {
            this.successMessage = null;
          }, 3000);
        },
        error: (error) => {
          console.error('Error al generar PDF de calibración:', error);
          this.errorMessage = `Error: ${error.error?.error || 'No se pudo generar el PDF de calibración'}`;
          this.isLoading = false;
        }
      });
      
    this.subscriptions.add(subscription);
  }
  
  
  /**
   * Aplica los cambios de posición a la ubicación de la variable
   */
  aplicarCalibracion(): void {
    if (!this.ubicacionSeleccionada || !this.variableSeleccionada) return;
    
    // Get updated coordinates
    const posX = this.ubicacionSeleccionada.visualX || this.ubicacionSeleccionada.posX;
    const posY = this.ubicacionSeleccionada.visualY || this.ubicacionSeleccionada.posY;
    
    // Update the position in the variable
    const ubicacionIndex = this.variableSeleccionada.ubicaciones.findIndex(
      u => u.id === this.ubicacionSeleccionada?.id
    );
    
    if (ubicacionIndex !== -1) {
      // Update in memory
      this.variableSeleccionada.ubicaciones[ubicacionIndex].posX = posX;
      this.variableSeleccionada.ubicaciones[ubicacionIndex].posY = posY;
      
      // Also update the main variable position if this is the latest ubicación
      if (ubicacionIndex === this.variableSeleccionada.ubicaciones.length - 1) {
        this.variableSeleccionada.posX = posX;
        this.variableSeleccionada.posY = posY;
      }
      
      // Save changes to the database
      this.saveChangesToDatabase();
    }
  }

  saveChangesToDatabase(): void {
    if (!this.documentoId) return;
    
    this.isLoading = true;
    const subscription = this.apiService.put(`api_obtener-documento/${this.documentoId}/`, {
      variables: this.variables
    }).subscribe({
      next: (response) => {
        this.isLoading = false;
        this.successMessage = 'Posición guardada correctamente en la base de datos';
        setTimeout(() => this.successMessage = null, 3000);
      },
      error: (error) => {
        this.isLoading = false;
        this.errorMessage = `Error al guardar: ${error.message}`;
      }
    });
    
    this.subscriptions.add(subscription);
  }
  
  /**
   * Reestablece la posición original de la variable
   */
  reestablecerPosicion(): void {
    if (!this.variableSeleccionada || !this.ubicacionSeleccionada) return;
    
    // Volver a los valores originales
    this.ubicacionSeleccionada.visualX = this.ubicacionSeleccionada.posX;
    this.ubicacionSeleccionada.visualY = this.ubicacionSeleccionada.posY;
    
    // Actualizar visualización
    this.actualizarElementoVisual();
    
    // Actualizar la vista previa
    this.renderPdfPreview();
    
    this.successMessage = 'Posición restablecida a los valores originales';
    
    // Ocultar mensaje después de 2 segundos
    setTimeout(() => {
      this.successMessage = null;
    }, 2000);
  }
  
  /**
   * Guarda la calibración actual en el backend
   */
  guardarCalibracion(): void {
    if (!this.documentoId) {
      this.errorMessage = 'No se puede guardar: falta ID de documento';
      return;
    }
    
    this.isLoading = true;
    
    // Preparar datos para guardar
    const datosGuardar = {
      documento_id: this.documentoId,
      nombre: this.calibracionActual.nombre,
      escala_x: this.calibracionActual.escala_x,
      escala_y: this.calibracionActual.escala_y,
      offset_x: this.calibracionActual.offset_x,
      offset_y: this.calibracionActual.offset_y,
      invertir_y: this.calibracionActual.invertir_y,
      activo: true // Por defecto, activamos la nueva calibración
    };
    
    const subscription = this.apiService.post('api_calibraciones/', datosGuardar)
      .subscribe({
        next: (response: any) => {
          // Actualizar lista de calibraciones
          const nuevaCalibracion = {
            ...this.calibracionActual,
            id: response.id
          };
          
          // Desactivar las calibraciones actuales
          this.calibracionesGuardadas.forEach(c => c.activo = false);
          
          // Añadir la nueva calibración a la lista
          this.calibracionesGuardadas.push(nuevaCalibracion);
          
          this.isLoading = false;
          this.successMessage = 'Calibración guardada correctamente';
          
          // Ocultar mensaje después de 3 segundos
          setTimeout(() => {
            this.successMessage = null;
          }, 3000);
        },
        error: (error) => {
          console.error('Error al guardar calibración:', error);
          this.errorMessage = `Error: ${error.error?.error || 'No se pudo guardar la calibración'}`;
          this.isLoading = false;
        }
      });
      
    this.subscriptions.add(subscription);
  }
  
  /**
   * Carga una calibración guardada
   */
  cargarCalibracionGuardada(calibracion: CalibrationSetting): void {
    this.calibracionActual = {...calibracion};
    
    this.successMessage = `Calibración "${calibracion.nombre}" cargada`;
    
    // Ocultar mensaje después de 2 segundos
    setTimeout(() => {
      this.successMessage = null;
    }, 2000);
  }
  
  /**
   * Establece una calibración como activa
   */
  establecerCalibracionComoActiva(calibracionId: number): void {
    if (!this.documentoId) return;
    
    this.isLoading = true;
    const subscription = this.apiService.put(`api_calibracion/${calibracionId}/`, {
      activo: true
    }).subscribe({
      next: () => {
        // Actualizar estado de las calibraciones
        this.calibracionesGuardadas.forEach(c => {
          c.activo = c.id === calibracionId;
        });
        
        // Actualizar la calibración actual si es la que se activó
        const calibracionActivada = this.calibracionesGuardadas.find(c => c.id === calibracionId);
        if (calibracionActivada) {
          this.calibracionActual = {...calibracionActivada};
        }
        
        this.isLoading = false;
        this.successMessage = 'Calibración establecida como activa';
        
        // Ocultar mensaje después de 3 segundos
        setTimeout(() => {
          this.successMessage = null;
        }, 3000);
      },
      error: (error) => {
        console.error('Error al activar calibración:', error);
        this.errorMessage = `Error: ${error.error?.error || 'No se pudo activar la calibración'}`;
        this.isLoading = false;
      }
    });
    
    this.subscriptions.add(subscription);
  }
  
  /**
   * Guarda los cambios y cierra el componente
   */
  finalizarCalibracion(): void {
    // Emitir evento con datos actualizados
    this.calibracionCompletada.emit({
      variables: this.variables,
      calibracion: this.calibracionActual
    });
  }
  
  /**
   * Cancela la calibración sin guardar cambios
   */
  cancelar(): void {
    // Emitir evento de cancelación
    this.cerrarCalibracion.emit();
  }
  
  /**
   * Devuelve una URL segura para mostrar en un iframe
   */
  getSafeUrl(url: string): SafeUrl {
    return this.sanitizer.bypassSecurityTrustResourceUrl(url);
  }
  
  /**
   * Métodos para mostrar coordenadas backend en la vista
   */
  getBackendX(): number {
    if (!this.ubicacionSeleccionada) return 0;
    const x = this.ubicacionSeleccionada.visualX || this.ubicacionSeleccionada.posX;
    return x * this.COORD_TRANSFORM.SCALE_X + this.COORD_TRANSFORM.OFFSET_X;
  }
  
  getBackendY(): number {
    if (!this.ubicacionSeleccionada) return 0;
    const y = this.ubicacionSeleccionada.visualY || this.ubicacionSeleccionada.posY;
    return y * this.COORD_TRANSFORM.SCALE_Y + this.COORD_TRANSFORM.OFFSET_Y;
  }
}