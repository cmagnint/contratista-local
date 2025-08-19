import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpEvent, HttpParams } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, map, retry, switchMap, timeout } from 'rxjs/operators';
import { JwtService } from './jwt.service';  // Importar nuestro JWT service

@Injectable({
  providedIn: 'root'
})
export class ContratistaApiService {
  public baseUrl = '/contratista_test_api';

  constructor(
    private http: HttpClient,
    private jwtService: JwtService  // Inyectar JWT service
  ) { }

  /**
   * 🎯 LOGIN SIMPLE - ESTÁNDAR DE INDUSTRIA
   * Método simplificado que envía contraseña en texto plano sobre HTTPS
   * Django maneja la validación y hash internamente
   */
  login(rut: string, password: string, origin: string = 'WEB'): Observable<any> {
    const loginData = {
      rut: rut,
      password: password,  
      origin: origin
    };

    console.log('📤 Enviando login simple a:', `${this.baseUrl}/api_login/`);
    
    return this.http.post(`${this.baseUrl}/api_login/`, loginData, {
      headers: new HttpHeaders({
        'Content-Type': 'application/json'
      })
    });
  }

  /**
   * Verifica si el JWT token es válido en el backend
   */
  verifyJWT(jwtToken?: string): Observable<any> {
    const token = jwtToken || this.jwtService.getToken();
    if (!token) {
      return throwError('No JWT token available');
    }

    const headers = new HttpHeaders({
      'Content-Type': 'application/json'
    });

    return this.http.post(`${this.baseUrl}/verify_jwt/`, { jwt_token: token }, { headers });
  }

  /**
   * Refresca el JWT token usando refresh token
   */
  refreshJWT(): Observable<any> {
    const refreshToken = this.jwtService.getRefreshToken();
    if (!refreshToken) {
      return throwError('No refresh token available');
    }

    const headers = new HttpHeaders({
      'Content-Type': 'application/json'
    });

    return this.http.post(`${this.baseUrl}/refresh_jwt/`, { refresh_token: refreshToken }, { headers });
  }

  /**
   * Método especial para descargar archivos con seguimiento de progreso.
   */
  getFile(endpoint: string): Observable<HttpEvent<Blob>> {
    const headers = this.createFileHeaders();
    
    return this.http.get(`${this.baseUrl}/${endpoint}`, {
      headers: headers,
      responseType: 'blob',    
      observe: 'events',       
      reportProgress: true     
    });
  }

  get(endpoint: string): Observable<any> {
    const headers = this.createHeaders();
    return this.http.get(`${this.baseUrl}/${endpoint}`, { headers });
  }

  getBlob(endpoint: string): Observable<Blob> {
    const headers = this.createHeaders();
    return this.http.get(`${this.baseUrl}/${endpoint}`, { 
      headers, 
      responseType: 'blob' 
    });
  }

  getPDF(endpoint: string): Observable<Blob> {
    const headers = this.createFileHeaders();
    return this.http.get(`${this.baseUrl}/${endpoint}`, { 
        headers, 
        responseType: 'blob',
        observe: 'body'
    });
  }

  postBlob(endpoint: string, data: any): Observable<Blob> {
    const headers = this.createHeaders();
    return this.http.post(`${this.baseUrl}/${endpoint}`, data, { 
      headers, 
      responseType: 'blob' 
    });
  }

  post(endpoint: string, data: any): Observable<any> {
    const headers = this.createHeaders();
    return this.http.post(`${this.baseUrl}/${endpoint}`, data, { headers });
  }

  postFormData(endpoint: string, formData: FormData): Observable<any> {
    const headers = this.createFileHeaders();
    return this.http.post(`${this.baseUrl}/${endpoint}`, formData, { headers });
  }

  delete(endpoint: string, data: any): Observable<any> {
    const headers = this.createHeaders();
    const options = {
        headers: headers,
        body: data
    };
    return this.http.delete(`${this.baseUrl}/${endpoint}`, options);
  }

