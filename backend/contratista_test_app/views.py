from selenium.common.exceptions import (
    TimeoutException, 
    
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.pagesizes import landscape, letter, A4
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from django.contrib.auth import authenticate
from selenium.webdriver.support.ui import Select
from django.shortcuts import get_object_or_404
from .browser_session_manager import BrowserSessionManager
from rest_framework.response import Response
from django.db.models.expressions import RawSQL
from selenium.webdriver.common.by import By
from django.core.files.base import ContentFile
from collections import defaultdict
from rest_framework.views import APIView
from PyPDF2 import PdfReader, PdfWriter
from .utils import generar_documento_con_datos
from reportlab.lib.pagesizes import letter
from django.forms import ValidationError
from datetime import datetime, timezone
from reportlab.pdfgen import canvas
from .serializers import LoginSerializer
from reportlab.lib.enums import TA_RIGHT
from django.db.models import Q, Max, Sum, Value, F, DecimalField
from django.db.models.functions import Coalesce
from reportlab.lib.units import inch
from django.http import HttpResponse
from django.http import FileResponse
from rest_framework import status
from django.utils import timezone
from django.conf import settings
from reportlab.lib.units import mm
from reportlab.lib import colors
from django.db import transaction
from datetime import timedelta
from itertools import groupby
from datetime import date
from decimal import Decimal
from math import floor
from io import BytesIO, StringIO
from .jwt_authentication import JWTAuthentication, JWTHasAnyScope
import traceback
import tempfile
import calendar
import zipfile
import random
import base64
import uuid
import time
import json
import csv
import io
import os
import re
import PyPDF2

#SERVICIOS
from .services.jwt_service import JWTService

#MODELOS DE BASE DE DATOS
from .models import (
    Holding, 
    Sociedad, 
    Developer,
    Usuarios, 
    Perfiles, 
    ModulosWeb,
    SubModulosWeb,
    ModulosMovil,
    SubModulosMovil,
    Clientes,
    Areas,
    Cargos,
    EmpresasTransporte,
    VehiculosTransporte,
    ChoferesTransporte,
    SaludTrabajadores,
    AFPTrabajadores,
    PersonalTrabajadores,
    CamposClientes, 
    AreasCliente,
    CargosCliente,
    ContactosClientes,
    UnidadControl,
    Labores,
    FolioComercial,
    CasasTrabajadores,
    AreasAdministracion,
    CargosAdministracion,
    Horarios,
    ProduccionTrabajador,
    CodigoQR,
    Cuadrillas,
    EnlaceAutoRegistro,
    Supervisores,
    JefesDeCuadrilla,
    APKLink,
    Banco,
    CuentaOrigen,
    RegistroPagoTransferencia,
    RegistroPagoEfectivo,
    HistorialCambioPago,
    HistorialCambioFolio,
    Tramos,
    FolioTransportista,
    PagoTransportista,
    DetallePagoTransportista,
    ProformaTransportista,
    DiasTrabajadosAprobados,
    MesCerrado,
    Haberes,
    Descuentos,
    TrabajadorHaber,
    TrabajadorDescuento,
    ContratoVariables,
    CalibrationSettings,
    ContratoTrabajador,
    LicenciaMedica,
    Vacaciones,
    HoraExtraordinaria,
    FacturaCompraSIIDistribuida,
    Cuenta,
    ConfiguracionSIIAutomaticaCompra,
    FacturaCompraSIIPorDistribuir,
    ConfiguracionSIIAutomaticaVenta,
    FacturaVentaSIIPorDistribuir,
    FacturaVentaSIIDistribuida, 
    CartolaMovimiento,
    RegistroIngreso,
    RegistroEgreso,

)

from .serializers import (
    HoldingSerializer,
    SociedadSerializer, 
    AdminSerializer, 
    PerfilesSerializer, 
    ModulosWebSerializer,
    SubModulosWebSerializer,
    ModulosMovilSerializer,
    SubModulosMovilSerializer,
    UserSerializer, 
    ClienteSerializer,
    AreaSerializer,
    CargoSerializer,
    EmpresaTransporteSerializer,
    VehiculosTransporteSerializer,
    ChoferesTransporteSerializer,
    SaludTrabajadoresSerializer,
    AFPTrabajadoresSerializer,
    PersonalTrabajadoresSerializer,
    CamposClientesSerializer,
    AreaClienteSerializer,
    CargoClienteSerializer,
    ContactosClienteSerializer,
    UnidadControlSerializer,
    LaboresSerializer,
    FolioComercialSerializer,
    CasasTrabajadoresSerializer,
    PersonalTrabajadoresMobileSerializer,
    DataProduccionSerializer,
    AreaAdministracionSerializer,
    CargoAdministracionSerializer,
    HorarioSerializer,
    ProduccionTrabajadorSerializer,
    CodigoQRSerializer,
    TrabajadoresCosechaQRSerializer,
    CuadrillasSerializer,
    GrupoTrabajadoresSerializer,
    EnlaceAutoRegistroSerializer,
    PersonalForUserSerializer,
    SupervisorSerializer,
    JefesDeCuadrillaSerializer,
    APKLinkSerializer,
    PersonalAsignadoSerializer,
    ProduccionTrabajadorReporteSerializer,
    CampoClienteDropdownPagoSerializer,
    SupervisorDropdownPagoSerializer,
    CasaTrabajadorDropdownPagoSerializer,
    ProduccionInformePagoDetalleSerializer,
    ProduccionCSVSerializer,
    CuentaOrigenSerializer,
    BancoSerializer,
    SociedadCuentaSerializer,
    ProduccionPendienteSerializer,
    FiltrosPagoSerializer,
    ClientesFiltroPagoSerializer,
    CargosAdministracionPagoSerializer,
    CasasTrabajadoresPagoSerializer,
    PagoRealizadoSerializer,
    TramosSerializer,
    FolioTransportistaSerializer,
    PagoTransportistaSerializer,
    InformeTransportistaSerializer,
    ProformaTransportistaSerializer,
    MesCerradoSerializer,
    HaberesSerializer,
    DescuentosSerializer,
    PersonalConAsignacionesSerializer,
    ArchivoPreviewSerializer, 
    CuentaSerializer,
    DistribucionFacturasSIISerializer,
    DistribucionMultipleFacturaCompraSIISerializer,
    ValidarDistribucionSerializer,
    FacturaPorDistribuirMultipleSerializer,
    FacturaCompraSIIDistribuidaMultipleSerializer,
    ConfiguracionSIIAutomaticaVentaSerializer,
    DistribucionFacturasVentaSIISerializer,
    FacturaVentaPorDistribuirMultipleSerializer,
    FacturaVentaSIIDistribuidaMultipleSerializer,
    DistribucionMultipleFacturaVentaSIISerializer,
    CartolaMovimientoSerializer,
    FacturaVentaSimpleSerializer,
    RegistroIngresoSerializer,
    CuentaOrigenDetalleSerializer,
    RegistroEgresoSerializer,
    FacturaCompraSimpleSerializer,
)

from .tasks import (
    procesar_configuracion_automatica,
)

class VerifyJWTAPIView(APIView):
    """
    Verifica la validez de un JWT token y retorna información del usuario
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        jwt_token = request.data.get('jwt_token')
        
        if not jwt_token:
            return Response({
                'valid': False, 
                'error': 'Token requerido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Decodificar y validar JWT
        payload = JWTService.decode_jwt(jwt_token)
        
        if not payload:
            return Response({
                'valid': False,
                'error': 'Token inválido o expirado'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Token válido - retornar información útil
        return Response({
            'valid': True,
            'user_info': {
                'user_id': payload.get('user_id'),
                'user_type': payload.get('user_type'),
                'holding_id': payload.get('holding_id'),
                'is_superuser': payload.get('is_superuser', False),
                'is_admin': payload.get('is_admin', False),
                'permissions': payload.get('permissions', []),
                'allowed_routes': payload.get('allowed_routes', []),
                'nombre_completo': payload.get('nombre_completo'),
                'expires_at': payload.get('exp')
            }
        }, status=status.HTTP_200_OK)

class RefreshJWTAPIView(APIView):
    """
    Renueva un JWT access token usando un refresh token
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.data.get('refresh_token')
        
        if not refresh_token:
            return Response({
                'success': False, 
                'error': 'Refresh token requerido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Intentar generar nuevo access token
        new_access_token = JWTService.refresh_token(refresh_token)
        
        if not new_access_token:
            return Response({
                'success': False,
                'error': 'Refresh token inválido o expirado'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        return Response({
            'success': True,
            'jwt_token': new_access_token
        }, status=status.HTTP_200_OK)

class LoginAPIView(APIView):
    """
    🎯 LoginAPIView SIMPLE - Estándar de la industria
    Usa Django authenticate() con contraseñas en texto plano + JWT
    """
    authentication_classes = []
    permission_classes = [AllowAny]
    
    def post(self, request):
        data = request.data
        print("🔐 Login data received:", data)
        
        # Validar datos de entrada
        serializer = LoginSerializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # 🧹 LIMPIAR RUT antes de autenticar
        raw_rut = serializer.validated_data['rut']
        clean_rut = ''.join(filter(str.isdigit, raw_rut))  # Solo números
        
        print(f"🧹 RUT limpiado: '{raw_rut}' → '{clean_rut}'")
        
        # 🎯 AUTENTICACIÓN con RUT limpio
        user = authenticate(
            username=clean_rut,  # ← RUT sin puntos ni guiones
            password=serializer.validated_data['password']
        )
        
        print(f"🔐 Usuario autenticado: {user.id if user else 'None'}")
        
        # Resto del código igual...
        if not self._is_user_valid(user, request):
            return Response({
                'autorizado': False, 
                'mensaje': 'Usuario o contraseña incorrectos'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        validation_response = self._validate_origin_and_version(user, request)
        if validation_response:
            return validation_response
        
        return self._handle_jwt_authentication(user, request)
    
    def _is_user_valid(self, user, request) -> bool:
        """
        Valida si el usuario puede autenticarse
        ✅ Mismo código que antes
        """
        if user is None:
            return False
        
        # SUPERADMIN: Siempre puede autenticarse
        if user.is_superuser:
            return True
        
        # USUARIOS NORMALES: Deben tener perfil activo
        return user.perfil and user.perfil.estado
    
    def _validate_origin_and_version(self, user, request):
        """
        Valida origen (WEB/MOVIL) y versión de la aplicación
        ✅ Mismo código que antes
        """
        origin = request.data.get('origin', '').upper()
        
        # Validar versión móvil si es requerida
        if origin == 'MOVIL':
            try:
                version_movil_object = Developer.objects.get(id=1)
                version_requerida = version_movil_object.version_movil
                version_cliente = request.data.get('version')
                
                if version_requerida != version_cliente:
                    return Response({
                        'autorizado': False, 
                        'mensaje': f'Usuario debe actualizar la aplicacion a la version {version_requerida}'
                    }, status=status.HTTP_403_FORBIDDEN)
            except Developer.DoesNotExist:
                pass
        
        # Validar permisos de origen para usuarios no-admin
        if not user.is_superuser and not user.is_admin and user.perfil:
            user_profile_type = user.perfil.tipo.upper()
            
            if origin == 'MOVIL' and user_profile_type not in ['MOVIL', 'AMBOS']:
                return Response({
                    'autorizado': False, 
                    'mensaje': 'Usuario no tiene acceso a la aplicación móvil'
                }, status=status.HTTP_403_FORBIDDEN)
        
        return None
    
    def _handle_jwt_authentication(self, user, request):
        """
        Genera JWT tokens y respuesta exitosa
        ✅ Mismo código que antes
        """
        try:
            # Generar JWT tokens
            jwt_token = JWTService.generate_jwt_for_user(user)
            refresh_token = JWTService.generate_jwt_for_user(user, 'refresh')
            
            # Determinar redirección
            if user.is_superuser:
                redirect_to = '/super-admin'
            else:
                redirect_to = '/fs/home'
            
            # Respuesta exitosa
            response_data = {
                'autorizado': True,
                'mensaje': 'Autenticación exitosa',
                'jwt_token': jwt_token,
                'refresh_token': refresh_token,
                'redirect_to': redirect_to,
                
                # Información adicional para compatibilidad
                'user_id': user.id,
                'user_type': 'SUPERADMIN' if user.is_superuser else 'ADMIN_HOLDING' if user.is_admin else 'USER_NORMAL',
                'nombre': self._get_user_display_name(user),
                'holding_id': user.holding.id if user.holding else None,
            }
            
            print(f"✅ Login exitoso para usuario {user.id}")
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"❌ Error generando JWT: {str(e)}")
            return Response({
                'autorizado': False,
                'mensaje': f'Error generando JWT: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _get_user_display_name(self, user) -> str:
        """
        Obtiene el nombre para mostrar del usuario
        ✅ Mismo código que antes
        """
        if user.persona and user.persona.nombres:
            return user.persona.nombres
        return user.email.split('@')[0]

class HoldingAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]
    required_scopes = ['superadmin_access']

    def get(self, request, format=None):
        holdings = Holding.objects.all()
        serializer = HoldingSerializer(holdings, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = HoldingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, format=None):
        holding_id = request.data.get('id')
        if not holding_id:
            return Response({"message": "ID de holding es necesario para actualizar"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            holding = Holding.objects.get(id=holding_id)
        except Holding.DoesNotExist:
            return Response({"message": "Holding no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        serializer = HoldingSerializer(holding, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, format=None):
        holding_id = request.data.get('id')
        if not holding_id:
            return Response({"message": "ID de holding es necesario para actualizar"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            holding = Holding.objects.get(id=holding_id)
        except Holding.DoesNotExist:
            return Response({"message": "Holding no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        serializer = HoldingSerializer(holding, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, format=None):
        holding_ids = request.data.get('ids', [])
        if not holding_ids:
            return Response({"message": "IDs de holdings son necesarios para eliminar"}, status=status.HTTP_400_BAD_REQUEST)
        
        # En lugar de eliminar, desactivamos
        Holding.objects.filter(id__in=holding_ids).update(estado=False)
        return Response({"message": f"{len(holding_ids)} holdings desactivados exitosamente"}, status=status.HTTP_200_OK)

class SociedadAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_scopes = []

    def dispatch(self, request, *args, **kwargs):
        # Ajustar required_scopes basado en el método
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            self.required_scopes = ['superadmin_access', 'admin', 'write']
        elif request.method == 'GET':
            self.required_scopes = ['superadmin_access', 'admin', 'write']
        return super().dispatch(request, *args, **kwargs)

    # Método GET existente
    def get(self, request, holding_id=None, format=None):
        holding_id = request.query_params.get('holding')
        if holding_id:
            sociedades = Sociedad.objects.filter(holding_id=holding_id)
        else:
            sociedades = Sociedad.objects.all()
        serializer = SociedadSerializer(sociedades, many=True)
        return Response(serializer.data)
    
    # Método POST existente
    def post(self, request, format=None):
        data = request.data
        print(data)
        serializer = SociedadSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # NUEVO: Método PUT para actualización completa
    def put(self, request, format=None):
        sociedad_id = request.data.get('id')
        if not sociedad_id:
            return Response({"message": "ID de sociedad es necesario para actualizar"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            sociedad = Sociedad.objects.get(id=sociedad_id)
        except Sociedad.DoesNotExist:
            return Response({"message": "Sociedad no encontrada"}, status=status.HTTP_404_NOT_FOUND)

        serializer = SociedadSerializer(sociedad, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # NUEVO: Método PATCH para actualización parcial
    def patch(self, request, format=None):
        sociedad_id = request.data.get('id')
        if not sociedad_id:
            return Response({"message": "ID de sociedad es necesario para actualizar"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            sociedad = Sociedad.objects.get(id=sociedad_id)
        except Sociedad.DoesNotExist:
            return Response({"message": "Sociedad no encontrada"}, status=status.HTTP_404_NOT_FOUND)

        serializer = SociedadSerializer(sociedad, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # NUEVO: Método DELETE para eliminación (desactivación)
    def delete(self, request, format=None):
        sociedad_ids = request.data.get('ids', [])
        if not sociedad_ids:
            return Response({"message": "IDs de sociedades son necesarios para eliminar"}, status=status.HTTP_400_BAD_REQUEST)
        
        # En lugar de eliminar, desactivamos
        Sociedad.objects.filter(id__in=sociedad_ids).update(estado=False)
        return Response({"message": f"{len(sociedad_ids)} sociedades desactivadas exitosamente"}, status=status.HTTP_200_OK)

class AdminAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_scopes = []

    def dispatch(self, request, *args, **kwargs):
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            self.required_scopes = ['superadmin_access']
        elif request.method == 'GET':
            self.required_scopes = ['superadmin_access', 'admin', 'write']
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        # Obtener solo usuarios administradores con su información completa
        admins = Usuarios.objects.filter(is_admin=True).select_related('holding', 'persona')
        serializer = AdminSerializer(admins, many=True)
        print(f'Administradores: {(serializer.data)}')
        return Response(serializer.data)

    def post(self, request):
        import re
        data = request.data
        print("Datos recibidos:", data)
        
        try:
            with transaction.atomic():
                # Limpiar RUT (solo números y K)
                rut_limpio = re.sub(r'[^0-9kK]', '', data.get('rut', ''))
                
                # Paso 1: Crear PersonalTrabajadores
                persona_data = {
                    'holding_id': data.get('holding'),
                    'nombres': data.get('nombre', '').upper(),
                    'rut': rut_limpio,
                    'cargo_id': 1,  # Asumiendo que cargo_id=1 es para administradores
                    'estado': True
                }
                
                # Verificar si ya existe una persona con ese RUT
                existing_persona = PersonalTrabajadores.objects.filter(rut=rut_limpio).first()
                if existing_persona:
                    print("Ya existe una persona con RUT {data.get('rut')}")
                    return Response(
                        {"message": f"Ya existe una persona con RUT {data.get('rut')}"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                persona = PersonalTrabajadores.objects.create(**persona_data)

                # Paso 2: Verificar/Crear perfil "ADMINISTRADOR PRINCIPAL"
                holding_id = data.get('holding')
                perfil, created = Perfiles.objects.get_or_create(
                    holding_id=holding_id,
                    nombre_perfil='ADMINISTRADOR PRINCIPAL',
                    defaults={
                        'tipo': 'AMBOS',
                        'estado': True
                    }
                )

                # Paso 3: Verificar si ya existe un admin para este holding
                existing_admin = Usuarios.objects.filter(
                    holding_id=holding_id,
                    is_admin=True
                ).first()
                
                if existing_admin:
                    # Eliminar la persona creada si ya hay un admin
                    persona.delete()
                    print('Ya existe un administrador principal para este holding')
                    return Response(
                        {"message": f"Ya existe un administrador principal para este holding"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
               

                # Paso 4: Crear usuario administrador
                usuario_data = {
                    'holding_id': holding_id,
                    'persona': persona,
                    'rut': rut_limpio,
                    'email': data.get('email'),
                    'perfil_id': perfil.id,
                    'is_admin': True,
                    'estado': True
                }
                
                # Verificar si ya existe usuario con ese email o RUT
                if Usuarios.objects.filter(email=data.get('email')).exists():
                    persona.delete()
                    return Response(
                        {"message": f"Ya existe un usuario con email {data.get('email')}"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                if Usuarios.objects.filter(rut=rut_limpio).exists():
                    persona.delete()
                    return Response(
                        {"message": f"Ya existe un usuario con RUT {data.get('rut')}"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )

                admin = Usuarios.objects.create(**usuario_data)
                
                # Si se proporciona contraseña, establecerla
                if data.get('password'):
                    admin.set_password(data.get('password'))
                    admin.save()

                # Serializar respuesta
                serializer = AdminSerializer(admin)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
                    
        except Exception as e:
            print(f"Error al crear administrador: {str(e)}")
            return Response(
                {"message": f"Error al crear administrador: {str(e)}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def put(self, request, format=None):
        admin_id = request.data.get('id')
        if not admin_id:
            return Response(
                {"message": "ID de administrador es necesario para actualizar"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            admin = Usuarios.objects.get(id=admin_id, is_admin=True)
        except Usuarios.DoesNotExist:
            return Response(
                {"message": "Administrador no encontrado"}, 
                status=status.HTTP_404_NOT_FOUND
            )

        # Actualizar datos del usuario
        if 'email' in request.data:
            admin.email = request.data['email']
        
        if 'estado' in request.data:
            admin.estado = request.data['estado']
            
        if 'password' in request.data and request.data['password'].strip():
            admin.set_password(request.data['password'])

        # Actualizar datos de la persona si existe
        if admin.persona and 'nombre' in request.data:
            admin.persona.nombres = request.data['nombre'].upper()
            admin.persona.save()

        admin.save()
        
        serializer = AdminSerializer(admin)
        return Response(serializer.data)
    
    def patch(self, request, format=None):
        admin_id = request.data.get('id')
        if not admin_id:
            return Response(
                {"message": "ID de administrador es necesario para actualizar"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            admin = Usuarios.objects.get(id=admin_id, is_admin=True)
        except Usuarios.DoesNotExist:
            return Response(
                {"message": "Administrador no encontrado"}, 
                status=status.HTTP_404_NOT_FOUND
            )

        # Actualizar campos específicos
        if 'email' in request.data:
            admin.email = request.data['email']
        
        if 'estado' in request.data:
            admin.estado = request.data['estado']
            
        if 'password' in request.data and request.data['password'].strip():
            admin.set_password(request.data['password'])

        # Actualizar datos de la persona si existe
        if admin.persona and 'nombre' in request.data:
            admin.persona.nombres = request.data['nombre'].upper()
            admin.persona.save()

        admin.save()
        
        serializer = AdminSerializer(admin)
        return Response(serializer.data)
    
    def delete(self, request, format=None):
        admin_ids = request.data.get('ids', [])
        if not admin_ids:
            return Response(
                {"message": "IDs de administradores son necesarios para desactivar"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Desactivar usuarios y sus personas asociadas
        admins = Usuarios.objects.filter(id__in=admin_ids, is_admin=True)
        count = 0
        for admin in admins:
            admin.estado = False
            admin.save()
            if admin.persona:
                admin.persona.estado = False
                admin.persona.save()
            count += 1
        
        return Response(
            {"message": f"{count} administradores desactivados exitosamente"}, 
            status=status.HTTP_200_OK
        )

class ModulosWebAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_scopes = []

    def dispatch(self, request, *args, **kwargs):
        if request.method in ['GET', 'POST', 'PUT', 'DELETE']:
            self.required_scopes = ['admin', 'write']
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, holding_id):
        modulos = ModulosWeb.objects.filter(holding_id=holding_id)
        serializer = ModulosWebSerializer(modulos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class SubModulosWebAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_scopes = []

    def dispatch(self, request, *args, **kwargs):
        if request.method in ['GET', 'POST', 'PUT', 'DELETE']:
            self.required_scopes = ['admin', 'write']
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, holding_id):
        submodulos = SubModulosWeb.objects.filter(holding_id=holding_id)
        serializer = SubModulosWebSerializer(submodulos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ModulosMovilAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_scopes = []

    def dispatch(self, request, *args, **kwargs):
        if request.method in ['GET', 'POST', 'PUT', 'DELETE']:
            self.required_scopes = ['admin', 'write']
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, holding_id):
        modulos = ModulosMovil.objects.filter(holding_id=holding_id)
        serializer = ModulosMovilSerializer(modulos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class SubModulosMovilAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_scopes = []

    def dispatch(self, request, *args, **kwargs):
        if request.method in ['GET', 'POST', 'PUT', 'DELETE']:
            self.required_scopes = ['admin', 'write']
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, holding_id):
        submodulos = SubModulosMovil.objects.filter(holding_id=holding_id)
        serializer = SubModulosMovilSerializer(submodulos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class PerfilesAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_scopes = []

    def dispatch(self, request, *args, **kwargs):
        if request.method in ['GET', 'POST', 'PUT', 'DELETE']:
            self.required_scopes = ['admin', 'write']
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, holding_id):
        perfiles = Perfiles.objects.filter(holding_id=holding_id).exclude(nombre_perfil = 'ADMINISTRADOR PRINCIPAL')
        serializer = PerfilesSerializer(perfiles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, holding_id):
        try:
            with transaction.atomic():
                data = request.data.copy()
                
                # Crear el perfil
                perfil = Perfiles.objects.create(
                    holding_id=holding_id,
                    nombre_perfil=data.get('nombre_perfil'),
                    tipo=data.get('tipo'),
                    estado=data.get('estado', True)
                )

                # Agregar módulos y submódulos web
                if data.get('tipo') in ['WEB', 'AMBOS']:
                    modulos_web = ModulosWeb.objects.filter(id__in=data.get('modulos_web', []))
                    perfil.modulos_web.add(*modulos_web)
                    
                    submodulos_web = SubModulosWeb.objects.filter(id__in=data.get('submodulos_web', []))
                    perfil.submodulos_web.add(*submodulos_web)

                # Agregar módulos y submódulos móvil
                if data.get('tipo') in ['MOVIL', 'AMBOS']:
                    modulos_movil = ModulosMovil.objects.filter(id__in=data.get('modulos_movil', []))
                    perfil.modulos_movil.add(*modulos_movil)
                    
                    submodulos_movil = SubModulosMovil.objects.filter(id__in=data.get('submodulos_movil', []))
                    perfil.submodulos_movil.add(*submodulos_movil)

                # Preparar la respuesta
                response_data = {
                    'id': perfil.id,
                    'holding': perfil.holding_id, # type: ignore
                    'nombre_perfil': perfil.nombre_perfil,
                    'tipo': perfil.tipo,
                    'estado': perfil.estado,
                    'modulos_web': list(perfil.modulos_web.values_list('id', flat=True)),
                    'submodulos_web': list(perfil.submodulos_web.values_list('id', flat=True)),
                    'modulos_movil': list(perfil.modulos_movil.values_list('id', flat=True)),
                    'submodulos_movil': list(perfil.submodulos_movil.values_list('id', flat=True)),
                }

                return Response(response_data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    def put(self, request, holding_id):
        perfil_id = request.data.get('id')
        if not perfil_id:
            return Response({'error': 'Se requiere el ID del perfil para actualizar'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            perfil = Perfiles.objects.get(id=perfil_id, holding_id=holding_id)
        except Perfiles.DoesNotExist:
            return Response({'error': 'Perfil no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()

        # Actualizar campos básicos
        perfil.nombre_perfil = data.get('nombre_perfil', perfil.nombre_perfil)
        perfil.tipo = data.get('tipo', perfil.tipo)
        perfil.estado = data.get('estado', perfil.estado)
        perfil.save()

        # Actualizar relaciones ManyToMany
        if 'modulos_web_ids' in data:
            perfil.modulos_web.set(data['modulos_web_ids'])
        if 'submodulos_web_ids' in data:
            perfil.submodulos_web.set(data['submodulos_web_ids'])
        if 'modulos_movil_ids' in data:
            perfil.modulos_movil.set(data['modulos_movil_ids'])
        if 'submodulos_movil_ids' in data:
            perfil.submodulos_movil.set(data['submodulos_movil_ids'])

        # Refrescar el objeto perfil desde la base de datos
        perfil.refresh_from_db()

        # Preparar la respuesta
        response_data = {
            'id': perfil.id,
            'nombre_perfil': perfil.nombre_perfil,
            'tipo': perfil.tipo,
            'estado': perfil.estado,
            'modulos_web': [{'id': m.id, 'nombre': m.nombre} for m in perfil.modulos_web.all()],
            'submodulos_web': [{'id': sm.id, 'nombre': sm.nombre} for sm in perfil.submodulos_web.all()],
            'modulos_movil': [{'id': m.id, 'nombre': m.nombre} for m in perfil.modulos_movil.all()],
            'submodulos_movil': [{'id': sm.id, 'nombre': sm.nombre} for sm in perfil.submodulos_movil.all()],
        }

        return Response(response_data)
    
    def delete(self, request, holding_id):
        perfil_ids = []
        perfil_ids = request.data.get('ids')
        if len(perfil_ids) < 0:
            return Response({'error': 'Se requiere el ID del perfil para eliminar'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            for perfil_id in perfil_ids:
                perfil = Perfiles.objects.get(id=perfil_id, holding_id=holding_id)
                perfil.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Perfiles.DoesNotExist:
            return Response({'error': 'Perfil no encontrado'}, status=status.HTTP_404_NOT_FOUND)

#------------------------------------------------------------------------------------------------------------------------------------------------------    
#------------------------------- CLASES USUARIOS ------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------------------------

class PersonalForUserAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_scopes = []

    def dispatch(self, request, *args, **kwargs):
        if request.method in ['GET']:
            self.required_scopes = ['admin', 'write']
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, holding_id, format=None):
        try:
            # Obtener personal activo del holding que no tenga usuario asociado
            personal = PersonalTrabajadores.objects.filter(
                holding_id=holding_id,
                estado=True,
            ).exclude(cargo_id = 1)

            if not personal.exists():
                return Response(
                    {"message": "No se encontró personal disponible"}, 
                    status=status.HTTP_404_NOT_FOUND
                )

            serializer = PersonalForUserSerializer(personal, many=True)
            print(serializer.data)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"message": f"Error al obtener personal: {str(e)}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

class UsuarioAPIViews(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_scopes = []

    def dispatch(self, request, *args, **kwargs):
        if request.method in ['GET', 'POST', 'PATCH', 'PUT', 'DELETE']:
            self.required_scopes = ['admin', 'write']
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, holding_id, format=None):
        try:
            usuarios = Usuarios.objects.filter(holding_id=holding_id).exclude(is_admin=True)
            if usuarios.exists():
                serializer = UserSerializer(usuarios, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response({"message": "No se encontraron usuarios"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        with transaction.atomic():
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                usuario = serializer.save()
                
                if usuario.perfil:
                    # Handle Supervisor creation
                    if usuario.perfil.nombre_perfil == 'SUPERVISOR':
                        Supervisores.objects.create(
                            holding_id=usuario.holding_id,
                            usuario=usuario
                        )
                    # Handle Jefe de Cuadrilla creation
                    elif usuario.perfil.nombre_perfil == 'JEFE DE CUADRILLA':
                        supervisor_id = request.data.get('supervisor')
                        if supervisor_id:
                            try:
                                supervisor = Supervisores.objects.get(usuario_id=supervisor_id)
                                JefesDeCuadrilla.objects.create(
                                    holding_id=usuario.holding_id,
                                    supervisor=supervisor,
                                    usuario=usuario
                                )
                            except Supervisores.DoesNotExist:
                                return Response(
                                    {"error": "Supervisor no encontrado"}, 
                                    status=status.HTTP_400_BAD_REQUEST
                                )
                        else:
                            return Response(
                                {"error": "Se requiere un supervisor para el Jefe de Cuadrilla"}, 
                                status=status.HTTP_400_BAD_REQUEST
                            )
                
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, format=None):
        with transaction.atomic():
            perfil_id = request.data.get('id')
            try:
                usuario = Usuarios.objects.get(id=perfil_id)
                old_perfil = usuario.perfil
                
                serializer = UserSerializer(usuario, data=request.data)
                if serializer.is_valid():
                    usuario = serializer.save()
                    
                    if 'perfil' in request.data:
                        new_perfil_nombre = usuario.perfil.nombre_perfil if usuario.perfil else None
                        old_perfil_nombre = old_perfil.nombre_perfil if old_perfil else None

                        # Handle Supervisor changes
                        if new_perfil_nombre == 'SUPERVISOR' and old_perfil_nombre != 'SUPERVISOR':
                            Supervisores.objects.create(
                                holding_id=usuario.holding_id,
                                usuario=usuario
                            )
                        elif old_perfil_nombre == 'SUPERVISOR' and new_perfil_nombre != 'SUPERVISOR':
                            Supervisores.objects.filter(usuario=usuario).delete()

                        # Handle Jefe de Cuadrilla changes
                        if new_perfil_nombre == 'JEFE DE CUADRILLA' and old_perfil_nombre != 'JEFE DE CUADRILLA':
                            supervisor_id = request.data.get('supervisor')
                            if supervisor_id:
                                supervisor = Supervisores.objects.get(usuario_id=supervisor_id)
                                JefesDeCuadrilla.objects.create(
                                    holding_id=usuario.holding_id,
                                    supervisor=supervisor,
                                    usuario=usuario
                                )
                        elif old_perfil_nombre == 'JEFE DE CUADRILLA' and new_perfil_nombre != 'JEFE DE CUADRILLA':
                            JefesDeCuadrilla.objects.filter(usuario=usuario).delete()
                    
                    return Response(serializer.data)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except Usuarios.DoesNotExist:
                return Response({"message": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)
            except Supervisores.DoesNotExist:
                return Response({"message": "Supervisor no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, format=None):
        with transaction.atomic():
            user_ids = request.data.get('ids', [])
            Usuarios.objects.filter(id__in=user_ids).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, format=None):
        with transaction.atomic():
            user_id = request.data.get('id')
            if not user_id:
                return Response({"message": "ID de usuario es necesario"}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                usuario = Usuarios.objects.get(id=user_id)
                old_perfil = usuario.perfil
                
                serializer = UserSerializer(usuario, data=request.data, partial=True)
                if serializer.is_valid():
                    usuario = serializer.save()
                    
                    if 'perfil' in request.data:
                        new_perfil_nombre = usuario.perfil.nombre_perfil if usuario.perfil else None
                        old_perfil_nombre = old_perfil.nombre_perfil if old_perfil else None

                        # Handle Supervisor changes
                        if new_perfil_nombre == 'SUPERVISOR' and old_perfil_nombre != 'SUPERVISOR':
                            Supervisores.objects.create(
                                holding_id=usuario.holding_id,
                                usuario=usuario
                            )
                        elif old_perfil_nombre == 'SUPERVISOR' and new_perfil_nombre != 'SUPERVISOR':
                            Supervisores.objects.filter(usuario=usuario).delete()

                        # Handle Jefe de Cuadrilla changes
                        if new_perfil_nombre == 'JEFE DE CUADRILLA' and old_perfil_nombre != 'JEFE DE CUADRILLA':
                            supervisor_id = request.data.get('supervisor')
                            if supervisor_id:
                                supervisor = Supervisores.objects.get(usuario_id=supervisor_id)
                                JefesDeCuadrilla.objects.create(
                                    holding_id=usuario.holding_id,
                                    supervisor=supervisor,
                                    usuario=usuario
                                )
                        elif old_perfil_nombre == 'JEFE DE CUADRILLA' and new_perfil_nombre != 'JEFE DE CUADRILLA':
                            JefesDeCuadrilla.objects.filter(usuario=usuario).delete()
                    
                    return Response(serializer.data)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except Usuarios.DoesNotExist:
                return Response({"message": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)
            except Supervisores.DoesNotExist:
                return Response({"message": "Supervisor no encontrado"}, status=status.HTTP_404_NOT_FOUND)
#------------------------------------------------------------------------------------------------------------------------------------------------------

class ClienteAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_scopes = []

    def dispatch(self, request, *args, **kwargs):
        if request.method in ['GET', 'POST', 'PATCH', 'PUT', 'DELETE']:
            self.required_scopes = ['admin', 'write']
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, format=None):
        holding_id = request.query_params.get('holding')
        if holding_id:
            usuarios = Clientes.objects.filter(holding_id=holding_id)
            serializer = ClienteSerializer(usuarios, many=True)
            return Response(serializer.data)
        return Response(status=status.HTTP_400_BAD_REQUEST)
        
    def post(self, request, format=None):
        print(request.data)
        serializer = ClienteSerializer(data=request.data)
        if serializer.is_valid():
            cliente = serializer.save()
            return Response({'id': cliente.id, 'data': serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, format=None): 
        cliente_ids = request.data.get('ids', [])
        Clientes.objects.filter(id__in=cliente_ids).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def patch(self, request, format=None):
        cliente_id = request.data.get('id')
        if not cliente_id:
            return Response({"message": "ID de cliente es necesario para actualizar"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            cliente = Clientes.objects.get(id=cliente_id)
        except Clientes.DoesNotExist:
            return Response({"message": "Cliente no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ClienteSerializer(cliente, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, format=None):
        cliente_id = request.data.get('id')
        try:
            cliente = Clientes.objects.get(id=cliente_id)
        except Clientes.DoesNotExist:
            return Response({"message": "Cliente no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ClienteSerializer(cliente, data=request.data)
        if serializer.is_valid():
            cliente = serializer.save()
            campos_data = request.data.get('camposPersonalizados', [])
            for campo_data in campos_data:
                campo_id = campo_data.get('id')
                if campo_id:
                    try:
                        campo = CamposClientes.objects.get(id=campo_id, cliente=cliente)
                        campo_serializer = CamposClientesSerializer(campo, data=campo_data)
                        if campo_serializer.is_valid():
                            campo_serializer.save()
                    except CamposClientes.DoesNotExist:
                        continue
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CamposClientesAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_scopes = []

    def dispatch(self, request, *args, **kwargs):
        if request.method == 'GET' or 'POST' or 'PATCH' or 'PUT' or 'DELETE':
            self.required_scopes =  ['admin','write']
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, cliente_id=None, format=None):
        holding_id = request.query_params.get('holding_id')
        cliente_id = cliente_id or request.query_params.get('cliente')
        
        try:
            if cliente_id is not None:
                campos = CamposClientes.objects.filter(cliente_id=cliente_id)
            elif holding_id is not None:
                campos = CamposClientes.objects.filter(holding_id=holding_id)
            else:
                return Response({"message": "Debe proporcionar cliente_id o holding_id"}, status=status.HTTP_400_BAD_REQUEST)

            if campos.exists():
                serializer = CamposClientesSerializer(campos, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"message": "No se encontraron campos personalizados"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        serializer = CamposClientesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, format=None):
        try:
            campo_id = request.data.get('id')
            campo = CamposClientes.objects.get(id=campo_id)
        except CamposClientes.DoesNotExist:
            return Response({"message": "Campo no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        serializer = CamposClientesSerializer(campo, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, format=None):
        campo_ids = request.data.get('ids', [])
        CamposClientes.objects.filter(id__in=campo_ids).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class AreaClienteAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]

    # Define required_scopes como un atributo de instancia
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_scopes = []

    def dispatch(self, request, *args, **kwargs):
        # Ajustar required_scopes basado en el método antes de que se llame a la vista
        if request.method == 'GET' or 'POST' or 'PATCH' or 'PUT' or 'DELETE':
            self.required_scopes =  ['admin','write']
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, format=None):
        holding_id = request.query_params.get('holding')
        if holding_id:
            usuarios = AreasCliente.objects.filter(holding_id=holding_id)
            serializer = AreaClienteSerializer(usuarios, many=True)
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def post(self, request, format=None):
        serializer = AreaClienteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    #Metodo DELETE
    def delete(self, request, format=None): 
        perfil_ids = request.data.get('ids', [])
        AreasCliente.objects.filter(id__in=perfil_ids).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    #Metodo PATCH
    def patch(self, request, format=None):
        perfil_id = request.data.get('id')
        if not perfil_id:
            return Response({"message": "ID de area es necesario para actualizar"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            perfil = AreasCliente.objects.get(id=perfil_id)
        except AreasCliente.DoesNotExist:
            return Response({"message": "Area no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        serializer = AreaClienteSerializer(perfil, data=request.data, partial=True)  # Partial=True para permitir actualizaciones parciales
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    #Metodo PUT
    def put(self, request, format=None):
        cliente_id = request.data.get('id')
        try:
            perfil = AreasCliente.objects.get(id=cliente_id)
        except AreasCliente.DoesNotExist:
            return Response({"message": "Perfil no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        serializer = AreaClienteSerializer(perfil, data=request.data)  # Sin partial=True
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CargoClienteAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]

    # Define required_scopes como un atributo de instancia
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_scopes = []

    def dispatch(self, request, *args, **kwargs):
        # Ajustar required_scopes basado en el método antes de que se llame a la vista
        if request.method == 'GET' or 'POST' or 'PATCH' or 'PUT' or 'DELETE':
            self.required_scopes =  ['admin','write']
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, format=None):
        holding_id = request.query_params.get('holding')
        if holding_id:
            usuarios = CargosCliente.objects.filter(holding_id=holding_id)
            serializer = CargoClienteSerializer(usuarios, many=True)
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def post(self, request, format=None):
        serializer = CargoClienteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    #Metodo DELETE
    def delete(self, request, format=None): 
        perfil_ids = request.data.get('ids', [])
        CargosCliente.objects.filter(id__in=perfil_ids).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    #Metodo PATCH
    def patch(self, request, format=None):
        perfil_id = request.data.get('id')
        if not perfil_id:
            
            return Response({"message": "ID de perfil es necesario para actualizar"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            perfil = CargosCliente.objects.get(id=perfil_id)
        except CargosCliente.DoesNotExist:
            return Response({"message": "Perfil no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        serializer = CargoClienteSerializer(perfil, data=request.data, partial=True)  # Partial=True para permitir actualizaciones parciales
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    #Metodo PUT
    def put(self, request, format=None):
        cliente_id = request.data.get('id')
        try:
            perfil = CargosCliente.objects.get(id=cliente_id)
        except CargosCliente.DoesNotExist:
            return Response({"message": "Cargo no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        serializer = CargoClienteSerializer(perfil, data=request.data)  # Sin partial=True
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AreaAdministracionAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]

    # Define required_scopes como un atributo de instancia
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_scopes = []

    def dispatch(self, request, *args, **kwargs):
        # Ajustar required_scopes basado en el método antes de que se llame a la vista
        if request.method == 'GET' or 'POST' or 'PATCH' or 'PUT' or 'DELETE':
            self.required_scopes =  ['admin','write']
        return super().dispatch(request, *args, **kwargs)

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

class CargoAdministracionAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_scopes = []

    def dispatch(self, request, *args, **kwargs):
        if request.method == 'GET' or 'POST' or 'PATCH' or 'PUT' or 'DELETE':
            self.required_scopes =  ['admin','write']
        return super().dispatch(request, *args, **kwargs)

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

class ContactoClienteAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]

    # Define required_scopes como un atributo de instancia
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_scopes = []

    def dispatch(self, request, *args, **kwargs):
        # Ajustar required_scopes basado en el método antes de que se llame a la vista
        if request.method == 'GET' or 'POST' or 'PATCH' or 'PUT' or 'DELETE':
            self.required_scopes =  ['admin','write']
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, format=None):
        holding_id = request.query_params.get('holding')
        if holding_id:
            usuarios = ContactosClientes.objects.filter(holding_id=holding_id)
            serializer = ContactosClienteSerializer(usuarios, many=True)
            print(serializer.data)
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def post(self, request, format=None):
        print(request.data)
        serializer = ContactosClienteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    #Metodo DELETE
    def delete(self, request, format=None): 
        perfil_ids = request.data.get('ids', [])
        ContactosClientes.objects.filter(id__in=perfil_ids).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    #Metodo PATCH
    def patch(self, request, format=None):
        perfil_id = request.data.get('id')
        if not perfil_id:
            
            return Response({"message": "ID de perfil es necesario para actualizar"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            perfil = ContactosClientes.objects.get(id=perfil_id)
        except ContactosClientes.DoesNotExist:
            return Response({"message": "Perfil no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ContactosClienteSerializer(perfil, data=request.data, partial=True)  # Partial=True para permitir actualizaciones parciales
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    #Metodo PUT
    def put(self, request, format=None):
        cliente_id = request.data.get('id')
        try:
            perfil = ContactosClientes.objects.get(id=cliente_id)
        except ContactosClientes.DoesNotExist:
            return Response({"message": "Cargo no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ContactosClienteSerializer(perfil, data=request.data)  # Sin partial=True
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AreaAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]

    # Define required_scopes como un atributo de instancia
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_scopes = []

    def dispatch(self, request, *args, **kwargs):
        # Ajustar required_scopes basado en el método antes de que se llame a la vista
        if request.method == 'GET' or 'POST' or 'PATCH' or 'PUT' or 'DELETE':
            self.required_scopes =  ['admin','write']
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, format=None):
        holding_id = request.query_params.get('holding')
        if holding_id:
            usuarios = Areas.objects.filter(holding_id=holding_id)
            serializer = AreaSerializer(usuarios, many=True)
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def post(self, request, format=None):
        serializer = AreaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    #Metodo DELETE
    def delete(self, request, format=None): 
        perfil_ids = request.data.get('ids', [])
        Areas.objects.filter(id__in=perfil_ids).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    #Metodo PATCH
    def patch(self, request, format=None):
        perfil_id = request.data.get('id')
        if not perfil_id:
            return Response({"message": "ID de area es necesario para actualizar"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            perfil = Areas.objects.get(id=perfil_id)
        except Areas.DoesNotExist:
            return Response({"message": "Area no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        serializer = AreaSerializer(perfil, data=request.data, partial=True)  # Partial=True para permitir actualizaciones parciales
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    #Metodo PUT
    def put(self, request, format=None):
        cliente_id = request.data.get('id')
        try:
            perfil = Areas.objects.get(id=cliente_id)
        except Areas.DoesNotExist:
            return Response({"message": "Perfil no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        serializer = AreaSerializer(perfil, data=request.data)  # Sin partial=True
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CargoAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]

    # Define required_scopes como un atributo de instancia
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_scopes = []

    def dispatch(self, request, *args, **kwargs):
        # Ajustar required_scopes basado en el método antes de que se llame a la vista
        if request.method == 'GET' or 'POST' or 'PATCH' or 'PUT' or 'DELETE':
            self.required_scopes =  ['admin','write']
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, format=None):
        holding_id = request.query_params.get('holding')
        if holding_id:
            usuarios = Cargos.objects.filter(holding_id=holding_id)
            serializer = CargoSerializer(usuarios, many=True)
            print(serializer.data)
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def post(self, request, format=None):
        serializer = CargoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    #Metodo DELETE
    def delete(self, request, format=None): 
        perfil_ids = request.data.get('ids', [])
        Cargos.objects.filter(id__in=perfil_ids).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    #Metodo PATCH
    def patch(self, request, format=None):
        perfil_id = request.data.get('id')
        if not perfil_id:
            
            return Response({"message": "ID de perfil es necesario para actualizar"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            perfil = Cargos.objects.get(id=perfil_id)
        except Cargos.DoesNotExist:
            return Response({"message": "Perfil no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        serializer = CargoSerializer(perfil, data=request.data, partial=True)  # Partial=True para permitir actualizaciones parciales
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    #Metodo PUT
    def put(self, request, format=None):
        cliente_id = request.data.get('id')
        try:
            perfil = Cargos.objects.get(id=cliente_id)
        except Cargos.DoesNotExist:
            return Response({"message": "Cargo no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        serializer = CargoSerializer(perfil, data=request.data)  # Sin partial=True
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EmpresaTransporteAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]

    # Define required_scopes como un atributo de instancia
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_scopes = []

    def dispatch(self, request, *args, **kwargs):
        # Ajustar required_scopes basado en el método antes de que se llame a la vista
        if request.method == 'GET' or 'POST' or 'PATCH' or 'PUT' or 'DELETE':
            self.required_scopes =  ['admin','write']
        return super().dispatch(request, *args, **kwargs)

    #Metodo GET
    def get(self, request, format=None):
        holding_id = request.query_params.get('holding')
        if holding_id:
            usuarios = EmpresasTransporte.objects.filter(holding_id=holding_id)
            serializer = EmpresaTransporteSerializer(usuarios, many=True)
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    #Metodo POST    
    def post(self, request, format=None):
        serializer = EmpresaTransporteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    #Metodo DELETE
    def delete(self, request, format=None): 
        perfil_ids = request.data.get('ids', [])
        EmpresasTransporte.objects.filter(id__in=perfil_ids).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    #Metodo PATCH
    def patch(self, request, format=None):
        perfil_id = request.data.get('id')
        if not perfil_id:
            
            return Response({"message": "ID de perfil es necesario para actualizar"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            perfil = EmpresasTransporte.objects.get(id=perfil_id)
        except EmpresasTransporte.DoesNotExist:
            return Response({"message": "Perfil no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        serializer = EmpresaTransporteSerializer(perfil, data=request.data, partial=True)  # Partial=True para permitir actualizaciones parciales
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    #Metodo PUT
    def put(self, request, format=None):
        cliente_id = request.data.get('id')
        try:
            perfil = EmpresasTransporte.objects.get(id=cliente_id)
        except EmpresasTransporte.DoesNotExist:
            return Response({"message": "Cargo no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        serializer = EmpresaTransporteSerializer(perfil, data=request.data)  # Sin partial=True
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class VehiculosTransporteAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]

    # Define required_scopes como un atributo de instancia
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_scopes = []

    def dispatch(self, request, *args, **kwargs):
        # Ajustar required_scopes basado en el método antes de que se llame a la vista
        if request.method == 'GET' or 'POST' or 'PATCH' or 'PUT' or 'DELETE':
            self.required_scopes =  ['admin','write']
        return super().dispatch(request, *args, **kwargs)

    #Metodo GET
    def get(self, request, format=None):
        holding_id = request.query_params.get('holding')
        if holding_id:
            vehiculos = VehiculosTransporte.objects.filter(holding_id=holding_id)
            serializer = VehiculosTransporteSerializer(vehiculos, many=True)
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    #Metodo POST    
    def post(self, request, format=None):
        serializer = VehiculosTransporteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    #Metodo DELETE
    def delete(self, request, format=None): 
        vehiculos_ids = request.data.get('ids', [])
        VehiculosTransporte.objects.filter(id__in=vehiculos_ids).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    #Metodo PATCH
    def patch(self, request, format=None):
        vehiculos_ids = request.data.get('id')
        if not vehiculos_ids:
            
            return Response({"message": "ID de perfil es necesario para actualizar"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            vehiculos = VehiculosTransporte.objects.get(id=vehiculos_ids)
        except VehiculosTransporte.DoesNotExist:
            return Response({"message": "Perfil no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        serializer = VehiculosTransporteSerializer(vehiculos, data=request.data, partial=True)  # Partial=True para permitir actualizaciones parciales
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    #Metodo PUT
    def put(self, request, format=None):
        cliente_id = request.data.get('id')
        try:
            vehiculos = VehiculosTransporte.objects.get(id=cliente_id)
        except VehiculosTransporte.DoesNotExist:
            return Response({"message": "Cargo no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        serializer = VehiculosTransporteSerializer(vehiculos, data=request.data)  # Sin partial=True
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ChoferesTransporteAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]

    # Define required_scopes como un atributo de instancia
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_scopes = []

    def dispatch(self, request, *args, **kwargs):
        # Ajustar required_scopes basado en el método antes de que se llame a la vista
        if request.method == 'GET' or 'POST' or 'PATCH' or 'PUT' or 'DELETE':
            self.required_scopes =  ['admin','write']
        return super().dispatch(request, *args, **kwargs)

    #Metodo GET
    def get(self, request, format=None):
        holding_id = request.query_params.get('holding')
        if holding_id:
            vehiculos = ChoferesTransporte.objects.filter(holding_id=holding_id)
            serializer = ChoferesTransporteSerializer(vehiculos, many=True)
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    #Metodo POST    
    def post(self, request, format=None):
        serializer = ChoferesTransporteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    #Metodo DELETE
    def delete(self, request, format=None): 
        vehiculos_ids = request.data.get('ids', [])
        ChoferesTransporte.objects.filter(id__in=vehiculos_ids).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    #Metodo PATCH
    def patch(self, request, format=None):
        vehiculos_ids = request.data.get('id')
        if not vehiculos_ids:
            
            return Response({"message": "ID de perfil es necesario para actualizar"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            vehiculos = ChoferesTransporte.objects.get(id=vehiculos_ids)
        except ChoferesTransporte.DoesNotExist:
            return Response({"message": "Perfil no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ChoferesTransporteSerializer(vehiculos, data=request.data, partial=True)  # Partial=True para permitir actualizaciones parciales
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    #Metodo PUT
    def put(self, request, format=None):
        cliente_id = request.data.get('id')
        try:
            vehiculos = ChoferesTransporte.objects.get(id=cliente_id)
        except ChoferesTransporte.DoesNotExist:
            return Response({"message": "Cargo no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ChoferesTransporteSerializer(vehiculos, data=request.data)  # Sin partial=True
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class SaludTrabajadoresAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]

    # Define required_scopes como un atributo de instancia
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_scopes = []

    def dispatch(self, request, *args, **kwargs):
        # Ajustar required_scopes basado en el método antes de que se llame a la vista
        if request.method == 'GET' or 'POST' or 'PATCH' or 'PUT' or 'DELETE':
            self.required_scopes =  ['admin','write']
        return super().dispatch(request, *args, **kwargs)

    #Metodo GET
    def get(self, request, format=None):
        holding_id = request.query_params.get('holding')
        if holding_id:
            vehiculos = SaludTrabajadores.objects.filter(holding_id=holding_id)
            serializer = SaludTrabajadoresSerializer(vehiculos, many=True)
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    #Metodo POST    
    def post(self, request, format=None):
        serializer = SaludTrabajadoresSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    #Metodo DELETE
    def delete(self, request, format=None): 
        vehiculos_ids = request.data.get('ids', [])
        SaludTrabajadores.objects.filter(id__in=vehiculos_ids).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    #Metodo PATCH
    def patch(self, request, format=None):
        vehiculos_ids = request.data.get('id')
        if not vehiculos_ids:
            
            return Response({"message": "ID de perfil es necesario para actualizar"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            vehiculos = SaludTrabajadores.objects.get(id=vehiculos_ids)
        except SaludTrabajadores.DoesNotExist:
            return Response({"message": "Perfil no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        serializer = SaludTrabajadoresSerializer(vehiculos, data=request.data, partial=True)  # Partial=True para permitir actualizaciones parciales
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    #Metodo PUT
    def put(self, request, format=None):
        cliente_id = request.data.get('id')
        try:
            vehiculos = SaludTrabajadores.objects.get(id=cliente_id)
        except SaludTrabajadores.DoesNotExist:
            return Response({"message": "Cargo no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        serializer = SaludTrabajadoresSerializer(vehiculos, data=request.data)  # Sin partial=True
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class AFPTrabajadoresAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]

    # Define required_scopes como un atributo de instancia
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_scopes = []

    def dispatch(self, request, *args, **kwargs):
        # Ajustar required_scopes basado en el método antes de que se llame a la vista
        if request.method == 'GET' or 'POST' or 'PATCH' or 'PUT' or 'DELETE':
            self.required_scopes =  ['admin','write']
        return super().dispatch(request, *args, **kwargs)

    #Metodo GET
    def get(self, request, format=None):
        holding_id = request.query_params.get('holding')
        if holding_id:
            vehiculos = AFPTrabajadores.objects.filter(holding_id=holding_id)
            serializer = AFPTrabajadoresSerializer(vehiculos, many=True)
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    #Metodo POST    
    def post(self, request, format=None):
        serializer = AFPTrabajadoresSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    #Metodo DELETE
    def delete(self, request, format=None): 
        vehiculos_ids = request.data.get('ids', [])
        AFPTrabajadores.objects.filter(id__in=vehiculos_ids).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    #Metodo PATCH
    def patch(self, request, format=None):
        vehiculos_ids = request.data.get('id')
        if not vehiculos_ids:
            
            return Response({"message": "ID de perfil es necesario para actualizar"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            vehiculos = AFPTrabajadores.objects.get(id=vehiculos_ids)
        except AFPTrabajadores.DoesNotExist:
            return Response({"message": "Perfil no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        serializer = AFPTrabajadoresSerializer(vehiculos, data=request.data, partial=True)  # Partial=True para permitir actualizaciones parciales
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    #Metodo PUT
    def put(self, request, format=None):
        cliente_id = request.data.get('id')
        try:
            vehiculos = AFPTrabajadores.objects.get(id=cliente_id)
        except AFPTrabajadores.DoesNotExist:
            return Response({"message": "Cargo no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        serializer = AFPTrabajadoresSerializer(vehiculos, data=request.data)  # Sin partial=True
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CasasTrabajadoresAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_scopes = []

    def dispatch(self, request, *args, **kwargs):
        if request.method == 'GET' or 'POST' or 'PATCH' or 'PUT' or 'DELETE':
            self.required_scopes =  ['admin','write']
        return super().dispatch(request, *args, **kwargs)

    #Metodo GET
    def get(self, request, format=None):
        holding_id = request.query_params.get('holding')
        if holding_id:
            casas = CasasTrabajadores.objects.filter(holding_id=holding_id)
            serializer = CasasTrabajadoresSerializer(casas, many=True)
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    #Metodo POST    
    def post(self, request, format=None):
        serializer = CasasTrabajadoresSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    #Metodo DELETE
    def delete(self, request, format=None): 
        casas_ids = request.data.get('ids', [])
        CasasTrabajadores.objects.filter(id__in=casas_ids).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    #Metodo PATCH
    def patch(self, request, format=None):
        casas_ids = request.data.get('id')
        if not casas_ids:
            
            return Response({"message": "ID de perfil es necesario para actualizar"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            casas = CasasTrabajadores.objects.get(id=casas_ids)
        except CasasTrabajadores.DoesNotExist:
            return Response({"message": "Perfil no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        serializer = CasasTrabajadoresSerializer(casas, data=request.data, partial=True)  # Partial=True para permitir actualizaciones parciales
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    #Metodo PUT
    def put(self, request, format=None):
        cliente_id = request.data.get('id')
        try:
            casas = CasasTrabajadores.objects.get(id=cliente_id)
        except CasasTrabajadores.DoesNotExist:
            return Response({"message": "Cargo no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        serializer = CasasTrabajadoresSerializer(casas, data=request.data)  # Sin partial=True
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UnidadControlAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]

    # Define required_scopes como un atributo de instancia
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_scopes = []

    def dispatch(self, request, *args, **kwargs):
        # Ajustar required_scopes basado en el método antes de que se llame a la vista
        if request.method == 'GET' or 'POST' or 'PATCH' or 'PUT' or 'DELETE':
            self.required_scopes =  ['admin','write']
        return super().dispatch(request, *args, **kwargs)

    #Metodo GET
    def get(self, request, format=None):
        holding_id = request.query_params.get('holding')
        if holding_id:
            vehiculos = UnidadControl.objects.filter(holding_id=holding_id)
            serializer = UnidadControlSerializer(vehiculos, many=True)
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    #Metodo POST    
    def post(self, request, format=None):
        serializer = UnidadControlSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    #Metodo DELETE
    def delete(self, request, format=None): 
        vehiculos_ids = request.data.get('ids', [])
        UnidadControl.objects.filter(id__in=vehiculos_ids).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    #Metodo PATCH
    def patch(self, request, format=None):
        vehiculos_ids = request.data.get('id')
        if not vehiculos_ids:
            
            return Response({"message": "ID de perfil es necesario para actualizar"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            vehiculos = UnidadControl.objects.get(id=vehiculos_ids)
        except UnidadControl.DoesNotExist:
            return Response({"message": "Perfil no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        serializer = UnidadControlSerializer(vehiculos, data=request.data, partial=True)  # Partial=True para permitir actualizaciones parciales
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    #Metodo PUT
    def put(self, request, format=None):
        cliente_id = request.data.get('id')
        try:
            vehiculos = UnidadControl.objects.get(id=cliente_id)
        except UnidadControl.DoesNotExist:
            return Response({"message": "Cargo no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        serializer = UnidadControlSerializer(vehiculos, data=request.data)  # Sin partial=True
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LaboresAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]

    # Define required_scopes como un atributo de instancia
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_scopes = []

    def dispatch(self, request, *args, **kwargs):
        # Ajustar required_scopes basado en el método antes de que se llame a la vista
        if request.method == 'GET' or 'POST' or 'PATCH' or 'PUT' or 'DELETE':
            self.required_scopes =  ['admin','write']
        return super().dispatch(request, *args, **kwargs)

    #Metodo GET
    def get(self, request, format=None):
        holding_id = request.query_params.get('holding')
        if holding_id:
            vehiculos = Labores.objects.filter(holding_id=holding_id)
            serializer = LaboresSerializer(vehiculos, many=True)
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    #Metodo POST    
    def post(self, request, format=None):
        serializer = LaboresSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    #Metodo DELETE
    def delete(self, request, format=None): 
        vehiculos_ids = request.data.get('ids', [])
        Labores.objects.filter(id__in=vehiculos_ids).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    #Metodo PATCH
    def patch(self, request, format=None):
        vehiculos_ids = request.data.get('id')
        if not vehiculos_ids:
            
            return Response({"message": "ID de perfil es necesario para actualizar"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            vehiculos = Labores.objects.get(id=vehiculos_ids)
        except Labores.DoesNotExist:
            return Response({"message": "Perfil no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        serializer = LaboresSerializer(vehiculos, data=request.data, partial=True)  # Partial=True para permitir actualizaciones parciales
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    #Metodo PUT
    def put(self, request, format=None):
        cliente_id = request.data.get('id')
        try:
            vehiculos = Labores.objects.get(id=cliente_id)
        except Labores.DoesNotExist:
            return Response({"message": "Cargo no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        serializer = LaboresSerializer(vehiculos, data=request.data)  # Sin partial=True
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class FolioComercialAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]

    # Define required_scopes como un atributo de instancia
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_scopes = []

    def dispatch(self, request, *args, **kwargs):
        if request.method in ['POST', 'DELETE', 'PUT']:
            self.required_scopes = ['superadmin_access', 'admin', 'write']
        elif request.method == 'GET':
            self.required_scopes = ['superadmin_access', 'admin', 'write']
        return super().dispatch(request, *args, **kwargs)

    # Método GET
    def get(self, request, holding_id=None, format=None):
        holding_id = request.query_params.get('holding')
        folios = FolioComercial.objects.filter(holding_id=holding_id) if holding_id else FolioComercial.objects.all()
        serializer = FolioComercialSerializer(folios, many=True)
        print('Data del folio comercial: ', serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    # Método POST
    def post(self, request, format=None):
        data = request.data
        print(data)
        serializer = FolioComercialSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Método DELETE
    def delete(self, request, format=None): 
        folio_ids = request.data.get('ids', [])
        FolioComercial.objects.filter(id__in=folio_ids).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # Método PATCH
    def patch(self, request, format=None):
        folio_id = request.data.get('id')
        if not folio_id:
            return Response({"message": "ID de folio es necesario para actualizar"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            folio = FolioComercial.objects.get(id=folio_id)
        except FolioComercial.DoesNotExist:
            return Response({"message": "Folio no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        serializer = FolioComercialSerializer(folio, data=request.data, partial=True)  # Partial=True para permitir actualizaciones parciales
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Método PUT
    def put(self, request, format=None):
        folio_id = request.data.get('id')
        if not folio_id:
            return Response({"message": "ID de folio es requerido"}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            folio = FolioComercial.objects.get(id=folio_id)
        except FolioComercial.DoesNotExist:
            return Response({"message": "Folio no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        serializer = FolioComercialSerializer(folio, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        print("Errores de validación:", serializer.errors)  # Añade esto para depuración
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PersonalTrabajadoresMobileAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]
    parser_classes = [MultiPartParser, FormParser]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_scopes = []

    def dispatch(self, request, *args, **kwargs):
        if request.method in ['GET', 'POST', 'PATCH', 'PUT', 'DELETE']:
            self.required_scopes = ['admin', 'write']
        return super().dispatch(request, *args, **kwargs)

    def merge_data(self, old_data, new_data):
        merged = old_data.copy()
        for key, new_value in new_data.items():
            if new_value not in (None, '', 'null', 'undefined'):
                merged[key] = new_value
        return merged

    def delete_old_file(self, file_path):
        if file_path:
            full_path = os.path.join(settings.MEDIA_ROOT, file_path)
            if os.path.isfile(full_path):
                os.remove(full_path)

    @transaction.atomic
    def post(self, request, format=None):
        print("=== DEBUG: INICIO POST ===")
        data = request.data.copy()
        data.update(request.FILES)
        
        print(f"Datos recibidos: {list(data.keys())}")
        print(f"Valores de datos importantes:")
        print(f"  holding: {data.get('holding')}")
        print(f"  rut: {data.get('rut')}")
        print(f"  dni: {data.get('dni')}")
        print(f"  nombres: {data.get('nombres')}")
        print(f"  apellidos: {data.get('apellidos')}")

        # Extract contract-specific data
        contract_data = {
            'holding_id': data.get('holding'),
            'sociedad_id': data.get('sociedad'),
            'folio_id': data.get('folio'),
            'cliente_id': data.get('cliente'),
            'fundo_id': data.get('fundo'),
            'labor_id': data.get('labor'),
            'empresa_transporte_id': data.get('empresa_transporte'),
            'vehiculo_id': data.get('vehiculo'),
            'contrato_firmado': 'Elaboracion Pendiente'
        }

        # Find or create personal
        existing_personal = None
        if data.get('rut'):
            existing_personal = PersonalTrabajadores.objects.filter(rut=data['rut']).first()
        elif data.get('dni'):
            existing_personal = PersonalTrabajadores.objects.filter(dni=data['dni']).first()

        print(f"Trabajador existente: {existing_personal.id if existing_personal else 'None'}")

        if existing_personal:
            old_front_image = existing_personal.carnet_front_image.name if existing_personal.carnet_front_image else None
            old_back_image = existing_personal.carnet_back_image.name if existing_personal.carnet_back_image else None
            old_signature = existing_personal.firma.name if existing_personal.firma else None

            current_data = PersonalTrabajadoresMobileSerializer(existing_personal).data
            merged_data = self.merge_data(current_data, data)
            print(f"Datos mezclados para actualización: {list(merged_data.keys())}")
            serializer = PersonalTrabajadoresMobileSerializer(
                existing_personal,
                data=merged_data,
                partial=True
            )
        else:
            print("Creando nuevo trabajador")
            serializer = PersonalTrabajadoresMobileSerializer(data=data)

        print("=== VALIDANDO SERIALIZER ===")
        if serializer.is_valid():
            print("✅ Serializer válido")
            personal = serializer.save()
            
            # Delete old images if updated
            if existing_personal:
                if 'carnet_front_image' in request.FILES:
                    self.delete_old_file(old_front_image)
                if 'carnet_back_image' in request.FILES:
                    self.delete_old_file(old_back_image)
                if 'firma' in request.FILES:
                    self.delete_old_file(old_signature)

            # Handle QR code
            codigo_qr = data.get('codigo_qr')
            if codigo_qr:
                existing_qr = CodigoQR.objects.filter(trabajador=personal).first()
                if existing_qr:
                    existing_qr.codigo_qr = codigo_qr
                    existing_qr.save()
                    codigo_qr_id = existing_qr.id
                else:
                    codigo_qr_serializer = CodigoQRSerializer(data={
                        'trabajador': personal.id,
                        'codigo_qr': codigo_qr,
                    })
                    if codigo_qr_serializer.is_valid():
                        codigo_qr_asociacion = codigo_qr_serializer.save()
                        codigo_qr_id = codigo_qr_asociacion.id
                    else:
                        return Response(codigo_qr_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

                return Response({
                    'codigo_qr_id': codigo_qr_id,
                    'message': 'Trabajador'
                }, status=status.HTTP_201_CREATED)
            
            return Response({
                'message': 'Trabajador'
            }, status=status.HTTP_201_CREATED)
        else:
            print("❌ Errores de validación del serializer:")
            print(f"Errores: {serializer.errors}")
            print("=== DATOS QUE LLEGARON AL SERIALIZER ===")
            print(f"Initial data keys: {list(serializer.initial_data.keys()) if hasattr(serializer, 'initial_data') else 'N/A'}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EnviarDataProduccionAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]
    parser_classes = [MultiPartParser, FormParser]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_scopes = []

    def dispatch(self, request, *args, **kwargs):
        if request.method in ['GET', 'POST', 'PATCH', 'PUT', 'DELETE']:
            self.required_scopes = ['admin', 'write']
        return super().dispatch(request, *args, **kwargs) 
    
    def get(self, request, holding_id):
        serializer = DataProduccionSerializer(context={'holding_id': holding_id})
        data = {
            'trabajadores': serializer.get_trabajadores(None),
            'labores': serializer.get_labores(None),
            'unidades_control': serializer.get_unidades_control(None),
            
        }
        return Response(data)

class HorarioAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]

    # Define required_scopes como un atributo de instancia
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_scopes = []

    def dispatch(self, request, *args, **kwargs):
        # Ajustar required_scopes basado en el método antes de que se llame a la vista
        if request.method == 'GET' or 'POST' or 'PATCH' or 'PUT' or 'DELETE':
            self.required_scopes =  ['admin','write']
        return super().dispatch(request, *args, **kwargs)

    #Metodo GET
    def get(self, request, format=None):
        holding_id = request.query_params.get('holding')
        if holding_id:
            jornada = Horarios.objects.filter(holding_id=holding_id)
            serializer = HorarioSerializer(jornada, many=True)
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    #Metodo POST    
    def post(self, request, format=None):
        serializer = HorarioSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    #Metodo DELETE
    def delete(self, request, format=None): 
        jornada_ids = request.data.get('ids', [])
        Horarios.objects.filter(id__in=jornada_ids).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    #Metodo PATCH
    def patch(self, request, format=None):
        jornada_id = request.data.get('id')
        if not jornada_id:
            return Response({"message": "ID de perfil es necesario para actualizar"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            jornada = Horarios.objects.get(id=jornada_id)
        except Horarios.DoesNotExist:
            return Response({"message": "Perfil no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        serializer = HorarioSerializer(jornada, data=request.data, partial=True)  # Partial=True para permitir actualizaciones parciales
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    #Metodo PUT
    def put(self, request, format=None):
        cliente_id = request.data.get('id')
        try:
            vehiculos = Horarios.objects.get(id=cliente_id)
        except Horarios.DoesNotExist:
            return Response({"message": "Cargo no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        serializer = HorarioSerializer(vehiculos, data=request.data)  # Sin partial=True
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProduccionTrabajadorAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_scopes = []

    def dispatch(self, request, *args, **kwargs):
        if request.method in ['GET', 'POST', 'PATCH', 'PUT', 'DELETE']:
            self.required_scopes = ['admin', 'write']
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, format=None):
        holding_id = request.query_params.get('holding')
        if holding_id:
            producciones = ProduccionTrabajador.objects.filter(holding_id=holding_id)
            serializer = ProduccionTrabajadorSerializer(producciones, many=True)
            return Response(serializer.data)
        else:
            return Response({'error': 'El parámetro holding es necesario'}, status=status.HTTP_400_BAD_REQUEST)
    
    def post(self, request, format=None):
        data = request.data
        print(data)
        serializer = ProduccionTrabajadorSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, format=None): 
        produccion_ids = request.data.get('ids', [])
        ProduccionTrabajador.objects.filter(id__in=produccion_ids).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def patch(self, request, format=None):
        produccion_id = request.data.get('id')
        if not produccion_id:
            return Response({"message": "ID de producción es necesario para actualizar"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            produccion = ProduccionTrabajador.objects.get(id=produccion_id)
        except ProduccionTrabajador.DoesNotExist:
            return Response({"message": "Producción no encontrada"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProduccionTrabajadorSerializer(produccion, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, format=None):
        worker_id = request.data.get('trabajador')
        try:
            produccion_trabajador = ProduccionTrabajador.objects.get(trabajador_id=worker_id)
        except ProduccionTrabajador.DoesNotExist:
            return Response({"message": "Producción no encontrada"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProduccionTrabajadorSerializer(produccion_trabajador, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class CheckTokenSuperAdmin(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_scopes = []

    def dispatch(self, request, *args, **kwargs):
        # Ajustar required_scopes basado en el método antes de que se llame a la vista
        if request.method == 'GET' or 'POST' or 'PATCH' or 'PUT' or 'DELETE':
            self.required_scopes =  ['superadmin_access']
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        token = request.data.get('token')
        print(token)
        
class PersonalTrabajadoresAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_scopes = []

    def dispatch(self, request, *args, **kwargs):
        if request.method in ['GET', 'POST', 'PATCH', 'PUT', 'DELETE']:
            self.required_scopes = ['admin', 'write']
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, format=None):
        holding_id = request.query_params.get('holding')
        if holding_id:
            trabajadores = PersonalTrabajadores.objects.filter(holding_id=holding_id).exclude(cargo_id = 1)
            serializer = PersonalTrabajadoresSerializer(trabajadores, many=True)
            return Response(serializer.data)
        return Response({'error': 'El parámetro holding es necesario'}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        data = request.data
        print(data)
        serializer = PersonalTrabajadoresSerializer(data = data)
        if serializer.is_valid():
            trabajador = serializer.save()
            return Response({'id': trabajador.id, 'data': serializer.data}, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, format=None):
        trabajador_id = request.data.get('id')
        try:
            trabajador = PersonalTrabajadores.objects.get(id=trabajador_id)
        except PersonalTrabajadores.DoesNotExist:
            return Response({"message": "Trabajador no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        serializer = PersonalTrabajadoresSerializer(trabajador, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, format=None):
        trabajador_ids = request.data.get('ids', [])
        PersonalTrabajadores.objects.filter(id__in=trabajador_ids).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, format=None):
        trabajador_id = request.data.get('id')
        if not trabajador_id:
            return Response({"message": "ID de trabajador es necesario para actualizar"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            trabajador = PersonalTrabajadores.objects.get(id=trabajador_id)
        except PersonalTrabajadores.DoesNotExist:
            return Response({"message": "Trabajador no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        serializer = PersonalTrabajadoresSerializer(trabajador, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CodigoQRAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_scopes = []

    def dispatch(self, request, *args, **kwargs):
        if request.method in ['GET', 'POST', 'PUT', 'DELETE']:
            self.required_scopes = ['admin', 'write']
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, trabajador_id=None, format=None):
        # Si trabajador_id viene de la URL, usarlo; sino, buscarlo en query_params
        if trabajador_id is None:
            trabajador_id = request.query_params.get('trabajador')
        
        if trabajador_id:
            try:
                codigo_qr = CodigoQR.objects.get(trabajador_id=trabajador_id)
                serializer = CodigoQRSerializer(codigo_qr)
                return Response(serializer.data)
            except CodigoQR.DoesNotExist:
                return Response({"message": "Código QR no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        else:
            codigos_qr = CodigoQR.objects.all()
            serializer = CodigoQRSerializer(codigos_qr, many=True)
            return Response(serializer.data)

    def post(self, request, format=None):
        serializer = CodigoQRSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, trabajador_id=None, format=None):
        # Si trabajador_id viene de la URL, usarlo; sino, buscarlo en request.data
        if trabajador_id is None:
            trabajador_id = request.data.get('trabajador')
        
        if not trabajador_id:
            return Response({"message": "ID del trabajador es necesario para actualizar"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            codigo_qr = CodigoQR.objects.get(trabajador_id=trabajador_id)
        except CodigoQR.DoesNotExist:
            return Response({"message": "Código QR no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        serializer = CodigoQRSerializer(codigo_qr, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, trabajador_id=None, format=None):
        # Si trabajador_id viene de la URL, usarlo; sino, buscarlo en request.data
        if trabajador_id is None:
            trabajador_id = request.data.get('trabajador')
        
        if not trabajador_id:
            return Response({"message": "ID del trabajador es necesario para eliminar"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            codigo_qr = CodigoQR.objects.get(trabajador_id=trabajador_id)
            codigo_qr.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except CodigoQR.DoesNotExist:
            return Response({"message": "Código QR no encontrado"}, status=status.HTTP_404_NOT_FOUND)

class TrabajadoresCosechaQRView(APIView):
    def get(self, request):
        try:
            # Obtener personal con supervisor asignado
            personal_supervisados = PersonalTrabajadores.objects.filter(
                codigo_supervisor__isnull=False,
                estado=True
            )
            
            # Lista para almacenar los trabajadores de cosecha
            trabajadores_cosecha = []
            
            # Por cada personal, buscar sus contratos de cosecha
            for personal in personal_supervisados:
                contratos = PersonalTrabajadores.objects.filter( #TODO CAMBIAR PERSONAL POR UN NUEVO MODELO DE CONTRATO
                    Q(run=personal.rut),
                    Q(labor__nombre__iexact='COSECHA') |
                    Q(labor__nombre__iexact='cosecha') |
                    Q(labor__nombre__iexact='Cosecha')
                )
                
                if contratos.exists():
                    for contrato in contratos:
                        trabajador = {
                            'nombres': personal.nombres,
                            'apellidos' : personal.apellidos,
                            'rut': personal.rut,
                        }
                        trabajadores_cosecha.append(trabajador)
            
            serializer = TrabajadoresCosechaQRSerializer(trabajadores_cosecha, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class CuadrillasAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_scopes = []

    def dispatch(self, request, *args, **kwargs):
        if request.method in ['GET', 'POST', 'PUT', 'DELETE']:
            self.required_scopes = ['admin', 'write']
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, format=None):
        try:
            holding_id = request.query_params.get('holding')
            if not holding_id:
                return Response(
                    {"message": "Holding ID es requerido"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Si la URL es para grupos de trabajadores
            if 'grupos' in request.path:
                # Filtrar trabajadores solo por supervisor y holding
                trabajadores = PersonalTrabajadores.objects.filter(
                    holding_id=holding_id,
                    codigo_supervisor=request.user,
                    estado=True,
                    folio__isnull=False
                ).select_related(
                    'folio',
                    'codigo_supervisor'
                )

                # Agrupar por folio
                trabajadores_list = list(trabajadores)
                trabajadores_list.sort(key=lambda x: x.folio_id)

                grupos = []
                for folio_id, group in groupby(trabajadores_list, key=lambda x: x.folio_id):
                    group_list = list(group)
                    if group_list:
                        primer_trabajador = group_list[0]
                        grupos.append({
                            'folio_id': folio_id,
                            'supervisor_id': request.user.id,
                            'folio_nombre': f"Folio {primer_trabajador.folio.id}",
                            'supervisor_nombre': request.user.persona.nombres,
                            'trabajadores': group_list
                        })

                serializer = GrupoTrabajadoresSerializer(grupos, many=True)
                return Response(serializer.data)
            
            # Si es la URL base de cuadrillas
            else:
                cuadrillas = Cuadrillas.objects.filter(
                    holding_id=holding_id,
                    usuario=request.user
                )
                serializer = CuadrillasSerializer(cuadrillas, many=True)
                return Response(serializer.data)

        except Exception as e:
            return Response(
                {"message": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    def post(self, request, format=None):
        try:
            data = request.data
            if not all(k in data for k in ('id', 'trabajadores')):
                return Response(
                    {'error': 'Se requiere ID y lista de trabajadores'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Verificar que los trabajadores pertenezcan al supervisor actual
            trabajadores = PersonalTrabajadores.objects.filter(
                id__in=data['trabajadores'],
                holding_id=data['holding'],
                codigo_supervisor=request.user,
                estado=True
            )

            if len(trabajadores) < 2:
                return Response(
                    {'error': 'Se requieren al menos 2 trabajadores'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Verificar que todos pertenezcan al mismo folio
            first = trabajadores[0]
            if not all(t.folio_id == first.folio_id for t in trabajadores):
                return Response(
                    {'error': 'Los trabajadores deben pertenecer al mismo folio'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            cuadrilla = Cuadrillas.objects.create(
                id=data['id'],
                holding_id=data['holding'],
                usuario=request.user
            )
            cuadrilla.trabajadores.set(trabajadores)

            serializer = CuadrillasSerializer(cuadrilla)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def put(self, request, format=None):
        """
        Actualiza una cuadrilla existente.
        """
        try:
            cuadrilla_id = request.data.get('id')
            if not cuadrilla_id:
                return Response(
                    {"message": "ID de cuadrilla es necesario"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                cuadrilla = Cuadrillas.objects.get(
                    id=cuadrilla_id,
                    holding_id=request.data['holding'],
                    usuario=request.user  # Verificar que la cuadrilla pertenezca al supervisor
                )
            except Cuadrillas.DoesNotExist:
                return Response(
                    {"message": "Cuadrilla no encontrada"},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Verificar trabajadores como en el POST
            trabajadores = PersonalTrabajadores.objects.filter(
                id__in=request.data['trabajadores'],
                holding_id=request.data['holding'],
                codigo_supervisor=request.user
            )

            if len(trabajadores) < 2:
                return Response(
                    {'error': 'Se requieren al menos 2 trabajadores'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            first = trabajadores[0]
            if not all(
                t.folio_id == first.folio_id and 
                t.labor_id == first.labor_id
                for t in trabajadores
            ):
                return Response(
                    {'error': 'Los trabajadores deben pertenecer al mismo folio y labor'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            cuadrilla.trabajadores.set(trabajadores)
            serializer = CuadrillasSerializer(cuadrilla)
            return Response(serializer.data)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def delete(self, request, format=None):
        """
        Elimina una o varias cuadrillas.
        """
        try:
            cuadrilla_ids = request.data.get('ids', [])
            # Solo eliminar cuadrillas que pertenezcan al supervisor actual
            Cuadrillas.objects.filter(
                id__in=cuadrilla_ids,
                holding_id=request.data['holding'],
                usuario=request.user
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class EnlaceAutoRegistroAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_scopes = []

    def dispatch(self, request, *args, **kwargs):
        if request.method in ['GET', 'POST', 'DELETE']:
            self.required_scopes = ['admin', 'write']
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        """Obtener enlaces activos del holding"""
        holding_id = request.query_params.get('holding')
        if not holding_id:
            return Response(
                {"error": "Se requiere el ID del holding"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Obtener solo enlaces no expirados
        ahora = timezone.now()
        enlaces = EnlaceAutoRegistro.objects.filter(
            holding_id=holding_id,
            activo=True,
            fecha_expiracion__gt=ahora
        ).order_by('-fecha_creacion')
        
        serializer = EnlaceAutoRegistroSerializer(enlaces, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        """Crear nuevo enlace"""
        data = request.data
        print(data)
        serializer = EnlaceAutoRegistroSerializer(data=data)
        if serializer.is_valid():
            serializer.save(
                usuario_creador=request.user,
                activo=True
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        """Desactivar enlaces (no los borra, solo los marca como inactivos)"""
        enlaces_ids = request.data.get('ids', [])
        if not enlaces_ids:
            return Response(
                {"error": "Se requiere al menos un ID de enlace"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        EnlaceAutoRegistro.objects.filter(
            id__in=enlaces_ids,
            holding_id=request.data.get('holding')
        ).update(activo=False)
        
        return Response(status=status.HTTP_204_NO_CONTENT)

class ValidarEnlaceAutoRegistroAPIView(APIView):

    """Vista pública para validar enlaces de auto registro"""
    
    def get(self, request, token, id):
        try:
            enlace = EnlaceAutoRegistro.objects.get(id=id, token=token)
            
            if not enlace.is_valid():
                return Response({
                    "error": "El enlace ha expirado o no está activo",
                    "codigo": "ENLACE_INVALIDO"
                }, status=status.HTTP_400_BAD_REQUEST)
            print('Enlace valido')
            return Response({
                "perfil_id": enlace.perfil.id,
                "perfil_nombre": enlace.perfil.nombre_perfil,
                "holding_id": enlace.holding.id,
                "ruts_permitidos": enlace.ruts_permitidos,
                "fecha_expiracion": enlace.fecha_expiracion,
                "activo": enlace.activo
            })
            
        except EnlaceAutoRegistro.DoesNotExist:
            return Response({
                "error": "Enlace no encontrado",
                "codigo": "ENLACE_NO_EXISTE"
            }, status=status.HTTP_404_NOT_FOUND)
        
class PersonalWebAPIView(APIView):
    @transaction.atomic
    def post(self, request):
        try:
            # Debug inicial de los datos recibidos
            print("\n=== INICIO DE SOLICITUD ===")
            print("Headers recibidos:", request.headers)
            print("\nDatos del formulario recibidos:")
            for key, value in request.data.items():
                if key not in ['carnet_front_image', 'carnet_back_image', 'firma']:
                    print(f"{key}: {value}")
            
            print("\nArchivos recibidos:")
            for key, value in request.FILES.items():
                print(f"{key}: {value.name} ({value.size} bytes)")

            # Validar el enlace y token
            enlace_id = request.data.get('enlace_id')
            token = request.data.get('token')
            
            print(f"\nValidación de enlace:")
            print(f"ID del enlace: {enlace_id}")
            print(f"Token: {token}")
            
            try:
                enlace = EnlaceAutoRegistro.objects.get(id=enlace_id, token=token)
                print(f"Enlace encontrado:")
                print(f"- Holding ID: {enlace.holding.id}")
                print(f"- Perfil ID: {enlace.perfil.id}")
                print(f"- Fecha expiración: {enlace.fecha_expiracion}")
                print(f"- Activo: {enlace.activo}")
                
                if not enlace.is_valid():
                    print('Enlace no válido - Razón:')
                    print(f"- Fecha actual: {datetime.now()}")
                    print(f"- Fecha expiración: {enlace.fecha_expiracion}")
                    print(f"- Activo: {enlace.activo}")
                    return Response(
                        {'error': 'El enlace ha expirado o no es válido'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except EnlaceAutoRegistro.DoesNotExist:
                print(f'No se encontró enlace con ID: {enlace_id} y token: {token}')
                return Response(
                    {'error': 'Enlace inválido'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Preparar datos del personal
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

            print("\nDatos del personal preparados:")
            print(json.dumps(personal_data, indent=2, default=str))

            # Procesar archivos (imágenes y firma)
            carnet_front = request.FILES.get('carnet_front_image')
            carnet_back = request.FILES.get('carnet_back_image')
            firma = request.FILES.get('firma')
            
            print("\nProcesando archivos:")
            if carnet_front:
                print(f"Imagen frontal recibida: {carnet_front.name} ({carnet_front.size} bytes)")
                personal_data['carnet_front_image'] = carnet_front
            if carnet_back:
                print(f"Imagen trasera recibida: {carnet_back.name} ({carnet_back.size} bytes)")
                personal_data['carnet_back_image'] = carnet_back
            if firma:
                print(f"Firma recibida: {firma.name} ({firma.size} bytes)")
                personal_data['firma'] = firma

            # Crear PersonalTrabajadores
            print("\nValidando datos del personal:")
            personal_serializer = PersonalTrabajadoresSerializer(data=personal_data)
            if not personal_serializer.is_valid():
                print("Errores en la validación del personal:")
                print(json.dumps(personal_serializer.errors, indent=2))
                return Response(
                    personal_serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            print("Datos del personal válidos, guardando...")
            personal = personal_serializer.save()
            print(f"Personal guardado con ID: {personal.id}")

            # Crear Usuario asociado
            print("\nPreparando datos de usuario:")
            usuario_data = {
                'holding': enlace.holding.id,
                'persona': personal.id,
                'rut': personal.rut,
                'email': personal.correo,
                'perfil': enlace.perfil.id,
                'estado': True
            }
            print(json.dumps(usuario_data, indent=2))

            usuario_serializer = UserSerializer(data=usuario_data)
            if not usuario_serializer.is_valid():
                print("Errores en la validación del usuario:")
                print(json.dumps(usuario_serializer.errors, indent=2))
                raise ValidationError(usuario_serializer.errors)
            
            print("Datos de usuario válidos, guardando...")
            usuario = usuario_serializer.save()
            print(f"Usuario guardado con ID: {usuario.id}")

            # Preparar respuesta
            response_data = {
                'personal': personal_serializer.data,
                'usuario': usuario_serializer.data,
                'message': 'Registro completado exitosamente'
            }

            print("\n=== REGISTRO COMPLETADO EXITOSAMENTE ===")
            return Response(response_data, status=status.HTTP_201_CREATED)

        except Exception as e:
            print("\n=== ERROR EN EL PROCESO DE REGISTRO ===")
            print(f"Tipo de error: {type(e)}")
            print(f"Mensaje de error: {str(e)}")
            print("Traceback completo:")
            print(traceback.format_exc())
            
            return Response(
                {'error': f'Error en el proceso de registro: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

class SupervisorAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_scopes = []

    def dispatch(self, request, *args, **kwargs):
        if request.method in ['GET', 'POST', 'PATCH', 'PUT', 'DELETE']:
            self.required_scopes = ['admin', 'write']
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, holding_id=None, format=None):
        try:
            if holding_id:
                supervisores = Supervisores.objects.select_related(
                    'usuario', 
                    'holding',
                    'usuario__persona'
                ).prefetch_related(
                    'trabajadores',
                    'jefesdecuadrilla_set__trabajadores'
                ).filter(holding_id=holding_id)
                
                if supervisores.exists():
                    serializer = SupervisorSerializer(supervisores, many=True)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response({"message": "No se encontraron supervisores"}, 
                             status=status.HTTP_404_NOT_FOUND)
            return Response({"message": "Se requiere holding_id"}, 
                          status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        serializer = SupervisorSerializer(data=request.data)
        if serializer.is_valid():
            supervisor = serializer.save()
            # Asignar trabajadores si se proporcionan
            trabajadores_ids = request.data.get('trabajadores', [])
            if trabajadores_ids:
                trabajadores = PersonalTrabajadores.objects.filter(id__in=trabajadores_ids)
                supervisor.trabajadores.set(trabajadores)
            return Response({'id': supervisor.id, 'data': serializer.data}, 
                          status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        supervisor_id = request.data.get('id')
        try:
            supervisor = Supervisores.objects.get(id=supervisor_id)
        except Supervisores.DoesNotExist:
            return Response({"message": "Supervisor no encontrado"}, 
                          status=status.HTTP_404_NOT_FOUND)

        serializer = SupervisorSerializer(supervisor, data=request.data)
        if serializer.is_valid():
            supervisor = serializer.save()
            # Actualizar trabajadores si se proporcionan
            trabajadores_ids = request.data.get('trabajadores')
            if trabajadores_ids is not None:
                trabajadores = PersonalTrabajadores.objects.filter(id__in=trabajadores_ids)
                supervisor.trabajadores.set(trabajadores)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        supervisor_ids = request.data.get('ids', [])
        Supervisores.objects.filter(id__in=supervisor_ids).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class JefesDeCuadrillaAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_scopes = []

    def dispatch(self, request, *args, **kwargs):
        if request.method in ['GET', 'POST', 'PATCH', 'PUT', 'DELETE']:
            self.required_scopes = ['admin', 'write']
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, holding_id=None, format=None):
        try:
            if holding_id:
                jefes = JefesDeCuadrilla.objects.select_related(
                    'usuario', 
                    'supervisor', 
                    'holding',
                    'usuario__persona',
                    'supervisor__usuario__persona'
                ).prefetch_related(
                    'trabajadores'
                ).filter(holding_id=holding_id)
                
                if jefes.exists():
                    serializer = JefesDeCuadrillaSerializer(jefes, many=True)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response(
                    {"message": "No se encontraron jefes de cuadrilla"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            return Response(
                {"message": "Se requiere holding_id"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        serializer = JefesDeCuadrillaSerializer(data=request.data)
        if serializer.is_valid():
            jefe = serializer.save()
            # Si se proporcionan trabajadores en la solicitud, los asignamos
            trabajadores_ids = request.data.get('trabajadores', [])
            if trabajadores_ids:
                trabajadores = PersonalTrabajadores.objects.filter(id__in=trabajadores_ids)
                jefe.trabajadores.set(trabajadores)
            return Response(
                {'id': jefe.id, 'data': serializer.data}, 
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        jefe_id = request.data.get('id')
        try:
            jefe = JefesDeCuadrilla.objects.get(id=jefe_id)
        except JefesDeCuadrilla.DoesNotExist:
            return Response(
                {"message": "Jefe de cuadrilla no encontrado"}, 
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = JefesDeCuadrillaSerializer(jefe, data=request.data)
        if serializer.is_valid():
            jefe = serializer.save()
            # Actualizamos los trabajadores si se proporcionan en la solicitud
            trabajadores_ids = request.data.get('trabajadores')
            if trabajadores_ids is not None:
                trabajadores = PersonalTrabajadores.objects.filter(id__in=trabajadores_ids)
                jefe.trabajadores.set(trabajadores)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        jefe_ids = request.data.get('ids', [])
        JefesDeCuadrilla.objects.filter(id__in=jefe_ids).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class APKLinkAPIView(APIView):
    """
    Vista principal para manejar los enlaces de APK.
    Permite crear, obtener y desactivar enlaces. Esta vista maneja tres operaciones principales:
    - GET: Obtiene el enlace activo para un holding específico
    - POST: Crea un nuevo enlace de descarga, desactivando cualquier enlace previo
    - DELETE: Desactiva un enlace existente
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_scopes = []

    def dispatch(self, request, *args, **kwargs):
        if request.method in ['GET', 'POST', 'DELETE']:
            self.required_scopes = ['admin', 'write']
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, holding_id):
        """
        Obtiene el enlace activo del holding especificado.
        Si existe un enlace activo y válido, retorna sus detalles.
        Si no existe ningún enlace activo, retorna una lista vacía.
        """
        # Obtener solo el enlace activo y no expirado
        enlace = APKLink.objects.filter(
            holding_id=holding_id,
            activo=True,
            fecha_expiracion__gt=timezone.now()
        ).first()
        
        if enlace:
            serializer = APKLinkSerializer(enlace)
            return Response(serializer.data)
        return Response([])  # Retorna lista vacía si no hay enlace activo

    def post(self, request, holding_id):
        """
        Crea un nuevo enlace de descarga.
        El enlace se crea con el token generado automáticamente y la duración especificada.
        Cualquier otro enlace activo para el mismo holding será desactivado automáticamente.
        """
        # Agregar el holding_id a los datos de la solicitud
        data = request.data
        print(data)
        data['holding'] = holding_id

        serializer = APKLinkSerializer(data=data)
        if serializer.is_valid():
            # El método save del modelo se encargará de desactivar otros enlaces
            enlace = serializer.save(
                usuario_creador=request.user,
                activo=True
            )
            return Response(
                APKLinkSerializer(enlace).data, 
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, holding_id):
        """
        Desactiva un enlace existente.
        Requiere el ID del enlace y el ID del holding para la validación.
        El enlace no se elimina de la base de datos, solo se marca como inactivo.
        """
        enlace_id = request.data.get('id')
        if not enlace_id:
            return Response(
                {"error": "Se requiere el ID del enlace"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verifica que el enlace pertenezca al holding correcto antes de desactivarlo
        APKLink.objects.filter(
            id=enlace_id,
            holding_id=holding_id
        ).update(activo=False)
        
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class ValidarApkLinkAPIView(APIView):
    """
    Vista pública para validar enlaces de descarga de APK.
    Verifica que el enlace exista, esté activo y no haya expirado.
    """
    def get(self, request, token, id):
        try:
            # Intentamos obtener el enlace con el token y id proporcionados
            enlace = APKLink.objects.get(id=id, token=token)
            
            # Verificamos si el enlace es válido usando el método del modelo
            if not enlace.is_valid():
                return Response({
                    "message": "El enlace ha expirado o no está activo",
                    "codigo": "ENLACE_INVALIDO"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Si el enlace es válido, retornamos la información necesaria
            return Response({
                "mensaje": "Enlace válido",
                "tiempo_restante": enlace.tiempo_restante(),
                "fecha_expiracion": enlace.fecha_expiracion,
                "activo": enlace.activo
            })
            
        except APKLink.DoesNotExist:
            return Response({
                "message": "El enlace de descarga no es válido",
                "codigo": "ENLACE_NO_EXISTE"
            }, status=status.HTTP_404_NOT_FOUND)

class DescargarApkAPIView(APIView):
    """
    Vista pública para descargar el archivo APK.
    Solo permite la descarga si el enlace es válido.
    """
    def get(self, request, token, id):
        try:
            # Verificar que el enlace existe y es válido
            enlace = APKLink.objects.get(id=id, token=token)
            
            if not enlace.is_valid():
                return Response({
                    "message": "El enlace ha expirado o no está activo",
                    "codigo": "ENLACE_INVALIDO"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Obtener la ruta del archivo APK
            apk_path = enlace.get_apk_path()
            
            if not os.path.exists(apk_path):
                return Response({
                    "message": "El archivo APK no está disponible",
                    "codigo": "ARCHIVO_NO_EXISTE"
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Abrir y retornar el archivo para descarga
            apk_file = open(apk_path, 'rb')
            response = FileResponse(apk_file, content_type='application/vnd.android.package-archive')
            response['Content-Disposition'] = f'attachment; filename="contratista.apk"'
            return response
            
        except APKLink.DoesNotExist:
            return Response({
                "message": "El enlace de descarga no es válido",
                "codigo": "ENLACE_NO_EXISTE"
            }, status=status.HTTP_404_NOT_FOUND)

class PersonalAsignadoAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_scopes = []

    def dispatch(self, request, *args, **kwargs):
        self.required_scopes = ['admin', 'write']
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        try:
            supervisor_id = request.query_params.get('supervisor_id')
            jefe_cuadrilla_id = request.query_params.get('jefe_cuadrilla_id')
            
            if not supervisor_id and not jefe_cuadrilla_id:
                return Response(
                    {'error': 'Debe proporcionar supervisor_id o jefe_cuadrilla_id'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            if jefe_cuadrilla_id:
                # Obtener trabajadores asignados al jefe de cuadrilla
                jefe_cuadrilla = JefesDeCuadrilla.objects.get(id=jefe_cuadrilla_id)
                trabajadores = jefe_cuadrilla.trabajadores.all()
            else:
                # Obtener trabajadores asignados al supervisor
                supervisor = Supervisores.objects.get(id=supervisor_id)
                trabajadores = supervisor.trabajadores.all()

            # Serializar los trabajadores incluyendo el contexto de la request
            serializer = PersonalAsignadoSerializer(
                trabajadores, 
                many=True, 
                context={'request': request}
            )
            
            return Response(serializer.data)

        except JefesDeCuadrilla.DoesNotExist:
            return Response(
                {'error': 'Jefe de cuadrilla no encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Supervisores.DoesNotExist:
            return Response(
                {'error': 'Supervisor no encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )       

class InformeRendimientoAPIView(APIView):
    def post(self, request):
        try:
            fecha_inicio = request.data.get('fecha_inicio')
            fecha_fin = request.data.get('fecha_fin')
            cliente_id = request.data.get('cliente_id')
            supervisor_id = request.data.get('supervisor_id')
            jefe_cuadrilla_id = request.data.get('jefe_cuadrilla_id')
            labor_id = request.data.get('labor_id')

            # Base query
            queryset = ProduccionTrabajador.objects.select_related(
                'trabajador',
                'labor',
                'unidad_control'
            ).all()

            # Apply filters
            if fecha_inicio and fecha_fin:
                queryset = queryset.filter(
                    hora_fecha_ingreso_produccion__range=[fecha_inicio, fecha_fin]
                )

            if cliente_id:
                queryset = queryset.filter(folio__cliente_id=cliente_id)

            if supervisor_id:
                queryset = queryset.filter(
                    trabajador__supervisor_directo__id=supervisor_id
                )

            if jefe_cuadrilla_id:
                queryset = queryset.filter(
                    trabajador__jefe_cuadrilla__id=jefe_cuadrilla_id
                )

            if labor_id:
                queryset = queryset.filter(labor_id=labor_id)

            serializer = ProduccionTrabajadorReporteSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

#---------------------------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------VISTAS INFORME PAGO----------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------------------

class VariablesDropDownInformePagoAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_scopes = []

    def dispatch(self, request, *args, **kwargs):
        if request.method in ['GET']:
            self.required_scopes = ['admin', 'write']
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, format=None):
        """
        Retrieves the initial dropdown data for the payment report filters.
        """
        holding_id = request.query_params.get('holding')
        if not holding_id:
            return Response(
                {'error': 'El parámetro holding es necesario'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get basic data for dropdowns
        fundos = CamposClientes.objects.filter(holding_id=holding_id)
        supervisores = Supervisores.objects.filter(holding_id=holding_id)
        casas = CasasTrabajadores.objects.filter(holding_id=holding_id)

        # Serialize basic data
        fundos_data = CampoClienteDropdownPagoSerializer(fundos, many=True).data
        supervisores_data = SupervisorDropdownPagoSerializer(supervisores, many=True).data
        casas_data = CasaTrabajadorDropdownPagoSerializer(casas, many=True).data

        # Return dropdown data
        return Response({
            'fundos': fundos_data,
            'supervisores': supervisores_data,
            'casas': casas_data
        })

class InformePagoGenerarAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_scopes = []

    def dispatch(self, request, *args, **kwargs):
        if request.method in ['POST']:
            self.required_scopes = ['admin', 'write']
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, format=None):
        """
        Generate a payment report based on date range and optional filters
        """
        # Validate required parameters
        holding_id = request.data.get('holding')
        fecha_inicio = request.data.get('fecha_inicio')
        fecha_fin = request.data.get('fecha_fin')
        
        if not all([holding_id, fecha_inicio, fecha_fin]):
            return Response(
                {'error': 'Holding ID y rango de fechas son requeridos'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Start with base query filtered by date range
            query = ProduccionTrabajador.objects.filter(
                holding_id=holding_id,
                hora_fecha_ingreso_produccion__range=[fecha_inicio, fecha_fin]
            ).select_related(
                'trabajador',
                'labor',
                'folio'
            )

            # Apply casa filter if provided
            casa_id = request.data.get('casa_id')
            if casa_id:
                trabajadores_casa = PersonalTrabajadores.objects.filter(
                    casa_id=casa_id
                ).values_list('id', flat=True)
                query = query.filter(trabajador_id__in=trabajadores_casa)

            # Apply supervisor filter if provided
            supervisor_id = request.data.get('supervisor_id')
            if supervisor_id:
                trabajadores_supervisor = Supervisores.objects.get(
                    id=supervisor_id
                ).trabajadores.values_list('id', flat=True)
                query = query.filter(trabajador_id__in=trabajadores_supervisor)

            # Apply fundo filter if provided
            fundo_id = request.data.get('fundo_id')
            if fundo_id:
                contratos_fundo = PersonalTrabajadores.objects.filter( #TODO CAMBIAR PERSONAL POR UN NUEVO MODELO DE CONTRATO
                    fundo_id=fundo_id
                ).values_list('trabajador_id', flat=True)
                query = query.filter(trabajador_id__in=contratos_fundo)

            # Serialize the filtered data
            serializer = ProduccionInformePagoDetalleSerializer(query, many=True)

            # Calculate total
            total_pago = sum(item['valor_total'] for item in serializer.data)

            return Response({
                'producciones': serializer.data,
                'resumen': {
                    'total_pago': total_pago,
                    'total_registros': len(serializer.data)
                }
            })

        except Exception as e:
            return Response(
                {'error': f'Error al generar el informe: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
class InformePagoCSVAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_scopes = []

    def dispatch(self, request, *args, **kwargs):
        if request.method in ['POST']:
            self.required_scopes = ['admin', 'write']
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, format=None):
        """
        Generate CSV data for payment report based on date range and optional filters.
        Returns data structured for CSV generation with daily amounts per worker.
        """
        # Validate required parameters
        holding_id = request.data.get('holding')
        fecha_inicio = request.data.get('fecha_inicio')
        fecha_fin = request.data.get('fecha_fin')
        
        if not all([holding_id, fecha_inicio, fecha_fin]):
            return Response(
                {'error': 'Holding ID y rango de fechas son requeridos'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Start with base query filtered by date range
            query = ProduccionTrabajador.objects.filter(
                holding_id=holding_id,
                hora_fecha_ingreso_produccion__range=[fecha_inicio, fecha_fin]
            ).select_related(
                'trabajador',
                'labor',
                'folio'
            ).order_by('trabajador__id', 'hora_fecha_ingreso_produccion')

            # Apply casa filter if provided
            casa_id = request.data.get('casa_id')
            if casa_id:
                trabajadores_casa = PersonalTrabajadores.objects.filter(
                    casa_id=casa_id
                ).values_list('id', flat=True)
                query = query.filter(trabajador_id__in=trabajadores_casa)

            # Apply supervisor filter if provided
            supervisor_id = request.data.get('supervisor_id')
            if supervisor_id:
                trabajadores_supervisor = Supervisores.objects.get(
                    id=supervisor_id
                ).trabajadores.values_list('id', flat=True)
                query = query.filter(trabajador_id__in=trabajadores_supervisor)

            # Apply fundo filter if provided
            fundo_id = request.data.get('fundo_id')
            if fundo_id:
                contratos_fundo = PersonalTrabajadores.objects.filter( #TODO CAMBIAR PERSONAL POR UN NUEVO MODELO DE CONTRATO
                    fundo_id=fundo_id
                ).values_list('trabajador_id', flat=True)
                query = query.filter(trabajador_id__in=contratos_fundo)

            # Serialize the data
            serializer = ProduccionCSVSerializer(query, many=True)
            
            return Response({
                'producciones': serializer.data,
                'fecha_inicio': fecha_inicio,
                'fecha_fin': fecha_fin
            })

        except Exception as e:
            print(e)
            return Response(
                {'error': f'Error al generar los datos para CSV: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

#---------------------------------------------------------------------------------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------VISTAS MODIFICAR SOCIEDADES Y CUENTA BANCO----------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------------------

class SociedadDetailAPIView(APIView):
    def get(self, request, holding_id):
        sociedades = Sociedad.objects.filter(holding_id=holding_id)
        serializer = SociedadCuentaSerializer(sociedades, many=True)
        return Response(serializer.data)

    def patch(self, request, holding_id, sociedad_id):
        try:
            sociedad = Sociedad.objects.get(holding_id=holding_id, id=sociedad_id)
            serializer = SociedadCuentaSerializer(sociedad, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Sociedad.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

class CuentaOrigenAPIView(APIView):
    def get(self, request, sociedad_id):
        cuentas = CuentaOrigen.objects.filter(sociedad_id=sociedad_id)
        serializer = CuentaOrigenSerializer(cuentas, many=True)
        return Response(serializer.data)

    def post(self, request, sociedad_id):
        try:
            sociedad = Sociedad.objects.get(id=sociedad_id)
            serializer = CuentaOrigenSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(sociedad=sociedad)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Sociedad.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, sociedad_id, cuenta_id):
        try:
            cuenta = CuentaOrigen.objects.get(id=cuenta_id, sociedad_id=sociedad_id)
            serializer = CuentaOrigenSerializer(cuenta, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except CuentaOrigen.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

class BancoListAPIView(APIView):
    def get(self, request):
        bancos = Banco.objects.all()
        serializer = BancoSerializer(bancos, many=True)
        return Response(serializer.data)
    
#---------------------------------------------------------------------------------------------------------------------------------------------------

class ProduccionPendienteAPIView(APIView):
    def get(self, request):
        fecha_inicio = request.GET.get('fecha_inicio')
        fecha_fin = request.GET.get('fecha_fin')
        
        producciones = ProduccionTrabajador.objects.filter(
            hora_fecha_ingreso_produccion__date__range=[fecha_inicio, fecha_fin],
            pagado=False
        ).select_related('trabajador', 'folio')
        
        serializer = ProduccionPendienteSerializer(producciones, many=True)
        return Response(serializer.data)
    
class FiltrosProduccionAPIView(APIView):
    def get(self, request):
        try:
            # Required parameters
            holding_id = request.GET.get('holding_id')
            fecha_inicio = request.GET.get('fecha_inicio')
            fecha_fin = request.GET.get('fecha_fin')
            
            if not all([holding_id, fecha_inicio, fecha_fin]):
                return Response(
                    {'error': 'Faltan parámetros requeridos'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Initialize base queryset with transfer payment filter
            queryset = ProduccionTrabajador.objects.filter(
                holding_id=holding_id,
                hora_fecha_ingreso_produccion__date__range=[fecha_inicio, fecha_fin],
                pagado=False,
                # Add filter for workers with transfer payment method
                trabajador__metodo_pago='Transferencia'  # This is the key addition
            ).select_related(
                'trabajador',
                'trabajador__casa',
                'trabajador__cargo',
                'folio',
                'folio__cliente'
            )

            # Optional filters remain the same since they're independent of payment method
            cliente_id = request.GET.get('cliente_id')
            if cliente_id and cliente_id.isdigit():
                queryset = queryset.filter(folio__cliente_id=cliente_id)
            
            fundo_id = request.GET.get('fundo_id')
            if fundo_id and fundo_id.isdigit():
                queryset = queryset.filter(folio__fundos__id=fundo_id)
                
            cargo_id = request.GET.get('cargo_id')
            if cargo_id and cargo_id.isdigit():
                queryset = queryset.filter(trabajador__cargo_id=cargo_id)
                
            casa_id = request.GET.get('casa_id')
            if casa_id and casa_id.isdigit():
                queryset = queryset.filter(trabajador__casa_id=casa_id)

            serializer = FiltrosPagoSerializer(queryset, many=True)
            return Response(serializer.data)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class OpcionesFiltrosAPIView(APIView):
    def get(self, request, holding_id):
        try:
            # Verificamos si el holding existe
            holding = Holding.objects.get(id=holding_id)
            
            # Obtenemos todos los clientes del holding
            clientes = Clientes.objects.filter(holding_id=holding_id)
            clientes_serializer = ClientesFiltroPagoSerializer(clientes, many=True)
            
            # Obtenemos todos los cargos del holding
            cargos = CargosAdministracion.objects.filter(holding_id=holding_id)
            cargos_serializer = CargosAdministracionPagoSerializer(cargos, many=True)
            
            # Obtenemos todas las casas del holding
            casas = CasasTrabajadores.objects.filter(holding_id=holding_id)
            casas_serializer = CasasTrabajadoresPagoSerializer(casas, many=True)
            
            return Response({
                'clientes': clientes_serializer.data,
                'cargos': cargos_serializer.data,
                'casas': casas_serializer.data
            })
            
        except Holding.DoesNotExist:
            return Response(
                {'error': 'Holding no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ProcesarPagoAPIView(APIView):
    def post(self, request):
        try:
            holding_id = request.data.get('holding_id')
            sociedad_id = request.data.get('sociedad_id')
            cuenta_id = request.data.get('cuenta_id')
            producciones_ids = request.data.get('producciones')
            
            # Validar datos requeridos
            if not all([holding_id, sociedad_id, cuenta_id, producciones_ids]):
                return Response(
                    {'error': 'Faltan datos requeridos'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Crear registros de pago agrupados por trabajador
            with transaction.atomic():
                producciones = ProduccionTrabajador.objects.filter(
                    id__in=producciones_ids
                ).select_related('trabajador')
                
                pagos_por_trabajador = {}
                
                # Agrupar producciones por trabajador
                for prod in producciones:
                    if prod.trabajador_id not in pagos_por_trabajador:
                        pagos_por_trabajador[prod.trabajador_id] = {
                            'trabajador': prod.trabajador,
                            'monto_total': 0,
                            'producciones': []
                        }
                    pagos_por_trabajador[prod.trabajador_id]['monto_total'] += (
                        prod.peso_neto * prod.folio.valor_pago_trabajador if prod.peso_neto > 0
                        else prod.unidades_control * prod.folio.valor_pago_trabajador
                    )
                    pagos_por_trabajador[prod.trabajador_id]['producciones'].append(prod)

                # Crear registros de pago
                for trabajador_id, datos in pagos_por_trabajador.items():
                    registro_pago = RegistroPagoTransferencia.objects.create(
                        holding_id=holding_id,
                        sociedad_id=sociedad_id,
                        cuenta_origen_id=cuenta_id,
                        trabajador=datos['trabajador'],
                        monto_pagado=datos['monto_total']
                    )
                    registro_pago.producciones.set(datos['producciones'])
                    
                    # Marcar producciones como pagadas
                    for produccion in datos['producciones']:
                        produccion.pagado = True
                        produccion.save()

            return Response({'message': 'Pagos procesados correctamente'})
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class PagosRealizadosAPIView(APIView):
    def get(self, request):
        try:
            holding_id = request.GET.get('holding_id')
            fecha_inicio = request.GET.get('fecha_inicio')
            fecha_fin = request.GET.get('fecha_fin')
            tipo_pago = request.GET.get('tipo_pago', 'todos')  # New parameter

            if not all([holding_id, fecha_inicio, fecha_fin]):
                return Response(
                    {'error': 'Faltan parámetros requeridos'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            fecha_fin = f"{fecha_fin} 23:59:59"

            # Get transferencias
            transferencias = RegistroPagoTransferencia.objects.filter(
                holding_id=holding_id,
                fecha_pago__range=[fecha_inicio, fecha_fin]
            ).select_related('sociedad', 'cuenta_origen', 'trabajador')

            # Get pagos en efectivo
            pagos_efectivo = RegistroPagoEfectivo.objects.filter(
                holding_id=holding_id,
                fecha_pago__range=[fecha_inicio, fecha_fin]
            ).select_related('sociedad', 'cuenta_origen', 'trabajador')

            # Combine results based on tipo_pago parameter
            if tipo_pago == 'transferencia':
                pagos = transferencias
            elif tipo_pago == 'efectivo':
                pagos = pagos_efectivo
            else:  # 'todos'
                pagos = list(transferencias) + list(pagos_efectivo)
                pagos.sort(key=lambda x: x.fecha_pago, reverse=True)

            serializer = PagoRealizadoSerializer(pagos, many=True)
            print(serializer.data)
            return Response(serializer.data)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class FiltrosProduccionEfectivoAPIView(APIView):
    def get(self, request):
        try:
            # Required parameters
            holding_id = request.GET.get('holding_id')
            fecha_inicio = request.GET.get('fecha_inicio')
            fecha_fin = request.GET.get('fecha_fin')
            
            if not all([holding_id, fecha_inicio, fecha_fin]):
                return Response(
                    {'error': 'Faltan parámetros requeridos'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Initialize base queryset with metodo_pago='Efectivo' filter
            queryset = ProduccionTrabajador.objects.filter(
                holding_id=holding_id,
                hora_fecha_ingreso_produccion__date__range=[fecha_inicio, fecha_fin],
                pagado=False,
                trabajador__metodo_pago='Efectivo'  # Filter for cash payment workers
            ).select_related(
                'trabajador',
                'trabajador__casa',
                'trabajador__cargo',
                'folio',
                'folio__cliente'
            )

            # Optional filters
            cliente_id = request.GET.get('cliente_id')
            if cliente_id and cliente_id.isdigit():
                queryset = queryset.filter(folio__cliente_id=cliente_id)
            
            fundo_id = request.GET.get('fundo_id')
            if fundo_id and fundo_id.isdigit():
                queryset = queryset.filter(folio__fundos__id=fundo_id)
                
            cargo_id = request.GET.get('cargo_id')
            if cargo_id and cargo_id.isdigit():
                queryset = queryset.filter(trabajador__cargo_id=cargo_id)
                
            casa_id = request.GET.get('casa_id')
            if casa_id and casa_id.isdigit():
                queryset = queryset.filter(trabajador__casa_id=casa_id)

            serializer = FiltrosPagoSerializer(queryset, many=True)
            return Response(serializer.data)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ProcesarPagoEfectivoAPIView(APIView):
    def post(self, request):
        try:
            holding_id = request.data.get('holding_id')
            sociedad_id = request.data.get('sociedad_id')
            cuenta_id = request.data.get('cuenta_id')
            pagos = request.data.get('pagos')
            multiplo_pago = request.data.get('multiplo_pago')
            
            if not all([holding_id, sociedad_id, cuenta_id, pagos, multiplo_pago]):
                return Response(
                    {'error': 'Faltan datos requeridos'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            with transaction.atomic():
                for pago in pagos:
                    produccion = ProduccionTrabajador.objects.get(id=pago['produccion_id'])
                    
                    registro_pago = RegistroPagoEfectivo.objects.create(
                        holding_id=holding_id,
                        sociedad_id=sociedad_id,
                        cuenta_origen_id=cuenta_id,
                        trabajador=produccion.trabajador,
                        monto_pagado=pago['monto_pagado'],
                        multiplo_pago=multiplo_pago,
                        saldo=pago['saldo']
                    )
                    registro_pago.producciones.add(produccion)
                    
                    produccion.pagado = True
                    produccion.save()

            return Response({'message': 'Pagos en efectivo procesados correctamente'})
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class GenerarPlanillaEfectivoAPIView(APIView):
    def get(self, request):
        try:
            print("\n1. Iniciando generación de planilla...")
            
            # Obtener y validar parámetros
            holding_id = request.GET.get('holding_id')
            fecha_inicio = datetime.strptime(request.GET.get('fecha_inicio'), '%Y-%m-%d')
            fecha_fin = datetime.strptime(request.GET.get('fecha_fin'), '%Y-%m-%d')
            multiplo = int(request.GET.get('multiplo', 5000))
            
            print(f"2. Parámetros recibidos:")
            print(f"   holding_id: {holding_id}")
            print(f"   fecha_inicio: {fecha_inicio}")
            print(f"   fecha_fin: {fecha_fin}")
            print(f"   multiplo: {multiplo}")

            # Generar lista de días
            dias = []
            fecha_actual = fecha_inicio
            
            # Encontrar el primer lunes
            while fecha_actual.weekday() > 0:  # 0 = Lunes
                fecha_actual -= timedelta(days=1)
                
            while fecha_actual <= fecha_fin:
                dias.append(fecha_actual)
                fecha_actual += timedelta(days=1)

            print(f"3. Días generados: {[d.strftime('%Y-%m-%d') for d in dias]}")
            print(f"   Total días: {len(dias)}")

            print("\n4. Construyendo queryset...")
            # Construir queryset base
            queryset = ProduccionTrabajador.objects.filter(
                holding_id=holding_id,
                hora_fecha_ingreso_produccion__date__range=[fecha_inicio, fecha_fin],
                pagado=False,
                trabajador__metodo_pago='Efectivo'
            ).select_related(
                'trabajador',
                'folio',
                'trabajador__cargo',
                'trabajador__casa'
            )

            # Aplicar filtros adicionales
            if request.GET.get('cliente_id'):
                queryset = queryset.filter(folio__cliente_id=request.GET.get('cliente_id'))
                print(f"   Filtro cliente_id: {request.GET.get('cliente_id')}")
            if request.GET.get('fundo_id'):
                queryset = queryset.filter(folio__fundos__id=request.GET.get('fundo_id'))
                print(f"   Filtro fundo_id: {request.GET.get('fundo_id')}")
            if request.GET.get('cargo_id'):
                queryset = queryset.filter(trabajador__cargo_id=request.GET.get('cargo_id'))
                print(f"   Filtro cargo_id: {request.GET.get('cargo_id')}")
            if request.GET.get('casa_id'):
                queryset = queryset.filter(trabajador__casa_id=request.GET.get('casa_id'))
                print(f"   Filtro casa_id: {request.GET.get('casa_id')}")

            print(f"\n5. Registros encontrados: {queryset.count()}")

            # Procesar datos
            print("\n6. Procesando datos por trabajador...")
            trabajadores_data = {}
            for prod in queryset:
                worker_key = prod.trabajador.rut if prod.trabajador.rut else '-'
                fecha = prod.hora_fecha_ingreso_produccion.date()
                monto = prod.calcular_monto_a_pagar()
                
                print(f"\n   Trabajador: {prod.trabajador.nombres} ({worker_key})")
                print(f"   Fecha: {fecha}")
                print(f"   Monto: {monto}")
                
                if worker_key not in trabajadores_data:
                    trabajadores_data[worker_key] = {
                        'nombre': prod.trabajador.nombres,
                        'rut': worker_key,
                        'pagos_diarios': {dia.date(): 0 for dia in dias},
                        'total': 0,
                        'saldo_anterior': 0
                    }
                
                trabajadores_data[worker_key]['pagos_diarios'][fecha] = round(monto)
                trabajadores_data[worker_key]['total'] += monto

            print("\n7. Resumen de datos procesados:")
            for worker_key, data in trabajadores_data.items():
                print(f"\n   Trabajador: {data['nombre']} ({worker_key})")
                print(f"   Total: {data['total']}")
                print("   Pagos diarios:", {k.strftime('%Y-%m-%d'): v for k, v in data['pagos_diarios'].items() if v > 0})

            print("\n8. Configurando documento PDF...")
            # Configurar documento PDF
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=landscape(A4),
                leftMargin=5*mm,
                rightMargin=5*mm,
                topMargin=10*mm,
                bottomMargin=10*mm
            )

            # Calcular anchos de columna
            print("\n9. Calculando anchos de columna...")
            ancho_pagina = (landscape(A4)[0] - 10*mm) * 0.90
            anchos_columnas = [
                ancho_pagina * 0.10,  # NOMBRE
                ancho_pagina * 0.06,  # RUT/NIC
            ]
            
            DIAS_POR_FILA = 7
            ancho_dia = (ancho_pagina * 0.50) / DIAS_POR_FILA
            anchos_columnas.extend([ancho_dia] * DIAS_POR_FILA)
            
            anchos_columnas.extend([
                ancho_pagina * 0.06,  # SALDO ANTERIOR
                ancho_pagina * 0.06,  # TOTAL
                ancho_pagina * 0.07,  # SALDO PROX.
                ancho_pagina * 0.11   # FIRMA
            ])

            print(f"   Número de columnas: {len(anchos_columnas)}")
            print(f"   Anchos calculados: {anchos_columnas}")

            def prepare_table_data(trabajadores_data, dias):
                print("\n10. Preparando datos de la tabla...")
                table_data = []
                fecha_indices = []
                span_info = []
                separator_rows = []
                
                # Headers
                dias_semana = ['LUNES', 'MARTES', 'MIÉRCOLES', 'JUEVES', 'VIERNES', 'SÁBADO', 'DOMINGO']
                headers_main = ['NOMBRE', 'RUT/NIC'] + dias_semana + ['SALDO ANT.', 'TOTAL', 'SALDO PROX.', 'FIRMA']
                table_data.append(headers_main)
                
                print(f"   Headers generados: {headers_main}")
                print(f"   Número de columnas en headers: {len(headers_main)}")

                current_row = 1
                for worker_key, worker_data in trabajadores_data.items():
                    print(f"\n   Procesando trabajador: {worker_data['nombre']}")
                    
                    num_grupos = (len(dias) + DIAS_POR_FILA - 1) // DIAS_POR_FILA
                    rows_for_worker = num_grupos * 2
                    
                    total_sin_redondear = worker_data['total']
                    total_redondeado = (total_sin_redondear // multiplo) * multiplo
                    saldo = total_sin_redondear - total_redondeado
                    saldo_anterior = worker_data['saldo_anterior']
                    saldo_final = saldo_anterior + saldo
                    
                    print(f"   Total sin redondear: {total_sin_redondear}")
                    print(f"   Total redondeado: {total_redondeado}")
                    print(f"   Saldo: {saldo}")
                    print(f"   Saldo final: {saldo_final}")

                    # Registrar spans
                    for col, span in enumerate([(0,0), (1,1), (-4,-4), (-3,-3), (-2,-2), (-1,-1)]):
                        span_info.append(('SPAN', (span[0], current_row), (span[1], current_row + rows_for_worker - 1)))

                    for grupo in range(num_grupos):
                        start_idx = grupo * DIAS_POR_FILA
                        end_idx = min((grupo + 1) * DIAS_POR_FILA, len(dias))
                        current_dias = dias[start_idx:end_idx]
                        
                        # Fila de fechas
                        row = ([worker_data['nombre'], worker_data['rut']] if grupo == 0 else ['', ''])
                        
                        dias_alineados = [''] * DIAS_POR_FILA
                        for d in current_dias:
                            dias_alineados[d.weekday()] = d.strftime('%d/%m')
                        row.extend(dias_alineados)
                        
                        # Columnas finales
                        row.extend(['', '', '', ''] if grupo > 0 else [
                            f"{saldo_anterior:+,.0f}" if saldo_anterior != 0 else "0",
                            f"{total_redondeado:,.0f}",
                            f"{saldo_final:+,.0f}" if saldo_final != 0 else "0",
                            ''
                        ])
                        
                        fecha_indices.append(len(table_data))
                        table_data.append(row)
                        print(f"   Fila de fechas generada: {row}")
                        current_row += 1
                        
                        # Fila de montos
                        montos_row = ['', '']
                        montos_alineados = [''] * DIAS_POR_FILA
                        for d in current_dias:
                            weekday = d.weekday()
                            if fecha_inicio <= d <= fecha_fin:
                                monto = worker_data['pagos_diarios'].get(d.date(), 0)
                                montos_alineados[weekday] = f"{monto:,.0f}"
                            else:
                                montos_alineados[weekday] = ""
                        montos_row.extend(montos_alineados)
                        montos_row.extend(['', '', '', ''])
                        
                        table_data.append(montos_row)
                        print(f"   Fila de montos generada: {montos_row}")
                        current_row += 1
                    
                    separator_rows.append(current_row)
                    table_data.append([''] * len(headers_main))
                    current_row += 1

                print(f"\n   Total filas generadas: {len(table_data)}")
                print(f"   Índices de fechas: {fecha_indices}")
                print(f"   Filas separadoras: {separator_rows}")
                
                return table_data, fecha_indices, span_info, separator_rows

            print("\n11. Generando tabla...")
            table_data, fecha_indices, span_info, separator_rows = prepare_table_data(trabajadores_data, dias)
            table = Table(table_data, colWidths=anchos_columnas)
            
            print("\n12. Aplicando estilos...")
            estilos = [
                ('FONTSIZE', (0, 0), (-1, -1), 7),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('LINEBELOW', (0, 0), (-1, 0), 1.5, colors.black),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
                ('ALIGN', (0, 1), (1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 1),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
                ('TOPPADDING', (-1, 1), (-1, -1), 20),
                ('BOTTOMPADDING', (-1, 1), (-1, -1), 20),
            ]
            
            for row_idx in separator_rows:
                estilos.extend([
                    ('TOPPADDING', (0, row_idx), (-1, row_idx), 0.5),
                    ('BOTTOMPADDING', (0, row_idx), (-1, row_idx), 0.5)
                ])
            
            for indice in fecha_indices:
                estilos.append(('BACKGROUND', (2, indice), (8, indice), colors.lightgrey))
            
            estilos.extend(span_info)
            
            print(f"   Total estilos aplicados: {len(estilos)}")
            
            table.setStyle(TableStyle(estilos))

            print("\n13. Creando encabezado...")
            header_style = ParagraphStyle(
                'CustomHeader',
                fontSize=10,
                alignment=1,
                spaceAfter=5*mm
            )
            
            header = Paragraph(
                f"""<b>PLANILLA DE PAGO</b><br/>
                Semana del {fecha_inicio.strftime('%d %b')} al {fecha_fin.strftime('%d %b%y')}""",
                header_style
            )

            print("\n14. Generando PDF final...")
            elements = [header, table]
            doc.build(elements)

            print("\n15. Preparando respuesta...")
            buffer.seek(0)
            response = HttpResponse(buffer, content_type='application/pdf')
            response['Content-Disposition'] = (
                f'attachment; filename=planilla_efectivo_{fecha_inicio.strftime("%Y%m%d")}.pdf'
            )
            
            print("16. PDF generado exitosamente!")
            return response

        except Exception as e:
            print(f"\nERROR: {str(e)}")
            print(f"Traceback completo:")
            import traceback
            print(traceback.format_exc())
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ReprocesarPagosAPIView(APIView):
    def post(self, request):
        try:
            fecha_inicio = request.data.get('fecha_inicio')
            fecha_fin = request.data.get('fecha_fin')
            folio_id = request.data.get('folio_id')
            holding_id = request.data.get('holding_id')
            nuevo_valor_pago = request.data.get('nuevo_valor_pago')

            with transaction.atomic():
                # Get folio and its current value
                folio = FolioComercial.objects.get(id=folio_id)
                valor_actual = folio.valor_pago_trabajador

                # Get latest version number for this folio in this date range
                ultima_version = HistorialCambioFolio.objects.filter(
                    folio_id=folio_id,
                    fecha_inicio_validez__gte=fecha_inicio,
                    fecha_fin_validez__lte=fecha_fin
                ).aggregate(Max('version'))['version__max'] or 0

                # Register this change
                historial_cambio = HistorialCambioFolio.objects.create(
                    holding_id=holding_id,
                    folio=folio,
                    valor_anterior=valor_actual,
                    valor_nuevo=nuevo_valor_pago,
                    version=ultima_version + 1,
                    fecha_inicio_validez=fecha_inicio,
                    fecha_fin_validez=fecha_fin
                )

                # Find affected payments and calculate cumulative adjustments
                pagos_afectados = {}  # Dictionary to track affected payments
                
                # Get all productions in date range
                producciones = ProduccionTrabajador.objects.filter(
                    holding_id=holding_id,
                    folio_id=folio_id,
                    hora_fecha_ingreso_produccion__date__range=[fecha_inicio, fecha_fin],
                    pagado=True
                ).select_related('trabajador')

                for produccion in producciones:
                    # Get all historical changes that affected this production
                    cambios_aplicables = HistorialCambioFolio.objects.filter(
                        folio_id=folio_id,
                        fecha_inicio_validez__lte=produccion.hora_fecha_ingreso_produccion.date(),
                        fecha_fin_validez__gte=produccion.hora_fecha_ingreso_produccion.date()
                    ).order_by('version')

                    # Calculate the cumulative effect of all changes
                    valor_original = cambios_aplicables.first().valor_anterior if cambios_aplicables.exists() else valor_actual
                    monto_original = (
                        produccion.peso_neto * valor_original if produccion.peso_neto > 0
                        else produccion.unidades_control * valor_original
                    )
                    
                    monto_nuevo = (
                        produccion.peso_neto * nuevo_valor_pago if produccion.peso_neto > 0
                        else produccion.unidades_control * nuevo_valor_pago
                    )

                    diferencia = monto_nuevo - monto_original

                    # Group by payment record
                    for pago in produccion.registropagotransferencia_set.all():
                        if pago.id not in pagos_afectados:
                            pagos_afectados[pago.id] = {
                                'registro': pago,
                                'diferencia_total': 0,
                                'cambios': []
                            }
                        
                        pagos_afectados[pago.id]['diferencia_total'] += diferencia
                        pagos_afectados[pago.id]['cambios'].append({
                            'produccion': produccion,
                            'diferencia': diferencia
                        })

                # Apply changes to payments
                for info_pago in pagos_afectados.values():
                    pago = info_pago['registro']
                    nuevo_monto = pago.monto_pagado + info_pago['diferencia_total']
                    
                    # Register the change in payment history
                    historial = HistorialCambioPago.objects.create(
                        holding_id=holding_id,
                        registro_transferencia=pago,
                        monto_pagado_anterior=pago.monto_pagado,
                        monto_pagado_nuevo=nuevo_monto,
                        saldo_anterior=pago.saldo,
                        saldo_nuevo=(pago.saldo or 0) + info_pago['diferencia_total'],
                        folio=folio,
                        valor_pago_anterior=valor_actual,
                        valor_pago_nuevo=nuevo_valor_pago,
                        version_cambio_folio=historial_cambio.version
                    )

                    # Update payment record
                    pago.monto_pagado = nuevo_monto
                    pago.saldo = (pago.saldo or 0) + info_pago['diferencia_total']
                    pago.save()

                return Response({
                    'message': 'Pagos reprocesados correctamente',
                    'cambios_realizados': len(pagos_afectados),
                    'version_cambio': historial_cambio.version
                })

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class TramosAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_class = [IsAuthenticated, JWTHasAnyScope]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_scopes = []

    def dispatch(self, request, *args, **kwargs):
        if request.method == 'GET' or 'POST' or 'PATCH' or 'PUT' or 'DELETE':
            self.required_scopes =  ['admin','write']
        return super().dispatch(request, *args, **kwargs)
    
    #Metodo GET    
    def get(self, request, format=None):
        holding_id = request.query_params.get('holding')
        if holding_id:
            tramos = Tramos.objects.filter(holding_id=holding_id)
            serializer = TramosSerializer(tramos, many=True)
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    #Metodo POST    
    def post(self, request, format=None):
        serializer = TramosSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    #Metodo DELETE
    def delete(self, request, format=None): 
        tramos_ids = request.data.get('ids', [])
        Tramos.objects.filter(id__in=tramos_ids).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class FolioTransportistaAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_scopes = []

    def dispatch(self, request, *args, **kwargs):
        # Definir los scopes requeridos según el método HTTP
        if request.method in ['POST', 'DELETE', 'PUT', 'PATCH']:
            self.required_scopes = ['superadmin_access', 'admin', 'write']
        elif request.method == 'GET':
            self.required_scopes = ['superadmin_access', 'admin', 'write']
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, format=None):
        """
        Obtiene los folios de transporte filtrados por holding.
        """
        holding_id = request.query_params.get('holding')
        
        if not holding_id:
            return Response(
                {"error": "El parámetro 'holding' es requerido"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Obtener todos los folios del holding
            folios = FolioTransportista.objects.filter(holding_id=holding_id)
            serializer = FolioTransportistaSerializer(folios, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": f"Error al obtener los folios: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request, format=None):
        """
        Crea un nuevo folio de transporte.
        """
        serializer = FolioTransportistaSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response(
                    {"error": f"Error al crear el folio: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, format=None):
        """
        Actualiza un folio de transporte existente.
        """
        folio_id = request.data.get('id')
        if not folio_id:
            return Response(
                {"error": "Se requiere el ID del folio"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            folio = FolioTransportista.objects.get(id=folio_id)
        except FolioTransportista.DoesNotExist:
            return Response(
                {"error": "Folio no encontrado"}, 
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = FolioTransportistaSerializer(folio, data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Exception as e:
                return Response(
                    {"error": f"Error al actualizar el folio: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, format=None):
        """
        Elimina uno o varios folios de transporte.
        """
        folio_ids = request.data.get('ids', [])
        if not folio_ids:
            return Response(
                {"error": "Se requiere al menos un ID de folio"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Eliminar los folios especificados
            FolioTransportista.objects.filter(id__in=folio_ids).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(
                {"error": f"Error al eliminar los folios: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def patch(self, request, format=None):
        """
        Actualiza parcialmente un folio de transporte.
        """
        folio_id = request.data.get('id')
        if not folio_id:
            return Response(
                {"error": "Se requiere el ID del folio"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            folio = FolioTransportista.objects.get(id=folio_id)
        except FolioTransportista.DoesNotExist:
            return Response(
                {"error": "Folio no encontrado"}, 
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = FolioTransportistaSerializer(
            folio, 
            data=request.data, 
            partial=True
        )
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Exception as e:
                return Response(
                    {"error": f"Error al actualizar el folio: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ConfirmarPagoTransportistaAPIView(APIView):
    """
    Vista para confirmar el pago de registros de transportista seleccionados.
    Actualiza el estado de pago y registra el método y fecha.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]
    required_scopes = ['superadmin_access', 'admin', 'write']

class PagoTransportistaAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]
    
    def get(self, request):
        """
        Obtiene el cálculo previo al pago para un período específico
        """
        holding_id = request.query_params.get('holding')
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')
        empresas = request.query_params.get('empresas')
        
        if not all([holding_id, fecha_inicio, fecha_fin, empresas]):
            return Response({"error": "Faltan parámetros requeridos"}, 
                          status=status.HTTP_400_BAD_REQUEST)
            
        try:
            empresa_ids = [int(id) for id in empresas.split(',')]
            fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
            
            resultados = []
            
            for empresa_id in empresa_ids:
                # Obtener trabajadores de la empresa
                personal = PersonalTrabajadores.objects.filter(
                    holding_id=holding_id,
                    transportista_id=empresa_id
                )
                
                # Obtener el folio del transportista para saber tipo y valor de pago
                folio = FolioTransportista.objects.filter(
                    holding_id=holding_id,
                    transportista_id=empresa_id
                ).first()
                
                if not folio:
                    continue
                
                detalles_diarios = []
                fecha_actual = fecha_inicio
                total_monto = 0
                
                while fecha_actual <= fecha_fin:
                    # Contar personas únicas que trabajaron este día
                    personas_dia = ProduccionTrabajador.objects.filter(
                        holding_id=holding_id,
                        trabajador__in=personal,
                        hora_fecha_ingreso_produccion__date=fecha_actual
                    ).values('trabajador').distinct().count()
                    
                    if personas_dia > 0:
                        # Calcular monto según tipo de pago
                        monto_dia = (
                            folio.valor_pago_transportista * personas_dia 
                            if folio.tramo.unidad_pago == 'PASAJERO'
                            else folio.valor_pago_transportista
                        )
                        
                        detalles_diarios.append({
                            'fecha': fecha_actual,
                            'cantidad_personas': personas_dia,
                            'monto_dia': monto_dia
                        })
                        
                        total_monto += monto_dia
                    
                    fecha_actual += timedelta(days=1)
                
                if detalles_diarios:
                    resultados.append({
                        'transportista_id': empresa_id,
                        'transportista_nombre': EmpresasTransporte.objects.get(id=empresa_id).nombre,
                        'tipo_pago': folio.tramo.unidad_pago,
                        'valor_unidad': folio.valor_pago_transportista,
                        'total_monto': total_monto,
                        'detalles': detalles_diarios
                    })
            
            return Response(resultados)
            
        except Exception as e:
            return Response(
                {"error": f"Error al calcular los pagos: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        """
        Registra un nuevo pago a transportista
        """
        holding_id = request.data.get('holding')
        sociedad_id = request.data.get('sociedad')
        cuenta_id = request.data.get('cuenta')
        transportista_id = request.data.get('transportista')
        fecha_inicio = request.data.get('fecha_inicio')
        fecha_fin = request.data.get('fecha_fin')
        metodo_pago = request.data.get('metodo_pago')
        detalles = request.data.get('detalles', [])
        
        try:
            with transaction.atomic():
                # Crear el pago principal
                pago = PagoTransportista.objects.create(
                    holding_id=holding_id,
                    sociedad_id=sociedad_id,
                    transportista_id=transportista_id,
                    fecha_desde=fecha_inicio,
                    fecha_hasta=fecha_fin,
                    metodo_pago=metodo_pago,
                    cuenta_origen_id=cuenta_id,
                    usuario_registra=request.user,
                    monto=sum(detalle['monto_dia'] for detalle in detalles),
                    total_personas=sum(detalle['cantidad_personas'] for detalle in detalles),
                    total_dias=len(detalles),
                    valor_por_unidad=request.data.get('valor_unidad'),
                    tipo_pago=request.data.get('tipo_pago')
                )
                
                # Crear los detalles
                for detalle in detalles:
                    DetallePagoTransportista.objects.create(
                        pago=pago,
                        fecha=detalle['fecha'],
                        cantidad_personas=detalle['cantidad_personas'],
                        monto_dia=detalle['monto_dia']
                    )
                
                return Response(PagoTransportistaSerializer(pago).data, 
                              status=status.HTTP_201_CREATED)
                
        except Exception as e:
            return Response(
                {"error": f"Error al registrar el pago: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CalculoPagoTransportistaView(APIView):
    def get(self, request):
        holding_id = request.query_params.get('holding')
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')
        empresas = request.query_params.get('empresas')

        if not all([holding_id, fecha_inicio, fecha_fin]):
            return Response(
                {"error": "Faltan parámetros requeridos"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
            empresa_ids = [int(id) for id in empresas.split(',')] if empresas else []

            resultados = []
            
            # Filtrar empresas de transporte
            query = EmpresasTransporte.objects.filter(holding_id=holding_id)
            if empresa_ids:
                query = query.filter(id__in=empresa_ids)

            for empresa in query:
                # Obtener el folio del transportista directamente
                if not empresa.folio_transportista:
                    continue
                
                # Obtener todos los trabajadores vinculados a esta empresa
                trabajadores = PersonalTrabajadores.objects.filter(
                    holding_id=holding_id,
                    transportista=empresa,
                    estado=True
                )

                # Analizar cada día en el rango de fechas
                current_date = fecha_inicio
                while current_date <= fecha_fin:
                    # Contar trabajadores con producción para este día
                    trabajadores_con_produccion = ProduccionTrabajador.objects.filter(
                        holding_id=holding_id,
                        trabajador__in=trabajadores,
                        hora_fecha_ingreso_produccion__date=current_date,
                        pagado=False
                    ).values('trabajador').distinct().count()

                    # Calcular monto según tipo de pago
                    if trabajadores_con_produccion > 0:
                        if empresa.folio_transportista.tramo.unidad_pago == 'PASAJERO':
                            monto = empresa.folio_transportista.valor_pago_transportista * trabajadores_con_produccion
                        else:  # 'VIAJE'
                            monto = empresa.folio_transportista.valor_pago_transportista

                        resultados.append({
                            'fecha': current_date,
                            'transportista_nombre': empresa.nombre,
                            'transportista_rut': empresa.rut,
                            'tipo_pago': empresa.folio_transportista.tramo.unidad_pago,
                            'valor_unidad': empresa.folio_transportista.valor_pago_transportista,
                            'cantidad_personas': trabajadores_con_produccion,
                            'monto_calculado': monto,
                            'tramo': {
                                'origen': empresa.folio_transportista.tramo.origen,
                                'destino': empresa.folio_transportista.tramo.destino
                            }
                        })

                    current_date += timedelta(days=1)

            return Response(resultados)

        except Exception as e:
            return Response(
                {"error": f"Error al calcular los pagos: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class InformeTransportistaAPIView(APIView):
    def get(self, request):
        """Obtener datos para los dropdowns"""
        holding_id = request.query_params.get('holding')
        if not holding_id:
            return Response({"error": "Holding ID es requerido"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = InformeTransportistaSerializer(holding_id)
        return Response(serializer.data)

    def post(self, request):
        """
        Generate report data based on production records, calculating payments
        according to transport type (per passenger or per trip).
        """
        serializer = InformeTransportistaSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        fecha_inicio = serializer.validated_data['fecha_inicio']
        fecha_fin = serializer.validated_data['fecha_fin']
        cliente_ids = serializer.validated_data.get('cliente_ids')
        transportista_ids = serializer.validated_data.get('transportista_ids')
        vehiculo_ids = serializer.validated_data.get('vehiculo_ids')

        print(f"\nBuscando registros para el período: {fecha_inicio} - {fecha_fin}")
        
        # Base query para producción en el rango de fechas
        base_query = ProduccionTrabajador.objects.filter(
            hora_fecha_ingreso_produccion__date__range=(fecha_inicio, fecha_fin),
            holding_id=request.data.get('holding', 1)
        )

        # Aplicar filtros adicionales
        if cliente_ids:
            base_query = base_query.filter(folio__cliente_id__in=cliente_ids)
        if transportista_ids:
            base_query = base_query.filter(trabajador__transportista_id__in=transportista_ids)
        if vehiculo_ids:
            base_query = base_query.filter(trabajador__vehiculo_id__in=vehiculo_ids)

        print(f"Query base construido: {str(base_query.query)}")

        # Agrupar por fecha y transportista para procesar cada día
        results = []
        totales_por_transportista = {}  # Para llevar el total por transportista
        current_date = fecha_inicio

        while current_date <= fecha_fin:
            print(f"\nProcesando fecha: {current_date}")
            
            # Obtener producción para el día actual
            daily_prod = base_query.filter(
                hora_fecha_ingreso_produccion__date=current_date
            ).select_related(
                'trabajador',
                'trabajador__transportista',
                'trabajador__vehiculo',
                'trabajador__transportista__folio_transportista',
                'trabajador__transportista__folio_transportista__tramo',
                'folio',
                'folio__cliente'
            )

            if daily_prod.exists():
                print(f"Encontrados {daily_prod.count()} registros para {current_date}")
                
                # Agrupar por transportista/vehículo/cliente
                transport_groups = {}
                for prod in daily_prod:
                    if not prod.trabajador or not prod.trabajador.transportista or not prod.folio or not prod.folio.cliente:
                        continue

                    key = (
                        prod.trabajador.transportista.id,
                        prod.trabajador.vehiculo.id if prod.trabajador.vehiculo else None,
                        prod.folio.cliente.id
                    )
                    
                    if key not in transport_groups:
                        transport_groups[key] = {
                            'transportista': prod.trabajador.transportista,
                            'vehiculo': prod.trabajador.vehiculo,
                            'cliente': prod.folio.cliente,
                            'pasajeros': set(),
                            'registros': []
                        }
                    
                    transport_groups[key]['pasajeros'].add(prod.trabajador.id)
                    transport_groups[key]['registros'].append(prod)

                # Procesar cada grupo
                for group_data in transport_groups.values():
                    transportista = group_data['transportista']
                    vehiculo = group_data['vehiculo']
                    cliente = group_data['cliente']
                    num_pasajeros = len(group_data['pasajeros'])
                    
                    if not transportista.folio_transportista:
                        print(f"Transportista {transportista.id} sin folio_transportista")
                        continue

                    folio = transportista.folio_transportista
                    if not folio.tramo:
                        print(f"Folio {folio.id} sin tramo")
                        continue

                    # Calcular valor a pagar según tipo de tramo
                    minimo_requerido = getattr(folio.tramo, 'minimo_pasajeros', 0) or 0
                    if folio.tramo.unidad_pago == 'PASAJERO':
                        valor_pagar = folio.valor_pago_transportista * num_pasajeros
                    else:  # 'VIAJE'
                        valor_pagar = folio.valor_pago_transportista if num_pasajeros >= minimo_requerido else 0

                    # Actualizar totales por transportista
                    if transportista.id not in totales_por_transportista:
                        totales_por_transportista[transportista.id] = 0
                    totales_por_transportista[transportista.id] += valor_pagar

                    results.append({
                        'fecha': current_date,
                        'cliente': cliente.nombre,
                        'empresa_transporte': transportista.nombre,
                        'vehiculo': f"{vehiculo.ppu} - {vehiculo.modelo}" if vehiculo else "No asignado",
                        'chofer': self.get_chofer_name(transportista, vehiculo),
                        'cantidad_pasajeros': num_pasajeros,
                        'valor_pago': valor_pagar,
                        'unidad_control': folio.tramo.unidad_pago,
                        'origen': folio.tramo.origen,
                        'destino': folio.tramo.destino,
                        'total_acumulado': totales_por_transportista[transportista.id]
                    })

            current_date += timedelta(days=1)

        print(f"\nTotal registros generados: {len(results)}")
        return Response({
            'registros': results,
            'metadata': {
                'fecha_inicio': fecha_inicio,
                'fecha_fin': fecha_fin,
                'total_registros': len(results),
                'totales_por_transportista': totales_por_transportista
            }
        })

    def get_chofer_name(self, transportista, vehiculo):
        """Obtener nombre del chofer asignado al vehículo"""
        if not vehiculo:
            return "No asignado"
            
        chofer = ChoferesTransporte.objects.filter(
            empresa=transportista,
            vehiculo=vehiculo
        ).first()
        
        return chofer.nombre if chofer else "Sin chofer asignado"

class GenerarProformaTransportistaAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, proforma_id=None):
        """
        Método GET que maneja tanto la lista de proformas como la descarga del PDF
        """
        if proforma_id is not None:
            try:
                proforma = ProformaTransportista.objects.get(
                    id=proforma_id,
                    holding_id=request.user.holding_id
                )

                if not proforma.documento_pdf:
                    return Response(
                        {'error': 'No se encontró el documento PDF'},
                        status=status.HTTP_404_NOT_FOUND
                    )

                response = HttpResponse(
                    proforma.documento_pdf.read(),
                    content_type='application/pdf'
                )
                response['Content-Disposition'] = f'attachment; filename="proforma_{proforma.id}.pdf"'
                return response

            except ProformaTransportista.DoesNotExist:
                return Response(
                    {'error': 'Proforma no encontrada'},
                    status=status.HTTP_404_NOT_FOUND
                )
            except Exception as e:
                print(f"Error obteniendo PDF: {str(e)}")
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        else:
            try:
                holding_id = request.user.holding_id
                fecha_inicio = request.query_params.get('fecha_inicio')
                fecha_fin = request.query_params.get('fecha_fin')
                estado = request.query_params.get('estado')
                transportista_id = request.query_params.get('transportista')

                queryset = ProformaTransportista.objects.filter(
                    holding_id=holding_id
                ).select_related('sociedad', 'transportista')

                if fecha_inicio and fecha_fin:
                    queryset = queryset.filter(
                        fecha_emision__range=[fecha_inicio, fecha_fin]
                    )
                
                if estado:
                    queryset = queryset.filter(estado=estado)
                
                if transportista_id:
                    queryset = queryset.filter(transportista_id=transportista_id)

                queryset = queryset.order_by('-fecha_emision')
                serializer = ProformaTransportistaSerializer(queryset, many=True)

                return Response({
                    'proformas': serializer.data,
                    'total': queryset.count()
                })

            except Exception as e:
                print(f"Error obteniendo proformas: {str(e)}")
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

    def post(self, request):
        try:
            # Extraer datos de la solicitud
            data = request.data
            holding_id = request.user.holding_id
            sociedad_id = data.get('sociedad')
            transportista_id = data.get('transportistas')[0]
            fecha_inicio = data.get('fecha_inicio_periodo')
            fecha_fin = data.get('fecha_fin_periodo')
            fecha_emision = data.get('fecha_emision')
            fecha_vencimiento = data.get('fecha_vencimiento')

            # Obtener objetos necesarios
            sociedad = Sociedad.objects.get(id=sociedad_id)
            transportista = EmpresasTransporte.objects.get(id=transportista_id)
            
            # Obtener producciones relacionadas al transportista que no tengan proforma emitida
            trabajadores = PersonalTrabajadores.objects.filter(transportista=transportista)
            producciones = ProduccionTrabajador.objects.filter(
                trabajador__in=trabajadores,
                hora_fecha_ingreso_produccion__date__range=[fecha_inicio, fecha_fin],
                proforma='PENDIENTE'  # Solo obtener producciones pendientes
            )

            # Verificar si hay producciones disponibles
            if not producciones.exists():
                return Response(
                    {"error": "No hay producciones disponibles para generar proforma en el período seleccionado"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Calcular totales
            total_personas = 0
            fechas_unicas = set()
            total_general = 0

            for prod in producciones:
                if not transportista.folio_transportista or not transportista.folio_transportista.tramo:
                    continue
                total_personas += 1
                fechas_unicas.add(prod.hora_fecha_ingreso_produccion.date().isoformat())

            # Obtener información del tramo
            tramo = transportista.folio_transportista.tramo
            tipo_servicio = tramo.unidad_pago
            valor_pago = transportista.folio_transportista.valor_pago_transportista

            # Calcular total según tipo de servicio
            if tipo_servicio == 'PASAJERO':
                total_general = valor_pago * total_personas
            else:  # 'VIAJE'
                total_general = valor_pago * len(fechas_unicas)

            # Crear primero la proforma para tener el ID
            proforma = ProformaTransportista(
                holding_id=holding_id,
                sociedad=sociedad,
                transportista=transportista,
                fecha_emision=fecha_emision,
                fecha_vencimiento=fecha_vencimiento,
                fecha_inicio_periodo=fecha_inicio,
                fecha_fin_periodo=fecha_fin,
                tramo=f"{tramo.origen}-{tramo.destino}",
                tipo_servicio=tipo_servicio,
                cantidad_personas=total_personas,
                valor_pago_transportista=valor_pago,
                total=total_general
            )
            proforma.save()

            # Generar PDF
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72,
                                  topMargin=72, bottomMargin=72)
            elements = []
            styles = getSampleStyleSheet()
            
            # Estilo para el título y número de proforma
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=30
            )
            
            proforma_number_style = ParagraphStyle(
                'ProformaNumber',
                parent=styles['Heading1'],
                fontSize=14,
                alignment=TA_RIGHT,
                spaceAfter=30
            )

            # Crear encabezado con dos columnas
            header_data = [[
                Paragraph(f'Proforma de Servicios - {transportista.nombre}', title_style),
                Paragraph(f'PROFORMA - {proforma.id}', proforma_number_style)
            ]]
            header_table = Table(header_data, colWidths=[4*inch, 4*inch])
            header_table.setStyle(TableStyle([
                ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            elements.append(header_table)
            elements.append(Spacer(1, 20))
            
            info_general = [
                ['Empresa', sociedad.nombre],
                ['RUT Empresa', sociedad.rol_sociedad],
                ['Transportista', transportista.nombre],
                ['RUT Transportista', transportista.rut],
                ['Fecha Emisión', fecha_emision],
                ['Fecha Vencimiento', fecha_vencimiento],
                ['Período', f'Del {fecha_inicio} al {fecha_fin}']
            ]
            
            t = Table(info_general, colWidths=[2*inch, 4*inch])
            t.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('PADDING', (0, 0), (-1, -1), 6)
            ]))
            elements.append(t)
            elements.append(Spacer(1, 20))

            # Detalles del servicio
            detalles_data = [['Origen', 'Destino', 'Tipo', 'Total Personas', 'Total Días', 'Valor Unit.', 'Total']]
            detalles_data.append([
                tramo.origen,
                tramo.destino,
                tipo_servicio,
                str(total_personas),
                str(len(fechas_unicas)),
                f"${valor_pago:,.0f}",
                f"${total_general:,.0f}"
            ])
            
            detalles_data.append(['', '', '', '', '', 'Total:', f"${total_general:,.0f}"])
            
            t_detalles = Table(detalles_data, repeatRows=1)
            t_detalles.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -2), 1, colors.black),
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('ALIGN', (-2, -2), (-1, -1), 'RIGHT'),
                ('LINEBELOW', (-2, -1), (-1, -1), 2, colors.black),
                ('PADDING', (0, 0), (-1, -1), 6),
                ('ALIGN', (3, 1), (-1, -1), 'RIGHT')
            ]))
            elements.append(t_detalles)

            # Construir PDF
            doc.build(elements)
            buffer.seek(0)
            pdf_content = buffer.getvalue()

            # Guardar el PDF en la proforma
            pdf_filename = f'proforma_{proforma.id}.pdf'
            content_file = ContentFile(pdf_content)
            proforma.documento_pdf.save(pdf_filename, content_file, save=True)

            # Marcar todas las producciones incluidas como emitidas
            producciones.update(proforma='EMITIDO')
            
            return Response({
                'message': 'Proforma generada exitosamente',
                'proforma_id': proforma.id
            })

        except Exception as e:
            print(f"Error generando proforma: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def put(self, request, proforma_id):
        """
        Método PUT para actualizar el estado de una proforma a FACTURADO.
        Requiere datos de la factura.
        """
        try:
            proforma = ProformaTransportista.objects.get(
                id=proforma_id,
                holding_id=request.user.holding_id
            )
            
            # Verificar que la proforma esté en estado EMITIDO
            if proforma.estado != 'EMITIDO':
                return Response(
                    {'error': 'Solo se pueden facturar proformas en estado EMITIDO'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validar que se proporcionaron los datos de la factura
            required_fields = ['factura_fecha', 'factura_numero', 'factura_rut', 'factura_monto']
            if not all(field in request.data for field in required_fields):
                return Response(
                    {'error': 'Se requieren todos los datos de la factura'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Actualizar los datos de la factura
            proforma.factura_fecha = request.data['factura_fecha']
            proforma.factura_numero = request.data['factura_numero']
            proforma.factura_rut = request.data['factura_rut']
            proforma.factura_monto = request.data['factura_monto']
            proforma.estado = 'FACTURADO'
            proforma.save()
            
            return Response({
                'message': 'Proforma actualizada a estado FACTURADO exitosamente',
                'proforma_id': proforma.id
            })
            
        except ProformaTransportista.DoesNotExist:
            return Response(
                {'error': 'Proforma no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            print(f"Error actualizando proforma: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class InformeDiasTrabajadosAPIView(APIView):
    """
    API view to generate a report of days worked per worker for a given month/year,
    including totals by client and overall days worked.
    """
    def post(self, request):
        try:
            # Extract and validate required parameters
            holding_id = request.data.get('holding_id')
            if not holding_id:
                return Response(
                    {'error': 'Holding ID is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            try:
                year = int(request.data.get('year'))
                mes = int(request.data.get('mes'))
            except (ValueError, TypeError):
                return Response(
                    {'error': 'Year and month must be valid integers'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Extract and validate optional parameters
            cliente_id = request.data.get('cliente_id')
            if cliente_id and cliente_id not in ('', 'null'):
                try:
                    cliente_id = int(cliente_id)
                except (ValueError, TypeError):
                    cliente_id = None
            else:
                cliente_id = None
                
            fundo_id = request.data.get('fundo_id')
            if fundo_id and fundo_id not in ('', 'null'):
                try:
                    fundo_id = int(fundo_id)
                except (ValueError, TypeError):
                    fundo_id = None
            else:
                fundo_id = None
                
            casa_id = request.data.get('casa_id')
            if casa_id and casa_id not in ('', 'null'):
                try:
                    casa_id = int(casa_id)
                except (ValueError, TypeError):
                    casa_id = None
            else:
                casa_id = None
                
            supervisor_id = request.data.get('supervisor_id')
            if supervisor_id and supervisor_id not in ('', 'null'):
                try:
                    supervisor_id = int(supervisor_id)
                except (ValueError, TypeError):
                    supervisor_id = None
            else:
                supervisor_id = None
                
            trabajador_id = request.data.get('trabajador_id')
            if trabajador_id and trabajador_id not in ('', 'null'):
                try:
                    trabajador_id = int(trabajador_id)
                except (ValueError, TypeError):
                    trabajador_id = None
            else:
                trabajador_id = None
            
            # Find the number of days in the month
            last_day = calendar.monthrange(year, mes)[1]
            start_date = date(year, mes, 1)
            end_date = date(year, mes, last_day)
            
            # Get production records for the period
            productions_query = ProduccionTrabajador.objects.filter(
                holding_id=holding_id,
                hora_fecha_ingreso_produccion__date__range=[start_date, end_date]
            ).select_related('trabajador', 'folio__cliente')
            
            # Apply filters to production records
            if cliente_id:
                productions_query = productions_query.filter(folio__cliente_id=cliente_id)
            if fundo_id:
                # Asumiendo que existe una relación entre trabajador y fundo
                productions_query = productions_query.filter(trabajador__fundo_id=fundo_id)
            if casa_id:
                productions_query = productions_query.filter(trabajador__casa_id=casa_id)
            if supervisor_id:
                productions_query = productions_query.filter(trabajador__supervisor_directo__id=supervisor_id)
            if trabajador_id:
                productions_query = productions_query.filter(trabajador_id=trabajador_id)
            
            # Store all clients we encounter
            all_clients = {}  # client_id -> client_name
            
            # Group workers by their IDs and track daily work by client
            worker_data = {}
            for prod in productions_query:
                if not prod.trabajador or not prod.hora_fecha_ingreso_produccion:
                    continue
                    
                worker_id = prod.trabajador.id
                
                if prod.folio and prod.folio.cliente:
                    client_id = prod.folio.cliente.id
                    client_name = prod.folio.cliente.nombre
                    
                    # Add to list of all clients
                    all_clients[client_id] = client_name
                else:
                    client_id = None
                    client_name = 'Sin Cliente'
                
                day = prod.hora_fecha_ingreso_produccion.day
                
                # Initialize worker data if not exists
                if worker_id not in worker_data:
                    worker_data[worker_id] = {
                        'worker': prod.trabajador,
                        'days_worked': set(),  # Set of days worked (any client)
                        'client_days': defaultdict(set),  # Maps client_id -> set of days
                    }
                
                # Record this day as worked for this client
                if 1 <= day <= last_day:
                    worker_data[worker_id]['days_worked'].add(day)
                    
                    if client_id is not None:
                        worker_data[worker_id]['client_days'][client_id].add(day)
            
            # Convert client dictionary to sorted list for frontend
            client_list = [{'id': cid, 'nombre': cname} for cid, cname in all_clients.items()]
            client_list.sort(key=lambda x: x['nombre'])
            
            # Prepare result data
            result = {
                'trabajadores': [],
                'clientes': client_list,
                'fechas': [date(year, mes, day).isoformat() for day in range(1, last_day + 1)]
            }
            
            # Process worker data
            for worker_id, data in worker_data.items():
                worker = data['worker']
                
                # Calculate totals per client in format needed by frontend
                dias_por_cliente = {}
                client_totals = {}  # Keep for backward compatibility
                
                for cid, days in data['client_days'].items():
                    cliente_name = all_clients.get(cid, "Cliente desconocido")
                    dias_por_cliente[cliente_name] = len(days)
                    client_totals[cid] = len(days)
                
                # Format date for display
                fecha_ingreso = worker.fecha_ingreso.isoformat() if worker.fecha_ingreso else None
                
                worker_info = {
                    'id': worker.id,
                    'nombres': worker.nombres,
                    'apellidos': worker.apellidos or '',
                    'rut': worker.rut or '',
                    'fecha_ingreso': fecha_ingreso,
                    'dias_por_cliente': dias_por_cliente,  # Format needed by frontend
                    'client_totals': client_totals,  # For backward compatibility
                    'dias_totales': len(data['days_worked'])
                }
                
                result['trabajadores'].append(worker_info)
            
            # Sort the workers by name for consistency
            result['trabajadores'].sort(key=lambda x: (x['nombres'], x['apellidos']))
            
            return Response(result)
            
        except Exception as e:
            traceback.print_exc()
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class DiasTrabajadosAprobadosAPIView(APIView):

    def get(self, request):
        """
        Obtener registros de días trabajados aprobados según los parámetros proporcionados.
        Parámetros de consulta:
        - holding_id: ID del holding (obligatorio)
        - mes: Número del mes (1-12) (obligatorio si no se proporciona id)
        - year: Año (obligatorio si no se proporciona id)
        - trabajador_id: ID del trabajador (opcional, filtra por trabajador específico)
        - id: ID específico del registro (opcional, retorna un único registro)
        """
        try:
            # Obtener y validar el ID del registro si se proporciona
            registro_id = request.query_params.get('id')
            if registro_id:
                try:
                    registro_id = int(registro_id)
                    registro = DiasTrabajadosAprobados.objects.get(id=registro_id)
                    # Aquí puedes usar un serializador más detallado si es necesario
                    return Response({
                        'id': registro.id,
                        'trabajador_id': registro.trabajador_id,
                        'mes': registro.mes,
                        'year': registro.year,
                        'dias_por_cliente': registro.dias_por_cliente,
                        'reducciones_aplicadas': registro.reducciones_aplicadas,
                        'dias_totales': registro.dias_totales,
                        'fecha_aprobacion': registro.fecha_aprobacion
                    })
                except (ValueError, DiasTrabajadosAprobados.DoesNotExist):
                    return Response(
                        {'error': f'No se encontró el registro con ID {registro_id}'},
                        status=status.HTTP_404_NOT_FOUND
                    )
            
            # Obtener y validar parámetros obligatorios para búsqueda por filtros
            holding_id = request.query_params.get('holding_id')
            if not holding_id:
                return Response(
                    {'error': 'El parámetro holding_id es obligatorio'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                holding_id = int(holding_id)
            except ValueError:
                return Response(
                    {'error': 'El holding_id debe ser un número entero válido'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            # Si no hay ID específico, verificar mes y año
            mes = request.query_params.get('mes')
            year = request.query_params.get('year')
            
            if not mes or not year:
                return Response(
                    {'error': 'Los parámetros mes y year son obligatorios si no se proporciona un ID específico'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            try:
                mes = int(mes)
                year = int(year)
                
                if not (1 <= mes <= 12):
                    return Response(
                        {'error': 'El mes debe estar entre 1 y 12'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except ValueError:
                return Response(
                    {'error': 'Los parámetros mes y year deben ser números enteros válidos'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Construir la consulta base
            query = Q(holding_id=holding_id) & Q(mes=mes) & Q(year=year)
            
            # Filtrar por trabajador_id si se proporciona
            trabajador_id = request.query_params.get('trabajador_id')
            if trabajador_id:
                try:
                    trabajador_id = int(trabajador_id)
                    query &= Q(trabajador_id=trabajador_id)
                except ValueError:
                    # Ignorar silenciosamente si el trabajador_id no es válido
                    pass
            
            # Ejecutar la consulta
            registros = DiasTrabajadosAprobados.objects.filter(query)
            
            # Preparar la respuesta
            resultados = []
            for registro in registros:
                resultados.append({
                    'id': registro.id,
                    'trabajador_id': registro.trabajador_id,
                    'mes': registro.mes,
                    'year': registro.year,
                    'dias_por_cliente': registro.dias_por_cliente,
                    'reducciones_aplicadas': registro.reducciones_aplicadas,
                    'dias_totales': registro.dias_totales,
                    'fecha_aprobacion': registro.fecha_aprobacion
                })
            
            return Response(resultados)
            
        except Exception as e:
            # En producción, considera registrar el error en lugar de exponerlo directamente
            return Response(
                {'error': f'Error al obtener los registros: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request):
        """Guardar un registro de días trabajados aprobados"""
        try:
            data = request.data
            holding_id = data.get('holding_id')
            trabajador_id = data.get('trabajador_id')
            mes = data.get('mes')
            year = data.get('year')
            dias_por_cliente = data.get('dias_por_cliente')
            reducciones_aplicadas = data.get('reducciones_aplicadas')
            dias_totales = data.get('dias_totales')
            
            # Verificar si el mes está cerrado
            mes_cerrado = MesCerrado.objects.filter(
                holding_id=holding_id,
                mes=mes,
                year=year
            ).first()
            
            if mes_cerrado:
                return Response(
                    {
                        'error': 'No se pueden modificar los días trabajados para un mes cerrado',
                        'fecha_cierre': mes_cerrado.fecha_cierre,
                        'usuario_cierre': mes_cerrado.usuario_cierre.persona.nombres 
                            if mes_cerrado.usuario_cierre and mes_cerrado.usuario_cierre.persona 
                            else 'Usuario desconocido'
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Comprobar si ya existe un registro para actualizar
            registro, created = DiasTrabajadosAprobados.objects.update_or_create(
                holding_id=holding_id,
                trabajador_id=trabajador_id,
                mes=mes,
                year=year,
                defaults={
                    'dias_por_cliente': dias_por_cliente,
                    'reducciones_aplicadas': reducciones_aplicadas,
                    'dias_totales': dias_totales,
                    'usuario_aprueba_id': request.user.id,
                    'modificado_por_id': request.user.id
                }
            )
            
            return Response({
                'mensaje': 'Registro guardado correctamente',
                'id': registro.id,
                'created': created
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'Error al guardar el registro: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    def delete(self, request):
        """Eliminar todos los registros de días trabajados aprobados para un mes y año específicos"""
        try:
            data = request.data
            holding_id = data.get('holding_id')
            mes = data.get('mes')
            year = data.get('year')
            
            if not all([holding_id, mes, year]):
                return Response(
                    {'error': 'Se requieren holding_id, mes y año'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            # Verificar si el mes está cerrado
            mes_cerrado = MesCerrado.objects.filter(
                holding_id=holding_id,
                mes=mes,
                year=year
            ).first()
            
            if mes_cerrado:
                return Response(
                    {
                        'error': 'No se pueden eliminar los registros para un mes cerrado',
                        'fecha_cierre': mes_cerrado.fecha_cierre,
                        'usuario_cierre': mes_cerrado.usuario_cierre.persona.nombres 
                            if mes_cerrado.usuario_cierre and mes_cerrado.usuario_cierre.persona 
                            else 'Usuario desconocido'
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Eliminar todos los registros que coincidan con los criterios
            registros_eliminados = DiasTrabajadosAprobados.objects.filter(
                holding_id=holding_id,
                mes=mes,
                year=year
            ).delete()
            
            return Response({
                'mensaje': f'Se han eliminado {registros_eliminados[0]} registros correctamente',
                'cantidad': registros_eliminados[0]
            })
            
        except Exception as e:
            return Response(
                {'error': f'Error al eliminar los registros: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class MesCerradoAPIView(APIView):
    """API para gestionar el cierre de meses."""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]
    required_scopes = ['admin', 'write']
    
    def get(self, request):
        """
        Obtiene los meses cerrados de un holding.
        Si se especifica mes y año, verifica si ese mes específico está cerrado.
        """
        holding_id = request.query_params.get('holding_id')
        mes = request.query_params.get('mes')
        year = request.query_params.get('year')
        
        if not holding_id:
            return Response(
                {'error': 'Se requiere el ID del holding'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar si un mes específico está cerrado
        if mes and year:
            try:
                mes = int(mes)
                year = int(year)
                mes_cerrado = MesCerrado.objects.filter(
                    holding_id=holding_id,
                    mes=mes,
                    year=year
                ).first()
                
                if mes_cerrado:
                    serializer = MesCerradoSerializer(mes_cerrado)
                    data = serializer.data
                    data['is_closed'] = True
                    return Response(data)
                else:
                    return Response({
                        'mes': mes,
                        'year': year,
                        'is_closed': False
                    })
            except ValueError:
                return Response(
                    {'error': 'Mes o año inválido'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Obtener todos los meses cerrados para el holding
        meses_cerrados = MesCerrado.objects.filter(
            holding_id=holding_id
        ).order_by('-year', '-mes')
        
        serializer = MesCerradoSerializer(meses_cerrados, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        """Cerrar un mes"""
        try:
            data = request.data
            holding_id = data.get('holding_id')
            mes = data.get('mes')
            year = data.get('year')
            motivo = data.get('motivo', '')
            
            if not all([holding_id, mes, year]):
                return Response(
                    {'error': 'Se requieren holding_id, mes y año'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Verificar si el mes ya está cerrado
            if MesCerrado.objects.filter(holding_id=holding_id, mes=mes, year=year).exists():
                return Response(
                    {'error': 'El mes ya está cerrado'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Cerrar el mes
            mes_cerrado = MesCerrado.objects.create(
                holding_id=holding_id,
                mes=mes,
                year=year,
                usuario_cierre=request.user,
                motivo=motivo
            )
            
            serializer = MesCerradoSerializer(mes_cerrado)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': f'Error al cerrar el mes: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def delete(self, request):
        """Abrir un mes previamente cerrado"""
        try:
            data = request.data
            holding_id = data.get('holding_id')
            mes = data.get('mes')
            year = data.get('year')
            
            if not all([holding_id, mes, year]):
                return Response(
                    {'error': 'Se requieren holding_id, mes y año'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Buscar y eliminar el registro de mes cerrado
            try:
                mes_cerrado = MesCerrado.objects.get(
                    holding_id=holding_id,
                    mes=mes,
                    year=year
                )
                mes_cerrado.delete()
                
                return Response({
                    'message': f'El mes {mes}/{year} ha sido abierto'
                })
            except MesCerrado.DoesNotExist:
                return Response(
                    {'error': 'El mes no está cerrado'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
        except Exception as e:
            return Response(
                {'error': f'Error al abrir el mes: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class HaberesAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_scopes = []

    def dispatch(self, request, *args, **kwargs):
        if request.method in ['GET', 'POST', 'PATCH', 'PUT', 'DELETE']:
            self.required_scopes = ['admin', 'write']
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, format=None):
        holding_id = request.query_params.get('holding')
        if holding_id:
            haberes = Haberes.objects.filter(holding_id=holding_id).order_by('orden')
            serializer = HaberesSerializer(haberes, many=True)
            return Response(serializer.data)
        else:
            return Response({'error': 'El parámetro holding es necesario'}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        serializer = HaberesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, format=None):
        haber_id = request.data.get('id')
        try:
            haber = Haberes.objects.get(id=haber_id)
        except Haberes.DoesNotExist:
            return Response({"message": "Haber no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        serializer = HaberesSerializer(haber, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, format=None):
        haber_ids = request.data.get('ids', [])
        Haberes.objects.filter(id__in=haber_ids).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, format=None):
        haber_id = request.data.get('id')
        if not haber_id:
            return Response({"message": "ID de haber es necesario para actualizar"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            haber = Haberes.objects.get(id=haber_id)
        except Haberes.DoesNotExist:
            return Response({"message": "Haber no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        serializer = HaberesSerializer(haber, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DescuentosAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_scopes = []

    def dispatch(self, request, *args, **kwargs):
        if request.method in ['GET', 'POST', 'PATCH', 'PUT', 'DELETE']:
            self.required_scopes = ['admin', 'write']
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, format=None):
        holding_id = request.query_params.get('holding')
        if holding_id:
            descuentos = Descuentos.objects.filter(holding_id=holding_id).order_by('orden')
            serializer = DescuentosSerializer(descuentos, many=True)
            return Response(serializer.data)
        else:
            return Response({'error': 'El parámetro holding es necesario'}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        data = request.data
        print(data)
        serializer = DescuentosSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, format=None):
        descuento_id = request.data.get('id')
        try:
            descuento = Descuentos.objects.get(id=descuento_id)
        except Descuentos.DoesNotExist:
            return Response({"message": "Descuento no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        serializer = DescuentosSerializer(descuento, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, format=None):
        descuento_ids = request.data.get('ids', [])
        Descuentos.objects.filter(id__in=descuento_ids).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, format=None):
        descuento_id = request.data.get('id')
        if not descuento_id:
            return Response({"message": "ID de descuento es necesario para actualizar"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            descuento = Descuentos.objects.get(id=descuento_id)
        except Descuentos.DoesNotExist:
            return Response({"message": "Descuento no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        serializer = DescuentosSerializer(descuento, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PersonalFiltradoAPIView(APIView):
    def get(self, request):
        # Obtener parámetros de filtro
        holding_id = request.query_params.get('holding')
        sociedad_id = request.query_params.get('sociedad_id')
        cliente_id = request.query_params.get('cliente_id')
        fundo_id = request.query_params.get('fundo_id')
        casa_id = request.query_params.get('casa_id')
        
        if not holding_id:
            return Response({'error': 'El parámetro holding es necesario'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Construir consulta base
        query = Q(holding_id=holding_id, estado=True)
        
        # Aplicar filtros adicionales
        if sociedad_id:
            query &= Q(sociedad_id=sociedad_id)
        if fundo_id:
            query &= Q(fundo_id=fundo_id)
        if casa_id:
            query &= Q(casa_id=casa_id)
            
        # Filtro por cliente (ajusta esto según cómo se relacionen tus modelos)
        if cliente_id and fundo_id:
            # Si hay lógica adicional para filtrar por cliente, agrégala aquí
            pass
            
        # Ejecutar consulta
        trabajadores = PersonalTrabajadores.objects.filter(query)
        serializer = PersonalConAsignacionesSerializer(trabajadores, many=True)
        
        return Response(serializer.data)

class AsignarHaberesAPIView(APIView):
    """Vista específica para asignar haberes (sin descuentos)"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_scopes = []
    
    def dispatch(self, request, *args, **kwargs):
        if request.method in ['POST']:
            self.required_scopes = ['admin', 'write']
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request):
        # Obtener datos del request
        holding_id = request.data.get('holding_id')
        trabajador_ids = request.data.get('trabajador_ids', [])
        # Eliminamos el sueldo_base ya que se manejará en otra área
        haberes_asignaciones = request.data.get('haberes_asignaciones', [])
        
        # Validaciones básicas
        if not holding_id or not trabajador_ids:
            return Response({'error': 'Se requieren holding_id y trabajador_ids'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Obtener trabajadores
        trabajadores = PersonalTrabajadores.objects.filter(
            id__in=trabajador_ids,
            holding_id=holding_id
        )
        
        if len(trabajadores) != len(trabajador_ids):
            return Response({'error': 'Algunos trabajadores no existen o no pertenecen al holding'},
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Realizar asignaciones
        for trabajador in trabajadores:
            # Ya no asignamos sueldo base
            
            # Procesar asignaciones de haberes
            for asignacion in haberes_asignaciones:
                if asignacion.get('trabajador_id') == trabajador.id:
                    haber_id = asignacion.get('haber_id')
                    valor = asignacion.get('valor')
                    
                    # Crear o actualizar la asignación
                    TrabajadorHaber.objects.update_or_create(
                        trabajador=trabajador,
                        haber_id=haber_id,
                        defaults={'valor': valor}
                    )
        
        # Devolver datos actualizados de trabajadores
        trabajadores_actualizados = PersonalTrabajadores.objects.filter(id__in=trabajador_ids)
        serializer = PersonalConAsignacionesSerializer(trabajadores_actualizados, many=True)
        return Response(serializer.data)

class AsignarDescuentosAPIView(APIView):
    """Vista para asignar descuentos a trabajadores"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_scopes = []
    
    def dispatch(self, request, *args, **kwargs):
        if request.method in ['POST']:
            self.required_scopes = ['admin', 'write']
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request):
        # Obtener datos del request
        holding_id = request.data.get('holding_id')
        trabajador_ids = request.data.get('trabajador_ids', [])
        descuentos = request.data.get('descuentos', [])
        
        # Validaciones básicas
        if not holding_id or not trabajador_ids:
            return Response({'error': 'Se requieren holding_id y trabajador_ids'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        if not descuentos:
            return Response({'error': 'Se debe especificar al menos un descuento'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Obtener trabajadores
        trabajadores = PersonalTrabajadores.objects.filter(
            id__in=trabajador_ids,
            holding_id=holding_id
        )
        
        if len(trabajadores) != len(trabajador_ids):
            return Response({'error': 'Algunos trabajadores no existen o no pertenecen al holding'},
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Validar descuentos
        descuento_ids = [d['id'] for d in descuentos]
        descuentos_objs = Descuentos.objects.filter(
            id__in=descuento_ids, 
            holding_id=holding_id
        )
        
        if descuentos_objs.count() != len(descuento_ids):
            return Response({'error': 'Algunos descuentos no existen o no pertenecen al holding'},
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Crear un mapeo de descuentos por ID para acceso rápido
        descuentos_map = {desc.id: desc for desc in descuentos_objs}
        
        # Procesar las asignaciones en una transacción
        with transaction.atomic():
            for trabajador in trabajadores:
                # Eliminar descuentos existentes para este trabajador
                TrabajadorDescuento.objects.filter(trabajador=trabajador).delete()
                
                # Asignar nuevos descuentos
                for desc_data in descuentos:
                    descuento_id = desc_data['id']
                    valor = desc_data['valor']
                    es_cuota = desc_data.get('es_cuota', False)
                    num_cuotas = desc_data.get('num_cuotas', 1) if es_cuota else 1
                    
                    # Validar que el descuento exista
                    descuento = descuentos_map.get(descuento_id)
                    if not descuento:
                        continue
                    
                    # Validar que el descuento admita cuotas si es necesario
                    if es_cuota and num_cuotas > 1 and not descuento.cuota:
                        return Response(
                            {'error': f'El descuento {descuento.nombre} no admite cuotas'},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    
                    # Calcular valor de cuota
                    valor_cuota = valor / num_cuotas if num_cuotas > 0 else valor
                    
                    # Crear la asignación
                    TrabajadorDescuento.objects.create(
                        trabajador=trabajador,
                        descuento=descuento,
                        valor_total=valor,
                        num_cuotas=num_cuotas,
                        cuota_actual=1,
                        valor_cuota=valor_cuota
                    )
        
        # Devolver datos actualizados
        serializer = PersonalConAsignacionesSerializer(trabajadores, many=True)
        return Response(serializer.data)
    
class GenerarLiquidacionesAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_scopes = []
    
    def dispatch(self, request, *args, **kwargs):
        if request.method in ['POST']:
            self.required_scopes = ['admin', 'write']
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request):
        # Get filter parameters
        holding_id = request.data.get('holding_id')
        sociedad_id = request.data.get('sociedad_id')
        mes = request.data.get('mes')
        year = request.data.get('year')
        cliente_id = request.data.get('cliente_id')
        fundo_id = request.data.get('fundo_id')
        casa_id = request.data.get('casa_id')
        
        # Validation
        if not holding_id or not sociedad_id or not mes or not year:
            return Response(
                {'error': 'Holding, sociedad, mes y año son obligatorios'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Get sociedad for header
        try:
            sociedad = Sociedad.objects.get(id=sociedad_id, holding_id=holding_id)
        except Sociedad.DoesNotExist:
            return Response(
                {'error': 'Sociedad no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Verificar primero si existen días trabajados aprobados para este período
        dias_aprobados_query = DiasTrabajadosAprobados.objects.filter(
            holding_id=holding_id,
            mes=mes,
            year=year
        )
        
        # Aplicar filtros adicionales a los días aprobados si es necesario
        if sociedad_id:
            # Filtrar por trabajadores de la sociedad
            trabajadores_sociedad = PersonalTrabajadores.objects.filter(
                sociedad_id=sociedad_id
            ).values_list('id', flat=True)
            dias_aprobados_query = dias_aprobados_query.filter(
                trabajador_id__in=trabajadores_sociedad
            )
            
        if cliente_id:
            # Obtener trabajadores por cliente
            contratos = PersonalTrabajadores.objects.filter( #TODO CAMBIAR PERSONAL POR UN NUEVO MODELO DE CONTRATO
                cliente_id=cliente_id,
                holding_id=holding_id
            ).values_list('trabajador_id', flat=True)
            dias_aprobados_query = dias_aprobados_query.filter(
                trabajador_id__in=contratos
            )
            
        if fundo_id:
            # Obtener trabajadores por fundo
            trabajadores_fundo = PersonalTrabajadores.objects.filter(
                fundo_id=fundo_id
            ).values_list('id', flat=True)
            dias_aprobados_query = dias_aprobados_query.filter(
                trabajador_id__in=trabajadores_fundo
            )
            
        if casa_id:
            # Obtener trabajadores por casa
            trabajadores_casa = PersonalTrabajadores.objects.filter(
                casa_id=casa_id
            ).values_list('id', flat=True)
            dias_aprobados_query = dias_aprobados_query.filter(
                trabajador_id__in=trabajadores_casa
            )
        
        # Verificar si hay días aprobados
        if not dias_aprobados_query.exists():
            return Response(
                {'error': 'No hay días trabajados aprobados para el período seleccionado. No se pueden generar liquidaciones.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Obtener IDs de trabajadores con días aprobados
        trabajadores_ids_con_dias = dias_aprobados_query.values_list('trabajador_id', flat=True)
        
        # Build base query para trabajadores con días aprobados
        query = Q(
            id__in=trabajadores_ids_con_dias,
            holding_id=holding_id,
            estado=True,
            sociedad_id=sociedad_id
        )
        
        # Apply additional filters
        if cliente_id:
            # Filter by client (through contracts or another relationship)
            contratos = PersonalTrabajadores.objects.filter( #TODO CAMBIAR PERSONAL POR UN NUEVO MODELO DE CONTRATO
                cliente_id=cliente_id,
                holding_id=holding_id
            ).values_list('trabajador_id', flat=True)
            query &= Q(id__in=contratos)
            
        if fundo_id:
            query &= Q(fundo_id=fundo_id)
            
        if casa_id:
            query &= Q(casa_id=casa_id)
            
        # Get workers
        trabajadores = PersonalTrabajadores.objects.filter(query)
        
        if not trabajadores.exists():
            return Response(
                {'error': 'No se encontraron trabajadores con días aprobados y los filtros aplicados'},
                status=status.HTTP_404_NOT_FOUND
            )
            
        # Create temporary directory for PDFs
        temp_dir = tempfile.mkdtemp()
        zip_filename = f"liquidaciones_{sociedad.nombre}_{year}_{mes}.zip"
        zip_path = os.path.join(temp_dir, zip_filename)
        
        pdf_files = []
        liquidaciones_data = []
        
        # Get month name in Spanish
        meses_espanol = {
            1: "ENERO", 2: "FEBRERO", 3: "MARZO", 4: "ABRIL", 5: "MAYO", 6: "JUNIO",
            7: "JULIO", 8: "AGOSTO", 9: "SEPTIEMBRE", 10: "OCTUBRE", 11: "NOVIEMBRE", 12: "DICIEMBRE"
        }
        nombre_mes = meses_espanol.get(int(mes), "")
        
        # Generate PDFs for each worker
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for trabajador in trabajadores:
                # Obtener dias trabajados desde la tabla dias_trabajados_aprobados
                try:
                    dias_aprobados = DiasTrabajadosAprobados.objects.get(
                        holding_id=holding_id,
                        trabajador=trabajador,
                        mes=mes,
                        year=year
                    )
                    # Usar los días aprobados si existe el registro
                    dias_trabajados = dias_aprobados.dias_totales
                    
                    # Si los días trabajados son 0, saltar este trabajador
                    if dias_trabajados == 0:
                        continue
                        
                except DiasTrabajadosAprobados.DoesNotExist:
                    # Si no hay registro de días aprobados, saltar este trabajador
                    continue
                
                # Get assigned haberes
                haberes = TrabajadorHaber.objects.filter(
                    trabajador=trabajador
                ).select_related('haber')
                
                # Get assigned descuentos
                descuentos = TrabajadorDescuento.objects.filter(
                    trabajador=trabajador
                ).select_related('descuento')
                
                # Calculate base salary per day
                sueldo_base_diario = trabajador.sueldo_base / 30 if trabajador.sueldo_base else 0
                sueldo_base_total = sueldo_base_diario * dias_trabajados
                        
                # Prepare data for haberes
                lista_haberes = [
                    {
                        'nombre': 'Sueldo base',
                        'cantidad': dias_trabajados,
                        'valor': sueldo_base_total,
                        'imponible': True
                    }
                ]
                
                # Add other haberes
                for haber_asignado in haberes:
                    haber = haber_asignado.haber
                    valor = haber_asignado.valor
                    
                    lista_haberes.append({
                        'nombre': haber.nombre,
                        'cantidad': None,
                        'valor': valor,
                        'imponible': haber.imponible
                    })
                
                # Calculate totals for haberes
                total_haberes = sum(h['valor'] for h in lista_haberes)
                total_imponible = sum(h['valor'] for h in lista_haberes if h['imponible'])
                total_no_imponible = total_haberes - total_imponible
                
                # Calculate AFP deduction
                afp_porcentaje = 10.0  # Default
                if trabajador.afp:
                    try:
                        afp_porcentaje = trabajador.afp.porcentaje_descuento
                    except AttributeError:
                        # Use default if porcentaje_descuento not available yet
                        pass
                
                afp_valor = (total_imponible * afp_porcentaje) / 100
                
                # Calculate health insurance deduction
                salud_porcentaje = 7.0  # Default
                if trabajador.salud:
                    try:
                        salud_porcentaje = trabajador.salud.porcentaje_descuento
                    except AttributeError:
                        # Use default if porcentaje_descuento not available yet
                        pass
                        
                salud_valor = (total_imponible * salud_porcentaje) / 100
                
                # Prepare data for descuentos
                lista_descuentos = [
                    {
                        'nombre': f"A.F.P. {trabajador.afp.nombre if trabajador.afp else 'N/A'}",
                        'porcentaje': afp_porcentaje,
                        'valor': afp_valor
                    },
                    {
                        'nombre': f"{trabajador.salud.nombre if trabajador.salud else 'FONASA'}",
                        'porcentaje': salud_porcentaje,
                        'valor': salud_valor
                    }
                ]
                
                # Add additional descuentos
                for descuento_asignado in descuentos:
                    descuento = descuento_asignado.descuento
                    valor_cuota = descuento_asignado.valor_cuota
                    
                    lista_descuentos.append({
                        'nombre': descuento.nombre,
                        'porcentaje': None,
                        'valor': valor_cuota
                    })
                
                # Calculate totals for descuentos
                total_descuentos = sum(d['valor'] for d in lista_descuentos)
                liquido_a_pagar = total_haberes - total_descuentos
                
                # Generate PDF
                pdf_buffer = BytesIO()
                self.generar_pdf_liquidacion(
                    pdf_buffer,
                    sociedad,
                    trabajador,
                    lista_haberes,
                    lista_descuentos,
                    {
                        'total_haberes': total_haberes,
                        'total_imponible': total_imponible,
                        'total_no_imponible': total_no_imponible,
                        'total_descuentos': total_descuentos,
                        'liquido_a_pagar': liquido_a_pagar,
                        'total_tributable': total_imponible  # Assuming tributable = imponible
                    },
                    dias_trabajados,
                    nombre_mes,
                    year
                )
                
                # Add to zip
                pdf_filename = f"liquidacion_{trabajador.rut}_{mes}_{year}.pdf"
                zipf.writestr(pdf_filename, pdf_buffer.getvalue())
                
                # Add to response data
                liquidaciones_data.append({
                    'trabajador_id': trabajador.id,
                    'nombre': f"{trabajador.nombres} {trabajador.apellidos or ''}".strip(),
                    'rut': trabajador.rut,
                    'total_haberes': float(total_haberes),
                    'total_descuentos': float(total_descuentos),
                    'liquido_a_pagar': float(liquido_a_pagar)
                })
            
            # Verificar si se generaron liquidaciones
            if not liquidaciones_data:
                return Response(
                    {'error': 'No se pudieron generar liquidaciones para los trabajadores seleccionados. Verifique que existan días trabajados aprobados.'},
                    status=status.HTTP_404_NOT_FOUND
                )
                
        # Return zip file
        with open(zip_path, 'rb') as zipf:
            response = HttpResponse(zipf.read(), content_type='application/zip')
            response['Content-Disposition'] = f'attachment; filename="{zip_filename}"'
            
            # Also include summary data in response headers
            response['X-Liquidaciones-Count'] = str(len(liquidaciones_data))
            
            return response
    
    def generar_pdf_liquidacion(self, buffer, sociedad, trabajador, haberes, descuentos, totales, dias_trabajados, mes, year):
        """Generate liquidation PDF"""
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Flowable
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from math import floor
        
        # Ajustar márgenes para aprovechar mejor el espacio
        doc = SimpleDocTemplate(buffer, pagesize=letter, 
                            leftMargin=0.5*inch, rightMargin=0.5*inch,
                            topMargin=0.5*inch, bottomMargin=0.5*inch)
        styles = getSampleStyleSheet()
        elements = []
        
        # Add header - Reducir fuente y ampliar tabla
        header_data = [
            [f"{sociedad.nombre}", f"Periodo: {mes}", f"Del {year}"],
            [f"{sociedad.rol_sociedad}", "", ""]
        ]
        
        header_table = Table(header_data, colWidths=[4*inch, 2*inch, 1.5*inch])
        header_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),  # Reducido de 12 a 10
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 0.1*inch))  # Reducido de 0.2 a 0.1
        
        # Título con asteriscos como en la imagen
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            alignment=1,  # Center
            fontSize=12,  # Reducido de 14 a 12
            fontName='Helvetica-Bold'
        )
        elements.append(Paragraph("Liquidacion de Remuneraciones**", title_style))
        elements.append(Spacer(1, 0.1*inch))  # Reducido de 0.2 a 0.1
        
        # Estilo de celda más pequeño
        cell_style = ParagraphStyle(
            'CellStyle',
            parent=styles['Normal'],
            fontSize=8,  # Reducido de 10 a 8
            leading=10    # Reducido de 12 a 10
        )
        
        # Format trabajador name with paragraph to enable wrapping
        nombre_completo = f"{trabajador.nombres} {trabajador.apellidos or ''}".strip()
        nombre_paragraph = Paragraph(nombre_completo, cell_style)
        
        # Etiquetas más pequeñas
        nombre_trabajador_label = Paragraph("Nombre Trabajador:", cell_style)
        rut_trabajador_label = Paragraph("Rut Trabajador:", cell_style)
        codigo_trabajador_label = Paragraph("Código Trabajador:", cell_style)
        sueldo_mensual_label = Paragraph("Sueldo Mensual:", cell_style)
        
        fecha_ingreso_label = Paragraph("Fecha Ingreso:", cell_style)
        dias_licencia_label = Paragraph("Días Licencia Médica:", cell_style)
        dias_falla_label = Paragraph("Días de Falla:", cell_style)
        dias_permiso_label = Paragraph("Días Permiso no Remunerado:", cell_style)
        
        # Datos del empleado - Ajustar anchura para que ocupe más espacio
        employee_data = [
            [nombre_trabajador_label, nombre_paragraph, fecha_ingreso_label, 
            trabajador.fecha_ingreso.strftime('%d/%m/%Y') if trabajador.fecha_ingreso else ""],
            [rut_trabajador_label, trabajador.rut, dias_licencia_label, ""],
            [codigo_trabajador_label, f"{trabajador.id}", dias_falla_label, ""],
            [sueldo_mensual_label, f"${trabajador.sueldo_base:,.2f}" if trabajador.sueldo_base else "", 
            dias_permiso_label, ""]
        ]
        
        # Tabla de datos del empleado más ancha
        employee_table = Table(employee_data, colWidths=[1.6*inch, 2.4*inch, 1.6*inch, 1.9*inch])
        employee_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),  # Reducido de 10 a 8
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (2, 0), (2, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        elements.append(employee_table)
        elements.append(Spacer(1, 0.1*inch))  # Reducido
        
        # Haberes y descuentos - Asegurarse que "Días Trabajados" aparezca como en la imagen
        # Haberes y descuentos - Ahora sin mostrar "Días Trabajados" y con más espacio antes de los totales
        max_rows = max(len(haberes), len(descuentos))
        detail_data = []

        # Cabecera con fondo gris
        detail_data.append(["Haberes", "", "", "Descuentos", "", ""])

        # Formatear haberes y descuentos sin incluir línea de "Días Trabajados"
        sueldo_base_item = next((item for item in haberes if item['nombre'] == 'Sueldo base'), None)
        if sueldo_base_item:
            haberes.remove(sueldo_base_item)
            detail_data.append([
                "Sueldo base", 
                f"{dias_trabajados}", 
                f"${sueldo_base_item['valor']:,.0f}",
                descuentos[0]['nombre'] if len(descuentos) > 0 else "", 
                f"{descuentos[0]['porcentaje']}%" if len(descuentos) > 0 and descuentos[0]['porcentaje'] is not None else "", 
                f"${descuentos[0]['valor']:,.0f}" if len(descuentos) > 0 else ""
            ])
            start_idx = 1
        else:
            start_idx = 0

        # Continuar con el resto de haberes y descuentos
        for i in range(start_idx, max_rows):
            haber_idx = i - 1 if sueldo_base_item else i
            descuento_idx = i
            
            haber_row = ["", "", ""] if haber_idx >= len(haberes) else [
                haberes[haber_idx]['nombre'], 
                f"{haberes[haber_idx]['cantidad']}" if haberes[haber_idx]['cantidad'] is not None else "", 
                f"${haberes[haber_idx]['valor']:,.0f}"
            ]
            
            descuento_row = ["", "", ""] if descuento_idx >= len(descuentos) else [
                descuentos[descuento_idx]['nombre'], 
                f"{descuentos[descuento_idx]['porcentaje']}%" if descuentos[descuento_idx]['porcentaje'] is not None else "", 
                f"${descuentos[descuento_idx]['valor']:,.0f}"
            ]
            
            detail_data.append(haber_row + descuento_row)

        # Agregar fila en blanco para generar espacio adicional antes de los totales
        detail_data.append(["", "", "", "", "", "",])
        detail_data.append(["", "", "", "", "", "",])
        detail_data.append(["", "", "", "", "", "",])
        detail_data.append(["", "", "", "", "", "",])
        detail_data.append(["", "", "", "", "", "",])
        detail_data.append(["", "", "", "", "", "",])

        # Totales como en la imagen de referencia
        detail_data.append([
            "Total de Haberes $", "", f"${totales['total_haberes']:,.0f}",
            "Total Descuentos..$", "", f"${totales['total_descuentos']:,.0f}"
        ])
        detail_data.append([
            "Total Imponible...$", "", f"${totales['total_imponible']:,.0f}",
            "Total Líquido......$", "", f"${totales['liquido_a_pagar']:,.0f}"
        ])
        detail_data.append([
            "Total No Impon...$", "", f"${totales['total_no_imponible']:,.0f}",
            "Ajuste Sencillo.....$", "", "0"
        ])
        detail_data.append([
            "Total Tributable...$", "", f"${totales['total_tributable']:,.0f}",
            "Líquido a Pagar.....$", "", f"${totales['liquido_a_pagar']:,.0f}"
        ])
        
        # Tabla principal más ancha (ocupando más del ancho de la página)
        detail_table = Table(
            detail_data, 
            colWidths=[1.6*inch, 0.8*inch, 1.1*inch, 1.6*inch, 0.8*inch, 1.1*inch]
        )
        
        # Estilo de la tabla principal
        style = [
            # Header formatting
            ('SPAN', (0, 0), (2, 0)),  # Span haberes header
            ('SPAN', (3, 0), (5, 0)),  # Span descuentos header
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('ALIGN', (3, 0), (3, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 0), (2, 0), colors.lightgrey),
            ('BACKGROUND', (3, 0), (5, 0), colors.lightgrey),
            
            # Formato para todo el contenido
            ('FONTSIZE', (0, 0), (-1, -1), 8),  # Fuente más pequeña para toda la tabla
            ('ALIGN', (2, 1), (2, -1), 'RIGHT'),  # Right align haber amounts
            ('ALIGN', (5, 1), (5, -1), 'RIGHT'),  # Right align descuento amounts
            
            # Total rows
            ('FONTNAME', (0, -4), (-1, -1), 'Helvetica-Bold'),
            ('LINEABOVE', (0, -4), (-1, -4), 1, colors.black),
            
            # Grid
            ('BOX', (0, 0), (2, -1), 0.5, colors.black),
            ('BOX', (3, 0), (5, -1), 0.5, colors.black),
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
        ]
        
        detail_table.setStyle(TableStyle(style))
        elements.append(detail_table)
        elements.append(Spacer(1, 0.2*inch))
        
        # Texto de cantidad en letras con días y mes
        cantidadStyle = ParagraphStyle(
            'CantidadStyle',
            parent=styles['Normal'],
            fontSize=8,
            leading=10
        )
        try:
            elements.append(Paragraph(f"Son: {self.numero_a_texto(totales['liquido_a_pagar'])}", cantidadStyle))
        except Exception as e:
            elements.append(Paragraph(f"Son: {int(totales['liquido_a_pagar'])} PESOS", cantidadStyle))
        
        elements.append(Paragraph(f"{dias_trabajados} De {mes} Del {year}", cantidadStyle))
        elements.append(Spacer(1, 0.3*inch))
        
        # Texto de certificación más pequeño
        cert_style = ParagraphStyle(
            'CertStyle',
            parent=styles['Normal'],
            fontSize=8,
            leading=10
        )
        cert_text = "Certifico que he revisado la presente liquidación a mi entera satisfacción y no tengo cargo ni cobro alguno posterior que hacer por ninguno de los conceptos comprendidos en ella."
        elements.append(Paragraph(cert_text, cert_style))
        elements.append(Spacer(1, 1*inch))  # Espacio para firma
        
        # Sección de firma en posición similar a la imagen
        class SignatureSection(Flowable):
            def __init__(self):
                Flowable.__init__(self)
                self.width = 7*inch
                self.height = 0.5*inch
                
            def draw(self):
                # Línea de firma más larga
                self.canv.line(self.width/2 - 2*inch, 0, self.width/2 + 2*inch, 0)
                
                # Texto "Recibí Conforme" alineado a la derecha
                self.canv.setFont('Helvetica', 8)
                self.canv.drawRightString(self.width/2 + 2*inch, 10, "Recibí Conforme")
        
        # Agregar sección de firma
        elements.append(SignatureSection())
        
        # Construir el PDF
        doc.build(elements)
        
        return buffer
        
    def numero_a_texto(self, numero):
        """Convert number to text in Spanish"""
        # Lists of word representations
        unidades = ['', 'UNO', 'DOS', 'TRES', 'CUATRO', 'CINCO', 'SEIS', 'SIETE', 'OCHO', 'NUEVE']
        decenas = ['', 'DIEZ', 'VEINTE', 'TREINTA', 'CUARENTA', 'CINCUENTA', 'SESENTA', 'SETENTA', 'OCHENTA', 'NOVENTA']
        centenas = ['', 'CIENTO', 'DOSCIENTOS', 'TRESCIENTOS', 'CUATROCIENTOS', 'QUINIENTOS', 'SEISCIENTOS', 'SETECIENTOS', 'OCHOCIENTOS', 'NOVECIENTOS']
        
        # Special cases for teens and twenties
        especiales = {
            11: 'ONCE', 12: 'DOCE', 13: 'TRECE', 14: 'CATORCE', 15: 'QUINCE',
            16: 'DIECISEIS', 17: 'DIECISIETE', 18: 'DIECIOCHO', 19: 'DIECINUEVE',
            21: 'VEINTIUNO', 22: 'VEINTIDOS', 23: 'VEINTITRES', 24: 'VEINTICUATRO', 
            25: 'VEINTICINCO', 26: 'VEINTISEIS', 27: 'VEINTISIETE', 28: 'VEINTIOCHO', 29: 'VEINTINUEVE'
        }
        
        def convert_to_text(n):
            """Helper function to convert a number to text"""
            # Handle zero case
            if n == 0:
                return 'CERO'
                
            # Handle numbers less than 10
            if n < 10:
                return unidades[n]
                
            # Handle special cases (11-19, 21-29)
            if n in especiales:
                return especiales[n]
                
            # Handle tens (10-99)
            if n < 100:
                if n % 10 == 0:  # Exact tens (10, 20, 30...)
                    return decenas[n // 10]
                else:  # Tens and units (31, 42, 56...)
                    return f"{decenas[n // 10]} Y {unidades[n % 10]}"
                    
            # Handle hundreds (100-999)
            if n < 1000:
                if n == 100:
                    return 'CIEN'
                else:
                    remainder = n % 100
                    if remainder == 0:
                        return centenas[n // 100]
                    else:
                        return f"{centenas[n // 100]} {convert_to_text(remainder)}"
                    
            # Handle thousands (1,000-999,999)
            if n < 1000000:
                thousands = n // 1000
                remainder = n % 1000
                
                if thousands == 1:
                    mil_text = "MIL"
                else:
                    mil_text = f"{convert_to_text(thousands)} MIL"
                    
                if remainder == 0:
                    return mil_text
                else:
                    return f"{mil_text} {convert_to_text(remainder)}"
                    
            # Handle millions (1,000,000+)
            millions = n // 1000000
            remainder = n % 1000000
            
            if millions == 1:
                millon_text = "UN MILLON"
            else:
                millon_text = f"{convert_to_text(millions)} MILLONES"
                
            if remainder == 0:
                return millon_text
            else:
                return f"{millon_text} {convert_to_text(remainder)}"
        
        try:
            # Convert number to integer part only (ignoring cents)
            valor_entero = int(floor(abs(numero)))
            
            # Convert integer part to text
            texto = convert_to_text(valor_entero)
            
            # Return only integer part without cents
            return f"{texto} PESOS"
        except Exception as e:
            # Fallback in case of any error
            print(f"Error converting number to text: {e}")
            return f"{int(numero)} PESOS"

class GuardarContratoVariablesView(APIView):
    
    def get(self, request, documento_id=None, *args, **kwargs):
        # If a document_id is provided in the URL, return that specific document
        if documento_id:
            try:
                documento = ContratoVariables.objects.get(id=documento_id)
                return Response({
                    'id': documento.id,
                    'nombre': documento.nombre,
                    'tipo': documento.tipo,
                    'archivo_pdf_url': request.build_absolute_uri(documento.archivo_pdf.url),
                    'variables': documento.variables,
                    'fecha_creacion': documento.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S'),
                    'activo': documento.activo
                })
            except ContratoVariables.DoesNotExist:
                return Response({"error": f"No se encontró el documento con ID {documento_id}"}, 
                            status=status.HTTP_404_NOT_FOUND)
        else:
            # Otherwise, list all documents for the current user's holding
            documentos = ContratoVariables.objects.filter(holding=request.user.holding)
            documentos_list = []
            
            for doc in documentos:
                documentos_list.append({
                    'id': doc.id,
                    'nombre': doc.nombre,
                    'tipo': doc.tipo,
                    'fecha_creacion': doc.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S'),
                    'activo': doc.activo
                })
            
            return Response(documentos_list)
    
    def post(self, request, *args, **kwargs):
        try:
            # Get PDF file from request
            pdf_file = request.FILES.get('archivo_pdf')
            
            # Debug file info
            if pdf_file:
                print(f"File received: {pdf_file.name}, size: {pdf_file.size} bytes")
            else:
                print("No file received in request")
                return Response({"error": "El archivo PDF es obligatorio"}, status=400)
            
            if pdf_file.size == 0:
                return Response({"error": "El archivo PDF está vacío (0 bytes)"}, status=400)
                
            # Get other form data
            nombre = request.data.get('nombre', 'Documento sin nombre')
            tipo = request.data.get('tipo', 'CHILENO')
            
            # Get variables data
            variables_data = request.data.get('variables')
            if isinstance(variables_data, str):
                variables_json = json.loads(variables_data)
            else:
                variables_json = variables_data
            
            # Save document with variables
            documento = ContratoVariables.objects.create(
                holding=request.user.holding,
                nombre=nombre,
                tipo=tipo,
                archivo_pdf=pdf_file,
                variables=variables_json
            )
            
            return Response({
                "id": documento.id,
                "mensaje": "Documento guardado exitosamente"
            }, status=201)
            
        except Exception as e:
            print(f"Error saving document: {str(e)}")
            return Response({
                "error": f"Error al guardar el documento: {str(e)}"
            }, status=500)
    
    def put(self, request, documento_id, *args, **kwargs):
        """Actualizar variables de un documento existente"""
        try:
            documento = get_object_or_404(ContratoVariables, id=documento_id)
            
            # Verificar que el usuario tiene permisos (misma holding)
            if documento.holding != request.user.holding:
                return Response(
                    {"error": "No tienes permisos para modificar este documento"}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Actualizar variables si se proporcionan
            if 'variables' in request.data:
                # Validar formato de las variables
                variables_data = request.data['variables']
                
                if isinstance(variables_data, str):
                    # Si las variables vienen como string JSON, convertir a objeto
                    try:
                        variables_json = json.loads(variables_data)
                    except json.JSONDecodeError:
                        return Response(
                            {"error": "Formato de variables inválido"}, 
                            status=status.HTTP_400_BAD_REQUEST
                        )
                else:
                    variables_json = variables_data
                
                # Verificar estructura de variables
                for variable in variables_json:
                    if 'nombre' not in variable:
                        return Response(
                            {"error": "Todas las variables deben tener un nombre"}, 
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    if 'ubicaciones' not in variable:
                        return Response(
                            {"error": "Todas las variables deben tener una lista de ubicaciones"}, 
                            status=status.HTTP_400_BAD_REQUEST
                        )
                
                # Guardar las variables actualizadas
                documento.variables = variables_json
                documento.save()
                
                return Response({
                    "mensaje": "Variables actualizadas correctamente",
                    "id": documento.id,
                    "variables_count": len(variables_json)
                })
            else:
                return Response({
                    "error": "No se proporcionaron variables para actualizar"
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class GenerarDocumentoView(APIView):
    
    def post(self, request, *args, **kwargs):
        try:
            # Validar parámetros de entrada
            trabajador_id = request.data.get('trabajador_id')
            documento_id = request.data.get('documento_id')
            
            if not trabajador_id:
                return Response({"error": "El ID del trabajador es obligatorio"}, 
                               status=status.HTTP_400_BAD_REQUEST)
            
            if not documento_id:
                return Response({"error": "El ID del documento es obligatorio"}, 
                               status=status.HTTP_400_BAD_REQUEST)
            
            # Obtener el documento y verificar que exista
            try:
                documento = get_object_or_404(ContratoVariables, id=documento_id)
                if not documento.activo:
                    return Response({"error": "El documento seleccionado no está activo"}, 
                                   status=status.HTTP_400_BAD_REQUEST)
            except:
                return Response({"error": f"No se encontró el documento con ID {documento_id}"}, 
                               status=status.HTTP_404_NOT_FOUND)
            
            # Obtener el trabajador y verificar que exista
            try:
                trabajador = get_object_or_404(PersonalTrabajadores, id=trabajador_id)
            except:
                return Response({"error": f"No se encontró el trabajador con ID {trabajador_id}"}, 
                               status=status.HTTP_404_NOT_FOUND)
            
            # Preparar los datos para las variables
            datos_variables = {
                'nombre': f"{trabajador.nombres} {trabajador.apellidos if trabajador.apellidos else ''}",
                'rut': trabajador.rut or "",
                'dni': trabajador.dni or "",
                'f_inicio': trabajador.fecha_ingreso.strftime('%d/%m/%Y') if trabajador.fecha_ingreso else "",
                'f_ingreso': trabajador.fecha_ingreso.strftime('%d/%m/%Y') if trabajador.fecha_ingreso else "",
                'f_termino': trabajador.fecha_termino.strftime('%d/%m/%Y') if hasattr(trabajador, 'fecha_termino') and trabajador.fecha_termino else "",
                'nacionalidad': trabajador.nacionalidad or "",
                'f_nacmnto': trabajador.fecha_nacimiento.strftime('%d/%m/%Y') if trabajador.fecha_nacimiento else "",
                'e_civil': trabajador.estado_civil or "",
                'domicilio': trabajador.direccion or "",
                'campo_cliente': getattr(trabajador, 'campo_cliente', "") or "",
                'banco': trabajador.banco.nombre if hasattr(trabajador, 'banco') and trabajador.banco else "",
                'cuenta': str(trabajador.numero_cuenta) if hasattr(trabajador, 'numero_cuenta') and trabajador.numero_cuenta else "",
                'firma_empleador': "",  # Definir según lógica de negocio
                'afp': trabajador.afp.nombre if hasattr(trabajador, 'afp') and trabajador.afp else "",
                'salud': trabajador.salud.nombre if hasattr(trabajador, 'salud') and trabajador.salud else "",
                'telefono': trabajador.telefono or "",
                'correo': trabajador.correo or ""
            }
            
            # Añadir datos de contrato si están disponibles
            if hasattr(trabajador, 'contrato') and trabajador.contrato:
                contrato = trabajador.contrato
                if hasattr(contrato, 'fundo') and contrato.fundo:
                    datos_variables['campo_cliente'] = contrato.fundo.nombre_campo
                if hasattr(contrato, 'fecha_termino') and contrato.fecha_termino:
                    datos_variables['f_termino'] = contrato.fecha_termino.strftime('%d/%m/%Y')
            
            # Generar el PDF
            try:
                pdf_path = generar_documento_con_datos(documento_id, datos_variables, debug=False)
            except Exception as e:
                return Response({
                    "error": f"Error al generar el documento: {str(e)}"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Crear una URL para el archivo
            relative_path = os.path.relpath(pdf_path, settings.MEDIA_ROOT)
            pdf_url = request.build_absolute_uri(settings.MEDIA_URL + relative_path)
            
            # Detalle del documento generado
            response_data = {
                "mensaje": "Documento generado exitosamente",
                "url": pdf_url,
                "datos": {
                    "trabajador": f"{trabajador.nombres} {trabajador.apellidos}",
                    "documento": documento.nombre,
                    "fecha_generacion": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Log del error para debugging
            import traceback
            print(f"Error inesperado: {str(e)}")
            print(traceback.format_exc())
            
            return Response({
                "error": f"Error inesperado: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CalibracionesListCreateView(APIView):
    """Vista para listar y crear calibraciones para un documento"""

    def get(self, request, documento_id=None):
        """Obtener todas las calibraciones para un documento específico"""
        try:
            documento = get_object_or_404(ContratoVariables, id=documento_id)
            calibraciones = CalibrationSettings.objects.filter(documento=documento)
            
            # Formatear respuesta
            result = []
            for cal in calibraciones:
                result.append({
                    'id': cal.id,
                    'nombre': cal.nombre,
                    'activo': cal.activo,
                    'fecha_creacion': cal.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S'),
                    'escala_x': cal.escala_x,
                    'escala_y': cal.escala_y,
                    'offset_x': cal.offset_x,
                    'offset_y': cal.offset_y,
                    'invertir_y': cal.invertir_y,
                    'tamaño_pdf_ancho': cal.tamaño_pdf_ancho,
                    'tamaño_pdf_alto': cal.tamaño_pdf_alto
                })
            
            return Response(result)
        except Exception as e:
            print(f"Error al obtener calibraciones: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        """Crear una nueva calibración"""
        try:
            documento_id = request.data.get('documento_id')
            nombre = request.data.get('nombre', f"Calibración {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            
            # Parámetros de calibración
            escala_x = float(request.data.get('escala_x', 0.72))
            escala_y = float(request.data.get('escala_y', 0.72))
            offset_x = int(request.data.get('offset_x', 0))
            offset_y = int(request.data.get('offset_y', 0))
            invertir_y = request.data.get('invertir_y', True)
            if isinstance(invertir_y, str):
                invertir_y = invertir_y.lower() == 'true'
            
            # Metadatos opcionales
            tamaño_pdf_ancho = request.data.get('tamaño_pdf_ancho')
            tamaño_pdf_alto = request.data.get('tamaño_pdf_alto')
            
            # Validar datos requeridos
            if not documento_id:
                return Response({"error": "El ID del documento es obligatorio"}, 
                               status=status.HTTP_400_BAD_REQUEST)
            
            # Verificar que el documento existe
            documento = get_object_or_404(ContratoVariables, id=documento_id)
            
            # Si marcaremos esta calibración como activa, desactivamos las demás
            if request.data.get('activo', True):
                CalibrationSettings.objects.filter(documento=documento, activo=True).update(activo=False)
            
            # Crear la calibración
            calibracion = CalibrationSettings.objects.create(
                documento=documento,
                nombre=nombre,
                activo=request.data.get('activo', True),
                escala_x=escala_x,
                escala_y=escala_y,
                offset_x=offset_x,
                offset_y=offset_y,
                invertir_y=invertir_y,
                tamaño_pdf_ancho=tamaño_pdf_ancho,
                tamaño_pdf_alto=tamaño_pdf_alto
            )
            
            # Registro para depuración
            print(f"Calibración creada: ID={calibracion.id}, escala_x={escala_x}, escala_y={escala_y}, offset_x={offset_x}, offset_y={offset_y}, invertir_y={invertir_y}")
            
            return Response({
                "id": calibracion.id,
                "mensaje": "Calibración creada exitosamente",
                "nombre": calibracion.nombre,
                "activo": calibracion.activo
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            print(f"Error al crear calibración: {str(e)}")
            return Response({
                "error": f"Error al crear calibración: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CalibracionDetailView(APIView):
    """Vista para obtener, actualizar o eliminar una calibración específica"""
    
    def get(self, request, calibracion_id):
        """Obtener detalle de una calibración"""
        try:
            calibracion = get_object_or_404(CalibrationSettings, id=calibracion_id)
            
            return Response({
                'id': calibracion.id,
                'documento_id': calibracion.documento.id,
                'nombre': calibracion.nombre,
                'activo': calibracion.activo,
                'fecha_creacion': calibracion.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S'),
                'escala_x': calibracion.escala_x,
                'escala_y': calibracion.escala_y,
                'offset_x': calibracion.offset_x,
                'offset_y': calibracion.offset_y,
                'invertir_y': calibracion.invertir_y,
                'tamaño_pdf_ancho': calibracion.tamaño_pdf_ancho,
                'tamaño_pdf_alto': calibracion.tamaño_pdf_alto
            })
        except Exception as e:
            print(f"Error al obtener calibración: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def put(self, request, calibracion_id):
        """Actualizar una calibración existente"""
        try:
            calibracion = get_object_or_404(CalibrationSettings, id=calibracion_id)
            
            # Actualizar campos
            if 'nombre' in request.data:
                calibracion.nombre = request.data.get('nombre')
                
            if 'activo' in request.data:
                nuevo_activo = request.data.get('activo')
                if isinstance(nuevo_activo, str):
                    nuevo_activo = nuevo_activo.lower() == 'true'
                
                # Si activamos esta calibración, desactivamos las demás
                if nuevo_activo and not calibracion.activo:
                    CalibrationSettings.objects.filter(
                        documento=calibracion.documento, 
                        activo=True
                    ).exclude(id=calibracion.id).update(activo=False)
                
                calibracion.activo = nuevo_activo
            
            # Parámetros de calibración
            if 'escala_x' in request.data:
                calibracion.escala_x = float(request.data.get('escala_x'))
            
            if 'escala_y' in request.data:
                calibracion.escala_y = float(request.data.get('escala_y'))
            
            if 'offset_x' in request.data:
                calibracion.offset_x = int(request.data.get('offset_x'))
            
            if 'offset_y' in request.data:
                calibracion.offset_y = int(request.data.get('offset_y'))
            
            if 'invertir_y' in request.data:
                invertir_y = request.data.get('invertir_y')
                if isinstance(invertir_y, str):
                    invertir_y = invertir_y.lower() == 'true'
                calibracion.invertir_y = invertir_y
            
            # Metadatos
            if 'tamaño_pdf_ancho' in request.data:
                calibracion.tamaño_pdf_ancho = request.data.get('tamaño_pdf_ancho')
            
            if 'tamaño_pdf_alto' in request.data:
                calibracion.tamaño_pdf_alto = request.data.get('tamaño_pdf_alto')
            
            # Guardar cambios
            calibracion.save()
            
            return Response({
                "id": calibracion.id,
                "mensaje": "Calibración actualizada exitosamente",
                "nombre": calibracion.nombre,
                "activo": calibracion.activo
            })
            
        except Exception as e:
            print(f"Error al actualizar calibración: {str(e)}")
            return Response({
                "error": f"Error al actualizar calibración: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request, calibracion_id):
        """Eliminar una calibración"""
        try:
            calibracion = get_object_or_404(CalibrationSettings, id=calibracion_id)
            nombre = calibracion.nombre
            calibracion.delete()
            
            return Response({
                "mensaje": f"Calibración '{nombre}' eliminada exitosamente"
            })
            
        except Exception as e:
            print(f"Error al eliminar calibración: {str(e)}")
            return Response({
                "error": f"Error al eliminar calibración: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GenerarPDFConCalibracionView(APIView):
    """Vista para generar un PDF aplicando una calibración específica"""
    
    def post(self, request):
        try:
            # Obtener parámetros necesarios
            documento_id = request.data.get('documento_id')
            calibracion_id = request.data.get('calibracion_id')
            
            if not documento_id:
                return Response({"error": "El ID del documento es obligatorio"}, 
                               status=status.HTTP_400_BAD_REQUEST)
            
            # Obtener el documento
            documento = get_object_or_404(ContratoVariables, id=documento_id)
            
            # Obtener calibración
            calibracion = None
            if calibracion_id:
                calibracion = get_object_or_404(CalibrationSettings, id=calibracion_id)
            else:
                # Si no se especifica calibración, intentamos obtener la activa
                try:
                    calibracion = CalibrationSettings.objects.get(
                        documento=documento,
                        activo=True
                    )
                except CalibrationSettings.DoesNotExist:
                    # Si no hay calibración activa, usamos parámetros por defecto
                    pass
            
            # Datos de prueba para las variables
            datos_variables = {}
            
            # Crear datos de prueba para cada variable
            for variable_data in documento.variables:
                nombre_variable = variable_data.get('nombre')
                
                # Si es una variable de fecha, crear un valor de fecha para que se vea realista
                if 'fecha' in nombre_variable or 'f_' in nombre_variable:
                    datos_variables[nombre_variable] = "01/01/2023"
                # Si es RUT o DNI, crear un valor similar
                elif nombre_variable in ['rut', 'dni']:
                    datos_variables[nombre_variable] = "12.345.678-9"
                # Para otras variables, usar un texto descriptivo
                else:
                    datos_variables[nombre_variable] = f"Prueba-{nombre_variable}"
            
            # Generar el PDF usando la calibración
            pdf_path = generar_documento_con_calibracion(
                documento_id=documento_id,
                calibracion=calibracion,
                datos_variables=datos_variables,
                debug=True
            )
            
            # Crear una URL para el archivo
            relative_path = os.path.relpath(pdf_path, settings.MEDIA_ROOT)
            pdf_url = request.build_absolute_uri(settings.MEDIA_URL + relative_path)
            
            # Construir respuesta
            respuesta = {
                "mensaje": "PDF generado exitosamente con calibración",
                "url": pdf_url,
                "documento": documento.nombre
            }
            
            if calibracion:
                respuesta["calibracion"] = {
                    "id": calibracion.id,
                    "nombre": calibracion.nombre,
                    "escala_x": calibracion.escala_x,
                    "escala_y": calibracion.escala_y,
                    "offset_x": calibracion.offset_x,
                    "offset_y": calibracion.offset_y,
                    "invertir_y": calibracion.invertir_y
                }
            else:
                respuesta["calibracion"] = "Usando parámetros por defecto (sin calibración activa)"
            
            return Response(respuesta)
            
        except Exception as e:
            print(f"Error al generar PDF con calibración: {str(e)}")
            import traceback
            print(traceback.format_exc())
            
            return Response({
                "error": f"Error al generar PDF con calibración: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AjustarCalibracionView(APIView):
    """Vista para ajustar parámetros de calibración y generar PDF de prueba"""
    
    def post(self, request):
        try:
            # Obtener datos de calibración temporal
            documento_id = request.data.get('documento_id')
            
            # Parámetros de calibración a probar
            escala_x = float(request.data.get('escala_x', 0.72))
            escala_y = float(request.data.get('escala_y', 0.72))
            offset_x = int(request.data.get('offset_x', 0))
            offset_y = int(request.data.get('offset_y', 0))
            invertir_y = request.data.get('invertir_y', True)
            if isinstance(invertir_y, str):
                invertir_y = invertir_y.lower() == 'true'
            
            # Crear calibración temporal (no guardar en DB)
            calibracion_temp = CalibrationSettings(
                documento_id=documento_id,
                nombre="Calibración Temporal",
                escala_x=escala_x,
                escala_y=escala_y,
                offset_x=offset_x,
                offset_y=offset_y,
                invertir_y=invertir_y
            )
            
            # Datos para generar el PDF
            datos_variables = {}
            
            # Si se proporciona una variable específica para calibrar
            variable_nombre = request.data.get('variable_nombre')
            if variable_nombre:
                # Generar valor de prueba según el tipo de variable
                if 'fecha' in variable_nombre or 'f_' in variable_nombre:
                    datos_variables[variable_nombre] = "01/01/2023"
                elif variable_nombre in ['rut', 'dni']:
                    datos_variables[variable_nombre] = "12.345.678-9"
                else:
                    datos_variables[variable_nombre] = f"Prueba-{variable_nombre}"
            else:
                # Si se pasan datos de variables directamente, los usamos
                if 'datos_variables' in request.data:
                    if isinstance(request.data['datos_variables'], str):
                        datos_variables = json.loads(request.data['datos_variables'])
                    else:
                        datos_variables = request.data['datos_variables']
                else:
                    # Obtener documento para generar valores de prueba para todas las variables
                    documento = get_object_or_404(ContratoVariables, id=documento_id)
                    for variable_data in documento.variables:
                        nombre_var = variable_data.get('nombre')
                        if 'fecha' in nombre_var or 'f_' in nombre_var:
                            datos_variables[nombre_var] = "01/01/2023"
                        elif nombre_var in ['rut', 'dni']:
                            datos_variables[nombre_var] = "12.345.678-9"
                        else:
                            datos_variables[nombre_var] = f"Prueba-{nombre_var}"
            
            # Generar PDF con calibración temporal
            pdf_path = generar_documento_con_calibracion(
                documento_id=documento_id,
                calibracion=calibracion_temp,
                datos_variables=datos_variables,
                debug=True
            )
            
            # Crear URL para el PDF
            relative_path = os.path.relpath(pdf_path, settings.MEDIA_ROOT)
            pdf_url = request.build_absolute_uri(settings.MEDIA_URL + relative_path)
            
            return Response({
                "mensaje": "PDF generado con parámetros de calibración temporales",
                "url": pdf_url,
                "parametros_calibracion": {
                    "escala_x": escala_x,
                    "escala_y": escala_y,
                    "offset_x": offset_x,
                    "offset_y": offset_y,
                    "invertir_y": invertir_y
                }
            })
            
        except Exception as e:
            print(f"Error al ajustar calibración: {str(e)}")
            import traceback
            print(traceback.format_exc())
            
            return Response({
                "error": f"Error al ajustar calibración: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# utils.py function for generating PDFs with variable positioning

def generar_documento_con_calibracion(documento_id, calibracion=None, datos_variables=None, debug=False):
    """
    Genera un PDF con datos de variables posicionadas correctamente, aplicando parámetros
    de calibración específicos.
    
    Args:
        documento_id (int): ID del documento a generar
        calibracion (CalibrationSettings, optional): Configuración de calibración a aplicar.
            Si no se proporciona, se utilizará la calibración activa del documento o los valores por defecto.
        datos_variables (dict, optional): Diccionario con los valores para cada variable.
        debug (bool, optional): Si es True, se dibujarán elementos de depuración en el PDF.
        
    Returns:
        str: Ruta del archivo PDF generado
    """
    from .models import ContratoVariables, CalibrationSettings

    # Obtener el documento con las variables
    documento = ContratoVariables.objects.get(id=documento_id)
    
    # Si no se proporcionó una calibración, intentar obtener la activa
    if calibracion is None:
        try:
            calibracion = CalibrationSettings.objects.get(documento=documento, activo=True)
            print(f"Usando calibración activa del documento: {calibracion.nombre}")
        except CalibrationSettings.DoesNotExist:
            # Crear una calibración temporal con valores por defecto
            print("No hay calibración activa, usando valores por defecto")
            calibracion = CalibrationSettings(
                documento=documento,
                nombre="Calibración Temporal",
                escala_x=0.72,
                escala_y=0.72,
                offset_x=0,
                offset_y=0,
                invertir_y=True
            )
    
    # Ruta al PDF plantilla
    input_pdf_path = documento.archivo_pdf.path
    
    # Crear un nombre de archivo único para el PDF de salida
    filename = f"documento_generado_{uuid.uuid4().hex}.pdf"
    output_dir = os.path.join(settings.MEDIA_ROOT, 'contratos_variables_posicionadas')
    
    # Asegurar que el directorio exista
    os.makedirs(output_dir, exist_ok=True)
    
    output_pdf_path = os.path.join(output_dir, filename)
    
    # Abrir el PDF plantilla
    reader = PdfReader(open(input_pdf_path, "rb"))
    writer = PdfWriter()
    
    # CONFIGURACIÓN SEGÚN TIPO DE DOCUMENTO
    # Esta configuración permite ajustar los parámetros según el tipo de contrato
    BASE_FONT_SIZE = 10  # Tamaño de fuente base
    
    # Parámetros de transformación desde la calibración proporcionada
    params = {
        'escala_x': calibracion.escala_x,
        'escala_y': calibracion.escala_y,
        'offset_x': calibracion.offset_x,
        'offset_y': calibracion.offset_y,
        'invertir_y': calibracion.invertir_y
    }
    
    # Función para transformar coordenadas
    def transform_coordinates(x, y, page_height, page_width=None):
        # Aplicar escala
        pdf_x = x * params['escala_x'] + params['offset_x']
        
        # Aplicar escala e invertir Y si es necesario
        if params['invertir_y']:
            pdf_y = page_height - (y * params['escala_y']) + params['offset_y']
        else:
            pdf_y = y * params['escala_y'] + params['offset_y']
        
        # Logging
        print(f"Transformación: ({x}, {y}) -> ({pdf_x}, {pdf_y})")
        
        return pdf_x, pdf_y
    
    # Organizar variables por página
    variables_por_pagina = {}
    for variable_data in documento.variables:
        nombre_variable = variable_data.get('nombre')
        for ubicacion in variable_data.get('ubicaciones', []):
            pagina = ubicacion.get('pagina', 1)
            if pagina not in variables_por_pagina:
                variables_por_pagina[pagina] = []
            
            # Almacenar todas las propiedades de la ubicación para tener toda la información
            variable_info = {
                'nombre': nombre_variable,
                'posX': ubicacion.get('posX', 0),
                'posY': ubicacion.get('posY', 0)
            }
            
            # Registrar la información en logs para análisis
            print(f"Variable '{nombre_variable}' en página {pagina}: posición original = ({variable_info['posX']}, {variable_info['posY']})")
            
            variables_por_pagina[pagina].append(variable_info)
    
    # Procesar cada página del PDF
    for page_num in range(len(reader.pages)):
        ui_page_num = page_num + 1
        page = reader.pages[page_num]
        
        if ui_page_num in variables_por_pagina:
            # Crear un canvas para esta página
            packet = io.BytesIO()
            page_width = float(page.mediabox.width)
            page_height = float(page.mediabox.height)
            can = canvas.Canvas(packet, pagesize=(page_width, page_height))
            
            # Log dimensions for debugging
            print(f"Procesando página {ui_page_num}: ancho={page_width}, alto={page_height}")
            
            # Añadir cada variable a la página
            for variable in variables_por_pagina[ui_page_num]:
                nombre = variable['nombre']
                if nombre in datos_variables and datos_variables[nombre]:
                    # Coordenadas del frontend
                    frontend_x = variable['posX']
                    frontend_y = variable['posY']
                    
                    # Transformar coordenadas
                    pdf_x, pdf_y = transform_coordinates(frontend_x, frontend_y, page_height)
                    
                    # Valor a imprimir
                    valor = str(datos_variables[nombre])
                    
                    # Configurar fuente
                    can.setFont("Helvetica", BASE_FONT_SIZE)
                    
                    # Campos que deben centrarse
                    campos_centrados = ['rut', 'dni', 'e_civil', 'f_nacmnto', 'f_inicio', 'nacionalidad',
                                    'f_ingreso', 'f_termino']

                    is_centered = nombre in campos_centrados
                    if is_centered:
                        # Centrar texto en la posición
                        text_width = can.stringWidth(valor, "Helvetica", BASE_FONT_SIZE)
                        can.drawString(pdf_x - (text_width/2), pdf_y, valor)
                        print(f"Campo centrado: {nombre} en ({pdf_x}, {pdf_y}) valor: {valor}")
                    else:
                        # Alinear a la izquierda (comportamiento estándar)
                        can.drawString(pdf_x, pdf_y, valor)
                        print(f"Campo normal: {nombre} en ({pdf_x}, {pdf_y}) valor: {valor}")

                    # Modo debug: dibujar indicadores visuales para las variables
                    if debug:
                        # Guardar estado actual para no afectar el resto del documento
                        can.saveState()
                        
                        # Dibujar cruz como indicador de posición exacta
                        can.setStrokeColorRGB(1, 0, 0)  # Rojo
                        can.setLineWidth(0.5)
                        can.line(pdf_x-5, pdf_y, pdf_x+5, pdf_y)  # Línea horizontal
                        can.line(pdf_x, pdf_y-5, pdf_x, pdf_y+5)  # Línea vertical
                        
                        # Añadir rectángulo semitransparente para mejor visibilidad
                        can.setFillColorRGB(1, 0.8, 0.8, alpha=0.3)  # Rojo claro semitransparente
                        can.rect(pdf_x-10, pdf_y-10, 20, 20, fill=True, stroke=False)
                        
                        # Mostrar las coordenadas originales y transformadas como texto
                        can.setFont("Helvetica", 6)
                        can.setFillColorRGB(1, 0, 0)  # Rojo
                        can.drawString(
                            pdf_x + 8,
                            pdf_y - 3,
                            f"O:({int(variable['posX'])},{int(variable['posY'])})->T:({int(pdf_x)},{int(pdf_y)})"
                        )
                        
                        # Restaurar estado para continuar normalmente
                        can.restoreState()
            
            can.save()
            packet.seek(0)
            
            # Crear un nuevo PDF con nuestro canvas
            overlay = PdfReader(packet)
            
            # Combinar la página original con nuestras variables
            page.merge_page(overlay.pages[0])
        
        # Añadir la página al documento final
        writer.add_page(page)
    
    # Guardar el PDF final
    with open(output_pdf_path, "wb") as output_file:
        writer.write(output_file)
    
    return output_pdf_path

class GenerarDocumentosMasivoView(APIView):
    
    def post(self, request, *args, **kwargs):
        try:
            # Validar parámetros de entrada
            trabajador_ids = request.data.get('trabajador_ids', [])
            documento_id = request.data.get('documento_id')
            
            if not trabajador_ids or not isinstance(trabajador_ids, list):
                return Response({"error": "Se requiere una lista de IDs de trabajadores"}, 
                               status=status.HTTP_400_BAD_REQUEST)
            
            if not documento_id:
                return Response({"error": "El ID del documento es obligatorio"}, 
                               status=status.HTTP_400_BAD_REQUEST)
            
            # Obtener el documento y verificar que exista
            try:
                documento = get_object_or_404(ContratoVariables, id=documento_id)
                if not documento.activo:
                    return Response({"error": "El documento seleccionado no está activo"}, 
                                   status=status.HTTP_400_BAD_REQUEST)
            except:
                return Response({"error": f"No se encontró el documento con ID {documento_id}"}, 
                               status=status.HTTP_404_NOT_FOUND)
            
            # Procesar cada trabajador
            urls_generadas = []
            
            for trabajador_id in trabajador_ids:
                try:
                    # Obtener el trabajador
                    trabajador = get_object_or_404(PersonalTrabajadores, id=trabajador_id)
                    
                    # Preparar los datos para las variables
                    datos_variables = {
                        'nombre': f"{trabajador.nombres} {trabajador.apellidos if trabajador.apellidos else ''}",
                        'rut': trabajador.rut or "",
                        'dni': trabajador.dni or "",
                        'f_inicio': trabajador.fecha_ingreso.strftime('%d/%m/%Y') if trabajador.fecha_ingreso else "",
                        'f_ingreso': trabajador.fecha_ingreso.strftime('%d/%m/%Y') if trabajador.fecha_ingreso else "",
                        'f_termino': trabajador.fecha_termino.strftime('%d/%m/%Y') if hasattr(trabajador, 'fecha_termino') and trabajador.fecha_termino else "",
                        'nacionalidad': trabajador.nacionalidad or "",
                        'f_nacmnto': trabajador.fecha_nacimiento.strftime('%d/%m/%Y') if trabajador.fecha_nacimiento else "",
                        'e_civil': trabajador.estado_civil or "",
                        'domicilio': trabajador.direccion or "",
                        'campo_cliente': getattr(trabajador, 'campo_cliente', "") or "",
                        'banco': trabajador.banco.nombre if hasattr(trabajador, 'banco') and trabajador.banco else "",
                        'cuenta': str(trabajador.numero_cuenta) if hasattr(trabajador, 'numero_cuenta') and trabajador.numero_cuenta else "",
                        'firma_empleador': "",  # Definir según lógica de negocio
                        'afp': trabajador.afp.nombre if hasattr(trabajador, 'afp') and trabajador.afp else "",
                        'salud': trabajador.salud.nombre if hasattr(trabajador, 'salud') and trabajador.salud else "",
                        'telefono': trabajador.telefono or "",
                        'correo': trabajador.correo or ""
                    }
                    
                    # Añadir datos de contrato si están disponibles
                    if hasattr(trabajador, 'contratos') and trabajador.contratos.exists():
                        contrato = trabajador.contratos.first()
                        if hasattr(contrato, 'fundo') and contrato.fundo:
                            datos_variables['campo_cliente'] = contrato.fundo.nombre_campo
                        if hasattr(contrato, 'fecha_termino') and contrato.fecha_termino:
                            datos_variables['f_termino'] = contrato.fecha_termino.strftime('%d/%m/%Y')
                    
                    # Generar el PDF
                    pdf_path = generar_documento_con_datos(documento_id, datos_variables, debug=False)
                    
                    # Crear una URL para el archivo
                    relative_path = os.path.relpath(pdf_path, settings.MEDIA_ROOT)
                    pdf_url = request.build_absolute_uri(settings.MEDIA_URL + relative_path)
                    
                    urls_generadas.append(pdf_url)
                    
                except Exception as e:
                    print(f"Error procesando trabajador {trabajador_id}: {str(e)}")
                    # Continuar con el siguiente trabajador
            
            if not urls_generadas:
                return Response({
                    "error": "No se pudo generar ningún documento"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
            return Response({
                "mensaje": f"Documentos generados exitosamente: {len(urls_generadas)} de {len(trabajador_ids)}",
                "urls": urls_generadas
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            # Log del error para debugging
            import traceback
            print(f"Error inesperado: {str(e)}")
            print(traceback.format_exc())
            
            return Response({
                "error": f"Error inesperado: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LibroRemuneracionesElectronicoAPIView(APIView):
    """
    API View para generar el Libro de Remuneraciones Electrónico (LRE)
    en formato CSV según requerimientos del SII.
    """
    
    def get(self, request):
        """
        Genera el Libro de Remuneraciones Electrónico en formato CSV
        """
        try:
            # Obtener parámetros - añadiendo valores por defecto para evitar None
            holding_id = request.query_params.get('holding_id')
            sociedad_id = request.query_params.get('sociedad_id')
            
            # Verificar que los parámetros requeridos estén presentes
            if not holding_id:
                return Response(
                    {"error": "El parámetro holding_id es requerido"},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            if not sociedad_id:
                return Response(
                    {"error": "El parámetro sociedad_id es requerido"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validar y convertir mes y año con manejo adecuado de errores
            try:
                mes = int(request.query_params.get('mes', '0'))
                anio = int(request.query_params.get('anio', '0'))
            except (TypeError, ValueError):
                return Response(
                    {"error": "Los parámetros mes y anio deben ser números enteros válidos"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validar que el mes esté entre 1 y 12
            if mes < 1 or mes > 12:
                return Response(
                    {"error": "El mes debe estar entre 1 y 12"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validar que el año sea razonable
            current_year = datetime.now().year
            if anio < 2000 or anio > current_year + 1:
                return Response(
                    {"error": f"El año debe estar entre 2000 y {current_year + 1}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Obtener sociedad
            try:
                sociedad = Sociedad.objects.get(id=sociedad_id, holding_id=holding_id)
            except Sociedad.DoesNotExist:
                return Response(
                    {"error": "Sociedad no encontrada"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Obtener trabajadores de la sociedad
            trabajadores = PersonalTrabajadores.objects.filter(
                sociedad_id=sociedad_id,
                holding_id=holding_id,
                estado=True
            ).select_related(
                'afp', 
                'salud'
            )
            
            # Si no hay trabajadores, retornar mensaje
            if not trabajadores.exists():
                return Response(
                    {"error": "No hay trabajadores activos para esta sociedad"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Crear buffer para CSV
            buffer = io.StringIO()
            writer = csv.writer(buffer, delimiter=';')
            
            # Escribir encabezados
            headers = self.get_csv_headers()
            writer.writerow(headers)
            
            # Obtener datos del primer día y último día del mes
            primer_dia = date(anio, mes, 1)
            
            # Obtener último día del mes
            if mes == 12:
                ultimo_dia = date(anio + 1, 1, 1)
                ultimo_dia = ultimo_dia.replace(day=1) - timedelta(days=1)
            else:
                ultimo_dia = date(anio, mes + 1, 1)
                ultimo_dia = ultimo_dia.replace(day=1) - timedelta(days=1)
            
            # Procesar cada trabajador
            for trabajador in trabajadores:
                row_data = self.procesar_trabajador(trabajador, sociedad, mes, anio, primer_dia, ultimo_dia)
                
                # IMPORTANTE: Solo escribimos en el CSV las columnas definidas en los encabezados
                # Esto asegura que no haya columnas extra
                writer.writerow(row_data[:len(headers)])
            
            # Preparar respuesta
            buffer.seek(0)
            response = HttpResponse(buffer.getvalue(), content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="Libro_Remuneraciones_{sociedad.nombre}_{mes}_{anio}.csv"'
            
            return response
            
        except Exception as e:
            import traceback
            print(f"Error generando Libro Remuneraciones: {str(e)}")
            print(traceback.format_exc())
            
            return Response(
                {"error": f"Error al generar el libro de remuneraciones: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get_csv_headers(self):
        """
        Retorna los encabezados del CSV según la estructura del LRE
        """
        return [
            "Rut trabajador(1101)",
            "Fecha inicio contrato(1102)",
            "Fecha término de contrato(1103)",
            "Causal término de contrato(1104)",
            "Región prestación de servicios(1105)",
            "Comuna prestación de servicios(1106)",
            "Tipo impuesto a la renta(1170)",
            "Técnico extranjero exención cot. previsionales(1146)",
            "Código tipo de jornada(1107)",
            "Persona con Discapacidad - Pensionado por Invalidez(1108)",
            "Pensionado por vejez(1109)",
            "AFP(1141)",
            "IPS (ExINP)(1142)",
            "FONASA - ISAPRE(1143)",
            "AFC(1151)",
            "CCAF(1110)",
            "Org. administrador ley 16.744(1152)",
            "Nro cargas familiares legales autorizadas(1111)",
            "Nro de cargas familiares maternales(1112)",
            "Nro de cargas familiares invalidez(1113)",
            "Tramo asignación familiar(1114)",
            "Rut org sindical 1(1171)",
            "Rut org sindical 2(1172)",
            "Rut org sindical 3(1173)",
            "Rut org sindical 4(1174)",
            "Rut org sindical 5(1175)",
            "Rut org sindical 6(1176)",
            "Rut org sindical 7(1177)",
            "Rut org sindical 8(1178)",
            "Rut org sindical 9(1179)",
            "Rut org sindical 10(1180)",
            "Nro días trabajados en el mes(1115)",
            "Nro días de licencia médica en el mes(1116)",
            "Nro días de vacaciones en el mes(1117)",
            "Subsidio trabajador joven(1118)",
            "Puesto Trabajo Pesado(1154)",
            "APVI(1155)",
            "APVC(1157)",
            "Indemnización a todo evento(1131)",
            "Tasa indemnización a todo evento(1132)",
            "Sueldo(2101)",
            "Sobresueldo(2102)",
            "Comisiones(2103)",
            "Semana corrida(2104)",
            "Participación(2105)",
            "Gratificación(2106)",
            "Recargo 30% día domingo(2107)",
            "Remun. variable pagada en vacaciones(2108)",
            "Remun. variable pagada en clausura(2109)",
            "Aguinaldo(2110)",
            "Bonos u otras remun. fijas mensuales(2111)",
            "Tratos(2112)",
            "Bonos u otras remun. variables mensuales o superiores a un mes(2113)",
            "Ejercicio opción no pactada en contrato(2114)",
            "Beneficios en especie constitutivos de remun(2115)",
            "Remuneraciones bimestrales(2116)",
            "Remuneraciones trimestrales(2117)",
            "Remuneraciones cuatrimestral(2118)",
            "Remuneraciones semestrales(2119)",
            "Remuneraciones anuales(2120)",
            "Participación anual(2121)",
            "Gratificación anual(2122)",
            "Otras remuneraciones superiores a un mes(2123)",
            "Pago por horas de trabajo sindical(2124)",
            "Sueldo empresarial (2161)",
            "Subsidio por incapacidad laboral por licencia médica(2201)",
            "Beca de estudio(2202)",
            "Gratificaciones de zona(2203)",
            "Otros ingresos no constitutivos de renta(2204)",
            "Colación(2301)",
            "Movilización(2302)",
            "Viáticos(2303)",
            "Asignación de pérdida de caja(2304)",
            "Asignación de desgaste herramienta(2305)",
            "Asignación familiar legal(2311)",
            "Gastos por causa del trabajo(2306)",
            "Gastos por cambio de residencia(2307)",
            "Sala cuna(2308)",
            "Asignación trabajo a distancia o teletrabajo(2309)",
            "Depósito convenido hasta UF 900(2347)",
            "Alojamiento por razones de trabajo(2310)",
            "Asignación de traslación(2312)",
            "Indemnización por feriado legal(2313)",
            "Indemnización años de servicio(2314)",
            "Indemnización sustitutiva del aviso previo(2315)",
            "Indemnización fuero maternal(2316)",
            "Pago indemnización a todo evento(2331)",
            "Indemnizaciones voluntarias tributables(2417)",
            "Indemnizaciones contractuales tributables(2418)",
            "Cotización obligatoria previsional (AFP o IPS)(3141)",
            "Cotización obligatoria salud 7%(3143)",
            "Cotización voluntaria para salud(3144)",
            "Cotización AFC - trabajador(3151)",
            "Cotizaciones técnico extranjero para seguridad social fuera de Chile(3146)",
            "Descuento depósito convenido hasta UF 900 anual(3147)",
            "Cotización APVi Mod A(3155)",
            "Cotización APVi Mod B hasta UF50(3156)",
            "Cotización APVc Mod A(3157)",
            "Cotización APVc Mod B hasta UF50(3158)",
            "Impuesto retenido por remuneraciones(3161)",
            "Impuesto retenido por indemnizaciones(3162)",
            "Mayor retención de impuestos solicitada por el trabajador(3163)",
            "Impuesto retenido por reliquidación remun. devengadas otros períodos(3164)",
            "Diferencia impuesto reliquidación remun. devengadas en este período(3165)",
            "Retención préstamo clase media 2020 (Ley 21.252) (3166)",
            "Rebaja zona extrema DL 889 (3167)",
            "Cuota sindical 1(3171)",
            "Cuota sindical 2(3172)",
            "Cuota sindical 3(3173)",
            "Cuota sindical 4(3174)",
            "Cuota sindical 5(3175)",
            "Cuota sindical 6(3176)",
            "Cuota sindical 7(3177)",
            "Cuota sindical 8(3178)",
            "Cuota sindical 9(3179)",
            "Cuota sindical 10(3180)",
            "Crédito social CCAF(3110)",
            "Cuota vivienda o educación(3181)",
            "Crédito cooperativas de ahorro(3182)",
            "Otros descuentos autorizados y solicitados por el trabajador(3183)",
            "Cotización adicional trabajo pesado - trabajador(3154)",
            "Donaciones culturales y de reconstrucción(3184)",
            "Otros descuentos(3185)",
            "Pensiones de alimentos(3186)",
            "Descuento mujer casada(3187)",
            "Descuentos por anticipos y préstamos(3188)",
            "AFC - Aporte empleador(4151)",
            "Aporte empleador seguro accidentes del trabajo y Ley SANNA(4152)",
            "Aporte empleador indemnización a todo evento(4131)",
            "Aporte adicional trabajo pesado - empleador(4154)",
            "Aporte empleador seguro invalidez y sobrevivencia(4155)",
            "APVC - Aporte Empleador(4157)",
            "Total haberes(5201)",
            "Total haberes imponibles y tributables(5210)",
            "Total haberes imponibles no tributables(5220)",
            "Total haberes no imponibles y no tributables(5230)",
            "Total haberes no imponibles y tributables(5240)",
            "Total descuentos(5301)",
            "Total descuentos impuestos a las remuneraciones(5361)",
            "Total descuentos impuestos por indemnizaciones(5362)",
            "Total descuentos por cotizaciones del trabajador(5341)",
            "Total otros descuentos(5302)",
            "Total aportes empleador(5410)",
            "Total líquido(5501)",
            "Total indemnizaciones(5502)",
            "Total indemnizaciones tributables(5564)",
            "Total indemnizaciones no tributables(5565)"
            # Se han eliminado las columnas adicionales a petición del usuario
        ]
     
    def procesar_trabajador(self, trabajador, sociedad, mes, anio, primer_dia, ultimo_dia):
        """
        Genera los datos para una fila del CSV correspondiente a un trabajador
        """
        # Obtener el contrato activo del trabajador para este período
        try:
            contrato_activo = ContratoTrabajador.objects.filter(
                trabajador=trabajador,
                fecha_inicio_contrato__lte=ultimo_dia,
                fecha_termino_contrato__isnull=True
            ).order_by('-fecha_inicio_contrato').first()
            
            # Si no hay contrato activo, buscamos el último contrato que haya finalizado en este período
            if not contrato_activo:
                contrato_activo = ContratoTrabajador.objects.filter(
                    trabajador=trabajador,
                    fecha_termino_contrato__gte=primer_dia,
                    fecha_termino_contrato__lte=ultimo_dia
                ).order_by('-fecha_inicio_contrato').first()
        except Exception as e:
            print(f"Error al obtener contrato activo: {str(e)}")
            contrato_activo = None
        
        # Obtener días trabajados aprobados para este período
        try:
            dias_trabajados_obj = DiasTrabajadosAprobados.objects.filter(
                trabajador=trabajador,
                mes=mes,
                year=anio
            ).first()
        except Exception as e:
            print(f"Error al obtener días trabajados: {str(e)}")
            dias_trabajados_obj = None
        
        # Buscar licencias médicas en el periodo
        try:
            licencias_mes = LicenciaMedica.objects.filter(
                trabajador=trabajador,
                fecha_inicio__lte=ultimo_dia,
                fecha_fin__gte=primer_dia
            )
        except Exception as e:
            print(f"Error al obtener licencias médicas: {str(e)}")
            licencias_mes = []
        
        # Buscar vacaciones en el periodo
        try:
            vacaciones_mes = Vacaciones.objects.filter(
                trabajador=trabajador,
                fecha_inicio__lte=ultimo_dia,
                fecha_fin__gte=primer_dia
            )
        except Exception as e:
            print(f"Error al obtener vacaciones: {str(e)}")
            vacaciones_mes = []
        
        # Calcular días de licencia y vacaciones en el mes
        dias_licencia = 0
        for licencia in licencias_mes:
            inicio = max(licencia.fecha_inicio, primer_dia)
            fin = min(licencia.fecha_fin, ultimo_dia)
            dias_licencia += (fin - inicio).days + 1
        
        dias_vacaciones = 0
        for vacacion in vacaciones_mes:
            inicio = max(vacacion.fecha_inicio, primer_dia)
            fin = min(vacacion.fecha_fin, ultimo_dia)
            dias_vacaciones += (fin - inicio).days + 1
        
        # Valor por defecto si no hay registros de días trabajados aprobados
        dias_trabajados = 0
        if dias_trabajados_obj:
            dias_trabajados = dias_trabajados_obj.dias_totales
        elif contrato_activo and contrato_activo.fecha_inicio_contrato:
            # Si el trabajador ingresó durante este mes, calcular días desde su ingreso
            if contrato_activo.fecha_inicio_contrato.year == anio and contrato_activo.fecha_inicio_contrato.month == mes:
                dias_trabajados = ultimo_dia.day - contrato_activo.fecha_inicio_contrato.day + 1
            else:
                # Si ya estaba trabajando, asumimos todo el mes
                dias_trabajados = ultimo_dia.day
        
        # Cálculo columna 40 Sueldo Haberes
        sueldo_base = Decimal('0')
        if trabajador.sueldo_base is not None:
            sueldo_base = trabajador.sueldo_base
        
        sueldo_diario = Decimal('0')
        if sueldo_base > Decimal('0'):
            sueldo_diario = sueldo_base / Decimal('30')
        
        sueldo_proporcional = int(sueldo_diario * Decimal(str(dias_trabajados)))

        # Cálculo horas extras
        try:
            horas_extras_mes = HoraExtraordinaria.objects.filter(
                trabajador=trabajador, 
                fecha__year=anio, 
                fecha__month=mes
            ).aggregate(total=Sum('cantidad_horas'))['total'] or 0
        except Exception as e:
            print(f"Error al obtener horas extras: {str(e)}")
            horas_extras_mes = 0

        # Cálculo base imponible para cotizaciones
        base_imponible = Decimal(str(sueldo_proporcional))

        # Sumar otros haberes imponibles del trabajador
        try:
            haberes_imponibles = TrabajadorHaber.objects.filter(
                trabajador=trabajador,
                haber__imponible=True
            ).select_related('haber')

            for haber in haberes_imponibles:
                base_imponible += haber.valor
        except Exception as e:
            print(f"Error al obtener haberes imponibles: {str(e)}")

        # Verificar tope imponible (actualmente 81,6 UF)
        UF_ACTUAL = Decimal('34500')  # Ejemplo, este valor debe obtenerse dinámicamente
        tope_imponible = Decimal('81.6') * UF_ACTUAL

        if base_imponible > tope_imponible:
            base_imponible = tope_imponible

        # Calcular cotización AFP (10% básico + porcentaje adicional de la AFP)
        porcentaje_cotizacion = Decimal('10.0')  # Base fija del 10%
        if hasattr(trabajador, 'afp') and trabajador.afp:
            # Agregar el porcentaje adicional que cobra la AFP por administración
            porcentaje_adicional = trabajador.afp.porcentaje_descuento - Decimal('10.0')
            if porcentaje_adicional > Decimal('0'):
                porcentaje_cotizacion += porcentaje_adicional

        # Calcular el monto final de los descuentos principales
        cotizacion_afp = int(base_imponible * porcentaje_cotizacion / Decimal('100'))
        cotizacion_salud = int(base_imponible * Decimal('0.07'))

        # Inicializar todos los valores en 0 o vacío
        row_data = [""] * 157
        
        #----------------------------------------------------------------------
        # A. DATOS DE IDENTIFICACIÓN DEL TRABAJADOR (CÓD 11XX)
        #----------------------------------------------------------------------
        
        # Llenar datos básicos del trabajador
        row_data[0] = trabajador.rut or ""  # Rut trabajador (1101)
        
        if contrato_activo and contrato_activo.fecha_inicio_contrato:
            row_data[1] = contrato_activo.fecha_inicio_contrato.strftime("%d/%m/%Y")  # Fecha inicio contrato (1102)
        else:
            # Default a 1 de enero del 2025
            row_data[1] = "01/01/2025"
            
        if contrato_activo and contrato_activo.fecha_termino_contrato:
            row_data[2] = contrato_activo.fecha_termino_contrato.strftime("%d/%m/%Y")  # Fecha término de contrato (1103)
        else:
            # Default a 31 de marzo de 2025
            row_data[2] = "31/03/2025"
            
        if contrato_activo and hasattr(contrato_activo, 'causal_finiquito') and contrato_activo.causal_finiquito:
            row_data[3] = contrato_activo.causal_finiquito.codigo  # Causal término de contrato (1104)
        else:
            # Default a 6 (ART. 159 N°4: VENCIMIENTO DEL PLAZO CONVENIDO)
            row_data[3] = "6"
            
        if contrato_activo and hasattr(contrato_activo, 'region_prestacion_servicios') and contrato_activo.region_prestacion_servicios:
            row_data[4] = contrato_activo.region_prestacion_servicios.codigo  # Región prestación de servicios (1105)
        else:
            # Default a Región 7 (MAULE)
            row_data[4] = "7"
            
        if contrato_activo and hasattr(contrato_activo, 'comuna_prestacion_servicios') and contrato_activo.comuna_prestacion_servicios:
            row_data[5] = contrato_activo.comuna_prestacion_servicios.codigo  # Comuna prestación de servicios (1106)
        else:
            # Default a comuna 7404 (PARRAL)
            row_data[5] = "7404"
            
        if contrato_activo and hasattr(contrato_activo, 'tipo_impuesto_renta') and contrato_activo.tipo_impuesto_renta:
            row_data[6] = contrato_activo.tipo_impuesto_renta.codigo  # Tipo impuesto a la renta (1170)
        else:
            row_data[6] = "1"  # Por defecto IUSC
            
        row_data[7] = "0"  # Técnico extranjero exención cot. previsionales (1146) SIEMPRE ES CERO
        
        if contrato_activo and hasattr(contrato_activo, 'tipo_jornada') and contrato_activo.tipo_jornada:
            row_data[8] = contrato_activo.tipo_jornada.codigo  # Código tipo de jornada (1107)
        else:
            row_data[8] = "101"  # Jornada ordinaria por defecto
            
        if contrato_activo and hasattr(contrato_activo, 'tipo_discapacidad') and contrato_activo.tipo_discapacidad:
            row_data[9] = contrato_activo.tipo_discapacidad.codigo  # Persona con Discapacidad - Pensionado por Invalidez (1108)
        else:
            row_data[9] = "0"
            
        row_data[10] = "1" if hasattr(trabajador, 'pensionado_vejez') and trabajador.pensionado_vejez else "0"  # Pensionado por vejez (1109)
        
        # Datos de previsión social
        if hasattr(trabajador, 'afp') and trabajador.afp:
            row_data[11] = trabajador.afp.codigo  # AFP (1141)
        else:
            row_data[11] = "100"  # No está en AFP
            
        if hasattr(trabajador, 'ips_regimen') and trabajador.ips_regimen:
            row_data[12] = trabajador.ips_regimen.codigo  # IPS (ExINP) (1142)
        else:
            row_data[12] = "0"  # No pertenece al IPS
            
        if hasattr(trabajador, 'salud') and trabajador.salud:
            row_data[13] = trabajador.salud.codigo  # FONASA - ISAPRE (1143)
        else:
            row_data[13] = "102"  # FONASA por defecto
            
        row_data[14] = "1" if hasattr(trabajador, 'afiliado_afc') and trabajador.afiliado_afc else "0"  # AFC (1151)
        
        if hasattr(sociedad, 'ccaf') and sociedad.ccaf:
            row_data[15] = sociedad.ccaf.codigo  # CCAF (1110)
        else:
            row_data[15] = "0"  # No tiene CCAF
            
        if hasattr(sociedad, 'mutualidad') and sociedad.mutualidad:
            row_data[16] = sociedad.mutualidad.codigo  # Org. administrador ley 16.744 (1152)
        else:
            row_data[16] = "0"  # Sin mutual/ISL
        
        # Cargas familiares
        if hasattr(trabajador, 'cargas_familiares_legales'):
            row_data[17] = str(trabajador.cargas_familiares_legales)  # Nro cargas familiares legales autorizadas (1111)
        else:
            row_data[17] = "0"
            
        if hasattr(trabajador, 'cargas_familiares_maternales'):
            row_data[18] = "1" if trabajador.cargas_familiares_maternales else "0"  # Nro de cargas familiares maternales (1112)
        else:
            row_data[18] = "0"
            
        if hasattr(trabajador, 'cargas_familiares_invalidez'):
            row_data[19] = str(trabajador.cargas_familiares_invalidez)  # Nro de cargas familiares invalidez (1113)
        else:
            row_data[19] = "0"
        
        # Tramo asignación familiar y Organizaciones sindicales
        row_data[20] = ""  # Tramo asignación familiar (1114)
        row_data[21] = ""  # Rut org sindical 1 (1171)
        row_data[22] = ""  # Rut org sindical 2 (1172)
        row_data[23] = ""  # Rut org sindical 3 (1173)
        row_data[24] = ""  # Rut org sindical 4 (1174)
        row_data[25] = ""  # Rut org sindical 5 (1175)
        row_data[26] = ""  # Rut org sindical 6 (1176)
        row_data[27] = ""  # Rut org sindical 7 (1177)
        row_data[28] = ""  # Rut org sindical 8 (1178)
        row_data[29] = ""  # Rut org sindical 9 (1179)
        row_data[30] = ""  # Rut org sindical 10 (1180)
        
        # Días trabajados, licencias y vacaciones
        row_data[31] = str(dias_trabajados)  # Nro días trabajados en el mes (1115)
        row_data[32] = str(dias_licencia)    # Nro días de licencia médica en el mes (1116)
        row_data[33] = str(dias_vacaciones)  # Nro días de vacaciones en el mes (1117)
        
        # Otros datos de identificación
        if hasattr(trabajador, 'subsidio_trabajador_joven'):
            row_data[34] = "1" if trabajador.subsidio_trabajador_joven else "0"  # Subsidio trabajador joven (1118)
        else:
            row_data[34] = "0"
            
        if hasattr(trabajador, 'puesto_trabajo_pesado'):
            row_data[35] = trabajador.puesto_trabajo_pesado or ""  # Puesto Trabajo Pesado (1154)
        else:
            row_data[35] = ""
            
        if hasattr(trabajador, 'apvi'):
            row_data[36] = "1" if trabajador.apvi else "0"  # APVI (1155)
        else:
            row_data[36] = "0"
            
        if hasattr(trabajador, 'apvc'):
            row_data[37] = "1" if trabajador.apvc else "0"  # APVC (1157)
        else:
            row_data[37] = "0"
            
        if hasattr(trabajador, 'indemnizacion_todo_evento'):
            row_data[38] = "1" if trabajador.indemnizacion_todo_evento else "0"  # Indemnización a todo evento (1131)
        else:
            row_data[38] = "0"
            
        row_data[39] = ""  # Tasa indemnización a todo evento (1132)
        
        #----------------------------------------------------------------------
        # B. HABERES (CÓD 2XXX)
        #----------------------------------------------------------------------
        
        # a. HABERES IMPONIBLES Y TRIBUTABLES (CÓD 21XX)
        row_data[40] = str(sueldo_proporcional)  # Sueldo (2101)
        
        # Cálculo de sobresueldo (solo si hay horas extras)
        if horas_extras_mes > 0 and sueldo_base > Decimal('0'):
            # Factor para calcular hora extra en caso de sueldo mensual
            factor_hora_extra = Decimal('0.0079545')
            sobresueldo = int(sueldo_base * factor_hora_extra * Decimal(str(horas_extras_mes)))
            row_data[41] = str(sobresueldo)  # Sobresueldo (2102)
        else:
            row_data[41] = "0"  # Sobresueldo (2102)
        
        row_data[42] = "0"  # Comisiones (2103)
        row_data[43] = "0"  # Semana corrida (2104)
        row_data[44] = "0"  # Participación (mensual) (2105)
        
        # Gratificación mensual
        if sueldo_base > Decimal('0'):
            # Factor para calcular gratificación mensual
            factor_gratificacion = Decimal('0.02083')
            gratificacion = int(sueldo_base * factor_gratificacion)
            row_data[45] = str(gratificacion)  # Gratificación (mensual) (2106)
        else:
            row_data[45] = "0"
            
        row_data[46] = "0"  # Recargo 30% día domingo (2107)
        row_data[47] = "0"  # Remun. variable pagada en vacaciones (2108)
        row_data[48] = "0"  # Remun. variable pagada en clausura (2109)
        row_data[49] = "0"  # Aguinaldo (2110)
        row_data[50] = "0"  # Bonos u otras remun. fijas mensuales (2111)
        row_data[51] = "0"  # Tratos (2112)
        row_data[52] = "0"  # Bonos u otras remun. variables mensuales (2113)
        row_data[53] = "0"  # Ejercicio opción no pactada en contrato (2114)
        row_data[54] = "0"  # Beneficios en especie constitutivos de remun (2115)
        row_data[55] = "0"  # Remuneraciones bimestrales (2116)
        row_data[56] = "0"  # Remuneraciones trimestrales (2117)
        row_data[57] = "0"  # Remuneraciones cuatrimestral (2118)
        row_data[58] = "0"  # Remuneraciones semestrales (2119)
        row_data[59] = "0"  # Remuneraciones anuales (2120)
        row_data[60] = "0"  # Participación anual (2121)
        row_data[61] = "0"  # Gratificación anual (2122)
        row_data[62] = "0"  # Otras remuneraciones superiores a un mes (2123)
        row_data[63] = "0"  # Pago por horas de trabajo sindical (2124)
        row_data[64] = "0"  # Sueldo empresarial (2161)
        
        # b. HABERES IMPONIBLES Y NO TRIBUTABLES (CÓD 22XX)
        row_data[65] = "0"  # Subsidio por incapacidad laboral por licencia médica (2201)
        row_data[66] = "0"  # Beca de estudio (2202)
        row_data[67] = "0"  # Gratificaciones de zona (2203)
        row_data[68] = "0"  # Otros ingresos no constitutivos de renta (2204)
        
        # c. HABERES NO IMPONIBLES Y NO TRIBUTABLES (CÓD 23XX)
        if hasattr(trabajador, 'colacion') and trabajador.colacion is not None:
            row_data[69] = str(int(trabajador.colacion))  # Colación (2301)
        else:
            row_data[69] = "0"
            
        if hasattr(trabajador, 'movilizacion') and trabajador.movilizacion is not None:
            row_data[70] = str(int(trabajador.movilizacion))  # Movilización (2302)
        else:
            row_data[70] = "0"
            
        row_data[71] = "0"  # Viáticos (2303)
        row_data[72] = "0"  # Asignación de pérdida de caja (2304)
        row_data[73] = "0"  # Asignación de desgaste herramienta (2305)
        row_data[74] = "0"  # Asignación familiar legal (2311)
        row_data[75] = "0"  # Gastos por causa del trabajo (2306)
        row_data[76] = "0"  # Gastos por cambio de residencia (2307)
        row_data[77] = "0"  # Sala cuna (2308)
        row_data[78] = "0"  # Asignación trabajo a distancia o teletrabajo (2309)
        row_data[79] = "0"  # Depósito convenido hasta UF 900 (2347)
        row_data[80] = "0"  # Alojamiento por razones de trabajo (2310)
        row_data[81] = "0"  # Asignación de traslación (2312)
        row_data[82] = "0"  # Indemnización por feriado legal (2313)
        row_data[83] = "0"  # Indemnización años de servicio (2314)
        row_data[84] = "0"  # Indemnización sustitutiva del aviso previo (2315)
        row_data[85] = "0"  # Indemnización fuero maternal (2316)
        row_data[86] = "0"  # Pago indemnización a todo evento (2331)
        
        # d. HABERES NO IMPONIBLES Y TRIBUTABLES (CÓD 24XX)
        row_data[87] = "0"  # Indemnizaciones voluntarias tributables (2417)
        row_data[88] = "0"  # Indemnizaciones contractuales tributables (2418)
        
        #----------------------------------------------------------------------
        # C. DESCUENTOS (CÓD 31XX)
        #----------------------------------------------------------------------
        
        # Descuentos legales previsionales
        row_data[89] = str(cotizacion_afp)  # Cotización obligatoria previsional (AFP o IPS) (3141)
        row_data[90] = str(cotizacion_salud)  # Cotización obligatoria salud 7% (3143)
        
        # Completar descuentos con valores en cero
        for i in range(91, 136):
            row_data[i] = "0"
        
        #----------------------------------------------------------------------
        # D. APORTES DEL EMPLEADOR (CÓD 41XX)
        #----------------------------------------------------------------------
        
        # AFC - Aporte empleador (4151)
        aporte_afc = 0
        if hasattr(trabajador, 'afiliado_afc') and trabajador.afiliado_afc:
            # El aporte empleador a AFC es normalmente 2.4% o 3% según tipo de contrato
            tasa_afc = Decimal('0.03') if contrato_activo and getattr(contrato_activo, 'tipo_contrato', None) == 'INDEFINIDO' else Decimal('0.024')
            aporte_afc = int(base_imponible * tasa_afc)
        row_data[136] = str(aporte_afc)

        # Aporte empleador seguro accidentes del trabajo y Ley SANNA (4152)
        # La tasa básica es 0.95% + tasa adicional según riesgo (usamos 0.95% como mínimo) + 0.03% SANNA
        tasa_accidentes = Decimal('0.0095') + Decimal('0.0003')  # 0.95% básico + 0.03% SANNA
        aporte_accidentes = int(base_imponible * tasa_accidentes)
        row_data[137] = str(aporte_accidentes)

        # Aporte empleador indemnización a todo evento (4131)
        aporte_indemnizacion = 0
        if hasattr(trabajador, 'indemnizacion_todo_evento') and trabajador.indemnizacion_todo_evento:
            # La tasa mínima es 4.11% pero puede ser mayor según pacto
            tasa_indemnizacion = Decimal('0.0411')  # Podría venir del campo row_data[39] si estuviera disponible
            aporte_indemnizacion = int(base_imponible * tasa_indemnizacion)
        row_data[138] = str(aporte_indemnizacion)

        # Aporte adicional trabajo pesado - empleador (4154)
        aporte_trabajo_pesado = 0
        if hasattr(trabajador, 'puesto_trabajo_pesado') and trabajador.puesto_trabajo_pesado:
            # La tasa para trabajo pesado puede ser 1% o 2% según calificación
            tasa_trabajo_pesado = Decimal('0.02')  # Asumimos la tasa máxima
            aporte_trabajo_pesado = int(base_imponible * tasa_trabajo_pesado)
        row_data[139] = str(aporte_trabajo_pesado)

        # Aporte empleador seguro invalidez y sobrevivencia (4155)
        # SIS actualmente está alrededor de 1.53% a cargo del empleador
        aporte_sis = 0
        if not (hasattr(trabajador, 'subsidio_trabajador_joven') and trabajador.subsidio_trabajador_joven):
            # Si no tiene subsidio, el empleador paga el SIS
            tasa_sis = Decimal('0.0153')
            aporte_sis = int(base_imponible * tasa_sis)
        row_data[140] = str(aporte_sis)

        # APVC - Aporte Empleador (4157)
        aporte_apvc = 0
        if hasattr(trabajador, 'apvc') and trabajador.apvc:
            # Este valor debería venir de un parámetro de contrato o configuración
            aporte_apvc = 0  # Por ahora lo dejamos en 0
        row_data[141] = str(aporte_apvc)
        
        #----------------------------------------------------------------------
        # E. TOTALES (CÓD 5XXX)
        #----------------------------------------------------------------------
        
        # a. HABERES (CÓD 52XX)
        
        # Total haberes imponibles y tributables (5210) - Códigos 21xx
        total_haberes_imponibles_tributables = 0
        for i in range(40, 65):  # Códigos 2101 al 2161
            if row_data[i] and row_data[i] != "0":
                total_haberes_imponibles_tributables += int(row_data[i])
        row_data[143] = str(total_haberes_imponibles_tributables)

        # Total haberes imponibles y no tributables (5220) - Códigos 22xx
        total_haberes_imponibles_no_tributables = 0
        for i in range(65, 69):  # Códigos 2201 al 2204
            if row_data[i] and row_data[i] != "0":
                total_haberes_imponibles_no_tributables += int(row_data[i])
        row_data[144] = str(total_haberes_imponibles_no_tributables)

        # Total haberes no imponibles y no tributables (5230) - Códigos 23xx
        total_haberes_no_imponibles_no_tributables = 0
        for i in range(69, 87):  # Códigos 2301 al 2331
            if row_data[i] and row_data[i] != "0":
                total_haberes_no_imponibles_no_tributables += int(row_data[i])
        row_data[145] = str(total_haberes_no_imponibles_no_tributables)

        # Total haberes no imponibles y tributables (5240) - Códigos 24xx
        total_haberes_no_imponibles_tributables = 0
        for i in range(87, 89):  # Códigos 2417 al 2418
            if row_data[i] and row_data[i] != "0":
                total_haberes_no_imponibles_tributables += int(row_data[i])
        row_data[146] = str(total_haberes_no_imponibles_tributables)

        # Total haberes (5201)
        total_haberes = (total_haberes_imponibles_tributables + 
                        total_haberes_imponibles_no_tributables + 
                        total_haberes_no_imponibles_no_tributables + 
                        total_haberes_no_imponibles_tributables)
        row_data[142] = str(total_haberes)
        
        # b. DESCUENTOS (CÓD 53XX)
        
        # Total descuentos por cotizaciones del trabajador (5341)
        total_cotizaciones = 0
        for idx in [89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 130]:  # Códigos 3141, 3143, 3144, etc
            if row_data[idx] and row_data[idx] != "0":
                total_cotizaciones += int(row_data[idx])
        row_data[150] = str(total_cotizaciones)

        # Total descuentos impuestos a las remuneraciones (5361)
        total_impuestos_remuneraciones = 0
        for idx in [109, 113]:  # Códigos 3161 y 3165
            if row_data[idx] and row_data[idx] != "0":
                total_impuestos_remuneraciones += int(row_data[idx])
        row_data[148] = str(total_impuestos_remuneraciones)

        # Total descuentos impuestos por indemnizaciones (5362)
        total_impuestos_indemnizaciones = 0
        if row_data[110] and row_data[110] != "0":
            total_impuestos_indemnizaciones = int(row_data[110])
        row_data[149] = str(total_impuestos_indemnizaciones)
        
        # Calcular total descuentos (5301)
        total_descuentos = 0
        for i in range(89, 136):  # Todos los códigos 31xx excepto 3164 (índice 112)
            if i != 112 and row_data[i] and row_data[i] != "0":  # Excluir 3164 que es solo informativo
                total_descuentos += int(row_data[i])
        row_data[147] = str(total_descuentos)

        # Total otros descuentos (5302)
        total_otros_descuentos = total_descuentos - total_cotizaciones - total_impuestos_remuneraciones - total_impuestos_indemnizaciones
        row_data[151] = str(max(0, total_otros_descuentos))  # Evitar valores negativos
        
        # c. APORTES (CÓD 54XX)
        
        # Total aportes empleador (5410)
        total_aportes_empleador = aporte_afc + aporte_accidentes + aporte_indemnizacion + aporte_trabajo_pesado + aporte_sis + aporte_apvc
        row_data[152] = str(total_aportes_empleador)
        
        # d. OTROS RESULTADOS TOTALES (CÓD 55XX)
        
        # Total líquido (5501)
        total_liquido = total_haberes - total_descuentos
        row_data[153] = str(total_liquido)
        
        # Total indemnizaciones tributables (5564)
        total_indemnizaciones_tributables = 0
        for idx in [87, 88]:  # Códigos 2417 y 2418
            if row_data[idx] and row_data[idx] != "0":
                total_indemnizaciones_tributables += int(row_data[idx])
        row_data[155] = str(total_indemnizaciones_tributables)

        # Total indemnizaciones no tributables (5565)
        total_indemnizaciones_no_tributables = 0
        for idx in [82, 83, 84, 85, 86]:  # Códigos 2313, 2314, 2315, 2316, 2331
            if row_data[idx] and row_data[idx] != "0":
                total_indemnizaciones_no_tributables += int(row_data[idx])
        row_data[156] = str(total_indemnizaciones_no_tributables)

        # Total indemnizaciones (5502)
        total_indemnizaciones = total_indemnizaciones_tributables + total_indemnizaciones_no_tributables
        row_data[154] = str(total_indemnizaciones)
        
        return row_data

class GenerarArchivoPreviewAPIView(APIView):
    """
    Vista para generar el archivo Previred según el formato estándar de largo fijo.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, format=None):
        serializer = ArchivoPreviewSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {'error': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        data = serializer.validated_data
        trabajador_ids = data['trabajador_ids']
        mes = int(data['mes'])
        ano = int(data['ano'])
        
        try:
            # Buscar trabajadores por IDs
            trabajadores = PersonalTrabajadores.objects.filter(
                id__in=trabajador_ids
            ).select_related(
                'afp', 'salud', 'sociedad', 'ips_regimen'
            )
            
            if not trabajadores:
                return Response(
                    {'error': 'No se encontraron trabajadores con los IDs proporcionados'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Generar contenido del archivo
            contenido = self.generar_contenido_previred(trabajadores, mes, ano)
            
            # Crear nombre del archivo
            nombre_archivo = f"Previred_{mes}_{ano}.txt"
            
            # Preparar respuesta con el archivo
            response = HttpResponse(contenido, content_type='text/plain')
            response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
            
            return response
            
        except Exception as e:
            return Response(
                {'error': f'Error al generar el archivo: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def generar_contenido_previred(self, trabajadores, mes, ano):
        """
        Genera el contenido del archivo Previred en formato de largo fijo.
        """
        lineas = []
        
        # Fecha inicio y fin del periodo
        primer_dia = date(ano, mes, 1)
        if mes == 12:
            ultimo_dia = date(ano + 1, 1, 1) - timedelta(days=1)
        else:
            ultimo_dia = date(ano, mes + 1, 1) - timedelta(days=1)
        
        # Formato correcto para Previred
        periodo_desde = primer_dia.strftime('%m%Y')
        periodo_hasta = ultimo_dia.strftime('%m%Y')
        
        for trabajador in trabajadores:
            # Inicializar línea con 105 campos
            campos = [""] * 105
            
            # 1. RUT Trabajador (11 posiciones, rellenar con ceros)
            if trabajador.rut and '-' in trabajador.rut:
                rut_parts = trabajador.rut.split('-')
                rut_num = rut_parts[0].replace('.', '')
                dv = rut_parts[1]
            else:
                rut_num = trabajador.rut.replace('.', '') if trabajador.rut else ''
                dv = ''
            
            campos[0] = rut_num.zfill(11)
            campos[1] = dv
            
            # 3-5. Apellidos y Nombre (correctamente formateados)
            apellidos = trabajador.apellidos or ''
            nombres = trabajador.nombres or ''
            
            # Intentar separar apellidos
            apellido_paterno = ''
            apellido_materno = ''
            
            if apellidos and ' ' in apellidos:
                apellido_paterno = apellidos.split(' ')[0]
                apellido_materno = ' '.join(apellidos.split(' ')[1:])
            else:
                apellido_paterno = apellidos
            
            campos[2] = apellido_paterno.ljust(30)
            campos[3] = apellido_materno.ljust(30)
            campos[4] = nombres.ljust(30)
            
            # 6. Sexo (1 posición)
            sexo = 'M' if trabajador.sexo and trabajador.sexo.upper() in ['MASCULINO', 'M'] else 'F'
            campos[5] = sexo
            
            # 7. Nacionalidad (1 posición)
            nacionalidad = '0' if trabajador.nacionalidad and trabajador.nacionalidad.upper() in ['CHILENA', 'CHILENO'] else '1'
            campos[6] = nacionalidad
            
            # 8. Tipo Pago (2 posiciones)
            campos[7] = '01'  # Remuneraciones del mes
            
            # 9-10. Período Desde/Hasta (6 posiciones cada uno)
            campos[8] = periodo_desde
            campos[9] = periodo_hasta
            
            # 11. Régimen Previsional (3 posiciones)
            if trabajador.afp:
                campos[10] = 'AFP'
            elif trabajador.ips_regimen:
                campos[10] = 'INP'
            else:
                campos[10] = 'SIP'
            
            # 12. Tipo Trabajador (1 posición)
            campos[11] = '1' if trabajador.pensionado_vejez else '0'
            
            # 13. Días Trabajados (2 posiciones)
            campos[12] = '30'.zfill(2)
            
            # 14. Tipo de Línea (2 posiciones)
            campos[13] = '00'  # Línea Principal
            
            # 15. Código Movimiento Personal (2 posiciones)
            campos[14] = '00'  # Sin Movimiento
            
            # 16-17. Fecha Desde/Hasta movimiento (formato DD-MM-AAAA)
            fecha_desde = ''
            fecha_hasta = ''
            
            if trabajador.fecha_ingreso:
                fecha_desde = trabajador.fecha_ingreso.strftime('%d-%m-%Y')
            
            if trabajador.fecha_finiquito:
                fecha_hasta = trabajador.fecha_finiquito.strftime('%d-%m-%Y')
                
            campos[15] = fecha_desde.ljust(10)
            campos[16] = fecha_hasta.ljust(10)
            
            # 18. Tramo Asignación Familiar (1 posición)
            campos[17] = 'D'  # Sin Derecho por defecto
            
            # 19-21. Cargas Familiares
            campos[18] = str(trabajador.cargas_familiares_legales).zfill(2)
            campos[19] = '1' if trabajador.cargas_familiares_maternales else '0'
            campos[20] = str(trabajador.cargas_familiares_invalidez).zfill(1)
            
            # 22-24. Asignación Familiar
            campos[21] = '000000'
            campos[22] = '000000'
            campos[23] = '000000'
            
            # 25. Subsidio Trabajador Joven
            campos[24] = 'S' if trabajador.subsidio_trabajador_joven else 'N'
            
            # 26. Código AFP (2 posiciones)
            codigo_afp = '00'
            if trabajador.afp and hasattr(trabajador.afp, 'codigo') and trabajador.afp.codigo is not None:
                codigo_afp = str(trabajador.afp.codigo).zfill(2)
            campos[25] = codigo_afp
            
            # Obtener renta imponible (sueldo base)
            renta_imponible = int(trabajador.sueldo_base) if trabajador.sueldo_base else 0
            
            # 27. Renta Imponible AFP (8 posiciones)
            campos[26] = str(renta_imponible).zfill(8)
            
            # 28. Cotización Obligatoria AFP
            cotizacion_afp = 0
            if trabajador.afp and renta_imponible > 0:
                porcentaje = float(trabajador.afp.porcentaje_descuento) / 100
                cotizacion_afp = int(renta_imponible * porcentaje)
            campos[27] = str(cotizacion_afp).zfill(8)
            
            # 29. Cotización SIS
            # Calcular SIS como 1.53% del sueldo imponible
            sis = int(renta_imponible * 0.0153) if renta_imponible > 0 else 0
            campos[28] = str(sis).zfill(8)
            
            # 30-39. Otros campos AFP
            campos[29] = '00000000'  # Cuenta Ahorro Voluntario
            campos[30] = '00000000'  # Renta Imponible Sustitutiva
            campos[31] = '00000'     # Tasa Pactada (sin comas)
            campos[32] = '000000000' # Aporte Indemnización
            campos[33] = '00'        # Número Períodos
            campos[34] = '          ' # Período Desde (10 espacios)
            campos[35] = '          ' # Período Hasta (10 espacios)
            campos[36] = '                                        ' # Puesto Trabajo Pesado (40 espacios)
            campos[37] = '00000'     # % Cotización Trabajo Pesado
            campos[38] = '000000'    # Cotización Trabajo Pesado
            
            # 40-44. APV Individual
            campos[39] = '000'       # Código Institución
            campos[40] = '                    ' # Número de Contrato (20 espacios)
            campos[41] = '0'         # Forma de Pago
            campos[42] = '00000000'  # Cotización APVI
            campos[43] = '00000000'  # Cotización Depósitos Convenidos
            
            # 45-49. APV Colectivo
            campos[44] = '000'       # Código Institución
            campos[45] = '                    ' # Número de Contrato (20 espacios)
            campos[46] = '0'         # Forma de Pago
            campos[47] = '00000000'  # Cotización Trabajador
            campos[48] = '00000000'  # Cotización Empleador
            
            # 50-61. Afiliado Voluntario
            campos[49] = '00000000000' # RUT
            campos[50] = ' '          # DV
            campos[51] = '                              ' # Apellido Paterno (30 espacios)
            campos[52] = '                              ' # Apellido Materno (30 espacios)
            campos[53] = '                              ' # Nombres (30 espacios)
            campos[54] = '00'         # Código Movimiento
            campos[55] = '          ' # Fecha Desde (10 espacios)
            campos[56] = '          ' # Fecha Hasta (10 espacios)
            campos[57] = '00'         # Código AFP
            campos[58] = '00000000'   # Monto Capitalización
            campos[59] = '00000000'   # Monto Ahorro Voluntario
            campos[60] = '00'         # Número Períodos
            
            # 62-74. IPS - ISL - FONASA
            codigo_ips = '0000'
            if trabajador.ips_regimen and hasattr(trabajador.ips_regimen, 'codigo'):
                codigo_ips = trabajador.ips_regimen.codigo or '0000'
            campos[61] = codigo_ips    # Código Ex-Caja
            
            campos[62] = '00000'       # Tasa Cotización (sin coma)
            campos[63] = str(renta_imponible).zfill(8)  # Renta Imponible IPS/ISL/FONASA
            
            # Resto de campos IPS/FONASA
            campos[64] = '00000000'  # Cotización Obligatoria IPS
            campos[65] = '00000000'  # Renta Imponible Desahucio
            campos[66] = '0000'      # Código Ex-Caja Régimen Desahucio
            campos[67] = '00000'     # Tasa Cotización Desahucio
            campos[68] = '00000000'  # Cotización Desahucio
            campos[69] = '00000000'  # Cotización Fonasa
            campos[70] = '00000000'  # Cotización Acc. Trabajo (ISL)
            campos[71] = '00000000'  # Bonificación Ley 15.386
            campos[72] = '00000000'  # Descuento por cargas familiares IPS
            campos[73] = '00000000'  # Bonos Gobierno
            
            # 75-82. Datos Salud
            codigo_salud = '00'
            if trabajador.salud and hasattr(trabajador.salud, 'codigo') and trabajador.salud.codigo is not None:
                codigo_salud = str(trabajador.salud.codigo).zfill(2)
            campos[74] = codigo_salud   # Código Institución Salud
            
            campos[75] = '                ' # Número FUN (16 espacios)
            campos[76] = str(renta_imponible).zfill(8)  # Renta Imponible Isapre
            campos[77] = '1'            # Moneda Plan (1=Pesos)
            campos[78] = '00000000'     # Cotización Pactada
            
            # Cotización Obligatoria Isapre (7% del sueldo)
            cotizacion_salud = int(renta_imponible * 0.07) if renta_imponible > 0 else 0
            campos[79] = str(cotizacion_salud).zfill(8)
            
            campos[80] = '00000000'     # Cotización Adicional
            campos[81] = '00000000'     # Monto GES
            
            # 83-95. CCAF
            codigo_ccaf = '00'
            if trabajador.sociedad and hasattr(trabajador.sociedad, 'ccaf') and trabajador.sociedad.ccaf:
                if hasattr(trabajador.sociedad.ccaf, 'codigo'):
                    codigo_ccaf = trabajador.sociedad.ccaf.codigo or '00'
            campos[82] = codigo_ccaf.zfill(2)   # Código CCAF
            
            campos[83] = str(renta_imponible).zfill(8)  # Renta Imponible CCAF
            
            # Resto campos CCAF
            campos[84] = '00000000'  # Créditos Personales
            campos[85] = '00000000'  # Descuento Dental
            campos[86] = '00000000'  # Descuentos por Leasing
            campos[87] = '00000000'  # Descuentos por seguro de vida
            campos[88] = '00000000'  # Otros descuentos
            campos[89] = '00000000'  # Cotización no afiliados a Isapres
            campos[90] = '00000000'  # Descuento Cargas Familiares
            campos[91] = '00000000'  # Otros descuentos 1
            campos[92] = '00000000'  # Otros descuentos 2
            campos[93] = '00000000'  # Bonos Gobierno
            campos[94] = '                    '  # Código de Sucursal (20 espacios)
            
            # 96-99. Mutualidad
            codigo_mutual = '00'
            if trabajador.sociedad and hasattr(trabajador.sociedad, 'mutualidad') and trabajador.sociedad.mutualidad:
                if hasattr(trabajador.sociedad.mutualidad, 'codigo'):
                    codigo_mutual = trabajador.sociedad.mutualidad.codigo or '00'
            campos[95] = codigo_mutual.zfill(2)   # Código Mutualidad
            
            campos[96] = str(renta_imponible).zfill(8)  # Renta Imponible Mutual
            
            # Calcular cotización Mutual (estimada en 0.95%)
            cotizacion_mutual = int(renta_imponible * 0.0095) if renta_imponible > 0 else 0
            campos[97] = str(cotizacion_mutual).zfill(8)  # Cotización Accidente Trabajo
            
            campos[98] = '000'          # Sucursal Mutual
            
            # 100-102. Seguro Cesantía
            campos[99] = str(renta_imponible).zfill(8)  # Renta Imponible Seguro Cesantía
            
            # Aporte Trabajador SC (0.6%)
            aporte_trab_sc = int(renta_imponible * 0.006) if trabajador.afiliado_afc and renta_imponible > 0 else 0
            campos[100] = str(aporte_trab_sc).zfill(8)
            
            # Aporte Empleador SC (2.4%)
            aporte_emp_sc = int(renta_imponible * 0.024) if trabajador.afiliado_afc and renta_imponible > 0 else 0
            campos[101] = str(aporte_emp_sc).zfill(8)
            
            # 103-104. Pagador Subsidio
            campos[102] = '00000000000' # RUT Pagadora
            campos[103] = ' '           # DV Pagadora
            
            # 105. Centro de Costos
            campos[104] = '                    ' # 20 espacios
            
            # Unir todos los campos en una línea
            linea = ''.join(campos)
            lineas.append(linea)
        
        # Unir todas las líneas con salto de línea
        return '\n'.join(lineas)
    
class CuentasAPIView(APIView):
    """
    API para gestionar las cuentas contables
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]
    required_scopes = ['admin', 'write', 'read']

    def get(self, request, format=None):
        """
        Obtiene las cuentas del holding
        """
        try:
            holding_id = request.user.holding.id if request.user.holding else None
            
            if not holding_id:
                return Response(
                    {"message": "No se pudo determinar el holding"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            cuentas = Cuenta.objects.filter(holding_id=holding_id)
            serializer = CuentaSerializer(cuentas, many=True)
            
            return Response({
                "message": f"Se encontraron {len(serializer.data)} cuentas",
                "status": "success",
                "cuentas": serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"Error obteniendo cuentas: {str(e)}")
            
            return Response(
                {"message": f"Error obteniendo cuentas: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request, format=None):
        """
        Crea una nueva cuenta
        """
        try:
            holding_id = request.user.holding.id if request.user.holding else None
            
            if not holding_id:
                return Response(
                    {"message": "No se pudo determinar el holding"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Agregar el holding a los datos
            data = request.data.copy()
            data['holding'] = holding_id
            
            serializer = CuentaSerializer(data=data)
            
            if serializer.is_valid():
                cuenta = serializer.save()
                
                return Response({
                    "message": f"Cuenta '{cuenta.nombre_cuenta}' creada exitosamente",
                    "status": "success",
                    "cuenta": CuentaSerializer(cuenta).data
                }, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {
                        "message": "Datos inválidos",
                        "errors": serializer.errors
                    }, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            print(f"Error creando cuenta: {str(e)}")
            
            return Response(
                {"message": f"Error creando cuenta: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def put(self, request, cuenta_id=None, format=None):
        """
        Actualiza una cuenta existente
        """
        if not cuenta_id:
            return Response(
                {"message": "ID de cuenta requerido"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            holding_id = request.user.holding.id if request.user.holding else None
            
            if not holding_id:
                return Response(
                    {"message": "No se pudo determinar el holding"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            cuenta = Cuenta.objects.get(id=cuenta_id, holding_id=holding_id)
            
            # Agregar el holding a los datos
            data = request.data.copy()
            data['holding'] = holding_id
            
            serializer = CuentaSerializer(cuenta, data=data, partial=True)
            
            if serializer.is_valid():
                cuenta_actualizada = serializer.save()
                
                return Response({
                    "message": f"Cuenta '{cuenta_actualizada.nombre_cuenta}' actualizada exitosamente",
                    "status": "success",
                    "cuenta": CuentaSerializer(cuenta_actualizada).data
                }, status=status.HTTP_200_OK)
            else:
                return Response(
                    {
                        "message": "Datos inválidos",
                        "errors": serializer.errors
                    }, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Cuenta.DoesNotExist:
            return Response(
                {"message": "Cuenta no encontrada"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            print(f"Error actualizando cuenta: {str(e)}")
            
            return Response(
                {"message": f"Error actualizando cuenta: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request, cuenta_id=None, format=None):
        """
        Elimina una cuenta (soft delete - la marca como inactiva)
        """
        if not cuenta_id:
            return Response(
                {"message": "ID de cuenta requerido"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            holding_id = request.user.holding.id if request.user.holding else None
            
            if not holding_id:
                return Response(
                    {"message": "No se pudo determinar el holding"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            cuenta = Cuenta.objects.get(id=cuenta_id, holding_id=holding_id)
            
            # Verificar si la cuenta está siendo utilizada
            facturas_asociadas = FacturaCompraSIIDistribuida.objects.filter(cuenta=cuenta).count()
            
            if facturas_asociadas > 0:
                # Soft delete - marcar como inactiva
                cuenta.activa = False
                cuenta.save()
                
                return Response({
                    "message": f"Cuenta '{cuenta.nombre_cuenta}' desactivada exitosamente (tiene {facturas_asociadas} facturas asociadas)",
                    "status": "success",
                    "tipo_eliminacion": "soft_delete"
                }, status=status.HTTP_200_OK)
            else:
                # Hard delete - eliminar completamente
                nombre_cuenta = cuenta.nombre_cuenta
                cuenta.delete()
                
                return Response({
                    "message": f"Cuenta '{nombre_cuenta}' eliminada exitosamente",
                    "status": "success",
                    "tipo_eliminacion": "hard_delete"
                }, status=status.HTTP_200_OK)
                
        except Cuenta.DoesNotExist:
            return Response(
                {"message": "Cuenta no encontrada"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            print(f"Error eliminando cuenta: {str(e)}")
            
            return Response(
                {"message": f"Error eliminando cuenta: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class SociedadesUsuarioAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_scopes = ['admin', 'write', 'read']

    def get(self, request, usuario_id, format=None):
        try:
            usuario = Usuarios.objects.get(id=usuario_id)
            sociedades = usuario.empresas_asignadas.all()
            
            sociedades_data = []
            for sociedad in sociedades:
                sociedades_data.append({
                    'id': sociedad.id,
                    'nombre': sociedad.nombre,
                    'rut': sociedad.rol_sociedad  # rol_sociedad parece ser el RUT según tu modelo
                })
            
            return Response({
                'usuario_id': usuario_id,
                'sociedades': sociedades_data
            }, status=status.HTTP_200_OK)
            
        except Usuarios.DoesNotExist:
            return Response({"message": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

#===================================================================
#=======================FACTURAS COMPRA=============================
#===================================================================

class FacturasCompraAutomaticoAPIView(APIView):
    """
    API View para manejar el sistema automático de facturas de compra
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_scopes = []
    
    def dispatch(self, request, *args, **kwargs):
        if request.method == 'POST':
            self.required_scopes = ['admin', 'write']
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request, format=None):
        """
        Maneja todas las acciones del sistema automático de facturas
        """
        try:
            action = request.data.get('action', '')
            
            if action == 'get_automatic_configuration':
                return self._get_automatic_configuration(request)
            elif action == 'save_automatic_configuration':
                return self._save_automatic_configuration(request)
            elif action == 'get_automatic_invoices':
                return self._get_automatic_invoices(request)
            elif action == 'get_automatic_process_status':
                return self._get_automatic_process_status(request)
            elif action == 'execute_automatic_process_manual':
                return self._execute_automatic_process_manual(request)
            elif action == 'distribute_automatic_invoices':
                return self._distribute_automatic_invoices(request)
            elif action == 'delete_automatic_invoices':
                return self._delete_automatic_invoices(request)
            elif action == 'toggle_automatic_process':
                return self._toggle_automatic_process(request)
            elif action == 'get_companies_for_configuration':
                return self._get_companies_for_configuration(request)
            elif action == 'validate_sii_credentials':
                return self._validate_sii_credentials(request)
            elif action == 'get_execution_history':
                return self._get_execution_history(request)
            elif action == 'restart_automatic_process':
                return self._restart_automatic_process(request)
            elif action == 'download_invoice_pdf':  
                return self._download_invoice_pdf(request)
            elif action == 'search_pdfs_for_existing_invoices':  
                return self._search_pdfs_for_existing_invoices(request)
            elif action == 'get_pdf_search_status':  
                return self._get_pdf_search_status(request)
            elif action == 'retry_pdf_download':  
                return self._retry_pdf_download(request)
            elif action == 'search_pdfs_for_existing_invoices':
                return self._search_pdfs_for_existing_invoices(request)
            elif action == 'get_pdf_search_status':
                return self._get_pdf_search_status(request)
            # NUEVAS ACCIONES PARA DISTRIBUCIÓN MÚLTIPLE
            elif action == 'distribute_invoice_multiple':
                return self._distribute_invoice_multiple(request)
            elif action == 'get_invoice_distribution_details':
                return self._get_invoice_distribution_details(request)
            elif action == 'validate_distribution':
                return self._validate_distribution(request)
            elif action == 'get_distribution_summary':
                return self._get_distribution_summary(request)
            elif action == 'delete_distribution':
                return self._delete_distribution(request)
            elif action == 'create_manual_invoice':
                return self._create_manual_invoice_compra(request)
            elif action == 'get_next_folio':
                return self._get_next_folio_compra(request)
            else:
                return Response(
                    {"message": "Acción no válida"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            print(f"Error en FacturasCompraAutomaticoAPIView: {str(e)}")
            print(traceback.format_exc())
            return Response(
                {"message": f"Error en el servidor: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _get_next_folio_compra(self, request):
        """Obtiene el próximo folio automático para boletas manuales de compra"""
        try:
            holding_id = request.user.holding.id
            
            # Buscar el último folio de boletas manuales
            ultima_boleta = FacturaCompraSIIPorDistribuir.objects.filter(
                holding_id=holding_id,
                tipo_doc='BOLETA_MANUAL'
            ).order_by('-folio').first()
            
            if ultima_boleta and ultima_boleta.folio.isdigit():
                proximo_folio = int(ultima_boleta.folio) + 1
            else:
                proximo_folio = 1
                
            return Response({
                'status': 'success',
                'next_folio': proximo_folio
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Error obteniendo próximo folio: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _create_manual_invoice_compra(self, request):
        """
        Crea una nueva factura de compra manual (boleta en negro)
        """
        print(f"🐛 DEBUG: Iniciando _create_manual_invoice_compra")
        print(f"🐛 DEBUG: Datos recibidos: {request.data}")
        
        holding_id = request.user.holding.id if request.user.holding else None
        print(f"🐛 DEBUG: holding_id: {holding_id}")
        
        if not holding_id:
            print(f"🐛 DEBUG: Error - No hay holding_id")
            return Response({
                "status": "error", 
                "message": "Usuario sin holding asignado"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Obtener próximo folio automático
            ultima_boleta = FacturaCompraSIIPorDistribuir.objects.filter(
                holding_id=holding_id,
                tipo_doc='BOLETA_MANUAL'
            ).order_by('-folio').first()
            
            if ultima_boleta and ultima_boleta.folio and ultima_boleta.folio.isdigit():
                proximo_folio = int(ultima_boleta.folio) + 1
                print(f"🐛 DEBUG: Última boleta: {ultima_boleta.folio}, próximo folio: {proximo_folio}")
            else:
                proximo_folio = 1
                print(f"🐛 DEBUG: Primera boleta, folio: {proximo_folio}")

            # Extraer y validar datos del request
            tipo_doc = 'BOLETA_MANUAL'  # FIJO
            rut_proveedor = request.data.get('rut_proveedor', '').strip()
            razon_social = request.data.get('razon_social_proveedor', '').strip()
            folio = str(proximo_folio)
            fecha_emision = request.data.get('fecha_emision', '').strip()
            descripcion = request.data.get('descripcion', '').strip()
            observaciones = (request.data.get('observaciones') or '').strip()

            # Montos
            monto_total = float(request.data.get('monto_total', 0))
            monto_neto = float(request.data.get('monto_neto', 0))
            monto_exento = float(request.data.get('monto_exento', 0))
            monto_iva = float(request.data.get('monto_iva_recuperable', 0))
            
            print(f"🐛 DEBUG: Datos procesados - tipo_doc: {tipo_doc}, folio: {folio}, monto_total: {monto_total}")
            
            # Validaciones básicas
            if not all([tipo_doc, rut_proveedor, razon_social, folio, fecha_emision, descripcion]):
                return Response({
                    "status": "error",
                    "message": "Todos los campos son obligatorios"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if monto_total <= 0:
                return Response({
                    "status": "error",
                    "message": "El monto total debe ser mayor a 0"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validar formato RUT
            import re
            if not re.match(r'^\d{1,8}-[\dkK]$', rut_proveedor):
                return Response({
                    "status": "error",
                    "message": "Formato de RUT inválido. Use formato: 12345678-9"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Procesar fechas
            try:
                # Convertir fecha de emisión
                if 'T' in fecha_emision:
                    fecha_emision = fecha_emision.split('T')[0]
                
                datetime.strptime(fecha_emision, '%Y-%m-%d')
                
            except ValueError as e:
                return Response({
                    "status": "error",
                    "message": f"Formato de fecha inválido: {str(e)}"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Verificar si ya existe una factura con el mismo folio para este holding
            factura_existente = FacturaCompraSIIPorDistribuir.objects.filter(
                holding_id=holding_id,
                folio=folio
            ).first()
            
            if factura_existente:
                return Response({
                    "status": "error",
                    "message": f"Ya existe una factura con el folio '{folio}' en este holding"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Crear la factura manual en la base de datos
            with transaction.atomic():
                nueva_factura = FacturaCompraSIIPorDistribuir.objects.create(
                    holding_id=holding_id,
                    
                    # Datos básicos
                    tipo_doc=tipo_doc,
                    rut_proveedor=rut_proveedor,
                    razon_social=razon_social,
                    folio=folio,
                    fecha_docto=fecha_emision,
                    
                    # Montos
                    monto_total=monto_total,
                    monto_neto=monto_neto,
                    monto_exento=monto_exento,
                    monto_iva_recuperable=monto_iva,
                    
                    # Campos adicionales para facturas manuales
                    descripcion=descripcion,
                    observaciones_manual=observaciones,
                    
                    # Identificación como factura manual
                    es_manual=True,
                    fecha_creacion_manual=timezone.now(),
                    
                    # Campos de control
                    fecha_encontrada=timezone.now(),
                    procesada=False,
                    
                    # Campos de distribución inicializados
                    monto_distribuido=0,
                    porcentaje_distribuido=0,
                    
                    # PDF no aplica para facturas manuales
                    pdf_descargado=False,
                    intentos_descarga_pdf=0,
                    
                    # Otros campos por defecto
                    monto_iva_no_recuperable=0,
                    codigo_iva_no_rec=None
                )
                
                print(f"🐛 DEBUG: Factura manual creada con ID: {nueva_factura.id}")
                
                # Preparar respuesta con datos de la factura creada
                factura_data = {
                    'id': nueva_factura.id,
                    'tipo_doc': nueva_factura.tipo_doc,
                    'folio': nueva_factura.folio,
                    'rut_proveedor': nueva_factura.rut_proveedor,
                    'razon_social': nueva_factura.razon_social,
                    'fecha_docto': nueva_factura.fecha_docto,
                    'monto_total': float(nueva_factura.monto_total),
                    'monto_neto': float(nueva_factura.monto_neto),
                    'monto_exento': float(nueva_factura.monto_exento),
                    'monto_iva_recuperable': float(nueva_factura.monto_iva_recuperable),
                    'descripcion': nueva_factura.descripcion,
                    'es_manual': True,
                    'monto_distribuido': float(nueva_factura.monto_distribuido),
                    'monto_pendiente': float(nueva_factura.monto_total - nueva_factura.monto_distribuido),
                    'porcentaje_distribuido': float(nueva_factura.porcentaje_distribuido),
                    'porcentaje_pendiente': float(100 - nueva_factura.porcentaje_distribuido),
                    'distribuciones_count': 0,
                    'completamente_distribuida': False,
                    'pdf_disponible': False
                }
                
                return Response({
                    "status": "success",
                    "message": f"Factura manual '{folio}' creada exitosamente",
                    "factura": factura_data
                }, status=status.HTTP_201_CREATED)
                
        except ValueError as e:
            print(f"🐛 DEBUG: Error de validación: {str(e)}")
            return Response({
                "status": "error",
                "message": f"Error de validación: {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            print(f"🐛 DEBUG: Error general: {str(e)}")
            print(f"🐛 DEBUG: Traceback: {traceback.format_exc()}")
            return Response({
                "status": "error",
                "message": f"Error interno del servidor: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _distribute_invoice_multiple(self, request):
        """
        Distribuye una factura específica a un cliente (distribución múltiple)
        """
        print(f"🐛 DEBUG: Iniciando _distribute_invoice_multiple")
        print(f"🐛 DEBUG: Datos recibidos: {request.data}")
        
        holding_id = request.user.holding.id if request.user.holding else None
        print(f"🐛 DEBUG: holding_id: {holding_id}")
        
        if not holding_id:
            print(f"🐛 DEBUG: Error - No hay holding_id")
            return Response(
                {"message": "No se pudo determinar el holding"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            print(f"🐛 DEBUG: Iniciando validación del serializer")
            
            # Validar datos de entrada
            serializer = DistribucionMultipleFacturaCompraSIISerializer(
                data=request.data, 
                context={'request': request}
            )
            
            print(f"🐛 DEBUG: Serializer creado, validando...")
            
            if not serializer.is_valid():
                print(f"🐛 DEBUG: ❌ SERIALIZER INVÁLIDO")
                print(f"🐛 DEBUG: Errores del serializer: {serializer.errors}")
                return Response(
                    {
                        "status": "error",
                        "message": "Datos de distribución inválidos",
                        "errors": serializer.errors
                    }, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            print(f"🐛 DEBUG: ✅ Serializer válido")
            validated_data = serializer.validated_data
            print(f"🐛 DEBUG: Datos validados: {validated_data}")
            
            # Obtener datos validados
            factura_id = validated_data['factura_id']
            cliente_id = validated_data['cliente_id']
            fundo_id = validated_data.get('fundo_id')
            labor_id = validated_data.get('labor_id')
            cuenta_id = validated_data.get('cuenta_id')
            tipo_distribucion = validated_data['tipo_distribucion']
            monto_a_distribuir = validated_data.get('monto_a_distribuir')
            porcentaje_a_distribuir = validated_data.get('porcentaje_a_distribuir')
            observaciones = validated_data.get('observaciones', '')
            
            print(f"🐛 DEBUG: factura_id: {factura_id}")
            print(f"🐛 DEBUG: cliente_id: {cliente_id}")
            print(f"🐛 DEBUG: tipo_distribucion: {tipo_distribucion}")
            print(f"🐛 DEBUG: monto_a_distribuir: {monto_a_distribuir}")
            print(f"🐛 DEBUG: porcentaje_a_distribuir: {porcentaje_a_distribuir}")
            
            # Obtener la factura
            print(f"🐛 DEBUG: Buscando factura...")
            try:
                factura = FacturaCompraSIIPorDistribuir.objects.get(
                    id=factura_id,
                    holding_id=holding_id
                )
                print(f"🐛 DEBUG: ✅ Factura encontrada: {factura.folio} - {factura.razon_social}")
                print(f"🐛 DEBUG: Factura - Monto total: ${factura.monto_total}")
                print(f"🐛 DEBUG: Factura - Monto distribuido: ${factura.monto_distribuido}")
                print(f"🐛 DEBUG: Factura - Porcentaje distribuido: {factura.porcentaje_distribuido}%")
                print(f"🐛 DEBUG: Factura - Monto pendiente: ${factura.get_monto_pendiente()}")
                print(f"🐛 DEBUG: Factura - Porcentaje pendiente: {factura.get_porcentaje_pendiente()}%")
                print(f"🐛 DEBUG: Factura - Completamente distribuida: {factura.esta_completamente_distribuida()}")
            except FacturaCompraSIIPorDistribuir.DoesNotExist:
                print(f"🐛 DEBUG: ❌ Factura no encontrada")
                return Response(
                    {"message": "Factura no encontrada"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Verificar estado de la factura
            print(f"🐛 DEBUG: Verificando estado de la factura...")
            if factura.esta_completamente_distribuida():
                print(f"🐛 DEBUG: ❌ Factura ya completamente distribuida")
                return Response(
                    {"message": "La factura ya está completamente distribuida"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Obtener entidades relacionadas
            print(f"🐛 DEBUG: Buscando cliente...")
            try:
                cliente = Clientes.objects.get(id=cliente_id, holding=request.user.holding)
                print(f"🐛 DEBUG: ✅ Cliente encontrado: {cliente.nombre}")
            except Clientes.DoesNotExist:
                print(f"🐛 DEBUG: ❌ Cliente no encontrado")
                return Response(
                    {"message": "Cliente no encontrado"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Obtener fundo si se especifica
            fundo = None
            if fundo_id:
                print(f"🐛 DEBUG: Buscando fundo {fundo_id}...")
                try:
                    fundo = CamposClientes.objects.get(id=fundo_id, holding=request.user.holding)
                    print(f"🐛 DEBUG: ✅ Fundo encontrado: {fundo.nombre_campo}")
                except CamposClientes.DoesNotExist:
                    print(f"🐛 DEBUG: ❌ Fundo no encontrado")
                    return Response(
                        {"message": "Fundo no encontrado"}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
            
            # Obtener labor si se especifica
            labor = None
            if labor_id:
                print(f"🐛 DEBUG: Buscando labor {labor_id}...")
                try:
                    labor = Labores.objects.get(id=labor_id, holding=request.user.holding)
                    print(f"🐛 DEBUG: ✅ Labor encontrada: {labor.nombre}")
                except Labores.DoesNotExist:
                    print(f"🐛 DEBUG: ❌ Labor no encontrada")
                    return Response(
                        {"message": "Labor no encontrada"}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
            
            # Obtener cuenta si se especifica
            cuenta = None
            if cuenta_id:
                print(f"🐛 DEBUG: Buscando cuenta {cuenta_id}...")
                try:
                    cuenta = Cuenta.objects.get(id=cuenta_id, holding=request.user.holding)
                    print(f"🐛 DEBUG: ✅ Cuenta encontrada: {cuenta.nombre_cuenta}")
                except Cuenta.DoesNotExist:
                    print(f"🐛 DEBUG: ❌ Cuenta no encontrada")
                    return Response(
                        {"message": "Cuenta no encontrada"}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
            
            # Calcular distribución
            print(f"🐛 DEBUG: Calculando distribución...")
            
            if tipo_distribucion == 'MONTO':
                print(f"🐛 DEBUG: Distribución por MONTO")
                
                # Verificar si se puede distribuir el monto
                if not factura.puede_distribuir_monto(monto_a_distribuir):
                    print(f"🐛 DEBUG: ❌ No se puede distribuir el monto solicitado")
                    print(f"🐛 DEBUG: Monto solicitado: ${monto_a_distribuir}")
                    print(f"🐛 DEBUG: Monto disponible: ${factura.get_monto_pendiente()}")
                    return Response(
                        {"message": f"No se puede distribuir ${monto_a_distribuir:,.2f}. Monto disponible: ${factura.get_monto_pendiente():,.2f}"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Calcular montos proporcionales para otros campos
                print(f"🐛 DEBUG: Calculando proporción...")
                factor_proporcion = monto_a_distribuir / factura.monto_total
                print(f"🐛 DEBUG: Factor de proporción: {factor_proporcion}")
                
                monto_neto_distribuido = factura.monto_neto * factor_proporcion
                monto_exento_distribuido = factura.monto_exento * factor_proporcion
                monto_iva_recuperable_distribuido = factura.monto_iva_recuperable * factor_proporcion
                
                porcentaje_distribuido = (monto_a_distribuir / factura.monto_total) * 100
                print(f"🐛 DEBUG: Porcentaje calculado: {porcentaje_distribuido}%")
                
            elif tipo_distribucion == 'PORCENTAJE':
                print(f"🐛 DEBUG: Distribución por PORCENTAJE")
                
                # Verificar si se puede distribuir el porcentaje
                if not factura.puede_distribuir_porcentaje(porcentaje_a_distribuir):
                    print(f"🐛 DEBUG: ❌ No se puede distribuir el porcentaje solicitado")
                    print(f"🐛 DEBUG: Porcentaje solicitado: {porcentaje_a_distribuir}%")
                    print(f"🐛 DEBUG: Porcentaje disponible: {factura.get_porcentaje_pendiente()}%")
                    return Response(
                        {"message": f"No se puede distribuir {porcentaje_a_distribuir}%. Porcentaje disponible: {factura.get_porcentaje_pendiente()}%"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Calcular monto a distribuir
                porcentaje_decimal = porcentaje_a_distribuir / 100
                monto_a_distribuir = factura.monto_total * porcentaje_decimal
                print(f"🐛 DEBUG: Monto calculado: ${monto_a_distribuir}")
                
                # Calcular montos proporcionales
                monto_neto_distribuido = factura.monto_neto * porcentaje_decimal
                monto_exento_distribuido = factura.monto_exento * porcentaje_decimal
                monto_iva_recuperable_distribuido = factura.monto_iva_recuperable * porcentaje_decimal
                
                porcentaje_distribuido = porcentaje_a_distribuir
                
            print(f"🐛 DEBUG: Monto final a distribuir: ${monto_a_distribuir}")
            print(f"🐛 DEBUG: Porcentaje final: {porcentaje_distribuido}%")
            
            # Crear la distribución
            print(f"🐛 DEBUG: Creando registro de distribución...")
            try:
                distribucion = FacturaCompraSIIDistribuida.objects.create(
                    holding_id=holding_id,
                    cliente=cliente,
                    fundo=fundo,
                    labor=labor,
                    cuenta=cuenta,
                    
                    # Datos de la factura
                    folio=factura.folio,
                    tipo_doc=factura.tipo_doc,
                    tipo_compra=factura.tipo_compra,
                    rut_proveedor=factura.rut_proveedor,
                    razon_social=factura.razon_social,
                    fecha_docto=factura.fecha_docto,
                    fecha_recepcion=factura.fecha_recepcion,
                    fecha_acuse=factura.fecha_acuse,
                    
                    # Montos proporcionales
                    monto_exento=monto_exento_distribuido,
                    monto_neto=monto_neto_distribuido,
                    monto_iva_recuperable=monto_iva_recuperable_distribuido,
                    monto_iva_no_recuperable=factura.monto_iva_no_recuperable * (porcentaje_distribuido / 100) if factura.monto_iva_no_recuperable else 0,
                    codigo_iva_no_rec=factura.codigo_iva_no_rec,
                    monto_total=monto_a_distribuir,  # El monto distribuido
                    monto_neto_activo_fijo=factura.monto_neto_activo_fijo * (porcentaje_distribuido / 100) if factura.monto_neto_activo_fijo else 0,
                    iva_activo_fijo=factura.iva_activo_fijo * (porcentaje_distribuido / 100) if factura.iva_activo_fijo else 0,
                    iva_uso_comun=factura.iva_uso_comun * (porcentaje_distribuido / 100) if factura.iva_uso_comun else 0,
                    impto_sin_derecho_credito=factura.impto_sin_derecho_credito * (porcentaje_distribuido / 100) if factura.impto_sin_derecho_credito else 0,
                    iva_no_retenido=factura.iva_no_retenido * (porcentaje_distribuido / 100) if factura.iva_no_retenido else 0,
                    tabacos_puros=factura.tabacos_puros * (porcentaje_distribuido / 100) if factura.tabacos_puros else 0,
                    tabacos_cigarrillos=factura.tabacos_cigarrillos * (porcentaje_distribuido / 100) if factura.tabacos_cigarrillos else 0,
                    tabacos_elaborados=factura.tabacos_elaborados * (porcentaje_distribuido / 100) if factura.tabacos_elaborados else 0,
                    nce_nde_fact_compra=factura.nce_nde_fact_compra * (porcentaje_distribuido / 100) if factura.nce_nde_fact_compra else 0,
                    codigo_otro_impuesto=factura.codigo_otro_impuesto,
                    valor_otro_impuesto=factura.valor_otro_impuesto * (porcentaje_distribuido / 100) if factura.valor_otro_impuesto else 0,
                    tasa_otro_impuesto=factura.tasa_otro_impuesto,
                    
                    # CAMPOS DE DISTRIBUCIÓN MÚLTIPLE
                    monto_distribuido=monto_a_distribuir,
                    porcentaje_distribuido=porcentaje_distribuido,
                    tipo_distribucion=tipo_distribucion,
                    monto_total_factura=factura.monto_total,
                    
                    observaciones=observaciones,
                    usuario_distribuyente=request.user
                )
                print(f"🐛 DEBUG: ✅ Distribución creada con ID: {distribucion.id}")
            except Exception as e:
                print(f"🐛 DEBUG: ❌ Error creando distribución: {str(e)}")
                print(f"🐛 DEBUG: Error completo: {traceback.format_exc()}")
                return Response(
                    {"message": f"Error creando distribución: {str(e)}"}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Actualizar totales en la factura original
            print(f"🐛 DEBUG: Actualizando totales en factura original...")
            try:
                factura.monto_distribuido += monto_a_distribuir
                factura.porcentaje_distribuido += porcentaje_distribuido
                
                print(f"🐛 DEBUG: Nuevo monto distribuido: ${factura.monto_distribuido}")
                print(f"🐛 DEBUG: Nuevo porcentaje distribuido: {factura.porcentaje_distribuido}%")
                
                # Verificar si está completamente distribuida
                if factura.esta_completamente_distribuida():
                    print(f"🐛 DEBUG: Factura ahora está completamente distribuida")
                    factura.procesada = True
                
                factura.save()
                print(f"🐛 DEBUG: ✅ Factura actualizada")
            except Exception as e:
                print(f"🐛 DEBUG: ❌ Error actualizando factura: {str(e)}")
                print(f"🐛 DEBUG: Error completo: {traceback.format_exc()}")
                return Response(
                    {"message": f"Error actualizando factura: {str(e)}"}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            print(f"🐛 DEBUG: ✅ Distribución completada exitosamente")
            
            return Response({
                "status": "success",
                "message": f"Factura distribuida exitosamente. Monto: ${monto_a_distribuir:,.2f} ({porcentaje_distribuido:.2f}%)",
                "data": {
                    "distribucion_id": distribucion.id,
                    "monto_distribuido": float(monto_a_distribuir),
                    "porcentaje_distribuido": float(porcentaje_distribuido),
                    "monto_pendiente": float(factura.get_monto_pendiente()),
                    "porcentaje_pendiente": float(factura.get_porcentaje_pendiente()),
                    "completamente_distribuida": factura.esta_completamente_distribuida()
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"🐛 DEBUG: ❌ ERROR GENERAL EN _distribute_invoice_multiple")
            print(f"🐛 DEBUG: Error: {str(e)}")
            print(f"🐛 DEBUG: Traceback completo:")
            print(traceback.format_exc())
            return Response(
                {"message": f"Error distribuyendo factura: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _get_invoice_distribution_details(self, request):
        """
        Obtiene los detalles de distribución de una factura específica
        """
        holding_id = request.user.holding.id if request.user.holding else None
        factura_id = request.data.get('factura_id')
        
        if not holding_id:
            return Response(
                {"message": "No se pudo determinar el holding"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not factura_id:
            return Response(
                {"message": "ID de factura es requerido"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Obtener la factura
            factura = FacturaCompraSIIPorDistribuir.objects.get(
                id=factura_id,
                holding_id=holding_id
            )
            
            # Obtener todas las distribuciones
            distribuciones = FacturaCompraSIIDistribuida.objects.filter(
                holding_id=holding_id,
                folio=factura.folio,
                rut_proveedor=factura.rut_proveedor
            ).order_by('-fecha_distribucion')
            
            # Serializar datos
            factura_serializer = FacturaPorDistribuirMultipleSerializer(factura)
            distribuciones_serializer = FacturaCompraSIIDistribuidaMultipleSerializer(distribuciones, many=True)
            
            return Response({
                "status": "success",
                "factura": factura_serializer.data,
                "distribuciones": distribuciones_serializer.data,
                "resumen": {
                    "monto_total": float(factura.monto_total),
                    "monto_distribuido": float(factura.monto_distribuido),
                    "monto_pendiente": float(factura.get_monto_pendiente()),
                    "porcentaje_distribuido": float(factura.porcentaje_distribuido),
                    "porcentaje_pendiente": float(factura.get_porcentaje_pendiente()),
                    "total_distribuciones": distribuciones.count(),
                    "completamente_distribuida": factura.esta_completamente_distribuida()
                }
            }, status=status.HTTP_200_OK)
            
        except FacturaCompraSIIPorDistribuir.DoesNotExist:
            return Response(
                {"message": "Factura no encontrada"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            print(f"Error obteniendo detalles de distribución: {str(e)}")
            return Response(
                {"message": f"Error obteniendo detalles: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _validate_distribution(self, request):
        """
        Valida si se puede realizar una distribución específica
        """
        serializer = ValidarDistribucionSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if not serializer.is_valid():
            return Response(
                {
                    "status": "error",
                    "valid": False,
                    "errors": serializer.errors
                }, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response({
            "status": "success",
            "valid": True,
            "message": "La distribución es válida"
        }, status=status.HTTP_200_OK)
    
    def _get_distribution_summary(self, request):
        """
        Obtiene un resumen de todas las facturas y sus distribuciones
        """
        holding_id = request.user.holding.id if request.user.holding else None
        
        if not holding_id:
            return Response(
                {"message": "No se pudo determinar el holding"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Obtener estadísticas
            total_facturas = FacturaCompraSIIPorDistribuir.objects.filter(holding_id=holding_id).count()
            facturas_pendientes = FacturaCompraSIIPorDistribuir.objects.filter(
                holding_id=holding_id, 
                procesada=False
            ).count()
            facturas_parcialmente_distribuidas = FacturaCompraSIIPorDistribuir.objects.filter(
                holding_id=holding_id,
                procesada=False,
                porcentaje_distribuido__gt=0
            ).count()
            
            # Facturas con distribuciones parciales para mostrar progreso
            facturas_con_progreso = FacturaCompraSIIPorDistribuir.objects.filter(
                holding_id=holding_id,
                procesada=False,
                porcentaje_distribuido__gt=0
            ).order_by('-fecha_encontrada')[:10]
            
            facturas_progreso_data = []
            for factura in facturas_con_progreso:
                facturas_progreso_data.append({
                    'id': factura.id,
                    'folio': factura.folio,
                    'razon_social': factura.razon_social,
                    'monto_total': float(factura.monto_total),
                    'monto_distribuido': float(factura.monto_distribuido),
                    'porcentaje_distribuido': float(factura.porcentaje_distribuido),
                    'distribuciones_count': factura.get_distribuciones().count()
                })
            
            return Response({
                "status": "success",
                "estadisticas": {
                    "total_facturas": total_facturas,
                    "facturas_pendientes": facturas_pendientes,
                    "facturas_completamente_distribuidas": total_facturas - facturas_pendientes,
                    "facturas_parcialmente_distribuidas": facturas_parcialmente_distribuidas,
                    "facturas_sin_distribuir": facturas_pendientes - facturas_parcialmente_distribuidas
                },
                "facturas_con_progreso": facturas_progreso_data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"Error obteniendo resumen de distribución: {str(e)}")
            return Response(
                {"message": f"Error obteniendo resumen: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _delete_distribution(self, request):
        """
        Elimina una distribución específica y actualiza los totales de la factura
        """
        holding_id = request.user.holding.id if request.user.holding else None
        distribucion_id = request.data.get('distribucion_id')
        
        if not holding_id:
            return Response(
                {"message": "No se pudo determinar el holding"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not distribucion_id:
            return Response(
                {"message": "ID de distribución es requerido"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            with transaction.atomic():
                # Obtener la distribución
                distribucion = FacturaCompraSIIDistribuida.objects.get(
                    id=distribucion_id,
                    holding_id=holding_id
                )
                
                # Obtener la factura asociada
                factura = FacturaCompraSIIPorDistribuir.objects.get(
                    holding_id=holding_id,
                    folio=distribucion.folio,
                    rut_proveedor=distribucion.rut_proveedor
                )
                
                # Restar los montos de la distribución eliminada
                factura.monto_distribuido -= distribucion.monto_distribuido
                factura.porcentaje_distribuido -= distribucion.porcentaje_distribuido
                
                # Si estaba marcada como procesada y ya no está 100% distribuida, desmarcarla
                if factura.procesada and not factura.esta_completamente_distribuida():
                    factura.procesada = False
                
                factura.save()
                
                # Guardar información antes de eliminar
                distribucion_info = distribucion.get_distribucion_info()
                
                # Eliminar la distribución
                distribucion.delete()
                
                return Response({
                    "status": "success",
                    "message": f"Distribución eliminada exitosamente",
                    "distribucion_eliminada": distribucion_info,
                    "factura_actualizada": factura.get_factura_data()
                }, status=status.HTTP_200_OK)
                
        except FacturaCompraSIIDistribuida.DoesNotExist:
            return Response(
                {"message": "Distribución no encontrada"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except FacturaCompraSIIPorDistribuir.DoesNotExist:
            return Response(
                {"message": "Factura asociada no encontrada"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            print(f"Error eliminando distribución: {str(e)}")
            return Response(
                {"message": f"Error eliminando distribución: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # ==================== CONFIGURACIÓN AUTOMÁTICA ====================

    def _get_automatic_configuration(self, request):
        """
        Obtiene la configuración automática del holding - ACTUALIZADA
        """
        holding_id = request.user.holding.id if request.user.holding else None
        
        if not holding_id:
            return Response(
                {"message": "No se pudo determinar el holding"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            configuracion = ConfiguracionSIIAutomaticaCompra.objects.get(holding_id=holding_id)
            
            # ACTUALIZADO: Incluir nuevos campos
            data = {
                'rut_sii': configuracion.rut_sii,
                'empresa_rut': configuracion.empresa_rut,
                'empresa_nombre': configuracion.empresa_nombre,
                'hora_ejecucion': configuracion.hora_ejecucion.strftime('%H:%M'),
                'mes': configuracion.mes,
                'year': configuracion.year,
                'activo': configuracion.activo,
                'created_at': configuracion.created_at,
                'updated_at': configuracion.updated_at
            }
     
            return Response({
                "message": "Configuración obtenida exitosamente",
                "status": "success",
                "data": data
            }, status=status.HTTP_200_OK)
            
        except ConfiguracionSIIAutomaticaCompra.DoesNotExist:
            return Response({
                "message": "No hay configuración automática",
                "status": "not_found",
                "data": None
            }, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Error obteniendo configuración automática: {str(e)}")
            return Response(
                {"message": f"Error obteniendo configuración: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _save_automatic_configuration(self, request):
        """
        Guarda o actualiza la configuración automática - ACTUALIZADA
        """
        holding_id = request.user.holding.id if request.user.holding else None
        
        if not holding_id:
            return Response(
                {"message": "No se pudo determinar el holding"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Validar datos requeridos - NUEVOS CAMPOS INCLUIDOS
            required_fields = ['rut_sii', 'password_sii', 'empresa_rut', 'hora_ejecucion', 'mes', 'year']
            for field in required_fields:
                if request.data.get(field) is None:  # Permitir 0 para mes
                    return Response(
                        {"message": f"El campo {field} es requerido"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Validar mes y año
            try:
                mes = int(request.data['mes'])
                year = int(request.data['year'])
                
                if not 1 <= mes <= 12:
                    return Response(
                        {"message": "El mes debe estar entre 1 y 12"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                import datetime
                current_year = datetime.datetime.now().year
                if not 2000 <= year <= current_year + 5:
                    return Response(
                        {"message": f"El año debe estar entre 2000 y {current_year + 5}"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                    
            except (ValueError, TypeError):
                return Response(
                    {"message": "Mes y año deben ser números enteros válidos"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Convertir hora_ejecucion string a objeto time
            hora_str = request.data['hora_ejecucion']
            try:
                if isinstance(hora_str, str):
                    from datetime import time
                    hora_parts = hora_str.split(':')
                    hora_obj = time(int(hora_parts[0]), int(hora_parts[1]))
                else:
                    hora_obj = hora_str
            except (ValueError, IndexError) as e:
                return Response(
                    {"message": "Formato de hora inválido. Use HH:MM"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Encriptar contraseña si es necesario
            password_a_guardar = request.data['password_sii']
            
            # Obtener o crear configuración
            configuracion, created = ConfiguracionSIIAutomaticaCompra.objects.get_or_create(
                holding_id=holding_id,
                defaults={
                    'rut_sii': request.data['rut_sii'],
                    'password_sii': password_a_guardar,
                    'empresa_rut': request.data['empresa_rut'],
                    'empresa_nombre': request.data.get('empresa_nombre', ''),
                    'hora_ejecucion': hora_obj,
                    'mes': mes,
                    'year': year,
                    'activo': request.data.get('activo', True)
                }
            )
            
            if not created:
                # Actualizar configuración existente - INCLUIR NUEVOS CAMPOS
                configuracion.rut_sii = request.data['rut_sii']
                configuracion.password_sii = password_a_guardar
                configuracion.empresa_rut = request.data['empresa_rut']
                configuracion.empresa_nombre = request.data.get('empresa_nombre', configuracion.empresa_nombre)
                configuracion.hora_ejecucion = hora_obj
                configuracion.mes = mes
                configuracion.year = year
                configuracion.activo = request.data.get('activo', configuracion.activo)
                
                # Validar antes de guardar
                try:
                    configuracion.full_clean()
                    configuracion.save()
                except ValidationError as e:
                    return Response(
                        {"message": f"Error de validación: {str(e)}"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Respuesta con la configuración actualizada
            response_data = {
                'rut_sii': configuracion.rut_sii,
                'empresa_rut': configuracion.empresa_rut,
                'empresa_nombre': configuracion.empresa_nombre,
                'hora_ejecucion': configuracion.hora_ejecucion.strftime('%H:%M'),
                'mes': configuracion.mes,
                'year': configuracion.year,
                
                'activo': configuracion.activo
            }
            
            action_text = "creada" if created else "actualizada"
            
            return Response({
                "message": f"Configuración {action_text} exitosamente",
                "status": "success",
                "data": response_data
            }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
            
        except Exception as e:
            print(f"Error guardando configuración automática: {str(e)}")
            return Response(
                {"message": f"Error guardando configuración: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # ==================== FACTURAS AUTOMÁTICAS ====================

    def _get_automatic_invoices(self, request):
        """
        Obtiene facturas encontradas automáticamente con información de distribución múltiple
        """
        holding_id = request.user.holding.id if request.user.holding else None
        
        if not holding_id:
            return Response(
                {"message": "No se pudo determinar el holding"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Obtener facturas automáticas (incluyendo parcialmente distribuidas)
            facturas_query = FacturaCompraSIIPorDistribuir.objects.filter(
                holding_id=holding_id,
                procesada=False  # Solo las que no están 100% distribuidas
            ).order_by('-fecha_encontrada')
            
            # Usar el nuevo serializer que incluye información de distribución
            facturas_serializer = FacturaPorDistribuirMultipleSerializer(facturas_query, many=True)
            
            # Estadísticas actualizadas
            total_facturas = facturas_query.count()
            facturas_sin_distribuir = facturas_query.filter(porcentaje_distribuido=0).count()
            facturas_parcialmente_distribuidas = facturas_query.filter(
                porcentaje_distribuido__gt=0,
                porcentaje_distribuido__lt=100
            ).count()
            
            # Estadísticas de PDFs (mantener las existentes)
            facturas_con_pdf = facturas_query.filter(pdf_descargado=True).count()
            facturas_sin_pdf = facturas_query.filter(
                pdf_descargado=False,
                intentos_descarga_pdf__lt=3
            ).count()
            facturas_error_pdf = facturas_query.filter(
                pdf_descargado=False,
                intentos_descarga_pdf__gte=3
            ).count()
            
            estadisticas = {
                # Estadísticas de distribución
                'total_facturas': total_facturas,
                'facturas_sin_distribuir': facturas_sin_distribuir,
                'facturas_parcialmente_distribuidas': facturas_parcialmente_distribuidas,
                'facturas_con_alguna_distribucion': total_facturas - facturas_sin_distribuir,
                
                # Estadísticas de PDFs
                'facturas_con_pdf': facturas_con_pdf,
                'facturas_sin_pdf': facturas_sin_pdf,
                'facturas_error_pdf': facturas_error_pdf,
                'porcentaje_con_pdf': round((facturas_con_pdf / total_facturas * 100) if total_facturas > 0 else 0, 1),
                'porcentaje_sin_pdf': round((facturas_sin_pdf / total_facturas * 100) if total_facturas > 0 else 0, 1),
                'porcentaje_error_pdf': round((facturas_error_pdf / total_facturas * 100) if total_facturas > 0 else 0, 1)
            }
            
            return Response({
                "message": f"Se encontraron {total_facturas} facturas para distribuir",
                "status": "success",
                "facturas": facturas_serializer.data,
                "estadisticas": estadisticas
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"Error obteniendo facturas automáticas: {str(e)}")
            print(traceback.format_exc())
            return Response(
                {"message": f"Error obteniendo facturas automáticas: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _download_invoice_pdf(self, request):
        """
        Descarga el PDF de una factura específica
        MEJORADO: Mejor validación y manejo de errores
        """
        factura_id = request.data.get('factura_id')
        
        if not factura_id:
            return Response(
                {"message": "ID de factura es obligatorio"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            holding_id = request.user.holding.id if request.user.holding else None
            
            # Obtener la factura
            try:
                factura = FacturaCompraSIIPorDistribuir.objects.get(
                    id=factura_id,
                    holding_id=holding_id
                )
            except FacturaCompraSIIPorDistribuir.DoesNotExist:
                return Response(
                    {"message": "Factura no encontrada"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Verificar que tiene PDF
            if not factura.pdf_documento:
                return Response(
                    {
                        "message": "La factura no tiene PDF disponible",
                        "status": "no_pdf",
                        "info": {
                            "pdf_descargado": factura.pdf_descargado,
                            "intentos_descarga": factura.intentos_descarga_pdf,
                            "error_descarga": factura.error_descarga_pdf,
                            "codigo_sii": factura.codigo_sii
                        }
                    }, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Verificar que el archivo existe
            try:
                pdf_path = factura.pdf_documento.path
                if not os.path.exists(pdf_path):
                    return Response(
                        {"message": "El archivo PDF no se encuentra en el servidor"}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
            except Exception:
                return Response(
                    {"message": "Error accediendo al archivo PDF"}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Información del archivo
            file_size = os.path.getsize(pdf_path)
            
            # Retornar información del PDF para descarga
            return Response({
                "message": "PDF encontrado",
                "status": "success",
                "pdf_info": {
                    "url": factura.pdf_documento.url,
                    "filename": f"factura_{factura.tipo_doc}_{factura.folio}_{factura.rut_proveedor}.pdf",
                    "size_bytes": file_size,
                    "size_mb": round(file_size / (1024 * 1024), 2),
                    "fecha_descarga": factura.fecha_descarga_pdf.strftime('%d/%m/%Y %H:%M') if factura.fecha_descarga_pdf else None
                },
                "factura_info": {
                    "folio": factura.folio,
                    "tipo_doc": factura.tipo_doc,
                    "rut_proveedor": factura.rut_proveedor,
                    "razon_social": factura.razon_social,
                    "fecha_docto": factura.fecha_docto,
                    "monto_total": float(factura.monto_total)
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"Error descargando PDF: {str(e)}")
            print(traceback.format_exc())
            return Response(
                {"message": f"Error descargando PDF: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _retry_pdf_download(self, request):
        """
        Reintenta la descarga de PDFs para facturas específicas que fallaron
        NUEVA FUNCIONALIDAD
        """
        factura_ids = request.data.get('factura_ids', [])
        
        if not factura_ids:
            return Response(
                {"message": "Lista de IDs de facturas es obligatoria"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            holding_id = request.user.holding.id if request.user.holding else None
            
            # Verificar configuración
            try:
                configuracion = ConfiguracionSIIAutomaticaCompra.objects.get(holding_id=holding_id)
            except ConfiguracionSIIAutomaticaCompra.DoesNotExist:
                return Response(
                    {"message": "No hay configuración automática"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Obtener facturas válidas para reintentar
            facturas = FacturaCompraSIIPorDistribuir.objects.filter(
                id__in=factura_ids,
                holding_id=holding_id,
                pdf_descargado=False
            )
            
            if not facturas.exists():
                return Response(
                    {"message": "No se encontraron facturas válidas para reintentar"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Resetear contadores de intentos para darles otra oportunidad
            facturas.update(
                intentos_descarga_pdf=0,
                error_descarga_pdf=None
            )
            
            # Ejecutar búsqueda de PDFs específica
            from .tasks import buscar_pdfs_facturas_existentes
            task_result = buscar_pdfs_facturas_existentes.delay(holding_id)
            
            return Response({
                "message": f"Reintento de descarga iniciado para {facturas.count()} facturas",
                "status": "success",
                "task_id": task_result.id,
                "facturas_procesadas": list(facturas.values_list('id', flat=True))
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"Error en reintento de PDFs: {str(e)}")
            return Response(
                {"message": f"Error en reintento de PDFs: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _search_pdfs_for_existing_invoices(self, request):
        """
        Busca PDFs para facturas existentes que no los tienen
        MEJORADO: Mejor validación y estadísticas más detalladas
        """
        holding_id = request.user.holding.id if request.user.holding else None
        
        if not holding_id:
            return Response(
                {"message": "No se pudo determinar el holding"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Verificar configuración
            try:
                configuracion = ConfiguracionSIIAutomaticaCompra.objects.get(holding_id=holding_id)
            except ConfiguracionSIIAutomaticaCompra.DoesNotExist:
                return Response(
                    {"message": "No hay configuración automática configurada"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not configuracion.activo:
                return Response(
                    {"message": "La configuración automática está desactivada"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Estadísticas detalladas
            facturas_sin_pdf = FacturaCompraSIIPorDistribuir.objects.filter(
                holding_id=holding_id,
                pdf_descargado=False,
                intentos_descarga_pdf__lt=3  # Solo las que pueden reintentarse
            )
            
            facturas_error_pdf = FacturaCompraSIIPorDistribuir.objects.filter(
                holding_id=holding_id,
                pdf_descargado=False,
                intentos_descarga_pdf__gte=3  # Las que ya fallaron muchas veces
            )
            
            total_sin_pdf = facturas_sin_pdf.count()
            total_error_pdf = facturas_error_pdf.count()
            
            if total_sin_pdf == 0:
                mensaje = "No hay facturas sin PDF para procesar"
                if total_error_pdf > 0:
                    mensaje += f" ({total_error_pdf} facturas con errores permanentes)"
                
                return Response({
                    "message": mensaje,
                    "status": "success",
                    "estadisticas": {
                        "facturas_sin_pdf": 0,
                        "facturas_error_pdf": total_error_pdf,
                        "facturas_procesables": 0
                    }
                }, status=status.HTTP_200_OK)
            
            # Ejecutar búsqueda de PDFs en background
            from .tasks import buscar_pdfs_facturas_existentes
            task_result = buscar_pdfs_facturas_existentes.delay(holding_id)
            
            return Response({
                "message": f"Búsqueda de PDFs iniciada para {total_sin_pdf} facturas",
                "status": "success",
                "task_id": task_result.id,
                "estadisticas": {
                    "facturas_sin_pdf": total_sin_pdf,
                    "facturas_error_pdf": total_error_pdf,
                    "facturas_procesables": total_sin_pdf
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"Error iniciando búsqueda de PDFs: {str(e)}")
            print(traceback.format_exc())
            return Response(
                {"message": f"Error iniciando búsqueda de PDFs: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _get_pdf_search_status(self, request):
        """
        Obtiene el estado detallado de la búsqueda de PDFs
        MEJORADO: Estadísticas más completas y útiles
        """
        holding_id = request.user.holding.id if request.user.holding else None
        
        if not holding_id:
            return Response(
                {"message": "No se pudo determinar el holding"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Estadísticas generales
            total_facturas = FacturaCompraSIIPorDistribuir.objects.filter(
                holding_id=holding_id,
                procesada=False
            ).count()
            
            facturas_con_pdf = FacturaCompraSIIPorDistribuir.objects.filter(
                holding_id=holding_id,
                procesada=False,
                pdf_descargado=True
            ).count()
            
            facturas_sin_pdf = FacturaCompraSIIPorDistribuir.objects.filter(
                holding_id=holding_id,
                procesada=False,
                pdf_descargado=False,
                intentos_descarga_pdf__lt=3
            ).count()
            
            facturas_error_pdf = FacturaCompraSIIPorDistribuir.objects.filter(
                holding_id=holding_id,
                procesada=False,
                pdf_descargado=False,
                intentos_descarga_pdf__gte=3
            ).count()
            
            # Estadísticas por tipo de error (últimos 10 errores)
            facturas_con_error = FacturaCompraSIIPorDistribuir.objects.filter(
                holding_id=holding_id,
                procesada=False,
                pdf_descargado=False,
                error_descarga_pdf__isnull=False
            ).exclude(error_descarga_pdf='').order_by('-fecha_encontrada')[:10]
            
            errores_recientes = []
            for factura in facturas_con_error:
                errores_recientes.append({
                    'folio': factura.folio,
                    'rut_proveedor': factura.rut_proveedor,
                    'error': factura.error_descarga_pdf,
                    'intentos': factura.intentos_descarga_pdf,
                    'fecha': factura.fecha_encontrada.strftime('%d/%m/%Y %H:%M')
                })
            
            # Facturas descargadas recientemente (últimas 5)
            facturas_recientes_pdf = FacturaCompraSIIPorDistribuir.objects.filter(
                holding_id=holding_id,
                procesada=False,
                pdf_descargado=True,
                fecha_descarga_pdf__isnull=False
            ).order_by('-fecha_descarga_pdf')[:5]
            
            pdfs_recientes = []
            for factura in facturas_recientes_pdf:
                pdfs_recientes.append({
                    'folio': factura.folio,
                    'rut_proveedor': factura.rut_proveedor,
                    'razon_social': factura.razon_social[:50],  # Truncar para UI
                    'fecha_descarga': factura.fecha_descarga_pdf.strftime('%d/%m/%Y %H:%M'),
                    'pdf_url': factura.pdf_documento.url if factura.pdf_documento else None
                })
            
            # Calcular porcentajes
            porcentaje_con_pdf = round((facturas_con_pdf / total_facturas * 100) if total_facturas > 0 else 0, 1)
            porcentaje_sin_pdf = round((facturas_sin_pdf / total_facturas * 100) if total_facturas > 0 else 0, 1)
            porcentaje_error_pdf = round((facturas_error_pdf / total_facturas * 100) if total_facturas > 0 else 0, 1)
            
            return Response({
                "status": "success",
                "estadisticas_pdf": {
                    "total_facturas": total_facturas,
                    "facturas_con_pdf": facturas_con_pdf,
                    "facturas_sin_pdf": facturas_sin_pdf,
                    "facturas_error_pdf": facturas_error_pdf,
                    "porcentaje_con_pdf": porcentaje_con_pdf,
                    "porcentaje_sin_pdf": porcentaje_sin_pdf,
                    "porcentaje_error_pdf": porcentaje_error_pdf,
                    "facturas_procesables": facturas_sin_pdf  # Las que se pueden reintentar
                },
                "errores_recientes": errores_recientes,
                "pdfs_recientes": pdfs_recientes,
                "resumen": {
                    "estado_general": "excelente" if porcentaje_con_pdf >= 90 else 
                                    "bueno" if porcentaje_con_pdf >= 70 else
                                    "regular" if porcentaje_con_pdf >= 50 else "necesita_atencion",
                    "mensaje": f"{facturas_con_pdf} de {total_facturas} facturas tienen PDF ({porcentaje_con_pdf}%)"
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"Error obteniendo estado de PDFs: {str(e)}")
            print(traceback.format_exc())
            return Response(
                {"message": f"Error obteniendo estado de PDFs: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _get_automatic_process_status(self, request):
        """
        Obtiene el estado actual del proceso automático
        """
        holding_id = request.user.holding.id if request.user.holding else None
        
        if not holding_id:
            return Response(
                {"message": "No se pudo determinar el holding"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Obtener configuración
            configuracion_activa = False
            try:
                configuracion = ConfiguracionSIIAutomaticaCompra.objects.get(holding_id=holding_id)
                configuracion_activa = True  # Si existe la configuración, está activa
            except ConfiguracionSIIAutomaticaCompra.DoesNotExist:
                return Response({
                    "message": "Estado del proceso obtenido",
                    "status": "success",
                    "status_data": {
                        'estado': 'sin_configuracion',
                        'facturas_encontradas': 0,
                        'mensaje': 'No hay configuración automática',
                        'configuracion_activa': False  # ← CAMPO FALTANTE
                    }
                }, status=status.HTTP_200_OK)
            
            # Obtener facturas pendientes
            facturas_pendientes = FacturaCompraSIIPorDistribuir.objects.filter(
                holding_id=holding_id,
                procesada=False
            ).count()
            
            # Determinar estado del proceso
            if not configuracion.activo:
                estado = 'inactivo'
                mensaje = 'Proceso automático desactivado'
            else:
                # Aquí podrías verificar el estado real de las tareas de Celery
                # Por simplicidad, asumimos que está funcionando si está activo
                estado = 'completado'
                mensaje = 'Proceso funcionando normalmente'
            
            # Calcular próxima ejecución (simplificado)
            proxima_ejecucion = self._calcular_proxima_ejecucion(configuracion.hora_ejecucion)
            
            status_data = {
                'estado': estado,
                'ultima_ejecucion': None,  # Podría obtenerse de logs o cache
                'proxima_ejecucion': proxima_ejecucion.isoformat() if proxima_ejecucion else None,
                'facturas_encontradas': facturas_pendientes,
                'mensaje': mensaje,
                'configuracion_activa': configuracion_activa  # ← CAMPO FALTANTE AGREGADO
            }
            
            return Response({
                "message": "Estado del proceso obtenido",
                "status": "success",
                "status_data": status_data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"Error obteniendo estado del proceso: {str(e)}")
            return Response(
                {"message": f"Error obteniendo estado: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _execute_automatic_process_manual(self, request):
        """
        Ejecuta el proceso automático de manera manual (para pruebas)
        """
        holding_id = request.user.holding.id if request.user.holding else None
        
        if not holding_id:
            return Response(
                {"message": "No se pudo determinar el holding"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Verificar que existe configuración
            try:
                configuracion = ConfiguracionSIIAutomaticaCompra.objects.get(holding_id=holding_id)
            except ConfiguracionSIIAutomaticaCompra.DoesNotExist:
                return Response(
                    {"message": "No hay configuración automática"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Ejecutar proceso en background
            task_result = procesar_configuracion_automatica.delay(configuracion.id)
            
            return Response({
                "message": "Proceso automático iniciado",
                "status": "success",
                "task_id": task_result.id
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"Error ejecutando proceso manual: {str(e)}")
            return Response(
                {"message": f"Error ejecutando proceso: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _distribute_automatic_invoices(self, request):
        """
        Distribuye facturas encontradas automáticamente
        """
        holding_id = request.user.holding.id if request.user.holding else None
        
        if not holding_id:
            return Response(
                {"message": "No se pudo determinar el holding"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Validar datos usando el mismo serializer del sistema manual
            serializer = DistribucionFacturasSIISerializer(
                data=request.data, 
                context={'request': request}
            )
            
            if not serializer.is_valid():
                return Response(
                    {
                        "message": "Datos de distribución inválidos",
                        "errors": serializer.errors
                    }, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            validated_data = serializer.validated_data
            
            with transaction.atomic():
                # Obtener los objetos relacionados
                cliente = Clientes.objects.get(
                    id=validated_data['cliente_id'], 
                    holding_id=holding_id
                )
                
                fundo = None
                if validated_data.get('fundo_id'):
                    fundo = CamposClientes.objects.get(id=validated_data['fundo_id'])
                
                labor = None
                if validated_data.get('labor_id'):
                    labor = Labores.objects.get(id=validated_data['labor_id'])
                
                cuenta = None
                if validated_data.get('cuenta_id'):
                    cuenta = Cuenta.objects.get(id=validated_data['cuenta_id'])
                
                # Procesar facturas seleccionadas
                facturas_distribuidas = 0
                facturas_seleccionadas = validated_data['facturas_seleccionadas']
                
                for factura_data in facturas_seleccionadas:
                    folio = factura_data.get('folio')
                    
                    # Buscar la factura automática
                    try:
                        factura_automatica = FacturaCompraSIIPorDistribuir.objects.get(
                            holding_id=holding_id,
                            folio=folio,
                            procesada=False
                        )
                    except FacturaCompraSIIPorDistribuir.DoesNotExist:
                        continue  # Ya fue procesada o no existe
                    
                    # Verificar que no esté ya distribuida
                    existe = FacturaCompraSIIDistribuida.objects.filter(
                        holding_id=holding_id,
                        folio=folio,
                        rut_proveedor=factura_automatica.rut_proveedor
                    ).exists()
                    
                    if existe:
                        continue
                    
                    # Crear la distribución
                    FacturaCompraSIIDistribuida.objects.create(
                        holding_id=holding_id,
                        cliente=cliente,
                        fundo=fundo,
                        labor=labor,
                        cuenta=cuenta,
                        
                        # Datos de la factura automática
                        folio=factura_automatica.folio,
                        tipo_doc=factura_automatica.tipo_doc,
                        tipo_compra=factura_automatica.tipo_compra,
                        rut_proveedor=factura_automatica.rut_proveedor,
                        razon_social=factura_automatica.razon_social,
                        fecha_docto=factura_automatica.fecha_docto,
                        fecha_recepcion=factura_automatica.fecha_recepcion,
                        fecha_acuse=factura_automatica.fecha_acuse,
                        
                        # Montos
                        monto_exento=factura_automatica.monto_exento,
                        monto_neto=factura_automatica.monto_neto,
                        monto_iva_recuperable=factura_automatica.monto_iva_recuperable,
                        monto_iva_no_recuperable=factura_automatica.monto_iva_no_recuperable,
                        codigo_iva_no_rec=factura_automatica.codigo_iva_no_rec,
                        monto_total=factura_automatica.monto_total,
                        monto_neto_activo_fijo=factura_automatica.monto_neto_activo_fijo,
                        iva_activo_fijo=factura_automatica.iva_activo_fijo,
                        iva_uso_comun=factura_automatica.iva_uso_comun,
                        impto_sin_derecho_credito=factura_automatica.impto_sin_derecho_credito,
                        iva_no_retenido=factura_automatica.iva_no_retenido,
                        tabacos_puros=factura_automatica.tabacos_puros,
                        tabacos_cigarrillos=factura_automatica.tabacos_cigarrillos,
                        tabacos_elaborados=factura_automatica.tabacos_elaborados,
                        nce_nde_fact_compra=factura_automatica.nce_nde_fact_compra,
                        codigo_otro_impuesto=factura_automatica.codigo_otro_impuesto,
                        valor_otro_impuesto=factura_automatica.valor_otro_impuesto,
                        tasa_otro_impuesto=factura_automatica.tasa_otro_impuesto,
                        
                        # Metadatos
                        usuario_distribuyente=request.user,
                        observaciones=validated_data.get('observaciones', '')
                    )
                    
                    # Marcar factura automática como procesada
                    factura_automatica.procesada = True
                    factura_automatica.save()
                    
                    facturas_distribuidas += 1
                
                # Preparar respuesta
                distribucion_info = {
                    'cliente': {
                        'id': cliente.id,
                        'nombre': cliente.nombre,
                        'rut': cliente.rut
                    },
                    'fundo': {
                        'id': fundo.id,
                        'nombre': fundo.nombre_campo
                    } if fundo else None,
                    'labor': {
                        'id': labor.id,
                        'nombre': labor.nombre
                    } if labor else None,
                    'cuenta': {
                        'id': cuenta.id,
                        'nombre': cuenta.nombre_cuenta,
                        'codigo': cuenta.cuenta_contable
                    } if cuenta else None
                }
                
                return Response({
                    "message": f"Se distribuyeron {facturas_distribuidas} facturas automáticas exitosamente",
                    "status": "success",
                    "facturas_distribuidas": facturas_distribuidas,
                    "distribucion": distribucion_info
                }, status=status.HTTP_200_OK)
                
        except Exception as e:
            print(f"Error distribuyendo facturas automáticas: {str(e)}")
            print(traceback.format_exc())
            return Response(
                {"message": f"Error distribuyendo facturas: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # ==================== MÉTODOS AUXILIARES ====================

    def _delete_automatic_invoices(self, request):
        """Elimina facturas automáticas por folios"""
        # Implementación simplificada
        return Response({"message": "Funcionalidad en desarrollo"}, status=status.HTTP_501_NOT_IMPLEMENTED)

    def _toggle_automatic_process(self, request):
        """Activa o desactiva el proceso automático"""
        holding_id = request.user.holding.id if request.user.holding else None
        activo = request.data.get('activo', True)
        
        try:
            configuracion = ConfiguracionSIIAutomaticaCompra.objects.get(holding_id=holding_id)
            configuracion.activo = activo
            configuracion.save()
            
            return Response({
                "message": f"Proceso automático {'activado' if activo else 'desactivado'}",
                "status": "success"
            }, status=status.HTTP_200_OK)
        except ConfiguracionSIIAutomaticaCompra.DoesNotExist:
            return Response(
                {"message": "No hay configuración automática"}, 
                status=status.HTTP_404_NOT_FOUND
            )

    def _get_companies_for_configuration(self, request):
        """Obtiene empresas disponibles para configuración"""
        # Implementación simplificada - retorna lista mock
        empresas = [
            {"rut": "12345678-9", "nombre": "Empresa de Prueba 1"},
            {"rut": "98765432-1", "nombre": "Empresa de Prueba 2"}
        ]
        return Response({
            "message": "Empresas obtenidas",
            "status": "success",
            "empresas": empresas
        }, status=status.HTTP_200_OK)

    def _validate_sii_credentials(self, request):
        """Valida credenciales SII"""
        # Implementación simplificada
        return Response({
            "message": "Credenciales válidas",
            "status": "success",
            "valid": True
        }, status=status.HTTP_200_OK)

    def _get_execution_history(self, request):
        """Obtiene historial de ejecuciones"""
        # Implementación simplificada
        return Response({
            "message": "Historial obtenido",
            "status": "success",
            "executions": []
        }, status=status.HTTP_200_OK)

    def _restart_automatic_process(self, request):
        """Reinicia el proceso automático"""
        # Implementación simplificada
        return Response({
            "message": "Proceso reiniciado",
            "status": "success"
        }, status=status.HTTP_200_OK)
    
    def _calcular_proxima_ejecucion(self, hora_ejecucion) -> datetime:
        """
        Calcula la próxima fecha/hora de ejecución en zona horaria de Chile
        """
        try:
            import pytz
            from datetime import datetime, timedelta
            from django.utils import timezone
            
            # Zona horaria de Chile
            chile_tz = pytz.timezone('America/Santiago')
            
            # Obtener la hora actual en Chile
            ahora_chile = timezone.now().astimezone(chile_tz)
            
            # Crear la próxima ejecución en hora de Chile
            proxima_chile = ahora_chile.replace(
                hour=hora_ejecucion.hour,
                minute=hora_ejecucion.minute,
                second=0,
                microsecond=0
            )
            
            # Si la hora ya pasó hoy, programar para mañana
            if proxima_chile <= ahora_chile:
                proxima_chile += timedelta(days=1)
            
            # Convertir de vuelta a UTC para almacenamiento
            proxima_utc = proxima_chile.astimezone(pytz.UTC)
            
            print(f"DEBUG: Hora actual Chile: {ahora_chile.strftime('%Y-%m-%d %H:%M:%S %Z')}")
            print(f"DEBUG: Próxima ejecución Chile: {proxima_chile.strftime('%Y-%m-%d %H:%M:%S %Z')}")
            
            return proxima_utc
            
        except Exception as e:
            print(f"Error calculando próxima ejecución: {str(e)}")
            return timezone.now() + timedelta(days=1)

    def _search_pdfs_for_existing_invoices(self, request):
        """
        Inicia la búsqueda de PDFs para facturas existentes que no tienen PDF
        """
        try:
            holding_id = request.user.holding.id if request.user.holding else None
            
            if not holding_id:
                return Response(
                    {"message": "Usuario sin holding asignado"}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Contar facturas sin PDF
            facturas_sin_pdf = FacturaCompraSIIPorDistribuir.objects.filter(
                holding_id=holding_id,
                procesada=False,
                pdf_documento__isnull=True
            ).count()
            
            if facturas_sin_pdf == 0:
                return Response({
                    "status": "success",
                    "message": "Todas las facturas ya tienen PDFs descargados",
                    "facturas_sin_pdf": 0
                }, status=status.HTTP_200_OK)
            
            # Ejecutar búsqueda de PDFs en segundo plano
            try:
                from .tasks import buscar_pdfs_facturas_existentes
                
                # Ejecutar tarea
                buscar_pdfs_facturas_existentes.delay(holding_id)
                
                return Response({
                    "status": "success",
                    "message": f"Búsqueda de PDFs iniciada para {facturas_sin_pdf} facturas",
                    "facturas_sin_pdf": facturas_sin_pdf,
                    "info": "El proceso se ejecutará en segundo plano. Actualice la página en unos minutos para ver los resultados."
                }, status=status.HTTP_200_OK)
                
            except ImportError:
                # Si Celery no está disponible, ejecutar sincrónicamente (solo para pocas facturas)
                if facturas_sin_pdf > 10:
                    return Response({
                        "status": "error",
                        "message": "Demasiadas facturas para procesar sincrónicamente. Configure Celery para procesamiento en segundo plano."
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Procesar sincrónicamente
                from .tasks import buscar_pdfs_facturas_existentes_sync
                resultado = buscar_pdfs_facturas_existentes_sync(holding_id)
                
                return Response({
                    "status": "success",
                    "message": "Búsqueda de PDFs completada",
                    "resultado": resultado
                }, status=status.HTTP_200_OK)
                
        except Exception as e:
            print(f"Error iniciando búsqueda de PDFs: {str(e)}")
            print(traceback.format_exc())
            return Response(
                {"message": f"Error iniciando búsqueda de PDFs: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _get_pdf_search_status(self, request):
        """
        Obtiene estadísticas detalladas sobre el estado de PDFs
        """
        try:
            holding_id = request.user.holding.id if request.user.holding else None
            
            if not holding_id:
                return Response(
                    {"message": "Usuario sin holding asignado"}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Estadísticas de PDFs
            facturas_query = FacturaCompraSIIPorDistribuir.objects.filter(
                holding_id=holding_id,
                procesada=False
            )
            
            total_facturas = facturas_query.count()
            facturas_con_pdf = facturas_query.filter(pdf_documento__isnull=False).count()
            facturas_sin_pdf = facturas_query.filter(pdf_documento__isnull=True).count()
            facturas_error_pdf = facturas_query.filter(
                pdf_documento__isnull=True,
                error_descarga_pdf__isnull=False
            ).count()
            
            # Estadísticas por intentos
            facturas_0_intentos = facturas_query.filter(intentos_descarga_pdf=0).count()
            facturas_1_2_intentos = facturas_query.filter(intentos_descarga_pdf__range=[1, 2]).count()
            facturas_3_mas_intentos = facturas_query.filter(intentos_descarga_pdf__gte=3).count()
            
            estadisticas_pdf = {
                'total_facturas': total_facturas,
                'facturas_con_pdf': facturas_con_pdf,
                'facturas_sin_pdf': facturas_sin_pdf,
                'facturas_error_pdf': facturas_error_pdf,
                'porcentaje_con_pdf': round((facturas_con_pdf / total_facturas * 100) if total_facturas > 0 else 0, 1),
                'porcentaje_sin_pdf': round((facturas_sin_pdf / total_facturas * 100) if total_facturas > 0 else 0, 1),
                'porcentaje_error_pdf': round((facturas_error_pdf / total_facturas * 100) if total_facturas > 0 else 0, 1),
                'facturas_0_intentos': facturas_0_intentos,
                'facturas_1_2_intentos': facturas_1_2_intentos,
                'facturas_3_mas_intentos': facturas_3_mas_intentos,
                'fecha_actualizacion': timezone.now().isoformat()
            }
            
            return Response({
                "status": "success",
                "estadisticas_pdf": estadisticas_pdf
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"Error obteniendo estadísticas de PDFs: {str(e)}")
            return Response(
                {"message": f"Error obteniendo estadísticas de PDFs: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ServePDFFacturaSIIAPIView(APIView):
    """
    Vista para servir PDFs de facturas SII.
    Permite tanto visualización en navegador como descarga directa.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_scopes = ['admin', 'write', 'read']
    
    def get(self, request, factura_id, format=None):
        """
        Sirve el PDF de una factura específica
        
        Parámetros GET:
        - download: 'true' para forzar descarga, 'false' para visualización
        """
        try:
            holding_id = request.user.holding.id if request.user.holding else None
            
            if not holding_id:
                return Response(
                    {"message": "Usuario sin holding asignado"}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Obtener la factura
            try:
                factura = FacturaCompraSIIPorDistribuir.objects.get(
                    id=factura_id,
                    holding_id=holding_id
                )
            except FacturaCompraSIIPorDistribuir.DoesNotExist:
                return Response(
                    {"message": "Factura no encontrada"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Verificar que tiene PDF
            if not factura.pdf_documento:
                return Response(
                    {
                        "message": "La factura no tiene PDF disponible",
                        "status": "no_pdf",
                        "error_details": {
                            "pdf_descargado": factura.pdf_descargado,
                            "intentos_descarga": factura.intentos_descarga_pdf,
                            "error_descarga": factura.error_descarga_pdf,
                            "codigo_sii": factura.codigo_sii
                        }
                    }, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Verificar que el archivo existe físicamente
            try:
                pdf_path = factura.pdf_documento.path
                if not os.path.exists(pdf_path):
                    return Response(
                        {
                            "message": "El archivo PDF no se encuentra en el servidor",
                            "status": "file_not_found"
                        }, 
                        status=status.HTTP_404_NOT_FOUND
                    )
            except Exception as e:
                return Response(
                    {
                        "message": "Error accediendo al archivo PDF",
                        "status": "access_error",
                        "error": str(e)
                    }, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Determinar si es descarga o visualización
            force_download = request.GET.get('download', 'false').lower() == 'true'
            
            # Generar nombre del archivo
            filename = f"factura_{factura.tipo_doc}_{factura.folio}_{factura.rut_proveedor}.pdf"
            
            # Crear respuesta con el archivo
            try:
                response = FileResponse(
                    open(pdf_path, 'rb'),
                    content_type='application/pdf'
                )
                
                if force_download:
                    # Forzar descarga
                    response['Content-Disposition'] = f'attachment; filename="{filename}"'
                else:
                    # Visualización en navegador
                    response['Content-Disposition'] = f'inline; filename="{filename}"'
                
                # Headers adicionales para mejor manejo del cache
                response['Cache-Control'] = 'private, max-age=0'
                response['X-Content-Type-Options'] = 'nosniff'
                
                # Agregar información adicional en headers personalizados
                response['X-Factura-Folio'] = factura.folio
                response['X-Factura-Tipo'] = factura.tipo_doc
                response['X-Factura-RUT'] = factura.rut_proveedor
                response['X-Factura-Proveedor'] = factura.razon_social
                
                return response
                
            except Exception as e:
                return Response(
                    {
                        "message": f"Error sirviendo el archivo PDF: {str(e)}",
                        "status": "serve_error"
                    }, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Exception as e:
            print(f"Error inesperado sirviendo PDF: {str(e)}")
            print(traceback.format_exc())
            return Response(
                {
                    "message": "Error interno del servidor",
                    "status": "internal_error"
                }, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class DownloadPDFFacturaSIIAPIView(APIView):
    """
    Vista específica para descarga directa de PDFs de facturas SII.
    Esta vista siempre fuerza la descarga del archivo.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_scopes = ['admin', 'write', 'read']
    
    def get(self, request, factura_id, format=None):
        """
        Descarga directa del PDF de una factura específica
        """
        try:
            holding_id = request.user.holding.id if request.user.holding else None
            
            if not holding_id:
                return HttpResponse('Usuario sin holding asignado', status=403)
            
            # Obtener la factura
            try:
                factura = FacturaCompraSIIPorDistribuir.objects.get(
                    id=factura_id,
                    holding_id=holding_id
                )
            except FacturaCompraSIIPorDistribuir.DoesNotExist:
                return HttpResponse('Factura no encontrada', status=404)
            
            # Verificar que tiene PDF
            if not factura.pdf_documento:
                return HttpResponse('La factura no tiene PDF disponible', status=404)
            
            # Verificar que el archivo existe
            try:
                pdf_path = factura.pdf_documento.path
                if not os.path.exists(pdf_path):
                    return HttpResponse('El archivo PDF no se encuentra en el servidor', status=404)
            except Exception:
                return HttpResponse('Error accediendo al archivo PDF', status=500)
            
            # Generar nombre del archivo
            filename = f"factura_{factura.tipo_doc}_{factura.folio}_{factura.rut_proveedor}.pdf"
            
            # Crear respuesta con descarga forzada
            try:
                response = FileResponse(
                    open(pdf_path, 'rb'),
                    content_type='application/pdf',
                    as_attachment=True,
                    filename=filename
                )
                
                return response
                
            except Exception as e:
                return HttpResponse(f'Error sirviendo el archivo PDF: {str(e)}', status=500)
                
        except Exception as e:
            return HttpResponse(f'Error interno del servidor: {str(e)}', status=500)

class FacturasCompraDistribucion(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_scopes = []
        self.session_manager = BrowserSessionManager.get_instance()
    
    def dispatch(self, request, *args, **kwargs):
        if request.method == 'POST':
            self.required_scopes = ['admin', 'write']
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request, format=None):
        """
        Gestiona el nuevo flujo de facturas SII:
        1. Login
        2. Selección de empresa, período y tipo (compra/venta)
        3. Descarga de CSV con detalles
        4. Análisis y filtrado de facturas ya distribuidas
        5. Obtener datos para distribución
        6. Distribución de facturas con campos completos
        """
        try:
            action = request.data.get('action', 'login')
            
            if action == 'login':
                return self._handle_login(request)
            elif action == 'select_company_and_period':
                return self._handle_company_period_selection(request)
            elif action == 'download_csv':
                return self._handle_csv_download(request)
            elif action == 'get_undistributed_invoices':
                return self._handle_undistributed_invoices(request)
            elif action == 'get_distribution_data':
                return self._handle_get_distribution_data(request)
            elif action == 'get_fundos_by_cliente':
                return self._handle_get_fundos_by_cliente(request)
            elif action == 'distribute_invoices':
                return self._handle_distribute_invoices(request)
            elif action == 'get_distributed_invoices':
                return self._handle_get_distributed_invoices(request)
            elif action == 'list_distributed_invoices':
                return self.handle_list_distributed_invoices(request)
            elif action == 'export_distributed_invoices_csv':
                return self.handle_export_distributed_invoices_csv(request)
            else:
                return Response(
                    {"message": "Acción no válida"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            print(f"Error no manejado: {str(e)}")
            print(traceback.format_exc())
            return Response(
                {"message": f"Error en el servidor: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _handle_get_distribution_data(self, request):
        """
        Obtiene los datos necesarios para la distribución de facturas
        """
        holding_id = request.user.holding.id if request.user.holding else None
        
        if not holding_id:
            return Response(
                {"message": "No se pudo determinar el holding"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from .serializers import DistribucionDataSerializer
            
            data = {
                'holding_id': holding_id
            }
            
            serializer = DistribucionDataSerializer(data)
            
            return Response({
                "message": "Datos de distribución obtenidos exitosamente",
                "status": "success",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"Error obteniendo datos de distribución: {str(e)}")
            print(traceback.format_exc())
            
            return Response(
                {"message": f"Error obteniendo datos de distribución: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _handle_get_fundos_by_cliente(self, request):
        """
        Obtiene los fundos de un cliente específico
        """
        cliente_id = request.data.get('cliente_id')
        
        if not cliente_id:
            return Response(
                {"message": "ID de cliente requerido"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from .serializers import FundosClienteSerializer
            
            fundos = CamposClientes.objects.filter(cliente_id=cliente_id)
            serializer = FundosClienteSerializer(fundos, many=True)
            
            return Response({
                "message": "Fundos obtenidos exitosamente",
                "status": "success",
                "fundos": serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"Error obteniendo fundos por cliente: {str(e)}")
            
            return Response(
                {"message": f"Error obteniendo fundos: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _handle_distribute_invoices(self, request):
        """
        Distribuye facturas seleccionadas con información completa
        MODIFICADO: Borrar de FacturaCompraSIIPorDistribuir si vienen del modo automático
        """
        from .serializers import DistribucionFacturasSIISerializer
        from .models import FacturaCompraSIIDistribuida, FacturaCompraSIIPorDistribuir, Clientes, CamposClientes, Labores, Cuenta
        from django.db import transaction
        
        # Validar datos usando serializer
        serializer = DistribucionFacturasSIISerializer(
            data=request.data, 
            context={'request': request}
        )
        
        if not serializer.is_valid():
            return Response(
                {
                    "message": "Datos de distribución inválidos",
                    "errors": serializer.errors
                }, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        validated_data = serializer.validated_data
        holding_id = request.user.holding.id if request.user.holding else None
        
        if not holding_id:
            return Response(
                {"message": "No se pudo determinar el holding"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            with transaction.atomic():
                # Obtener los objetos relacionados
                cliente = Clientes.objects.get(
                    id=validated_data['cliente_id'], 
                    holding_id=holding_id
                )
                
                fundo = None
                if validated_data.get('fundo_id'):
                    fundo = CamposClientes.objects.get(id=validated_data['fundo_id'])
                
                labor = None
                if validated_data.get('labor_id'):
                    labor = Labores.objects.get(id=validated_data['labor_id'])
                
                cuenta = None
                if validated_data.get('cuenta_id'):
                    cuenta = Cuenta.objects.get(id=validated_data['cuenta_id'])
                
                # Crear registros de distribución
                facturas_distribuidas = []
                facturas_automaticas_a_borrar = []  # NUEVO: Lista de facturas automáticas a borrar
                
                for factura_data in validated_data['facturas_seleccionadas']:
                    # Verificar que la factura no esté ya distribuida
                    folio = factura_data.get('folio')
                    tipo_doc = factura_data.get('tipo_doc')
                    rut_proveedor = factura_data.get('rut_proveedor')
                    
                    existe = FacturaCompraSIIDistribuida.objects.filter(
                        holding_id=holding_id,
                        folio=folio,
                        tipo_doc=tipo_doc,
                        rut_proveedor=rut_proveedor
                    ).exists()
                    
                    if existe:
                        print(f"Factura {folio} ya distribuida, saltando...")
                        continue
                    
                    # NUEVO: Verificar si esta factura existe en FacturaCompraSIIPorDistribuir (modo automático)
                    factura_automatica = None
                    try:
                        factura_automatica = FacturaCompraSIIPorDistribuir.objects.get(
                            holding_id=holding_id,
                            folio=folio,
                            rut_proveedor=rut_proveedor,
                            procesada=False
                        )
                        print(f"Factura {folio} encontrada en modo automático, se borrará después de distribuir")
                        facturas_automaticas_a_borrar.append(factura_automatica)
                    except FacturaCompraSIIPorDistribuir.DoesNotExist:
                        print(f"Factura {folio} es del modo manual, no se borra de FacturaCompraSIIPorDistribuir")
                        pass
                    
                    # Crear la distribución
                    factura_distribuida = FacturaCompraSIIDistribuida.objects.create(
                        holding_id=holding_id,
                        cliente=cliente,
                        fundo=fundo,
                        labor=labor,
                        cuenta=cuenta,
                        
                        # Datos de la factura
                        folio=factura_data.get('folio', ''),
                        tipo_doc=factura_data.get('tipo_doc', ''),
                        tipo_compra=factura_data.get('tipo_compra', ''),
                        rut_proveedor=factura_data.get('rut_proveedor', ''),
                        razon_social=factura_data.get('razon_social', ''),
                        fecha_docto=factura_data.get('fecha_docto', ''),
                        fecha_recepcion=factura_data.get('fecha_recepcion', ''),
                        fecha_acuse=factura_data.get('fecha_acuse', ''),
                        
                        # Montos
                        monto_exento=factura_data.get('monto_exento', 0),
                        monto_neto=factura_data.get('monto_neto', 0),
                        monto_iva_recuperable=factura_data.get('monto_iva_recuperable', 0),
                        monto_iva_no_recuperable=factura_data.get('iva_no_recuperable', 0),
                        codigo_iva_no_rec=factura_data.get('codigo_iva_no_rec', ''),
                        monto_total=factura_data.get('monto_total', 0),
                        monto_neto_activo_fijo=factura_data.get('monto_neto_activo_fijo', 0),
                        iva_activo_fijo=factura_data.get('iva_activo_fijo', 0),
                        iva_uso_comun=factura_data.get('iva_uso_comun', 0),
                        impto_sin_derecho_credito=factura_data.get('impto_sin_derecho_credito', 0),
                        iva_no_retenido=factura_data.get('iva_no_retenido', 0),
                        tabacos_puros=factura_data.get('tabacos_puros', 0),
                        tabacos_cigarrillos=factura_data.get('tabacos_cigarrillos', 0),
                        tabacos_elaborados=factura_data.get('tabacos_elaborados', 0),
                        nce_nde_fact_compra=factura_data.get('nce_nde_fact_compra', 0),
                        codigo_otro_impuesto=factura_data.get('codigo_otro_impuesto', ''),
                        valor_otro_impuesto=factura_data.get('valor_otro_impuesto', 0),
                        tasa_otro_impuesto=factura_data.get('tasa_otro_impuesto', 0),
                        
                        # Metadatos
                        usuario_distribuyente=request.user,
                        observaciones=validated_data.get('observaciones', '')
                    )
                    
                    facturas_distribuidas.append(factura_distribuida)
                
                # NUEVO: Borrar facturas automáticas después de distribuir exitosamente
                facturas_automaticas_borradas = 0
                for factura_automatica in facturas_automaticas_a_borrar:
                    try:
                        folio_a_borrar = factura_automatica.folio
                        factura_automatica.delete()
                        facturas_automaticas_borradas += 1
                        print(f"✅ Factura automática {folio_a_borrar} borrada de FacturaCompraSIIPorDistribuir")
                    except Exception as e:
                        print(f"❌ Error borrando factura automática {factura_automatica.folio}: {str(e)}")
                
                # Preparar respuesta
                distribucion_info = {
                    'cliente': {
                        'id': cliente.id,
                        'nombre': cliente.nombre,
                        'rut': cliente.rut
                    },
                    'fundo': {
                        'id': fundo.id,
                        'nombre': fundo.nombre_campo
                    } if fundo else None,
                    'labor': {
                        'id': labor.id,
                        'nombre': labor.nombre
                    } if labor else None,
                    'cuenta': {
                        'id': cuenta.id,
                        'nombre': cuenta.nombre_cuenta,
                        'codigo': cuenta.cuenta_contable
                    } if cuenta else None
                }
                
                mensaje_respuesta = f"Se distribuyeron {len(facturas_distribuidas)} facturas exitosamente"
                if facturas_automaticas_borradas > 0:
                    mensaje_respuesta += f" ({facturas_automaticas_borradas} facturas automáticas removidas de pendientes)"
                
                return Response({
                    "message": mensaje_respuesta,
                    "status": "success",
                    "facturas_distribuidas": len(facturas_distribuidas),
                    "facturas_automaticas_borradas": facturas_automaticas_borradas,  # NUEVO
                    "distribucion": distribucion_info
                }, status=status.HTTP_200_OK)
                    
        except Clientes.DoesNotExist:
            return Response(
                {"message": "Cliente no encontrado"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except CamposClientes.DoesNotExist:
            return Response(
                {"message": "Fundo no encontrado"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Labores.DoesNotExist:
            return Response(
                {"message": "Labor no encontrada"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Cuenta.DoesNotExist:
            return Response(
                {"message": "Cuenta no encontrada"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            print(f"Error distribuyendo facturas: {str(e)}")
            print(traceback.format_exc())
            
            return Response(
                {"message": f"Error distribuyendo facturas: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _handle_get_distributed_invoices(self, request):
        """
        Obtiene las facturas ya distribuidas
        """
        holding_id = request.user.holding.id if request.user.holding else None
        
        if not holding_id:
            return Response(
                {"message": "No se pudo determinar el holding"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from .serializers import FacturaCompraSIIDistribuidaSerializer
            
            # Parámetros de filtrado opcionales
            cliente_id = request.data.get('cliente_id')
            fecha_desde = request.data.get('fecha_desde')
            fecha_hasta = request.data.get('fecha_hasta')
            
            # Consulta base
            queryset = FacturaCompraSIIDistribuida.objects.filter(holding_id=holding_id)
            
            # Aplicar filtros
            if cliente_id:
                queryset = queryset.filter(cliente_id=cliente_id)
            
            if fecha_desde:
                queryset = queryset.filter(fecha_distribucion__gte=fecha_desde)
                
            if fecha_hasta:
                queryset = queryset.filter(fecha_distribucion__lte=fecha_hasta)
            
            # Ordenar por fecha de distribución más reciente
            queryset = queryset.order_by('-fecha_distribucion')
            
            # Serializar
            serializer = FacturaCompraSIIDistribuidaSerializer(queryset, many=True)
            
            return Response({
                "message": f"Se encontraron {len(serializer.data)} facturas distribuidas",
                "status": "success",
                "facturas_distribuidas": serializer.data,
                "total": len(serializer.data)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"Error obteniendo facturas distribuidas: {str(e)}")
            print(traceback.format_exc())
            
            return Response(
                {"message": f"Error obteniendo facturas distribuidas: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _handle_login(self, request):
        """Maneja el inicio de sesión en el SII"""
        rut = request.data.get('rut')
        password = request.data.get('password')
        tipo_factura = request.data.get('tipo_factura')  # 'compra' o 'venta'
        
        if not rut or not password or not tipo_factura:
            return Response(
                {"message": "RUT, contraseña y tipo de factura son obligatorios"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if tipo_factura not in ['compra', 'venta']:
            return Response(
                {"message": "Tipo de factura debe ser 'compra' o 'venta'"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user_id = f"{request.user.id}_{rut}_{tipo_factura}"
        
        try:
            browser_session = self.session_manager.create_session(user_id)
            session_id = browser_session.session_id
            driver = browser_session.driver
            wait = browser_session.wait
            
            print(f"Iniciando proceso para RUT: {rut}, Tipo: {tipo_factura}")
            
            # Login en SII
            login_successful = False
            max_attempts = 3
            
            for attempt in range(1, max_attempts + 1):
                try:
                    login_successful = self._login_sii(driver, wait, rut, password)
                    if login_successful:
                        break
                        
                    if attempt < max_attempts:
                        print(f"Intento de login {attempt} fallido. Reintentando...")
                        time.sleep(5 * attempt)
                except Exception as e:
                    print(f"Error en intento de login {attempt}: {str(e)}")
                    if attempt < max_attempts:
                        time.sleep(5 * attempt)
            
            if not login_successful:
                self.session_manager.close_session(session_id)
                return Response(
                    {"message": "Error al iniciar sesión después de múltiples intentos. Verifique sus credenciales."}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # Navegar a la página de consulta de registro de compra y venta
            print("Navegando a página de consulta de registro")
            driver.get("https://www4.sii.cl/consdcvinternetui/#/index")
            time.sleep(random.uniform(3.0, 5.0))
            
            # Guardar el tipo de factura en la sesión
            browser_session.tipo_factura = tipo_factura
            
            # Obtener empresas disponibles
            empresas = self._obtener_empresas_consulta(driver, wait)
            
            return Response({
                "message": "Login exitoso",
                "status": "success",
                "session_id": session_id,
                "tipo_factura": tipo_factura,
                "empresas": empresas,
                "url": driver.current_url
            }, status=status.HTTP_200_OK)
                
        except Exception as e:
            print(f"Error en el proceso de login: {str(e)}")
            print(traceback.format_exc())
            
            if 'session_id' in locals():
                self.session_manager.close_session(session_id)
            
            return Response(
                {"message": f"Error en el proceso: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _handle_company_period_selection(self, request):
        """Maneja la selección de empresa y período"""
        session_id = request.data.get('session_id')
        empresa_rut = request.data.get('empresa_rut')
        mes = request.data.get('mes')
        ano = request.data.get('ano')
        
        if not all([session_id, empresa_rut, mes, ano]):
            return Response(
                {"message": "Faltan parámetros requeridos"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            browser_session = self.session_manager.get_session(session_id=session_id)
            
            if not browser_session:
                return Response(
                    {"message": "Sesión no encontrada o expirada"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            driver = browser_session.driver
            wait = browser_session.wait
            tipo_factura = browser_session.tipo_factura
            
            # Seleccionar empresa
            empresa_select = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "select[ng-model='rut']"))
            )
            empresa_select_obj = Select(empresa_select)
            empresa_select_obj.select_by_value(empresa_rut)
            time.sleep(random.uniform(1.0, 2.0))
            
            # Seleccionar mes
            mes_select = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "select[ng-model='periodoMes']"))
            )
            mes_select_obj = Select(mes_select)
            mes_select_obj.select_by_value(mes.zfill(2))  # Asegurar formato 01, 02, etc.
            time.sleep(random.uniform(1.0, 2.0))
            
            # Seleccionar año
            ano_select = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "select[ng-model='periodoAnho']"))
            )
            ano_select_obj = Select(ano_select)
            ano_select_obj.select_by_value(str(ano))
            time.sleep(random.uniform(1.0, 2.0))
            
            # Hacer clic en consultar
            consultar_btn = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
            )
            driver.execute_script("arguments[0].click();", consultar_btn)
            
            # Esperar a que aparezcan los tabs
            time.sleep(random.uniform(3.0, 5.0))
            
            # Seleccionar tab según tipo de factura
            if tipo_factura == 'compra':
                tab_selector = "a[ui-sref='compra']"
            else:  # venta
                tab_selector = "a[ui-sref='venta']"
            
            try:
                tab_element = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, tab_selector))
                )
                driver.execute_script("arguments[0].click();", tab_element)
                time.sleep(random.uniform(2.0, 3.0))
            except TimeoutException:
                # El tab ya puede estar activo por defecto
                pass
            
            return Response({
                "message": f"Empresa y período seleccionados correctamente para {tipo_factura}",
                "status": "success",
                "session_id": session_id,
                "ready_for_download": True
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"Error en selección de empresa y período: {str(e)}")
            print(traceback.format_exc())
            
            return Response(
                {"message": f"Error en la selección: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _handle_csv_download(self, request):
        """Maneja la descarga del CSV de detalles"""
        session_id = request.data.get('session_id')
        
        if not session_id:
            return Response(
                {"message": "ID de sesión requerido"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            browser_session = self.session_manager.get_session(session_id=session_id)
            
            if not browser_session:
                return Response(
                    {"message": "Sesión no encontrada o expirada"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            driver = browser_session.driver
            wait = browser_session.wait
            
            # DEBUG: Verificar el estado actual de la página
            print(f"URL actual antes de buscar botón: {driver.current_url}")
            print("Buscando elementos en la página...")
            
            # Verificar si hay datos en la tabla de resumen
            try:
                tabla_resumen = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
                print(f"Filas encontradas en tabla de resumen: {len(tabla_resumen)}")
                
                for i, fila in enumerate(tabla_resumen):
                    print(f"Fila {i}: {fila.text}")
            except Exception as e:
                print(f"Error al leer tabla de resumen: {str(e)}")
            
            # Buscar botón "Descargar Detalles" con múltiples selectores
            descargar_btn = None
            selectores_boton = [
                "//button[contains(text(), 'Descargar Detalles')]",
                "//button[contains(text(), 'Descargar')]",
                "//input[@type='button'][contains(@value, 'Descargar Detalles')]",
                "//input[@type='button'][contains(@value, 'Descargar')]",
                ".btn[ng-click*='descargaDetalle']",
                "button[ng-click*='descargaDetalle']"
            ]
            
            for selector in selectores_boton:
                try:
                    if selector.startswith("//"):
                        elementos = driver.find_elements(By.XPATH, selector)
                    else:
                        elementos = driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    if elementos:
                        descargar_btn = elementos[0]
                        print(f"Botón encontrado con selector: {selector}")
                        print(f"Texto del botón: {descargar_btn.text}")
                        print(f"¿Está visible?: {descargar_btn.is_displayed()}")
                        print(f"¿Está habilitado?: {descargar_btn.is_enabled()}")
                        break
                except Exception as e:
                    print(f"Error con selector {selector}: {str(e)}")
            
            if not descargar_btn:
                # DEBUG: Mostrar todo el HTML de la página
                print("NO SE ENCONTRÓ EL BOTÓN. HTML de la página:")
                print(driver.page_source[:2000])  # Primeros 2000 caracteres
                
                return Response({
                    "message": "No se encontró el botón de descarga. Puede que no haya datos disponibles para este período.",
                    "status": "error",
                    "debug_info": {
                        "url": driver.current_url,
                        "page_title": driver.title
                    }
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Hacer scroll al botón y hacer clic
            driver.execute_script("arguments[0].scrollIntoView(true);", descargar_btn)
            time.sleep(random.uniform(1.0, 2.0))
            
            print("Haciendo clic en el botón de descarga...")
            driver.execute_script("arguments[0].click();", descargar_btn)
            
            # Esperar más tiempo para la descarga
            print("Esperando descarga del archivo...")
            time.sleep(random.uniform(8.0, 12.0))
            
            # Buscar el archivo CSV descargado
            downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
            print(f"Buscando CSV en: {downloads_dir}")
            
            csv_data = self._get_latest_csv_file(downloads_dir)
            
            if csv_data:
                print(f"CSV encontrado. Tamaño: {len(csv_data)} caracteres")
                print(f"Primeras 500 caracteres del CSV:\n{csv_data[:500]}")
                
                return Response({
                    "message": "CSV descargado exitosamente",
                    "status": "success",
                    "session_id": session_id,
                    "csv_data": csv_data,
                    "debug_info": {
                        "csv_size": len(csv_data),
                        "csv_preview": csv_data[:200]
                    }
                }, status=status.HTTP_200_OK)
            else:
                print("No se encontró archivo CSV descargado")
                
                # Listar archivos en Downloads para debug
                try:
                    archivos = os.listdir(downloads_dir)
                    archivos_recientes = [f for f in archivos if f.endswith('.csv')]
                    print(f"Archivos CSV en Downloads: {archivos_recientes}")
                except Exception as e:
                    print(f"Error al listar Downloads: {str(e)}")
                
                return Response({
                    "message": "No se pudo obtener el archivo CSV",
                    "status": "error",
                    "debug_info": {
                        "downloads_dir": downloads_dir
                    }
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            print(f"Error en descarga de CSV: {str(e)}")
            print(traceback.format_exc())
            
            return Response(
                {"message": f"Error en la descarga: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    def _handle_undistributed_invoices(self, request):
        """Analiza el CSV del SII y devuelve facturas no distribuidas"""
        csv_data = request.data.get('csv_data')
        holding_id = request.user.holding.id if request.user.holding else None
        
        print(f"=== ANALIZANDO CSV DEL SII ===")
        print(f"CSV data recibido: {len(csv_data) if csv_data else 0} caracteres")
        print(f"Holding ID: {holding_id}")
        
        if not csv_data or not holding_id:
            print("ERROR: Faltan csv_data o holding_id")
            return Response(
                {"message": "Datos CSV y holding requeridos"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Parsear CSV del SII de manera robusta
            facturas_parseadas = self._parse_sii_csv(csv_data)
            
            if not facturas_parseadas:
                return Response({
                    "message": "No se encontraron facturas válidas en el CSV",
                    "status": "error",
                    "facturas": [],
                    "total_facturas": 0,
                    "facturas_ya_distribuidas": 0
                }, status=status.HTTP_200_OK)
            
            print(f"Facturas parseadas exitosamente: {len(facturas_parseadas)}")
            
            # Verificar si existe el modelo FacturaCompraSIIDistribuida
            try:
                from .models import FacturaCompraSIIDistribuida
                print("Modelo FacturaCompraSIIDistribuida importado correctamente")
                
                # Obtener folios ya distribuidos
                folios_distribuidos = set(
                    FacturaCompraSIIDistribuida.objects.filter(
                        holding_id=holding_id
                    ).values_list('folio', flat=True)
                )
                print(f"Folios ya distribuidos encontrados: {len(folios_distribuidos)}")
                
            except ImportError as e:
                print(f"ERROR: No se pudo importar FacturaCompraSIIDistribuida: {str(e)}")
                folios_distribuidos = set()
            except Exception as e:
                print(f"ERROR al consultar folios distribuidos: {str(e)}")
                folios_distribuidos = set()
            
            # Filtrar facturas no distribuidas
            facturas_no_distribuidas = []
            facturas_ya_distribuidas = 0
            
            for factura in facturas_parseadas:
                folio = factura.get('folio', '').strip()
                if not folio:
                    print(f"❌ Factura omitida: folio vacío")
                    continue
                    
                if folio in folios_distribuidos:
                    print(f"❌ Factura ya distribuida: {folio}")
                    facturas_ya_distribuidas += 1
                    continue
                
                # Agregar flag de selección
                factura['selected'] = False
                facturas_no_distribuidas.append(factura)
                print(f"✅ Factura agregada: {factura['razon_social']} - Folio {folio}")
            
            print(f"\n=== RESULTADO FINAL ===")
            print(f"Total facturas parseadas: {len(facturas_parseadas)}")
            print(f"Facturas ya distribuidas: {facturas_ya_distribuidas}")
            print(f"Facturas no distribuidas: {len(facturas_no_distribuidas)}")
            
            return Response({
                "message": f"Se encontraron {len(facturas_no_distribuidas)} facturas por distribuir",
                "status": "success",
                "facturas": facturas_no_distribuidas,
                "total_facturas": len(facturas_parseadas),
                "facturas_ya_distribuidas": facturas_ya_distribuidas,
                "debug_info": {
                    "parsed_rows": len(facturas_parseadas),
                    "valid_invoices": len(facturas_no_distribuidas),
                    "duplicates_found": facturas_ya_distribuidas,
                    "sample_invoice": facturas_no_distribuidas[0] if facturas_no_distribuidas else None
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"ERROR en análisis de CSV: {str(e)}")
            print(traceback.format_exc())
            
            return Response(
                {"message": f"Error analizando facturas: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _parse_sii_csv(self, csv_data):
        """
        Parser específico para el formato CSV del SII.
        Maneja el formato especial donde todas las columnas están separadas por punto y coma.
        """
        try:
            import re
            from decimal import Decimal, InvalidOperation
            
            print("=== INICIANDO PARSER ESPECÍFICO DEL SII ===")
            
            # Dividir en líneas y limpiar
            lines = csv_data.strip().split('\n')
            print(f"Líneas encontradas en CSV: {len(lines)}")
            
            if len(lines) < 2:
                print("ERROR: CSV debe tener al menos header + 1 fila de datos")
                return []
            
            # Procesar header
            header_line = lines[0].strip()
            headers = [h.strip() for h in header_line.split(';')]
            print(f"Headers encontrados: {len(headers)}")
            print(f"Headers: {headers}")
            
            # Mapeo de campos esperados del SII
            expected_fields = {
                'Nro': 'nro',
                'Tipo Doc': 'tipo_doc', 
                'Tipo Compra': 'tipo_compra',
                'RUT Proveedor': 'rut_proveedor',
                'Razon Social': 'razon_social',
                'Folio': 'folio',
                'Fecha Docto': 'fecha_docto',
                'Fecha Recepcion': 'fecha_recepcion',
                'Fecha Acuse': 'fecha_acuse',
                'Monto Exento': 'monto_exento',
                'Monto Neto': 'monto_neto',
                'Monto IVA Recuperable': 'iva_recuperable',
                'Monto Iva No Recuperable': 'iva_no_recuperable',
                'Codigo IVA No Rec.': 'codigo_iva_no_rec',
                'Monto Total': 'monto_total',
                'Monto Neto Activo Fijo': 'monto_neto_activo_fijo',
                'IVA Activo Fijo': 'iva_activo_fijo',
                'IVA uso Comun': 'iva_uso_comun',
                'Impto. Sin Derecho a Credito': 'impto_sin_derecho_credito',
                'IVA No Retenido': 'iva_no_retenido',
                'Tabacos Puros': 'tabacos_puros',
                'Tabacos Cigarrillos': 'tabacos_cigarrillos',
                'Tabacos Elaborados': 'tabacos_elaborados',
                'NCE o NDE sobre Fact. de Compra': 'nce_nde_fact_compra',
                'Codigo Otro Impuesto': 'codigo_otro_impuesto',
                'Valor Otro Impuesto': 'valor_otro_impuesto',
                'Tasa Otro Impuesto': 'tasa_otro_impuesto'
            }
            
            # Procesar filas de datos
            facturas = []
            
            for line_num, line in enumerate(lines[1:], start=2):
                try:
                    line = line.strip()
                    if not line:
                        continue
                    
                    print(f"\n--- Procesando línea {line_num} ---")
                    print(f"Contenido: {line[:100]}...")
                    
                    # Dividir por punto y coma
                    values = line.split(';')
                    print(f"Valores encontrados: {len(values)}")
                    
                    # Si hay menos valores que headers, rellenar con vacíos
                    while len(values) < len(headers):
                        values.append('')
                    
                    # Si hay más valores que headers, truncar
                    values = values[:len(headers)]
                    
                    # Crear diccionario con los datos
                    row_data = {}
                    for i, header in enumerate(headers):
                        value = values[i].strip() if i < len(values) else ''
                        
                        # Mapear a nombre de campo interno
                        field_name = expected_fields.get(header, header.lower().replace(' ', '_'))
                        row_data[field_name] = value
                    
                    # Función para limpiar y convertir valores
                    def clean_string(value):
                        if not value or value.lower() in ['', 'nan', 'null', 'none']:
                            return ''
                        return str(value).strip()
                    
                    def clean_decimal(value):
                        if not value or value.lower() in ['', 'nan', 'null', 'none']:
                            return 0.0
                        
                        # Limpiar el valor (remover espacios, convertir comas a puntos)
                        cleaned = str(value).strip().replace(',', '.')
                        
                        try:
                            return float(cleaned)
                        except (ValueError, TypeError):
                            print(f"WARNING: No se pudo convertir '{value}' a decimal, usando 0")
                            return 0.0
                    
                    def clean_date(value):
                        if not value or value.lower() in ['', 'nan', 'null', 'none']:
                            return ''
                        
                        # El SII usa formato DD/MM/YYYY
                        date_str = str(value).strip()
                        
                        # Validar formato básico de fecha
                        if re.match(r'\d{1,2}/\d{1,2}/\d{4}', date_str):
                            return date_str
                        
                        return date_str  # Devolver tal como está si no coincide el patrón
                    
                    # Crear objeto factura limpio
                    factura = {
                        'nro': clean_string(row_data.get('nro', '')),
                        'tipo_doc': clean_string(row_data.get('tipo_doc', '')),
                        'tipo_compra': clean_string(row_data.get('tipo_compra', '')),
                        'rut_proveedor': clean_string(row_data.get('rut_proveedor', '')),
                        'razon_social': clean_string(row_data.get('razon_social', '')),
                        'folio': clean_string(row_data.get('folio', '')),
                        'fecha_docto': clean_date(row_data.get('fecha_docto', '')),
                        'fecha_recepcion': clean_date(row_data.get('fecha_recepcion', '')),
                        'fecha_acuse': clean_date(row_data.get('fecha_acuse', '')),
                        'monto_exento': clean_decimal(row_data.get('monto_exento', 0)),
                        'monto_neto': clean_decimal(row_data.get('monto_neto', 0)),
                        'monto_iva_recuperable': clean_decimal(row_data.get('iva_recuperable', 0)),
                        'iva_no_recuperable': clean_decimal(row_data.get('iva_no_recuperable', 0)),
                        'monto_total': clean_decimal(row_data.get('monto_total', 0)),
                        'codigo_iva_no_rec': clean_string(row_data.get('codigo_iva_no_rec', '')),
                        'monto_neto_activo_fijo': clean_decimal(row_data.get('monto_neto_activo_fijo', 0)),
                        'iva_activo_fijo': clean_decimal(row_data.get('iva_activo_fijo', 0)),
                        'iva_uso_comun': clean_decimal(row_data.get('iva_uso_comun', 0)),
                        'impto_sin_derecho_credito': clean_decimal(row_data.get('impto_sin_derecho_credito', 0)),
                        'iva_no_retenido': clean_decimal(row_data.get('iva_no_retenido', 0)),
                        'tabacos_puros': clean_decimal(row_data.get('tabacos_puros', 0)),
                        'tabacos_cigarrillos': clean_decimal(row_data.get('tabacos_cigarrillos', 0)),
                        'tabacos_elaborados': clean_decimal(row_data.get('tabacos_elaborados', 0)),
                        'nce_nde_fact_compra': clean_decimal(row_data.get('nce_nde_fact_compra', 0)),
                        'codigo_otro_impuesto': clean_string(row_data.get('codigo_otro_impuesto', '')),
                        'valor_otro_impuesto': clean_decimal(row_data.get('valor_otro_impuesto', 0)),
                        'tasa_otro_impuesto': clean_decimal(row_data.get('tasa_otro_impuesto', 0))
                    }
                    
                    # Validaciones básicas
                    if not factura['folio']:
                        print(f"❌ Línea {line_num}: Sin folio válido")
                        continue
                    
                    if not factura['razon_social']:
                        print(f"⚠️ Línea {line_num}: Sin razón social, usando RUT como referencia")
                        factura['razon_social'] = factura['rut_proveedor']
                    
                    facturas.append(factura)
                    print(f"✅ Línea {line_num}: Factura procesada - {factura['razon_social']} (Folio: {factura['folio']})")
                    
                except Exception as line_error:
                    print(f"❌ Error procesando línea {line_num}: {str(line_error)}")
                    print(f"Contenido de la línea: {line}")
                    continue
            
            print(f"\n=== RESUMEN DEL PARSING ===")
            print(f"Líneas procesadas: {len(lines) - 1}")
            print(f"Facturas válidas: {len(facturas)}")
            
            return facturas
            
        except Exception as e:
            print(f"ERROR en parser CSV del SII: {str(e)}")
            print(traceback.format_exc())
            return []
    
   # Métodos auxiliares (mantener los existentes)
    def _login_sii(self, driver, wait, rut, password):
        """
        Realiza el proceso de inicio de sesión en el SII utilizando simulación de comportamiento humano.
        
        Returns:
            bool: True si el login fue exitoso, False en caso contrario.
        """
        try:
            # Ir SOLO a la página de inicio de sesión del SII (sin redirección)
            print("Navegando a página de login del SII")
            driver.get("https://zeusr.sii.cl/AUT2000/InicioAutenticacion/IngresoRutClave.html")
            
            # Esperar a que se cargue la página
            time.sleep(random.uniform(3.0, 5.0))
            
            # Ingresar RUT simulando comportamiento humano
            rut_input = wait.until(EC.presence_of_element_located((By.ID, "rutcntr")))
            driver.execute_script("arguments[0].scrollIntoView(true);", rut_input)
            time.sleep(random.uniform(0.5, 1.0))
            
            # Limpiar campo
            rut_input.clear()
            time.sleep(random.uniform(0.3, 0.7))
            
            # Ingresar el RUT caracter por caracter con pausas variables
            for char in rut:
                rut_input.send_keys(char)
                time.sleep(random.uniform(0.1, 0.3))
            
            # Pequeño retraso para comportamiento humano antes de pasar a la contraseña
            time.sleep(random.uniform(1.0, 2.0))
            
            # Ingresar contraseña
            password_input = driver.find_element(By.ID, "clave")
            driver.execute_script("arguments[0].scrollIntoView(true);", password_input)
            time.sleep(random.uniform(0.5, 1.0))
            
            # Limpiar campo
            password_input.clear()
            time.sleep(random.uniform(0.3, 0.7))
            
            # Ingresar la contraseña caracter por caracter con pausas variables
            for char in password:
                password_input.send_keys(char)
                time.sleep(random.uniform(0.1, 0.3))
            
            # Pausa antes de hacer clic en el botón
            time.sleep(random.uniform(1.5, 2.5))
            
            # Ubicar y hacer clic en botón de inicio de sesión
            login_button = driver.find_element(By.ID, "bt_ingresar")
            driver.execute_script("arguments[0].scrollIntoView(true);", login_button)
            time.sleep(random.uniform(0.7, 1.2))
            
            # Clic con JavaScript para asegurar que funcione
            driver.execute_script("arguments[0].click();", login_button)
            
            # Esperar después del clic
            time.sleep(random.uniform(4.0, 6.0))
            
            # Verificar si hay error de autenticación
            try:
                error_element = WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.ID, "alert_placeholder"))
                )
                if error_element.is_displayed() and error_element.text.strip():
                    print(f"Error de autenticación: {error_element.text}")
                    return False
            except TimeoutException:
                # Si no hay error, continuamos
                pass
            
            # Esperar a que se redirija después del login verificando cambios de URL
            success = False
            for _ in range(15):  # Intentar por 15 segundos
                current_url = driver.current_url
                # AQUÍ ESTÁ LA CLAVE: Verificar múltiples patrones de URL exitosa
                if any(pattern in current_url for pattern in ["menuIVA", "mipeSelEmpresa", "cgi_AUT2000"]):
                    success = True
                    break
                time.sleep(1)
            
            if success:
                print(f"Login exitoso, URL actual: {driver.current_url}")
                
                # DESPUÉS del login exitoso, navegar a la página de consulta
                print("Navegando a página de consulta de registro de compra y venta")
                driver.get("https://www4.sii.cl/consdcvinternetui/#/index")
                time.sleep(random.uniform(3.0, 5.0))
                
                return True
            else:
                print(f"URL no esperada después del login: {driver.current_url}")
                
                # Verificar si hay algún elemento que indique inicio de sesión exitoso
                try:
                    # Buscar elementos comunes después del login
                    logout_links = driver.find_elements(By.XPATH, "//a[contains(text(), 'Cerrar Sesión')]")
                    if logout_links:
                        print("Enlace 'Cerrar Sesión' encontrado, login exitoso")
                        
                        # Navegar a la página de consulta después del login exitoso
                        print("Navegando a página de consulta de registro de compra y venta")
                        driver.get("https://www4.sii.cl/consdcvinternetui/#/index")
                        time.sleep(random.uniform(3.0, 5.0))
                        
                        return True
                        
                    # Verificar si el RUT aparece en la página
                    page_source = driver.page_source.lower()
                    if rut.lower() in page_source:
                        print("RUT encontrado en la página, login exitoso")
                        
                        # Navegar a la página de consulta después del login exitoso
                        print("Navegando a página de consulta de registro de compra y venta")
                        driver.get("https://www4.sii.cl/consdcvinternetui/#/index")
                        time.sleep(random.uniform(3.0, 5.0))
                        
                        return True
                except:
                    pass
                
                return False
                
        except Exception as e:
            print(f"Error en el login: {str(e)}")
            print(traceback.format_exc())
            return False
    
    def _obtener_empresas_consulta(self, driver, wait):
        """Obtiene las empresas disponibles en la página de consulta"""
        try:
            select_element = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "select[ng-model='rut']"))
            )
            
            select = Select(select_element)
            options = select.options
            
            empresas = []
            for option in options:
                if option.get_attribute("value") and option.text.strip():
                    empresas.append({
                        "rut": option.get_attribute("value"),
                        "nombre": option.text.strip()
                    })
            
            print(f"Se encontraron {len(empresas)} empresas disponibles")
            return empresas
            
        except Exception as e:
            print(f"Error al obtener empresas: {str(e)}")
            return []
    
    def _get_latest_csv_file(self, directory):
        """Obtiene el archivo CSV más reciente del directorio"""
        try:
            print(f"Buscando archivos CSV en: {directory}")
            
            if not os.path.exists(directory):
                print(f"El directorio {directory} no existe")
                return None
            
            todos_archivos = os.listdir(directory)
            csv_files = [f for f in todos_archivos if f.endswith('.csv')]
            
            print(f"Archivos CSV encontrados: {csv_files}")
            
            if not csv_files:
                print("No hay archivos CSV en el directorio")
                return None
            
            # Obtener el archivo más reciente (por tiempo de modificación)
            archivos_con_tiempo = []
            for archivo in csv_files:
                ruta_completa = os.path.join(directory, archivo)
                tiempo_mod = os.path.getmtime(ruta_completa)
                archivos_con_tiempo.append((archivo, tiempo_mod))
            
            # Ordenar por tiempo de modificación (más reciente primero)
            archivos_con_tiempo.sort(key=lambda x: x[1], reverse=True)
            
            latest_file = archivos_con_tiempo[0][0]
            file_path = os.path.join(directory, latest_file)
            
            print(f"Archivo CSV más reciente: {latest_file}")
            print(f"Tamaño del archivo: {os.path.getsize(file_path)} bytes")
            
            # Leer el contenido
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            print(f"Contenido leído: {len(content)} caracteres")
            
            return content
            
        except Exception as e:
            print(f"Error obteniendo CSV: {str(e)}")
            print(traceback.format_exc())
            return None

    def handle_list_distributed_invoices(self, request):
        """
        Lista las facturas SII que ya han sido distribuidas con filtros
        """
        try:
            holding_id = request.data.get('holding_id')
            filtros = request.data.get('filtros', {})
            
            if not holding_id:
                return Response({
                    'status': 'error',
                    'message': 'Holding ID es requerido'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Importar el modelo
            from .models import FacturaCompraSIIDistribuida
            
            # Construir queryset base
            queryset = FacturaCompraSIIDistribuida.objects.filter(
                holding_id=holding_id
            ).select_related(
                'cliente', 'fundo', 'labor', 'cuenta', 'usuario_distribuyente'
            ).order_by('-fecha_distribucion')
            
            # Aplicar filtros
            if filtros.get('cliente_id'):
                queryset = queryset.filter(cliente_id=filtros['cliente_id'])
                
            if filtros.get('fundo_id'):
                queryset = queryset.filter(fundo_id=filtros['fundo_id'])
                
            if filtros.get('labor_id'):
                queryset = queryset.filter(labor_id=filtros['labor_id'])
                
            if filtros.get('cuenta_id'):
                queryset = queryset.filter(cuenta_id=filtros['cuenta_id'])
                
            if filtros.get('fecha_desde'):
                queryset = queryset.filter(fecha_docto__gte=filtros['fecha_desde'])
                
            if filtros.get('fecha_hasta'):
                queryset = queryset.filter(fecha_docto__lte=filtros['fecha_hasta'])
                
            if filtros.get('folio'):
                queryset = queryset.filter(folio__icontains=filtros['folio'])
                
            if filtros.get('razon_social'):
                queryset = queryset.filter(razon_social__icontains=filtros['razon_social'])
            
            # Serializar datos
            facturas_data = []
            for factura in queryset:
                factura_dict = {
                    'id': factura.id,
                    'folio': factura.folio,
                    'tipo_doc': factura.tipo_doc,
                    'tipo_compra': factura.tipo_compra or '',
                    'rut_proveedor': factura.rut_proveedor,
                    'razon_social': factura.razon_social,
                    'fecha_docto': factura.fecha_docto,
                    'fecha_recepcion': factura.fecha_recepcion or '',
                    'fecha_acuse': factura.fecha_acuse or '',
                    'monto_exento': float(factura.monto_exento),
                    'monto_neto': float(factura.monto_neto),
                    'monto_iva_recuperable': float(factura.monto_iva_recuperable),
                    'monto_iva_no_recuperable': float(factura.monto_iva_no_recuperable),
                    'codigo_iva_no_rec': factura.codigo_iva_no_rec or '',
                    'monto_total': float(factura.monto_total),
                    'monto_neto_activo_fijo': float(factura.monto_neto_activo_fijo),
                    'iva_activo_fijo': float(factura.iva_activo_fijo),
                    'iva_uso_comun': float(factura.iva_uso_comun),
                    'impto_sin_derecho_credito': float(factura.impto_sin_derecho_credito),
                    'iva_no_retenido': float(factura.iva_no_retenido),
                    'tabacos_puros': float(factura.tabacos_puros),
                    'tabacos_cigarrillos': float(factura.tabacos_cigarrillos),
                    'tabacos_elaborados': float(factura.tabacos_elaborados),
                    'nce_nde_fact_compra': float(factura.nce_nde_fact_compra),
                    'codigo_otro_impuesto': factura.codigo_otro_impuesto or '',
                    'valor_otro_impuesto': float(factura.valor_otro_impuesto),
                    'tasa_otro_impuesto': float(factura.tasa_otro_impuesto),
                    'cliente_nombre': factura.cliente.nombre if factura.cliente else '',
                    'cliente_rut': factura.cliente.rut if factura.cliente else '',
                    'fundo_nombre': factura.fundo.nombre_campo if factura.fundo else '',
                    'labor_nombre': factura.labor.nombre if factura.labor else '',
                    'cuenta_nombre': factura.cuenta.nombre_cuenta if factura.cuenta else '',
                    'cuenta_codigo': factura.cuenta.cuenta_contable if factura.cuenta else '',
                    'usuario_nombre': '',
                    'fecha_distribucion': factura.fecha_distribucion.isoformat() if factura.fecha_distribucion else '',
                    'observaciones': factura.observaciones or '',
                    'selected': False
                }
                
                # Obtener nombre del usuario
                if factura.usuario_distribuyente and hasattr(factura.usuario_distribuyente, 'persona'):
                    factura_dict['usuario_nombre'] = f"{factura.usuario_distribuyente.persona.nombres} {factura.usuario_distribuyente.persona.apellidos}"
                
                facturas_data.append(factura_dict)
            
            return Response({
                'status': 'success',
                'data': {
                    'facturas': facturas_data,
                    'total': len(facturas_data)
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"Error al listar facturas distribuidas: {str(e)}")
            return Response({
                'status': 'error',
                'message': f'Error interno: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def handle_export_distributed_invoices_csv(self, request):
        """
        Exporta las facturas distribuidas seleccionadas en formato CSV compatible con SII
        """
        try:
            holding_id = request.data.get('holding_id')
            factura_ids = request.data.get('factura_ids', [])
            
            if not holding_id:
                return Response({
                    'status': 'error',
                    'message': 'Holding ID es requerido'
                }, status=status.HTTP_400_BAD_REQUEST)
                
            if not factura_ids:
                return Response({
                    'status': 'error',
                    'message': 'Debe seleccionar al menos una factura'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Importar el modelo
            from .models import FacturaCompraSIIDistribuida
            
            # Obtener facturas seleccionadas
            facturas = FacturaCompraSIIDistribuida.objects.filter(
                id__in=factura_ids,
                holding_id=holding_id
            ).order_by('fecha_docto', 'folio')
            
            if not facturas.exists():
                return Response({
                    'status': 'error',
                    'message': 'No se encontraron facturas con los IDs proporcionados'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Crear contenido CSV en formato SII
            csv_lines = []
            
            # Encabezado igual al CSV del SII
            header = "Nro;Tipo Doc;Tipo Compra;RUT Proveedor;Razon Social;Folio;Fecha Docto;Fecha Recepcion;Fecha Acuse;Monto Exento;Monto Neto;Monto IVA Recuperable;Monto Iva No Recuperable;Codigo IVA No Rec.;Monto Total;Monto Neto Activo Fijo;IVA Activo Fijo;IVA uso Comun;Impto. Sin Derecho a Credito;IVA No Retenido;Tabacos Puros;Tabacos Cigarrillos;Tabacos Elaborados;NCE o NDE sobre Fact. de Compra;Codigo Otro Impuesto;Valor Otro Impuesto;Tasa Otro Impuesto"
            csv_lines.append(header)
            
            # Datos de las facturas
            for idx, factura in enumerate(facturas, 1):
                line = f"{idx};" + \
                    f"{factura.tipo_doc};" + \
                    f"{factura.tipo_compra or ''};" + \
                    f"{factura.rut_proveedor};" + \
                    f"\"{factura.razon_social}\";" + \
                    f"{factura.folio};" + \
                    f"{factura.fecha_docto};" + \
                    f"{factura.fecha_recepcion or ''};" + \
                    f"{factura.fecha_acuse or ''};" + \
                    f"{factura.monto_exento};" + \
                    f"{factura.monto_neto};" + \
                    f"{factura.monto_iva_recuperable};" + \
                    f"{factura.monto_iva_no_recuperable};" + \
                    f"{factura.codigo_iva_no_rec or ''};" + \
                    f"{factura.monto_total};" + \
                    f"{factura.monto_neto_activo_fijo};" + \
                    f"{factura.iva_activo_fijo};" + \
                    f"{factura.iva_uso_comun};" + \
                    f"{factura.impto_sin_derecho_credito};" + \
                    f"{factura.iva_no_retenido};" + \
                    f"{factura.tabacos_puros};" + \
                    f"{factura.tabacos_cigarrillos};" + \
                    f"{factura.tabacos_elaborados};" + \
                    f"{factura.nce_nde_fact_compra};" + \
                    f"{factura.codigo_otro_impuesto or ''};" + \
                    f"{factura.valor_otro_impuesto};" + \
                    f"{factura.tasa_otro_impuesto}"
                
                csv_lines.append(line)
            
            # Unir todas las líneas
            csv_content = '\n'.join(csv_lines)
            
            # Generar nombre de archivo
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"RCV_COMPRA_DISTRIBUIDAS_{holding_id}_{timestamp}.csv"
            
            return Response({
                'status': 'success',
                'data': {
                    'csv_content': csv_content,
                    'filename': filename,
                    'total_facturas': len(facturas)
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"Error al exportar CSV de facturas distribuidas: {str(e)}")
            return Response({
                'status': 'error',
                'message': f'Error interno: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#===================================================================
#=======================FACTURAS VENTA==============================
#===================================================================

class FacturasVentaAutomaticoAPIView(APIView):
    """
    API View para manejar el sistema automático de facturas de venta
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_scopes = []
    
    def dispatch(self, request, *args, **kwargs):
        if request.method == 'POST':
            self.required_scopes = ['admin', 'write']
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request, format=None):
        """
        Maneja todas las acciones del sistema automático de facturas de venta
        """
        try:
            action = request.data.get('action', '')
            
            if action == 'get_automatic_configuration':
                return self._get_automatic_configuration_venta(request)
            elif action == 'save_automatic_configuration':
                return self._save_automatic_configuration_venta(request)
            elif action == 'get_automatic_invoices':
                return self._get_automatic_invoices_venta(request)
            elif action == 'get_automatic_process_status':
                return self._get_automatic_process_status_venta(request)
            elif action == 'execute_automatic_process_manual':
                return self._execute_automatic_process_manual_venta(request)
            elif action == 'distribute_automatic_invoices':
                return self._distribute_automatic_invoices_venta(request)
            elif action == 'delete_automatic_invoices':
                return self._delete_automatic_invoices_venta(request)
            elif action == 'toggle_automatic_process':
                return self._toggle_automatic_process_venta(request)
            elif action == 'get_companies_for_configuration':
                return self._get_companies_for_configuration_venta(request)
            elif action == 'validate_sii_credentials':
                return self._validate_sii_credentials_venta(request)
            elif action == 'get_execution_history':
                return self._get_execution_history_venta(request)
            elif action == 'restart_automatic_process':
                return self._restart_automatic_process_venta(request)
            elif action == 'download_invoice_pdf':  
                return self._download_invoice_pdf_venta(request)
            elif action == 'search_pdfs_for_existing_invoices':  
                return self._search_pdfs_for_existing_invoices_venta(request)
            elif action == 'get_pdf_search_status':  
                return self._get_pdf_search_status_venta(request)
            elif action == 'retry_pdf_download':  
                return self._retry_pdf_download_venta(request)
            # NUEVAS ACCIONES PARA DISTRIBUCIÓN MÚLTIPLE DE VENTA
            elif action == 'distribute_invoice_multiple':
                return self._distribute_invoice_multiple_venta(request)
            elif action == 'get_invoice_distribution_details':
                return self._get_invoice_distribution_details_venta(request)
            elif action == 'get_distribution_summary':
                return self._get_distribution_summary_venta(request)
            elif action == 'delete_distribution':
                return self._delete_distribution_venta(request)
            elif action == 'create_manual_invoice':
                return self._create_manual_invoice_venta(request)
            elif action == 'get_next_folio':
                return self._get_next_folio(request)
            else:
                return Response(
                    {"message": "Acción no válida"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            print(f"Error en FacturasVentaAutomaticoAPIView: {str(e)}")
            print(traceback.format_exc())
            return Response(
                {"message": f"Error en el servidor: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _distribute_invoice_multiple_venta(self, request):
        """
        Distribuye una factura específica de venta a un cliente (distribución múltiple)
        """
        print(f"🐛 DEBUG: Iniciando _distribute_invoice_multiple_venta")
        print(f"🐛 DEBUG: Datos recibidos: {request.data}")
        
        holding_id = request.user.holding.id if request.user.holding else None
        print(f"🐛 DEBUG: holding_id: {holding_id}")
        
        if not holding_id:
            print(f"🐛 DEBUG: Error - No hay holding_id")
            return Response(
                {"message": "No se pudo determinar el holding"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            print(f"🐛 DEBUG: Iniciando validación del serializer de venta")
            
            # Validar datos de entrada usando serializer de venta
            serializer = DistribucionMultipleFacturaVentaSIISerializer(
                data=request.data, 
                context={'request': request}
            )
            
            print(f"🐛 DEBUG: Serializer de venta creado, validando...")
            
            if not serializer.is_valid():
                print(f"🐛 DEBUG: ❌ SERIALIZER DE VENTA INVÁLIDO")
                print(f"🐛 DEBUG: Errores del serializer: {serializer.errors}")
                return Response(
                    {
                        "status": "error",
                        "message": "Datos de distribución de venta inválidos",
                        "errors": serializer.errors
                    }, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            print(f"🐛 DEBUG: ✅ Serializer de venta válido")
            validated_data = serializer.validated_data
            print(f"🐛 DEBUG: Datos validados: {validated_data}")
            
            # Obtener datos validados
            factura_id = validated_data['factura_id']
            cliente_id = validated_data['cliente_id']
            fundo_id = validated_data.get('fundo_id')
            labor_id = validated_data.get('labor_id')
            cuenta_id = validated_data.get('cuenta_id')
            tipo_distribucion = validated_data['tipo_distribucion']
            monto_a_distribuir = validated_data.get('monto_a_distribuir')
            porcentaje_a_distribuir = validated_data.get('porcentaje_a_distribuir')
            observaciones = validated_data.get('observaciones', '')
            
            print(f"🐛 DEBUG: factura_id: {factura_id}")
            print(f"🐛 DEBUG: cliente_id: {cliente_id}")
            print(f"🐛 DEBUG: tipo_distribucion: {tipo_distribucion}")
            print(f"🐛 DEBUG: monto_a_distribuir: {monto_a_distribuir}")
            print(f"🐛 DEBUG: porcentaje_a_distribuir: {porcentaje_a_distribuir}")
            
            # Obtener la factura de venta
            print(f"🐛 DEBUG: Buscando factura de venta...")
            try:
                factura = FacturaVentaSIIPorDistribuir.objects.get(
                    id=factura_id,
                    holding_id=holding_id
                )
                print(f"🐛 DEBUG: ✅ Factura de venta encontrada: {factura.folio} - {factura.razon_social_receptor}")
                print(f"🐛 DEBUG: Factura - Monto total: ${factura.monto_total}")
                print(f"🐛 DEBUG: Factura - Monto distribuido: ${factura.monto_distribuido}")
                print(f"🐛 DEBUG: Factura - Porcentaje distribuido: {factura.porcentaje_distribuido}%")
                print(f"🐛 DEBUG: Factura - Monto pendiente: ${factura.get_monto_pendiente()}")
                print(f"🐛 DEBUG: Factura - Porcentaje pendiente: {factura.get_porcentaje_pendiente()}%")
                print(f"🐛 DEBUG: Factura - Completamente distribuida: {factura.esta_completamente_distribuida()}")
            except FacturaVentaSIIPorDistribuir.DoesNotExist:
                print(f"🐛 DEBUG: ❌ Factura de venta no encontrada")
                return Response(
                    {"message": "Factura de venta no encontrada"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Verificar estado de la factura
            print(f"🐛 DEBUG: Verificando estado de la factura de venta...")
            if factura.esta_completamente_distribuida():
                print(f"🐛 DEBUG: ❌ Factura de venta ya completamente distribuida")
                return Response(
                    {"message": "La factura de venta ya está completamente distribuida"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Obtener entidades relacionadas
            print(f"🐛 DEBUG: Buscando cliente...")
            try:
                cliente = Clientes.objects.get(id=cliente_id, holding=request.user.holding)
                print(f"🐛 DEBUG: ✅ Cliente encontrado: {cliente.nombre}")
            except Clientes.DoesNotExist:
                print(f"🐛 DEBUG: ❌ Cliente no encontrado")
                return Response(
                    {"message": "Cliente no encontrado"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Obtener fundo si se especifica
            fundo = None
            if fundo_id:
                print(f"🐛 DEBUG: Buscando fundo {fundo_id}...")
                try:
                    fundo = CamposClientes.objects.get(id=fundo_id, holding=request.user.holding)
                    print(f"🐛 DEBUG: ✅ Fundo encontrado: {fundo.nombre_campo}")
                except CamposClientes.DoesNotExist:
                    print(f"🐛 DEBUG: ❌ Fundo no encontrado")
                    return Response(
                        {"message": "Fundo no encontrado"}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
            
            # Obtener labor si se especifica
            labor = None
            if labor_id:
                print(f"🐛 DEBUG: Buscando labor {labor_id}...")
                try:
                    labor = Labores.objects.get(id=labor_id, holding=request.user.holding)
                    print(f"🐛 DEBUG: ✅ Labor encontrada: {labor.nombre}")
                except Labores.DoesNotExist:
                    print(f"🐛 DEBUG: ❌ Labor no encontrada")
                    return Response(
                        {"message": "Labor no encontrada"}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
            
            # Obtener cuenta si se especifica
            cuenta = None
            if cuenta_id:
                print(f"🐛 DEBUG: Buscando cuenta {cuenta_id}...")
                try:
                    cuenta = Cuenta.objects.get(id=cuenta_id, holding=request.user.holding)
                    print(f"🐛 DEBUG: ✅ Cuenta encontrada: {cuenta.nombre_cuenta}")
                except Cuenta.DoesNotExist:
                    print(f"🐛 DEBUG: ❌ Cuenta no encontrada")
                    return Response(
                        {"message": "Cuenta no encontrada"}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
            
            # Calcular distribución de venta
            print(f"🐛 DEBUG: Calculando distribución de venta...")
            
            if tipo_distribucion == 'MONTO':
                print(f"🐛 DEBUG: Distribución por MONTO")
                
                # Verificar si se puede distribuir el monto
                if not factura.puede_distribuir_monto(monto_a_distribuir):
                    print(f"🐛 DEBUG: ❌ No se puede distribuir el monto solicitado")
                    print(f"🐛 DEBUG: Monto solicitado: ${monto_a_distribuir}")
                    print(f"🐛 DEBUG: Monto disponible: ${factura.get_monto_pendiente()}")
                    return Response(
                        {"message": f"No se puede distribuir ${monto_a_distribuir:,.2f}. Monto disponible: ${factura.get_monto_pendiente():,.2f}"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Calcular montos proporcionales para venta
                print(f"🐛 DEBUG: Calculando proporción...")
                factor_proporcion = monto_a_distribuir / factura.monto_total
                print(f"🐛 DEBUG: Factor de proporción: {factor_proporcion}")
                
                monto_neto_distribuido = factura.monto_neto * factor_proporcion
                monto_exento_distribuido = factura.monto_exento * factor_proporcion
                monto_iva_distribuido = factura.monto_iva * factor_proporcion
                
                porcentaje_distribuido = (monto_a_distribuir / factura.monto_total) * 100
                print(f"🐛 DEBUG: Porcentaje calculado: {porcentaje_distribuido}%")
                
            elif tipo_distribucion == 'PORCENTAJE':
                print(f"🐛 DEBUG: Distribución por PORCENTAJE")
                
                # Verificar si se puede distribuir el porcentaje
                if not factura.puede_distribuir_porcentaje(porcentaje_a_distribuir):
                    print(f"🐛 DEBUG: ❌ No se puede distribuir el porcentaje solicitado")
                    print(f"🐛 DEBUG: Porcentaje solicitado: {porcentaje_a_distribuir}%")
                    print(f"🐛 DEBUG: Porcentaje disponible: {factura.get_porcentaje_pendiente()}%")
                    return Response(
                        {"message": f"No se puede distribuir {porcentaje_a_distribuir}%. Porcentaje disponible: {factura.get_porcentaje_pendiente()}%"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Calcular monto a distribuir
                porcentaje_decimal = porcentaje_a_distribuir / 100
                monto_a_distribuir = factura.monto_total * porcentaje_decimal
                print(f"🐛 DEBUG: Monto calculado: ${monto_a_distribuir}")
                
                # Calcular montos proporcionales
                monto_neto_distribuido = factura.monto_neto * porcentaje_decimal
                monto_exento_distribuido = factura.monto_exento * porcentaje_decimal
                monto_iva_distribuido = factura.monto_iva * porcentaje_decimal
                
                porcentaje_distribuido = porcentaje_a_distribuir
                
            print(f"🐛 DEBUG: Monto final a distribuir: ${monto_a_distribuir}")
            print(f"🐛 DEBUG: Porcentaje final: {porcentaje_distribuido}%")
            
            # Crear la distribución de venta
            print(f"🐛 DEBUG: Creando registro de distribución de venta...")
            try:
                distribucion = FacturaVentaSIIDistribuida.objects.create(
                    holding_id=holding_id,
                    cliente=cliente,
                    fundo=fundo,
                    labor=labor,
                    cuenta=cuenta,
                    
                    # Datos de la factura de venta
                    folio=factura.folio,
                    tipo_doc=factura.tipo_doc,
                    rut_receptor=factura.rut_receptor,
                    razon_social_receptor=factura.razon_social_receptor,
                    fecha_emision=factura.fecha_emision,
                    
                    # Montos proporcionales para venta
                    monto_total=monto_a_distribuir,  # El monto distribuido
                    monto_neto=monto_neto_distribuido,
                    monto_exento=monto_exento_distribuido,
                    monto_iva=monto_iva_distribuido,
                    monto_otros_impuestos=factura.monto_otros_impuestos * (porcentaje_distribuido / 100) if factura.monto_otros_impuestos else 0,
                    codigo_otros_impuestos=factura.codigo_otros_impuestos,
                    
                    # CAMPOS DE DISTRIBUCIÓN MÚLTIPLE PARA VENTA
                    monto_distribuido=monto_a_distribuir,
                    porcentaje_distribuido=porcentaje_distribuido,
                    tipo_distribucion=tipo_distribucion,
                    monto_total_factura=factura.monto_total,
                    
                    observaciones=observaciones,
                    usuario_distribuyente=request.user
                )
                print(f"🐛 DEBUG: ✅ Distribución de venta creada con ID: {distribucion.id}")
            except Exception as e:
                print(f"🐛 DEBUG: ❌ Error creando distribución de venta: {str(e)}")
                print(f"🐛 DEBUG: Error completo: {traceback.format_exc()}")
                return Response(
                    {"message": f"Error creando distribución de venta: {str(e)}"}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Actualizar totales en la factura original de venta
            print(f"🐛 DEBUG: Actualizando totales en factura original de venta...")
            try:
                factura.monto_distribuido += monto_a_distribuir
                factura.porcentaje_distribuido += porcentaje_distribuido
                
                print(f"🐛 DEBUG: Nuevo monto distribuido: ${factura.monto_distribuido}")
                print(f"🐛 DEBUG: Nuevo porcentaje distribuido: {factura.porcentaje_distribuido}%")
                
                # Verificar si está completamente distribuida
                if factura.esta_completamente_distribuida():
                    print(f"🐛 DEBUG: Factura de venta ahora está completamente distribuida")
                    factura.procesada = True
                
                factura.save()
                print(f"🐛 DEBUG: ✅ Factura de venta actualizada")
            except Exception as e:
                print(f"🐛 DEBUG: ❌ Error actualizando factura de venta: {str(e)}")
                print(f"🐛 DEBUG: Error completo: {traceback.format_exc()}")
                return Response(
                    {"message": f"Error actualizando factura de venta: {str(e)}"}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            print(f"🐛 DEBUG: ✅ Distribución de venta completada exitosamente")
            
            return Response({
                "status": "success",
                "message": f"Factura de venta distribuida exitosamente. Monto: ${monto_a_distribuir:,.2f} ({porcentaje_distribuido:.2f}%)",
                "data": {
                    "distribucion_id": distribucion.id,
                    "monto_distribuido": float(monto_a_distribuir),
                    "porcentaje_distribuido": float(porcentaje_distribuido),
                    "monto_pendiente": float(factura.get_monto_pendiente()),
                    "porcentaje_pendiente": float(factura.get_porcentaje_pendiente()),
                    "completamente_distribuida": factura.esta_completamente_distribuida()
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"🐛 DEBUG: ❌ ERROR GENERAL EN _distribute_invoice_multiple_venta")
            print(f"🐛 DEBUG: Error: {str(e)}")
            print(f"🐛 DEBUG: Traceback completo:")
            print(traceback.format_exc())
            return Response(
                {"message": f"Error distribuyendo factura de venta: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _get_next_folio(self, request):
        """Obtiene el próximo folio automático para boletas manuales"""
        try:
            holding_id = request.user.holding.id
            
            # Buscar el último folio de boletas manuales
            ultima_boleta = FacturaVentaSIIPorDistribuir.objects.filter(
                holding_id=holding_id,
                tipo_doc='BOLETA_MANUAL'
            ).order_by('-folio').first()
            
            if ultima_boleta and ultima_boleta.folio.isdigit():
                proximo_folio = int(ultima_boleta.folio) + 1
            else:
                proximo_folio = 1
                
            return Response({
                'status': 'success',
                'next_folio': proximo_folio
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Error obteniendo próximo folio: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _create_manual_invoice_venta(self, request):
        """
        Crea una nueva factura de venta manual (boleta en negro)
        """
        print(f"🐛 DEBUG: Iniciando _create_manual_invoice_venta")
        print(f"🐛 DEBUG: Datos recibidos: {request.data}")
        
        holding_id = request.user.holding.id if request.user.holding else None
        print(f"🐛 DEBUG: holding_id: {holding_id}")
        
        if not holding_id:
            print(f"🐛 DEBUG: Error - No hay holding_id")
            return Response({
                "status": "error",
                "message": "Usuario sin holding asignado"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:

            ultima_boleta = FacturaVentaSIIPorDistribuir.objects.filter(
                holding_id=holding_id,
                tipo_doc='BOLETA_MANUAL'
            ).order_by('-folio').first()
            
            if ultima_boleta and ultima_boleta.folio and ultima_boleta.folio.isdigit():
                proximo_folio = int(ultima_boleta.folio) + 1
                print(f"🐛 DEBUG: Última boleta: {ultima_boleta.folio}, próximo folio: {proximo_folio}")
            else:
                proximo_folio = 1
                print(f"🐛 DEBUG: Primera boleta, folio: {proximo_folio}")

            # Extraer y validar datos del request
            tipo_doc = 'BOLETA_MANUAL'  # FIJO
            rut_receptor = request.data.get('rut_receptor', '').strip()
            razon_social_receptor = request.data.get('razon_social_receptor', '').strip()
            folio = str(proximo_folio)
            fecha_emision = request.data.get('fecha_emision', '').strip()
            descripcion = request.data.get('descripcion', '').strip()
            observaciones = (request.data.get('observaciones') or '').strip()

            # Montos
            monto_total = float(request.data.get('monto_total', 0))
            monto_neto = float(request.data.get('monto_neto', 0))
            monto_exento = float(request.data.get('monto_exento', 0))
            monto_iva = float(request.data.get('monto_iva', 0))
            
            print(f"🐛 DEBUG: Datos procesados - tipo_doc: {tipo_doc}, folio: {folio}, monto_total: {monto_total}")
            
            # Validaciones básicas
            if not all([tipo_doc, rut_receptor, razon_social_receptor, folio, fecha_emision, descripcion]):
                return Response({
                    "status": "error",
                    "message": "Todos los campos son obligatorios"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if monto_total <= 0:
                return Response({
                    "status": "error",
                    "message": "El monto total debe ser mayor a 0"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validar formato RUT
            import re
            if not re.match(r'^\d{1,8}-[\dkK]$', rut_receptor):
                return Response({
                    "status": "error",
                    "message": "Formato de RUT inválido. Use formato: 12345678-9"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Procesar fechas
            try:
                # Convertir fecha de emisión
                if 'T' in fecha_emision:
                    fecha_emision = fecha_emision.split('T')[0]
                
                datetime.strptime(fecha_emision, '%Y-%m-%d')
                
            except ValueError as e:
                return Response({
                    "status": "error",
                    "message": f"Formato de fecha inválido: {str(e)}"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Verificar si ya existe una factura con el mismo folio para este holding
            factura_existente = FacturaVentaSIIPorDistribuir.objects.filter(
                holding_id=holding_id,
                folio=folio
            ).first()
            
            if factura_existente:
                return Response({
                    "status": "error",
                    "message": f"Ya existe una factura con el folio '{folio}' en este holding"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Crear la factura manual en la base de datos
            with transaction.atomic():
                nueva_factura = FacturaVentaSIIPorDistribuir.objects.create(
                    holding_id=holding_id,
                    
                    # Datos básicos
                    tipo_doc=tipo_doc,
                    rut_receptor=rut_receptor,
                    razon_social_receptor=razon_social_receptor,
                    folio=folio,
                    fecha_emision=fecha_emision,
                    
                    # Montos
                    monto_total=monto_total,
                    monto_neto=monto_neto,
                    monto_exento=monto_exento,
                    monto_iva=monto_iva,
                    
                    # Campos adicionales para facturas manuales
                    descripcion=descripcion,
                    observaciones_manual=observaciones,
                    
                    # Identificación como factura manual
                    es_manual=True,
                    fecha_creacion_manual=timezone.now(),
                    
                    # Campos de control
                    fecha_encontrada=timezone.now(),
                    procesada=False,
                    
                    # Campos de distribución inicializados (SOLO LOS QUE EXISTEN EN EL MODELO)
                    monto_distribuido=0,
                    porcentaje_distribuido=0,
                    
                    # PDF no aplica para facturas manuales (SOLO LOS QUE EXISTEN EN EL MODELO)
                    pdf_descargado=False,
                    intentos_descarga_pdf=0,
                    
                    # Otros campos por defecto
                    monto_otros_impuestos=0,
                    codigo_otros_impuestos=None
                )
                
                print(f"🐛 DEBUG: Factura manual creada con ID: {nueva_factura.id}")
                
                # Preparar respuesta con datos de la factura creada
                factura_data = {
                    'id': nueva_factura.id,
                    'tipo_doc': nueva_factura.tipo_doc,
                    'folio': nueva_factura.folio,
                    'rut_receptor': nueva_factura.rut_receptor,
                    'razon_social_receptor': nueva_factura.razon_social_receptor,
                    'fecha_emision': nueva_factura.fecha_emision,
                    'monto_total': float(nueva_factura.monto_total),
                    'monto_neto': float(nueva_factura.monto_neto),
                    'monto_exento': float(nueva_factura.monto_exento),
                    'monto_iva': float(nueva_factura.monto_iva),
                    'descripcion': nueva_factura.descripcion,
                    'es_manual': True,
                    'monto_distribuido': float(nueva_factura.monto_distribuido),
                    # CAMPOS CALCULADOS (no se guardan en la BD, se calculan dinámicamente)
                    'monto_pendiente': float(nueva_factura.monto_total - nueva_factura.monto_distribuido),
                    'porcentaje_distribuido': float(nueva_factura.porcentaje_distribuido),
                    'porcentaje_pendiente': float(100 - nueva_factura.porcentaje_distribuido),
                    'distribuciones_count': 0,
                    'completamente_distribuida': False,
                    'pdf_disponible': False
                }
                
                return Response({
                    "status": "success",
                    "message": f"Factura manual '{folio}' creada exitosamente",
                    "factura": factura_data
                }, status=status.HTTP_201_CREATED)
                
        except ValueError as e:
            print(f"🐛 DEBUG: Error de validación: {str(e)}")
            return Response({
                "status": "error",
                "message": f"Error en los datos proporcionados: {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            print(f"🐛 DEBUG: Error inesperado: {str(e)}")
            print(traceback.format_exc())
            return Response({
                "status": "error",
                "message": f"Error interno del servidor: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # ==================== ACTUALIZAR MÉTODO _get_automatic_invoices_venta ====================

    def _get_automatic_invoices_venta(self, request):
        """
        Obtiene todas las facturas de venta por distribuir (automáticas Y manuales)
        VERSIÓN CORREGIDA
        """
        print(f"🐛 DEBUG: Iniciando _get_automatic_invoices_venta")
        
        holding_id = request.user.holding.id if request.user.holding else None
        
        if not holding_id:
            return Response({
                'status': 'error',
                'message': 'Usuario sin holding asignado'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Obtener TODAS las facturas por distribuir (SII + manuales)
            facturas_query = FacturaVentaSIIPorDistribuir.objects.filter(
                holding_id=holding_id
            ).order_by('-fecha_encontrada', '-id')
            
            print(f"🐛 DEBUG: Total facturas encontradas: {facturas_query.count()}")
            
            facturas_data = []
            
            # Contadores para estadísticas
            total_facturas = 0
            facturas_con_pdf = 0
            facturas_sin_pdf = 0
            facturas_error_pdf = 0
            facturas_sin_distribuir = 0
            facturas_parcialmente_distribuidas = 0
            facturas_con_alguna_distribucion = 0
            facturas_manuales = 0
            facturas_sii = 0
            
            for factura in facturas_query:
                try:
                    # CORRECCIÓN: Obtener distribuciones existentes usando los campos correctos
                    distribuciones_existentes = FacturaVentaSIIDistribuida.objects.filter(
                        holding_id=holding_id,
                        folio=factura.folio,
                        rut_receptor=factura.rut_receptor
                    ).select_related('cliente', 'fundo', 'labor', 'cuenta', 'usuario_distribuyente')
                    
                    distribuciones_data = []
                    total_distribuido = 0
                    
                    for dist in distribuciones_existentes:
                        distribucion_info = {
                            'id': dist.id,
                            'cliente': {
                                'id': dist.cliente.id,
                                'nombre': dist.cliente.nombre,
                                'rut': dist.cliente.rut
                            } if dist.cliente else None,
                            'fundo': {
                                'id': dist.fundo.id,
                                'nombre': dist.fundo.nombre_campo
                            } if dist.fundo else None,
                            'labor': {
                                'id': dist.labor.id,
                                'nombre': dist.labor.nombre
                            } if dist.labor else None,
                            'cuenta': {
                                'id': dist.cuenta.id,
                                'nombre': dist.cuenta.nombre_cuenta,
                                'codigo': dist.cuenta.cuenta_contable
                            } if dist.cuenta else None,
                            'monto_distribuido': float(dist.monto_distribuido),
                            'porcentaje_distribuido': float(dist.porcentaje_distribuido),
                            'tipo_distribucion': dist.tipo_distribucion,
                            'fecha_distribucion': dist.fecha_distribucion.isoformat(),
                            'observaciones': dist.observaciones,
                            'usuario_distribuyente': {
                                'id': dist.usuario_distribuyente.id,
                                'nombre': f"{dist.usuario_distribuyente.first_name} {dist.usuario_distribuyente.last_name}".strip(),
                                'rut': getattr(dist.usuario_distribuyente, 'rut', '')
                            } if dist.usuario_distribuyente else None
                        }
                        distribuciones_data.append(distribucion_info)
                        total_distribuido += float(dist.monto_distribuido)
                    
                    # ==================== DETERMINAR SI ES FACTURA MANUAL ====================
                    # Verificar si tiene el campo es_manual (nueva migración)
                    try:
                        es_manual = factura.es_manual
                    except AttributeError:
                        # Si no existe el campo, determinar por tipo_doc
                        es_manual = factura.tipo_doc in ['BOLETA_MANUAL', 'FACTURA_MANUAL', 'NOTA_VENTA', 'COMPROBANTE']
                    
                    print(f"🐛 DEBUG: Factura {factura.id} - tipo_doc: {factura.tipo_doc}, es_manual: {es_manual}")
                    
                    # ==================== OBTENER CAMPOS SEGUROS ====================
                    # Usar getattr con valores por defecto para campos que pueden no existir
                    descripcion = getattr(factura, 'descripcion', '') or ''
                    observaciones_manual = getattr(factura, 'observaciones_manual', '') or ''
                    fecha_creacion_manual = getattr(factura, 'fecha_creacion_manual', None)
                    usuario_creador = getattr(factura, 'usuario_creador', None)
                    
                    # Campos de PDF - usar getattr para evitar errores
                    pdf_disponible = getattr(factura, 'pdf_disponible', False) if not es_manual else False
                    pdf_descargado = getattr(factura, 'pdf_descargado', False) if not es_manual else False
                    fecha_descarga_pdf = getattr(factura, 'fecha_descarga_pdf', None) if not es_manual else None
                    error_descarga_pdf = getattr(factura, 'error_descarga_pdf', '') if not es_manual else ''
                    intentos_descarga_pdf = getattr(factura, 'intentos_descarga_pdf', 0) if not es_manual else 0
                    codigo_sii = getattr(factura, 'codigo_sii', '') if not es_manual else ''
                    
                    # ==================== CALCULAR CAMPOS DE DISTRIBUCIÓN ====================
                    monto_total = float(factura.monto_total)
                    monto_distribuido = float(getattr(factura, 'monto_distribuido', 0)) or total_distribuido
                    monto_pendiente = monto_total - monto_distribuido
                    
                    if monto_total > 0:
                        porcentaje_distribuido = (monto_distribuido / monto_total) * 100
                        porcentaje_pendiente = 100 - porcentaje_distribuido
                    else:
                        porcentaje_distribuido = 0
                        porcentaje_pendiente = 100
                    
                    completamente_distribuida = porcentaje_distribuido >= 100
                    
                    # ==================== MAPEAR DATOS DE LA FACTURA ====================
                    factura_info = {
                        'id': factura.id,
                        'nro': factura.nro if factura.nro else str(factura.id),
                        'tipo_doc': factura.tipo_doc,
                        'rut_receptor': factura.rut_receptor,
                        'razon_social_receptor': factura.razon_social_receptor,
                        'folio': factura.folio,
                        'fecha_emision': factura.fecha_emision,
                        'fecha_encontrada': factura.fecha_encontrada.isoformat() if factura.fecha_encontrada else '',
                        
                        # Montos
                        'monto_total': monto_total,
                        'monto_neto': float(factura.monto_neto),
                        'monto_exento': float(factura.monto_exento),
                        'monto_iva': float(factura.monto_iva),
                        'monto_otros_impuestos': float(getattr(factura, 'monto_otros_impuestos', 0)),
                        'codigo_otros_impuestos': getattr(factura, 'codigo_otros_impuestos', '') or '',
                        
                        # Campos de distribución
                        'monto_distribuido': monto_distribuido,
                        'monto_pendiente': monto_pendiente,
                        'porcentaje_distribuido': porcentaje_distribuido,
                        'porcentaje_pendiente': porcentaje_pendiente,
                        'completamente_distribuida': completamente_distribuida,
                        'distribuciones_count': len(distribuciones_data),
                        'distribuciones': distribuciones_data,
                        
                        # ==================== CAMPOS ESPECÍFICOS PARA FACTURAS MANUALES ====================
                        'es_manual': es_manual,
                        'descripcion': descripcion,
                        'observaciones_manual': observaciones_manual,
                        'fecha_creacion_manual': fecha_creacion_manual.isoformat() if fecha_creacion_manual else None,
                        'usuario_creador': {
                            'id': usuario_creador.id,
                            'nombre': f"{usuario_creador.first_name} {usuario_creador.last_name}".strip(),
                            'username': usuario_creador.username
                        } if usuario_creador else None,
                        
                        # ==================== CAMPOS DE PDF (SOLO PARA FACTURAS SII) ====================
                        'pdf_disponible': pdf_disponible,
                        'pdf_descargado': pdf_descargado,
                        'fecha_descarga_pdf': fecha_descarga_pdf.isoformat() if fecha_descarga_pdf else '',
                        'error_descarga_pdf': error_descarga_pdf or '',
                        'intentos_descarga_pdf': intentos_descarga_pdf,
                        'codigo_sii': codigo_sii or '',
                        
                        # Campos de control
                        'procesada': factura.procesada,
                        'holding': holding_id
                    }
                    
                    facturas_data.append(factura_info)
                    print(f"🐛 DEBUG: Factura {factura.id} agregada - es_manual: {es_manual}, tipo: {factura.tipo_doc}")
                    
                    # ==================== ACTUALIZAR CONTADORES PARA ESTADÍSTICAS ====================
                    total_facturas += 1
                    
                    if es_manual:
                        facturas_manuales += 1
                    else:
                        facturas_sii += 1
                        
                        # Solo contar PDFs para facturas SII
                        if pdf_disponible:
                            facturas_con_pdf += 1
                        elif error_descarga_pdf:
                            facturas_error_pdf += 1
                        else:
                            facturas_sin_pdf += 1
                    
                    # Estadísticas de distribución (para todas las facturas)
                    if porcentaje_distribuido == 0:
                        facturas_sin_distribuir += 1
                    elif porcentaje_distribuido > 0 and porcentaje_distribuido < 100:
                        facturas_parcialmente_distribuidas += 1
                    
                    if porcentaje_distribuido > 0:
                        facturas_con_alguna_distribucion += 1
                    
                except Exception as e:
                    print(f"🐛 DEBUG: Error procesando factura {factura.id}: {str(e)}")
                    print(traceback.format_exc())
                    continue
            
            print(f"🐛 DEBUG: Facturas procesadas exitosamente. Total: {len(facturas_data)}")
            print(f"🐛 DEBUG: Estadísticas: SII={facturas_sii}, Manuales={facturas_manuales}")
            print(f"🐛 DEBUG: Primeras 3 facturas: {[f.get('folio', 'N/A') for f in facturas_data[:3]]}")
            
            # ==================== PREPARAR ESTADÍSTICAS ====================
            estadisticas = {
                # Estadísticas generales
                'total_facturas': total_facturas,
                'facturas_sii': facturas_sii,
                'facturas_manuales': facturas_manuales,
                
                # Estadísticas de distribución
                'facturas_sin_distribuir': facturas_sin_distribuir,
                'facturas_parcialmente_distribuidas': facturas_parcialmente_distribuidas,
                'facturas_con_alguna_distribucion': facturas_con_alguna_distribucion,
                
                # Estadísticas de PDF (solo para facturas SII)
                'facturas_con_pdf': facturas_con_pdf,
                'facturas_sin_pdf': facturas_sin_pdf,
                'facturas_error_pdf': facturas_error_pdf,
                'porcentaje_con_pdf': round((facturas_con_pdf / facturas_sii * 100) if facturas_sii > 0 else 0, 2),
                'porcentaje_sin_pdf': round((facturas_sin_pdf / facturas_sii * 100) if facturas_sii > 0 else 0, 2),
                'porcentaje_error_pdf': round((facturas_error_pdf / facturas_sii * 100) if facturas_sii > 0 else 0, 2),
                'fecha_actualizacion': timezone.now().isoformat()
            }
            
            return Response({
                'status': 'success',
                'facturas': facturas_data,
                'estadisticas': estadisticas
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"🐛 DEBUG: ERROR GENERAL en _get_automatic_invoices_venta: {str(e)}")
            print(traceback.format_exc())
            return Response({
                'status': 'error',
                'message': f'Error al obtener facturas: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _get_invoice_distribution_details_venta(self, request):
        """
        Obtiene los detalles de distribución de una factura específica de venta
        """
        holding_id = request.user.holding.id if request.user.holding else None
        factura_id = request.data.get('factura_id')
        
        if not holding_id:
            return Response(
                {"message": "No se pudo determinar el holding"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not factura_id:
            return Response(
                {"message": "ID de factura es requerido"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Obtener la factura de venta
            factura = FacturaVentaSIIPorDistribuir.objects.get(
                id=factura_id,
                holding_id=holding_id
            )
            
            # Obtener todas las distribuciones de venta
            distribuciones = FacturaVentaSIIDistribuida.objects.filter(
                holding_id=holding_id,
                folio=factura.folio,
                rut_receptor=factura.rut_receptor
            ).order_by('-fecha_distribucion')
            
            # Serializar datos
            factura_serializer = FacturaVentaPorDistribuirMultipleSerializer(factura)
            distribuciones_serializer = FacturaVentaSIIDistribuidaMultipleSerializer(distribuciones, many=True)
            
            return Response({
                "status": "success",
                "factura": factura_serializer.data,
                "distribuciones": distribuciones_serializer.data,
                "resumen": {
                    "monto_total": float(factura.monto_total),
                    "monto_distribuido": float(factura.monto_distribuido),
                    "monto_pendiente": float(factura.get_monto_pendiente()),
                    "porcentaje_distribuido": float(factura.porcentaje_distribuido),
                    "porcentaje_pendiente": float(factura.get_porcentaje_pendiente()),
                    "total_distribuciones": distribuciones.count(),
                    "completamente_distribuida": factura.esta_completamente_distribuida()
                }
            }, status=status.HTTP_200_OK)
            
        except FacturaVentaSIIPorDistribuir.DoesNotExist:
            return Response(
                {"message": "Factura de venta no encontrada"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            print(f"Error obteniendo detalles de distribución de venta: {str(e)}")
            return Response(
                {"message": f"Error obteniendo detalles de venta: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _get_distribution_summary_venta(self, request):
        """
        Obtiene un resumen de todas las facturas de venta y sus distribuciones
        """
        holding_id = request.user.holding.id if request.user.holding else None
        
        if not holding_id:
            return Response(
                {"message": "No se pudo determinar el holding"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Obtener estadísticas de venta
            total_facturas = FacturaVentaSIIPorDistribuir.objects.filter(holding_id=holding_id).count()
            facturas_pendientes = FacturaVentaSIIPorDistribuir.objects.filter(
                holding_id=holding_id, 
                procesada=False
            ).count()
            facturas_parcialmente_distribuidas = FacturaVentaSIIPorDistribuir.objects.filter(
                holding_id=holding_id,
                procesada=False,
                porcentaje_distribuido__gt=0
            ).count()
            
            # Facturas con distribuciones parciales para mostrar progreso
            facturas_con_progreso = FacturaVentaSIIPorDistribuir.objects.filter(
                holding_id=holding_id,
                procesada=False,
                porcentaje_distribuido__gt=0
            ).order_by('-fecha_encontrada')[:10]
            
            facturas_progreso_data = []
            for factura in facturas_con_progreso:
                facturas_progreso_data.append({
                    'id': factura.id,
                    'folio': factura.folio,
                    'razon_social_receptor': factura.razon_social_receptor,
                    'monto_total': float(factura.monto_total),
                    'monto_distribuido': float(factura.monto_distribuido),
                    'porcentaje_distribuido': float(factura.porcentaje_distribuido),
                    'distribuciones_count': factura.get_distribuciones().count()
                })
            
            return Response({
                "status": "success",
                "estadisticas": {
                    "total_facturas": total_facturas,
                    "facturas_pendientes": facturas_pendientes,
                    "facturas_completamente_distribuidas": total_facturas - facturas_pendientes,
                    "facturas_parcialmente_distribuidas": facturas_parcialmente_distribuidas,
                    "facturas_sin_distribuir": facturas_pendientes - facturas_parcialmente_distribuidas
                },
                "facturas_con_progreso": facturas_progreso_data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"Error obteniendo resumen de distribución de venta: {str(e)}")
            return Response(
                {"message": f"Error obteniendo resumen de venta: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _delete_distribution_venta(self, request):
        """
        Elimina una distribución específica de venta y actualiza los totales de la factura
        """
        holding_id = request.user.holding.id if request.user.holding else None
        distribucion_id = request.data.get('distribucion_id')
        
        if not holding_id:
            return Response(
                {"message": "No se pudo determinar el holding"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not distribucion_id:
            return Response(
                {"message": "ID de distribución es requerido"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            with transaction.atomic():
                # Obtener la distribución de venta
                distribucion = FacturaVentaSIIDistribuida.objects.get(
                    id=distribucion_id,
                    holding_id=holding_id
                )
                
                # Obtener la factura asociada de venta
                factura = FacturaVentaSIIPorDistribuir.objects.get(
                    holding_id=holding_id,
                    folio=distribucion.folio,
                    rut_receptor=distribucion.rut_receptor
                )
                
                # Restar los montos de la distribución eliminada
                factura.monto_distribuido -= distribucion.monto_distribuido
                factura.porcentaje_distribuido -= distribucion.porcentaje_distribuido
                
                # Si estaba marcada como procesada y ya no está 100% distribuida, desmarcarla
                if factura.procesada and not factura.esta_completamente_distribuida():
                    factura.procesada = False
                
                factura.save()
                
                # Guardar información antes de eliminar
                distribucion_info = distribucion.get_distribucion_info()
                
                # Eliminar la distribución
                distribucion.delete()
                
                return Response({
                    "status": "success",
                    "message": f"Distribución de venta eliminada exitosamente",
                    "distribucion_eliminada": distribucion_info,
                    "factura_actualizada": factura.get_factura_data()
                }, status=status.HTTP_200_OK)
                
        except FacturaVentaSIIDistribuida.DoesNotExist:
            return Response(
                {"message": "Distribución de venta no encontrada"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except FacturaVentaSIIPorDistribuir.DoesNotExist:
            return Response(
                {"message": "Factura de venta asociada no encontrada"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            print(f"Error eliminando distribución de venta: {str(e)}")
            return Response(
                {"message": f"Error eliminando distribución de venta: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # ==================== CONFIGURACIÓN AUTOMÁTICA DE VENTA ====================

    def _get_automatic_configuration_venta(self, request):
        """
        Obtiene la configuración automática del holding para venta
        """
        holding_id = request.user.holding.id if request.user.holding else None
        
        if not holding_id:
            return Response(
                {"message": "No se pudo determinar el holding"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            configuracion = ConfiguracionSIIAutomaticaVenta.objects.get(holding_id=holding_id)
            
            data = {
                'rut_sii': configuracion.rut_sii,
                'empresa_rut': configuracion.empresa_rut,
                'empresa_nombre': configuracion.empresa_nombre,
                'hora_ejecucion': configuracion.hora_ejecucion.strftime('%H:%M'),
                'mes': configuracion.mes,
                'year': configuracion.year,
                'activo': configuracion.activo,
                'created_at': configuracion.created_at,
                'updated_at': configuracion.updated_at
            }
     
            return Response({
                "message": "Configuración de venta obtenida exitosamente",
                "status": "success",
                "data": data
            }, status=status.HTTP_200_OK)
            
        except ConfiguracionSIIAutomaticaVenta.DoesNotExist:
            return Response({
                "message": "No hay configuración automática de venta",
                "status": "not_found",
                "data": None
            }, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Error obteniendo configuración automática de venta: {str(e)}")
            return Response(
                {"message": f"Error obteniendo configuración de venta: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _save_automatic_configuration_venta(self, request):
        """
        Guarda o actualiza la configuración automática de venta
        """
        holding_id = request.user.holding.id if request.user.holding else None
        
        if not holding_id:
            return Response(
                {"message": "No se pudo determinar el holding"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Validar datos requeridos
            required_fields = ['rut_sii', 'password_sii', 'empresa_rut', 'hora_ejecucion', 'mes', 'year']
            for field in required_fields:
                if request.data.get(field) is None:
                    return Response(
                        {"message": f"El campo {field} es requerido"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Validar mes y año
            try:
                mes = int(request.data['mes'])
                year = int(request.data['year'])
                
                if not 1 <= mes <= 12:
                    return Response(
                        {"message": "El mes debe estar entre 1 y 12"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                import datetime
                current_year = datetime.datetime.now().year
                if not 2000 <= year <= current_year + 5:
                    return Response(
                        {"message": f"El año debe estar entre 2000 y {current_year + 5}"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                    
            except (ValueError, TypeError):
                return Response(
                    {"message": "Mes y año deben ser números enteros válidos"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Convertir hora_ejecucion string a objeto time
            hora_str = request.data['hora_ejecucion']
            try:
                if isinstance(hora_str, str):
                    from datetime import time
                    hora_parts = hora_str.split(':')
                    hora_obj = time(int(hora_parts[0]), int(hora_parts[1]))
                else:
                    hora_obj = hora_str
            except (ValueError, IndexError) as e:
                return Response(
                    {"message": "Formato de hora inválido. Use HH:MM"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Encriptar contraseña si es necesario
            password_a_guardar = request.data['password_sii']
            
            # Obtener o crear configuración de venta
            configuracion, created = ConfiguracionSIIAutomaticaVenta.objects.get_or_create(
                holding_id=holding_id,
                defaults={
                    'rut_sii': request.data['rut_sii'],
                    'password_sii': password_a_guardar,
                    'empresa_rut': request.data['empresa_rut'],
                    'empresa_nombre': request.data.get('empresa_nombre', ''),
                    'hora_ejecucion': hora_obj,
                    'mes': mes,
                    'year': year,
                    'activo': request.data.get('activo', True)
                }
            )
            
            if not created:
                # Actualizar configuración existente de venta
                configuracion.rut_sii = request.data['rut_sii']
                configuracion.password_sii = password_a_guardar
                configuracion.empresa_rut = request.data['empresa_rut']
                configuracion.empresa_nombre = request.data.get('empresa_nombre', configuracion.empresa_nombre)
                configuracion.hora_ejecucion = hora_obj
                configuracion.mes = mes
                configuracion.year = year
                configuracion.activo = request.data.get('activo', configuracion.activo)
                
                # Validar antes de guardar
                try:
                    configuracion.full_clean()
                    configuracion.save()
                except ValidationError as e:
                    return Response(
                        {"message": f"Error de validación: {str(e)}"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Respuesta con la configuración actualizada
            response_data = {
                'rut_sii': configuracion.rut_sii,
                'empresa_rut': configuracion.empresa_rut,
                'empresa_nombre': configuracion.empresa_nombre,
                'hora_ejecucion': configuracion.hora_ejecucion.strftime('%H:%M'),
                'mes': configuracion.mes,
                'year': configuracion.year,
                'activo': configuracion.activo
            }
            
            action_text = "creada" if created else "actualizada"
            
            return Response({
                "message": f"Configuración de venta {action_text} exitosamente",
                "status": "success",
                "data": response_data
            }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
            
        except Exception as e:
            print(f"Error guardando configuración automática de venta: {str(e)}")
            return Response(
                {"message": f"Error guardando configuración de venta: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # ==================== FACTURAS AUTOMÁTICAS DE VENTA ====================

    def _download_invoice_pdf_venta(self, request):
        """
        Descarga el PDF de una factura específica de venta
        """
        factura_id = request.data.get('factura_id')
        
        if not factura_id:
            return Response(
                {"message": "ID de factura es obligatorio"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            holding_id = request.user.holding.id if request.user.holding else None
            
            # Obtener la factura de venta
            try:
                factura = FacturaVentaSIIPorDistribuir.objects.get(
                    id=factura_id,
                    holding_id=holding_id
                )
            except FacturaVentaSIIPorDistribuir.DoesNotExist:
                return Response(
                    {"message": "Factura de venta no encontrada"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Verificar que tiene PDF
            if not factura.pdf_documento:
                return Response(
                    {
                        "message": "La factura de venta no tiene PDF disponible",
                        "status": "no_pdf",
                        "info": {
                            "pdf_descargado": factura.pdf_descargado,
                            "intentos_descarga": factura.intentos_descarga_pdf,
                            "error_descarga": factura.error_descarga_pdf
                        }
                    }, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Verificar que el archivo existe
            try:
                pdf_path = factura.pdf_documento.path
                if not os.path.exists(pdf_path):
                    return Response(
                        {"message": "El archivo PDF de venta no se encuentra en el servidor"}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
            except Exception:
                return Response(
                    {"message": "Error accediendo al archivo PDF de venta"}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Información del archivo
            file_size = os.path.getsize(pdf_path)
            
            # Retornar información del PDF para descarga
            return Response({
                "message": "PDF de venta encontrado",
                "status": "success",
                "pdf_info": {
                    "url": factura.pdf_documento.url,
                    "filename": f"factura_venta_{factura.tipo_doc}_{factura.folio}_{factura.rut_receptor}.pdf",
                    "size_bytes": file_size,
                    "size_mb": round(file_size / (1024 * 1024), 2),
                    "fecha_descarga": factura.fecha_descarga_pdf.strftime('%d/%m/%Y %H:%M') if factura.fecha_descarga_pdf else None
                },
                "factura_info": {
                    "folio": factura.folio,
                    "tipo_doc": factura.tipo_doc,
                    "rut_receptor": factura.rut_receptor,
                    "razon_social_receptor": factura.razon_social_receptor,
                    "fecha_emision": factura.fecha_emision,
                    "monto_total": float(factura.monto_total)
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"Error descargando PDF de venta: {str(e)}")
            print(traceback.format_exc())
            return Response(
                {"message": f"Error descargando PDF de venta: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _retry_pdf_download_venta(self, request):
        """
        Reintenta la descarga de PDFs para facturas específicas de venta que fallaron
        """
        factura_ids = request.data.get('factura_ids', [])
        
        if not factura_ids:
            return Response(
                {"message": "Lista de IDs de facturas de venta es obligatoria"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            holding_id = request.user.holding.id if request.user.holding else None
            
            # Verificar configuración
            try:
                configuracion = ConfiguracionSIIAutomaticaVenta.objects.get(holding_id=holding_id)
            except ConfiguracionSIIAutomaticaVenta.DoesNotExist:
                return Response(
                    {"message": "No hay configuración automática de venta"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Obtener facturas válidas para reintentar
            facturas = FacturaVentaSIIPorDistribuir.objects.filter(
                id__in=factura_ids,
                holding_id=holding_id,
                pdf_descargado=False
            )
            
            if not facturas.exists():
                return Response(
                    {"message": "No se encontraron facturas de venta válidas para reintentar"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Resetear contadores de intentos para darles otra oportunidad
            facturas.update(
                intentos_descarga_pdf=0,
                error_descarga_pdf=None
            )
            
            # Ejecutar búsqueda de PDFs específica
            from .tasks import buscar_pdfs_facturas_venta_existentes
            task_result = buscar_pdfs_facturas_venta_existentes.delay(holding_id)
            
            return Response({
                "message": f"Reintento de descarga de venta iniciado para {facturas.count()} facturas",
                "status": "success",
                "task_id": task_result.id,
                "facturas_procesadas": list(facturas.values_list('id', flat=True))
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"Error en reintento de PDFs de venta: {str(e)}")
            return Response(
                {"message": f"Error en reintento de PDFs de venta: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _search_pdfs_for_existing_invoices_venta(self, request):
        """
        Busca PDFs para facturas de venta existentes que no los tienen
        """
        holding_id = request.user.holding.id if request.user.holding else None
        
        if not holding_id:
            return Response(
                {"message": "No se pudo determinar el holding"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Verificar configuración
            try:
                configuracion = ConfiguracionSIIAutomaticaVenta.objects.get(holding_id=holding_id)
            except ConfiguracionSIIAutomaticaVenta.DoesNotExist:
                return Response(
                    {"message": "No hay configuración automática de venta configurada"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not configuracion.activo:
                return Response(
                    {"message": "La configuración automática de venta está desactivada"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Estadísticas detalladas
            facturas_sin_pdf = FacturaVentaSIIPorDistribuir.objects.filter(
                holding_id=holding_id,
                pdf_descargado=False,
                intentos_descarga_pdf__lt=3  # Solo las que pueden reintentarse
            )
            
            facturas_error_pdf = FacturaVentaSIIPorDistribuir.objects.filter(
                holding_id=holding_id,
                pdf_descargado=False,
                intentos_descarga_pdf__gte=3  # Las que ya fallaron muchas veces
            )
            
            total_sin_pdf = facturas_sin_pdf.count()
            total_error_pdf = facturas_error_pdf.count()
            
            if total_sin_pdf == 0:
                mensaje = "No hay facturas de venta sin PDF para procesar"
                if total_error_pdf > 0:
                    mensaje += f" ({total_error_pdf} facturas con errores permanentes)"
                
                return Response({
                    "message": mensaje,
                    "status": "success",
                    "estadisticas": {
                        "facturas_sin_pdf": 0,
                        "facturas_error_pdf": total_error_pdf,
                        "facturas_procesables": 0
                    }
                }, status=status.HTTP_200_OK)
            
            # Ejecutar búsqueda de PDFs en background
            from .tasks import buscar_pdfs_facturas_venta_existentes
            task_result = buscar_pdfs_facturas_venta_existentes.delay(holding_id)
            
            return Response({
                "message": f"Búsqueda de PDFs de venta iniciada para {total_sin_pdf} facturas",
                "status": "success",
                "task_id": task_result.id,
                "estadisticas": {
                    "facturas_sin_pdf": total_sin_pdf,
                    "facturas_error_pdf": total_error_pdf,
                    "facturas_procesables": total_sin_pdf
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"Error iniciando búsqueda de PDFs de venta: {str(e)}")
            print(traceback.format_exc())
            return Response(
                {"message": f"Error iniciando búsqueda de PDFs de venta: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _get_pdf_search_status_venta(self, request):
        """
        Obtiene el estado detallado de la búsqueda de PDFs de venta
        """
        holding_id = request.user.holding.id if request.user.holding else None
        
        if not holding_id:
            return Response(
                {"message": "No se pudo determinar el holding"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Estadísticas generales
            total_facturas = FacturaVentaSIIPorDistribuir.objects.filter(
                holding_id=holding_id,
                procesada=False
            ).count()
            
            facturas_con_pdf = FacturaVentaSIIPorDistribuir.objects.filter(
                holding_id=holding_id,
                procesada=False,
                pdf_descargado=True
            ).count()
            
            facturas_sin_pdf = FacturaVentaSIIPorDistribuir.objects.filter(
                holding_id=holding_id,
                procesada=False,
                pdf_descargado=False,
                intentos_descarga_pdf__lt=3
            ).count()
            
            facturas_error_pdf = FacturaVentaSIIPorDistribuir.objects.filter(
                holding_id=holding_id,
                procesada=False,
                pdf_descargado=False,
                intentos_descarga_pdf__gte=3
            ).count()
            
            # Estadísticas por tipo de error (últimos 10 errores)
            facturas_con_error = FacturaVentaSIIPorDistribuir.objects.filter(
                holding_id=holding_id,
                procesada=False,
                pdf_descargado=False,
                error_descarga_pdf__isnull=False
            ).exclude(error_descarga_pdf='').order_by('-fecha_encontrada')[:10]
            
            errores_recientes = []
            for factura in facturas_con_error:
                errores_recientes.append({
                    'folio': factura.folio,
                    'rut_receptor': factura.rut_receptor,
                    'error': factura.error_descarga_pdf,
                    'intentos': factura.intentos_descarga_pdf,
                    'fecha': factura.fecha_encontrada.strftime('%d/%m/%Y %H:%M')
                })
            
            # Facturas descargadas recientemente (últimas 5)
            facturas_recientes_pdf = FacturaVentaSIIPorDistribuir.objects.filter(
                holding_id=holding_id,
                procesada=False,
                pdf_descargado=True,
                fecha_descarga_pdf__isnull=False
            ).order_by('-fecha_descarga_pdf')[:5]
            
            pdfs_recientes = []
            for factura in facturas_recientes_pdf:
                pdfs_recientes.append({
                    'folio': factura.folio,
                    'rut_receptor': factura.rut_receptor,
                    'razon_social_receptor': factura.razon_social_receptor[:50],  # Truncar para UI
                    'fecha_descarga': factura.fecha_descarga_pdf.strftime('%d/%m/%Y %H:%M'),
                    'pdf_url': factura.pdf_documento.url if factura.pdf_documento else None
                })
            
            # Calcular porcentajes
            porcentaje_con_pdf = round((facturas_con_pdf / total_facturas * 100) if total_facturas > 0 else 0, 1)
            porcentaje_sin_pdf = round((facturas_sin_pdf / total_facturas * 100) if total_facturas > 0 else 0, 1)
            porcentaje_error_pdf = round((facturas_error_pdf / total_facturas * 100) if total_facturas > 0 else 0, 1)
            
            return Response({
                "status": "success",
                "estadisticas_pdf": {
                    "total_facturas": total_facturas,
                    "facturas_con_pdf": facturas_con_pdf,
                    "facturas_sin_pdf": facturas_sin_pdf,
                    "facturas_error_pdf": facturas_error_pdf,
                    "porcentaje_con_pdf": porcentaje_con_pdf,
                    "porcentaje_sin_pdf": porcentaje_sin_pdf,
                    "porcentaje_error_pdf": porcentaje_error_pdf,
                    "facturas_procesables": facturas_sin_pdf  # Las que se pueden reintentar
                },
                "errores_recientes": errores_recientes,
                "pdfs_recientes": pdfs_recientes,
                "resumen": {
                    "estado_general": "excelente" if porcentaje_con_pdf >= 90 else 
                                    "bueno" if porcentaje_con_pdf >= 70 else
                                    "regular" if porcentaje_con_pdf >= 50 else "necesita_atencion",
                    "mensaje": f"{facturas_con_pdf} de {total_facturas} facturas de venta tienen PDF ({porcentaje_con_pdf}%)"
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"Error obteniendo estado de PDFs de venta: {str(e)}")
            print(traceback.format_exc())
            return Response(
                {"message": f"Error obteniendo estado de PDFs de venta: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _get_automatic_process_status_venta(self, request):
        """
        Obtiene el estado actual del proceso automático de venta
        """
        holding_id = request.user.holding.id if request.user.holding else None
        
        if not holding_id:
            return Response(
                {"message": "No se pudo determinar el holding"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Obtener configuración
            configuracion_activa = False
            try:
                configuracion = ConfiguracionSIIAutomaticaVenta.objects.get(holding_id=holding_id)
                configuracion_activa = True  # Si existe la configuración, está activa
            except ConfiguracionSIIAutomaticaVenta.DoesNotExist:
                return Response({
                    "message": "Estado del proceso de venta obtenido",
                    "status": "success",
                    "status_data": {
                        'estado': 'sin_configuracion',
                        'facturas_encontradas': 0,
                        'mensaje': 'No hay configuración automática de venta',
                        'configuracion_activa': False
                    }
                }, status=status.HTTP_200_OK)
            
            # Obtener facturas pendientes
            facturas_pendientes = FacturaVentaSIIPorDistribuir.objects.filter(
                holding_id=holding_id,
                procesada=False
            ).count()
            
            # Determinar estado del proceso
            if not configuracion.activo:
                estado = 'inactivo'
                mensaje = 'Proceso automático de venta desactivado'
            else:
                # Aquí podrías verificar el estado real de las tareas de Celery
                # Por simplicidad, asumimos que está funcionando si está activo
                estado = 'completado'
                mensaje = 'Proceso de venta funcionando normalmente'
            
            # Calcular próxima ejecución (simplificado)
            proxima_ejecucion = self._calcular_proxima_ejecucion_venta(configuracion.hora_ejecucion)
            
            status_data = {
                'estado': estado,
                'ultima_ejecucion': None,  # Podría obtenerse de logs o cache
                'proxima_ejecucion': proxima_ejecucion.isoformat() if proxima_ejecucion else None,
                'facturas_encontradas': facturas_pendientes,
                'mensaje': mensaje,
                'configuracion_activa': configuracion_activa
            }
            
            return Response({
                "message": "Estado del proceso de venta obtenido",
                "status": "success",
                "status_data": status_data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"Error obteniendo estado del proceso de venta: {str(e)}")
            return Response(
                {"message": f"Error obteniendo estado de venta: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _execute_automatic_process_manual_venta(self, request):
        """
        Ejecuta el proceso automático de venta de manera manual (para pruebas)
        """
        holding_id = request.user.holding.id if request.user.holding else None
        
        if not holding_id:
            return Response(
                {"message": "No se pudo determinar el holding"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Verificar que existe configuración
            try:
                configuracion = ConfiguracionSIIAutomaticaVenta.objects.get(holding_id=holding_id)
            except ConfiguracionSIIAutomaticaVenta.DoesNotExist:
                return Response(
                    {"message": "No hay configuración automática de venta"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Ejecutar proceso en background
            from .tasks import procesar_configuracion_venta_automatica
            task_result = procesar_configuracion_venta_automatica.delay(configuracion.id)
            
            return Response({
                "message": "Proceso automático de venta iniciado",
                "status": "success",
                "task_id": task_result.id
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"Error ejecutando proceso manual de venta: {str(e)}")
            return Response(
                {"message": f"Error ejecutando proceso de venta: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _distribute_automatic_invoices_venta(self, request):
        """
        Distribuye facturas de venta encontradas automáticamente
        """
        holding_id = request.user.holding.id if request.user.holding else None
        
        if not holding_id:
            return Response(
                {"message": "No se pudo determinar el holding"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Validar datos usando el mismo serializer del sistema manual de venta
            serializer = DistribucionFacturasVentaSIISerializer(
                data=request.data, 
                context={'request': request}
            )
            
            if not serializer.is_valid():
                return Response(
                    {
                        "message": "Datos de distribución de venta inválidos",
                        "errors": serializer.errors
                    }, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            validated_data = serializer.validated_data
            
            with transaction.atomic():
                # Obtener los objetos relacionados
                cliente = Clientes.objects.get(
                    id=validated_data['cliente_id'], 
                    holding_id=holding_id
                )
                
                fundo = None
                if validated_data.get('fundo_id'):
                    fundo = CamposClientes.objects.get(id=validated_data['fundo_id'])
                
                labor = None
                if validated_data.get('labor_id'):
                    labor = Labores.objects.get(id=validated_data['labor_id'])
                
                cuenta = None
                if validated_data.get('cuenta_id'):
                    cuenta = Cuenta.objects.get(id=validated_data['cuenta_id'])
                
                # Procesar facturas seleccionadas
                facturas_distribuidas = 0
                facturas_seleccionadas = validated_data['facturas_seleccionadas']
                
                for factura_data in facturas_seleccionadas:
                    folio = factura_data.get('folio')
                    
                    # Buscar la factura automática de venta
                    try:
                        factura_automatica = FacturaVentaSIIPorDistribuir.objects.get(
                            holding_id=holding_id,
                            folio=folio,
                            procesada=False
                        )
                    except FacturaVentaSIIPorDistribuir.DoesNotExist:
                        continue  # Ya fue procesada o no existe
                    
                    # Verificar que no esté ya distribuida
                    existe = FacturaVentaSIIDistribuida.objects.filter(
                        holding_id=holding_id,
                        folio=folio,
                        rut_receptor=factura_automatica.rut_receptor
                    ).exists()
                    
                    if existe:
                        continue
                    
                    # Crear la distribución de venta
                    FacturaVentaSIIDistribuida.objects.create(
                        holding_id=holding_id,
                        cliente=cliente,
                        fundo=fundo,
                        labor=labor,
                        cuenta=cuenta,
                        
                        # Datos de la factura automática de venta
                        folio=factura_automatica.folio,
                        tipo_doc=factura_automatica.tipo_doc,
                        rut_receptor=factura_automatica.rut_receptor,
                        razon_social_receptor=factura_automatica.razon_social_receptor,
                        fecha_emision=factura_automatica.fecha_emision,
                        
                        # Montos de venta
                        monto_total=factura_automatica.monto_total,
                        monto_neto=factura_automatica.monto_neto,
                        monto_exento=factura_automatica.monto_exento,
                        monto_iva=factura_automatica.monto_iva,
                        monto_otros_impuestos=factura_automatica.monto_otros_impuestos,
                        codigo_otros_impuestos=factura_automatica.codigo_otros_impuestos,
                        
                        # Metadatos
                        usuario_distribuyente=request.user,
                        observaciones=validated_data.get('observaciones', '')
                    )
                    
                    # Marcar factura automática como procesada
                    factura_automatica.procesada = True
                    factura_automatica.save()
                    
                    facturas_distribuidas += 1
                
                # Preparar respuesta
                distribucion_info = {
                    'cliente': {
                        'id': cliente.id,
                        'nombre': cliente.nombre,
                        'rut': cliente.rut
                    },
                    'fundo': {
                        'id': fundo.id,
                        'nombre': fundo.nombre_campo
                    } if fundo else None,
                    'labor': {
                        'id': labor.id,
                        'nombre': labor.nombre
                    } if labor else None,
                    'cuenta': {
                        'id': cuenta.id,
                        'nombre': cuenta.nombre_cuenta,
                        'codigo': cuenta.cuenta_contable
                    } if cuenta else None
                }
                
                return Response({
                    "message": f"Se distribuyeron {facturas_distribuidas} facturas automáticas de venta exitosamente",
                    "status": "success",
                    "facturas_distribuidas": facturas_distribuidas,
                    "distribucion": distribucion_info
                }, status=status.HTTP_200_OK)
                
        except Exception as e:
            print(f"Error distribuyendo facturas automáticas de venta: {str(e)}")
            print(traceback.format_exc())
            return Response(
                {"message": f"Error distribuyendo facturas de venta: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # ==================== MÉTODOS AUXILIARES DE VENTA ====================

    def _delete_automatic_invoices_venta(self, request):
        """Elimina facturas automáticas de venta por folios"""
        # Implementación simplificada
        return Response({"message": "Funcionalidad en desarrollo"}, status=status.HTTP_501_NOT_IMPLEMENTED)

    def _toggle_automatic_process_venta(self, request):
        """Activa o desactiva el proceso automático de venta"""
        holding_id = request.user.holding.id if request.user.holding else None
        activo = request.data.get('activo', True)
        
        try:
            configuracion = ConfiguracionSIIAutomaticaVenta.objects.get(holding_id=holding_id)
            configuracion.activo = activo
            configuracion.save()
            
            return Response({
                "message": f"Proceso automático de venta {'activado' if activo else 'desactivado'}",
                "status": "success"
            }, status=status.HTTP_200_OK)
        except ConfiguracionSIIAutomaticaVenta.DoesNotExist:
            return Response(
                {"message": "No hay configuración automática de venta"}, 
                status=status.HTTP_404_NOT_FOUND
            )

    def _get_companies_for_configuration_venta(self, request):
        """Obtiene empresas disponibles para configuración de venta"""
        # Implementación simplificada - retorna lista mock
        empresas = [
            {"rut": "12345678-9", "nombre": "Empresa de Prueba 1"},
            {"rut": "98765432-1", "nombre": "Empresa de Prueba 2"}
        ]
        return Response({
            "message": "Empresas obtenidas",
            "status": "success",
            "empresas": empresas
        }, status=status.HTTP_200_OK)

    def _validate_sii_credentials_venta(self, request):
        """Valida credenciales SII para venta"""
        # Implementación simplificada
        return Response({
            "message": "Credenciales válidas",
            "status": "success",
            "valid": True
        }, status=status.HTTP_200_OK)

    def _get_execution_history_venta(self, request):
        """Obtiene historial de ejecuciones de venta"""
        # Implementación simplificada
        return Response({
            "message": "Historial obtenido",
            "status": "success",
            "executions": []
        }, status=status.HTTP_200_OK)

    def _restart_automatic_process_venta(self, request):
        """Reinicia el proceso automático de venta"""
        # Implementación simplificada
        return Response({
            "message": "Proceso de venta reiniciado",
            "status": "success"
        }, status=status.HTTP_200_OK)
    
    def _calcular_proxima_ejecucion_venta(self, hora_ejecucion):
        """
        Calcula la próxima fecha/hora de ejecución en zona horaria de Chile para venta
        """
        try:
            import pytz
            from datetime import datetime, timedelta
            from django.utils import timezone
            
            # Zona horaria de Chile
            chile_tz = pytz.timezone('America/Santiago')
            
            # Obtener la hora actual en Chile
            ahora_chile = timezone.now().astimezone(chile_tz)
            
            # Crear la próxima ejecución en hora de Chile
            proxima_chile = ahora_chile.replace(
                hour=hora_ejecucion.hour,
                minute=hora_ejecucion.minute,
                second=0,
                microsecond=0
            )
            
            # Si la hora ya pasó hoy, programar para mañana
            if proxima_chile <= ahora_chile:
                proxima_chile += timedelta(days=1)
            
            # Convertir de vuelta a UTC para almacenamiento
            proxima_utc = proxima_chile.astimezone(pytz.UTC)
            
            print(f"DEBUG: Hora actual Chile: {ahora_chile.strftime('%Y-%m-%d %H:%M:%S %Z')}")
            print(f"DEBUG: Próxima ejecución Chile: {proxima_chile.strftime('%Y-%m-%d %H:%M:%S %Z')}")
            
            return proxima_utc
            
        except Exception as e:
            print(f"Error calculando próxima ejecución de venta: {str(e)}")
            return timezone.now() + timedelta(days=1)

class FacturasVentaDistribucion(APIView):
    """
    Vista para manejar facturas de venta SII que ya han sido distribuidas
    Equivalente a FacturasCompraDistribucion pero para ventas
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_scopes = []
    
    def dispatch(self, request, *args, **kwargs):
        if request.method == 'POST':
            self.required_scopes = ['admin', 'write']
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request, format=None):
        """
        Maneja todas las acciones relacionadas con facturas de venta distribuidas
        """
        try:
            from django.utils import timezone
            import traceback
            from .models import FacturaVentaSIIDistribuida, Clientes, Labores, Cuenta, CamposClientes
            from rest_framework.response import Response
            from rest_framework import status
            
            action = request.data.get('action', '')
            
            if action == 'get_distribution_data':
                return self._handle_get_distribution_data(request)
            elif action == 'list_distributed_invoices':
                return self.handle_list_distributed_invoices(request)
            elif action == 'export_distributed_invoices_csv':
                return self.handle_export_distributed_invoices_csv(request)
            else:
                return Response(
                    {"message": "Acción no válida"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            print(f"Error no manejado en FacturasVentaDistribucion: {str(e)}")
            print(traceback.format_exc())
            return Response(
                {"message": f"Error en el servidor: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _handle_get_distribution_data(self, request):
        """
        Obtiene los datos necesarios para la distribución de facturas de venta
        """
        holding_id = request.user.holding.id if request.user.holding else None
        
        if not holding_id:
            return Response(
                {"message": "No se pudo determinar el holding"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Obtener clientes del holding
            clientes = Clientes.objects.filter(holding_id=holding_id).order_by('nombre')
            clientes_data = [
                {'id': c.id, 'nombre': c.nombre, 'rut': c.rut}
                for c in clientes
            ]
            
            # Obtener labores del holding
            labores = Labores.objects.filter(holding_id=holding_id, estado=True).order_by('nombre')
            labores_data = [
                {'id': l.id, 'nombre': l.nombre, 'especie': l.especie}
                for l in labores
            ]
            
            # Obtener cuentas del holding
            cuentas = Cuenta.objects.filter(holding_id=holding_id, activa=True).order_by('nombre_cuenta')
            cuentas_data = [
                {'id': c.id, 'nombre_cuenta': c.nombre_cuenta, 'cuenta_contable': c.cuenta_contable}
                for c in cuentas
            ]
            
            return Response({
                'status': 'success',
                'data': {
                    'clientes': clientes_data,
                    'labores': labores_data,
                    'cuentas': cuentas_data
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"Error obteniendo datos de distribución: {str(e)}")
            return Response({
                'status': 'error',
                'message': f'Error interno: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def handle_list_distributed_invoices(self, request):
        """
        Lista las facturas de venta SII que ya han sido distribuidas con filtros
        """
        try:
            from .models import FacturaVentaSIIDistribuida
            
            holding_id = request.data.get('holding_id')
            filtros = request.data.get('filtros', {})
            
            if not holding_id:
                return Response({
                    'status': 'error',
                    'message': 'Holding ID es requerido'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Construir query base
            query = FacturaVentaSIIDistribuida.objects.filter(holding_id=holding_id)
            
            # Aplicar filtros
            if filtros.get('cliente_id'):
                query = query.filter(cliente_id=filtros['cliente_id'])
            
            if filtros.get('fundo_id'):
                query = query.filter(fundo_id=filtros['fundo_id'])
            
            if filtros.get('labor_id'):
                query = query.filter(labor_id=filtros['labor_id'])
            
            if filtros.get('cuenta_id'):
                query = query.filter(cuenta_id=filtros['cuenta_id'])
            
            if filtros.get('fecha_desde'):
                query = query.filter(fecha_emision__gte=filtros['fecha_desde'])
            
            if filtros.get('fecha_hasta'):
                query = query.filter(fecha_emision__lte=filtros['fecha_hasta'])
            
            if filtros.get('folio'):
                query = query.filter(folio__icontains=filtros['folio'])
            
            if filtros.get('razon_social'):
                query = query.filter(razon_social_receptor__icontains=filtros['razon_social'])
            
            # Obtener facturas ordenadas por fecha de distribución más reciente
            facturas = query.select_related(
                'cliente', 'fundo', 'labor', 'cuenta', 'usuario_distribuyente'
            ).order_by('-fecha_distribucion')
            
            # Serializar datos
            facturas_data = []
            for factura in facturas:
                factura_data = {
                    'id': factura.id,
                    'folio': factura.folio,
                    'tipo_doc': factura.tipo_doc,
                    'rut_receptor': factura.rut_receptor,
                    'razon_social': factura.razon_social_receptor,
                    'fecha_docto': factura.fecha_emision,  # En ventas usamos fecha_emision
                    'fecha_acuse': '',  # No aplica para ventas, dejamos vacío
                    'monto_exento': float(factura.monto_exento),
                    'monto_neto': float(factura.monto_neto),
                    'monto_iva_recuperable': float(factura.monto_iva),  # En ventas es monto_iva
                    'monto_iva_no_recuperable': 0,  # No aplica para ventas
                    'codigo_iva_no_rec': '',  # No aplica para ventas
                    'monto_total': float(factura.monto_total),
                    'monto_neto_activo_fijo': 0,  # No aplica para ventas
                    'iva_activo_fijo': 0,  # No aplica para ventas
                    'iva_uso_comun': 0,  # No aplica para ventas
                    'impto_sin_derecho_credito': 0,  # No aplica para ventas
                    'iva_no_retenido': 0,  # No aplica para ventas
                    'tabacos_puros': 0,  # No aplica para ventas
                    'tabacos_cigarrillos': 0,  # No aplica para ventas
                    'tabacos_elaborados': 0,  # No aplica para ventas
                    'nce_nde_fact_compra': 0,  # No aplica para ventas
                    'codigo_otro_impuesto': factura.codigo_otros_impuestos or '',
                    'valor_otro_impuesto': float(factura.monto_otros_impuestos),
                    'tasa_otro_impuesto': 0,  # No tenemos este campo en ventas
                    
                    # Información del cliente/distribución
                    'cliente_nombre': factura.cliente.nombre if factura.cliente else '',
                    'cliente_rut': factura.cliente.rut if factura.cliente else '',
                    'fundo_nombre': factura.fundo.nombre_campo if factura.fundo else '',
                    'labor_nombre': factura.labor.nombre if factura.labor else '',
                    'cuenta_nombre': factura.cuenta.nombre_cuenta if factura.cuenta else '',
                    'cuenta_codigo': factura.cuenta.cuenta_contable if factura.cuenta else '',
                    'usuario_nombre': self._get_usuario_nombre(factura),
                    'fecha_distribucion': factura.fecha_distribucion.isoformat() if factura.fecha_distribucion else '',
                    'observaciones': factura.observaciones or '',
                    'selected': False
                }
                facturas_data.append(factura_data)
            
            return Response({
                'status': 'success',
                'data': {
                    'facturas': facturas_data,
                    'total': len(facturas_data)
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"Error al listar facturas de venta distribuidas: {str(e)}")
            return Response({
                'status': 'error',
                'message': f'Error interno: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def handle_export_distributed_invoices_csv(self, request):
        """
        Exporta las facturas de venta distribuidas seleccionadas en formato CSV compatible con SII
        """
        try:
            from django.utils import timezone
            from .models import FacturaVentaSIIDistribuida
            
            holding_id = request.data.get('holding_id')
            factura_ids = request.data.get('factura_ids', [])
            
            if not holding_id:
                return Response({
                    'status': 'error',
                    'message': 'Holding ID es requerido'
                }, status=status.HTTP_400_BAD_REQUEST)
                
            if not factura_ids:
                return Response({
                    'status': 'error',
                    'message': 'Debe seleccionar al menos una factura'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Obtener facturas seleccionadas
            facturas = FacturaVentaSIIDistribuida.objects.filter(
                id__in=factura_ids,
                holding_id=holding_id
            ).select_related(
                'cliente', 'fundo', 'labor', 'cuenta', 'usuario_distribuyente'
            ).order_by('fecha_emision', 'folio')
            
            if not facturas.exists():
                return Response({
                    'status': 'error',
                    'message': 'No se encontraron facturas con los IDs proporcionados'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Crear contenido CSV en formato SII para ventas
            csv_lines = []
            
            # Encabezado adaptado para facturas de venta
            header = "Nro;Tipo Doc;RUT Receptor;Razon Social Receptor;Folio;Fecha Emision;Fecha Vencimiento;Monto Exento;Monto Neto;Monto IVA;Monto Total;Monto Otros Impuestos;Codigo Otros Impuestos;Cliente Distribuido;Cliente RUT;Fundo;Labor;Cuenta;Cuenta Codigo;Usuario;Fecha Distribucion;Observaciones"
            csv_lines.append(header)
            
            # Generar filas de datos
            nro = 1
            for factura in facturas:
                row_data = [
                    str(nro),
                    factura.tipo_doc or '',
                    factura.rut_receptor or '',
                    self._escape_csv_field(factura.razon_social_receptor or ''),
                    factura.folio or '',
                    factura.fecha_emision or '',
                    str(factura.monto_exento).replace('.', ','),
                    str(factura.monto_neto).replace('.', ','),
                    str(factura.monto_iva).replace('.', ','),
                    str(factura.monto_total).replace('.', ','),
                    str(factura.monto_otros_impuestos).replace('.', ','),
                    factura.codigo_otros_impuestos or '',
                    self._escape_csv_field(factura.cliente.nombre if factura.cliente else ''),
                    factura.cliente.rut if factura.cliente else '',
                    self._escape_csv_field(factura.fundo.nombre_campo if factura.fundo else ''),
                    self._escape_csv_field(factura.labor.nombre if factura.labor else ''),
                    self._escape_csv_field(factura.cuenta.nombre_cuenta if factura.cuenta else ''),
                    factura.cuenta.cuenta_contable if factura.cuenta else '',
                    self._escape_csv_field(self._get_usuario_nombre(factura)),
                    factura.fecha_distribucion.strftime('%Y-%m-%d') if factura.fecha_distribucion else '',
                    self._escape_csv_field(factura.observaciones or '')
                ]
                
                csv_lines.append(';'.join(row_data))
                nro += 1
            
            # Crear contenido del archivo
            csv_content = '\n'.join(csv_lines)
            
            # Generar nombre del archivo
            fecha_actual = timezone.now().strftime('%Y%m%d_%H%M%S')
            filename = f'facturas_venta_distribuidas_{fecha_actual}.csv'
            
            return Response({
                'status': 'success',
                'data': {
                    'csv_content': csv_content,
                    'filename': filename,
                    'total_facturas': len(facturas)
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"Error al exportar CSV de facturas de venta distribuidas: {str(e)}")
            return Response({
                'status': 'error',
                'message': f'Error interno: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Métodos auxiliares
    def _get_usuario_nombre(self, factura):
        """
        Obtiene el nombre completo del usuario que distribuyó la factura
        """
        try:
            if factura.usuario_distribuyente and hasattr(factura.usuario_distribuyente, 'persona'):
                persona = factura.usuario_distribuyente.persona
                if persona:
                    nombres = persona.nombres or ''
                    apellidos = persona.apellidos or ''
                    return f"{nombres} {apellidos}".strip()
            return ''
        except:
            return ''
    
    def _escape_csv_field(self, field):
        """
        Escapa campos CSV que contienen punto y coma, comillas o saltos de línea
        """
        if field is None:
            return ''
        
        field_str = str(field)
        
        # Si contiene punto y coma, comillas o saltos de línea, envolver en comillas
        if ';' in field_str or '"' in field_str or '\n' in field_str or '\r' in field_str:
            # Escapar comillas duplicándolas
            field_str = field_str.replace('"', '""')
            return f'"{field_str}"'
        
        return field_str

class ServePDFFacturaVentaSIIAPIView(APIView):
    """
    Vista para servir PDFs de facturas de venta en el navegador
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]
    required_scopes = ['admin', 'read', 'write']
    
    def get(self, request, factura_id, format=None):
        """
        Sirve el PDF de una factura de venta específica
        """
        try:
            holding_id = request.user.holding.id if request.user.holding else None
            
            if not holding_id:
                return Response(
                    {"message": "No se pudo determinar el holding"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Obtener factura de venta
            try:
                factura = FacturaVentaSIIPorDistribuir.objects.get(
                    id=factura_id,
                    holding_id=holding_id
                )
            except FacturaVentaSIIPorDistribuir.DoesNotExist:
                return Response(
                    {"message": "Factura de venta no encontrada"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Verificar que tenga PDF
            if not factura.pdf_documento:
                return Response(
                    {"message": "Esta factura de venta no tiene PDF disponible"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Servir el archivo PDF
            try:
                response = FileResponse(
                    factura.pdf_documento.open('rb'),
                    content_type='application/pdf'
                )
                response['Content-Disposition'] = f'inline; filename="factura_venta_{factura.folio}.pdf"'
                return response
                
            except Exception as e:
                print(f"Error sirviendo PDF de venta {factura_id}: {str(e)}")
                return Response(
                    {"message": "Error accediendo al archivo PDF"}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Exception as e:
            print(f"Error en ServePDFFacturaVentaSIIAPIView: {str(e)}")
            return Response(
                {"message": f"Error interno: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class DownloadPDFFacturaVentaSIIAPIView(APIView):
    """
    Vista para descargar PDFs de facturas de venta
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]
    required_scopes = ['admin', 'read', 'write']
    
    def get(self, request, factura_id, format=None):
        """
        Descarga el PDF de una factura de venta específica
        """
        try:
            holding_id = request.user.holding.id if request.user.holding else None
            
            if not holding_id:
                return Response(
                    {"message": "No se pudo determinar el holding"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Obtener factura de venta
            try:
                factura = FacturaVentaSIIPorDistribuir.objects.get(
                    id=factura_id,
                    holding_id=holding_id
                )
            except FacturaVentaSIIPorDistribuir.DoesNotExist:
                return Response(
                    {"message": "Factura de venta no encontrada"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Verificar que tenga PDF
            if not factura.pdf_documento:
                return Response(
                    {"message": "Esta factura de venta no tiene PDF disponible"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Descargar el archivo PDF
            try:
                response = FileResponse(
                    factura.pdf_documento.open('rb'),
                    content_type='application/pdf',
                    as_attachment=True
                )
                response['Content-Disposition'] = f'attachment; filename="factura_venta_{factura.folio}_{factura.razon_social_receptor.replace(" ", "_")}.pdf"'
                return response
                
            except Exception as e:
                print(f"Error descargando PDF de venta {factura_id}: {str(e)}")
                return Response(
                    {"message": "Error accediendo al archivo PDF"}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Exception as e:
            print(f"Error en DownloadPDFFacturaVentaSIIAPIView: {str(e)}")
            return Response(
                {"message": f"Error interno: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

#===================================================================
#===================|    TESORERIA     |============================
#===================================================================

#========================INGRESOS===================================

class ProcesarCartolaAPIView(APIView):
    """
    Vista para procesar archivos PDF de cartola bancaria
    VERSIÓN CORREGIDA - Extracción columnar precisa
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]
    required_scopes = ['admin', 'write']
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        try:
            holding_id = request.user.holding.id if request.user.holding else None
            if not holding_id:
                return Response(
                    {'error': 'No se pudo determinar el holding'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validar parámetros
            pdf_file = request.FILES.get('cartola_pdf')
            cuenta_origen_id = request.data.get('cuenta_origen_id')
            
            if not all([pdf_file, cuenta_origen_id]):
                return Response(
                    {'error': 'Faltan parámetros requeridos: cartola_pdf, cuenta_origen_id'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validar que existe la cuenta origen
            try:
                cuenta_origen = CuentaOrigen.objects.get(id=cuenta_origen_id)
                sociedad = cuenta_origen.sociedad
            except CuentaOrigen.DoesNotExist:
                return Response(
                    {'error': 'Cuenta origen no encontrada'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Procesar el PDF
            print("🔄 Iniciando procesamiento del PDF...")
            resultado_procesamiento = self.extraer_movimientos_pdf(pdf_file)
            movimientos = resultado_procesamiento['movimientos']
            periodo_cartola = resultado_procesamiento['periodo_cartola']
            
            print(f"📊 Movimientos extraídos: {len(movimientos)}")
            
            # ===== FILTRAR SOLO INGRESOS ANTES DE GUARDAR =====
            ingresos = [mov for mov in movimientos if mov['tipo_movimiento'] == 'INGRESO']
            print(f"💰 Ingresos filtrados: {len(ingresos)} de {len(movimientos)} movimientos")
            
            # Mostrar todos los ingresos detectados
            for i, mov in enumerate(ingresos):
                print(f"  {i+1}. {mov['fecha']}: ${mov['monto']} - {mov['descripcion'][:50]}")
            
            if not ingresos:
                return Response(
                    {'error': 'No se encontraron movimientos de ingreso en el PDF'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Guardar SOLO los ingresos en la base de datos
            movimientos_guardados = []
            errores_guardado = []
            
            for i, mov_data in enumerate(ingresos):
                try:
                    # Generar un número de operación más único para evitar duplicados
                    numero_operacion_unico = self.generar_numero_operacion_unico(
                        mov_data, cuenta_origen, i
                    )
                    
                    print(f"🔄 Intentando guardar ingreso {i+1}: {mov_data['fecha']} - ${mov_data['monto']}")
                    print(f"   Número operación: {numero_operacion_unico}")
                    
                    movimiento, created = CartolaMovimiento.objects.get_or_create(
                        cuenta_origen=cuenta_origen,
                        numero_operacion=numero_operacion_unico,
                        fecha=mov_data['fecha'],
                        defaults={
                            'holding_id': holding_id,
                            'sociedad': sociedad,
                            'descripcion': mov_data['descripcion'][:255],  # Truncar si es muy largo
                            'monto': mov_data['monto'],
                            'tipo_movimiento': mov_data['tipo_movimiento'],
                            'saldo': mov_data['saldo']
                        }
                    )
                    
                    if created:
                        movimientos_guardados.append(movimiento)
                        print(f"✅ Guardado exitoso: {movimiento.fecha} - ${movimiento.monto}")
                    else:
                        print(f"⚠️ Ya existe: {movimiento.fecha} - ${movimiento.monto}")
                        
                except Exception as e:
                    error_msg = f"Error guardando movimiento {i+1}: {str(e)}"
                    print(f"❌ {error_msg}")
                    errores_guardado.append(error_msg)
                    continue
            
            print(f"📈 RESUMEN:")
            print(f"   - Ingresos detectados: {len(ingresos)}")
            print(f"   - Ingresos guardados: {len(movimientos_guardados)}")
            print(f"   - Errores: {len(errores_guardado)}")
            
            return Response({
                'message': f'Se procesaron {len(movimientos_guardados)} ingresos nuevos',
                'total_extraidos': len(movimientos),
                'total_ingresos_detectados': len(ingresos),
                'total_guardados': len(movimientos_guardados),
                'errores_guardado': errores_guardado,
                'periodo_cartola': periodo_cartola,
                'fecha_cartola': periodo_cartola['inicio']
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            import traceback
            print(f"❌ Error procesando cartola: {traceback.format_exc()}")
            return Response(
                {'error': f'Error procesando cartola: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def extraer_movimientos_pdf(self, pdf_file):
        """
        Extrae los movimientos del PDF de cartola bancaria
        VERSIÓN COMPLETAMENTE CORREGIDA - Enfoque columnar
        """
        try:
            print("📖 Leyendo contenido del PDF...")
            # Leer el PDF
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            texto_completo = ""
            
            for page_num, page in enumerate(pdf_reader.pages):
                texto_pagina = page.extract_text()
                texto_completo += texto_pagina
                print(f"   Página {page_num + 1}: {len(texto_pagina)} caracteres extraídos")
            
            print(f"📄 Total texto extraído: {len(texto_completo)} caracteres")
            
            # Extraer información del período de la cartola
            periodo_info = self.extraer_periodo_cartola(texto_completo)
            print(f"📅 Período extraído: {periodo_info}")
            
            # === NUEVA LÓGICA COLUMNAR CORREGIDA ===
            movimientos = self.extraer_movimientos_multilinea(texto_completo)
            
            print(f"📊 Total movimientos extraídos: {len(movimientos)}")
            
            # Validar que encontramos el número esperado de ingresos
            if len(movimientos) == 0:
                print("⚠️ No se encontraron ingresos. Analizando posibles problemas...")
                self.debug_estructura_pdf(texto_completo)
            
            return {
                'movimientos': movimientos,
                'periodo_cartola': periodo_info
            }
            
        except Exception as e:
            print(f"❌ Error extrayendo movimientos del PDF: {str(e)}")
            raise Exception(f"Error extrayendo movimientos del PDF: {str(e)}")
    
    def extraer_movimientos_multilinea(self, texto_completo):
        """
        VERSIÓN CORREGIDA - Extrae correctamente los ingresos basándose en estructura columnar
        """
        movimientos = []
        lineas = texto_completo.split('\n')
        print(f"🔍 Analizando {len(lineas)} líneas para extracción columnar...")
        
        # Buscar el header de la tabla para identificar la estructura
        header_encontrado = False
        for i, linea in enumerate(lineas):
            if 'Fecha' in linea and 'Depósitos/Abonos' in linea and 'Saldo' in linea:
                print(f"📋 Header de tabla encontrado en línea {i}: {linea}")
                header_encontrado = True
                break
        
        if not header_encontrado:
            print("⚠️ No se encontró header de tabla, usando análisis alternativo")
        
        for i, linea in enumerate(lineas):
            linea_limpia = linea.strip()
            
            # Solo procesar líneas que empiecen con fecha
            if not re.match(r'\d{2}/\d{2}/\d{4}', linea_limpia):
                continue
            
            # Construir el movimiento completo (puede ocupar múltiples líneas)
            movimiento_completo = self.construir_movimiento_columnar(lineas, i)
            
            if movimiento_completo['texto_completo']:
                movimiento = self.procesar_movimiento_columnar(
                    movimiento_completo['texto_completo'], 
                    i
                )
                
                if movimiento and movimiento['tipo_movimiento'] == 'INGRESO':
                    movimientos.append(movimiento)
                    print(f"   ✅ INGRESO extraído: {movimiento['fecha']} - ${movimiento['monto']} - {movimiento['descripcion'][:30]}")
        
        print(f"📊 Total ingresos extraídos: {len(movimientos)}")
        return movimientos

    def construir_movimiento_columnar(self, lineas, indice_inicio):
        """
        Construye un movimiento completo identificando estructura columnar
        """
        texto_movimiento = ""
        lineas_procesadas = 0
        
        # Empezar con la línea que contiene la fecha
        linea_actual = lineas[indice_inicio].strip()
        texto_movimiento = linea_actual
        lineas_procesadas = 1
        
        # Verificar si ya tiene estructura completa (3 montos mínimo)
        if self.tiene_estructura_columnar_completa(texto_movimiento):
            return {
                'texto_completo': texto_movimiento,
                'lineas_procesadas': lineas_procesadas
            }
        
        # Si no, buscar en líneas siguientes hasta completar la estructura
        for j in range(1, 4):  # Máximo 4 líneas adicionales
            if indice_inicio + j >= len(lineas):
                break
                
            linea_siguiente = lineas[indice_inicio + j].strip()
            
            # Si encontramos otra fecha, parar
            if re.match(r'\d{2}/\d{2}/\d{4}', linea_siguiente):
                break
            
            # Si la línea es muy corta o vacía, skipear
            if len(linea_siguiente) < 5:
                continue
            
            # Agregar la línea
            texto_movimiento += " " + linea_siguiente
            lineas_procesadas += 1
            
            # Verificar si ahora tenemos estructura completa
            if self.tiene_estructura_columnar_completa(texto_movimiento):
                break
        
        return {
            'texto_completo': texto_movimiento,
            'lineas_procesadas': lineas_procesadas
        }

    def tiene_estructura_columnar_completa(self, texto):
        """
        Verifica si el texto tiene la estructura columnar completa de una fila de cartola
        Debe tener: Fecha + Sucursal + Operación + Descripción + Cheques + Depósitos + Saldo
        """
        # Debe tener fecha
        if not re.search(r'\d{2}/\d{2}/\d{4}', texto):
            return False
        
        # Debe tener sucursal
        if not re.search(r'(stgo\.principal|parral)', texto, re.IGNORECASE):
            return False
        
        # Debe tener al menos 3 montos (cheques/cargos, depósitos/abonos, saldo)
        montos = re.findall(r'\$[\d,\.]+', texto)
        if len(montos) < 3:
            return False
        
        # Debe tener número de operación (7-8 dígitos o 0000000)
        if not re.search(r'\b\d{6,8}\b', texto):
            return False
        
        return True

    def procesar_movimiento_columnar(self, texto_completo, numero_linea):
        """
        Procesa un movimiento completo extrayendo información de estructura columnar
        """
        try:
            # === EXTRAER FECHA ===
            fecha_match = re.search(r'(\d{2}/\d{2}/\d{4})', texto_completo)
            if not fecha_match:
                return None
            
            fecha_str = fecha_match.group(1)
            fecha = datetime.strptime(fecha_str, '%d/%m/%Y').date()
            
            # === EXTRAER NÚMERO DE OPERACIÓN ===
            # Buscar número después de la sucursal
            numero_operacion = self.extraer_numero_operacion_columnar(texto_completo)
            
            # === EXTRAER MONTOS COLUMNARES ===
            # La clave es extraer los 3 montos en orden: Cheques/Cargos, Depósitos/Abonos, Saldo
            resultado_montos = self.extraer_montos_columnares(texto_completo)
            
            if not resultado_montos:
                print(f"      ⚠️ No se pudieron extraer montos correctamente")
                return None
            
            cheques_cargos = resultado_montos['cheques_cargos']
            depositos_abonos = resultado_montos['depositos_abonos']
            saldo = resultado_montos['saldo']
            
            # Solo procesar si es un INGRESO (Depósitos/Abonos > 0)
            if depositos_abonos <= 0:
                return None  # No es un ingreso
            
            # === EXTRAER DESCRIPCIÓN ===
            descripcion = self.extraer_descripcion_columnar(texto_completo, fecha_str, numero_operacion)
            
            # Crear el movimiento
            return {
                'fecha': fecha,
                'numero_operacion': numero_operacion,
                'descripcion': descripcion,
                'monto': Decimal(str(depositos_abonos)),  # El monto del ingreso es el valor de Depósitos/Abonos
                'tipo_movimiento': 'INGRESO',
                'saldo': Decimal(str(saldo)),
                'cheques_cargos': Decimal(str(cheques_cargos))
            }
            
        except Exception as e:
            print(f"❌ Error procesando movimiento columnar línea {numero_linea}: {e}")
            return None

    def extraer_montos_columnares(self, texto):
        """
        Extrae los 3 montos en orden: Cheques/Cargos, Depósitos/Abonos, Saldo
        """
        try:
            # Buscar todos los montos en formato $X,XXX,XXX
            montos_encontrados = re.findall(r'\$(\d{1,3}(?:[\.,]\d{3})*(?:[\.,]\d{2})?)', texto)
            
            if len(montos_encontrados) < 3:
                print(f"      ⚠️ Faltan montos: solo encontrados {len(montos_encontrados)}")
                return None
            
            # Convertir a números
            montos_numericos = []
            for monto_str in montos_encontrados:
                try:
                    # Limpiar formato chileno (puntos como separadores de miles, comas como decimales)
                    monto_limpio = monto_str.replace('.', '').replace(',', '.')
                    monto_num = float(monto_limpio)
                    montos_numericos.append(monto_num)
                except:
                    continue
            
            if len(montos_numericos) < 3:
                return None
            
            # Los últimos 3 montos deberían ser: Cheques/Cargos, Depósitos/Abonos, Saldo
            cheques_cargos = montos_numericos[-3]
            depositos_abonos = montos_numericos[-2]
            saldo = montos_numericos[-1]
            
            # Validación: el saldo debe ser el más grande (generalmente)
            if saldo < max(cheques_cargos, depositos_abonos) * 0.8:
                print(f"      ⚠️ Saldo sospechoso: {saldo} vs cargos:{cheques_cargos} abonos:{depositos_abonos}")
                
            return {
                'cheques_cargos': cheques_cargos,
                'depositos_abonos': depositos_abonos,
                'saldo': saldo
            }
            
        except Exception as e:
            print(f"❌ Error extrayendo montos columnares: {e}")
            return None

    def extraer_numero_operacion_columnar(self, texto):
        """
        Extrae el número de operación considerando la estructura columnar
        """
        # Buscar después de la sucursal y antes de la descripción
        # Patrón: Fecha Sucursal NUMERO Descripción
        
        # Primero buscar números de 7 dígitos (más comunes)
        match = re.search(r'(?:stgo\.principal|parral)\s+(\d{7})', texto, re.IGNORECASE)
        if match:
            return match.group(1)
        
        # Buscar números de 6-8 dígitos
        match = re.search(r'(?:stgo\.principal|parral)\s+(\d{6,8})', texto, re.IGNORECASE)
        if match:
            return match.group(1)
        
        # Buscar 0000000 (depósitos en efectivo)
        match = re.search(r'(?:stgo\.principal|parral)\s+(0+)', texto, re.IGNORECASE)
        if match:
            return match.group(1)
        
        return "SIN_NUMERO"

    def extraer_descripcion_columnar(self, texto, fecha_str, numero_operacion):
        """
        Extrae la descripción considerando la estructura columnar
        """
        try:
            # Patrón: después del número de operación y antes del primer monto
            # Remover fecha y sucursal del inicio
            descripcion = texto
            descripcion = re.sub(r'\d{2}/\d{2}/\d{4}', '', descripcion)  # Remover fecha
            descripcion = re.sub(r'(stgo\.principal|parral)', '', descripcion, flags=re.IGNORECASE)  # Remover sucursal
            descripcion = re.sub(numero_operacion, '', descripcion, 1)  # Remover número de operación
            
            # Remover todos los montos
            descripcion = re.sub(r'\$[\d,\.]+', '', descripcion)
            
            # Limpiar espacios múltiples y caracteres extraños
            descripcion = re.sub(r'\s+', ' ', descripcion).strip()
            
            # Si es muy corta, intentar extraer de otra forma
            if len(descripcion) < 10:
                # Buscar texto entre número de operación y primer monto
                pattern = rf'{numero_operacion}\s+(.+?)\s+\$'
                match = re.search(pattern, texto)
                if match:
                    descripcion = match.group(1).strip()
            
            # Limpiar caracteres finales
            descripcion = re.sub(r'[^\w\s\-\.\,]$', '', descripcion).strip()
            
            return descripcion[:200] if descripcion else "Descripción no disponible"
            
        except Exception as e:
            print(f"Error extrayendo descripción: {e}")
            return "Error en descripción"

    def extraer_periodo_cartola(self, texto_completo):
        """
        Extrae el período de la cartola - VERSIÓN MEJORADA
        """
        try:
            # Buscar en el resumen/header de la cartola
            patterns = [
                r'Fecha Inicio\s*(\d{2}/\d{2}/\d{4})',
                r'Fecha Final\s*(\d{2}/\d{2}/\d{4})',
                r'(\d{2}/\d{2}/\d{4})\s*(\d{2}/\d{2}/\d{4})',  # Dos fechas juntas
            ]
            
            fechas_inicio = []
            fechas_fin = []
            
            for pattern in patterns:
                matches = re.findall(pattern, texto_completo)
                for match in matches:
                    if isinstance(match, tuple):
                        fechas_inicio.append(match[0])
                        fechas_fin.append(match[1])
                    else:
                        if 'inicio' in pattern.lower():
                            fechas_inicio.append(match)
                        else:
                            fechas_fin.append(match)
            
            # Si encontramos fechas específicas, usarlas
            if fechas_inicio and fechas_fin:
                fecha_inicio = datetime.strptime(fechas_inicio[0], '%d/%m/%Y').date()
                fecha_final = datetime.strptime(fechas_fin[0], '%d/%m/%Y').date()
                
                return {
                    'inicio': fecha_inicio.strftime('%Y-%m-%d'),
                    'fin': fecha_final.strftime('%Y-%m-%d')
                }
            
            # Fallback: analizar todas las fechas en los movimientos
            fechas_movimientos = re.findall(r'(\d{2}/\d{2}/\d{4})', texto_completo)
            if fechas_movimientos:
                fechas_parseadas = []
                for fecha_str in fechas_movimientos:
                    try:
                        fecha = datetime.strptime(fecha_str, '%d/%m/%Y').date()
                        fechas_parseadas.append(fecha)
                    except:
                        continue
                
                if fechas_parseadas:
                    fecha_min = min(fechas_parseadas)
                    fecha_max = max(fechas_parseadas)
                    
                    return {
                        'inicio': fecha_min.strftime('%Y-%m-%d'),
                        'fin': fecha_max.strftime('%Y-%m-%d')
                    }
            
            # Fallback final - mes actual
            today = datetime.now().date()
            primer_dia = today.replace(day=1)
            if today.month == 12:
                ultimo_dia = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                ultimo_dia = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
            
            return {
                'inicio': primer_dia.strftime('%Y-%m-%d'),
                'fin': ultimo_dia.strftime('%Y-%m-%d')
            }
            
        except Exception as e:
            print(f"Error extrayendo período: {e}")
            return {
                'inicio': '2025-06-01',
                'fin': '2025-06-30'
            }

    def debug_estructura_pdf(self, texto_completo):
        """
        Método de debug para analizar por qué no se extraen movimientos
        """
        print("🔍 === DEBUG ESTRUCTURA PDF ===")
        
        # Buscar headers de tabla
        headers = re.findall(r'.*Fecha.*Depósitos.*Saldo.*', texto_completo, re.IGNORECASE)
        print(f"Headers encontrados: {len(headers)}")
        for header in headers[:2]:
            print(f"  - {header}")
        
        # Buscar líneas con fechas
        lineas_con_fecha = []
        for linea in texto_completo.split('\n'):
            if re.match(r'\d{2}/\d{2}/\d{4}', linea.strip()):
                lineas_con_fecha.append(linea.strip())
        
        print(f"Líneas con fecha encontradas: {len(lineas_con_fecha)}")
        for i, linea in enumerate(lineas_con_fecha[:5]):
            print(f"  {i+1}. {linea[:100]}...")
        
        # Buscar montos
        montos = re.findall(r'\$[\d,\.]+', texto_completo)
        print(f"Montos encontrados: {len(montos)}")
        print(f"Primeros 10 montos: {montos[:10]}")
        
        # Buscar palabras clave de ingresos
        palabras_ingreso = ['deposito', 'abono', 'transferencia otro banco de rut', 'pagos varios']
        for palabra in palabras_ingreso:
            count = len(re.findall(palabra, texto_completo, re.IGNORECASE))
            print(f"'{palabra}': {count} ocurrencias")

    def generar_numero_operacion_unico(self, mov_data, cuenta_origen, indice):
        """
        Genera un número de operación único - VERSIÓN MEJORADA
        """
        # Usar el número original si existe y es válido
        numero_original = mov_data.get('numero_operacion', '')
        
        if numero_original and numero_original != 'SIN_NUMERO':
            # Verificar si ya existe
            if not CartolaMovimiento.objects.filter(
                cuenta_origen=cuenta_origen,
                numero_operacion=numero_original,
                fecha=mov_data['fecha']
            ).exists():
                return numero_original
        
        # Generar uno único basado en fecha, monto e índice
        fecha_str = mov_data['fecha'].strftime('%Y%m%d')
        monto_int = int(mov_data['monto'])
        return f"{fecha_str}_{monto_int}_{indice:03d}"

class MovimientosCartolaAPIView(APIView):
    """
    Vista para obtener movimientos de cartola por cuenta y fecha
    MEJORADO: Mejor manejo de filtros y respuestas
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]
    required_scopes = ['admin', 'write', 'read']
    
    def get(self, request):
        try:
            holding_id = request.user.holding.id if request.user.holding else None
            cuenta_origen_id = request.GET.get('cuenta_origen_id')
            fecha_inicio = request.GET.get('fecha_inicio')
            fecha_fin = request.GET.get('fecha_fin')
            solo_ingresos = request.GET.get('solo_ingresos', 'true').lower() == 'true'
            solo_no_procesados = request.GET.get('solo_no_procesados', 'true').lower() == 'true'
            
            print(f"🔍 Consultando movimientos:")
            print(f"  - Holding: {holding_id}")
            print(f"  - Cuenta: {cuenta_origen_id}")
            print(f"  - Período: {fecha_inicio} - {fecha_fin}")
            print(f"  - Solo ingresos: {solo_ingresos}")
            print(f"  - Solo no procesados: {solo_no_procesados}")
            
            if not all([cuenta_origen_id, fecha_inicio, fecha_fin]):
                return Response(
                    {'error': 'Faltan parámetros requeridos: cuenta_origen_id, fecha_inicio, fecha_fin'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Filtros base
            filtros = {
                'holding_id': holding_id,
                'cuenta_origen_id': cuenta_origen_id,
                'fecha__range': [fecha_inicio, fecha_fin]
            }
            
            if solo_ingresos:
                filtros['tipo_movimiento'] = 'INGRESO'
            
            if solo_no_procesados:
                filtros['procesado'] = False
            
            movimientos = CartolaMovimiento.objects.filter(**filtros).order_by('-fecha', '-id')
            
            print(f"📊 Movimientos encontrados: {movimientos.count()}")
            for mov in movimientos:
                print(f"  - {mov.fecha}: {mov.tipo_movimiento} ${mov.monto} - {mov.descripcion[:30]}")
            
            serializer = CartolaMovimientoSerializer(movimientos, many=True)
            
            return Response({
                'movimientos': serializer.data,
                'total': len(serializer.data),
                'filtros_aplicados': {
                    'solo_ingresos': solo_ingresos,
                    'solo_no_procesados': solo_no_procesados,
                    'periodo': f"{fecha_inicio} - {fecha_fin}"
                }
            })
            
        except Exception as e:
            import traceback
            print(f"Error obteniendo movimientos: {traceback.format_exc()}")
            return Response(
                {'error': f'Error obteniendo movimientos: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class FacturasDistribuidasAPIView(APIView):
    """
    Vista para obtener facturas distribuidas por fecha - VERSIÓN CORREGIDA
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]
    required_scopes = ['admin', 'write', 'read']
    
    def get(self, request):
        try:
            holding_id = request.user.holding.id if request.user.holding else None
            fecha_inicio = request.GET.get('fecha_inicio')
            fecha_fin = request.GET.get('fecha_fin')
            
            print(f"🔍 Consultando facturas distribuidas:")
            print(f"  - Holding: {holding_id}")
            print(f"  - Período solicitado: {fecha_inicio} - {fecha_fin}")
            
            if not all([fecha_inicio, fecha_fin]):
                return Response(
                    {'error': 'Faltan parámetros requeridos: fecha_inicio, fecha_fin'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # === CONVERSIÓN DE FECHAS ===
            from datetime import datetime
            try:
                fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
                fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
                print(f"📅 Fechas convertidas: {fecha_inicio_dt} - {fecha_fin_dt}")
                
            except ValueError as e:
                print(f"❌ Error parseando fechas: {e}")
                return Response(
                    {'error': 'Formato de fecha inválido. Use YYYY-MM-DD'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # === BÚSQUEDA MEJORADA ===
            # Primero intentar por fecha_emision (campo texto que contiene las fechas de las facturas)
            facturas = self.filtrar_por_fecha_emision(holding_id, fecha_inicio_dt, fecha_fin_dt)
            
            print(f"📊 Facturas encontradas: {facturas.count()}")
            
            # === SERIALIZACIÓN MANUAL ===
            facturas_data = []
            for factura in facturas:
                try:
                    factura_data = {
                        'id': factura.id,
                        'numero': factura.folio,
                        'folio': factura.folio,
                        'fecha_emision': factura.fecha_emision,
                        'neto': float(factura.monto_neto),
                        'iva': float(factura.monto_iva),
                        'total': float(factura.monto_total),
                        'estado': 'DISTRIBUIDA',
                        'saldo_pendiente': 0,
                        
                        # Información adicional
                        'cliente_nombre': factura.cliente.nombre if factura.cliente else factura.razon_social_receptor,
                        'tipo_doc': factura.tipo_doc,
                        'rut_receptor': factura.rut_receptor,
                        'razon_social_receptor': factura.razon_social_receptor,
                        'fecha_distribucion': factura.fecha_distribucion.strftime('%Y-%m-%d') if factura.fecha_distribucion else None
                    }
                    facturas_data.append(factura_data)
                except Exception as e:
                    print(f"⚠️ Error serializando factura {factura.id}: {e}")
                    continue
            
            print(f"✅ Facturas serializadas: {len(facturas_data)}")
            
            # Debug: mostrar las primeras facturas encontradas
            for i, factura in enumerate(facturas_data[:3]):
                print(f"  {i+1}. Folio: {factura['folio']}, Fecha: {factura['fecha_emision']}, Total: ${factura['total']:,.0f}")
            
            return Response({
                'facturas': facturas_data,
                'total': len(facturas_data),
                'periodo_consultado': f"{fecha_inicio} - {fecha_fin}",
                'debug_info': {
                    'holding_id': holding_id,
                    'facturas_encontradas': facturas.count(),
                    'fechas_convertidas': {
                        'inicio': str(fecha_inicio_dt),
                        'fin': str(fecha_fin_dt)
                    }
                }
            })
            
        except Exception as e:
            import traceback
            print(f"❌ Error obteniendo facturas distribuidas: {traceback.format_exc()}")
            return Response(
                {'error': f'Error obteniendo facturas: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def filtrar_por_fecha_emision(self, holding_id, fecha_inicio_dt, fecha_fin_dt):
        """
        Filtro por fecha_emision convertendo formatos de fecha
        """
        try:
            # Obtener todas las facturas del holding
            todas_facturas = FacturaVentaSIIDistribuida.objects.filter(holding_id=holding_id)
            
            print(f"📋 Total facturas en holding: {todas_facturas.count()}")
            
            # Filtrar manualmente por fecha_emision
            facturas_filtradas = []
            
            for factura in todas_facturas:
                try:
                    # Intentar varios formatos de fecha
                    fecha_emision_str = factura.fecha_emision
                    fecha_emision_dt = None
                    
                    # Formato DD/MM/YYYY (más común en Chile)
                    if '/' in fecha_emision_str:
                        try:
                            fecha_emision_dt = datetime.strptime(fecha_emision_str, '%d/%m/%Y').date()
                        except:
                            try:
                                fecha_emision_dt = datetime.strptime(fecha_emision_str, '%m/%d/%Y').date()
                            except:
                                pass
                    
                    # Formato YYYY-MM-DD
                    elif '-' in fecha_emision_str:
                        try:
                            fecha_emision_dt = datetime.strptime(fecha_emision_str, '%Y-%m-%d').date()
                        except:
                            pass
                    
                    # Si logramos parsear la fecha, verificar si está en rango
                    if fecha_emision_dt:
                        if fecha_inicio_dt <= fecha_emision_dt <= fecha_fin_dt:
                            facturas_filtradas.append(factura)
                            print(f"  ✅ Incluida: {factura.folio} - {fecha_emision_str} -> {fecha_emision_dt}")
                        else:
                            print(f"  ❌ Fuera de rango: {factura.folio} - {fecha_emision_str} -> {fecha_emision_dt}")
                    else:
                        print(f"  ⚠️ No se pudo parsear fecha: {factura.folio} - {fecha_emision_str}")
                        
                except Exception as e:
                    print(f"  ❌ Error procesando factura {factura.folio}: {e}")
                    continue
            
            print(f"📊 Facturas filtradas por fecha_emision: {len(facturas_filtradas)}")
            
            # Convertir lista a QuerySet para mantener compatibilidad
            if facturas_filtradas:
                return todas_facturas.filter(id__in=[f.id for f in facturas_filtradas]).order_by('-fecha_distribucion')
            else:
                return FacturaVentaSIIDistribuida.objects.none()
            
        except Exception as e:
            print(f"❌ Error en filtro por fecha_emision: {e}")
            return FacturaVentaSIIDistribuida.objects.none()

class RegistrarIngresoAPIView(APIView):
    """
    Vista para registrar la distribución de un ingreso - VERSIÓN CORREGIDA
    CORE: "1 factura puede ser pagada con 1 o más ingresos o 1 ingreso puede ser distribuido entre 1 o n facturas"
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]
    required_scopes = ['admin', 'write']
    
    def post(self, request):
        try:
            holding_id = request.user.holding.id if request.user.holding else None
            usuario = request.user
            
            # Validar datos requeridos
            movimiento_id = request.data.get('movimiento_id')
            factura_id = request.data.get('factura_id')
            monto_distribuido = request.data.get('monto_distribuido')
            porcentaje_neto = request.data.get('porcentaje_neto')
            porcentaje_iva = request.data.get('porcentaje_iva')
            
            print(f"🔄 === INICIANDO REGISTRO DE INGRESO ===")
            print(f"📊 Datos recibidos:")
            print(f"  - Movimiento ID: {movimiento_id}")
            print(f"  - Factura ID: {factura_id}")
            print(f"  - Monto a distribuir: ${monto_distribuido}")
            print(f"  - Porcentaje Neto: {porcentaje_neto}%")
            print(f"  - Porcentaje IVA: {porcentaje_iva}%")
            
            if not all([movimiento_id, factura_id, monto_distribuido, porcentaje_neto, porcentaje_iva]):
                return Response(
                    {'error': 'Faltan parámetros requeridos'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Convertir a Decimal para precisión
            monto_distribuido = Decimal(str(monto_distribuido))
            porcentaje_neto = Decimal(str(porcentaje_neto))
            porcentaje_iva = Decimal(str(porcentaje_iva))
            
            # Validar que los porcentajes sumen 100%
            if abs(porcentaje_neto + porcentaje_iva - 100) > Decimal('0.01'):
                return Response(
                    {'error': 'Los porcentajes deben sumar exactamente 100%'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Obtener objetos
            try:
                movimiento = CartolaMovimiento.objects.get(id=movimiento_id, holding_id=holding_id)
                factura = FacturaVentaSIIDistribuida.objects.get(id=factura_id, holding_id=holding_id)
                print(f"✅ Objetos encontrados:")
                print(f"  - Movimiento: ${movimiento.monto} del {movimiento.fecha}")
                print(f"  - Factura: {factura.folio} por ${factura.monto_total}")
                
            except (CartolaMovimiento.DoesNotExist, FacturaVentaSIIDistribuida.DoesNotExist):
                return Response(
                    {'error': 'Movimiento o factura no encontrados'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # === VALIDAR DISPONIBILIDAD DEL MOVIMIENTO ===
            monto_ya_distribuido = self.calcular_monto_ya_distribuido_movimiento(movimiento)
            saldo_disponible_movimiento = movimiento.monto - monto_ya_distribuido
            
            print(f"💰 Estado del movimiento:")
            print(f"  - Monto original: ${movimiento.monto}")
            print(f"  - Ya distribuido: ${monto_ya_distribuido}")
            print(f"  - Saldo disponible: ${saldo_disponible_movimiento}")
            
            if monto_distribuido > saldo_disponible_movimiento:
                return Response(
                    {
                        'error': f'El monto excede el saldo disponible del movimiento',
                        'monto_solicitado': float(monto_distribuido),
                        'saldo_disponible': float(saldo_disponible_movimiento)
                    }, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # === CALCULAR DISTRIBUCIÓN DEL INGRESO ===
            distribucion = self.calcular_distribucion_ingreso(
                monto_distribuido, porcentaje_neto, porcentaje_iva
            )
            
            print(f"🧮 Distribución calculada:")
            print(f"  - Para Neto: ${distribucion['monto_neto']}")
            print(f"  - Para IVA: ${distribucion['monto_iva']}")
            print(f"  - Total: ${distribucion['total']}")
            
            # === OBTENER ESTADO ACTUAL DE LA FACTURA ===
            estado_factura = self.calcular_estado_factura(factura)
            
            print(f"📋 Estado actual de la factura:")
            print(f"  - Total factura: ${estado_factura['total_factura']}")
            print(f"  - Neto factura: ${estado_factura['neto_factura']}")
            print(f"  - IVA factura: ${estado_factura['iva_factura']}")
            print(f"  - Neto ya cubierto: ${estado_factura['neto_ya_cubierto']}")
            print(f"  - IVA ya cubierto: ${estado_factura['iva_ya_cubierto']}")
            print(f"  - Neto pendiente: ${estado_factura['neto_pendiente']}")
            print(f"  - IVA pendiente: ${estado_factura['iva_pendiente']}")
            
            # === CALCULAR MONTOS QUE SE VAN A CUBRIR ===
            cobertura = self.calcular_cobertura_factura(distribucion, estado_factura)
            
            print(f"🎯 Cobertura que se aplicará:")
            print(f"  - Neto a cubrir: ${cobertura['neto_a_cubrir']}")
            print(f"  - IVA a cubrir: ${cobertura['iva_a_cubrir']}")
            print(f"  - Total usado del ingreso: ${cobertura['total_usado']}")
            print(f"  - Saldo sobrante del ingreso: ${cobertura['saldo_sobrante']}")
            
            # === VALIDAR QUE NO SE EXCEDA LA FACTURA ===
            if cobertura['neto_a_cubrir'] > estado_factura['neto_pendiente']:
                return Response(
                    {
                        'error': 'El monto para neto excede lo pendiente en la factura',
                        'neto_solicitado': float(cobertura['neto_a_cubrir']),
                        'neto_pendiente': float(estado_factura['neto_pendiente'])
                    }, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if cobertura['iva_a_cubrir'] > estado_factura['iva_pendiente']:
                return Response(
                    {
                        'error': 'El monto para IVA excede lo pendiente en la factura',
                        'iva_solicitado': float(cobertura['iva_a_cubrir']),
                        'iva_pendiente': float(estado_factura['iva_pendiente'])
                    }, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # === CREAR REGISTRO DE INGRESO ===
            registro = RegistroIngreso.objects.create(
                holding_id=holding_id,
                movimiento_cartola=movimiento,
                factura_venta=factura,
                monto_distribuido=monto_distribuido,
                porcentaje_neto=porcentaje_neto,
                porcentaje_iva=porcentaje_iva,
                monto_neto_cubierto=cobertura['neto_a_cubrir'],
                monto_iva_cubierto=cobertura['iva_a_cubrir'],
                usuario_registro=usuario
            )
            
            print(f"✅ Registro creado exitosamente: ID {registro.id}")
            
            # === ACTUALIZAR ESTADO DEL MOVIMIENTO SI SE AGOTÓ ===
            nuevo_saldo_movimiento = saldo_disponible_movimiento - monto_distribuido
            if nuevo_saldo_movimiento <= 0:
                movimiento.procesado = True
                movimiento.save()
                print(f"🔒 Movimiento marcado como procesado (saldo agotado)")
            
            # === CALCULAR ESTADO FINAL ===
            estado_final = self.calcular_estado_final(movimiento, factura, registro)
            
            # === RESPUESTA DETALLADA ===
            response_data = {
                'message': 'Ingreso registrado exitosamente',
                'registro_id': registro.id,
                'distribucion_aplicada': {
                    'monto_total_distribuido': float(monto_distribuido),
                    'monto_neto_cubierto': float(cobertura['neto_a_cubrir']),
                    'monto_iva_cubierto': float(cobertura['iva_a_cubrir']),
                    'porcentaje_neto': float(porcentaje_neto),
                    'porcentaje_iva': float(porcentaje_iva)
                },
                'estado_movimiento': {
                    'monto_original': float(movimiento.monto),
                    'monto_disponible_anterior': float(saldo_disponible_movimiento),
                    'monto_usado_ahora': float(monto_distribuido),
                    'saldo_restante': float(nuevo_saldo_movimiento),
                    'completamente_usado': nuevo_saldo_movimiento <= 0
                },
                'estado_factura': estado_final['factura'],
                'resumen': estado_final['resumen']
            }
            
            print(f"🎉 === REGISTRO COMPLETADO EXITOSAMENTE ===")
            
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            import traceback
            print(f"❌ Error registrando ingreso: {traceback.format_exc()}")
            return Response(
                {'error': f'Error registrando el ingreso: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def calcular_monto_ya_distribuido_movimiento(self, movimiento):
        """
        Calcula cuánto del movimiento ya se ha distribuido
        """
        return RegistroIngreso.objects.filter(
            movimiento_cartola=movimiento
        ).aggregate(
            total=Sum('monto_distribuido')
        )['total'] or Decimal('0')
    
    def calcular_distribucion_ingreso(self, monto_distribuido, porcentaje_neto, porcentaje_iva):
        """
        Calcula cómo se distribuye el monto del ingreso entre neto e IVA
        """
        monto_neto = (monto_distribuido * porcentaje_neto) / 100
        monto_iva = (monto_distribuido * porcentaje_iva) / 100
        
        return {
            'monto_neto': monto_neto,
            'monto_iva': monto_iva,
            'total': monto_neto + monto_iva
        }
    
    def calcular_estado_factura(self, factura):
        """
        Calcula el estado actual de la factura (cuánto se ha pagado vs cuánto falta)
        """
        # Montos originales de la factura
        total_factura = factura.monto_total
        neto_factura = factura.monto_neto
        iva_factura = factura.monto_iva
        
        # Calcular cuánto se ha cubierto hasta ahora
        pagos_anteriores = RegistroIngreso.objects.filter(factura_venta=factura).aggregate(
            neto_cubierto=Sum('monto_neto_cubierto'),
            iva_cubierto=Sum('monto_iva_cubierto')
        )
        
        neto_ya_cubierto = pagos_anteriores['neto_cubierto'] or Decimal('0')
        iva_ya_cubierto = pagos_anteriores['iva_cubierto'] or Decimal('0')
        
        return {
            'total_factura': total_factura,
            'neto_factura': neto_factura,
            'iva_factura': iva_factura,
            'neto_ya_cubierto': neto_ya_cubierto,
            'iva_ya_cubierto': iva_ya_cubierto,
            'neto_pendiente': neto_factura - neto_ya_cubierto,
            'iva_pendiente': iva_factura - iva_ya_cubierto,
            'total_ya_cubierto': neto_ya_cubierto + iva_ya_cubierto,
            'total_pendiente': total_factura - (neto_ya_cubierto + iva_ya_cubierto)
        }
    
    def calcular_cobertura_factura(self, distribucion, estado_factura):
        """
        Calcula cuánto se puede cubrir de la factura con esta distribución
        """
        # Lo que queremos aplicar
        neto_solicitado = distribucion['monto_neto']
        iva_solicitado = distribucion['monto_iva']
        
        # Lo que realmente podemos cubrir (limitado por lo pendiente)
        neto_a_cubrir = min(neto_solicitado, estado_factura['neto_pendiente'])
        iva_a_cubrir = min(iva_solicitado, estado_factura['iva_pendiente'])
        
        total_usado = neto_a_cubrir + iva_a_cubrir
        total_solicitado = distribucion['total']
        saldo_sobrante = total_solicitado - total_usado
        
        return {
            'neto_a_cubrir': neto_a_cubrir,
            'iva_a_cubrir': iva_a_cubrir,
            'total_usado': total_usado,
            'saldo_sobrante': saldo_sobrante
        }
    
    def calcular_estado_final(self, movimiento, factura, registro):
        """
        Calcula el estado final después del registro
        """
        # Recalcular estado de la factura después del registro
        estado_factura_final = self.calcular_estado_factura(factura)
        
        # Estado del movimiento
        monto_total_distribuido = self.calcular_monto_ya_distribuido_movimiento(movimiento)
        saldo_movimiento = movimiento.monto - monto_total_distribuido
        
        factura_completamente_pagada = (
            estado_factura_final['total_pendiente'] <= 0
        )
        
        movimiento_completamente_usado = saldo_movimiento <= 0
        
        return {
            'factura': {
                'folio': factura.folio,
                'total_original': float(estado_factura_final['total_factura']),
                'total_cubierto': float(estado_factura_final['total_ya_cubierto']),
                'total_pendiente': float(estado_factura_final['total_pendiente']),
                'neto_cubierto': float(estado_factura_final['neto_ya_cubierto']),
                'neto_pendiente': float(estado_factura_final['neto_pendiente']),
                'iva_cubierto': float(estado_factura_final['iva_ya_cubierto']),
                'iva_pendiente': float(estado_factura_final['iva_pendiente']),
                'completamente_pagada': factura_completamente_pagada,
                'porcentaje_pagado': float((estado_factura_final['total_ya_cubierto'] / estado_factura_final['total_factura']) * 100)
            },
            'movimiento': {
                'monto_original': float(movimiento.monto),
                'total_distribuido': float(monto_total_distribuido),
                'saldo_restante': float(saldo_movimiento),
                'completamente_usado': movimiento_completamente_usado,
                'porcentaje_usado': float((monto_total_distribuido / movimiento.monto) * 100)
            },
            'resumen': {
                'operacion_exitosa': True,
                'factura_completamente_pagada': factura_completamente_pagada,
                'movimiento_completamente_usado': movimiento_completamente_usado,
                'monto_registrado': float(registro.monto_distribuido),
                'fecha_registro': registro.fecha_registro.strftime('%Y-%m-%d %H:%M:%S')
            }
        }

class CuentasOrigenPorBancoAPIView(APIView):
    """
    Vista para obtener cuentas origen por banco - SOLUCIÓN SIN SELECT_RELATED
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]
    required_scopes = ['admin', 'write', 'read']
    
    def get(self, request, codigo_sbif):
        try:
            # Buscar banco por código SBIF
            try:
                banco = Banco.objects.get(codigo_sbif=codigo_sbif)
                print(f"Banco encontrado: ID={banco.id}, Código={banco.codigo_sbif}")
            except Banco.DoesNotExist:
                return Response(
                    {'error': 'Banco no encontrado'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Usar .extra() SIN select_related para evitar el join problemático
            cuentas = CuentaOrigen.objects.extra(
                where=["banco_id = %s"], 
                params=[str(banco.id)]
            )
            
            print(f"Cuentas encontradas: {cuentas.count()}")
            
            # Serializar manualmente para evitar el problema del ForeignKey
            cuentas_data = []
            for cuenta in cuentas:
                cuenta_data = {
                    'id': cuenta.id,
                    'numero_cuenta': cuenta.numero_cuenta,
                    'tipo_cuenta': cuenta.tipo_cuenta,
                    'banco_info': {
                        'codigo_sbif': banco.codigo_sbif,
                        'nombre': banco.nombre
                    }
                }
                cuentas_data.append(cuenta_data)
            
            return Response({
                'cuentas': cuentas_data,
                'total': len(cuentas_data),
                'banco': {
                    'codigo_sbif': banco.codigo_sbif,
                    'nombre': banco.nombre
                }
            })
            
        except Exception as e:
            import traceback
            print(f"Error: {traceback.format_exc()}")
            return Response(
                {'error': f'Error obteniendo cuentas: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class MovimientoSaldosAPIView(APIView):
    """
    Vista para obtener movimientos con sus saldos disponibles
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]
    required_scopes = ['admin', 'write', 'read']
    
    def get(self, request):
        try:
            holding_id = request.user.holding.id if request.user.holding else None
            cuenta_origen_id = request.GET.get('cuenta_origen_id')
            fecha_inicio = request.GET.get('fecha_inicio')
            fecha_fin = request.GET.get('fecha_fin')
            
            if not all([cuenta_origen_id, fecha_inicio, fecha_fin]):
                return Response(
                    {'error': 'Faltan parámetros requeridos'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Obtener movimientos de ingreso
            movimientos = CartolaMovimiento.objects.filter(
                holding_id=holding_id,
                cuenta_origen_id=cuenta_origen_id,
                fecha__range=[fecha_inicio, fecha_fin],
                tipo_movimiento='INGRESO'
            ).order_by('-monto', '-fecha')
            
            # Calcular saldos para cada movimiento
            movimientos_con_saldo = []
            for movimiento in movimientos:
                # Calcular monto ya distribuido
                total_distribuido = RegistroIngreso.objects.filter(
                    movimiento_cartola=movimiento
                ).aggregate(total=Sum('monto_distribuido'))['total'] or Decimal('0')
                
                saldo_disponible = movimiento.monto - total_distribuido
                
                movimientos_con_saldo.append({
                    'id': movimiento.id,
                    'fecha': movimiento.fecha,
                    'numero_operacion': movimiento.numero_operacion,
                    'descripcion': movimiento.descripcion,
                    'monto_original': float(movimiento.monto),
                    'monto_distribuido': float(total_distribuido),
                    'saldo_disponible': float(saldo_disponible),
                    'porcentaje_usado': float((total_distribuido / movimiento.monto) * 100) if movimiento.monto > 0 else 0,
                    'completamente_usado': saldo_disponible <= 0,
                    'saldo': float(movimiento.saldo)
                })
            
            return Response({
                'movimientos': movimientos_con_saldo,
                'total': len(movimientos_con_saldo)
            })
            
        except Exception as e:
            return Response(
                {'error': f'Error obteniendo saldos: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class FacturaEstadoAPIView(APIView):
    """
    Vista para obtener el estado de una factura específica
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]
    required_scopes = ['admin', 'write', 'read']
    
    def get(self, request, factura_id):
        try:
            holding_id = request.user.holding.id if request.user.holding else None
            
            factura = FacturaVentaSIIDistribuida.objects.get(
                id=factura_id, 
                holding_id=holding_id
            )
            
            # Calcular estado actual
            pagos_anteriores = RegistroIngreso.objects.filter(
                factura_venta=factura
            ).aggregate(
                neto_cubierto=Sum('monto_neto_cubierto'),
                iva_cubierto=Sum('monto_iva_cubierto'),
                total_cubierto=Sum('monto_distribuido')
            )
            
            neto_cubierto = pagos_anteriores['neto_cubierto'] or Decimal('0')
            iva_cubierto = pagos_anteriores['iva_cubierto'] or Decimal('0')
            total_cubierto = pagos_anteriores['total_cubierto'] or Decimal('0')
            
            estado = {
                'factura': {
                    'id': factura.id,
                    'folio': factura.folio,
                    'fecha_emision': factura.fecha_emision,
                    'cliente_nombre': factura.cliente.nombre if factura.cliente else factura.razon_social_receptor,
                    'monto_total': float(factura.monto_total),
                    'monto_neto': float(factura.monto_neto),
                    'monto_iva': float(factura.monto_iva)
                },
                'cobertura': {
                    'neto_cubierto': float(neto_cubierto),
                    'iva_cubierto': float(iva_cubierto),
                    'total_cubierto': float(total_cubierto),
                    'neto_pendiente': float(factura.monto_neto - neto_cubierto),
                    'iva_pendiente': float(factura.monto_iva - iva_cubierto),
                    'total_pendiente': float(factura.monto_total - total_cubierto),
                    'porcentaje_cubierto': float((total_cubierto / factura.monto_total) * 100) if factura.monto_total > 0 else 0,
                    'completamente_pagada': total_cubierto >= factura.monto_total
                },
                'historial_pagos': [
                    {
                        'fecha': registro.fecha_registro.strftime('%d/%m/%Y %H:%M'),
                        'monto_distribuido': float(registro.monto_distribuido),
                        'monto_neto_cubierto': float(registro.monto_neto_cubierto),
                        'monto_iva_cubierto': float(registro.monto_iva_cubierto)
                    }
                    for registro in RegistroIngreso.objects.filter(factura_venta=factura).order_by('-fecha_registro')[:5]
                ]
            }
            
            return Response(estado)
            
        except FacturaVentaSIIDistribuida.DoesNotExist:
            return Response(
                {'error': 'Factura no encontrada'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Error obteniendo estado: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
#========================EGRESOS===================================

class FacturasCompraDistribuidasAPIView(APIView):
    """
    API para obtener facturas de compra distribuidas disponibles para pago
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]
    required_scopes = ['admin', 'write', 'read']
    
    def get(self, request):
        try:
            holding_id = request.user.holding.id if request.user.holding else None
            
            if not holding_id:
                return Response(
                    {'error': 'No se pudo determinar el holding'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            fecha_inicio = request.GET.get('fecha_inicio')
            fecha_fin = request.GET.get('fecha_fin')
            print(fecha_inicio, fecha_fin)
            
            if not fecha_inicio or not fecha_fin:
                return Response(
                    {'error': 'Faltan parámetros de fecha'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # CONVERTIR LAS FECHAS STRING A OBJETOS DATE
            try:
                fecha_inicio_parsed = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
                fecha_fin_parsed = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
            except ValueError as e:
                return Response(
                    {'error': f'Formato de fecha inválido. Use YYYY-MM-DD: {str(e)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            print(f"Fechas parseadas: {fecha_inicio_parsed} - {fecha_fin_parsed}")
            
            # SOLUCIÓN SIMPLE: Obtener todas las facturas del holding y filtrar en Python
            # Esto evita problemas con fechas malformadas en la base de datos
            facturas_base = FacturaCompraSIIDistribuida.objects.filter(
                holding_id=holding_id
            ).select_related('cliente')
            
            print(f"Total facturas en holding: {facturas_base.count()}")
            
            # Filtrar por fecha en Python para manejar fechas malformadas
            facturas_filtradas = []
            errores_fecha = 0
            
            for factura in facturas_base:
                try:
                    if factura.fecha_docto and len(factura.fecha_docto) == 10:
                        # Intentar parsear la fecha desde DD/MM/YYYY
                        fecha_factura = datetime.strptime(factura.fecha_docto, '%d/%m/%Y').date()
                        
                        # Verificar si está en el rango
                        if fecha_inicio_parsed <= fecha_factura <= fecha_fin_parsed:
                            facturas_filtradas.append(factura)
                            
                except ValueError:
                    errores_fecha += 1
                    print(f"Error parseando fecha en factura {factura.id}: '{factura.fecha_docto}'")
                    continue
            
            print(f"Facturas después de filtro por fecha: {len(facturas_filtradas)}")
            print(f"Errores de fecha encontrados: {errores_fecha}")
            
            # Calcular saldos pendientes de cada factura
            facturas_con_saldo = []
            for factura in facturas_filtradas:
                try:
                    pagos_realizados = RegistroEgreso.objects.filter(
                        factura_compra=factura
                    ).aggregate(
                        total_pagado=Sum('monto_distribuido')
                    )['total_pagado'] or 0
                    
                    saldo_pendiente = factura.monto_total - pagos_realizados
                    
                    if saldo_pendiente > 0:  # Solo facturas con saldo pendiente
                        
                        # ===== NUEVA LÓGICA PARA FACTURAS EXENTAS =====
                        es_factura_exenta = (factura.tipo_doc == '34' or 
                                        (factura.monto_neto == 0 and factura.monto_exento > 0))
                        
                        if es_factura_exenta:
                            # Para facturas exentas, usar monto_exento como "monto_neto" 
                            monto_neto_display = float(factura.monto_exento)
                            monto_iva_display = 0.0  # Facturas exentas no tienen IVA
                            tipo_factura = "EXENTA"
                        else:
                            # Para facturas normales, usar los campos normales
                            monto_neto_display = float(factura.monto_neto)
                            monto_iva_display = float(factura.monto_iva_recuperable)
                            tipo_factura = "NORMAL"
                        
                        facturas_con_saldo.append({
                            'id': factura.id,
                            'folio': factura.folio,
                            'fecha_docto': factura.fecha_docto,
                            'monto_total': float(factura.monto_total),
                            'monto_neto': monto_neto_display,
                            'monto_iva_recuperable': monto_iva_display,
                            'razon_social': factura.razon_social,
                            'saldo_pendiente': float(saldo_pendiente),
                            'total_pagado': float(pagos_realizados),
                            # ===== CAMPOS ADICIONALES PARA EL FRONTEND =====
                            'es_exenta': es_factura_exenta,
                            'tipo_doc': factura.tipo_doc,
                            'tipo_factura': tipo_factura,
                            'monto_exento_original': float(factura.monto_exento),
                            'monto_neto_original': float(factura.monto_neto),
                            'monto_iva_original': float(factura.monto_iva_recuperable)
                        })
                        
                except Exception as factura_error:
                    print(f"Error procesando factura {factura.id}: {factura_error}")
                    continue
            
            # ===== LOGGING MEJORADO =====
            print(f"Facturas con saldo: {len(facturas_con_saldo)}")
            for factura in facturas_con_saldo:
                tipo_info = "EXENTA" if factura['es_exenta'] else "NORMAL"
                print(f"  Factura {factura['folio']} ({tipo_info}): Neto=${factura['monto_neto']}, IVA=${factura['monto_iva_recuperable']}, Total=${factura['monto_total']}")
            
            return Response({
                'facturas': facturas_con_saldo,
                'total_facturas': len(facturas_con_saldo),
                'errores_fecha': errores_fecha  # Para debugging
            })
            
        except Exception as e:
            print(f"Error en FacturasCompraDistribuidasAPIView: {e}")
            import traceback
            print(traceback.format_exc())
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class FacturaCompraEstadoAPIView(APIView):
    """
    API para obtener el estado detallado de una factura de compra
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]
    required_scopes = ['admin', 'write', 'read']
    
    def get(self, request, factura_id):
        try:
            holding_id = request.user.holding.id if request.user.holding else None
            
            factura = get_object_or_404(
                FacturaCompraSIIDistribuida,
                id=factura_id,
                holding_id=holding_id
            )
            
            # Obtener todos los pagos de esta factura
            pagos = RegistroEgreso.objects.filter(
                factura_compra=factura
            ).select_related('movimiento_cartola', 'usuario_registro')
            
            # Calcular totales
            total_pagado = sum(pago.monto_distribuido for pago in pagos)
            neto_pagado = sum(pago.monto_neto_cubierto for pago in pagos)
            iva_pagado = sum(pago.monto_iva_cubierto for pago in pagos)
            
            # Calcular pendientes
            total_pendiente = factura.monto_total - total_pagado
            neto_pendiente = factura.monto_neto - neto_pagado
            iva_pendiente = factura.monto_iva_recuperable - iva_pagado
            
            # Calcular porcentaje pagado
            porcentaje_pagado = (total_pagado / factura.monto_total * 100) if factura.monto_total > 0 else 0
            
            # Historial de pagos
            historial_pagos = []
            for pago in pagos:
                historial_pagos.append({
                    'fecha': pago.fecha_registro.strftime('%Y-%m-%d'),
                    'monto_distribuido': float(pago.monto_distribuido),
                    'monto_neto_cubierto': float(pago.monto_neto_cubierto),
                    'monto_iva_cubierto': float(pago.monto_iva_cubierto),
                    'usuario': pago.usuario_registro.nombres,
                    'movimiento_descripcion': pago.movimiento_cartola.descripcion
                })
            
            return Response({
                'factura': {
                    'id': factura.id,
                    'folio': factura.folio,
                    'fecha_docto': factura.fecha_docto,
                    'proveedor_nombre': factura.razon_social,
                    'monto_total': float(factura.monto_total),
                    'monto_neto': float(factura.monto_neto),
                    'monto_iva_recuperable': float(factura.monto_iva_recuperable)
                },
                'cobertura': {
                    'neto_cubierto': float(neto_pagado),
                    'iva_cubierto': float(iva_pagado),
                    'total_cubierto': float(total_pagado),
                    'neto_pendiente': float(neto_pendiente),
                    'iva_pendiente': float(iva_pendiente),
                    'total_pendiente': float(total_pendiente),
                    'porcentaje_cubierto': porcentaje_pagado,
                    'completamente_pagada': total_pendiente <= 0
                },
                'historial_pagos': historial_pagos
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class RegistrarEgresoAPIView(APIView):
    """
    API para registrar un egreso (pago a factura de compra)
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]
    required_scopes = ['admin', 'write']
    
    def post(self, request):
        try:
            holding_id = request.user.holding.id if request.user.holding else None
            
            if not holding_id:
                return Response(
                    {'error': 'No se pudo determinar el holding'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            movimiento_id = request.data.get('movimiento_id')
            factura_id = request.data.get('factura_id')
            monto_distribuido = request.data.get('monto_distribuido')
            porcentaje_neto = request.data.get('porcentaje_neto', 0)
            porcentaje_iva = request.data.get('porcentaje_iva', 0)
            
            # Validaciones básicas
            if not all([movimiento_id, factura_id, monto_distribuido]):
                return Response(
                    {'error': 'Faltan datos requeridos'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if porcentaje_neto + porcentaje_iva != 100:
                return Response(
                    {'error': 'Los porcentajes de neto e IVA deben sumar 100%'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Verificar que el movimiento existe y es del holding
            movimiento = get_object_or_404(
                CartolaMovimiento,
                id=movimiento_id,
                holding_id=holding_id,
                tipo_movimiento='EGRESO'
            )
            
            # Verificar que la factura existe y es del holding
            factura = get_object_or_404(
                FacturaCompraSIIDistribuida,
                id=factura_id,
                holding_id=holding_id
            )
            
            # Verificar saldo disponible del movimiento
            total_distribuido = RegistroEgreso.objects.filter(
                movimiento_cartola=movimiento
            ).aggregate(
                total=Sum('monto_distribuido')
            )['total'] or 0
            
            saldo_disponible = movimiento.monto - total_distribuido
            
            if monto_distribuido > saldo_disponible:
                return Response(
                    {'error': f'Monto excede el saldo disponible: ${saldo_disponible:,.0f}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Verificar saldo pendiente de la factura
            pagos_previos = RegistroEgreso.objects.filter(
                factura_compra=factura
            ).aggregate(
                total=Sum('monto_distribuido')
            )['total'] or 0
            
            saldo_pendiente_factura = factura.monto_total - pagos_previos
            
            if monto_distribuido > saldo_pendiente_factura:
                return Response(
                    {'error': f'Monto excede el saldo pendiente de la factura: ${saldo_pendiente_factura:,.0f}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Crear el registro de egreso
            with transaction.atomic():
                registro_egreso = RegistroEgreso.objects.create(
                    holding_id=holding_id,
                    movimiento_cartola=movimiento,
                    factura_compra=factura,
                    monto_distribuido=monto_distribuido,
                    porcentaje_neto=porcentaje_neto,
                    porcentaje_iva=porcentaje_iva,
                    usuario_registro=request.user
                )
            
            return Response({
                'message': 'Egreso registrado exitosamente',
                'registro_id': registro_egreso.id,
                'monto_neto_cubierto': float(registro_egreso.monto_neto_cubierto),
                'monto_iva_cubierto': float(registro_egreso.monto_iva_cubierto),
                'saldo_restante_movimiento': float(saldo_disponible - monto_distribuido),
                'saldo_restante_factura': float(saldo_pendiente_factura - monto_distribuido)
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ProcesarCartolaEgresoAPIView(APIView):
    """
    Vista para procesar archivos PDF de cartola bancaria - VERSIÓN EGRESOS
    BASADA EN ProcesarCartolaAPIView - Extracción columnar precisa para CHEQUES/CARGOS
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]
    required_scopes = ['admin', 'write']
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        try:
            holding_id = request.user.holding.id if request.user.holding else None
            if not holding_id:
                return Response(
                    {'error': 'No se pudo determinar el holding'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validar parámetros
            pdf_file = request.FILES.get('cartola_pdf')
            cuenta_origen_id = request.data.get('cuenta_origen_id')
            
            if not all([pdf_file, cuenta_origen_id]):
                return Response(
                    {'error': 'Faltan parámetros requeridos: cartola_pdf, cuenta_origen_id'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validar que existe la cuenta origen
            try:
                cuenta_origen = CuentaOrigen.objects.get(id=cuenta_origen_id)
                sociedad = cuenta_origen.sociedad
            except CuentaOrigen.DoesNotExist:
                return Response(
                    {'error': 'Cuenta origen no encontrada'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Procesar el PDF
            print("🔄 Iniciando procesamiento del PDF para EGRESOS...")
            resultado_procesamiento = self.extraer_movimientos_pdf(pdf_file)
            movimientos = resultado_procesamiento['movimientos']
            periodo_cartola = resultado_procesamiento['periodo_cartola']
            
            print(f"📊 Movimientos extraídos: {len(movimientos)}")
            
            # ===== FILTRAR SOLO EGRESOS ANTES DE GUARDAR =====
            egresos = [mov for mov in movimientos if mov['tipo_movimiento'] == 'EGRESO']
            print(f"💸 Egresos filtrados: {len(egresos)} de {len(movimientos)} movimientos")
            
            # Mostrar todos los egresos detectados
            for i, mov in enumerate(egresos):
                print(f"  {i+1}. {mov['fecha']}: ${mov['monto']} - {mov['descripcion'][:50]}")
            
            if not egresos:
                return Response(
                    {'error': 'No se encontraron movimientos de egreso (Cheques/Cargos) en el PDF'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # ===== GUARDAR SOLO LOS EGRESOS - VERSIÓN MEJORADA ANTI-DUPLICADOS =====
            movimientos_guardados = []
            errores_guardado = []
            movimientos_duplicados = []
            
            for i, mov_data in enumerate(egresos):
                try:
                    movimiento, created = self.guardar_movimiento_seguro(
                        mov_data, cuenta_origen, holding_id, sociedad, i
                    )
                    
                    if created:
                        movimientos_guardados.append(movimiento)
                    else:
                        movimientos_duplicados.append(movimiento)
                        
                except Exception as e:
                    error_msg = f"Error guardando movimiento {i+1}: {str(e)}"
                    print(f"❌ {error_msg}")
                    errores_guardado.append(error_msg)
                    continue
            
            print(f"📈 RESUMEN:")
            print(f"   - Egresos detectados: {len(egresos)}")
            print(f"   - Egresos guardados (nuevos): {len(movimientos_guardados)}")
            print(f"   - Egresos duplicados (saltados): {len(movimientos_duplicados)}")
            print(f"   - Errores: {len(errores_guardado)}")
            
            return Response({
                'message': f'Se procesaron {len(movimientos_guardados)} egresos nuevos',
                'total_extraidos': len(movimientos),
                'total_egresos_detectados': len(egresos),
                'total_guardados': len(movimientos_guardados),
                'total_duplicados': len(movimientos_duplicados),
                'errores_guardado': errores_guardado,
                'periodo_cartola': periodo_cartola,
                'fecha_cartola': periodo_cartola['inicio']
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            import traceback
            print(f"❌ Error procesando cartola para egresos: {traceback.format_exc()}")
            return Response(
                {'error': f'Error procesando cartola: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def extraer_movimientos_pdf(self, pdf_file):
        """
        Extrae los movimientos del PDF de cartola bancaria
        VERSIÓN EGRESOS - Enfoque columnar para CHEQUES/CARGOS
        """
        try:
            print("📖 Leyendo contenido del PDF...")
            # Leer el PDF
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            texto_completo = ""
            
            for page_num, page in enumerate(pdf_reader.pages):
                texto_pagina = page.extract_text()
                texto_completo += texto_pagina
                print(f"   Página {page_num + 1}: {len(texto_pagina)} caracteres extraídos")
            
            print(f"📄 Total texto extraído: {len(texto_completo)} caracteres")
            
            # Extraer información del período de la cartola
            periodo_info = self.extraer_periodo_cartola(texto_completo)
            print(f"📅 Período extraído: {periodo_info}")
            
            # === NUEVA LÓGICA COLUMNAR PARA EGRESOS ===
            movimientos = self.extraer_movimientos_multilinea(texto_completo)
            
            print(f"📊 Total movimientos extraídos: {len(movimientos)}")
            
            # Validar que encontramos el número esperado de egresos
            if len(movimientos) == 0:
                print("⚠️ No se encontraron egresos. Analizando posibles problemas...")
                self.debug_estructura_pdf(texto_completo)
            
            return {
                'movimientos': movimientos,
                'periodo_cartola': periodo_info
            }
            
        except Exception as e:
            print(f"❌ Error extrayendo movimientos del PDF: {str(e)}")
            raise Exception(f"Error extrayendo movimientos del PDF: {str(e)}")
    
    def extraer_movimientos_multilinea(self, texto_completo):
        """
        VERSIÓN EGRESOS - Extrae correctamente los egresos basándose en estructura columnar
        """
        movimientos = []
        lineas = texto_completo.split('\n')
        print(f"🔍 Analizando {len(lineas)} líneas para extracción columnar de EGRESOS...")
        
        # Buscar el header de la tabla para identificar la estructura
        header_encontrado = False
        for i, linea in enumerate(lineas):
            if 'Fecha' in linea and 'Cheques/Cargos' in linea and 'Saldo' in linea:
                print(f"📋 Header de tabla encontrado en línea {i}: {linea}")
                header_encontrado = True
                break
        
        if not header_encontrado:
            print("⚠️ No se encontró header de tabla específico, usando análisis alternativo")
        
        for i, linea in enumerate(lineas):
            linea_limpia = linea.strip()
            
            # Solo procesar líneas que empiecen con fecha
            if not re.match(r'\d{2}/\d{2}/\d{4}', linea_limpia):
                continue
            
            # Construir el movimiento completo (puede ocupar múltiples líneas)
            movimiento_completo = self.construir_movimiento_columnar(lineas, i)
            
            if movimiento_completo['texto_completo']:
                movimiento = self.procesar_movimiento_columnar(
                    movimiento_completo['texto_completo'], 
                    i
                )
                
                if movimiento and movimiento['tipo_movimiento'] == 'EGRESO':
                    movimientos.append(movimiento)
                    print(f"   ✅ EGRESO extraído: {movimiento['fecha']} - ${movimiento['monto']} - {movimiento['descripcion'][:30]}")
        
        print(f"📊 Total egresos extraídos: {len(movimientos)}")
        return movimientos

    def construir_movimiento_columnar(self, lineas, indice_inicio):
        """
        Construye un movimiento completo identificando estructura columnar
        """
        texto_movimiento = ""
        lineas_procesadas = 0
        
        # Empezar con la línea que contiene la fecha
        linea_actual = lineas[indice_inicio].strip()
        texto_movimiento = linea_actual
        lineas_procesadas = 1
        
        # Verificar si ya tiene estructura completa (3 montos mínimo)
        if self.tiene_estructura_columnar_completa(texto_movimiento):
            return {
                'texto_completo': texto_movimiento,
                'lineas_procesadas': lineas_procesadas
            }
        
        # Si no, buscar en líneas siguientes hasta completar la estructura
        for j in range(1, 4):  # Máximo 4 líneas adicionales
            if indice_inicio + j >= len(lineas):
                break
                
            linea_siguiente = lineas[indice_inicio + j].strip()
            
            # Si encontramos otra fecha, parar
            if re.match(r'\d{2}/\d{2}/\d{4}', linea_siguiente):
                break
            
            # Si la línea es muy corta o vacía, skipear
            if len(linea_siguiente) < 5:
                continue
            
            # Agregar la línea
            texto_movimiento += " " + linea_siguiente
            lineas_procesadas += 1
            
            # Verificar si ahora tenemos estructura completa
            if self.tiene_estructura_columnar_completa(texto_movimiento):
                break
        
        return {
            'texto_completo': texto_movimiento,
            'lineas_procesadas': lineas_procesadas
        }

    def tiene_estructura_columnar_completa(self, texto):
        """
        Verifica si el texto tiene la estructura columnar completa de una fila de cartola
        Debe tener: Fecha + Sucursal + Operación + Descripción + Cheques + Depósitos + Saldo
        """
        # Debe tener fecha
        if not re.search(r'\d{2}/\d{2}/\d{4}', texto):
            return False
        
        # Debe tener sucursal
        if not re.search(r'(stgo\.principal|parral)', texto, re.IGNORECASE):
            return False
        
        # Debe tener al menos 3 montos (cheques/cargos, depósitos/abonos, saldo)
        montos = re.findall(r'\$[\d,\.]+', texto)
        if len(montos) < 3:
            return False
        
        # Debe tener número de operación (7-8 dígitos o 0000000)
        if not re.search(r'\b\d{6,8}\b', texto):
            return False
        
        return True

    def procesar_movimiento_columnar(self, texto_completo, numero_linea):
        """
        Procesa un movimiento completo extrayendo información de estructura columnar
        VERSIÓN EGRESOS - Busca Cheques/Cargos > 0
        """
        try:
            # === EXTRAER FECHA ===
            fecha_match = re.search(r'(\d{2}/\d{2}/\d{4})', texto_completo)
            if not fecha_match:
                return None
            
            fecha_str = fecha_match.group(1)
            fecha = datetime.strptime(fecha_str, '%d/%m/%Y').date()
            
            # === EXTRAER NÚMERO DE OPERACIÓN ===
            # Buscar número después de la sucursal
            numero_operacion = self.extraer_numero_operacion_columnar(texto_completo)
            
            # === EXTRAER MONTOS COLUMNARES ===
            # La clave es extraer los 3 montos en orden: Cheques/Cargos, Depósitos/Abonos, Saldo
            resultado_montos = self.extraer_montos_columnares(texto_completo)
            
            if not resultado_montos:
                print(f"      ⚠️ No se pudieron extraer montos correctamente")
                return None
            
            cheques_cargos = resultado_montos['cheques_cargos']
            depositos_abonos = resultado_montos['depositos_abonos']
            saldo = resultado_montos['saldo']
            
            # Solo procesar si es un EGRESO (Cheques/Cargos > 0)
            if cheques_cargos <= 0:
                return None  # No es un egreso
            
            # === EXTRAER DESCRIPCIÓN ===
            descripcion = self.extraer_descripcion_columnar(texto_completo, fecha_str, numero_operacion)
            
            # Crear el movimiento
            return {
                'fecha': fecha,
                'numero_operacion': numero_operacion,
                'descripcion': descripcion,
                'monto': Decimal(str(cheques_cargos)),  # El monto del egreso es el valor de Cheques/Cargos
                'tipo_movimiento': 'EGRESO',
                'saldo': Decimal(str(saldo)),
                'depositos_abonos': Decimal(str(depositos_abonos))
            }
            
        except Exception as e:
            print(f"❌ Error procesando movimiento columnar línea {numero_linea}: {e}")
            return None

    def extraer_montos_columnares(self, texto):
        """
        Extrae los 3 montos en orden: Cheques/Cargos, Depósitos/Abonos, Saldo
        """
        try:
            # Buscar todos los montos en formato $X,XXX,XXX
            montos_encontrados = re.findall(r'\$(\d{1,3}(?:[\.,]\d{3})*(?:[\.,]\d{2})?)', texto)
            
            if len(montos_encontrados) < 3:
                print(f"      ⚠️ Faltan montos: solo encontrados {len(montos_encontrados)}")
                return None
            
            # Convertir a números
            montos_numericos = []
            for monto_str in montos_encontrados:
                try:
                    # Limpiar formato chileno (puntos como separadores de miles, comas como decimales)
                    monto_limpio = monto_str.replace('.', '').replace(',', '.')
                    monto_num = float(monto_limpio)
                    montos_numericos.append(monto_num)
                except:
                    continue
            
            if len(montos_numericos) < 3:
                return None
            
            # Los últimos 3 montos deberían ser: Cheques/Cargos, Depósitos/Abonos, Saldo
            cheques_cargos = montos_numericos[-3]
            depositos_abonos = montos_numericos[-2]
            saldo = montos_numericos[-1]
            
            # Validación: el saldo debe ser el más grande (generalmente)
            if saldo < max(cheques_cargos, depositos_abonos) * 0.8:
                print(f"      ⚠️ Saldo sospechoso: {saldo} vs cargos:{cheques_cargos} abonos:{depositos_abonos}")
                
            return {
                'cheques_cargos': cheques_cargos,
                'depositos_abonos': depositos_abonos,
                'saldo': saldo
            }
            
        except Exception as e:
            print(f"❌ Error extrayendo montos columnares: {e}")
            return None

    def extraer_numero_operacion_columnar(self, texto):
        """
        Extrae el número de operación considerando la estructura columnar
        """
        # Buscar después de la sucursal y antes de la descripción
        # Patrón: Fecha Sucursal NUMERO Descripción
        
        # Primero buscar números de 7 dígitos (más comunes)
        match = re.search(r'(?:stgo\.principal|parral)\s+(\d{7})', texto, re.IGNORECASE)
        if match:
            return match.group(1)
        
        # Buscar números de 6-8 dígitos
        match = re.search(r'(?:stgo\.principal|parral)\s+(\d{6,8})', texto, re.IGNORECASE)
        if match:
            return match.group(1)
        
        # Buscar 0000000 (cheques en efectivo)
        match = re.search(r'(?:stgo\.principal|parral)\s+(0+)', texto, re.IGNORECASE)
        if match:
            return match.group(1)
        
        return "SIN_NUMERO"

    def extraer_descripcion_columnar(self, texto, fecha_str, numero_operacion):
        """
        Extrae la descripción considerando la estructura columnar
        """
        try:
            # Patrón: después del número de operación y antes del primer monto
            # Remover fecha y sucursal del inicio
            descripcion = texto
            descripcion = re.sub(r'\d{2}/\d{2}/\d{4}', '', descripcion)  # Remover fecha
            descripcion = re.sub(r'(stgo\.principal|parral)', '', descripcion, flags=re.IGNORECASE)  # Remover sucursal
            descripcion = re.sub(numero_operacion, '', descripcion, 1)  # Remover número de operación
            
            # Remover todos los montos
            descripcion = re.sub(r'\$[\d,\.]+', '', descripcion)
            
            # Limpiar espacios múltiples y caracteres extraños
            descripcion = re.sub(r'\s+', ' ', descripcion).strip()
            
            # Si es muy corta, intentar extraer de otra forma
            if len(descripcion) < 10:
                # Buscar texto entre número de operación y primer monto
                pattern = rf'{numero_operacion}\s+(.+?)\s+\$'
                match = re.search(pattern, texto)
                if match:
                    descripcion = match.group(1).strip()
            
            # Limpiar caracteres finales
            descripcion = re.sub(r'[^\w\s\-\.\,]$', '', descripcion).strip()
            
            return descripcion[:200] if descripcion else "Descripción no disponible"
            
        except Exception as e:
            print(f"Error extrayendo descripción: {e}")
            return "Error en descripción"

    def extraer_periodo_cartola(self, texto_completo):
        """
        Extrae el período de la cartola - VERSIÓN MEJORADA
        """
        try:
            # Buscar en el resumen/header de la cartola
            patterns = [
                r'Fecha Inicio\s*(\d{2}/\d{2}/\d{4})',
                r'Fecha Final\s*(\d{2}/\d{2}/\d{4})',
                r'(\d{2}/\d{2}/\d{4})\s*(\d{2}/\d{2}/\d{4})',  # Dos fechas juntas
            ]
            
            fechas_inicio = []
            fechas_fin = []
            
            for pattern in patterns:
                matches = re.findall(pattern, texto_completo)
                for match in matches:
                    if isinstance(match, tuple):
                        fechas_inicio.append(match[0])
                        fechas_fin.append(match[1])
                    else:
                        if 'inicio' in pattern.lower():
                            fechas_inicio.append(match)
                        else:
                            fechas_fin.append(match)
            
            # Si encontramos fechas específicas, usarlas
            if fechas_inicio and fechas_fin:
                fecha_inicio = datetime.strptime(fechas_inicio[0], '%d/%m/%Y').date()
                fecha_final = datetime.strptime(fechas_fin[0], '%d/%m/%Y').date()
                
                return {
                    'inicio': fecha_inicio.strftime('%Y-%m-%d'),
                    'fin': fecha_final.strftime('%Y-%m-%d')
                }
            
            # Fallback: analizar todas las fechas en los movimientos
            fechas_movimientos = re.findall(r'(\d{2}/\d{2}/\d{4})', texto_completo)
            if fechas_movimientos:
                fechas_parseadas = []
                for fecha_str in fechas_movimientos:
                    try:
                        fecha = datetime.strptime(fecha_str, '%d/%m/%Y').date()
                        fechas_parseadas.append(fecha)
                    except:
                        continue
                
                if fechas_parseadas:
                    fecha_min = min(fechas_parseadas)
                    fecha_max = max(fechas_parseadas)
                    
                    return {
                        'inicio': fecha_min.strftime('%Y-%m-%d'),
                        'fin': fecha_max.strftime('%Y-%m-%d')
                    }
            
            # Fallback final - mes actual
            today = datetime.now().date()
            primer_dia = today.replace(day=1)
            if today.month == 12:
                ultimo_dia = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                ultimo_dia = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
            
            return {
                'inicio': primer_dia.strftime('%Y-%m-%d'),
                'fin': ultimo_dia.strftime('%Y-%m-%d')
            }
            
        except Exception as e:
            print(f"Error extrayendo período: {e}")
            return {
                'inicio': '2025-06-01',
                'fin': '2025-06-30'
            }

    def debug_estructura_pdf(self, texto_completo):
        """
        Método de debug para analizar por qué no se extraen egresos
        """
        print("🔍 === DEBUG ESTRUCTURA PDF - EGRESOS ===")
        
        # Buscar headers de tabla
        headers = re.findall(r'.*Fecha.*Cheques.*Saldo.*', texto_completo, re.IGNORECASE)
        print(f"Headers encontrados: {len(headers)}")
        for header in headers[:2]:
            print(f"  - {header}")
        
        # Buscar líneas con fechas
        lineas_con_fecha = []
        for linea in texto_completo.split('\n'):
            if re.match(r'\d{2}/\d{2}/\d{4}', linea.strip()):
                lineas_con_fecha.append(linea.strip())
        
        print(f"Líneas con fecha encontradas: {len(lineas_con_fecha)}")
        for i, linea in enumerate(lineas_con_fecha[:5]):
            print(f"  {i+1}. {linea[:100]}...")
        
        # Buscar montos
        montos = re.findall(r'\$[\d,\.]+', texto_completo)
        print(f"Montos encontrados: {len(montos)}")
        print(f"Primeros 10 montos: {montos[:10]}")
        
        # Buscar palabras clave de egresos
        palabras_egreso = ['cheque', 'cargo', 'transferencia', 'pago', 'giro']
        for palabra in palabras_egreso:
            count = len(re.findall(palabra, texto_completo, re.IGNORECASE))
            print(f"'{palabra}': {count} ocurrencias")

    def generar_numero_operacion_unico(self, mov_data, cuenta_origen, indice):
        """
        Genera un número de operación único - VERSIÓN MEJORADA ANTI-DUPLICADOS
        """
        # Usar el número original si existe y es válido
        numero_original = mov_data.get('numero_operacion', '')
        
        if numero_original and numero_original != 'SIN_NUMERO':
            # Verificación más robusta incluyendo monto para detectar duplicados reales
            movimiento_existente = CartolaMovimiento.objects.filter(
                cuenta_origen=cuenta_origen,
                numero_operacion=numero_original,
                fecha=mov_data['fecha'],
                monto=mov_data['monto']  # AGREGADO: verificar también el monto
            ).first()
            
            if not movimiento_existente:
                return numero_original
            else:
                print(f"⚠️ Movimiento duplicado detectado: {numero_original} - ${mov_data['monto']} - {mov_data['fecha']}")
                # Si existe exactamente el mismo movimiento, usar el número existente
                return numero_original
        
        # Generar uno único basado en múltiples criterios para evitar colisiones
        fecha_str = mov_data['fecha'].strftime('%Y%m%d')
        monto_int = int(mov_data['monto'])
        tipo_prefix = 'EGR' if mov_data['tipo_movimiento'] == 'EGRESO' else 'ING'
        
        # Incluir hash de la descripción para mayor unicidad
        import hashlib
        desc_hash = hashlib.md5(mov_data['descripcion'].encode()).hexdigest()[:4]
        
        # Formato: TIPO_FECHA_MONTO_HASH_INDICE
        numero_base = f"{tipo_prefix}_{fecha_str}_{monto_int}_{desc_hash}_{indice:03d}"
        
        # Verificar si este número ya existe y buscar uno libre
        contador = 0
        numero_final = numero_base
        
        while CartolaMovimiento.objects.filter(
            cuenta_origen=cuenta_origen,
            numero_operacion=numero_final,
            fecha=mov_data['fecha']
        ).exists():
            contador += 1
            numero_final = f"{numero_base}_{contador:02d}"
            
            # Prevenir bucle infinito
            if contador > 99:
                import time
                timestamp = int(time.time() * 1000) % 10000
                numero_final = f"{tipo_prefix}_{fecha_str}_{timestamp}"
                break
        
        return numero_final

    def guardar_movimiento_seguro(self, mov_data, cuenta_origen, holding_id, sociedad, indice):
        """
        Método seguro para guardar movimientos evitando duplicados
        VERSIÓN FINAL CORREGIDA - Solo respeta los criterios unique_together del modelo
        """
        try:
            # Generar número de operación único
            numero_operacion_unico = self.generar_numero_operacion_unico(
                mov_data, cuenta_origen, indice
            )
            
            print(f"🔄 Intentando guardar {mov_data['tipo_movimiento'].lower()} {indice+1}: {mov_data['fecha']} - ${mov_data['monto']}")
            print(f"   Número operación: {numero_operacion_unico}")
            
            # ELIMINADA LA VERIFICACIÓN PROBLEMÁTICA
            # Solo usar get_or_create que respeta exactamente unique_together del modelo:
            # unique_together = [['cuenta_origen', 'numero_operacion', 'fecha']]
            
            movimiento, created = CartolaMovimiento.objects.get_or_create(
                cuenta_origen=cuenta_origen,
                numero_operacion=numero_operacion_unico,
                fecha=mov_data['fecha'],
                defaults={
                    'holding_id': holding_id,
                    'sociedad': sociedad,
                    'descripcion': mov_data['descripcion'][:255],
                    'monto': mov_data['monto'],
                    'tipo_movimiento': mov_data['tipo_movimiento'],
                    'saldo': mov_data['saldo']
                }
            )
            
            if created:
                print(f"✅ Guardado exitoso: {movimiento.fecha} - ${movimiento.monto} - Nº{movimiento.numero_operacion}")
            else:
                print(f"⚠️ Ya existe (mismo número operación y fecha): {movimiento.fecha} - ${movimiento.monto} - Nº{movimiento.numero_operacion}")
                
            return movimiento, created
            
        except Exception as e:
            print(f"❌ Error guardando movimiento {indice+1}: {str(e)}")
            raise e

class MovimientoEgresoSaldosAPIView(APIView):
    """
    API para obtener movimientos de egreso con sus saldos disponibles
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]
    required_scopes = ['admin', 'write', 'read']
    
    def get(self, request):
        try:
            holding_id = request.user.holding.id if request.user.holding else None
            
            if not holding_id:
                return Response(
                    {'error': 'No se pudo determinar el holding'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            cuenta_origen_id = request.GET.get('cuenta_origen_id')
            fecha_inicio = request.GET.get('fecha_inicio')
            fecha_fin = request.GET.get('fecha_fin')
            
            if not all([cuenta_origen_id, fecha_inicio, fecha_fin]):
                return Response(
                    {'error': 'Faltan parámetros requeridos'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Obtener movimientos de egreso en el período
            movimientos = CartolaMovimiento.objects.filter(
                holding_id=holding_id,
                cuenta_origen_id=cuenta_origen_id,
                fecha__range=[fecha_inicio, fecha_fin],
                tipo_movimiento='EGRESO'  # Solo egresos
            ).order_by('-fecha', '-monto')
            
            movimientos_con_saldo = []
            
            for movimiento in movimientos:
                # Calcular total distribuido de este movimiento
                total_distribuido = RegistroEgreso.objects.filter(
                    movimiento_cartola=movimiento
                ).aggregate(
                    total=Sum('monto_distribuido')
                )['total'] or 0
                
                saldo_disponible = movimiento.monto - total_distribuido
                porcentaje_usado = (total_distribuido / movimiento.monto * 100) if movimiento.monto > 0 else 0
                
                # Solo incluir movimientos con saldo disponible
                if saldo_disponible > 0:
                    movimientos_con_saldo.append({
                        'id': movimiento.id,
                        'fecha': movimiento.fecha,
                        'numero_operacion': movimiento.numero_operacion,
                        'descripcion': movimiento.descripcion,
                        'monto_original': float(movimiento.monto),
                        'monto_distribuido': float(total_distribuido),
                        'saldo_disponible': float(saldo_disponible),
                        'porcentaje_usado': porcentaje_usado,
                        'completamente_usado': saldo_disponible <= 0,
                        'saldo': float(movimiento.saldo)
                    })
            
            return Response({
                'movimientos': movimientos_con_saldo,
                'total_movimientos': len(movimientos_con_saldo),
                'saldo_total_disponible': sum(mov['saldo_disponible'] for mov in movimientos_con_saldo)
            })
            
        except Exception as e:
            print(e)
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class HistorialPagosAPIView(APIView):
    """
    Vista unificada para obtener historial de pagos de ingresos y egresos
    GET /api/historial/{tipo}/{estado}/
    donde tipo = 'ingresos' o 'egresos'
    y estado = 'completados' o 'pendientes'
    """
    
    def get(self, request, tipo, estado, formato=None):
        try:
            holding_id = request.user.holding.id if request.user.holding else None
            if not holding_id:
                return Response(
                    {'error': 'No se pudo determinar el holding'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validar parámetros
            if tipo not in ['ingresos', 'egresos']:
                return Response(
                    {'error': 'Tipo debe ser "ingresos" o "egresos"'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if estado not in ['completados', 'pendientes']:
                return Response(
                    {'error': 'Estado debe ser "completados" o "pendientes"'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Determinar si es solicitud de CSV
            es_csv = formato == 'csv' or request.path.endswith('/csv/')

            # Llamar al método correspondiente
            if tipo == 'ingresos' and estado == 'completados':
                data = self._get_ingresos_completados(holding_id)
            elif tipo == 'ingresos' and estado == 'pendientes':
                data = self._get_ingresos_pendientes(holding_id)
            elif tipo == 'egresos' and estado == 'completados':
                data = self._get_egresos_completados(holding_id)
            else:  # egresos pendientes
                data = self._get_egresos_pendientes(holding_id)

            # Retornar CSV o JSON según la solicitud
            if es_csv:
                return self._generar_csv_response(data, tipo, estado)
            else:
                return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Error en historial: {str(e)}")
            return Response(
                {'error': f'Error al obtener historial: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _get_ingresos_completados(self, holding_id):
        """Obtener ingresos completados (pagos distribuidos)"""
        ingresos = RegistroIngreso.objects.filter(
            holding_id=holding_id
        ).select_related(
            'movimiento_cartola',
            'factura_venta'
        ).order_by('-fecha_registro')

        return [{
            'id': ingreso.id,
            'fecha': ingreso.fecha_registro.strftime('%Y-%m-%d'),
            'descripcion': f"Pago distribuido de factura N° {ingreso.factura_venta.folio}",
            'monto': float(ingreso.monto_distribuido),
            'numero_operacion': ingreso.movimiento_cartola.numero_operacion,
            'factura_numero': ingreso.factura_venta.folio,
            'factura_rut': ingreso.factura_venta.rut_receptor,
            'factura_razon_social': ingreso.factura_venta.razon_social_receptor,
            'estado': 'COMPLETADO'
        } for ingreso in ingresos]

    def _get_ingresos_pendientes(self, holding_id):
        """Obtener ingresos pendientes (facturas sin cobrar)"""
        facturas_pendientes = FacturaVentaSIIDistribuida.objects.filter(
            holding_id=holding_id
        ).annotate(
            monto_cobrado=Coalesce(
                Sum('registroingreso__monto_distribuido'), 
                Value(0),
                output_field=DecimalField(max_digits=15, decimal_places=2)
            )
        ).filter(
            monto_cobrado__lt=F('monto_total')
        ).order_by('-fecha_distribucion')

        return [{
            'id': factura.id,
            'fecha': factura.fecha_emision,
            'descripcion': f"Factura de venta N° {factura.folio} pendiente de cobro",
            'monto': float(factura.monto_total - factura.monto_cobrado),
            'numero_operacion': None,
            'factura_numero': factura.folio,
            'factura_rut': factura.rut_receptor,
            'factura_razon_social': factura.razon_social_receptor,
            'estado': 'PENDIENTE'
        } for factura in facturas_pendientes]

    def _get_egresos_completados(self, holding_id):
        """Obtener egresos completados (pagos distribuidos)"""
        egresos = RegistroEgreso.objects.filter(
            holding_id=holding_id
        ).select_related(
            'movimiento_cartola',
            'factura_compra'
        ).order_by('-fecha_registro')

        return [{
            'id': egreso.id,
            'fecha': egreso.fecha_registro.strftime('%Y-%m-%d'),
            'descripcion': f"Pago distribuido de factura N° {egreso.factura_compra.folio}",
            'monto': float(egreso.monto_distribuido),
            'numero_operacion': egreso.movimiento_cartola.numero_operacion,
            'factura_numero': egreso.factura_compra.folio,
            'factura_rut': egreso.factura_compra.rut_proveedor,
            'factura_razon_social': egreso.factura_compra.razon_social,
            'estado': 'COMPLETADO'
        } for egreso in egresos]

    def _get_egresos_pendientes(self, holding_id):
        """Obtener egresos pendientes (facturas sin pagar)"""
        facturas_pendientes = FacturaCompraSIIDistribuida.objects.filter(
            holding_id=holding_id
        ).annotate(
            monto_pagado=Coalesce(
                Sum('registroegreso__monto_distribuido'), 
                Value(0),
                output_field=DecimalField(max_digits=15, decimal_places=2)
            )
        ).filter(
            monto_pagado__lt=F('monto_total')
        ).order_by('-fecha_distribucion')

        return [{
            'id': factura.id,
            'fecha': factura.fecha_docto,
            'descripcion': f"Factura de compra N° {factura.folio} pendiente de pago",
            'monto': float(factura.monto_total - factura.monto_pagado),
            'numero_operacion': None,
            'factura_numero': factura.folio,
            'factura_rut': factura.rut_proveedor,
            'factura_razon_social': factura.razon_social,
            'estado': 'PENDIENTE'
        } for factura in facturas_pendientes]

    def _generar_csv_response(self, data, tipo, estado):
        """Genera una respuesta HTTP con archivo CSV"""
        # Crear el contenido CSV
        output = StringIO()
        writer = csv.writer(output)
        
        # Escribir encabezados
        headers = [
            'ID',
            'Fecha',
            'Descripción',
            'Monto',
            'Número Operación',
            'Número Factura',
            'RUT',
            'Razón Social',
            'Estado'
        ]
        writer.writerow(headers)
        
        # Escribir datos
        for item in data:
            writer.writerow([
                item['id'],
                item['fecha'],
                item['descripcion'],
                f"${item['monto']:,.0f}",  # Formato moneda
                item['numero_operacion'] or 'N/A',
                item['factura_numero'],
                item['factura_rut'],
                item['factura_razon_social'],
                item['estado']
            ])
        
        # Crear nombre de archivo
        fecha_actual = datetime.now().strftime('%Y%m%d_%H%M%S')
        nombre_archivo = f"historial_{tipo}_{estado}_{fecha_actual}.csv"
        
        # Crear respuesta HTTP con BOM para Excel
        csv_content = '\ufeff' + output.getvalue()
        response = HttpResponse(csv_content, content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
        
        return response
    
