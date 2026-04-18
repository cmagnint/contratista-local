import { Component, OnInit, PLATFORM_ID, Inject } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ContratistaApiService } from '../../../../services/contratista-api.service';

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
    numero_cuenta?: string;
    tipo_cuenta?: string;
    banco?: any;
    selected?: boolean;
}

interface RegistroTransportista {
    id: number;
    fecha: string;
    transportista_nombre: string;
    transportista_rut: string;
    tipo_pago: 'PASAJERO' | 'VIAJE';
    valor_unidad: number;
    cantidad_personas: number;
    monto_calculado: number;
    tramo: { origen: string; destino: string; };
    transportista: { id: number; nombre: string; rut: string; };
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

    sociedades: Sociedad[] = [];
    cuentas: Cuenta[] = [];
    empresasTransporte: EmpresaTransporte[] = [];
    registrosTransportista: RegistroTransportista[] = [];
    registrosAgrupados: RegistroAgrupado[] = [];

    mostrarReconfirmacion: boolean = false;
    registrosSeleccionadosParaPago: number[] = [];
    pagoProcesandose: boolean = false;

    sociedadSeleccionada: Sociedad | null = null;
    cuentaSeleccionada: Cuenta | null = null;
    metodoPago: 'EFECTIVO' | 'TRANSFERENCIA' = 'TRANSFERENCIA';
    mostrarModalPago: boolean = false;
    mostrarModalConfirmacion: boolean = false;
    mensajeConfirmacion: string = '';
    tituloConfirmacion: string = '';

    fechaInicio: string = '';
    fechaFin: string = '';
    totalGeneral: number = 0;

    constructor(
        private apiService: ContratistaApiService,
        @Inject(PLATFORM_ID) private platformId: Object
    ) {}

    ngOnInit(): void {
        if (isPlatformBrowser(this.platformId)) {
            this.inicializarFechas();
            this.cargarSociedades();
            this.cargarEmpresasTransporte();
        }
    }

    private inicializarFechas(): void {
        const hoy = new Date();
        this.fechaFin = hoy.toISOString().split('T')[0];
        const primerDiaMes = new Date(hoy.getFullYear(), hoy.getMonth(), 1);
        this.fechaInicio = primerDiaMes.toISOString().split('T')[0];
    }

    private getHoldingId(): string | null {
        return isPlatformBrowser(this.platformId) ? localStorage.getItem('holding_id') : null;
    }

    cargarEmpresasTransporte(): void {
        const holdingId = this.getHoldingId();
        if (!holdingId) return;
        this.apiService.get(`api_empresa_transportes/?holding=${holdingId}`).subscribe({
            next: (data) => {
                this.empresasTransporte = data.map((e: EmpresaTransporte) => ({ ...e, selected: false }));
            },
            error: () => alert('Error al cargar empresas de transporte')
        });
    }

    cargarSociedades(): void {
        const holdingId = this.getHoldingId();
        if (!holdingId) return;
        this.apiService.get(`api_sociedades_modify/${holdingId}`).subscribe({
            next: (data) => this.sociedades = data,
            error: () => alert('Error al cargar sociedades')
        });
    }

    onSociedadChange(event: Event): void {
        const id = (event.target as HTMLSelectElement).value;
        if (!id) return;
        this.sociedadSeleccionada = this.sociedades.find(s => s.id === Number(id)) || null;
        this.apiService.get(`api_cuentas_origen/${id}`).subscribe({
            next: (data) => this.cuentas = data,
            error: () => alert('Error al cargar cuentas')
        });
    }

    onCuentaChange(event: Event): void {
        const id = (event.target as HTMLSelectElement).value;
        if (id) this.cuentaSeleccionada = this.cuentas.find(c => c.id === Number(id)) || null;
    }

    buscarRegistros(): void {
        if (!this.fechaInicio || !this.fechaFin) { alert('Seleccione un rango de fechas'); return; }
        if (!this.empresasTransporte.some(e => e.selected)) { alert('Seleccione al menos una empresa'); return; }
        if (!this.getHoldingId()) { alert('No se pudo obtener el ID del holding'); return; }

        const empresasIds = this.empresasTransporte.filter(e => e.selected).map(e => e.id);
        const params = new URLSearchParams({
            holding: this.getHoldingId()!,
            fecha_inicio: this.fechaInicio,
            fecha_fin: this.fechaFin,
            empresas: empresasIds.join(',')
        });

        this.apiService.get(`calculo-pago-transportista/?${params}`).subscribe({
            next: (data) => {
                if (Array.isArray(data) && data.length > 0) {
                    this.registrosTransportista = data.map(r => ({ ...r, selected: false }));
                    this.agruparRegistros();
                    this.calcularTotal();
                } else {
                    this.registrosTransportista = [];
                    this.registrosAgrupados = [];
                    this.totalGeneral = 0;
                    alert('No se encontraron registros para el período seleccionado');
                }
            },
            error: () => alert('Error al buscar los registros')
        });
    }

