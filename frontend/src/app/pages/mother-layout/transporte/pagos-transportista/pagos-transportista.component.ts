import { Component, OnInit, PLATFORM_ID, Inject } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ContratistaApiService } from '../../../../services/contratista-api.service';

// Interfaces that define our data structures
interface Sociedad {
    id: number;
    nombre: string;
    cuentas_origen: any[];
}

interface Cuenta {
    id: number;
    banco_nombre: string;
    numero_cuenta: string;
}

interface EmpresaTransporte {
    id: number;
    nombre: string;
    rut: string;
    direccion: string;
    selected?: boolean;
}

interface CSVBancoRegistro {
    tipoCuentaOrigen: string;
    cuentaOrigen: string;
    codigoBancoDestino: string;
    tipoCuentaDestino: string;
    cuentaDestino: string;
    rutBeneficiario: string;
    nombreBeneficiario: string;
    montoTransferencia: number;
    concepto: string;
    mensajeBeneficiario: string;
}


// Comprehensive interface for transportista records
interface RegistroTransportista {
    id: number;
    transportista: {
        rut: string;
        id: number;
        nombre: string;
    };
    fecha: string;
    hora_llegada: string;
    hora_salida: string;
    pasajeros: number;
    monto_calculado: number;
    tipo_tramo: 'PASAJERO' | 'VIAJE';
    valor_pago: number;
    pagado: boolean;
    selected?: boolean;
}

interface RegistroTransportista {
    fecha: string;
    transportista_nombre: string;
    transportista_rut: string;
    tipo_pago: 'PASAJERO' | 'VIAJE';
    valor_unidad: number;
    cantidad_personas: number;
    monto_calculado: number;
    tramo: {
        origen: string;
        destino: string;
    };
    selected?: boolean;
}

interface RegistroAgrupado {
    fecha: string;
    transportistas: {
id: number;
        nombre: string;
        rut: string;
        registros: RegistroTransportista[];
    }[];
}


@Component({
    selector: 'app-pagos-transportista',
    standalone: true,
    imports: [CommonModule, FormsModule],
    templateUrl: './pagos-transportista.component.html',
    styleUrl: './pagos-transportista.component.css'
})
export class PagosTransportistaComponent implements OnInit {
    // Data storage properties
    sociedades: Sociedad[] = [];
    cuentas: Cuenta[] = [];
    empresasTransporte: EmpresaTransporte[] = [];
    registrosTransportista: RegistroTransportista[] = [];
    registrosAgrupados: RegistroAgrupado[] = [];
    
    mostrarReconfirmacion: boolean = false;
    registrosSeleccionadosParaPago: number[] = [];
    pagoProcesandose: boolean = false;
    

    // Selection and state properties
    sociedadSeleccionada: Sociedad | null = null;
    cuentaSeleccionada: Cuenta | null = null;
    metodoPago: 'EFECTIVO' | 'TRANSFERENCIA' = 'TRANSFERENCIA';
    mostrarModalPago: boolean = false;

    mostrarModalConfirmacion: boolean = false;
    mensajeConfirmacion: string = '';
    tituloConfirmacion: string = '';
        
    // Date control properties
    fechaInicio: string = '';
    fechaFin: string = '';
    
    // Calculation properties
    totalGeneral: number = 0;

    constructor(
        private apiService: ContratistaApiService,
        @Inject(PLATFORM_ID) private platformId: Object
    ) {}

    ngOnInit(): void {
        if (isPlatformBrowser(this.platformId)) {
            this.inicializarComponente();
        }
    }

    private inicializarComponente(): void {
        this.inicializarFechas();
        this.cargarDatosIniciales();
    }

    private inicializarFechas(): void {
        const hoy = new Date();
        this.fechaFin = hoy.toISOString().split('T')[0];
        const primerDiaMes = new Date(hoy.getFullYear(), hoy.getMonth(), 1);
        this.fechaInicio = primerDiaMes.toISOString().split('T')[0];
    }

    private cargarDatosIniciales(): void {
        this.cargarSociedades();
        this.cargarEmpresasTransporte();
    }

    private getHoldingId(): string | null {
        return isPlatformBrowser(this.platformId) ? localStorage.getItem('holding_id') : null;
    }

    cargarEmpresasTransporte(): void {
        const holdingId = this.getHoldingId();
        if (!holdingId) return;

        this.apiService.get(`api_empresa_transportes/?holding=${holdingId}`).subscribe({
            next: (data) => {
                this.empresasTransporte = data.map((empresa: EmpresaTransporte) => ({
                    ...empresa,
                    selected: false
                }));
            },
            error: (error) => {
                console.error('Error al cargar empresas:', error);
                alert('Error al cargar empresas de transporte');
            }
        });
    }

