# contratista_test_app/tasks.py
import csv
import os
import io
import time
import random
import traceback
from datetime import timedelta
from typing import Dict, List, Any
from decimal import Decimal
import requests # type: ignore
from django.core.files.base import ContentFile

from celery import shared_task
from django.utils import timezone
from django.conf import settings
from django.db import transaction
from django.core.mail import send_mail

# Importar modelos
from .models import (
    ConfiguracionSIIAutomaticaCompra, 
    FacturaCompraSIIPorDistribuir, 
    FacturaCompraSIIDistribuida,
    ConfiguracionSIIAutomaticaVenta,
    FacturaVentaSIIPorDistribuir,
    FacturaVentaSIIDistribuida,
)

# Importar el browser session manager del sistema manual
from .browser_session_manager import BrowserSessionManager

# Importar utilidades de Selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException

# ==================== TAREA PRINCIPAL ====================

@shared_task
def revisar_configuraciones_pendientes():
    """Revisa configuraciones y ejecuta las que corresponden a la hora actual"""
    from datetime import datetime
    import pytz
    from django.utils import timezone
    
    print("Revisando configuraciones automáticas...")
    
    try:
        chile_tz = pytz.timezone('America/Santiago')
        ahora_chile = timezone.now().astimezone(chile_tz)
        hora_actual = ahora_chile.time()
        
        configuraciones_activas = ConfiguracionSIIAutomaticaCompra.objects.filter(activo=True)
        print(f"Hora actual: {hora_actual.strftime('%H:%M')}")
        
        for config in configuraciones_activas:
            hora_config = config.hora_ejecucion
            minutos_actual = hora_actual.hour * 60 + hora_actual.minute
            minutos_config = hora_config.hour * 60 + hora_config.minute
            
            # Si la hora coincide (con 1 minuto de tolerancia)
            if abs(minutos_actual - minutos_config) <= 1:
                print(f"⏰ Ejecutando configuración {config.id}")
                procesar_configuracion_automatica.delay(config.id)
        
        return f"Revisión completada a las {hora_actual.strftime('%H:%M')}"
        
    except Exception as e:
        print(f"Error en revisión: {str(e)}")
        return f"Error: {str(e)}"

@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def buscar_facturas_automaticamente(self):
    """
    Tarea principal que busca facturas automáticamente para todas las configuraciones activas.
    Se ejecuta periódicamente según la configuración de Celery Beat.
    """
    print("=== INICIANDO BÚSQUEDA AUTOMÁTICA DE FACTURAS ===")
    
    resultados = {
        'configuraciones_procesadas': 0,
        'facturas_encontradas': 0,
        'errores': [],
        'tiempo_ejecucion': None,
        'estado': 'iniciado'
    }
    
    tiempo_inicio = timezone.now()
    
    try:
        # Obtener todas las configuraciones activas
        configuraciones = ConfiguracionSIIAutomaticaCompra.objects.filter(activo=True)
        
        if not configuraciones.exists():
            print("No hay configuraciones automáticas activas")
            resultados['estado'] = 'sin_configuraciones'
            return resultados
        
        print(f"Procesando {configuraciones.count()} configuraciones activas")
        
        for configuracion in configuraciones:
            try:
                print(f"Procesando configuración para holding {configuracion.holding.nombre}")
                
                # Verificar si es hora de ejecutar
                if not es_hora_de_ejecutar(configuracion):
                    print(f"No es hora de ejecutar para {configuracion.holding.nombre}")
                    continue
                
                # Procesar esta configuración
                facturas_encontradas = procesar_configuracion_automatica.delay(configuracion.id)
                
                # Esperar resultado (con timeout)
                resultado_config = facturas_encontradas.get(timeout=600)  # 10 minutos max
                
                resultados['configuraciones_procesadas'] += 1
                resultados['facturas_encontradas'] += resultado_config.get('facturas_nuevas', 0)
                
                print(f"Configuración {configuracion.id} procesada: {resultado_config.get('facturas_nuevas', 0)} facturas nuevas")
                
            except Exception as e:
                error_msg = f"Error procesando configuración {configuracion.id}: {str(e)}"
                print(error_msg)
                print(traceback.format_exc())
                resultados['errores'].append(error_msg)
                
                # Intentar retry si no hemos excedido el límite
                if self.request.retries < self.max_retries:
                    print(f"Reintentando en {self.default_retry_delay} segundos...")
                    self.retry(countdown=self.default_retry_delay)
        
        tiempo_fin = timezone.now()
        resultados['tiempo_ejecucion'] = (tiempo_fin - tiempo_inicio).total_seconds()
        resultados['estado'] = 'completado'
        
        print(f"=== BÚSQUEDA AUTOMÁTICA COMPLETADA ===")
        print(f"Configuraciones procesadas: {resultados['configuraciones_procesadas']}")
        print(f"Facturas encontradas: {resultados['facturas_encontradas']}")
        print(f"Tiempo de ejecución: {resultados['tiempo_ejecucion']:.2f} segundos")
        
        return resultados
        
    except Exception as e:
        print(f"Error crítico en búsqueda automática: {str(e)}")
        print(traceback.format_exc())
        
        resultados['estado'] = 'error'
        resultados['errores'].append(str(e))
        
        # Notificar administradores por email
        enviar_notificacion_error.delay(
            "Error crítico en búsqueda automática de facturas",
            str(e),
            traceback.format_exc()
        )
        
        raise

def calcular_periodo_pdfs(mes: int, ano: int) -> tuple:
    """
    Calcula el período para búsqueda de PDFs (8 días antes del mes hasta último día del mes)
    
    Args:
        mes: Mes del período de facturas
        ano: Año del período de facturas
        
    Returns:
        tuple: (fecha_inicio, fecha_fin) como objetos datetime
    """
    from datetime import datetime, timedelta
    import calendar
    
    # Fecha de inicio: 8 días antes del primer día del mes
    fecha_inicio_mes = datetime(ano, mes, 1)
    fecha_inicio_pdfs = fecha_inicio_mes - timedelta(days=9)
    
    # Fecha de fin: último día del mes
    ultimo_dia_mes = calendar.monthrange(ano, mes)[1]
    fecha_fin_pdfs = datetime(ano, mes, ultimo_dia_mes)
    
    print(f"Período PDFs calculado: {fecha_inicio_pdfs.strftime('%d-%m-%Y')} a {fecha_fin_pdfs.strftime('%d-%m-%Y')}")
    
    return fecha_inicio_pdfs, fecha_fin_pdfs

@shared_task(bind=True, max_retries=2, soft_time_limit=900, time_limit=1200)  
def procesar_configuracion_automatica(self, configuracion_id: int):
    """
    Procesa una configuración específica para buscar facturas y sus PDFs.
    ACTUALIZADO: Usar mes y año dinámicos desde la configuración
    """
    print(f"Procesando configuración ID: {configuracion_id}")
    
    resultado = {
        'configuracion_id': configuracion_id,
        'facturas_nuevas': 0,
        'facturas_actualizadas': 0,
        'pdfs_encontrados': 0,
        'pdfs_descargados': 0,
        'errores': [],
        'estado': 'iniciado',
        'periodo_usado': None
    }
    
    session_manager = None
    browser_session = None
    
    try:
        # Obtener la configuración
        configuracion = ConfiguracionSIIAutomaticaCompra.objects.get(id=configuracion_id)
        
        # NUEVO: Obtener mes y año desde la configuración
        mes_configurado = configuracion.mes
        ano_configurado = configuracion.year
        
        
        resultado['periodo_usado'] = {
            'mes': mes_configurado,
            'ano': ano_configurado,
            
        }
        
        print(f"Configuración obtenida: {configuracion.empresa_nombre}")
        print(f"Período configurado:  (mes={mes_configurado}, año={ano_configurado})")
        
        # Crear sesión del navegador UNA SOLA VEZ
        session_manager = BrowserSessionManager.get_instance()
        user_id = f"auto_{configuracion.holding.id}_{configuracion_id}"
        
        browser_session = session_manager.create_session(user_id)
        driver = browser_session.driver
        wait = browser_session.wait
        
        print(f"Sesión del navegador creada para {user_id}")
        
        # ===== PARTE 1: PROCESO DE FACTURAS =====
        print("="*60)
        print(f"PARTE 1: DESCARGA DE FACTURAS CSV" )
        print("="*60)
        
        # 1. LOGIN EN EL SII
        login_exitoso = realizar_login_automatico(
            driver, wait, 
            configuracion.rut_sii, 
            configuracion.password_sii
        )
        
        if not login_exitoso:
            raise Exception("Error en el login del SII")
        
        # 2. NAVEGAR A PÁGINA DE CONSULTA
        driver.get("https://www4.sii.cl/consdcvinternetui/#/index")
        time.sleep(random.uniform(3.0, 5.0))
        
        # 3. SELECCIONAR EMPRESA Y PERÍODO - USANDO CONFIGURACIÓN DINÁMICA
        seleccionar_empresa_y_periodo(
            driver, wait,
            configuracion.empresa_rut,
            mes_configurado,  # Usar mes de la configuración
            ano_configurado   # Usar año de la configuración
        )
        
        # 4. DESCARGAR CSV
        csv_data = descargar_csv_automatico(driver, wait)
        
        if not csv_data:
            print("No se pudo obtener CSV o está vacío")
            resultado['estado'] = 'sin_datos'
            return resultado
        
        # 5. PROCESAR Y GUARDAR FACTURAS
        facturas_procesadas = procesar_csv_y_guardar_facturas(
            csv_data, 
            configuracion.holding.id
        )
        
        resultado['facturas_nuevas'] = facturas_procesadas['nuevas']
        resultado['facturas_actualizadas'] = facturas_procesadas['actualizadas']
        
        print(f"✅ Facturas procesadas: {resultado['facturas_nuevas']} nuevas, {resultado['facturas_actualizadas']} actualizadas")
        
        # ===== PARTE 2: BÚSQUEDA DE PDFs (USANDO MISMA SESIÓN) =====
        print("="*60)
        print(f"PARTE 2: BÚSQUEDA DE PDFs ")
        print("="*60)
        
        if resultado['facturas_nuevas'] > 0 or resultado['facturas_actualizadas'] > 0:
            try:
                # IMPORTANTE: Usar la misma sesión del navegador (driver, wait)
                # USAR configuración dinámica para PDFs
                resultado_pdfs = buscar_y_descargar_pdfs_facturas(
                    driver, wait,  # ← Misma sesión
                    configuracion.holding.id,
                    ano_configurado,  # Año de la configuración
                    mes_configurado   # Mes de la configuración
                )
                
                resultado['pdfs_encontrados'] = resultado_pdfs['pdfs_encontrados']
                resultado['pdfs_descargados'] = resultado_pdfs['pdfs_descargados']
                resultado['errores'].extend(resultado_pdfs['errores'])
                
                print(f"✅ PDFs procesados: {resultado_pdfs}")
                
            except Exception as e:
                error_msg = f"Error en búsqueda de PDFs: {str(e)}"
                print(error_msg)
                print(traceback.format_exc())
                resultado['errores'].append(error_msg)
        else:
            print("No hay facturas nuevas o actualizadas, omitiendo búsqueda de PDFs")
        
        resultado['estado'] = 'completado'
        
        # ===== RESUMEN FINAL =====
        print("="*60)
        print("RESUMEN FINAL")
        print("="*60)
        print(f"Configuración {configuracion_id} procesada exitosamente")
   
        print(f"📄 Facturas nuevas: {resultado['facturas_nuevas']}")
        print(f"🔄 Facturas actualizadas: {resultado['facturas_actualizadas']}")
        print(f"🔍 PDFs encontrados: {resultado['pdfs_encontrados']}")
        print(f"📥 PDFs descargados: {resultado['pdfs_descargados']}")
        print(f"❌ Errores: {len(resultado['errores'])}")
        
        if resultado['errores']:
            print("Errores encontrados:")
            for i, error in enumerate(resultado['errores'], 1):
                print(f"  {i}. {error}")
        
        return resultado
        
    except Exception as e:
        print(f"Error crítico procesando configuración {configuracion_id}: {str(e)}")
        print(traceback.format_exc())
        
        resultado['estado'] = 'error'
        resultado['errores'].append(str(e))
        
        # Notificar administradores por email si el error es crítico
        if "login" in str(e).lower() or "credenciales" in str(e).lower():
            enviar_notificacion_error.delay(
                f"Error de credenciales en configuración automática {configuracion_id}",
                str(e),
                traceback.format_exc()
            )
        
        return resultado
        
    finally:
        # Limpiar recursos
        if session_manager and browser_session:
            try:
                session_manager.close_session(browser_session.session_id)
                print(f"Sesión del navegador cerrada: {browser_session.session_id}")
            except Exception as cleanup_error:
                print(f"Error cerrando sesión: {str(cleanup_error)}")

# Agregar nueva tarea específica para buscar PDFs de facturas existentes
@shared_task(bind=True, max_retries=2, soft_time_limit=600, time_limit=900)
def buscar_pdfs_facturas_existentes(self, holding_id: int):
    """
    Busca PDFs para facturas existentes que no los tienen.
    ACTUALIZADO: Usar mes y año desde la configuración del holding
    """
    print(f"Buscando PDFs para facturas existentes del holding {holding_id}")
    
    resultado = {
        'holding_id': holding_id,
        'pdfs_encontrados': 0,
        'pdfs_descargados': 0,
        'errores': [],
        'estado': 'iniciado',
        'periodo_usado': None
    }
    
    session_manager = None
    
    try:
        # Obtener configuración del holding
        configuracion = ConfiguracionSIIAutomaticaCompra.objects.get(holding_id=holding_id)
        
        # NUEVO: Usar mes y año de la configuración
        mes_configurado = configuracion.mes
        ano_configurado = configuracion.year
        
        
        resultado['periodo_usado'] = {
            'mes': mes_configurado,
            'ano': ano_configurado,
            
        }
        
        print(f"Usando período configurado")
        
        # Crear sesión del navegador
        session_manager = BrowserSessionManager.get_instance()
        user_id = f"pdf_search_{holding_id}"
        
        browser_session = session_manager.create_session(user_id)
        driver = browser_session.driver
        wait = browser_session.wait
        
        # Login en el SII
        login_exitoso = realizar_login_automatico(
            driver, wait, 
            configuracion.rut_sii, 
            configuracion.password_sii
        )
        
        if not login_exitoso:
            raise Exception("Error en el login del SII para búsqueda de PDFs")
        
        # Buscar PDFs usando configuración dinámica
        resultado_pdfs = buscar_y_descargar_pdfs_facturas(
            driver, wait,
            holding_id,
            ano_configurado,  # Año de la configuración
            mes_configurado   # Mes de la configuración
        )
        
        resultado['pdfs_encontrados'] = resultado_pdfs['pdfs_encontrados']
        resultado['pdfs_descargados'] = resultado_pdfs['pdfs_descargados']
        resultado['errores'] = resultado_pdfs['errores']
        resultado['estado'] = 'completado'
        
        print(f"Búsqueda de PDFs completada para holding {holding_id}: {resultado}")
        
        return resultado
        
    except Exception as e:
        print(f"Error buscando PDFs para holding {holding_id}: {str(e)}")
        resultado['estado'] = 'error'
        resultado['errores'].append(str(e))
        return resultado
        
    finally:
        if session_manager and 'browser_session' in locals():
            try:
                session_manager.close_session(browser_session.session_id)
            except:
                pass

# ==================== FUNCIONES AUXILIARES PARA SELENIUM ====================

def realizar_login_automatico(driver, wait, rut: str, password: str) -> bool:
    """
    Realiza el login automático en el SII.
    """
    try:
        print(f"Iniciando login automático para RUT: {rut}")
        
        # Navegar a la página de login
        driver.get("https://zeusr.sii.cl/AUT2000/InicioAutenticacion/IngresoRutClave.html")
        time.sleep(random.uniform(3.0, 5.0))
        
        # Ingresar RUT
        rut_input = wait.until(EC.presence_of_element_located((By.ID, "rutcntr")))
        rut_input.clear()
        time.sleep(random.uniform(0.5, 1.0))
        
        for char in rut:
            rut_input.send_keys(char)
            time.sleep(random.uniform(0.1, 0.3))
        
        # Ingresar contraseña
        password_input = driver.find_element(By.ID, "clave")
        password_input.clear()
        time.sleep(random.uniform(0.5, 1.0))
        
        for char in password:
            password_input.send_keys(char)
            time.sleep(random.uniform(0.1, 0.3))
        
        # Hacer clic en login
        login_button = driver.find_element(By.ID, "bt_ingresar")
        driver.execute_script("arguments[0].click();", login_button)
        time.sleep(random.uniform(4.0, 6.0))
        
        # Verificar login exitoso
        current_url = driver.current_url
        if any(pattern in current_url for pattern in ["menuIVA", "mipeSelEmpresa", "cgi_AUT2000"]):
            print("Login automático exitoso")
            return True
        
        print(f"Login automático fallido. URL actual: {current_url}")
        return False
        
    except Exception as e:
        print(f"Error en login automático: {str(e)}")
        return False

