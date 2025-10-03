//worker_sinc_service.dart; Contratista
import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'dart:typed_data';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:contratista/services/contratista_api_service.dart';
import 'package:contratista/utils/globals.dart';
import 'package:contratista/pages/mother_layout/contratacion/enrollment_db.dart';
import 'package:path_provider/path_provider.dart';

class WorkerSyncService {
  // ignore: constant_identifier_names
  static const String LAST_SYNC_KEY = 'last_worker_sync_time';
  static Timer? _syncTimer;
  static bool _isSyncing = false;
  static final FlutterLocalNotificationsPlugin _notificationsPlugin =
      FlutterLocalNotificationsPlugin();
  static final ApiService _apiService = ApiService();
  static final EnrollmentDatabase _enrollmentDb = EnrollmentDatabase();

  static Future<void> initialize() async {
    await _initializeNotifications();
  }

  static Future<void> _initializeNotifications() async {
    // Configurar canal para sincronización
    const AndroidNotificationChannel syncChannel = AndroidNotificationChannel(
      'worker_sync_channel',
      'Sincronización de Trabajadores',
      description:
          'Notificaciones sobre la sincronización de datos de trabajadores',
      importance: Importance.high,
      playSound: true,
      showBadge: true,
      enableVibration: true,
    );

    // Configurar canal para errores
    const AndroidNotificationChannel errorChannel = AndroidNotificationChannel(
      'worker_sync_error_channel',
      'Errores de Sincronización',
      description: 'Notificaciones sobre errores en la sincronización',
      importance: Importance.high,
      playSound: true,
      showBadge: true,
      enableVibration: true,
    );

    // Crear los canales
    await _notificationsPlugin
        .resolvePlatformSpecificImplementation<
          AndroidFlutterLocalNotificationsPlugin
        >()
        ?.createNotificationChannel(syncChannel);

    await _notificationsPlugin
        .resolvePlatformSpecificImplementation<
          AndroidFlutterLocalNotificationsPlugin
        >()
        ?.createNotificationChannel(errorChannel);

    // Configurar inicialización
    const AndroidInitializationSettings initializationSettingsAndroid =
        AndroidInitializationSettings('@mipmap/ic_launcher');

    const InitializationSettings initializationSettings =
        InitializationSettings(android: initializationSettingsAndroid);

    await _notificationsPlugin.initialize(
      initializationSettings,
      onDidReceiveNotificationResponse:
          (NotificationResponse notificationResponse) {
            // Manejar tap en la notificación si es necesario
          },
    );
  }

  static Future<void> scheduleSync() async {
    _syncTimer?.cancel();
    _syncTimer = Timer(const Duration(minutes: 1), () async {
      if (!_isSyncing) {
        await _performSync();
      }
    });
  }

  static Future<void> _performSync() async {
    if (_isSyncing) return;
    _isSyncing = true;

    try {
      await _showSyncNotification(0);

      // Obtener inscripciones no sincronizadas
      final unsyncedEnrollments = await _enrollmentDb.getUnsyncedEnrollments();

      if (unsyncedEnrollments.isEmpty) {
        _isSyncing = false;
        return;
      }

      int totalToSync = unsyncedEnrollments.length;
      int syncedCount = 0;

      for (var enrollment in unsyncedEnrollments) {
        try {
          await _uploadEnrollment(enrollment);
          syncedCount++;
          await _showSyncNotification((syncedCount / totalToSync) * 100);
        } catch (e) {
          loggerGlobal.e('Error sincronizando inscripción: $e');
          continue;
        }
      }

      await _updateLastSyncInfo();
      await _showSyncNotification(100);
    } catch (e) {
      loggerGlobal.e('Error durante la sincronización: $e');
      await _showSyncErrorNotification();
    } finally {
      _isSyncing = false;
    }
  }

