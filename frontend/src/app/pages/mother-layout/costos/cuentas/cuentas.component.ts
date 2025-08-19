import { Component, Inject, OnInit, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser, CommonModule } from '@angular/common';
import { ContratistaApiService } from '../../../../services/contratista-api.service';
import { ReactiveFormsModule } from '@angular/forms';
import { FormsModule } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';

@Component({
  selector: 'app-cuentas',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    FormsModule,
    MatTableModule,
    MatIconModule,
    MatButtonModule
  ],
  templateUrl: './cuentas.component.html',
  styleUrl: './cuentas.component.css'
})
export class CuentasComponent implements OnInit {
  
  constructor(
    private contratistaApiService: ContratistaApiService,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {}

  // VARIABLES
  public holding: string = '';
  
  // Variables para crear cuenta
  public nombreCuenta: string = '';
  public cuentaContable: string = '';
  
  // Variables para modificar cuenta
  public nombreCuentaNew: string = '';
  public cuentaContableNew: string = '';
  public activaNew: boolean = true;
  
  // Variables para datos cargados
  public cuentasCargadas: any[] = [];
  
  // Variables para manejo de selección
  public selectedRows: any[] = [];
  public selectedCuentaId: number | null = null;
  
  // Variables para mensajes
  public errorMessage: string = '';
  
  // Configuración de tabla
  public columnasDesplegadas = ['id', 'nombre_cuenta', 'cuenta_contable', 'estado'];
  
  // Booleanos para modales
  public modals: { [key: string]: boolean } = {
    crearCuenta: false,
    modificarCuenta: false,
    exitoModal: false,
    errorModal: false,
    confirmacionModal: false
  };

  ngOnInit(): void {
    if (isPlatformBrowser(this.platformId)) {
      this.holding = localStorage.getItem('holding_id') || '';
      this.cargarCuentas();
    }
  }

  // MÉTODOS PARA CARGAR DATOS
  cargarCuentas(): void {
    this.contratistaApiService.get(`api_cuentas/?holding=${this.holding}`).subscribe({
      next: (response) => {
        if (response.cuentas) {
          this.cuentasCargadas = response.cuentas;
        } else {
          this.cuentasCargadas = [];
        }
        this.selectedRows = [];
      },
      error: (error) => {
        console.error('Error al cargar cuentas:', error);
        this.errorMessage = 'Error al cargar las cuentas';
        this.openModal('errorModal');
      }
    });
  }

  // MÉTODOS CRUD
  crearCuenta(): void {
    if (!this.nombreCuenta.trim() || !this.cuentaContable.trim()) {
      this.errorMessage = 'Todos los campos son obligatorios';
      this.openModal('errorModal');
      return;
    }

    const data = {
      holding: this.holding,
      nombre_cuenta: this.nombreCuenta.trim(),
      cuenta_contable: this.cuentaContable.trim(),
      activa: true
    };

    this.contratistaApiService.post('api_cuentas/', data).subscribe({
      next: (response) => {
        this.closeModal('crearCuenta');
        this.limpiarFormularioCrear();
        this.cargarCuentas();
        this.openModal('exitoModal');
      },
      error: (error) => {
        console.error('Error al crear cuenta:', error);
        this.errorMessage = error.error?.message || 'Error al crear la cuenta';
        this.openModal('errorModal');
      }
    });
  }

  modificarCuenta(): void {
    if (!this.selectedCuentaId) {
      this.errorMessage = 'No se ha seleccionado ninguna cuenta';
      this.openModal('errorModal');
      return;
    }

    if (!this.nombreCuentaNew.trim() || !this.cuentaContableNew.trim()) {
      this.errorMessage = 'Todos los campos son obligatorios';
      this.openModal('errorModal');
      return;
    }

    const data = {
      holding: this.holding,
      nombre_cuenta: this.nombreCuentaNew.trim(),
      cuenta_contable: this.cuentaContableNew.trim(),
      activa: this.activaNew
    };

    this.contratistaApiService.put(`api_cuentas/update/${this.selectedCuentaId}/`, data).subscribe({
      next: (response) => {
        this.closeModal('modificarCuenta');
        this.limpiarFormularioModificar();
        this.cargarCuentas();
        this.openModal('exitoModal');
      },
      error: (error) => {
        console.error('Error al modificar cuenta:', error);
        this.errorMessage = error.error?.message || 'Error al modificar la cuenta';
        this.openModal('errorModal');
      }
    });
  }

  eliminarCuentasSeleccionadas(): void {
    if (this.selectedRows.length === 0) {
      this.errorMessage = 'No se han seleccionado cuentas para eliminar';
      this.openModal('errorModal');
      return;
    }

    // Para cada cuenta seleccionada, hacer la eliminación
    const eliminaciones = this.selectedRows.map(cuenta => {
      return this.contratistaApiService.delete(`api_cuentas/delete/${cuenta.id}/`, {});
    });

    // Ejecutar todas las eliminaciones
    Promise.allSettled(eliminaciones).then(results => {
      let errores = 0;
      let exitosos = 0;

      results.forEach(result => {
        if (result.status === 'fulfilled') {
          exitosos++;
        } else {
          errores++;
        }
      });

      this.closeModal('confirmacionModal');
      this.selectedRows = [];
      this.cargarCuentas();

      if (errores === 0) {
        this.openModal('exitoModal');
      } else {
        this.errorMessage = `Se eliminaron ${exitosos} cuentas. ${errores} no pudieron eliminarse.`;
        this.openModal('errorModal');
      }
    });
  }

  // MÉTODOS DE UTILIDAD
  limpiarFormularioCrear(): void {
    this.nombreCuenta = '';
    this.cuentaContable = '';
  }

  limpiarFormularioModificar(): void {
    this.nombreCuentaNew = '';
    this.cuentaContableNew = '';
    this.activaNew = true;
    this.selectedCuentaId = null;
  }

  // MÉTODOS PARA MANEJO DE SELECCIÓN
  isSelected(row: any): boolean {
    return this.selectedRows.some(r => r.id === row.id);
  }

  selectRow(row: any): void {
    const index = this.selectedRows.findIndex(selectedRow => selectedRow.id === row.id);
    
    if (index > -1) {
      this.selectedRows.splice(index, 1);
    } else {
      this.selectedRows.push(row);
    }

    // Si hay exactamente una fila seleccionada, cargar sus datos para modificación
    if (this.selectedRows.length === 1) {
      const selectedRow = this.selectedRows[0];
      this.selectedCuentaId = selectedRow.id;
      this.nombreCuentaNew = selectedRow.nombre_cuenta;
      this.cuentaContableNew = selectedRow.cuenta_contable;
      this.activaNew = selectedRow.activa;
    } else {
      this.limpiarFormularioModificar();
    }
  }

  deseleccionarFila(event: MouseEvent): void {
    this.selectedRows = [];
    this.limpiarFormularioModificar();
  }

  // MÉTODOS PARA MODALES
  openModal(key: string): void {
    this.modals[key] = true;
  }

  closeModal(key: string): void {
    this.modals[key] = false;
    
    if (key === 'crearCuenta') {
      this.limpiarFormularioCrear();
    } else if (key === 'modificarCuenta') {
      this.limpiarFormularioModificar();
    }
  }

  // VALIDACIONES
  validateInput(event: KeyboardEvent, allowNumbers: boolean = true, allowLetters: boolean = true): void {
    const char = String.fromCharCode(event.charCode);
    const isNumber = /[0-9]/.test(char);
    const isLetter = /[a-zA-ZÀ-ÿ\u00f1\u00d1\s]/.test(char);
    const isSpecial = /[-._]/.test(char);

    if ((!allowNumbers || !isNumber) && (!allowLetters || !isLetter) && !isSpecial) {
      if (!allowNumbers && isNumber) {
        event.preventDefault();
      } else if (!allowLetters && isLetter) {
        event.preventDefault();
      } else if (!isNumber && !isLetter && !isSpecial) {
        event.preventDefault();
      }
    }
  }

  // Validación específica para cuenta contable (solo números, puntos y guiones)
  validateCuentaContable(event: KeyboardEvent): void {
    const char = String.fromCharCode(event.charCode);
    const pattern = /[0-9.-]/;
    
    if (!pattern.test(char)) {
      event.preventDefault();
    }
  }
}