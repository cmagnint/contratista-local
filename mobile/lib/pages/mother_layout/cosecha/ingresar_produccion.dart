//ingresar_producion.dart; Contratista
import 'dart:convert';
import 'package:contratista/services/prod_sinc_service.dart';
import 'package:contratista/services/production_db.dart';
import 'package:flutter/material.dart';
import 'package:mobile_scanner/mobile_scanner.dart';
import 'package:flutter_tts/flutter_tts.dart';
import 'package:contratista/utils/globals.dart';
import 'package:contratista/services/contratista_api_service.dart';

class Worker {
  int id;
  String name;
  String? qrCode;
  double pesoNeto;
  double pesoBruto;
  int cantidadUnidadesControl;

  Worker({
    required this.id,
    required this.name,
    this.qrCode,
    this.pesoNeto = 0.0,
    this.pesoBruto = 0.0,
    this.cantidadUnidadesControl = 0,
  });

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'name': name,
      'qrCode': qrCode,
      'pesoNeto': pesoNeto,
      'pesoBruto': pesoBruto,
      'cantidadUnidadesControl': cantidadUnidadesControl,
    };
  }

  static Worker fromMap(Map<String, dynamic> map) {
    try {
      return Worker(
        id: map['id'] as int,
        name: map['name'] as String,
        qrCode: map['qrCode'] as String?,
        pesoNeto: (map['pesoNeto'] as num?)?.toDouble() ?? 0.0,
        pesoBruto: (map['pesoBruto'] as num?)?.toDouble() ?? 0.0,
        cantidadUnidadesControl:
            (map['cantidadUnidadesControl'] as num?)?.toInt() ?? 0,
      );
    } catch (e) {
      loggerGlobal.e('Error en fromMap: $e\nDatos recibidos: $map');
      rethrow;
    }
  }
}

class WorkerProductionScreen extends StatefulWidget {
  const WorkerProductionScreen({super.key});

  @override
  WorkerProductionScreenState createState() => WorkerProductionScreenState();
}

class WorkerProductionScreenState extends State<WorkerProductionScreen> {
  final ProductionDatabase _productionDb = ProductionDatabase();

  final FlutterTts flutterTts = FlutterTts();
  // Add controllers for the input fields
  final TextEditingController _cantidadController = TextEditingController();
  final TextEditingController _pesoBalanzaController = TextEditingController();

  // Add state variables for unit control
  List<Map<String, dynamic>> unidadesControl = [];
  Map<String, dynamic>? unidadControlSeleccionada;

  MobileScannerController cameraController = MobileScannerController();
  bool isScanning = false;
  bool isEnteringProduction = false;
  List<Worker> workers = [];
  Worker? selectedWorker;
  ApiService apiService = ApiService();

  @override
  void initState() {
    super.initState();
    _openDatabase();
    _initializeTts();
    _loadUnidadesControl();
  }

  Future<void> _loadUnidadesControl() async {
    try {
      final response = await apiService.get(
        'unidad_control_comercial/?holding=${userInfo.holding}',
      );

      if (response.statusCode == 200) {
        setState(() {
          unidadesControl = List<Map<String, dynamic>>.from(
            json.decode(response.body),
          );
        });
      } else {
        _showErrorMessage('Error al cargar unidades de control');
      }
    } catch (e) {
      _showErrorMessage('Error al cargar unidades de control: $e');
    }
  }

