# contratista_test_app/services/jwt_service.py - VERSIÓN ACTUALIZADA CON PERMISOS REALES
import jwt
from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from typing import Dict, List, Optional, Any
from contratista_test_app.models import Usuarios

class JWTService:
    """
    Servicio centralizado para manejar JWT tokens
    Genera, valida y decodifica tokens con claims específicos del negocio
    ✅ ACTUALIZADO: Incluye permisos reales desde la base de datos
    """
    
    # Configuración JWT
    ALGORITHM = 'HS256'
    ACCESS_TOKEN_LIFETIME = timedelta(hours=8)  # 8 horas por defecto
    REFRESH_TOKEN_LIFETIME = timedelta(days=7)   # 7 días para refresh
    
    @classmethod
    def get_secret_key(cls) -> str:
        """
        Obtiene la clave secreta de Django settings
        En producción, esta debe ser una clave fuerte y única
        """
        return settings.SECRET_KEY
    
    @classmethod
    def generate_jwt_for_user(cls, user, token_type: str = 'access') -> str:
        """
        Genera un JWT token para un usuario específico
        ✅ ACTUALIZADO: Incluye permisos reales del perfil
        
        Args:
            user: Instancia del modelo Usuarios
            token_type: 'access' o 'refresh'
            
        Returns:
            str: JWT token firmado
        """
        # Determinar el tipo de usuario y permisos
        user_type, permissions_structure, allowed_routes = cls._get_user_permissions(user)
        
        # Calcular expiración según tipo de token
        if token_type == 'refresh':
            expiration = timezone.now() + cls.REFRESH_TOKEN_LIFETIME
        else:
            expiration = timezone.now() + cls.ACCESS_TOKEN_LIFETIME
        
        # Construir payload con claims
        payload = {
            # Claims estándar JWT
            'exp': int(expiration.timestamp()),
            'iat': int(timezone.now().timestamp()),
            'iss': 'contratista-system',  # Issuer
            'sub': str(user.id),          # Subject (user ID)
            'jti': cls._generate_jti(),   # JWT ID único
            
            # Claims personalizados del negocio
            'user_id': user.id,
            'user_type': user_type,
            'token_type': token_type,
            
            # Información del usuario
            'rut': user.rut,
            'email': user.email,
            'is_superuser': user.is_superuser,
            'is_admin': user.is_admin,
            
            # Información organizacional
            'holding_id': user.holding.id if user.holding else None,
            'holding_name': user.holding.nombre if user.holding else None,
            
            # Información del perfil/persona
            'perfil': {
                'id': user.perfil.id if user.perfil else None,
                'nombre': user.perfil.nombre_perfil if user.perfil else None,
                'tipo': user.perfil.tipo if user.perfil else None,
                'estado': user.perfil.estado if user.perfil else None
            } if user.perfil else None,
            'persona_id': user.persona.id if user.persona else None,
            'nombre_completo': user.persona.nombres if user.persona else user.email,
            
            # ✅ PERMISOS Y RUTAS ACTUALIZADOS
            'permissions': permissions_structure,
            'allowed_routes': allowed_routes,
            
            # Empresas asignadas (para admins que manejan múltiples sociedades)
            'empresas_asignadas': [s.id for s in user.empresas_asignadas.all()] if user.empresas_asignadas else [],
        }
        
        # Generar y firmar token
        token = jwt.encode(payload, cls.get_secret_key(), algorithm=cls.ALGORITHM)
        
        # ✅ LOGGING DETALLADO PARA DEBUG
        print(f"🔐 JWT generado para usuario {user.id} ({user.rut})")
        print(f"👤 Tipo de usuario: {user_type}")
        print(f"📊 Permisos web: {list(permissions_structure.get('web', {}).keys())}")
        print(f"📱 Permisos móvil: {list(permissions_structure.get('movil', {}).keys())}")
        print(f"🛡️ Rutas permitidas: {len(allowed_routes)} rutas")
        
        return token
    
    @classmethod
    def _get_user_permissions(cls, user) -> tuple[str, Dict[str, Any], List[str]]:
        """
        ✅ VERSIÓN ACTUALIZADA: Determina el tipo de usuario y sus permisos basado en el modelo de la BD
        
        Args:
            user: Instancia del modelo Usuarios
            
        Returns:
            Tuple con (user_type, permissions_structure, allowed_routes)
        """
        print(f"🔍 Obteniendo permisos para usuario {user.id} ({user.rut})")
        
        # ✅ SUPERADMIN: Acceso total al sistema
        if user.is_superuser:
            print("👑 Usuario SUPERADMIN detectado")
            return (
                'SUPERADMIN',
                {'superadmin_access': True},
                ['/super-admin']
            )
        
        # ✅ Si no tiene perfil activo, denegar acceso
        if not user.perfil or not user.perfil.estado:
            print("❌ Usuario sin perfil activo")
            return ('INACTIVE', {}, [])
        
        print(f"📋 Perfil encontrado: {user.perfil.nombre_perfil} ({user.perfil.tipo})")
        
        # ✅ Construir estructura de permisos basada en módulos/submódulos del perfil
        permissions_structure = {}
        allowed_routes = ['/fs/home']  # Siempre permitir home
        
        # Obtener tipo de usuario
        user_type = 'ADMIN_HOLDING' if user.is_admin else 'USER_NORMAL'
        
        # ✅ PERMISOS WEB
        if user.perfil.tipo in ['WEB', 'AMBOS']:
            print("🌐 Procesando permisos WEB...")
            web_permissions = {}
            
            # Obtener módulos web del perfil con optimización de consultas
            modulos_web = user.perfil.modulos_web.all().prefetch_related('submodulos')
            print(f"📦 Módulos web encontrados: {[m.nombre for m in modulos_web]}")
            
            for modulo in modulos_web:
                # Obtener submódulos asociados a este módulo desde el perfil
                submodulos_del_modulo = user.perfil.submodulos_web.filter(modulo=modulo)
                submodulos_nombres = [sm.nombre for sm in submodulos_del_modulo]
                
                if submodulos_nombres:  # Solo agregar si tiene submódulos
                    web_permissions[modulo.nombre] = submodulos_nombres
                    print(f"  📂 {modulo.nombre}: {submodulos_nombres}")
                    
                    # ✅ Mapear submódulos a rutas
                    rutas_del_modulo = cls._map_submodulos_to_routes(submodulos_del_modulo)
                    allowed_routes.extend(rutas_del_modulo)
                    print(f"  🛤️ Rutas agregadas: {rutas_del_modulo}")
            
            if web_permissions:
                permissions_structure['web'] = web_permissions
        
        # ✅ PERMISOS MÓVIL  
        if user.perfil.tipo in ['MOVIL', 'AMBOS']:
            print("📱 Procesando permisos MÓVIL...")
            movil_permissions = {}
            
            # Obtener módulos móvil del perfil
            modulos_movil = user.perfil.modulos_movil.all().prefetch_related('submodulos')
            print(f"📦 Módulos móvil encontrados: {[m.nombre for m in modulos_movil]}")
            
            for modulo in modulos_movil:
                # Obtener submódulos asociados a este módulo desde el perfil
                submodulos_del_modulo = user.perfil.submodulos_movil.filter(modulo=modulo)
                submodulos_nombres = [sm.nombre for sm in submodulos_del_modulo]
                
                if submodulos_nombres:  # Solo agregar si tiene submódulos
                    movil_permissions[modulo.nombre] = submodulos_nombres
                    print(f"  📂 {modulo.nombre}: {submodulos_nombres}")
            
            if movil_permissions:
                permissions_structure['movil'] = movil_permissions
        
        print(f"✅ Permisos finales: {permissions_structure}")
        print(f"🛡️ Rutas permitidas: {allowed_routes}")
        
        return (user_type, permissions_structure, allowed_routes)
    
    @classmethod
    def _map_submodulos_to_routes(cls, submodulos) -> List[str]:
        """
        ✅ ACTUALIZADO: Mapea submódulos a rutas específicas del frontend Angular
        
        Args:
            submodulos: QuerySet de submódulos
            
        Returns:
            Lista de rutas permitidas
        """
        # ✅ MAPEO ACTUALIZADO basado en tu app.routes.ts y base de datos
        submodulo_to_route = {
            # ADMINISTRACION
            'PERSONAL': '/fs/personal-empresas',
            'PERFILES': '/fs/administrar-perfiles',
            'USUARIOS': '/fs/administrar-usuarios',
            'AREAS/CARGOS ADMINISTRACION': '/fs/areas-cargos-administracion',
            'PARAMETROS ADMINISTRACION': '/fs/admin-sociedad',
            
            # RECURSOS HUMANOS
            'CONTRATACION PERSONAL': '/fs/autoregistro-personal',
            'CREAR CONTRATO': '/fs/generar-contrato',
            'CONTRATOS FIRMADOS': '/fs/generar-contrato',  # Mismo componente?
            'PRODUCCION TRABAJADOR': '/fs/produccion-trabajador',
            'PARAMETROS RECURSOS HUMANOS': '/fs/r-h-afp',  # O una ruta general de parámetros
            
            # CLIENTES
            'ADMINISTRAR CLIENTES': '/fs/administrar-clientes',
            'AREA/CARGOS CLIENTES': '/fs/administrar-area-cargos-cliente',
            'CONTACTOS': '/fs/administrar-contactos-clientes',
            
            # COMERCIAL
            'ACUERDO COMERCIAL': '/fs/folio-comercial',
            'PARAMETROS COMERCIAL': '/fs/labores-comercial',
            
            # TRANSPORTE
            'TRANSPORTISTAS': '/fs/empresas-transporte',
            'VEHICULOS': '/fs/vehiculos-transporte',
            'CHOFERES': '/fs/choferes-transporte',
            
            # ✅ AGREGAR MÁS SEGÚN TUS RUTAS
            # Puedes expandir este mapeo según vayas añadiendo más funcionalidades
        }
        
        routes = []
        for submodulo in submodulos:
            route = submodulo_to_route.get(submodulo.nombre)
            if route:
                routes.append(route)
            else:
                # ✅ LOG para submódulos sin mapeo
                print(f"⚠️ Submódulo sin mapeo de ruta: '{submodulo.nombre}'")
        
        return routes
    
    @classmethod
    def decode_jwt(cls, token: str) -> Optional[Dict[str, Any]]:
        """
        Decodifica y valida un JWT token
        
        Args:
            token: JWT token string
            
        Returns:
            Dict con el payload si es válido, None si es inválido
        """
        try:
            payload = jwt.decode(
                token, 
                cls.get_secret_key(), 
                algorithms=[cls.ALGORITHM],
                # Verificaciones automáticas
                verify_exp=True,  # Verifica expiración
                verify_iat=True,  # Verifica issued_at
                verify_signature=True  # Verifica firma
            )
            return payload
        except jwt.ExpiredSignatureError:
            print("JWT expirado")
            return None
        except jwt.InvalidTokenError:
            print("JWT inválido")
            return None
        except Exception as e:
            print(f"Error decodificando JWT: {e}")
            return None
    
    @classmethod
    def is_token_valid(cls, token: str) -> bool:
        """
        Verifica si un token es válido sin decodificar completamente
        
        Args:
            token: JWT token string
            
        Returns:
            bool: True si es válido, False en caso contrario
        """
        return cls.decode_jwt(token) is not None
    
    @classmethod
    def refresh_token(cls, refresh_token: str) -> Optional[str]:
        """
        Genera un nuevo access token usando un refresh token válido
        
        Args:
            refresh_token: Refresh token JWT
            
        Returns:
            Nuevo access token o None si refresh token es inválido
        """
        payload = cls.decode_jwt(refresh_token)
        if not payload or payload.get('token_type') != 'refresh':
            return None
        
        # Buscar usuario y generar nuevo access token
        try:
            user = Usuarios.objects.get(id=payload['user_id'])
            return cls.generate_jwt_for_user(user, 'access')
        except Usuarios.DoesNotExist:
            return None
    
    @classmethod
    def _generate_jti(cls) -> str:
        """
        Genera un JWT ID único para prevenir replay attacks
        """
        import uuid
        return str(uuid.uuid4())
    
    @classmethod
    def extract_user_info_from_token(cls, token: str) -> Optional[Dict[str, Any]]:
        """
        Extrae información útil del usuario desde el token para uso en vistas
        
        Args:
            token: JWT token string
            
        Returns:
            Dict con información del usuario o None
        """
        payload = cls.decode_jwt(token)
        if not payload:
            return None
        
        return {
            'user_id': payload.get('user_id'),
            'user_type': payload.get('user_type'),
            'holding_id': payload.get('holding_id'),
            'is_superuser': payload.get('is_superuser', False),
            'is_admin': payload.get('is_admin', False),
            'permissions': payload.get('permissions', {}),  # Ahora es un dict, no lista
            'allowed_routes': payload.get('allowed_routes', []),
            'rut': payload.get('rut'),
            'nombre_completo': payload.get('nombre_completo'),
            'perfil': payload.get('perfil', {}),
        }

    @classmethod
    def get_user_modules(cls, token: str, module_type: str = 'web') -> List[str]:
        """
        ✅ NUEVO: Obtiene los módulos disponibles para un usuario desde el token
        
        Args:
            token: JWT token
            module_type: 'web' o 'movil'
            
        Returns:
            Lista de nombres de módulos
        """
        payload = cls.decode_jwt(token)
        if not payload:
            return []
        
        permissions = payload.get('permissions', {})
        module_permissions = permissions.get(module_type, {})
        
        return list(module_permissions.keys())
    
    @classmethod
    def can_user_access_module(cls, token: str, module_name: str, module_type: str = 'web') -> bool:
        """
        ✅ NUEVO: Verifica si el usuario puede acceder a un módulo específico
        
        Args:
            token: JWT token
            module_name: Nombre del módulo (ej: 'ADMINISTRACION')
            module_type: 'web' o 'movil'
            
        Returns:
            bool: True si tiene acceso
        """
        payload = cls.decode_jwt(token)
        if not payload:
            return False
        
        # Superadmins tienen acceso total
        if payload.get('is_superuser'):
            return True
        
        permissions = payload.get('permissions', {})
        module_permissions = permissions.get(module_type, {})
        
        return module_name in module_permissions
    
    @classmethod
    def can_user_access_submodule(cls, token: str, module_name: str, submodule_name: str, module_type: str = 'web') -> bool:
        """
        ✅ NUEVO: Verifica si el usuario puede acceder a un submódulo específico
        
        Args:
            token: JWT token
            module_name: Nombre del módulo padre
            submodule_name: Nombre del submódulo
            module_type: 'web' o 'movil'
            
        Returns:
            bool: True si tiene acceso
        """
        payload = cls.decode_jwt(token)
        if not payload:
            return False
        
        # Superadmins tienen acceso total
        if payload.get('is_superuser'):
            return True
        
        permissions = payload.get('permissions', {})
        module_permissions = permissions.get(module_type, {})
        submodules = module_permissions.get(module_name, [])
        
        return submodule_name in submodules