def seleccionar_empresa_y_periodo(driver, wait, empresa_rut: str, mes: int, ano: int):
    """
    Selecciona empresa, mes y año en la página de consulta.
    CORREGIDO: Formato de RUT con guión y manejo de parámetros como enteros
    """
    try:
        print(f"Seleccionando empresa {empresa_rut}, período {mes:02d}/{ano}")
        
        # CORREGIR FORMATO RUT - Agregar guión si no lo tiene
        if '-' not in str(empresa_rut):
            # Convertir 766678521 a 76667852-1
            rut_str = str(empresa_rut).strip()
            if len(rut_str) >= 8:
                empresa_rut_formatted = f"{rut_str[:-1]}-{rut_str[-1]}"
            else:
                empresa_rut_formatted = empresa_rut
        else:
            empresa_rut_formatted = str(empresa_rut)
        
        print(f"RUT formateado: {empresa_rut} -> {empresa_rut_formatted}")
        
        # Seleccionar empresa
        empresa_select = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "select[ng-model='rut']"))
        )
        empresa_select_obj = Select(empresa_select)
        empresa_select_obj.select_by_value(empresa_rut_formatted)  # Usar RUT con guión
        time.sleep(random.uniform(1.0, 2.0))
        
        # Seleccionar mes - ASEGURAR FORMATO 01, 02, etc.
        # CORREGIDO: mes ya es int, formatear correctamente
        mes_formatted = f"{mes:02d}"
        mes_select = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "select[ng-model='periodoMes']"))
        )
        mes_select_obj = Select(mes_select)
        mes_select_obj.select_by_value(mes_formatted)
        time.sleep(random.uniform(1.0, 2.0))
        
        # Seleccionar año
        # CORREGIDO: ano ya es int, convertir a string
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
        time.sleep(random.uniform(3.0, 5.0))
        
        # Seleccionar tab de compras
        try:
            tab_element = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a[ui-sref='compra']"))
            )
            driver.execute_script("arguments[0].click();", tab_element)
            time.sleep(random.uniform(2.0, 3.0))
        except TimeoutException:
            pass
        
        print("Empresa y período seleccionados exitosamente")
        
    except Exception as e:
        print(f"Error seleccionando empresa y período: {str(e)}")
        raise

def descargar_csv_automatico(driver, wait) -> str:
    """
    Descarga el CSV de detalles de facturas.
    """
    try:
        print("Iniciando descarga de CSV")
        
        # Buscar botón "Descargar Detalles"
        selectores_boton = [
            "//button[contains(text(), 'Descargar Detalles')]",
            "//button[contains(text(), 'Descargar')]",
            "button[ng-click*='descargaDetalle']"
        ]
        
        descargar_btn = None
        for selector in selectores_boton:
            try:
                if selector.startswith("//"):
                    elementos = driver.find_elements(By.XPATH, selector)
                else:
                    elementos = driver.find_elements(By.CSS_SELECTOR, selector)
                
                if elementos:
                    descargar_btn = elementos[0]
                    break
            except:
                continue
        
        if not descargar_btn:
            print("No se encontró el botón de descarga")
            return None
        
        # Hacer clic en el botón
        driver.execute_script("arguments[0].scrollIntoView(true);", descargar_btn)
        time.sleep(random.uniform(1.0, 2.0))
        driver.execute_script("arguments[0].click();", descargar_btn)
        
        # Esperar descarga
        time.sleep(random.uniform(8.0, 12.0))
        
        # Buscar archivo CSV descargado
        downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        csv_data = obtener_csv_mas_reciente(downloads_dir)
        
        if csv_data:
            print(f"CSV descargado exitosamente. Tamaño: {len(csv_data)} caracteres")
            return csv_data
        else:
            print("No se pudo obtener el archivo CSV")
            return None
            
    except Exception as e:
        print(f"Error descargando CSV: {str(e)}")
        return None

def obtener_csv_mas_reciente(directory: str) -> str:
    """
    Obtiene el archivo CSV más reciente del directorio.
    """
    try:
        if not os.path.exists(directory):
            return None
        
        csv_files = [f for f in os.listdir(directory) if f.endswith('.csv')]
        
        if not csv_files:
            return None
        
        # Obtener el más reciente por tiempo de modificación
        archivos_con_tiempo = []
        for archivo in csv_files:
            ruta_completa = os.path.join(directory, archivo)
            tiempo_mod = os.path.getmtime(ruta_completa)
            archivos_con_tiempo.append((archivo, tiempo_mod))
        
        archivos_con_tiempo.sort(key=lambda x: x[1], reverse=True)
        latest_file = archivos_con_tiempo[0][0]
        file_path = os.path.join(directory, latest_file)
        
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        return content
        
    except Exception as e:
        print(f"Error obteniendo CSV más reciente: {str(e)}")
        return None

def procesar_csv_y_guardar_facturas(csv_data: str, holding_id: int) -> Dict[str, int]:
    """
    Procesa el CSV del SII y guarda las facturas nuevas.
    """
    print(f"Procesando CSV para holding {holding_id}")
    
    resultado = {
        'nuevas': 0,
        'actualizadas': 0,
        'errores': 0
    }
    
    try:
        # Parsear CSV usando la misma lógica del sistema manual
        facturas_parseadas = parsear_csv_sii(csv_data)
        
        if not facturas_parseadas:
            print("No se encontraron facturas válidas en el CSV")
            return resultado
        
        print(f"Facturas parseadas del CSV: {len(facturas_parseadas)}")
        
        with transaction.atomic():
            for factura_data in facturas_parseadas:
                try:
                    # Verificar si la factura ya existe (distribuida o por distribuir)
                    folio = factura_data.get('folio', '').strip()
                    rut_proveedor = factura_data.get('rut_proveedor', '').strip()
                    
                    if not folio:
                        continue
                    
                    # Verificar en facturas distribuidas
                    existe_distribuida = FacturaCompraSIIDistribuida.objects.filter(
                        holding_id=holding_id,
                        folio=folio,
                        rut_proveedor=rut_proveedor
                    ).exists()
                    
                    if existe_distribuida:
                        continue  # Ya está distribuida, no hacer nada
                    
                    # Verificar en facturas por distribuir
                    factura_existente = FacturaCompraSIIPorDistribuir.objects.filter(
                        holding_id=holding_id,
                        folio=folio,
                        rut_proveedor=rut_proveedor
                    ).first()
                    
                    if factura_existente:
                        # Actualizar fecha de última verificación
                        factura_existente.save()
                        resultado['actualizadas'] += 1
                    else:
                        # Crear nueva factura por distribuir
                        FacturaCompraSIIPorDistribuir.objects.create(
                            holding_id=holding_id,
                            folio=folio,
                            tipo_doc=factura_data.get('tipo_doc', ''),
                            tipo_compra=factura_data.get('tipo_compra', ''),
                            rut_proveedor=rut_proveedor,
                            razon_social=factura_data.get('razon_social', ''),
                            fecha_docto=factura_data.get('fecha_docto', ''),
                            fecha_recepcion=factura_data.get('fecha_recepcion', ''),
                            fecha_acuse=factura_data.get('fecha_acuse', ''),
                            monto_exento=Decimal(str(factura_data.get('monto_exento', 0))),
                            monto_neto=Decimal(str(factura_data.get('monto_neto', 0))),
                            monto_iva_recuperable=Decimal(str(factura_data.get('iva_recuperable', 0))),
                            monto_iva_no_recuperable=Decimal(str(factura_data.get('iva_no_recuperable', 0))),
                            codigo_iva_no_rec=factura_data.get('codigo_iva_no_rec', ''),
                            monto_total=Decimal(str(factura_data.get('monto_total', 0))),
                            monto_neto_activo_fijo=Decimal(str(factura_data.get('monto_neto_activo_fijo', 0))),
                            iva_activo_fijo=Decimal(str(factura_data.get('iva_activo_fijo', 0))),
                            iva_uso_comun=Decimal(str(factura_data.get('iva_uso_comun', 0))),
                            impto_sin_derecho_credito=Decimal(str(factura_data.get('impto_sin_derecho_credito', 0))),
                            iva_no_retenido=Decimal(str(factura_data.get('iva_no_retenido', 0))),
                            tabacos_puros=Decimal(str(factura_data.get('tabacos_puros', 0))),
                            tabacos_cigarrillos=Decimal(str(factura_data.get('tabacos_cigarrillos', 0))),
                            tabacos_elaborados=Decimal(str(factura_data.get('tabacos_elaborados', 0))),
                            nce_nde_fact_compra=Decimal(str(factura_data.get('nce_nde_fact_compra', 0))),
                            codigo_otro_impuesto=factura_data.get('codigo_otro_impuesto', ''),
                            valor_otro_impuesto=Decimal(str(factura_data.get('valor_otro_impuesto', 0))),
                            tasa_otro_impuesto=Decimal(str(factura_data.get('tasa_otro_impuesto', 0))),
                            procesada=False
                        )
                        resultado['nuevas'] += 1
                        
                except Exception as e:
                    print(f"Error procesando factura individual: {str(e)}")
                    resultado['errores'] += 1
                    continue
        
        print(f"Procesamiento completado. Nuevas: {resultado['nuevas']}, Actualizadas: {resultado['actualizadas']}, Errores: {resultado['errores']}")
        return resultado
        
    except Exception as e:
        print(f"Error procesando CSV y guardando facturas: {str(e)}")
        print(traceback.format_exc())
        raise

def parsear_csv_sii(csv_data: str) -> List[Dict[str, Any]]:
    """
    Parser específico para el formato CSV del SII (reutiliza la lógica del sistema manual).
    """
    try:
        import re
        from decimal import Decimal
        
        lines = csv_data.strip().split('\n')
        if len(lines) < 2:
            return []
        
        # Procesar header
        header_line = lines[0].strip()
        headers = [h.strip() for h in header_line.split(';')]
        
        # Mapeo de campos
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
        
        def clean_string(value):
            if not value or value.lower() in ['', 'nan', 'null', 'none']:
                return ''
            return str(value).strip()
        
        def clean_decimal(value):
            if not value or value.lower() in ['', 'nan', 'null', 'none']:
                return 0.0
            cleaned = str(value).strip().replace(',', '.')
            try:
                return float(cleaned)
            except (ValueError, TypeError):
                return 0.0
        
        def clean_date(value):
            if not value or value.lower() in ['', 'nan', 'null', 'none']:
                return ''
            date_str = str(value).strip()
            if re.match(r'\d{1,2}/\d{1,2}/\d{4}', date_str):
                return date_str
            return date_str
        
        # Procesar filas de datos
        facturas = []
        for line_num, line in enumerate(lines[1:], start=2):
            try:
                line = line.strip()
                if not line:
                    continue
                
                values = line.split(';')
                while len(values) < len(headers):
                    values.append('')
                values = values[:len(headers)]
                
                row_data = {}
                for i, header in enumerate(headers):
                    value = values[i].strip() if i < len(values) else ''
                    field_name = expected_fields.get(header, header.lower().replace(' ', '_'))
                    row_data[field_name] = value
                
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
                    'iva_recuperable': clean_decimal(row_data.get('iva_recuperable', 0)),
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
                    continue
                
                if not factura['razon_social']:
                    factura['razon_social'] = factura['rut_proveedor']
                
                facturas.append(factura)
                
            except Exception as line_error:
                print(f"Error procesando línea {line_num}: {str(line_error)}")
                continue
        
        return facturas
        
    except Exception as e:
        print(f"Error en parser CSV del SII: {str(e)}")
        return []

# ==================== TAREAS DE UTILIDAD ====================

def es_hora_de_ejecutar(configuracion: ConfiguracionSIIAutomaticaCompra) -> bool:
    """
    Verifica si es hora de ejecutar usando zona horaria de Chile
    """
    try:
        import pytz
        from django.utils import timezone
        
        chile_tz = pytz.timezone('America/Santiago')
        ahora_chile = timezone.now().astimezone(chile_tz)
        hora_configurada = configuracion.hora_ejecucion
        
        print(f"DEBUG: Hora actual Chile: {ahora_chile.strftime('%H:%M:%S')}")
        print(f"DEBUG: Hora configurada: {hora_configurada.strftime('%H:%M:%S')}")
        
        # Ejecutar si estamos dentro de una ventana de 10 minutos
        if (ahora_chile.hour == hora_configurada.hour and 
            abs(ahora_chile.minute - hora_configurada.minute) <= 10):
            print(f"DEBUG: ¡Es hora de ejecutar! Configuración ID: {configuracion.id}")
            return True
        
        return False
        
    except Exception as e:
        print(f"Error verificando hora de ejecución: {str(e)}")
        return False

def obtener_mes_desde_configuracion(configuracion_id: int) -> int:
    """
    Obtiene el mes configurado para una configuración específica
    """
    try:
        configuracion = ConfiguracionSIIAutomaticaCompra.objects.get(id=configuracion_id)
        return configuracion.mes
    except ConfiguracionSIIAutomaticaCompra.DoesNotExist:
        print(f"Configuración {configuracion_id} no encontrada, usando mes por defecto")
        return 1  # Enero por defecto

def obtener_ano_desde_configuracion(configuracion_id: int) -> int:
    """
    Obtiene el año configurado para una configuración específica
    """
    try:
        configuracion = ConfiguracionSIIAutomaticaCompra.objects.get(id=configuracion_id)
        return configuracion.year
    except ConfiguracionSIIAutomaticaCompra.DoesNotExist:
        print(f"Configuración {configuracion_id} no encontrada, usando año por defecto")
        return 2025  # 2025 por defecto

def validar_y_convertir_fecha_params(mes, ano):
    """
    Valida y convierte parámetros de fecha a enteros
    """
    try:
        if isinstance(mes, str):
            mes_int = int(mes)
        else:
            mes_int = int(mes)
            
        if isinstance(ano, str):
            ano_int = int(ano)
        else:
            ano_int = int(ano)
            
        # Validaciones básicas
        if not (1 <= mes_int <= 12):
            raise ValueError(f"Mes inválido: {mes_int}")
            
        if not (2000 <= ano_int <= 2100):
            raise ValueError(f"Año inválido: {ano_int}")
            
        return mes_int, ano_int
        
    except (ValueError, TypeError) as e:
        print(f"Error validando parámetros de fecha: {str(e)}")
        raise
    
@shared_task
def verificar_estado_sistema():
    """
    Verifica el estado general del sistema automático.
    """
    try:
        print("Verificando estado del sistema automático")
        
        # Verificar configuraciones activas
        configuraciones_activas = ConfiguracionSIIAutomaticaCompra.objects.filter(activo=True).count()
        
        # Verificar facturas pendientes
        facturas_pendientes = FacturaCompraSIIPorDistribuir.objects.filter(procesada=False).count()
        
        # Log de estado
        print(f"Estado del sistema: {configuraciones_activas} configuraciones activas, {facturas_pendientes} facturas pendientes")
        
        # Si hay muchas facturas pendientes, enviar alerta
        if facturas_pendientes > 100:
            enviar_notificacion_error.delay(
                "Alerta: Muchas facturas pendientes",
                f"Hay {facturas_pendientes} facturas pendientes de distribución",
                "Sistema automático de facturas"
            )
        
    except Exception as e:
        print(f"Error verificando estado del sistema: {str(e)}")

@shared_task
def enviar_notificacion_error(asunto: str, mensaje: str, detalle: str = ""):
    """
    Envía notificación por email cuando hay errores críticos.
    """
    try:
        if hasattr(settings, 'ADMINS') and settings.ADMINS:
            destinatarios = [admin[1] for admin in settings.ADMINS]
            
            mensaje_completo = f"""
            {mensaje}
            
            Detalle:
            {detalle}
            
            Timestamp: {timezone.now()}
            Sistema: Facturas Automáticas SII
            """
            
            send_mail(
                subject=f"[Sistema Automático] {asunto}",
                message=mensaje_completo,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=destinatarios,
                fail_silently=False
            )
            
            print(f"Notificación de error enviada: {asunto}")
        else:
            print("No hay administradores configurados para notificaciones")
            
    except Exception as e:
        print(f"Error enviando notificación: {str(e)}")

