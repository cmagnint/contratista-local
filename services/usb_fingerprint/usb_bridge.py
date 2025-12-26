from flask import Flask, jsonify
import usb.core
import usb.util
import base64
from PIL import Image
import io
import numpy as np
import time

app = Flask(__name__)
device_handle = None

class UareU4500:
    """Comandos USB correctos extraídos de captura Wireshark"""
    
    VID = 0x05ba
    PID = 0x000a
    
    # Comandos vendor identificados en Wireshark
    CMD_VENDOR_MAIN = 12
    CMD_CONFIG = 4
    
    # Endpoint correcto según Wireshark
    ENDPOINT_IN = 0x82  # Corregido de 0x81
    
    # Tamaño esperado de imagen
    IMAGE_SIZE_EXPECTED = 111067
    
    @staticmethod
    def initialize_device(dev):
        """Secuencia de inicialización basada en análisis Wireshark"""
        print("🔧 Inicializando U.are.U 4500...")
        
        # Comando 1: Setup inicial (wValue=0x004e, Data=0x20)
        try:
            print("  → Comando setup 1...")
            dev.ctrl_transfer(0x40, 12, 0x004e, 0, [0x20], timeout=2000)
            time.sleep(0.1)
        except Exception as e:
            print(f"  ⚠️  Setup 1: {e}")
        
        # Comando 2: Activación (wValue=0x0020, Data=0x05)
        try:
            print("  → Comando activación...")
            dev.ctrl_transfer(0x40, 12, 0x0020, 0, [0x05], timeout=2000)
            time.sleep(0.1)
        except Exception as e:
            print(f"  ⚠️  Activación: {e}")
        
        # Comando 3: Setup 2 (wValue=0x004e, Data=0x30)
        try:
            print("  → Comando setup 2...")
            dev.ctrl_transfer(0x40, 12, 0x004e, 0, [0x30], timeout=2000)
            time.sleep(0.1)
        except Exception as e:
            print(f"  ⚠️  Setup 2: {e}")
        
        # Comando 4: Configuración de captura - MODIFICADO para RAW
        try:
            print("  → Comando config captura (modo RAW)...")
            # Cambiar parámetros para forzar imagen RAW
            # 0x08, 0x29 puede ser el modo comprimido
            # Probar: 0x00, 0x00 para raw sin compresión
            dev.ctrl_transfer(0x40, 4, 0x0033, 0, [0x00, 0x00, 0x00, 0x00, 0x00], timeout=2000)
            time.sleep(0.1)
        except Exception as e:
            print(f"  ⚠️  Config: {e}")
        
        # Comando 5: Leer estado (Device-to-host)
        try:
            print("  → Leer estado...")
            status = dev.ctrl_transfer(0xC0, 12, 0x0090, 0, 1, timeout=2000)
            print(f"  ✓ Status: {status.tobytes().hex()}")
        except Exception as e:
            print(f"  ⚠️  Status: {e}")
        
        # Comando 6: Configurar status
        try:
            print("  → Set status...")
            dev.ctrl_transfer(0x40, 12, 0x0090, 0, [0x83], timeout=2000)
            time.sleep(0.1)
        except Exception as e:
            print(f"  ⚠️  Set status: {e}")
        
        # Comando 7: Leer información del dispositivo
        try:
            print("  → Leer info...")
            info = dev.ctrl_transfer(0xC0, 4, 0x2020, 0, 16, timeout=2000)
            print(f"  ✓ Info: {info.tobytes().hex()}")
        except Exception as e:
            print(f"  ⚠️  Info: {e}")
        
        print("✓ Inicialización completa")
        return True
    
    @staticmethod
    def wait_for_finger(dev):
        """Esperar evento INTERRUPT que indica dedo en sensor"""
        print("👆 Esperando que coloques el dedo...")
        
        try:
            # Leer del endpoint INTERRUPT (0x81)
            interrupt_data = dev.read(0x81, 64, timeout=15000)
            print(f"  ✓ Dedo detectado! ({len(interrupt_data)} bytes de evento)")
            print(f"  → Datos: {interrupt_data.tobytes().hex()[:40]}...")
            
            # CRÍTICO: Enviar comandos de activación de streaming
            print("  → Activando streaming completo...")
            try:
                dev.ctrl_transfer(0x40, 12, 0x004e, 0, [0x20], timeout=1000)
                time.sleep(0.05)
            except Exception as e:
                print(f"    ⚠️  Cmd1: {e}")
            
            try:
                dev.ctrl_transfer(0x40, 12, 0x0020, 0, [0x05], timeout=1000)
                time.sleep(0.05)
            except Exception as e:
                print(f"    ⚠️  Cmd2: {e}")
            
            print("  ✓ Streaming activado")
            return True
            
        except usb.core.USBTimeoutError:
            print(f"  ⚠️  Timeout - no se detectó dedo en 15 segundos")
            return False
        except Exception as e:
            print(f"  ⚠️  Error esperando dedo: {e}")
            return False
    
    @staticmethod
    def finalize_capture(dev):
        """Finalizar captura y apagar LED"""
        print("🔄 Finalizando captura...")
        
        # Apagar LED / modo captura
        try:
            dev.ctrl_transfer(0x40, 12, 0x004e, 0, [0x30], timeout=1000)
            time.sleep(0.1)
            print("  ✓ LED apagado")
        except Exception as e:
            print(f"  ⚠️  LED off: {e}")
        
        # Comando de finalización
        try:
            dev.ctrl_transfer(0x40, 12, 0x0090, 0, [0x00], timeout=1000)
            time.sleep(0.1)
            print("  ✓ Sensor en reposo")
        except Exception as e:
            print(f"  ⚠️  Finalización: {e}")
    
    @staticmethod
    def capture_fingerprint(dev):
        """Captura desde endpoint 0x82 con lectura completa"""
        print("📸 Iniciando captura...")
        
        # CRÍTICO: Esperar evento INTERRUPT primero
        if not UareU4500.wait_for_finger(dev):
            print("  ❌ No se detectó dedo, abortando captura")
            return None
        
        print("🔄 Leyendo imagen desde BULK...")
        
        raw_data = bytearray()
        chunk_size = 4096  # 4KB chunks (más frecuente)
        max_iterations = 50  # Aumentar iteraciones
        
        try:
            for i in range(max_iterations):
                try:
                    # Leer desde endpoint 0x82
                    chunk = dev.read(UareU4500.ENDPOINT_IN, chunk_size, timeout=10000)
                    raw_data.extend(chunk)
                    
                    # Log cada 4KB
                    if len(raw_data) % 4096 == 0:
                        print(f"  → {len(raw_data)} bytes...")
                    
                    # Comando de continuación cada 20KB (si es necesario)
                    if len(raw_data) % 20480 == 0 and len(raw_data) < UareU4500.IMAGE_SIZE_EXPECTED:
                        try:
                            dev.ctrl_transfer(0x40, 12, 0x0090, 0, [0x83], timeout=1000)
                        except:
                            pass
                    
                    # Verificar si ya tenemos imagen completa
                    if len(raw_data) >= UareU4500.IMAGE_SIZE_EXPECTED:
                        print(f"  ✓ Imagen completa alcanzada")
                        break
                        
                except usb.core.USBTimeoutError:
                    # Timeout normal - fin de transmisión
                    if len(raw_data) > 0:
                        print(f"  ✓ Timeout - fin de lectura")
                        break
                    else:
                        print(f"  ⚠️  Timeout sin datos")
                        raise
                        
        except Exception as e:
            print(f"  ⚠️  Error leyendo: {e}")
            if len(raw_data) == 0:
                return None
        
        print(f"  ✓ Total capturado: {len(raw_data)} bytes")
        
        # Finalizar captura y apagar LED
        UareU4500.finalize_capture(dev)
        
        return bytes(raw_data)
    
    @staticmethod
    def raw_to_image(raw_data, save_path=None):
        """Convertir datos RAW a imagen PIL"""
        if not raw_data or len(raw_data) == 0:
            return None
        
        try:
            print(f"  → Convirtiendo {len(raw_data)} bytes a imagen...")
            
            # Debug: Guardar datos crudos para análisis
            if save_path:
                raw_path = save_path.replace('.png', '_raw.bin')
                with open(raw_path, 'wb') as f:
                    f.write(raw_data)
                print(f"  💾 Datos crudos guardados: {raw_path}")
            
            # Buscar posibles offsets (headers comunes: 64, 128, 256, 512, 1024)
            possible_offsets = [0, 64, 128, 256, 512, 1024, 2048]
            
            for offset in possible_offsets:
                if len(raw_data) - offset >= 92160:
                    try:
                        # Intentar crear imagen desde este offset
                        img_array = np.frombuffer(raw_data[offset:offset+92160], dtype=np.uint8)
                        img_array = img_array.reshape((360, 256))
                        img = Image.fromarray(img_array, mode='L')
                        
                        # Guardar con sufijo de offset
                        if save_path:
                            test_path = save_path.replace('.png', f'_offset{offset}.png')
                            img.save(test_path)
                            print(f"  💾 Prueba offset {offset}: {test_path}")
                        
                        # Si es offset 0, retornar esta como principal
                        if offset == 0 and save_path:
                            img.save(save_path)
                            print(f"  ✓ Imagen principal guardada")
                        
                    except Exception as e:
                        print(f"  ⚠️  Offset {offset} falló: {e}")
            
            # Retornar imagen desde offset 0 por defecto
            if len(raw_data) >= 92160:
                img_array = np.frombuffer(raw_data[:92160], dtype=np.uint8)
                img_array = img_array.reshape((360, 256))
                return Image.fromarray(img_array, mode='L')
            
            # Caso 2: Datos parciales - generar imagen de prueba
            else:
                print(f"  ⚠️  Datos insuficientes ({len(raw_data)} bytes)")
                img = Image.new('L', (256, 360), color=200)
                pixels = img.load()
                
                # Usar datos disponibles
                for i in range(min(len(raw_data), 256)):
                    for j in range(360):
                        if i < len(raw_data):
                            pixels[i, j] = raw_data[i % len(raw_data)]
                
                print(f"  ✓ Imagen de prueba generada")
                return img
                
        except Exception as e:
            print(f"  ⚠️  Error convirtiendo: {e}")
            return None