  Future<void> _sincronizeData() async {
    try {
      _showLoadingDialog('Sincronizando datos...');

      // 1. Actualizar códigos QR
      final qrResponse = await apiService.get('api_codigo_qr/');
      if (qrResponse.statusCode == 200) {
        final qrData = json.decode(qrResponse.body) as List<dynamic>;

        for (var qr in qrData) {
          final trabajadorId = (qr['trabajador'] as num).toInt();
          final codigoQr = qr['codigo_qr'] as String;

          // Usar el nuevo método para actualizar QR
          await _productionDb.updateWorkerQR(trabajadorId, codigoQr);
        }
      }

      // 2. Sincronizar producciones con el servidor
      final produccionResponse = await apiService.get(
        'produccion-trabajador/?holding=${userInfo.holding}',
      );

      if (produccionResponse.statusCode == 200) {
        final serverProductions =
            json.decode(produccionResponse.body) as List<dynamic>;

        // 3. Procesar producciones del servidor
        Map<int, Map<String, dynamic>> serverTotals = {};
        for (var prod in serverProductions) {
          final workerId = (prod['trabajador'] as num).toInt();
          if (!serverTotals.containsKey(workerId)) {
            serverTotals[workerId] = {
              'pesoNeto': 0.0,
              'pesoBruto': 0.0,
              'cantidadUnidadesControl': 0,
            };
          }

          final pesoNeto = prod['peso_neto'] != null
              ? (prod['peso_neto'] as num).toDouble()
              : 0.0;
          final pesoBruto = prod['peso_bruto'] != null
              ? (prod['peso_bruto'] as num).toDouble()
              : 0.0;
          final unidades = prod['unidades_control'] != null
              ? (prod['unidades_control'] as num).toInt()
              : 0;

          serverTotals[workerId]!['pesoNeto'] += pesoNeto;
          serverTotals[workerId]!['pesoBruto'] += pesoBruto;
          serverTotals[workerId]!['cantidadUnidadesControl'] += unidades;
        }

        // 4. Actualizar totales locales usando el nuevo método
        await _productionDb.updateServerTotals(serverTotals);

        // 5. Sincronizar producciones locales no enviadas
        final unsyncedProductions = await _productionDb
            .getUnsyncedProductions();
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

          final response = await apiService.post(
            'produccion-trabajador/',
            data,
          );
          if (response.statusCode == 201) {
            await _productionDb.markAsSynced(production['id']);
          }
        }

        await _loadWorkers(); // Recargar la lista de trabajadores
        _showSuccessMessage('Sincronización completada exitosamente');
        await _speak('Datos sincronizados correctamente');
      }
    } catch (e) {
      loggerGlobal.e('Error durante la sincronización: $e');
      _showErrorMessage('Error durante la sincronización: $e');
    } finally {
      _hideLoadingDialog();
    }
  }

  // Widget para mostrar el diálogo de carga
  void _showLoadingDialog(String message) {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (BuildContext context) {
        return AlertDialog(
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const CircularProgressIndicator(),
              const SizedBox(height: 20),
              Text(message),
            ],
          ),
        );
      },
    );
  }

  void _hideLoadingDialog() {
    if (context.mounted) {
      Navigator.of(context).pop();
    }
  }

  Future<void> _openDatabase() async {
    await _loadWorkers();
  }

  Future<void> _loadWorkers() async {
    loggerGlobal.d('Cargando trabajadores');
    try {
      final records = await _productionDb.getAllWorkers();
      loggerGlobal.d(
        'Registros obtenidos de la base de datos: $records',
      ); // Log raw records

      setState(() {
        workers = records.map((record) {
          loggerGlobal.d(
            'Procesando registro: $record',
          ); // Log each record being processed
          try {
            return Worker.fromMap(record);
          } catch (e) {
            loggerGlobal.e(
              'Error convirtiendo registro a Worker: $e',
            ); // Log any conversion errors
            rethrow;
          }
        }).toList();
      });
      loggerGlobal.d('Trabajadores cargados: ${workers.length}');
    } catch (e) {
      loggerGlobal.e('Error cargando trabajadores: $e');
    }
  }

  Future<void> _initializeTts() async {
    await flutterTts.setLanguage("es-ES");
    await flutterTts.setSpeechRate(0.5);
    await flutterTts.setVolume(1.0);
    await flutterTts.setPitch(1.0);
  }

  Future<void> _speak(String text) async {
    await flutterTts.speak(text);
  }

  void _startScanning(bool isEnteringProduction) {
    setState(() {
      this.isEnteringProduction = isEnteringProduction;
      isScanning = true;
    });
  }

  void _stopScanning() {
    setState(() {
      isScanning = false;
    });
  }

  Future<void> _handleScannedCode(String? scannedCode) async {
    if (scannedCode != null) {
      final workerData = await _productionDb.getWorkerByQR(scannedCode);
      if (workerData != null) {
        final worker = Worker.fromMap(workerData);
        if (isEnteringProduction) {
          _showProductionDialog(worker);
        } else {
          await _queryProduction(worker);
        }
      } else {
        _showErrorMessage('Trabajador no encontrado');
      }
    }
    _stopScanning();
  }

  void _showProductionDialog(Worker worker) {
    _cantidadController.clear();
    _pesoBalanzaController.clear();

    // Check if unit control requires weight input
    bool requiresWeight = unidadControlSeleccionada!['cantidad'] > 0;
    String unidadControlNombre = unidadControlSeleccionada!['nombre'];

    showDialog(
      context: context,
      builder: (context) => StatefulBuilder(
        builder: (context, setState) {
          // Calculate production based on input values
          double calculateProduction() {
            int cantidad = int.tryParse(_cantidadController.text) ?? 0;
            double pesoBalanza =
                double.tryParse(_pesoBalanzaController.text) ?? 0;

            if (requiresWeight) {
              return pesoBalanza -
                  (cantidad * unidadControlSeleccionada!['cantidad']);
            } else {
              return cantidad.toDouble();
            }
          }

          return AlertDialog(
            title: Text('Ingresar Producción para ${worker.name}'),
            content: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  'Unidad de Control: $unidadControlNombre',
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 16),
                TextField(
                  controller: _cantidadController,
                  keyboardType: TextInputType.number,
                  decoration: InputDecoration(
                    labelText: 'Número de $unidadControlNombre',
                  ),
                  onChanged: (_) => setState(() {}),
                ),
                if (requiresWeight) ...[
                  const SizedBox(height: 16),
                  TextField(
                    controller: _pesoBalanzaController,
                    keyboardType: TextInputType.number,
                    decoration: const InputDecoration(
                      labelText: 'Peso en balanza (kg)',
                    ),
                    onChanged: (_) => setState(() {}),
                  ),
                  const SizedBox(height: 16),
                  Text(
                    'Producción neta: ${calculateProduction()} kg',
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                ],
              ],
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.of(context).pop(),
                child: const Text('Cancelar'),
              ),
              TextButton(
                onPressed: () {
                  // Get cantidad (units) and validate
                  int cantidad = int.tryParse(_cantidadController.text) ?? 0;
                  if (cantidad <= 0) {
                    _showErrorMessage('Ingrese una cantidad válida');
                    return;
                  }

                  // Handle peso balanza (weight) differently based on whether it's required
                  double? pesoBalanza;
                  if (requiresWeight) {
                    // Only parse peso balanza if weight is required
                    pesoBalanza = double.tryParse(_pesoBalanzaController.text);
                    if (pesoBalanza == null || pesoBalanza <= 0) {
                      _showErrorMessage('Ingrese un peso válido');
                      return;
                    }
                  }

                  // Now we can safely pass pesoBalanza which will be:
                  // - A valid double if weight is required
                  // - null if weight is not required
                  _saveProduction(worker, cantidad, pesoBalanza!);
                  Navigator.of(context).pop();
                },
                child: const Text('Guardar'),
              ),
            ],
          );
        },
      ),
    );
  }

  double _calcularProduccion(
    int rejillas,
    double pesoBalanza,
    int cantidadUnidadesControl,
  ) {
    return pesoBalanza - (rejillas * cantidadUnidadesControl);
  }

  Future<void> _saveProduction(
    Worker worker,
    int cantidadUnidadesControl,
    double pesoBalanza,
  ) async {
    double pesoNeto = _calcularProduccion(
      cantidadUnidadesControl,
      pesoBalanza,
      unidadControlSeleccionada!['cantidad'],
    );

    if (pesoNeto > 0) {
      // Save production record
      await _productionDb.saveProduction({
        'workerId': worker.id,
        'holding': userInfo.holding,
        'usuario_ingresa': userInfo.idUsuario,
        'pesoNeto': pesoNeto,
        'pesoBruto': pesoBalanza,
        'unidadControlId': unidadControlSeleccionada!['id'],
        'unidadesControl': cantidadUnidadesControl,
      });

      // Update worker totals
      Map<String, dynamic> newTotals = {
        'id': worker.id,
        'name': worker.name,
        'qrCode': worker.qrCode,
        'pesoNeto': worker.pesoNeto + pesoNeto,
        'pesoBruto': worker.pesoBruto + pesoBalanza,
        'cantidadUnidadesControl':
            worker.cantidadUnidadesControl + cantidadUnidadesControl,
      };
      await _productionDb.updateWorkerTotals(worker.id, newTotals);

      // Schedule synchronization
      ProductionSyncService.scheduleSync();

      // Show success message
      _showSuccessMessage('Producción guardada exitosamente');
      String message =
          "Se ingresaron $cantidadUnidadesControl unidades con $pesoNeto kilos netos";
      await _speak(message);
      await _loadWorkers();

      // Automatically restart scanning mode after successful save
      if (mounted) {
        Future.delayed(const Duration(milliseconds: 500), () {
          _startScanning(true);
        });
      }
    } else {
      _showErrorMessage('La producción calculada debe ser mayor a 0');
    }
  }

  Future<void> _queryProduction(Worker worker) async {
    final productions = await _productionDb.getWorkerProductionHistory(
      worker.id,
    );

    double totalPesoNeto = 0.0;
    int totalUnidades = 0;

    for (var production in productions) {
      totalPesoNeto += production['pesoNeto'] as double;
      totalUnidades += production['unidadesControl'] as int;
    }

    String message =
        "El trabajador ${worker.name} ha producido un total de $totalPesoNeto kilos netos y ha entregado $totalUnidades unidades";
    await _speak(message);
    _showSuccessMessage(message);
  }

  void _showSuccessMessage(String message) {
    ScaffoldMessenger.of(
      context,
    ).showSnackBar(SnackBar(content: Text(message)));
  }

  void _showErrorMessage(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), backgroundColor: Colors.red),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Producción de Trabajadores'),
        // Agregar botón de cerrar scanner en el AppBar como alternativa
        actions: isScanning
            ? [
                IconButton(
                  onPressed: _stopScanning,
                  icon: const Icon(Icons.close),
                  tooltip: 'Cerrar Scanner',
                ),
              ]
            : null,
      ),
      body: Center(
        child: isScanning
            ? Stack(
                children: [
                  // Scanner
                  MobileScanner(
                    controller: cameraController,
                    onDetect: (capture) {
                      final List<Barcode> barcodes = capture.barcodes;
                      for (final barcode in barcodes) {
                        _handleScannedCode(barcode.rawValue);
                      }
                    },
                  ),
                  // Overlay con instrucciones y botón de cerrar
                  Positioned(
                    top: 20,
                    left: 20,
                    right: 20,
                    child: Container(
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: Colors.black54,
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(
                        isEnteringProduction
                            ? 'Escanea el código QR del trabajador para ingresar producción'
                            : 'Escanea el código QR del trabajador para consultar producción',
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 16,
                        ),
                        textAlign: TextAlign.center,
                      ),
                    ),
                  ),
                ],
              )
            : SingleChildScrollView(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    // Unit Control Selection
                    Padding(
                      padding: const EdgeInsets.all(8.0),
                      child: DropdownButton<Map<String, dynamic>>(
                        value: unidadControlSeleccionada,
                        hint: const Text('Seleccionar Unidad de Control'),
                        isExpanded: true,
                        items: unidadesControl.map((unidad) {
                          return DropdownMenuItem<Map<String, dynamic>>(
                            value: unidad,
                            child: Text(
                              '${unidad['nombre']} (${unidad['cantidad']} kg)',
                            ),
                          );
                        }).toList(),
                        onChanged: (Map<String, dynamic>? value) {
                          setState(() {
                            unidadControlSeleccionada = value;
                          });
                        },
                      ),
                    ),

                    const SizedBox(height: 20),

                    // Action Buttons
                    ElevatedButton(
                      onPressed: unidadControlSeleccionada != null
                          ? () => _startScanning(true)
                          : null,
                      child: const Text('Ingresar Producción'),
                    ),
                    const SizedBox(height: 20),
                    ElevatedButton(
                      onPressed: () => _startScanning(false),
                      child: const Text('Consultar Producción'),
                    ),
                    const SizedBox(height: 20),
                    ElevatedButton(
                      onPressed: _sincronizeData,
                      child: const Text('Sincronizar data con la nube'),
                    ),
                  ],
                ),
              ),
      ),
      // Botón flotante para cerrar el scanner
      floatingActionButton: isScanning
          ? FloatingActionButton(
              onPressed: _stopScanning,
              backgroundColor: Colors.red,
              tooltip: 'Cerrar Scanner',
              child: const Icon(Icons.close, color: Colors.white),
            )
          : null,
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