    cargarSociedades(): void {
        const holdingId = this.getHoldingId();
        if (!holdingId) return;

        this.apiService.get(`api_sociedades_modify/${holdingId}`).subscribe({
            next: (data) => this.sociedades = data,
            error: (error) => {
                console.error('Error al cargar sociedades:', error);
                alert('Error al cargar sociedades');
            }
        });
    }

    onSociedadChange(event: Event): void {
        const sociedadId = (event.target as HTMLSelectElement).value;
        if (!sociedadId) return;

        this.sociedadSeleccionada = this.sociedades.find(s => s.id === Number(sociedadId)) || null;
        this.cargarCuentas(sociedadId);
    }

    private cargarCuentas(sociedadId: string): void {
        this.apiService.get(`api_cuentas_origen/${sociedadId}`).subscribe({
            next: (data) => this.cuentas = data,
            error: (error) => {
                console.error('Error al cargar cuentas:', error);
                alert('Error al cargar cuentas');
            }
        });
    }

    onCuentaChange(event: Event): void {
        const cuentaId = (event.target as HTMLSelectElement).value;
        if (cuentaId) {
            this.cuentaSeleccionada = this.cuentas.find(c => c.id === Number(cuentaId)) || null;
        }
    }

    buscarRegistros(): void {
        if (!this.validarParametrosBusqueda()) return;
    
        const params = this.construirParametrosBusqueda();
        
        this.apiService.get(`calculo-pago-transportista/?${params}`).subscribe({
            next: (data) => {
                console.log('Datos recibidos:', data);
                if (Array.isArray(data) && data.length > 0) {
                    this.procesarRegistros(data);
                } else {
                    this.limpiarRegistros();
                    alert('No se encontraron registros para el período seleccionado');
                }
            },
            error: (error) => {
                console.error('Error en búsqueda:', error);
                alert('Error al buscar los registros');
            }
        });
    }

    private validarParametrosBusqueda(): boolean {
        if (!this.fechaInicio || !this.fechaFin) {
            alert('Seleccione un rango de fechas');
            return false;
        }

        if (!this.empresasTransporte.some(e => e.selected)) {
            alert('Seleccione al menos una empresa');
            return false;
        }

        if (!this.getHoldingId()) {
            alert('No se pudo obtener el ID del holding');
            return false;
        }

        return true;
    }

    private construirParametrosBusqueda(): URLSearchParams {
        const empresasSeleccionadas = this.empresasTransporte
            .filter(e => e.selected)
            .map(e => e.id);

        return new URLSearchParams({
            holding: this.getHoldingId()!,
            fecha_inicio: this.fechaInicio,
            fecha_fin: this.fechaFin,
            empresas: empresasSeleccionadas.join(',')
        });
    }

    private procesarRegistros(data: any[]): void {
        this.registrosTransportista = data.map(registro => ({
            ...registro,
            selected: false
        }));
    
        this.agruparRegistros();
        this.calcularTotal();
    }

    private limpiarRegistros(): void {
        this.registrosTransportista = [];
        this.registrosAgrupados = [];
        this.totalGeneral = 0;
    }

    agruparRegistros(): void {
        try {
            const registrosPorFecha = new Map<string, Map<string, { registros: RegistroTransportista[], id: number }>>();
            
            this.registrosTransportista.forEach(registro => {
                if (!registro.fecha) {
                    console.warn('Registro inválido:', registro);
                    return;
                }
    
                const fecha = registro.fecha;
                if (!registrosPorFecha.has(fecha)) {
                    registrosPorFecha.set(fecha, new Map());
                }
                
                const transportistaRut = registro.transportista_rut;
                const registrosPorTransportista = registrosPorFecha.get(fecha)!;
                
                if (!registrosPorTransportista.has(transportistaRut)) {
                    registrosPorTransportista.set(transportistaRut, {
                        registros: [],
                        id: this.empresasTransporte.find(e => e.rut === transportistaRut)?.id || 0
                    });
                }
                
                registrosPorTransportista.get(transportistaRut)!.registros.push(registro);
            });
    
            this.registrosAgrupados = Array.from(registrosPorFecha.entries())
                .map(([fecha, transportistas]) => ({
                    fecha,
                    transportistas: Array.from(transportistas.entries())
                        .map(([rut, data]) => ({
                            id: data.id,
                            rut,
                            nombre: data.registros[0].transportista_nombre,
                            registros: data.registros.sort((a, b) => 
                                a.transportista_nombre.localeCompare(b.transportista_nombre)
                            )
                        }))
                }))
                .sort((a, b) => new Date(a.fecha).getTime() - new Date(b.fecha).getTime());
        } catch (error) {
            console.error('Error al agrupar registros:', error);
            this.registrosAgrupados = [];
        }
    }
    toggleEmpresaTransporte(empresa: EmpresaTransporte): void {
        empresa.selected = !empresa.selected;
        if (!empresa.selected) {
            this.registrosTransportista = this.registrosTransportista.filter(
                r => r.transportista.id !== empresa.id
            );
            this.agruparRegistros();
            this.calcularTotal();
        }
    }

