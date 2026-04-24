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
    monto_redondeado?: number;
    saldo?: number;
    pagado: boolean;
}

interface MultiploPago { valor: number; etiqueta: string; }

@Component({
    selector: 'app-pago-efectivo',
    standalone: true,
    imports: [CommonModule, FormsModule],
    templateUrl: './pago-efectivo.component.html',
    styleUrl: './pago-efectivo.component.css'
})
export class PagoEfectivoComponent implements OnInit {
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

    multiplosDisponibles: MultiploPago[] = [
        { valor: 1000, etiqueta: '$1.000' },
        { valor: 2000, etiqueta: '$2.000' },
        { valor: 5000, etiqueta: '$5.000' },
        { valor: 10000, etiqueta: '$10.000' }
    ];
    multiploSeleccionado: number = 5000;

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
        }
    }

    onCuentaChange(event: Event) {
        const selectElement = event.target as HTMLSelectElement;
        const cuentaId = selectElement.value;
        if (cuentaId) {
            this.cuentaSeleccionada = this.cuentas.find(c => c.id === Number(cuentaId)) || null;
        }
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
            if (cliente) {
                this.fundos.push(...cliente.campos_clientes);
            }
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

        let url = `produccion-filtrada-efectivo/?holding_id=${holdingId}&fecha_inicio=${this.fechaInicio}&fecha_fin=${this.fechaFin}`;

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
                            pagado: !!prod.pagado
                        });
                    }
                });

                const lista = Array.from(mapa.values()).map(prod => {
                    const monto_redondeado = Math.floor(prod.monto_total / this.multiploSeleccionado) * this.multiploSeleccionado;
                    const saldo = prod.monto_total - monto_redondeado;
                    return { ...prod, monto_redondeado, saldo };
                });

                this.produccionesPagadas = lista.filter(p => p.pagado);
                this.produccionesNoPagadas = lista.filter(p => !p.pagado);

                this.totalPagado = this.produccionesPagadas.reduce((s, p) => s + (p.monto_redondeado || 0), 0);
                this.totalNoPagado = this.produccionesNoPagadas.reduce((s, p) => s + (p.monto_redondeado || 0), 0);
                this.totalGeneral = this.totalPagado + this.totalNoPagado;
            },
            error: (error) => {
                console.error('Error al buscar producciones:', error);
                alert('Ocurrió un error al buscar las producciones');
            }
        });
    }

    // ---- Procesar pago ----

    procesarPago() {
        if (!this.sociedadSeleccionada || !this.cuentaSeleccionada ||
            !this.produccionesNoPagadas.length || !this.multiploSeleccionado) {
            alert('No hay datos suficientes para procesar el pago');
            return;
        }

        const holdingId = this.getHoldingId();
        if (!holdingId) {
            alert('No se pudo obtener el ID del holding');
            return;
        }

        const pagos = this.produccionesNoPagadas.map(prod => ({
            registro_ids: prod.registro_ids,
            monto_pagado: prod.monto_redondeado,
            saldo: prod.saldo
        }));

        const datosPago = {
            holding_id: holdingId,
            sociedad_id: this.sociedadSeleccionada.id,
            cuenta_id: this.cuentaSeleccionada.id,
            pagos: pagos,
            multiplo_pago: this.multiploSeleccionado
        };

        this.apiService.post('procesar-pago-efectivo/', datosPago).subscribe({
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

    // ---- PDF ----

    generarPlanillaPDF() {
        if (!this.fechaInicio || !this.fechaFin || !this.multiploSeleccionado) {
            alert('Por favor seleccione un rango de fechas y un múltiplo de pago');
            return;
        }

        const holdingId = this.getHoldingId();
        if (!holdingId) {
            alert('No se pudo obtener el ID del holding');
            return;
        }

        let url = `generar-planilla-efectivo/?holding_id=${holdingId}&fecha_inicio=${this.fechaInicio}&fecha_fin=${this.fechaFin}&multiplo=${this.multiploSeleccionado}`;

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
                a.download = `planilla_efectivo_${fecha}.pdf`;
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

    hayResultados(): boolean {
        return this.produccionesPagadas.length > 0 || this.produccionesNoPagadas.length > 0;
    }
}