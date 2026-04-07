import logging
import re

from django.db import transaction
from rest_framework import status
from rest_framework.response import Response

from .base import BaseAPIView
from ..models import (
    AFPTrabajadores,
    AreasAdministracion,
    CargosAdministracion,
    Holding,
    ModulosMovil,
    ModulosWeb,
    Perfiles,
    PersonalTrabajadores,
    SaludTrabajadores,
    Sociedad,
    SubModulosMovil,
    SubModulosWeb,
    Usuarios,
)
from ..serializers import (
    AdminSerializer,
    HoldingSerializer,
    ModulosMovilSerializer,
    ModulosWebSerializer,
    PerfilesSerializer,
    SociedadCuentaSerializer,
    SociedadSerializer,
    SubModulosMovilSerializer,
    SubModulosWebSerializer,
    AreaAdministracionSerializer,
    CargoAdministracionSerializer,
)

logger = logging.getLogger('contratista_test_app')


# ==============================================================================
# HOLDING
# ==============================================================================

class HoldingAPIView(BaseAPIView):
    required_scopes = ['superadmin_access']

    def get(self, request, format=None):
        holdings = Holding.objects.all()
        return Response(HoldingSerializer(holdings, many=True).data)

    def post(self, request, format=None):
        serializer = HoldingSerializer(data=request.data)
        if serializer.is_valid():
            holding = serializer.save()
            self._crear_modulos_defecto(holding)
            logger.debug(f'HoldingAPIView POST: holding {holding.id} creado')
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        logger.error(f'HoldingAPIView POST: datos inválidos: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, format=None):
        holding_id = request.data.get('id')
        if not holding_id:
            return Response(
                {'message': 'ID de holding es necesario para actualizar'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            holding = Holding.objects.get(id=holding_id)
        except Holding.DoesNotExist:
            logger.error(f'HoldingAPIView PUT: holding {holding_id} no encontrado')
            return Response({'message': 'Holding no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        serializer = HoldingSerializer(holding, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        logger.error(f'HoldingAPIView PUT: datos inválidos para holding {holding_id}: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, format=None):
        holding_id = request.data.get('id')
        if not holding_id:
            return Response(
                {'message': 'ID de holding es necesario para actualizar'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            holding = Holding.objects.get(id=holding_id)
        except Holding.DoesNotExist:
            logger.error(f'HoldingAPIView PATCH: holding {holding_id} no encontrado')
            return Response({'message': 'Holding no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        serializer = HoldingSerializer(holding, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        logger.error(f'HoldingAPIView PATCH: datos inválidos para holding {holding_id}: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, format=None):
        holding_ids = request.data.get('ids', [])
        if not holding_ids:
            return Response(
                {'message': 'IDs de holdings son necesarios para eliminar'},
                status=status.HTTP_400_BAD_REQUEST
            )

        Holding.objects.filter(id__in=holding_ids).update(estado=False)
        logger.debug(f'HoldingAPIView DELETE: {len(holding_ids)} holdings desactivados')
        return Response(
            {'message': f'{len(holding_ids)} holdings desactivados exitosamente'},
            status=status.HTTP_200_OK
        )

    def _crear_modulos_defecto(self, holding):
        perfiles_defecto = [
            {'nombre_perfil': 'ADMINISTRADOR PRINCIPAL', 'tipo': 'AMBOS'},
            {'nombre_perfil': 'SUPERVISOR', 'tipo': 'MOVIL'},
            {'nombre_perfil': 'JEFE DE CUADRILLA', 'tipo': 'MOVIL'},
        ]
        for perfil_data in perfiles_defecto:
            Perfiles.objects.get_or_create(
                holding=holding,
                nombre_perfil=perfil_data['nombre_perfil'],
                defaults={'tipo': perfil_data['tipo'], 'estado': True}
            )

        modulos_web = [
            ('ADMINISTRACION', [
                'PERSONAL', 'PERFILES', 'USUARIOS', 'AREAS/CARGOS ADMINISTRACION',
                'PARAMETROS ADMINISTRACION', 'SOCIEDADES', 'AFP', 'SALUD',
            ]),
            ('RECURSOS HUMANOS', [
                'CONTRATACION PERSONAL', 'CREAR CONTRATO', 'CONTRATOS FIRMADOS',
                'MAESTRO TRABAJADORES', 'PARAMETROS RECURSOS HUMANOS', 'GENERAR CODIGOS QR',
                'FORMATOS', 'LIBRO DE REMUNERACIONES ELECTRONICO', 'CASAS', 'HORARIOS',
                'PARAMETROS RH', 'GENERACION CONTRATOS',
            ]),
            ('CLIENTES', [
                'ADMINISTRAR CLIENTES', 'AREA/CARGOS CLIENTES', 'CONTACTOS',
                'PARAMETROS CLIENTES',
            ]),
            ('COMERCIAL', [
                'ACUERDO COMERCIAL', 'PARAMETROS COMERCIAL', 'UNIDAD DE CONTROL', 'LABORES',
            ]),
            ('TRANSPORTE', [
                'TRANSPORTISTAS', 'VEHICULOS', 'CHOFERES', 'TRAMOS', 'ACUERDO TRANSPORTES',
                'PAGO TRANSPORTISTA', 'PROFORMA', 'PARAMETROS TRANSPORTE',
            ]),
            ('PAGOS', [
                'TRANSFERENCIA', 'EFECTIVO', 'PAGOS REALIZADOS', 'REPROCESAR PAGO',
            ]),
            ('INFORMES', [
                'INFORME RENDIMIENTO', 'INFORME PAGO', 'INFORME TRANSPORTISTA',
            ]),
            ('LEYES SOCIALES', [
                'INFORME DIAS TRABAJADOS', 'HABERES DESCUENTOS', 'ARCHIVO PREVIRED',
                'LIQUIDACIONES', 'ASIGNACION HABERES', 'ASIGNACION DESCUENTOS',
                'PARAMETROS LEYES SOCIALES',
            ]),
            ('COSTOS', [
                'FACTURAS COMPRA AUTOMATICO', 'FACTURAS COMPRA DISTRIBUIDAS',
                'PARAMETROS FACTURA COMPRA', 'FACTURAS VENTA AUTOMATICO',
                'FACTURAS VENTA DISTRIBUIDAS', 'PARAMETROS FACTURA VENTA',
                'CUENTAS', 'PARAMETROS COSTOS', 'FACTURAS COMPRAS', 'FACTURAS VENTAS',
            ]),
            ('TESORERIA', [
                'PAGOS INGRESOS', 'PAGOS EGRESOS', 'HISTORIAL PAGOS',
            ]),
        ]

        for modulo_nombre, submodulos in modulos_web:
            modulo = ModulosWeb.objects.create(nombre=modulo_nombre, holding=holding)
            for sub in submodulos:
                SubModulosWeb.objects.create(nombre=sub, holding=holding, modulo=modulo)

        modulos_movil = [
            ('GESTION TRABAJADORES', ['ENROLLAR TRABAJADOR', 'ASIGNAR QR']),
            ('MANO DE OBRA', [
                'INGRESAR RENDIMIENTO PERSONA MANO OBRA', 'INFORMES PERSONA MANO OBRA',
                'INGRESAR RENDIMIENTO CUADRILLA MANO OBRA', 'INFORMES CUADRILLA MANO OBRA',
            ]),
            ('COSECHA', [
                'INGRESAR RENDIMIENTO PERSONA COSECHA', 'INFORMES PERSONA COSECHA',
                'INGRESAR RENDIMIENTO CUADRILLA COSECHA', 'INFORMES CUADRILLA COSECHA',
            ]),
        ]

        for modulo_nombre, submodulos in modulos_movil:
            modulo = ModulosMovil.objects.create(nombre=modulo_nombre, holding=holding)
            for sub in submodulos:
                SubModulosMovil.objects.create(nombre=sub, holding=holding, modulo=modulo)

        afps_defecto = [
            {'codigo': 0,  'nombre': 'NO ESTÁ EN AFP', 'cotizacion': 0.00,  'comision': 0.00, 'cargo_empleador': 0.00, 'seguro_social': 0.00},
            {'codigo': 3,  'nombre': 'CUPRUM',          'cotizacion': 10.00, 'comision': 1.44, 'cargo_empleador': 0.10, 'seguro_social': 0.90},
            {'codigo': 5,  'nombre': 'HABITAT',         'cotizacion': 10.00, 'comision': 1.27, 'cargo_empleador': 0.10, 'seguro_social': 0.90},
            {'codigo': 8,  'nombre': 'PROVIDA',         'cotizacion': 10.00, 'comision': 1.45, 'cargo_empleador': 0.10, 'seguro_social': 0.90},
            {'codigo': 29, 'nombre': 'PLANVITAL',       'cotizacion': 10.00, 'comision': 1.16, 'cargo_empleador': 0.10, 'seguro_social': 0.90},
            {'codigo': 33, 'nombre': 'CAPITAL',         'cotizacion': 10.00, 'comision': 1.44, 'cargo_empleador': 0.10, 'seguro_social': 0.90},
            {'codigo': 34, 'nombre': 'MODELO',          'cotizacion': 10.00, 'comision': 0.58, 'cargo_empleador': 0.10, 'seguro_social': 0.90},
            {'codigo': 35, 'nombre': 'UNO',             'cotizacion': 10.00, 'comision': 0.49, 'cargo_empleador': 0.10, 'seguro_social': 0.90},
        ]

        for afp in afps_defecto:
            AFPTrabajadores.objects.get_or_create(
                holding=holding,
                codigo=afp['codigo'],
                defaults={
                    'nombre': afp['nombre'],
                    'porcentaje_cotizacion_individual': afp['cotizacion'],
                    'comision_afp': afp['comision'],
                    'porcentaje_cargo_empleador': afp['cargo_empleador'],
                    'porcentaje_seguro_social': afp['seguro_social'],
                }
            )

        salud_defecto = [
            {'codigo': 0,  'nombre': 'SIN ISAPRE',              'porcentaje': 7.00},
            {'codigo': 1,  'nombre': 'BANMEDICA',               'porcentaje': 7.00},
            {'codigo': 2,  'nombre': 'CONSALUD',                'porcentaje': 7.00},
            {'codigo': 3,  'nombre': 'VIDATRES',                'porcentaje': 7.00},
            {'codigo': 4,  'nombre': 'COLMENA',                 'porcentaje': 7.00},
            {'codigo': 5,  'nombre': 'ISAPRE CRUZ BLANCA S.A.', 'porcentaje': 7.00},
            {'codigo': 7,  'nombre': 'FONASA',                  'porcentaje': 7.00},
            {'codigo': 10, 'nombre': 'NUEVA MASVIDA',           'porcentaje': 7.00},
            {'codigo': 11, 'nombre': 'ISAPRE DE CODELCO LTDA.', 'porcentaje': 7.00},
            {'codigo': 12, 'nombre': 'ISAPRE BCO. ESTADO',      'porcentaje': 7.00},
            {'codigo': 25, 'nombre': 'CRUZ DEL NORTE',          'porcentaje': 7.00},
        ]

        for salud in salud_defecto:
            SaludTrabajadores.objects.get_or_create(
                holding=holding,
                codigo=salud['codigo'],
                defaults={'nombre': salud['nombre'], 'porcentaje': salud['porcentaje']}
            )

        logger.debug(f'_crear_modulos_defecto: completado para holding {holding.id}')


# ==============================================================================
# SOCIEDAD
# ==============================================================================

class SociedadAPIView(BaseAPIView):
    required_scopes = ['superadmin_access', 'admin', 'write']

    def get(self, request, holding_id=None, format=None):
        if holding_id:
            sociedades = Sociedad.objects.filter(holding_id=holding_id)
        else:
            sociedades = Sociedad.objects.all()
        return Response(SociedadSerializer(sociedades, many=True).data)

    def post(self, request, format=None):
        serializer = SociedadSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.debug(f'SociedadAPIView POST: sociedad {serializer.data.get("id")} creada')
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        logger.error(f'SociedadAPIView POST: datos inválidos: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, format=None):
        sociedad_id = request.data.get('id')
        if not sociedad_id:
            return Response(
                {'message': 'ID de sociedad es necesario para actualizar'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            sociedad = Sociedad.objects.get(id=sociedad_id)
        except Sociedad.DoesNotExist:
            logger.error(f'SociedadAPIView PUT: sociedad {sociedad_id} no encontrada')
            return Response({'message': 'Sociedad no encontrada'}, status=status.HTTP_404_NOT_FOUND)

        serializer = SociedadSerializer(sociedad, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        logger.error(f'SociedadAPIView PUT: datos inválidos para sociedad {sociedad_id}: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, format=None):
        sociedad_id = request.data.get('id')
        if not sociedad_id:
            return Response(
                {'message': 'ID de sociedad es necesario para actualizar'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            sociedad = Sociedad.objects.get(id=sociedad_id)
        except Sociedad.DoesNotExist:
            logger.error(f'SociedadAPIView PATCH: sociedad {sociedad_id} no encontrada')
            return Response({'message': 'Sociedad no encontrada'}, status=status.HTTP_404_NOT_FOUND)

        serializer = SociedadSerializer(sociedad, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        logger.error(f'SociedadAPIView PATCH: datos inválidos para sociedad {sociedad_id}: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, format=None):
        sociedad_ids = request.data.get('ids', [])
        if not sociedad_ids:
            return Response(
                {'message': 'IDs de sociedades son necesarios para eliminar'},
                status=status.HTTP_400_BAD_REQUEST
            )

        Sociedad.objects.filter(id__in=sociedad_ids).update(estado=False)
        logger.debug(f'SociedadAPIView DELETE: {len(sociedad_ids)} sociedades desactivadas')
        return Response(
            {'message': f'{len(sociedad_ids)} sociedades desactivadas exitosamente'},
            status=status.HTTP_200_OK
        )


class SociedadDetailAPIView(BaseAPIView):

    def get(self, request, holding_id):
        sociedades = Sociedad.objects.filter(holding_id=holding_id)
        return Response(SociedadCuentaSerializer(sociedades, many=True).data)

    def patch(self, request, holding_id, sociedad_id):
        try:
            sociedad = Sociedad.objects.get(holding_id=holding_id, id=sociedad_id)
        except Sociedad.DoesNotExist:
            logger.error(f'SociedadDetailAPIView PATCH: sociedad {sociedad_id} no encontrada en holding {holding_id}')
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = SociedadCuentaSerializer(sociedad, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        logger.error(f'SociedadDetailAPIView PATCH: datos inválidos: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SociedadesUsuarioAPIView(BaseAPIView):
    required_scopes = ['admin', 'write', 'read']

    def get(self, request, usuario_id, format=None):
        try:
            usuario = Usuarios.objects.get(id=usuario_id)
        except Usuarios.DoesNotExist:
            logger.error(f'SociedadesUsuarioAPIView GET: usuario {usuario_id} no encontrado')
            return Response({'message': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f'SociedadesUsuarioAPIView GET: error para usuario {usuario_id}: {e}', exc_info=True)
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        sociedades_data = [
            {'id': s.id, 'nombre': s.nombre, 'rut': s.rol_sociedad}
            for s in usuario.empresas_asignadas.all()
        ]
        return Response({'usuario_id': usuario_id, 'sociedades': sociedades_data}, status=status.HTTP_200_OK)


# ==============================================================================
# ADMIN (USUARIOS ADMINISTRADORES)
# ==============================================================================

class AdminAPIView(BaseAPIView):

    def dispatch(self, request, *args, **kwargs):
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            self.required_scopes = ['superadmin_access']
        else:
            self.required_scopes = ['superadmin_access', 'admin', 'write']
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        admins = Usuarios.objects.filter(is_admin=True).select_related('holding', 'persona')
        logger.debug(f'AdminAPIView GET: {admins.count()} administradores retornados')
        return Response(AdminSerializer(admins, many=True).data)

    def post(self, request):
        data = request.data

        try:
            with transaction.atomic():
                holding_id = data.get('holding')
                rut_limpio = re.sub(r'[^0-9kK]', '', data.get('rut', ''))

                area_admin, _ = AreasAdministracion.objects.get_or_create(
                    holding_id=holding_id,
                    nombre='ADMINISTRACION',
                    defaults={'nombre': 'ADMINISTRACION'}
                )
                cargo_admin, _ = CargosAdministracion.objects.get_or_create(
                    holding_id=holding_id,
                    area=area_admin,
                    nombre='ADMINISTRADOR PRINCIPAL',
                    defaults={'nombre': 'ADMINISTRADOR PRINCIPAL', 'area': area_admin}
                )

                if PersonalTrabajadores.objects.filter(rut=rut_limpio).exists():
                    return Response(
                        {'message': f'Ya existe una persona con RUT {data.get("rut")}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                persona = PersonalTrabajadores.objects.create(
                    holding_id=holding_id,
                    nombres=data.get('nombre', '').upper(),
                    rut=rut_limpio,
                    cargo=cargo_admin,
                    area=area_admin,
                    estado=True
                )

                perfil, _ = Perfiles.objects.get_or_create(
                    holding_id=holding_id,
                    nombre_perfil='ADMINISTRADOR PRINCIPAL',
                    defaults={'tipo': 'AMBOS', 'estado': True}
                )
                perfil.modulos_web.set(ModulosWeb.objects.filter(holding_id=holding_id))
                perfil.submodulos_web.set(SubModulosWeb.objects.filter(holding_id=holding_id))

                if Usuarios.objects.filter(holding_id=holding_id, is_admin=True).exists():
                    persona.delete()
                    return Response(
                        {'message': 'Ya existe un administrador principal para este holding'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                if Usuarios.objects.filter(email=data.get('email')).exists():
                    persona.delete()
                    return Response(
                        {'message': f'Ya existe un usuario con email {data.get("email")}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                if Usuarios.objects.filter(rut=rut_limpio).exists():
                    persona.delete()
                    return Response(
                        {'message': f'Ya existe un usuario con RUT {data.get("rut")}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                admin = Usuarios.objects.create(
                    holding_id=holding_id,
                    persona=persona,
                    rut=rut_limpio,
                    email=data.get('email'),
                    perfil=perfil,
                    is_admin=True,
                    estado=True
                )

                if data.get('password'):
                    admin.set_password(data.get('password'))
                    admin.save()

                logger.debug(f'AdminAPIView POST: admin {admin.id} creado en holding {holding_id}')
                return Response(AdminSerializer(admin).data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f'AdminAPIView POST: error creando administrador: {e}', exc_info=True)
            return Response(
                {'message': f'Error al crear administrador: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    def _actualizar_admin(self, admin, data):
        if 'email' in data:
            admin.email = data['email']
        if 'estado' in data:
            admin.estado = data['estado']
        if data.get('password', '').strip():
            admin.set_password(data['password'])
        if admin.persona and 'nombre' in data:
            admin.persona.nombres = data['nombre'].upper()
            admin.persona.save()
        admin.save()

    def put(self, request, format=None):
        admin_id = request.data.get('id')
        if not admin_id:
            return Response(
                {'message': 'ID de administrador es necesario para actualizar'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            admin = Usuarios.objects.get(id=admin_id, is_admin=True)
        except Usuarios.DoesNotExist:
            logger.error(f'AdminAPIView PUT: admin {admin_id} no encontrado')
            return Response({'message': 'Administrador no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        self._actualizar_admin(admin, request.data)
        logger.debug(f'AdminAPIView PUT: admin {admin_id} actualizado')
        return Response(AdminSerializer(admin).data)

    def patch(self, request, format=None):
        admin_id = request.data.get('id')
        if not admin_id:
            return Response(
                {'message': 'ID de administrador es necesario para actualizar'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            admin = Usuarios.objects.get(id=admin_id, is_admin=True)
        except Usuarios.DoesNotExist:
            logger.error(f'AdminAPIView PATCH: admin {admin_id} no encontrado')
            return Response({'message': 'Administrador no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        self._actualizar_admin(admin, request.data)
        logger.debug(f'AdminAPIView PATCH: admin {admin_id} actualizado')
        return Response(AdminSerializer(admin).data)

    def delete(self, request, format=None):
        admin_ids = request.data.get('ids', [])
        if not admin_ids:
            return Response(
                {'message': 'IDs de administradores son necesarios para desactivar'},
                status=status.HTTP_400_BAD_REQUEST
            )

        admins = Usuarios.objects.filter(id__in=admin_ids, is_admin=True)
        count = 0
        for admin in admins:
            admin.estado = False
            admin.save()
            if admin.persona:
                admin.persona.estado = False
                admin.persona.save()
            count += 1

        logger.debug(f'AdminAPIView DELETE: {count} administradores desactivados')
        return Response(
            {'message': f'{count} administradores desactivados exitosamente'},
            status=status.HTTP_200_OK
        )


# ==============================================================================
# MÓDULOS WEB / MÓVIL
# ==============================================================================

class ModulosWebAPIView(BaseAPIView):

    def get(self, request, holding_id):
        modulos = ModulosWeb.objects.filter(holding_id=holding_id)
        return Response(ModulosWebSerializer(modulos, many=True).data, status=status.HTTP_200_OK)


class SubModulosWebAPIView(BaseAPIView):

    def get(self, request, holding_id):
        submodulos = SubModulosWeb.objects.filter(holding_id=holding_id)
        return Response(SubModulosWebSerializer(submodulos, many=True).data, status=status.HTTP_200_OK)


class ModulosMovilAPIView(BaseAPIView):

    def get(self, request, holding_id):
        modulos = ModulosMovil.objects.filter(holding_id=holding_id)
        return Response(ModulosMovilSerializer(modulos, many=True).data, status=status.HTTP_200_OK)


class SubModulosMovilAPIView(BaseAPIView):

    def get(self, request, holding_id):
        submodulos = SubModulosMovil.objects.filter(holding_id=holding_id)
        return Response(SubModulosMovilSerializer(submodulos, many=True).data, status=status.HTTP_200_OK)


# ==============================================================================
# PERFILES
# ==============================================================================

class PerfilesAPIView(BaseAPIView):

    def get(self, request, holding_id):
        perfiles = Perfiles.objects.filter(
            holding_id=holding_id
        ).exclude(nombre_perfil='ADMINISTRADOR PRINCIPAL')
        return Response(PerfilesSerializer(perfiles, many=True).data, status=status.HTTP_200_OK)

    def post(self, request, holding_id):
        data = request.data

        try:
            with transaction.atomic():
                perfil = Perfiles.objects.create(
                    holding_id=holding_id,
                    nombre_perfil=data.get('nombre_perfil'),
                    tipo=data.get('tipo'),
                    estado=data.get('estado', True)
                )

                tipo = data.get('tipo')

                if tipo in ['WEB', 'AMBOS']:
                    perfil.modulos_web.add(*ModulosWeb.objects.filter(id__in=data.get('modulos_web', [])))
                    perfil.submodulos_web.add(*SubModulosWeb.objects.filter(id__in=data.get('submodulos_web', [])))

                if tipo in ['MOVIL', 'AMBOS']:
                    perfil.modulos_movil.add(*ModulosMovil.objects.filter(id__in=data.get('modulos_movil', [])))
                    perfil.submodulos_movil.add(*SubModulosMovil.objects.filter(id__in=data.get('submodulos_movil', [])))

                logger.debug(f'PerfilesAPIView POST: perfil {perfil.id} creado en holding {holding_id}')

                return Response({
                    'id': perfil.id,
                    'holding': perfil.holding_id,
                    'nombre_perfil': perfil.nombre_perfil,
                    'tipo': perfil.tipo,
                    'estado': perfil.estado,
                    'modulos_web': list(perfil.modulos_web.values_list('id', flat=True)),
                    'submodulos_web': list(perfil.submodulos_web.values_list('id', flat=True)),
                    'modulos_movil': list(perfil.modulos_movil.values_list('id', flat=True)),
                    'submodulos_movil': list(perfil.submodulos_movil.values_list('id', flat=True)),
                }, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f'PerfilesAPIView POST: error creando perfil en holding {holding_id}: {e}', exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    def put(self, request, holding_id):
        perfil_id = request.data.get('id')
        if not perfil_id:
            return Response(
                {'error': 'Se requiere el ID del perfil para actualizar'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            perfil = Perfiles.objects.get(id=perfil_id, holding_id=holding_id)
        except Perfiles.DoesNotExist:
            logger.error(f'PerfilesAPIView PUT: perfil {perfil_id} no encontrado en holding {holding_id}')
            return Response({'error': 'Perfil no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        data = request.data
        perfil.nombre_perfil = data.get('nombre_perfil', perfil.nombre_perfil)
        perfil.tipo = data.get('tipo', perfil.tipo)
        perfil.estado = data.get('estado', perfil.estado)
        perfil.save()

        if 'modulos_web_ids' in data:
            perfil.modulos_web.set(data['modulos_web_ids'])
        if 'submodulos_web_ids' in data:
            perfil.submodulos_web.set(data['submodulos_web_ids'])
        if 'modulos_movil_ids' in data:
            perfil.modulos_movil.set(data['modulos_movil_ids'])
        if 'submodulos_movil_ids' in data:
            perfil.submodulos_movil.set(data['submodulos_movil_ids'])

        perfil.refresh_from_db()
        logger.debug(f'PerfilesAPIView PUT: perfil {perfil_id} actualizado')

        return Response({
            'id': perfil.id,
            'nombre_perfil': perfil.nombre_perfil,
            'tipo': perfil.tipo,
            'estado': perfil.estado,
            'modulos_web': [{'id': m.id, 'nombre': m.nombre} for m in perfil.modulos_web.all()],
            'submodulos_web': [{'id': sm.id, 'nombre': sm.nombre} for sm in perfil.submodulos_web.all()],
            'modulos_movil': [{'id': m.id, 'nombre': m.nombre} for m in perfil.modulos_movil.all()],
            'submodulos_movil': [{'id': sm.id, 'nombre': sm.nombre} for sm in perfil.submodulos_movil.all()],
        })

    def delete(self, request, holding_id):
        perfil_ids = request.data.get('ids', [])
        if not perfil_ids:
            return Response(
                {'error': 'Se requiere el ID del perfil para eliminar'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            for perfil_id in perfil_ids:
                Perfiles.objects.get(id=perfil_id, holding_id=holding_id).delete()
            logger.debug(f'PerfilesAPIView DELETE: {len(perfil_ids)} perfiles eliminados en holding {holding_id}')
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Perfiles.DoesNotExist:
            logger.error(f'PerfilesAPIView DELETE: perfil no encontrado en holding {holding_id}')
            return Response({'error': 'Perfil no encontrado'}, status=status.HTTP_404_NOT_FOUND)

class AreaAdministracionAPIView(BaseAPIView):
    
    def get(self, request, format=None):
        holding_id = request.query_params.get('holding')
        if holding_id:
            usuarios = AreasAdministracion.objects.filter(holding_id=holding_id)
            serializer = AreaAdministracionSerializer(usuarios, many=True)
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def post(self, request, format=None):
        serializer = AreaAdministracionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    #Metodo DELETE
    def delete(self, request, format=None): 
        perfil_ids = request.data.get('ids', [])
        AreasAdministracion.objects.filter(id__in=perfil_ids).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    #Metodo PATCH
    def patch(self, request, format=None):
        perfil_id = request.data.get('id')
        if not perfil_id:
            return Response({"message": "ID de area es necesario para actualizar"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            perfil = AreasAdministracion.objects.get(id=perfil_id)
        except AreasAdministracion.DoesNotExist:
            return Response({"message": "Area no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        serializer = AreaAdministracionSerializer(perfil, data=request.data, partial=True)  # Partial=True para permitir actualizaciones parciales
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    #Metodo PUT
    def put(self, request, format=None):
        cliente_id = request.data.get('id')
        try:
            perfil = AreasAdministracion.objects.get(id=cliente_id)
        except AreasAdministracion.DoesNotExist:
            return Response({"message": "Perfil no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        serializer = AreaAdministracionSerializer(perfil, data=request.data)  # Sin partial=True
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CargoAdministracionAPIView(BaseAPIView):
    
    def get(self, request, format=None):
        holding_id = request.query_params.get('holding')
        if holding_id:
            usuarios = CargosAdministracion.objects.filter(holding_id=holding_id)
            serializer = CargoAdministracionSerializer(usuarios, many=True)
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def post(self, request, format=None):
        serializer = CargoAdministracionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    #Metodo DELETE
    def delete(self, request, format=None): 
        perfil_ids = request.data.get('ids', [])
        CargosAdministracion.objects.filter(id__in=perfil_ids).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    #Metodo PATCH
    def patch(self, request, format=None):
        perfil_id = request.data.get('id')
        if not perfil_id:
            
            return Response({"message": "ID de perfil es necesario para actualizar"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            perfil = CargosAdministracion.objects.get(id=perfil_id)
        except CargosAdministracion.DoesNotExist:
            return Response({"message": "Perfil no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        serializer = CargoAdministracionSerializer(perfil, data=request.data, partial=True)  # Partial=True para permitir actualizaciones parciales
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    #Metodo PUT
    def put(self, request, format=None):
        cliente_id = request.data.get('id')
        try:
            perfil = CargosAdministracion.objects.get(id=cliente_id)
        except CargosAdministracion.DoesNotExist:
            return Response({"message": "Cargo no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        serializer = CargoAdministracionSerializer(perfil, data=request.data)  # Sin partial=True
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
