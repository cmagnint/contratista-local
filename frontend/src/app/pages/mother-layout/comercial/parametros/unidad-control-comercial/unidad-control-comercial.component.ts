import { Component, Inject, OnInit, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser, CommonModule } from '@angular/common';
import { ContratistaApiService } from '../../../../../services/contratista-api.service';
import { FormsModule } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';
import { JwtService } from '../../../../../services/jwt.service';
@Component({
  selector: 'app-unidad-control-comercial',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatTableModule,
  ],
  templateUrl: './unidad-control-comercial.component.html',
  styleUrl: './unidad-control-comercial.component.css'
})
export class UnidadControlComercialComponent implements OnInit {
  //VARIABLES

  constructor(
    private contratistaApiService: ContratistaApiService,
    private jwtService: JwtService,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {}

  // Booleanos para abrir o cerrar ventanas
  public modals: { [key: string]: boolean } = {
    exitoModal: false,
    errorModal: false,
    crearUnidadControl: false,
    modificarUnidadControl: false,
    confirmacionModal: false,
  };

  //Unidad Contrl  seleccionado

  public unidadControlSeleccionada: any = {
    nombre_unidad_control_seleccionada : '',
    id_unidad_control_seleccionada : 0,
    cantidad_unidad_control_seleccionada: 0,
    estado_unidad_control_seleccionada: true,
  }

  
  public holding: string = ''; //Variable para guardar el ID del holding al cual pertenece al adminitrador
  public nombreUnidadControl: string = '';
  public nombreUnidadControlNew: string = '';
  public cantidadUnidadControl: number | null = null;
  public cantidadUnidadControlNew: number | null = null;
 

  errorMessage!: string; //Variable usada para mostrar los mensajes de error de la API
  selectedRows: any[] = []; //Array usado para guardar las filas seleccionadas
  dropdownOpen: boolean = false; //Booleano usado para abrir los dropdownmenus 

  public todasSeleccionadas: boolean = false; //Booleano para seleccionar todas/ninguna casilla

  public unidadControlCargadas: any[] = [];

  columnasDesplegadas = ['codigo','nombre','peso','estado'];
  
  public deletedRow: any[] = [];
  //TESTING 

  //------------------------------------------------------------//

 
  public selectedUnidadControlId: number | null = null;

  //FUNCIONES
  
  ngOnInit(): void {
    if (isPlatformBrowser(this.platformId)) {
      this.holding = this.getHoldingIdFromJWT();
      this.cargarUnidadControl();
    }
  }

  private getHoldingIdFromJWT(): string {
    try {
      const userInfo = this.jwtService.getUserInfo();
      const holdingId = userInfo?.holding_id;
      
      console.log('🔍 Holding ID del JWT:', holdingId);
      
      if (holdingId && holdingId !== null ) {
        return holdingId.toString();
      } else {
        console.warn('⚠️ Holding ID no encontrado en JWT o es null');
        return '';
      }
    } catch (error) {
      console.error('❌ Error extrayendo holding_id del JWT:', error);
      return '';
    }
  }

  //FUNCIONES CRUD

  crearUnidadControl():void{
    let data = {
      holding: this.holding,
      nombre : this.nombreUnidadControl,
      cantidad: this.cantidadUnidadControl,
    }
    this.contratistaApiService.post('unidad_control_comercial/', data).subscribe({
      next: (response) => {
        console.log(response);
        this.closeModal('crearUnidadControl');
        this.cargarUnidadControl();
        this.openModal('exitoModal');
        
      }, error:(error) => {
        this.openModal('errorModal');
      }
    })
  }

  cargarUnidadControl():void{
    this.contratistaApiService.get(`unidad_control_comercial/?holding=${this.holding}`).subscribe({
      next: (response) => {
        this.unidadControlCargadas = response;
      },
      error: (error) => {
        console.error('Error al recibir las sociedades:', error);
      }
    });
  }

  modificarAfps():void{
    let data = {
      holding: this.holding,
      id : this.selectedUnidadControlId,
      nombre: this.nombreUnidadControlNew,
      cantidad: this.cantidadUnidadControlNew,
      estado: this.estadoUnidadControl,
    }
    this.contratistaApiService.put('unidad_control_comercial/', data).subscribe({
      next:(response) => {
        this.closeModal('modificarUnidadControl');
        this.cargarUnidadControl();
        this.openModal('exitoModal');
      }, error:(error) => {
        console.log(error);
        this.openModal('errorModal');
      }
    })
  }
  
  eliminarAfpSeleccionadas(): void {
    if (this.deletedRow.length > 0) {
        const idsToDelete = this.deletedRow.map(row => row.id);
        this.contratistaApiService.delete('unidad_control_comercial/', {ids: idsToDelete}).subscribe({
            next: () => {
                this.closeModal('confirmacionModal')
                this.cargarUnidadControl();
                this.openModal('exitoModal');
                this.deletedRow = []; // Limpiar la selección después de eliminar
            },
            error: (error) => {
                this.openModal('errorModal');
                console.error('Error al eliminar perfiles:', error);
            }
        });
    }
  }

  //------------------------------------------------------------------------------//

  toggleSelection(afpId: number): void {
    if (this.selectedUnidadControlId === afpId) {
      this.selectedUnidadControlId = null;  // Deseleccionar si el mismo perfil es clickeado nuevamente
    } else {
      this.selectedUnidadControlId = afpId;  // Seleccionar el nuevo perfil
    }
  }

  isSelected(row: any): boolean {
    return this.selectedRows.some(r => r.id === row.id);
  }

  selectRow(row: any): void {
    const index = this.selectedRows.findIndex(selectedRow => selectedRow.id === row.id);
    if (index > -1) {
        // Si la fila ya está seleccionada, deseleccionarla
        this.selectedRows.splice(index, 1);
    } else {
        // Agregar fila a las seleccionadas
        this.selectedRows.push(row);
    }

    if (this.selectedRows.length > 0){
        const lastSelectedRow = this.selectedRows[this.selectedRows.length - 1];
        this.unidadControlSeleccionada = {
        nombre_unidad_control_seleccionada : lastSelectedRow.nombre,
        id_unidad_control_seleccionada : lastSelectedRow.id,
        cantidad_unidad_control_seleccionada : lastSelectedRow.cantidad,
        estado_unidad_control_seleccionada: lastSelectedRow.estado,
      };
      this.selectedUnidadControlId = this.unidadControlSeleccionada.id_unidad_control_seleccionada;
      this.nombreUnidadControlNew = this.unidadControlSeleccionada.nombre_unidad_control_seleccionada;
      this.cantidadUnidadControlNew = this.unidadControlSeleccionada.cantidad_unidad_control_seleccionada;
      this.estadoUnidadControl = this.unidadControlSeleccionada.estado_unidad_control_seleccionada;


    } else {
      // Limpiar perfilSeleccionado si no hay filas seleccionadas
      this.unidadControlSeleccionada = {
        nombre_unidad_control_seleccionada : '',
        id_unidad_control_seleccionada : 0,
        cantidad_unidad_control_seleccionada: 0,
        estdo_unidad_control_seleccionada: true,
      }
    }
  }

  estadoUnidadControl: boolean = true; // Inicializa el estado

  toggleEstadoUnidadControl() {
    this.estadoUnidadControl = !this.estadoUnidadControl;
  }

  formatNumber(event: Event): void {
    const target = event.target as HTMLInputElement; // Casting seguro
    if (!target) return; // Verificar que realmente existe un target

    // Mantener solo caracteres numéricos
    target.value = target.value.replace(/[^\d]/g, '');
  }

  formatRUT(event: Event): void {
    const target = event.target as HTMLInputElement; // Casting seguro
    if (!target) return; // Verificar que realmente existe un target

    let rut = target.value.replace(/\D/g, '');
    let parts = [];
    const verifier = rut.slice(-1);
    rut = rut.slice(0, -1);
    while (rut.length > 3) {
        parts.unshift(rut.slice(-3));
        rut = rut.slice(0, -3);
    }
    parts.unshift(rut);
    target.value = parts.join('.') + '-' + verifier;
    if (target.value === '-') {
        target.value = '';
    }
  }
  
  formatRUTString(value: string): string {
    let rut = value.replace(/\D/g, '');
    let parts = [];
    const verifier = rut.slice(-1);
    rut = rut.slice(0, -1);
    while (rut.length > 3) {
        parts.unshift(rut.slice(-3));
        rut = rut.slice(0, -3);
    }
    parts.unshift(rut);
    return parts.join('.') + '-' + verifier;
  }

  toggleDropdown() {
    this.dropdownOpen = !this.dropdownOpen;
  }

  deseleccionarFila(event: MouseEvent) {
    this.selectedRows = [];  // Deselecciona todas las filas
  }

  openModal(key: string): void {
    this.modals[key] = true;
    if(key== 'confirmacionModal'){
      this.deletedRow = this.selectedRows;
      console.log(this.deletedRow);
    }

   
  }

  closeModal(key: string): void {
    this.modals[key] = false;
    if (key === 'exitoModal') {
      this.cargarUnidadControl();  
    }
  }

  checkValue():void{
    
    
  }
}
