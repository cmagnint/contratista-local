# contratista_test_app/jwt_authentication.py
from rest_framework.authentication import BaseAuthentication
from rest_framework.permissions import BasePermission
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import AnonymousUser
from .services.jwt_service import JWTService
from .models import Usuarios


class JWTAuthentication(BaseAuthentication):
    """
    🎯 JWT Authentication Class - Reemplazo directo de OAuth2Authentication
    
    Extrae JWT del header Authorization: Bearer <token>
    Valida el token y retorna usuario autenticado
    """
    
    def authenticate(self, request):
        """
        Autentica el request usando JWT token
        
        Returns:
            tuple: (user, token_payload) si es válido, None si no hay token
        """
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return None  # No hay token, no es error (permite AllowAny)
        
        # Extraer token del header "Bearer <token>"
        try:
            token = auth_header.split(' ')[1]
        except IndexError:
            raise AuthenticationFailed('Token mal formateado')
        
        # Validar y decodificar JWT
        payload = JWTService.decode_jwt(token)
        if not payload:
            raise AuthenticationFailed('Token inválido o expirado')
        
        # Obtener usuario de la BD
        try:
            user_id = payload.get('user_id')
            user = Usuarios.objects.get(id=user_id)
            
            # Verificar que el usuario sigue activo
            if not user.is_active:
                raise AuthenticationFailed('Usuario desactivado')
                
        except Usuarios.DoesNotExist:
            raise AuthenticationFailed('Usuario no encontrado')
        
        # Retornar usuario autenticado y payload (como request.auth)
        return (user, payload)


class JWTHasAnyScope(BasePermission):
    """
    🎯 JWT Scopes Permission - Reemplazo directo de TokenHasAnyScope
    
    Verifica que el usuario JWT tenga al menos uno de los scopes requeridos
    Compatible con el sistema existing de required_scopes
    """
    
    def has_permission(self, request, view):
        """
        Verifica permisos basados en JWT payload
        
        Args:
            request: Request con user autenticado y auth=payload
            view: Vista con required_scopes definidos
            
        Returns:
            bool: True si tiene permisos
        """
        # Verificar que hay usuario autenticado
        if not request.user or request.user.is_anonymous:
            return False
        
        # Verificar que hay payload JWT
        if not request.auth:
            return False
        
        # SUPERADMIN: Acceso total
        if request.user.is_superuser:
            return True
        
        # Obtener scopes requeridos por la vista
        required_scopes = getattr(view, 'required_scopes', [])
        
        if not required_scopes:
            return True  # No requiere scopes específicos
        
        # Mapear permisos del usuario a scopes OAuth2 equivalentes
        user_scopes = self._get_user_scopes(request.user, request.auth)
        
        # Verificar que tenga al menos uno de los scopes requeridos
        return any(scope in user_scopes for scope in required_scopes)
    
    def _get_user_scopes(self, user, jwt_payload):
        """
        Convierte permisos del usuario JWT a scopes OAuth2 equivalentes
        
        Args:
            user: Usuario autenticado
            jwt_payload: Payload del JWT con permisos
            
        Returns:
            list: Lista de scopes equivalentes a OAuth2
        """
        scopes = []
        
        # SUPERADMIN: Todos los scopes
        if user.is_superuser:
            scopes.extend(['superadmin_access', 'admin', 'write', 'read'])
        
        # ADMIN: Scopes de administración
        elif user.is_admin:
            scopes.extend(['admin', 'write', 'read'])
        
        # USER NORMAL: Scopes básicos
        else:
            scopes.extend(['write', 'read'])
        
        return scopes


# ===== CLASE ADICIONAL PARA DEBUGGING =====

class JWTDebugInfo:
    """
    🔍 Utilidad para debugging JWT en desarrollo
    """
    
    @staticmethod
    def print_auth_info(request, view_name=""):
        """
        Imprime información de autenticación para debugging
        """
        print(f"\n🔍 === JWT DEBUG INFO - {view_name} ===")
        print(f"User: {request.user}")
        print(f"Is authenticated: {request.user.is_authenticated}")
        print(f"Is superuser: {getattr(request.user, 'is_superuser', False)}")
        print(f"JWT Payload: {request.auth}")
        
        if hasattr(request, 'META'):
            auth_header = request.META.get('HTTP_AUTHORIZATION', 'None')
            print(f"Auth Header: {auth_header[:50]}...")
        
        print("=== END DEBUG INFO ===\n")