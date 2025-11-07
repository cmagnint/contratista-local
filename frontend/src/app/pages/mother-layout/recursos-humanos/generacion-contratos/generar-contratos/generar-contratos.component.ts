import { Component, Inject, OnInit, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser, CommonModule } from '@angular/common';
import { ContratistaApiService } from '../../../../../services/contratista-api.service';
import { FormsModule } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatInputModule } from '@angular/material/input';
import { SelectionModel } from '@angular/cdk/collections';

@Component({
  selector: 'app-generar-contratos',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatTableModule,
    MatButtonModule,
    MatSelectModule,
    MatFormFieldModule,
    MatIconModule,
    MatCheckboxModule,
    MatInputModule
  ],
  templateUrl: './generar-contratos.component.html',
  styleUrl: './generar-contratos.component.css'
})
export class GenerarContratosComponent implements OnInit {
  
  constructor(
    private apiService: ContratistaApiService,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {}

  // ============================================
  // 🎯 VARIABLES
  // ============================================
  public holding: string = '';
  public sociedad: string = '';
  public sociedades: any[] = [];
  public trabajadores: any[] = [];
  public documentos: any[] = [];
  public documentoSeleccionado: number | null = null;
  public fechaEmision: string = '';
  public filtroContrato: string = 'sin_contrato'; // ✅ NUEVO: filtro por defecto
  public contratosGenerados: any[] = []; // ✅ NUEVO: almacenar contratos generados
  public mostrarContratos: boolean = false; // ✅ NUEVO: controlar visibilidad
  // Selección
  public selection = new SelectionModel<any>(true, []);
  public selectedRows: any[] = [];
  
  // Columnas de la tabla
  displayedColumns: string[] = [
    'select',
    'id',
    'nombres',
    'apellidos',
    'rut',
    'estado_contrato', // ✅ NUEVO
    'cargo',
    'fecha_ingreso'
  ];
  
  // Modales
  public modals: { [key: string]: boolean } = {
    exitoModal: false,
    errorModal: false,
    confirmacionRegenerarModal: false // ✅ NUEVO
  };
  
  public errorMessage: string = '';
  public confirmMessage: string = ''; // ✅ NUEVO

  // ============================================
  // 🎯 LIFECYCLE
  // ============================================
  ngOnInit(): void {
    if (isPlatformBrowser(this.platformId)) {
      this.holding = localStorage.getItem('holding_id') || '';
      this.fechaEmision = new Date().toISOString().split('T')[0]; // Fecha actual por defecto
      this.cargarSociedades();
      this.cargarDocumentos();
    }
    
    // Observar cambios en la selección
    this.selection.changed.subscribe(() => {
      this.selectedRows = this.selection.selected;
    });
  }

  // ============================================
  // 🎯 CARGA DE DATOS
  // ============================================
  cargarSociedades(): void {
    this.apiService.get(`api_sociedades_modify/${this.holding}/`).subscribe({
      next: (response) => {
        this.sociedades = response;
        console.log('✅ Sociedades cargadas:', this.sociedades.length);
      },
      error: (error) => {
        console.error('❌ Error al cargar sociedades:', error);
        this.errorMessage = 'Error al cargar sociedades';
        this.openModal('errorModal');
      }
    });
  }

  cargarDocumentos(): void {
    // Cargar documentos tipo CHILENO (puedes agregar filtro por tipo si lo necesitas)
    this.apiService.get(`api_listar-documentos/?tipo=CHILENO&holding=${this.holding}`).subscribe({
      next: (response) => {
        this.documentos = response;
        console.log('✅ Documentos cargados:', this.documentos.length);
      },
      error: (error) => {
        console.error('❌ Error al cargar documentos:', error);
        this.errorMessage = 'Error al cargar documentos';
        this.openModal('errorModal');
      }
    });
  }

  cargarTrabajadores(): void {
    if (!this.sociedad) {
      this.trabajadores = [];
      return;
    }
    
    // ✅ INCLUIR filtro_contrato en la petición
    const params = `holding=${this.holding}&sociedad_id=${this.sociedad}&filtro_contrato=${this.filtroContrato}`;
    
    this.apiService.get(`api_personal_filtrado/?${params}`).subscribe({
      next: (response) => {
        this.trabajadores = response;
        this.selection.clear(); // Limpiar selección al cargar nuevos datos
        console.log('✅ Trabajadores cargados:', this.trabajadores.length);
      },
      error: (error) => {
        console.error('❌ Error al cargar trabajadores:', error);
        this.errorMessage = 'Error al cargar trabajadores';
        this.openModal('errorModal');
      }
    });
  }

  // ============================================
  // 🎯 FILTROS
  // ============================================
  cambiarFiltroContrato(filtro: string): void {
    this.filtroContrato = filtro;
    this.selection.clear(); // Limpiar selección al cambiar filtro
    this.cargarTrabajadores();
  }

  // ============================================
  // 🎯 SELECCIÓN DE TRABAJADORES
  // ============================================
  isAllSelected(): boolean {
    const numSelected = this.selection.selected.length;
    const numRows = this.trabajadores.length;
    return numSelected === numRows;
  }

  toggleAllRows(): void {
    if (this.isAllSelected()) {
      this.selection.clear();
    } else {
      this.trabajadores.forEach(row => this.selection.select(row));
    }
  }

  // ============================================
  // 🎯 GENERACIÓN DE CONTRATOS
  // ============================================
  generarContratos(): void {
    // Validaciones
    if (this.selectedRows.length === 0) {
      this.errorMessage = 'Debe seleccionar al menos un trabajador';
      this.openModal('errorModal');
      return;
    }

    if (!this.documentoSeleccionado) {
      this.errorMessage = 'Debe seleccionar un tipo de documento';
      this.openModal('errorModal');
      return;
    }

    if (!this.fechaEmision) {
      this.errorMessage = 'Debe seleccionar una fecha de emisión';
      this.openModal('errorModal');
      return;
    }
    
    // ✅ VERIFICAR si hay trabajadores con contrato ya generado
    const conContrato = this.selectedRows.filter(t => t.tiene_contrato);
    
    if (conContrato.length > 0 && this.filtroContrato !== 'con_contrato') {
      this.confirmMessage = `${conContrato.length} trabajador(es) ya tienen contrato generado. ¿Desea regenerarlo?`;
      this.openModal('confirmacionRegenerarModal');
      return;
    }
    
    // Si no hay conflicto, generar directamente
    this.confirmarGeneracion();
  }

  confirmarGeneracion(): void {
    const trabajadorIds = this.selectedRows.map(t => t.id);
    
    const payload = {
      documento_id: this.documentoSeleccionado,
      trabajador_ids: trabajadorIds,
      fecha_emision: this.fechaEmision,
      sociedad_id: this.sociedad
    };

    console.log('📤 Enviando payload:', payload);
    
    this.apiService.post('api_generar-documentos-masivo/', payload).subscribe({
      next: (response) => {
        console.log('✅ Contratos generados:', response);
        
        // ✅ CAPTURAR CONTRATOS GENERADOS
        this.contratosGenerados = response.contratos || [];
        this.mostrarContratos = true;
        
        this.closeModal('confirmacionRegenerarModal');
        this.selection.clear();
        this.selectedRows = [];
        this.cargarTrabajadores();
        this.openModal('exitoModal');
      },
      error: (error) => {
        console.error('❌ Error al generar contratos:', error);
        this.errorMessage = error.error?.error || 'Error al generar contratos';
        this.closeModal('confirmacionRegenerarModal');
        this.openModal('errorModal');
      }
    });
  }

  // ✅ NUEVO: Descargar un contrato individual
  descargarContrato(url: string, nombreTrabajador: string): void {
    window.open(url, '_blank');
  }

  // ✅ NUEVO: Descargar todos en ZIP
  descargarTodosContratos(): void {
    if (this.contratosGenerados.length === 0) return;

    // Si es solo 1, descargar directamente
    if (this.contratosGenerados.length === 1) {
      this.descargarContrato(
        this.contratosGenerados[0].url, 
        this.contratosGenerados[0].trabajador_nombre
      );
      return;
    }

    // Si son múltiples, usar JSZip
    import('jszip').then(JSZip => {
      const zip = new JSZip.default();
      let completados = 0;

      this.contratosGenerados.forEach((contrato, index) => {
        fetch(contrato.url)
          .then(response => response.blob())
          .then(blob => {
            const nombreArchivo = `contrato_${contrato.trabajador_nombre.replace(/\s+/g, '_')}.pdf`;
            zip.file(nombreArchivo, blob);
            completados++;

            // Cuando todos estén listos, descargar ZIP
            if (completados === this.contratosGenerados.length) {
              zip.generateAsync({ type: 'blob' }).then(content => {
                const link = document.createElement('a');
                link.href = URL.createObjectURL(content);
                link.download = `contratos_${new Date().toISOString().split('T')[0]}.zip`;
                link.click();
              });
            }
          })
          .catch(error => {
            console.error('Error descargando contrato:', error);
            completados++;
          });
      });
    });
  }

  // ✅ NUEVO: Cerrar panel de contratos
  cerrarPanelContratos(): void {
    this.contratosGenerados = [];
    this.mostrarContratos = false;
  }

  // ============================================
  // 🎯 GESTIÓN DE MODALES
  // ============================================
  openModal(key: string): void {
    this.modals[key] = true;
  }

  closeModal(key: string): void {
    this.modals[key] = false;
    
    // Limpiar mensajes al cerrar
    if (key === 'errorModal') {
      this.errorMessage = '';
    }
    if (key === 'confirmacionRegenerarModal') {
      this.confirmMessage = '';
    }
  }
}