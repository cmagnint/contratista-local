
from .base import BaseAPIView
from rest_framework.response import Response
from rest_framework import status
import logging


from ..models import (
    ElementoSeguridad,
)

from ..serializers import (
    ElementoSeguridadSerializer,
)

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
        return Response(ElementoSeguridadSerializer(elementos_seguridad, many=True).data)

    def post(self, request, format=None):
        serializer = ElementoSeguridadSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error(f'ElementoSeguridadAPIView POST: datos inválidos: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, format=None):
        ids = request.data.get('ids', [])
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
            return Response({'message': 'Perfil no encontrado'}, status=status.HTTP_404_NOT_FOUND)

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
            return Response({'message': 'Cargo no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ElementoSeguridadSerializer(elemento_seguridad, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        logger.error(f'ElementoSeguridadAPIView PUT: datos inválidos: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
