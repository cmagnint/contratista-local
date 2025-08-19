import { Component, OnInit, Inject, PLATFORM_ID } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule, AbstractControl } from '@angular/forms';
import { ContratistaApiService } from '../../../../services/contratista-api.service';
import { forkJoin } from 'rxjs';

@Component({
  selector: 'app-proformas-transportista',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './proformas-transportista.component.html',
  styleUrls: ['./proformas-transportista.component.css']
})
export class ProformasTransportistaComponent implements OnInit {
  // Form management
  calculoForm!: FormGroup;
  filtrosForm!: FormGroup;
  facturaForm!: FormGroup;

  // Data storage
  sociedades: any[] = [];
  transportistas: any[] = [];
  selectedTransportistas: number[] = [];
  proformas: any[] = [];

  // State management
  public holding: string = '';
  calculando = false;
  cargandoProformas = false;
  selectedProformas: number[] = [];
  showInvoiceModal = false;
  processingFactura = false;
  selectedProformaId: number | null = null;
  showFacturaDetalles = false;
  facturaSeleccionada: any = null;

  constructor(
    private fb: FormBuilder,
    private api: ContratistaApiService,
    @Inject(PLATFORM_ID) private platformId: object,
  ) {
    this.initForm();
    this.initFiltrosForm();
    this.initFacturaForm();
  }

  ngOnInit(): void {
    if(isPlatformBrowser(this.platformId)) {
      this.holding = localStorage.getItem('holding_id') || '';
      this.loadSociedades();
      this.loadTransportistas();
      this.cargarProformas();
    }
  }

  private initForm(): void {
    this.calculoForm = this.fb.group({
      sociedad: ['', Validators.required],
      fecha_emision: ['', Validators.required],
      fecha_vencimiento: ['', Validators.required],
      fecha_inicio_periodo: ['', Validators.required],
      fecha_fin_periodo: ['', Validators.required],
      transportistas: [[], [Validators.required, Validators.minLength(1)]]
    });

    this.calculoForm.patchValue({
      fecha_emision: new Date().toISOString().split('T')[0]
    });
  }

  private initFiltrosForm(): void {
    this.filtrosForm = this.fb.group({
      fecha_inicio: [''],
      fecha_fin: [''],
      estado: [''],
      transportista: ['']
    });
  }

   // Custom validator function for RUT
   private initFacturaForm(): void {
    this.facturaForm = this.fb.group({
      factura_fecha: ['', Validators.required],
      factura_numero: ['', Validators.required],
      factura_rut: ['', [Validators.required, this.rutValidator.bind(this)]],
      factura_monto: ['', [Validators.required, Validators.min(0)]]
    });
  }

  private rutValidator(control: AbstractControl) {
    const rut = control.value;
    if (!rut) return null;
    return this.validateRut(rut) ? null : { invalidRut: true };
  }


  private loadSociedades(): void {
    this.api.get(`api_sociedad/?holding=${this.holding}`)
      .subscribe({
        next: (response) => {
          this.sociedades = response;
        },
        error: (error) => {
          console.error('Error cargando sociedades:', error);
          this.manejarError(error);
        }
      });
  }

  private loadTransportistas(): void {
    this.api.get(`api_empresa_transportes/?holding=${this.holding}`)
      .subscribe({
        next: (response) => {
          this.transportistas = response;
        },
        error: (error) => {
          console.error('Error cargando transportistas:', error);
          this.manejarError(error);
        }
      });
  }

  // Métodos para la selección de transportistas en el formulario
  toggleEmpresaTransporte(empresa: any): void {
    const index = this.selectedTransportistas.indexOf(empresa.id);
    if (index === -1) {
      this.selectedTransportistas.push(empresa.id);
    } else {
      this.selectedTransportistas.splice(index, 1);
    }
    this.calculoForm.get('transportistas')?.setValue(this.selectedTransportistas);
  }

  isTransportistaSelected(transportistaId: number): boolean {
    return this.selectedTransportistas.includes(transportistaId);
  }

  getColorEmpresa(empresaId: number): string {
    const colores = [
      '#4CAF50', '#2196F3', '#9C27B0', '#FF9800', '#F44336',
      '#009688', '#673AB7', '#3F51B5', '#FFC107', '#795548'
    ];
    return colores[empresaId % colores.length];
  }

