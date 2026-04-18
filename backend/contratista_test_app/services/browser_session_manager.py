import os
import time
import uuid
import threading
import random
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

logger = logging.getLogger(__name__)

class BrowserSession:
    """
    Representa una sesión de navegador para un usuario específico con técnicas
    avanzadas anti-detección para interactuar con el SII.
    """
    def __init__(self, user_id):
        self.session_id = str(uuid.uuid4())
        self.user_id = user_id
        self.driver = None
        self.wait = None
        self.last_activity = time.time()
        self.empresa_seleccionada = None
        self.cookies = None
        self.init_attempts = 0
        
        # NUEVO: Definir directorio de descarga específico
        self.downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        
        # Crear directorio si no existe
        os.makedirs(self.downloads_dir, exist_ok=True)
        
    def initialize(self):
        """Inicializa el navegador con técnicas anti-detección avanzadas"""
        self.init_attempts += 1
        
        # Configurar opciones
        options = webdriver.ChromeOptions()

        options.binary_location = '/usr/bin/chromium-browser'

        
        # En producción, mantener headless. En pruebas, comentar esta línea para ver el navegador
        if self.init_attempts <= 2:  # Solo usar headless en los primeros intentos
            options.add_argument('--headless')
        
        # Configuraciones para evitar detección
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-gpu')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--start-maximized')
        options.add_argument('--window-size=1920,1080')
        
        # NUEVO: Configuraciones específicas para descargas automáticas
        options.add_argument('--disable-popup-blocking')
        options.add_argument('--disable-default-apps')
        options.add_argument('--disable-notifications')
        options.add_argument('--disable-features=VizDisplayCompositor')
        options.add_argument('--disable-features=DownloadBubble')  # NUEVO en Chrome 118+
        options.add_argument('--disable-features=DownloadBubbleV2')  # NUEVO
        options.add_argument('--disable-web-security')
        options.add_argument('--allow-running-insecure-content')
        
        # Rotar user-agents para parecer distintos navegadores
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.47',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
        ]
        options.add_argument(f'--user-agent={random.choice(user_agents)}')
        
        # CONFIGURACIONES MEJORADAS PARA DESCARGAS
        prefs = {
            "profile.default_content_setting_values.notifications": 2,
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
            "webrtc.ip_handling_policy": "disable_non_proxied_udp",
            "webrtc.multiple_routes_enabled": False,
            "webrtc.nonproxied_udp_enabled": False,
            "profile.default_content_settings.popups": 0,
            
            # CONFIGURACIONES CRÍTICAS PARA DESCARGAS
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "download.default_directory": self.downloads_dir,  # CLAVE: Directorio específico
            "download.extensions_to_open": "",  # No abrir archivos automáticamente
            "safebrowsing.enabled": False,
            "safebrowsing.disable_download_protection": True,  # NUEVO
            
            # CONFIGURACIONES ADICIONALES PARA SEGURIDAD DE DESCARGAS
            "browser.download.folderList": 2,
            "browser.download.manager.showWhenStarting": False,
            "browser.download.dir": self.downloads_dir,
            "browser.helperApps.neverAsk.saveToDisk": "text/csv,application/csv,application/vnd.ms-excel,application/octet-stream",
            
            # CONFIGURACIONES ESPECÍFICAS PARA CSV
            "browser.helperApps.neverAsk.openFile": "",
            "browser.download.useDownloadDir": True,
            "browser.download.viewableInternally.enabledTypes": "",
            
            # CONFIGURACIONES PARA EVITAR POPUPS
            "profile.default_content_setting_values.automatic_downloads": 1,
            "profile.managed_default_content_settings.images": 2
        }
        
        options.add_experimental_option("prefs", prefs)
        options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        options.add_experimental_option("useAutomationExtension", False)
        
        # Crear driver con las opciones
        try:
            self.driver = webdriver.Chrome(options=options)
            
            # NUEVO: Configurar capacidades de descarga usando Chrome DevTools Protocol
            try:
                self.driver.execute_cdp_cmd('Page.setDownloadBehavior', {
                    'behavior': 'allow',
                    'downloadPath': self.downloads_dir
                })
                logger.info(f"Directorio de descarga configurado via CDP: {self.downloads_dir}")
            except Exception as e:
                logger.warning(f"No se pudo configurar descarga via CDP: {e}")
            
            # Script de "estealth" avanzado para eludir detecciones
            stealth_js = """
            // Quitar navigator.webdriver flag
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            // Quitar flags del window.navigator.chrome
            window.navigator.chrome = {
                runtime: {},
                app: {},
                loadTimes: function() {},
                csi: function() {},
                runtime: {}
            };
            
            // Falsificar plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [
                    {
                        0: {type: "application/x-google-chrome-pdf", suffixes: "pdf", description: "Portable Document Format"},
                        description: "Portable Document Format",
                        filename: "internal-pdf-viewer",
                        length: 1,
                        name: "Chrome PDF Plugin"
                    },
                    {
                        0: {type: "application/pdf", suffixes: "pdf", description: "Portable Document Format"},
                        description: "Portable Document Format",
                        filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai",
                        length: 1,
                        name: "Chrome PDF Viewer"
                    },
                    {
                        0: {type: "application/x-shockwave-flash", suffixes: "swf", description: "Shockwave Flash"},
                        description: "Shockwave Flash",
                        filename: "internal-flash-player",
                        length: 1,
                        name: "Shockwave Flash"
                    }
                ]
            });
            
            // Falsificar idiomas
            Object.defineProperty(navigator, 'languages', {
                get: () => ['es-CL', 'es', 'en-US', 'en']
            });
            
            // Falsificar platform
            Object.defineProperty(navigator, 'platform', {
                get: () => 'Linux x86_64'
            });
            
            // Falsificar compatibilidad con Flash
            Object.defineProperty(navigator, 'mimeTypes', {
                get: () => [
                    {
                        type: "application/pdf",
                        suffixes: "pdf",
                        description: "Portable Document Format",
                        enabledPlugin: {
                            name: "Chrome PDF Plugin",
                            filename: "internal-pdf-viewer"
                        }
                    },
                    {
                        type: "application/x-google-chrome-pdf",
                        suffixes: "pdf",
                        description: "Portable Document Format",
                        enabledPlugin: {
                            name: "Chrome PDF Plugin",
                            filename: "internal-pdf-viewer"
                        }
                    },
                    {
                        type: "application/x-shockwave-flash",
                        suffixes: "swf",
                        description: "Shockwave Flash",
                        enabledPlugin: {
                            name: "Shockwave Flash",
                            filename: "internal-flash-player"
                        }
                    }
                ]
            });
            
            // Falsificar fingerprints de WebGL
            const getParameter = WebGLRenderingContext.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                // UNMASKED_VENDOR_WEBGL
                if (parameter === 37445) {
                    return 'Google Inc. (Intel)';
                }
                // UNMASKED_RENDERER_WEBGL
                if (parameter === 37446) {
                    return 'ANGLE (Intel, Intel(R) UHD Graphics Direct3D11 vs_5_0 ps_5_0, D3D11)';
                }
                return getParameter(parameter);
            };
            
            // Añadir recaptcha window
            window.recaptcha = {};
            
            // NUEVO: Sobreescribir funciones de descarga para debugging
            window.downloadDebug = true;
            const originalOpen = window.open;
            window.open = function(...args) {
                console.log('window.open intercepted:', args);
                return originalOpen.apply(this, args);
            };
            """
            
            self.driver.execute_script(stealth_js)
            
            # Simular actividad de mousepad para parecer humano
            try:
                mouse_js = """
                document.addEventListener('mousemove', function(e) {
                    window.lastMouseX = e.clientX;
                    window.lastMouseY = e.clientY;
                });
                """
                self.driver.execute_script(mouse_js)
            except:
                pass
            
            # Configurar timeouts más altos para descargas
            self.driver.implicitly_wait(10)
            self.driver.set_page_load_timeout(60)  # Aumentado para paginas lentas del SII
            
            # Crear objeto de espera (wait) con un timeout razonable
            self.wait = WebDriverWait(self.driver, 30)
            
            # Actualizar timestamp de última actividad
            self.update_activity()
            
            logger.info(f"Sesión {self.session_id} inicializada correctamente")
            logger.info(f"Directorio de descarga configurado: {self.downloads_dir}")
            return self
            
        except Exception as e:
            logger.error(f"Error al inicializar sesión: {str(e)}")
            if self.driver:
                self.driver.quit()
            
            # Si fallamos, intentamos una vez más sin modo headless
            if '--headless' in options.arguments and self.init_attempts <= 3:
                logger.info("Reintentando sin modo headless...")
                return self.initialize()
                
            raise
    
    def get_downloads_directory(self):
        """Retorna el directorio de descargas configurado para esta sesión"""
        return self.downloads_dir
    
    def verify_download_setup(self):
        """Verifica que la configuración de descarga esté correcta"""
        try:
            # Verificar directorio
            if not os.path.exists(self.downloads_dir):
                logger.error(f"Directorio de descarga no existe: {self.downloads_dir}")
                return False
            
            if not os.access(self.downloads_dir, os.W_OK):
                logger.error(f"Directorio de descarga no es escribible: {self.downloads_dir}")
                return False
            
            # Verificar configuración del navegador
            if self.driver:
                download_path = self.driver.execute_script("return navigator.userAgent")
                logger.info(f"User Agent configurado: {download_path[:100]}...")
            
            logger.info("Configuración de descarga verificada correctamente")
            return True
            
        except Exception as e:
            logger.error(f"Error verificando configuración de descarga: {e}")
            return False
    
    def force_download_permissions(self):
        """Fuerza permisos de descarga usando JavaScript"""
        try:
            if not self.driver:
                return False
                
            # Script para forzar permisos de descarga
            download_permission_js = """
            // Simular que el usuario dio permisos de descarga
            Object.defineProperty(navigator, 'permissions', {
                value: {
                    query: function() {
                        return Promise.resolve({state: 'granted'});
                    }
                }
            });
            
            // Permitir descargas automáticas
            if (window.chrome && window.chrome.downloads) {
                window.chrome.downloads.download = function(options, callback) {
                    console.log('Download intercepted:', options);
                    if (callback) callback();
                };
            }
            
            return 'Download permissions set';
            """
            
            result = self.driver.execute_script(download_permission_js)
            logger.info(f"Permisos de descarga forzados: {result}")
            return True
            
        except Exception as e:
            logger.warning(f"No se pudieron forzar permisos de descarga: {e}")
            return False
    
    def refresh_cookies(self):
        """Refresca las cookies para mantener la sesión"""
        if not self.driver:
            return None
            
        try:
            # Guardar las cookies actuales
            self.cookies = self.driver.get_cookies()
            
            # Opcionalmente, podemos limpiar y restaurar para refrescar la sesión
            # self.driver.delete_all_cookies()
            # for cookie in self.cookies:
            #     try:
            #         self.driver.add_cookie(cookie)
            #     except Exception as cookie_err:
            #         logger.warning(f"No se pudo añadir cookie: {str(cookie_err)}")
                    
            logger.debug(f"Cookies refrescadas ({len(self.cookies)} cookies)")
            return self.cookies
        except Exception as e:
            logger.warning(f"Error al refrescar cookies: {str(e)}")
            return None
    
    def update_activity(self):
        """Actualiza el timestamp de última actividad"""
        self.last_activity = time.time()
    
    def is_expired(self, timeout_seconds=1800):  # 30 minutos por defecto
        """Verifica si la sesión ha expirado basado en la inactividad"""
        return (time.time() - self.last_activity) > timeout_seconds
    
    def simulate_human_interaction(self):
        """Simula interacciones humanas básicas para evitar detección"""
        if not self.driver:
            return
            
        try:
            # Mover mouse a posiciones aleatorias
            for _ in range(2):
                x = random.randint(100, 700)
                y = random.randint(100, 500)
                self.driver.execute_script(f"window.scrollTo({x}, {y})")
                time.sleep(random.uniform(0.3, 0.7))
            
            # Pequeños movimientos del scroll
            scroll_y = random.randint(50, 200)
            self.driver.execute_script(f"window.scrollTo(0, {scroll_y})")
            time.sleep(random.uniform(0.5, 1.2))
            self.driver.execute_script(f"window.scrollTo(0, 0)")
            
            logger.debug(f"Interacción humana simulada en sesión {self.session_id}")
        except Exception as e:
            logger.warning(f"Error en simulación humana: {str(e)}")
    
    def verify_connection(self):
        """Verifica que la conexión sigue activa, útil después de periodos de inactividad"""
        if not self.driver:
            return False
            
        try:
            # Intentar acceder a una propiedad para verificar que el navegador sigue respondiendo
            current_url = self.driver.current_url
            return True
        except WebDriverException:
            logger.warning(f"Conexión rota en sesión {self.session_id}")
            return False
    
    def cleanup(self):
        """Limpia los recursos del navegador"""
        if self.driver:
            try:
                # Intentar cerrar correctamente manejando cualquier alerta
                try:
                    self.driver.execute_script("window.onbeforeunload = function() {};")
                except:
                    pass
                    
                try:
                    alert = self.driver.switch_to.alert
                    alert.accept()
                except:
                    pass
                    
                self.driver.quit()
                logger.info(f"Navegador de la sesión {self.session_id} cerrado correctamente")
            except Exception as e:
                logger.error(f"Error al cerrar navegador de la sesión {self.session_id}: {str(e)}")
        
        self.driver = None
        self.wait = None