    agruparRegistros(): void {
        try {
            const porFecha = new Map<string, Map<string, { id: number; registros: RegistroTransportista[] }>>();
            this.registrosTransportista.forEach(r => {
                if (!r.fecha) return;
                if (!porFecha.has(r.fecha)) porFecha.set(r.fecha, new Map());
                const rut = r.transportista_rut;
                const porTransportista = porFecha.get(r.fecha)!;
                if (!porTransportista.has(rut)) {
                    const empresa = this.empresasTransporte.find(e => e.rut === rut);
                    porTransportista.set(rut, { id: empresa?.id || 0, registros: [] });
                }
                porTransportista.get(rut)!.registros.push(r);
            });

            this.registrosAgrupados = Array.from(porFecha.entries())
                .map(([fecha, transportistas]) => ({
                    fecha,
                    transportistas: Array.from(transportistas.entries()).map(([rut, data]) => ({
                        id: data.id,
                        rut,
                        nombre: data.registros[0].transportista_nombre,
                        registros: data.registros
                    }))
                }))
                .sort((a, b) => new Date(a.fecha).getTime() - new Date(b.fecha).getTime());
        } catch {
            this.registrosAgrupados = [];
        }
    }

    toggleEmpresaTransporte(empresa: EmpresaTransporte): void {
        empresa.selected = !empresa.selected;
        if (!empresa.selected) {
            this.registrosTransportista = this.registrosTransportista.filter(
                r => r.transportista_nombre !== empresa.nombre
            );
            this.agruparRegistros();
            this.calcularTotal();
        }
    }

    // ── Selección ──

    selectAllRegistros(): void {
        this.registrosTransportista.forEach(r => r.selected = true);
        this.calcularTotal();
    }

    deselectAllRegistros(): void {
        this.registrosTransportista.forEach(r => r.selected = false);
        this.calcularTotal();
    }

    toggleSeleccionFecha(fecha: string, seleccionar: boolean): void {
        this.registrosTransportista
            .filter(r => r.fecha === fecha)
            .forEach(r => r.selected = seleccionar);
        this.calcularTotal();
    }

    toggleSeleccionTransportista(fecha: string, transportistaId: number, seleccionar: boolean): void {
        this.registrosTransportista
            .filter(r => r.fecha === fecha && r.transportista?.id === transportistaId)
            .forEach(r => r.selected = seleccionar);
        this.calcularTotal();
    }

    // ── Cálculo ──

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

    // ── Pago ──

    abrirModalPago(): void {
        if (!this.registrosTransportista.some(r => r.selected)) {
            alert('Seleccione al menos un registro para pagar');
            return;
        }
        if (!this.sociedadSeleccionada || !this.cuentaSeleccionada) {
            alert('Seleccione una sociedad y cuenta de origen');
            return;
        }
        this.mostrarModalPago = true;
    }

    onMetodoPagoSeleccionado(metodo: 'EFECTIVO' | 'TRANSFERENCIA'): void {
        this.mostrarModalPago = false;
        this.metodoPago = metodo;
        this.registrosSeleccionadosParaPago = this.registrosTransportista
            .filter(r => r.selected)
            .map(r => r.id);

        if (metodo === 'EFECTIVO') {
            this.generarPlanillaEfectivo();
        } else {
            this.generarTxtBanco();
        }
    }

    private generarPlanillaEfectivo(): void {
        const url = `generar-planilla-efectivo/?holding_id=${this.getHoldingId()}&fecha_inicio=${this.fechaInicio}&fecha_fin=${this.fechaFin}&multiplo=5000`;
        this.apiService.getPDF(url).subscribe({
            next: (response: Blob) => {
                const blob = new Blob([response], { type: 'application/pdf' });
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `planilla_efectivo_${new Date().toISOString().slice(0, 10)}.pdf`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                this.mostrarConfirmacionPago('Pago en Efectivo', '¿Confirmar el pago?');
            },
            error: () => alert('Error al generar la planilla PDF')
        });
    }