  patch(endpoint: string, data: any): Observable<any> {
    const headers = this.createHeaders();
    return this.http.patch(`${this.baseUrl}/${endpoint}`, data, { headers });
  }

  put(endpoint: string, data: any): Observable<any> {
    const headers = this.createHeaders();
    return this.http.put(`${this.baseUrl}/${endpoint}`, data, { headers });
  }

  /**
   * Crea headers estándar para las peticiones JSON con JWT
   */
  private createHeaders(): HttpHeaders {
    const jwtToken = this.jwtService.getToken();
    const headers: any = {
      'Content-Type': 'application/json'
    };

    if (jwtToken) {
      headers['Authorization'] = `Bearer ${jwtToken}`;
    }

    return new HttpHeaders(headers);
  }

  /**
   * Crea headers específicos para la descarga de archivos y FormData con JWT
   */
  private createFileHeaders(): HttpHeaders {
    const jwtToken = this.jwtService.getToken();
    const headers: any = {};

    if (jwtToken) {
      headers['Authorization'] = `Bearer ${jwtToken}`;
    }

    return new HttpHeaders(headers);
  }

  /**
   * Manejo mejorado de errores específico para JWT
   */
  private handleError = (error: any) => {
    let errorMessage = 'Ha ocurrido un error desconocido';
    
    if (error.error instanceof ErrorEvent) {
      errorMessage = `Error: ${error.error.message}`;
    } else {
      switch (error.status) {
        case 401:
          // Token expirado o inválido
          this.jwtService.clearTokens();
          errorMessage = 'Sesión expirada. Por favor, inicie sesión nuevamente.';
          break;
        case 403:
          errorMessage = 'No tiene permisos para realizar esta acción.';
          break;
        case 404:
          errorMessage = 'Recurso no encontrado.';
          break;
        case 500:
          errorMessage = 'Error interno del servidor.';
          break;
        default:
          errorMessage = `Código de error: ${error.status}\nMensaje: ${error.message}`;
      }
    }
    
    return throwError(errorMessage);
  }

  /**
   * Método con retry automático y manejo de JWT
   */
  private requestWithRetry<T>(request: Observable<T>, maxRetries: number = 3): Observable<T> {
    return request.pipe(
      retry(maxRetries),
      timeout(30000),
      catchError(this.handleError)
    );
  }

  /**
   * GET con manejo de errores mejorado y auto-refresh de JWT
   */
  getSafe(endpoint: string): Observable<any> {
    // Verificar si el token está expirado antes de hacer la petición
    if (this.jwtService.isTokenExpired()) {
      // Intentar refrescar token automáticamente
      return this.refreshJWT().pipe(
        map((response: any) => {
          if (response.success) {
            this.jwtService.storeToken(response.jwt_token);
            // Retry original request con nuevo token
            return this.get(endpoint);
          } else {
            throw new Error('Unable to refresh token');
          }
        }),
        catchError(() => {
          // Si no se puede refrescar, limpiar tokens y lanzar error
          this.jwtService.clearTokens();
          return throwError('Session expired. Please login again.');
        })
      );
    }

    const headers = this.createHeaders();
    const request = this.http.get(`${this.baseUrl}/${endpoint}`, { headers });
    return this.requestWithRetry(request);
  }

  /**
   * POST con manejo de errores mejorado y auto-refresh de JWT
   */
  postSafe(endpoint: string, data: any): Observable<any> {
    // Verificar token como en getSafe()
    if (this.jwtService.isTokenExpired()) {
      return this.refreshJWT().pipe(
        map((response: any) => {
          if (response.success) {
            this.jwtService.storeToken(response.jwt_token);
            return this.post(endpoint, data);
          } else {
            throw new Error('Unable to refresh token');
          }
        }),
        catchError(() => {
          this.jwtService.clearTokens();
          return throwError('Session expired. Please login again.');
        })
      );
    }

    const headers = this.createHeaders();
    const request = this.http.post(`${this.baseUrl}/${endpoint}`, data, { headers });
    return this.requestWithRetry(request);
  }