  // Métodos para manejo de proformas existentes
  cargarProformas(): void {
    this.cargandoProformas = true;
    const filtros = this.filtrosForm.value;
    let endpoint = `generar-proformas/?holding=${this.holding}`;

    if (filtros.fecha_inicio) endpoint += `&fecha_inicio=${filtros.fecha_inicio}`;
    if (filtros.fecha_fin) endpoint += `&fecha_fin=${filtros.fecha_fin}`;
    if (filtros.estado) endpoint += `&estado=${filtros.estado}`;
    if (filtros.transportista) endpoint += `&transportista=${filtros.transportista}`;

    this.api.get(endpoint)
      .subscribe({
        next: (response) => {
          this.proformas = response.proformas;
          this.cargandoProformas = false;
        },
        error: (error) => {
          console.error('Error cargando proformas:', error);
          this.manejarError(error);
          this.cargandoProformas = false;
        }
      });
  }

  // Métodos para selección múltiple de proformas
  toggleProformaSelection(proforma: any) {
    const index = this.selectedProformas.indexOf(proforma.id);
    if (index === -1) {
      this.selectedProformas.push(proforma.id);
    } else {
      this.selectedProformas.splice(index, 1);
    }
  }

  isProformaSelected(proforma: any): boolean {
    return this.selectedProformas.includes(proforma.id);
  }

  toggleAllProformas() {
    if (this.areAllProformasSelected()) {
      this.selectedProformas = [];
    } else {
      this.selectedProformas = this.proformas
        .filter(p => p.estado === 'EMITIDO')
        .map(p => p.id);
    }
  }

  areAllProformasSelected(): boolean {
    const selectableProformas = this.proformas.filter(p => p.estado === 'EMITIDO');
    return selectableProformas.length > 0 && 
           selectableProformas.every(p => this.selectedProformas.includes(p.id));
  }

  hasSelectableProformas(): boolean {
    return this.proformas.some(p => p.estado === 'EMITIDO');
  }

  hasSelectedProformas(): boolean {
    return this.selectedProformas.length > 0;
  }

  // Métodos para facturación individual y múltiple
  facturarProforma(proformaId: number): void {
    this.selectedProformaId = proformaId;
    this.showInvoiceModal = true;
    this.facturaForm.reset();
    // Establecer la fecha actual como valor predeterminado
    this.facturaForm.patchValue({
      factura_fecha: new Date().toISOString().split('T')[0]
    });
  }

  closeModal(event?: MouseEvent): void {
    if (!event || event.target === event.currentTarget) {
      this.showInvoiceModal = false;
      this.selectedProformaId = null;
      this.facturaForm.reset();
    }
  }

  // Métodos para el formateo de inputs
  onNumeroFacturaInput(event: any): void {
    const input = event.target;
    let value = input.value.replace(/\D/g, ''); // Solo permite números
    input.value = value;
    this.facturaForm.patchValue({ factura_numero: value });
  }



  // Métodos para detalles de factura
  mostrarDetallesFactura(proforma: any): void {
    this.facturaSeleccionada = proforma;
    this.showFacturaDetalles = true;
  }

  closeDetallesFactura(): void {
    this.showFacturaDetalles = false;
    this.facturaSeleccionada = null;
  }

  submitFactura(): void {
    if (this.facturaForm.valid && this.selectedProformaId) {
      this.processingFactura = true;
      
      const facturaData = this.facturaForm.value;
      
      this.api.put(`generar-proformas/${this.selectedProformaId}/`, facturaData)
        .subscribe({
          next: () => {
            alert('Proforma marcada como FACTURADA exitosamente');
            this.closeModal();
            this.cargarProformas();
            this.processingFactura = false;
          },
          error: (error) => {
            console.error('Error actualizando proforma:', error);
            this.manejarError(error);
            this.processingFactura = false;
          }
        });
    }
  }

  facturarProformasSeleccionadas() {
    if (!this.hasSelectedProformas()) return;

    const message = `¿Está seguro de marcar ${this.selectedProformas.length} proforma(s) como FACTURADA(S)? Esta acción no se puede deshacer.`;
    
    if (confirm(message)) {
      const requests = this.selectedProformas.map(id => 
        this.api.put(`generar-proformas/${id}/`, {})
      );

      this.calculando = true;
      forkJoin(requests).subscribe({
        next: () => {
          alert('Proformas marcadas como FACTURADAS exitosamente');
          this.selectedProformas = [];
          this.calculando = false;
          this.cargarProformas();
        },
        error: (error) => {
          console.error('Error actualizando proformas:', error);
          this.calculando = false;
          this.manejarError(error);
        }
      });
    }
  }

