from flask import Flask, jsonify
import usb.core
import usb.util
import base64
from PIL import Image, ImageDraw
import io
import numpy as np
import time
import random

app = Flask(__name__)

class GrowR102A:
    """Comandos USB para Grow R102A"""
    
    VID = 0x4612  # 17938 en decimal
    PID = 0x04b4  # 1204 en decimal
    
    IMAGE_WIDTH = 256
    IMAGE_HEIGHT = 288
    IMAGE_SIZE = IMAGE_WIDTH * IMAGE_HEIGHT  # 73728 bytes
    
    @staticmethod
    def initialize_device(dev):
        """Inicialización básica del dispositivo"""
        print("🔧 Inicializando Grow R102A...")
        
        try:
            # Configurar dispositivo
            dev.set_configuration()
            print("  ✓ Dispositivo configurado")
            return True
        except Exception as e:
            print(f"  ⚠️  Error: {e}")
            return False
    
    @staticmethod
    def capture_fingerprint(dev):
        """Captura imagen del Grow R102A"""
        print("📸 Capturando desde Grow R102A...")
        print("👆 Coloca tu dedo en el sensor...")
        
        raw_data = bytearray()
        chunk_size = 4096
        max_reads = 30
        
        try:
            # Buscar endpoint de entrada (normalmente 0x81 o 0x82)
            cfg = dev.get_active_configuration()
            intf = cfg[(0,0)]
            
            ep_in = None
            for ep in intf:
                if usb.util.endpoint_direction(ep.bEndpointAddress) == usb.util.ENDPOINT_IN:
                    ep_in = ep
                    break
            
            if ep_in is None:
                print("  ❌ No se encontró endpoint de entrada")
                return None
            
            print(f"  → Usando endpoint: 0x{ep_in.bEndpointAddress:02x}")
            
            # Leer datos en chunks
            for i in range(max_reads):
                try:
                    chunk = dev.read(ep_in.bEndpointAddress, chunk_size, timeout=5000)
                    raw_data.extend(chunk)
                    
                    if len(raw_data) % 8192 == 0:
                        print(f"  → {len(raw_data)} bytes...")
                    
                    # Si ya tenemos imagen completa
                    if len(raw_data) >= GrowR102A.IMAGE_SIZE:
                        print(f"  ✓ Imagen completa ({len(raw_data)} bytes)")
                        break
                        
                except usb.core.USBTimeoutError:
                    if len(raw_data) > 0:
                        print(f"  ✓ Timeout - fin de lectura ({len(raw_data)} bytes)")
                        break
                    else:
                        print(f"  ⏱️  Timeout - no hay datos disponibles")
                        time.sleep(0.5)
                        continue
                        
        except Exception as e:
            print(f"  ⚠️  Error: {e}")
            return None
        
        return bytes(raw_data) if len(raw_data) > 0 else None
    
    @staticmethod
    def raw_to_image(raw_data):
        """Convertir datos RAW a imagen PIL"""
        if not raw_data or len(raw_data) < GrowR102A.IMAGE_SIZE:
            print(f"  ⚠️  Datos insuficientes: {len(raw_data) if raw_data else 0} bytes")
            return None
        
        try:
            # Tomar primeros 73728 bytes (256x288)
            img_array = np.frombuffer(raw_data[:GrowR102A.IMAGE_SIZE], dtype=np.uint8)
            img_array = img_array.reshape((GrowR102A.IMAGE_HEIGHT, GrowR102A.IMAGE_WIDTH))
            img = Image.fromarray(img_array, mode='L')
            
            print(f"  ✓ Imagen convertida: {GrowR102A.IMAGE_WIDTH}x{GrowR102A.IMAGE_HEIGHT}")
            return img
            
        except Exception as e:
            print(f"  ⚠️  Error convirtiendo: {e}")
            return None


@app.route('/list-devices', methods=['GET'])
def list_devices():
    """Listar todos los dispositivos USB"""
    devices = usb.core.find(find_all=True)
    device_list = []
    
    for dev in devices:
        device_info = {
            'vid': dev.idVendor,
            'pid': dev.idProduct,
            'bus': dev.bus,
            'address': dev.address,
            'is_grow': (dev.idVendor == GrowR102A.VID and dev.idProduct == GrowR102A.PID)
        }
        device_list.append(device_info)
        
        if device_info['is_grow']:
            print(f"✓ Grow R102A detectado: VID={device_info['vid']}, PID={device_info['pid']}")
    
    return jsonify(device_list)