class BrowserSessionManager:
    """
    Administra las sesiones de navegador para múltiples usuarios.
    Implementa un sistema de limpieza periódica para sesiones inactivas.
    """
    _instance = None
    
    @classmethod
    def get_instance(cls):
        """Implementa el patrón Singleton para asegurar una única instancia"""
        if cls._instance is None:
            cls._instance = BrowserSessionManager()
        return cls._instance
    
    def __init__(self):
        self.sessions = {}  # Map: session_id -> BrowserSession
        self.user_sessions = {}  # Map: user_id -> session_id
        self.lock = threading.RLock()  # Para sincronización en entornos multi-hilo
        
        # Iniciar hilo de limpieza
        self.cleanup_thread = threading.Thread(target=self._cleanup_expired_sessions, daemon=True)
        self.cleanup_thread.start()
    
    def create_session(self, user_id):
        """
        Crea una nueva sesión de navegador para un usuario.
        Si ya existe una sesión para el usuario, la cierra primero.
        """
        with self.lock:
            # Si el usuario ya tiene una sesión, cerrarla
            if user_id in self.user_sessions:
                self.close_session(self.user_sessions[user_id])
            
            # Crear nueva sesión
            session = BrowserSession(user_id).initialize()
            
            # Verificar configuración de descarga
            session.verify_download_setup()
            session.force_download_permissions()
            
            self.sessions[session.session_id] = session
            self.user_sessions[user_id] = session.session_id
            
            logger.info(f"Creada nueva sesión {session.session_id} para usuario {user_id}")
            return session
    
    def get_session(self, session_id=None, user_id=None):
        """
        Obtiene una sesión existente por su ID o por el ID de usuario.
        Actualiza el timestamp de última actividad.
        """
        with self.lock:
            # Buscar por session_id directo
            if session_id and session_id in self.sessions:
                session = self.sessions[session_id]
                
                # Verificar que la conexión sigue activa
                if not session.verify_connection():
                    logger.warning(f"Conexión perdida en sesión {session_id}, recreando")
                    self.close_session(session_id)
                    if user_id:
                        return self.create_session(user_id)
                    return None
                
                session.update_activity()
                return session
            
            # Buscar por user_id
            if user_id and user_id in self.user_sessions:
                session_id = self.user_sessions[user_id]
                if session_id in self.sessions:
                    session = self.sessions[session_id]
                    
                    # Verificar que la conexión sigue activa
                    if not session.verify_connection():
                        logger.warning(f"Conexión perdida en sesión {session_id}, recreando")
                        self.close_session(session_id)
                        return self.create_session(user_id)
                    
                    session.update_activity()
                    return session
            
            return None
    
    def close_session(self, session_id):
        """Cierra una sesión específica y libera sus recursos"""
        with self.lock:
            if session_id in self.sessions:
                session = self.sessions[session_id]
                # Eliminar mapeo de usuario a sesión
                if session.user_id in self.user_sessions and self.user_sessions[session.user_id] == session_id:
                    del self.user_sessions[session.user_id]
                
                # Limpiar recursos
                session.cleanup()
                
                # Eliminar sesión
                del self.sessions[session_id]
                logger.info(f"Sesión {session_id} cerrada y eliminada")
    
    def get_session_stats(self):
        """Retorna estadísticas de las sesiones activas"""
        with self.lock:
            return {
                'total_sessions': len(self.sessions),
                'active_users': len(self.user_sessions),
                'session_ids': list(self.sessions.keys())
            }
    
    def _cleanup_expired_sessions(self):
        """
        Hilo background que limpia periódicamente las sesiones inactivas.
        """
        while True:
            try:
                time.sleep(300)  # Verificar cada 5 minutos
                
                with self.lock:
                    # Identificar sesiones expiradas
                    expired_sessions = [sid for sid, session in self.sessions.items() if session.is_expired()]
                    
                    # Cerrar cada sesión expirada
                    for sid in expired_sessions:
                        logger.info(f"Eliminando sesión inactiva {sid}")
                        self.close_session(sid)
                        
                    if expired_sessions:
                        logger.info(f"Limpieza completada: {len(expired_sessions)} sesiones eliminadas")
                        
            except Exception as e:
                logger.error(f"Error en el hilo de limpieza: {str(e)}")