  // Métodos para generación y descarga de proformas
  generarProformas(): void {
    if (this.calculoForm.valid) {
      this.calculando = true;
      const formData = {
        ...this.calculoForm.value,
        holding: this.holding
      };
  
      this.api.post('generar-proformas/', formData)
        .subscribe({
          next: (response) => {
            alert('Proforma generada exitosamente');
            this.calculando = false;
            this.cargarProformas();
            this.calculoForm.reset();
            this.selectedTransportistas = [];
            // Establecer la fecha de emisión nuevamente después del reset
            this.calculoForm.patchValue({
              fecha_emision: new Date().toISOString().split('T')[0]
            });
            // Descargar el PDF automáticamente
            this.descargarProformaExistente(response.proforma_id);
          },
          error: (error) => {
            console.error('Error generando proforma:', error);
            this.calculando = false;
            this.manejarError(error);
          }
        });
    }
  }

  descargarProformaExistente(proformaId: number): void {
    this.api.getBlob(`generar-proformas/${proformaId}/pdf/`)
      .subscribe({
        next: (response: Blob) => {
          this.descargarPDF(response, `proforma_${proformaId}.pdf`);
        },
        error: (error) => {
          console.error('Error descargando proforma:', error);
          this.manejarError(error);
        }
      });
  }

  private descargarPDF(blob: Blob, filename: string): void {
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  }

  aplicarFiltros(): void {
    this.cargarProformas();
  }

  eliminarProforma(proforma: any): void {
    const mensaje = `¿Está seguro de eliminar la proforma ${proforma.id}? ` +
                   'Esta acción revertirá las producciones asociadas a estado PENDIENTE ' +
                   'y permitirá generar una nueva proforma para este período.';
    
    if (confirm(mensaje)) {
      this.calculando = true;
      
      this.api.delete(`generar-proformas/${proforma.id}/`, {})
        .subscribe({
          next: (response) => {
            alert('Proforma eliminada exitosamente');
            this.calculando = false;
            this.cargarProformas();
          },
          error: (error) => {
            console.error('Error eliminando proforma:', error);
            this.calculando = false;
            this.manejarError(error);
          }
        });
    }
  }

  private validateRut(rut: string): boolean {
    if (!rut) return false;

    // Remove dots and dashes
    rut = rut.replace(/\./g, '').replace(/-/g, '').toUpperCase();

    // Check basic format
    if (!/^[0-9]{1,8}[0-9K]$/.test(rut)) return false;

    const rutDigits = rut.slice(0, -1);
    const dv = rut.slice(-1);

    return this.calculateDv(rutDigits) === dv;
  }

  private calculateDv(rutDigits: string): string {
    const digits = rutDigits.split('').map(Number).reverse();
    let sum = 0;
    let factor = 2;
    
    for (const digit of digits) {
      sum += digit * factor;
      factor = factor === 7 ? 2 : factor + 1;
    }

    const remainder = 11 - (sum % 11);
    
    if (remainder === 11) return '0';
    if (remainder === 10) return 'K';
    return remainder.toString();
  }

  private formatRut(rut: string): string {
    if (!rut) return '';

    // Remove any existing dots, dashes and spaces
    rut = rut.replace(/\./g, '').replace(/-/g, '').replace(/\s/g, '');

    // Extract the verification digit if present
    let body = rut;
    let dv = '';
    
    if (rut.length > 1) {
      body = rut.slice(0, -1);
      dv = rut.slice(-1);
    }

    // Add dots for thousand separators
    body = body.replace(/\B(?=(\d{3})+(?!\d))/g, '.');

    // Return formatted RUT
    return body + (dv ? '-' + dv : '');
  }

 
  // Update your existing onRutFacturaInput method
  onRutFacturaInput(event: any): void {
    const input = event.target;
    let value = input.value.toUpperCase();
    
    // Remove invalid characters (allow only numbers and K)
    value = value.replace(/[^0-9K]/g, '');
    
    // Format the RUT with dots and dash
    const formattedValue = this.formatRut(value);
    
    // Update the input value and form control
    input.value = formattedValue;
    this.facturaForm.patchValue({ factura_rut: formattedValue });
  }

  private manejarError(error: any): void {
    let mensaje = 'Error al procesar la solicitud';
    if (error.error instanceof Blob) {
      const reader = new FileReader();
      reader.onload = () => {
        try {
          const errorJson = JSON.parse(reader.result as string);
          mensaje = errorJson.error || mensaje;
        } catch (e) {
          console.error('Error parseando el mensaje de error:', e);
        }
        alert(mensaje);
      };
      reader.readAsText(error.error);
    } else {
      if (error.error?.error) {
        mensaje = error.error.error;
      }
      alert(mensaje);
    }
  }
}