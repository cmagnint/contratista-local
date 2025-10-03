//enrollment_db.dart; Contratista
import 'dart:convert';
import 'package:path_provider/path_provider.dart';
import 'package:path/path.dart' as p;
import 'package:sembast/sembast_io.dart';
import 'dart:io';

class EnrollmentDatabase {
  static final EnrollmentDatabase _singleton = EnrollmentDatabase._();
  static Database? _database;

  // Un solo store para los enrollments
  final StoreRef<int, Map<String, dynamic>> _enrollmentStore =
      intMapStoreFactory.store('local_enrollments');

  EnrollmentDatabase._();
  factory EnrollmentDatabase() => _singleton;

  Future<Database> get database async {
    if (_database != null) return _database!;
    _database = await _initDatabase();
    return _database!;
  }

  Future<Database> _initDatabase() async {
    final dir = await getApplicationDocumentsDirectory();
    final dbPath = p.join(dir.path, 'local_enrollment.db');
    return await databaseFactoryIo.openDatabase(dbPath);
  }

  Future<int> saveEnrollment(
      Map<String, String> fields, List<MapEntry<String, File>> files) async {
    final db = await database;

    // Convertir los archivos a base64 para almacenamiento local
    Map<String, String> fileData = {};
    for (var file in files) {
      final bytes = await file.value.readAsBytes();
      fileData[file.key] = base64Encode(bytes);
    }

    // Combinar fields y fileData en un solo mapa
    final enrollmentData = {
      ...fields,
      ...fileData,
      'synced': false,
      'createdAt': DateTime.now().toIso8601String(),
    };

    return await _enrollmentStore.add(db, enrollmentData);
  }

  Future<List<Map<String, dynamic>>> getUnsyncedEnrollments() async {
    final db = await database;
    final records = await _enrollmentStore.find(db,
        finder: Finder(
          filter: Filter.equals('synced', false),
          sortOrders: [SortOrder('createdAt')],
        ));

    return records
        .map((record) => {
              'id': record.key,
              ...record.value,
            })
        .toList();
  }

  Future<void> markAsSynced(int id) async {
    final db = await database;
    await _enrollmentStore.record(id).update(db, {
      'synced': true,
      'syncDate': DateTime.now().toIso8601String(),
    });
  }

  Future<void> deleteEnrollment(int id) async {
    final db = await database;
    await _enrollmentStore.record(id).delete(db);
  }

  Future<int> getUnsyncedCount() async {
    final db = await database;
    final records = await _enrollmentStore.find(db,
        finder: Finder(filter: Filter.equals('synced', false)));
    return records.length;
  }

  Future<void> close() async {
    final db = await database;
    await db.close();
    _database = null;
  }
}
