import { Component, OnInit, PLATFORM_ID, Inject } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ContratistaApiService } from '../../../../services/contratista-api.service';

interface Sociedad { id: number; nombre: string; cuentas_origen: any[]; }
interface Cuenta { id: number; banco_nombre: string; numero_cuenta: string; }
interface Cliente { id: number; nombre: string; campos_clientes: any[]; }
interface Fundo { id: number; nombre_campo: string; }
interface Cargo { id: number; nombre: string; }
interface Casa { id: number; nombre: string; }

interface Produccion {
    id: number;
    registro_ids: number[];
    trabajador_id: number;
    trabajador_nombre: string;
    trabajador_apellidos: string;
    trabajador_rut: string;
    trabajador_dni: string;
    montos_a_pagar: number[];
    monto_total: number;
    numero_cuenta: string;
    banco_rut: string;
    tipo_cuenta: string;
    pagado: boolean;
}

@Component({
    selector: 'app-pago-transferencia',
    standalone: true,
    imports: [CommonModule, FormsModule],
    templateUrl: './pago-transferencia.component.html',
    styleUrl: './pago-transferencia.component.css'
})
export class PagoTransferenciaComponent implements OnInit {
    sociedades: Sociedad[] = [];
    cuentas: Cuenta[] = [];
    clientes: Cliente[] = [];
    fundos: Fundo[] = [];
    cargos: Cargo[] = [];
    casas: Casa[] = [];

    produccionesPagadas: Produccion[] = [];
    produccionesNoPagadas: Produccion[] = [];

    sociedadSeleccionada: Sociedad | null = null;
    cuentaSeleccionada: Cuenta | null = null;

    clientesSeleccionados: number[] = [];
    fundosSeleccionados: number[] = [];
    cargosSeleccionados: number[] = [];
    casasSeleccionadas: number[] = [];

    dropdownAbierto: string | null = null;

    fechaInicio: string = '';
    fechaFin: string = '';

    totalPagado: number = 0;
    totalNoPagado: number = 0;
    totalGeneral: number = 0;

    nombreArchivoBase: string = '';
    busquedaRealizada: boolean = false;

    private isBrowser: boolean;

    constructor(
        private apiService: ContratistaApiService,
        @Inject(PLATFORM_ID) platformId: Object
    ) {
        this.isBrowser = isPlatformBrowser(platformId);
    }

    ngOnInit() {
        if (this.isBrowser) {
            this.cargarSociedades();
            this.cargarOpcionesFiltros();
            document.addEventListener('click', this.cerrarDropdownsExternos.bind(this));
        }
    }

    ngOnDestroy() {
        if (this.isBrowser) {
            document.removeEventListener('click', this.cerrarDropdownsExternos.bind(this));
        }
    }

    cerrarDropdownsExternos(event: MouseEvent) {
        const target = event.target as HTMLElement;
        if (!target.closest('.multi-select-container')) {
            this.dropdownAbierto = null;
        }
    }

    toggleDropdown(nombre: string, event: MouseEvent) {
        event.stopPropagation();
        this.dropdownAbierto = this.dropdownAbierto === nombre ? null : nombre;
    }

    private getHoldingId(): string | null {
        return this.isBrowser ? localStorage.getItem('holding_id') : null;
    }

    cargarSociedades() {
        const holdingId = this.getHoldingId();
        if (holdingId) {
            this.apiService.get(`api_sociedades_modify/${holdingId}`).subscribe(
                data => this.sociedades = data
            );
        }
    }

    cargarOpcionesFiltros() {
        const holdingId = this.getHoldingId();
        if (holdingId) {
            this.apiService.get(`opciones-filtros/${holdingId}`).subscribe(
                data => {
                    this.clientes = data.clientes;
                    this.cargos = data.cargos;
                    this.casas = data.casas;
                }
            );
        }
    }

    onSociedadChange(event: Event) {
        const selectElement = event.target as HTMLSelectElement;
        const sociedadId = selectElement.value;
        if (sociedadId) {
            this.sociedadSeleccionada = this.sociedades.find(s => s.id === Number(sociedadId)) || null;
            this.apiService.get(`api_cuentas_origen/${sociedadId}`).subscribe(
                data => this.cuentas = data
            );
        } else {
            this.sociedadSeleccionada = null;
            this.cuentaSeleccionada = null;
            this.cuentas = [];
        }
    }

    onCuentaChange(event: Event) {
        const selectElement = event.target as HTMLSelectElement;
        const cuentaId = selectElement.value;
        this.cuentaSeleccionada = cuentaId
            ? this.cuentas.find(c => c.id === Number(cuentaId)) || null
            : null;
    }

    // ---- Multi-select helpers ----

    toggleItem(lista: number[], id: number) {
        const idx = lista.indexOf(id);
        if (idx === -1) lista.push(id);
        else lista.splice(idx, 1);
    }

    isSelected(lista: number[], id: number): boolean {
        return lista.includes(id);
    }

