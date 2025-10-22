//salud.component.ts
import { Component, Inject, OnInit, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser, CommonModule } from '@angular/common';
import { ContratistaApiService } from '../../../../../services/contratista-api.service';
import { FormsModule } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';

@Component({
  selector: 'app-salud',
  standalone: true,
  imports: [
    MatTableModule,
    FormsModule,
    CommonModule,
  ],
  templateUrl: './salud.component.html',
  styleUrl: './salud.component.css'
})
export class SaludComponent implements OnInit {

  constructor(
    private apiService: ContratistaApiService,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {}

  // Booleanos para abrir o cerrar ventanas
  public modals: { [key: string]: boolean } = {
    exitoModal: false,
    errorModal: false,
    modificarSalud: false,
  };

  // Salud seleccionada - CORREGIDO: incluye codigo
  public saludSeleccionada: any = {
    id_salud_seleccionada: 0,        // ID interno autoincremental
    codigo_salud_seleccionado: 0,    // Código Previred
    nombre_salud_seleccionada: '',
    porcentaje_seleccionado: 7.0,
  }
  
  public holding: string = '';
  
  // Variables para modificar Salud (solo porcentaje)
  public porcentajeNew: number = 7.0;

  errorMessage!: string;
  selectedRows: any[] = [];

  public saludCargadas: any[] = [];

  // Columnas para mostrar - CORREGIDO: usa 'codigo'
  columnasDesplegadas = [
    'codigo',     // Código Previred
    'nombre',     
    'porcentaje'  
  ];
  
  public selectedSaludId: number | null = null;

  ngOnInit(): void {
    if (isPlatformBrowser(this.platformId)) {
      this.holding = localStorage.getItem('holding_id') || '';
      this.cargarSalud();
    }
  }

  cargarSalud(): void {
    this.apiService.get(`api_salud_trabajadores/?holding=${this.holding}`).subscribe({
      next: (response) => {
        console.log('Salud cargada:', response); // Debug para verificar estructura
        this.saludCargadas = response;
      },
      error: (error) => {
        console.error('Error al recibir la salud:', error);
        this.errorMessage = 'Error al cargar Salud';
        this.openModal('errorModal');
      }
    });
  }

  modificarSalud(): void {
    // Verificación adicional antes de enviar
    if (!this.selectedSaludId) {
      this.errorMessage = 'No se ha seleccionado una Salud válida';
      this.openModal('errorModal');
      return;
    }

    let data = {
      holding: this.holding,
      id: this.selectedSaludId,  // Usa ID interno para modificar
      porcentaje: this.porcentajeNew
    }
    
    console.log('Datos a enviar:', data); // Debug para verificar datos
    
    this.apiService.put('api_salud_trabajadores/', data).subscribe({
      next: (response) => {
        this.closeModal('modificarSalud');
        this.cargarSalud();
        this.openModal('exitoModal');
      }, 
      error: (error) => {
        console.log(error);
        this.errorMessage = error.error?.message || 'Error al modificar Salud';
        this.openModal('errorModal');
      }
    })
  }

  isSelected(row: any): boolean {
    return this.selectedRows.some(r => r.id === row.id);
  }

  selectRow(row: any): void {
    console.log('Fila seleccionada:', row); // Debug para verificar objeto row
    
    const index = this.selectedRows.findIndex(selectedRow => selectedRow.id === row.id);
    if (index > -1) {
      this.selectedRows.splice(index, 1);
    } else {
      // Solo permitir una fila seleccionada
      this.selectedRows = [row];
    }

    if (this.selectedRows.length > 0) {
      const selectedRow = this.selectedRows[0];
      
      // VERIFICACIÓN: Asegurar que el ID existe
      if (!selectedRow.id) {
        console.error('Error: El objeto seleccionado no tiene campo id:', selectedRow);
        this.errorMessage = 'Error: No se pudo obtener el ID de la Salud seleccionada';
        this.openModal('errorModal');
        return;
      }

      // CORREGIDO: incluye codigo y verificaciones
      this.saludSeleccionada = {
        id_salud_seleccionada: selectedRow.id,                           // ID interno
        codigo_salud_seleccionado: selectedRow.codigo || 0,              // Código Previred
        nombre_salud_seleccionada: selectedRow.nombre || '',
        porcentaje_seleccionado: selectedRow.porcentaje || 7.0,
      };
      
      this.selectedSaludId = this.saludSeleccionada.id_salud_seleccionada;
      
      // Debug para verificar asignación
      console.log('Salud seleccionada:', this.saludSeleccionada);
      console.log('ID asignado:', this.selectedSaludId);
      
      // Cargar dato en el formulario de modificación
      this.porcentajeNew = this.saludSeleccionada.porcentaje_seleccionado;
    } else {
      // Reset cuando no hay selección
      this.saludSeleccionada = {
        id_salud_seleccionada: 0,
        codigo_salud_seleccionado: 0,
        nombre_salud_seleccionada: '',
        porcentaje_seleccionado: 7.0,
      }
      this.selectedSaludId = null;
    }
  }

  deseleccionarFila(event: MouseEvent) {
    this.selectedRows = [];
    this.selectedSaludId = null;
    // Reset objeto seleccionado
    this.saludSeleccionada = {
      id_salud_seleccionada: 0,
      codigo_salud_seleccionado: 0,
      nombre_salud_seleccionada: '',
      porcentaje_seleccionado: 7.0,
    }
  }

  openModal(key: string): void {
    this.modals[key] = true;
  }

  closeModal(key: string): void {
    this.modals[key] = false;
    if (key === 'exitoModal') {
      this.cargarSalud();  
    }
  }
}