@shared_task
def debug_timezone_task():
    """
    Tarea de debug para verificar zonas horarias cada minuto
    """
    try:
        import pytz
        from django.utils import timezone
        
        # Obtener horas en diferentes zonas
        utc_now = timezone.now()
        chile_tz = pytz.timezone('America/Santiago')
        chile_now = utc_now.astimezone(chile_tz)
        
        print(f"=== DEBUG TIMEZONE TASK ===")
        print(f"UTC: {utc_now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"Chile: {chile_now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"Offset: {chile_now.utcoffset().total_seconds() / 3600:.1f} horas")
        
        # Verificar configuraciones activas
        configuraciones = ConfiguracionSIIAutomaticaCompra.objects.filter(activo=True)
        print(f"Configuraciones activas: {configuraciones.count()}")
        
        for config in configuraciones:
            hora_config = config.hora_ejecucion
            print(f"Config {config.id}: {config.empresa_nombre} - Hora: {hora_config.strftime('%H:%M')}")
            
            # Verificar si es hora de ejecutar
            es_hora = es_hora_de_ejecutar(config)
            print(f"  -> ¿Es hora de ejecutar? {es_hora}")
            
            if es_hora:
                print(f"  -> ¡EJECUTANDO CONFIGURACIÓN {config.id}!")
        
        print(f"========================")
        
        return {
            'utc': utc_now.isoformat(),
            'chile': chile_now.isoformat(),
            'configuraciones_activas': configuraciones.count()
        }
        
    except Exception as e:
        print(f"Error en debug timezone task: {str(e)}")
        return {'error': str(e)}

def buscar_y_descargar_pdfs_facturas(driver, wait, holding_id, ano, mes):
    """
    Busca y descarga PDFs de las facturas por distribuir.
    CORREGIDO: Guardar URL con filtros aplicados para regresar después
    """
    print(f"=== INICIANDO BÚSQUEDA DE PDFs ===")
    print(f"Holding: {holding_id}, Año: {ano}, Mes: {mes}")
    
    resultado = {
        'pdfs_encontrados': 0,
        'pdfs_descargados': 0,
        'errores': []
    }
    
    try:
        # VALIDACIÓN OBLIGATORIA de parámetros
        if not ano or not mes:
            error_msg = f"Parámetros faltantes: año={ano}, mes={mes}"
            print(f"❌ {error_msg}")
            resultado['errores'].append(error_msg)
            return resultado
        
        # Validar parámetros
        mes_int, ano_int = validar_y_convertir_fecha_params(mes, ano)
        
        print(f"✅ Parámetros validados: Año={ano_int}, Mes={mes_int}")
        
        # Obtener facturas sin PDF
        facturas_sin_pdf = FacturaCompraSIIPorDistribuir.objects.filter(
            holding_id=holding_id,
            pdf_descargado=False,
            intentos_descarga_pdf__lt=3
        )
        
        print(f"Facturas sin PDF encontradas: {facturas_sin_pdf.count()}")
        
        if not facturas_sin_pdf.exists():
            print("No hay facturas sin PDF para procesar")
            return resultado
        
        # Obtener configuración para el RUT de empresa
        try:
            configuracion = ConfiguracionSIIAutomaticaCompra.objects.get(holding_id=holding_id)
            empresa_rut = configuracion.empresa_rut
            print(f"✅ RUT empresa obtenido: {empresa_rut}")
        except ConfiguracionSIIAutomaticaCompra.DoesNotExist:
            error_msg = f"No se encontró configuración para holding {holding_id}"
            resultado['errores'].append(error_msg)
            return resultado
        
        # 1. SELECCIONAR EMPRESA PARA PDFs
        print("=== PASO 1: SELECCIONANDO EMPRESA PARA PDFs ===")
        if not seleccionar_empresa_para_pdfs(driver, wait, empresa_rut):
            error_msg = f"Error al seleccionar empresa {empresa_rut}"
            resultado['errores'].append(error_msg)
            return resultado
        
        # 2. NAVEGAR A ADMINISTRACIÓN DE DOCUMENTOS
        print("=== PASO 2: NAVEGANDO A ADMINISTRACIÓN DE DOCUMENTOS ===")
        url_admin_docs = f"https://www1.sii.cl/cgi-bin/Portal001/mipeAdminDocsRcp.cgi?RUT_EMI=&FOLIO=&RZN_SOC=&FEC_DESDE=&FEC_HASTA=&TPO_DOC=&ESTADO=&ORDEN=&NUM_PAG=1"
        
        driver.get(url_admin_docs)
        time.sleep(random.uniform(3.0, 5.0))
        print(f"✅ Navegado a: {driver.current_url}")
        
        # 3. CONFIGURAR FILTROS UNA SOLA VEZ
        print("=== PASO 3: CONFIGURANDO FILTROS DE BÚSQUEDA ===")
        print(f"Configurando filtros para período: {mes_int:02d}/{ano_int}")
        
        if not configurar_filtros_busqueda_pdf(driver, wait, ano_int, mes_int):
            error_msg = "Error al configurar filtros de búsqueda"
            resultado['errores'].append(error_msg)
            return resultado
        
        # ===== CAMBIO MÍNIMO 1: GUARDAR URL CON FILTROS =====
        url_con_filtros = driver.current_url
        print(f"✅ URL con filtros guardada: {url_con_filtros}")
        
        # 4. BUSCAR PDFs USANDO LA TABLA YA CARGADA
        print("=== PASO 4: BUSCANDO PDFs EN TABLA CARGADA ===")
        facturas_a_procesar = list(facturas_sin_pdf[:10])  # Procesar máximo 10
        print(f"Procesando {len(facturas_a_procesar)} facturas")
        
        for i, factura in enumerate(facturas_a_procesar, 1):
            print(f"--- Procesando factura {i}/{len(facturas_a_procesar)}: {factura.folio} ---")
            try:
                # ===== CAMBIO MÍNIMO 2: PASAR URL CON FILTROS =====
                pdf_descargado = buscar_y_descargar_pdf_factura(driver, wait, factura, url_con_filtros)
                if pdf_descargado:
                    resultado['pdfs_descargados'] += 1
                    print(f"✅ PDF descargado para factura {factura.folio}")
                else:
                    print(f"⚠️ No se pudo descargar PDF para factura {factura.folio}")
                
                resultado['pdfs_encontrados'] += 1
                    
            except Exception as e:
                error_msg = f"Error procesando factura {factura.folio}: {str(e)}"
                print(error_msg)
                resultado['errores'].append(error_msg)
                
                # Incrementar intentos fallidos
                factura.intentos_descarga_pdf += 1
                factura.error_descarga_pdf = str(e)
                factura.save()
        
        print(f"=== BÚSQUEDA DE PDFs COMPLETADA ===")
        print(f"Resultado final: {resultado}")
        return resultado
        
    except Exception as e:
        error_msg = f"Error general en búsqueda de PDFs: {str(e)}"
        print(error_msg)
        print(traceback.format_exc())
        resultado['errores'].append(error_msg)
        return resultado

def seleccionar_empresa_para_pdfs(driver, wait, empresa_rut):
    """
    Selecciona la empresa en la URL de selección para PDFs.
    VERSIÓN MEJORADA con mejor debugging
    """
    try:
        print(f"🏢 Seleccionando empresa: {empresa_rut}")
        
        # URL para seleccionar empresa
        url_seleccion = "https://www1.sii.cl/cgi-bin/Portal001/mipeSelEmpresa.cgi?DESDE_DONDE_URL=OPCION%3D1%26TIPO%3D4"
        print(f"Navegando a: {url_seleccion}")
        
        driver.get(url_seleccion)
        time.sleep(5)
        
        print(f"URL actual: {driver.current_url}")
        print(f"Título: {driver.title}")
        
        # Buscar el select de empresas
        try:
            select_empresas = wait.until(
                EC.presence_of_element_located((By.NAME, "RUT_EMP"))
            )
            print("✅ Select de empresas encontrado")
        except TimeoutException:
            print("❌ No se encontró el select de empresas")
            return False
        
        # Preparar diferentes formatos del RUT
        def formatear_rut_con_guion(rut_str):
            rut_str = str(rut_str).strip()
            if '-' in rut_str:
                return rut_str
            if len(rut_str) >= 2:
                return f"{rut_str[:-1]}-{rut_str[-1]}"
            return rut_str
        
        empresa_rut_str = str(empresa_rut).strip()
        rut_con_guion = formatear_rut_con_guion(empresa_rut_str)
        rut_sin_guion = empresa_rut_str.replace('-', '')
        
        print(f"RUT original: {empresa_rut_str}")
        print(f"RUT con guión: {rut_con_guion}")
        print(f"RUT sin guión: {rut_sin_guion}")
        
        # Obtener opciones y buscar coincidencia
        from selenium.webdriver.support.ui import Select
        select_obj = Select(select_empresas)
        opciones = select_obj.options
        
        print(f"Opciones disponibles ({len(opciones)}):")
        for i, opcion in enumerate(opciones[:5]):  # Solo mostrar primeras 5
            value = opcion.get_attribute('value')
            text = opcion.text[:50]  # Truncar texto
            print(f"  {i}: value='{value}' text='{text}'")
        
        # Buscar empresa por coincidencia exacta
        empresa_encontrada = False
        for opcion in opciones:
            value = opcion.get_attribute('value')
            if value in [rut_con_guion, rut_sin_guion, empresa_rut_str]:
                print(f"✅ Empresa encontrada: {value}")
                select_obj.select_by_value(value)
                empresa_encontrada = True
                break
        
        if not empresa_encontrada:
            print(f"❌ Empresa {empresa_rut} no encontrada en las opciones")
            return False
        
        # Enviar formulario
        print("Enviando formulario...")
        try:
            boton_enviar = driver.find_element(By.XPATH, "//button[@type='submit'] | //input[@type='submit']")
            boton_enviar.click()
            time.sleep(5)
        except Exception as e:
            print(f"❌ Error enviando formulario: {str(e)}")
            return False
        
        # Verificar éxito
        print(f"URL después de selección: {driver.current_url}")
        print(f"Título después de selección: {driver.title}")
        
        if "mipeSelEmpresa" in driver.current_url:
            print("❌ Seguimos en página de selección")
            return False
        
        print(f"✅ Empresa {empresa_rut} seleccionada exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error seleccionando empresa: {str(e)}")
        print(traceback.format_exc())
        return False

def configurar_filtros_busqueda_pdf(driver, wait, ano, mes):
    """
    Configura los filtros de fecha para buscar documentos en el período específico.
    CORREGIDO: Usar formato YYYY-MM-DD consistente y fechas dinámicas
    """
    try:
        # Validar y convertir parámetros
        mes_int = int(mes) if isinstance(mes, str) else mes
        ano_int = int(ano) if isinstance(ano, str) else ano
        
        print(f"📅 Configurando filtros para {mes_int:02d}/{ano_int}")
        
        # Calcular fechas del período (9 días antes del mes hasta último día del mes)
        from datetime import datetime, timedelta
        import calendar
        
        # Fecha de inicio: 9 días antes del primer día del mes
        fecha_inicio_mes = datetime(ano_int, mes_int, 1)
        fecha_inicio = fecha_inicio_mes - timedelta(days=9)
        
        # Fecha de fin: último día del mes
        ultimo_dia_mes = calendar.monthrange(ano_int, mes_int)[1]
        fecha_fin = datetime(ano_int, mes_int, ultimo_dia_mes)
        
        # CORRECCIÓN CRÍTICA: Usar formato YYYY-MM-DD para campos del SII
        fecha_desde = fecha_inicio.strftime("%Y-%m-%d")
        fecha_hasta = fecha_fin.strftime("%Y-%m-%d")
        
        print(f"Período de búsqueda CORREGIDO: {fecha_desde} a {fecha_hasta}")
        
        # Verificar que estamos en la página correcta
        print(f"URL actual: {driver.current_url}")
        
        # Esperar a que la página se cargue completamente
        time.sleep(5)
        
        # PASO 1: Expandir panel de filtros si está colapsado
        try:
            print("Verificando panel de filtros...")
            panel_colapsado = driver.find_elements(By.CSS_SELECTOR, "#collapseFiltro.collapse:not(.in)")
            if panel_colapsado:
                print("Panel de filtros colapsado, expandiendo...")
                toggle_button = driver.find_element(By.CSS_SELECTOR, "a[href='#collapseFiltro']")
                driver.execute_script("arguments[0].click();", toggle_button)
                time.sleep(3)
                print("✅ Panel de filtros expandido")
        except Exception as e:
            print(f"Error expandiendo panel: {str(e)}")
        
        # PASO 2: Configurar fecha desde
        print("Configurando fecha desde...")
        try:
            campo_fecha_desde = wait.until(
                EC.presence_of_element_located((By.NAME, "FEC_DESDE"))
            )
            
            # CORRECCIÓN: Limpiar completamente y usar formato correcto
            driver.execute_script("arguments[0].value = '';", campo_fecha_desde)
            driver.execute_script("arguments[0].setAttribute('value', '');", campo_fecha_desde)
            time.sleep(1)
            
            # Establecer valor usando JavaScript para asegurar formato correcto
            driver.execute_script(f"arguments[0].value = '{fecha_desde}';", campo_fecha_desde)
            time.sleep(1)
            
            valor_actual = campo_fecha_desde.get_attribute('value')
            print(f"✅ Fecha desde configurada: {fecha_desde} -> {valor_actual}")
            
        except Exception as e:
            print(f"❌ Error configurando fecha desde: {str(e)}")
            return False
        
        # PASO 3: Configurar fecha hasta
        print("Configurando fecha hasta...")
        try:
            campo_fecha_hasta = driver.find_element(By.NAME, "FEC_HASTA")
            
            # CORRECCIÓN: Limpiar completamente y usar formato correcto
            driver.execute_script("arguments[0].value = '';", campo_fecha_hasta)
            driver.execute_script("arguments[0].setAttribute('value', '');", campo_fecha_hasta)
            time.sleep(1)
            
            # Establecer valor usando JavaScript
            driver.execute_script(f"arguments[0].value = '{fecha_hasta}';", campo_fecha_hasta)
            time.sleep(1)
            
            valor_actual = campo_fecha_hasta.get_attribute('value')
            print(f"✅ Fecha hasta configurada: {fecha_hasta} -> {valor_actual}")
            
        except Exception as e:
            print(f"❌ Error configurando fecha hasta: {str(e)}")
            return False
        
        # PASO 4: Hacer clic en buscar
        print("Iniciando búsqueda...")
        try:
            boton_buscar = driver.find_element(By.CSS_SELECTOR, "input[onclick='verificaCampos()']")
            print("✅ Botón de búsqueda encontrado")
            
            # Scroll y click
            driver.execute_script("arguments[0].scrollIntoView(true);", boton_buscar)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", boton_buscar)
            
            print("✅ Búsqueda iniciada, esperando resultados...")
            time.sleep(8)  # Esperar que carguen los resultados
            
        except Exception as e:
            print(f"❌ Error haciendo búsqueda: {str(e)}")
            return False
        
        # PASO 5: Verificar resultados
        print(f"URL después de búsqueda: {driver.current_url}")
        
        # Verificar si hay tabla de resultados
        try:
            wait.until(EC.presence_of_element_located((By.ID, "tablaDatos")))
            print("✅ Tabla de resultados encontrada")
            return True
        except TimeoutException:
            print("⚠️ No se encontró tabla de resultados en tiempo esperado")
            return True  # Continuar porque puede que no haya datos
            
    except Exception as e:
        print(f"❌ Error crítico configurando filtros: {str(e)}")
        print(traceback.format_exc())
        return False

def buscar_y_descargar_pdf_factura(driver, wait, factura, url_con_filtros=None):
    """
    Busca una factura específica en la tabla y descarga su PDF.
    CORREGIDO: Regresar a tabla principal si es necesario usando URL con filtros
    """
    try:
        print(f"🔍 Buscando PDF para factura {factura.folio} - RUT {factura.rut_proveedor}")
        
        # ===== CAMBIO MÍNIMO 3: VERIFICAR Y REGRESAR SI ES NECESARIO =====
        current_url = driver.current_url
        print(f"URL actual: {current_url}")
        
        # Verificar que estemos en la página de administración de documentos
        if "mipeAdminDocsRcp.cgi" not in current_url:
            if url_con_filtros:
                print(f"🔄 Regresando a tabla principal: {url_con_filtros}")
                driver.get(url_con_filtros)
                time.sleep(random.uniform(3.0, 5.0))
                print("✅ De vuelta en tabla principal")
            else:
                print("❌ No estamos en la página correcta de administración de documentos")
                return False
        
        # ===== RESTO DEL CÓDIGO IGUAL (sin cambios) =====
        codigo_sii = buscar_codigo_factura_en_tabla(driver, wait, factura.folio, factura.rut_proveedor)
        
        if not codigo_sii:
            error_msg = f"Factura {factura.folio} - {factura.rut_proveedor} no encontrada en la tabla del SII"
            print(f"⚠️ {error_msg}")
            
            factura.intentos_descarga_pdf += 1
            factura.error_descarga_pdf = error_msg
            factura.save()
            return False
        
        print(f"✅ Código SII encontrado: {codigo_sii}")
        
        # ===== GUARDAR CÓDIGO Y CONTINUAR =====
        factura.codigo_sii = codigo_sii
        factura.save()
        
        # ===== NAVEGAR A PÁGINA DE DETALLE =====
        url_detalle = f"https://www1.sii.cl/cgi-bin/Portal001/mipeGesDocRcp.cgi?CODIGO={codigo_sii}&ALL_PAGE_ANT=2"
        print(f"Navegando a detalle: {url_detalle}")
        
        driver.get(url_detalle)
        time.sleep(random.uniform(4.0, 6.0))
        
        # ===== BUSCAR Y DESCARGAR PDF =====
        try:
            print("Buscando link de PDF...")
            
            selectores_pdf = [
                "//a[contains(text(), 'VISUALIZACIÓN DOCUMENTO (pdf)')]",
                "//a[contains(text(), 'VISUALIZACIÓN DOCUMENTO')]",
                "//a[contains(text(), 'PDF')]",
                "//a[contains(text(), 'pdf')]",
                "//a[contains(@href, 'mipeShowPdf')]",
                "//a[contains(@href, 'pdf')]"
            ]
            
            link_pdf = None
            for selector in selectores_pdf:
                try:
                    link_pdf = driver.find_element(By.XPATH, selector)
                    print(f"✅ Link PDF encontrado con selector: {selector}")
                    break
                except:
                    continue
            
            if not link_pdf:
                error_msg = f"Link de PDF no encontrado para factura {factura.folio}"
                print(f"❌ {error_msg}")
                factura.intentos_descarga_pdf += 1
                factura.error_descarga_pdf = error_msg
                factura.save()
                return False
            
            # ===== DESCARGAR PDF =====
            url_pdf = link_pdf.get_attribute('href')
            print(f"✅ URL del PDF: {url_pdf}")
            
            pdf_content = descargar_pdf_desde_url(url_pdf, driver)
            
            if pdf_content:
                filename = f"factura_{factura.rut_proveedor}_{factura.folio}_{factura.id}.pdf"
                factura.pdf_documento.save(
                    filename,
                    ContentFile(pdf_content),
                    save=False
                )
                factura.pdf_descargado = True
                factura.fecha_descarga_pdf = timezone.now()
                factura.error_descarga_pdf = None
                factura.save()
                
                print(f"✅ PDF descargado y guardado para factura {factura.folio}")
                return True
            else:
                error_msg = "No se pudo descargar el contenido del PDF"
                print(f"❌ {error_msg}")
                factura.intentos_descarga_pdf += 1
                factura.error_descarga_pdf = error_msg
                factura.save()
                return False
                
        except Exception as e:
            error_msg = f"Error buscando/descargando PDF: {str(e)}"
            print(f"❌ {error_msg}")
            factura.intentos_descarga_pdf += 1
            factura.error_descarga_pdf = error_msg
            factura.save()
            return False
            
    except Exception as e:
        error_msg = f"Error general descargando PDF para factura {factura.folio}: {str(e)}"
        print(f"❌ {error_msg}")
        print(traceback.format_exc())
        factura.intentos_descarga_pdf += 1
        factura.error_descarga_pdf = error_msg
        factura.save()
        return False
    
def buscar_codigo_factura_en_tabla(driver, wait, folio, rut_proveedor):
    """
    Versión mejorada de búsqueda en tabla con mejor manejo de DataTables
    CORREGIDO: Mejorar normalización de RUT para coincidencias exactas
    """
    try:
        print(f"🔍 Buscando factura: folio={folio}, RUT={rut_proveedor}")
        
        # PASO 1: Esperar que la página se cargue completamente
        print("⏱️ Esperando carga completa de la página...")
        time.sleep(8)
        
        # PASO 2: Asegurar que DataTables esté cargado
        max_intentos = 15
        for intento in range(max_intentos):
            try:
                tabla = driver.find_element(By.ID, "tablaDatos")
                loading_elements = driver.find_elements(By.CSS_SELECTOR, 
                    ".dataTables_processing, [class*='loading']")
                
                loading_visible = any(elem.is_displayed() for elem in loading_elements if elem.is_displayed())
                
                if not loading_visible and tabla.is_displayed():
                    print(f"✅ Tabla cargada completamente (intento {intento + 1})")
                    break
                    
                print(f"⏳ Esperando carga completa... intento {intento + 1}/{max_intentos}")
                time.sleep(2)
                
            except Exception:
                print(f"⏳ Tabla no disponible aún... intento {intento + 1}/{max_intentos}")
                time.sleep(2)
        
        time.sleep(3)  # Espera adicional de seguridad
        
        # PASO 3: Obtener todas las filas
        try:
            filas = []
            
            # Estrategia 1: Filas en tbody
            try:
                tbody = driver.find_element(By.CSS_SELECTOR, "#tablaDatos tbody")
                filas_tbody = tbody.find_elements(By.TAG_NAME, "tr")
                filas.extend(filas_tbody)
            except:
                pass
            
            # Estrategia 2: Todas las filas de la tabla
            try:
                tabla = driver.find_element(By.ID, "tablaDatos")
                filas_tabla = tabla.find_elements(By.TAG_NAME, "tr")
                for fila in filas_tabla:
                    if fila.find_elements(By.TAG_NAME, "td"):  # Solo filas con celdas td
                        filas.append(fila)
            except:
                pass
            
            # Remover duplicados
            filas_unicas = []
            for fila in filas:
                if fila not in filas_unicas:
                    filas_unicas.append(fila)
            
            filas = filas_unicas
            
        except Exception as e:
            print(f"❌ Error obteniendo filas: {str(e)}")
            return None
        
        print(f"📊 Total de filas encontradas: {len(filas)}")
        
        if len(filas) == 0:
            print("❌ No se encontraron filas en la tabla")
            return None
        
        # PASO 4: Mejorar normalización de RUT
        def normalizar_rut_mejorado(rut_str):
            """Normaliza RUT con múltiples variaciones"""
            if not rut_str:
                return ""
            
            # Limpiar espacios, puntos y guiones
            rut_limpio = str(rut_str).replace('.', '').replace(' ', '').replace('-', '').strip()
            
            # Si tiene dígito verificador separado, juntarlo
            if len(rut_limpio) >= 2:
                return rut_limpio
            
            return rut_limpio
        
        # PASO 5: Buscar con múltiples variaciones de RUT
        def generar_variaciones_rut(rut_original):
            """Genera diferentes variaciones del RUT para buscar"""
            rut_base = normalizar_rut_mejorado(rut_original)
            
            variaciones = [
                rut_base,  # Sin guión: 142896796
                rut_original,  # Original: 14289679-6
            ]
            
            # Si no tiene guión, agregar con guión
            if '-' not in rut_original and len(rut_base) >= 2:
                rut_con_guion = f"{rut_base[:-1]}-{rut_base[-1]}"
                variaciones.append(rut_con_guion)
            
            # Si tiene guión, agregar sin guión
            if '-' in rut_original:
                rut_sin_guion = rut_original.replace('-', '')
                variaciones.append(rut_sin_guion)
            
            return list(set(variaciones))  # Eliminar duplicados
        
        variaciones_rut = generar_variaciones_rut(rut_proveedor)
        folio_buscar = str(folio).strip()
        
        print(f"🎯 Buscando Folio='{folio_buscar}', RUT variaciones: {variaciones_rut}")
        
        # DEBUG: Mostrar estructura de primeras filas
        for i, fila in enumerate(filas[:3]):
            try:
                celdas = fila.find_elements(By.TAG_NAME, "td")
                if len(celdas) >= 5:
                    print(f"DEBUG fila {i}: {[c.text.strip()[:15] for c in celdas[:5]]}")
            except:
                pass
        
        # PASO 6: Buscar coincidencia con todas las variaciones
        for i, fila in enumerate(filas):
            try:
                celdas = fila.find_elements(By.TAG_NAME, "td")
                
                if len(celdas) >= 5:
                    # Columnas: 0=Ver, 1=Emisor, 2=Razón, 3=Documento, 4=Folio
                    rut_fila_original = celdas[1].text.strip()
                    rut_fila_normalizado = normalizar_rut_mejorado(rut_fila_original)
                    folio_fila = celdas[4].text.strip()
                    
                    # Verificar coincidencia de folio
                    if folio_fila == folio_buscar:
                        # Verificar cualquier variación de RUT
                        rut_coincide = False
                        for var_rut in variaciones_rut:
                            var_normalizada = normalizar_rut_mejorado(var_rut)
                            if (var_normalizada == rut_fila_normalizado or 
                                var_rut == rut_fila_original):
                                rut_coincide = True
                                break
                        
                        if rut_coincide:
                            print(f"🎉 ¡FACTURA ENCONTRADA en fila {i+1}!")
                            print(f"   Folio: {folio_fila} == {folio_buscar}")
                            print(f"   RUT: {rut_fila_original} coincide con variaciones de {rut_proveedor}")
                            
                            # Extraer código del link en columna 0
                            try:
                                link_ver = celdas[0].find_element(By.TAG_NAME, "a")
                                href = link_ver.get_attribute('href')
                                print(f"🔗 Link encontrado: {href}")
                                
                                # Extraer código usando regex
                                import re
                                match = re.search(r'CODIGO=([^&]+)', href)
                                if match:
                                    codigo = match.group(1)
                                    print(f"✅ Código SII extraído: {codigo}")
                                    return codigo
                                else:
                                    print("❌ No se pudo extraer código del href")
                                    
                            except Exception as e:
                                print(f"❌ Error extrayendo código: {str(e)}")
                            
                            return None
                        
            except Exception as e:
                print(f"❌ Error procesando fila {i+1}: {str(e)}")
                continue
        
        print(f"❌ Factura {folio_buscar} - {rut_proveedor} no encontrada en {len(filas)} filas")
        print(f"   Variaciones buscadas: {variaciones_rut}")
        return None
        
    except Exception as e:
        print(f"❌ Error crítico buscando en tabla: {str(e)}")
        print(traceback.format_exc())
        return None
  
def descargar_pdf_desde_url(url_pdf, driver):
    """
    Descarga el contenido del PDF desde la URL usando las cookies de la sesión.
    CORREGIDO: Mejor validación y manejo de errores.
    """
    try:
        print(f"⬇️ Descargando PDF desde: {url_pdf}")
        
        # ===== PASO 1: PREPARAR SESIÓN CON COOKIES =====
        cookies = driver.get_cookies()
        print(f"Cookies obtenidas: {len(cookies)}")
        
        session = requests.Session()
        for cookie in cookies:
            session.cookies.set(cookie['name'], cookie['value'])
        
        # ===== PASO 2: CONFIGURAR HEADERS =====
        headers = {
            'User-Agent': driver.execute_script("return navigator.userAgent;"),
            'Accept': 'application/pdf,application/octet-stream,*/*',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Referer': driver.current_url
        }
        
        # ===== PASO 3: REALIZAR DESCARGA =====
        print("Realizando petición HTTP...")
        
        response = session.get(
            url_pdf, 
            headers=headers, 
            timeout=30,
            stream=True  # Para manejar archivos grandes
        )
        
        response.raise_for_status()
        
        print(f"Respuesta HTTP: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'N/A')}")
        
        # ===== PASO 4: VALIDAR CONTENIDO =====
        content = response.content
        print(f"Tamaño descargado: {len(content)} bytes")
        
        # Verificar que es un PDF válido
        content_type = response.headers.get('content-type', '').lower()
        
        if 'pdf' in content_type:
            print("✅ Content-Type indica PDF")
        elif content.startswith(b'%PDF'):
            print("✅ Contenido comienza con signature de PDF")
        else:
            # Verificar si es HTML de error
            if content.startswith(b'<!DOCTYPE') or content.startswith(b'<html'):
                content_str = content.decode('utf-8', errors='ignore')[:500]
                print(f"❌ Recibido HTML en lugar de PDF: {content_str}")
                return None
            else:
                print(f"⚠️ Content-Type no es PDF pero el contenido parece binario")
        
        # Verificar tamaño mínimo (un PDF válido debe tener al menos unos pocos KB)
        if len(content) < 1024:  # Menos de 1KB es sospechoso
            print(f"❌ Archivo muy pequeño: {len(content)} bytes")
            return None
        
        print(f"✅ PDF válido descargado exitosamente")
        return content
        
    except requests.exceptions.Timeout:
        print(f"❌ Timeout descargando PDF (30s)")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de red descargando PDF: {str(e)}")
        return None
    except Exception as e:
        print(f"❌ Error inesperado descargando PDF: {str(e)}")
        print(traceback.format_exc())
        return None
    
def verificar_disponibilidad_pdf(driver, wait, codigo_sii):
    """
    Verifica que el PDF esté disponible antes de intentar descargarlo
    """
    try:
        # Navegar a la página de detalle
        url_detalle = f"https://www1.sii.cl/cgi-bin/Portal001/mipeGesDocRcp.cgi?CODIGO={codigo_sii}&ALL_PAGE_ANT=2"
        print(f"Verificando disponibilidad de PDF: {url_detalle}")
        
        driver.get(url_detalle)
        time.sleep(random.uniform(2.0, 4.0))
        
        # Buscar el link de visualización PDF
        selectores_pdf = [
            "//a[contains(text(), 'VISUALIZACIÓN DOCUMENTO (pdf)')]",
            "//a[contains(text(), 'VISUALIZACIÓN DOCUMENTO')]",
            "//a[contains(text(), 'PDF')]",
            "//a[contains(text(), 'pdf')]",
            "//a[contains(@href, 'mipeShowPdf')]"
        ]
        
        for selector in selectores_pdf:
            try:
                link_pdf = driver.find_element(By.XPATH, selector)
                print(f"✅ Link PDF encontrado: {selector}")
                return True
            except NoSuchElementException:
                continue
        
        print("⚠️ No se encontró link de PDF disponible")
        return False
        
    except Exception as e:
        print(f"❌ Error verificando disponibilidad de PDF: {str(e)}")
        return False

def descargar_pdf_factura_individual(driver, wait, factura, codigo_sii):
    """
    Descarga el PDF de una factura individual usando su código SII.
    CORREGIDO: Flujo mejorado y mejor manejo de errores.
    """
    try:
        print(f"📥 Descargando PDF para factura {factura.folio}")
        
        # ===== PASO 1: IR A PÁGINA DE DETALLE =====
        url_detalle = f"https://www1.sii.cl/cgi-bin/Portal001/mipeGesDocRcp.cgi?CODIGO={codigo_sii}&ALL_PAGE_ANT=2"
        print(f"Navegando a detalle: {url_detalle}")
        
        driver.get(url_detalle)
        time.sleep(random.uniform(3.0, 5.0))
        
        # ===== PASO 2: BUSCAR LINK DEL PDF =====
        print("Buscando link de PDF...")
        
        selectores_pdf = [
            "//a[contains(text(), 'VISUALIZACIÓN DOCUMENTO (pdf)')]",
            "//a[contains(text(), 'VISUALIZACIÓN DOCUMENTO')]",
            "//a[contains(text(), 'PDF')]",
            "//a[contains(text(), 'pdf')]",
            "//a[contains(@href, 'mipeShowPdf')]"
        ]
        
        link_pdf = None
        for selector in selectores_pdf:
            try:
                link_pdf = driver.find_element(By.XPATH, selector)
                print(f"✅ Link PDF encontrado: {selector}")
                break
            except NoSuchElementException:
                continue
        
        if not link_pdf:
            error_msg = f"Link de PDF no encontrado para factura {factura.folio}"
            print(f"❌ {error_msg}")
            
            factura.intentos_descarga_pdf += 1
            factura.error_descarga_pdf = error_msg
            factura.save()
            return False
        
        # ===== PASO 3: OBTENER URL DEL PDF =====
        url_pdf = link_pdf.get_attribute('href')
        print(f"✅ URL del PDF: {url_pdf}")
        
        # ===== PASO 4: DESCARGAR CONTENIDO DEL PDF =====
        pdf_content = descargar_pdf_desde_url(url_pdf, driver)
        
        if not pdf_content:
            error_msg = "No se pudo descargar el contenido del PDF"
            print(f"❌ {error_msg}")
            
            factura.intentos_descarga_pdf += 1
            factura.error_descarga_pdf = error_msg
            factura.save()
            return False
        
        # ===== PASO 5: GUARDAR PDF EN EL MODELO =====
        try:
            filename = f"factura_{factura.rut_proveedor}_{factura.folio}_{factura.id}.pdf"
            factura.pdf_documento.save(
                filename,
                ContentFile(pdf_content),
                save=False
            )
            
            # Actualizar campos de estado
            factura.pdf_descargado = True
            factura.fecha_descarga_pdf = timezone.now()
            factura.error_descarga_pdf = None
            factura.save()
            
            print(f"✅ PDF guardado exitosamente: {filename}")
            return True
            
        except Exception as e:
            error_msg = f"Error guardando PDF: {str(e)}"
            print(f"❌ {error_msg}")
            
            factura.intentos_descarga_pdf += 1
            factura.error_descarga_pdf = error_msg
            factura.save()
            return False
            
    except Exception as e:
        error_msg = f"Error descargando PDF para factura {factura.folio}: {str(e)}"
        print(f"❌ {error_msg}")
        print(traceback.format_exc())
        
        factura.intentos_descarga_pdf += 1
        factura.error_descarga_pdf = error_msg
        factura.save()
        return False

def configurar_filtros_periodo_pdfs(driver, wait, mes: int, ano: int):
    """
    Configura los filtros de período para búsqueda de PDFs.
    ACTUALIZADO: Usar el período calculado con 8 días de anticipación
    """
    try:
        print(f"📅 Configurando filtros PDFs para período: {mes:02d}/{ano}")
        
        # Calcular período para PDFs (9 días antes del mes hasta último día del mes)
        fecha_inicio_pdfs, fecha_fin_pdfs = calcular_periodo_pdfs(mes, ano)
        
        # Formatear fechas para el SII (DD-MM-YYYY)
        fecha_desde = fecha_inicio_pdfs.strftime("%d-%m-%Y")
        fecha_hasta = fecha_fin_pdfs.strftime("%d-%m-%Y")
        
        print(f"Período PDFs: {fecha_desde} a {fecha_hasta}")
        
        # Resto de la lógica existente para configurar filtros...
        # [El código existente de configurar_filtros_periodo_pdfs continúa aquí]
        
    except Exception as e:
        print(f"Error configurando filtros de período PDFs: {str(e)}")
        raise

#===========================FACTURAS VENTAS AUTOMATICAS =============================

# ==================== TAREA PRINCIPAL ====================

@shared_task
def revisar_configuraciones_venta_pendientes():
    """Revisa configuraciones de venta y ejecuta las que corresponden a la hora actual"""
    from datetime import datetime
    import pytz
    from django.utils import timezone
    
    print("Revisando configuraciones automáticas de venta...")
    
    try:
        chile_tz = pytz.timezone('America/Santiago')
        ahora_chile = timezone.now().astimezone(chile_tz)
        hora_actual = ahora_chile.time()
        
        configuraciones_activas = ConfiguracionSIIAutomaticaVenta.objects.filter(activo=True)
        print(f"Hora actual: {hora_actual.strftime('%H:%M')}")
        
        for config in configuraciones_activas:
            hora_config = config.hora_ejecucion
            minutos_actual = hora_actual.hour * 60 + hora_actual.minute
            minutos_config = hora_config.hour * 60 + hora_config.minute
            
            # Si la hora coincide (con 1 minuto de tolerancia)
            if abs(minutos_actual - minutos_config) <= 1:
                print(f"⏰ Ejecutando configuración de venta {config.id}")
                procesar_configuracion_venta_automatica.delay(config.id)
        
        return f"Revisión de venta completada a las {hora_actual.strftime('%H:%M')}"
        
    except Exception as e:
        print(f"Error en revisión de venta: {str(e)}")
        return f"Error: {str(e)}"

@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def buscar_facturas_venta_automaticamente(self):
    """
    Tarea principal que busca facturas de venta automáticamente para todas las configuraciones activas.
    """
    print("=== INICIANDO BÚSQUEDA AUTOMÁTICA DE FACTURAS DE VENTA ===")
    
    resultados = {
        'configuraciones_procesadas': 0,
        'facturas_encontradas': 0,
        'errores': [],
        'tiempo_ejecucion': None,
        'estado': 'iniciado'
    }
    
    tiempo_inicio = timezone.now()
    
    try:
        # Obtener todas las configuraciones activas de venta
        configuraciones = ConfiguracionSIIAutomaticaVenta.objects.filter(activo=True)
        
        if not configuraciones.exists():
            print("No hay configuraciones automáticas de venta activas")
            resultados['estado'] = 'sin_configuraciones'
            return resultados
        
        print(f"Procesando {configuraciones.count()} configuraciones de venta activas")
        
        for configuracion in configuraciones:
            try:
                print(f"Procesando configuración de venta para holding {configuracion.holding.nombre}")
                
                # Verificar si es hora de ejecutar
                if not es_hora_de_ejecutar_venta(configuracion):
                    print(f"No es hora de ejecutar para {configuracion.holding.nombre}")
                    continue
                
                # Procesar esta configuración
                facturas_encontradas = procesar_configuracion_venta_automatica.delay(configuracion.id)
                
                # Esperar resultado (con timeout)
                resultado_config = facturas_encontradas.get(timeout=600)  # 10 minutos max
                
                resultados['configuraciones_procesadas'] += 1
                resultados['facturas_encontradas'] += resultado_config.get('facturas_nuevas', 0)
                
                print(f"Configuración de venta {configuracion.id} procesada: {resultado_config.get('facturas_nuevas', 0)} facturas nuevas")
                
            except Exception as e:
                error_msg = f"Error procesando configuración de venta {configuracion.id}: {str(e)}"
                print(error_msg)
                print(traceback.format_exc())
                resultados['errores'].append(error_msg)
                
                # Intentar retry si no hemos excedido el límite
                if self.request.retries < self.max_retries:
                    print(f"Reintentando en {self.default_retry_delay} segundos...")
                    self.retry(countdown=self.default_retry_delay)
        
        tiempo_fin = timezone.now()
        resultados['tiempo_ejecucion'] = (tiempo_fin - tiempo_inicio).total_seconds()
        resultados['estado'] = 'completado'
        
        print(f"=== BÚSQUEDA AUTOMÁTICA DE VENTA COMPLETADA ===")
        print(f"Configuraciones procesadas: {resultados['configuraciones_procesadas']}")
        print(f"Facturas encontradas: {resultados['facturas_encontradas']}")
        print(f"Tiempo de ejecución: {resultados['tiempo_ejecucion']:.2f} segundos")
        
        return resultados
        
    except Exception as e:
        print(f"Error crítico en búsqueda automática de venta: {str(e)}")
        print(traceback.format_exc())
        
        resultados['estado'] = 'error'
        resultados['errores'].append(str(e))
        
        # Notificar administradores por email
        enviar_notificacion_error_venta.delay(
            "Error crítico en búsqueda automática de facturas de venta",
            str(e),
            traceback.format_exc()
        )
        
        raise

def calcular_periodo_pdfs_venta(mes: int, ano: int) -> tuple:
    """
    Calcula el período para búsqueda de PDFs de venta (8 días antes del mes hasta último día del mes)
    """
    from datetime import datetime, timedelta
    import calendar
    
    # Fecha de inicio: 8 días antes del primer día del mes
    fecha_inicio_mes = datetime(ano, mes, 1)
    fecha_inicio_pdfs = fecha_inicio_mes - timedelta(days=8)
    
    # Fecha de fin: último día del mes
    ultimo_dia_mes = calendar.monthrange(ano, mes)[1]
    fecha_fin_pdfs = datetime(ano, mes, ultimo_dia_mes)
    
    print(f"Período PDFs venta calculado: {fecha_inicio_pdfs.strftime('%d-%m-%Y')} a {fecha_fin_pdfs.strftime('%d-%m-%Y')}")
    
    return fecha_inicio_pdfs, fecha_fin_pdfs

@shared_task(bind=True, max_retries=2, soft_time_limit=900, time_limit=1200)  
def procesar_configuracion_venta_automatica(self, configuracion_id: int):
    """
    Procesa una configuración específica para buscar facturas de venta y sus PDFs.
    """
    print(f"Procesando configuración de venta ID: {configuracion_id}")
    
    resultado = {
        'configuracion_id': configuracion_id,
        'facturas_nuevas': 0,
        'facturas_actualizadas': 0,
        'pdfs_encontrados': 0,
        'pdfs_descargados': 0,
        'errores': [],
        'estado': 'iniciado',
        'periodo_usado': None
    }
    
    session_manager = None
    browser_session = None
    
    try:
        # Obtener la configuración
        configuracion = ConfiguracionSIIAutomaticaVenta.objects.get(id=configuracion_id)
        
        # NUEVO: Obtener mes y año desde la configuración
        mes_configurado = configuracion.mes
        ano_configurado = configuracion.year
        
        
        resultado['periodo_usado'] = {
            'mes': mes_configurado,
            'ano': ano_configurado,
            
        }
        
        print(f"Configuración obtenida: {configuracion.empresa_nombre}")
        print(f"Período configurado:  (mes={mes_configurado}, año={ano_configurado})")
        
        # Crear sesión del navegador UNA SOLA VEZ
        session_manager = BrowserSessionManager.get_instance()
        user_id = f"auto_{configuracion.holding.id}_{configuracion_id}"
        
        browser_session = session_manager.create_session(user_id)
        driver = browser_session.driver
        wait = browser_session.wait
        
        print(f"Sesión del navegador creada para venta {user_id}")
        
        # ===== PARTE 1: PROCESO DE FACTURAS DE VENTA =====
        print("="*60)
        print(f"PARTE 1: DESCARGA DE FACTURAS VENTA CSV")
        print("="*60)
        
        # 1. LOGIN EN EL SII
        login_exitoso = realizar_login_automatico_venta(
            driver, wait, 
            configuracion.rut_sii, 
            configuracion.password_sii
        )
        
        if not login_exitoso:
            raise Exception("Error en el login del SII para venta")
        
        # 2. NAVEGAR A PÁGINA DE CONSULTA DE VENTA
        driver.get("https://www4.sii.cl/consdcvinternetui/#/index")
        time.sleep(random.uniform(3.0, 5.0))
        
        # 3. SELECCIONAR EMPRESA Y PERÍODO - USANDO CONFIGURACIÓN DINÁMICA
        seleccionar_empresa_y_periodo_venta(
            driver, wait,
            configuracion.empresa_rut,
            mes_configurado,  # Usar mes de la configuración
            ano_configurado   # Usar año de la configuración
        )
        
        # 4. SELECCIONAR TIPO VENTA (DIFERENCIA CLAVE CON COMPRAS)
        seleccionar_tipo_venta(driver, wait)
        
        # 5. DESCARGAR CSV
        csv_data = descargar_csv_automatico_venta(driver, wait)
        
        if not csv_data:
            print("No se pudo obtener CSV de venta o está vacío")
            resultado['estado'] = 'sin_datos'
            return resultado
        
        # 6. PROCESAR Y GUARDAR FACTURAS DE VENTA
        facturas_procesadas = procesar_csv_y_guardar_facturas_venta(
            csv_data, 
            configuracion.holding.id
        )
        
        resultado['facturas_nuevas'] = facturas_procesadas['nuevas']
        resultado['facturas_actualizadas'] = facturas_procesadas['actualizadas']
        
        print(f"✅ Facturas de venta procesadas: {resultado['facturas_nuevas']} nuevas, {resultado['facturas_actualizadas']} actualizadas")
        
        # ===== PARTE 2: BÚSQUEDA DE PDFs DE VENTA (USANDO MISMA SESIÓN) =====
        print("="*60)
        print(f"PARTE 2: BÚSQUEDA DE PDFs DE VENTA")
        print("="*60)
        
        if resultado['facturas_nuevas'] > 0 or resultado['facturas_actualizadas'] > 0:
            try:
                # IMPORTANTE: Usar la misma sesión del navegador (driver, wait)
                resultado_pdfs = buscar_y_descargar_pdfs_facturas_venta(
                    driver, wait,  # ← Misma sesión
                    configuracion.holding.id,
                    ano_configurado,  # Año de la configuración
                    mes_configurado   # Mes de la configuración
                )
                
                resultado['pdfs_encontrados'] = resultado_pdfs['pdfs_encontrados']
                resultado['pdfs_descargados'] = resultado_pdfs['pdfs_descargados']
                resultado['errores'].extend(resultado_pdfs['errores'])
                
                print(f"✅ PDFs de venta procesados: {resultado_pdfs}")
                
            except Exception as e:
                error_msg = f"Error en búsqueda de PDFs de venta: {str(e)}"
                print(error_msg)
                print(traceback.format_exc())
                resultado['errores'].append(error_msg)
        else:
            print("No hay facturas de venta nuevas o actualizadas, omitiendo búsqueda de PDFs")
        
        resultado['estado'] = 'completado'
        
        # ===== RESUMEN FINAL =====
        print("="*60)
        print("RESUMEN FINAL VENTA")
        print("="*60)
        print(f"Configuración de venta {configuracion_id} procesada exitosamente")
        print(f"📄 Facturas nuevas: {resultado['facturas_nuevas']}")
        print(f"🔄 Facturas actualizadas: {resultado['facturas_actualizadas']}")
        print(f"🔍 PDFs encontrados: {resultado['pdfs_encontrados']}")
        print(f"📥 PDFs descargados: {resultado['pdfs_descargados']}")
        print(f"❌ Errores: {len(resultado['errores'])}")
        
        if resultado['errores']:
            print("Errores encontrados:")
            for i, error in enumerate(resultado['errores'], 1):
                print(f"  {i}. {error}")
        
        return resultado
        
    except Exception as e:
        print(f"Error crítico procesando configuración de venta {configuracion_id}: {str(e)}")
        print(traceback.format_exc())
        
        resultado['estado'] = 'error'
        resultado['errores'].append(str(e))
        
        # Notificar administradores por email si el error es crítico
        if "login" in str(e).lower() or "credenciales" in str(e).lower():
            enviar_notificacion_error_venta.delay(
                f"Error de credenciales en configuración automática de venta {configuracion_id}",
                str(e),
                traceback.format_exc()
            )
        
        return resultado
        
    finally:
        # Limpiar recursos
        if session_manager and browser_session:
            try:
                session_manager.close_session(browser_session.session_id)
                print(f"Sesión del navegador de venta cerrada: {browser_session.session_id}")
            except Exception as cleanup_error:
                print(f"Error cerrando sesión de venta: {str(cleanup_error)}")

# ==================== FUNCIONES AUXILIARES PARA SELENIUM VENTA ====================

def realizar_login_automatico_venta(driver, wait, rut: str, password: str) -> bool:
    """
    Realiza el login automático en el SII para venta.
    """
    try:
        print(f"Iniciando login automático de venta para RUT: {rut}")
        
        # Navegar a la página de login
        driver.get("https://zeusr.sii.cl/AUT2000/InicioAutenticacion/IngresoRutClave.html")
        time.sleep(random.uniform(3.0, 5.0))
        
        # Ingresar RUT
        rut_input = wait.until(EC.presence_of_element_located((By.ID, "rutcntr")))
        rut_input.clear()
        time.sleep(random.uniform(0.5, 1.0))
        
        for char in rut:
            rut_input.send_keys(char)
            time.sleep(random.uniform(0.1, 0.3))
        
        # Ingresar contraseña
        password_input = driver.find_element(By.ID, "clave")
        password_input.clear()
        time.sleep(random.uniform(0.5, 1.0))
        
        for char in password:
            password_input.send_keys(char)
            time.sleep(random.uniform(0.1, 0.3))
        
        # Hacer clic en login
        login_button = driver.find_element(By.ID, "bt_ingresar")
        driver.execute_script("arguments[0].click();", login_button)
        time.sleep(random.uniform(4.0, 6.0))
        
        # Verificar login exitoso
        current_url = driver.current_url
        if any(pattern in current_url for pattern in ["menuIVA", "mipeSelEmpresa", "cgi_AUT2000"]):
            print("Login automático de venta exitoso")
            return True
        
        print(f"Login automático de venta fallido. URL actual: {current_url}")
        return False
        
    except Exception as e:
        print(f"Error en login automático de venta: {str(e)}")
        return False

def verificar_pagina_consulta_cargada(driver, wait) -> bool:
    """
    Verifica que la página de consulta de registro de compra y venta se haya cargado correctamente
    """
    try:
        print("Verificando que la página de consulta se haya cargado...")
        
        # Verificar elementos específicos de la aplicación Angular
        elementos_a_verificar = [
            (By.CSS_SELECTOR, "select[ng-model='rut']", "Select de empresa"),
            (By.CSS_SELECTOR, "select[ng-model='periodoMes']", "Select de mes"),
            (By.CSS_SELECTOR, "select[ng-model='periodoAnho']", "Select de año"),
            (By.CSS_SELECTOR, "button[type='submit']", "Botón Consultar"),
            (By.CSS_SELECTOR, ".panel-primary", "Panel principal"),
            (By.TAG_NAME, "h2", "Título de página")
        ]
        
        elementos_encontrados = 0
        for selector_type, selector, nombre in elementos_a_verificar:
            try:
                elementos = driver.find_elements(selector_type, selector)
                if elementos:
                    print(f"✅ {nombre} encontrado")
                    elementos_encontrados += 1
                else:
                    print(f"❌ {nombre} NO encontrado")
            except Exception as e:
                print(f"❌ Error verificando {nombre}: {str(e)}")
        
        # Verificar título específico
        try:
            titulo = driver.title
            if "Consulta Registro Compra Venta" in titulo or "REGISTRO DE COMPRAS Y VENTAS" in titulo:
                print(f"✅ Título correcto encontrado: {titulo}")
                elementos_encontrados += 1
            else:
                print(f"⚠️ Título no esperado: {titulo}")
        except Exception as e:
            print(f"Error verificando título: {str(e)}")
        
        # Considerar exitoso si encontramos al menos 4 de los elementos esperados
        exitoso = elementos_encontrados >= 4
        
        print(f"Verificación de página: {elementos_encontrados} elementos encontrados - {'✅ EXITOSO' if exitoso else '❌ FALLIDO'}")
        return exitoso
        
    except Exception as e:
        print(f"Error en verificación de página: {str(e)}")
        return False

def seleccionar_empresa_y_periodo_venta(driver, wait, empresa_rut: str, mes: int, ano: int):
    """
    Selecciona empresa, mes y año en la página de consulta de venta.
    """
    try:
        print(f"Seleccionando empresa de venta {empresa_rut}, período {mes:02d}/{ano}")
        
        # CORREGIR FORMATO RUT - Agregar guión si no lo tiene
        if '-' not in str(empresa_rut):
            rut_str = str(empresa_rut).strip()
            if len(rut_str) >= 8:
                empresa_rut_formatted = f"{rut_str[:-1]}-{rut_str[-1]}"
            else:
                empresa_rut_formatted = empresa_rut
        else:
            empresa_rut_formatted = str(empresa_rut)
        
        print(f"RUT formateado para venta: {empresa_rut} -> {empresa_rut_formatted}")
        
        # Seleccionar empresa
        empresa_select = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "select[ng-model='rut']"))
        )
        empresa_select_obj = Select(empresa_select)
        empresa_select_obj.select_by_value(empresa_rut_formatted)
        time.sleep(random.uniform(1.0, 2.0))
        
        # Seleccionar mes
        mes_formatted = f"{mes:02d}"
        mes_select = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "select[ng-model='periodoMes']"))
        )
        mes_select_obj = Select(mes_select)
        mes_select_obj.select_by_value(mes_formatted)
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
        time.sleep(random.uniform(3.0, 5.0))
        
        print("Empresa y período de venta seleccionados exitosamente")
        
    except Exception as e:
        print(f"Error seleccionando empresa y período de venta: {str(e)}")
        raise

