import logging
import random
from datetime import timedelta

from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response

from .base import BaseAPIView, PublicAPIView
from ..serializers import LoginSerializer
from ..models import Developer, Sociedad, Supervisores, Usuarios
from ..services.jwt_service import JWTService

logger = logging.getLogger('contratista_test_app')


# ==============================================================================
# HEALTH
# ==============================================================================

class CheckHealthAPIView(PublicAPIView):

    def get(self, request):
        return Response({'status': 'healthy'}, status=status.HTTP_200_OK)

# ==============================================================================
# PASSWORD RESET
# ==============================================================================

class PasswordResetAPIView(PublicAPIView):

    def post(self, request):
        action = request.data.get('action')

        actions = {
            'check_user':      self._check_user,
            'generate_code':   self._generate_code,
            'verify_code':     self._verify_code,
            'change_password': self._change_password,
        }

        handler = actions.get(action)
        if not handler:
            return Response(
                {'status': 'error', 'message': 'Acción no válida.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return handler(request)

    def _check_user(self, request):
        rut = request.data.get('rut_user')

        if not rut:
            return Response(
                {'status': 'error', 'message': 'RUT es requerido.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            Usuarios.objects.get(rut=rut)
            logger.debug(f'PasswordReset check_user: RUT encontrado {rut}')
            return Response(
                {'valid': True, 'status': 'success', 'message': 'RUT válido'},
                status=status.HTTP_200_OK
            )
        except ObjectDoesNotExist:
            logger.error(f'PasswordReset check_user: RUT no encontrado {rut}')
            return Response(
                {'valid': False, 'status': 'error', 'message': 'RUT no encontrado en el sistema'},
                status=status.HTTP_404_NOT_FOUND
            )

    def _generate_code(self, request):
        email = request.data.get('email')
        rut = request.data.get('rut')

        if not email or not rut:
            return Response(
                {'status': 'error', 'message': 'Email y RUT son requeridos.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            usuario = Usuarios.objects.get(email=email, rut=rut)
            codigo = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            usuario.codigo = codigo
            usuario.codigo_expiracion = timezone.now() + timedelta(days=1)
            usuario.save()

            try:
                send_mail(
                    'Tu código de verificación - Terrasoft',
                    f'Tu código de verificación es: {codigo}\n\nEste código expira en 24 horas.',
                    'contacto.terrasoft.23@gmail.com',
                    [usuario.email],
                    fail_silently=False,
                )
                logger.debug(f'PasswordReset generate_code: código enviado a {email}')
                return Response(
                    {'status': 'success', 'message': 'Código enviado exitosamente.'},
                    status=status.HTTP_200_OK
                )
            except Exception as e:
                logger.error(
                    f'PasswordReset generate_code: error enviando email a {email}: {e}',
                    exc_info=True
                )
                return Response(
                    {'status': 'error', 'message': 'Error al enviar el correo.'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        except ObjectDoesNotExist:
            logger.error(f'PasswordReset generate_code: RUT/Email no encontrado {rut}/{email}')
            return Response(
                {'status': 'error', 'message': 'Correo no encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

    def _verify_code(self, request):
        rut = request.data.get('rut')
        codigo = request.data.get('codigo')

        if not rut or not codigo:
            return Response(
                {'status': 'error', 'message': 'RUT y código son requeridos.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            usuario = Usuarios.objects.get(rut=rut, codigo=codigo)

            if usuario.codigo_expiracion and usuario.codigo_expiracion > timezone.now():
                logger.debug(f'PasswordReset verify_code: código verificado para RUT {rut}')
                return Response(
                    {'status': 'success', 'message': 'Código verificado.'},
                    status=status.HTTP_200_OK
                )

            logger.error(f'PasswordReset verify_code: código expirado para RUT {rut}')
            return Response(
                {'status': 'error', 'message': 'El código ha expirado.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        except ObjectDoesNotExist:
            logger.error(f'PasswordReset verify_code: código incorrecto para RUT {rut}')
            return Response(
                {'status': 'error', 'message': 'Código incorrecto.'},
                status=status.HTTP_404_NOT_FOUND
            )

    def _change_password(self, request):
        rut = request.data.get('rut')
        nueva_contrasena = request.data.get('nuevaContrasena')
        codigo = request.data.get('codigo')

        if not rut or not nueva_contrasena:
            return Response(
                {'status': 'error', 'message': 'RUT y contraseña son requeridos.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            usuario = Usuarios.objects.get(rut=rut)

            if not (codigo and usuario.codigo == codigo):
                logger.error(f'PasswordReset change_password: código inválido para RUT {rut}')
                return Response(
                    {'status': 'error', 'message': 'Código inválido.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if not (usuario.codigo_expiracion and usuario.codigo_expiracion > timezone.now()):
                logger.error(f'PasswordReset change_password: código expirado para RUT {rut}')
                return Response(
                    {'status': 'error', 'message': 'Código expirado.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            usuario.set_password(nueva_contrasena)
            usuario.codigo = None
            usuario.codigo_expiracion = None
            usuario.save()
            logger.debug(f'PasswordReset change_password: contraseña actualizada para RUT {rut}')
            return Response(
                {'status': 'success', 'message': 'Contraseña actualizada.'},
                status=status.HTTP_200_OK
            )

        except ObjectDoesNotExist:
            logger.error(f'PasswordReset change_password: usuario no encontrado RUT {rut}')
            return Response(
                {'status': 'error', 'message': 'Usuario no encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

# ==============================================================================
# JWT
# ==============================================================================

class VerifyJWTAPIView(PublicAPIView):

    def post(self, request):
        jwt_token = request.data.get('jwt_token')

        if not jwt_token:
            return Response(
                {'valid': False, 'error': 'Token requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )

        payload = JWTService.decode_jwt(jwt_token)

        if not payload:
            logger.error('VerifyJWT: token inválido o expirado')
            return Response(
                {'valid': False, 'error': 'Token inválido'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        user_id = payload.get('user_id')
        sociedades_list = []

        try:
            user = Usuarios.objects.get(id=user_id)
            sociedades_list = self._build_sociedades(user)
        except Usuarios.DoesNotExist:
            logger.error(f'VerifyJWT: usuario {user_id} no encontrado en DB')

        return Response({
            'valid': True,
            'user_id': payload.get('user_id'),
            'holding_id': payload.get('holding_id'),
            'sociedades': sociedades_list,
            'supervisor_id': payload.get('supervisor_id'),
            'jefe_cuadrilla_id': payload.get('jefe_cuadrilla_id'),
            'nombre': payload.get('nombre_completo'),
            'rut': payload.get('rut'),
            'is_admin': payload.get('is_admin', False),
        }, status=status.HTTP_200_OK)

    def _build_sociedades(self, user):
        if user.is_admin and user.holding:
            sociedades = Sociedad.objects.filter(holding=user.holding, estado=True)
        else:
            sociedades = user.empresas_asignadas.filter(estado=True)

        return [
            {'id': s.id, 'nombre': s.nombre, 'rol_sociedad': s.rol_sociedad or ''}
            for s in sociedades
        ]

class RefreshJWTAPIView(PublicAPIView):

    def post(self, request):
        refresh_token = request.data.get('refresh_token')

        if not refresh_token:
            return Response(
                {'success': False, 'error': 'Refresh token requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )

        new_access_token = JWTService.refresh_token(refresh_token)

        if not new_access_token:
            logger.error('RefreshJWT: refresh token inválido o expirado')
            return Response(
                {'success': False, 'error': 'Refresh token inválido o expirado'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        return Response({'success': True, 'jwt_token': new_access_token}, status=status.HTTP_200_OK)

# ==============================================================================
# LOGIN
# ==============================================================================

class LoginAPIView(PublicAPIView):

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            logger.error(f'Login: datos inválidos: {serializer.errors}')
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        raw_rut = serializer.validated_data['rut']
        clean_rut = ''.join(filter(str.isdigit, raw_rut))

        user = authenticate(username=clean_rut, password=serializer.validated_data['password'])

        if not self._is_user_valid(user):
            logger.error(f'Login: autenticación fallida para RUT {clean_rut}')
            return Response(
                {'autorizado': False, 'mensaje': 'Usuario o contraseña incorrectos'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        validation_response = self._validate_origin_and_version(user, request)
        if validation_response:
            return validation_response

        return self._handle_jwt_authentication(user)

    def _is_user_valid(self, user) -> bool:
        if user is None:
            return False
        if user.is_superuser:
            return True
        return bool(user.perfil and user.perfil.estado)

    def _validate_origin_and_version(self, user, request):
        origin = request.data.get('origin', '').upper()

        if origin == 'MOVIL':
            try:
                version_requerida = Developer.objects.get(id=2).version_movil
                version_cliente = request.data.get('version')
                if version_requerida != version_cliente:
                    return Response({
                        'autorizado': False,
                        'mensaje': f'Usuario debe actualizar la aplicacion a la version {version_requerida}'
                    }, status=status.HTTP_403_FORBIDDEN)
            except Developer.DoesNotExist:
                logger.error('Login: registro Developer id=1 no existe')

        if not user.is_superuser and not user.is_admin and user.perfil:
            if origin == 'MOVIL' and user.perfil.tipo.upper() not in ['MOVIL', 'AMBOS']:
                return Response({
                    'autorizado': False,
                    'mensaje': 'Usuario no tiene acceso a la aplicación móvil'
                }, status=status.HTTP_403_FORBIDDEN)

        return None

    def _handle_jwt_authentication(self, user):
        try:
            jwt_token = JWTService.generate_jwt_for_user(user)
            refresh_token = JWTService.generate_jwt_for_user(user, 'refresh')

            redirect_to = '/super-admin' if user.is_superuser else '/fs/home'

            supervisor_id = None
            try:
                supervisor_id = Supervisores.objects.get(usuario=user).id
            except Supervisores.DoesNotExist:
                pass

            sociedades_list = self._build_sociedades(user)

            response_data = {
                'autorizado': True,
                'mensaje': 'Autenticación exitosa',
                'jwt_token': jwt_token,
                'refresh_token': refresh_token,
                'redirect_to': redirect_to,
                'user_id': user.id,
                'user_type': (
                    'SUPERADMIN' if user.is_superuser
                    else 'ADMIN_HOLDING' if user.is_admin
                    else 'USER_NORMAL'
                ),
                'nombre': self._get_user_display_name(user),
                'holding_id': user.holding.id if user.holding else None,
                'nombre_holding': user.holding.nombre if user.holding else None,
                'sociedades': sociedades_list,
                'supervisor_id': supervisor_id,
                'is_admin': user.is_admin,
            }

            logger.debug(f'Login exitoso: usuario {user.id}, supervisor_id={supervisor_id}')
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(
                f'Login: error generando JWT para usuario {user.id}: {e}',
                exc_info=True
            )
            return Response(
                {'autorizado': False, 'mensaje': 'Error interno al autenticar'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _build_sociedades(self, user):
        if user.is_admin and user.holding:
            sociedades = Sociedad.objects.filter(holding=user.holding, estado=True)
        else:
            sociedades = user.empresas_asignadas.filter(estado=True)

        return [
            {'id': s.id, 'nombre': s.nombre, 'rol_sociedad': s.rol_sociedad or ''}
            for s in sociedades
        ]

    def _get_user_display_name(self, user) -> str:
        if user.persona and user.persona.nombres:
            return user.persona.nombres
        return user.email.split('@')[0]

# ==============================================================================
# SUPERADMIN CHECK
# ==============================================================================

class CheckTokenSuperAdmin(BaseAPIView):
    required_scopes = ['superadmin_access']

    def post(self, request):
        token = request.data.get('token')
        logger.debug(f'CheckTokenSuperAdmin: verificación por usuario {request.user.id}')