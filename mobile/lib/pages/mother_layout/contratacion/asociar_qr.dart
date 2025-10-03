//asociar_qr.dart
import 'package:contratista/services/production_db.dart';
import 'package:flutter/material.dart';
import 'package:flutter_tts/flutter_tts.dart';
import 'package:http/http.dart' as http;
import 'package:mobile_scanner/mobile_scanner.dart';
import 'package:contratista/utils/globals.dart';
import 'dart:convert';
import 'package:contratista/services/contratista_api_service.dart';

class Worker {
  int id;
  String name;
  String? qrCode;
  double production;
  double cantidadUnidadControl;
  int cantidadRejillas; // Variable local

  Worker({
    required this.id,
    required this.name,
    this.qrCode,
    this.production = 0.0,
    required this.cantidadUnidadControl,
    this.cantidadRejillas = 0, // Inicializada en 0
  });

  factory Worker.fromJson(Map<String, dynamic> json) {
    return Worker(
      id: json['id'],
      name: json['nombres'],
      qrCode: json['codigo_qr'],
      production: json['production']?.toDouble() ?? 0.0,
      cantidadUnidadControl: json['cantidad_unidad_control']?.toDouble() ?? 0.0,
      // No inicializamos cantidadRejillas desde json
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'name': name,
      'qrCode': qrCode,
      'production': production,
      'cantidadUnidadControl': cantidadUnidadControl,
      'cantidadRejillas': cantidadRejillas, // Incluimos en el mapa local
    };
  }

  static Worker fromMap(Map<String, dynamic> map) {
    return Worker(
      id: map['id'] as int,
      name: map['name'] as String,
      qrCode: map['qrCode'] as String?,
      production: map['production'] as double,
      cantidadUnidadControl: map['cantidadUnidadControl'] as double,
      cantidadRejillas:
          map['cantidadRejillas'] as int, // Recuperamos del mapa local
    );
  }
}

class WorkerQRAssociationScreen extends StatefulWidget {
  const WorkerQRAssociationScreen({super.key});

  @override
  WorkerQRAssociationScreenState createState() =>
      WorkerQRAssociationScreenState();
}

class WorkerQRAssociationScreenState extends State<WorkerQRAssociationScreen> {
  // Core services and controllers
  final ProductionDatabase _productionDb = ProductionDatabase();
  final ApiService _apiService = ApiService();
  late FlutterTts flutterTts;
  MobileScannerController cameraController = MobileScannerController();

  // State variables
  String? scannedCode;
  List<Worker> workers = [];
  Worker? selectedWorker;
  int? holdingId;

  @override
  void initState() {
    super.initState();
    _initializeData();
    _initializeTts();
  }

  // Initialize text-to-speech functionality
  Future<void> _initializeTts() async {
    flutterTts = FlutterTts();
    await flutterTts.setLanguage("es-ES");
    await flutterTts.setSpeechRate(0.5);
    await flutterTts.setVolume(1.0);
    await flutterTts.setPitch(1.0);
  }

  Future<void> _speak(String text) async {
    await flutterTts.speak(text);
  }

  // Initialize basic data and load workers
  Future<void> _initializeData() async {
    await _loadHoldingId();
    await loadWorkersFromApi();
  }

  Future<void> _loadHoldingId() async {
    try {
      final holdingString = await storage.read(key: 'holding');
      if (holdingString != null) {
        holdingId = int.parse(holdingString);
        loggerGlobal.d('Holding cargado desde storage: $holdingId');
      } else {
        loggerGlobal.e('No se encontró holding en el storage');
        _showErrorMessage('Error: No se encontró información del holding');
      }
    } catch (e) {
      loggerGlobal.e('Error al cargar holding desde storage: $e');
      _showErrorMessage('Error al cargar información del holding');
    }
  }

  // Load workers from API and store in local database
  Future<void> loadWorkersFromApi() async {
    if (holdingId == null) {
      _showErrorMessage('Error: No se encontró el ID del holding');
      return;
    }

    if (!userInfo.isSupervisorOrJefe) {
      _showErrorMessage('Usuario no tiene permisos para ver trabajadores');
      return;
    }

    try {
      // Build URL based on user role
      String url = 'api_personal_asignado/?';
      if (userInfo.idJefeCuadrilla != 0) {
        url += 'jefe_cuadrilla_id=${userInfo.idJefeCuadrilla}';
      } else {
        url += 'supervisor_id=${userInfo.idSupervisor}';
      }

      final response = await _apiService.get(url);

      if (response.statusCode == 200) {
        final List<dynamic> workersJson = json.decode(response.body);

        setState(() {
          workers = workersJson.map((json) => Worker.fromJson(json)).toList();
          workers = _sortWorkers(workers);
        });

        // Store workers in local database
        for (var worker in workers) {
          await _productionDb.updateWorkerTotals(worker.id, worker.toMap());
        }

        loggerGlobal.d('Trabajadores cargados: ${workers.length}');
        _showSuccessMessage('Trabajadores cargados exitosamente');
      } else {
        throw Exception('Failed to load workers: ${response.statusCode}');
      }
    } catch (e) {
      loggerGlobal.e('Error al cargar trabajadores: $e');
      _showErrorMessage(
        'Error al cargar trabajadores. Por favor, inténtelo de nuevo.',
      );
    }
  }