def seleccionar_tipo_venta(driver, wait):
    """
    DIFERENCIA CLAVE: Selecciona el tipo VENTA en lugar de COMPRA
    """
    try:
        print("Seleccionando tipo VENTA...")
        
        # Buscar y hacer clic en el tab/botón de VENTA
        try:
            # Método 1: Buscar tab de venta
            tab_venta = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a[ui-sref='venta']"))
            )
            driver.execute_script("arguments[0].click();", tab_venta)
            time.sleep(random.uniform(2.0, 3.0))
            print("✅ Tab VENTA seleccionado")
            return
        except TimeoutException:
            pass
        
        # Método 2: Buscar radio button de venta  
        try:
            radio_venta = driver.find_element(By.CSS_SELECTOR, "input[value='VENTA']")
            driver.execute_script("arguments[0].click();", radio_venta)
            time.sleep(random.uniform(1.0, 2.0))
            print("✅ Radio VENTA seleccionado")
            return
        except NoSuchElementException:
            pass
        
        # Método 3: Buscar por texto
        try:
            venta_link = driver.find_element(By.XPATH, "//a[contains(text(), 'Venta')]")
            driver.execute_script("arguments[0].click();", venta_link)
            time.sleep(random.uniform(2.0, 3.0))
            print("✅ Link VENTA seleccionado")
            return
        except NoSuchElementException:
            pass
        
        print("⚠️ No se pudo encontrar selector de VENTA, continuando...")
        
    except Exception as e:
        print(f"Error seleccionando tipo VENTA: {str(e)}")
        # No hacer raise aquí, puede que no sea necesario
        pass