@app.route('/list-devices', methods=['GET'])
def list_devices():
    devices = usb.core.find(find_all=True)
    device_list = []
    for dev in devices:
        device_list.append({
            'vid': hex(dev.idVendor),
            'pid': hex(dev.idProduct),
            'bus': dev.bus,
            'address': dev.address,
            'is_uareu': (dev.idVendor == UareU4500.VID and dev.idProduct == UareU4500.PID)
        })
    return jsonify(device_list)


@app.route('/capture-image-raw', methods=['POST'])
def capture_image_raw():
    """Captura imagen RAW visual (256x360 píxeles) sin template"""
    global device_handle
    
    try:
        print("\n" + "="*60)
        print("🔍 MODO IMAGEN RAW - Buscando dispositivo...")
        dev = usb.core.find(idVendor=UareU4500.VID, idProduct=UareU4500.PID)
        
        if dev is None:
            return jsonify({'error': 'Dispositivo no encontrado'}), 404
        
        print(f"✓ Encontrado: Bus {dev.bus}, Address {dev.address}")
        
        # Configurar dispositivo (mismo proceso)
        print("🔓 Desvinculando drivers...")
        try:
            for cfg in dev:
                for intf in cfg:
                    if_num = intf.bInterfaceNumber
                    try:
                        if dev.is_kernel_driver_active(if_num):
                            dev.detach_kernel_driver(if_num)
                    except:
                        pass
        except:
            pass
        
        print("⚙️  Configurando...")
        try:
            if device_handle is None:
                try:
                    dev.reset()
                    time.sleep(0.5)
                except:
                    pass
            dev.set_configuration()
        except usb.core.USBError as e:
            if e.errno == 16:
                usb.util.dispose_resources(dev)
                time.sleep(0.5)
                dev = usb.core.find(idVendor=UareU4500.VID, idProduct=UareU4500.PID)
                dev.set_configuration()
        
        device_handle = dev
        
        # Inicialización básica
        print("🔧 Inicializando...")
        try:
            dev.ctrl_transfer(0x40, 12, 0x004e, 0, [0x20], timeout=2000)
            time.sleep(0.1)
            dev.ctrl_transfer(0x40, 12, 0x0020, 0, [0x05], timeout=2000)
            time.sleep(0.1)
        except Exception as e:
            print(f"  ⚠️  Init: {e}")
        
        # Esperar dedo
        print("👆 Esperando dedo...")
        try:
            interrupt_data = dev.read(0x81, 64, timeout=15000)
            print(f"  ✓ Dedo detectado!")
        except usb.core.USBTimeoutError:
            return jsonify({'error': 'Timeout - no se detectó dedo'}), 408
        
        # INTENTAR CAPTURA DIRECTA SIN COMANDOS DE TEMPLATE
        print("📸 Capturando imagen RAW directa...")
        
        raw_data = bytearray()
        expected_size = 92160  # 256x360 = 92160 bytes
        chunk_size = 4096
        
        try:
            for i in range(30):
                try:
                    chunk = dev.read(0x82, chunk_size, timeout=3000)
                    raw_data.extend(chunk)
                    
                    if len(raw_data) % 16384 == 0:
                        print(f"  → {len(raw_data)} bytes...")
                    
                    # Si ya tenemos suficiente para una imagen
                    if len(raw_data) >= expected_size:
                        break
                        
                except usb.core.USBTimeoutError:
                    if len(raw_data) >= expected_size:
                        break
                    # Si tenemos datos pero no los suficientes, continuar
                    if len(raw_data) > 0 and len(raw_data) < expected_size:
                        continue
                    break
                    
        except Exception as e:
            print(f"  ⚠️  Error: {e}")
        
        print(f"  ✓ Total capturado: {len(raw_data)} bytes")
        
        # Finalizar
        try:
            dev.ctrl_transfer(0x40, 12, 0x004e, 0, [0x30], timeout=1000)
            dev.ctrl_transfer(0x40, 12, 0x0090, 0, [0x00], timeout=1000)
        except:
            pass
        
        if len(raw_data) < 92160:
            return jsonify({
                'error': f'Datos insuficientes: {len(raw_data)} bytes (se necesitan 92160)',
                'bytes_received': len(raw_data)
            }), 500
        
        # Convertir primeros 92160 bytes a imagen
        img_array = np.frombuffer(raw_data[:92160], dtype=np.uint8)
        img_array = img_array.reshape((360, 256))
        img = Image.fromarray(img_array, mode='L')
        
        # Guardar imagen
        import os
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        img_path = os.path.join(os.path.dirname(__file__), f"imagen_raw_{timestamp}.png")
        img.save(img_path)
        print(f"💾 Imagen guardada: {img_path}")
        
        # Convertir a base64
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        img_base64 = base64.b64encode(img_byte_arr).decode()
        
        print("="*60)
        print("✅ IMAGEN RAW CAPTURADA")
        print(f"   Tamaño: 256x360 píxeles")
        print("="*60 + "\n")
        
        return jsonify({
            'success': True,
            'image_base64': img_base64,
            'width': 256,
            'height': 360,
            'bytes_received': len(raw_data),
            'message': 'Imagen RAW capturada'
        })
        
    except Exception as e:
        import traceback
        print("\n" + "="*60)
        print("❌ ERROR:")
        print(traceback.format_exc())
        print("="*60 + "\n")
        device_handle = None
        return jsonify({'error': str(e)}), 500


