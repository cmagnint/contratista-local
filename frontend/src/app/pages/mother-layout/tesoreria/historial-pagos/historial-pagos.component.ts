import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ContratistaApiService } from '../../../../services/contratista-api.service';
interface HistorialItem {
  id: number;
  fecha: string;
  descripcion: string;
  monto: number;
  numero_operacion?: string;
  factura_numero?: string;
  factura_rut?: string;
  factura_razon_social?: string;
  estado: 'COMPLETADO' | 'PENDIENTE';
}

@Component({
  selector: 'app-historial-pagos',
  standalone: true,
  imports: [
    CommonModule,
  ],
  templateUrl: './historial-pagos.component.html',
  styleUrl: './historial-pagos.component.css'
})
export class HistorialPagosComponent implements OnInit, OnDestroy {
  
  // Estados de navegación
  tipoSeleccionado: 'ingresos' | 'egresos' | null = null;
  estadoSeleccionado: 'completados' | 'pendientes' | null = null;
  
  // Datos
  historialData: HistorialItem[] = [];
  cargando = false;
  error: string | null = null;
  descargandoCsv = false;

  constructor(private contratistaApi: ContratistaApiService) {}

  ngOnInit() {
    // Verificar si hay datos en sessionStorage para mantener estado (opcional)
    this.recuperarEstadoSesion();

  }

  /**
   * Recupera el estado previo de la sesión si existe
   * Útil si el usuario navega y vuelve al componente
   */
  private recuperarEstadoSesion() {
    try {
      const estadoGuardado = sessionStorage.getItem('historial_estado');
      if (estadoGuardado) {
        const estado = JSON.parse(estadoGuardado);
        // Solo recuperar si es reciente (menos de 1 hora)
        const tiempoLimite = 60 * 60 * 1000; // 1 hora en ms
        if (Date.now() - estado.timestamp < tiempoLimite) {
          this.tipoSeleccionado = estado.tipo;
          this.estadoSeleccionado = estado.estado;
          // Auto-cargar si ambos están seleccionados
          if (this.tipoSeleccionado && this.estadoSeleccionado) {
            this.cargarHistorial();
          }
        } else {
          // Limpiar estado expirado
          sessionStorage.removeItem('historial_estado');
        }
      }
    } catch (error) {
      console.warn('Error recuperando estado de sesión:', error);
    }
  }

  /**
   * Guarda el estado actual en sessionStorage
   */
  private guardarEstadoSesion() {
    if (this.tipoSeleccionado || this.estadoSeleccionado) {
      const estado = {
        tipo: this.tipoSeleccionado,
        estado: this.estadoSeleccionado,
        timestamp: Date.now()
      };
      sessionStorage.setItem('historial_estado', JSON.stringify(estado));
    }
  }

  seleccionarTipo(tipo: 'ingresos' | 'egresos') {
    this.tipoSeleccionado = tipo;
    this.estadoSeleccionado = null;
    this.historialData = [];
    this.error = null;
    this.guardarEstadoSesion();
  }

  seleccionarEstado(estado: 'completados' | 'pendientes') {
    this.estadoSeleccionado = estado;
    this.guardarEstadoSesion();
    this.cargarHistorial();
  }

  cargarHistorial() {
    if (!this.tipoSeleccionado || !this.estadoSeleccionado) return;

    this.cargando = true;
    this.error = null;

    const endpoint = `historial/${this.tipoSeleccionado}/${this.estadoSeleccionado}/`;
    
    this.contratistaApi.get(endpoint).subscribe({
      next: (data) => {
        this.historialData = data;
        this.cargando = false;
      },
      error: (err) => {
        console.error('Error cargando historial:', err);
        this.error = 'Error al cargar el historial. Por favor, intente nuevamente.';
        this.cargando = false;
      }
    });
  }

  volver() {
    if (this.estadoSeleccionado) {
      this.estadoSeleccionado = null;
      this.historialData = [];
    } else if (this.tipoSeleccionado) {
      this.tipoSeleccionado = null;
      // Limpiar sessionStorage cuando vuelve al inicio
      sessionStorage.removeItem('historial_estado');
    }
    this.error = null;
    this.guardarEstadoSesion();
  }

  formatearMonto(monto: number): string {
    return new Intl.NumberFormat('es-CL', {
      style: 'currency',
      currency: 'CLP',
      minimumFractionDigits: 0
    }).format(monto);
  }

  formatearFecha(fecha: string): string {
    return new Date(fecha).toLocaleDateString('es-CL', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
    });
  }

  getIconoTipo(): string {
    if (this.tipoSeleccionado === 'ingresos') {
      return 'fas fa-arrow-down text-success';
    } else if (this.tipoSeleccionado === 'egresos') {
      return 'fas fa-arrow-up text-danger';
    }
    return '';
  }

  getIconoEstado(estado: string): string {
    return estado === 'COMPLETADO' ? 'fas fa-check-circle text-success' : 'fas fa-clock text-warning';
  }

  getTotalMonto(): number {
    return this.historialData.reduce((sum, item) => sum + item.monto, 0);
  }

  trackByFn(index: number, item: HistorialItem): number {
    return item.id;
  }

  descargarCsv() {
    if (!this.tipoSeleccionado || !this.estadoSeleccionado) return;

    this.descargandoCsv = true;
    this.error = null;

    const endpoint = `historial/${this.tipoSeleccionado}/${this.estadoSeleccionado}/csv/`;
    
    this.contratistaApi.getBlob(endpoint).subscribe({
      next: (blob) => {
        this.descargarArchivo(blob, this.generarNombreArchivo());
        this.descargandoCsv = false;
      },
      error: (err) => {
        console.error('Error descargando CSV:', err);
        this.error = 'Error al descargar el archivo CSV. Por favor, intente nuevamente.';
        this.descargandoCsv = false;
      }
    });
  }

  private descargarArchivo(blob: Blob, nombreArchivo: string) {
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = nombreArchivo;
    link.click();
    window.URL.revokeObjectURL(url);
  }

  private generarNombreArchivo(): string {
    const fecha = new Date().toISOString().split('T')[0]; // YYYY-MM-DD
    const tipo = this.tipoSeleccionado;
    const estado = this.estadoSeleccionado;
    return `historial_${tipo}_${estado}_${fecha}.csv`;
  }

  ngOnDestroy() {
    // Opcional: limpiar estado al salir del componente
    // sessionStorage.removeItem('historial_estado');
  }
}