    private generarTxtBanco(): void {
        const seleccionados = this.registrosTransportista.filter(r => r.selected);

        // Agrupar por transportista y sumar montos del período
        const porTransportista = new Map<string, { registro: RegistroTransportista; monto: number }>();
        seleccionados.forEach(r => {
            const rut = r.transportista_rut;
            if (!porTransportista.has(rut)) {
                porTransportista.set(rut, { registro: r, monto: 0 });
            }
            porTransportista.get(rut)!.monto += r.monto_calculado;
        });

        // Construir CSV con el formato esperado por GenerarTxtBancoAPIView (14 columnas, separador ;)
        const filas: string[] = [];
        porTransportista.forEach(({ registro, monto }, rut) => {
            const empresa = this.empresasTransporte.find(e => e.rut === rut);
            const rutLimpio = rut.replace(/\./g, '').replace(/-/g, '');
            const cuentaCargo = this.cuentaSeleccionada?.numero_cuenta || '';
            const cuentaBenef = empresa?.numero_cuenta || rutLimpio;
            const rutBancoBenef = empresa?.banco?.codigo_sbif
                ? String(empresa.banco.codigo_sbif).padStart(9, '0')
                : '970060006';
            const tipoCuenta = empresa?.tipo_cuenta || 'CTD';
            const montoEntero = Math.round(monto);
            const periodo = this.fechaInicio.slice(0, 7).replace('-', '');
            const motivo = `PAGO FLETE ${periodo}`;
            const nombre = registro.transportista_nombre.slice(0, 30);

            // Columnas: tipo_op;rut_cliente;cuenta_cargo;rut_benef;nombre;cuenta_benef;rut_banco_benef;monto;;motivo;notif_email;asunto;email;tipo_cuenta
            filas.push([
                'TOB',
                '',          // rut_cliente — la sociedad no siempre está disponible desde la cuenta
                cuentaCargo,
                rutLimpio,
                nombre,
                cuentaBenef,
                rutBancoBenef,
                montoEntero,
                '',          // abono inmediato vacío
                motivo,
                '0',
                'Pago transporte',
                '',
                tipoCuenta
            ].join(';'));
        });

        if (filas.length === 0) {
            alert('No hay registros para generar el archivo');
            return;
        }

        const csvContenido = filas.join('\n');
        const csvFile = new File(
            [new Blob([csvContenido], { type: 'text/plain;charset=utf-8' })],
            'transportistas.csv',
            { type: 'text/plain' }
        );

        const nombreBase = `pago_transporte_${this.fechaInicio}_${this.fechaFin}`;
        const formData = new FormData();
        formData.append('csv_file', csvFile);
        formData.append('nombre_archivo', nombreBase);
        formData.append('action', 'generar_txt_banco');

        this.apiService.postFormData('generar_txt_banco/', formData).subscribe({
            next: (response: any) => {
                if (response.success) {
                    response.archivos.forEach((archivo: any, index: number) => {
                        setTimeout(() => {
                            const blob = new Blob([archivo.contenido], { type: 'text/plain;charset=utf-8' });
                            const url = window.URL.createObjectURL(blob);
                            const a = document.createElement('a');
                            a.href = url;
                            a.download = archivo.nombre;
                            document.body.appendChild(a);
                            a.click();
                            window.URL.revokeObjectURL(url);
                            document.body.removeChild(a);
                        }, index * 400);
                    });
                    this.mostrarConfirmacionPago(
                        'Transferencia Bancaria',
                        `Se generó(n) ${response.total_archivos} archivo(s) TXT con ${response.total_registros} transferencia(s). ¿Confirmar el pago?`
                    );
                } else {
                    alert(response.message || 'Error al generar el archivo TXT');
                }
            },
            error: () => alert('Error al comunicarse con el servidor para generar el TXT')
        });
    }

    private mostrarConfirmacionPago(titulo: string, mensaje: string): void {
        this.tituloConfirmacion = titulo;
        this.mensajeConfirmacion = mensaje;
        this.mostrarModalConfirmacion = true;
    }

    confirmarPago(): void {
        if (this.pagoProcesandose) return;
        this.pagoProcesandose = true;
        this.apiService.post('confirmar-pago-transportista/', {
            registro_ids: this.registrosSeleccionadosParaPago,
            metodo_pago: this.metodoPago
        }).subscribe({
            next: () => {
                this.pagoProcesandose = false;
                this.mostrarModalConfirmacion = false;
                this.mostrarReconfirmacion = false;
                alert('Pago confirmado exitosamente');
                this.buscarRegistros();
            },
            error: () => {
                this.pagoProcesandose = false;
                alert('Error al confirmar el pago');
            }
        });
    }

    cancelarPago(): void {
        this.mostrarReconfirmacion = false;
        this.mostrarModalConfirmacion = false;
        this.registrosSeleccionadosParaPago = [];
        this.tituloConfirmacion = '';
        this.mensajeConfirmacion = '';
    }

    // ── Utilidades ──

    hayEmpresasSeleccionadas(): boolean {
        return this.empresasTransporte.some(e => e.selected);
    }

    hayRegistrosSeleccionados(): boolean {
        return this.registrosTransportista.some(r => r.selected);
    }

    getColorEmpresa(empresaId: number): string {
        const colores = ['#14b35c', '#2196F3', '#9C27B0', '#FF9800', '#F44336',
                         '#009688', '#673AB7', '#3F51B5', '#FFC107', '#795548'];
        return colores[empresaId % colores.length];
    }

    formatearFecha(fecha: string): string {
        try {
            return new Date(fecha + 'T12:00:00').toLocaleDateString('es-CL', {
                weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
            });
        } catch {
            return fecha;
        }
    }

    formatearMonto(monto: number | undefined): string {
        if (monto === undefined || monto === null) return '$0';
        return `$${monto.toLocaleString('es-CL')}`;
    }
}