def descargar_csv_automatico_venta(driver, wait) -> str:
    """
    Descarga el CSV de detalles de facturas de venta.
    CORREGIDO: Verificar que estamos en tab de VENTA y esperar carga completa
    """
    try:
        print("Iniciando descarga de CSV de venta")
        
        # PASO 1: VERIFICAR QUE ESTAMOS EN LA VISTA CORRECTA
        print("Verificando que estamos en vista de VENTA...")
        current_url = driver.current_url
        print(f"URL actual: {current_url}")
        
        # PASO 2: ESPERAR A QUE LA VISTA DE VENTA SE CARGUE COMPLETAMENTE
        print("Esperando carga completa de vista de venta...")
        time.sleep(random.uniform(5.0, 8.0))
        
        # PASO 3: VERIFICAR QUE HAY DATOS PARA DESCARGAR
        try:
            # Buscar elementos que indiquen que hay datos
            datos_elements = driver.find_elements(By.CSS_SELECTOR, ".ng-scope, [ng-show='datos'], .panel-body")
            if datos_elements:
                print(f"✅ Elementos de datos encontrados: {len(datos_elements)}")
            else:
                print("⚠️ No se encontraron elementos de datos")
        except Exception as e:
            print(f"Error verificando datos: {str(e)}")
        
        # PASO 4: BUSCAR BOTÓN DE DESCARGA CON MÚLTIPLES ESTRATEGIAS
        print("Buscando botón de descarga...")
        
        selectores_boton = [
            "//button[contains(text(), 'Descargar Detalles')]",
            "//button[contains(text(), 'Descargar')]",
            "//input[@value='Descargar Detalles']",
            "//input[@value='Descargar']",
            "button[ng-click*='descargaDetalle']",
            "input[ng-click*='descargaDetalle']",
            "button[onclick*='descarga']",
            "input[onclick*='descarga']",
            ".btn:contains('Descargar')",
            "//a[contains(text(), 'Descargar')]"
        ]
        
        descargar_btn = None
        selector_usado = None
        
        for selector in selectores_boton:
            try:
                if selector.startswith("//"):
                    elementos = driver.find_elements(By.XPATH, selector)
                else:
                    elementos = driver.find_elements(By.CSS_SELECTOR, selector)
                
                # Buscar elemento visible y habilitado
                for elemento in elementos:
                    if elemento.is_displayed() and elemento.is_enabled():
                        descargar_btn = elemento
                        selector_usado = selector
                        print(f"✅ Botón encontrado con selector: {selector}")
                        break
                
                if descargar_btn:
                    break
                    
            except Exception as e:
                print(f"Error con selector {selector}: {str(e)}")
                continue
        
        if not descargar_btn:
            print("❌ No se encontró el botón de descarga de venta")
            
            # DEBUG: Mostrar todos los botones disponibles
            try:
                todos_botones = driver.find_elements(By.TAG_NAME, "button")
                todos_inputs = driver.find_elements(By.TAG_NAME, "input")
                print(f"Botones encontrados: {len(todos_botones)}")
                print(f"Inputs encontrados: {len(todos_inputs)}")
                
                for i, btn in enumerate(todos_botones[:5]):  # Solo mostrar primeros 5
                    text = btn.text or btn.get_attribute('value') or btn.get_attribute('onclick') or 'Sin texto'
                    print(f"  Botón {i}: '{text}' - visible: {btn.is_displayed()}")
                    
                for i, inp in enumerate(todos_inputs[:5]):  # Solo mostrar primeros 5
                    if inp.get_attribute('type') in ['button', 'submit']:
                        text = inp.get_attribute('value') or inp.get_attribute('onclick') or 'Sin value'
                        print(f"  Input {i}: '{text}' - visible: {inp.is_displayed()}")
                        
            except Exception as debug_error:
                print(f"Error en debug: {str(debug_error)}")
            
            return None
        
        # PASO 5: HACER CLIC EN EL BOTÓN DE DESCARGA
        print(f"Haciendo clic en botón de descarga (selector: {selector_usado})...")
        
        try:
            # Scroll hacia el elemento
            driver.execute_script("arguments[0].scrollIntoView(true);", descargar_btn)
            time.sleep(random.uniform(1.0, 2.0))
            
            # Intentar click normal primero
            try:
                descargar_btn.click()
                print("✅ Click normal exitoso")
            except Exception:
                # Si falla, usar JavaScript
                driver.execute_script("arguments[0].click();", descargar_btn)
                print("✅ Click con JavaScript exitoso")
                
        except Exception as click_error:
            print(f"❌ Error haciendo clic: {str(click_error)}")
            return None
        
        # PASO 6: ESPERAR DESCARGA
        print("Esperando descarga del archivo...")
        tiempo_espera_inicial = random.uniform(8.0, 12.0)
        time.sleep(tiempo_espera_inicial)
        
        # PASO 7: BUSCAR ARCHIVO CSV DESCARGADO
        downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        
        # Intentar múltiples veces con espera adicional
        max_intentos_busqueda = 3
        for intento in range(max_intentos_busqueda):
            csv_data = obtener_csv_mas_reciente_venta(downloads_dir)
            
            if csv_data:
                print(f"✅ CSV de venta descargado exitosamente en intento {intento + 1}")
                print(f"Tamaño: {len(csv_data)} caracteres")
                return csv_data
            else:
                if intento < max_intentos_busqueda - 1:
                    print(f"⏳ CSV no encontrado, esperando más... intento {intento + 1}")
                    time.sleep(5.0)
                else:
                    print("❌ No se pudo obtener el archivo CSV de venta después de múltiples intentos")
        
        return None
            
    except Exception as e:
        print(f"❌ Error descargando CSV de venta: {str(e)}")
        print(f"URL actual: {driver.current_url}")
        print(f"Título: {driver.title}")
        return None
    