  // Handle QR code association with worker
  Future<void> _associateWorkerWithQR() async {
    loggerGlobal.d('Entering _associateWorkerWithQR');
    if (selectedWorker != null && scannedCode != null) {
      try {
        final Map<String, String> data = {
          'trabajador': selectedWorker!.id.toString(),
          'codigo_qr': scannedCode!,
        };

        late final http.Response response;
        if (selectedWorker!.qrCode == null || selectedWorker!.qrCode!.isEmpty) {
          response = await _apiService.post('api_codigo_qr/', data);
        } else {
          response = await _apiService.put(
            'api_codigo_qr/${selectedWorker!.id}/',
            data,
          );
        }

        loggerGlobal.d('API Response: ${response.body}');
        if (response.statusCode == 200 || response.statusCode == 201) {
          selectedWorker!.qrCode = scannedCode;

          // Update local database with new QR code
          await _productionDb.updateWorkerQR(selectedWorker!.id, scannedCode!);

          await _updateWorkerList(selectedWorker!.id, scannedCode!);
          _showSuccessMessage('Código QR del trabajador actualizado con éxito');
          await _speak(
            "Trabajador ${selectedWorker!.name} enlazado exitosamente",
          );
        } else {
          throw Exception(
            'Error al actualizar el código QR del trabajador: ${response.statusCode}',
          );
        }
      } catch (e) {
        loggerGlobal.e('Error in _associateWorkerWithQR: $e');
        _showErrorMessage('Error: $e');
      }
    } else {
      _showErrorMessage(
        'Por favor, seleccione un trabajador y escanee un código QR',
      );
    }
  }

  // Update worker list and local database after QR association
  Future<void> _updateWorkerList(int workerId, String newQrCode) async {
    setState(() {
      int index = workers.indexWhere((w) => w.id == workerId);
      if (index != -1) {
        workers[index].qrCode = newQrCode;
        selectedWorker = workers[index];
      }
      workers = _sortWorkers(workers);
    });

    await _productionDb.updateWorkerTotals(workerId, selectedWorker!.toMap());
  }

  // Sort workers by QR code status and name
  List<Worker> _sortWorkers(List<Worker> workers) {
    List<Worker> withoutQR = [];
    List<Worker> withQR = [];

    for (var worker in workers) {
      if (worker.qrCode == null || worker.qrCode!.isEmpty) {
        withoutQR.add(worker);
      } else {
        withQR.add(worker);
      }
    }

    withoutQR.sort((a, b) => a.name.compareTo(b.name));
    withQR.sort((a, b) => a.name.compareTo(b.name));

    return [...withoutQR, ...withQR];
  }

  // Utility functions for user feedback
  void _showSuccessMessage(String message) {
    if (mounted) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text(message)));
    }
  }

  void _showErrorMessage(String message) {
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(message), backgroundColor: Colors.red),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Asociar Trabajador con QR')),
      body: Column(
        children: [
          Expanded(
            flex: 4,
            child: MobileScanner(
              controller: cameraController,
              onDetect: (capture) {
                final List<Barcode> barcodes = capture.barcodes;
                for (final barcode in barcodes) {
                  setState(() {
                    scannedCode = barcode.rawValue;
                  });
                }
              },
            ),
          ),
          Expanded(
            flex: 1,
            child: Center(
              child: Text('Código escaneado: ${scannedCode ?? "Ninguno"}'),
            ),
          ),
          Expanded(
            flex: 2,
            child: DropdownButton<Worker>(
              value: selectedWorker,
              hint: const Text('Seleccionar trabajador'),
              isExpanded: true,
              items: workers.map((Worker worker) {
                return DropdownMenuItem<Worker>(
                  value: worker,
                  child: Text(
                    worker.qrCode == null || worker.qrCode!.isEmpty
                        ? '${worker.name} (Sin código) - ${worker.cantidadUnidadControl} kg - ${worker.cantidadRejillas} rejillas'
                        : '${worker.name} (${worker.qrCode}) - ${worker.cantidadUnidadControl} kg - ${worker.cantidadRejillas} rejillas',
                    overflow: TextOverflow.ellipsis,
                  ),
                );
              }).toList(),
              onChanged: (Worker? value) {
                setState(() {
                  selectedWorker = value;
                });
              },
            ),
          ),
          Padding(
            padding: const EdgeInsets.only(bottom: 85),
            child: ElevatedButton(
              onPressed: _associateWorkerWithQR,
              child: const Text('Asociar trabajador con QR'),
            ),
          ),
        ],
      ),
    );
  }

  @override
  void dispose() {
    cameraController.dispose();
    _productionDb.close();
    flutterTts.stop();
    super.dispose();
  }
}
