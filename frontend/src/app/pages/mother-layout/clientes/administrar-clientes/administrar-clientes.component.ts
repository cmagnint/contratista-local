import { Component, Inject, OnInit, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser, CommonModule } from '@angular/common';
import { ContratistaApiService } from '../../../../services/contratista-api.service';
import { ReactiveFormsModule } from '@angular/forms';
import { FormsModule } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';
import { JwtService } from '../../../../services/jwt.service';

@Component({
  selector: 'app-administrar-clientes',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatTableModule,
    FormsModule
  ],
  templateUrl: './administrar-clientes.component.html',
  styleUrl: './administrar-clientes.component.css'
})
export class AdministrarClientesComponent implements OnInit {
  public modals: { [key: string]: boolean } = {
    exitoModal: false,
    errorModal: false,
    crearCliente: false,
    modificarCliente: false,
    confirmacionModal: false,
  };

  public clienteSeleccionado: any = {
    nombre_cliente_seleccionado: '',
    rut_cliente_seleccionado: '',
    direccion_cliente_seleccionado: '',
    comuna_cliente_seleccionado: '',
    giro_cliente_seleccionado: '',
    id_cliente_seleccionado: 0,
    nombre_rep_legal_seleccionado: '',
    direccion_rep_legal_seleccionado: '',
  };

  public usuarioIdNew = 0;
  public holding: string = '';
  public nombreCliente: string = '';
  public rutCliente: string = '';
  public direccionCliente: string = '';
  public comunaCliente: string = '';
  public giroCliente: string = '';
  public nombreRepresentanteLegal: string = '';
  public direccionRepresentanteLegal: string = '';
  public nuevoCampo: { nombre: string, direccion: string, comuna: string } = { nombre: '', direccion: '', comuna: '' };
  public campos: { nombre: string, direccion: string, comuna: string }[] = [];
  public camposNew: { id: number, nombre_campo: string, direccion_campo: string, comuna_campo: string }[] = [];
  public nuevosCampos: { nombre: string, direccion: string, comuna: string }[] = [];
  public camposAEliminar: number[] = [];
  
  errorMessage!: string;
  selectedRows: any[] = [];
  dropdownOpen: boolean = false;
  public todasSeleccionadas: boolean = false;
  public clientesCargados: any[] = [];
  columnasDesplegadas = ['rut', 'nombre', 'direccion', 'comuna', 'giro', 'campos_personalizados','nombre_rep'];

  public nombreClienteNew: string = '';
  public rutClienteNew: string = '';
  public direccionClienteNew: string = '';
  public comunaClienteNew: string = '';
  public giroClienteNew: string = '';
  public nombreRepresentanteLegalNew: string = '';
  public direccionRepresentanteLegalNew: string = '';
  
  public deletedRow: any[] = [];
  public selectedClienteId: number | null = null;

  // VARIABLES PARA BÚSQUEDA DE COMUNAS
  public comunasFiltradas: any[] = [];
  public searchComuna: string = '';
  public searchComunaNew: string = '';
  public dropdownComunaOpen: boolean = false;
  public dropdownComunaNewOpen: boolean = false;