  /**
   * Verifica conectividad con el servidor
   */
  checkServerHealth(): Observable<any> {
    return this.http.get(`${this.baseUrl}/health/`).pipe(
      timeout(5000),
      catchError(error => {
        console.error('Servidor no disponible:', error);
        return throwError('Servidor no disponible');
      })
    );
  }

  /**
   * Limpia caché local y tokens
   */
  clearLocalCache(): void {
    this.jwtService.clearTokens();
    
    if (typeof localStorage !== 'undefined') {
      const keysToRemove = Object.keys(localStorage).filter(key => 
        key.startsWith('cache_') || key.startsWith('temp_')
      );
      keysToRemove.forEach(key => localStorage.removeItem(key));
    }
  }

  /**
   * Obtiene información de depuración incluyendo JWT
   */
  getDebugInfo(): any {
    const userInfo = this.jwtService.getUserInfo();
    return {
      baseUrl: this.baseUrl,
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      hasJWT: !!this.jwtService.getToken(),
      jwtExpired: this.jwtService.isTokenExpired(),
      userInfo: userInfo,
      hasRefreshToken: !!this.jwtService.getRefreshToken()
    };
  }

  // ===============================================================
  // MÉTODOS ESPECÍFICOS PARA INTERACCIÓN CON SII (MANUAL)
  // ===============================================================

  /**
   * Login con el SII usando credenciales 
   * Ahora muestra la página principal después del login
   */
  loginSII(rut: string, password: string): Observable<any> {
    const data = {
      action: 'login',
      rut: rut,
      password: password,
      show_main_page: true // Nuevo parámetro para indicar que queremos mostrar la página principal
    };
    return this.post('facturas_sii_compra_distribuidas/', data);
  }

  /**
   * Obtiene las empresas disponibles para un tipo de documento específico
   */
  getSIICompanies(sessionId: string, tipoDocumento: 'emitidos' | 'recibidos'): Observable<any> {
    const data = {
      action: 'get_companies',
      session_id: sessionId,
      tipo_documento: tipoDocumento
    };
    return this.post('facturas_sii_compra_distribuidas/', data);
  }

  /**
   * Selecciona una empresa después del login exitoso
   * Ahora recibe el tipo de documento (emitidos o recibidos)
   */
  selectCompany(sessionId: string, empresaSeleccionada: string, tipoDocumento: 'emitidos' | 'recibidos'): Observable<any> {
    const data = {
      action: 'select_company',
      session_id: sessionId,
      empresa_seleccionada: empresaSeleccionada,
      tipo_documento: tipoDocumento
    };
    return this.post('facturas_sii_compra_distribuidas/', data);
  }

  /**
   * Busca documentos con los filtros proporcionados
   * Si no se proporcionan filtros, devuelve todos los documentos
   * Ahora recibe el tipo de documento (emitidos o recibidos)
   */
  searchDocuments(
    sessionId: string,
    tipoDocumento: 'emitidos' | 'recibidos',
    filters: {
      rut_receptor?: string,
      rut_emisor?: string,
      folio?: string,
      razon_social?: string,
      fecha_desde?: string | Date,
      fecha_hasta?: string | Date,
      tipo_documento?: string,  // Este es el filtro específico del tipo de documento
      estado_documento?: string
    } = {}
  ): Observable<any> {
    // Preparamos el objeto de datos
    const data: any = {
      action: 'search_documents',
      session_id: sessionId,
      tipo_documento: tipoDocumento  // Este especifica si son emitidos o recibidos
    };
    
    // Agregamos los filtros, transformando fechas y renombrando tipo_documento
    Object.keys(filters).forEach(key => {
      const typedKey = key as keyof typeof filters;
      const value = filters[typedKey];
      
      // Transformar fechas de Date a string YYYY-MM-DD
      if (value instanceof Date) {
        data[key] = `${value.getFullYear()}-${String(value.getMonth() + 1).padStart(2, '0')}-${String(value.getDate()).padStart(2, '0')}`;
      } else if (value !== undefined && value !== null && value !== '') {
        // Manejar el caso especial del filtro tipo_documento
        if (key === 'tipo_documento') {
          // Renombrar para evitar conflicto con el parámetro del request
          data['tipo_documento_filtro'] = value;
        } else {
          data[key] = value;
        }
      }
    });
    
    console.log('Datos enviados al backend:', data);
    
    return this.post('facturas_sii_compra_distribuidas/', data);
  }

