// pago-transferencia.component.ts

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

// Interfaz modificada para manejar múltiples montos por trabajador
interface Produccion {
    id: number;
    trabajador_nombre: string;
    trabajador_rut: string;
    montos_a_pagar: number[];
    monto_total: number;
}

interface CSVBancoEstado {
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

@Component({
    selector: 'app-pago-transferencia',
    standalone: true,
    imports: [CommonModule, FormsModule],
    templateUrl: './pago-transferencia.component.html',
    styleUrl: './pago-transferencia.component.css'
})
export class PagoTransferenciaComponent implements OnInit {
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

        // Construcción de la URL con parámetros requeridos
        let url = `produccion-filtrada/?holding_id=${holdingId}&fecha_inicio=${this.fechaInicio}&fecha_fin=${this.fechaFin}`;
        
        // Añadir filtros opcionales si tienen valores válidos
        if (this.clienteSeleccionado?.id) {
            url += `&cliente_id=${this.clienteSeleccionado.id}`;
        }
        
        if (this.fundoSeleccionado) {
            url += `&fundo_id=${this.fundoSeleccionado}`;
        }
        
        if (this.cargoSeleccionado) {
            url += `&cargo_id=${this.cargoSeleccionado}`;
        }
        
        if (this.casaSeleccionada) {
            url += `&casa_id=${this.casaSeleccionada}`;
        }

        this.apiService.get(url).subscribe({
            next: (data) => {
                // Agrupar producciones por trabajador usando Map
                const produccionesAgrupadas = new Map<string, Produccion>();
                
                data.forEach((prod: any) => {
                    const key = prod.trabajador_rut;
                    
                    if (produccionesAgrupadas.has(key)) {
                        // Si el trabajador ya existe, actualizar sus montos
                        const existing = produccionesAgrupadas.get(key)!;
                        existing.montos_a_pagar.push(prod.monto_a_pagar);
                        existing.monto_total += prod.monto_a_pagar;
                    } else {
                        // Si es nuevo trabajador, crear nuevo registro
                        produccionesAgrupadas.set(key, {
                            id: prod.id,
                            trabajador_nombre: prod.trabajador_nombre,
                            trabajador_rut: prod.trabajador_rut,
                            montos_a_pagar: [prod.monto_a_pagar],
                            monto_total: prod.monto_a_pagar
                        });
                    }
                });

                // Convertir el Map a array y calcular total general
                this.produccionesPendientes = Array.from(produccionesAgrupadas.values());
                this.totalGeneral = this.produccionesPendientes.reduce(
                    (sum, prod) => sum + prod.monto_total, 
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
      if (!this.sociedadSeleccionada || !this.cuentaSeleccionada || !this.produccionesPendientes.length) {
          alert('No hay datos para procesar el pago');
          return;
      }

      const holdingId = this.getHoldingId();
      if (!holdingId) {
          alert('No se pudo obtener el ID del holding');
          return;
      }

      // Obtener IDs de todas las producciones a pagar
      const produccionesIds = this.produccionesPendientes.map(prod => prod.id);

      const datosPago = {
          holding_id: holdingId,
          sociedad_id: this.sociedadSeleccionada.id,
          cuenta_id: this.cuentaSeleccionada.id,
          producciones: produccionesIds
      };

      this.apiService.post('procesar-pago/', datosPago).subscribe({
          next: (response) => {
              alert('Pago procesado correctamente');
              this.buscarProducciones(); // Recargar la lista
          },
          error: (error) => {
              console.error('Error al procesar el pago:', error);
              alert('Error al procesar el pago');
          }
      });
  }


    generarCSVBanco() {
      if (!this.sociedadSeleccionada || !this.cuentaSeleccionada || !this.produccionesPendientes.length) {
          alert('Faltan datos necesarios para generar el CSV');
          return;
      }

      // Preparar los datos en el formato requerido
      const csvData: CSVBancoEstado[] = this.produccionesPendientes.map(prod => ({
          tipoCuentaOrigen: 'CTV', // Valor fijo según ejemplo
          cuentaOrigen: this.cuentaSeleccionada!.numero_cuenta,
          codigoBancoDestino: '12', // Código Banco Estado
          tipoCuentaDestino: 'CRUT', // CRUT para Cuenta RUT
          cuentaDestino: prod.trabajador_rut.replace(/\./g, '').replace(/-/g, ''),
          rutBeneficiario: prod.trabajador_rut,
          nombreBeneficiario: prod.trabajador_nombre,
          montoTransferencia: prod.monto_total,
          concepto: 'MILLACHE', // Según ejemplo
          mensajeBeneficiario: `Semana del ${this.fechaInicio} al ${this.fechaFin}`
      }));

      // Crear el contenido del CSV
      const headers = [
          'Tipo de Cuenta Origen',
          'Cuenta Origen',
          'Codigo Banco Destino',
          'Tipo de Cuenta Destino',
          'Cuenta Destino',
          'Rut Beneficiario',
          'Nombre Beneficiario',
          'Monto Transferencia',
          'Concepto',
          'Mensaje a Beneficiario'
      ];

      const csvContent = [
          headers.join(','),
          ...csvData.map(row => [
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
      const link = document.createElement('a');
      const fecha = new Date().toISOString().slice(0, 10);
      link.href = URL.createObjectURL(blob);
      link.download = `transferencias_${fecha}.csv`;
      link.style.visibility = 'hidden';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
  }
}