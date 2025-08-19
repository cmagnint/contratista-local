
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
import io
import os
import secrets
import string
from django.conf import settings
import uuid


def generate_token():
    # Genera un token aleatorio de 16 caracteres
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(16))

def generate_token_link_apk():
    """Genera un token único para cada enlace APK"""
    return os.urandom(16).hex()

def generar_documento_con_datos(documento_id, datos_variables, debug=False):
    """
    Genera un PDF con datos de variables posicionadas correctamente.
    """
    from .models import ContratoVariables
    import logging
    logger = logging.getLogger(__name__)
    
    # Obtener el documento con las variables
    documento = ContratoVariables.objects.get(id=documento_id)
    
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
    
    # Parámetros de transformación según el tipo de documento
    transformacion_por_tipo = {
    'CHILENO': {
        'escala_x': 0.72,        # Aproximadamente 1.0/1.4
        'escala_y': 0.72,        # Aproximadamente 1.0/1.4
        'offset_x': 0,           # Ajustable según pruebas
        'offset_y': 0,           # Ajustable según pruebas
        'invertir_y': True       # Mantener invertido para el sistema de coordenadas PDF
    },
    'EXTRANJERO': {
        'escala_x': 0.72,        # Igual que el tipo CHILENO para consistencia
        'escala_y': 0.72,
        'offset_x': 0,
        'offset_y': 0,
        'invertir_y': True
    },
}
    
    # Obtener parámetros para este tipo de documento
    tipo_doc = documento.tipo
    if tipo_doc in transformacion_por_tipo:
        params = transformacion_por_tipo[tipo_doc]
    else:
        # Parámetros por defecto si no se encuentra el tipo
        params = {
            'escala_x': 0.5,
            'escala_y': 0.5,
            'offset_x': 0,
            'offset_y': 0,
            'invertir_y': True
        }
    
    # Función para transformar coordenadas
    
    def transform_coordinates(x, y, page_height, page_width=None):
        # Factor de escala inverso del frontend
        frontend_scale = 1.4
        backend_scale = 1.0 / frontend_scale
        
        # Aplicar escala con factor inverso
        pdf_x = x * backend_scale + params['offset_x']
        
        # Aplicar escala e invertir Y
        if params['invertir_y']:
            pdf_y = page_height - (y * backend_scale) + params['offset_y']
        else:
            pdf_y = y * backend_scale + params['offset_y']
        
        # Logging
        logger.info(f"Transformación: ({x}, {y}) -> ({pdf_x}, {pdf_y})")
        
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
            logger.info(f"Variable '{nombre_variable}' en página {pagina}: posición original = ({variable_info['posX']}, {variable_info['posY']})")
            
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
            logger.info(f"Procesando página {ui_page_num}: ancho={page_width}, alto={page_height}")
            
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
                        logger.info(f"Campo centrado: {nombre} en ({pdf_x}, {pdf_y}) valor: {valor}")
                    else:
                        # Alinear a la izquierda (comportamiento estándar)
                        can.drawString(pdf_x, pdf_y, valor)
                        logger.info(f"Campo normal: {nombre} en ({pdf_x}, {pdf_y}) valor: {valor}")

                    # La línea comentada, ya NO forzamos el modo debug
                    # debug = True

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