import io
import os
import base64
import logging
import re
from rest_framework import status
from rest_framework.response import Response
from pdf2image import convert_from_bytes
from google.cloud import vision_v1
from .base import BaseAPIView, PublicAPIView
from ..models import (
    Holding,
    PersonalTrabajadores,
)

logger = logging.getLogger('contratista_test_app')

# ==============================================================================
# CARNET OCR
# ==============================================================================
class CarnetOCRAPIView(BaseAPIView):
    def post(self, request):
        try:
            image_file = request.FILES.get('image')
            if not image_file:
                return Response({'error': 'No se recibió imagen'}, status=status.HTTP_400_BAD_REQUEST)

            content = image_file.read()
            imagen_convertida_base64 = None

            if image_file.content_type == 'application/pdf':
                images = convert_from_bytes(content, first_page=1, last_page=1)
                img_byte_arr = io.BytesIO()
                images[0].save(img_byte_arr, format='PNG')
                content = img_byte_arr.getvalue()
                imagen_convertida_base64 = base64.b64encode(content).decode('utf-8')

            client = vision_v1.ImageAnnotatorClient(
                client_options={"api_key": 'GOOGLE_VISION_API_KEY_REMOVED'}
            )
            image = vision_v1.Image(content=content)
            response = client.text_detection(image=image)

            if not response.text_annotations:
                return Response({'error': 'No se detectó texto'}, status=status.HTTP_400_BAD_REQUEST)

            texto = response.text_annotations[0].description
            datos = self.parse_carnet_chileno(texto)

            logger.debug(f'CarnetOCRAPIView POST: OCR completado')
            return Response({
                'success': True,
                'datos': datos,
                'imagen_convertida': imagen_convertida_base64,
            })
        except Exception as e:
            logger.error(f'CarnetOCRAPIView POST: error inesperado', exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def parse_carnet_chileno(self, texto):
        datos = {
            'nombres': '',
            'apellidos': '',
            'rut': '',
            'sexo': '',
            'fecha_nacimiento': '',
            'nacionalidad': 'CHILENA',
        }

        texto_limpio = texto.upper()
        logger.debug(f'CarnetOCRAPIView parse_carnet_chileno: texto recibido length={len(texto_limpio)}')

        run_match = re.search(r'RUN[:\s]*(\d{1,2}\.?\d{3}\.?\d{3}-?[\dkK])', texto_limpio, re.I)
        if run_match:
            rut_crudo = run_match.group(1).replace('.', '').replace('-', '')
            datos['rut'] = rut_crudo[:-1] + rut_crudo[-1] if len(rut_crudo) > 1 else rut_crudo

        apellidos_match = re.search(
            r'APELLIDOS\s*\n\s*([A-ZÁÉÍÓÚÑ\s]+?)(?=\n\s*NOMBRES|\n\s*NACIONALIDAD)',
            texto_limpio, re.DOTALL
        )
        if apellidos_match:
            apellidos_raw = apellidos_match.group(1).strip()
            apellidos_clean = re.sub(r'(NACIONALIDAD|SEXO|RUN|FECHA|NUMERO)', '', apellidos_raw)
            datos['apellidos'] = re.sub(r'\s+', ' ', apellidos_clean).strip()

        lineas = texto_limpio.split('\n')
        for i, linea in enumerate(lineas):
            if 'NOMBRES' in linea and i + 1 < len(lineas):
                nombres_raw = lineas[i + 1].strip()
                if not re.search(r'(RUN|NACIONALIDAD|SEXO|FECHA|NUMERO|APELLIDOS)', nombres_raw):
                    datos['nombres'] = nombres_raw
                    logger.debug(f'CarnetOCRAPIView parse_carnet_chileno: nombres={nombres_raw}')
                    break

        sexo_match = re.search(r'SEXO\s*\n?\s*([MF])\s', texto_limpio)
        if sexo_match:
            datos['sexo'] = sexo_match.group(1)

        fecha_match = re.search(
            r'(\d{1,2})\s+(ENE|FEB|MAR|ABR|MAY|JUN|JUL|AGO|SEP|OCT|NOV|DIC)[A-Z]*\s+(\d{4})',
            texto_limpio
        )
        if fecha_match:
            meses = {
                'ENE': '01', 'FEB': '02', 'MAR': '03', 'ABR': '04',
                'MAY': '05', 'JUN': '06', 'JUL': '07', 'AGO': '08',
                'SEP': '09', 'OCT': '10', 'NOV': '11', 'DIC': '12',
            }
            dia = fecha_match.group(1).zfill(2)
            mes = meses.get(fecha_match.group(2)[:3], '01')
            anio = fecha_match.group(3)
            datos['fecha_nacimiento'] = f"{anio}-{mes}-{dia}"
        else:
            fecha_match2 = re.search(r'(\d{2})[/-](\d{2})[/-](\d{4})', texto_limpio)
            if fecha_match2:
                datos['fecha_nacimiento'] = f"{fecha_match2.group(3)}-{fecha_match2.group(2)}-{fecha_match2.group(1)}"

        return datos

# ==============================================================================
# PDF TO IMAGE
# ==============================================================================
class PDFToImageAPIView(BaseAPIView):
    def post(self, request):
        try:
            file = request.FILES.get('image')
            if not file:
                return Response({'error': 'No se recibió archivo'}, status=status.HTTP_400_BAD_REQUEST)

            if file.content_type != 'application/pdf':
                return Response({'error': 'Solo se aceptan archivos PDF'}, status=status.HTTP_400_BAD_REQUEST)

            content = file.read()
            images = convert_from_bytes(content, first_page=1, last_page=1)
            img_byte_arr = io.BytesIO()
            images[0].save(img_byte_arr, format='PNG')
            imagen_base64 = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')

            logger.debug(f'PDFToImageAPIView POST: PDF convertido a imagen')
            return Response({'success': True, 'imagen_convertida': imagen_base64})
        except Exception as e:
            logger.error(f'PDFToImageAPIView POST: error inesperado', exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ==============================================================================
# FIRMA EMPLEADOR
# ==============================================================================

class FirmaEmpleadorAPIView(PublicAPIView):
    def get(self, request, *args, **kwargs):
        try:
            holding_id = request.GET.get('holding_id')
            if not holding_id:
                return Response({'error': 'Se requiere holding_id como parámetro'}, status=status.HTTP_400_BAD_REQUEST)
            holding = Holding.objects.filter(id=holding_id).first()
            if not holding:
                return Response({'error': 'Holding no encontrado'}, status=status.HTTP_404_NOT_FOUND)
            if not holding.firma_empleador:
                return Response({'firma_disponible': False, 'mensaje': 'No hay firma del empleador configurada'})
            return Response({
                'firma_disponible': True,
                'firma_url': request.build_absolute_uri(holding.firma_empleador.url),
                'firma_nombre': holding.firma_empleador.name.split('/')[-1],
            })
        except Exception as e:
            logger.error(f'FirmaEmpleadorAPIView GET: error inesperado', exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, *args, **kwargs):
        try:
            holding_id = request.data.get('holding_id')
            if not holding_id:
                return Response({'error': 'Se requiere holding_id'}, status=status.HTTP_400_BAD_REQUEST)
            holding = Holding.objects.filter(id=holding_id).first()
            if not holding:
                return Response({'error': 'Holding no encontrado'}, status=status.HTTP_404_NOT_FOUND)
            if 'firma_empleador' not in request.FILES:
                return Response({'error': 'No se proporcionó archivo de firma'}, status=status.HTTP_400_BAD_REQUEST)
            firma_file = request.FILES['firma_empleador']
            if firma_file.content_type not in ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']:
                return Response({'error': 'Formato de imagen no válido. Use JPG, PNG o GIF'}, status=status.HTTP_400_BAD_REQUEST)
            if firma_file.size > 5 * 1024 * 1024:
                return Response({'error': 'La imagen es demasiado grande. Máximo 5MB'}, status=status.HTTP_400_BAD_REQUEST)
            if holding.firma_empleador:
                holding.firma_empleador.delete(save=False)
            holding.firma_empleador = firma_file
            holding.save()
            logger.debug(f'FirmaEmpleadorAPIView POST: firma actualizada para holding {holding_id}')
            return Response({
                'mensaje': 'Firma del empleador actualizada exitosamente',
                'firma_url': request.build_absolute_uri(holding.firma_empleador.url),
                'firma_nombre': holding.firma_empleador.name.split('/')[-1],
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f'FirmaEmpleadorAPIView POST: error inesperado', exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, *args, **kwargs):
        try:
            holding_id = request.GET.get('holding_id')
            if not holding_id:
                return Response({'error': 'Se requiere holding_id como parámetro'}, status=status.HTTP_400_BAD_REQUEST)
            holding = Holding.objects.filter(id=holding_id).first()
            if not holding:
                return Response({'error': 'Holding no encontrado'}, status=status.HTTP_404_NOT_FOUND)
            if not holding.firma_empleador:
                return Response({'error': 'No hay firma para eliminar'}, status=status.HTTP_404_NOT_FOUND)
            holding.firma_empleador.delete(save=True)
            logger.debug(f'FirmaEmpleadorAPIView DELETE: firma eliminada para holding {holding_id}')
            return Response({'mensaje': 'Firma del empleador eliminada exitosamente'})
        except Exception as e:
            logger.error(f'FirmaEmpleadorAPIView DELETE: error inesperado', exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ==============================================================================
# FIRMA HUELLA
# ==============================================================================
class FirmaHuellaAPIView(BaseAPIView):
    def get(self, request):
        holding_id = request.query_params.get('holding')
        if not holding_id:
            return Response({'error': 'Parámetro holding requerido'}, status=status.HTTP_400_BAD_REQUEST)
        trabajadores = PersonalTrabajadores.objects.filter(
            holding_id=holding_id,
            estado=True,
        ).order_by('apellidos', 'nombres').values('id', 'nombres', 'apellidos', 'rut', 'dni')
        return Response(list(trabajadores), status=status.HTTP_200_OK)

    def patch(self, request, trabajador_id):
        try:
            trabajador = PersonalTrabajadores.objects.get(id=trabajador_id)
        except PersonalTrabajadores.DoesNotExist:
            logger.error(f'FirmaHuellaAPIView PATCH: trabajador {trabajador_id} no encontrado')
            return Response({'error': 'Trabajador no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        if 'firma' not in request.FILES and 'huella_digital' not in request.FILES:
            return Response({'error': 'Se requiere firma o huella_digital'}, status=status.HTTP_400_BAD_REQUEST)

        if 'firma' in request.FILES:
            if trabajador.firma and os.path.isfile(trabajador.firma.path):
                os.remove(trabajador.firma.path)
            trabajador.firma = request.FILES['firma']

        if 'huella_digital' in request.FILES:
            if trabajador.huella_digital and os.path.isfile(trabajador.huella_digital.path):
                os.remove(trabajador.huella_digital.path)
            trabajador.huella_digital = request.FILES['huella_digital']

        trabajador.save()
        logger.debug(f'FirmaHuellaAPIView PATCH: trabajador {trabajador_id} actualizado')
        return Response({
            'id': trabajador.id,
            'firma': trabajador.firma.url if trabajador.firma else None,
            'huella_digital': trabajador.huella_digital.url if trabajador.huella_digital else None,
        }, status=status.HTTP_200_OK)
    