  // COMUNAS DE CHILE HARDCODEADAS
  public todasLasComunas: any[] = [
    // Región de Arica y Parinacota
    { nombre: 'ARICA', region: 'ARICA Y PARINACOTA' },
    { nombre: 'CAMARONES', region: 'ARICA Y PARINACOTA' },
    { nombre: 'PUTRE', region: 'ARICA Y PARINACOTA' },
    { nombre: 'GENERAL LAGOS', region: 'ARICA Y PARINACOTA' },
    
    // Región de Tarapacá
    { nombre: 'IQUIQUE', region: 'TARAPACÁ' },
    { nombre: 'ALTO HOSPICIO', region: 'TARAPACÁ' },
    { nombre: 'POZO ALMONTE', region: 'TARAPACÁ' },
    { nombre: 'CAMIÑA', region: 'TARAPACÁ' },
    { nombre: 'COLCHANE', region: 'TARAPACÁ' },
    { nombre: 'HUARA', region: 'TARAPACÁ' },
    { nombre: 'PICA', region: 'TARAPACÁ' },
    
    // Región de Antofagasta
    { nombre: 'ANTOFAGASTA', region: 'ANTOFAGASTA' },
    { nombre: 'MEJILLONES', region: 'ANTOFAGASTA' },
    { nombre: 'SIERRA GORDA', region: 'ANTOFAGASTA' },
    { nombre: 'TALTAL', region: 'ANTOFAGASTA' },
    { nombre: 'CALAMA', region: 'ANTOFAGASTA' },
    { nombre: 'OLLAGÜE', region: 'ANTOFAGASTA' },
    { nombre: 'SAN PEDRO DE ATACAMA', region: 'ANTOFAGASTA' },
    { nombre: 'TOCOPILLA', region: 'ANTOFAGASTA' },
    { nombre: 'MARÍA ELENA', region: 'ANTOFAGASTA' },
    
    // Región de Atacama
    { nombre: 'COPIAPÓ', region: 'ATACAMA' },
    { nombre: 'CALDERA', region: 'ATACAMA' },
    { nombre: 'TIERRA AMARILLA', region: 'ATACAMA' },
    { nombre: 'CHAÑARAL', region: 'ATACAMA' },
    { nombre: 'DIEGO DE ALMAGRO', region: 'ATACAMA' },
    { nombre: 'VALLENAR', region: 'ATACAMA' },
    { nombre: 'ALTO DEL CARMEN', region: 'ATACAMA' },
    { nombre: 'FREIRINA', region: 'ATACAMA' },
    { nombre: 'HUASCO', region: 'ATACAMA' },
    
    // Región de Coquimbo
    { nombre: 'LA SERENA', region: 'COQUIMBO' },
    { nombre: 'COQUIMBO', region: 'COQUIMBO' },
    { nombre: 'ANDACOLLO', region: 'COQUIMBO' },
    { nombre: 'LA HIGUERA', region: 'COQUIMBO' },
    { nombre: 'PAIGUANO', region: 'COQUIMBO' },
    { nombre: 'VICUÑA', region: 'COQUIMBO' },
    { nombre: 'ILLAPEL', region: 'COQUIMBO' },
    { nombre: 'CANELA', region: 'COQUIMBO' },
    { nombre: 'LOS VILOS', region: 'COQUIMBO' },
    { nombre: 'SALAMANCA', region: 'COQUIMBO' },
    { nombre: 'OVALLE', region: 'COQUIMBO' },
    { nombre: 'COMBARBALÁ', region: 'COQUIMBO' },
    { nombre: 'MONTE PATRIA', region: 'COQUIMBO' },
    { nombre: 'PUNITAQUI', region: 'COQUIMBO' },
    { nombre: 'RÍO HURTADO', region: 'COQUIMBO' },
    
    // Región de Valparaíso
    { nombre: 'VALPARAÍSO', region: 'VALPARAÍSO' },
    { nombre: 'CASABLANCA', region: 'VALPARAÍSO' },
    { nombre: 'CONCÓN', region: 'VALPARAÍSO' },
    { nombre: 'JUAN FERNÁNDEZ', region: 'VALPARAÍSO' },
    { nombre: 'PUCHUNCAVÍ', region: 'VALPARAÍSO' },
    { nombre: 'QUINTERO', region: 'VALPARAÍSO' },
    { nombre: 'VIÑA DEL MAR', region: 'VALPARAÍSO' },
    { nombre: 'ISLA DE PASCUA', region: 'VALPARAÍSO' },
    { nombre: 'LOS ANDES', region: 'VALPARAÍSO' },
    { nombre: 'CALLE LARGA', region: 'VALPARAÍSO' },
    { nombre: 'RINCONADA', region: 'VALPARAÍSO' },
    { nombre: 'SAN ESTEBAN', region: 'VALPARAÍSO' },
    { nombre: 'LA LIGUA', region: 'VALPARAÍSO' },
    { nombre: 'CABILDO', region: 'VALPARAÍSO' },
    { nombre: 'PAPUDO', region: 'VALPARAÍSO' },
    { nombre: 'PETORCA', region: 'VALPARAÍSO' },
    { nombre: 'ZAPALLAR', region: 'VALPARAÍSO' },
    { nombre: 'QUILLOTA', region: 'VALPARAÍSO' },
    { nombre: 'CALERA', region: 'VALPARAÍSO' },
    { nombre: 'HIJUELAS', region: 'VALPARAÍSO' },
    { nombre: 'LA CRUZ', region: 'VALPARAÍSO' },
    { nombre: 'NOGALES', region: 'VALPARAÍSO' },
    { nombre: 'SAN ANTONIO', region: 'VALPARAÍSO' },
    { nombre: 'ALGARROBO', region: 'VALPARAÍSO' },
    { nombre: 'CARTAGENA', region: 'VALPARAÍSO' },
    { nombre: 'EL QUISCO', region: 'VALPARAÍSO' },
    { nombre: 'EL TABO', region: 'VALPARAÍSO' },
    { nombre: 'SANTO DOMINGO', region: 'VALPARAÍSO' },
    { nombre: 'SAN FELIPE', region: 'VALPARAÍSO' },
    { nombre: 'CATEMU', region: 'VALPARAÍSO' },
    { nombre: 'LLAILLAY', region: 'VALPARAÍSO' },
    { nombre: 'PANQUEHUE', region: 'VALPARAÍSO' },
    { nombre: 'PUTAENDO', region: 'VALPARAÍSO' },
    { nombre: 'SANTA MARÍA', region: 'VALPARAÍSO' },
    { nombre: 'QUILPUÉ', region: 'VALPARAÍSO' },
    { nombre: 'LIMACHE', region: 'VALPARAÍSO' },
    { nombre: 'OLMUÉ', region: 'VALPARAÍSO' },
    { nombre: 'VILLA ALEMANA', region: 'VALPARAÍSO' },
    
    // Región Metropolitana
    { nombre: 'SANTIAGO', region: 'METROPOLITANA' },
    { nombre: 'CERRILLOS', region: 'METROPOLITANA' },
    { nombre: 'CERRO NAVIA', region: 'METROPOLITANA' },
    { nombre: 'CONCHALÍ', region: 'METROPOLITANA' },
    { nombre: 'EL BOSQUE', region: 'METROPOLITANA' },
    { nombre: 'ESTACIÓN CENTRAL', region: 'METROPOLITANA' },
    { nombre: 'HUECHURABA', region: 'METROPOLITANA' },
    { nombre: 'INDEPENDENCIA', region: 'METROPOLITANA' },
    { nombre: 'LA CISTERNA', region: 'METROPOLITANA' },
    { nombre: 'LA FLORIDA', region: 'METROPOLITANA' },
    { nombre: 'LA GRANJA', region: 'METROPOLITANA' },
    { nombre: 'LA PINTANA', region: 'METROPOLITANA' },
    { nombre: 'LA REINA', region: 'METROPOLITANA' },
    { nombre: 'LAS CONDES', region: 'METROPOLITANA' },
    { nombre: 'LO BARNECHEA', region: 'METROPOLITANA' },
    { nombre: 'LO ESPEJO', region: 'METROPOLITANA' },
    { nombre: 'LO PRADO', region: 'METROPOLITANA' },
    { nombre: 'MACUL', region: 'METROPOLITANA' },
    { nombre: 'MAIPÚ', region: 'METROPOLITANA' },
    { nombre: 'ÑUÑOA', region: 'METROPOLITANA' },
    { nombre: 'PEDRO AGUIRRE CERDA', region: 'METROPOLITANA' },
    { nombre: 'PEÑALOLÉN', region: 'METROPOLITANA' },
    { nombre: 'PROVIDENCIA', region: 'METROPOLITANA' },
    { nombre: 'PUDAHUEL', region: 'METROPOLITANA' },
    { nombre: 'QUILICURA', region: 'METROPOLITANA' },
    { nombre: 'QUINTA NORMAL', region: 'METROPOLITANA' },
    { nombre: 'RECOLETA', region: 'METROPOLITANA' },
    { nombre: 'RENCA', region: 'METROPOLITANA' },
    { nombre: 'SAN JOAQUÍN', region: 'METROPOLITANA' },
    { nombre: 'SAN MIGUEL', region: 'METROPOLITANA' },
    { nombre: 'SAN RAMÓN', region: 'METROPOLITANA' },
    { nombre: 'VITACURA', region: 'METROPOLITANA' },
    { nombre: 'PUENTE ALTO', region: 'METROPOLITANA' },
    { nombre: 'PIRQUE', region: 'METROPOLITANA' },
    { nombre: 'SAN JOSÉ DE MAIPO', region: 'METROPOLITANA' },
    { nombre: 'COLINA', region: 'METROPOLITANA' },
    { nombre: 'LAMPA', region: 'METROPOLITANA' },
    { nombre: 'TILTIL', region: 'METROPOLITANA' },
    { nombre: 'SAN BERNARDO', region: 'METROPOLITANA' },
    { nombre: 'BUIN', region: 'METROPOLITANA' },
    { nombre: 'CALERA DE TANGO', region: 'METROPOLITANA' },
    { nombre: 'PAINE', region: 'METROPOLITANA' },
    { nombre: 'MELIPILLA', region: 'METROPOLITANA' },
    { nombre: 'ALHUÉ', region: 'METROPOLITANA' },
    { nombre: 'CURACAVÍ', region: 'METROPOLITANA' },
    { nombre: 'MARÍA PINTO', region: 'METROPOLITANA' },
    { nombre: 'SAN PEDRO', region: 'METROPOLITANA' },
    { nombre: 'TALAGANTE', region: 'METROPOLITANA' },
    { nombre: 'EL MONTE', region: 'METROPOLITANA' },
    { nombre: 'ISLA DE MAIPO', region: 'METROPOLITANA' },
    { nombre: 'PADRE HURTADO', region: 'METROPOLITANA' },
    { nombre: 'PEÑAFLOR', region: 'METROPOLITANA' },
    
    // Región del Libertador Bernardo O'Higgins
    { nombre: 'RANCAGUA', region: 'O\'HIGGINS' },
    { nombre: 'CODEGUA', region: 'O\'HIGGINS' },
    { nombre: 'COINCO', region: 'O\'HIGGINS' },
    { nombre: 'COLTAUCO', region: 'O\'HIGGINS' },
    { nombre: 'DOÑIHUE', region: 'O\'HIGGINS' },
    { nombre: 'GRANEROS', region: 'O\'HIGGINS' },
    { nombre: 'LAS CABRAS', region: 'O\'HIGGINS' },
    { nombre: 'MACHALÍ', region: 'O\'HIGGINS' },
    { nombre: 'MALLOA', region: 'O\'HIGGINS' },
    { nombre: 'MOSTAZAL', region: 'O\'HIGGINS' },
    { nombre: 'OLIVAR', region: 'O\'HIGGINS' },
    { nombre: 'PEUMO', region: 'O\'HIGGINS' },
    { nombre: 'PICHIDEGUA', region: 'O\'HIGGINS' },
    { nombre: 'QUINTA DE TILCOCO', region: 'O\'HIGGINS' },
    { nombre: 'RENGO', region: 'O\'HIGGINS' },
    { nombre: 'REQUÍNOA', region: 'O\'HIGGINS' },
    { nombre: 'SAN VICENTE', region: 'O\'HIGGINS' },
    { nombre: 'PICHILEMU', region: 'O\'HIGGINS' },
    { nombre: 'LA ESTRELLA', region: 'O\'HIGGINS' },
    { nombre: 'LITUECHE', region: 'O\'HIGGINS' },
    { nombre: 'MARCHIHUE', region: 'O\'HIGGINS' },
    { nombre: 'NAVIDAD', region: 'O\'HIGGINS' },
    { nombre: 'PAREDONES', region: 'O\'HIGGINS' },
    { nombre: 'SAN FERNANDO', region: 'O\'HIGGINS' },
    { nombre: 'CHÉPICA', region: 'O\'HIGGINS' },
    { nombre: 'CHIMBARONGO', region: 'O\'HIGGINS' },
    { nombre: 'LOLOL', region: 'O\'HIGGINS' },
    { nombre: 'NANCAGUA', region: 'O\'HIGGINS' },
    { nombre: 'PALMILLA', region: 'O\'HIGGINS' },
    { nombre: 'PERALILLO', region: 'O\'HIGGINS' },
    { nombre: 'PLACILLA', region: 'O\'HIGGINS' },
    { nombre: 'PUMANQUE', region: 'O\'HIGGINS' },
    { nombre: 'SANTA CRUZ', region: 'O\'HIGGINS' },
    
    // Región del Maule
    { nombre: 'TALCA', region: 'MAULE' },
    { nombre: 'CONSTITUCIÓN', region: 'MAULE' },
    { nombre: 'CUREPTO', region: 'MAULE' },
    { nombre: 'EMPEDRADO', region: 'MAULE' },
    { nombre: 'MAULE', region: 'MAULE' },
    { nombre: 'PELARCO', region: 'MAULE' },
    { nombre: 'PENCAHUE', region: 'MAULE' },
    { nombre: 'RÍO CLARO', region: 'MAULE' },
    { nombre: 'SAN CLEMENTE', region: 'MAULE' },
    { nombre: 'SAN RAFAEL', region: 'MAULE' },
    { nombre: 'CAUQUENES', region: 'MAULE' },
    { nombre: 'CHANCO', region: 'MAULE' },
    { nombre: 'PELLUHUE', region: 'MAULE' },
    { nombre: 'CURICÓ', region: 'MAULE' },
    { nombre: 'HUALAÑÉ', region: 'MAULE' },
    { nombre: 'LICANTÉN', region: 'MAULE' },
    { nombre: 'MOLINA', region: 'MAULE' },
    { nombre: 'RAUCO', region: 'MAULE' },
    { nombre: 'ROMERAL', region: 'MAULE' },
    { nombre: 'SAGRADA FAMILIA', region: 'MAULE' },
    { nombre: 'TENO', region: 'MAULE' },
    { nombre: 'VICHUQUÉN', region: 'MAULE' },
    { nombre: 'LINARES', region: 'MAULE' },
    { nombre: 'COLBÚN', region: 'MAULE' },
    { nombre: 'LONGAVÍ', region: 'MAULE' },
    { nombre: 'PARRAL', region: 'MAULE' },
    { nombre: 'RETIRO', region: 'MAULE' },
    { nombre: 'SAN JAVIER', region: 'MAULE' },
    { nombre: 'VILLA ALEGRE', region: 'MAULE' },
    { nombre: 'YERBAS BUENAS', region: 'MAULE' },
    
    // Región de Ñuble
    { nombre: 'CHILLÁN', region: 'ÑUBLE' },
    { nombre: 'BULNES', region: 'ÑUBLE' },
    { nombre: 'CHILLÁN VIEJO', region: 'ÑUBLE' },
    { nombre: 'EL CARMEN', region: 'ÑUBLE' },
    { nombre: 'PEMUCO', region: 'ÑUBLE' },
    { nombre: 'PINTO', region: 'ÑUBLE' },
    { nombre: 'QUILLÓN', region: 'ÑUBLE' },
    { nombre: 'SAN IGNACIO', region: 'ÑUBLE' },
    { nombre: 'YUNGAY', region: 'ÑUBLE' },
    { nombre: 'QUIRIHUE', region: 'ÑUBLE' },
    { nombre: 'COBQUECURA', region: 'ÑUBLE' },
    { nombre: 'COELEMU', region: 'ÑUBLE' },
    { nombre: 'NINHUE', region: 'ÑUBLE' },
    { nombre: 'PORTEZUELO', region: 'ÑUBLE' },
    { nombre: 'RANQUIL', region: 'ÑUBLE' },
    { nombre: 'TREGUACO', region: 'ÑUBLE' },
    { nombre: 'SAN CARLOS', region: 'ÑUBLE' },
    { nombre: 'COIHUECO', region: 'ÑUBLE' },
    { nombre: 'ÑIQUÉN', region: 'ÑUBLE' },
    { nombre: 'SAN FABIÁN', region: 'ÑUBLE' },
    { nombre: 'SAN NICOLÁS', region: 'ÑUBLE' },
    
    // Región del Biobío
    { nombre: 'CONCEPCIÓN', region: 'BIOBÍO' },
    { nombre: 'CORONEL', region: 'BIOBÍO' },
    { nombre: 'CHIGUAYANTE', region: 'BIOBÍO' },
    { nombre: 'FLORIDA', region: 'BIOBÍO' },
    { nombre: 'HUALQUI', region: 'BIOBÍO' },
    { nombre: 'LOTA', region: 'BIOBÍO' },
    { nombre: 'PENCO', region: 'BIOBÍO' },
    { nombre: 'SAN PEDRO DE LA PAZ', region: 'BIOBÍO' },
    { nombre: 'SANTA JUANA', region: 'BIOBÍO' },
    { nombre: 'TALCAHUANO', region: 'BIOBÍO' },
    { nombre: 'TOMÉ', region: 'BIOBÍO' },
    { nombre: 'HUALPÉN', region: 'BIOBÍO' },
    { nombre: 'LEBU', region: 'BIOBÍO' },
    { nombre: 'ARAUCO', region: 'BIOBÍO' },
    { nombre: 'CAÑETE', region: 'BIOBÍO' },
    { nombre: 'CONTULMO', region: 'BIOBÍO' },
    { nombre: 'CURANILAHUE', region: 'BIOBÍO' },
    { nombre: 'LOS ÁLAMOS', region: 'BIOBÍO' },
    { nombre: 'TIRÚA', region: 'BIOBÍO' },
    { nombre: 'LOS ÁNGELES', region: 'BIOBÍO' },
    { nombre: 'ANTUCO', region: 'BIOBÍO' },
    { nombre: 'CABRERO', region: 'BIOBÍO' },
    { nombre: 'LAJA', region: 'BIOBÍO' },
    { nombre: 'MULCHÉN', region: 'BIOBÍO' },
    { nombre: 'NACIMIENTO', region: 'BIOBÍO' },
    { nombre: 'NEGRETE', region: 'BIOBÍO' },
    { nombre: 'QUILACO', region: 'BIOBÍO' },
    { nombre: 'QUILLECO', region: 'BIOBÍO' },
    { nombre: 'SAN ROSENDO', region: 'BIOBÍO' },
    { nombre: 'SANTA BÁRBARA', region: 'BIOBÍO' },
    { nombre: 'TUCAPEL', region: 'BIOBÍO' },
    { nombre: 'YUMBEL', region: 'BIOBÍO' },
    { nombre: 'ALTO BIOBÍO', region: 'BIOBÍO' },
    
    // Región de La Araucanía
    { nombre: 'TEMUCO', region: 'ARAUCANÍA' },
    { nombre: 'CARAHUE', region: 'ARAUCANÍA' },
    { nombre: 'CUNCO', region: 'ARAUCANÍA' },
    { nombre: 'CURARREHUE', region: 'ARAUCANÍA' },
    { nombre: 'FREIRE', region: 'ARAUCANÍA' },
    { nombre: 'GALVARINO', region: 'ARAUCANÍA' },
    { nombre: 'GORBEA', region: 'ARAUCANÍA' },
    { nombre: 'LAUTARO', region: 'ARAUCANÍA' },
    { nombre: 'LONCOCHE', region: 'ARAUCANÍA' },
    { nombre: 'MELIPEUCO', region: 'ARAUCANÍA' },
    { nombre: 'NUEVA IMPERIAL', region: 'ARAUCANÍA' },
    { nombre: 'PADRE LAS CASAS', region: 'ARAUCANÍA' },
    { nombre: 'PERQUENCO', region: 'ARAUCANÍA' },
    { nombre: 'PITRUFQUÉN', region: 'ARAUCANÍA' },
    { nombre: 'PUCÓN', region: 'ARAUCANÍA' },
    { nombre: 'SAAVEDRA', region: 'ARAUCANÍA' },
    { nombre: 'TEODORO SCHMIDT', region: 'ARAUCANÍA' },
    { nombre: 'TOLTÉN', region: 'ARAUCANÍA' },
    { nombre: 'VILCÚN', region: 'ARAUCANÍA' },
    { nombre: 'VILLARRICA', region: 'ARAUCANÍA' },
    { nombre: 'CHOLCHOL', region: 'ARAUCANÍA' },
    { nombre: 'ANGOL', region: 'ARAUCANÍA' },
    { nombre: 'COLLIPULLI', region: 'ARAUCANÍA' },
    { nombre: 'CURACAUTÍN', region: 'ARAUCANÍA' },
    { nombre: 'ERCILLA', region: 'ARAUCANÍA' },
    { nombre: 'LONQUIMAY', region: 'ARAUCANÍA' },
    { nombre: 'LOS SAUCES', region: 'ARAUCANÍA' },
    { nombre: 'LUMACO', region: 'ARAUCANÍA' },
    { nombre: 'PURÉN', region: 'ARAUCANÍA' },
    { nombre: 'RENAICO', region: 'ARAUCANÍA' },
    { nombre: 'TRAIGUÉN', region: 'ARAUCANÍA' },
    { nombre: 'VICTORIA', region: 'ARAUCANÍA' },
    
    // Región de Los Ríos
    { nombre: 'VALDIVIA', region: 'LOS RÍOS' },
    { nombre: 'CORRAL', region: 'LOS RÍOS' },
    { nombre: 'LANCO', region: 'LOS RÍOS' },
    { nombre: 'LOS LAGOS', region: 'LOS RÍOS' },
    { nombre: 'MÁFIL', region: 'LOS RÍOS' },
    { nombre: 'MARIQUINA', region: 'LOS RÍOS' },
    { nombre: 'PAILLACO', region: 'LOS RÍOS' },
    { nombre: 'PANGUIPULLI', region: 'LOS RÍOS' },
    { nombre: 'LA UNIÓN', region: 'LOS RÍOS' },
    { nombre: 'FUTRONO', region: 'LOS RÍOS' },
    { nombre: 'LAGO RANCO', region: 'LOS RÍOS' },
    { nombre: 'RÍO BUENO', region: 'LOS RÍOS' },
    
    // Región de Los Lagos
    { nombre: 'PUERTO MONTT', region: 'LOS LAGOS' },
    { nombre: 'CALBUCO', region: 'LOS LAGOS' },
    { nombre: 'COCHAMÓ', region: 'LOS LAGOS' },
    { nombre: 'FRESIA', region: 'LOS LAGOS' },
    { nombre: 'FRUTILLAR', region: 'LOS LAGOS' },
    { nombre: 'LOS MUERMOS', region: 'LOS LAGOS' },
    { nombre: 'LLANQUIHUE', region: 'LOS LAGOS' },
    { nombre: 'MAULLÍN', region: 'LOS LAGOS' },
    { nombre: 'PUERTO VARAS', region: 'LOS LAGOS' },
    { nombre: 'CASTRO', region: 'LOS LAGOS' },
    { nombre: 'ANCUD', region: 'LOS LAGOS' },
    { nombre: 'CHONCHI', region: 'LOS LAGOS' },
    { nombre: 'CURACO DE VÉLEZ', region: 'LOS LAGOS' },
    { nombre: 'DALCAHUE', region: 'LOS LAGOS' },
    { nombre: 'PUQUELDÓN', region: 'LOS LAGOS' },
    { nombre: 'QUEILÉN', region: 'LOS LAGOS' },
    { nombre: 'QUELLÓN', region: 'LOS LAGOS' },
    { nombre: 'QUEMCHI', region: 'LOS LAGOS' },
    { nombre: 'QUINCHAO', region: 'LOS LAGOS' },
    { nombre: 'OSORNO', region: 'LOS LAGOS' },
    { nombre: 'PUERTO OCTAY', region: 'LOS LAGOS' },
    { nombre: 'PURRANQUE', region: 'LOS LAGOS' },
    { nombre: 'PUYEHUE', region: 'LOS LAGOS' },
    { nombre: 'RÍO NEGRO', region: 'LOS LAGOS' },
    { nombre: 'SAN JUAN DE LA COSTA', region: 'LOS LAGOS' },
    { nombre: 'SAN PABLO', region: 'LOS LAGOS' },
    { nombre: 'CHAITÉN', region: 'LOS LAGOS' },
    { nombre: 'FUTALEUFÚ', region: 'LOS LAGOS' },
    { nombre: 'HUALAIHUÉ', region: 'LOS LAGOS' },
    { nombre: 'PALENA', region: 'LOS LAGOS' },
    
    // Región de Aysén
    { nombre: 'COYHAIQUE', region: 'AYSÉN' },
    { nombre: 'LAGO VERDE', region: 'AYSÉN' },
    { nombre: 'AYSÉN', region: 'AYSÉN' },
    { nombre: 'CISNES', region: 'AYSÉN' },
    { nombre: 'GUAITECAS', region: 'AYSÉN' },
    { nombre: 'COCHRANE', region: 'AYSÉN' },
    { nombre: 'O\'HIGGINS', region: 'AYSÉN' },
    { nombre: 'TORTEL', region: 'AYSÉN' },
    { nombre: 'CHILE CHICO', region: 'AYSÉN' },
    { nombre: 'RÍO IBÁÑEZ', region: 'AYSÉN' },
    
    // Región de Magallanes
    { nombre: 'PUNTA ARENAS', region: 'MAGALLANES' },
    { nombre: 'LAGUNA BLANCA', region: 'MAGALLANES' },
    { nombre: 'RÍO VERDE', region: 'MAGALLANES' },
    { nombre: 'SAN GREGORIO', region: 'MAGALLANES' },
    { nombre: 'CABO DE HORNOS', region: 'MAGALLANES' },
    { nombre: 'ANTÁRTICA', region: 'MAGALLANES' },
    { nombre: 'PORVENIR', region: 'MAGALLANES' },
    { nombre: 'PRIMAVERA', region: 'MAGALLANES' },
    { nombre: 'TIMAUKEL', region: 'MAGALLANES' },
    { nombre: 'NATALES', region: 'MAGALLANES' },
    { nombre: 'TORRES DEL PAINE', region: 'MAGALLANES' }
  ];