  static Future<void> _uploadEnrollment(Map<String, dynamic> enrollment) async {
    try {
      Map<String, String> fields = {};
      List<MapEntry<String, File>> files = [];

      // Lista de campos válidos que acepta el serializer
      const validFields = {
        'holding',
        'sociedad',
        'folio',
        'fundo',
        'casa',
        'rut',
        'dni',
        'nic',
        'apellidos',
        'nombres',
        'nacionalidad',
        'sexo',
        'estado_civil',
        'telefono',
        'correo',
        'direccion',
        'fecha_nacimiento',
        'metodo_pago',
        'banco',
        'tipo_cuenta_bancaria',
        'numero_cuenta',
        'estado',
      };

      // Procesar solo los campos válidos
      for (var entry in enrollment.entries) {
        if (validFields.contains(entry.key) &&
            entry.key != 'synced' &&
            entry.key != 'createdAt' &&
            entry.key != 'id') {
          fields[entry.key] = entry.value.toString();
        }
      }

      // Corregir el campo supervisor si existe
      if (enrollment.containsKey('supervisor_contratador')) {
        fields['codigo_supervisor'] = enrollment['supervisor_contratador']
            .toString();
      }

      // Asegurar que estado esté presente
      fields['estado'] = 'true';

      // Solo agregar codigo_qr si existe y no está vacío
      if (enrollment['codigo_qr'] != null &&
          enrollment['codigo_qr'].toString().isNotEmpty) {
        fields['codigo_qr'] = enrollment['codigo_qr'].toString();
      }

      // Procesar los archivos
      final tempDir = await getTemporaryDirectory();

      // Procesar la foto frontal del carnet
      if (enrollment['carnet_front_image'] != null) {
        final frontBytes = base64Decode(enrollment['carnet_front_image']);
        final frontFile = File(
          '${tempDir.path}/carnet_front_${DateTime.now().millisecondsSinceEpoch}.png',
        );
        await frontFile.writeAsBytes(frontBytes);
        files.add(MapEntry('carnet_front_image', frontFile));
      }

      // Procesar la foto trasera del carnet
      if (enrollment['carnet_back_image'] != null) {
        final backBytes = base64Decode(enrollment['carnet_back_image']);
        final backFile = File(
          '${tempDir.path}/carnet_back_${DateTime.now().millisecondsSinceEpoch}.png',
        );
        await backFile.writeAsBytes(backBytes);
        files.add(MapEntry('carnet_back_image', backFile));
      }

      // Procesar la firma
      if (enrollment['firma'] != null) {
        Uint8List signatureBytes;
        if (enrollment['firma'] is String) {
          signatureBytes = base64Decode(enrollment['firma']);
        } else {
          signatureBytes = Uint8List.fromList(enrollment['firma']);
        }

        String fileName =
            enrollment['rut'] != null && enrollment['rut'].toString().isNotEmpty
            ? 'firma_${enrollment['rut'].toString().replaceAll('.', '').replaceAll('-', '')}.png'
            : 'firma_${enrollment['dni']}.png';

        final signatureFile = await File('${tempDir.path}/$fileName').create();
        await signatureFile.writeAsBytes(signatureBytes);
        files.add(MapEntry('firma', signatureFile));
      }

      // Debug: Mostrar campos que se enviarán
      loggerGlobal.d(
        'Campos que se enviarán al servidor: ${fields.keys.toList()}',
      );

      // Enviar al servidor
      final response = await _apiService.postMultipart(
        'personal_trabajadores_mobile/',
        fields,
        files,
      );

      if (response.statusCode == 201 || response.statusCode == 200) {
        await _enrollmentDb.markAsSynced(enrollment['id']);
      } else {
        throw Exception(
          'Error en la respuesta del servidor: ${response.statusCode} - ${response.body}',
        );
      }

      // Limpiar archivos temporales
      for (var file in files) {
        if (await file.value.exists()) {
          await file.value.delete();
        }
      }
    } catch (e) {
      loggerGlobal.e('Error al procesar inscripción: $e');
      rethrow;
    }
  }

  static Future<void> _showSyncNotification(double progress) async {
    AndroidNotificationDetails androidPlatformChannelSpecifics =
        AndroidNotificationDetails(
          'worker_sync_channel',
          'Sincronización de Trabajadores',
          channelDescription:
              'Notificaciones sobre la sincronización de datos de trabajadores',
          importance: Importance.high,
          priority: Priority.high,
          showProgress: true,
          maxProgress: 100,
          progress: progress.round(),
          ongoing: true, // Mantiene la notificación visible
          autoCancel: false, // No se puede descartar
          playSound: false, // Sin sonido para actualizaciones de progreso
          enableVibration: false,
          channelShowBadge: true,
          category: AndroidNotificationCategory.progress,
        );

    NotificationDetails platformChannelSpecifics = NotificationDetails(
      android: androidPlatformChannelSpecifics,
    );

    await _notificationsPlugin.show(
      1, // ID único para la notificación de sincronización
      'Sincronizando Trabajadores',
      'Progreso: ${progress.round()}%',
      platformChannelSpecifics,
      payload: 'sync_progress',
    );

    // Si llegamos al 100%, mostrar notificación final y permitir descartarla
    if (progress >= 100) {
      await Future.delayed(const Duration(seconds: 1));
      androidPlatformChannelSpecifics = const AndroidNotificationDetails(
        'worker_sync_channel',
        'Sincronización de Trabajadores',
        channelDescription:
            'Notificaciones sobre la sincronización de datos de trabajadores',
        importance: Importance.high,
        priority: Priority.high,
        ongoing: false,
        autoCancel: true,
        playSound: true,
        enableVibration: true,
      );

      platformChannelSpecifics = NotificationDetails(
        android: androidPlatformChannelSpecifics,
      );

      await _notificationsPlugin.show(
        1,
        'Sincronización Completada',
        'Todos los trabajadores han sido sincronizados',
        platformChannelSpecifics,
        payload: 'sync_complete',
      );
    }
  }

  static Future<void> _showSyncErrorNotification() async {
    AndroidNotificationDetails androidPlatformChannelSpecifics =
        const AndroidNotificationDetails(
          'worker_sync_error_channel',
          'Errores de Sincronización',
          channelDescription:
              'Notificaciones sobre errores en la sincronización',
          importance: Importance.high,
          priority: Priority.high,
          playSound: true,
          enableVibration: true,
          channelShowBadge: true,
        );

    NotificationDetails platformChannelSpecifics = NotificationDetails(
      android: androidPlatformChannelSpecifics,
    );

    await _notificationsPlugin.show(
      2, // ID único para notificaciones de error
      'Error de Sincronización',
      'No se pudieron sincronizar todos los trabajadores. Se reintentará más tarde.',
      platformChannelSpecifics,
      payload: 'sync_error',
    );
  }

  static Future<void> _updateLastSyncInfo() async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    await prefs.setInt(LAST_SYNC_KEY, DateTime.now().millisecondsSinceEpoch);
  }
}
