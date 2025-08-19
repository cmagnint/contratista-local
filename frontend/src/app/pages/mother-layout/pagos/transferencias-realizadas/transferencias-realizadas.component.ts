// transferencias-realizadas.component.ts

import { Component, OnInit, PLATFORM_ID, Inject } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ContratistaApiService } from '../../../../services/contratista-api.service';

interface PagoRealizado {
    id: number;
    sociedad: {
        id: number;
        nombre: string;
    };
    cuenta_origen: {
        banco_nombre: string;
        numero_cuenta: string;
    };
    trabajador: {
        nombres: string;
        rut: string;
    };
    monto_pagado: number;
    fecha_pago: string;
    tipo_pago: string;
    multiplo?: number | undefined;
    saldo?: number | undefined;
}

@Component({
    selector: 'app-transferencias-realizadas',
    standalone: true,
    imports: [CommonModule, FormsModule],
    templateUrl: './transferencias-realizadas.component.html',
    styleUrl: './transferencias-realizadas.component.css'
})
export class TransferenciasRealizadasComponent implements OnInit {
    pagos: PagoRealizado[] = [];
    fechaInicio: string = '';
    fechaFin: string = '';
    totalPagos: number = 0;
    tipoPagoSeleccionado: string = 'todos';
    private isBrowser: boolean;

    constructor(
        private apiService: ContratistaApiService,
        @Inject(PLATFORM_ID) platformId: Object
    ) {
        this.isBrowser = isPlatformBrowser(platformId);
    }

    ngOnInit() {
        // Set default date range to current month
        const today = new Date();
        const firstDay = new Date(today.getFullYear(), today.getMonth(), 1);
        const lastDay = new Date(today.getFullYear(), today.getMonth() + 1, 0);
        
        this.fechaInicio = firstDay.toISOString().split('T')[0];
        this.fechaFin = lastDay.toISOString().split('T')[0];
    }

    private getHoldingId(): string | null {
        if (this.isBrowser) {
            return localStorage.getItem('holding_id');
        }
        return null;
    }

    getSaldoClass(saldo: number | undefined): { [key: string]: boolean } {
        if (saldo === undefined) return {};
        return {
            'saldo-positivo': saldo > 0,
            'saldo-negativo': saldo < 0
        };
    }

    formatSaldo(saldo: number | undefined): string {
        if (saldo === undefined) return '-';
        return new Intl.NumberFormat('es-CL', {
            style: 'currency',
            currency: 'CLP',
            signDisplay: 'always'
        }).format(saldo);
    }

    buscarPagos() {
        const holdingId = this.getHoldingId();
        if (!holdingId) {
            alert('No se pudo obtener el ID del holding');
            return;
        }

        const url = `pagos-realizados/?holding_id=${holdingId}&fecha_inicio=${this.fechaInicio}&fecha_fin=${this.fechaFin}&tipo_pago=${this.tipoPagoSeleccionado}`;
        
        this.apiService.get(url).subscribe({
            next: (data) => {
                this.pagos = data;
                this.totalPagos = this.pagos.reduce(
                    (sum, pago) => sum + pago.monto_pagado, 
                    0
                );
            },
            error: (error) => {
                console.error('Error al obtener pagos:', error);
                alert('Error al obtener los pagos');
            }
        });
    }

    formatDate(date: string): string {
        return new Date(date).toLocaleDateString('es-CL', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }
}