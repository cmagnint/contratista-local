import logging

from rest_framework import status
from rest_framework.response import Response

from .base import BaseAPIView
from ..models import (
    AreasAdministracion,
    AreasCliente,
    CamposClientes,
    CargosAdministracion,
    CargosCliente,
    Clientes,
    ContactosClientes,
)
from ..serializers import (
    AreaAdministracionSerializer,
    AreaClienteSerializer,
    CamposClientesSerializer,
    CargoAdministracionSerializer,
    CargoClienteSerializer,
    ClienteSerializer,
    ContactosClienteSerializer,
)

logger = logging.getLogger('contratista_test_app')


# ==============================================================================
# CLIENTES
# ==============================================================================

class ClienteAPIView(BaseAPIView):

    def get(self, request, format=None):
        holding_id = request.query_params.get('holding')
        if not holding_id:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        clientes = Clientes.objects.filter(holding_id=holding_id)
        return Response(ClienteSerializer(clientes, many=True).data)

    def post(self, request, format=None):
        serializer = ClienteSerializer(data=request.data)
        if serializer.is_valid():
            cliente = serializer.save()
            logger.debug(f'ClienteAPIView POST: cliente {cliente.id} creado')
            return Response({'id': cliente.id, 'data': serializer.data}, status=status.HTTP_201_CREATED)

        logger.error(f'ClienteAPIView POST: datos inválidos: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, format=None):
        cliente_ids = request.data.get('ids', [])
        Clientes.objects.filter(id__in=cliente_ids).delete()
        logger.debug(f'ClienteAPIView DELETE: {len(cliente_ids)} clientes eliminados')
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, format=None):
        cliente_id = request.data.get('id')
        if not cliente_id:
            return Response(
                {'message': 'ID de cliente es necesario para actualizar'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            cliente = Clientes.objects.get(id=cliente_id)
        except Clientes.DoesNotExist:
            logger.error(f'ClienteAPIView PATCH: cliente {cliente_id} no encontrado')
            return Response({'message': 'Cliente no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ClienteSerializer(cliente, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        logger.error(f'ClienteAPIView PATCH: datos inválidos para cliente {cliente_id}: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, format=None):
        cliente_id = request.data.get('id')
        if not cliente_id:
            return Response(
                {'message': 'ID de cliente es necesario para actualizar'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            cliente = Clientes.objects.get(id=cliente_id)
        except Clientes.DoesNotExist:
            logger.error(f'ClienteAPIView PUT: cliente {cliente_id} no encontrado')
            return Response({'message': 'Cliente no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ClienteSerializer(cliente, data=request.data)
        if serializer.is_valid():
            cliente = serializer.save()
            for campo_data in request.data.get('camposPersonalizados', []):
                campo_id = campo_data.get('id')
                if not campo_id:
                    continue
                try:
                    campo = CamposClientes.objects.get(id=campo_id, cliente=cliente)
                    campo_serializer = CamposClientesSerializer(campo, data=campo_data)
                    if campo_serializer.is_valid():
                        campo_serializer.save()
                    else:
                        logger.error(f'ClienteAPIView PUT: campo {campo_id} inválido: {campo_serializer.errors}')
                except CamposClientes.DoesNotExist:
                    continue
            return Response(serializer.data)

        logger.error(f'ClienteAPIView PUT: datos inválidos para cliente {cliente_id}: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ==============================================================================
# CAMPOS CLIENTES
# ==============================================================================

class CamposClientesAPIView(BaseAPIView):

    def get(self, request, cliente_id=None, format=None):
        holding_id = request.query_params.get('holding_id')
        cliente_id = cliente_id or request.query_params.get('cliente')

        try:
            if cliente_id is not None:
                campos = CamposClientes.objects.filter(cliente_id=cliente_id)
            elif holding_id is not None:
                campos = CamposClientes.objects.filter(holding_id=holding_id)
            else:
                return Response(
                    {'message': 'Debe proporcionar cliente_id o holding_id'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if campos.exists():
                return Response(CamposClientesSerializer(campos, many=True).data, status=status.HTTP_200_OK)

            return Response(
                {'message': 'No se encontraron campos personalizados'},
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:
            logger.error(f'CamposClientesAPIView GET: error inesperado: {e}', exc_info=True)
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        serializer = CamposClientesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        logger.error(f'CamposClientesAPIView POST: datos inválidos: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, format=None):
        campo_id = request.data.get('id')
        try:
            campo = CamposClientes.objects.get(id=campo_id)
        except CamposClientes.DoesNotExist:
            logger.error(f'CamposClientesAPIView PUT: campo {campo_id} no encontrado')
            return Response({'message': 'Campo no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        serializer = CamposClientesSerializer(campo, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        logger.error(f'CamposClientesAPIView PUT: datos inválidos para campo {campo_id}: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, format=None):
        campo_ids = request.data.get('ids', [])
        CamposClientes.objects.filter(id__in=campo_ids).delete()
        logger.debug(f'CamposClientesAPIView DELETE: {len(campo_ids)} campos eliminados')
        return Response(status=status.HTTP_204_NO_CONTENT)


# ==============================================================================
# ÁREAS CLIENTES
# ==============================================================================

class AreaClienteAPIView(BaseAPIView):

    def get(self, request, format=None):
        holding_id = request.query_params.get('holding')
        if not holding_id:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        areas = AreasCliente.objects.filter(holding_id=holding_id)
        return Response(AreaClienteSerializer(areas, many=True).data)

    def post(self, request, format=None):
        serializer = AreaClienteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        logger.error(f'AreaClienteAPIView POST: datos inválidos: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, format=None):
        ids = request.data.get('ids', [])
        AreasCliente.objects.filter(id__in=ids).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, format=None):
        obj_id = request.data.get('id')
        if not obj_id:
            return Response(
                {'message': 'ID de area es necesario para actualizar'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            area = AreasCliente.objects.get(id=obj_id)
        except AreasCliente.DoesNotExist:
            logger.error(f'AreaClienteAPIView PATCH: area {obj_id} no encontrada')
            return Response({'message': 'Area no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        serializer = AreaClienteSerializer(area, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        logger.error(f'AreaClienteAPIView PATCH: datos inválidos para area {obj_id}: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, format=None):
        obj_id = request.data.get('id')
        try:
            area = AreasCliente.objects.get(id=obj_id)
        except AreasCliente.DoesNotExist:
            logger.error(f'AreaClienteAPIView PUT: area {obj_id} no encontrada')
            return Response({'message': 'Perfil no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        serializer = AreaClienteSerializer(area, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        logger.error(f'AreaClienteAPIView PUT: datos inválidos para area {obj_id}: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ==============================================================================
# CARGOS CLIENTES
# ==============================================================================

class CargoClienteAPIView(BaseAPIView):

    def get(self, request, format=None):
        holding_id = request.query_params.get('holding')
        if not holding_id:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        cargos = CargosCliente.objects.filter(holding_id=holding_id)
        return Response(CargoClienteSerializer(cargos, many=True).data)

    def post(self, request, format=None):
        serializer = CargoClienteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        logger.error(f'CargoClienteAPIView POST: datos inválidos: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, format=None):
        ids = request.data.get('ids', [])
        CargosCliente.objects.filter(id__in=ids).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, format=None):
        obj_id = request.data.get('id')
        if not obj_id:
            return Response(
                {'message': 'ID de perfil es necesario para actualizar'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            cargo = CargosCliente.objects.get(id=obj_id)
        except CargosCliente.DoesNotExist:
            logger.error(f'CargoClienteAPIView PATCH: cargo {obj_id} no encontrado')
            return Response({'message': 'Perfil no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        serializer = CargoClienteSerializer(cargo, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        logger.error(f'CargoClienteAPIView PATCH: datos inválidos para cargo {obj_id}: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, format=None):
        obj_id = request.data.get('id')
        try:
            cargo = CargosCliente.objects.get(id=obj_id)
        except CargosCliente.DoesNotExist:
            logger.error(f'CargoClienteAPIView PUT: cargo {obj_id} no encontrado')
            return Response({'message': 'Cargo no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        serializer = CargoClienteSerializer(cargo, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        logger.error(f'CargoClienteAPIView PUT: datos inválidos para cargo {obj_id}: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ==============================================================================
# CONTACTOS CLIENTES
# ==============================================================================

class ContactoClienteAPIView(BaseAPIView):

    def get(self, request, format=None):
        holding_id = request.query_params.get('holding')
        if not holding_id:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        contactos = ContactosClientes.objects.filter(holding_id=holding_id)
        return Response(ContactosClienteSerializer(contactos, many=True).data)

    def post(self, request, format=None):
        serializer = ContactosClienteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        logger.error(f'ContactoClienteAPIView POST: datos inválidos: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, format=None):
        ids = request.data.get('ids', [])
        ContactosClientes.objects.filter(id__in=ids).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, format=None):
        obj_id = request.data.get('id')
        if not obj_id:
            return Response(
                {'message': 'ID de perfil es necesario para actualizar'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            contacto = ContactosClientes.objects.get(id=obj_id)
        except ContactosClientes.DoesNotExist:
            logger.error(f'ContactoClienteAPIView PATCH: contacto {obj_id} no encontrado')
            return Response({'message': 'Perfil no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ContactosClienteSerializer(contacto, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        logger.error(f'ContactoClienteAPIView PATCH: datos inválidos para contacto {obj_id}: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, format=None):
        obj_id = request.data.get('id')
        try:
            contacto = ContactosClientes.objects.get(id=obj_id)
        except ContactosClientes.DoesNotExist:
            logger.error(f'ContactoClienteAPIView PUT: contacto {obj_id} no encontrado')
            return Response({'message': 'Cargo no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ContactosClienteSerializer(contacto, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        logger.error(f'ContactoClienteAPIView PUT: datos inválidos para contacto {obj_id}: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


