
from .base import BaseAPIView
from rest_framework.response import Response
from rest_framework import status
import logging
from django.db import transaction
from django.db.models import Q
from django.utils.dateparse import parse_date
from django.utils import timezone

from ..models import (
    ElementoSeguridad,
)

from ..serializers import (
    ElementoSeguridadSerializer,
)

from ..models import ContratoTrabajador, RegistroCharlaSupervisor, Supervisores
from ..serializers import RegistroCharlaSupervisorSerializer, SupervisorSerializer


logger = logging.getLogger('contratista_test_app')

# ==============================================================================
# ELEMENTO SEGURIDAD
# ==============================================================================

class ElementoSeguridadAPIView(BaseAPIView):

    def get(self, request, format=None):
        holding_id = request.query_params.get('holding')
        if not holding_id:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        elementos_seguridad = ElementoSeguridad.objects.filter(holding_id=holding_id)
        print(ElementoSeguridadSerializer(elementos_seguridad, many=True).data)
        return Response(ElementoSeguridadSerializer(elementos_seguridad, many=True).data)

    def post(self, request, format=None):
        serializer = ElementoSeguridadSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error(f'ElementoSeguridadAPIView POST: datos inválidos: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, format=None):
        logger.info(f'DELETE request.data: {request.data}')
        ids = request.data.get('ids', [])
        logger.info(f'DELETE ids: {ids}')
        ElementoSeguridad.objects.filter(id__in=ids).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, format=None):
        obj_id = request.data.get('id')
        if not obj_id:
            return Response({'message': 'ID es necesario para actualizar'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            elemento_seguridad = ElementoSeguridad.objects.get(id=obj_id)
        except ElementoSeguridad.DoesNotExist:
            logger.error(f'ElementoSeguridadAPIView PATCH: elemento_seguridad {obj_id} no encontrada')
            return Response({'message': 'Elemento de seguridad no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ElementoSeguridadSerializer(elemento_seguridad, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        logger.error(f'ElementoSeguridadAPIView PATCH: datos inválidos: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, format=None):
        obj_id = request.data.get('id')
        try:
            elemento_seguridad = ElementoSeguridad.objects.get(id=obj_id)
        except ElementoSeguridad.DoesNotExist:
            logger.error(f'ElementoSeguridadAPIView PUT: elemento_seguridad {obj_id} no encontrada')
            return Response({'message': 'Elemento de seguridad no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ElementoSeguridadSerializer(elemento_seguridad, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        logger.error(f'ElementoSeguridadAPIView PUT: datos inválidos: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ElementoSeguridadListAPIView(BaseAPIView):
    def get(self, request, *args, **kwargs):
        try:
            holding_id = request.query_params.get('holding')

            if holding_id:
                elementos = ElementoSeguridad.objects.filter(
                    holding_id=holding_id
                ).order_by('elemento')
            else:
                elementos = ElementoSeguridad.objects.filter(
                    holding=request.user.holding
                ).order_by('elemento')

            data = [
                {
                    'id': e.id,
                    'elemento': e.elemento,
                    'cantidad': e.cantidad,
                }
                for e in elementos
            ]

            return Response(data)

        except Exception as e:
            logger.error('ElementoSeguridadListAPIView GET: error inesperado', exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class RegistroCharlaSupervisorAPIView(BaseAPIView):
    """
    GET:
      Lista contratos por rango de fecha y los agrupa así:
      supervisor que dio charla -> trabajadores A-Z -> contratos.

    POST:
      Asigna masivamente 1 o N contratos a 1 supervisor.
      Si accion='quitar', elimina la charla de esos contratos.
    """

    def get(self, request, holding_id=None, format=None):
        holding_id = holding_id or request.query_params.get('holding')
        if not holding_id:
            return Response({'message': 'Se requiere holding_id'}, status=status.HTTP_400_BAD_REQUEST)

        fecha_inicio_raw = request.query_params.get('fecha_inicio')
        fecha_fin_raw = request.query_params.get('fecha_fin')
        trabajador_texto = (request.query_params.get('trabajador') or '').strip()
        supervisor_filtro = request.query_params.get('supervisor')

        fecha_inicio = parse_date(fecha_inicio_raw) if fecha_inicio_raw else timezone.localdate()
        fecha_fin = parse_date(fecha_fin_raw) if fecha_fin_raw else fecha_inicio

        if not fecha_inicio or not fecha_fin:
            return Response({'message': 'Formato de fecha inválido. Usa YYYY-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)

        if fecha_inicio > fecha_fin:
            return Response({'message': 'La fecha de inicio no puede ser mayor que la fecha fin.'}, status=status.HTTP_400_BAD_REQUEST)

        contratos = ContratoTrabajador.objects.select_related(
            'holding',
            'trabajador',
            'trabajador__sociedad',
            'documento',
            'cliente',
            'fundo',
        ).filter(
            holding_id=holding_id,
            fecha_inicio_contrato__gte=fecha_inicio,
            fecha_inicio_contrato__lte=fecha_fin,
        )

        if trabajador_texto:
            contratos = contratos.filter(
                Q(trabajador__nombres__icontains=trabajador_texto) |
                Q(trabajador__apellidos__icontains=trabajador_texto) |
                Q(trabajador__rut__icontains=trabajador_texto) |
                Q(trabajador__dni__icontains=trabajador_texto)
            )

        registros_base = RegistroCharlaSupervisor.objects.filter(holding_id=holding_id)

        if supervisor_filtro:
            if supervisor_filtro == 'sin':
                contratos = contratos.exclude(id__in=registros_base.values_list('contrato_id', flat=True))
            else:
                contratos = contratos.filter(
                    id__in=registros_base.filter(supervisor_id=supervisor_filtro).values_list('contrato_id', flat=True)
                )

        contratos = contratos.order_by(
            'fecha_inicio_contrato',
            'trabajador__nombres',
            'trabajador__apellidos',
            'id',
        )

        contrato_ids = list(contratos.values_list('id', flat=True))
        registros_qs = RegistroCharlaSupervisor.objects.select_related(
            'supervisor',
            'supervisor__usuario',
            'supervisor__usuario__persona',
        ).filter(
            holding_id=holding_id,
            contrato_id__in=contrato_ids,
        ).order_by('id')

        # Si históricamente se duplicó un contrato, usamos el primer registro.
        registros_por_contrato = {}
        for registro in registros_qs:
            registros_por_contrato.setdefault(registro.contrato_id, registro)

        grupos_map = {}
        total_con_charla = 0
        total_sin_charla = 0

        for contrato in contratos:
            registro = registros_por_contrato.get(contrato.id)
            trabajador = contrato.trabajador

            if registro and registro.supervisor_id:
                total_con_charla += 1
                supervisor_id = registro.supervisor_id
                supervisor_nombre = self._nombre_supervisor(registro.supervisor)
            else:
                total_sin_charla += 1
                supervisor_id = None
                supervisor_nombre = 'Sin Charla Asignada'

            grupo_key = supervisor_id if supervisor_id is not None else 'sin-charla'
            if grupo_key not in grupos_map:
                grupos_map[grupo_key] = {
                    'supervisor_id': supervisor_id,
                    'supervisor_nombre': supervisor_nombre,
                    'trabajadores_map': {},
                }

            trabajador_id = trabajador.id if trabajador else 0
            trabajador_nombre = self._nombre_trabajador(trabajador)
            trabajador_rut = trabajador.rut if trabajador else None

            trabajadores_map = grupos_map[grupo_key]['trabajadores_map']
            if trabajador_id not in trabajadores_map:
                trabajadores_map[trabajador_id] = {
                    'trabajador_id': trabajador_id,
                    'trabajador_nombre': trabajador_nombre,
                    'trabajador_rut': trabajador_rut,
                    'contratos': [],
                }

            trabajadores_map[trabajador_id]['contratos'].append({
                'id': contrato.id,
                'fecha_inicio_contrato': contrato.fecha_inicio_contrato,
                'fecha_termino_contrato': contrato.fecha_termino_contrato,
                'nombre_documento': contrato.documento.nombre if contrato.documento_id else None,
                'nombre_cliente': contrato.cliente.nombre if contrato.cliente_id else None,
                'nombre_fundo': contrato.fundo.nombre_campo if contrato.fundo_id else None,
                'estado_contrato': self._estado_contrato(contrato),
                'registro_charla_id': registro.id if registro else None,
                'supervisor_id': supervisor_id,
                'supervisor_nombre': supervisor_nombre if supervisor_id else None,
            })

        grupos = []
        for key, grupo in grupos_map.items():
            trabajadores = list(grupo['trabajadores_map'].values())
            trabajadores.sort(key=lambda t: (t['trabajador_nombre'] or '').lower())

            total_contratos_grupo = sum(len(t['contratos']) for t in trabajadores)
            grupos.append({
                'supervisor_id': grupo['supervisor_id'],
                'supervisor_nombre': grupo['supervisor_nombre'],
                'total_trabajadores': len(trabajadores),
                'total_contratos': total_contratos_grupo,
                'trabajadores': trabajadores,
            })

        grupos.sort(key=lambda g: (0 if g['supervisor_id'] is None else 1, g['supervisor_nombre'].lower()))

        supervisores = Supervisores.objects.select_related(
            'usuario',
            'usuario__persona',
            'holding',
        ).prefetch_related('trabajadores').filter(
            holding_id=holding_id
        ).order_by('usuario__persona__nombres', 'usuario__rut')

        return Response({
            'grupos': grupos,
            'supervisores': SupervisorSerializer(supervisores, many=True, context={'request': request}).data,
            'resumen': {
                'total_contratos': len(contrato_ids),
                'con_charla': total_con_charla,
                'sin_charla': total_sin_charla,
            }
        }, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        holding_id = request.data.get('holding')
        contrato_ids = request.data.get('contrato_ids', [])
        supervisor_id = request.data.get('supervisor')
        accion = request.data.get('accion', 'asignar')

        if not holding_id:
            return Response({'message': 'El holding es obligatorio.'}, status=status.HTTP_400_BAD_REQUEST)

        if not isinstance(contrato_ids, list) or len(contrato_ids) == 0:
            return Response({'message': 'Debes enviar contrato_ids como lista.'}, status=status.HTTP_400_BAD_REQUEST)

        contratos = ContratoTrabajador.objects.select_related('trabajador').filter(
            holding_id=holding_id,
            id__in=contrato_ids,
        )

        if contratos.count() != len(set(contrato_ids)):
            return Response(
                {'message': 'Uno o más contratos no existen o no pertenecen al holding.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if accion == 'quitar':
            eliminados, _ = RegistroCharlaSupervisor.objects.filter(
                holding_id=holding_id,
                contrato_id__in=contrato_ids,
            ).delete()
            return Response({'eliminados': eliminados}, status=status.HTTP_200_OK)

        if not supervisor_id:
            return Response({'message': 'Debes seleccionar un supervisor.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            supervisor = Supervisores.objects.select_related('usuario').get(id=supervisor_id, holding_id=holding_id)
        except Supervisores.DoesNotExist:
            return Response({'message': 'Supervisor no encontrado para este holding.'}, status=status.HTTP_404_NOT_FOUND)

        actualizados = 0
        creados = 0

        with transaction.atomic():
            for contrato in contratos:
                # Limpieza defensiva: si alguna vez hubo duplicados, dejamos solo uno.
                existentes = list(RegistroCharlaSupervisor.objects.filter(contrato=contrato).order_by('id'))

                if existentes:
                    registro = existentes[0]
                    if len(existentes) > 1:
                        RegistroCharlaSupervisor.objects.filter(id__in=[r.id for r in existentes[1:]]).delete()

                    registro.holding_id = holding_id
                    registro.sociedad_id = contrato.trabajador.sociedad_id if contrato.trabajador_id else None
                    registro.supervisor = supervisor
                    registro.save(update_fields=['holding', 'sociedad', 'supervisor'])
                    actualizados += 1
                else:
                    RegistroCharlaSupervisor.objects.create(
                        holding_id=holding_id,
                        sociedad_id=contrato.trabajador.sociedad_id if contrato.trabajador_id else None,
                        supervisor=supervisor,
                        contrato=contrato,
                    )
                    creados += 1
                    actualizados += 1

        registros = RegistroCharlaSupervisor.objects.filter(
            holding_id=holding_id,
            contrato_id__in=contrato_ids,
        ).select_related(
            'supervisor',
            'supervisor__usuario',
            'supervisor__usuario__persona',
            'contrato',
            'contrato__trabajador',
        )

        return Response({
            'message': 'Registros de charla actualizados correctamente.',
            'actualizados': actualizados,
            'creados': creados,
            'registros': RegistroCharlaSupervisorSerializer(registros, many=True).data,
        }, status=status.HTTP_200_OK)

    def _nombre_supervisor(self, supervisor):
        if not supervisor or not supervisor.usuario_id:
            return 'Sin supervisor'
        persona = getattr(supervisor.usuario, 'persona', None)
        if persona:
            return f'{persona.nombres} {persona.apellidos or ""}'.strip()
        return supervisor.usuario.rut

    def _nombre_trabajador(self, trabajador):
        if not trabajador:
            return 'Sin trabajador'
        return f'{trabajador.nombres} {trabajador.apellidos or ""}'.strip()

    def _estado_contrato(self, contrato):
        if not contrato.fecha_termino_contrato:
            return 'VIGENTE'
        return 'VENCIDO' if contrato.fecha_termino_contrato < timezone.localdate() else 'VIGENTE'