    toggleTodos(lista: number[], fuente: any[], campo: string = 'id') {
        if (lista.length === fuente.length) {
            lista.splice(0, lista.length);
        } else {
            lista.splice(0, lista.length, ...fuente.map(i => i[campo]));
        }
    }

    todosMarcados(lista: number[], fuente: any[]): boolean {
        return fuente.length > 0 && lista.length === fuente.length;
    }

    algunoMarcado(lista: number[], fuente: any[]): boolean {
        return lista.length > 0 && lista.length < fuente.length;
    }

    getLabelMultiSelect(lista: number[], fuente: any[], campoNombre: string, placeholder: string): string {
        if (lista.length === 0) return placeholder;
        if (lista.length === fuente.length) return 'Todos';
        if (lista.length === 1) {
            const item = fuente.find(i => i.id === lista[0]);
            return item ? item[campoNombre] : placeholder;
        }
        return `${lista.length} seleccionados`;
    }

    onClienteToggle(id: number) {
        this.toggleItem(this.clientesSeleccionados, id);
        this.fundos = [];
        this.fundosSeleccionados = [];
        this.clientesSeleccionados.forEach(clienteId => {
            const cliente = this.clientes.find(c => c.id === clienteId);
            if (cliente) this.fundos.push(...cliente.campos_clientes);
        });
    }

    toggleTodosClientes() {
        this.toggleTodos(this.clientesSeleccionados, this.clientes);
        this.fundos = [];
        this.fundosSeleccionados = [];
        if (this.clientesSeleccionados.length > 0) {
            this.clientesSeleccionados.forEach(clienteId => {
                const cliente = this.clientes.find(c => c.id === clienteId);
                if (cliente) this.fundos.push(...cliente.campos_clientes);
            });
        }
    }

    // ---- Búsqueda ----

    buscarProducciones() {
        if (!this.fechaInicio || !this.fechaFin) {
            alert('Por favor seleccione un rango de fechas');
            return;
        }

        const holdingId = this.getHoldingId();
        if (!holdingId) {
            alert('No se pudo obtener el ID del holding');
            return;
        }

        let url = `produccion-filtrada-transferencia/?holding_id=${holdingId}&fecha_inicio=${this.fechaInicio}&fecha_fin=${this.fechaFin}`;

        if (this.clientesSeleccionados.length > 0 && this.clientesSeleccionados.length < this.clientes.length)
            url += `&cliente_ids=${this.clientesSeleccionados.join(',')}`;
        if (this.fundosSeleccionados.length > 0 && this.fundosSeleccionados.length < this.fundos.length)
            url += `&fundo_ids=${this.fundosSeleccionados.join(',')}`;
        if (this.cargosSeleccionados.length > 0 && this.cargosSeleccionados.length < this.cargos.length)
            url += `&cargo_ids=${this.cargosSeleccionados.join(',')}`;
        if (this.casasSeleccionadas.length > 0 && this.casasSeleccionadas.length < this.casas.length)
            url += `&casa_ids=${this.casasSeleccionadas.join(',')}`;

        this.apiService.get(url).subscribe({
            next: (data) => {
                const mapa = new Map<number, Produccion>();

                data.forEach((prod: any) => {
                    const key = prod.trabajador_id;
                    if (mapa.has(key)) {
                        const ex = mapa.get(key)!;
                        ex.registro_ids.push(prod.id);
                        ex.montos_a_pagar.push(prod.monto_a_pagar);
                        ex.monto_total += prod.monto_a_pagar;
                        if (prod.pagado) ex.pagado = true;
                    } else {
                        const nombreCompleto = `${prod.trabajador_nombre || ''} ${prod.trabajador_apellidos || ''}`.trim();
                        mapa.set(key, {
                            id: prod.id,
                            registro_ids: [prod.id],
                            trabajador_id: prod.trabajador_id,
                            trabajador_nombre: nombreCompleto,
                            trabajador_apellidos: prod.trabajador_apellidos,
                            trabajador_rut: prod.trabajador_rut || '-',
                            trabajador_dni: prod.trabajador_dni || '-',
                            montos_a_pagar: [prod.monto_a_pagar],
                            monto_total: prod.monto_a_pagar,
                            numero_cuenta: prod.numero_cuenta || '',
                            banco_rut: prod.banco_rut || '',
                            tipo_cuenta: prod.tipo_cuenta || 'CTD',
                            pagado: !!prod.pagado
                        });
                    }
                });

                const lista = Array.from(mapa.values());
                this.produccionesPagadas = lista.filter(p => p.pagado);
                this.produccionesNoPagadas = lista.filter(p => !p.pagado);

                this.totalPagado = this.produccionesPagadas.reduce((s, p) => s + p.monto_total, 0);
                this.totalNoPagado = this.produccionesNoPagadas.reduce((s, p) => s + p.monto_total, 0);
                this.totalGeneral = this.totalPagado + this.totalNoPagado;

                this.busquedaRealizada = true;
            },
            error: (error) => {
                console.error('Error al buscar producciones:', error);
                alert('Ocurrió un error al buscar las producciones');
            }
        });
    }