  /**
   * Método para visualizar un PDF local (para simulación)
   */
  viewLocalPDF(documentIndex: number): Observable<any> {
    const data = {
      action: 'view_local_pdf',
      documento_index: documentIndex,
    }
    return this.post('facturas_sii_compra_distribuidas/', data).pipe(
      map(response => {
        // Si la respuesta es exitosa y contiene datos, procesamos para descargar
        if (response.status === 'success' && response.data) {
          return response;
        }
        throw new Error('No se pudo procesar la respuesta del servidor');
      }),
      catchError(error => {
        console.error('Error en viewLocalPDF:', error);
        return throwError(error);
      })
    );
  }

  /**
   * Descarga un documento específico desde el SII
   */
  downloadDocument(sessionId: string, documentoUrl: string, tipoDocumento: 'emitidos' | 'recibidos'): Observable<any> {
    const data = {
      action: 'download_document',
      session_id: sessionId,
      documento_url: documentoUrl,
      tipo_documento: tipoDocumento
    };
    return this.post('facturas_sii_compra_distribuidas/', data);
  }

  /**
   * Descarga reporte en Excel desde el SII
   */
  downloadExcel(sessionId: string, tipoDocumento: 'emitidos' | 'recibidos', filtros: any = {}): Observable<any> {
    const data = {
      action: 'download_excel',
      session_id: sessionId,
      tipo_documento: tipoDocumento,
      ...filtros
    };
    return this.post('facturas_sii_compra_distribuidas/', data);
  }

  /**
   * Cierra la sesión del SII
   */
  closeSIISession(sessionId: string): Observable<any> {
    const data = {
      action: 'close_session',
      session_id: sessionId
    };
    return this.post('facturas_sii_compra_distribuidas/', data);
  }

  /**
   * Verifica el estado de una sesión del SII
   */
  checkSIISessionStatus(sessionId: string): Observable<any> {
    const data = {
      action: 'check_session_status',
      session_id: sessionId
    };
    return this.post('facturas_sii_compra_distribuidas/', data);
  }

  // ===============================================================
  // MÉTODOS PARA FACTURAS DE COMPRA MANUAL
  // ===============================================================

  /**
   * Obtiene datos necesarios para la distribución de facturas
   */
  obtenerDatosDistribucion(): Observable<any> {
    const data = {
      action: 'get_distribution_data'
    };
    return this.post('facturas_sii_compra_distribuidas/', data);
  }

  /**
   * Obtiene fundos asociados a un cliente específico
   */
  obtenerFundosPorCliente(clienteId: number): Observable<any> {
    const data = {
      action: 'get_fundos_by_cliente',
      cliente_id: clienteId
    };
    return this.post('facturas_sii_compra_distribuidas/', data);
  }

  /**
   * Distribuye facturas seleccionadas con información completa
   */
  distribuirFacturas(distribucionData: any): Observable<any> {
    const data = {
      action: 'distribute_invoices',
      ...distribucionData
    };
    return this.post('facturas_sii_compra_distribuidas/', data);
  }

  /**
   * Obtiene facturas ya distribuidas con filtros opcionales
   */
  obtenerFacturasDistribuidas(filtros: any = {}): Observable<any> {
    const data = {
      action: 'get_distributed_invoices',
      ...filtros
    };
    return this.post('facturas_sii_compra_distribuidas/', data);
  }

