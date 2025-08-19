import { Component, Inject, OnInit, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser, CommonModule } from '@angular/common';
import { ContratistaApiService } from '../../../../../services/contratista-api.service';
import { FormsModule } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';
import { JwtService } from '../../../../../services/jwt.service';
@Component({
  selector: 'app-labores-comercial',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatTableModule,
  ],
  templateUrl: './labores-comercial.component.html',
  styleUrl: './labores-comercial.component.css'
})
export class LaboresComercialComponent implements OnInit {
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
    crearLabor: false,
    modificarLabor: false,
    confirmacionModal: false,
    unidadControlModal: false,
  };

  //Unidad Contrl  seleccionado

  public laborSeleccionada: any = {
    id_labor_seleccionada : 0,
    id_unidad_control_labor_seleccionada: 0,
    nombre_labor_seleccionada : '',
    especie_labor_seleccionada: 0,
    estado_labor_seleccionada: true,
  }

  public holding: string = ''; 
  public nombreLabor: string = '';
  public nombreLaborNew: string = '';
  public nombreEspecieLabor: number | null = null;
  public nombreEspecieLaborNew: number | null = null;
  public selectedLaborId: number | null = null;
  public selectedUnidadControlId: number | null = null;
  public selectedUnidadControlNewId: number | null = null;

  errorMessage!: string; //Variable usada para mostrar los mensajes de error de la API
  selectedRows: any[] = []; //Array usado para guardar las filas seleccionadas
  dropdownOpen: boolean = false; //Booleano usado para abrir los dropdownmenus 

  public todasSeleccionadas: boolean = false; //Booleano para seleccionar todas/ninguna casilla

  public laboresCargadas: any[] = [];
  public unidadControlCargadas: any[] = [];
  columnasDesplegadas = ["codigo","nombre","especie","unidad_control","estado"];
  
  public deletedRow: any[] = [];
  //TESTING 

  //------------------------------------------------------------//

 
 

  //FUNCIONES
  
  ngOnInit(): void {
    if (isPlatformBrowser(this.platformId)) {
      this.holding = this.getHoldingIdFromJWT();
      this.cargarLabor();
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

  crearLabor():void{
    let data = {
      holding: this.holding,
      nombre : this.nombreLabor,
      especie: this.nombreEspecieLabor,
      unidad_control: this.selectedUnidadControlId
    }
    this.contratistaApiService.post('labores_comercial/', data).subscribe({
      next: (response) => {
        console.log(response);
        this.closeModal('crearLabor');
        this.cargarLabor();
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


  cargarLabor():void{
    this.contratistaApiService.get(`labores_comercial/?holding=${this.holding}`).subscribe({
      next: (response) => {
        this.laboresCargadas = response;
      },
      error: (error) => {
        console.error('Error al recibir las labores:', error);
      }
    });
  }

  modificarLabor():void{
    let data = {
      holding: this.holding,
      id : this.selectedLaborId,
      nombre: this.nombreLaborNew,
      especie: this.nombreEspecieLaborNew,
      unidad_control: this.selectedUnidadControlNewId,
      estado: this.estadoLabor,
    }
    this.contratistaApiService.put('labores_comercial/', data).subscribe({
      next:(response) => {
        this.closeModal('modificarLabor');
        this.cargarLabor();
        this.openModal('exitoModal');
      }, error:(error) => {
        console.log(error);
        this.openModal('errorModal');
      }
    })
  }
  
  eliminarLaborSeleccionadas(): void {
    if (this.deletedRow.length > 0) {
        const idsToDelete = this.deletedRow.map(row => row.id);
        this.contratistaApiService.delete('labores_comercial/', {ids: idsToDelete}).subscribe({
            next: () => {
                this.closeModal('confirmacionModal')
                this.cargarLabor();
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

  toggleSelectionUnidadControlSelectedNew(unidadId: number): void {
    if (this.selectedUnidadControlNewId === unidadId) {
      this.selectedUnidadControlNewId = null;  // Deseleccionar si el mismo perfil es clickeado nuevamente
    } else {
      this.selectedUnidadControlNewId = unidadId;  // Seleccionar el nuevo perfil
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
        this.laborSeleccionada = {
        nombre_labor_seleccionada : lastSelectedRow.nombre,
        id_labor_seleccionada : lastSelectedRow.id,
        id_unidad_control_labor_seleccionada : lastSelectedRow.unidad_control,
        estado_labor_seleccionada: lastSelectedRow.estado,
        especie_labor_seleccionada: lastSelectedRow.especie,
      };
      this.selectedLaborId = this.laborSeleccionada.id_labor_seleccionada;
      this.selectedUnidadControlNewId = this.laborSeleccionada.id_unidad_control_labor_seleccionada;
      this.nombreLaborNew = this.laborSeleccionada.nombre_labor_seleccionada;
      this.nombreEspecieLaborNew = this.laborSeleccionada.especie_labor_seleccionada;
      this.estadoLabor = this.laborSeleccionada.estado_labor_seleccionada;


    } else {
      // Limpiar perfilSeleccionado si no hay filas seleccionadas
      this.laborSeleccionada = {
        id_labor_seleccionada : 0,
        id_unidad_control_labor_seleccionada: 0,
        nombre_labor_seleccionada : '',
        especie_labor_seleccionada: 0,
        estado_labor_seleccionada: true,
      }
    }
  }

  estadoLabor: boolean = true; // Inicializa el estado

  toggleEstadoLabor() {
    this.estadoLabor = !this.estadoLabor;
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
      this.cargarLabor();  
    }
  }

  checkValue():void{
    
    
  }
}