    hayResultados(): boolean {
        return this.produccionesPagadas.length > 0 || this.produccionesNoPagadas.length > 0;
    }

    // ---- Procesar pago ----

    procesarPago() {
        if (!this.sociedadSeleccionada || !this.cuentaSeleccionada || !this.produccionesNoPagadas.length) {
            alert('No hay datos para procesar el pago');
            return;
        }

        const holdingId = this.getHoldingId();
        if (!holdingId) {
            alert('No se pudo obtener el ID del holding');
            return;
        }

        const registrosIds: number[] = [];
        this.produccionesNoPagadas.forEach(p => registrosIds.push(...p.registro_ids));

        const datosPago = {
            holding_id: holdingId,
            sociedad_id: this.sociedadSeleccionada.id,
            cuenta_id: this.cuentaSeleccionada.id,
            producciones: registrosIds
        };

        this.apiService.post('procesar-pago/', datosPago).subscribe({
            next: () => {
                alert('Pago procesado correctamente');
                this.buscarProducciones();
            },
            error: (error) => {
                console.error('Error al procesar el pago:', error);
                alert('Error al procesar el pago');
            }
        });
    }

    // ---- TXT Banco (intacto) ----

    async generarTXTBanco(): Promise<void> {
        if (!this.sociedadSeleccionada || !this.cuentaSeleccionada || !this.produccionesNoPagadas.length) {
            alert('Faltan datos para generar el TXT');
            return;
        }
        if (!this.nombreArchivoBase.trim()) {
            alert('Ingrese un nombre base para los archivos');
            return;
        }

        const rutCliente = this.cuentaSeleccionada.numero_cuenta;

        const csvLines = this.produccionesNoPagadas.map(prod => [
            'TOB',
            rutCliente,
            this.cuentaSeleccionada!.numero_cuenta,
            prod.trabajador_rut.replace(/\./g, '').replace(/-/g, ''),
            prod.trabajador_nombre,
            prod.numero_cuenta,
            prod.banco_rut,
            Math.round(prod.monto_total),
            '',
            `SEMANA ${this.fechaInicio} AL ${this.fechaFin}`,
            '0',
            'PAGO',
            '',
            prod.tipo_cuenta
        ].join(';'));

        const blob = new Blob([csvLines.join('\n')], { type: 'text/csv;charset=utf-8;' });
        const file = new File([blob], 'transferencias.csv', { type: 'text/csv' });

        const formData = new FormData();
        formData.append('csv_file', file);
        formData.append('nombre_archivo', this.nombreArchivoBase.trim());
        formData.append('action', 'generar_txt_banco');

        try {
            const response = await this.apiService.postFormData('generar_txt_banco/', formData).toPromise();
            if (response.success) {
                response.archivos.forEach((archivo: any, index: number) => {
                    setTimeout(() => {
                        const b = new Blob([archivo.contenido], { type: 'text/plain;charset=utf-8' });
                        const link = document.createElement('a');
                        link.href = URL.createObjectURL(b);
                        link.download = archivo.nombre;
                        document.body.appendChild(link);
                        link.click();
                        document.body.removeChild(link);
                    }, index * 300);
                });
            } else {
                alert(response.message || 'Error al generar TXT');
            }
        } catch (error: any) {
            alert(error.error?.message || 'Error al generar TXT');
        }
    }

    // ---- PDF ----

    generarPlanillaPDF() {
        if (!this.fechaInicio || !this.fechaFin) {
            alert('Por favor seleccione un rango de fechas');
            return;
        }

        const holdingId = this.getHoldingId();
        if (!holdingId) {
            alert('No se pudo obtener el ID del holding');
            return;
        }

        let url = `generar-planilla-transferencia/?holding_id=${holdingId}&fecha_inicio=${this.fechaInicio}&fecha_fin=${this.fechaFin}`;

        if (this.clientesSeleccionados.length > 0 && this.clientesSeleccionados.length < this.clientes.length)
            url += `&cliente_ids=${this.clientesSeleccionados.join(',')}`;
        if (this.fundosSeleccionados.length > 0 && this.fundosSeleccionados.length < this.fundos.length)
            url += `&fundo_ids=${this.fundosSeleccionados.join(',')}`;
        if (this.cargosSeleccionados.length > 0 && this.cargosSeleccionados.length < this.cargos.length)
            url += `&cargo_ids=${this.cargosSeleccionados.join(',')}`;
        if (this.casasSeleccionadas.length > 0 && this.casasSeleccionadas.length < this.casas.length)
            url += `&casa_ids=${this.casasSeleccionadas.join(',')}`;

        this.apiService.getPDF(url).subscribe({
            next: (response: any) => {
                const blob = new Blob([response], { type: 'application/pdf' });
                const blobUrl = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                const fecha = new Date().toISOString().slice(0, 10);
                a.href = blobUrl;
                a.download = `planilla_transferencia_${fecha}.pdf`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(blobUrl);
                document.body.removeChild(a);
            },
            error: (error: any) => {
                console.error('Error al generar PDF:', error);
                alert('Error al generar la planilla PDF');
            }
        });
    }
}