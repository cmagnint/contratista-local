import { Component, Inject, OnInit, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser, CommonModule } from '@angular/common';
import { ContratistaApiService } from '../../../../services/contratista-api.service';
import { ReactiveFormsModule } from '@angular/forms';
import { FormsModule } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';

@Component({
  selector: 'app-vehiculos-transporte',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatTableModule,
    FormsModule
  ],
  templateUrl: './vehiculos-transporte.component.html',
  styleUrl: './vehiculos-transporte.component.css'
})
export class VehiculosTransporteComponent implements OnInit {
  //VARIABLES

  constructor(
    private apiService: ContratistaApiService,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {}

  // Booleanos para abrir o cerrar ventanas
  public modals: { [key: string]: boolean } = {
    exitoModal: false,
    errorModal: false,
    crearVehiculo: false,
    modificarVehiculo: false,
    confirmacionModal: false,
    empresasModal: false,
  };

  //Perfil seleccionado

  public vehiculoSeleccionado: any = {
    ppu_vehiculo_seleccionado : '',
    modelo_vehiculo_seleccionado : '',
    year_vehiculo_seleccionado : 0,
    color_vehiculo_seleccionado : '',
    numero_pasajeros_vehiculo_seleccionado : 0,
    marca_vehiculo_seleccionado : '',
    id_empresa_vehiculo_seleccionado: 0,
    id_vehiculo_seleccionada : 0,
  }

  public holding: string = ''; //Variable para guardar el ID del holding al cual pertenece al adminitrador
  public nombreEmpresa: string = '';
  public ppuVehiculo: string = '';
  public modeloVehiculo: string = '';
  public yearVehiculo: number = 0;
  public colorVehiculo: string = '';
  public numeroPasajerosVehiculo: number = 0;
  public marcaVehiculo: string = '';

  errorMessage!: string; //Variable usada para mostrar los mensajes de error de la API
  selectedRows: any[] = []; //Array usado para guardar las filas seleccionadas
  dropdownOpen: boolean = false; //Booleano usado para abrir los dropdownmenus 

  public todasSeleccionadas: boolean = false; //Booleano para seleccionar todas/ninguna casilla

  public vehiculosCargados: any[] = [];
  public empresasCargadas: any[] = [];

  columnasDesplegadas = ['empresa','ppu','modelo','year','color','numero_pasajeros','marca'];
  
  public ppuVehiculoNew: string = '';
  public modeloVehiculoNew: string = '';
  public yearVehiculoNew: number | null = null;
  public colorVehiculoNew: string = '';
  public numeroPasajerosVehiculoNew: number | null = null;
  public marcaVehiculoNew: string = '';

  public deletedRow: any[] = [];

  //TESTING 

  //------------------------------------------------------------//
  
  public selectedVehiculoId: number | null = null;
  public selectedEmpresaId: number | null = null;

  //FUNCIONES
  
  ngOnInit(): void {
    if (isPlatformBrowser(this.platformId)) {
      this.holding = localStorage.getItem('holding_id') || '';
      this.cargarVehiculos();
      this.cargarEmpresas();
    }
  }

  //FUNCIONES CRUD

  crearVehiculos():void{
    let data = {
      holding: this.holding,
      empresa : this.selectedEmpresaId,
      ppu : this.ppuVehiculo,
      modelo: this.modeloVehiculo,
      year: this.yearVehiculo,
      color: this.colorVehiculo,
      num_pasajeros: this.numeroPasajerosVehiculo,
      marca: this.marcaVehiculo
    }
    this.apiService.post('api_vehiculos_transportes/', data).subscribe({
      next: (response) => {
        console.log(response);
        this.closeModal('crearVehiculo');
        this.cargarVehiculos();
        this.openModal('exitoModal');
        
      }, error:(error) => {
        this.openModal('errorModal');
      }
    })
  }

  cargarEmpresas():void{
    this.apiService.get(`api_empresa_transportes/?holding=${this.holding}`).subscribe({
      next: (response) => {
        this.empresasCargadas = response;
        console.log(this.empresasCargadas);
      },
      error: (error) => {
        console.error('Error al recibir las sociedades:', error);
      }
    });
  }

  cargarVehiculos():void{
    this.apiService.get(`api_vehiculos_transportes/?holding=${this.holding}`).subscribe({
      next: (response) => {
        this.vehiculosCargados = response;
      },
      error: (error) => {
        console.error('Error al recibir las sociedades:', error);
      }
    });
  }

  modificarVehiculos():void{
    let data = {
      holding: this.holding,
      id : this.selectedVehiculoId,
      empresa: this.selectedEmpresaId,
      ppu: this.ppuVehiculoNew,
      modelo: this.modeloVehiculoNew,
      year: this.yearVehiculoNew,
      color: this.colorVehiculoNew,
      num_pasajeros: this.numeroPasajerosVehiculoNew,
      marca: this.marcaVehiculoNew,
      
    }
    this.apiService.put('api_vehiculos_transportes/', data).subscribe({
      next:(response) => {
        this.closeModal('crearVehiculo');
        this.cargarVehiculos();
        this.openModal('exitoModal');
      }, error:(error) => {
        console.log(error);
        this.openModal('errorModal');
      }
    })
  }
  
  eliminarVehiculosSeleccionados(): void {
    if (this.deletedRow.length > 0) {
        const idsToDelete = this.deletedRow.map(row => row.id);
        this.apiService.delete('api_vehiculos_transportes/', {ids: idsToDelete}).subscribe({
            next: () => {
                this.closeModal('confirmacionModal')
                this.cargarVehiculos();
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

  toggleSelection(empresaId: number): void {
    if (this.selectedEmpresaId === empresaId) {
      this.selectedEmpresaId = null;  // Deseleccionar si el mismo perfil es clickeado nuevamente
    } else {
      this.selectedEmpresaId = empresaId;  // Seleccionar el nuevo perfil
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
        this.vehiculoSeleccionado = {
        ppu_vehiculo_seleccionado: lastSelectedRow.ppu,
        modelo_vehiculo_seleccionado: lastSelectedRow.modelo,
        year_vehiculo_seleccionado: lastSelectedRow.year,
        color_vehiculo_seleccionado:  lastSelectedRow.color,
        numero_pasajeros_vehiculo_seleccionado: lastSelectedRow.num_pasajeros,
        marca_vehiculo_seleccionado: lastSelectedRow.marca,
        id_vehiculo_seleccionado : lastSelectedRow.id,
        id_empresa_vehiculo_seleccionado: lastSelectedRow.empresa
      };
      this.ppuVehiculoNew = this.vehiculoSeleccionado.ppu_vehiculo_seleccionado
      this.modeloVehiculoNew = this.vehiculoSeleccionado.modelo_vehiculo_seleccionado
      this.yearVehiculoNew = this.vehiculoSeleccionado.year_vehiculo_seleccionado
      this.colorVehiculoNew = this.vehiculoSeleccionado.color_vehiculo_seleccionado
      this.numeroPasajerosVehiculoNew = this.vehiculoSeleccionado.numero_pasajeros_vehiculo_seleccionado
      this.marcaVehiculoNew = this.vehiculoSeleccionado.marca_vehiculo_seleccionado
      this.selectedVehiculoId = this.vehiculoSeleccionado.id_vehiculo_seleccionado;
      this.selectedEmpresaId = this.vehiculoSeleccionado. id_empresa_vehiculo_seleccionado;

    } else {
      // Limpiar perfilSeleccionado si no hay filas seleccionadas
      this.vehiculoSeleccionado = {
        ppu_vehiculo_seleccionado : '',
        modelo_vehiculo_seleccionado : '',
        year_vehiculo_seleccionado : 0,
        color_vehiculo_seleccionado : '',
        numero_pasajeros_vehiculo_seleccionado : 0,
        marca_vehiculo_seleccionado : '',
        id_empresa_vehiculo_seleccionado: 0,
        id_vehiculo_seleccionada : 0,
      }
    }
  }


  formatNumber(event: Event): void{
    const target = event.target as HTMLInputElement; // Casting seguro
    if (!target) return; // Verificar que realmente existe un target
    let rut = target.value.replace(/\D/g, '');
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
      this.cargarEmpresas();  
    }
  }

}
