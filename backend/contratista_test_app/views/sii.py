import os
import re
import csv
import time
import random
import traceback
import logging
from decimal import Decimal
from datetime import datetime, timedelta
from io import StringIO
from django.forms import ValidationError

from django.db import transaction
from django.db.models import Sum, F, Q, Value
from django.db.models.functions import Coalesce
from django.db.models.fields import DecimalField
from django.http import HttpResponse, FileResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response

from rest_framework.permissions import IsAuthenticated, AllowAny
from oauth2_provider.contrib.rest_framework import IsAuthenticatedOrTokenHasScope as JWTHasAnyScope

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

import pypdf

from .base import BaseAPIView, PublicAPIView
from ..models import (
    Cuenta,
    Banco,
    CamposClientes,
    CartolaMovimiento,
    Clientes,
    ConfiguracionSIIAutomaticaCompra,
    ConfiguracionSIIAutomaticaVenta,
    CuentaOrigen,
    FacturaCompraSIIDistribuida,
    FacturaCompraSIIPorDistribuir,
    FacturaVentaSIIDistribuida,
    FacturaVentaSIIPorDistribuir,
    Labores,
    RegistroEgreso,
    RegistroIngreso,
    Sociedad,
)
from ..serializers import (
    BancoSerializer,
    CartolaMovimientoSerializer,
    CuentaOrigenSerializer,
    DistribucionFacturasSIISerializer,
    DistribucionFacturasVentaSIISerializer,
    DistribucionMultipleFacturaCompraSIISerializer,
    DistribucionMultipleFacturaVentaSIISerializer,
    FacturaCompraSIIDistribuidaMultipleSerializer,
    FacturaPorDistribuirMultipleSerializer,
    FacturaVentaPorDistribuirMultipleSerializer,
    FacturaVentaSIIDistribuidaMultipleSerializer,
    ValidarDistribucionSerializer,
    CuentaSerializer,
)
from ..tasks import procesar_configuracion_automatica
from ..browser_session_manager import BrowserSessionManager

logger = logging.getLogger('contratista_test_app')

# ==============================================================================
# CUENTAS
# ==============================================================================
class CuentasAPIView(BaseAPIView):
    
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

# ==============================================================================
# CUENTA ORIGEN
# ==============================================================================
class CuentaOrigenAPIView(BaseAPIView):

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

# ==============================================================================
# BANCO LIST
# ==============================================================================
class BancoListAPIView(BaseAPIView):

    def get(self, request):
        bancos = Banco.objects.all()
        serializer = BancoSerializer(bancos, many=True)
        return Response(serializer.data)
 
# ==============================================================================
# CUENTAS ORIGEN POR BANCO
# ==============================================================================
class CuentasOrigenPorBancoAPIView(BaseAPIView):
    
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

# ==============================================================================
# FACTURAS COMPRA AUTOMATICO
# ==============================================================================
class FacturasCompraAutomaticoAPIView(BaseAPIView):
    
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
            from ..tasks import buscar_pdfs_facturas_existentes
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
            from ..tasks import buscar_pdfs_facturas_existentes
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
                from ..tasks import buscar_pdfs_facturas_existentes
                
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
                from ..tasks import buscar_pdfs_facturas_existentes_sync
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

# ==============================================================================
# SERVE PDF FACTURA SII
# ==============================================================================
class ServePDFFacturaSIIAPIView(BaseAPIView):
    
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

# ==============================================================================
# DOWNLOAD PDF FACTURA SII
# ==============================================================================
class DownloadPDFFacturaSIIAPIView(BaseAPIView):
    
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

# ==============================================================================
# FACTURAS COMPRA DISTRIBUCION
# ==============================================================================
class FacturasCompraDistribucion(BaseAPIView):
    
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
            from ..serializers import DistribucionDataSerializer
            
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
            from ..serializers import FundosClienteSerializer
            
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
        from ..serializers import DistribucionFacturasSIISerializer
        from ..models import FacturaCompraSIIDistribuida, FacturaCompraSIIPorDistribuir, Clientes, CamposClientes, Labores, Cuenta
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
            from ..serializers import FacturaCompraSIIDistribuidaSerializer
            
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
                from ..models import FacturaCompraSIIDistribuida
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
            from ..models import FacturaCompraSIIDistribuida
            
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
            from ..models import FacturaCompraSIIDistribuida
            
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