  // ===============================================================
  // MÉTODOS PARA FACTURAS DE COMPRA AUTOMÁTICO
  // ===============================================================

  /**
   * Obtiene la configuración actual del proceso automático
   */
  obtenerConfiguracionAutomatica(): Observable<any> {
    const data = {
      action: 'get_automatic_configuration'
    };
    return this.post('facturas_compra_automatico/', data);
  }

  /**
   * Guarda o actualiza la configuración del proceso automático
   */
  guardarConfiguracionAutomatica(configuracion: any): Observable<any> {
    const data = {
      action: 'save_automatic_configuration',
      ...configuracion
    };
    return this.post('facturas_compra_automatico/', data);
  }

  /**
   * Obtiene facturas encontradas automáticamente y pendientes de distribución
   */
  obtenerFacturasAutomaticas(): Observable<any> {
    const data = {
      action: 'get_automatic_invoices'
    };
    return this.post('facturas_compra_automatico/', data);
  }

  /**
   * Obtiene el estado actual del proceso automático (Celery task status)
   */
  obtenerStatusProcesoAutomatico(): Observable<any> {
    const data = {
      action: 'get_automatic_process_status'
    };
    return this.post('facturas_compra_automatico/', data);
  }

  /**
   * Ejecuta el proceso automático de manera manual (para pruebas)
   */
  ejecutarProcesoAutomaticoManual(): Observable<any> {
    const data = {
      action: 'execute_automatic_process_manual'
    };
    return this.post('facturas_compra_automatico/', data);
  }

 

  /**
   * Elimina facturas automáticas que ya no se necesitan
   */
  eliminarFacturasAutomaticas(folios: string[]): Observable<any> {
    const data = {
      action: 'delete_automatic_invoices',
      folios: folios
    };
    return this.post('facturas_compra_automatico/', data);
  }

  /**
   * Activa o desactiva el proceso automático
   */
  toggleProcesoAutomatico(activo: boolean): Observable<any> {
    const data = {
      action: 'toggle_automatic_process',
      activo: activo
    };
    return this.post('facturas_compra_automatico/', data);
  }

  /**
   * Obtiene las empresas disponibles para configuración automática
   * (Reutiliza la lógica de login temporal)
   */
  obtenerEmpresasParaConfiguracion(rut: string, password: string): Observable<any> {
    const data = {
      action: 'get_companies_for_configuration',
      rut: rut,
      password: password
    };
    return this.post('facturas_compra_automatico/', data);
  }

  /**
   * Valida credenciales SII para configuración automática
   */
  validarCredencialesSII(rut: string, password: string): Observable<any> {
    const data = {
      action: 'validate_sii_credentials',
      rut: rut,
      password: password
    };
    return this.post('facturas_compra_automatico/', data);
  }

  /**
   * Obtiene historial de ejecuciones del proceso automático
   */
  obtenerHistorialEjecuciones(fechaDesde?: string, fechaHasta?: string): Observable<any> {
    const data: any = {
      action: 'get_execution_history'
    };
    
    if (fechaDesde) data.fecha_desde = fechaDesde;
    if (fechaHasta) data.fecha_hasta = fechaHasta;
    
    return this.post('facturas_compra_automatico/', data);
  }

  /**
   * Fuerza la reinicialización del proceso automático
   */
  reiniciarProcesoAutomatico(): Observable<any> {
    const data = {
      action: 'restart_automatic_process'
    };
    return this.post('facturas_compra_automatico/', data);
  }

  // ===============================================================
  // MÉTODOS PARA GESTIÓN DE CUENTAS CONTABLES
  // ===============================================================

  /**
   * Obtiene todas las cuentas contables del holding
   */
  obtenerCuentas(): Observable<any> {
    return this.get('cuentas/');
  }

  /**
   * Crea una nueva cuenta contable
   */
  crearCuenta(cuentaData: any): Observable<any> {
    return this.post('cuentas/', cuentaData);
  }