    abrirModalPago(): void {
        if (!this.hayRegistrosSeleccionados()) {
            alert('Por favor seleccione al menos un registro para pagar');
            return;
        }
        if (!this.sociedadSeleccionada || !this.cuentaSeleccionada) {
            alert('Por favor seleccione una sociedad y cuenta de origen');
            return;
        }
        this.mostrarModalPago = true;
    }

    
    // Add new methods for document generation
    
private generarPlanillaEfectivo(datosPago: any): void {
    let url = `generar-planilla-efectivo/?holding_id=${datosPago.holding_id}&fecha_inicio=${datosPago.fecha_inicio}&fecha_fin=${datosPago.fecha_fin}&multiplo=5000`;
    
    this.apiService.getPDF(url).subscribe({
        next: (response: Blob) => {
            const blob = new Blob([response], { type: 'application/pdf' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            const fecha = new Date().toISOString().slice(0, 10);
            a.href = url;
            a.download = `planilla_efectivo_${fecha}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            this.mostrarConfirmacionPago('Pago en Efectivo', 
                'Se ha generado la planilla PDF. ¿Desea confirmar el pago?');
        },
        error: (error) => {
            console.error('Error al generar PDF:', error);
            alert('Error al generar la planilla PDF');
            this.mostrarModalConfirmacion = false;
        }
    });
}

    onMetodoPagoSeleccionado(metodo: 'EFECTIVO' | 'TRANSFERENCIA'): void {
        this.mostrarModalPago = false;
        this.metodoPago = metodo;
        
        // Guardar los IDs de registros seleccionados
        this.registrosSeleccionadosParaPago = this.registrosTransportista
            .filter(r => r.selected)
            .map(r => r.id);
    
        const registrosAPagar = this.registrosTransportista
            .filter(r => r.selected)
            .map(r => ({
                id: r.id,
                monto: r.monto_calculado
            }));
    
        const datosPago = {
            holding_id: this.getHoldingId(),
            sociedad_id: this.sociedadSeleccionada?.id,
            cuenta_id: this.cuentaSeleccionada?.id,
            registros: registrosAPagar,
            metodo_pago: this.metodoPago,
            fecha_inicio: this.fechaInicio,
            fecha_fin: this.fechaFin
        };
    
        if (metodo === 'EFECTIVO') {
            this.generarPlanillaEfectivo(datosPago);
        } else {
            this.generarArchivoBanco(datosPago);
            this.mostrarConfirmacionPago('Transferencia Bancaria', 
                'Se generará el archivo CSV para el banco. ¿Desea confirmar el pago?');
        }
    }

    private mostrarConfirmacionPago(titulo: string, mensaje: string): void {
        this.tituloConfirmacion = titulo;
        this.mensajeConfirmacion = mensaje;
        this.mostrarModalConfirmacion = true;
    }

    confirmarPago(): void {
        if (this.pagoProcesandose) return;
        
        this.pagoProcesandose = true;
        
        const datosPago = {
            registro_ids: this.registrosSeleccionadosParaPago,
            metodo_pago: this.metodoPago
        };

        this.apiService.post('confirmar-pago-transportista/', datosPago).subscribe({
            next: (response) => {
                alert('Pago confirmado exitosamente');
                this.mostrarReconfirmacion = false;
                this.buscarRegistros(); // Recargar los registros
            },
            error: (error) => {
                console.error('Error al confirmar el pago:', error);
                alert('Error al confirmar el pago');
            },
            complete: () => {
                this.pagoProcesandose = false;
            }
        });
    }

    cancelarPago(): void {
        this.mostrarReconfirmacion = false;
        this.registrosSeleccionadosParaPago = [];
        this.mostrarModalConfirmacion = false;  // Cerrar la ventana modal de confirmación
        this.tituloConfirmacion = '';          // Limpiar el título
        this.mensajeConfirmacion = '';         // Limpiar el mensaje
    }
    
    private generarArchivoBanco(datosPago: any): void {
        // Obtener solo los registros seleccionados y preparar los datos para el CSV
        const registrosSeleccionados = this.registrosTransportista
            .filter(r => r.selected)
            .map(registro => {
                // Limpiar RUT (quitar puntos y guión)
                const rutLimpio = registro.transportista.rut?.replace(/\./g, '').replace(/-/g, '') || '';
                
                return {
                    tipoCuentaOrigen: 'CTA CTE', // O el valor que corresponda
                    cuentaOrigen: this.cuentaSeleccionada?.numero_cuenta || '',
                    codigoBancoDestino: '012', // Código Banco Estado
                    tipoCuentaDestino: 'CUENTA RUT',
                    cuentaDestino: rutLimpio,
                    rutBeneficiario: registro.transportista.rut || '',
                    nombreBeneficiario: registro.transportista.nombre || '',
                    montoTransferencia: registro.monto_calculado,
                    concepto: 'PAGO FLETE',
                    mensajeBeneficiario: `Pago transporte del ${this.fechaInicio} al ${this.fechaFin}`
                } as CSVBancoRegistro;
            });
    
        // Definir los headers del CSV
        const headers = [
            'Tipo de Cuenta Origen',
            'Cuenta Origen',
            'Código Banco Destino',
            'Tipo de Cuenta Destino',
            'Cuenta Destino',
            'RUT Beneficiario',
            'Nombre Beneficiario',
            'Monto Transferencia',
            'Concepto',
            'Mensaje Beneficiario'
        ];
    
        // Generar el contenido del CSV
        const csvContent = [
            headers.join(','),
            ...registrosSeleccionados.map(row => [
                row.tipoCuentaOrigen,
                row.cuentaOrigen,
                row.codigoBancoDestino,
                row.tipoCuentaDestino,
                row.cuentaDestino,
                row.rutBeneficiario,
                row.nombreBeneficiario,
                row.montoTransferencia,
                row.concepto,
                row.mensajeBeneficiario
            ].join(','))
        ].join('\n');
    
        // Crear y descargar el archivo
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        const fecha = new Date().toISOString().slice(0, 10);
        a.href = url;
        a.download = `pago_transportistas_${this.fechaInicio}_${this.fechaFin}.csv`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        // Después de generar el CSV, procesamos el pago
        this.confirmarPago();
    }

    // Selection methods
    selectAllRegistros(): void {
        this.registrosTransportista.forEach(r => {
            if (r.hora_llegada && r.hora_salida) {
                r.selected = true;
            }
        });
        this.calcularTotal();
    }

    deselectAllRegistros(): void {
        this.registrosTransportista.forEach(r => r.selected = false);
        this.calcularTotal();
    }

    toggleSeleccionFecha(fecha: string, seleccionar: boolean): void {
        this.registrosTransportista
            .filter(r => r.fecha === fecha && r.hora_llegada && r.hora_salida)
            .forEach(r => r.selected = seleccionar);
        this.calcularTotal();
    }

    toggleSeleccionTransportista(fecha: string, transportistaId: number, seleccionar: boolean): void {
        this.registrosTransportista
            .filter(r => 
                r.fecha === fecha && 
                r.transportista.id === transportistaId && 
                r.hora_llegada && 
                r.hora_salida
            )
            .forEach(r => r.selected = seleccionar);
        this.calcularTotal();
    }

    // Calculation methods
    calcularTotal(): void {
        this.totalGeneral = this.registrosTransportista
            .filter(r => r.selected)
            .reduce((sum, r) => sum + (r.monto_calculado || 0), 0);
    }

    calcularTotalTransportistaDia(registros: RegistroTransportista[]): number {
        return registros
            .filter(r => r.selected)
            .reduce((sum, r) => sum + (r.monto_calculado || 0), 0);
    }

    // Utility methods
    hayEmpresasSeleccionadas(): boolean {
        return this.empresasTransporte.some(e => e.selected);
    }

    hayRegistrosSeleccionados(): boolean {
        return this.registrosTransportista.some(r => r.selected);
    }

    getColorEmpresa(empresaId: number): string {
        const colores = [
            '#4CAF50', '#2196F3', '#9C27B0', '#FF9800', '#F44336',
            '#009688', '#673AB7', '#3F51B5', '#FFC107', '#795548'
        ];
        return colores[empresaId % colores.length];
    }

    // Formatting methods
    formatearFecha(fecha: string): string {
        try {
            const date = new Date(fecha);
            if (isNaN(date.getTime())) {
                console.error('Fecha inválida:', fecha);
                return fecha;
            }
            return date.toLocaleDateString('es-CL', {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });
        } catch (error) {
            console.error('Error al formatear fecha:', error);
            return fecha;
        }
    }

    formatearHora(hora: string): string {
        if (!hora) return '';
        const fecha = new Date(hora);
        return fecha.toLocaleTimeString('es-CL', {
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    formatearMonto(monto: number | undefined): string {
        if (monto === undefined || monto === null) return '$0';
        return `$${monto.toLocaleString('es-CL')}`;
    }
}