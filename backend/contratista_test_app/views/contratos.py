import io
import os
import re
import csv
import json
import logging
from datetime import date, datetime, timedelta

from django.shortcuts import get_object_or_404
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from django.conf import settings
from django.core.files.base import ContentFile
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response

from .base import BaseAPIView
from ..models import (
    CasasTrabajadores,
    ChoferesTransporte,
    ContratoTrabajador,
    ContratoVariables,
    EmpresasTransporte,
    FolioComercial,
    PersonalTrabajadores,
    RegistroCasaTrabajador,
    Sociedad,
    SupervisorTrabajadorHistorial,
    Supervisores,
    VehiculosTransporte,
    Holding,
    FirmaOrganizacion,
    TrabajadorTransporteHistorial,
    Horarios,
    ContratoAsociadoTrabajador,
    Parametro,
)
from ..serializers import (
    ContratoTrabajadorSerializer,
    FolioComercialPreContratacionSerializer,
)

logger = logging.getLogger('contratista_test_app')
def slugify_nombre(nombre):
    return re.sub(r'[^a-z0-9]', '_', nombre.lower().strip())

# ==============================================================================
# DOCUMENTO VARIABLES NATIVAS
# ==============================================================================
class DocumentoVariablesNativasAPIView(BaseAPIView):
    
    def get(self, request, documento_id=None, *args, **kwargs):
        try:
            if documento_id:
                # Obtener documento específico
                documento = get_object_or_404(ContratoVariables, id=documento_id)
                
                return Response({
                    'id': documento.id,
                    'nombre': documento.nombre,
                    'tipo': documento.tipo,
                    'archivo_pdf_url': request.build_absolute_uri(documento.archivo_pdf.url),
                    'variables': documento.variables,
                    'fecha_creacion': documento.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S'),
                    'activo': documento.activo
                })
            else:
                # Otherwise, list all documents for the current user's holding
                documentos = ContratoVariables.objects.filter(holding=request.user.holding)
                
                # Filtrar por tipo si se proporciona
                tipo = request.GET.get('tipo')
                if tipo:
                    documentos = documentos.filter(tipo=tipo)
                
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
                
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request, *args, **kwargs):
        action = request.data.get('action', 'create')
        
        if action == 'generar_prueba':
            return self._generar_pdf_prueba(request)
        else:
            return self._crear_documento(request)
    
    def put(self, request, documento_id, *args, **kwargs):
        return self._actualizar_documento(request, documento_id)
    
    def delete(self, request, documento_id, *args, **kwargs):
        try:
            documento = get_object_or_404(ContratoVariables, id=documento_id)
            
            if documento.holding != request.user.holding:
                return Response(
                    {"error": "No tienes permisos para eliminar este documento"}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            nombre = documento.nombre
            documento.delete()
            
            return Response({
                "mensaje": f"Documento '{nombre}' eliminado exitosamente"
            })
            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _normalizar_pdf_a_carta(self, pdf_file):
        import fitz
        import io

        TARGET_WIDTH  = 612.0
        TARGET_HEIGHT = 792.0
        TOLERANCE     = 1.0  # puntos

        if hasattr(pdf_file, 'read'):
            pdf_file.seek(0)
            pdf_bytes = pdf_file.read()
        else:
            with open(pdf_file, "rb") as f:
                pdf_bytes = f.read()

        # ── FAST PATH: si todas las páginas ya son carta, devolver sin procesar ──
        doc_check = fitz.open(stream=pdf_bytes, filetype="pdf")
        todas_carta = all(
            abs(page.rect.width  - TARGET_WIDTH)  < TOLERANCE and
            abs(page.rect.height - TARGET_HEIGHT) < TOLERANCE
            for page in doc_check
        )
        doc_check.close()

        if todas_carta:
            return io.BytesIO(pdf_bytes)  # cero procesamiento, cero memoria extra

        # ── SLOW PATH: normalizar páginas que no son carta ────────────────────────
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        output_doc = fitz.open()

        for page_num in range(len(doc)):
            page = doc[page_num]
            rect = page.rect
            original_width  = rect.width
            original_height = rect.height

            temp_doc = fitz.open()
            temp_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
            temp_page = temp_doc[0]

            new_page = output_doc.new_page(width=TARGET_WIDTH, height=TARGET_HEIGHT)

            scale        = min(TARGET_WIDTH / original_width, TARGET_HEIGHT / original_height)
            scaled_width = original_width  * scale
            scaled_height= original_height * scale
            offset_x     = (TARGET_WIDTH  - scaled_width)  / 2
            offset_y     = (TARGET_HEIGHT - scaled_height) / 2

            dest_rect = fitz.Rect(offset_x, offset_y, offset_x + scaled_width, offset_y + scaled_height)
            new_page.show_pdf_page(dest_rect, temp_doc, 0, clip=temp_page.rect)
            temp_doc.close()

        output_bytes = output_doc.tobytes(garbage=4, deflate=True, clean=True)
        doc.close()
        output_doc.close()

        return io.BytesIO(output_bytes)
    
    def _crear_documento(self, request):
        """Crear documento con variables posicionadas (soporta merge de PDFs)"""
        try:
            from pypdf import PdfWriter, PdfReader  # ✅ Actualizado
            from django.core.files.base import ContentFile
            import io
            
            nombre = request.data.get('nombre', 'Documento sin nombre')
            tipo = request.data.get('tipo', 'CHILENO')
            requiere_merge = request.data.get('requiere_merge', 'false') == 'true'
            
            # ========== MANEJO DE PDF (SIMPLE O FUSIONADO) ==========
            if requiere_merge:
                # Fusionar múltiples PDFs
                num_partes = int(request.data.get('num_partes', 1))
                print(f"🔀 Fusionando {num_partes} PDFs...")
                
                writer = PdfWriter()  # ✅ PdfWriter en lugar de PdfMerger
                
                # ⭐ Normalizar cada parte ANTES de fusionar
                for i in range(num_partes):
                    parte_file = request.FILES.get(f'pdf_parte_{i}')
                    if parte_file:
                        print(f"  📄 Parte {i+1}: {parte_file.size} bytes")
                        
                        # Normalizar a 612x792 con PyMuPDF
                        parte_normalizada = self._normalizar_pdf_a_carta(parte_file)
                        
                        # ✅ Agregar páginas con PdfWriter
                        reader = PdfReader(parte_normalizada)
                        for page in reader.pages:
                            writer.add_page(page)
                    else:
                        print(f"  ⚠️ No se encontró pdf_parte_{i}")
                
                # Crear archivo fusionado en memoria
                merged_buffer = io.BytesIO()
                writer.write(merged_buffer)  # ✅ Sin close()
                merged_buffer.seek(0)
                
                print(f"✅ PDF fusionado: {len(merged_buffer.getvalue())} bytes")
                
                # Crear archivo Django desde el buffer
                nombre_archivo = f"{nombre.lower().replace(' ', '_')}.pdf"
                pdf_file = ContentFile(merged_buffer.read(), name=nombre_archivo)
            else:
                # ⭐ Normalizar archivo único
                pdf_file_original = request.FILES.get('archivo_pdf')
                
                if not pdf_file_original:
                    return Response({
                        "error": "El archivo PDF es obligatorio"
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                if pdf_file_original.size == 0:
                    return Response({
                        "error": "El archivo PDF está vacío"
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Normalizar a 612x792 con PyMuPDF
                pdf_normalizado = self._normalizar_pdf_a_carta(pdf_file_original)
                
                # Convertir a ContentFile para Django
                nombre_archivo = pdf_file_original.name
                pdf_file = ContentFile(pdf_normalizado.read(), name=nombre_archivo)
            
            # ========== PROCESAR VARIABLES ==========
            variables_data = request.data.get('variables')
            if isinstance(variables_data, str):
                variables_json = json.loads(variables_data)
            else:
                variables_json = variables_data or []
            
            # Validar estructura de variables
            for variable in variables_json:
                if 'nombre' not in variable:
                    return Response(
                        {"error": "Todas las variables deben tener un nombre"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                if 'ubicaciones' not in variable:
                    return Response(
                        {"error": "Todas las variables deben tener ubicaciones"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # ========== CREAR DOCUMENTO ==========
            documento = ContratoVariables.objects.create(
                holding=request.user.holding,
                nombre=nombre,
                tipo=tipo,
                archivo_pdf=pdf_file,
                variables=variables_json
            )
            
            print(f"✅ Documento guardado: ID {documento.id}, {len(variables_json)} variables, PDF normalizado a 612x792 con PyMuPDF")
            
            return Response({
                "id": documento.id,
                "mensaje": "Documento guardado exitosamente (PDF normalizado a 612x792)",
                "num_paginas": num_partes if requiere_merge else 1
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            print(f"❌ Error al guardar el documento: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response({
                "error": f"Error al guardar el documento: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _actualizar_documento(self, request, documento_id):
        """Actualizar variables de un documento existente"""
        try:
            documento = get_object_or_404(ContratoVariables, id=documento_id)
            
            if documento.holding != request.user.holding:
                return Response(
                    {"error": "No tienes permisos para modificar este documento"}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            if 'variables' in request.data:
                variables_data = request.data['variables']
                
                if isinstance(variables_data, str):
                    try:
                        variables_json = json.loads(variables_data)
                    except json.JSONDecodeError:
                        return Response(
                            {"error": "El formato de variables no es válido"}, 
                            status=status.HTTP_400_BAD_REQUEST
                        )
                else:
                    variables_json = variables_data
                
                documento.variables = variables_json
                documento.save()
                
                return Response({
                    "mensaje": "Variables actualizadas exitosamente",
                    "documento_id": documento.id,
                    "variables_count": len(variables_json)
                })
            else:
                return Response({
                    "error": "No se proporcionaron variables para actualizar"
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _generar_pdf_prueba(self, request):
        """Generar PDF con datos de prueba EN MEMORIA"""
        try:
            documento_id = request.data.get('documento_id')
            datos_variables = request.data.get('datos_variables', {})
            debug = request.data.get('debug', False)
            
            if not documento_id:
                return Response({
                    "error": "Se requiere documento_id"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            documento = get_object_or_404(ContratoVariables, id=documento_id)
            
            # Generar PDF en memoria
            pdf_buffer = self._generar_documento_coordenadas_nativas(
                documento_id, 
                datos_variables, 
                debug=debug
            )
            
            # Retornar PDF directamente como HttpResponse
            response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = 'inline; filename="vista_previa.pdf"'
            return response
            
        except Exception as e:
            return Response({
                "error": f"Error al generar PDF de prueba: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _generar_documento_coordenadas_nativas(self, documento_id, datos_variables, debug=False):
        import fitz
        import io
        import os
        import re
        from django.conf import settings

        def slugify_nombre(nombre):
            return re.sub(r'[^a-z0-9]', '_', nombre.lower().strip())

        documento = ContratoVariables.objects.get(id=documento_id)
        input_pdf_path = documento.archivo_pdf.path

        BASE_FONT_SIZE = 9
        OFFSET_X = -8

        campos_centrados = [
            'rut', 'dni', 'nic', 'estado_civil',
            'fecha_nacimiento', 'fecha_emision',
            'fecha_ingreso', 'fecha_inicio_contrato', 'fecha_termino'
        ]

        variables_por_pagina = {}
        for variable_data in documento.variables:
            nombre_variable = variable_data.get('nombre')
            for ubicacion in variable_data.get('ubicaciones', []):
                pagina = ubicacion.get('pagina', 1)
                if pagina not in variables_por_pagina:
                    variables_por_pagina[pagina] = []
                variables_por_pagina[pagina].append({
                    'nombre': nombre_variable,
                    'posX': ubicacion.get('posX', 0),
                    'posY': ubicacion.get('posY', 0),
                    'width': ubicacion.get('width'),
                    'height': ubicacion.get('height')
                })

        holding = documento.holding

        # Cargar firmas y huellas de organización (firma_empleador, firma_gerente, huella_empleador, etc.)
        firmas_org = {
            f"{f.tipo}_{slugify_nombre(f.nombre)}": f.imagen.path
            for f in FirmaOrganizacion.objects.filter(holding=holding)
            if f.imagen and os.path.exists(f.imagen.path)
        }

        trabajador = None
        if 'trabajador_id' in datos_variables:
            try:
                from ..models import PersonalTrabajadores
                trabajador = PersonalTrabajadores.objects.get(id=datos_variables['trabajador_id'])
            except PersonalTrabajadores.DoesNotExist:
                pass

        doc = fitz.open(input_pdf_path)

        for page_num in range(len(doc)):
            ui_page_num = page_num + 1
            if ui_page_num not in variables_por_pagina:
                continue

            page = doc[page_num]

            for var_data in variables_por_pagina[ui_page_num]:
                nombre_variable = var_data['nombre']
                x_nativo = var_data['posX']
                y_nativo = var_data['posY']

                # Firmas y huellas de organización (dinámicas)
                if nombre_variable in firmas_org:
                    path = firmas_org[nombre_variable]
                    w = var_data.get('width') or (100 if nombre_variable.startswith('firma') else 80)
                    h = var_data.get('height') or (40 if nombre_variable.startswith('firma') else 100)
                    x_img = x_nativo + OFFSET_X
                    rect = fitz.Rect(x_img, y_nativo, x_img + w, y_nativo + h)
                    page.insert_image(rect, filename=path, keep_proportion=True)
                    continue

                # Firma del trabajador (placeholder o real)
                elif nombre_variable == 'firma':
                    if trabajador and bool(getattr(trabajador, 'firma', None)):
                        firma_path = trabajador.firma.path
                    else:
                        firma_path = os.path.join(settings.MEDIA_ROOT, 'firma_trabajador_placeholder.png')
                    if os.path.exists(firma_path):
                        w = var_data.get('width') or 100
                        h = var_data.get('height') or 40
                        x_img = x_nativo + OFFSET_X
                        rect = fitz.Rect(x_img, y_nativo, x_img + w, y_nativo + h)
                        page.insert_image(rect, filename=firma_path, keep_proportion=True)
                    continue

                # Huella del trabajador (placeholder o real)
                elif nombre_variable == 'huella':
                    if trabajador and bool(getattr(trabajador, 'huella_digital', None)):
                        huella_path = trabajador.huella_digital.path
                    else:
                        huella_path = os.path.join(settings.MEDIA_ROOT, 'huella_trabajador_placeholder.png')
                    if os.path.exists(huella_path):
                        w = var_data.get('width') or 80
                        h = var_data.get('height') or 100
                        x_img = x_nativo + OFFSET_X
                        rect = fitz.Rect(x_img, y_nativo, x_img + w, y_nativo + h)
                        page.insert_image(rect, filename=huella_path, keep_proportion=True)
                    continue

                # Variables de texto
                else:
                    valor = datos_variables.get(nombre_variable, '')
                    if valor:
                        x_text = x_nativo + OFFSET_X
                        y_text = y_nativo + BASE_FONT_SIZE

                        if nombre_variable in campos_centrados:
                            tw = fitz.get_text_length(str(valor), fontname="helv", fontsize=BASE_FONT_SIZE)
                            x_text = x_text - tw / 2

                        page.insert_text(
                            fitz.Point(x_text, y_text),
                            str(valor),
                            fontsize=BASE_FONT_SIZE,
                            fontname="helv",
                            color=(0, 0, 0)
                        )

        output_buffer = io.BytesIO()
        doc.save(output_buffer, garbage=4, deflate=True, clean=True)
        output_buffer.seek(0)
        doc.close()
        return output_buffer

# ==============================================================================
# GENERAR TXT BANCO
# ==============================================================================
class GenerarTxtBancoAPIView(BaseAPIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, format=None):
        try:
            csv_file = request.FILES.get('csv_file')
            nombre_base = re.sub(r'[^a-zA-Z0-9_-]', '', request.POST.get('nombre_archivo', 'transferencias')) or 'transferencias'

            if not csv_file:
                return Response({'success': False, 'message': 'No se recibió archivo CSV'}, status=status.HTTP_400_BAD_REQUEST)
            if not csv_file.name.lower().endswith('.csv'):
                return Response({'success': False, 'message': 'El archivo debe ser formato CSV'}, status=status.HTTP_400_BAD_REQUEST)
            if csv_file.size > 5 * 1024 * 1024:
                return Response({'success': False, 'message': 'El archivo es demasiado grande. Máximo 5MB'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                decoded_file = csv_file.read().decode('utf-8-sig')
                io_string = io.StringIO(decoded_file)
                reader = csv.reader(io_string, delimiter=';')
                registros = []
                for row_num, row in enumerate(reader, start=1):
                    if len(row) < 14:
                        return Response({
                            'success': False,
                            'message': f'Línea {row_num}: formato inválido. Se esperan 14 columnas, se encontraron {len(row)}',
                        }, status=status.HTTP_400_BAD_REQUEST)
                    registros.append(row)
                if not registros:
                    return Response({'success': False, 'message': 'El archivo CSV está vacío'}, status=status.HTTP_400_BAD_REQUEST)
            except UnicodeDecodeError:
                return Response({'success': False, 'message': 'Error de codificación. El archivo debe estar en UTF-8'}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({'success': False, 'message': f'Error al leer el archivo CSV: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

            archivos_generados = []
            total_registros = len(registros)

            for i in range(0, total_registros, 100):
                grupo = registros[i:i + 100]
                numero_archivo = (i // 100) + 1
                contenido_txt = self._generar_contenido_txt(grupo)
                if contenido_txt is None:
                    return Response({
                        'success': False,
                        'message': f'Error al formatear los datos del grupo {numero_archivo}',
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                archivos_generados.append({
                    'nombre': f'{nombre_base}_{numero_archivo}.txt',
                    'contenido': contenido_txt,
                    'numero_archivo': numero_archivo,
                    'total_lineas': len(grupo),
                })

            logger.debug(f'GenerarTxtBancoAPIView POST: {total_registros} registros → {len(archivos_generados)} archivos')
            return Response({
                'success': True,
                'total_registros': total_registros,
                'total_archivos': len(archivos_generados),
                'archivos': archivos_generados,
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error('GenerarTxtBancoAPIView POST: error inesperado', exc_info=True)
            return Response({'success': False, 'message': f'Error interno del servidor: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _generar_contenido_txt(self, registros):
        try:
            lineas = []
            for registro in registros:
                tipo_operacion       = registro[0].strip()
                rut_cliente          = registro[1].strip()
                cuenta_cargo         = registro[2].strip()
                rut_beneficiario     = registro[3].strip()
                nombre_beneficiario  = registro[4].strip()
                cuenta_beneficiario  = registro[5].strip()
                rut_banco_beneficiario = registro[6].strip()
                monto                = registro[7].strip()
                motivo               = registro[9].strip()
                notif_email_valor    = registro[10].strip()
                asunto_email         = registro[11].strip()
                email                = registro[12].strip()
                tipo_cuenta          = registro[13].strip()

                tipo_op_fmt      = self._format_text(tipo_operacion, 3)
                rut_cliente_fmt  = self._format_rut(rut_cliente, 10)
                cuenta_cargo_fmt = self._format_numeric(cuenta_cargo, 12)
                rut_benef_fmt    = self._format_rut(rut_beneficiario, 10)
                nombre_fmt       = self._format_text(nombre_beneficiario, 30)
                cuenta_benef_fmt = self._format_text(cuenta_beneficiario, 18)
                rut_banco_fmt    = self._format_rut(rut_banco_beneficiario, 10)
                monto_fmt        = self._format_numeric(monto, 11)
                monto_fmt        = self._format_numeric(monto, 11)
                abono_inmediato  = ' '
                motivo_fmt       = self._format_text(motivo, 30)
                notif_email      = notif_email_valor if notif_email_valor in ['0', '1'] else '1'
                asunto_fmt       = self._format_text(asunto_email, 30)
                email_fmt        = self._format_text(email, 50)
                tipo_cuenta_fmt  = self._format_text(tipo_cuenta, 3)

                linea = (
                    tipo_op_fmt      +
                    rut_cliente_fmt  +
                    cuenta_cargo_fmt +
                    rut_benef_fmt    +
                    nombre_fmt       +
                    cuenta_benef_fmt +
                    rut_banco_fmt    +
                    monto_fmt        +
                    abono_inmediato  +
                    motivo_fmt       +
                    notif_email      +
                    asunto_fmt       +
                    email_fmt        +
                    tipo_cuenta_fmt
                )

                if len(linea) != 219:
                    logger.error(f'GenerarTxtBancoAPIView _generar_contenido_txt: longitud incorrecta {len(linea)} caracteres')
                    return None
                lineas.append(linea)

            return '\n'.join(lineas)
        except Exception as e:
            logger.error('GenerarTxtBancoAPIView _generar_contenido_txt: error', exc_info=True)
            return None

    def _format_rut(self, value, length):
        value_str = str(value).upper().strip()
        tiene_k = value_str.endswith('K')
        if tiene_k:
            cleaned = ''.join(c for c in value_str[:-1] if c.isdigit())
            formatted = cleaned.zfill(length - 1) + 'K'
        else:
            cleaned = ''.join(c for c in value_str if c.isdigit())
            formatted = cleaned.zfill(length)
        return formatted[-length:]

    def _format_numeric(self, value, length):
        cleaned = ''.join(c for c in str(value) if c.isdigit())
        return cleaned.zfill(length)[-length:]

    def _format_text(self, value, length):
        return str(value).upper().strip().ljust(length)[:length]

# ==============================================================================
# GENERAR DOCUMENTOS MASIVO
# ==============================================================================
class GenerarDocumentosMasivoAPIView(BaseAPIView):

    def post(self, request, *args, **kwargs):
        try:
            documento_id         = request.data.get('documento_id')
            trabajador_ids       = request.data.get('trabajador_ids', [])
            fecha_emision        = request.data.get('fecha_emision')
            sociedad_id          = request.data.get('sociedad_id')
            marcar_como_generado = request.data.get('marcar_como_generado', False)

            if not documento_id:
                return Response({'error': 'Se requiere documento_id'}, status=status.HTTP_400_BAD_REQUEST)
            if not trabajador_ids:
                return Response({'error': 'Se requiere al menos un trabajador_id'}, status=status.HTTP_400_BAD_REQUEST)

            from django.shortcuts import get_object_or_404
            documento = get_object_or_404(ContratoVariables, id=documento_id)
            if documento.holding != request.user.holding:
                return Response({'error': 'No tienes permisos para usar este documento'}, status=status.HTTP_403_FORBIDDEN)

            urls_generadas = []
            errores = []

            for trabajador_id in trabajador_ids:
                try:
                    trabajador = PersonalTrabajadores.objects.get(id=trabajador_id, holding=request.user.holding)
                    datos_variables = self._mapear_datos_trabajador(trabajador, fecha_emision, sociedad_id)
                    datos_variables['trabajador_id'] = trabajador.id
                    pdf_buffer = self._generar_documento_coordenadas_nativas(documento_id, datos_variables, debug=False)
                    pdf_url = self._guardar_contrato_generado(pdf_buffer, trabajador, documento, request, marcar_como_generado)
                    urls_generadas.append({
                        'trabajador_id': trabajador.id,
                        'trabajador_nombre': f'{trabajador.nombres} {trabajador.apellidos}',
                        'url': pdf_url,
                        'success': True,
                        'marcado_como_generado': marcar_como_generado,
                    })
                except PersonalTrabajadores.DoesNotExist:
                    errores.append({'trabajador_id': trabajador_id, 'error': 'Trabajador no encontrado'})
                except Exception as e:
                    logger.error(f'GenerarDocumentosMasivoAPIView POST: error en trabajador {trabajador_id}', exc_info=True)
                    errores.append({'trabajador_id': trabajador_id, 'error': str(e)})

            logger.debug(f'GenerarDocumentosMasivoAPIView POST: {len(urls_generadas)} exitosos, {len(errores)} errores')
            return Response({
                'mensaje': f'Se generaron {len(urls_generadas)} contratos exitosamente',
                'contratos': urls_generadas,
                'errores': errores,
                'total_exitosos': len(urls_generadas),
                'total_errores': len(errores),
                'marcados_como_generados': marcar_como_generado,
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error('GenerarDocumentosMasivoAPIView POST: error inesperado', exc_info=True)
            return Response({'error': f'Error al generar contratos: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _guardar_contrato_generado(self, pdf_buffer, trabajador, documento, request, marcar_como_generado=False):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        rut_limpio = (trabajador.rut or trabajador.dni or str(trabajador.id)).replace('.', '').replace('-', '')
        nombre_archivo = f'contrato_{documento.tipo}_{rut_limpio}_{timestamp}.pdf'
        ruta_relativa = f'contratos_generados/{trabajador.holding.id}/{documento.tipo.lower()}/'
        ruta_completa = os.path.join(settings.MEDIA_ROOT, ruta_relativa)
        os.makedirs(ruta_completa, exist_ok=True)
        ruta_archivo = os.path.join(ruta_completa, nombre_archivo)
        with open(ruta_archivo, 'wb') as f:
            f.write(pdf_buffer.getvalue())
        url_relativa = f'{ruta_relativa}{nombre_archivo}'.replace('\\', '/')
        url_absoluta = request.build_absolute_uri(f'{settings.MEDIA_URL}{url_relativa}')
        logger.debug(f'GenerarDocumentosMasivoAPIView _guardar_contrato_generado: {ruta_archivo}')

        if marcar_como_generado:
            try:
                contrato = ContratoTrabajador.objects.filter(
                    trabajador=trabajador,
                    holding=trabajador.holding,
                ).latest('fecha_inicio_contrato')
                contrato.contrato_generado = True
                contrato.save(update_fields=['contrato_generado'])
                logger.debug(f'GenerarDocumentosMasivoAPIView _guardar_contrato_generado: contrato {contrato.id} marcado como generado')
            except ContratoTrabajador.DoesNotExist:
                logger.error(f'GenerarDocumentosMasivoAPIView _guardar_contrato_generado: trabajador {trabajador.id} sin contrato registrado')

        return url_absoluta

    def _mapear_datos_trabajador(self, trabajador, fecha_emision=None, sociedad_id=None):
        def formatear_fecha(fecha):
            if not fecha:
                return ''
            return fecha if isinstance(fecha, str) else fecha.strftime('%d/%m/%Y')

        def formatear_rut(rut):
            if not rut:
                return ''
            rut = rut.replace('.', '').replace('-', '')
            if len(rut) < 2:
                return ''
            rut_num = rut[:-1]
            dv = rut[-1]
            rut_formateado = ''
            for i, digit in enumerate(reversed(rut_num)):
                if i > 0 and i % 3 == 0:
                    rut_formateado = '.' + rut_formateado
                rut_formateado = digit + rut_formateado
            return f'{rut_formateado}-{dv}'

        contrato_activo = trabajador.contratos.filter(
            fecha_inicio_contrato__lte=date.today()
        ).filter(
            Q(fecha_termino_contrato__gte=date.today()) |
            Q(fecha_termino_contrato__isnull=True)
        ).order_by('-fecha_inicio_contrato').first()

        if fecha_emision:
            try:
                fecha_emision_formateada = formatear_fecha(datetime.strptime(fecha_emision, '%Y-%m-%d').date())
            except ValueError:
                fecha_emision_formateada = formatear_fecha(date.today())
        else:
            fecha_emision_formateada = formatear_fecha(date.today())

        sociedad_nombre = ''
        if sociedad_id:
            try:
                sociedad_nombre = Sociedad.objects.get(id=sociedad_id).nombre
            except Sociedad.DoesNotExist:
                logger.error(f'GenerarDocumentosMasivoAPIView _mapear_datos_trabajador: sociedad {sociedad_id} no encontrada')

        return {
            'fecha_emision':          fecha_emision_formateada,
            'fecha_ingreso':          formatear_fecha(trabajador.fecha_ingreso),
            'fecha_inicio_contrato':  formatear_fecha(contrato_activo.fecha_inicio_contrato) if contrato_activo else '',
            'fecha_termino':          formatear_fecha(contrato_activo.fecha_termino_contrato) if contrato_activo else '',
            'nombre_completo':        f"{trabajador.nombres or ''} {trabajador.apellidos or ''}".strip(),
            'rut':                    formatear_rut(trabajador.rut) if trabajador.rut else '',
            'dni':                    trabajador.dni or '',
            'nic':                    trabajador.nic or '',
            'nacionalidad':           trabajador.nacionalidad or '',
            'fecha_nacimiento':       formatear_fecha(trabajador.fecha_nacimiento),
            'estado_civil':           trabajador.estado_civil or '',
            'domicilio':              trabajador.direccion or '',
            'telefono':               trabajador.telefono or '',
            'correo':                 trabajador.correo or '',
            'lugar_trabajo':          contrato_activo.fundo.nombre_campo if (contrato_activo and contrato_activo.fundo) else '',
            'cargo':                  trabajador.cargo.nombre if trabajador.cargo else '',
            'area':                   trabajador.area.nombre if trabajador.area else '',
            'horario':                contrato_activo.horario.nombre if (contrato_activo and contrato_activo.horario) else '',
            'sociedad':               sociedad_nombre,
            'nombre_cliente':         contrato_activo.folio_comercial.cliente.nombre if (contrato_activo and contrato_activo.folio_comercial and contrato_activo.folio_comercial.cliente) else '',
            'nombre_campo':           contrato_activo.fundo.nombre_campo if (contrato_activo and contrato_activo.fundo) else '',
            'afp':                    trabajador.afp.nombre if trabajador.afp else '',
            'salud':                  trabajador.salud.nombre if trabajador.salud else '',
            'tipo_pago':              'Transferencia bancaria',
            'banco':                  trabajador.banco.nombre if trabajador.banco else '',
            'tipo_cuenta':            trabajador.tipo_cuenta_bancaria or '',
            'numero_cuenta':          str(trabajador.numero_cuenta) if trabajador.numero_cuenta else '',
            'elementos_proteccion':   '',
            'contacto_emergencia_nombre':   '',
            'contacto_emergencia_telefono': '',
            'huella':                 '[HUELLA DIGITAL]',
        }

    def _generar_documento_coordenadas_nativas(self, documento_id, datos_variables, debug=False):
        documento = ContratoVariables.objects.get(id=documento_id)
        input_pdf_path = documento.archivo_pdf.path
        reader = PdfReader(open(input_pdf_path, 'rb'))

        BASE_FONT_SIZE = 9
        BASE_OFFSET_X = -8
        BASE_OFFSET_Y = -15.2
        FONT_BASELINE = BASE_FONT_SIZE * 0.3
        campos_centrados = [
            'rut', 'dni', 'nic', 'estado_civil',
            'fecha_nacimiento', 'fecha_emision',
            'fecha_ingreso', 'fecha_inicio_contrato', 'fecha_termino',
        ]

        variables_por_pagina = {}
        for variable_data in documento.variables:
            nombre_variable = variable_data.get('nombre')
            for ubicacion in variable_data.get('ubicaciones', []):
                pagina = ubicacion.get('pagina', 1)
                if pagina not in variables_por_pagina:
                    variables_por_pagina[pagina] = []
                variables_por_pagina[pagina].append({
                    'nombre': nombre_variable,
                    'posX':   ubicacion.get('posX', 0),
                    'posY':   ubicacion.get('posY', 0),
                    'width':  ubicacion.get('width'),
                    'height': ubicacion.get('height'),
                })

        holding = documento.holding
        firma_empleador_disponible = bool(holding.firma_empleador)
        trabajador = None
        if 'trabajador_id' in datos_variables:
            try:
                trabajador = PersonalTrabajadores.objects.get(id=datos_variables['trabajador_id'])
            except PersonalTrabajadores.DoesNotExist:
                logger.error(f'GenerarDocumentosMasivoAPIView _generar_documento_coordenadas_nativas: trabajador {datos_variables["trabajador_id"]} no encontrado')

        final_writer = PdfWriter()

        for page_num in range(len(reader.pages)):
            ui_page_num = page_num + 1
            temp_doc_buffer = io.BytesIO()
            temp_doc_writer = PdfWriter()
            original_page = reader.pages[page_num]
            temp_doc_writer.add_page(original_page)
            temp_doc_writer.write(temp_doc_buffer)
            temp_doc_buffer.seek(0)
            temp_doc_reader = PdfReader(temp_doc_buffer)
            isolated_page = temp_doc_reader.pages[0]
            page_width = float(isolated_page.mediabox.width)
            page_height = float(isolated_page.mediabox.height)

            if ui_page_num not in variables_por_pagina:
                final_writer.add_page(isolated_page)
                continue

            overlay_buffer = io.BytesIO()
            can = canvas.Canvas(overlay_buffer, pagesize=(page_width, page_height))
            variables_escritas = 0

            for variable in variables_por_pagina[ui_page_num]:
                nombre = variable['nombre']

                if nombre == 'firma_empleador':
                    if firma_empleador_disponible:
                        try:
                            firma_path = holding.firma_empleador.path
                            if os.path.exists(firma_path):
                                img_width  = variable.get('width', 150)
                                img_height = variable.get('height', 50)
                                pdf_x = variable['posX'] + BASE_OFFSET_X
                                pdf_y = page_height - variable['posY'] + BASE_OFFSET_Y - img_height
                                can.drawImage(firma_path, pdf_x, pdf_y, width=img_width, height=img_height, preserveAspectRatio=True, mask='auto')
                                variables_escritas += 1
                        except Exception as e:
                            logger.error(f'GenerarDocumentosMasivoAPIView _generar_documento_coordenadas_nativas: error insertando firma_empleador', exc_info=True)
                    continue

                elif nombre == 'firma':
                    if trabajador:
                        firma_trabajador_disponible = bool(trabajador.firma and os.path.exists(trabajador.firma.path))
                        if firma_trabajador_disponible:
                            try:
                                img_width  = variable.get('width', 100)
                                img_height = variable.get('height', 40)
                                pdf_x = variable['posX'] + BASE_OFFSET_X
                                pdf_y = page_height - variable['posY'] + BASE_OFFSET_Y - img_height
                                can.drawImage(trabajador.firma.path, pdf_x, pdf_y, width=img_width, height=img_height, preserveAspectRatio=True, mask='auto')
                                variables_escritas += 1
                            except Exception as e:
                                logger.error(f'GenerarDocumentosMasivoAPIView _generar_documento_coordenadas_nativas: error insertando firma trabajador', exc_info=True)
                                pdf_x = variable['posX'] + BASE_OFFSET_X
                                pdf_y = page_height - variable['posY'] + BASE_OFFSET_Y + FONT_BASELINE
                                can.drawString(pdf_x, pdf_y, '[ERROR FIRMA]')
                        else:
                            pdf_x = variable['posX'] + BASE_OFFSET_X
                            pdf_y = page_height - variable['posY'] + BASE_OFFSET_Y + FONT_BASELINE
                            can.drawString(pdf_x, pdf_y, '[FIRMA PENDIENTE]')
                    continue

                elif nombre == 'huella':
                    if trabajador:
                        huella_trabajador_disponible = bool(trabajador.huella_digital and os.path.exists(trabajador.huella_digital.path))
                        if huella_trabajador_disponible:
                            try:
                                img_width  = variable.get('width', 80)
                                img_height = variable.get('height', 100)
                                pdf_x = variable['posX'] + BASE_OFFSET_X
                                pdf_y = page_height - variable['posY'] + BASE_OFFSET_Y - img_height
                                can.drawImage(trabajador.huella_digital.path, pdf_x, pdf_y, width=img_width, height=img_height, preserveAspectRatio=True, mask='auto')
                                variables_escritas += 1
                            except Exception as e:
                                logger.error(f'GenerarDocumentosMasivoAPIView _generar_documento_coordenadas_nativas: error insertando huella trabajador', exc_info=True)
                                pdf_x = variable['posX'] + BASE_OFFSET_X
                                pdf_y = page_height - variable['posY'] + BASE_OFFSET_Y + FONT_BASELINE
                                can.drawString(pdf_x, pdf_y, '[ERROR HUELLA]')
                        else:
                            pdf_x = variable['posX'] + BASE_OFFSET_X
                            pdf_y = page_height - variable['posY'] + BASE_OFFSET_Y + FONT_BASELINE
                            can.drawString(pdf_x, pdf_y, '[HUELLA PENDIENTE]')
                    continue

                if nombre not in datos_variables:
                    continue
                valor = datos_variables[nombre]
                if not valor:
                    continue

                pdf_x = variable['posX'] + BASE_OFFSET_X
                pdf_y = page_height - variable['posY'] + BASE_OFFSET_Y + FONT_BASELINE

                if nombre == 'rut':
                    pdf_x += BASE_OFFSET_X * 0.5
                elif nombre == 'nombre':
                    pdf_x += BASE_OFFSET_X * 0.1

                valor_str = str(valor)
                can.setFont('Helvetica', BASE_FONT_SIZE)
                if nombre in campos_centrados:
                    text_width = can.stringWidth(valor_str, 'Helvetica', BASE_FONT_SIZE)
                    can.drawString(pdf_x - (text_width / 2), pdf_y, valor_str)
                else:
                    can.drawString(pdf_x, pdf_y, valor_str)
                variables_escritas += 1

                if debug:
                    can.saveState()
                    can.setStrokeColorRGB(1, 0, 0)
                    can.setLineWidth(1)
                    can.line(pdf_x - 9, pdf_y, pdf_x + 9, pdf_y)
                    can.line(pdf_x, pdf_y - 9, pdf_x, pdf_y + 9)
                    can.restoreState()

            can.save()
            overlay_buffer.seek(0)
            logger.debug(f'GenerarDocumentosMasivoAPIView _generar_documento_coordenadas_nativas: página {ui_page_num} — {variables_escritas} variables')

            if variables_escritas > 0:
                try:
                    overlay_reader = PdfReader(overlay_buffer)
                    isolated_page.merge_page(overlay_reader.pages[0])
                except Exception as e:
                    logger.error(f'GenerarDocumentosMasivoAPIView _generar_documento_coordenadas_nativas: error en merge página {ui_page_num}', exc_info=True)

            final_writer.add_page(isolated_page)

        output_buffer = io.BytesIO()
        final_writer.write(output_buffer)
        output_buffer.seek(0)
        logger.debug(f'GenerarDocumentosMasivoAPIView _generar_documento_coordenadas_nativas: PDF generado {len(output_buffer.getvalue())} bytes')
        return output_buffer

# ==============================================================================
# LISTAR DOCUMENTOS
# ==============================================================================
class ListarDocumentosAPIView(BaseAPIView):

    def get(self, request, *args, **kwargs):
        try:
            tipo       = request.query_params.get('tipo')
            holding_id = request.query_params.get('holding')

            if not tipo:
                return Response({'error': "Se requiere el parámetro 'tipo' (CHILENO o EXTRANJERO)"}, status=status.HTTP_400_BAD_REQUEST)
            if tipo not in ['CHILENO', 'EXTRANJERO']:
                return Response({'error': "El tipo debe ser 'CHILENO' o 'EXTRANJERO'"}, status=status.HTTP_400_BAD_REQUEST)

            queryset = ContratoVariables.objects.filter(tipo=tipo, activo=True)
            queryset = queryset.filter(holding_id=holding_id) if holding_id else queryset.filter(holding=request.user.holding)

            documentos = [{
                'id': doc.id,
                'nombre': doc.nombre,
                'tipo': doc.tipo,
                'fecha_creacion': doc.fecha_creacion.strftime('%Y-%m-%d'),
                'activo': doc.activo,
                'cantidad_variables': len(doc.variables) if doc.variables else 0,
            } for doc in queryset]

            return Response(documentos, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error('ListarDocumentosAPIView GET: error inesperado', exc_info=True)
            return Response({'error': f'Error al listar documentos: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ==============================================================================
# CONTRATO TRABAJADOR
# ==============================================================================
class ContratoTrabajadorAPIView(BaseAPIView):

    def get(self, request):
        holding_id    = request.query_params.get('holding')
        estado_filtro = request.query_params.get('estado', 'todos')
        trabajador_id = request.query_params.get('trabajador_id')

        if not holding_id:
            return Response({'error': 'holding es requerido'}, status=status.HTTP_400_BAD_REQUEST)

        queryset = ContratoTrabajador.objects.filter(holding_id=holding_id).select_related(
            'trabajador', 'trabajador__sociedad', 'documento', 'cliente', 'fundo', 'horario'
        )
        if trabajador_id:
            queryset = queryset.filter(trabajador_id=trabajador_id)
        if estado_filtro == 'vigente':
            queryset = queryset.filter(fecha_termino_contrato__gte=date.today()) | queryset.filter(fecha_termino_contrato__isnull=True)
        elif estado_filtro == 'vencido':
            queryset = queryset.filter(fecha_termino_contrato__lt=date.today())

        horario_map = {}
        for c in queryset:
            if c.horario:
                h = c.horario
                total_minutos = 0
                dias = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']
                for dia in dias:
                    inicio   = getattr(h, f'{dia}_inicio', None)
                    fin      = getattr(h, f'{dia}_fin', None)
                    colacion = getattr(h, f'{dia}_minutos_colacion', 0) or 0
                    if inicio and fin:
                        mins = (datetime.combine(datetime.today(), fin) - datetime.combine(datetime.today(), inicio)).seconds // 60
                        total_minutos += mins - colacion
                horario_map[c.id] = f"{h.nombre} ({round(total_minutos / 60, 1)}h)"
            else:
                horario_map[c.id] = None

        # Cargar todos los historiales del holding de una sola vez
        todos_historial = SupervisorTrabajadorHistorial.objects.filter(
            holding_id=holding_id
        ).select_related('supervisor__usuario__persona')

        data = ContratoTrabajadorSerializer(queryset, many=True).data

        for contrato in data:
            trab_id          = contrato.get('trabajador')
            fecha_inicio_str = contrato.get('fecha_inicio_contrato')

            try:
                fecha_inicio_contrato = datetime.strptime(str(fecha_inicio_str), '%Y-%m-%d').date()
            except (ValueError, TypeError):
                fecha_inicio_contrato = date.today()

            # Buscar el historial cuyo período cubre la fecha_inicio del contrato
            historial_match = None
            for h in todos_historial:
                if h.trabajador_id != trab_id:
                    continue
                if h.fecha_inicio > fecha_inicio_contrato:
                    continue
                if h.fecha_fin and h.fecha_fin < fecha_inicio_contrato:
                    continue
                # Cubre la fecha: quedarse con el más reciente (fecha_inicio más alta)
                if historial_match is None or h.fecha_inicio > historial_match.fecha_inicio:
                    historial_match = h

            supervisores = []
            if historial_match and historial_match.supervisor:
                p = None
                if historial_match.supervisor.usuario and historial_match.supervisor.usuario.persona:
                    p = historial_match.supervisor.usuario.persona
                nombre = f'{p.nombres} {p.apellidos or ""}'.strip() if p else ''
                supervisores = [{'id': historial_match.supervisor.id, 'nombre': nombre}]

            contrato['supervisores'] = supervisores
            contrato['supervisor']   = supervisores[0] if supervisores else None
            contrato['horario_info'] = horario_map.get(contrato.get('id'))

        return Response(data)
    def post(self, request):
        serializer = ContratoTrabajadorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            contrato = serializer.instance
            if contrato.horario:
                try:
                    from ..models import ContratoHorarioSnapshot
                    horario = contrato.horario
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
                    ContratoHorarioSnapshot.objects.update_or_create(
                        contrato=contrato,
                        defaults={
                            'trabajador': contrato.trabajador,
                            'holding': contrato.holding,
                            'datos': {'nombre': horario.nombre, 'horas_por_dia': horas_por_dia}
                        }
                    )
                except Exception as e:
                    logger.error(f'Error creando snapshot horario: {e}')
            logger.debug(f'ContratoTrabajadorAPIView POST: contrato creado')
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error(f'ContratoTrabajadorAPIView POST: datos inválidos: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        contrato_id = request.data.get('id')
        try:
            contrato = ContratoTrabajador.objects.get(id=contrato_id)
        except ContratoTrabajador.DoesNotExist:
            logger.error(f'ContratoTrabajadorAPIView PUT: contrato {contrato_id} no encontrado')
            return Response({'error': 'Contrato no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ContratoTrabajadorSerializer(contrato, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            contrato = serializer.instance
            if contrato.horario:
                try:
                    from ..models import ContratoHorarioSnapshot
                    horario = contrato.horario
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
                    ContratoHorarioSnapshot.objects.update_or_create(
                        contrato=contrato,
                        defaults={
                            'trabajador': contrato.trabajador,
                            'holding': contrato.holding,
                            'datos': {'nombre': horario.nombre, 'horas_por_dia': horas_por_dia}
                        }
                    )
                except Exception as e:
                    logger.error(f'Error creando snapshot horario: {e}')
            return Response(serializer.data)
        logger.error(f'ContratoTrabajadorAPIView PUT: datos inválidos para contrato {contrato_id}: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'error': 'Se requiere lista de IDs'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Obtener trabajadores afectados antes de borrar
        contratos = ContratoTrabajador.objects.filter(id__in=ids).select_related('trabajador')
        trabajador_ids = [c.trabajador_id for c in contratos]
        
        deleted_count = ContratoTrabajador.objects.filter(id__in=ids).delete()[0]
        
        # Cerrar historiales de los trabajadores afectados
        hoy = date.today()
        TrabajadorTransporteHistorial.objects.filter(
            trabajador_id__in=trabajador_ids, fecha_fin__isnull=True
        ).update(fecha_fin=hoy)
        
        return Response({'mensaje': f'Se eliminaron {deleted_count} contratos', 'eliminados': deleted_count})

    def patch(self, request):
        contrato_id = request.data.get('id')
        if not contrato_id:
            return Response({'error': 'ID de contrato es requerido'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            contrato = ContratoTrabajador.objects.get(id=contrato_id)
        except ContratoTrabajador.DoesNotExist:
            logger.error(f'ContratoTrabajadorAPIView PATCH: contrato {contrato_id} no encontrado')
            return Response({'error': 'Contrato no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        if contrato.fecha_termino_contrato and contrato.fecha_termino_contrato < date.today():
            return Response({'error': 'El contrato ya está vencido'}, status=status.HTTP_400_BAD_REQUEST)

        fecha_termino = request.data.get('fecha_termino_contrato')
        if not fecha_termino:
            return Response({'error': 'fecha_termino_contrato es requerida'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            fecha_termino = date.fromisoformat(fecha_termino)
        except ValueError:
            return Response({'error': 'Formato de fecha inválido, use YYYY-MM-DD'}, status=status.HTTP_400_BAD_REQUEST)
        if fecha_termino < contrato.fecha_inicio_contrato:
            return Response({'error': 'La fecha de término no puede ser anterior a la fecha de inicio'}, status=status.HTTP_400_BAD_REQUEST)
        if fecha_termino > date.today():
            return Response({'error': 'La fecha de término no puede ser posterior a hoy'}, status=status.HTTP_400_BAD_REQUEST)

        contrato.fecha_termino_contrato = fecha_termino
        contrato.save(update_fields=['fecha_termino_contrato'])
        TrabajadorTransporteHistorial.objects.filter(
            trabajador=contrato.trabajador,
            fecha_fin__isnull=True
        ).update(fecha_fin=fecha_termino)

        # También cerrar supervisor y casa si quieres consistencia
        SupervisorTrabajadorHistorial.objects.filter(
            trabajador=contrato.trabajador,
            fecha_fin__isnull=True
        ).update(fecha_fin=fecha_termino)

        RegistroCasaTrabajador.objects.filter(
            trabajador=contrato.trabajador,
            fecha_fin__isnull=True
        ).update(fecha_fin=fecha_termino)
        logger.debug(f'ContratoTrabajadorAPIView PATCH: contrato {contrato_id} terminado con fecha {fecha_termino}')
        return Response({
            'mensaje': 'Contrato terminado exitosamente',
            'contrato_id': contrato.id,
            'fecha_termino': contrato.fecha_termino_contrato.strftime('%Y-%m-%d'),
        })

# ==============================================================================
# CREAR CONTRATO WEB
# ==============================================================================
class CrearContratoWebAPIView(BaseAPIView):

    def get(self, request, format=None):
        try:
            holding_id  = request.query_params.get('holding')
            sociedad_id = request.query_params.get('sociedad_id')
            folio_id    = request.query_params.get('folio_id')

            if not holding_id:
                return Response({'error': 'Holding es requerido'}, status=status.HTTP_400_BAD_REQUEST)

            if not sociedad_id and not folio_id:
                logger.debug(f'CrearContratoWebAPIView GET: datos iniciales para holding {holding_id}')
                sociedades = Sociedad.objects.filter(holding_id=holding_id, estado=True)
                sociedades_data = [{'id': s.id, 'nombre': s.nombre, 'rol_sociedad': s.rol_sociedad} for s in sociedades]

                folios = FolioComercial.objects.filter(holding_id=holding_id, estado=True)
                folios_data = FolioComercialPreContratacionSerializer(folios, many=True).data

                supervisores = Supervisores.objects.filter(holding_id=holding_id).select_related('usuario__persona')
                supervisores_data = [{
                    'id': s.id,
                    'nombre': f"{s.usuario.persona.nombres} {s.usuario.persona.apellidos}" if s.usuario and s.usuario.persona else 'Sin nombre',
                    'rut': s.usuario.rut if s.usuario else None,
                } for s in supervisores]

                transportistas = EmpresasTransporte.objects.filter(holding_id=holding_id).prefetch_related('vehiculostransporte_set__choferestransporte_set')
                transportistas_data = [{
                    'id': t.id,
                    'nombre': t.nombre,
                    'rut': t.rut,
                    'vehiculos': [{
                        'id': v.id, 'tipo': v.tipo, 'marca': v.marca, 'modelo': v.modelo, 'ppu': v.ppu,
                        'choferes': [{'id': c.id, 'nombre': c.nombre, 'rut': c.rut, 'licencia': c.licencia} for c in v.choferestransporte_set.all()],
                    } for v in t.vehiculostransporte_set.all()],
                } for t in transportistas]

                return Response({
                    'sociedades': sociedades_data,
                    'folios': folios_data,
                    'supervisores': supervisores_data,
                    'transportistas': transportistas_data,
                }, status=status.HTTP_200_OK)

            if sociedad_id and folio_id:
                logger.debug(f'CrearContratoWebAPIView GET: trabajadores disponibles sociedad={sociedad_id}, folio={folio_id}')
                try:
                    folio = FolioComercial.objects.get(id=folio_id, holding_id=holding_id)
                except FolioComercial.DoesNotExist:
                    logger.error(f'CrearContratoWebAPIView GET: folio {folio_id} no encontrado')
                    return Response({'error': 'Folio no encontrado'}, status=status.HTTP_404_NOT_FOUND)

                fecha_actual = date.today()
                todos_trabajadores = PersonalTrabajadores.objects.filter(holding_id=holding_id, estado=True).exclude(
                    Q(cargo__nombre__icontains='administrador') | Q(cargo__nombre__icontains='admin')
                )
                trabajadores_con_contrato = ContratoTrabajador.objects.filter(
                    holding_id=holding_id,
                    fecha_inicio_contrato__lte=fecha_actual,
                ).filter(
                    Q(fecha_termino_contrato__gte=fecha_actual) | Q(fecha_termino_contrato__isnull=True)
                ).values_list('trabajador_id', flat=True).distinct()

                trabajadores_data = [{
                    'id': t.id, 'nombres': t.nombres, 'apellidos': t.apellidos,
                    'rut': t.rut, 'cargo_nombre': t.cargo.nombre if t.cargo else 'Sin cargo',
                } for t in todos_trabajadores.exclude(id__in=trabajadores_con_contrato)]

                fundos_data  = [{'id': f.id, 'nombre_campo': f.nombre_campo} for f in folio.fundos.all()]
                labores_data = [{'id': l.id, 'nombre': l.nombre} for l in folio.labores.all()]

                horarios_data = []
                for h in folio.horarios.all():
                    total_minutos = 0
                    dias = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']
                    for dia in dias:
                        inicio   = getattr(h, f'{dia}_inicio', None)
                        fin      = getattr(h, f'{dia}_fin', None)
                        colacion = getattr(h, f'{dia}_minutos_colacion', 0)
                        if inicio and fin:
                            total_minutos += (datetime.combine(datetime.today(), fin) - datetime.combine(datetime.today(), inicio)).seconds // 60 - colacion
                    horarios_data.append({'id': h.id, 'nombre': h.nombre, 'jornada': round(total_minutos / 60, 1)})

                casas_data      = [{'id': c.id, 'nombre': c.nombre} for c in CasasTrabajadores.objects.filter(holding_id=holding_id, estado=True)]
                documentos_data = [{'id': d.id, 'nombre': d.nombre, 'tipo': d.tipo} for d in ContratoVariables.objects.filter(holding_id=holding_id, activo=True)]

                return Response({
                    'trabajadores': trabajadores_data,
                    'folio': {
                        'id': folio.id,
                        'fecha_inicio': folio.fecha_inicio_contrato.strftime('%Y-%m-%d'),
                        'fecha_termino': folio.fecha_termino_contrato.strftime('%Y-%m-%d') if folio.fecha_termino_contrato else None,
                        'cliente_id': folio.cliente.id if folio.cliente else None,
                        'cliente_nombre': folio.cliente.nombre if folio.cliente else None,
                    },
                    'fundos': fundos_data,
                    'labores': labores_data,
                    'horarios': horarios_data,
                    'casas': casas_data,
                    'documentos': documentos_data,
                }, status=status.HTTP_200_OK)

            return Response({'error': 'Parámetros inválidos'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error('CrearContratoWebAPIView GET: error inesperado', exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, format=None):
        try:
            required_fields = ['holding', 'trabajador', 'fecha_inicio_contrato', 'labor', 'folio_comercial', 'horario', 'fundo']
            missing_fields = [f for f in required_fields if f not in request.data]
            if missing_fields:
                logger.error(f'CrearContratoWebAPIView POST: campos faltantes: {", ".join(missing_fields)}')
                return Response({'error': f'Campos requeridos faltantes: {", ".join(missing_fields)}'}, status=status.HTTP_400_BAD_REQUEST)

            with transaction.atomic():
                try:
                    trabajador = PersonalTrabajadores.objects.get(id=request.data['trabajador'], holding_id=request.data['holding'])
                except PersonalTrabajadores.DoesNotExist:
                    logger.error(f'CrearContratoWebAPIView POST: trabajador {request.data["trabajador"]} no encontrado')
                    return Response({'error': 'Trabajador no encontrado'}, status=status.HTTP_404_NOT_FOUND)

                fecha_inicio = datetime.strptime(request.data['fecha_inicio_contrato'], '%Y-%m-%d').date()
                contrato_vigente = ContratoTrabajador.objects.filter(
                    trabajador=trabajador,
                    fecha_inicio_contrato__lte=fecha_inicio,
                ).filter(
                    Q(fecha_termino_contrato__gte=fecha_inicio) | Q(fecha_termino_contrato__isnull=True)
                ).exists()

                if contrato_vigente:
                    logger.error(f'CrearContratoWebAPIView POST: trabajador {trabajador.id} ya tiene contrato vigente')
                    return Response({'error': 'El trabajador ya tiene un contrato vigente'}, status=status.HTTP_400_BAD_REQUEST)

                try:
                    folio = FolioComercial.objects.get(id=request.data['folio_comercial'], holding_id=request.data['holding'])
                except FolioComercial.DoesNotExist:
                    logger.error(f'CrearContratoWebAPIView POST: folio {request.data["folio_comercial"]} no encontrado')
                    return Response({'error': 'Folio comercial no encontrado'}, status=status.HTTP_404_NOT_FOUND)

                contrato_data = {
                    'holding_id':            request.data['holding'],
                    'trabajador_id':         request.data['trabajador'],
                    'fecha_inicio_contrato': request.data['fecha_inicio_contrato'],
                    'labor_id':              request.data['labor'],
                    'folio_comercial_id':    request.data['folio_comercial'],
                    'horario_id':            request.data['horario'],
                    'fundo_id':              request.data['fundo'],
                    'cliente_id':            folio.cliente.id if folio.cliente else None,
                }
                fecha_termino_historial = None
                if request.data.get('fecha_termino_contrato'):
                    contrato_data['fecha_termino_contrato'] = request.data['fecha_termino_contrato']
                    fecha_termino_historial = datetime.strptime(request.data['fecha_termino_contrato'], '%Y-%m-%d').date()

                contrato = ContratoTrabajador.objects.create(**contrato_data)
                try:
                    horario = Horarios.objects.get(id=request.data['horario'])
                    from ..models import ContratoHorarioSnapshot
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
                    ContratoHorarioSnapshot.objects.update_or_create(
                        contrato=contrato,
                        defaults={
                            'trabajador': trabajador,
                            'holding_id': request.data['holding'],
                            'datos': {'nombre': horario.nombre, 'horas_por_dia': horas_por_dia}
                        }
                    )
                except Exception as e:
                    logger.error(f'Error creando snapshot horario: {e}')
                logger.debug(f'CrearContratoWebAPIView POST: contrato {contrato.id} creado para trabajador {trabajador.id}')

                casa_id = request.data.get('casa_id')
                if casa_id:
                    RegistroCasaTrabajador.objects.filter(trabajador=trabajador, fecha_fin__isnull=True).update(fecha_fin=fecha_inicio - timedelta(days=1))
                    RegistroCasaTrabajador.objects.create(
                        holding_id=request.data['holding'],
                        trabajador=trabajador,
                        casa_id=casa_id,
                        fecha_inicio=fecha_inicio,
                        fecha_fin=fecha_termino_historial,
                    )

                supervisor_asignado     = False
                jefe_cuadrilla_asignado = False
                transporte_asignado     = False

                supervisor_id = request.data.get('supervisor_id')
                if supervisor_id:
                    try:
                        supervisor = Supervisores.objects.get(id=supervisor_id, holding_id=request.data['holding'])
                        supervisor.trabajadores.add(trabajador)
                        supervisor_asignado = True
                        SupervisorTrabajadorHistorial.objects.filter(trabajador=trabajador, fecha_fin__isnull=True).update(fecha_fin=fecha_inicio - timedelta(days=1))
                        SupervisorTrabajadorHistorial.objects.create(
                            holding_id=request.data['holding'],
                            supervisor=supervisor,
                            trabajador=trabajador,
                            fecha_inicio=fecha_inicio,
                            fecha_fin=fecha_termino_historial,
                        )
                        logger.debug(f'CrearContratoWebAPIView POST: trabajador {trabajador.id} asignado a supervisor {supervisor.id}')
                    except Supervisores.DoesNotExist:
                        raise Exception(f'Supervisor {supervisor_id} no encontrado')

                transportista_id = request.data.get('transportista_id')
                vehiculo_id      = request.data.get('vehiculo_id')
                chofer_id        = request.data.get('chofer_id')

                if transportista_id or vehiculo_id:
                    if transportista_id:
                        try:
                            EmpresasTransporte.objects.get(id=transportista_id, holding_id=request.data['holding'])
                        except EmpresasTransporte.DoesNotExist:
                            raise Exception(f'Empresa de transporte {transportista_id} no encontrada')
                    if vehiculo_id:
                        try:
                            VehiculosTransporte.objects.get(id=vehiculo_id, holding_id=request.data['holding'])
                        except VehiculosTransporte.DoesNotExist:
                            raise Exception(f'Vehículo {vehiculo_id} no encontrado')
                    if chofer_id:
                        try:
                            ChoferesTransporte.objects.get(id=chofer_id, holding_id=request.data['holding'])
                        except ChoferesTransporte.DoesNotExist:
                            raise Exception(f'Chofer {chofer_id} no encontrado')

                    TrabajadorTransporteHistorial.objects.filter(
                        trabajador=trabajador, fecha_fin__isnull=True
                    ).update(fecha_fin=fecha_inicio - timedelta(days=1))

                    TrabajadorTransporteHistorial.objects.create(
                        holding_id=request.data['holding'],
                        trabajador=trabajador,
                        transportista_id=transportista_id or None,
                        vehiculo_id=vehiculo_id or None,
                        chofer_id=chofer_id or None,
                        fecha_inicio=fecha_inicio,
                        fecha_fin=fecha_termino_historial,
                    )
                    transporte_asignado = True

                return Response({
                    'message':       'Contrato creado exitosamente',
                    'contrato_id':   contrato.id,
                    'trabajador':    f'{trabajador.nombres} {trabajador.apellidos}',
                    'fecha_inicio':  request.data['fecha_inicio_contrato'],
                    'fecha_termino': request.data.get('fecha_termino_contrato', 'INDEFINIDO'),
                    'asignaciones': {
                        'supervisor':     supervisor_asignado,
                        'jefe_cuadrilla': jefe_cuadrilla_asignado,
                        'transporte':     transporte_asignado,
                    },
                }, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error('CrearContratoWebAPIView POST: error inesperado', exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FirmaOrganizacionAPIView(BaseAPIView):

    def get(self, request, *args, **kwargs):
        holding_id = request.GET.get('holding_id')
        if not holding_id:
            return Response({'error': 'Se requiere holding_id'}, status=400)
        
        holding = get_object_or_404(Holding, id=holding_id)
        firmas = FirmaOrganizacion.objects.filter(holding=holding)
        
        return Response([{
            'id': f.id,
            'tipo': f.tipo,
            'nombre': f.nombre,
            'key': f"{f.tipo}_{slugify_nombre(f.nombre)}",
            'imagen_url': request.build_absolute_uri(f.imagen.url)
        } for f in firmas])

    def post(self, request, *args, **kwargs):
        holding_id = request.data.get('holding_id')
        tipo = request.data.get('tipo')
        nombre = request.data.get('nombre', '').strip()

        if not holding_id:
            return Response({'error': 'Se requiere holding_id'}, status=400)
        if tipo not in ['firma', 'huella']:
            return Response({'error': 'tipo debe ser "firma" o "huella"'}, status=400)
        if not nombre:
            return Response({'error': 'nombre es obligatorio'}, status=400)

        holding = get_object_or_404(Holding, id=holding_id)
        imagen = request.FILES.get('imagen')

        if not imagen:
            return Response({'error': 'No se proporcionó imagen'}, status=400)
        if imagen.content_type not in ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']:
            return Response({'error': 'Formato no válido. Use JPG, PNG o GIF'}, status=400)
        if imagen.size > 5 * 1024 * 1024:
            return Response({'error': 'Máximo 5MB'}, status=400)

        firma, _ = FirmaOrganizacion.objects.get_or_create(
            holding=holding, tipo=tipo, nombre=nombre
        )
        if firma.imagen:
            firma.imagen.delete(save=False)
        firma.imagen = imagen
        firma.save()

        return Response({
            'id': firma.id,
            'tipo': firma.tipo,
            'nombre': firma.nombre,
            'key': f"{tipo}_{slugify_nombre(nombre)}",
            'imagen_url': request.build_absolute_uri(firma.imagen.url)
        }, status=201)

    def delete(self, request, *args, **kwargs):
        firma_id = request.GET.get('id')
        if not firma_id:
            return Response({'error': 'Se requiere id'}, status=400)

        firma = get_object_or_404(FirmaOrganizacion, id=firma_id)
        firma.imagen.delete(save=False)
        firma.delete()

        return Response({'mensaje': 'Eliminada exitosamente'})
    
# ==============================================================================
# CONTRATO RETROACTIVO
# ==============================================================================

class ContratoRetroactivoAPIView(BaseAPIView):
    
    def get(self, request):
        from django.db.models import Q
        from datetime import datetime

        holding_id = request.query_params.get('holding')
        fecha_str  = request.query_params.get('fecha')

        if not holding_id or not fecha_str:
            return Response({'error': 'holding y fecha requeridos'}, status=400)

        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'fecha debe ser YYYY-MM-DD'}, status=400)

        todos = PersonalTrabajadores.objects.filter(holding_id=holding_id, estado=True)

        resultados = []
        for t in todos:
            tiene_contrato = ContratoTrabajador.objects.filter(
                trabajador_id=t.id,
                fecha_inicio_contrato__lte=fecha
            ).filter(
                Q(fecha_termino_contrato__gte=fecha) | Q(fecha_termino_contrato__isnull=True)
            ).exists()

            if not tiene_contrato:
                resultados.append({
                    'trabajador_id':     t.id,
                    'trabajador_nombre': f"{t.nombres} {t.apellidos or ''}".strip(),
                    'trabajador_rut':    t.rut or '',
                    'fecha_inicio_sugerida': fecha,
                    'fecha_fin_periodo': None,
                })

        return Response(resultados)

    def post(self, request):
        from datetime import datetime
        from django.db.models import Q

        holding_id       = request.data.get('holding')
        trabajador_id    = request.data.get('trabajador')
        fecha_inicio_str = request.data.get('fecha_inicio_contrato')
        supervisor_id    = request.data.get('supervisor_id')

        campos_requeridos = ['holding', 'trabajador', 'fecha_inicio_contrato',
                            'labor', 'folio_comercial', 'horario', 'fundo']
        faltantes = [c for c in campos_requeridos if not request.data.get(c)]
        if faltantes:
            return Response({'error': f'Faltan campos: {faltantes}'}, status=400)

        try:
            fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'fecha_inicio_contrato debe ser YYYY-MM-DD'}, status=400)

        tiene_contrato = ContratoTrabajador.objects.filter(
            trabajador_id=trabajador_id,
            fecha_inicio_contrato__lte=fecha_inicio
        ).filter(
            Q(fecha_termino_contrato__gte=fecha_inicio) | Q(fecha_termino_contrato__isnull=True)
        ).exists()

        if tiene_contrato:
            return Response(
                {'error': 'El trabajador ya tiene un contrato vigente en esa fecha'},
                status=400
            )

        try:
            folio = FolioComercial.objects.get(
                id=request.data['folio_comercial'], holding_id=holding_id
            )
        except FolioComercial.DoesNotExist:
            return Response({'error': 'Folio comercial no encontrado'}, status=404)

        contrato_data = {
            'holding_id':            holding_id,
            'trabajador_id':         trabajador_id,
            'fecha_inicio_contrato': fecha_inicio,
            'labor_id':              request.data['labor'],
            'folio_comercial_id':    request.data['folio_comercial'],
            'horario_id':            request.data['horario'],
            'fundo_id':              request.data['fundo'],
            'cliente_id':            folio.cliente.id if folio.cliente else None,
        }

        fecha_termino = None
        if request.data.get('fecha_termino_contrato'):
            try:
                fecha_termino = datetime.strptime(
                    request.data['fecha_termino_contrato'], '%Y-%m-%d'
                ).date()
                contrato_data['fecha_termino_contrato'] = fecha_termino
            except ValueError:
                return Response({'error': 'fecha_termino_contrato debe ser YYYY-MM-DD'}, status=400)

        contrato = ContratoTrabajador.objects.create(**contrato_data)

        try:
            horario = Horarios.objects.get(id=request.data['horario'])
            from ..models import ContratoHorarioSnapshot, PersonalTrabajadores
            trabajador_obj = PersonalTrabajadores.objects.get(id=trabajador_id)
            dias = ['lunes','martes','miercoles','jueves','viernes','sabado','domingo']
            horas_por_dia = {}
            for i, dia in enumerate(dias):
                inicio = getattr(horario, f'{dia}_inicio', None)
                fin = getattr(horario, f'{dia}_fin', None)
                colacion = getattr(horario, f'{dia}_minutos_colacion', 0) or 0
                if inicio and fin:
                    mins = (datetime.combine(datetime.today(), fin) - datetime.combine(datetime.today(), inicio)).seconds // 60
                    horas_por_dia[str(i)] = round((mins - colacion) / 60, 2)
                else:
                    horas_por_dia[str(i)] = 0.0
            ContratoHorarioSnapshot.objects.update_or_create(
                contrato=contrato,
                defaults={
                    'trabajador': trabajador_obj,
                    'holding_id': holding_id,
                    'datos': {'nombre': horario.nombre, 'horas_por_dia': horas_por_dia}
                }
            )
        except Exception as e:
            logger.error(f'Error creando snapshot horario retroactivo: {e}')

        if supervisor_id:
            try:
                supervisor = Supervisores.objects.get(id=supervisor_id, holding_id=holding_id)

                # Solo crear si NO existe ya un historial de cualquier supervisor
                # que cubra exactamente este período del contrato retroactivo
                solapado = SupervisorTrabajadorHistorial.objects.filter(
                    trabajador_id=trabajador_id,
                    fecha_inicio__lte=fecha_inicio,
                ).filter(
                    Q(fecha_fin__gte=fecha_inicio) | Q(fecha_fin__isnull=True)
                ).exists()

                if not solapado:
                    SupervisorTrabajadorHistorial.objects.create(
                        holding_id=holding_id,
                        supervisor=supervisor,
                        trabajador_id=trabajador_id,
                        fecha_inicio=fecha_inicio,
                        fecha_fin=fecha_termino,
                    )

            except Supervisores.DoesNotExist:
                return Response({'error': 'Supervisor no encontrado'}, status=404)

        return Response({'id': contrato.id, 'mensaje': 'Contrato retroactivo creado'}, status=201)

# ==============================================================================
# PARAMETRO
# ==============================================================================
class ParametroAPIView(BaseAPIView):

    def get(self, request, *args, **kwargs):
        solo_con_formato = request.query_params.get('con_formato') == 'true'
        qs = Parametro.objects.filter(holding=request.user.holding)
        if solo_con_formato:
            qs = qs.exclude(formato__isnull=True)
        data = []
        for p in qs:
            data.append({
                'id': p.id,
                'nombre': p.nombre,
                'formato_id': p.formato_id,
                'formato_nombre': p.formato.nombre if p.formato else None,
            })
        return Response(data)

    def post(self, request, *args, **kwargs):
        nombre = request.data.get('nombre', '').strip()
        if not nombre:
            return Response({'error': 'nombre es requerido'}, status=status.HTTP_400_BAD_REQUEST)
        parametro = Parametro.objects.create(
            holding=request.user.holding,
            nombre=nombre,
        )
        return Response({'id': parametro.id, 'nombre': parametro.nombre}, status=status.HTTP_201_CREATED)

    def put(self, request, parametro_id, *args, **kwargs):
        try:
            parametro = Parametro.objects.get(id=parametro_id, holding=request.user.holding)
        except Parametro.DoesNotExist:
            return Response({'error': 'No encontrado'}, status=status.HTTP_404_NOT_FOUND)

        if 'nombre' in request.data:
            parametro.nombre = request.data['nombre'].strip()
        if 'formato_id' in request.data:
            formato_id = request.data['formato_id']
            if formato_id is None:
                parametro.formato = None
            else:
                try:
                    parametro.formato = ContratoVariables.objects.get(
                        id=formato_id, holding=request.user.holding
                    )
                except ContratoVariables.DoesNotExist:
                    return Response({'error': 'Formato no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        parametro.save()
        return Response({
            'id': parametro.id,
            'nombre': parametro.nombre,
            'formato_id': parametro.formato_id,
            'formato_nombre': parametro.formato.nombre if parametro.formato else None,
        })

    def delete(self, request, parametro_id, *args, **kwargs):
        try:
            parametro = Parametro.objects.get(id=parametro_id, holding=request.user.holding)
        except Parametro.DoesNotExist:
            return Response({'error': 'No encontrado'}, status=status.HTTP_404_NOT_FOUND)
        nombre = parametro.nombre
        parametro.delete()
        return Response({'mensaje': f"Parámetro '{nombre}' eliminado"})


# ==============================================================================
# CONTRATO ASOCIADO TRABAJADOR
# ==============================================================================
class ContratoAsociadoTrabajadorAPIView(BaseAPIView):
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, *args, **kwargs):
        trabajador_id = request.query_params.get('trabajador_id')
        parametro_id = request.query_params.get('parametro_id')

        if not trabajador_id:
            return Response({'error': 'trabajador_id es requerido'}, status=status.HTTP_400_BAD_REQUEST)

        qs = ContratoAsociadoTrabajador.objects.filter(
            holding=request.user.holding,
            trabajador_id=trabajador_id,
        ).select_related('parametro')

        if parametro_id:
            qs = qs.filter(parametro_id=parametro_id)

        data = [{
            'id': c.id,
            'parametro_id': c.parametro_id,
            'parametro_nombre': c.parametro.nombre,
            'archivo_pdf_url': request.build_absolute_uri(c.archivo_pdf.url),
            'orden': c.orden,
            'fecha_subida': c.fecha_subida.strftime('%Y-%m-%d %H:%M'),
        } for c in qs]

        return Response(data)

    def post(self, request, *args, **kwargs):
        trabajador_id = request.data.get('trabajador_id')
        parametro_id = request.data.get('parametro_id')
        archivo = request.FILES.get('archivo_pdf')

        if not trabajador_id or not parametro_id or not archivo:
            return Response(
                {'error': 'trabajador_id, parametro_id y archivo_pdf son requeridos'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            trabajador = PersonalTrabajadores.objects.get(
                id=trabajador_id, holding=request.user.holding
            )
        except PersonalTrabajadores.DoesNotExist:
            return Response({'error': 'Trabajador no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        try:
            parametro = Parametro.objects.get(
                id=parametro_id, holding=request.user.holding
            )
        except Parametro.DoesNotExist:
            return Response({'error': 'Parámetro no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        # Calcular orden incremental
        ultimo = ContratoAsociadoTrabajador.objects.filter(
            trabajador=trabajador, parametro=parametro
        ).order_by('-orden').first()
        siguiente_orden = (ultimo.orden + 1) if ultimo else 1

        contrato = ContratoAsociadoTrabajador.objects.create(
            holding=request.user.holding,
            trabajador=trabajador,
            parametro=parametro,
            archivo_pdf=archivo,
            orden=siguiente_orden,
        )

        return Response({
            'id': contrato.id,
            'parametro_id': contrato.parametro_id,
            'parametro_nombre': parametro.nombre,
            'archivo_pdf_url': request.build_absolute_uri(contrato.archivo_pdf.url),
            'orden': contrato.orden,
            'fecha_subida': contrato.fecha_subida.strftime('%Y-%m-%d %H:%M'),
        }, status=status.HTTP_201_CREATED)

    def delete(self, request, contrato_id, *args, **kwargs):
        try:
            contrato = ContratoAsociadoTrabajador.objects.get(
                id=contrato_id, holding=request.user.holding
            )
        except ContratoAsociadoTrabajador.DoesNotExist:
            return Response({'error': 'No encontrado'}, status=status.HTTP_404_NOT_FOUND)

        contrato.archivo_pdf.delete(save=False)
        contrato.delete()
        return Response({'mensaje': 'Asociación eliminada'})

# ==============================================================================
# TRABAJADORES POR PARÁMETRO (para el selector del modo nuevo)
# ==============================================================================
class TrabajadoresPorParametroAPIView(BaseAPIView):

    def get(self, request, *args, **kwargs):
        parametro_id = request.query_params.get('parametro_id')
        sociedad_id  = request.query_params.get('sociedad_id')

        if not parametro_id:
            return Response({'error': 'parametro_id es requerido'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            parametro = Parametro.objects.get(id=parametro_id, holding=request.user.holding)
        except Parametro.DoesNotExist:
            return Response({'error': 'Parámetro no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        if not parametro.formato:
            return Response({'error': 'El parámetro no tiene formato asignado'}, status=status.HTTP_400_BAD_REQUEST)

        # Contratos asociados agrupados por trabajador
        qs = ContratoAsociadoTrabajador.objects.filter(
            holding=request.user.holding,
            parametro=parametro,
        ).select_related('trabajador', 'trabajador__sociedad', 'trabajador__cargo')

        # Filtrar por sociedad si se proporciona
        if sociedad_id:
            qs = qs.filter(trabajador__sociedad_id=sociedad_id)

        # Agrupar por trabajador
        mapa = {}
        for ca in qs:
            t = ca.trabajador
            if t.id not in mapa:
                mapa[t.id] = {
                    'trabajador_id': t.id,
                    'nombres':       t.nombres,
                    'apellidos':     t.apellidos or '',
                    'rut':           t.rut or t.dni or '',
                    'cargo':         t.cargo.nombre if t.cargo else '',
                    'pdfs': [],
                }
            mapa[t.id]['pdfs'].append({
                'id':             ca.id,
                'orden':          ca.orden,
                'archivo_pdf_url': request.build_absolute_uri(ca.archivo_pdf.url),
            })

        return Response(list(mapa.values()))


# ==============================================================================
# GENERAR DOCUMENTOS POR PARÁMETRO (modo nuevo)
# ==============================================================================
class GenerarDocumentosPorParametroAPIView(GenerarDocumentosMasivoAPIView):
    """
    Igual que GenerarDocumentosMasivoAPIView pero:
    - El PDF base viene de ContratoAsociadoTrabajador.archivo_pdf
    - Las variables vienen de Parametro.formato.variables
    - Valida que contrato_asociado.parametro == parametro enviado
    """

    def post(self, request, *args, **kwargs):
        parametro_id   = request.data.get('parametro_id')
        trabajadores   = request.data.get('trabajadores', [])  # [{trabajador_id, contrato_asociado_id}]
        fecha_emision  = request.data.get('fecha_emision')
        sociedad_id    = request.data.get('sociedad_id')
        marcar_generado = request.data.get('marcar_como_generado', False)

        if not parametro_id:
            return Response({'error': 'parametro_id es requerido'}, status=status.HTTP_400_BAD_REQUEST)
        if not trabajadores:
            return Response({'error': 'Se requiere al menos un trabajador'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            parametro = Parametro.objects.get(id=parametro_id, holding=request.user.holding)
        except Parametro.DoesNotExist:
            return Response({'error': 'Parámetro no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        if not parametro.formato:
            return Response({'error': 'El parámetro no tiene formato asignado'}, status=status.HTTP_400_BAD_REQUEST)

        urls_generadas = []
        errores = []

        for item in trabajadores:
            trabajador_id        = item.get('trabajador_id')
            contrato_asociado_id = item.get('contrato_asociado_id')

            try:
                trabajador = PersonalTrabajadores.objects.get(
                    id=trabajador_id, holding=request.user.holding
                )
                contrato_asociado = ContratoAsociadoTrabajador.objects.get(
                    id=contrato_asociado_id, holding=request.user.holding
                )

                # Invariante spec §31
                if contrato_asociado.parametro_id != int(parametro_id):
                    errores.append({
                        'trabajador_id': trabajador_id,
                        'error': 'El PDF no pertenece al parámetro seleccionado'
                    })
                    continue

                datos_variables = self._mapear_datos_trabajador(trabajador, fecha_emision, sociedad_id)
                datos_variables['trabajador_id'] = trabajador.id

                # Generar usando el PDF del trabajador como base
                pdf_buffer = self._generar_con_pdf_custom(
                    pdf_path   = contrato_asociado.archivo_pdf.path,
                    variables  = parametro.formato.variables,
                    datos      = datos_variables,
                    holding    = request.user.holding,
                )

                pdf_url = self._guardar_contrato_generado(
                    pdf_buffer, trabajador, parametro.formato, request, marcar_generado
                )

                urls_generadas.append({
                    'trabajador_id':     trabajador.id,
                    'trabajador_nombre': f'{trabajador.nombres} {trabajador.apellidos}',
                    'url':               pdf_url,
                    'success':           True,
                })

            except PersonalTrabajadores.DoesNotExist:
                errores.append({'trabajador_id': trabajador_id, 'error': 'Trabajador no encontrado'})
            except ContratoAsociadoTrabajador.DoesNotExist:
                errores.append({'trabajador_id': trabajador_id, 'error': 'PDF asociado no encontrado'})
            except Exception as e:
                logger.error(f'GenerarDocumentosPorParametroAPIView: error trabajador {trabajador_id}', exc_info=True)
                errores.append({'trabajador_id': trabajador_id, 'error': str(e)})

        return Response({
            'mensaje':        f'Se generaron {len(urls_generadas)} contratos exitosamente',
            'contratos':      urls_generadas,
            'errores':        errores,
            'total_exitosos': len(urls_generadas),
            'total_errores':  len(errores),
        }, status=status.HTTP_200_OK)

    def _generar_con_pdf_custom(self, pdf_path, variables, datos, holding):
        """
        Igual que _generar_documento_coordenadas_nativas pero recibe
        pdf_path y variables directamente en vez de documento_id.
        """
        reader = PdfReader(open(pdf_path, 'rb'))

        BASE_FONT_SIZE = 9
        BASE_OFFSET_X  = -8
        BASE_OFFSET_Y  = -15.2
        FONT_BASELINE  = BASE_FONT_SIZE * 0.3
        campos_centrados = [
            'rut', 'dni', 'nic', 'estado_civil',
            'fecha_nacimiento', 'fecha_emision',
            'fecha_ingreso', 'fecha_inicio_contrato', 'fecha_termino',
        ]

        variables_por_pagina = {}
        for variable_data in variables:
            nombre_variable = variable_data.get('nombre')
            for ubicacion in variable_data.get('ubicaciones', []):
                pagina = ubicacion.get('pagina', 1)
                if pagina not in variables_por_pagina:
                    variables_por_pagina[pagina] = []
                variables_por_pagina[pagina].append({
                    'nombre': nombre_variable,
                    'posX':   ubicacion.get('posX', 0),
                    'posY':   ubicacion.get('posY', 0),
                    'width':  ubicacion.get('width'),
                    'height': ubicacion.get('height'),
                })

        firma_empleador_disponible = bool(holding.firma_empleador)
        trabajador = None
        if 'trabajador_id' in datos:
            try:
                trabajador = PersonalTrabajadores.objects.get(id=datos['trabajador_id'])
            except PersonalTrabajadores.DoesNotExist:
                pass

        final_writer = PdfWriter()

        for page_num in range(len(reader.pages)):
            ui_page_num = page_num + 1
            temp_buffer = io.BytesIO()
            temp_writer = PdfWriter()
            temp_writer.add_page(reader.pages[page_num])
            temp_writer.write(temp_buffer)
            temp_buffer.seek(0)
            temp_reader   = PdfReader(temp_buffer)
            isolated_page = temp_reader.pages[0]
            page_width    = float(isolated_page.mediabox.width)
            page_height   = float(isolated_page.mediabox.height)

            if ui_page_num not in variables_por_pagina:
                final_writer.add_page(isolated_page)
                continue

            overlay_buffer = io.BytesIO()
            can = canvas.Canvas(overlay_buffer, pagesize=(page_width, page_height))
            variables_escritas = 0

            for variable in variables_por_pagina[ui_page_num]:
                nombre = variable['nombre']

                if nombre == 'firma_empleador':
                    if firma_empleador_disponible:
                        try:
                            firma_path = holding.firma_empleador.path
                            if os.path.exists(firma_path):
                                img_w = variable.get('width', 150)
                                img_h = variable.get('height', 50)
                                pdf_x = variable['posX'] + BASE_OFFSET_X
                                pdf_y = page_height - variable['posY'] + BASE_OFFSET_Y - img_h
                                can.drawImage(firma_path, pdf_x, pdf_y, width=img_w, height=img_h,
                                              preserveAspectRatio=True, mask='auto')
                                variables_escritas += 1
                        except Exception:
                            pass
                    continue

                elif nombre == 'firma':
                    if trabajador and bool(trabajador.firma) and os.path.exists(trabajador.firma.path):
                        img_w = variable.get('width', 100)
                        img_h = variable.get('height', 40)
                        pdf_x = variable['posX'] + BASE_OFFSET_X
                        pdf_y = page_height - variable['posY'] + BASE_OFFSET_Y - img_h
                        try:
                            can.drawImage(trabajador.firma.path, pdf_x, pdf_y, width=img_w, height=img_h,
                                          preserveAspectRatio=True, mask='auto')
                            variables_escritas += 1
                        except Exception:
                            pass
                    continue

                elif nombre == 'huella':
                    if trabajador and bool(trabajador.huella_digital) and os.path.exists(trabajador.huella_digital.path):
                        img_w = variable.get('width', 80)
                        img_h = variable.get('height', 100)
                        pdf_x = variable['posX'] + BASE_OFFSET_X
                        pdf_y = page_height - variable['posY'] + BASE_OFFSET_Y - img_h
                        try:
                            can.drawImage(trabajador.huella_digital.path, pdf_x, pdf_y, width=img_w, height=img_h,
                                          preserveAspectRatio=True, mask='auto')
                            variables_escritas += 1
                        except Exception:
                            pass
                    continue

                if nombre not in datos or not datos[nombre]:
                    continue

                valor  = str(datos[nombre])
                pdf_x  = variable['posX'] + BASE_OFFSET_X
                pdf_y  = page_height - variable['posY'] + BASE_OFFSET_Y + FONT_BASELINE

                can.setFont('Helvetica', BASE_FONT_SIZE)
                if nombre in campos_centrados:
                    tw = can.stringWidth(valor, 'Helvetica', BASE_FONT_SIZE)
                    can.drawString(pdf_x - (tw / 2), pdf_y, valor)
                else:
                    can.drawString(pdf_x, pdf_y, valor)
                variables_escritas += 1

            can.save()
            overlay_buffer.seek(0)

            if variables_escritas > 0:
                try:
                    overlay_reader = PdfReader(overlay_buffer)
                    isolated_page.merge_page(overlay_reader.pages[0])
                except Exception:
                    pass

            final_writer.add_page(isolated_page)

        output_buffer = io.BytesIO()
        final_writer.write(output_buffer)
        output_buffer.seek(0)
        return output_buffer

