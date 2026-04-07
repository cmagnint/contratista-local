import logging
import os
from datetime import date
from django.conf import settings
from django.db import transaction
from django.db.models import Exists, OuterRef, Q
from django.utils import timezone
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from .base import BaseAPIView, PublicAPIView
from ..models import (
    APKLink,
    CodigoQR,
    ContratoTrabajador,
    EnlaceAutoRegistro,
    FolioComercial,
    Horarios,
    PersonalTrabajadores,
    ProduccionTrabajador,
    RegistroAsistencia,
    Supervisores,
    TrabajadorEmpresaTransporte,
    Usuarios,
    Perfiles,
    RegistroCasaTrabajador,
    SupervisorTrabajadorHistorial,
)
from ..serializers import (
    APKLinkSerializer,
    CodigoQRSerializer,
    EnlaceAutoRegistroSerializer,
    PersonalAsignadoSerializer,
    PersonalConAsignacionesSerializer,
    PersonalForUserSerializer,
    PersonalTrabajadoresMobileSerializer,
    PersonalTrabajadoresSerializer,
    ProduccionTrabajadorReporteSerializer,
    SupervisorSerializer,
    TrabajadoresCosechaQRSerializer,
    UserSerializer,
)

logger = logging.getLogger('contratista_test_app')


# ==============================================================================
# PERSONAL FOR USER (selector de persona al crear usuario)
# ==============================================================================

