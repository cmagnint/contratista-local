import { Component, Inject, OnInit, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser, CommonModule } from '@angular/common';
import { ContratistaApiService } from '../../../../../services/contratista-api.service';
import { FormsModule } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';

@Component({
  selector: 'app-afp',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatTableModule,
  ],
  templateUrl: './afp.component.html',
  styleUrl: './afp.component.css'
})
export class AfpComponent implements OnInit {

  constructor(
    private apiService: ContratistaApiService,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {}

  // Booleanos para abrir o cerrar ventanas
  public modals: { [key: string]: boolean } = {
    exitoModal: false,
    errorModal: false,
    modificarAfp: false,
  };

  // AFP seleccionada - CORREGIDO: incluye codigo
  public afpSeleccionada: any = {
    id_afp_seleccionada: 0,                               // ID interno autoincremental
    codigo_afp_seleccionado: 0,                           // ← AGREGADO: Código Previred
    nombre_afp_seleccionada: '',
    porcentaje_cotizacion_individual_seleccionado: 10.0,
    comision_afp_seleccionado: 0.58,
    porcentaje_cargo_empleador_seleccionado: 0.1,
    porcentaje_seguro_social_seleccionado: 0.9,
  }

  public holding: string = '';
  
  // Variables para modificar AFP (solo porcentajes)
  public porcentajeCotizacionIndividualNew: number = 10.0;
  public comisionAfpNew: number = 0.58;
  public porcentajeCargoEmpleadorNew: number = 0.1;
  public porcentajeSeguroSocialNew: number = 0.9;

  errorMessage!: string;
  selectedRows: any[] = [];

  public afpsCargadas: any[] = [];

  // Columnas según la especificación - YA ESTÁ CORRECTO
  columnasDesplegadas = [
    'codigo',  // ← CORRECTO: Código Previred
    'nombre', 
    'porcentaje_cotizacion_individual',
    'comision_afp',
    'porcentaje_cargo_empleador',
    'porcentaje_seguro_social'
  ];
  
  public selectedAfpId: number | null = null;

  ngOnInit(): void {
    if (isPlatformBrowser(this.platformId)) {
      this.holding = localStorage.getItem('holding_id') || '';
      this.cargarAfps();
    }
  }

  cargarAfps(): void {
    this.apiService.get(`api_afp_trabajadores/?holding=${this.holding}`).subscribe({
      next: (response) => {
        this.afpsCargadas = response;
      },
      error: (error) => {
        console.error('Error al recibir las afps:', error);
        this.errorMessage = 'Error al cargar AFPs';
        this.openModal('errorModal');
      }
    });
  }

  modificarAfps(): void {
    let data = {
      holding: this.holding,
      id: this.selectedAfpId,  // Usa ID interno para modificar
      porcentaje_cotizacion_individual: this.porcentajeCotizacionIndividualNew,
      comision_afp: this.comisionAfpNew,
      porcentaje_cargo_empleador: this.porcentajeCargoEmpleadorNew,
      porcentaje_seguro_social: this.porcentajeSeguroSocialNew
    }
    
    this.apiService.put('api_afp_trabajadores/', data).subscribe({
      next: (response) => {
        this.closeModal('modificarAfp');
        this.cargarAfps();
        this.openModal('exitoModal');
      }, 
      error: (error) => {
        console.log(error);
        this.errorMessage = error.error?.message || 'Error al modificar AFP';
        this.openModal('errorModal');
      }
    })
  }

  isSelected(row: any): boolean {
    return this.selectedRows.some(r => r.id === row.id);
  }

  selectRow(row: any): void {
    const index = this.selectedRows.findIndex(selectedRow => selectedRow.id === row.id);
    if (index > -1) {
      this.selectedRows.splice(index, 1);
    } else {
      // Solo permitir una fila seleccionada
      this.selectedRows = [row];
    }

    if (this.selectedRows.length > 0) {
      const selectedRow = this.selectedRows[0];
      // CORREGIDO: incluye codigo
      this.afpSeleccionada = {
        id_afp_seleccionada: selectedRow.id,                                    // ID interno
        codigo_afp_seleccionado: selectedRow.codigo,                            // ← AGREGADO: Código Previred
        nombre_afp_seleccionada: selectedRow.nombre,
        porcentaje_cotizacion_individual_seleccionado: selectedRow.porcentaje_cotizacion_individual,
        comision_afp_seleccionado: selectedRow.comision_afp,
        porcentaje_cargo_empleador_seleccionado: selectedRow.porcentaje_cargo_empleador,
        porcentaje_seguro_social_seleccionado: selectedRow.porcentaje_seguro_social,
      };
      
      this.selectedAfpId = this.afpSeleccionada.id_afp_seleccionada;
      
      // Cargar datos en el formulario de modificación
      this.porcentajeCotizacionIndividualNew = this.afpSeleccionada.porcentaje_cotizacion_individual_seleccionado;
      this.comisionAfpNew = this.afpSeleccionada.comision_afp_seleccionado;
      this.porcentajeCargoEmpleadorNew = this.afpSeleccionada.porcentaje_cargo_empleador_seleccionado;
      this.porcentajeSeguroSocialNew = this.afpSeleccionada.porcentaje_seguro_social_seleccionado;
    } else {
      this.afpSeleccionada = {
        id_afp_seleccionada: 0,
        codigo_afp_seleccionado: 0,  // ← AGREGADO
        nombre_afp_seleccionada: '',
        porcentaje_cotizacion_individual_seleccionado: 10.0,
        comision_afp_seleccionado: 0.58,
        porcentaje_cargo_empleador_seleccionado: 0.1,
        porcentaje_seguro_social_seleccionado: 0.9,
      }
      this.selectedAfpId = null;
    }
  }

  deseleccionarFila(event: MouseEvent) {
    this.selectedRows = [];
    this.selectedAfpId = null;
  }

  openModal(key: string): void {
    this.modals[key] = true;
  }

  closeModal(key: string): void {
    this.modals[key] = false;
    if (key === 'exitoModal') {
      this.cargarAfps();  
    }
  }
}