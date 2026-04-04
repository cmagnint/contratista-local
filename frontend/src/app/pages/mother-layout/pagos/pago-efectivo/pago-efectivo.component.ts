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
    trabajador_nombre: string;
    trabajador_rut: string;
    montos_a_pagar: number[];
    monto_total: number;
    monto_redondeado?: number;
    saldo?: number;
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
    produccionesPendientes: Produccion[] = [];

    sociedadSeleccionada: Sociedad | null = null;
    cuentaSeleccionada: Cuenta | null = null;

    // Selecciones múltiples
    clientesSeleccionados: number[] = [];
    fundosSeleccionados: number[] = [];
    cargosSeleccionados: number[] = [];
    casasSeleccionadas: number[] = [];

    // Control dropdowns abiertos
    dropdownAbierto: string | null = null;

    fechaInicio: string = '';
    fechaFin: string = '';
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

    // ---- Helpers selección múltiple ----

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
        // Reconstruir fundos disponibles
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
                const produccionesAgrupadas = new Map<string, Produccion>();

                data.forEach((prod: any) => {
                    const key = prod.trabajador_rut;
                    if (produccionesAgrupadas.has(key)) {
                        const existing = produccionesAgrupadas.get(key)!;
                        existing.montos_a_pagar.push(prod.monto_a_pagar);
                        existing.monto_total += prod.monto_a_pagar;
                    } else {
                        produccionesAgrupadas.set(key, {
                            id: prod.id,
                            trabajador_nombre: prod.trabajador_nombre,
                            trabajador_rut: prod.trabajador_rut,
                            montos_a_pagar: [prod.monto_a_pagar],
                            monto_total: prod.monto_a_pagar
                        });
                    }
                });

                this.produccionesPendientes = Array.from(produccionesAgrupadas.values())
                    .map(prod => {
                        const monto_redondeado = Math.floor(prod.monto_total / this.multiploSeleccionado) * this.multiploSeleccionado;
                        const saldo = prod.monto_total - monto_redondeado;
                        return { ...prod, monto_redondeado, saldo };
                    });

                this.totalGeneral = this.produccionesPendientes.reduce(
                    (sum, prod) => sum + (prod.monto_redondeado || 0), 0
                );
            },
            error: (error) => {
                console.error('Error al buscar producciones:', error);
                alert('Ocurrió un error al buscar las producciones');
            }
        });
    }

    procesarPago() {
        if (!this.sociedadSeleccionada || !this.cuentaSeleccionada ||
            !this.produccionesPendientes.length || !this.multiploSeleccionado) {
            alert('No hay datos suficientes para procesar el pago');
            return;
        }

        const holdingId = this.getHoldingId();
        if (!holdingId) {
            alert('No se pudo obtener el ID del holding');
            return;
        }

        const pagos = this.produccionesPendientes.map(prod => ({
            produccion_id: prod.id,
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
                this.multiploSeleccionado = 5000;
            },
            error: (error) => {
                console.error('Error al procesar el pago:', error);
                alert('Error al procesar el pago');
            }
        });
    }

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
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                const fecha = new Date().toISOString().slice(0, 10);
                a.href = url;
                a.download = `planilla_efectivo_${fecha}.pdf`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
            },
            error: (error: any) => {
                console.error('Error al generar PDF:', error);
                alert('Error al generar la planilla PDF');
            }
        });
    }
}