  /**
   * Actualiza una cuenta existente
   */
  actualizarCuenta(cuentaId: number, cuentaData: any): Observable<any> {
    return this.put(`cuentas/${cuentaId}/`, cuentaData);
  }

  /**
   * Elimina (desactiva) una cuenta
   */
  eliminarCuenta(cuentaId: number): Observable<any> {
    return this.delete(`cuentas/${cuentaId}/`, {});
  }

  // ===============================================================
  // MÉTODOS ADICIONALES PARA COMPATIBILIDAD
  // ===============================================================

  /**
   * Método genérico para mantener sesión activa
   */
  keepSessionAlive(sessionId: string): Observable<any> {
    const data = {
      action: 'keep_alive',
      session_id: sessionId
    };
    return this.post('facturas_sii_compra_distribuidas/', data);
  }

  /**
   * Obtiene información del usuario actual
   */
  getCurrentUser(): Observable<any> {
    return this.get('current_user/');
  }

  /**
   * Obtiene configuración del sistema
   */
  getSystemConfiguration(): Observable<any> {
    return this.get('system_config/');
  }

  /**
   * Método para subir archivos
   */
  uploadFile(endpoint: string, file: File, additionalData?: any): Observable<any> {
    const formData = new FormData();
    formData.append('file', file);
    
    if (additionalData) {
      Object.keys(additionalData).forEach(key => {
        formData.append(key, additionalData[key]);
      });
    }
    
    return this.postFormData(endpoint, formData);
  }

  /**
   * Exporta datos a Excel
   */
  exportToExcel(endpoint: string, data: any): Observable<Blob> {
    return this.postBlob(endpoint, data);
  }

  /**
   * Genera reporte PDF
   */
  generatePDFReport(endpoint: string, data: any): Observable<Blob> {
    return this.getPDF(endpoint);
  }

  /**
   * Busca elementos con paginación
   */
  searchWithPagination(endpoint: string, searchParams: any, page: number = 1, pageSize: number = 10): Observable<any> {
    const params = {
      ...searchParams,
      page: page,
      page_size: pageSize
    };
    return this.post(endpoint, params);
  }

  /**
   * Obtiene lista de opciones para selects
   */
  getSelectOptions(endpoint: string): Observable<any> {
    return this.get(`${endpoint}/options/`);
  }

  /**
   * Valida datos antes de enviar
   */
  validateData(endpoint: string, data: any): Observable<any> {
    return this.post(`${endpoint}/validate/`, data);
  }

  /**
   * Obtiene logs del sistema
   */
  getSystemLogs(filters?: any): Observable<any> {
    const endpoint = filters ? `system_logs/?${new URLSearchParams(filters).toString()}` : 'system_logs/';
    return this.get(endpoint);
  }

  /**
   * Envía notificación
   */
  sendNotification(data: any): Observable<any> {
    return this.post('notifications/', data);
  }

  /**
   * Obtiene estadísticas del dashboard
   */
  getDashboardStats(): Observable<any> {
    return this.get('dashboard_stats/');
  }

  // ===============================================================
  // MÉTODOS DE MANEJO DE FACTURAS
  // ===============================================================


    /**
   * Descarga el PDF de una factura específica
   */
  descargarPdfFactura(facturaId: string): Observable<any> {
    const data = {
      action: 'download_invoice_pdf',
      factura_id: facturaId
    };
    return this.post('facturas_compra_automatico/', data);
  }

  /**
   * Busca PDFs para facturas existentes que no los tienen
   */
  buscarPdfsFacturasExistentes(): Observable<any> {
    const data = {
      action: 'search_pdfs_for_existing_invoices'
    };
    return this.post('facturas_compra_automatico/', data);
  }

  /**
   * Obtiene estadísticas del estado de PDFs
   */
  obtenerEstadisticasPdf(): Observable<any> {
    const data = {
      action: 'get_pdf_search_status'
    };
    return this.post('facturas_compra_automatico/', data);
  }

