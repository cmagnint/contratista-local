// production_db.dart
import 'package:contratista/utils/globals.dart';
import 'package:path_provider/path_provider.dart';
import 'package:path/path.dart' as p;
import 'package:sembast/sembast_io.dart';

class ProductionDatabase {
  static final ProductionDatabase _singleton = ProductionDatabase._();
  static Database? _database;

  // Store for production records
  final StoreRef<int, Map<String, dynamic>> _productionStore =
      intMapStoreFactory.store('local_production');

  // Store for workers' accumulated totals
  final StoreRef<int, Map<String, dynamic>> _workerStore = intMapStoreFactory
      .store('workers');

  ProductionDatabase._();
  factory ProductionDatabase() => _singleton;

  Future<Database> get database async {
    if (_database != null) return _database!;
    _database = await _initDatabase();
    return _database!;
  }

  Future<Database> _initDatabase() async {
    final dir = await getApplicationDocumentsDirectory();
    final dbPath = p.join(dir.path, 'local_production.db');
    return await databaseFactoryIo.openDatabase(dbPath);
  }

  Future<List<Map<String, dynamic>>> getAllWorkers() async {
    final db = await database;
    final records = await _workerStore.find(db);
    return records.map((record) => record.value).toList();
  }

  Future<void> updateWorkerQR(int workerId, String qrCode) async {
    final db = await database;

    try {
      // First, attempt to get the existing worker record
      final workerRecord = await _workerStore.record(workerId).get(db);

      if (workerRecord != null) {
        // If the worker exists, create an updated copy of their data
        final updatedWorker = Map<String, dynamic>.from(workerRecord);
        // Update just the QR code while preserving other fields
        updatedWorker['qrCode'] = qrCode;
        // Save the updated record back to the database
        await _workerStore.record(workerId).put(db, updatedWorker);
      } else {
        // If the worker doesn't exist in our local database yet,
        // Create a minimal record with just the essential fields
        await _workerStore.record(workerId).put(db, {
          'id': workerId,
          'qrCode': qrCode,
          'pesoNeto': 0.0,
          'pesoBruto': 0.0,
          'cantidadUnidadesControl': 0,
        });
      }
    } catch (e) {
      throw Exception('Failed to update QR code for worker $workerId: $e');
    }
  }

  Future<void> updateServerTotals(
    Map<int, Map<String, dynamic>> serverTotals,
  ) async {
    final db = await database;

    try {
      // Start a transaction to ensure all updates are atomic
      await db.transaction((txn) async {
        for (var entry in serverTotals.entries) {
          final workerId = entry.key;
          final newTotals = entry.value;

          // Get the current worker record
          final existingRecord = await _workerStore.record(workerId).get(txn);

          if (existingRecord != null) {
            // If worker exists, update while preserving other fields
            final updatedWorker = Map<String, dynamic>.from(existingRecord);
            // Update the production totals
            updatedWorker['pesoNeto'] = newTotals['pesoNeto'] ?? 0.0;
            updatedWorker['pesoBruto'] = newTotals['pesoBruto'] ?? 0.0;
            updatedWorker['cantidadUnidadesControl'] =
                newTotals['cantidadUnidadesControl'] ?? 0;

            // Save the updated record
            await _workerStore.record(workerId).put(txn, updatedWorker);
          } else {
            // If worker doesn't exist, create a new record with the totals
            await _workerStore.record(workerId).put(txn, {
              'id': workerId,
              'pesoNeto': newTotals['pesoNeto'] ?? 0.0,
              'pesoBruto': newTotals['pesoBruto'] ?? 0.0,
              'cantidadUnidadesControl':
                  newTotals['cantidadUnidadesControl'] ?? 0,
              'qrCode': null, // Will be updated later if available
            });
          }
        }
      });
    } catch (e) {
      throw Exception('Failed to update server totals: $e');
    }
  }

  Future<Map<String, dynamic>?> getWorkerByQR(String qrCode) async {
    final db = await database;
    final record = await _workerStore.findFirst(
      db,
      finder: Finder(filter: Filter.equals('qrCode', qrCode)),
    );
    return record?.value;
  }

  // Save a new production record
  Future<int> saveProduction(Map<String, dynamic> productionData) async {
    final db = await database;
    final now = DateTime.now();

    // Prepare the production record
    final record = {
      ...productionData,
      'synced': false,
      'createdAt': now.toIso8601String(),
      'hora_fecha_ingreso_produccion': now.toIso8601String(),
    };

    // Save to production store
    return await _productionStore.add(db, record);
  }

  // Update worker's accumulated totals
  Future<void> updateWorkerTotals(
    int workerId,
    Map<String, dynamic> totals,
  ) async {
    final db = await database;
    loggerGlobal.d('Actualizando totales para trabajador $workerId: $totals');
    await _workerStore.record(workerId).put(db, totals);
  }

  // Get all unsynced production records
  Future<List<Map<String, dynamic>>> getUnsyncedProductions() async {
    final db = await database;
    final records = await _productionStore.find(
      db,
      finder: Finder(
        filter: Filter.equals('synced', false),
        sortOrders: [SortOrder('createdAt')],
      ),
    );

    return records
        .map((record) => {'id': record.key, ...record.value})
        .toList();
  }

  // Get worker's current totals
  Future<Map<String, dynamic>?> getWorkerTotals(int workerId) async {
    final db = await database;
    return await _workerStore.record(workerId).get(db);
  }

  // Mark a production record as synced
  Future<void> markAsSynced(int productionId) async {
    final db = await database;
    await _productionStore.record(productionId).update(db, {
      'synced': true,
      'syncedAt': DateTime.now().toIso8601String(),
    });
  }

  // Get production history for a worker
  Future<List<Map<String, dynamic>>> getWorkerProductionHistory(
    int workerId,
  ) async {
    final db = await database;
    final records = await _productionStore.find(
      db,
      finder: Finder(
        filter: Filter.equals('workerId', workerId),
        sortOrders: [SortOrder('createdAt', false)],
      ),
    );

    return records
        .map((record) => {'id': record.key, ...record.value})
        .toList();
  }

  // Get count of unsynced records
  Future<int> getUnsyncedCount() async {
    final db = await database;
    final records = await _productionStore.find(
      db,
      finder: Finder(filter: Filter.equals('synced', false)),
    );
    return records.length;
  }

  // Clean up resources
  Future<void> close() async {
    final db = await database;
    await db.close();
    _database = null;
  }
}
