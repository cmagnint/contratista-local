import io
import logging
from datetime import datetime, timedelta

from django.db import transaction
from django.db.models import Exists, OuterRef
from django.http import HttpResponse
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle

from .base import BaseAPIView
from ..models import (
    CamposClientes,
    CargosAdministracion,
    CasasTrabajadores,
    Clientes,
    ContratoTrabajador,
    FolioComercial,
    FolioComercialLabor,
    HistorialCambioFolio,
    HistorialCambioPago,
    Holding,
    Horarios,
    Labores,
    PersonalTrabajadores,
    ProduccionTrabajador,
    RegistroCasaTrabajador,
    RegistroManoObraPersona,
    RegistroPagoEfectivo,
    RegistroPagoTransferencia,
    Supervisores,
    UnidadControl,
)
from ..serializers import (
    CampoClienteDropdownPagoSerializer,
    CargosAdministracionPagoSerializer,
    CasaTrabajadorDropdownPagoSerializer,
    CasasTrabajadoresPagoSerializer,
    ClientesFiltroPagoSerializer,
    DataProduccionSerializer,
    FiltrosPagoEfectivoSerializer,
    FiltrosPagoSerializer,
    FolioComercialPreContratacionSerializer,
    FolioComercialSerializer,
    HorarioSerializer,
    LaboresSerializer,
    PagoRealizadoSerializer,
    ProduccionCSVSerializer,
    ProduccionInformePagoDetalleSerializer,
    ProduccionPendienteSerializer,
    ProduccionTrabajadorSerializer,
    SupervisorDropdownPagoSerializer,
    UnidadControlSerializer,
)

logger = logging.getLogger('contratista_test_app')


# ==============================================================================
# PRODUCCIÓN PENDIENTE
# ==============================================================================

class ProduccionPendienteAPIView(BaseAPIView):

    def get(self, request):
        fecha_inicio = request.GET.get('fecha_inicio')
        fecha_fin = request.GET.get('fecha_fin')

        producciones = ProduccionTrabajador.objects.filter(
            hora_fecha_ingreso_produccion__date__range=[fecha_inicio, fecha_fin],
            pagado=False
        ).select_related('trabajador', 'folio')

        return Response(ProduccionPendienteSerializer(producciones, many=True).data)


# ==============================================================================
# FILTROS PRODUCCIÓN (TRANSFERENCIA)
# ==============================================================================