def obtener_csv_mas_reciente_venta(directory: str) -> str:
    """
    Obtiene el archivo CSV más reciente del directorio para venta.
    """
    try:
        if not os.path.exists(directory):
            return None
        
        csv_files = [f for f in os.listdir(directory) if f.endswith('.csv')]
        
        if not csv_files:
            return None
        
        # Obtener el más reciente por tiempo de modificación
        archivos_con_tiempo = []
        for archivo in csv_files:
            ruta_completa = os.path.join(directory, archivo)
            tiempo_mod = os.path.getmtime(ruta_completa)
            archivos_con_tiempo.append((archivo, tiempo_mod))
        
        archivos_con_tiempo.sort(key=lambda x: x[1], reverse=True)
        latest_file = archivos_con_tiempo[0][0]
        file_path = os.path.join(directory, latest_file)
        
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        return content
        
    except Exception as e:
        print(f"Error obteniendo CSV más reciente de venta: {str(e)}")
        return None

def procesar_csv_y_guardar_facturas_venta(csv_data: str, holding_id: int) -> Dict[str, int]:
    """
    Procesa el CSV del SII de VENTA y guarda las facturas nuevas.
    """
    print(f"Procesando CSV de venta para holding {holding_id}")
    
    resultado = {
        'nuevas': 0,
        'actualizadas': 0,
        'errores': 0
    }
    
    try:
        # Parsear CSV usando la misma lógica del sistema manual pero para venta
        facturas_parseadas = parsear_csv_sii_venta(csv_data)
        
        if not facturas_parseadas:
            print("No se encontraron facturas de venta válidas en el CSV")
            return resultado
        
        print(f"Facturas de venta parseadas del CSV: {len(facturas_parseadas)}")
        
        with transaction.atomic():
            for factura_data in facturas_parseadas:
                try:
                    # Verificar si la factura ya existe
                    folio = factura_data.get('folio', '').strip()
                    rut_receptor = factura_data.get('rut_receptor', '').strip()
                    
                    if not folio:
                        continue
                    
                    # Verificar en facturas distribuidas
                    existe_distribuida = FacturaVentaSIIDistribuida.objects.filter(
                        holding_id=holding_id,
                        folio=folio,
                        rut_receptor=rut_receptor
                    ).exists()
                    
                    if existe_distribuida:
                        continue  # Ya está distribuida, no hacer nada
                    
                    # Verificar en facturas por distribuir
                    factura_existente = FacturaVentaSIIPorDistribuir.objects.filter(
                        holding_id=holding_id,
                        folio=folio,
                        rut_receptor=rut_receptor
                    ).first()
                    
                    if factura_existente:
                        # Actualizar fecha de última verificación
                        factura_existente.save()
                        resultado['actualizadas'] += 1
                    else:
                        # Crear nueva factura de venta por distribuir
                        FacturaVentaSIIPorDistribuir.objects.create(
                            holding_id=holding_id,
                            folio=folio,
                            tipo_doc=factura_data.get('tipo_doc', ''),
                            rut_receptor=rut_receptor,
                            razon_social_receptor=factura_data.get('razon_social_receptor', ''),
                            fecha_emision=factura_data.get('fecha_emision', ''),
                            monto_total=Decimal(str(factura_data.get('monto_total', 0))),
                            monto_neto=Decimal(str(factura_data.get('monto_neto', 0))),
                            monto_exento=Decimal(str(factura_data.get('monto_exento', 0))),
                            monto_iva=Decimal(str(factura_data.get('monto_iva', 0))),
                            monto_otros_impuestos=Decimal(str(factura_data.get('monto_otros_impuestos', 0))),
                            codigo_otros_impuestos=factura_data.get('codigo_otros_impuestos', ''),
                            procesada=False,
                            monto_distribuido=Decimal('0'),
                            porcentaje_distribuido=Decimal('0')
                        )
                        resultado['nuevas'] += 1
                        
                except Exception as e:
                    print(f"Error procesando factura de venta individual: {str(e)}")
                    resultado['errores'] += 1
                    continue
        
        print(f"Procesamiento de venta completado. Nuevas: {resultado['nuevas']}, Actualizadas: {resultado['actualizadas']}, Errores: {resultado['errores']}")
        return resultado
        
    except Exception as e:
        print(f"Error procesando CSV de venta y guardando facturas: {str(e)}")
        print(traceback.format_exc())
        raise

def parsear_csv_sii_venta(csv_data: str) -> List[Dict[str, Any]]:
    """
    Parser específico para el formato CSV del SII de VENTA.
    CORREGIDO: Mapeo de campos actualizado para coincidir con el formato real del CSV.
    """
    try:
        import re
        from decimal import Decimal
        
        lines = csv_data.strip().split('\n')
        if len(lines) < 2:
            return []
        
        # Procesar header
        header_line = lines[0].strip()
        headers = [h.strip() for h in header_line.split(';')]
        
        # ✅ MAPEO CORREGIDO para coincidir con CSV real de venta
        expected_fields = {
            'Nro': 'nro',
            'Tipo Doc': 'tipo_doc', 
            'Rut cliente': 'rut_receptor',  # ← CORRECCIÓN: era "RUT Receptor"
            'Razon Social': 'razon_social_receptor',
            'Folio': 'folio',
            'Fecha Docto': 'fecha_emision',  # ← CORRECCIÓN: era "Fecha Emision"
            'Monto total': 'monto_total',  # ← CORRECCIÓN: era "Monto Total" (mayúscula)
            'Monto Neto': 'monto_neto',
            'Monto Exento': 'monto_exento',
            'Monto IVA': 'monto_iva',
            # Campos adicionales específicos del CSV de venta
            'Tipo Venta': 'tipo_venta',
            'Fecha Recepcion': 'fecha_recepcion',
            'Fecha Acuse Recibo': 'fecha_acuse_recibo',
            'Fecha Reclamo': 'fecha_reclamo',
            'IVA Retenido Total': 'iva_retenido_total',
            'IVA Retenido Parcial': 'iva_retenido_parcial',
            'IVA no retenido': 'iva_no_retenido',
            'IVA propio': 'iva_propio',
            'IVA Terceros': 'iva_terceros',
            'Codigo Otro Imp.': 'codigo_otros_impuestos',
            'Valor Otro Imp.': 'monto_otros_impuestos',
            'Tasa Otro Imp.': 'tasa_otros_impuestos'
        }
        
        def clean_string(value):
            if not value or value.lower() in ['', 'nan', 'null', 'none']:
                return ''
            return str(value).strip()
        
        def clean_decimal(value):
            if not value or value.lower() in ['', 'nan', 'null', 'none']:
                return 0.0
            cleaned = str(value).strip().replace(',', '.')
            try:
                return float(cleaned)
            except (ValueError, TypeError):
                return 0.0
        
        def clean_date(value):
            if not value or value.lower() in ['', 'nan', 'null', 'none']:
                return ''
            date_str = str(value).strip()
            # Manejar formato "30/11/2023 18:27:46" y extraer solo la fecha
            if ' ' in date_str:
                date_str = date_str.split(' ')[0]
            if re.match(r'\d{1,2}/\d{1,2}/\d{4}', date_str):
                return date_str
            return date_str
        
        # Procesar filas de datos
        facturas = []
        for line_num, line in enumerate(lines[1:], start=2):
            try:
                line = line.strip()
                if not line:
                    continue
                
                values = line.split(';')
                while len(values) < len(headers):
                    values.append('')
                values = values[:len(headers)]
                
                row_data = {}
                for i, header in enumerate(headers):
                    value = values[i].strip() if i < len(values) else ''
                    field_name = expected_fields.get(header, header.lower().replace(' ', '_'))
                    row_data[field_name] = value
                
                # Crear objeto factura de venta limpio
                factura = {
                    'nro': clean_string(row_data.get('nro', '')),
                    'tipo_doc': clean_string(row_data.get('tipo_doc', '')),
                    'rut_receptor': clean_string(row_data.get('rut_receptor', '')),  # ← Este campo ahora se mapeará correctamente
                    'razon_social_receptor': clean_string(row_data.get('razon_social_receptor', '')),
                    'folio': clean_string(row_data.get('folio', '')),
                    'fecha_emision': clean_date(row_data.get('fecha_emision', '')),  # ← Mapea "Fecha Docto"
                    'monto_total': clean_decimal(row_data.get('monto_total', 0)),  # ← Mapea "Monto total"
                    'monto_neto': clean_decimal(row_data.get('monto_neto', 0)),
                    'monto_exento': clean_decimal(row_data.get('monto_exento', 0)),
                    'monto_iva': clean_decimal(row_data.get('monto_iva', 0)),
                    'monto_otros_impuestos': clean_decimal(row_data.get('monto_otros_impuestos', 0)),
                    'codigo_otros_impuestos': clean_string(row_data.get('codigo_otros_impuestos', ''))
                }
                
                # Validaciones básicas
                if not factura['folio']:
                    print(f"⚠️ Factura sin folio en línea {line_num}, omitiendo")
                    continue
                
                if not factura['razon_social_receptor']:
                    factura['razon_social_receptor'] = factura['rut_receptor']
                
                # ✅ VALIDACIÓN ADICIONAL: Verificar que el RUT no esté vacío
                if not factura['rut_receptor']:
                    print(f"⚠️ Factura {factura['folio']} sin RUT cliente en línea {line_num}")
                    # No continuar si falta el RUT, es crítico para búsqueda de PDFs
                    continue
                
                print(f"✅ Factura parseada: Folio={factura['folio']}, RUT={factura['rut_receptor']}, Razón={factura['razon_social_receptor'][:30]}...")
                facturas.append(factura)
                
            except Exception as line_error:
                print(f"Error procesando línea de venta {line_num}: {str(line_error)}")
                continue
        
        print(f"📊 Parser de venta completado: {len(facturas)} facturas válidas procesadas")
        return facturas
        
    except Exception as e:
        print(f"Error en parser CSV del SII de venta: {str(e)}")
        print(traceback.format_exc())
        return []

# ==================== BÚSQUEDA DE PDFs DE VENTA ====================