  /**
   * Distribuye facturas automáticas incluyendo información de PDFs
   */
  distribuirFacturasAutomaticas(distribucionData: any): Observable<any> {
    const data = {
      action: 'distribute_automatic_invoices',
      ...distribucionData
    };
    return this.post('facturas_compra_automatico/', data);
  }

  /**
   * Obtiene facturas automáticas con información completa de PDFs
   */
  obtenerFacturasAutomaticasConPdf(): Observable<any> {
    const data = {
      action: 'get_automatic_invoices'
    };
    return this.post('facturas_compra_automatico/', data);
  }

  /**
   * Reintenta la descarga de PDF para facturas con errores
   */
  reintentarDescargaPdf(facturaIds: string[]): Observable<any> {
    const data = {
      action: 'retry_pdf_download',
      factura_ids: facturaIds
    };
    return this.post('facturas_compra_automatico/', data);
  }

  /**
   * Obtiene el progreso de descarga de PDFs en tiempo real
   */
  obtenerProgresoDescargaPdf(): Observable<any> {
    const data = {
      action: 'get_pdf_download_progress'
    };
    return this.post('facturas_compra_automatico/', data);
  }

  /**
   * Configura las preferencias de descarga de PDFs
   */
  configurarDescargaPdf(configuracion: {
    auto_download: boolean;
    max_retries: number;
    download_on_discovery: boolean;
  }): Observable<any> {
    const data = {
      action: 'configure_pdf_download',
      ...configuracion
    };
    return this.post('facturas_compra_automatico/', data);
  }

  /**
   * Elimina PDFs de facturas específicas para liberar espacio
   */
  eliminarPdfsFacturas(facturaIds: string[]): Observable<any> {
    const data = {
      action: 'delete_invoice_pdfs',
      factura_ids: facturaIds
    };
    return this.post('facturas_compra_automatico/', data);
  }

  /**
   * Valida la integridad de PDFs almacenados
   */
  validarIntegridadPdfs(): Observable<any> {
    const data = {
      action: 'validate_pdf_integrity'
    };
    return this.post('facturas_compra_automatico/', data);
  }

  /**
   * Obtiene métricas detalladas de PDFs
   */
  obtenerMetricasPdf(fechaDesde?: string, fechaHasta?: string): Observable<any> {
    const data = {
      action: 'get_pdf_metrics',
      fecha_desde: fechaDesde,
      fecha_hasta: fechaHasta
    };
    return this.post('facturas_compra_automatico/', data);
  }

  /**
   * Exporta facturas con PDFs a un archivo ZIP
   */
  exportarFacturasConPdf(facturaIds: string[]): Observable<any> {
    const data = {
      action: 'export_invoices_with_pdfs',
      factura_ids: facturaIds
    };
    return this.post('facturas_compra_automatico/', data);
  }

  /**
   * Busca PDFs en lote para múltiples facturas
   */
  buscarPdfsEnLote(facturaIds: string[]): Observable<any> {
    const data = {
      action: 'bulk_search_pdfs',
      factura_ids: facturaIds
    };
    return this.post('facturas_compra_automatico/', data);
  }

  /**
   * Obtiene el historial de descargas de PDFs
   */
  obtenerHistorialDescargasPdf(limit: number = 50): Observable<any> {
    const data = {
      action: 'get_pdf_download_history',
      limit: limit
    };
    return this.post('facturas_compra_automatico/', data);
  }

  /**
   * Programa la descarga automática de PDFs
   */
  programarDescargaAutomaticaPdf(configuracion: {
    enabled: boolean;
    hora_ejecucion: string;
    frecuencia: 'diaria' | 'semanal' | 'mensual';
  }): Observable<any> {
    const data = {
      action: 'schedule_automatic_pdf_download',
      ...configuracion
    };
    return this.post('facturas_compra_automatico/', data);
  }
}