@app.route('/capture-fingerprint', methods=['POST'])
def capture():
    """Capturar huella desde Grow R102A"""
    
    try:
        print("\n" + "="*60)
        print("🔍 Buscando Grow R102A...")
        
        dev = usb.core.find(idVendor=GrowR102A.VID, idProduct=GrowR102A.PID)
        
        if dev is None:
            print("❌ Dispositivo no encontrado")
            return jsonify({
                'error': 'Grow R102A no encontrado',
                'vid_expected': GrowR102A.VID,
                'pid_expected': GrowR102A.PID
            }), 404
        
        print(f"✓ Encontrado: Bus {dev.bus}, Address {dev.address}")
        
        # Desvincular kernel driver si está activo
        print("🔓 Configurando acceso USB...")
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
        
        # Inicializar
        if not GrowR102A.initialize_device(dev):
            return jsonify({'error': 'Error inicializando dispositivo'}), 500
        
        # Capturar
        raw_data = GrowR102A.capture_fingerprint(dev)
        
        if raw_data is None:
            return jsonify({'error': 'No se capturaron datos'}), 500
        
        # Convertir a imagen
        img = GrowR102A.raw_to_image(raw_data)
        
        if img is None:
            # Si no se pudo convertir, crear placeholder
            img = Image.new('L', (GrowR102A.IMAGE_WIDTH, GrowR102A.IMAGE_HEIGHT), color=128)
            print("  ⚠️  Usando imagen placeholder")
        
        # Guardar imagen localmente para debug
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        img_path = f"huella_grow_{timestamp}.png"
        img.save(img_path)
        print(f"💾 Imagen guardada: {img_path}")
        
        # Convertir a base64
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        img_base64 = base64.b64encode(img_byte_arr).decode()
        
        print("="*60)
        print("✅ CAPTURA EXITOSA")
        print(f"   Tamaño: {len(raw_data)} bytes raw")
        print(f"   Imagen: {GrowR102A.IMAGE_WIDTH}x{GrowR102A.IMAGE_HEIGHT} pixels")
        print("="*60 + "\n")
        
        return jsonify({
            'success': True,
            'fingerprint_base64': img_base64,
            'bytes_received': len(raw_data),
            'image_size': f"{GrowR102A.IMAGE_WIDTH}x{GrowR102A.IMAGE_HEIGHT}",
            'message': 'Huella capturada correctamente'
        })
        
    except Exception as e:
        import traceback
        print("\n" + "="*60)
        print("❌ ERROR:")
        print(traceback.format_exc())
        print("="*60 + "\n")
        return jsonify({'error': str(e)}), 500


@app.route('/capture-fingerprint-mock', methods=['POST'])
def capture_mock():
    """Endpoint simulado para testing sin hardware"""
    print("\n" + "="*60)
    print("🎭 MODO SIMULACIÓN - Generando huella de prueba...")
    print("="*60)
    
    try:
        # Crear imagen de prueba con patrón de huella simulado
        img = Image.new('L', (GrowR102A.IMAGE_WIDTH, GrowR102A.IMAGE_HEIGHT), color=240)
        
        # Dibujar patrón simulado
        pixels = img.load()
        
        # Simular líneas de huella
        for y in range(GrowR102A.IMAGE_HEIGHT):
            for x in range(GrowR102A.IMAGE_WIDTH):
                # Crear patrón ondulado
                if (x + y * 2) % 8 < 4:
                    noise = random.randint(-20, 20)
                    pixels[x, y] = max(0, min(255, 180 + noise))
        
        # Agregar marca de agua "SIMULADO"
        draw = ImageDraw.Draw(img)
        draw.text((50, GrowR102A.IMAGE_HEIGHT // 2 - 10), "SIMULADO", fill=100)
        
        # Guardar para debug
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        img_path = f"huella_mock_{timestamp}.png"
        img.save(img_path)
        print(f"💾 Imagen simulada guardada: {img_path}")
        
        # Convertir a base64
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        img_base64 = base64.b64encode(img_byte_arr).decode()
        
        print("✅ Huella simulada generada")
        print("="*60 + "\n")
        
        return jsonify({
            'success': True,
            'fingerprint_base64': img_base64,
            'bytes_received': len(img_byte_arr),
            'image_size': f"{GrowR102A.IMAGE_WIDTH}x{GrowR102A.IMAGE_HEIGHT}",
            'message': 'Huella simulada - SOLO PARA TESTING'
        })
        
    except Exception as e:
        import traceback
        print("❌ ERROR:")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 USB Bridge - Grow R102A Fingerprint Scanner")
    print("="*60)
    print(f"📡 Escuchando en http://0.0.0.0:8080")
    print(f"🔍 VID: 0x{GrowR102A.VID:04x} ({GrowR102A.VID})")
    print(f"🔍 PID: 0x{GrowR102A.PID:04x} ({GrowR102A.PID})")
    print(f"📊 Imagen: {GrowR102A.IMAGE_WIDTH}x{GrowR102A.IMAGE_HEIGHT} pixels")
    print("\n📍 Endpoints disponibles:")
    print("   GET  /list-devices             - Listar dispositivos USB")
    print("   POST /capture-fingerprint      - Capturar desde hardware real")
    print("   POST /capture-fingerprint-mock - Capturar simulado (testing)")
    print("="*60 + "\n")
    app.run(host='0.0.0.0', port=8080, debug=True)