@shared_task(bind=True, max_retries=2, soft_time_limit=600, time_limit=900)
def buscar_pdfs_facturas_venta_existentes(self, holding_id: int):
    """
    Busca PDFs para facturas de venta existentes que no los tienen.
    """
    print(f"Buscando PDFs para facturas de venta existentes del holding {holding_id}")
    
    resultado = {
        'holding_id': holding_id,
        'pdfs_encontrados': 0,
        'pdfs_descargados': 0,
        'errores': [],
        'estado': 'iniciado',
        'periodo_usado': None
    }
    
    session_manager = None
    
    try:
        # Obtener configuración del holding
        configuracion = ConfiguracionSIIAutomaticaVenta.objects.get(holding_id=holding_id)
        
        # Usar mes y año de la configuración
        mes_configurado = configuracion.mes
        ano_configurado = configuracion.year
        
        resultado['periodo_usado'] = {
            'mes': mes_configurado,
            'ano': ano_configurado,
        }
        
        print(f"Usando período configurado para venta")
        
        # Crear sesión del navegador
        session_manager = BrowserSessionManager.get_instance()
        user_id = f"pdf_search_venta_{holding_id}"
        
        browser_session = session_manager.create_session(user_id)
        driver = browser_session.driver
        wait = browser_session.wait
        
        # Login en el SII
        login_exitoso = realizar_login_automatico_venta(
            driver, wait, 
            configuracion.rut_sii, 
            configuracion.password_sii
        )
        
        if not login_exitoso:
            raise Exception("Error en el login del SII para búsqueda de PDFs de venta")
        
        # Buscar PDFs usando configuración dinámica
        resultado_pdfs = buscar_y_descargar_pdfs_facturas_venta(
            driver, wait,
            holding_id,
            ano_configurado,  # Año de la configuración
            mes_configurado   # Mes de la configuración
        )
        
        resultado['pdfs_encontrados'] = resultado_pdfs['pdfs_encontrados']
        resultado['pdfs_descargados'] = resultado_pdfs['pdfs_descargados']
        resultado['errores'] = resultado_pdfs['errores']
        resultado['estado'] = 'completado'
        
        print(f"Búsqueda de PDFs de venta completada para holding {holding_id}: {resultado}")
        
        return resultado
        
    except Exception as e:
        print(f"Error buscando PDFs de venta para holding {holding_id}: {str(e)}")
        resultado['estado'] = 'error'
        resultado['errores'].append(str(e))
        return resultado
        
    finally:
        if session_manager and 'browser_session' in locals():
            try:
                session_manager.close_session(browser_session.session_id)
            except:
                pass

def buscar_y_descargar_pdfs_facturas_venta(driver, wait, holding_id, ano, mes):
    """
    Busca y descarga PDFs de las facturas de venta por distribuir.
    DIFERENCIA CLAVE: Usa el flujo de documentos EMITIDOS (no recibidos)
    """
    print(f"=== INICIANDO BÚSQUEDA DE PDFs DE VENTA ===")
    print(f"Holding: {holding_id}, Año: {ano}, Mes: {mes}")
    
    resultado = {
        'pdfs_encontrados': 0,
        'pdfs_descargados': 0,
        'errores': []
    }
    
    try:
        # VALIDACIÓN OBLIGATORIA de parámetros
        if not ano or not mes:
            error_msg = f"Parámetros faltantes: año={ano}, mes={mes}"
            print(f"❌ {error_msg}")
            resultado['errores'].append(error_msg)
            return resultado
        
        # Validar parámetros
        mes_int, ano_int = validar_y_convertir_fecha_params_venta(mes, ano)
        
        print(f"✅ Parámetros de venta validados: Año={ano_int}, Mes={mes_int}")
        
        # Obtener facturas de venta sin PDF
        facturas_sin_pdf = FacturaVentaSIIPorDistribuir.objects.filter(
            holding_id=holding_id,
            pdf_descargado=False,
            intentos_descarga_pdf__lt=3
        )
        
        print(f"Facturas de venta sin PDF encontradas: {facturas_sin_pdf.count()}")
        
        if not facturas_sin_pdf.exists():
            print("No hay facturas de venta sin PDF para procesar")
            return resultado
        
        # Obtener configuración para el RUT de empresa
        try:
            configuracion = ConfiguracionSIIAutomaticaVenta.objects.get(holding_id=holding_id)
            empresa_rut = configuracion.empresa_rut
            print(f"✅ RUT empresa obtenido para venta: {empresa_rut}")
        except ConfiguracionSIIAutomaticaVenta.DoesNotExist:
            error_msg = f"No se encontró configuración de venta para holding {holding_id}"
            resultado['errores'].append(error_msg)
            return resultado
        
        # 1. SELECCIONAR EMPRESA PARA PDFs DE VENTA
        print("=== PASO 1: SELECCIONANDO EMPRESA PARA PDFs DE VENTA ===")
        if not seleccionar_empresa_para_pdfs_venta(driver, wait, empresa_rut):
            error_msg = f"Error al seleccionar empresa de venta {empresa_rut}"
            resultado['errores'].append(error_msg)
            return resultado
        
        # 2. NAVEGAR A ADMINISTRACIÓN DE DOCUMENTOS EMITIDOS (DIFERENCIA CLAVE)
        print("=== PASO 2: NAVEGANDO A ADMINISTRACIÓN DE DOCUMENTOS EMITIDOS ===")
        url_admin_docs_emitidos = f"https://www1.sii.cl/cgi-bin/Portal001/mipeAdminDocsEmi.cgi?RUT_RECP=&FOLIO=&RZN_SOC=&FEC_DESDE=&FEC_HASTA=&TPO_DOC=&ESTADO=&ORDEN=&NUM_PAG=1"
        
        driver.get(url_admin_docs_emitidos)
        time.sleep(random.uniform(3.0, 5.0))
        print(f"✅ Navegado a documentos emitidos: {driver.current_url}")
        
        # 3. CONFIGURAR FILTROS UNA SOLA VEZ
        print("=== PASO 3: CONFIGURANDO FILTROS DE BÚSQUEDA DE VENTA ===")
        print(f"Configurando filtros para período: {mes_int:02d}/{ano_int}")
        
        if not configurar_filtros_busqueda_pdf_venta(driver, wait, ano_int, mes_int):
            error_msg = "Error al configurar filtros de búsqueda de venta"
            resultado['errores'].append(error_msg)
            return resultado
        
        # Guardar URL con filtros
        url_con_filtros = driver.current_url
        print(f"✅ URL con filtros de venta guardada: {url_con_filtros}")
        
        # 4. BUSCAR PDFs USANDO LA TABLA YA CARGADA
        print("=== PASO 4: BUSCANDO PDFs DE VENTA EN TABLA CARGADA ===")
        facturas_a_procesar = list(facturas_sin_pdf[:10])  # Procesar máximo 10
        print(f"Procesando {len(facturas_a_procesar)} facturas de venta")
        
        for i, factura in enumerate(facturas_a_procesar, 1):
            print(f"--- Procesando factura de venta {i}/{len(facturas_a_procesar)}: {factura.folio} ---")
            try:
                pdf_descargado = buscar_y_descargar_pdf_factura_venta(driver, wait, factura, url_con_filtros)
                if pdf_descargado:
                    resultado['pdfs_descargados'] += 1
                    print(f"✅ PDF descargado para factura de venta {factura.folio}")
                else:
                    print(f"⚠️ No se pudo descargar PDF para factura de venta {factura.folio}")
                
                resultado['pdfs_encontrados'] += 1
                    
            except Exception as e:
                error_msg = f"Error procesando factura de venta {factura.folio}: {str(e)}"
                print(error_msg)
                resultado['errores'].append(error_msg)
                
                # Incrementar intentos fallidos
                factura.intentos_descarga_pdf += 1
                factura.error_descarga_pdf = str(e)
                factura.save()
        
        print(f"=== BÚSQUEDA DE PDFs DE VENTA COMPLETADA ===")
        print(f"Resultado final: {resultado}")
        return resultado
        
    except Exception as e:
        error_msg = f"Error general en búsqueda de PDFs de venta: {str(e)}"
        print(error_msg)
        print(traceback.format_exc())
        resultado['errores'].append(error_msg)
        return resultado

def seleccionar_empresa_para_pdfs_venta(driver, wait, empresa_rut):
    """
    Selecciona la empresa en la URL de selección para PDFs de VENTA.
    DIFERENCIA CLAVE: Usa la URL de documentos EMITIDOS
    """
    try:
        print(f"🏢 Seleccionando empresa de venta: {empresa_rut}")
        
        # URL para seleccionar empresa - DOCUMENTOS EMITIDOS (OPCION=2&TIPO=4)
        url_seleccion = "https://www1.sii.cl/cgi-bin/Portal001/mipeSelEmpresa.cgi?DESDE_DONDE_URL=OPCION%3D2%26TIPO%3D4"
        print(f"Navegando a selección de venta: {url_seleccion}")
        
        driver.get(url_seleccion)
        time.sleep(5)
        
        print(f"URL actual: {driver.current_url}")
        print(f"Título: {driver.title}")
        
        # Buscar el select de empresas
        try:
            select_empresas = wait.until(
                EC.presence_of_element_located((By.NAME, "RUT_EMP"))
            )
            print("✅ Select de empresas de venta encontrado")
        except TimeoutException:
            print("❌ No se encontró el select de empresas de venta")
            return False
        
        # Preparar diferentes formatos del RUT
        def formatear_rut_con_guion(rut_str):
            rut_str = str(rut_str).strip()
            if '-' in rut_str:
                return rut_str
            if len(rut_str) >= 2:
                return f"{rut_str[:-1]}-{rut_str[-1]}"
            return rut_str
        
        empresa_rut_str = str(empresa_rut).strip()
        rut_con_guion = formatear_rut_con_guion(empresa_rut_str)
        rut_sin_guion = empresa_rut_str.replace('-', '')
        
        print(f"RUT original de venta: {empresa_rut_str}")
        print(f"RUT con guión de venta: {rut_con_guion}")
        print(f"RUT sin guión de venta: {rut_sin_guion}")
        
        # Obtener opciones y buscar coincidencia
        from selenium.webdriver.support.ui import Select
        select_obj = Select(select_empresas)
        opciones = select_obj.options
        
        print(f"Opciones de venta disponibles ({len(opciones)}):")
        for i, opcion in enumerate(opciones[:5]):  # Solo mostrar primeras 5
            value = opcion.get_attribute('value')
            text = opcion.text[:50]  # Truncar texto
            print(f"  {i}: value='{value}' text='{text}'")
        
        # Buscar empresa por coincidencia exacta
        empresa_encontrada = False
        for opcion in opciones:
            value = opcion.get_attribute('value')
            if value in [rut_con_guion, rut_sin_guion, empresa_rut_str]:
                print(f"✅ Empresa de venta encontrada: {value}")
                select_obj.select_by_value(value)
                empresa_encontrada = True
                break
        
        if not empresa_encontrada:
            print(f"❌ Empresa de venta {empresa_rut} no encontrada en las opciones")
            return False
        
        # Enviar formulario
        print("Enviando formulario de venta...")
        try:
            boton_enviar = driver.find_element(By.XPATH, "//button[@type='submit'] | //input[@type='submit']")
            boton_enviar.click()
            time.sleep(5)
        except Exception as e:
            print(f"❌ Error enviando formulario de venta: {str(e)}")
            return False
        
        # Verificar éxito
        print(f"URL después de selección de venta: {driver.current_url}")
        print(f"Título después de selección de venta: {driver.title}")
        
        if "mipeSelEmpresa" in driver.current_url:
            print("❌ Seguimos en página de selección de venta")
            return False
        
        print(f"✅ Empresa de venta {empresa_rut} seleccionada exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error seleccionando empresa de venta: {str(e)}")
        print(traceback.format_exc())
        return False

def configurar_filtros_busqueda_pdf_venta(driver, wait, ano, mes):
    """
    Configura los filtros de fecha para buscar documentos emitidos en el período específico.
    """
    try:
        # Validar y convertir parámetros
        mes_int = int(mes) if isinstance(mes, str) else mes
        ano_int = int(ano) if isinstance(ano, str) else ano
        
        print(f"📅 Configurando filtros de venta para {mes_int:02d}/{ano_int}")
        
        # Calcular fechas del período (8 días antes del mes hasta último día del mes)
        from datetime import datetime, timedelta
        import calendar
        
        # Fecha de inicio: 8 días antes del primer día del mes
        fecha_inicio_mes = datetime(ano_int, mes_int, 1)
        fecha_inicio = fecha_inicio_mes - timedelta(days=8)
        
        # Fecha de fin: último día del mes
        ultimo_dia_mes = calendar.monthrange(ano_int, mes_int)[1]
        fecha_fin = datetime(ano_int, mes_int, ultimo_dia_mes)
        
        # Usar formato YYYY-MM-DD para campos del SII
        fecha_desde = fecha_inicio.strftime("%Y-%m-%d")
        fecha_hasta = fecha_fin.strftime("%Y-%m-%d")
        
        print(f"Período de búsqueda de venta: {fecha_desde} a {fecha_hasta}")
        
        # Verificar que estamos en la página correcta
        print(f"URL actual: {driver.current_url}")
        
        # Esperar a que la página se cargue completamente
        time.sleep(5)
        
        # PASO 1: Expandir panel de filtros si está colapsado
        try:
            print("Verificando panel de filtros de venta...")
            panel_colapsado = driver.find_elements(By.CSS_SELECTOR, "#collapseFiltro.collapse:not(.in)")
            if panel_colapsado:
                print("Panel de filtros de venta colapsado, expandiendo...")
                toggle_button = driver.find_element(By.CSS_SELECTOR, "a[href='#collapseFiltro']")
                driver.execute_script("arguments[0].click();", toggle_button)
                time.sleep(3)
                print("✅ Panel de filtros de venta expandido")
        except Exception as e:
            print(f"Error expandiendo panel de venta: {str(e)}")
        
        # PASO 2: Configurar fecha desde
        print("Configurando fecha desde de venta...")
        try:
            campo_fecha_desde = wait.until(
                EC.presence_of_element_located((By.NAME, "FEC_DESDE"))
            )
            
            # Limpiar completamente y usar formato correcto
            driver.execute_script("arguments[0].value = '';", campo_fecha_desde)
            driver.execute_script("arguments[0].setAttribute('value', '');", campo_fecha_desde)
            time.sleep(1)
            
            # Establecer valor usando JavaScript para asegurar formato correcto
            driver.execute_script(f"arguments[0].value = '{fecha_desde}';", campo_fecha_desde)
            time.sleep(1)
            
            valor_actual = campo_fecha_desde.get_attribute('value')
            print(f"✅ Fecha desde de venta configurada: {fecha_desde} -> {valor_actual}")
            
        except Exception as e:
            print(f"❌ Error configurando fecha desde de venta: {str(e)}")
            return False
        
        # PASO 3: Configurar fecha hasta
        print("Configurando fecha hasta de venta...")
        try:
            campo_fecha_hasta = driver.find_element(By.NAME, "FEC_HASTA")
            
            # Limpiar completamente y usar formato correcto
            driver.execute_script("arguments[0].value = '';", campo_fecha_hasta)
            driver.execute_script("arguments[0].setAttribute('value', '');", campo_fecha_hasta)
            time.sleep(1)
            
            # Establecer valor usando JavaScript
            driver.execute_script(f"arguments[0].value = '{fecha_hasta}';", campo_fecha_hasta)
            time.sleep(1)
            
            valor_actual = campo_fecha_hasta.get_attribute('value')
            print(f"✅ Fecha hasta de venta configurada: {fecha_hasta} -> {valor_actual}")
            
        except Exception as e:
            print(f"❌ Error configurando fecha hasta de venta: {str(e)}")
            return False
        
        # PASO 4: Hacer clic en buscar
        print("Iniciando búsqueda de venta...")
        try:
            boton_buscar = driver.find_element(By.CSS_SELECTOR, "input[onclick='verificaCampos()']")
            print("✅ Botón de búsqueda de venta encontrado")
            
            # Scroll y click
            driver.execute_script("arguments[0].scrollIntoView(true);", boton_buscar)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", boton_buscar)
            
            print("✅ Búsqueda de venta iniciada, esperando resultados...")
            time.sleep(8)  # Esperar que carguen los resultados
            
        except Exception as e:
            print(f"❌ Error haciendo búsqueda de venta: {str(e)}")
            return False
        
        # PASO 5: Verificar resultados
        print(f"URL después de búsqueda de venta: {driver.current_url}")
        
        # Verificar si hay tabla de resultados
        try:
            wait.until(EC.presence_of_element_located((By.ID, "tablaDatos")))
            print("✅ Tabla de resultados de venta encontrada")
            return True
        except TimeoutException:
            print("⚠️ No se encontró tabla de resultados de venta en tiempo esperado")
            return True  # Continuar porque puede que no haya datos
            
    except Exception as e:
        print(f"❌ Error crítico configurando filtros de venta: {str(e)}")
        print(traceback.format_exc())
        return False