  constructor(
    private apiService: ContratistaApiService,
    private jwtService: JwtService,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {}

  ngOnInit(): void {
    if (isPlatformBrowser(this.platformId)) {
      this.holding = this.getHoldingIdFromJWT();
      this.cargarClientes();
      this.comunasFiltradas = this.todasLasComunas;
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
  
  crearCliente(): void {
    let data = {
      holding: this.holding,
      nombre: this.nombreCliente,
      rut: this.rutCliente.replace(/[\.\-]/g, ''),
      direccion: this.direccionCliente,
      comuna_cliente: this.comunaCliente,
      giro: this.giroCliente,
      nombre_rep_legal: this.nombreRepresentanteLegal,
      direccion_rep_legal: this.direccionRepresentanteLegal,
    };
    this.apiService.post('api_clientes/', data).subscribe({
      next: (response) => {
        this.crearCampos(response.id);
        this.cargarClientes();
        this.closeModal('crearCliente');
        this.openModal('exitoModal');
        this.limpiarFormularioCrear();
      },
      error: (error) => {
        this.openModal('errorModal');
      }
    });
  }

  limpiarFormularioCrear(): void {
    this.nombreCliente = '';
    this.rutCliente = '';
    this.direccionCliente = '';
    this.comunaCliente = '';
    this.searchComuna = '';
    this.giroCliente = '';
    this.nombreRepresentanteLegal = '';
    this.direccionRepresentanteLegal = '';
    this.campos = [];
    this.nuevoCampo = { nombre: '', direccion: '', comuna: '' };
    this.dropdownComunaOpen = false;
  }

  crearCampos(clienteId: number): void {
    for (let campo of this.campos) {
      let campoData = {
        holding: this.holding,
        cliente: clienteId,
        nombre_campo: campo.nombre,
        direccion_campo: campo.direccion,
        comuna_campo: campo.comuna
      };
      this.apiService.post('api_campos_clientes/', campoData).subscribe({
        next: (response) => {
          console.log('Campo creado:', response);
        },
        error: (error) => {
          console.error('Error al crear campo:', error);
          this.openModal('errorModal');
        }
      });
    }
    this.campos = [];
  }

  cargarClientes(): void {
    this.apiService.get(`api_clientes/?holding=${this.holding}`).subscribe({
      next: (response) => {
        this.clientesCargados = response;
      },
      error: (error) => {
        console.error('Error al recibir las sociedades:', error);
      }
    });
  }

  cargarCampos(clienteId: number): void {
    this.apiService.get(`api_campos_clientes/${clienteId}`).subscribe({
      next: (response) => {
        console.log(response)
        this.camposNew = response; 
      },
      error: (error) => {
        console.error('Error al cargar campos personalizados:', error);
      }
    });
  }

  modificarCliente(): void {
    // 1. Eliminar campos marcados
    if (this.camposAEliminar.length > 0) {
      this.apiService.delete('api_campos_clientes/', { ids: this.camposAEliminar }).subscribe();
    }

    // 2. Crear nuevos campos
    for (let campo of this.nuevosCampos) {
      let campoData = {
        holding: this.holding,
        cliente: this.selectedClienteId,
        nombre_campo: campo.nombre,
        direccion_campo: campo.direccion,
        comuna_campo: campo.comuna
      };
      this.apiService.post('api_campos_clientes/', campoData).subscribe();
    }

    // 3. Actualizar cliente y campos existentes
    let data = {
      holding: this.holding,
      id: this.selectedClienteId,
      nombre: this.nombreClienteNew,
      rut: this.rutClienteNew.replace(/[\.\-]/g, ''),
      direccion: this.direccionClienteNew,
      comuna_cliente: this.comunaClienteNew,
      giro: this.giroClienteNew,
      nombre_rep_legal: this.nombreRepresentanteLegalNew,
      direccion_rep_legal: this.direccionRepresentanteLegalNew,
      camposPersonalizados: this.camposNew.filter(c => !this.camposAEliminar.includes(c.id))
    };
    
    this.apiService.put('api_clientes/', data).subscribe({
      next: (response) => {
        this.closeModal('modificarCliente');
        this.cargarClientes();
        this.openModal('exitoModal');
        this.nuevosCampos = [];
        this.camposAEliminar = [];
      },
      error: (error) => {
        this.openModal('errorModal');
      }
    });
  }

  agregarCampoNuevo(): void {
    if (this.nuevoCampo.nombre.trim() && this.nuevoCampo.direccion.trim() && this.nuevoCampo.comuna.trim()) {
      this.nuevosCampos.push({ ...this.nuevoCampo });
      this.nuevoCampo = { nombre: '', direccion: '', comuna: '' };
    }
  }

  marcarCampoParaEliminar(campoId: number): void {
    this.camposAEliminar.push(campoId);
    this.camposNew = this.camposNew.filter(c => c.id !== campoId);
  }

  eliminarCampoNuevo(index: number): void {
    this.nuevosCampos.splice(index, 1);
  }

  eliminarClientesSeleccionados(): void {
    if (this.deletedRow.length > 0) {
      const idsToDelete = this.deletedRow.map(row => row.id);
      this.apiService.delete('api_clientes/', { ids: idsToDelete }).subscribe({
        next: () => {
          this.closeModal('confirmacionModal');
          this.cargarClientes();
          this.openModal('exitoModal');
          this.deletedRow = [];
        },
        error: (error) => {
          this.openModal('errorModal');
          console.error('Error al eliminar clientes:', error);
        }
      });
    }
  }

  agregarCampo(): void {
    if (this.nuevoCampo.nombre.trim() && this.nuevoCampo.direccion.trim() && this.nuevoCampo.comuna.trim()) {
      this.campos.push({ ...this.nuevoCampo });
      this.nuevoCampo = { nombre: '', direccion: '', comuna: '' };
    }
  }

  eliminarCampo(index: number): void {
    this.campos.splice(index, 1);
  }

  toggleSelection(clienteId: number): void {
    if (this.selectedClienteId === clienteId) {
      this.selectedClienteId = null;
    } else {
      this.selectedClienteId = clienteId;
    }
  }

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

    if (this.selectedRows.length > 0) {
      const lastSelectedRow = this.selectedRows[this.selectedRows.length - 1];
      this.clienteSeleccionado = {
        nombre_cliente_seleccionado: lastSelectedRow.nombre,
        rut_cliente_seleccionado: lastSelectedRow.rut,
        direccion_cliente_seleccionado: lastSelectedRow.direccion,
        comuna_cliente_seleccionado: lastSelectedRow.comuna_cliente || '',
        giro_cliente_seleccionado: lastSelectedRow.giro,
        id_cliente_seleccionado: lastSelectedRow.id,
        nombre_rep_legal_seleccionado: lastSelectedRow.nombre_rep_legal || '',
        direccion_rep_legal_seleccionado: lastSelectedRow.direccion_rep_legal || '',
      };
      
      this.selectedClienteId = this.clienteSeleccionado.id_cliente_seleccionado;
      this.nombreClienteNew = this.clienteSeleccionado.nombre_cliente_seleccionado;
      this.rutClienteNew = this.formatRUTString(this.clienteSeleccionado.rut_cliente_seleccionado);
      this.direccionClienteNew = this.clienteSeleccionado.direccion_cliente_seleccionado;
      this.comunaClienteNew = this.clienteSeleccionado.comuna_cliente_seleccionado;
      this.searchComunaNew = this.clienteSeleccionado.comuna_cliente_seleccionado;
      this.giroClienteNew = this.clienteSeleccionado.giro_cliente_seleccionado;
      this.nombreRepresentanteLegalNew = this.clienteSeleccionado.nombre_rep_legal_seleccionado;
      this.direccionRepresentanteLegalNew = this.clienteSeleccionado.direccion_rep_legal_seleccionado;

      this.cargarCampos(this.selectedClienteId!);
    } else {
      this.clienteSeleccionado = {
        nombre_cliente_seleccionado: '',
        rut_cliente_seleccionado: '',
        direccion_cliente_seleccionado: '',
        comuna_cliente_seleccionado: '',
        giro_cliente_seleccionado: '',
        nombre_rep_legal_seleccionado: '',
        direccion_rep_legal_seleccionado: '',
      };
    }
  }

  // FUNCIONES PARA COMUNAS
  filtrarComunas(searchTerm: string, isNew: boolean = false): void {
    const term = searchTerm.toLowerCase();
    this.comunasFiltradas = this.todasLasComunas.filter(comuna =>
      comuna.nombre.toLowerCase().includes(term) ||
      comuna.region.toLowerCase().includes(term)
    );
    
    if (isNew) {
      this.dropdownComunaNewOpen = true;
    } else {
      this.dropdownComunaOpen = true;
    }
  }

  seleccionarComuna(comuna: any, isNew: boolean = false): void {
    if (isNew) {
      this.comunaClienteNew = comuna.nombre;
      this.searchComunaNew = comuna.nombre;
      this.dropdownComunaNewOpen = false;
    } else {
      this.comunaCliente = comuna.nombre;
      this.searchComuna = comuna.nombre;
      this.dropdownComunaOpen = false;
    }
  }

  formatRUT(event: Event): void {
    const target = event.target as HTMLInputElement;
    if (!target) return;

    let rut = target.value.replace(/[^0-9kK]/g, '').toUpperCase();
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
    this.selectedRows = [];
  }

  openModal(key: string): void {
    this.modals[key] = true;
    if (key == 'confirmacionModal') {
      this.deletedRow = this.selectedRows;
      console.log(this.deletedRow);
    }
  }

  closeModal(key: string): void {
    this.modals[key] = false;
    if (key === 'exitoModal') {
      this.cargarClientes();
    }
  }
}