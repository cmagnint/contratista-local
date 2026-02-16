import 'dart:convert';
import 'package:flutter/services.dart';
import 'package:http/http.dart' as http;
import 'package:contratista/utils/globals.dart';

class FingerPrintService {
  static const platform = MethodChannel(
    'com.terrasoft.contratista/fingerprint',
  );

  final String _serverUrl = 'http://10.0.2.2:8080';
  String _mode = 'bridge';

  Future<bool> conectarDispositivo() async {
    try {
      loggerGlobal.d('=== Intentando modo nativo ===');
      final bool isConnected = await platform.invokeMethod('checkDevice');

      if (isConnected) {
        _mode = 'native';
        loggerGlobal.d('=== Modo NATIVO activado ===');
        return true;
      }
    } catch (e) {
      loggerGlobal.d('Modo nativo no disponible: $e');
    }

    try {
      loggerGlobal.d('=== Intentando modo bridge ===');

      final response = await http
          .get(Uri.parse('$_serverUrl/list-devices'))
          .timeout(Duration(seconds: 5));

      if (response.statusCode == 200) {
        final devices = jsonDecode(response.body) as List;
        loggerGlobal.d('Dispositivos encontrados: ${devices.length}');

        // Buscar Grow R102A (VID: 8210, PID: 8209)
        final device = devices.firstWhere(
          (d) => d['vid'] == 8210 && d['pid'] == 8209,
          orElse: () => null,
        );

        if (device != null) {
          _mode = 'bridge';
          loggerGlobal.d('=== Modo BRIDGE activado (Grow R102A) ===');
          loggerGlobal.d(
            'Dispositivo: VID=${device['vid']}, PID=${device['pid']}',
          );
          return true;
        }
      }

      loggerGlobal.e('Dispositivo Grow R102A no encontrado');
      return false;
    } catch (e) {
      loggerGlobal.e('Error conectando: $e');
      return false;
    }
  }

  Future<Uint8List?> capturarHuella() async {
    if (_mode == 'native') {
      return _capturarHuellaNativa();
    } else {
      return _capturarHuellaBridge();
    }
  }

  Future<Uint8List?> _capturarHuellaNativa() async {
    try {
      loggerGlobal.d('=== Captura nativa ===');

      final String base64Image = await platform.invokeMethod('scanFingerprint');
      loggerGlobal.d('Huella capturada: ${base64Image.length} chars');

      return base64Decode(base64Image);
    } on PlatformException catch (e) {
      loggerGlobal.e('Error nativo: ${e.message}');
      return null;
    } catch (e) {
      loggerGlobal.e('Error nativo: $e');
      return null;
    }
  }

  Future<Uint8List?> _capturarHuellaBridge() async {
    try {
      loggerGlobal.d('=== Captura vía bridge ===');

      final response = await http
          .post(Uri.parse('$_serverUrl/capture-fingerprint'))
          .timeout(Duration(seconds: 30));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        loggerGlobal.d('Respuesta recibida:');
        loggerGlobal.d('  - Bytes: ${data['bytes_received']}');
        loggerGlobal.d('  - Tamaño imagen: ${data['image_size']}');
        loggerGlobal.d('  - Mensaje: ${data['message']}');

        return base64Decode(data['fingerprint_base64']);
      }

      loggerGlobal.e('Error ${response.statusCode}: ${response.body}');
      return null;
    } catch (e) {
      loggerGlobal.e('Error bridge: $e');
      return null;
    }
  }

  Future<void> desconectar() async {
    loggerGlobal.d('Desconectado (modo: $_mode)');
  }
}