class PersonalForUserAPIView(BaseAPIView):

    def get(self, request, holding_id, format=None):
        try:
            admin_persona_ids = Usuarios.objects.filter(
                Q(is_admin=True) | Q(is_superuser=True),
                persona__isnull=False
            ).values_list('persona_id', flat=True)

            personal = PersonalTrabajadores.objects.filter(
                holding_id=holding_id,
                estado=True,
            ).exclude(
                id__in=admin_persona_ids
            ).exclude(
                usuarios__isnull=False
            )

            if not personal.exists():
                return Response(
                    {'message': 'No se encontró personal disponible'},
                    status=status.HTTP_404_NOT_FOUND
                )

            logger.debug(f'PersonalForUserAPIView GET: {personal.count()} registros disponibles en holding {holding_id}')
            return Response(PersonalForUserSerializer(personal, many=True).data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f'PersonalForUserAPIView GET: error en holding {holding_id}: {e}', exc_info=True)
            return Response(
                {'message': f'Error al obtener personal: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


# ==============================================================================
# USUARIOS
# ==============================================================================

class UsuarioAPIViews(BaseAPIView):

    def get(self, request, holding_id, format=None):
        try:
            usuarios = Usuarios.objects.filter(holding_id=holding_id).exclude(is_admin=True)
            if usuarios.exists():
                return Response(UserSerializer(usuarios, many=True).data, status=status.HTTP_200_OK)
            return Response({'message': 'No se encontraron usuarios'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f'UsuarioAPIViews GET: error en holding {holding_id}: {e}', exc_info=True)
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        with transaction.atomic():
            serializer = UserSerializer(data=request.data)

            if serializer.is_valid():
                try:
                    usuario = serializer.save()
                    logger.debug(
                        f'UsuarioAPIViews POST: usuario {usuario.id} creado | RUT: {usuario.rut} | '
                        f'Holding: {usuario.holding.nombre if usuario.holding else "N/A"} | '
                        f'Perfil: {usuario.perfil.nombre_perfil if usuario.perfil else "Sin perfil"}'
                    )

                    if usuario.perfil and usuario.perfil.nombre_perfil == 'SUPERVISOR':
                        supervisor = Supervisores.objects.create(
                            holding_id=usuario.holding_id,
                            usuario=usuario
                        )
                        logger.debug(f'UsuarioAPIViews POST: supervisor {supervisor.id} creado para usuario {usuario.id}')

                    return Response(serializer.data, status=status.HTTP_201_CREATED)

                except Exception as e:
                    logger.error(f'UsuarioAPIViews POST: error durante la creación: {e}', exc_info=True)
                    raise e
            else:
                logger.error(f'UsuarioAPIViews POST: datos inválidos: {serializer.errors}')
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, format=None):
        with transaction.atomic():
            perfil_id = request.data.get('id')
            try:
                usuario = Usuarios.objects.get(id=perfil_id)
                old_perfil = usuario.perfil
                old_perfil_nombre = old_perfil.nombre_perfil if old_perfil else None

                new_perfil_id = request.data.get('perfil')
                if new_perfil_id:
                    
                    new_perfil = Perfiles.objects.get(id=new_perfil_id)
                    new_perfil_nombre = new_perfil.nombre_perfil

                    if old_perfil_nombre == 'SUPERVISOR' and new_perfil_nombre != 'SUPERVISOR':
                        try:
                            supervisor = Supervisores.objects.get(usuario=usuario)
                            trabajadores_count = supervisor.trabajadores.count()
                            if trabajadores_count > 0:
                                return Response(
                                    {'message': f'No puede cambiar el perfil. El Supervisor tiene {trabajadores_count} trabajador(es) asignado(s). Debe reasignarlos primero.'},
                                    status=status.HTTP_400_BAD_REQUEST
                                )
                        except Supervisores.DoesNotExist:
                            pass

                serializer = UserSerializer(usuario, data=request.data)
                if serializer.is_valid():
                    usuario = serializer.save()
                    logger.debug(f'UsuarioAPIViews PUT: usuario {perfil_id} actualizado')

                    if 'perfil' in request.data:
                        new_perfil_nombre = usuario.perfil.nombre_perfil if usuario.perfil else None
                        old_perfil_nombre = old_perfil.nombre_perfil if old_perfil else None

                        if new_perfil_nombre == 'SUPERVISOR' and old_perfil_nombre != 'SUPERVISOR':
                            Supervisores.objects.create(holding_id=usuario.holding_id, usuario=usuario)
                        elif old_perfil_nombre == 'SUPERVISOR' and new_perfil_nombre != 'SUPERVISOR':
                            Supervisores.objects.filter(usuario=usuario).delete()

                    return Response(serializer.data)

                logger.error(f'UsuarioAPIViews PUT: datos inválidos para usuario {perfil_id}: {serializer.errors}')
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            except Usuarios.DoesNotExist:
                logger.error(f'UsuarioAPIViews PUT: usuario {perfil_id} no encontrado')
                return Response({'message': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                logger.error(f'UsuarioAPIViews PUT: error: {e}', exc_info=True)
                return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, format=None):
        with transaction.atomic():
            user_ids = request.data.get('ids', [])
            Usuarios.objects.filter(id__in=user_ids).delete()
            logger.debug(f'UsuarioAPIViews DELETE: {len(user_ids)} usuarios eliminados')
            return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, format=None):
        with transaction.atomic():
            user_id = request.data.get('id')
            if not user_id:
                return Response({'message': 'ID de usuario es necesario'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                usuario = Usuarios.objects.get(id=user_id)
                old_perfil = usuario.perfil

                serializer = UserSerializer(usuario, data=request.data, partial=True)
                if serializer.is_valid():
                    usuario = serializer.save()

                    if 'perfil' in request.data:
                        new_perfil_nombre = usuario.perfil.nombre_perfil if usuario.perfil else None
                        old_perfil_nombre = old_perfil.nombre_perfil if old_perfil else None

                        if new_perfil_nombre == 'SUPERVISOR' and old_perfil_nombre != 'SUPERVISOR':
                            Supervisores.objects.create(holding_id=usuario.holding_id, usuario=usuario)
                        elif old_perfil_nombre == 'SUPERVISOR' and new_perfil_nombre != 'SUPERVISOR':
                            Supervisores.objects.filter(usuario=usuario).delete()

                    logger.debug(f'UsuarioAPIViews PATCH: usuario {user_id} actualizado')
                    return Response(serializer.data)

                logger.error(f'UsuarioAPIViews PATCH: datos inválidos para usuario {user_id}: {serializer.errors}')
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            except Usuarios.DoesNotExist:
                logger.error(f'UsuarioAPIViews PATCH: usuario {user_id} no encontrado')
                return Response({'message': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                logger.error(f'UsuarioAPIViews PATCH: error: {e}', exc_info=True)
                return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ==============================================================================
# PERSONAL TRABAJADORES (web)
# ==============================================================================

class PersonalTrabajadoresAPIView(BaseAPIView):

    def get(self, request, format=None):
        holding_id = request.query_params.get('holding')
        if not holding_id:
            return Response({'error': 'El parámetro holding es necesario'}, status=status.HTTP_400_BAD_REQUEST)

        admin_persona_ids = Usuarios.objects.filter(
            Q(is_admin=True) | Q(is_superuser=True),
            persona__isnull=False
        ).values_list('persona_id', flat=True)

        trabajadores = PersonalTrabajadores.objects.filter(
            holding_id=holding_id
        ).exclude(id__in=admin_persona_ids)

        return Response(PersonalTrabajadoresSerializer(trabajadores, many=True).data)

    def post(self, request, format=None):
        from django.db import IntegrityError
        serializer = PersonalTrabajadoresSerializer(data=request.data)
        if serializer.is_valid():
            try:
                trabajador = serializer.save()
                logger.debug(f'PersonalTrabajadoresAPIView POST: trabajador {trabajador.id} creado')
                return Response({'id': trabajador.id, 'data': serializer.data}, status=status.HTTP_201_CREATED)
            except IntegrityError:
                logger.error('PersonalTrabajadoresAPIView POST: RUT duplicado')
                return Response(
                    {'rut': ['Ya existe un trabajador registrado con este RUT.']},
                    status=status.HTTP_400_BAD_REQUEST
                )

        logger.error(f'PersonalTrabajadoresAPIView POST: datos inválidos: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, format=None):
        trabajador_id = request.data.get('id')
        try:
            trabajador = PersonalTrabajadores.objects.get(id=trabajador_id)
        except PersonalTrabajadores.DoesNotExist:
            logger.error(f'PersonalTrabajadoresAPIView PUT: trabajador {trabajador_id} no encontrado')
            return Response({'message': 'Trabajador no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        serializer = PersonalTrabajadoresSerializer(trabajador, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        logger.error(f'PersonalTrabajadoresAPIView PUT: datos inválidos para trabajador {trabajador_id}: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, format=None):
        trabajador_ids = request.data.get('ids', [])
        PersonalTrabajadores.objects.filter(id__in=trabajador_ids).delete()
        logger.debug(f'PersonalTrabajadoresAPIView DELETE: {len(trabajador_ids)} trabajadores eliminados')
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, format=None):
        trabajador_id = request.data.get('id')
        if not trabajador_id:
            return Response(
                {'message': 'ID de trabajador es necesario para actualizar'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            trabajador = PersonalTrabajadores.objects.get(id=trabajador_id)
        except PersonalTrabajadores.DoesNotExist:
            logger.error(f'PersonalTrabajadoresAPIView PATCH: trabajador {trabajador_id} no encontrado')
            return Response({'message': 'Trabajador no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        serializer = PersonalTrabajadoresSerializer(trabajador, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()

            casa_id = request.data.get('casa')
            if casa_id:
                RegistroCasaTrabajador.objects.filter(
                    trabajador=trabajador,
                    fecha_fin__isnull=True
                ).update(fecha_fin=date.today())

                RegistroCasaTrabajador.objects.create(
                    holding_id=trabajador.holding_id,
                    trabajador=trabajador,
                    casa_id=casa_id,
                    fecha_inicio=date.today()
                )

            return Response(serializer.data)

        logger.error(f'PersonalTrabajadoresAPIView PATCH: datos inválidos para trabajador {trabajador_id}: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ==============================================================================
# PERSONAL TRABAJADORES (móvil)
# ==============================================================================

class PersonalTrabajadoresMobileAPIView(BaseAPIView):
    parser_classes = [MultiPartParser, FormParser]

    def merge_data(self, old_data, new_data):
        merged = old_data.copy()
        for key, new_value in new_data.items():
            if isinstance(new_value, list) and len(new_value) > 0:
                new_value = new_value[0]
            if new_value not in (None, '', 'null', 'undefined'):
                merged[key] = new_value
        return merged

    def delete_old_file(self, file_path):
        if file_path:
            full_path = os.path.join(settings.MEDIA_ROOT, file_path)
            if os.path.isfile(full_path):
                os.remove(full_path)

    def calcular_horas_dia(self, horario, fecha):
        from datetime import datetime
        if not horario:
            return 9.0
        dias = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']
        dia_nombre = dias[fecha.weekday()]
        inicio = getattr(horario, f'{dia_nombre}_inicio', None)
        fin = getattr(horario, f'{dia_nombre}_fin', None)
        colacion = getattr(horario, f'{dia_nombre}_minutos_colacion', 0)
        if not inicio or not fin:
            return 0.0
        inicio_dt = datetime.combine(fecha, inicio)
        fin_dt = datetime.combine(fecha, fin)
        minutos = (fin_dt - inicio_dt).seconds // 60 - colacion
        return round(minutos / 60, 1)

    @transaction.atomic
    def post(self, request, format=None):
        from django.conf import settings

        data = {}
        for key, value in request.data.items():
            if isinstance(value, list) and len(value) > 0:
                data[key] = value[0]
            elif not isinstance(value, list):
                data[key] = value
        for key, file in request.FILES.items():
            data[key] = file

        if 'estado' in data and isinstance(data['estado'], str):
            data['estado'] = data['estado'].lower() in ('true', '1', 'yes')

        if 'numero_cuenta' in data and data['numero_cuenta']:
            try:
                data['numero_cuenta'] = int(data['numero_cuenta'])
            except (ValueError, TypeError):
                pass

        if not data.get('area'):
            return Response({'error': 'El área es obligatoria'}, status=status.HTTP_400_BAD_REQUEST)
        if not data.get('cargo'):
            return Response({'error': 'El cargo es obligatorio'}, status=status.HTTP_400_BAD_REQUEST)

        existing_personal = None
        if data.get('rut'):
            existing_personal = PersonalTrabajadores.objects.filter(rut=data['rut']).first()
        elif data.get('dni'):
            existing_personal = PersonalTrabajadores.objects.filter(dni=data['dni']).first()

        if existing_personal:
            old_front_image = existing_personal.carnet_front_image.name if existing_personal.carnet_front_image else None
            old_back_image = existing_personal.carnet_back_image.name if existing_personal.carnet_back_image else None
            old_signature = existing_personal.firma.name if existing_personal.firma else None
            old_fingerprint = existing_personal.huella_digital.name if existing_personal.huella_digital else None

            current_data = PersonalTrabajadoresMobileSerializer(existing_personal).data
            merged_data = self.merge_data(current_data, data)
            serializer = PersonalTrabajadoresMobileSerializer(existing_personal, data=merged_data, partial=True)
        else:
            if 'fecha_ingreso' not in data or not data['fecha_ingreso']:
                data['fecha_ingreso'] = timezone.now().date()
            serializer = PersonalTrabajadoresMobileSerializer(data=data)

        if not serializer.is_valid():
            logger.error(f'PersonalTrabajadoresMobileAPIView POST: errores de validación: {serializer.errors}')
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        personal = serializer.save()

        # Registro casa
        casa_id = data.get('casa')
        if casa_id:
            RegistroCasaTrabajador.objects.filter(
                trabajador=personal, fecha_fin__isnull=True
            ).update(fecha_fin=timezone.now().date())
            RegistroCasaTrabajador.objects.create(
                holding_id=data.get('holding'),
                trabajador=personal,
                casa_id=casa_id,
                fecha_inicio=personal.fecha_ingreso or timezone.now().date()
            )

        # Supervisor
        supervisor_id = data.get('codigo_supervisor')
        if not supervisor_id:
            return Response({'error': 'El supervisor es obligatorio'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            supervisor = Supervisores.objects.filter(id=supervisor_id).first()
            if not supervisor:
                logger.error(f'PersonalTrabajadoresMobileAPIView POST: supervisor {supervisor_id} no encontrado')
                return Response(
                    {'error': f'Supervisor con ID {supervisor_id} no encontrado'},
                    status=status.HTTP_404_NOT_FOUND
                )

            supervisor.trabajadores.add(personal)
            supervisor.save()

            SupervisorTrabajadorHistorial.objects.filter(
                trabajador=personal, fecha_fin__isnull=True
            ).exclude(supervisor=supervisor).update(fecha_fin=timezone.now().date())

            SupervisorTrabajadorHistorial.objects.get_or_create(
                supervisor=supervisor,
                trabajador=personal,
                fecha_fin=None,
                defaults={
                    'holding_id': data.get('holding'),
                    'fecha_inicio': timezone.now().date(),
                }
            )
        except Exception as e:
            logger.error(f'PersonalTrabajadoresMobileAPIView POST: error asignando supervisor: {e}', exc_info=True)
            return Response({'error': f'Error al asignar supervisor: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Contrato y asistencia
        folio_id = data.get('folio')
        horario_id = data.get('horario')
        if folio_id:
            try:
                folio = FolioComercial.objects.get(id=folio_id)
                horario = Horarios.objects.filter(id=horario_id).first() if horario_id else None

                if data.get('transportista') or data.get('vehiculo'):
                    TrabajadorEmpresaTransporte.objects.create(
                        holding_id=data.get('holding'),
                        trabajador=personal,
                        transportista_id=data.get('transportista'),
                        vehiculo_id=data.get('vehiculo')
                    )

                contrato = ContratoTrabajador.objects.create(
                    holding_id=data.get('holding'),
                    trabajador=personal,
                    cliente_id=folio.cliente_id,
                    folio_comercial_id=folio_id,
                    labor_id=data.get('labor'),
                    fundo_id=data.get('fundo'),
                    horario=horario,
                    fecha_inicio_contrato=folio.fecha_inicio_contrato,
                    fecha_termino_contrato=folio.fecha_termino_contrato,
                )
                logger.debug(f'PersonalTrabajadoresMobileAPIView POST: contrato {contrato.id} creado')

                fecha_asistencia = personal.fecha_ingreso if personal.fecha_ingreso else timezone.now().date()
                horas_dia = self.calcular_horas_dia(horario, fecha_asistencia) if horario else 9.0

                RegistroAsistencia.objects.get_or_create(
                    trabajador=personal,
                    fecha_asistencia=fecha_asistencia,
                    defaults={
                        'holding_id': data.get('holding'),
                        'supervisor': supervisor,
                        'estado': 'A',
                        'horas_registradas': horas_dia,
                        'modificado_por': request.user
                    }
                )
            except FolioComercial.DoesNotExist:
                logger.error(f'PersonalTrabajadoresMobileAPIView POST: folio {folio_id} no encontrado')
            except Exception as e:
                logger.error(f'PersonalTrabajadoresMobileAPIView POST: error creando contrato/asistencia: {e}', exc_info=True)

        # Eliminar archivos viejos
        if existing_personal:
            if 'carnet_front_image' in request.FILES:
                self.delete_old_file(old_front_image)
            if 'carnet_back_image' in request.FILES:
                self.delete_old_file(old_back_image)
            if 'firma' in request.FILES:
                self.delete_old_file(old_signature)
            if 'huella_digital' in request.FILES:
                self.delete_old_file(old_fingerprint)

        logger.debug(f'PersonalTrabajadoresMobileAPIView POST: trabajador {personal.id} guardado exitosamente')
        return Response(PersonalTrabajadoresMobileSerializer(personal).data, status=status.HTTP_201_CREATED)


# ==============================================================================
# PERSONAL WEB (auto-registro desde enlace)
# ==============================================================================

class PersonalWebAPIView(PublicAPIView):

    @transaction.atomic
    def post(self, request):
        try:
            enlace_id = request.data.get('enlace_id')
            token = request.data.get('token')

            try:
                enlace = EnlaceAutoRegistro.objects.get(id=enlace_id, token=token)
                if not enlace.is_valid():
                    return Response(
                        {'error': 'El enlace ha expirado o no es válido'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except EnlaceAutoRegistro.DoesNotExist:
                logger.error(f'PersonalWebAPIView POST: enlace {enlace_id} no encontrado')
                return Response({'error': 'Enlace inválido'}, status=status.HTTP_400_BAD_REQUEST)

            personal_data = {
                'holding': enlace.holding.id,
                'nombres': request.data.get('nombres'),
                'apellidos': request.data.get('apellidos'),
                'rut': request.data.get('rut'),
                'correo': request.data.get('correo'),
                'direccion': request.data.get('direccion'),
                'telefono': request.data.get('telefono'),
                'nacionalidad': request.data.get('nacionalidad'),
                'sexo': request.data.get('sexo'),
                'estado_civil': request.data.get('estado_civil'),
                'fecha_nacimiento': request.data.get('fecha_nacimiento'),
                'estado': True
            }

            for campo in ['carnet_front_image', 'carnet_back_image', 'firma']:
                archivo = request.FILES.get(campo)
                if archivo:
                    personal_data[campo] = archivo

            personal_serializer = PersonalTrabajadoresSerializer(data=personal_data)
            if not personal_serializer.is_valid():
                logger.error(f'PersonalWebAPIView POST: datos de personal inválidos: {personal_serializer.errors}')
                return Response(personal_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            personal = personal_serializer.save()

            usuario_data = {
                'holding': enlace.holding.id,
                'persona': personal.id,
                'rut': personal.rut,
                'email': personal.correo,
                'perfil': enlace.perfil.id,
                'estado': True
            }

            from django.forms import ValidationError
            usuario_serializer = UserSerializer(data=usuario_data)
            if not usuario_serializer.is_valid():
                logger.error(f'PersonalWebAPIView POST: datos de usuario inválidos: {usuario_serializer.errors}')
                raise ValidationError(usuario_serializer.errors)

            usuario_serializer.save()
            logger.debug(f'PersonalWebAPIView POST: registro completado para personal {personal.id}')

            return Response({
                'personal': personal_serializer.data,
                'usuario': usuario_serializer.data,
                'message': 'Registro completado exitosamente'
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f'PersonalWebAPIView POST: error en proceso de registro: {e}', exc_info=True)
            return Response(
                {'error': f'Error en el proceso de registro: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


# ==============================================================================
# PERSONAL ASIGNADO
# ==============================================================================

class PersonalAsignadoAPIView(BaseAPIView):

    def get(self, request):
        supervisor_id = request.query_params.get('supervisor_id')
        if not supervisor_id:
            return Response({'error': 'Debe proporcionar supervisor_id'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            supervisor = Supervisores.objects.get(id=supervisor_id)
            trabajadores = supervisor.trabajadores.all()
            serializer = PersonalAsignadoSerializer(trabajadores, many=True, context={'request': request})
            return Response(serializer.data)
        except Supervisores.DoesNotExist:
            logger.error(f'PersonalAsignadoAPIView GET: supervisor {supervisor_id} no encontrado')
            return Response({'error': 'Supervisor no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f'PersonalAsignadoAPIView GET: error: {e}', exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==============================================================================
# PERSONAL DOCUMENTOS
# ==============================================================================

class PersonalDocumentosAPIView(BaseAPIView):

    def get(self, request, trabajador_id):
        try:
            trabajador = PersonalTrabajadores.objects.get(id=trabajador_id)
        except PersonalTrabajadores.DoesNotExist:
            logger.error(f'PersonalDocumentosAPIView GET: trabajador {trabajador_id} no encontrado')
            return Response({'error': 'Trabajador no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        tipo = request.query_params.get('tipo')
        campo_map = {
            'carnet_front': trabajador.carnet_front_image,
            'carnet_back': trabajador.carnet_back_image,
            'firma': trabajador.firma,
            'huella': trabajador.huella_digital,
        }

        imagen = campo_map.get(tipo)
        if not imagen:
            return Response({'error': 'Imagen no encontrada'}, status=status.HTTP_404_NOT_FOUND)

        import mimetypes
        from django.http import FileResponse
        mime_type, _ = mimetypes.guess_type(imagen.name)
        return FileResponse(imagen.open('rb'), content_type=mime_type or 'application/octet-stream')

    def patch(self, request, trabajador_id):
        try:
            trabajador = PersonalTrabajadores.objects.get(id=trabajador_id)
        except PersonalTrabajadores.DoesNotExist:
            logger.error(f'PersonalDocumentosAPIView PATCH: trabajador {trabajador_id} no encontrado')
            return Response({'error': 'Trabajador no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        for campo in ['carnet_front_image', 'carnet_back_image', 'firma', 'huella_digital']:
            if campo in request.FILES:
                setattr(trabajador, campo, request.FILES[campo])

        trabajador.save()
        return Response(PersonalTrabajadoresSerializer(trabajador).data, status=status.HTTP_200_OK)


# ==============================================================================
# PERSONAL FILTRADO
# ==============================================================================

class PersonalFiltradoAPIView(BaseAPIView):

    def get(self, request):
        holding_id = request.query_params.get('holding')
        sociedad_id = request.query_params.get('sociedad_id')
        filtro_contrato = request.query_params.get('filtro_contrato', 'sin_contrato')

        if not holding_id:
            return Response({'error': 'El parámetro holding es necesario'}, status=status.HTTP_400_BAD_REQUEST)

        hoy = date.today()
        query = Q(holding_id=holding_id, estado=True)
        if sociedad_id:
            query &= Q(sociedad_id=sociedad_id)

        contrato_vigente_base = ContratoTrabajador.objects.filter(
            trabajador=OuterRef('pk'),
            fecha_inicio_contrato__lte=hoy
        ).filter(
            Q(fecha_termino_contrato__gte=hoy) | Q(fecha_termino_contrato__isnull=True)
        )

        trabajadores = PersonalTrabajadores.objects.filter(query).filter(
            Exists(contrato_vigente_base)
        )

        if filtro_contrato == 'sin_contrato':
            trabajadores = trabajadores.filter(
                Exists(contrato_vigente_base.filter(contrato_generado=False))
            )
        elif filtro_contrato == 'con_contrato':
            trabajadores = trabajadores.filter(
                Exists(contrato_vigente_base.filter(contrato_generado=True))
            )

        trabajadores = trabajadores.annotate(
            tiene_contrato=Exists(contrato_vigente_base.filter(contrato_generado=True))
        )

        return Response(PersonalConAsignacionesSerializer(trabajadores, many=True).data)


# ==============================================================================
# SUPERVISOR
# ==============================================================================

class SupervisorAPIView(BaseAPIView):

    def get(self, request, holding_id=None, format=None):
        if not holding_id:
            return Response({'message': 'Se requiere holding_id'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            supervisores = Supervisores.objects.select_related(
                'usuario', 'holding', 'usuario__persona'
            ).prefetch_related('trabajadores').filter(holding_id=holding_id)

            if supervisores.exists():
                logger.debug(f'SupervisorAPIView GET: {supervisores.count()} supervisores en holding {holding_id}')
                return Response(SupervisorSerializer(supervisores, many=True).data, status=status.HTTP_200_OK)

            return Response({'message': 'No se encontraron supervisores'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            logger.error(f'SupervisorAPIView GET: error en holding {holding_id}: {e}', exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        serializer = SupervisorSerializer(data=request.data)
        if serializer.is_valid():
            supervisor = serializer.save()
            trabajadores_ids = request.data.get('trabajadores', [])
            if trabajadores_ids:
                supervisor.trabajadores.set(PersonalTrabajadores.objects.filter(id__in=trabajadores_ids))
            logger.debug(f'SupervisorAPIView POST: supervisor {supervisor.id} creado')
            return Response({'id': supervisor.id, 'data': serializer.data}, status=status.HTTP_201_CREATED)

        logger.error(f'SupervisorAPIView POST: datos inválidos: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        supervisor_id = request.data.get('id')
        try:
            supervisor = Supervisores.objects.get(id=supervisor_id)
        except Supervisores.DoesNotExist:
            logger.error(f'SupervisorAPIView PUT: supervisor {supervisor_id} no encontrado')
            return Response({'message': 'Supervisor no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        serializer = SupervisorSerializer(supervisor, data=request.data)
        if serializer.is_valid():
            supervisor = serializer.save()
            trabajadores_ids = request.data.get('trabajadores')
            if trabajadores_ids is not None:
                supervisor.trabajadores.set(PersonalTrabajadores.objects.filter(id__in=trabajadores_ids))
            return Response(serializer.data)

        logger.error(f'SupervisorAPIView PUT: datos inválidos para supervisor {supervisor_id}: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        supervisor_ids = request.data.get('ids', [])
        Supervisores.objects.filter(id__in=supervisor_ids).delete()
        logger.debug(f'SupervisorAPIView DELETE: {len(supervisor_ids)} supervisores eliminados')
        return Response(status=status.HTTP_204_NO_CONTENT)


# ==============================================================================
# CÓDIGO QR
# ==============================================================================

class CodigoQRAPIView(BaseAPIView):

    def get(self, request, trabajador_id=None, format=None):
        if trabajador_id is None:
            trabajador_id = request.query_params.get('trabajador')

        if trabajador_id:
            try:
                codigo_qr = CodigoQR.objects.get(trabajador_id=trabajador_id)
                return Response(CodigoQRSerializer(codigo_qr).data)
            except CodigoQR.DoesNotExist:
                logger.error(f'CodigoQRAPIView GET: QR no encontrado para trabajador {trabajador_id}')
                return Response({'message': 'Código QR no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        return Response(CodigoQRSerializer(CodigoQR.objects.all(), many=True).data)

    def post(self, request, format=None):
        serializer = CodigoQRSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        logger.error(f'CodigoQRAPIView POST: datos inválidos: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, trabajador_id=None, format=None):
        if trabajador_id is None:
            trabajador_id = request.data.get('trabajador')
        if not trabajador_id:
            return Response({'message': 'ID del trabajador es necesario para actualizar'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            codigo_qr = CodigoQR.objects.get(trabajador_id=trabajador_id)
        except CodigoQR.DoesNotExist:
            logger.error(f'CodigoQRAPIView PUT: QR no encontrado para trabajador {trabajador_id}')
            return Response({'message': 'Código QR no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        serializer = CodigoQRSerializer(codigo_qr, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        logger.error(f'CodigoQRAPIView PUT: datos inválidos: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, trabajador_id=None, format=None):
        if trabajador_id is None:
            trabajador_id = request.data.get('trabajador')
        if not trabajador_id:
            return Response({'message': 'ID del trabajador es necesario para eliminar'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            CodigoQR.objects.get(trabajador_id=trabajador_id).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except CodigoQR.DoesNotExist:
            logger.error(f'CodigoQRAPIView DELETE: QR no encontrado para trabajador {trabajador_id}')
            return Response({'message': 'Código QR no encontrado'}, status=status.HTTP_404_NOT_FOUND)


# ==============================================================================
# TRABAJADORES COSECHA QR
# ==============================================================================

class TrabajadoresCosechaQRView(BaseAPIView):

    def get(self, request):
        try:
            personal_supervisados = PersonalTrabajadores.objects.filter(
                codigo_supervisor__isnull=False,
                estado=True
            )

            trabajadores_cosecha = []
            for personal in personal_supervisados:
                contratos = PersonalTrabajadores.objects.filter(
                    Q(run=personal.rut),
                    Q(labor__nombre__iexact='COSECHA') |
                    Q(labor__nombre__iexact='cosecha') |
                    Q(labor__nombre__iexact='Cosecha')
                )
                if contratos.exists():
                    for _ in contratos:
                        trabajadores_cosecha.append({
                            'nombres': personal.nombres,
                            'apellidos': personal.apellidos,
                            'rut': personal.rut,
                        })

            return Response(TrabajadoresCosechaQRSerializer(trabajadores_cosecha, many=True).data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f'TrabajadoresCosechaQRView GET: error: {e}', exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==============================================================================
# ENLACE AUTO REGISTRO
# ==============================================================================

class EnlaceAutoRegistroAPIView(BaseAPIView):

    def get(self, request):
        holding_id = request.query_params.get('holding')
        if not holding_id:
            return Response({'error': 'Se requiere el ID del holding'}, status=status.HTTP_400_BAD_REQUEST)

        ahora = timezone.now()
        enlaces = EnlaceAutoRegistro.objects.filter(
            holding_id=holding_id,
            activo=True,
            fecha_expiracion__gt=ahora
        ).order_by('-fecha_creacion')

        return Response(EnlaceAutoRegistroSerializer(enlaces, many=True).data)

    def post(self, request):
        serializer = EnlaceAutoRegistroSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(usuario_creador=request.user, activo=True)
            logger.debug('EnlaceAutoRegistroAPIView POST: enlace creado')
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        logger.error(f'EnlaceAutoRegistroAPIView POST: datos inválidos: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        enlaces_ids = request.data.get('ids', [])
        if not enlaces_ids:
            return Response({'error': 'Se requiere al menos un ID de enlace'}, status=status.HTTP_400_BAD_REQUEST)

        EnlaceAutoRegistro.objects.filter(
            id__in=enlaces_ids,
            holding_id=request.data.get('holding')
        ).update(activo=False)

        return Response(status=status.HTTP_204_NO_CONTENT)


class ValidarEnlaceAutoRegistroAPIView(PublicAPIView):

    def get(self, request, token, id):
        try:
            enlace = EnlaceAutoRegistro.objects.get(id=id, token=token)

            if not enlace.is_valid():
                return Response({
                    'error': 'El enlace ha expirado o no está activo',
                    'codigo': 'ENLACE_INVALIDO'
                }, status=status.HTTP_400_BAD_REQUEST)

            return Response({
                'perfil_id': enlace.perfil.id,
                'perfil_nombre': enlace.perfil.nombre_perfil,
                'holding_id': enlace.holding.id,
                'ruts_permitidos': enlace.ruts_permitidos,
                'fecha_expiracion': enlace.fecha_expiracion,
                'activo': enlace.activo
            })

        except EnlaceAutoRegistro.DoesNotExist:
            logger.error(f'ValidarEnlaceAutoRegistroAPIView GET: enlace {id} no encontrado')
            return Response({
                'error': 'Enlace no encontrado',
                'codigo': 'ENLACE_NO_EXISTE'
            }, status=status.HTTP_404_NOT_FOUND)


# ==============================================================================
# APK LINK
# ==============================================================================

class APKLinkAPIView(BaseAPIView):

    def get(self, request, holding_id):
        enlace = APKLink.objects.filter(
            holding_id=holding_id,
            activo=True,
            fecha_expiracion__gt=timezone.now()
        ).first()

        if enlace:
            return Response(APKLinkSerializer(enlace).data)
        return Response([])

    def post(self, request, holding_id):
        data = request.data.copy()
        data['holding'] = holding_id

        serializer = APKLinkSerializer(data=data)
        if serializer.is_valid():
            enlace = serializer.save(usuario_creador=request.user, activo=True)
            logger.debug(f'APKLinkAPIView POST: enlace {enlace.id} creado para holding {holding_id}')
            return Response(APKLinkSerializer(enlace).data, status=status.HTTP_201_CREATED)

        logger.error(f'APKLinkAPIView POST: datos inválidos: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, holding_id):
        enlace_id = request.data.get('id')
        if not enlace_id:
            return Response({'error': 'Se requiere el ID del enlace'}, status=status.HTTP_400_BAD_REQUEST)

        APKLink.objects.filter(id=enlace_id, holding_id=holding_id).update(activo=False)
        logger.debug(f'APKLinkAPIView DELETE: enlace {enlace_id} desactivado')
        return Response(status=status.HTTP_204_NO_CONTENT)


class ValidarApkLinkAPIView(PublicAPIView):

    def get(self, request, token, id):
        try:
            enlace = APKLink.objects.get(id=id, token=token)
            if not enlace.is_valid():
                return Response({
                    'message': 'El enlace ha expirado o no está activo',
                    'codigo': 'ENLACE_INVALIDO'
                }, status=status.HTTP_400_BAD_REQUEST)

            return Response({
                'mensaje': 'Enlace válido',
                'tiempo_restante': enlace.tiempo_restante(),
                'fecha_expiracion': enlace.fecha_expiracion,
                'activo': enlace.activo
            })

        except APKLink.DoesNotExist:
            logger.error(f'ValidarApkLinkAPIView GET: enlace {id} no encontrado')
            return Response({
                'message': 'El enlace de descarga no es válido',
                'codigo': 'ENLACE_NO_EXISTE'
            }, status=status.HTTP_404_NOT_FOUND)


class DescargarApkAPIView(PublicAPIView):

    def get(self, request, token, id):
        from django.http import FileResponse
        try:
            enlace = APKLink.objects.get(id=id, token=token)

            if not enlace.is_valid():
                return Response({
                    'message': 'El enlace ha expirado o no está activo',
                    'codigo': 'ENLACE_INVALIDO'
                }, status=status.HTTP_400_BAD_REQUEST)

            apk_path = enlace.get_apk_path()
            if not os.path.exists(apk_path):
                logger.error(f'DescargarApkAPIView GET: archivo APK no existe en {apk_path}')
                return Response({
                    'message': 'El archivo APK no está disponible',
                    'codigo': 'ARCHIVO_NO_EXISTE'
                }, status=status.HTTP_404_NOT_FOUND)

            response = FileResponse(open(apk_path, 'rb'), content_type='application/vnd.android.package-archive')
            response['Content-Disposition'] = 'attachment; filename="contratista.apk"'
            return response

        except APKLink.DoesNotExist:
            logger.error(f'DescargarApkAPIView GET: enlace {id} no encontrado')
            return Response({
                'message': 'El enlace de descarga no es válido',
                'codigo': 'ENLACE_NO_EXISTE'
            }, status=status.HTTP_404_NOT_FOUND)


# ==============================================================================
# INFORME RENDIMIENTO
# ==============================================================================

class InformeRendimientoAPIView(BaseAPIView):

    def post(self, request):
        try:
            fecha_inicio = request.data.get('fecha_inicio')
            fecha_fin = request.data.get('fecha_fin')
            cliente_id = request.data.get('cliente_id')
            supervisor_id = request.data.get('supervisor_id')
            jefe_cuadrilla_id = request.data.get('jefe_cuadrilla_id')
            labor_id = request.data.get('labor_id')

            queryset = ProduccionTrabajador.objects.select_related(
                'trabajador', 'labor', 'unidad_control'
            ).all()

            if fecha_inicio and fecha_fin:
                queryset = queryset.filter(hora_fecha_ingreso_produccion__range=[fecha_inicio, fecha_fin])
            if cliente_id:
                queryset = queryset.filter(folio__cliente_id=cliente_id)
            if supervisor_id:
                queryset = queryset.filter(trabajador__supervisor_directo__id=supervisor_id)
            if jefe_cuadrilla_id:
                queryset = queryset.filter(trabajador__jefe_cuadrilla__id=jefe_cuadrilla_id)
            if labor_id:
                queryset = queryset.filter(labor_id=labor_id)

            return Response(ProduccionTrabajadorReporteSerializer(queryset, many=True).data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f'InformeRendimientoAPIView POST: error: {e}', exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)