def buscar_y_descargar_pdf_factura_venta(driver, wait, factura, url_con_filtros=None):
    """
    Busca una factura de venta específica en la tabla y descarga su PDF.
    DIFERENCIA CLAVE: Para venta el PDF se descarga automáticamente al hacer clic en "Ver"
    """
    try:
        print(f"🔍 Buscando PDF para factura de venta {factura.folio} - RUT {factura.rut_receptor}")
        
        # Verificar y regresar si es necesario
        current_url = driver.current_url
        print(f"URL actual: {current_url}")
        
        # Verificar que estemos en la página de administración de documentos emitidos
        if "mipeAdminDocsEmi.cgi" not in current_url:
            if url_con_filtros:
                print(f"🔄 Regresando a tabla principal de venta: {url_con_filtros}")
                driver.get(url_con_filtros)
                time.sleep(random.uniform(3.0, 5.0))
                print("✅ De vuelta en tabla principal de venta")
            else:
                print("❌ No estamos en la página correcta de administración de documentos emitidos")
                return False
        
        # Buscar código de la factura en la tabla
        codigo_sii = buscar_codigo_factura_venta_en_tabla(driver, wait, factura.folio, factura.rut_receptor)
        
        if not codigo_sii:
            error_msg = f"Factura de venta {factura.folio} - {factura.rut_receptor} no encontrada en la tabla del SII"
            print(f"⚠️ {error_msg}")
            
            factura.intentos_descarga_pdf += 1
            factura.error_descarga_pdf = error_msg
            factura.save()
            return False
        
        print(f"✅ Código SII de venta encontrado: {codigo_sii}")
        
        # Guardar código y continuar
        factura.codigo_sii = codigo_sii
        factura.save()
        
        # NAVEGAR A PÁGINA DE DETALLE DE VENTA
        url_detalle = f"https://www1.sii.cl/cgi-bin/Portal001/mipeGesDocEmi.cgi?ALL_PAGE_ANT=2&CODIGO={codigo_sii}"
        print(f"Navegando a detalle de venta: {url_detalle}")
        
        driver.get(url_detalle)
        time.sleep(random.uniform(4.0, 6.0))
        
        # BUSCAR Y DESCARGAR PDF - MÁS SIMPLE QUE COMPRAS
        try:
            print("Buscando link de PDF de venta...")
            
            # DIFERENCIA CLAVE: En ventas es más directo, buscar enlaces PDF
            selectores_pdf = [
                "//iframe[contains(@src, 'mipeDisplayPDF')]",  # PDF embebido
                "//a[contains(@href, 'PDF') or contains(@href, 'pdf')]",  # Enlaces PDF
                "//a[contains(text(), 'PDF') or contains(text(), 'pdf')]",  # Texto PDF
                "//a[contains(text(), 'Ver') and contains(@href, 'PDF')]",  # Ver PDF
            ]
            
            # Método 1: Verificar si hay PDF embebido (más fácil)
            try:
                iframe_pdf = driver.find_element(By.XPATH, "//iframe[contains(@src, 'mipeDisplayPDF')]")
                pdf_url = iframe_pdf.get_attribute('src')
                print(f"✅ PDF embebido encontrado: {pdf_url}")
                
                # Descargar desde iframe
                pdf_content = descargar_pdf_desde_url_venta(pdf_url, driver)
                
                if pdf_content:
                    filename = f"factura_venta_{factura.rut_receptor}_{factura.folio}_{factura.id}.pdf"
                    factura.pdf_documento.save(
                        filename,
                        ContentFile(pdf_content),
                        save=False
                    )
                    factura.pdf_descargado = True
                    factura.fecha_descarga_pdf = timezone.now()
                    factura.error_descarga_pdf = None
                    factura.save()
                    
                    print(f"✅ PDF de venta descargado y guardado para factura {factura.folio}")
                    return True
                    
            except NoSuchElementException:
                print("No hay PDF embebido, buscando enlaces...")
            
            # Método 2: Buscar enlaces PDF
            link_pdf = None
            for selector in selectores_pdf[1:]:  # Saltar el iframe
                try:
                    link_pdf = driver.find_element(By.XPATH, selector)
                    print(f"✅ Link PDF de venta encontrado con selector: {selector}")
                    break
                except:
                    continue
            
            if not link_pdf:
                error_msg = f"Link de PDF de venta no encontrado para factura {factura.folio}"
                print(f"❌ {error_msg}")
                factura.intentos_descarga_pdf += 1
                factura.error_descarga_pdf = error_msg
                factura.save()
                return False
            
            # Descargar PDF desde enlace
            url_pdf = link_pdf.get_attribute('href')
            print(f"✅ URL del PDF de venta: {url_pdf}")
            
            pdf_content = descargar_pdf_desde_url_venta(url_pdf, driver)
            
            if pdf_content:
                filename = f"factura_venta_{factura.rut_receptor}_{factura.folio}_{factura.id}.pdf"
                factura.pdf_documento.save(
                    filename,
                    ContentFile(pdf_content),
                    save=False
                )
                factura.pdf_descargado = True
                factura.fecha_descarga_pdf = timezone.now()
                factura.error_descarga_pdf = None
                factura.save()
                
                print(f"✅ PDF de venta descargado y guardado para factura {factura.folio}")
                return True
            else:
                error_msg = "No se pudo descargar el contenido del PDF de venta"
                print(f"❌ {error_msg}")
                factura.intentos_descarga_pdf += 1
                factura.error_descarga_pdf = error_msg
                factura.save()
                return False
                
        except Exception as e:
            error_msg = f"Error buscando/descargando PDF de venta: {str(e)}"
            print(f"❌ {error_msg}")
            factura.intentos_descarga_pdf += 1
            factura.error_descarga_pdf = error_msg
            factura.save()
            return False
            
    except Exception as e:
        error_msg = f"Error general descargando PDF para factura de venta {factura.folio}: {str(e)}"
        print(f"❌ {error_msg}")
        print(traceback.format_exc())
        factura.intentos_descarga_pdf += 1
        factura.error_descarga_pdf = error_msg
        factura.save()
        return False

def buscar_codigo_factura_venta_en_tabla(driver, wait, folio, rut_receptor):
    """
    Busca una factura de venta específica en la tabla de documentos emitidos
    """
    try:
        print(f"🔍 Buscando factura de venta: folio={folio}, RUT={rut_receptor}")
        
        # Esperar que la página se cargue completamente
        print("⏱️ Esperando carga completa de la página de venta...")
        time.sleep(8)
        
        # Asegurar que DataTables esté cargado
        max_intentos = 15
        for intento in range(max_intentos):
            try:
                tabla = driver.find_element(By.ID, "tablaDatos")
                loading_elements = driver.find_elements(By.CSS_SELECTOR, 
                    ".dataTables_processing, [class*='loading']")
                
                loading_visible = any(elem.is_displayed() for elem in loading_elements if elem.is_displayed())
                
                if not loading_visible and tabla.is_displayed():
                    print(f"✅ Tabla de venta cargada completamente (intento {intento + 1})")
                    break
                    
                print(f"⏳ Esperando carga completa de venta... intento {intento + 1}/{max_intentos}")
                time.sleep(2)
                
            except Exception:
                print(f"⏳ Tabla de venta no disponible aún... intento {intento + 1}/{max_intentos}")
                time.sleep(2)
        
        time.sleep(3)  # Espera adicional de seguridad
        
        # Obtener todas las filas
        try:
            filas = []
            
            # Estrategia 1: Filas en tbody
            try:
                tbody = driver.find_element(By.CSS_SELECTOR, "#tablaDatos tbody")
                filas_tbody = tbody.find_elements(By.TAG_NAME, "tr")
                filas.extend(filas_tbody)
            except:
                pass
            
            # Estrategia 2: Todas las filas de la tabla
            try:
                tabla = driver.find_element(By.ID, "tablaDatos")
                filas_tabla = tabla.find_elements(By.TAG_NAME, "tr")
                for fila in filas_tabla:
                    if fila.find_elements(By.TAG_NAME, "td"):  # Solo filas con celdas td
                        filas.append(fila)
            except:
                pass
            
            # Remover duplicados
            filas_unicas = []
            for fila in filas:
                if fila not in filas_unicas:
                    filas_unicas.append(fila)
            
            filas = filas_unicas
            
        except Exception as e:
            print(f"❌ Error obteniendo filas de venta: {str(e)}")
            return None
        
        print(f"📊 Total de filas de venta encontradas: {len(filas)}")
        
        if len(filas) == 0:
            print("❌ No se encontraron filas en la tabla de venta")
            return None
        
        # Mejorar normalización de RUT
        def normalizar_rut_mejorado_venta(rut_str):
            """Normaliza RUT con múltiples variaciones para venta"""
            if not rut_str:
                return ""
            
            # Limpiar espacios, puntos y guiones
            rut_limpio = str(rut_str).replace('.', '').replace(' ', '').replace('-', '').strip()
            
            if len(rut_limpio) >= 2:
                return rut_limpio
            
            return rut_limpio
        
        # Generar variaciones de RUT
        def generar_variaciones_rut_venta(rut_original):
            """Genera diferentes variaciones del RUT para buscar en venta"""
            rut_base = normalizar_rut_mejorado_venta(rut_original)
            
            variaciones = [
                rut_base,  # Sin guión
                rut_original,  # Original
            ]
            
            # Si no tiene guión, agregar con guión
            if '-' not in rut_original and len(rut_base) >= 2:
                rut_con_guion = f"{rut_base[:-1]}-{rut_base[-1]}"
                variaciones.append(rut_con_guion)
            
            # Si tiene guión, agregar sin guión
            if '-' in rut_original:
                rut_sin_guion = rut_original.replace('-', '')
                variaciones.append(rut_sin_guion)
            
            return list(set(variaciones))  # Eliminar duplicados
        
        variaciones_rut = generar_variaciones_rut_venta(rut_receptor)
        folio_buscar = str(folio).strip()
        
        print(f"🎯 Buscando Folio de venta='{folio_buscar}', RUT variaciones: {variaciones_rut}")
        
        # DEBUG: Mostrar estructura de primeras filas
        for i, fila in enumerate(filas[:3]):
            try:
                celdas = fila.find_elements(By.TAG_NAME, "td")
                if len(celdas) >= 5:
                    print(f"DEBUG fila venta {i}: {[c.text.strip()[:15] for c in celdas[:5]]}")
            except:
                pass
        
        # Buscar coincidencia con todas las variaciones
        for i, fila in enumerate(filas):
            try:
                celdas = fila.find_elements(By.TAG_NAME, "td")
                
                if len(celdas) >= 5:
                    # Columnas para documentos emitidos: 0=Ver, 1=Receptor, 2=Razón, 3=Documento, 4=Folio
                    rut_fila_original = celdas[1].text.strip()
                    rut_fila_normalizado = normalizar_rut_mejorado_venta(rut_fila_original)
                    folio_fila = celdas[4].text.strip()
                    
                    # Verificar coincidencia de folio
                    if folio_fila == folio_buscar:
                        # Verificar cualquier variación de RUT
                        rut_coincide = False
                        for var_rut in variaciones_rut:
                            var_normalizada = normalizar_rut_mejorado_venta(var_rut)
                            if (var_normalizada == rut_fila_normalizado or 
                                var_rut == rut_fila_original):
                                rut_coincide = True
                                break
                        
                        if rut_coincide:
                            print(f"🎉 ¡FACTURA DE VENTA ENCONTRADA en fila {i+1}!")
                            print(f"   Folio: {folio_fila} == {folio_buscar}")
                            print(f"   RUT: {rut_fila_original} coincide con variaciones de {rut_receptor}")
                            
                            # Extraer código del link en columna 0
                            try:
                                link_ver = celdas[0].find_element(By.TAG_NAME, "a")
                                href = link_ver.get_attribute('href')
                                print(f"🔗 Link de venta encontrado: {href}")
                                
                                # Extraer código usando regex
                                import re
                                match = re.search(r'CODIGO=([^&]+)', href)
                                if match:
                                    codigo = match.group(1)
                                    print(f"✅ Código SII de venta extraído: {codigo}")
                                    return codigo
                                else:
                                    print("❌ No se pudo extraer código del href de venta")
                                    
                            except Exception as e:
                                print(f"❌ Error extrayendo código de venta: {str(e)}")
                            
                            return None
                        
            except Exception as e:
                print(f"❌ Error procesando fila de venta {i+1}: {str(e)}")
                continue
        
        print(f"❌ Factura de venta {folio_buscar} - {rut_receptor} no encontrada en {len(filas)} filas")
        print(f"   Variaciones buscadas: {variaciones_rut}")
        return None
        
    except Exception as e:
        print(f"❌ Error crítico buscando en tabla de venta: {str(e)}")
        print(traceback.format_exc())
        return None

def descargar_pdf_desde_url_venta(url_pdf, driver):
    """
    Descarga el contenido del PDF de venta desde la URL usando las cookies de la sesión.
    """
    try:
        print(f"⬇️ Descargando PDF de venta desde: {url_pdf}")
        
        # Preparar sesión con cookies
        cookies = driver.get_cookies()
        print(f"Cookies obtenidas: {len(cookies)}")
        
        session = requests.Session()
        for cookie in cookies:
            session.cookies.set(cookie['name'], cookie['value'])
        
        # Configurar headers
        headers = {
            'User-Agent': driver.execute_script("return navigator.userAgent;"),
            'Accept': 'application/pdf,application/octet-stream,*/*',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Referer': driver.current_url
        }
        
        # Realizar descarga
        print("Realizando petición HTTP de venta...")
        
        response = session.get(
            url_pdf, 
            headers=headers, 
            timeout=30,
            stream=True  # Para manejar archivos grandes
        )
        
        response.raise_for_status()
        
        print(f"Respuesta HTTP de venta: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'N/A')}")
        
        # Validar contenido
        content = response.content
        print(f"Tamaño descargado de venta: {len(content)} bytes")
        
        # Verificar que es un PDF válido
        content_type = response.headers.get('content-type', '').lower()
        
        if 'pdf' in content_type:
            print("✅ Content-Type indica PDF de venta")
        elif content.startswith(b'%PDF'):
            print("✅ Contenido comienza con signature de PDF de venta")
        else:
            # Verificar si es HTML de error
            if content.startswith(b'<!DOCTYPE') or content.startswith(b'<html'):
                content_str = content.decode('utf-8', errors='ignore')[:500]
                print(f"❌ Recibido HTML en lugar de PDF de venta: {content_str}")
                return None
            else:
                print(f"⚠️ Content-Type no es PDF de venta pero el contenido parece binario")
        
        # Verificar tamaño mínimo
        if len(content) < 1024:  # Menos de 1KB es sospechoso
            print(f"❌ Archivo de venta muy pequeño: {len(content)} bytes")
            return None
        
        print(f"✅ PDF de venta válido descargado exitosamente")
        return content
        
    except requests.exceptions.Timeout:
        print(f"❌ Timeout descargando PDF de venta (30s)")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de red descargando PDF de venta: {str(e)}")
        return None
    except Exception as e:
        print(f"❌ Error inesperado descargando PDF de venta: {str(e)}")
        print(traceback.format_exc())
        return None

# ==================== FUNCIONES DE UTILIDAD ====================

def es_hora_de_ejecutar_venta(configuracion: ConfiguracionSIIAutomaticaVenta) -> bool:
    """
    Verifica si es hora de ejecutar usando zona horaria de Chile para venta
    """
    try:
        import pytz
        from django.utils import timezone
        
        chile_tz = pytz.timezone('America/Santiago')
        ahora_chile = timezone.now().astimezone(chile_tz)
        hora_configurada = configuracion.hora_ejecucion
        
        print(f"DEBUG VENTA: Hora actual Chile: {ahora_chile.strftime('%H:%M:%S')}")
        print(f"DEBUG VENTA: Hora configurada: {hora_configurada.strftime('%H:%M:%S')}")
        
        # Ejecutar si estamos dentro de una ventana de 10 minutos
        if (ahora_chile.hour == hora_configurada.hour and 
            abs(ahora_chile.minute - hora_configurada.minute) <= 10):
            print(f"DEBUG VENTA: ¡Es hora de ejecutar! Configuración ID: {configuracion.id}")
            return True
        
        return False
        
    except Exception as e:
        print(f"Error verificando hora de ejecución de venta: {str(e)}")
        return False

def validar_y_convertir_fecha_params_venta(mes, ano):
    """
    Valida y convierte parámetros de fecha a enteros para venta
    """
    try:
        if isinstance(mes, str):
            mes_int = int(mes)
        else:
            mes_int = int(mes)
            
        if isinstance(ano, str):
            ano_int = int(ano)
        else:
            ano_int = int(ano)
            
        # Validaciones básicas
        if not (1 <= mes_int <= 12):
            raise ValueError(f"Mes inválido de venta: {mes_int}")
            
        if not (2000 <= ano_int <= 2100):
            raise ValueError(f"Año inválido de venta: {ano_int}")
            
        return mes_int, ano_int
        
    except (ValueError, TypeError) as e:
        print(f"Error validando parámetros de fecha de venta: {str(e)}")
        raise

# ==================== TAREAS DE NOTIFICACIÓN ====================

@shared_task
def enviar_notificacion_error_venta(asunto: str, mensaje: str, detalle: str = ""):
    """
    Envía notificación por email cuando hay errores críticos en venta.
    """
    try:
        if hasattr(settings, 'ADMINS') and settings.ADMINS:
            destinatarios = [admin[1] for admin in settings.ADMINS]
            
            mensaje_completo = f"""
            {mensaje}
            
            Detalle:
            {detalle}
            
            Timestamp: {timezone.now()}
            Sistema: Facturas Automáticas SII - VENTA
            """
            
            send_mail(
                subject=f"[Sistema Automático VENTA] {asunto}",
                message=mensaje_completo,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=destinatarios,
                fail_silently=False
            )
            
            print(f"Notificación de error de venta enviada: {asunto}")
        else:
            print("No hay administradores configurados para notificaciones de venta")
            
    except Exception as e:
        print(f"Error enviando notificación de venta: {str(e)}")

# ==================== TAREAS DE LIMPIEZA ====================

@shared_task
def limpiar_facturas_venta_antiguas():
    """
    Limpia facturas de venta antiguas procesadas (más de 6 meses)
    """
    print("🧹 Iniciando limpieza de facturas de venta antiguas...")
    
    try:
        fecha_limite = timezone.now() - timedelta(days=180)  # 6 meses
        
        # Facturas completamente distribuidas y antiguas
        facturas_antiguas = FacturaVentaSIIPorDistribuir.objects.filter(
            procesada=True,
            fecha_encontrada__lt=fecha_limite
        )
        
        count = facturas_antiguas.count()
        
        if count > 0:
            facturas_antiguas.delete()
            print(f"🗑️ Eliminadas {count} facturas de venta antiguas")
        else:
            print("✅ No hay facturas de venta antiguas para eliminar")
        
        return {
            'status': 'success',
            'facturas_eliminadas': count,
            'timestamp': timezone.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Error en limpieza de facturas de venta: {str(e)}")
        return {
            'status': 'error',
            'message': str(e)
        }   