class FiltrosProduccionAPIView(BaseAPIView):

    def get(self, request):
        try:
            holding_id = request.GET.get('holding_id')
            fecha_inicio = request.GET.get('fecha_inicio')
            fecha_fin = request.GET.get('fecha_fin')

            if not all([holding_id, fecha_inicio, fecha_fin]):
                return Response({'error': 'Faltan parámetros requeridos'}, status=status.HTTP_400_BAD_REQUEST)

            queryset = ProduccionTrabajador.objects.filter(
                holding_id=holding_id,
                hora_fecha_ingreso_produccion__date__range=[fecha_inicio, fecha_fin],
                pagado=False,
                trabajador__metodo_pago='Transferencia'
            ).select_related('trabajador', 'trabajador__casa', 'trabajador__cargo', 'folio', 'folio__cliente')

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

            return Response(FiltrosPagoSerializer(queryset, many=True).data)

        except Exception as e:
            logger.error(f'FiltrosProduccionAPIView GET: error: {e}', exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==============================================================================
# OPCIONES FILTROS
# ==============================================================================

class OpcionesFiltrosAPIView(BaseAPIView):

    def get(self, request, holding_id):
        try:
            Holding.objects.get(id=holding_id)

            clientes = Clientes.objects.filter(holding_id=holding_id)
            cargos = CargosAdministracion.objects.filter(holding_id=holding_id)
            casas = CasasTrabajadores.objects.filter(holding_id=holding_id)

            return Response({
                'clientes': ClientesFiltroPagoSerializer(clientes, many=True).data,
                'cargos': CargosAdministracionPagoSerializer(cargos, many=True).data,
                'casas': CasasTrabajadoresPagoSerializer(casas, many=True).data,
            })

        except Holding.DoesNotExist:
            logger.error(f'OpcionesFiltrosAPIView GET: holding {holding_id} no encontrado')
            return Response({'error': 'Holding no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f'OpcionesFiltrosAPIView GET: error: {e}', exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==============================================================================
# FILTROS PRODUCCIÓN TRANSFERENCIA (RegistroManoObraPersona)
# ==============================================================================

class FiltrosProduccionTransferenciaAPIView(BaseAPIView):

    def get(self, request):
        try:
            holding_id = request.GET.get('holding_id')
            fecha_inicio = request.GET.get('fecha_inicio')
            fecha_fin = request.GET.get('fecha_fin')

            if not all([holding_id, fecha_inicio, fecha_fin]):
                return Response({'error': 'Faltan parámetros requeridos'}, status=status.HTTP_400_BAD_REQUEST)

            queryset = RegistroManoObraPersona.objects.filter(
                holding_id=holding_id,
                fecha_ingreso__range=[fecha_inicio, fecha_fin],
                trabajador__metodo_pago='Transferencia'
            ).select_related('trabajador', 'trabajador__cargo', 'folio', 'folio__cliente', 'labor')

            logger.debug(f'FiltrosProduccionTransferenciaAPIView GET: {queryset.count()} registros base')

            cliente_ids = request.GET.get('cliente_ids')
            if cliente_ids:
                ids = [i for i in cliente_ids.split(',') if i.isdigit()]
                if ids:
                    queryset = queryset.filter(folio__cliente_id__in=ids)

            fundo_ids = request.GET.get('fundo_ids')
            if fundo_ids:
                ids = [i for i in fundo_ids.split(',') if i.isdigit()]
                if ids:
                    queryset = queryset.filter(folio__fundos__id__in=ids)

            cargo_ids = request.GET.get('cargo_ids')
            if cargo_ids:
                ids = [i for i in cargo_ids.split(',') if i.isdigit()]
                if ids:
                    queryset = queryset.filter(trabajador__cargo_id__in=ids)

            casa_ids = request.GET.get('casa_ids')
            if casa_ids:
                ids = [i for i in casa_ids.split(',') if i.isdigit()]
                if ids:
                    trabajadores_en_casas = RegistroCasaTrabajador.objects.filter(
                        casa_id__in=ids, fecha_fin__isnull=True
                    ).values_list('trabajador_id', flat=True)
                    queryset = queryset.filter(trabajador_id__in=trabajadores_en_casas)

            serializer = FiltrosPagoEfectivoSerializer(queryset, many=True)
            logger.debug(f'FiltrosProduccionTransferenciaAPIView GET: {len(serializer.data)} registros retornados')
            return Response(serializer.data)

        except Exception as e:
            logger.error(f'FiltrosProduccionTransferenciaAPIView GET: error: {e}', exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==============================================================================
# PROCESAR PAGO (TRANSFERENCIA)
# ==============================================================================

class ProcesarPagoAPIView(BaseAPIView):

    def post(self, request):
        try:
            holding_id = request.data.get('holding_id')
            sociedad_id = request.data.get('sociedad_id')
            cuenta_id = request.data.get('cuenta_id')
            registros_ids = request.data.get('producciones')

            if not all([holding_id, sociedad_id, cuenta_id, registros_ids]):
                return Response({'error': 'Faltan datos requeridos'}, status=status.HTTP_400_BAD_REQUEST)

            with transaction.atomic():
                registros = RegistroManoObraPersona.objects.filter(
                    id__in=registros_ids
                ).select_related('trabajador', 'folio', 'labor')

                pagos_por_trabajador = {}

                for reg in registros:
                    trabajador_id = reg.trabajador_id
                    if trabajador_id not in pagos_por_trabajador:
                        pagos_por_trabajador[trabajador_id] = {
                            'trabajador': reg.trabajador,
                            'monto_total': 0,
                            'registros': []
                        }

                    monto = 0
                    if reg.folio and reg.labor:
                        fc_labor = FolioComercialLabor.objects.filter(
                            folio=reg.folio, labor=reg.labor
                        ).first()
                        if fc_labor:
                            monto = float(reg.produccion * fc_labor.valor_pago_trabajador)

                    pagos_por_trabajador[trabajador_id]['monto_total'] += monto
                    pagos_por_trabajador[trabajador_id]['registros'].append(reg)

                for trabajador_id, datos in pagos_por_trabajador.items():
                    RegistroPagoTransferencia.objects.create(
                        holding_id=holding_id,
                        sociedad_id=sociedad_id,
                        cuenta_origen_id=cuenta_id,
                        trabajador=datos['trabajador'],
                        monto_pagado=int(datos['monto_total'])
                    )

            logger.debug(f'ProcesarPagoAPIView POST: {len(pagos_por_trabajador)} pagos procesados')
            return Response({'message': 'Pagos procesados correctamente'})

        except Exception as e:
            logger.error(f'ProcesarPagoAPIView POST: error: {e}', exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==============================================================================
# PAGOS REALIZADOS
# ==============================================================================

class PagosRealizadosAPIView(BaseAPIView):

    def get(self, request):
        try:
            holding_id = request.GET.get('holding_id')
            fecha_inicio = request.GET.get('fecha_inicio')
            fecha_fin = request.GET.get('fecha_fin')
            tipo_pago = request.GET.get('tipo_pago', 'todos')

            if not all([holding_id, fecha_inicio, fecha_fin]):
                return Response({'error': 'Faltan parámetros requeridos'}, status=status.HTTP_400_BAD_REQUEST)

            fecha_fin_str = f'{fecha_fin} 23:59:59'

            transferencias = RegistroPagoTransferencia.objects.filter(
                holding_id=holding_id,
                fecha_pago__range=[fecha_inicio, fecha_fin_str]
            ).select_related('sociedad', 'cuenta_origen', 'trabajador')

            pagos_efectivo = RegistroPagoEfectivo.objects.filter(
                holding_id=holding_id,
                fecha_pago__range=[fecha_inicio, fecha_fin_str]
            ).select_related('sociedad', 'cuenta_origen', 'trabajador')

            if tipo_pago == 'transferencia':
                pagos = transferencias
            elif tipo_pago == 'efectivo':
                pagos = pagos_efectivo
            else:
                pagos = sorted(
                    list(transferencias) + list(pagos_efectivo),
                    key=lambda x: x.fecha_pago,
                    reverse=True
                )

            return Response(PagoRealizadoSerializer(pagos, many=True).data)

        except Exception as e:
            logger.error(f'PagosRealizadosAPIView GET: error: {e}', exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==============================================================================
# FILTROS PRODUCCIÓN EFECTIVO (RegistroManoObraPersona)
# ==============================================================================

class FiltrosProduccionEfectivoAPIView(BaseAPIView):

    def get(self, request):
        try:
            holding_id = request.GET.get('holding_id')
            fecha_inicio = request.GET.get('fecha_inicio')
            fecha_fin = request.GET.get('fecha_fin')

            if not all([holding_id, fecha_inicio, fecha_fin]):
                return Response(
                    {'error': 'Faltan parámetros requeridos'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            registros_pagados = RegistroPagoEfectivo.objects.filter(
                producciones=OuterRef('pk')
            )

            queryset = RegistroManoObraPersona.objects.filter(
                holding_id=holding_id,
                fecha_ingreso__range=[fecha_inicio, fecha_fin],
                trabajador__metodo_pago='Efectivo'
            ).annotate(
                pagado=Exists(registros_pagados)
            ).select_related(
                'trabajador', 'trabajador__cargo', 'folio', 'folio__cliente', 'labor'
            )

            cliente_ids = request.GET.get('cliente_ids')
            if cliente_ids:
                ids = [i for i in cliente_ids.split(',') if i.isdigit()]
                if ids:
                    queryset = queryset.filter(folio__cliente_id__in=ids)

            fundo_ids = request.GET.get('fundo_ids')
            if fundo_ids:
                ids = [i for i in fundo_ids.split(',') if i.isdigit()]
                if ids:
                    queryset = queryset.filter(folio__fundos__id__in=ids)

            cargo_ids = request.GET.get('cargo_ids')
            if cargo_ids:
                ids = [i for i in cargo_ids.split(',') if i.isdigit()]
                if ids:
                    queryset = queryset.filter(trabajador__cargo_id__in=ids)

            casa_ids = request.GET.get('casa_ids')
            if casa_ids:
                ids = [i for i in casa_ids.split(',') if i.isdigit()]
                if ids:
                    trabajadores_en_casas = RegistroCasaTrabajador.objects.filter(
                        casa_id__in=ids, fecha_fin__isnull=True
                    ).values_list('trabajador_id', flat=True)
                    queryset = queryset.filter(trabajador_id__in=trabajadores_en_casas)

            serializer = FiltrosPagoEfectivoSerializer(queryset, many=True)
            logger.debug(
                f'FiltrosProduccionEfectivoAPIView GET: {len(serializer.data)} registros retornados'
            )
            return Response(serializer.data)

        except Exception as e:
            logger.error(f'FiltrosProduccionEfectivoAPIView GET: error: {e}', exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
# ==============================================================================
# PROCESAR PAGO EFECTIVO
# ==============================================================================

class ProcesarPagoEfectivoAPIView(BaseAPIView):

    def post(self, request):
        try:
            holding_id = request.data.get('holding_id')
            sociedad_id = request.data.get('sociedad_id')
            pagos = request.data.get('pagos')
            multiplo_pago = request.data.get('multiplo_pago')

            if not all([holding_id, sociedad_id, pagos, multiplo_pago]):
                return Response(
                    {'error': 'Faltan datos requeridos'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            with transaction.atomic():
                for pago in pagos:
                    registro_ids = pago.get('registro_ids', [])
                    if not registro_ids:
                        continue

                    registros = RegistroManoObraPersona.objects.filter(
                        id__in=registro_ids,
                        holding_id=holding_id,
                    )

                    ya_pagados = RegistroPagoEfectivo.objects.filter(
                        producciones__in=registros
                    ).exists()

                    if ya_pagados:
                        continue

                    if not registros.exists():
                        continue

                    trabajador = registros.first().trabajador

                    registro_pago = RegistroPagoEfectivo.objects.create(
                        holding_id=holding_id,
                        sociedad_id=sociedad_id,
                        trabajador=trabajador,
                        monto_pagado=pago['monto_pagado'],
                        multiplo_pago=multiplo_pago,
                        saldo=pago['saldo']
                    )
                    registro_pago.producciones.add(*registros)

            logger.debug(
                f'ProcesarPagoEfectivoAPIView POST: {len(pagos)} pagos en efectivo procesados'
            )
            return Response(
                {'message': 'Pagos en efectivo procesados correctamente'},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            logger.error(
                f'ProcesarPagoEfectivoAPIView POST: error: {e}', exc_info=True
            )
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
# ==============================================================================
# GENERAR PLANILLA EFECTIVO
# ==============================================================================

MESES_ES = {
    1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
    5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
    9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
}


def formatear_rut(valor):
    """Formatea a XX.XXX.XXX-X. Limpia puntos/guiones/espacios primero."""
    if not valor or valor == '-':
        return '-'
    limpio = str(valor).replace('.', '').replace('-', '').replace(' ', '').strip().upper()
    if len(limpio) < 2:
        return valor
    cuerpo, dv = limpio[:-1], limpio[-1]
    # Puntos cada 3 dígitos desde la derecha
    cuerpo_formateado = ''
    for i, c in enumerate(reversed(cuerpo)):
        if i > 0 and i % 3 == 0:
            cuerpo_formateado = '.' + cuerpo_formateado
        cuerpo_formateado = c + cuerpo_formateado
    return f"{cuerpo_formateado}-{dv}"


class GenerarPlanillaEfectivoAPIView(BaseAPIView):

    def get(self, request):
        try:
            holding_id = request.GET.get('holding_id')
            fecha_inicio = datetime.strptime(request.GET.get('fecha_inicio'), '%Y-%m-%d')
            fecha_fin = datetime.strptime(request.GET.get('fecha_fin'), '%Y-%m-%d')
            multiplo = int(request.GET.get('multiplo', 5000))

            logger.debug(
                f'GenerarPlanillaEfectivoAPIView GET: holding={holding_id} '
                f'desde={fecha_inicio.date()} hasta={fecha_fin.date()} multiplo={multiplo}'
            )

            # Lista de días: retrocede al lunes de la semana de fecha_inicio
            dias = []
            fecha_actual = fecha_inicio
            while fecha_actual.weekday() > 0:
                fecha_actual -= timedelta(days=1)
            while fecha_actual <= fecha_fin:
                dias.append(fecha_actual)
                fecha_actual += timedelta(days=1)

            queryset = RegistroManoObraPersona.objects.filter(
                holding_id=holding_id,
                fecha_ingreso__range=[fecha_inicio.date(), fecha_fin.date()],
                trabajador__metodo_pago='Efectivo'
            ).select_related('trabajador', 'trabajador__cargo', 'folio', 'folio__cliente', 'labor')

            # Filtros opcionales
            for param, filtro in [
                ('cliente_ids', 'folio__cliente_id__in'),
                ('fundo_ids', 'folio__fundos__id__in'),
                ('cargo_ids', 'trabajador__cargo_id__in'),
            ]:
                valor = request.GET.get(param) or request.GET.get(param.rstrip('s') + '_id')
                if valor:
                    ids = [i for i in valor.split(',') if i.isdigit()]
                    if ids:
                        queryset = queryset.filter(**{filtro: ids})

            casa_ids = request.GET.get('casa_ids') or request.GET.get('casa_id')
            if casa_ids:
                ids = [i for i in casa_ids.split(',') if i.isdigit()]
                if ids:
                    trab_en_casas = RegistroCasaTrabajador.objects.filter(
                        casa_id__in=ids, fecha_fin__isnull=True
                    ).values_list('trabajador_id', flat=True)
                    queryset = queryset.filter(trabajador_id__in=trab_en_casas)

            queryset = queryset.distinct()

            logger.debug(f'GenerarPlanillaEfectivoAPIView GET: {queryset.count()} registros encontrados')

            # Agrupar por trabajador (key = trabajador.id)
            trabajadores_data = {}
            for prod in queryset:
                if not prod.trabajador:
                    continue

                t = prod.trabajador
                worker_key = t.id

                # Identificador: RUT → NIC → DNI → '-'
                identificador = t.rut or t.nic or t.dni or '-'
                identificador = formatear_rut(identificador)

                # Nombre completo
                nombre_completo = f"{t.nombres or ''} {t.apellidos or ''}".strip()

                # Normalizar fecha a date
                fecha = prod.fecha_ingreso
                if hasattr(fecha, 'date') and callable(fecha.date):
                    fecha = fecha.date()

                # Solo dentro del rango
                if not (fecha_inicio.date() <= fecha <= fecha_fin.date()):
                    continue

                monto = 0
                if prod.folio and prod.labor:
                    fc_labor = FolioComercialLabor.objects.filter(
                        folio=prod.folio, labor=prod.labor
                    ).first()
                    if fc_labor:
                        monto = float(prod.produccion * fc_labor.valor_pago_trabajador)

                if worker_key not in trabajadores_data:
                    trabajadores_data[worker_key] = {
                        'nombre': nombre_completo,
                        'rut': identificador,
                        'pagos_diarios': {dia.date(): 0 for dia in dias},
                        'total': 0,
                        'saldo_anterior': 0
                    }

                # Sumar (no sobreescribir): soporta varias labores en el mismo día
                if fecha in trabajadores_data[worker_key]['pagos_diarios']:
                    trabajadores_data[worker_key]['pagos_diarios'][fecha] += monto
                else:
                    trabajadores_data[worker_key]['pagos_diarios'][fecha] = monto

                trabajadores_data[worker_key]['total'] += monto

            # Generar PDF
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=landscape(A4),
                leftMargin=5*mm, rightMargin=5*mm,
                topMargin=10*mm, bottomMargin=10*mm
            )

            ancho_pagina = (landscape(A4)[0] - 10*mm) * 0.90
            DIAS_POR_FILA = 7
            ancho_dia = (ancho_pagina * 0.46) / DIAS_POR_FILA
            anchos_columnas = (
                [ancho_pagina * 0.15, ancho_pagina * 0.09]
                + [ancho_dia] * DIAS_POR_FILA
                + [ancho_pagina * 0.06, ancho_pagina * 0.06, ancho_pagina * 0.07, ancho_pagina * 0.11]
            )

            # Estilo para nombre con wrap
            nombre_style = ParagraphStyle(
                'NombreStyle',
                fontSize=7,
                leading=8,
                alignment=0,  # izquierda
                wordWrap='CJK'
            )

            def prepare_table_data(trabajadores_data, dias):
                dias_semana = ['LUNES', 'MARTES', 'MIÉRCOLES', 'JUEVES', 'VIERNES', 'SÁBADO', 'DOMINGO']
                table_data = [['NOMBRE', 'RUT/NIC'] + dias_semana + ['SALDO ANT.', 'TOTAL', 'SALDO PROX.', 'FIRMA']]
                fecha_indices, span_info, separator_rows = [], [], []
                current_row = 1

                for worker_key, worker_data in trabajadores_data.items():
                    num_grupos = (len(dias) + DIAS_POR_FILA - 1) // DIAS_POR_FILA
                    rows_for_worker = num_grupos * 2

                    total_sin_redondear = worker_data['total']
                    total_redondeado = (total_sin_redondear // multiplo) * multiplo
                    saldo = total_sin_redondear - total_redondeado
                    saldo_final = worker_data['saldo_anterior'] + saldo

                    for span in [(0, 0), (1, 1), (-4, -4), (-3, -3), (-2, -2), (-1, -1)]:
                        span_info.append(('SPAN', (span[0], current_row), (span[1], current_row + rows_for_worker - 1)))

                    for grupo in range(num_grupos):
                        start_idx = grupo * DIAS_POR_FILA
                        end_idx = min((grupo + 1) * DIAS_POR_FILA, len(dias))
                        current_dias = dias[start_idx:end_idx]

                        nombre_cell = Paragraph(worker_data['nombre'], nombre_style) if grupo == 0 else ''
                        row = [nombre_cell, worker_data['rut']] if grupo == 0 else ['', '']
                        dias_alineados = [''] * DIAS_POR_FILA
                        for d in current_dias:
                            if fecha_inicio <= d <= fecha_fin:
                                dias_alineados[d.weekday()] = d.strftime('%d/%m')
                        row.extend(dias_alineados)
                        row.extend(
                            [
                                f"{worker_data['saldo_anterior']:+,.0f}" if worker_data['saldo_anterior'] != 0 else '0',
                                f"{total_redondeado:,.0f}",
                                f"{saldo_final:+,.0f}" if saldo_final != 0 else '0',
                                ''
                            ] if grupo == 0 else ['', '', '', '']
                        )

                        fecha_indices.append(len(table_data))
                        table_data.append(row)
                        current_row += 1

                        montos_row = ['', '']
                        montos_alineados = [''] * DIAS_POR_FILA
                        for d in current_dias:
                            if fecha_inicio <= d <= fecha_fin:
                                monto = worker_data['pagos_diarios'].get(d.date(), 0)
                                montos_alineados[d.weekday()] = f'{monto:,.0f}' if monto else '0'
                        montos_row.extend(montos_alineados)
                        montos_row.extend(['', '', '', ''])
                        table_data.append(montos_row)
                        current_row += 1

                    separator_rows.append(current_row)
                    table_data.append([''] * (DIAS_POR_FILA + 6))
                    current_row += 1

                return table_data, fecha_indices, span_info, separator_rows

            table_data, fecha_indices, span_info, separator_rows = prepare_table_data(trabajadores_data, dias)
            table = Table(table_data, colWidths=anchos_columnas)

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
                    ('BOTTOMPADDING', (0, row_idx), (-1, row_idx), 0.5),
                ])
            for indice in fecha_indices:
                estilos.append(('BACKGROUND', (2, indice), (8, indice), colors.lightgrey))
            estilos.extend(span_info)
            table.setStyle(TableStyle(estilos))

            # Header en español
            mes_inicio = MESES_ES[fecha_inicio.month]
            mes_fin = MESES_ES[fecha_fin.month]
            año_fin = fecha_fin.year

            header_style = ParagraphStyle('CustomHeader', fontSize=10, alignment=1, spaceAfter=5*mm)
            header = Paragraph(
                f'<b>PLANILLA DE PAGO</b><br/>'
                f'Semana del {fecha_inicio.day:02d} de {mes_inicio} al '
                f'{fecha_fin.day:02d} de {mes_fin} {año_fin}',
                header_style
            )

            doc.build([header, table])
            buffer.seek(0)

            logger.debug('GenerarPlanillaEfectivoAPIView GET: PDF generado exitosamente')
            response = HttpResponse(buffer, content_type='application/pdf')
            response['Content-Disposition'] = (
                f'attachment; filename=planilla_efectivo_{fecha_inicio.strftime("%Y%m%d")}.pdf'
            )
            return response

        except Exception as e:
            logger.error(f'GenerarPlanillaEfectivoAPIView GET: error: {e}', exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
# ==============================================================================
# UNIDAD CONTROL
# ==============================================================================

class UnidadControlAPIView(BaseAPIView):

    def get(self, request, format=None):
        holding_id = request.query_params.get('holding')
        if not holding_id:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        unidades = UnidadControl.objects.filter(holding_id=holding_id)
        return Response(UnidadControlSerializer(unidades, many=True).data)

    def post(self, request, format=None):
        serializer = UnidadControlSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error(f'UnidadControlAPIView POST: datos inválidos: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, format=None):
        ids = request.data.get('ids', [])
        UnidadControl.objects.filter(id__in=ids).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, format=None):
        obj_id = request.data.get('id')
        if not obj_id:
            return Response({'message': 'ID es necesario para actualizar'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            unidad = UnidadControl.objects.get(id=obj_id)
        except UnidadControl.DoesNotExist:
            logger.error(f'UnidadControlAPIView PATCH: unidad {obj_id} no encontrada')
            return Response({'message': 'Perfil no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        serializer = UnidadControlSerializer(unidad, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        logger.error(f'UnidadControlAPIView PATCH: datos inválidos: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, format=None):
        obj_id = request.data.get('id')
        try:
            unidad = UnidadControl.objects.get(id=obj_id)
        except UnidadControl.DoesNotExist:
            logger.error(f'UnidadControlAPIView PUT: unidad {obj_id} no encontrada')
            return Response({'message': 'Cargo no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        serializer = UnidadControlSerializer(unidad, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        logger.error(f'UnidadControlAPIView PUT: datos inválidos: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ==============================================================================
# LABORES
# ==============================================================================

class LaboresAPIView(BaseAPIView):

    def get(self, request, format=None):
        holding_id = request.query_params.get('holding')
        if not holding_id:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        labores = Labores.objects.filter(holding_id=holding_id)
        return Response(LaboresSerializer(labores, many=True).data)

    def post(self, request, format=None):
        serializer = LaboresSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error(f'LaboresAPIView POST: datos inválidos: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, format=None):
        ids = request.data.get('ids', [])
        Labores.objects.filter(id__in=ids).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, format=None):
        obj_id = request.data.get('id')
        if not obj_id:
            return Response({'message': 'ID es necesario para actualizar'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            labor = Labores.objects.get(id=obj_id)
        except Labores.DoesNotExist:
            logger.error(f'LaboresAPIView PATCH: labor {obj_id} no encontrada')
            return Response({'message': 'Perfil no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        serializer = LaboresSerializer(labor, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        logger.error(f'LaboresAPIView PATCH: datos inválidos: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, format=None):
        obj_id = request.data.get('id')
        try:
            labor = Labores.objects.get(id=obj_id)
        except Labores.DoesNotExist:
            logger.error(f'LaboresAPIView PUT: labor {obj_id} no encontrada')
            return Response({'message': 'Cargo no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        serializer = LaboresSerializer(labor, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        logger.error(f'LaboresAPIView PUT: datos inválidos: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ==============================================================================
# FOLIO COMERCIAL
# ==============================================================================

class FolioComercialAPIView(BaseAPIView):

    def get(self, request, holding_id=None, format=None):
        holding_id = request.query_params.get('holding')
        pre_contratacion = request.query_params.get('pre_contratacion', 'false').lower() == 'true'
        estado = request.query_params.get('estado', 'activos')

        folios = FolioComercial.objects.filter(holding_id=holding_id) if holding_id else FolioComercial.objects.all()

        if estado == 'activos':
            folios = folios.filter(estado=True)
        elif estado == 'inactivos':
            folios = folios.filter(estado=False)

        if pre_contratacion:
            serializer = FolioComercialPreContratacionSerializer(folios, many=True)
        else:
            serializer = FolioComercialSerializer(folios, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        serializer = FolioComercialSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error(f'FolioComercialAPIView POST: datos inválidos: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, format=None):
        folio_ids = request.data.get('ids', [])
        folios_con_contratos = ContratoTrabajador.objects.filter(
            folio_id__in=folio_ids
        ).values_list('folio_id', flat=True).distinct()

        if folios_con_contratos:
            return Response({
                'message': 'No se pueden eliminar folios que tienen contratos asociados',
                'folios_con_contratos': list(folios_con_contratos)
            }, status=status.HTTP_400_BAD_REQUEST)

        FolioComercial.objects.filter(id__in=folio_ids).delete()
        logger.debug(f'FolioComercialAPIView DELETE: {len(folio_ids)} folios eliminados')
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, format=None):
        folio_id = request.data.get('id')
        if not folio_id:
            return Response({'message': 'ID de folio es necesario'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            folio = FolioComercial.objects.get(id=folio_id)
        except FolioComercial.DoesNotExist:
            logger.error(f'FolioComercialAPIView PATCH: folio {folio_id} no encontrado')
            return Response({'message': 'Folio no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        serializer = FolioComercialSerializer(folio, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        logger.error(f'FolioComercialAPIView PATCH: datos inválidos: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, format=None):
        folio_id = request.data.get('id')
        if not folio_id:
            return Response({'message': 'ID de folio es requerido'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            folio = FolioComercial.objects.get(id=folio_id)
        except FolioComercial.DoesNotExist:
            logger.error(f'FolioComercialAPIView PUT: folio {folio_id} no encontrado')
            return Response({'message': 'Folio no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        serializer = FolioComercialSerializer(folio, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        logger.error(f'FolioComercialAPIView PUT: datos inválidos: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ==============================================================================
# ENVIAR DATA PRODUCCIÓN
# ==============================================================================

class EnviarDataProduccionAPIView(BaseAPIView):
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, holding_id):
        serializer = DataProduccionSerializer(context={'holding_id': holding_id})
        return Response({
            'trabajadores': serializer.get_trabajadores(None),
            'labores': serializer.get_labores(None),
            'unidades_control': serializer.get_unidades_control(None),
        })


# ==============================================================================
# HORARIO
# ==============================================================================

class HorarioAPIView(BaseAPIView):

    def get(self, request, format=None):
        holding_id = request.query_params.get('holding')
        if not holding_id:
            return Response({'error': 'holding_id requerido'}, status=status.HTTP_400_BAD_REQUEST)
        horarios = Horarios.objects.filter(holding_id=holding_id)
        sociedad_id = request.query_params.get('sociedad')
        if sociedad_id:
            horarios = horarios.filter(sociedad_id=sociedad_id)
        return Response(HorarioSerializer(horarios, many=True).data)

    def post(self, request, format=None):
        serializer = HorarioSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error(f'HorarioAPIView POST: datos inválidos: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, format=None):
        ids = request.data.get('ids', [])
        Horarios.objects.filter(id__in=ids).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, format=None):
        horario_id = request.data.get('id')
        if not horario_id:
            return Response({'error': 'ID requerido'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            horario = Horarios.objects.get(id=horario_id)
        except Horarios.DoesNotExist:
            logger.error(f'HorarioAPIView PATCH: horario {horario_id} no encontrado')
            return Response({'error': 'No encontrado'}, status=status.HTTP_404_NOT_FOUND)
        serializer = HorarioSerializer(horario, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            from ..models import ContratoHorarioSnapshot, ContratoTrabajador
            horario = serializer.instance
            dias = ['lunes','martes','miercoles','jueves','viernes','sabado','domingo']
            horas_por_dia = {}
            for i, dia in enumerate(dias):
                inicio = getattr(horario, f'{dia}_inicio', None)
                fin = getattr(horario, f'{dia}_fin', None)
                colacion = getattr(horario, f'{dia}_minutos_colacion', 0) or 0
                if inicio and fin:
                    from datetime import datetime
                    mins = (datetime.combine(datetime.today(), fin) - datetime.combine(datetime.today(), inicio)).seconds // 60
                    horas_por_dia[str(i)] = round((mins - colacion) / 60, 2)
                else:
                    horas_por_dia[str(i)] = 0.0
            for contrato in ContratoTrabajador.objects.filter(horario=horario).select_related('trabajador', 'holding'):
                ContratoHorarioSnapshot.objects.update_or_create(
                    contrato=contrato,
                    defaults={
                        'trabajador': contrato.trabajador,
                        'holding': contrato.holding,
                        'datos': {'nombre': horario.nombre, 'horas_por_dia': horas_por_dia}
                    }
                )
            return Response(serializer.data)
        logger.error(f'HorarioAPIView PATCH: datos inválidos: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, format=None):
        horario_id = request.data.get('id')
        try:
            horario = Horarios.objects.get(id=horario_id)
        except Horarios.DoesNotExist:
            logger.error(f'HorarioAPIView PUT: horario {horario_id} no encontrado')
            return Response({'error': 'No encontrado'}, status=status.HTTP_404_NOT_FOUND)
        serializer = HorarioSerializer(horario, data=request.data)
        if serializer.is_valid():
            serializer.save()
            from ..models import ContratoHorarioSnapshot, ContratoTrabajador
            horario = serializer.instance
            dias = ['lunes','martes','miercoles','jueves','viernes','sabado','domingo']
            horas_por_dia = {}
            for i, dia in enumerate(dias):
                inicio = getattr(horario, f'{dia}_inicio', None)
                fin = getattr(horario, f'{dia}_fin', None)
                colacion = getattr(horario, f'{dia}_minutos_colacion', 0) or 0
                if inicio and fin:
                    from datetime import datetime
                    mins = (datetime.combine(datetime.today(), fin) - datetime.combine(datetime.today(), inicio)).seconds // 60
                    horas_por_dia[str(i)] = round((mins - colacion) / 60, 2)
                else:
                    horas_por_dia[str(i)] = 0.0
            for contrato in ContratoTrabajador.objects.filter(horario=horario).select_related('trabajador', 'holding'):
                ContratoHorarioSnapshot.objects.update_or_create(
                    contrato=contrato,
                    defaults={
                        'trabajador': contrato.trabajador,
                        'holding': contrato.holding,
                        'datos': {'nombre': horario.nombre, 'horas_por_dia': horas_por_dia}
                    }
                )
            return Response(serializer.data)
        logger.error(f'HorarioAPIView PUT: datos inválidos: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ==============================================================================
# PRODUCCIÓN TRABAJADOR
# ==============================================================================

class ProduccionTrabajadorAPIView(BaseAPIView):

    def get(self, request, format=None):
        holding_id = request.query_params.get('holding')
        if not holding_id:
            return Response({'error': 'El parámetro holding es necesario'}, status=status.HTTP_400_BAD_REQUEST)
        producciones = ProduccionTrabajador.objects.filter(holding_id=holding_id)
        return Response(ProduccionTrabajadorSerializer(producciones, many=True).data)

    def post(self, request, format=None):
        serializer = ProduccionTrabajadorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error(f'ProduccionTrabajadorAPIView POST: datos inválidos: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, format=None):
        ids = request.data.get('ids', [])
        ProduccionTrabajador.objects.filter(id__in=ids).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, format=None):
        produccion_id = request.data.get('id')
        if not produccion_id:
            return Response({'message': 'ID de producción es necesario para actualizar'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            produccion = ProduccionTrabajador.objects.get(id=produccion_id)
        except ProduccionTrabajador.DoesNotExist:
            logger.error(f'ProduccionTrabajadorAPIView PATCH: producción {produccion_id} no encontrada')
            return Response({'message': 'Producción no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ProduccionTrabajadorSerializer(produccion, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        logger.error(f'ProduccionTrabajadorAPIView PATCH: datos inválidos: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, format=None):
        worker_id = request.data.get('trabajador')
        try:
            produccion = ProduccionTrabajador.objects.get(trabajador_id=worker_id)
        except ProduccionTrabajador.DoesNotExist:
            logger.error(f'ProduccionTrabajadorAPIView PUT: producción para trabajador {worker_id} no encontrada')
            return Response({'message': 'Producción no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ProduccionTrabajadorSerializer(produccion, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        logger.error(f'ProduccionTrabajadorAPIView PUT: datos inválidos: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ==============================================================================
# VARIABLES DROPDOWN INFORME PAGO
# ==============================================================================

class VariablesDropDownInformePagoAPIView(BaseAPIView):

    def get(self, request, format=None):
        holding_id = request.query_params.get('holding')
        if not holding_id:
            return Response({'error': 'El parámetro holding es necesario'}, status=status.HTTP_400_BAD_REQUEST)

        fundos = CamposClientes.objects.filter(holding_id=holding_id)
        supervisores = Supervisores.objects.filter(holding_id=holding_id)
        casas = CasasTrabajadores.objects.filter(holding_id=holding_id)

        return Response({
            'fundos': CampoClienteDropdownPagoSerializer(fundos, many=True).data,
            'supervisores': SupervisorDropdownPagoSerializer(supervisores, many=True).data,
            'casas': CasaTrabajadorDropdownPagoSerializer(casas, many=True).data,
        })


# ==============================================================================
# INFORME PAGO GENERAR
# ==============================================================================

class InformePagoGenerarAPIView(BaseAPIView):

    def post(self, request, format=None):
        holding_id = request.data.get('holding')
        fecha_inicio = request.data.get('fecha_inicio')
        fecha_fin = request.data.get('fecha_fin')

        if not all([holding_id, fecha_inicio, fecha_fin]):
            return Response({'error': 'Holding ID y rango de fechas son requeridos'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            query = ProduccionTrabajador.objects.filter(
                holding_id=holding_id,
                hora_fecha_ingreso_produccion__range=[fecha_inicio, fecha_fin]
            ).select_related('trabajador', 'labor', 'folio')

            casa_id = request.data.get('casa_id')
            if casa_id:
                trab_casa = PersonalTrabajadores.objects.filter(casa_id=casa_id).values_list('id', flat=True)
                query = query.filter(trabajador_id__in=trab_casa)

            supervisor_id = request.data.get('supervisor_id')
            if supervisor_id:
                trab_supervisor = Supervisores.objects.get(id=supervisor_id).trabajadores.values_list('id', flat=True)
                query = query.filter(trabajador_id__in=trab_supervisor)

            fundo_id = request.data.get('fundo_id')
            if fundo_id:
                trab_fundo = PersonalTrabajadores.objects.filter(fundo_id=fundo_id).values_list('trabajador_id', flat=True)
                query = query.filter(trabajador_id__in=trab_fundo)

            serializer = ProduccionInformePagoDetalleSerializer(query, many=True)
            total_pago = sum(item['valor_total'] for item in serializer.data)

            logger.debug(f'InformePagoGenerarAPIView POST: {len(serializer.data)} registros, total={total_pago}')
            return Response({
                'producciones': serializer.data,
                'resumen': {'total_pago': total_pago, 'total_registros': len(serializer.data)}
            })

        except Exception as e:
            logger.error(f'InformePagoGenerarAPIView POST: error: {e}', exc_info=True)
            return Response({'error': f'Error al generar el informe: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==============================================================================
# INFORME PAGO CSV
# ==============================================================================

class InformePagoCSVAPIView(BaseAPIView):

    def post(self, request, format=None):
        holding_id = request.data.get('holding')
        fecha_inicio = request.data.get('fecha_inicio')
        fecha_fin = request.data.get('fecha_fin')

        if not all([holding_id, fecha_inicio, fecha_fin]):
            return Response({'error': 'Holding ID y rango de fechas son requeridos'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            query = ProduccionTrabajador.objects.filter(
                holding_id=holding_id,
                hora_fecha_ingreso_produccion__range=[fecha_inicio, fecha_fin]
            ).select_related('trabajador', 'labor', 'folio').order_by('trabajador__id', 'hora_fecha_ingreso_produccion')

            casa_id = request.data.get('casa_id')
            if casa_id:
                trab_casa = PersonalTrabajadores.objects.filter(casa_id=casa_id).values_list('id', flat=True)
                query = query.filter(trabajador_id__in=trab_casa)

            supervisor_id = request.data.get('supervisor_id')
            if supervisor_id:
                trab_supervisor = Supervisores.objects.get(id=supervisor_id).trabajadores.values_list('id', flat=True)
                query = query.filter(trabajador_id__in=trab_supervisor)

            fundo_id = request.data.get('fundo_id')
            if fundo_id:
                trab_fundo = PersonalTrabajadores.objects.filter(fundo_id=fundo_id).values_list('trabajador_id', flat=True)
                query = query.filter(trabajador_id__in=trab_fundo)

            serializer = ProduccionCSVSerializer(query, many=True)
            logger.debug(f'InformePagoCSVAPIView POST: {len(serializer.data)} registros')
            return Response({'producciones': serializer.data, 'fecha_inicio': fecha_inicio, 'fecha_fin': fecha_fin})

        except Exception as e:
            logger.error(f'InformePagoCSVAPIView POST: error: {e}', exc_info=True)
            return Response({'error': f'Error al generar los datos para CSV: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)