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

    const AndroidNotificationChannel errorChannel = AndroidNotificationChannel(
      'worker_sync_error_channel',
      'Errores de Sincronización',
      description: 'Notificaciones sobre errores en la sincronización',
      importance: Importance.high,
      playSound: true,
      showBadge: true,
      enableVibration: true,
    );

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

    const AndroidInitializationSettings initializationSettingsAndroid =
        AndroidInitializationSettings('@mipmap/ic_launcher');

    const InitializationSettings initializationSettings =
        InitializationSettings(android: initializationSettingsAndroid);

    await _notificationsPlugin.initialize(
      initializationSettings,
      onDidReceiveNotificationResponse:
          (NotificationResponse notificationResponse) {},
    );
  }

  static Future<void> scheduleSync() async {
    _syncTimer?.cancel();
    _syncTimer = Timer(const Duration(seconds: 10), () async {
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

      const validFields = {
        'holding',
        'sociedad',
        'folio',
        'fundo',
        'casa',
        'labor',
        'horario',
        'transportista',
        'rut',
        'codigo_supervisor',
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
        'area',
        'cargo',
        'charla_supervisor_id',
      };

      for (var entry in enrollment.entries) {
        if (validFields.contains(entry.key) &&
            entry.key != 'synced' &&
            entry.key != 'createdAt' &&
            entry.key != 'id') {
          fields[entry.key] = entry.value.toString();
        }
      }

      if (enrollment.containsKey('labor_id')) {
        fields['labor'] = enrollment['labor_id'].toString();
      }
      if (enrollment.containsKey('empresa_transporte_id')) {
        fields['transportista'] = enrollment['empresa_transporte_id']
            .toString();
      }

      if (enrollment.containsKey('supervisor_contratador')) {
        fields['codigo_supervisor'] = enrollment['supervisor_contratador']
            .toString();
      }

      fields['estado'] = 'true';

      if (enrollment['codigo_qr'] != null &&
          enrollment['codigo_qr'].toString().isNotEmpty) {
        fields['codigo_qr'] = enrollment['codigo_qr'].toString();
      }

      final tempDir = await getTemporaryDirectory();

      if (enrollment['carnet_front_image'] != null) {
        final frontBytes = base64Decode(enrollment['carnet_front_image']);
        final frontFile = File(
          '${tempDir.path}/carnet_front_${DateTime.now().millisecondsSinceEpoch}.png',
        );
        await frontFile.writeAsBytes(frontBytes);
        files.add(MapEntry('carnet_front_image', frontFile));
      }

      if (enrollment['carnet_back_image'] != null) {
        final backBytes = base64Decode(enrollment['carnet_back_image']);
        final backFile = File(
          '${tempDir.path}/carnet_back_${DateTime.now().millisecondsSinceEpoch}.png',
        );
        await backFile.writeAsBytes(backBytes);
        files.add(MapEntry('carnet_back_image', backFile));
      }

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

      // ✅ AGREGAR HUELLA DIGITAL
      if (enrollment['huella_digital'] != null) {
        Uint8List huellaBytes;
        if (enrollment['huella_digital'] is String) {
          huellaBytes = base64Decode(enrollment['huella_digital']);
        } else {
          huellaBytes = Uint8List.fromList(enrollment['huella_digital']);
        }

        String fileName =
            enrollment['rut'] != null && enrollment['rut'].toString().isNotEmpty
            ? 'huella_${enrollment['rut'].toString().replaceAll('.', '').replaceAll('-', '')}.png'
            : 'huella_${enrollment['dni']}.png';

        final huellaFile = await File('${tempDir.path}/$fileName').create();
        await huellaFile.writeAsBytes(huellaBytes);
        files.add(MapEntry('huella_digital', huellaFile));
        loggerGlobal.d('Huella digital agregada para sincronización');
      }

      loggerGlobal.d('=== CAMPOS QUE SE ENVÍAN ===');
      loggerGlobal.d('codigo_supervisor: ${fields['codigo_supervisor']}');
      loggerGlobal.d('horario: ${fields['horario']}');
      loggerGlobal.d('area: ${fields['area']}');
      loggerGlobal.d('cargo: ${fields['cargo']}');
      loggerGlobal.d('Todos los campos: ${fields.keys.toList()}');
      loggerGlobal.d('Total archivos: ${files.length}');

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
          ongoing: true,
          autoCancel: false,
          playSound: false,
          enableVibration: false,
          channelShowBadge: true,
          category: AndroidNotificationCategory.progress,
        );

    NotificationDetails platformChannelSpecifics = NotificationDetails(
      android: androidPlatformChannelSpecifics,
    );

    await _notificationsPlugin.show(
      1,
      'Sincronizando Trabajadores',
      'Progreso: ${progress.round()}%',
      platformChannelSpecifics,
      payload: 'sync_progress',
    );

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
      2,
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
