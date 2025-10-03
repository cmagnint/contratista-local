// production_sync_service.dart

import 'dart:async';
import 'dart:convert';
import 'package:contratista/services/production_db.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:contratista/utils/globals.dart';
import 'package:contratista/services/contratista_api_service.dart';

/// Service responsible for synchronizing production data between local storage and server.
/// Handles automatic scheduling of syncs, notifications, and data consistency.
class ProductionSyncService {
  // Constants and static fields
  static const String LAST_SYNC_KEY = 'last_sync_time';
  static Timer? _syncTimer;
  static bool _isSyncing = false;

  // Service instances
  static final FlutterLocalNotificationsPlugin _notificationsPlugin =
      FlutterLocalNotificationsPlugin();
  static final ApiService _apiService = ApiService();
  static final ProductionDatabase _productionDb = ProductionDatabase();

  /// Initialize the sync service and set up notifications
  static Future<void> initialize() async {
    await _initializeNotifications();
  }

  /// Configure notification settings for Android
  static Future<void> _initializeNotifications() async {
    const AndroidInitializationSettings initializationSettingsAndroid =
        AndroidInitializationSettings('@mipmap/ic_launcher');
    const InitializationSettings initializationSettings =
        InitializationSettings(android: initializationSettingsAndroid);
    await _notificationsPlugin.initialize(initializationSettings);
  }

  /// Schedule a sync operation to occur after a delay
  /// Cancels any previously scheduled sync
  static Future<void> scheduleSync() async {
    _syncTimer?.cancel();
    _syncTimer = Timer(const Duration(minutes: 1), () async {
      if (!_isSyncing) {
        await _performSync();
      }
    });
  }

  /// Main synchronization process that coordinates all sync operations
  static Future<void> _performSync() async {
    if (_isSyncing) return;
    _isSyncing = true;

    try {
      await _showSyncNotification(0);

      // Step 1: Sync QR codes from server
      await _syncQRCodes();
      await _showSyncNotification(25);

      // Step 2: Upload local productions
      await _uploadProductionsToServer();
      await _showSyncNotification(50);

      // Step 3: Update totals from server
      await _syncServerTotals();
      await _showSyncNotification(75);

      await _updateLastSyncInfo();
      await _showSyncNotification(100);
    } catch (e) {
      loggerGlobal.e('Error durante la sincronización: $e');
      await _showSyncErrorNotification();
    } finally {
      _isSyncing = false;
    }
  }

  /// Synchronize QR codes from server to local database
  static Future<void> _syncQRCodes() async {
    try {
      final qrResponse = await _apiService.get('api_codigo_qr/');
      if (qrResponse.statusCode == 200) {
        final qrData = json.decode(qrResponse.body) as List<dynamic>;
        for (var qr in qrData) {
          final trabajadorId = (qr['trabajador'] as num).toInt();
          final codigoQr = qr['codigo_qr'] as String;
          await _productionDb.updateWorkerQR(trabajadorId, codigoQr);
        }
      }
    } catch (e) {
      loggerGlobal.e('Error syncing QR codes: $e');
      throw Exception('Failed to sync QR codes: $e');
    }
  }

  /// Upload local unsynced productions to the server
  static Future<void> _uploadProductionsToServer() async {
    try {
      final unsyncedProductions = await _productionDb.getUnsyncedProductions();

      for (var production in unsyncedProductions) {
        Map<String, String> data = {
          'holding': userInfo.holding,
          'trabajador': production['workerId'].toString(),
          'usuario_ingresa': production['usuario_ingresa'].toString(),
          'peso_neto': production['pesoNeto'].toString(),
          'peso_bruto': production['pesoBruto'].toString(),
          'unidad_control': production['unidadControlId'].toString(),
          'unidades_control': production['unidadesControl'].toString(),
          'hora_fecha_ingreso_produccion':
              production['hora_fecha_ingreso_produccion'],
        };

        final response = await _apiService.post('produccion-trabajador/', data);

        if (response.statusCode == 201) {
          await _productionDb.markAsSynced(production['id']);
        }
      }
    } catch (e) {
      loggerGlobal.e('Error uploading productions: $e');
      throw Exception('Failed to upload productions: $e');
    }
  }

  /// Get and update worker totals from server data
  static Future<void> _syncServerTotals() async {
    try {
      final response = await _apiService.get(
        'produccion-trabajador/?holding=${userInfo.holding}',
      );

      if (response.statusCode == 200) {
        final serverProductions = json.decode(response.body) as List<dynamic>;
        Map<int, Map<String, dynamic>> serverTotals = {};

        // Calculate totals from server data
        for (var prod in serverProductions) {
          final workerId = (prod['trabajador'] as num).toInt();
          if (!serverTotals.containsKey(workerId)) {
            serverTotals[workerId] = {
              'pesoNeto': 0.0,
              'pesoBruto': 0.0,
              'cantidadUnidadesControl': 0,
            };
          }

          serverTotals[workerId]!['pesoNeto'] +=
              (prod['peso_neto'] as num?)?.toDouble() ?? 0.0;
          serverTotals[workerId]!['pesoBruto'] +=
              (prod['peso_bruto'] as num?)?.toDouble() ?? 0.0;
          serverTotals[workerId]!['cantidadUnidadesControl'] +=
              (prod['unidades_control'] as num?)?.toInt() ?? 0;
        }

        // Update local database with server totals
        await _productionDb.updateServerTotals(serverTotals);
      }
    } catch (e) {
      loggerGlobal.e('Error syncing server totals: $e');
      throw Exception('Failed to sync server totals: $e');
    }
  }

  /// Show a progress notification during synchronization
  static Future<void> _showSyncNotification(double progress) async {
    AndroidNotificationDetails androidPlatformChannelSpecifics =
        AndroidNotificationDetails(
          'sync_channel',
          'Synchronization',
          channelDescription: 'Notifications for data synchronization',
          importance: Importance.low,
          priority: Priority.low,
          showProgress: true,
          maxProgress: 100,
          progress: progress.round(),
        );
    NotificationDetails platformChannelSpecifics = NotificationDetails(
      android: androidPlatformChannelSpecifics,
    );
    await _notificationsPlugin.show(
      0,
      'Sincronizando datos',
      'Progreso: ${progress.round()}%',
      platformChannelSpecifics,
    );
  }

  /// Show an error notification when synchronization fails
  static Future<void> _showSyncErrorNotification() async {
    AndroidNotificationDetails androidPlatformChannelSpecifics =
        const AndroidNotificationDetails(
          'sync_error_channel',
          'Synchronization Errors',
          channelDescription: 'Notifications for synchronization errors',
          importance: Importance.high,
          priority: Priority.high,
        );
    NotificationDetails platformChannelSpecifics = NotificationDetails(
      android: androidPlatformChannelSpecifics,
    );
    await _notificationsPlugin.show(
      1,
      'Error de sincronización',
      'No se pudieron sincronizar los datos. Intente nuevamente más tarde.',
      platformChannelSpecifics,
    );
  }

  /// Update the timestamp of the last successful sync
  static Future<void> _updateLastSyncInfo() async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    await prefs.setInt(LAST_SYNC_KEY, DateTime.now().millisecondsSinceEpoch);
  }
}