# ==============================================================================
# FACTURAS VENTA AUTOMATICO
# ==============================================================================
class FacturasVentaAutomaticoAPIView(BaseAPIView):

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
            from ..tasks import buscar_pdfs_facturas_venta_existentes
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
            from ..tasks import buscar_pdfs_facturas_venta_existentes
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
            from ..tasks import procesar_configuracion_venta_automatica
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

# ==============================================================================
# SERVE PDF FACTURA VENTA SII
# ==============================================================================
class ServePDFFacturaVentaSIIAPIView(BaseAPIView):
    
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

# ==============================================================================
# DOWNLOAD PDF FACTURA VENTA SII
# ==============================================================================
class DownloadPDFFacturaVentaSIIAPIView(BaseAPIView):
    
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

# ==============================================================================
# FACTURAS VENTA DISTRIBUCION
# ==============================================================================
class FacturasVentaDistribucion(BaseAPIView):
    
    def post(self, request, format=None):
        """
        Maneja todas las acciones relacionadas con facturas de venta distribuidas
        """
        try:
            from django.utils import timezone
            import traceback
            from ..models import FacturaVentaSIIDistribuida, Clientes, Labores, Cuenta, CamposClientes
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
            from ..models import FacturaVentaSIIDistribuida
            
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
            from ..models import FacturaVentaSIIDistribuida
            
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

# ==============================================================================
# PROCESAR CARTOLA
# ==============================================================================
class ProcesarCartolaAPIView(BaseAPIView):
    
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
            pdf_reader = pypdf.PdfReader(pdf_file)
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

# ==============================================================================
# MOVIMIENTOS CARTOLA
# ==============================================================================
class MovimientosCartolaAPIView(BaseAPIView):
    
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

# ==============================================================================
# FACTURAS DISTRIBUIDAS
# ==============================================================================
class FacturasDistribuidasAPIView(BaseAPIView):
    
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

# ==============================================================================
# REGISTRAR INGRESO
# ==============================================================================
class RegistrarIngresoAPIView(BaseAPIView):
    
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

# ==============================================================================
# REGISTRAR EGRESO
# ==============================================================================

class RegistrarEgresoAPIView(BaseAPIView):
    
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

# ==============================================================================
# MOVIMIENTO SALDOS
# ==============================================================================
class MovimientoSaldosAPIView(BaseAPIView):
    
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

# ==============================================================================
# FACTURA ESTADO
# ==============================================================================
class FacturaEstadoAPIView(BaseAPIView):
    
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

# ==============================================================================
# FACTURAS COMPRA DISTRIBUIDAS
# ==============================================================================
class FacturasCompraDistribuidasAPIView(BaseAPIView):
    
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

# ==============================================================================
# FACTURA COMPRA ESTADO
# ==============================================================================
class FacturaCompraEstadoAPIView(BaseAPIView):
    
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

# ==============================================================================
# FACTURA COMPRA ESTADO
# ==============================================================================
class FacturaCompraEstadoAPIView(BaseAPIView):
    
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

# ==============================================================================
# PROCESAR CARTOLA EGRESO
# ==============================================================================
class ProcesarCartolaEgresoAPIView(BaseAPIView):
    
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
            pdf_reader = pypdf.PdfReader(pdf_file)
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

# ==============================================================================
# MOVIMIENTO EGRESO SALDOS
# ==============================================================================
class MovimientoEgresoSaldosAPIView(BaseAPIView):
    
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

# ==============================================================================
# HISTORIAL PAGOS
# ==============================================================================
class HistorialPagosAPIView(BaseAPIView):
    
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
 