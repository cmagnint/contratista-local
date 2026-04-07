import logging
import os
import time
from datetime import datetime, timedelta
from io import BytesIO

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db import transaction
from django.forms import ValidationError
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)
from rest_framework import status
from rest_framework.response import Response

from .base import BaseAPIView
from ..models import (
    ChoferesTransporte,
    DetallePagoTransportista,
    DocumentosChofer,
    DocumentosVehiculo,
    EmpresasTransporte,
    FolioTransportista,
    PagoTransportista,
    PersonalTrabajadores,
    ProduccionTrabajador,
    ProformaTransportista,
    Sociedad,
    Tramos,
    VehiculosTransporte,
)
from ..serializers import (
    ChoferesTransporteSerializer,
    EmpresaTransporteSerializer,
    FolioTransportistaSerializer,
    InformeTransportistaSerializer,
    PagoTransportistaSerializer,
    ProformaTransportistaSerializer,
    TramosSerializer,
    VehiculosTransporteSerializer,
)
from ..utils import validate_uploaded_documents

logger = logging.getLogger('contratista_test_app')


# ==============================================================================
# EMPRESAS TRANSPORTE
# ==============================================================================

class EmpresaTransporteAPIView(BaseAPIView):

    def get(self, request, format=None):
        holding_id = request.query_params.get('holding')
        if not holding_id:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        empresas = EmpresasTransporte.objects.filter(holding_id=holding_id)
        return Response(EmpresaTransporteSerializer(empresas, many=True).data)

    def post(self, request, format=None):
        serializer = EmpresaTransporteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        logger.error(f'EmpresaTransporteAPIView POST: datos inválidos: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, format=None):
        ids = request.data.get('ids', [])
        EmpresasTransporte.objects.filter(id__in=ids).delete()
        logger.debug(f'EmpresaTransporteAPIView DELETE: {len(ids)} empresas eliminadas')
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, format=None):
        obj_id = request.data.get('id')
        if not obj_id:
            return Response({'message': 'ID es necesario para actualizar'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            empresa = EmpresasTransporte.objects.get(id=obj_id)
        except EmpresasTransporte.DoesNotExist:
            logger.error(f'EmpresaTransporteAPIView PATCH: empresa {obj_id} no encontrada')
            return Response({'message': 'Perfil no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        serializer = EmpresaTransporteSerializer(empresa, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        logger.error(f'EmpresaTransporteAPIView PATCH: datos inválidos para empresa {obj_id}: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, format=None):
        obj_id = request.data.get('id')
        try:
            empresa = EmpresasTransporte.objects.get(id=obj_id)
        except EmpresasTransporte.DoesNotExist:
            logger.error(f'EmpresaTransporteAPIView PUT: empresa {obj_id} no encontrada')
            return Response({'message': 'Cargo no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        serializer = EmpresaTransporteSerializer(empresa, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        logger.error(f'EmpresaTransporteAPIView PUT: datos inválidos para empresa {obj_id}: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ==============================================================================
# VEHÍCULOS TRANSPORTE
# ==============================================================================

class VehiculosTransporteAPIView(BaseAPIView):

    def get(self, request, format=None):
        holding_id = request.query_params.get('holding')
        if not holding_id:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        vehiculos = VehiculosTransporte.objects.filter(holding_id=holding_id)
        return Response(VehiculosTransporteSerializer(vehiculos, many=True, context={'request': request}).data)

    def post(self, request, format=None):
        try:
            vehiculo_data = {
                'holding': request.data.get('holding'),
                'empresa': request.data.get('empresa'),
                'tipo': request.data.get('tipo'),
                'ppu': request.data.get('ppu'),
                'modelo': request.data.get('modelo'),
                'year': request.data.get('year'),
                'color': request.data.get('color'),
                'num_pasajeros': request.data.get('num_pasajeros'),
                'marca': request.data.get('marca'),
            }

            serializer = VehiculosTransporteSerializer(data=vehiculo_data)
            if serializer.is_valid():
                vehiculo = serializer.save()
                self._process_documents(request, vehiculo)
                logger.debug(f'VehiculosTransporteAPIView POST: vehículo {vehiculo.id} creado')
                return Response(
                    VehiculosTransporteSerializer(vehiculo, context={'request': request}).data,
                    status=status.HTTP_201_CREATED
                )

            logger.error(f'VehiculosTransporteAPIView POST: datos inválidos: {serializer.errors}')
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f'VehiculosTransporteAPIView POST: error: {e}', exc_info=True)
            return Response({'message': f'Error al crear vehículo: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, format=None):
        try:
            vehiculo_ids = request.data.get('ids', [])
            vehiculos = VehiculosTransporte.objects.filter(id__in=vehiculo_ids)
            for vehiculo in vehiculos:
                self._delete_vehiculo_files(vehiculo)
            VehiculosTransporte.objects.filter(id__in=vehiculo_ids).delete()
            logger.debug(f'VehiculosTransporteAPIView DELETE: {len(vehiculo_ids)} vehículos eliminados')
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error(f'VehiculosTransporteAPIView DELETE: error: {e}', exc_info=True)
            return Response({'message': f'Error al eliminar vehículos: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request, format=None):
        return self.put(request, format)

    def put(self, request, format=None):
        try:
            vehiculo_id = request.data.get('id')
            if not vehiculo_id:
                return Response({'message': 'ID de vehículo es necesario para actualizar'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                vehiculo = VehiculosTransporte.objects.get(id=vehiculo_id)
            except VehiculosTransporte.DoesNotExist:
                logger.error(f'VehiculosTransporteAPIView PUT: vehículo {vehiculo_id} no encontrado')
                return Response({'message': 'Vehículo no encontrado'}, status=status.HTTP_404_NOT_FOUND)

            vehiculo_data = {
                'holding': request.data.get('holding'),
                'empresa': request.data.get('empresa'),
                'tipo': request.data.get('tipo'),
                'ppu': request.data.get('ppu'),
                'modelo': request.data.get('modelo'),
                'year': request.data.get('year'),
                'color': request.data.get('color'),
                'num_pasajeros': request.data.get('num_pasajeros'),
                'marca': request.data.get('marca'),
            }

            serializer = VehiculosTransporteSerializer(vehiculo, data=vehiculo_data)
            if serializer.is_valid():
                vehiculo = serializer.save()
                self._process_documents(request, vehiculo)
                return Response(VehiculosTransporteSerializer(vehiculo, context={'request': request}).data)

            logger.error(f'VehiculosTransporteAPIView PUT: datos inválidos para vehículo {vehiculo_id}: {serializer.errors}')
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f'VehiculosTransporteAPIView PUT: error: {e}', exc_info=True)
            return Response({'message': f'Error al actualizar vehículo: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _process_documents(self, request, vehiculo):
        documento_files = [f for k, f in request.FILES.items() if k.startswith('documento_')]
        if not documento_files:
            return

        try:
            validate_uploaded_documents(documento_files)
        except ValidationError as e:
            logger.error(f'VehiculosTransporteAPIView _process_documents: error validando documentos: {e}')
            return

        rutas = []
        for doc_file in documento_files:
            timestamp = int(time.time())
            file_name = f'vehiculo_{vehiculo.id}_{timestamp}_{doc_file.name}'
            file_path = f'transporte/archivos_vehiculos/documentos/{file_name}'
            saved_path = default_storage.save(file_path, ContentFile(doc_file.read()))
            rutas.append(saved_path)

        doc_db, created = DocumentosVehiculo.objects.get_or_create(
            vehiculo=vehiculo,
            tipo='documentos_varios',
            defaults={'documentos_rutas': rutas}
        )

        if not created:
            for old_path in doc_db.documentos_rutas:
                if default_storage.exists(old_path):
                    default_storage.delete(old_path)
            doc_db.documentos_rutas = rutas
            doc_db.save()

    def _delete_vehiculo_files(self, vehiculo):
        for documento in DocumentosVehiculo.objects.filter(vehiculo=vehiculo):
            for doc_path in documento.documentos_rutas:
                if default_storage.exists(doc_path):
                    default_storage.delete(doc_path)


# ==============================================================================
# CHOFERES TRANSPORTE
# ==============================================================================

class ChoferesTransporteAPIView(BaseAPIView):

    def get(self, request, format=None):
        holding_id = request.query_params.get('holding')
        if not holding_id:
            return Response({'message': 'holding_id es requerido'}, status=status.HTTP_400_BAD_REQUEST)
        choferes = ChoferesTransporte.objects.filter(holding_id=holding_id)
        return Response(ChoferesTransporteSerializer(choferes, many=True, context={'request': request}).data)

    def post(self, request, format=None):
        try:
            chofer_data = {
                'holding': request.data.get('holding'),
                'empresa': request.data.get('empresa'),
                'nombre': request.data.get('nombre'),
                'rut': request.data.get('rut'),
                'licencia': request.data.get('licencia'),
                'vehiculo': request.data.get('vehiculo'),
            }

            serializer = ChoferesTransporteSerializer(data=chofer_data)
            if serializer.is_valid():
                chofer = serializer.save()
                self._process_images(request, chofer)
                self._process_documents(request, chofer)
                logger.debug(f'ChoferesTransporteAPIView POST: chofer {chofer.id} creado')
                return Response(
                    ChoferesTransporteSerializer(chofer, context={'request': request}).data,
                    status=status.HTTP_201_CREATED
                )

            logger.error(f'ChoferesTransporteAPIView POST: datos inválidos: {serializer.errors}')
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f'ChoferesTransporteAPIView POST: error: {e}', exc_info=True)
            return Response({'message': f'Error al crear chofer: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, format=None):
        try:
            chofer_id = request.data.get('id')
            if not chofer_id:
                return Response({'message': 'ID de chofer es necesario para actualizar'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                chofer = ChoferesTransporte.objects.get(id=chofer_id)
            except ChoferesTransporte.DoesNotExist:
                logger.error(f'ChoferesTransporteAPIView PUT: chofer {chofer_id} no encontrado')
                return Response({'message': 'Chofer no encontrado'}, status=status.HTTP_404_NOT_FOUND)

            chofer_data = {
                'holding': request.data.get('holding'),
                'empresa': request.data.get('empresa'),
                'nombre': request.data.get('nombre'),
                'rut': request.data.get('rut'),
                'licencia': request.data.get('licencia'),
                'vehiculo': request.data.get('vehiculo'),
            }

            serializer = ChoferesTransporteSerializer(chofer, data=chofer_data)
            if serializer.is_valid():
                chofer = serializer.save()
                self._process_images(request, chofer)
                self._process_documents(request, chofer)
                return Response(ChoferesTransporteSerializer(chofer, context={'request': request}).data)

            logger.error(f'ChoferesTransporteAPIView PUT: datos inválidos para chofer {chofer_id}: {serializer.errors}')
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f'ChoferesTransporteAPIView PUT: error: {e}', exc_info=True)
            return Response({'message': f'Error al actualizar chofer: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, format=None):
        try:
            chofer_ids = request.data.get('ids', [])
            choferes = ChoferesTransporte.objects.filter(id__in=chofer_ids)
            for chofer in choferes:
                self._delete_chofer_files(chofer)
            ChoferesTransporte.objects.filter(id__in=chofer_ids).delete()
            logger.debug(f'ChoferesTransporteAPIView DELETE: {len(chofer_ids)} choferes eliminados')
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error(f'ChoferesTransporteAPIView DELETE: error: {e}', exc_info=True)
            return Response({'message': f'Error al eliminar choferes: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request, format=None):
        return self.put(request, format)

    def _process_images(self, request, chofer):
        tipos_imagen = ['foto_licencia_frontal', 'foto_licencia_trasera', 'foto_cedula_frontal', 'foto_cedula_trasera']
        for tipo in tipos_imagen:
            file_key = f'imagen_{tipo}'
            if file_key not in request.FILES:
                continue

            imagen_file = request.FILES[file_key]
            extension = imagen_file.name.lower().split('.')[-1]
            if extension not in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                continue

            documento, created = DocumentosChofer.objects.get_or_create(
                chofer=chofer, tipo=tipo, defaults={'imagen': imagen_file}
            )

            if not created:
                if documento.imagen:
                    old_path = documento.imagen.path
                    if os.path.exists(old_path):
                        os.remove(old_path)
                documento.imagen = imagen_file
                documento.save()

    def _process_documents(self, request, chofer):
        documento_files = [f for k, f in request.FILES.items() if k.startswith('documento_')]
        if not documento_files:
            return

        try:
            validate_uploaded_documents(documento_files)
        except ValidationError as e:
            logger.error(f'ChoferesTransporteAPIView _process_documents: error validando documentos: {e}')
            return

        rutas = []
        for doc_file in documento_files:
            timestamp = int(time.time())
            file_name = f'chofer_{chofer.id}_{timestamp}_{doc_file.name}'
            file_path = f'transporte/archivos_choferes/documentos/{file_name}'
            saved_path = default_storage.save(file_path, ContentFile(doc_file.read()))
            rutas.append(saved_path)

        doc_db, created = DocumentosChofer.objects.get_or_create(
            chofer=chofer,
            tipo='documentos_varios',
            defaults={'documentos_rutas': rutas}
        )

        if not created:
            for old_path in doc_db.documentos_rutas:
                if default_storage.exists(old_path):
                    default_storage.delete(old_path)
            doc_db.documentos_rutas = rutas
            doc_db.save()

    def _delete_chofer_files(self, chofer):
        for documento in DocumentosChofer.objects.filter(chofer=chofer):
            if documento.imagen:
                image_path = documento.imagen.path
                if os.path.exists(image_path):
                    os.remove(image_path)
            for doc_path in documento.documentos_rutas:
                if default_storage.exists(doc_path):
                    default_storage.delete(doc_path)


# ==============================================================================
# TRAMOS
# ==============================================================================

class TramosAPIView(BaseAPIView):

    def get(self, request, format=None):
        holding_id = request.query_params.get('holding')
        if not holding_id:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        tramos = Tramos.objects.filter(holding_id=holding_id)
        return Response(TramosSerializer(tramos, many=True).data)

    def post(self, request, format=None):
        serializer = TramosSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        logger.error(f'TramosAPIView POST: datos inválidos: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, format=None):
        holding_id = request.query_params.get('holding')
        tramo_id = request.data.get('id')

        if not tramo_id:
            return Response({'error': 'Se requiere el id del tramo'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            tramo = Tramos.objects.get(id=tramo_id, holding_id=holding_id)
        except Tramos.DoesNotExist:
            logger.error(f'TramosAPIView PUT: tramo {tramo_id} no encontrado en holding {holding_id}')
            return Response({'error': 'Tramo no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        serializer = TramosSerializer(tramo, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        logger.error(f'TramosAPIView PUT: datos inválidos para tramo {tramo_id}: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, format=None):
        ids = request.data.get('ids', [])
        Tramos.objects.filter(id__in=ids).delete()
        logger.debug(f'TramosAPIView DELETE: {len(ids)} tramos eliminados')
        return Response(status=status.HTTP_204_NO_CONTENT)


# ==============================================================================
# FOLIO TRANSPORTISTA
# ==============================================================================

class FolioTransportistaAPIView(BaseAPIView):

    def get(self, request, format=None):
        holding_id = request.query_params.get('holding')
        if not holding_id:
            return Response({'error': "El parámetro 'holding' es requerido"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            folios = FolioTransportista.objects.filter(holding_id=holding_id)
            return Response(FolioTransportistaSerializer(folios, many=True).data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f'FolioTransportistaAPIView GET: error: {e}', exc_info=True)
            return Response({'error': f'Error al obtener los folios: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, format=None):
        serializer = FolioTransportistaSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.error(f'FolioTransportistaAPIView POST: error al guardar: {e}', exc_info=True)
                return Response({'error': f'Error al crear el folio: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        logger.error(f'FolioTransportistaAPIView POST: datos inválidos: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, format=None):
        folio_id = request.data.get('id')
        if not folio_id:
            return Response({'error': 'Se requiere el ID del folio'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            folio = FolioTransportista.objects.get(id=folio_id)
        except FolioTransportista.DoesNotExist:
            logger.error(f'FolioTransportistaAPIView PUT: folio {folio_id} no encontrado')
            return Response({'error': 'Folio no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        serializer = FolioTransportistaSerializer(folio, data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Exception as e:
                logger.error(f'FolioTransportistaAPIView PUT: error al guardar folio {folio_id}: {e}', exc_info=True)
                return Response({'error': f'Error al actualizar el folio: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        logger.error(f'FolioTransportistaAPIView PUT: datos inválidos para folio {folio_id}: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, format=None):
        folio_ids = request.data.get('ids', [])
        if not folio_ids:
            return Response({'error': 'Se requiere al menos un ID de folio'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            FolioTransportista.objects.filter(id__in=folio_ids).delete()
            logger.debug(f'FolioTransportistaAPIView DELETE: {len(folio_ids)} folios eliminados')
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error(f'FolioTransportistaAPIView DELETE: error: {e}', exc_info=True)
            return Response({'error': f'Error al eliminar los folios: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request, format=None):
        folio_id = request.data.get('id')
        if not folio_id:
            return Response({'error': 'Se requiere el ID del folio'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            folio = FolioTransportista.objects.get(id=folio_id)
        except FolioTransportista.DoesNotExist:
            logger.error(f'FolioTransportistaAPIView PATCH: folio {folio_id} no encontrado')
            return Response({'error': 'Folio no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        serializer = FolioTransportistaSerializer(folio, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Exception as e:
                logger.error(f'FolioTransportistaAPIView PATCH: error al guardar folio {folio_id}: {e}', exc_info=True)
                return Response({'error': f'Error al actualizar el folio: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        logger.error(f'FolioTransportistaAPIView PATCH: datos inválidos para folio {folio_id}: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ==============================================================================
# CONFIRMAR PAGO TRANSPORTISTA
# ==============================================================================

class ConfirmarPagoTransportistaAPIView(BaseAPIView):
    required_scopes = ['superadmin_access', 'admin', 'write']


# ==============================================================================
# PAGO TRANSPORTISTA
# ==============================================================================

class PagoTransportistaAPIView(BaseAPIView):

    def get(self, request):
        holding_id = request.query_params.get('holding')
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')
        empresas = request.query_params.get('empresas')

        if not all([holding_id, fecha_inicio, fecha_fin, empresas]):
            return Response({'error': 'Faltan parámetros requeridos'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            empresa_ids = [int(i) for i in empresas.split(',')]
            fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()

            resultados = []

            for empresa_id in empresa_ids:
                personal = PersonalTrabajadores.objects.filter(
                    holding_id=holding_id, transportista_id=empresa_id
                )
                folio = FolioTransportista.objects.filter(
                    holding_id=holding_id, transportista_id=empresa_id
                ).first()

                if not folio:
                    continue

                detalles_diarios = []
                fecha_actual = fecha_inicio
                total_monto = 0

                while fecha_actual <= fecha_fin:
                    personas_dia = ProduccionTrabajador.objects.filter(
                        holding_id=holding_id,
                        trabajador__in=personal,
                        hora_fecha_ingreso_produccion__date=fecha_actual
                    ).values('trabajador').distinct().count()

                    if personas_dia > 0:
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
            logger.error(f'PagoTransportistaAPIView GET: error: {e}', exc_info=True)
            return Response({'error': f'Error al calcular los pagos: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
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
                pago = PagoTransportista.objects.create(
                    holding_id=holding_id,
                    sociedad_id=sociedad_id,
                    transportista_id=transportista_id,
                    fecha_desde=fecha_inicio,
                    fecha_hasta=fecha_fin,
                    metodo_pago=metodo_pago,
                    cuenta_origen_id=cuenta_id,
                    usuario_registra=request.user,
                    monto=sum(d['monto_dia'] for d in detalles),
                    total_personas=sum(d['cantidad_personas'] for d in detalles),
                    total_dias=len(detalles),
                    valor_por_unidad=request.data.get('valor_unidad'),
                    tipo_pago=request.data.get('tipo_pago')
                )

                for detalle in detalles:
                    DetallePagoTransportista.objects.create(
                        pago=pago,
                        fecha=detalle['fecha'],
                        cantidad_personas=detalle['cantidad_personas'],
                        monto_dia=detalle['monto_dia']
                    )

            logger.debug(f'PagoTransportistaAPIView POST: pago {pago.id} registrado')
            return Response(PagoTransportistaSerializer(pago).data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f'PagoTransportistaAPIView POST: error: {e}', exc_info=True)
            return Response({'error': f'Error al registrar el pago: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==============================================================================
# CÁLCULO PAGO TRANSPORTISTA
# ==============================================================================

class CalculoPagoTransportistaView(BaseAPIView):

    def get(self, request):
        holding_id = request.query_params.get('holding')
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')
        empresas = request.query_params.get('empresas')

        if not all([holding_id, fecha_inicio, fecha_fin]):
            return Response({'error': 'Faltan parámetros requeridos'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
            empresa_ids = [int(i) for i in empresas.split(',')] if empresas else []

            query = EmpresasTransporte.objects.filter(holding_id=holding_id)
            if empresa_ids:
                query = query.filter(id__in=empresa_ids)

            resultados = []

            for empresa in query:
                if not empresa.folio_transportista:
                    continue

                trabajadores = PersonalTrabajadores.objects.filter(
                    holding_id=holding_id, transportista=empresa, estado=True
                )

                current_date = fecha_inicio
                while current_date <= fecha_fin:
                    count = ProduccionTrabajador.objects.filter(
                        holding_id=holding_id,
                        trabajador__in=trabajadores,
                        hora_fecha_ingreso_produccion__date=current_date,
                        pagado=False
                    ).values('trabajador').distinct().count()

                    if count > 0:
                        folio = empresa.folio_transportista
                        monto = (
                            folio.valor_pago_transportista * count
                            if folio.tramo.unidad_pago == 'PASAJERO'
                            else folio.valor_pago_transportista
                        )

                        resultados.append({
                            'fecha': current_date,
                            'transportista_nombre': empresa.nombre,
                            'transportista_rut': empresa.rut,
                            'tipo_pago': folio.tramo.unidad_pago,
                            'valor_unidad': folio.valor_pago_transportista,
                            'cantidad_personas': count,
                            'monto_calculado': monto,
                            'tramo': {
                                'origen': folio.tramo.origen,
                                'destino': folio.tramo.destino
                            }
                        })

                    current_date += timedelta(days=1)

            return Response(resultados)

        except Exception as e:
            logger.error(f'CalculoPagoTransportistaView GET: error: {e}', exc_info=True)
            return Response({'error': f'Error al calcular los pagos: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==============================================================================
# INFORME TRANSPORTISTA
# ==============================================================================

class InformeTransportistaAPIView(BaseAPIView):

    def get(self, request):
        holding_id = request.query_params.get('holding')
        if not holding_id:
            return Response({'error': 'Holding ID es requerido'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = InformeTransportistaSerializer(holding_id)
        return Response(serializer.data)

    def post(self, request):
        serializer = InformeTransportistaSerializer(data=request.data)
        if not serializer.is_valid():
            logger.error(f'InformeTransportistaAPIView POST: datos inválidos: {serializer.errors}')
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        fecha_inicio = serializer.validated_data['fecha_inicio']
        fecha_fin = serializer.validated_data['fecha_fin']
        cliente_ids = serializer.validated_data.get('cliente_ids')
        transportista_ids = serializer.validated_data.get('transportista_ids')
        vehiculo_ids = serializer.validated_data.get('vehiculo_ids')

        base_query = ProduccionTrabajador.objects.filter(
            hora_fecha_ingreso_produccion__date__range=(fecha_inicio, fecha_fin),
            holding_id=request.data.get('holding', 1)
        )

        if cliente_ids:
            base_query = base_query.filter(folio__cliente_id__in=cliente_ids)
        if transportista_ids:
            base_query = base_query.filter(trabajador__transportista_id__in=transportista_ids)
        if vehiculo_ids:
            base_query = base_query.filter(trabajador__vehiculo_id__in=vehiculo_ids)

        results = []
        totales_por_transportista = {}
        current_date = fecha_inicio

        while current_date <= fecha_fin:
            daily_prod = base_query.filter(
                hora_fecha_ingreso_produccion__date=current_date
            ).select_related(
                'trabajador', 'trabajador__transportista', 'trabajador__vehiculo',
                'trabajador__transportista__folio_transportista',
                'trabajador__transportista__folio_transportista__tramo',
                'folio', 'folio__cliente'
            )

            if daily_prod.exists():
                transport_groups = {}
                for prod in daily_prod:
                    if not (prod.trabajador and prod.trabajador.transportista and prod.folio and prod.folio.cliente):
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
                        }

                    transport_groups[key]['pasajeros'].add(prod.trabajador.id)

                for group_data in transport_groups.values():
                    transportista = group_data['transportista']
                    vehiculo = group_data['vehiculo']
                    cliente = group_data['cliente']
                    num_pasajeros = len(group_data['pasajeros'])

                    if not transportista.folio_transportista:
                        continue

                    folio = transportista.folio_transportista
                    if not folio.tramo:
                        continue

                    minimo_requerido = getattr(folio.tramo, 'minimo_pasajeros', 0) or 0
                    valor_pagar = (
                        folio.valor_pago_transportista * num_pasajeros
                        if folio.tramo.unidad_pago == 'PASAJERO'
                        else folio.valor_pago_transportista if num_pasajeros >= minimo_requerido else 0
                    )

                    totales_por_transportista[transportista.id] = (
                        totales_por_transportista.get(transportista.id, 0) + valor_pagar
                    )

                    results.append({
                        'fecha': current_date,
                        'cliente': cliente.nombre,
                        'empresa_transporte': transportista.nombre,
                        'vehiculo': f'{vehiculo.ppu} - {vehiculo.modelo}' if vehiculo else 'No asignado',
                        'chofer': self._get_chofer_name(transportista, vehiculo),
                        'cantidad_pasajeros': num_pasajeros,
                        'valor_pago': valor_pagar,
                        'unidad_control': folio.tramo.unidad_pago,
                        'origen': folio.tramo.origen,
                        'destino': folio.tramo.destino,
                        'total_acumulado': totales_por_transportista[transportista.id]
                    })

            current_date += timedelta(days=1)

        logger.debug(f'InformeTransportistaAPIView POST: {len(results)} registros generados')
        return Response({
            'registros': results,
            'metadata': {
                'fecha_inicio': fecha_inicio,
                'fecha_fin': fecha_fin,
                'total_registros': len(results),
                'totales_por_transportista': totales_por_transportista
            }
        })

    def _get_chofer_name(self, transportista, vehiculo):
        if not vehiculo:
            return 'No asignado'
        chofer = ChoferesTransporte.objects.filter(empresa=transportista, vehiculo=vehiculo).first()
        return chofer.nombre if chofer else 'Sin chofer asignado'


# ==============================================================================
# GENERAR PROFORMA TRANSPORTISTA
# ==============================================================================

class GenerarProformaTransportistaAPIView(BaseAPIView):

    def get(self, request, proforma_id=None):
        if proforma_id is not None:
            try:
                proforma = ProformaTransportista.objects.get(
                    id=proforma_id, holding_id=request.user.holding_id
                )

                if not proforma.documento_pdf:
                    return Response({'error': 'No se encontró el documento PDF'}, status=status.HTTP_404_NOT_FOUND)

                response = HttpResponse(proforma.documento_pdf.read(), content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="proforma_{proforma.id}.pdf"'
                return response

            except ProformaTransportista.DoesNotExist:
                logger.error(f'GenerarProformaTransportistaAPIView GET: proforma {proforma_id} no encontrada')
                return Response({'error': 'Proforma no encontrada'}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                logger.error(f'GenerarProformaTransportistaAPIView GET: error obteniendo PDF: {e}', exc_info=True)
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
                    queryset = queryset.filter(fecha_emision__range=[fecha_inicio, fecha_fin])
                if estado:
                    queryset = queryset.filter(estado=estado)
                if transportista_id:
                    queryset = queryset.filter(transportista_id=transportista_id)

                queryset = queryset.order_by('-fecha_emision')
                return Response({
                    'proformas': ProformaTransportistaSerializer(queryset, many=True).data,
                    'total': queryset.count()
                })

            except Exception as e:
                logger.error(f'GenerarProformaTransportistaAPIView GET (lista): error: {e}', exc_info=True)
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            data = request.data
            holding_id = request.user.holding_id
            sociedad_id = data.get('sociedad')
            transportista_id = data.get('transportistas')[0]
            fecha_inicio = data.get('fecha_inicio_periodo')
            fecha_fin = data.get('fecha_fin_periodo')
            fecha_emision = data.get('fecha_emision')
            fecha_vencimiento = data.get('fecha_vencimiento')

            sociedad = Sociedad.objects.get(id=sociedad_id)
            transportista = EmpresasTransporte.objects.get(id=transportista_id)

            trabajadores = PersonalTrabajadores.objects.filter(transportista=transportista)
            producciones = ProduccionTrabajador.objects.filter(
                trabajador__in=trabajadores,
                hora_fecha_ingreso_produccion__date__range=[fecha_inicio, fecha_fin],
                proforma='PENDIENTE'
            )

            if not producciones.exists():
                return Response(
                    {'error': 'No hay producciones disponibles para generar proforma en el período seleccionado'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            total_personas = 0
            fechas_unicas = set()

            for prod in producciones:
                if not transportista.folio_transportista or not transportista.folio_transportista.tramo:
                    continue
                total_personas += 1
                fechas_unicas.add(prod.hora_fecha_ingreso_produccion.date().isoformat())

            tramo = transportista.folio_transportista.tramo
            tipo_servicio = tramo.unidad_pago
            valor_pago = transportista.folio_transportista.valor_pago_transportista

            total_general = (
                valor_pago * total_personas
                if tipo_servicio == 'PASAJERO'
                else valor_pago * len(fechas_unicas)
            )

            proforma = ProformaTransportista(
                holding_id=holding_id,
                sociedad=sociedad,
                transportista=transportista,
                fecha_emision=fecha_emision,
                fecha_vencimiento=fecha_vencimiento,
                fecha_inicio_periodo=fecha_inicio,
                fecha_fin_periodo=fecha_fin,
                tramo=f'{tramo.origen}-{tramo.destino}',
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

            title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=16, spaceAfter=30)
            proforma_number_style = ParagraphStyle(
                'ProformaNumber', parent=styles['Heading1'], fontSize=14, alignment=TA_RIGHT, spaceAfter=30
            )

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

            detalles_data = [['Origen', 'Destino', 'Tipo', 'Total Personas', 'Total Días', 'Valor Unit.', 'Total']]
            detalles_data.append([
                tramo.origen, tramo.destino, tipo_servicio,
                str(total_personas), str(len(fechas_unicas)),
                f'${valor_pago:,.0f}', f'${total_general:,.0f}'
            ])
            detalles_data.append(['', '', '', '', '', 'Total:', f'${total_general:,.0f}'])

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

            doc.build(elements)
            buffer.seek(0)

            pdf_filename = f'proforma_{proforma.id}.pdf'
            proforma.documento_pdf.save(pdf_filename, ContentFile(buffer.getvalue()), save=True)

            producciones.update(proforma='EMITIDO')

            logger.debug(f'GenerarProformaTransportistaAPIView POST: proforma {proforma.id} generada')
            return Response({'message': 'Proforma generada exitosamente', 'proforma_id': proforma.id})

        except Exception as e:
            logger.error(f'GenerarProformaTransportistaAPIView POST: error: {e}', exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, proforma_id):
        try:
            proforma = ProformaTransportista.objects.get(
                id=proforma_id, holding_id=request.user.holding_id
            )

            if proforma.estado != 'EMITIDO':
                return Response(
                    {'error': 'Solo se pueden facturar proformas en estado EMITIDO'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            required_fields = ['factura_fecha', 'factura_numero', 'factura_rut', 'factura_monto']
            if not all(f in request.data for f in required_fields):
                return Response(
                    {'error': 'Se requieren todos los datos de la factura'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            proforma.factura_fecha = request.data['factura_fecha']
            proforma.factura_numero = request.data['factura_numero']
            proforma.factura_rut = request.data['factura_rut']
            proforma.factura_monto = request.data['factura_monto']
            proforma.estado = 'FACTURADO'
            proforma.save()

            logger.debug(f'GenerarProformaTransportistaAPIView PUT: proforma {proforma_id} facturada')
            return Response({
                'message': 'Proforma actualizada a estado FACTURADO exitosamente',
                'proforma_id': proforma.id
            })

        except ProformaTransportista.DoesNotExist:
            logger.error(f'GenerarProformaTransportistaAPIView PUT: proforma {proforma_id} no encontrada')
            return Response({'error': 'Proforma no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f'GenerarProformaTransportistaAPIView PUT: error: {e}', exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)