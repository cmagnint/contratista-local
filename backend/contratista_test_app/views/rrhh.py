import calendar
import csv
import io
import logging
import os
import tempfile
import zipfile
import zoneinfo
from collections import defaultdict
from datetime import date, datetime, timedelta
from decimal import Decimal
from io import BytesIO
from math import floor

from django.db import transaction
from django.db.models import  Q, Sum
from django.http import HttpResponse
from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    Flowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .base import BaseAPIView
from ..models import (
    AFPTrabajadores,
    CasasTrabajadores,
    ContratoTrabajador,
    Descuentos,
    DiasTrabajadosAprobados,
    Haberes,
    HoraExtraordinaria,
    LicenciaMedica,
    MesCerrado,
    PersonalTrabajadores,
    ProduccionTrabajador,
    RegistroAsistencia,
    RegistroManoObraPersona,
    SaludTrabajadores,
    Sociedad,
    Supervisores,
    SupervisorTrabajadorHistorial,
    TrabajadorDescuento,
    TrabajadorHaber,
    UnidadControl,
    Vacaciones,
    RegistroCasaTrabajador,
)
from ..serializers import (
    AFPTrabajadoresSerializer,
    ArchivoPreviewSerializer,
    CasasTrabajadoresSerializer,
    DescuentosSerializer,
    HaberesSerializer,
    MesCerradoSerializer,
    PersonalConAsignacionesSerializer,
    RegistroManoObraPersonaSerializer,
    SaludTrabajadoresSerializer,
    FolioComercialLabor,
)

logger = logging.getLogger('contratista_test_app')


# ==============================================================================
# SALUD TRABAJADORES
# ==============================================================================

