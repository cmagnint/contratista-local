// pago-efectivo.component.ts

import { Component, OnInit, PLATFORM_ID, Inject } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ContratistaApiService } from '../../../../services/contratista-api.service';

// Interfaces para el tipado de datos
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

interface Cliente {
    id: number;
    nombre: string;
    campos_clientes: any[];
}

interface Fundo {
    id: number;
    nombre_campo: string;
}

interface Cargo {
    id: number;
    nombre: string;
}

interface Casa {
    id: number;
    nombre: string;
}

interface Produccion {
    id: number;
    trabajador_nombre: string;
    trabajador_rut: string;
    montos_a_pagar: number[];
    monto_total: number;
    monto_redondeado?: number;  // Monto ajustado al múltiplo
    saldo?: number;             // Saldo pendiente
}

interface MultiploPago {
    valor: number;
    etiqueta: string;
}

@Component({
    selector: 'app-pago-efectivo',
    standalone: true,
    imports: [CommonModule, FormsModule],
    templateUrl: './pago-efectivo.component.html',
    styleUrl: './pago-efectivo.component.css'
})
export class PagoEfectivoComponent implements OnInit {
    // Arrays para las opciones de los selectores
    sociedades: Sociedad[] = [];
    cuentas: Cuenta[] = [];
    clientes: Cliente[] = [];
    fundos: Fundo[] = [];
    cargos: Cargo[] = [];
    casas: Casa[] = [];
    produccionesPendientes: Produccion[] = [];
    
    // Variables para las selecciones del usuario
    sociedadSeleccionada: Sociedad | null = null;
    cuentaSeleccionada: Cuenta | null = null;
    clienteSeleccionado: Cliente | null = null;
    fundoSeleccionado: number | null = null;
    cargoSeleccionado: number | null = null;
    casaSeleccionada: number | null = null;
    
    // Variables para fechas y totales
    fechaInicio: string = '';
    fechaFin: string = '';
    totalGeneral: number = 0;

    // Opciones de múltiplos para el pago en efectivo
    multiplosDisponibles: MultiploPago[] = [
        { valor: 1000, etiqueta: '$1.000' },
        { valor: 2000, etiqueta: '$2.000' },
        { valor: 5000, etiqueta: '$5.000' },
        { valor: 10000, etiqueta: '$10.000' }
    ];
    multiploSeleccionado: number = 5000; // Valor por defecto

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
        }
    }

    private getHoldingId(): string | null {
        if (this.isBrowser) {
            return localStorage.getItem('holding_id');
        }
        return null;
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

    onClienteChange(event: Event) {
        const selectElement = event.target as HTMLSelectElement;
        const clienteId = selectElement.value;
        if (clienteId) {
            this.clienteSeleccionado = this.clientes.find(c => c.id === Number(clienteId)) || null;
            this.fundos = this.clienteSeleccionado ? this.clienteSeleccionado.campos_clientes : [];
        } else {
            this.fundos = [];
        }
        this.fundoSeleccionado = null;
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
        
        // Agregar los demás parámetros de filtro...
    
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
    
                // Calcular montos redondeados y saldos
                this.produccionesPendientes = Array.from(produccionesAgrupadas.values())
                    .map(prod => {
                        const monto_redondeado = Math.floor(prod.monto_total / this.multiploSeleccionado) * this.multiploSeleccionado;
                        const saldo = prod.monto_total - monto_redondeado;
                        return {
                            ...prod,
                            monto_redondeado,
                            saldo
                        };
                    });
    
                this.totalGeneral = this.produccionesPendientes.reduce(
                    (sum, prod) => sum + (prod.monto_redondeado || 0), 
                    0
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
            next: (response) => {
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
        
        // Agregar filtros opcionales si están seleccionados
        if (this.clienteSeleccionado?.id) url += `&cliente_id=${this.clienteSeleccionado.id}`;
        if (this.fundoSeleccionado) url += `&fundo_id=${this.fundoSeleccionado}`;
        if (this.cargoSeleccionado) url += `&cargo_id=${this.cargoSeleccionado}`;
        if (this.casaSeleccionada) url += `&casa_id=${this.casaSeleccionada}`;

        // Realizar la solicitud GET y manejar la descarga del PDF
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