@app.route('/capture-fingerprint', methods=['POST'])
def capture():
    global device_handle
    
    try:
        print("\n" + "="*60)
        print("🔍 Buscando U.are.U 4500...")
        dev = usb.core.find(idVendor=UareU4500.VID, idProduct=UareU4500.PID)
        
        if dev is None:
            return jsonify({'error': 'Dispositivo U.are.U 4500 no encontrado'}), 404
        
        print(f"✓ Encontrado: Bus {dev.bus}, Address {dev.address}")
        
        # Desvincular kernel driver
        print("🔓 Desvinculando drivers del kernel...")
        try:
            for cfg in dev:
                for intf in cfg:
                    if_num = intf.bInterfaceNumber
                    try:
                        if dev.is_kernel_driver_active(if_num):
                            dev.detach_kernel_driver(if_num)
                            print(f"  ✓ Interface {if_num} desvinculada")
                    except:
                        pass
        except:
            pass
        
        # Configurar dispositivo
        print("⚙️  Configurando dispositivo...")
        try:
            if device_handle is None:
                try:
                    dev.reset()
                    time.sleep(0.5)
                except:
                    pass
            
            dev.set_configuration()
            print("✓ Dispositivo configurado")
        except usb.core.USBError as e:
            if e.errno == 16:  # Device busy
                usb.util.dispose_resources(dev)
                time.sleep(0.5)
                dev = usb.core.find(idVendor=UareU4500.VID, idProduct=UareU4500.PID)
                dev.set_configuration()
        
        device_handle = dev
        
        # Inicializar con comandos de Wireshark
        UareU4500.initialize_device(dev)
        
        # Capturar desde endpoint 0x82
        raw_data = UareU4500.capture_fingerprint(dev)
        
        if raw_data is None:
            return jsonify({'error': 'No se pudieron leer datos del sensor'}), 500
        
        # Guardar template binario
        import os
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        template_path = os.path.join(os.path.dirname(__file__), f"template_{timestamp}.fmd")
        
        with open(template_path, 'wb') as f:
            f.write(raw_data)
        print(f"💾 Template guardado: {template_path}")
        
        # Convertir template a base64 para transmisión
        template_base64 = base64.b64encode(raw_data).decode()
        
        # Crear imagen de placeholder (para UI)
        placeholder_img = Image.new('L', (256, 360), color=128)
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(placeholder_img)
        
        # Dibujar texto
        text_lines = [
            "Huella Capturada",
            f"{len(raw_data)} bytes",
            "Template FMD",
            f"{timestamp}"
        ]
        
        y = 150
        for line in text_lines:
            # Centrar texto aproximadamente
            draw.text((50, y), line, fill=255)
            y += 30
        
        # Convertir placeholder a PNG base64
        img_byte_arr = io.BytesIO()
        placeholder_img.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        placeholder_base64 = base64.b64encode(img_byte_arr).decode()
        
        print("="*60)
        print("✅ CAPTURA EXITOSA")
        print(f"   Template: {len(raw_data)} bytes")
        print(f"   Formato: FMD (Fingerprint Minutiae Data)")
        print("="*60 + "\n")
        
        return jsonify({
            'success': True,
            'fingerprint_template': template_base64,  # Template real para backend
            'fingerprint_base64': placeholder_base64,  # Placeholder para UI
            'bytes_received': len(raw_data),
            'format': 'FMD',
            'message': 'Template de huella capturado correctamente'
        })
        
    except Exception as e:
        import traceback
        print("\n" + "="*60)
        print("❌ ERROR:")
        print(traceback.format_exc())
        print("="*60 + "\n")
        device_handle = None
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 Servidor USB Bridge - U.are.U 4500")
    print("="*60)
    print("📡 Escuchando en http://0.0.0.0:8080")
    print("🔧 Comandos: Extraídos de Wireshark")
    print("📍 Endpoint: 0x82 (corregido)")
    print("📊 Tamaño esperado: ~111KB")
    print("="*60 + "\n")
    app.run(host='0.0.0.0', port=8080, debug=True)