class SaludTrabajadoresAPIView(BaseAPIView):

    def get(self, request, format=None):
        holding_id = request.query_params.get('holding')
        if not holding_id:
            return Response({'message': 'holding_id es requerido'}, status=status.HTTP_400_BAD_REQUEST)
        salud = SaludTrabajadores.objects.filter(holding_id=holding_id)
        return Response(SaludTrabajadoresSerializer(salud, many=True).data)

    def put(self, request, format=None):
        salud_id = request.data.get('id')
        try:
            salud = SaludTrabajadores.objects.get(id=salud_id)
        except SaludTrabajadores.DoesNotExist:
            logger.error(f'SaludTrabajadoresAPIView PUT: registro {salud_id} no encontrado')
            return Response({'message': 'Registro de salud no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        porcentaje = request.data.get('porcentaje')
        if porcentaje is None:
            return Response({'message': 'Porcentaje es requerido'}, status=status.HTTP_400_BAD_REQUEST)

        salud.porcentaje = porcentaje
        salud.save()
        return Response(SaludTrabajadoresSerializer(salud).data)


# ==============================================================================
# AFP TRABAJADORES
# ==============================================================================

class AFPTrabajadoresAPIView(BaseAPIView):

    def get(self, request, format=None):
        holding_id = request.query_params.get('holding')
        if not holding_id:
            return Response({'message': 'holding_id es requerido'}, status=status.HTTP_400_BAD_REQUEST)
        afp = AFPTrabajadores.objects.filter(holding_id=holding_id)
        return Response(AFPTrabajadoresSerializer(afp, many=True).data)

    def put(self, request, format=None):
        afp_id = request.data.get('id')
        try:
            afp = AFPTrabajadores.objects.get(id=afp_id)
        except AFPTrabajadores.DoesNotExist:
            logger.error(f'AFPTrabajadoresAPIView PUT: AFP {afp_id} no encontrada')
            return Response({'message': 'AFP no encontrada'}, status=status.HTTP_404_NOT_FOUND)

        campos_permitidos = [
            'porcentaje_cotizacion_individual',
            'comision_afp',
            'porcentaje_cargo_empleador',
            'porcentaje_seguro_social',
        ]
        data_to_update = {c: request.data[c] for c in campos_permitidos if c in request.data}

        if not data_to_update:
            return Response({'message': 'No hay campos válidos para actualizar'}, status=status.HTTP_400_BAD_REQUEST)

        for campo, valor in data_to_update.items():
            setattr(afp, campo, valor)
        afp.save()
        return Response(AFPTrabajadoresSerializer(afp).data)


# ==============================================================================
# CASAS TRABAJADORES
# ==============================================================================

class CasasTrabajadoresAPIView(BaseAPIView):

    def get(self, request, format=None):
        holding_id = request.query_params.get('holding')
        if not holding_id:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        casas = CasasTrabajadores.objects.filter(holding_id=holding_id)
        return Response(CasasTrabajadoresSerializer(casas, many=True).data)

    def post(self, request, format=None):
        serializer = CasasTrabajadoresSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error(f'CasasTrabajadoresAPIView POST: datos inválidos: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, format=None):
        ids = request.data.get('ids', [])
        CasasTrabajadores.objects.filter(id__in=ids).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, format=None):
        obj_id = request.data.get('id')
        if not obj_id:
            return Response({'message': 'ID es necesario para actualizar'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            casa = CasasTrabajadores.objects.get(id=obj_id)
        except CasasTrabajadores.DoesNotExist:
            logger.error(f'CasasTrabajadoresAPIView PATCH: casa {obj_id} no encontrada')
            return Response({'message': 'Perfil no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        serializer = CasasTrabajadoresSerializer(casa, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        logger.error(f'CasasTrabajadoresAPIView PATCH: datos inválidos: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, format=None):
        obj_id = request.data.get('id')
        try:
            casa = CasasTrabajadores.objects.get(id=obj_id)
        except CasasTrabajadores.DoesNotExist:
            logger.error(f'CasasTrabajadoresAPIView PUT: casa {obj_id} no encontrada')
            return Response({'message': 'Cargo no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        serializer = CasasTrabajadoresSerializer(casa, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        logger.error(f'CasasTrabajadoresAPIView PUT: datos inválidos: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ==============================================================================
# INFORME CASAS TRABAJADORES
# ==============================================================================

class InformeCasasAPIView(BaseAPIView):
    def get(self, request, format=None):
        holding_id = request.query_params.get('holding')
        fecha = request.query_params.get('fecha')  # YYYY-MM-DD opcional

        if not holding_id:
            return Response({'message': 'holding requerido'}, status=status.HTTP_400_BAD_REQUEST)

        from django.utils import timezone
        if not fecha:
            fecha = timezone.now().date()

        registros = RegistroCasaTrabajador.objects.filter(
            holding_id=holding_id,
            fecha_inicio__lte=fecha,
        ).filter(
            Q(fecha_fin__gte=fecha) | Q(fecha_fin__isnull=True)
        ).select_related('trabajador', 'casa')

        casas = CasasTrabajadores.objects.filter(holding_id=holding_id, estado=True)

        data = []
        for casa in casas:
            ocupantes = [
                {
                    'id': r.trabajador.id,
                    'nombres': r.trabajador.nombres,
                    'apellidos': r.trabajador.apellidos,
                    'rut': r.trabajador.rut,
                    'fecha_inicio': r.fecha_inicio,
                    'fecha_fin': r.fecha_fin,
                }
                for r in registros if r.casa_id == casa.id
            ]
            data.append({
                'casa_id': casa.id,
                'casa_nombre': casa.nombre,
                'total': len(ocupantes),
                'ocupantes': ocupantes,
            })

        sin_casa = [
            {
                'id': r.trabajador.id,
                'nombres': r.trabajador.nombres,
                'apellidos': r.trabajador.apellidos,
                'rut': r.trabajador.rut,
                'fecha_inicio': r.fecha_inicio,
                'fecha_fin': r.fecha_fin,
            }
            for r in registros if r.casa_id is None
        ]
        if sin_casa:
            data.append({
                'casa_id': None,
                'casa_nombre': 'Sin casa',
                'total': len(sin_casa),
                'ocupantes': sin_casa,
            })

        return Response({'fecha': fecha, 'casas': data})
    
# ==============================================================================
# INFORME DÍAS TRABAJADOS
# ==============================================================================

class InformeDiasTrabajadosAPIView(BaseAPIView):

    def post(self, request):
        try:
            holding_id = request.data.get('holding_id')
            if not holding_id:
                return Response({'error': 'Holding ID is required'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                year = int(request.data.get('year'))
                mes = int(request.data.get('mes'))
            except (ValueError, TypeError):
                return Response({'error': 'Year and month must be valid integers'}, status=status.HTTP_400_BAD_REQUEST)

            def parse_optional_int(val):
                if val and val not in ('', 'null'):
                    try:
                        return int(val)
                    except (ValueError, TypeError):
                        pass
                return None

            cliente_id = parse_optional_int(request.data.get('cliente_id'))
            fundo_id = parse_optional_int(request.data.get('fundo_id'))
            casa_id = parse_optional_int(request.data.get('casa_id'))
            supervisor_id = parse_optional_int(request.data.get('supervisor_id'))
            trabajador_id = parse_optional_int(request.data.get('trabajador_id'))

            last_day = calendar.monthrange(year, mes)[1]
            start_date = date(year, mes, 1)
            end_date = date(year, mes, last_day)

            productions_query = ProduccionTrabajador.objects.filter(
                holding_id=holding_id,
                hora_fecha_ingreso_produccion__date__range=[start_date, end_date]
            ).select_related('trabajador', 'folio__cliente')

            if cliente_id:
                productions_query = productions_query.filter(folio__cliente_id=cliente_id)
            if fundo_id:
                productions_query = productions_query.filter(trabajador__fundo_id=fundo_id)
            if casa_id:
                productions_query = productions_query.filter(trabajador__casa_id=casa_id)
            if supervisor_id:
                productions_query = productions_query.filter(trabajador__supervisor_directo__id=supervisor_id)
            if trabajador_id:
                productions_query = productions_query.filter(trabajador_id=trabajador_id)

            all_clients = {}
            worker_data = {}

            for prod in productions_query:
                if not prod.trabajador or not prod.hora_fecha_ingreso_produccion:
                    continue

                worker_id = prod.trabajador.id

                if prod.folio and prod.folio.cliente:
                    client_id = prod.folio.cliente.id
                    client_name = prod.folio.cliente.nombre
                    all_clients[client_id] = client_name
                else:
                    client_id = None

                day = prod.hora_fecha_ingreso_produccion.day

                if worker_id not in worker_data:
                    worker_data[worker_id] = {
                        'worker': prod.trabajador,
                        'days_worked': set(),
                        'client_days': defaultdict(set),
                    }

                if 1 <= day <= last_day:
                    worker_data[worker_id]['days_worked'].add(day)
                    if client_id is not None:
                        worker_data[worker_id]['client_days'][client_id].add(day)

            client_list = sorted(
                [{'id': cid, 'nombre': cname} for cid, cname in all_clients.items()],
                key=lambda x: x['nombre']
            )

            result = {
                'trabajadores': [],
                'clientes': client_list,
                'fechas': [date(year, mes, d).isoformat() for d in range(1, last_day + 1)]
            }

            for worker_id, data in worker_data.items():
                worker = data['worker']
                dias_por_cliente = {}
                client_totals = {}

                for cid, days in data['client_days'].items():
                    cliente_name = all_clients.get(cid, 'Cliente desconocido')
                    dias_por_cliente[cliente_name] = len(days)
                    client_totals[cid] = len(days)

                result['trabajadores'].append({
                    'id': worker.id,
                    'nombres': worker.nombres,
                    'apellidos': worker.apellidos or '',
                    'rut': worker.rut or '',
                    'fecha_ingreso': worker.fecha_ingreso.isoformat() if worker.fecha_ingreso else None,
                    'dias_por_cliente': dias_por_cliente,
                    'client_totals': client_totals,
                    'dias_totales': len(data['days_worked'])
                })

            result['trabajadores'].sort(key=lambda x: (x['nombres'], x['apellidos']))
            return Response(result)

        except Exception as e:
            logger.error(f'InformeDiasTrabajadosAPIView POST: error: {e}', exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==============================================================================
# DÍAS TRABAJADOS APROBADOS
# ==============================================================================

class DiasTrabajadosAprobadosAPIView(BaseAPIView):

    def get(self, request):
        try:
            registro_id = request.query_params.get('id')
            if registro_id:
                try:
                    registro = DiasTrabajadosAprobados.objects.get(id=int(registro_id))
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
                    logger.error(f'DiasTrabajadosAprobadosAPIView GET: registro {registro_id} no encontrado')
                    return Response(
                        {'error': f'No se encontró el registro con ID {registro_id}'},
                        status=status.HTTP_404_NOT_FOUND
                    )

            holding_id = request.query_params.get('holding_id')
            if not holding_id:
                return Response({'error': 'El parámetro holding_id es obligatorio'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                holding_id = int(holding_id)
            except ValueError:
                return Response({'error': 'El holding_id debe ser un número entero válido'}, status=status.HTTP_400_BAD_REQUEST)

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
                    return Response({'error': 'El mes debe estar entre 1 y 12'}, status=status.HTTP_400_BAD_REQUEST)
            except ValueError:
                return Response(
                    {'error': 'Los parámetros mes y year deben ser números enteros válidos'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            query = Q(holding_id=holding_id) & Q(mes=mes) & Q(year=year)

            trabajador_id = request.query_params.get('trabajador_id')
            if trabajador_id:
                try:
                    query &= Q(trabajador_id=int(trabajador_id))
                except ValueError:
                    pass

            registros = DiasTrabajadosAprobados.objects.filter(query)
            resultados = [
                {
                    'id': r.id,
                    'trabajador_id': r.trabajador_id,
                    'mes': r.mes,
                    'year': r.year,
                    'dias_por_cliente': r.dias_por_cliente,
                    'reducciones_aplicadas': r.reducciones_aplicadas,
                    'dias_totales': r.dias_totales,
                    'fecha_aprobacion': r.fecha_aprobacion
                }
                for r in registros
            ]
            return Response(resultados)

        except Exception as e:
            logger.error(f'DiasTrabajadosAprobadosAPIView GET: error: {e}', exc_info=True)
            return Response({'error': f'Error al obtener los registros: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            data = request.data
            holding_id = data.get('holding_id')
            trabajador_id = data.get('trabajador_id')
            mes = data.get('mes')
            year = data.get('year')

            mes_cerrado = MesCerrado.objects.filter(holding_id=holding_id, mes=mes, year=year).first()
            if mes_cerrado:
                return Response(
                    {
                        'error': 'No se pueden modificar los días trabajados para un mes cerrado',
                        'fecha_cierre': mes_cerrado.fecha_cierre,
                        'usuario_cierre': (
                            mes_cerrado.usuario_cierre.persona.nombres
                            if mes_cerrado.usuario_cierre and mes_cerrado.usuario_cierre.persona
                            else 'Usuario desconocido'
                        )
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

            registro, created = DiasTrabajadosAprobados.objects.update_or_create(
                holding_id=holding_id,
                trabajador_id=trabajador_id,
                mes=mes,
                year=year,
                defaults={
                    'dias_por_cliente': data.get('dias_por_cliente'),
                    'reducciones_aplicadas': data.get('reducciones_aplicadas'),
                    'dias_totales': data.get('dias_totales'),
                    'usuario_aprueba_id': request.user.id,
                    'modificado_por_id': request.user.id,
                }
            )

            logger.debug(f'DiasTrabajadosAprobadosAPIView POST: registro {registro.id} {"creado" if created else "actualizado"}')
            return Response({'mensaje': 'Registro guardado correctamente', 'id': registro.id, 'created': created})

        except Exception as e:
            logger.error(f'DiasTrabajadosAprobadosAPIView POST: error: {e}', exc_info=True)
            return Response({'error': f'Error al guardar el registro: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request):
        try:
            data = request.data
            holding_id = data.get('holding_id')
            mes = data.get('mes')
            year = data.get('year')

            if not all([holding_id, mes, year]):
                return Response({'error': 'Se requieren holding_id, mes y año'}, status=status.HTTP_400_BAD_REQUEST)

            mes_cerrado = MesCerrado.objects.filter(holding_id=holding_id, mes=mes, year=year).first()
            if mes_cerrado:
                return Response(
                    {
                        'error': 'No se pueden eliminar los registros para un mes cerrado',
                        'fecha_cierre': mes_cerrado.fecha_cierre,
                        'usuario_cierre': (
                            mes_cerrado.usuario_cierre.persona.nombres
                            if mes_cerrado.usuario_cierre and mes_cerrado.usuario_cierre.persona
                            else 'Usuario desconocido'
                        )
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

            resultado = DiasTrabajadosAprobados.objects.filter(
                holding_id=holding_id, mes=mes, year=year
            ).delete()

            logger.debug(f'DiasTrabajadosAprobadosAPIView DELETE: {resultado[0]} registros eliminados')
            return Response({'mensaje': f'Se han eliminado {resultado[0]} registros correctamente', 'cantidad': resultado[0]})

        except Exception as e:
            logger.error(f'DiasTrabajadosAprobadosAPIView DELETE: error: {e}', exc_info=True)
            return Response({'error': f'Error al eliminar los registros: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==============================================================================
# MES CERRADO
# ==============================================================================

class MesCerradoAPIView(BaseAPIView):

    def get(self, request):
        holding_id = request.query_params.get('holding_id')
        if not holding_id:
            return Response({'error': 'Se requiere el ID del holding'}, status=status.HTTP_400_BAD_REQUEST)

        mes = request.query_params.get('mes')
        year = request.query_params.get('year')

        if mes and year:
            try:
                mes = int(mes)
                year = int(year)
            except ValueError:
                return Response({'error': 'Mes o año inválido'}, status=status.HTTP_400_BAD_REQUEST)

            mes_cerrado = MesCerrado.objects.filter(holding_id=holding_id, mes=mes, year=year).first()
            if mes_cerrado:
                data = MesCerradoSerializer(mes_cerrado).data
                data['is_closed'] = True
                return Response(data)
            return Response({'mes': mes, 'year': year, 'is_closed': False})

        meses_cerrados = MesCerrado.objects.filter(holding_id=holding_id).order_by('-year', '-mes')
        return Response(MesCerradoSerializer(meses_cerrados, many=True).data)

    def post(self, request):
        try:
            data = request.data
            holding_id = data.get('holding_id')
            mes = data.get('mes')
            year = data.get('year')
            motivo = data.get('motivo', '')

            if not all([holding_id, mes, year]):
                return Response({'error': 'Se requieren holding_id, mes y año'}, status=status.HTTP_400_BAD_REQUEST)

            if MesCerrado.objects.filter(holding_id=holding_id, mes=mes, year=year).exists():
                return Response({'error': 'El mes ya está cerrado'}, status=status.HTTP_400_BAD_REQUEST)

            mes_cerrado = MesCerrado.objects.create(
                holding_id=holding_id, mes=mes, year=year,
                usuario_cierre=request.user, motivo=motivo
            )
            logger.debug(f'MesCerradoAPIView POST: mes {mes}/{year} cerrado en holding {holding_id}')
            return Response(MesCerradoSerializer(mes_cerrado).data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f'MesCerradoAPIView POST: error: {e}', exc_info=True)
            return Response({'error': f'Error al cerrar el mes: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request):
        try:
            data = request.data
            holding_id = data.get('holding_id')
            mes = data.get('mes')
            year = data.get('year')

            if not all([holding_id, mes, year]):
                return Response({'error': 'Se requieren holding_id, mes y año'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                mes_cerrado = MesCerrado.objects.get(holding_id=holding_id, mes=mes, year=year)
                mes_cerrado.delete()
                logger.debug(f'MesCerradoAPIView DELETE: mes {mes}/{year} abierto en holding {holding_id}')
                return Response({'message': f'El mes {mes}/{year} ha sido abierto'})
            except MesCerrado.DoesNotExist:
                logger.error(f'MesCerradoAPIView DELETE: mes {mes}/{year} no está cerrado')
                return Response({'error': 'El mes no está cerrado'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            logger.error(f'MesCerradoAPIView DELETE: error: {e}', exc_info=True)
            return Response({'error': f'Error al abrir el mes: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==============================================================================
# HABERES
# ==============================================================================

class HaberesAPIView(BaseAPIView):

    def get(self, request, format=None):
        holding_id = request.query_params.get('holding')
        if not holding_id:
            return Response({'error': 'El parámetro holding es necesario'}, status=status.HTTP_400_BAD_REQUEST)
        haberes = Haberes.objects.filter(holding_id=holding_id).order_by('orden')
        return Response(HaberesSerializer(haberes, many=True).data)

    def post(self, request, format=None):
        serializer = HaberesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error(f'HaberesAPIView POST: datos inválidos: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, format=None):
        haber_id = request.data.get('id')
        try:
            haber = Haberes.objects.get(id=haber_id)
        except Haberes.DoesNotExist:
            logger.error(f'HaberesAPIView PUT: haber {haber_id} no encontrado')
            return Response({'message': 'Haber no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        serializer = HaberesSerializer(haber, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        logger.error(f'HaberesAPIView PUT: datos inválidos: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, format=None):
        ids = request.data.get('ids', [])
        Haberes.objects.filter(id__in=ids).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, format=None):
        haber_id = request.data.get('id')
        if not haber_id:
            return Response({'message': 'ID de haber es necesario para actualizar'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            haber = Haberes.objects.get(id=haber_id)
        except Haberes.DoesNotExist:
            logger.error(f'HaberesAPIView PATCH: haber {haber_id} no encontrado')
            return Response({'message': 'Haber no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        serializer = HaberesSerializer(haber, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        logger.error(f'HaberesAPIView PATCH: datos inválidos: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ==============================================================================
# DESCUENTOS
# ==============================================================================

class DescuentosAPIView(BaseAPIView):

    def get(self, request, format=None):
        holding_id = request.query_params.get('holding')
        if not holding_id:
            return Response({'error': 'El parámetro holding es necesario'}, status=status.HTTP_400_BAD_REQUEST)
        descuentos = Descuentos.objects.filter(holding_id=holding_id).order_by('orden')
        return Response(DescuentosSerializer(descuentos, many=True).data)

    def post(self, request, format=None):
        serializer = DescuentosSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error(f'DescuentosAPIView POST: datos inválidos: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, format=None):
        descuento_id = request.data.get('id')
        try:
            descuento = Descuentos.objects.get(id=descuento_id)
        except Descuentos.DoesNotExist:
            logger.error(f'DescuentosAPIView PUT: descuento {descuento_id} no encontrado')
            return Response({'message': 'Descuento no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        serializer = DescuentosSerializer(descuento, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        logger.error(f'DescuentosAPIView PUT: datos inválidos: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, format=None):
        ids = request.data.get('ids', [])
        Descuentos.objects.filter(id__in=ids).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, format=None):
        descuento_id = request.data.get('id')
        if not descuento_id:
            return Response({'message': 'ID de descuento es necesario para actualizar'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            descuento = Descuentos.objects.get(id=descuento_id)
        except Descuentos.DoesNotExist:
            logger.error(f'DescuentosAPIView PATCH: descuento {descuento_id} no encontrado')
            return Response({'message': 'Descuento no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        serializer = DescuentosSerializer(descuento, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        logger.error(f'DescuentosAPIView PATCH: datos inválidos: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ==============================================================================
# ASIGNAR HABERES
# ==============================================================================

class AsignarHaberesAPIView(BaseAPIView):

    def post(self, request):
        holding_id = request.data.get('holding_id')
        trabajador_ids = request.data.get('trabajador_ids', [])
        haberes_asignaciones = request.data.get('haberes_asignaciones', [])

        if not holding_id or not trabajador_ids:
            return Response({'error': 'Se requieren holding_id y trabajador_ids'}, status=status.HTTP_400_BAD_REQUEST)

        trabajadores = PersonalTrabajadores.objects.filter(id__in=trabajador_ids, holding_id=holding_id)
        if len(trabajadores) != len(trabajador_ids):
            return Response(
                {'error': 'Algunos trabajadores no existen o no pertenecen al holding'},
                status=status.HTTP_400_BAD_REQUEST
            )

        for trabajador in trabajadores:
            for asignacion in haberes_asignaciones:
                if asignacion.get('trabajador_id') == trabajador.id:
                    TrabajadorHaber.objects.update_or_create(
                        trabajador=trabajador,
                        haber_id=asignacion.get('haber_id'),
                        defaults={'valor': asignacion.get('valor')}
                    )

        logger.debug(f'AsignarHaberesAPIView POST: haberes asignados a {len(trabajadores)} trabajadores')
        return Response(PersonalConAsignacionesSerializer(
            PersonalTrabajadores.objects.filter(id__in=trabajador_ids), many=True
        ).data)


# ==============================================================================
# ASIGNAR DESCUENTOS
# ==============================================================================

class AsignarDescuentosAPIView(BaseAPIView):

    def post(self, request):
        holding_id = request.data.get('holding_id')
        trabajador_ids = request.data.get('trabajador_ids', [])
        descuentos_data = request.data.get('descuentos', [])

        if not holding_id or not trabajador_ids:
            return Response({'error': 'Se requieren holding_id y trabajador_ids'}, status=status.HTTP_400_BAD_REQUEST)
        if not descuentos_data:
            return Response({'error': 'Se debe especificar al menos un descuento'}, status=status.HTTP_400_BAD_REQUEST)

        trabajadores = PersonalTrabajadores.objects.filter(id__in=trabajador_ids, holding_id=holding_id)
        if len(trabajadores) != len(trabajador_ids):
            return Response(
                {'error': 'Algunos trabajadores no existen o no pertenecen al holding'},
                status=status.HTTP_400_BAD_REQUEST
            )

        descuento_ids = [d['id'] for d in descuentos_data]
        descuentos_objs = Descuentos.objects.filter(id__in=descuento_ids, holding_id=holding_id)
        if descuentos_objs.count() != len(descuento_ids):
            return Response(
                {'error': 'Algunos descuentos no existen o no pertenecen al holding'},
                status=status.HTTP_400_BAD_REQUEST
            )

        descuentos_map = {d.id: d for d in descuentos_objs}

        with transaction.atomic():
            for trabajador in trabajadores:
                TrabajadorDescuento.objects.filter(trabajador=trabajador).delete()

                for desc_data in descuentos_data:
                    descuento_id = desc_data['id']
                    valor = desc_data['valor']
                    es_cuota = desc_data.get('es_cuota', False)
                    num_cuotas = desc_data.get('num_cuotas', 1) if es_cuota else 1

                    descuento = descuentos_map.get(descuento_id)
                    if not descuento:
                        continue

                    if es_cuota and num_cuotas > 1 and not descuento.cuota:
                        return Response(
                            {'error': f'El descuento {descuento.nombre} no admite cuotas'},
                            status=status.HTTP_400_BAD_REQUEST
                        )

                    valor_cuota = valor / num_cuotas if num_cuotas > 0 else valor
                    TrabajadorDescuento.objects.create(
                        trabajador=trabajador,
                        descuento=descuento,
                        valor_total=valor,
                        num_cuotas=num_cuotas,
                        cuota_actual=1,
                        valor_cuota=valor_cuota
                    )

        logger.debug(f'AsignarDescuentosAPIView POST: descuentos asignados a {len(trabajadores)} trabajadores')
        return Response(PersonalConAsignacionesSerializer(trabajadores, many=True).data)


# ==============================================================================
# GENERAR LIQUIDACIONES
# ==============================================================================

class GenerarLiquidacionesAPIView(BaseAPIView):

    def post(self, request):
        holding_id = request.data.get('holding_id')
        sociedad_id = request.data.get('sociedad_id')
        mes = request.data.get('mes')
        year = request.data.get('year')
        cliente_id = request.data.get('cliente_id')
        fundo_id = request.data.get('fundo_id')
        casa_id = request.data.get('casa_id')

        if not all([holding_id, sociedad_id, mes, year]):
            return Response({'error': 'Holding, sociedad, mes y año son obligatorios'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            sociedad = Sociedad.objects.get(id=sociedad_id, holding_id=holding_id)
        except Sociedad.DoesNotExist:
            logger.error(f'GenerarLiquidacionesAPIView POST: sociedad {sociedad_id} no encontrada')
            return Response({'error': 'Sociedad no encontrada'}, status=status.HTTP_404_NOT_FOUND)

        dias_aprobados_query = DiasTrabajadosAprobados.objects.filter(holding_id=holding_id, mes=mes, year=year)

        if sociedad_id:
            trabajadores_sociedad = PersonalTrabajadores.objects.filter(sociedad_id=sociedad_id).values_list('id', flat=True)
            dias_aprobados_query = dias_aprobados_query.filter(trabajador_id__in=trabajadores_sociedad)

        if not dias_aprobados_query.exists():
            return Response(
                {'error': 'No hay días trabajados aprobados para el período seleccionado.'},
                status=status.HTTP_404_NOT_FOUND
            )

        trabajadores_ids_con_dias = dias_aprobados_query.values_list('trabajador_id', flat=True)
        query = Q(id__in=trabajadores_ids_con_dias, holding_id=holding_id, estado=True, sociedad_id=sociedad_id)

        if casa_id:
            query &= Q(casa_id=casa_id)

        trabajadores = PersonalTrabajadores.objects.filter(query)
        if not trabajadores.exists():
            return Response(
                {'error': 'No se encontraron trabajadores con días aprobados y los filtros aplicados'},
                status=status.HTTP_404_NOT_FOUND
            )

        temp_dir = tempfile.mkdtemp()
        zip_filename = f'liquidaciones_{sociedad.nombre}_{year}_{mes}.zip'
        zip_path = os.path.join(temp_dir, zip_filename)

        liquidaciones_data = []
        meses_espanol = {
            1: 'ENERO', 2: 'FEBRERO', 3: 'MARZO', 4: 'ABRIL', 5: 'MAYO', 6: 'JUNIO',
            7: 'JULIO', 8: 'AGOSTO', 9: 'SEPTIEMBRE', 10: 'OCTUBRE', 11: 'NOVIEMBRE', 12: 'DICIEMBRE'
        }
        nombre_mes = meses_espanol.get(int(mes), '')

        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for trabajador in trabajadores:
                try:
                    dias_aprobados = DiasTrabajadosAprobados.objects.get(
                        holding_id=holding_id, trabajador=trabajador, mes=mes, year=year
                    )
                    dias_trabajados = dias_aprobados.dias_totales
                    if dias_trabajados == 0:
                        continue
                except DiasTrabajadosAprobados.DoesNotExist:
                    continue

                haberes = TrabajadorHaber.objects.filter(trabajador=trabajador).select_related('haber')
                descuentos = TrabajadorDescuento.objects.filter(trabajador=trabajador).select_related('descuento')

                sueldo_base_diario = trabajador.sueldo_base / 30 if trabajador.sueldo_base else 0
                sueldo_base_total = sueldo_base_diario * dias_trabajados

                lista_haberes = [{'nombre': 'Sueldo base', 'cantidad': dias_trabajados, 'valor': sueldo_base_total, 'imponible': True}]
                for h in haberes:
                    lista_haberes.append({'nombre': h.haber.nombre, 'cantidad': None, 'valor': h.valor, 'imponible': h.haber.imponible})

                total_haberes = sum(h['valor'] for h in lista_haberes)
                total_imponible = sum(h['valor'] for h in lista_haberes if h['imponible'])
                total_no_imponible = total_haberes - total_imponible

                afp_porcentaje = float(getattr(trabajador.afp, 'porcentaje_descuento', 10.0)) if trabajador.afp else 10.0
                salud_porcentaje = float(getattr(trabajador.salud, 'porcentaje_descuento', 7.0)) if trabajador.salud else 7.0

                afp_valor = (total_imponible * afp_porcentaje) / 100
                salud_valor = (total_imponible * salud_porcentaje) / 100

                lista_descuentos = [
                    {'nombre': f"A.F.P. {trabajador.afp.nombre if trabajador.afp else 'N/A'}", 'porcentaje': afp_porcentaje, 'valor': afp_valor},
                    {'nombre': f"{trabajador.salud.nombre if trabajador.salud else 'FONASA'}", 'porcentaje': salud_porcentaje, 'valor': salud_valor},
                ]
                for d in descuentos:
                    lista_descuentos.append({'nombre': d.descuento.nombre, 'porcentaje': None, 'valor': d.valor_cuota})

                total_descuentos = sum(d['valor'] for d in lista_descuentos)
                liquido_a_pagar = total_haberes - total_descuentos

                pdf_buffer = BytesIO()
                self.generar_pdf_liquidacion(
                    pdf_buffer, sociedad, trabajador, lista_haberes, lista_descuentos,
                    {
                        'total_haberes': total_haberes,
                        'total_imponible': total_imponible,
                        'total_no_imponible': total_no_imponible,
                        'total_descuentos': total_descuentos,
                        'liquido_a_pagar': liquido_a_pagar,
                        'total_tributable': total_imponible
                    },
                    dias_trabajados, nombre_mes, year
                )

                pdf_filename = f'liquidacion_{trabajador.rut}_{mes}_{year}.pdf'
                zipf.writestr(pdf_filename, pdf_buffer.getvalue())

                liquidaciones_data.append({
                    'trabajador_id': trabajador.id,
                    'nombre': f'{trabajador.nombres} {trabajador.apellidos or ""}'.strip(),
                    'rut': trabajador.rut,
                    'total_haberes': float(total_haberes),
                    'total_descuentos': float(total_descuentos),
                    'liquido_a_pagar': float(liquido_a_pagar)
                })

        if not liquidaciones_data:
            return Response(
                {'error': 'No se pudieron generar liquidaciones para los trabajadores seleccionados.'},
                status=status.HTTP_404_NOT_FOUND
            )

        with open(zip_path, 'rb') as zipf:
            response = HttpResponse(zipf.read(), content_type='application/zip')
            response['Content-Disposition'] = f'attachment; filename="{zip_filename}"'
            response['X-Liquidaciones-Count'] = str(len(liquidaciones_data))
            logger.debug(f'GenerarLiquidacionesAPIView POST: {len(liquidaciones_data)} liquidaciones generadas')
            return response

    def generar_pdf_liquidacion(self, buffer, sociedad, trabajador, haberes, descuentos, totales, dias_trabajados, mes, year):
        doc = SimpleDocTemplate(buffer, pagesize=letter,
                                leftMargin=0.5*inch, rightMargin=0.5*inch,
                                topMargin=0.5*inch, bottomMargin=0.5*inch)
        styles = getSampleStyleSheet()
        elements = []

        header_data = [
            [f'{sociedad.nombre}', f'Periodo: {mes}', f'Del {year}'],
            [f'{sociedad.rol_sociedad}', '', '']
        ]
        header_table = Table(header_data, colWidths=[4*inch, 2*inch, 1.5*inch])
        header_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 0.1*inch))

        title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], alignment=1, fontSize=12, fontName='Helvetica-Bold')
        elements.append(Paragraph('Liquidacion de Remuneraciones**', title_style))
        elements.append(Spacer(1, 0.1*inch))

        cell_style = ParagraphStyle('CellStyle', parent=styles['Normal'], fontSize=8, leading=10)
        nombre_completo = f'{trabajador.nombres} {trabajador.apellidos or ""}'.strip()

        employee_data = [
            [Paragraph('Nombre Trabajador:', cell_style), Paragraph(nombre_completo, cell_style),
             Paragraph('Fecha Ingreso:', cell_style), trabajador.fecha_ingreso.strftime('%d/%m/%Y') if trabajador.fecha_ingreso else ''],
            [Paragraph('Rut Trabajador:', cell_style), trabajador.rut, Paragraph('Días Licencia Médica:', cell_style), ''],
            [Paragraph('Código Trabajador:', cell_style), f'{trabajador.id}', Paragraph('Días de Falla:', cell_style), ''],
            [Paragraph('Sueldo Mensual:', cell_style), f'${trabajador.sueldo_base:,.2f}' if trabajador.sueldo_base else '', Paragraph('Días Permiso no Remunerado:', cell_style), '']
        ]
        employee_table = Table(employee_data, colWidths=[1.6*inch, 2.4*inch, 1.6*inch, 1.9*inch])
        employee_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        elements.append(employee_table)
        elements.append(Spacer(1, 0.1*inch))

        max_rows = max(len(haberes), len(descuentos))
        detail_data = [['Haberes', '', '', 'Descuentos', '', '']]

        sueldo_base_item = next((item for item in haberes if item['nombre'] == 'Sueldo base'), None)
        if sueldo_base_item:
            haberes = [h for h in haberes if h['nombre'] != 'Sueldo base']
            detail_data.append([
                'Sueldo base', f'{dias_trabajados}', f"${sueldo_base_item['valor']:,.0f}",
                descuentos[0]['nombre'] if descuentos else '',
                f"{descuentos[0]['porcentaje']}%" if descuentos and descuentos[0]['porcentaje'] is not None else '',
                f"${descuentos[0]['valor']:,.0f}" if descuentos else ''
            ])
            start_idx = 1
        else:
            start_idx = 0

        for i in range(start_idx, max_rows):
            hi = i - 1 if sueldo_base_item else i
            di = i
            haber_row = ['', '', ''] if hi >= len(haberes) else [
                haberes[hi]['nombre'],
                f"{haberes[hi]['cantidad']}" if haberes[hi]['cantidad'] is not None else '',
                f"${haberes[hi]['valor']:,.0f}"
            ]
            desc_row = ['', '', ''] if di >= len(descuentos) else [
                descuentos[di]['nombre'],
                f"{descuentos[di]['porcentaje']}%" if descuentos[di]['porcentaje'] is not None else '',
                f"${descuentos[di]['valor']:,.0f}"
            ]
            detail_data.append(haber_row + desc_row)

        for _ in range(6):
            detail_data.append([''] * 6)

        detail_data.extend([
            ['Total de Haberes $', '', f"${totales['total_haberes']:,.0f}", 'Total Descuentos..$', '', f"${totales['total_descuentos']:,.0f}"],
            ['Total Imponible...$', '', f"${totales['total_imponible']:,.0f}", 'Total Líquido......$', '', f"${totales['liquido_a_pagar']:,.0f}"],
            ['Total No Impon...$', '', f"${totales['total_no_imponible']:,.0f}", 'Ajuste Sencillo.....$', '', '0'],
            ['Total Tributable...$', '', f"${totales['total_tributable']:,.0f}", 'Líquido a Pagar.....$', '', f"${totales['liquido_a_pagar']:,.0f}"],
        ])

        detail_table = Table(detail_data, colWidths=[1.6*inch, 0.8*inch, 1.1*inch, 1.6*inch, 0.8*inch, 1.1*inch])
        style = [
            ('SPAN', (0, 0), (2, 0)), ('SPAN', (3, 0), (5, 0)),
            ('ALIGN', (0, 0), (0, 0), 'CENTER'), ('ALIGN', (3, 0), (3, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 0), (2, 0), colors.lightgrey),
            ('BACKGROUND', (3, 0), (5, 0), colors.lightgrey),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ALIGN', (2, 1), (2, -1), 'RIGHT'), ('ALIGN', (5, 1), (5, -1), 'RIGHT'),
            ('FONTNAME', (0, -4), (-1, -1), 'Helvetica-Bold'),
            ('LINEABOVE', (0, -4), (-1, -4), 1, colors.black),
            ('BOX', (0, 0), (2, -1), 0.5, colors.black),
            ('BOX', (3, 0), (5, -1), 0.5, colors.black),
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
        ]
        detail_table.setStyle(TableStyle(style))
        elements.append(detail_table)
        elements.append(Spacer(1, 0.2*inch))

        cant_style = ParagraphStyle('CantidadStyle', parent=styles['Normal'], fontSize=8, leading=10)
        try:
            elements.append(Paragraph(f"Son: {self.numero_a_texto(totales['liquido_a_pagar'])}", cant_style))
        except Exception:
            elements.append(Paragraph(f"Son: {int(totales['liquido_a_pagar'])} PESOS", cant_style))

        elements.append(Paragraph(f'{dias_trabajados} De {mes} Del {year}', cant_style))
        elements.append(Spacer(1, 0.3*inch))

        cert_style = ParagraphStyle('CertStyle', parent=styles['Normal'], fontSize=8, leading=10)
        elements.append(Paragraph(
            'Certifico que he revisado la presente liquidación a mi entera satisfacción y no tengo cargo ni cobro alguno posterior que hacer por ninguno de los conceptos comprendidos en ella.',
            cert_style
        ))
        elements.append(Spacer(1, 1*inch))

        class SignatureSection(Flowable):
            def __init__(self):
                Flowable.__init__(self)
                self.width = 7*inch
                self.height = 0.5*inch

            def draw(self):
                self.canv.line(self.width/2 - 2*inch, 0, self.width/2 + 2*inch, 0)
                self.canv.setFont('Helvetica', 8)
                self.canv.drawRightString(self.width/2 + 2*inch, 10, 'Recibí Conforme')

        elements.append(SignatureSection())
        doc.build(elements)
        return buffer

    def numero_a_texto(self, numero):
        unidades = ['', 'UNO', 'DOS', 'TRES', 'CUATRO', 'CINCO', 'SEIS', 'SIETE', 'OCHO', 'NUEVE']
        decenas = ['', 'DIEZ', 'VEINTE', 'TREINTA', 'CUARENTA', 'CINCUENTA', 'SESENTA', 'SETENTA', 'OCHENTA', 'NOVENTA']
        centenas = ['', 'CIENTO', 'DOSCIENTOS', 'TRESCIENTOS', 'CUATROCIENTOS', 'QUINIENTOS', 'SEISCIENTOS', 'SETECIENTOS', 'OCHOCIENTOS', 'NOVECIENTOS']
        especiales = {
            11: 'ONCE', 12: 'DOCE', 13: 'TRECE', 14: 'CATORCE', 15: 'QUINCE',
            16: 'DIECISEIS', 17: 'DIECISIETE', 18: 'DIECIOCHO', 19: 'DIECINUEVE',
            21: 'VEINTIUNO', 22: 'VEINTIDOS', 23: 'VEINTITRES', 24: 'VEINTICUATRO',
            25: 'VEINTICINCO', 26: 'VEINTISEIS', 27: 'VEINTISIETE', 28: 'VEINTIOCHO', 29: 'VEINTINUEVE'
        }

        def convert(n):
            if n == 0: return 'CERO'
            if n < 10: return unidades[n]
            if n in especiales: return especiales[n]
            if n < 100:
                return decenas[n // 10] if n % 10 == 0 else f'{decenas[n // 10]} Y {unidades[n % 10]}'
            if n < 1000:
                if n == 100: return 'CIEN'
                r = n % 100
                return centenas[n // 100] if r == 0 else f'{centenas[n // 100]} {convert(r)}'
            if n < 1000000:
                mil = n // 1000
                r = n % 1000
                mil_text = 'MIL' if mil == 1 else f'{convert(mil)} MIL'
                return mil_text if r == 0 else f'{mil_text} {convert(r)}'
            mil = n // 1000000
            r = n % 1000000
            mil_text = 'UN MILLON' if mil == 1 else f'{convert(mil)} MILLONES'
            return mil_text if r == 0 else f'{mil_text} {convert(r)}'

        try:
            return f'{convert(int(floor(abs(numero))))} PESOS'
        except Exception as e:
            logger.error(f'numero_a_texto: error convirtiendo {numero}: {e}')
            return f'{int(numero)} PESOS'


# ==============================================================================
# LIBRO REMUNERACIONES ELECTRÓNICO
# ==============================================================================

class LibroRemuneracionesElectronicoAPIView(BaseAPIView):

    def get(self, request):
        try:
            holding_id = request.query_params.get('holding_id')
            sociedad_id = request.query_params.get('sociedad_id')

            if not holding_id:
                return Response({'error': 'El parámetro holding_id es requerido'}, status=status.HTTP_400_BAD_REQUEST)
            if not sociedad_id:
                return Response({'error': 'El parámetro sociedad_id es requerido'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                mes = int(request.query_params.get('mes', '0'))
                anio = int(request.query_params.get('anio', '0'))
            except (TypeError, ValueError):
                return Response({'error': 'Los parámetros mes y anio deben ser números enteros válidos'}, status=status.HTTP_400_BAD_REQUEST)

            if mes < 1 or mes > 12:
                return Response({'error': 'El mes debe estar entre 1 y 12'}, status=status.HTTP_400_BAD_REQUEST)

            current_year = datetime.now().year
            if anio < 2000 or anio > current_year + 1:
                return Response({'error': f'El año debe estar entre 2000 y {current_year + 1}'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                sociedad = Sociedad.objects.get(id=sociedad_id, holding_id=holding_id)
            except Sociedad.DoesNotExist:
                logger.error(f'LibroRemuneracionesElectronicoAPIView GET: sociedad {sociedad_id} no encontrada')
                return Response({'error': 'Sociedad no encontrada'}, status=status.HTTP_404_NOT_FOUND)

            trabajadores = PersonalTrabajadores.objects.filter(
                sociedad_id=sociedad_id, holding_id=holding_id, estado=True
            ).select_related('afp', 'salud')

            if not trabajadores.exists():
                return Response({'error': 'No hay trabajadores activos para esta sociedad'}, status=status.HTTP_404_NOT_FOUND)

            buffer = io.StringIO()
            writer = csv.writer(buffer, delimiter=';')
            headers = self.get_csv_headers()
            writer.writerow(headers)

            primer_dia = date(anio, mes, 1)
            if mes == 12:
                ultimo_dia = date(anio + 1, 1, 1).replace(day=1) - timedelta(days=1)
            else:
                ultimo_dia = date(anio, mes + 1, 1).replace(day=1) - timedelta(days=1)

            for trabajador in trabajadores:
                row_data = self.procesar_trabajador(trabajador, sociedad, mes, anio, primer_dia, ultimo_dia)
                writer.writerow(row_data[:len(headers)])

            buffer.seek(0)
            response = HttpResponse(buffer.getvalue(), content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="Libro_Remuneraciones_{sociedad.nombre}_{mes}_{anio}.csv"'
            logger.debug(f'LibroRemuneracionesElectronicoAPIView GET: generado para {trabajadores.count()} trabajadores')
            return response

        except Exception as e:
            logger.error(f'LibroRemuneracionesElectronicoAPIView GET: error: {e}', exc_info=True)
            return Response({'error': f'Error al generar el libro de remuneraciones: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_csv_headers(self):
        return [
            "Rut trabajador(1101)", "Fecha inicio contrato(1102)", "Fecha término de contrato(1103)",
            "Causal término de contrato(1104)", "Región prestación de servicios(1105)",
            "Comuna prestación de servicios(1106)", "Tipo impuesto a la renta(1170)",
            "Técnico extranjero exención cot. previsionales(1146)", "Código tipo de jornada(1107)",
            "Persona con Discapacidad - Pensionado por Invalidez(1108)", "Pensionado por vejez(1109)",
            "AFP(1141)", "IPS (ExINP)(1142)", "FONASA - ISAPRE(1143)", "AFC(1151)", "CCAF(1110)",
            "Org. administrador ley 16.744(1152)", "Nro cargas familiares legales autorizadas(1111)",
            "Nro de cargas familiares maternales(1112)", "Nro de cargas familiares invalidez(1113)",
            "Tramo asignación familiar(1114)",
            "Rut org sindical 1(1171)", "Rut org sindical 2(1172)", "Rut org sindical 3(1173)",
            "Rut org sindical 4(1174)", "Rut org sindical 5(1175)", "Rut org sindical 6(1176)",
            "Rut org sindical 7(1177)", "Rut org sindical 8(1178)", "Rut org sindical 9(1179)",
            "Rut org sindical 10(1180)",
            "Nro días trabajados en el mes(1115)", "Nro días de licencia médica en el mes(1116)",
            "Nro días de vacaciones en el mes(1117)", "Subsidio trabajador joven(1118)",
            "Puesto Trabajo Pesado(1154)", "APVI(1155)", "APVC(1157)",
            "Indemnización a todo evento(1131)", "Tasa indemnización a todo evento(1132)",
            "Sueldo(2101)", "Sobresueldo(2102)", "Comisiones(2103)", "Semana corrida(2104)",
            "Participación(2105)", "Gratificación(2106)", "Recargo 30% día domingo(2107)",
            "Remun. variable pagada en vacaciones(2108)", "Remun. variable pagada en clausura(2109)",
            "Aguinaldo(2110)", "Bonos u otras remun. fijas mensuales(2111)", "Tratos(2112)",
            "Bonos u otras remun. variables mensuales o superiores a un mes(2113)",
            "Ejercicio opción no pactada en contrato(2114)",
            "Beneficios en especie constitutivos de remun(2115)",
            "Remuneraciones bimestrales(2116)", "Remuneraciones trimestrales(2117)",
            "Remuneraciones cuatrimestral(2118)", "Remuneraciones semestrales(2119)",
            "Remuneraciones anuales(2120)", "Participación anual(2121)", "Gratificación anual(2122)",
            "Otras remuneraciones superiores a un mes(2123)",
            "Pago por horas de trabajo sindical(2124)", "Sueldo empresarial (2161)",
            "Subsidio por incapacidad laboral por licencia médica(2201)", "Beca de estudio(2202)",
            "Gratificaciones de zona(2203)", "Otros ingresos no constitutivos de renta(2204)",
            "Colación(2301)", "Movilización(2302)", "Viáticos(2303)",
            "Asignación de pérdida de caja(2304)", "Asignación de desgaste herramienta(2305)",
            "Asignación familiar legal(2311)", "Gastos por causa del trabajo(2306)",
            "Gastos por cambio de residencia(2307)", "Sala cuna(2308)",
            "Asignación trabajo a distancia o teletrabajo(2309)",
            "Depósito convenido hasta UF 900(2347)", "Alojamiento por razones de trabajo(2310)",
            "Asignación de traslación(2312)", "Indemnización por feriado legal(2313)",
            "Indemnización años de servicio(2314)", "Indemnización sustitutiva del aviso previo(2315)",
            "Indemnización fuero maternal(2316)", "Pago indemnización a todo evento(2331)",
            "Indemnizaciones voluntarias tributables(2417)", "Indemnizaciones contractuales tributables(2418)",
            "Cotización obligatoria previsional (AFP o IPS)(3141)",
            "Cotización obligatoria salud 7%(3143)", "Cotización voluntaria para salud(3144)",
            "Cotización AFC - trabajador(3151)",
            "Cotizaciones técnico extranjero para seguridad social fuera de Chile(3146)",
            "Descuento depósito convenido hasta UF 900 anual(3147)",
            "Cotización APVi Mod A(3155)", "Cotización APVi Mod B hasta UF50(3156)",
            "Cotización APVc Mod A(3157)", "Cotización APVc Mod B hasta UF50(3158)",
            "Impuesto retenido por remuneraciones(3161)", "Impuesto retenido por indemnizaciones(3162)",
            "Mayor retención de impuestos solicitada por el trabajador(3163)",
            "Impuesto retenido por reliquidación remun. devengadas otros períodos(3164)",
            "Diferencia impuesto reliquidación remun. devengadas en este período(3165)",
            "Retención préstamo clase media 2020 (Ley 21.252) (3166)",
            "Rebaja zona extrema DL 889 (3167)",
            "Cuota sindical 1(3171)", "Cuota sindical 2(3172)", "Cuota sindical 3(3173)",
            "Cuota sindical 4(3174)", "Cuota sindical 5(3175)", "Cuota sindical 6(3176)",
            "Cuota sindical 7(3177)", "Cuota sindical 8(3178)", "Cuota sindical 9(3179)",
            "Cuota sindical 10(3180)", "Crédito social CCAF(3110)",
            "Cuota vivienda o educación(3181)", "Crédito cooperativas de ahorro(3182)",
            "Otros descuentos autorizados y solicitados por el trabajador(3183)",
            "Cotización adicional trabajo pesado - trabajador(3154)",
            "Donaciones culturales y de reconstrucción(3184)", "Otros descuentos(3185)",
            "Pensiones de alimentos(3186)", "Descuento mujer casada(3187)",
            "Descuentos por anticipos y préstamos(3188)",
            "AFC - Aporte empleador(4151)", "Aporte empleador seguro accidentes del trabajo y Ley SANNA(4152)",
            "Aporte empleador indemnización a todo evento(4131)",
            "Aporte adicional trabajo pesado - empleador(4154)",
            "Aporte empleador seguro invalidez y sobrevivencia(4155)", "APVC - Aporte Empleador(4157)",
            "Total haberes(5201)", "Total haberes imponibles y tributables(5210)",
            "Total haberes imponibles no tributables(5220)",
            "Total haberes no imponibles y no tributables(5230)",
            "Total haberes no imponibles y tributables(5240)",
            "Total descuentos(5301)", "Total descuentos impuestos a las remuneraciones(5361)",
            "Total descuentos impuestos por indemnizaciones(5362)",
            "Total descuentos por cotizaciones del trabajador(5341)", "Total otros descuentos(5302)",
            "Total aportes empleador(5410)", "Total líquido(5501)", "Total indemnizaciones(5502)",
            "Total indemnizaciones tributables(5564)", "Total indemnizaciones no tributables(5565)",
        ]

    def procesar_trabajador(self, trabajador, sociedad, mes, anio, primer_dia, ultimo_dia):
        try:
            contrato_activo = ContratoTrabajador.objects.filter(
                trabajador=trabajador, fecha_inicio_contrato__lte=ultimo_dia, fecha_termino_contrato__isnull=True
            ).order_by('-fecha_inicio_contrato').first()
            if not contrato_activo:
                contrato_activo = ContratoTrabajador.objects.filter(
                    trabajador=trabajador,
                    fecha_termino_contrato__gte=primer_dia,
                    fecha_termino_contrato__lte=ultimo_dia
                ).order_by('-fecha_inicio_contrato').first()
        except Exception as e:
            logger.error(f'LibroRemuneraciones procesar_trabajador: error obteniendo contrato para trabajador {trabajador.id}: {e}')
            contrato_activo = None

        try:
            dias_trabajados_obj = DiasTrabajadosAprobados.objects.filter(
                trabajador=trabajador, mes=mes, year=anio
            ).first()
        except Exception as e:
            logger.error(f'LibroRemuneraciones procesar_trabajador: error obteniendo días trabajados para trabajador {trabajador.id}: {e}')
            dias_trabajados_obj = None

        try:
            licencias_mes = LicenciaMedica.objects.filter(
                trabajador=trabajador, fecha_inicio__lte=ultimo_dia, fecha_fin__gte=primer_dia
            )
        except Exception as e:
            logger.error(f'LibroRemuneraciones procesar_trabajador: error obteniendo licencias para trabajador {trabajador.id}: {e}')
            licencias_mes = []

        try:
            vacaciones_mes = Vacaciones.objects.filter(
                trabajador=trabajador, fecha_inicio__lte=ultimo_dia, fecha_fin__gte=primer_dia
            )
        except Exception as e:
            logger.error(f'LibroRemuneraciones procesar_trabajador: error obteniendo vacaciones para trabajador {trabajador.id}: {e}')
            vacaciones_mes = []

        dias_licencia = sum(
            (min(l.fecha_fin, ultimo_dia) - max(l.fecha_inicio, primer_dia)).days + 1
            for l in licencias_mes
        )
        dias_vacaciones = sum(
            (min(v.fecha_fin, ultimo_dia) - max(v.fecha_inicio, primer_dia)).days + 1
            for v in vacaciones_mes
        )

        dias_trabajados = 0
        if dias_trabajados_obj:
            dias_trabajados = dias_trabajados_obj.dias_totales
        elif contrato_activo and contrato_activo.fecha_inicio_contrato:
            if (contrato_activo.fecha_inicio_contrato.year == anio and
                    contrato_activo.fecha_inicio_contrato.month == mes):
                dias_trabajados = ultimo_dia.day - contrato_activo.fecha_inicio_contrato.day + 1
            else:
                dias_trabajados = ultimo_dia.day

        sueldo_base = trabajador.sueldo_base or Decimal('0')
        sueldo_diario = sueldo_base / Decimal('30') if sueldo_base > 0 else Decimal('0')
        sueldo_proporcional = int(sueldo_diario * Decimal(str(dias_trabajados)))

        try:
            horas_extras_mes = HoraExtraordinaria.objects.filter(
                trabajador=trabajador, fecha__year=anio, fecha__month=mes
            ).aggregate(total=Sum('cantidad_horas'))['total'] or 0
        except Exception as e:
            logger.error(f'LibroRemuneraciones procesar_trabajador: error obteniendo horas extras para trabajador {trabajador.id}: {e}')
            horas_extras_mes = 0

        base_imponible = Decimal(str(sueldo_proporcional))
        try:
            for haber in TrabajadorHaber.objects.filter(trabajador=trabajador, haber__imponible=True).select_related('haber'):
                base_imponible += haber.valor
        except Exception as e:
            logger.error(f'LibroRemuneraciones procesar_trabajador: error obteniendo haberes imponibles para trabajador {trabajador.id}: {e}')

        UF_ACTUAL = Decimal('34500')
        tope_imponible = Decimal('81.6') * UF_ACTUAL
        if base_imponible > tope_imponible:
            base_imponible = tope_imponible

        porcentaje_cotizacion = Decimal('10.0')
        cotizacion_afp = int(base_imponible * porcentaje_cotizacion / Decimal('100'))
        cotizacion_salud = int(base_imponible * Decimal('0.07'))

        row_data = [''] * 157

        row_data[0] = trabajador.rut or ''
        row_data[1] = contrato_activo.fecha_inicio_contrato.strftime('%d/%m/%Y') if contrato_activo and contrato_activo.fecha_inicio_contrato else '01/01/2025'
        row_data[2] = contrato_activo.fecha_termino_contrato.strftime('%d/%m/%Y') if contrato_activo and contrato_activo.fecha_termino_contrato else '31/03/2025'
        row_data[3] = '6'
        row_data[4] = '7'
        row_data[5] = '7404'
        row_data[6] = '1'
        row_data[7] = '0'
        row_data[8] = '101'
        row_data[9] = '0'
        row_data[10] = '1' if getattr(trabajador, 'pensionado_vejez', False) else '0'
        row_data[11] = str(trabajador.afp.codigo) if trabajador.afp else '100'
        row_data[12] = getattr(trabajador.ips_regimen, 'codigo', '0') if getattr(trabajador, 'ips_regimen', None) else '0'
        row_data[13] = str(trabajador.salud.codigo) if trabajador.salud else '102'
        row_data[14] = '1' if getattr(trabajador, 'afiliado_afc', False) else '0'
        row_data[15] = sociedad.ccaf.codigo if getattr(sociedad, 'ccaf', None) else '0'
        row_data[16] = sociedad.mutualidad.codigo if getattr(sociedad, 'mutualidad', None) else '0'
        row_data[17] = str(getattr(trabajador, 'cargas_familiares_legales', 0))
        row_data[18] = '1' if getattr(trabajador, 'cargas_familiares_maternales', False) else '0'
        row_data[19] = str(getattr(trabajador, 'cargas_familiares_invalidez', 0))
        for i in range(20, 40):
            row_data[i] = ''
        row_data[31] = str(dias_trabajados)
        row_data[32] = str(dias_licencia)
        row_data[33] = str(dias_vacaciones)
        row_data[34] = '1' if getattr(trabajador, 'subsidio_trabajador_joven', False) else '0'

        row_data[40] = str(sueldo_proporcional)
        if horas_extras_mes > 0 and sueldo_base > 0:
            sobresueldo = int(sueldo_base * Decimal('0.0079545') * Decimal(str(horas_extras_mes)))
            row_data[41] = str(sobresueldo)
        else:
            row_data[41] = '0'

        for i in range(42, 65):
            row_data[i] = '0'

        if sueldo_base > 0:
            row_data[45] = str(int(sueldo_base * Decimal('0.02083')))

        for i in range(65, 89):
            row_data[i] = '0'

        if getattr(trabajador, 'colacion', None) is not None:
            row_data[69] = str(int(trabajador.colacion))
        if getattr(trabajador, 'movilizacion', None) is not None:
            row_data[70] = str(int(trabajador.movilizacion))

        row_data[89] = str(cotizacion_afp)
        row_data[90] = str(cotizacion_salud)
        for i in range(91, 136):
            row_data[i] = '0'

        aporte_afc = 0
        tasa_accidentes = Decimal('0.0095') + Decimal('0.0003')
        aporte_accidentes = int(base_imponible * tasa_accidentes)
        aporte_sis = int(base_imponible * Decimal('0.0153')) if not getattr(trabajador, 'subsidio_trabajador_joven', False) else 0

        row_data[136] = str(aporte_afc)
        row_data[137] = str(aporte_accidentes)
        row_data[138] = '0'
        row_data[139] = '0'
        row_data[140] = str(aporte_sis)
        row_data[141] = '0'

        total_hit = sum(int(row_data[i]) for i in range(40, 65) if row_data[i] and row_data[i] != '0')
        total_hint = sum(int(row_data[i]) for i in range(65, 69) if row_data[i] and row_data[i] != '0')
        total_hnint = sum(int(row_data[i]) for i in range(69, 87) if row_data[i] and row_data[i] != '0')
        total_hnit = sum(int(row_data[i]) for i in range(87, 89) if row_data[i] and row_data[i] != '0')
        total_haberes = total_hit + total_hint + total_hnint + total_hnit

        total_cotizaciones = sum(int(row_data[i]) for i in [89, 90] if row_data[i] and row_data[i] != '0')
        total_descuentos = total_cotizaciones

        total_aportes = aporte_afc + aporte_accidentes + aporte_sis

        row_data[142] = str(total_haberes)
        row_data[143] = str(total_hit)
        row_data[144] = str(total_hint)
        row_data[145] = str(total_hnint)
        row_data[146] = str(total_hnit)
        row_data[147] = str(total_descuentos)
        row_data[148] = '0'
        row_data[149] = '0'
        row_data[150] = str(total_cotizaciones)
        row_data[151] = '0'
        row_data[152] = str(total_aportes)
        row_data[153] = str(total_haberes - total_descuentos)
        row_data[154] = '0'
        row_data[155] = '0'
        row_data[156] = '0'

        return row_data


# ==============================================================================
# GENERAR ARCHIVO PREVIRED
# ==============================================================================

class GenerarArchivoPreviewAPIView(BaseAPIView):

    def post(self, request, format=None):
        serializer = ArchivoPreviewSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        trabajador_ids = data['trabajador_ids']
        mes = int(data['mes'])
        ano = int(data['ano'])

        try:
            trabajadores = PersonalTrabajadores.objects.filter(
                id__in=trabajador_ids
            ).select_related('afp', 'salud', 'sociedad', 'ips_regimen')

            if not trabajadores:
                return Response({'error': 'No se encontraron trabajadores con los IDs proporcionados'}, status=status.HTTP_404_NOT_FOUND)

            contenido = self._generar_contenido_previred(trabajadores, mes, ano)
            response = HttpResponse(contenido, content_type='text/plain')
            response['Content-Disposition'] = f'attachment; filename="Previred_{mes}_{ano}.txt"'
            logger.debug(f'GenerarArchivoPreviewAPIView POST: archivo generado para {len(trabajadores)} trabajadores')
            return response

        except Exception as e:
            logger.error(f'GenerarArchivoPreviewAPIView POST: error: {e}', exc_info=True)
            return Response({'error': f'Error al generar el archivo: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _generar_contenido_previred(self, trabajadores, mes, ano):
        lineas = []
        primer_dia = date(ano, mes, 1)
        ultimo_dia = date(ano + 1, 1, 1) - timedelta(days=1) if mes == 12 else date(ano, mes + 1, 1) - timedelta(days=1)
        periodo_desde = primer_dia.strftime('%m%Y')
        periodo_hasta = ultimo_dia.strftime('%m%Y')

        for trabajador in trabajadores:
            campos = [''] * 105

            if trabajador.rut and '-' in trabajador.rut:
                rut_parts = trabajador.rut.split('-')
                rut_num = rut_parts[0].replace('.', '')
                dv = rut_parts[1]
            else:
                rut_num = trabajador.rut.replace('.', '') if trabajador.rut else ''
                dv = ''

            campos[0] = rut_num.zfill(11)
            campos[1] = dv

            apellidos = trabajador.apellidos or ''
            nombres = trabajador.nombres or ''
            apellido_paterno = apellidos.split(' ')[0] if apellidos else ''
            apellido_materno = ' '.join(apellidos.split(' ')[1:]) if ' ' in apellidos else ''

            campos[2] = apellido_paterno.ljust(30)
            campos[3] = apellido_materno.ljust(30)
            campos[4] = nombres.ljust(30)
            campos[5] = 'M' if trabajador.sexo and trabajador.sexo.upper() in ['MASCULINO', 'M'] else 'F'
            campos[6] = '0' if trabajador.nacionalidad and trabajador.nacionalidad.upper() in ['CHILENA', 'CHILENO'] else '1'
            campos[7] = '01'
            campos[8] = periodo_desde
            campos[9] = periodo_hasta
            campos[10] = 'AFP' if trabajador.afp else ('INP' if getattr(trabajador, 'ips_regimen', None) else 'SIP')
            campos[11] = '1' if getattr(trabajador, 'pensionado_vejez', False) else '0'
            campos[12] = '30'.zfill(2)
            campos[13] = '00'
            campos[14] = '00'

            fecha_desde = trabajador.fecha_ingreso.strftime('%d-%m-%Y') if trabajador.fecha_ingreso else ''
            fecha_hasta = trabajador.fecha_finiquito.strftime('%d-%m-%Y') if getattr(trabajador, 'fecha_finiquito', None) else ''
            campos[15] = fecha_desde.ljust(10)
            campos[16] = fecha_hasta.ljust(10)
            campos[17] = 'D'
            campos[18] = str(trabajador.cargas_familiares_legales).zfill(2)
            campos[19] = '1' if trabajador.cargas_familiares_maternales else '0'
            campos[20] = str(trabajador.cargas_familiares_invalidez).zfill(1)
            campos[21] = '000000'
            campos[22] = '000000'
            campos[23] = '000000'
            campos[24] = 'S' if getattr(trabajador, 'subsidio_trabajador_joven', False) else 'N'

            codigo_afp = str(trabajador.afp.codigo).zfill(2) if trabajador.afp and trabajador.afp.codigo is not None else '00'
            campos[25] = codigo_afp

            renta_imponible = int(trabajador.sueldo_base) if trabajador.sueldo_base else 0
            campos[26] = str(renta_imponible).zfill(8)

            cotizacion_afp = int(renta_imponible * float(trabajador.afp.porcentaje_descuento) / 100) if (trabajador.afp and renta_imponible > 0) else 0
            campos[27] = str(cotizacion_afp).zfill(8)
            campos[28] = str(int(renta_imponible * 0.0153)).zfill(8) if renta_imponible > 0 else '00000000'

            for i, val in enumerate(['00000000', '00000000', '00000', '000000000', '00', '          ', '          ',
                                     '                                        ', '00000', '000000',
                                     '000', '                    ', '0', '00000000', '00000000',
                                     '000', '                    ', '0', '00000000', '00000000',
                                     '00000000000', ' ', '                              ',
                                     '                              ', '                              ',
                                     '00', '          ', '          ', '00', '00000000', '00000000', '00'],
                                    start=29):
                if i < 61:
                    campos[i] = val

            codigo_ips = getattr(getattr(trabajador, 'ips_regimen', None), 'codigo', '0000') or '0000'
            campos[61] = codigo_ips
            campos[62] = '00000'
            campos[63] = str(renta_imponible).zfill(8)
            for i in range(64, 74):
                campos[i] = '00000000'

            codigo_salud = str(trabajador.salud.codigo).zfill(2) if (trabajador.salud and trabajador.salud.codigo is not None) else '00'
            campos[74] = codigo_salud
            campos[75] = '                '
            campos[76] = str(renta_imponible).zfill(8)
            campos[77] = '1'
            campos[78] = '00000000'
            campos[79] = str(int(renta_imponible * 0.07)).zfill(8) if renta_imponible > 0 else '00000000'
            campos[80] = '00000000'
            campos[81] = '00000000'

            sociedad_trabajador = getattr(trabajador, 'sociedad', None)
            codigo_ccaf = getattr(getattr(sociedad_trabajador, 'ccaf', None), 'codigo', '00') or '00'
            campos[82] = codigo_ccaf.zfill(2)
            campos[83] = str(renta_imponible).zfill(8)
            for i in range(84, 95):
                campos[i] = '00000000' if i < 94 else '                    '

            codigo_mutual = getattr(getattr(sociedad_trabajador, 'mutualidad', None), 'codigo', '00') or '00'
            campos[95] = codigo_mutual.zfill(2)
            campos[96] = str(renta_imponible).zfill(8)
            campos[97] = str(int(renta_imponible * 0.0095)).zfill(8) if renta_imponible > 0 else '00000000'
            campos[98] = '000'
            campos[99] = str(renta_imponible).zfill(8)

            afiliado_afc = getattr(trabajador, 'afiliado_afc', False)
            campos[100] = str(int(renta_imponible * 0.006)).zfill(8) if (afiliado_afc and renta_imponible > 0) else '00000000'
            campos[101] = str(int(renta_imponible * 0.024)).zfill(8) if (afiliado_afc and renta_imponible > 0) else '00000000'
            campos[102] = '00000000000'
            campos[103] = ' '
            campos[104] = '                    '

            lineas.append(''.join(campos))

        return '\n'.join(lineas)


# ==============================================================================
# GESTIÓN ASISTENCIA
# ==============================================================================

class GestionAsistenciaAPIView(BaseAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            supervisor_id = request.query_params.get('supervisor_id')
            holding_id = request.query_params.get('holding')
            fecha_str = request.query_params.get('fecha')

            if not holding_id:
                return Response({'error': 'holding es obligatorio', 'acceso_asistencia': False}, status=status.HTTP_400_BAD_REQUEST)
            if not supervisor_id and not request.query_params.get('jefe_cuadrilla_id'):
                return Response({'error': 'Debe proporcionar supervisor_id o jefe_cuadrilla_id', 'acceso_asistencia': False}, status=status.HTTP_400_BAD_REQUEST)

            if fecha_str:
                try:
                    fecha_consulta = datetime.strptime(fecha_str, '%Y-%m-%d').date()
                except ValueError:
                    return Response({'error': 'Formato de fecha inválido. Use YYYY-MM-DD', 'acceso_asistencia': False}, status=status.HTTP_400_BAD_REQUEST)
            else:
                fecha_consulta = timezone.now().astimezone(zoneinfo.ZoneInfo('America/Santiago')).date()

            try:
                supervisor = Supervisores.objects.select_related('usuario', 'holding').get(id=supervisor_id, holding_id=holding_id)
            except Supervisores.DoesNotExist:
                logger.error(f'GestionAsistenciaAPIView GET: supervisor {supervisor_id} no encontrado en holding {holding_id}')
                return Response({'error': 'Supervisor no encontrado', 'acceso_asistencia': False}, status=status.HTTP_404_NOT_FOUND)

            trabajadores_con_contrato = supervisor.trabajadores.filter(
                holding_id=holding_id, estado=True,
                contratos__fecha_inicio_contrato__lte=fecha_consulta,
                contratos__fecha_termino_contrato__gte=fecha_consulta
            ).distinct().order_by('nombres', 'apellidos')

            workers_data = []
            for trabajador in trabajadores_con_contrato:
                try:
                    contrato = trabajador.contratos.filter(
                        fecha_inicio_contrato__lte=fecha_consulta,
                        fecha_termino_contrato__gte=fecha_consulta
                    ).select_related('horario').first()

                    horas_maximas = float(contrato.horario.get_horas_dia(fecha_consulta)) if (contrato and contrato.horario) else 9.0

                    horas_totales = float(
                        RegistroAsistencia.objects.filter(
                            trabajador=trabajador, fecha_asistencia=fecha_consulta
                        ).aggregate(total=Sum('horas_registradas'))['total'] or Decimal('0')
                    )

                    if horas_totales >= horas_maximas:
                        continue

                    workers_data.append({
                        'id': trabajador.id,
                        'nombre': f'{trabajador.nombres} {trabajador.apellidos or ""}'.strip(),
                        'rut': trabajador.rut or trabajador.dni or '',
                        'horas_registradas_hoy': horas_totales,
                        'horas_maximas': horas_maximas - horas_totales
                    })
                except Exception as e:
                    logger.error(f'GestionAsistenciaAPIView GET: error procesando trabajador {trabajador.id}: {e}', exc_info=True)
                    continue

            logger.debug(f'GestionAsistenciaAPIView GET: {len(workers_data)} trabajadores disponibles para fecha {fecha_consulta}')
            return Response({
                'acceso_asistencia': True,
                'workers': workers_data,
                'fecha_consulta': fecha_consulta.isoformat(),
                'total_trabajadores': len(workers_data),
                'supervisor_id': supervisor.id,
                'supervisor_nombre': supervisor.usuario.persona.nombres if supervisor.usuario and supervisor.usuario.persona else 'N/A'
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f'GestionAsistenciaAPIView GET: error: {e}', exc_info=True)
            return Response({'error': f'Error interno del servidor: {str(e)}', 'acceso_asistencia': False}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            supervisor_id = request.data.get('codigo_supervisor')
            asistencias = request.data.get('asistencias', [])
            fecha_str = request.data.get('fecha')

            if not supervisor_id and not request.data.get('jefe_cuadrilla_id'):
                return Response({'status': 'error', 'message': 'Debe proporcionar codigo_supervisor o jefe_cuadrilla_id'}, status=status.HTTP_400_BAD_REQUEST)
            if not asistencias:
                return Response({'status': 'error', 'message': 'Se requiere al menos una asistencia'}, status=status.HTTP_400_BAD_REQUEST)

            if fecha_str:
                try:
                    fecha_asistencia = datetime.strptime(fecha_str, '%Y-%m-%d').date()
                except ValueError:
                    return Response({'status': 'error', 'message': 'Formato de fecha inválido'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                fecha_asistencia = timezone.now().astimezone(zoneinfo.ZoneInfo('America/Santiago')).date()

            try:
                supervisor = Supervisores.objects.get(id=supervisor_id)
            except Supervisores.DoesNotExist:
                logger.error(f'GestionAsistenciaAPIView POST: supervisor {supervisor_id} no encontrado')
                return Response({'status': 'error', 'message': 'Supervisor no encontrado'}, status=status.HTTP_404_NOT_FOUND)

            trabajadores_validos = supervisor.trabajadores.all()
            registros_creados, registros_actualizados, errores = [], [], []

            with transaction.atomic():
                for asist_data in asistencias:
                    try:
                        trabajador_id = asist_data.get('trabajador_id')
                        horas = asist_data.get('horas_registradas', 0.0)
                        estado = asist_data.get('estado', 'A')

                        trabajador = PersonalTrabajadores.objects.get(id=trabajador_id)

                        if not trabajadores_validos.filter(id=trabajador_id).exists():
                            errores.append({'trabajador_id': trabajador_id, 'error': 'Trabajador no asignado'})
                            continue

                        asistencia_existente = RegistroAsistencia.objects.filter(
                            trabajador=trabajador, fecha_asistencia=fecha_asistencia, estado=estado
                        ).first()

                        if asistencia_existente:
                            asistencia_existente.horas_registradas += Decimal(str(horas))
                            asistencia_existente.modificado_por = request.user
                            asistencia_existente.save()
                            registros_actualizados.append(trabajador_id)
                        else:
                            RegistroAsistencia.objects.create(
                                trabajador=trabajador, fecha_asistencia=fecha_asistencia,
                                holding=trabajador.holding, supervisor=supervisor,
                                estado=estado, horas_registradas=horas, modificado_por=request.user
                            )
                            registros_creados.append(trabajador_id)

                    except PersonalTrabajadores.DoesNotExist:
                        errores.append({'trabajador_id': trabajador_id, 'error': 'Trabajador no encontrado'})
                    except Exception as e:
                        logger.error(f'GestionAsistenciaAPIView POST: error en trabajador {trabajador_id}: {e}', exc_info=True)
                        errores.append({'trabajador_id': trabajador_id, 'error': str(e)})

            trabajadores_restantes = trabajadores_validos.filter(
                estado=True,
                contratos__fecha_inicio_contrato__lte=fecha_asistencia,
                contratos__fecha_termino_contrato__gte=fecha_asistencia
            ).distinct()

            pendientes = 0
            for trab in trabajadores_restantes:
                contrato = trab.contratos.filter(
                    fecha_inicio_contrato__lte=fecha_asistencia,
                    fecha_termino_contrato__gte=fecha_asistencia
                ).select_related('horario').first()
                horas_dia = float(contrato.horario.get_horas_dia(fecha_asistencia)) if (contrato and contrato.horario) else 9.0
                horas_reg = float(RegistroAsistencia.objects.filter(
                    trabajador=trab, fecha_asistencia=fecha_asistencia
                ).aggregate(total=Sum('horas_registradas'))['total'] or Decimal('0'))
                if horas_reg < horas_dia:
                    pendientes += 1

            logger.debug(f'GestionAsistenciaAPIView POST: creados={len(registros_creados)}, actualizados={len(registros_actualizados)}, pendientes={pendientes}')
            return Response({
                'status': 'success',
                'message': 'Proceso de asistencia completado',
                'registros_creados': len(registros_creados),
                'registros_actualizados': len(registros_actualizados),
                'errores': errores,
                'remaining_workers': pendientes > 0,
                'trabajadores_pendientes': pendientes
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f'GestionAsistenciaAPIView POST: error: {e}', exc_info=True)
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==============================================================================
# INFORME ASISTENCIA
# ==============================================================================

class InformeAsistenciaAPIView(BaseAPIView):
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        try:
            fecha = request.query_params.get('fecha')
            is_admin = request.query_params.get('is_admin', 'false').lower() == 'true'
            supervisor_id = request.query_params.get('supervisor_id')
            estado_filtro = request.query_params.get('estado')

            if not request.user.holding:
                return Response({'error': 'Usuario sin holding asignado'}, status=status.HTTP_400_BAD_REQUEST)

            holding_id = request.user.holding.id

            if not fecha:
                return Response({'error': 'Fecha es requerida'}, status=status.HTTP_400_BAD_REQUEST)

            fecha_date = datetime.strptime(fecha, '%Y-%m-%d').date()

            registros = RegistroAsistencia.objects.filter(
                holding_id=holding_id, fecha_asistencia=fecha_date
            ).select_related('trabajador__sociedad', 'supervisor__usuario__persona')

            if not is_admin and supervisor_id:
                registros = registros.filter(supervisor_id=supervisor_id)
            if estado_filtro:
                registros = registros.filter(estado=estado_filtro)

            logger.debug(f'InformeAsistenciaAPIView GET: {registros.count()} registros para fecha {fecha_date}')

            trabajadores_agrupados = {}
            for reg in registros:
                trab_id = reg.trabajador.id
                if trab_id not in trabajadores_agrupados:
                    soc_nombre = reg.trabajador.sociedad.nombre if reg.trabajador.sociedad else 'Sin Sociedad'
                    contrato = reg.trabajador.contratos.filter(
                        fecha_inicio_contrato__lte=fecha_date,
                        fecha_termino_contrato__gte=fecha_date
                    ).select_related('fundo').first()
                    fundo_nombre = contrato.fundo.nombre_campo if (contrato and contrato.fundo) else 'Sin Fundo'
                    sup_nombre = (
                        f'{reg.supervisor.usuario.persona.nombres} {reg.supervisor.usuario.persona.apellidos}'
                        if reg.supervisor and reg.supervisor.usuario and reg.supervisor.usuario.persona
                        else 'Sin Supervisor'
                    )
                    trabajadores_agrupados[trab_id] = {
                        'nombretrabajador': f'{reg.trabajador.nombres} {reg.trabajador.apellidos or ""}'.strip(),
                        'sociedad': soc_nombre,
                        'fundo': fundo_nombre,
                        'supervisor': sup_nombre,
                        'estados': [],
                        'detalle_estados': {},
                        'horas_registradas': 0.0
                    }

                trabajadores_agrupados[trab_id]['estados'].append(reg.estado)
                trabajadores_agrupados[trab_id]['horas_registradas'] += float(reg.horas_registradas)
                det = trabajadores_agrupados[trab_id]['detalle_estados']
                det[reg.estado] = det.get(reg.estado, 0.0) + float(reg.horas_registradas)

            sociedades, fundos, supervisores, reporte_detallado = {}, {}, {}, []
            for td in trabajadores_agrupados.values():
                sociedades[td['sociedad']] = sociedades.get(td['sociedad'], 0) + 1
                fundos[td['fundo']] = fundos.get(td['fundo'], 0) + 1
                supervisores[td['supervisor']] = supervisores.get(td['supervisor'], 0) + 1
                reporte_detallado.append({
                    'nombretrabajador': td['nombretrabajador'],
                    'sociedad': td['sociedad'],
                    'fundo': td['fundo'],
                    'supervisor': td['supervisor'],
                    'estado': ', '.join(sorted(set(td['estados']))),
                    'horas_registradas': td['horas_registradas'],
                    'detalle_estados': td['detalle_estados'],
                })

            return Response({'sociedades': sociedades, 'fundos': fundos, 'supervisores': supervisores, 'reporte_detallado': reporte_detallado})

        except Exception as e:
            logger.error(f'InformeAsistenciaAPIView GET: error: {e}', exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ==============================================================================
# GESTIÓN MANO DE OBRA PERSONA
# ==============================================================================

class GestionManoObraPersonaAPIView(BaseAPIView):

    def get(self, request):
        try:
            supervisor_id = request.query_params.get('supervisor_id')
            holding = request.query_params.get('holding')

            if not holding:
                return Response({'error': 'Falta el parámetro holding'}, status=status.HTTP_400_BAD_REQUEST)
            if not supervisor_id and not request.query_params.get('jefe_cuadrilla_id'):
                return Response({'error': 'Debe proporcionar supervisor_id o jefe_cuadrilla_id'}, status=status.HTTP_400_BAD_REQUEST)

            hoy = date.today()

            try:
                supervisor_obj = Supervisores.objects.get(id=supervisor_id)
            except Supervisores.DoesNotExist:
                logger.error(f'GestionManoObraPersonaAPIView GET: supervisor {supervisor_id} no encontrado')
                return Response({'error': 'Supervisor no encontrado'}, status=status.HTTP_404_NOT_FOUND)

            trabajadores_con_contrato = supervisor_obj.trabajadores.filter(
                holding_id=holding, estado=True,
                contratos__fecha_inicio_contrato__lte=hoy,
                contratos__fecha_termino_contrato__gte=hoy
            ).distinct()

            pendientes_asistencia = 0
            for trab in trabajadores_con_contrato:
                contrato = trab.contratos.filter(
                    fecha_inicio_contrato__lte=hoy,
                    fecha_termino_contrato__gte=hoy
                ).select_related('horario').first()
                horas_dia = float(contrato.horario.get_horas_dia(hoy)) if (contrato and contrato.horario) else 9.0
                horas_reg = float(
                    RegistroAsistencia.objects.filter(trabajador=trab, fecha_asistencia=hoy)
                    .aggregate(total=Sum('horas_registradas'))['total'] or Decimal('0')
                )
                if horas_reg < horas_dia:
                    pendientes_asistencia += 1

            if pendientes_asistencia > 0:
                return Response(
                    {'mensaje': f'Debe completar la asistencia del día antes de ingresar mano de obra. Quedan {pendientes_asistencia} trabajadores sin asistencia completa.'},
                    status=status.HTTP_200_OK
                )

            asistencias = RegistroAsistencia.objects.filter(
                fecha_asistencia=hoy, supervisor_id=supervisor_id, holding=holding, estado='A'
            ).select_related('trabajador')

            if not asistencias.exists():
                return Response({'error': 'No hay trabajadores con asistencia registrada hoy'}, status=status.HTTP_404_NOT_FOUND)

            primer_trabajador = asistencias.first().trabajador

            try:
                contrato = ContratoTrabajador.objects.select_related(
                    'folio_comercial__cliente', 'fundo'
                ).get(
                    trabajador=primer_trabajador, holding=holding,
                    fecha_inicio_contrato__lte=hoy, fecha_termino_contrato__gte=hoy
                )
            except ContratoTrabajador.DoesNotExist:
                logger.error(f'GestionManoObraPersonaAPIView GET: trabajador {primer_trabajador.id} sin contrato activo')
                return Response({'error': 'El trabajador no tiene un contrato activo'}, status=status.HTTP_404_NOT_FOUND)

            folio = contrato.folio_comercial

            if not folio:
                return Response({'error': 'El contrato no tiene folio asociado'}, status=status.HTTP_404_NOT_FOUND)

            labores = FolioComercialLabor.objects.filter(folio=folio).select_related('labor')
            if not labores.exists():
                return Response({'error': 'El folio no tiene labores asociadas'}, status=status.HTTP_404_NOT_FOUND)

            trabajadores = []
            for asistencia in asistencias:
                trab = asistencia.trabajador
                try:
                    contrato_t = ContratoTrabajador.objects.select_related('fundo').get(
                        trabajador=trab, holding=holding,
                        fecha_inicio_contrato__lte=hoy, fecha_termino_contrato__gte=hoy
                    )
                except ContratoTrabajador.DoesNotExist:
                    continue

                horas_mo = float(
                    RegistroManoObraPersona.objects.filter(trabajador=trab, fecha_ingreso=hoy)
                    .aggregate(total=Sum('horas'))['total'] or Decimal('0')
                )
                horas_disponibles = float(asistencia.horas_registradas) - horas_mo

                if horas_disponibles > 0:
                    trabajadores.append({
                        'id': trab.id,
                        'nombre': f'{trab.nombres} {trab.apellidos or ""}'.strip(),
                        'horas_disponibles': horas_disponibles,
                        'horas_asistencia': float(asistencia.horas_registradas),
                        'horas_registradas': horas_mo,
                        'sociedad_id': trab.sociedad.id if trab.sociedad else None,
                        'fundo_id': contrato_t.fundo.id if contrato_t.fundo else None,
                    })

            if not trabajadores:
                return Response({'mensaje': 'No hay trabajadores con horas disponibles o sin contrato activo'}, status=status.HTTP_200_OK)

            unidades = UnidadControl.objects.filter(holding=holding, estado=True)
            logger.debug(f'GestionManoObraPersonaAPIView GET: {len(trabajadores)} trabajadores disponibles')

            return Response({
                'trabajadores': trabajadores,
                'folio': {
                    'id': folio.id,
                    'cliente': folio.cliente.nombre if folio.cliente else 'Sin cliente',
                    'fecha_inicio': folio.fecha_inicio_contrato,
                    'fecha_termino': folio.fecha_termino_contrato
                },
                'labores': [{'id': fl.labor.id, 'nombre': fl.labor.nombre} for fl in labores],
                'unidades_control': [{'id': u.id, 'descripcion': u.nombre} for u in unidades],
                'supervisor_id': int(supervisor_id),
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f'GestionManoObraPersonaAPIView GET: error: {e}', exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            data = request.data
            trabajador_id = data.get('trabajador')
            horas_a_registrar = Decimal(str(data.get('horas', 0)))
            hoy = date.today()

            asistencia = RegistroAsistencia.objects.filter(
                trabajador_id=trabajador_id, fecha_asistencia=hoy, estado='A'
            ).first()

            if not asistencia:
                return Response(
                    {'error': 'El trabajador no tiene asistencia con estado Asistente (A) registrada hoy'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            horas_registradas = RegistroManoObraPersona.objects.filter(
                trabajador_id=trabajador_id, fecha_ingreso=hoy
            ).aggregate(total=Sum('horas'))['total'] or Decimal('0')

            horas_disponibles = asistencia.horas_registradas - horas_registradas

            if horas_a_registrar > horas_disponibles:
                return Response(
                    {'error': f'Las horas a registrar ({horas_a_registrar}) exceden las horas disponibles ({horas_disponibles})'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer = RegistroManoObraPersonaSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                logger.debug(f'GestionManoObraPersonaAPIView POST: registro creado para trabajador {trabajador_id}')
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            logger.error(f'GestionManoObraPersonaAPIView POST: datos inválidos: {serializer.errors}')
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f'GestionManoObraPersonaAPIView POST: error: {e}', exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==============================================================================
# INFORME MANO DE OBRA
# ==============================================================================

class InformeManoObraAPIView(BaseAPIView):

    def get(self, request):
        try:
            supervisor_id = request.query_params.get('supervisor_id')
            holding = request.query_params.get('holding')
            fecha_inicio = request.query_params.get('fecha_inicio')
            fecha_fin = request.query_params.get('fecha_fin')

            if not holding:
                return Response({'error': 'Falta el parámetro holding'}, status=status.HTTP_400_BAD_REQUEST)

            filtros = {'holding': holding}
            if supervisor_id:
                filtros['supervisor_id'] = supervisor_id

            if fecha_inicio and fecha_fin:
                try:
                    filtros['fecha_ingreso__range'] = [
                        datetime.strptime(fecha_inicio, '%Y-%m-%d').date(),
                        datetime.strptime(fecha_fin, '%Y-%m-%d').date(),
                    ]
                except ValueError:
                    return Response({'error': 'Formato de fecha inválido. Use YYYY-MM-DD'}, status=status.HTTP_400_BAD_REQUEST)
            elif fecha_inicio:
                try:
                    filtros['fecha_ingreso'] = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
                except ValueError:
                    return Response({'error': 'Formato de fecha inválido. Use YYYY-MM-DD'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                filtros['fecha_ingreso'] = date.today()

            registros = RegistroManoObraPersona.objects.filter(**filtros).select_related(
                'labor', 'supervisor', 'supervisor__usuario', 'supervisor__usuario__persona',
                'trabajador', 'unidad_control', 'folio', 'folio__cliente'
            ).order_by('-produccion')

            logger.debug(f'InformeManoObraAPIView GET: {registros.count()} registros encontrados')

            if not registros.exists():
                return Response({'registros': [], 'mensaje': 'No hay registros para los filtros aplicados'}, status=status.HTTP_200_OK)

            registros_data = []
            for registro in registros:
                if registro.supervisor and registro.supervisor.usuario and registro.supervisor.usuario.persona:
                    nombre_sup = f'{registro.supervisor.usuario.persona.nombres} {registro.supervisor.usuario.persona.apellidos or ""}'.strip()
                else:
                    nombre_sup = 'Sin Supervisor'

                registros_data.append({
                    'id': registro.id,
                    'nombre_labor': registro.labor.nombre if registro.labor else 'Sin Labor',
                    'nombre_supervisor': nombre_sup,
                    'unidad_control': registro.unidad_control.nombre if registro.unidad_control else 'Sin U.Control',
                    'horas_trabajadas': float(registro.horas),
                    'produccion': float(registro.produccion),
                    'nombre_trabajador': f'{registro.trabajador.nombres} {registro.trabajador.apellidos or ""}'.strip() if registro.trabajador else 'Sin Trabajador',
                    'nombre_centro_costo': registro.folio.cliente.nombre if (registro.folio and registro.folio.cliente) else 'Sin Cliente',
                    'fecha_ingreso': registro.fecha_ingreso.strftime('%Y-%m-%d'),
                    'folio_id': registro.folio.id if registro.folio else None,
                })

            return Response({'registros': registros_data, 'total': len(registros_data)}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f'InformeManoObraAPIView GET: error: {e}', exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==============================================================================
# GESTIÓN RETROACTIVA MANO DE OBRA PERSONA
# ==============================================================================

class GestionRetroactivaManoObraPersonaAPIView(BaseAPIView):

    def get(self, request):
        try:
            supervisor_id = request.query_params.get('supervisor_id')
            holding = request.query_params.get('holding')
            fecha_str = request.query_params.get('fecha')

            if not holding:
                return Response({'error': 'Falta el parámetro holding'}, status=status.HTTP_400_BAD_REQUEST)
            if not supervisor_id:
                return Response({'error': 'Falta el parámetro supervisor_id'}, status=status.HTTP_400_BAD_REQUEST)
            if not fecha_str:
                return Response({'error': 'Falta el parámetro fecha'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            except ValueError:
                return Response({'error': 'Formato de fecha inválido. Use YYYY-MM-DD'}, status=status.HTTP_400_BAD_REQUEST)

            if fecha >= date.today():
                return Response({'error': 'La fecha debe ser anterior al día de hoy'}, status=status.HTTP_400_BAD_REQUEST)

            asistencias = RegistroAsistencia.objects.filter(
                fecha_asistencia=fecha, supervisor_id=supervisor_id, holding=holding, estado='A'
            ).select_related('trabajador')

            if not asistencias.exists():
                logger.error(f'GestionRetroactivaManoObraPersonaAPIView GET: sin asistencias para supervisor {supervisor_id}, fecha {fecha}')
                return Response({'error': f'No hay trabajadores con asistencia registrada el {fecha_str}'}, status=status.HTTP_404_NOT_FOUND)

            primer_trabajador = asistencias.first().trabajador

            contrato = ContratoTrabajador.objects.select_related(
                'folio_comercial__cliente', 'fundo'
            ).filter(
                trabajador=primer_trabajador, holding=holding,
                fecha_inicio_contrato__lte=fecha, fecha_termino_contrato__gte=fecha
            ).order_by('-fecha_inicio_contrato').first()

            if not contrato:
                logger.error(f'GestionRetroactivaManoObraPersonaAPIView GET: sin contrato activo para trabajador {primer_trabajador.id} en fecha {fecha}')
                return Response({'error': 'El trabajador no tiene un contrato activo para esa fecha'}, status=status.HTTP_404_NOT_FOUND)

            folio = contrato.folio_comercial

            if not folio:
                return Response({'error': 'El contrato no tiene folio asociado'}, status=status.HTTP_404_NOT_FOUND)

            labores = FolioComercialLabor.objects.filter(folio=folio).select_related('labor')
            if not labores.exists():
                return Response({'error': 'El folio no tiene labores asociadas'}, status=status.HTTP_404_NOT_FOUND)

            trabajadores = []
            for asistencia in asistencias:
                trab = asistencia.trabajador
                contrato_t = ContratoTrabajador.objects.select_related('fundo').filter(
                    trabajador=trab, holding=holding,
                    fecha_inicio_contrato__lte=fecha, fecha_termino_contrato__gte=fecha,
                    folio_comercial=folio
                ).order_by('-fecha_inicio_contrato').first()

                if not contrato_t:
                    continue

                horas_mo = float(
                    RegistroManoObraPersona.objects.filter(trabajador=trab, fecha_ingreso=fecha)
                    .aggregate(total=Sum('horas'))['total'] or Decimal('0')
                )
                horas_disponibles = float(asistencia.horas_registradas) - horas_mo

                if horas_disponibles > 0:
                    trabajadores.append({
                        'id': trab.id,
                        'nombre': f'{trab.nombres} {trab.apellidos or ""}'.strip(),
                        'horas_disponibles': horas_disponibles,
                        'horas_asistencia': float(asistencia.horas_registradas),
                        'horas_registradas': horas_mo,
                        'sociedad_id': trab.sociedad.id if trab.sociedad else None,
                        'fundo_id': contrato_t.fundo.id if contrato_t.fundo else None,
                    })

            if not trabajadores:
                return Response({'mensaje': 'Todos los trabajadores ya tienen sus horas de mano de obra completas para esa fecha'}, status=status.HTTP_200_OK)

            unidades = UnidadControl.objects.filter(holding=holding, estado=True)
            logger.debug(f'GestionRetroactivaManoObraPersonaAPIView GET: {len(trabajadores)} trabajadores disponibles para fecha {fecha}')

            return Response({
                'trabajadores': trabajadores,
                'folio': {
                    'id': folio.id,
                    'cliente': folio.cliente.nombre if folio.cliente else 'Sin cliente'
                },
                'labores': [{'id': fl.labor.id, 'nombre': fl.labor.nombre} for fl in labores],
                'unidades_control': [{'id': u.id, 'descripcion': u.nombre} for u in unidades],
                'supervisor_id': int(supervisor_id),
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.debug('Error: ', e)
            logger.error(f'GestionRetroactivaManoObraPersonaAPIView GET: error: {e}', exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            data = request.data.copy()
            fecha_str = data.get('fecha')

            if not fecha_str:
                return Response({'error': 'Falta el campo fecha'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            except ValueError:
                return Response({'error': 'Formato de fecha inválido. Use YYYY-MM-DD'}, status=status.HTTP_400_BAD_REQUEST)

            if fecha >= date.today():
                return Response({'error': 'La fecha debe ser anterior al día de hoy'}, status=status.HTTP_400_BAD_REQUEST)

            trabajador_id = data.get('trabajador')
            horas_a_registrar = Decimal(str(data.get('horas', 0)))

            asistencia = RegistroAsistencia.objects.filter(
                trabajador_id=trabajador_id, fecha_asistencia=fecha, estado='A'
            ).first()

            if not asistencia:
                return Response({'error': 'El trabajador no tiene asistencia con estado A para esa fecha'}, status=status.HTTP_400_BAD_REQUEST)

            horas_registradas = RegistroManoObraPersona.objects.filter(
                trabajador_id=trabajador_id, fecha_ingreso=fecha
            ).aggregate(total=Sum('horas'))['total'] or Decimal('0')

            horas_disponibles = asistencia.horas_registradas - horas_registradas

            if horas_a_registrar > horas_disponibles:
                return Response(
                    {'error': f'Las horas a registrar ({horas_a_registrar}) exceden las disponibles ({horas_disponibles})'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            registro = RegistroManoObraPersona.objects.create(
                holding_id=data.get('holding'),
                sociedad_id=data.get('sociedad'),
                supervisor_id=data.get('supervisor'),
                folio_id=data.get('folio'),
                labor_id=data.get('labor'),
                unidad_control_id=data.get('unidad_control'),
                trabajador_id=trabajador_id,
                produccion=data.get('produccion', 0),
                horas=horas_a_registrar,
                fecha_ingreso=fecha,
            )

            logger.debug(f'GestionRetroactivaManoObraPersonaAPIView POST: registro {registro.id} creado para fecha {fecha}')
            return Response({'id': registro.id, 'fecha_ingreso': str(registro.fecha_ingreso)}, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f'GestionRetroactivaManoObraPersonaAPIView POST: error: {e}', exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==============================================================================
# GESTIÓN RETROACTIVA ASISTENCIA
# ==============================================================================

class GestionRetroactivaAsistenciaAPIView(BaseAPIView):
    
    def get(self, request):
        try:
            supervisor_id = request.query_params.get('supervisor_id')
            holding_id = request.query_params.get('holding')
            fecha_str = request.query_params.get('fecha')

            if not holding_id:
                return Response({'error': 'holding es obligatorio', 'acceso_asistencia': False}, status=status.HTTP_400_BAD_REQUEST)
            if not supervisor_id:
                return Response({'error': 'supervisor_id es obligatorio', 'acceso_asistencia': False}, status=status.HTTP_400_BAD_REQUEST)
            if not fecha_str:
                return Response({'error': 'fecha es obligatoria', 'acceso_asistencia': False}, status=status.HTTP_400_BAD_REQUEST)

            try:
                fecha_consulta = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            except ValueError:
                logger.error(f'Fecha con formato inválido: {fecha_str}')
                return Response({'error': 'Formato de fecha inválido. Use YYYY-MM-DD', 'acceso_asistencia': False}, status=status.HTTP_400_BAD_REQUEST)

            hoy = timezone.now().astimezone(zoneinfo.ZoneInfo('America/Santiago')).date()
            if fecha_consulta >= hoy:
                logger.error(f'Fecha no permitida: {fecha_consulta} (debe ser anterior a hoy {hoy})')
                return Response({'error': 'La fecha debe ser anterior al día de hoy', 'acceso_asistencia': False}, status=status.HTTP_400_BAD_REQUEST)

            try:
                supervisor = Supervisores.objects.select_related('usuario', 'holding').get(id=supervisor_id, holding_id=holding_id)
            except Supervisores.DoesNotExist:
                logger.error(f'Supervisor id={supervisor_id} no encontrado en holding id={holding_id}')
                return Response({'error': 'Supervisor no encontrado', 'acceso_asistencia': False}, status=status.HTTP_404_NOT_FOUND)

            ids_en_fecha = SupervisorTrabajadorHistorial.objects.filter(
                supervisor=supervisor, fecha_inicio__lte=fecha_consulta
            ).filter(
                Q(fecha_fin__gte=fecha_consulta) | Q(fecha_fin__isnull=True)
            ).values_list('trabajador_id', flat=True)

            trabajadores_con_contrato = PersonalTrabajadores.objects.filter(
                id__in=ids_en_fecha, holding_id=holding_id, estado=True,
                contratos__fecha_inicio_contrato__lte=fecha_consulta,
                contratos__fecha_termino_contrato__gte=fecha_consulta
            ).distinct().order_by('nombres', 'apellidos')

            workers_data = []
            for trabajador in trabajadores_con_contrato:
                try:
                    contrato = trabajador.contratos.filter(
                        fecha_inicio_contrato__lte=fecha_consulta,
                        fecha_termino_contrato__gte=fecha_consulta
                    ).select_related('horario').first()
                    horas_maximas = float(contrato.horario.get_horas_dia(fecha_consulta)) if (contrato and contrato.horario) else 9.0
                    horas_reg = float(
                        RegistroAsistencia.objects.filter(trabajador=trabajador, fecha_asistencia=fecha_consulta)
                        .aggregate(total=Sum('horas_registradas'))['total'] or Decimal('0')
                    )
                    if horas_reg >= horas_maximas:
                        continue
                    workers_data.append({
                        'id': trabajador.id,
                        'nombre': f'{trabajador.nombres} {trabajador.apellidos or ""}'.strip(),
                        'rut': trabajador.rut or trabajador.dni or '',
                        'horas_registradas_hoy': horas_reg,
                        'horas_maximas': horas_maximas - horas_reg,
                    })
                except Exception as e:
                    logger.error(f'Error procesando trabajador id={trabajador.id}: {e}')
                    continue

            return Response({
                'acceso_asistencia': True,
                'workers': workers_data,
                'fecha_consulta': fecha_consulta.isoformat(),
                'total_trabajadores': len(workers_data),
                'supervisor_id': supervisor.id,
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f'Error inesperado en GestionRetroactivaAsistencia: {e}', exc_info=True)
            return Response({'error': str(e), 'acceso_asistencia': False}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            supervisor_id = request.data.get('codigo_supervisor')
            asistencias = request.data.get('asistencias', [])
            fecha_str = request.data.get('fecha')

            if not supervisor_id:
                return Response({'status': 'error', 'message': 'codigo_supervisor es obligatorio'}, status=status.HTTP_400_BAD_REQUEST)
            if not asistencias:
                return Response({'status': 'error', 'message': 'Se requiere al menos una asistencia'}, status=status.HTTP_400_BAD_REQUEST)
            if not fecha_str:
                return Response({'status': 'error', 'message': 'fecha es obligatoria'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                fecha_asistencia = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            except ValueError:
                return Response({'status': 'error', 'message': 'Formato de fecha inválido. Use YYYY-MM-DD'}, status=status.HTTP_400_BAD_REQUEST)

            hoy = timezone.now().astimezone(zoneinfo.ZoneInfo('America/Santiago')).date()
            if fecha_asistencia >= hoy:
                return Response({'status': 'error', 'message': 'La fecha debe ser anterior al día de hoy'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                supervisor = Supervisores.objects.get(id=supervisor_id)
            except Supervisores.DoesNotExist:
                logger.error(f'GestionRetroactivaAsistenciaAPIView POST: supervisor {supervisor_id} no encontrado')
                return Response({'status': 'error', 'message': 'Supervisor no encontrado'}, status=status.HTTP_404_NOT_FOUND)

            ids_validos = SupervisorTrabajadorHistorial.objects.filter(
                supervisor=supervisor, fecha_inicio__lte=fecha_asistencia
            ).filter(
                Q(fecha_fin__gte=fecha_asistencia) | Q(fecha_fin__isnull=True)
            ).values_list('trabajador_id', flat=True)

            trabajadores_validos = PersonalTrabajadores.objects.filter(id__in=ids_validos)
            registros_creados, registros_actualizados, errores = [], [], []

            with transaction.atomic():
                for asist_data in asistencias:
                    try:
                        trabajador_id = asist_data.get('trabajador_id')
                        horas = asist_data.get('horas_registradas', 0.0)
                        estado = asist_data.get('estado', 'A')

                        trabajador = PersonalTrabajadores.objects.get(id=trabajador_id)

                        if not trabajadores_validos.filter(id=trabajador_id).exists():
                            errores.append({'trabajador_id': trabajador_id, 'error': 'Trabajador no asignado'})
                            continue

                        asistencia_existente = RegistroAsistencia.objects.filter(
                            trabajador=trabajador, fecha_asistencia=fecha_asistencia, estado=estado
                        ).first()

                        if asistencia_existente:
                            asistencia_existente.horas_registradas += Decimal(str(horas))
                            asistencia_existente.modificado_por = request.user
                            asistencia_existente.save()
                            registros_actualizados.append(trabajador_id)
                        else:
                            RegistroAsistencia.objects.create(
                                trabajador=trabajador, fecha_asistencia=fecha_asistencia,
                                holding=trabajador.holding, supervisor=supervisor,
                                estado=estado, horas_registradas=horas, modificado_por=request.user
                            )
                            registros_creados.append(trabajador_id)

                    except PersonalTrabajadores.DoesNotExist:
                        errores.append({'trabajador_id': trabajador_id, 'error': 'Trabajador no encontrado'})
                    except Exception as e:
                        errores.append({'trabajador_id': trabajador_id, 'error': str(e)})

            pendientes = 0
            for trab in trabajadores_validos.filter(
                estado=True,
                contratos__fecha_inicio_contrato__lte=fecha_asistencia,
                contratos__fecha_termino_contrato__gte=fecha_asistencia
            ).distinct():
                contrato = trab.contratos.filter(
                    fecha_inicio_contrato__lte=fecha_asistencia,
                    fecha_termino_contrato__gte=fecha_asistencia
                ).select_related('horario').first()
                horas_dia = float(contrato.horario.get_horas_dia(fecha_asistencia)) if (contrato and contrato.horario) else 9.0
                horas_reg = float(RegistroAsistencia.objects.filter(
                    trabajador=trab, fecha_asistencia=fecha_asistencia
                ).aggregate(total=Sum('horas_registradas'))['total'] or Decimal('0'))
                if horas_reg < horas_dia:
                    pendientes += 1

            logger.debug(f'GestionRetroactivaAsistenciaAPIView POST: creados={len(registros_creados)}, actualizados={len(registros_actualizados)}, pendientes={pendientes}')
            return Response({
                'status': 'success',
                'message': 'Proceso de asistencia retroactiva completado',
                'registros_creados': len(registros_creados),
                'registros_actualizados': len(registros_actualizados),
                'errores': errores,
                'remaining_workers': pendientes > 0,
                'trabajadores_pendientes': pendientes,
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f'GestionRetroactivaAsistenciaAPIView POST: error: {e}', exc_info=True)
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==============================================================================
# TRASPASO TRABAJADORES
# ==============================================================================

class TraspasoTrabajadoresAPIView(BaseAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        holding_id = request.query_params.get('holding')
        supervisores = Supervisores.objects.filter(
            holding_id=holding_id
        ).select_related('usuario__persona').prefetch_related('trabajadores')

        data = []
        for sup in supervisores:
            persona = sup.usuario.persona if sup.usuario and sup.usuario.persona else None
            nombre = f'{persona.nombres} {persona.apellidos}' if persona else (sup.usuario.rut if sup.usuario else '')
            data.append({
                'id': sup.id,
                'nombre': nombre,
                'rut': sup.usuario.rut if sup.usuario else '',
                'trabajadores': [
                    {'id': t.id, 'nombres': t.nombres, 'apellidos': t.apellidos or '', 'rut': t.rut or ''}
                    for t in sup.trabajadores.filter(estado=True)
                ]
            })
        return Response(data)

    def post(self, request):
        holding_id = request.data.get('holding')
        origen_id = request.data.get('supervisor_origen_id')
        destino_id = request.data.get('supervisor_destino_id')
        trabajadores_ids = request.data.get('trabajadores_ids', [])

        if not all([holding_id, origen_id, destino_id, trabajadores_ids]):
            return Response({'error': 'Faltan campos requeridos'}, status=status.HTTP_400_BAD_REQUEST)
        if str(origen_id) == str(destino_id):
            return Response({'error': 'Origen y destino no pueden ser el mismo'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            sup_origen = Supervisores.objects.get(id=origen_id, holding_id=holding_id)
            sup_destino = Supervisores.objects.get(id=destino_id, holding_id=holding_id)
        except Supervisores.DoesNotExist:
            logger.error(f'TraspasoTrabajadoresAPIView POST: supervisor no encontrado')
            return Response({'error': 'Supervisor no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        hoy = timezone.now().date()
        bloqueados, transferibles = [], []

        for tid in trabajadores_ids:
            tiene_registro = (
                RegistroAsistencia.objects.filter(trabajador_id=tid, fecha_asistencia=hoy).exists() or
                RegistroManoObraPersona.objects.filter(trabajador_id=tid, fecha_ingreso=hoy).exists()
            )
            if tiene_registro:
                t = PersonalTrabajadores.objects.get(id=tid)
                bloqueados.append({'id': tid, 'nombre': f'{t.nombres} {t.apellidos or ""}'})
            else:
                transferibles.append(tid)

        for tid in transferibles:
            sup_origen.trabajadores.remove(tid)
            sup_destino.trabajadores.add(tid)
            SupervisorTrabajadorHistorial.objects.filter(
                trabajador_id=tid, supervisor=sup_origen, fecha_fin__isnull=True
            ).update(fecha_fin=hoy)
            SupervisorTrabajadorHistorial.objects.create(
                holding_id=holding_id, supervisor=sup_destino, trabajador_id=tid, fecha_inicio=hoy
            )

        logger.debug(f'TraspasoTrabajadoresAPIView POST: {len(transferibles)} transferidos, {len(bloqueados)} bloqueados')
        return Response({'transferidos': len(transferibles), 'bloqueados': bloqueados})

