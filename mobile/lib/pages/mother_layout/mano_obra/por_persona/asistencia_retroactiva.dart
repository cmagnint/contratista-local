import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:logger/logger.dart';
import 'package:contratista/utils/globals.dart';
import 'package:lottie/lottie.dart';
import 'package:contratista/services/contratista_api_service.dart';
import 'package:intl/intl.dart';

class AsistenciaRetroactiva extends StatefulWidget {
  final List<dynamic> workerNames;
  final Map<String, int> workerRuts;
  final Map<String, double> workerHours;
  final Map<String, int> workerIds;
  final DateTime fecha;

  const AsistenciaRetroactiva({
    super.key,
    required this.workerNames,
    required this.workerRuts,
    required this.workerHours,
    required this.workerIds,
    required this.fecha,
  });

  @override
  AsistenciaRetroactivaState createState() => AsistenciaRetroactivaState();
}

class AsistenciaRetroactivaState extends State<AsistenciaRetroactiva> {
  ApiService apiService = ApiService();
  List<dynamic> workerNames = [];
  Map<String, int> workerRuts = {};
  Map<String, double> workerHours = {};
  Map<String, int> workerIds = {};
  Map<String, String> workerCategories = {};
  Map<String, double> workerMaxHours = {};
  late String fechaDisplay;
  late String fechaStr;
  final List<String> categories = ['A', 'F', 'PN', 'PR'];
  Logger logger = Logger();

  @override
  void initState() {
    super.initState();
    workerNames = widget.workerNames;
    workerRuts = widget.workerRuts;
    workerHours = widget.workerHours;
    workerIds = widget.workerIds;
    workerMaxHours = Map.from(workerHours);
    fechaDisplay = DateFormat('dd-MM-yyyy').format(widget.fecha);
    fechaStr = DateFormat('yyyy-MM-dd').format(widget.fecha);
  }

  double convertToDecimal(int hours, int minutes) => hours + (minutes / 60);

  Map<String, int> convertFromDecimal(double decimal) {
    int hours = decimal.floor();
    int minutes = ((decimal - hours) * 60).round();
    return {'hours': hours, 'minutes': minutes};
  }

  void updateHours(String workerName) {
    double maxHoursPerDay = workerMaxHours[workerName] ?? 0;
    Map<String, int> maxTime = convertFromDecimal(maxHoursPerDay);
    TextEditingController hoursController = TextEditingController();
    TextEditingController minutesController = TextEditingController();
    String? hoursErrorText;
    String? minutesErrorText;

    showDialog(
      context: context,
      builder: (BuildContext context) {
        return StatefulBuilder(
          builder: (context, setState) {
            return AlertDialog(
              title: Text('Registrar Horas para $workerName'),
              content: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    'Máximo: ${maxTime['hours']} horas y ${maxTime['minutes']} minutos',
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 16),
                  Row(
                    children: [
                      Expanded(
                        child: TextField(
                          controller: hoursController,
                          keyboardType: TextInputType.number,
                          decoration: InputDecoration(
                            labelText: 'Horas',
                            errorText: hoursErrorText,
                            border: const OutlineInputBorder(),
                          ),
                          inputFormatters: [
                            FilteringTextInputFormatter.digitsOnly,
                          ],
                          onChanged: (value) {
                            setState(() {
                              int? hours = int.tryParse(value);
                              hoursErrorText =
                                  (hours != null && hours > maxTime['hours']!)
                                  ? 'Máximo ${maxTime['hours']} horas'
                                  : null;
                            });
                          },
                        ),
                      ),
                      const SizedBox(width: 10),
                      Expanded(
                        child: TextField(
                          controller: minutesController,
                          keyboardType: TextInputType.number,
                          decoration: InputDecoration(
                            labelText: 'Minutos',
                            errorText: minutesErrorText,
                            border: const OutlineInputBorder(),
                          ),
                          inputFormatters: [
                            FilteringTextInputFormatter.digitsOnly,
                          ],
                          onChanged: (value) {
                            setState(() {
                              int? minutes = int.tryParse(value);
                              minutesErrorText =
                                  (minutes != null &&
                                      (minutes < 0 || minutes > 59))
                                  ? 'Entre 0 y 59 minutos'
                                  : null;
                            });
                          },
                        ),
                      ),
                    ],
                  ),
                ],
              ),
              actions: [
                TextButton(
                  child: const Text('Cancelar'),
                  onPressed: () => Navigator.of(context).pop(),
                ),
                TextButton(
                  child: const Text('Guardar'),
                  onPressed: () {
                    int hours = int.tryParse(hoursController.text) ?? 0;
                    int minutes = int.tryParse(minutesController.text) ?? 0;

                    if (hours > maxTime['hours']! ||
                        (hours == maxTime['hours']! &&
                            minutes > maxTime['minutes']!) ||
                        minutes > 59) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                          content: Text(
                            'El tiempo ingresado excede el máximo o es inválido',
                          ),
                          backgroundColor: Colors.red,
                        ),
                      );
                    } else {
                      this.setState(() {
                        workerHours[workerName] = convertToDecimal(
                          hours,
                          minutes,
                        );
                      });
                      Navigator.of(context).pop();
                    }
                  },
                ),
              ],
            );
          },
        );
      },
    );
  }

  Future<void> submitAsistencia() async {
    if (workerNames.any(
      (name) => workerCategories[name] == null || workerHours[name] == null,
    )) {
      _showErrorDialog('Asigna asistencia y horas a todos los trabajadores.');
      return;
    }

    _showLoadingDialog();

    try {
      List<Map<String, dynamic>> asistencias = workerNames
          .map(
            (name) => {
              'trabajador_id': workerIds[name],
              'nombre_registrado': name,
              'horas_registradas': workerHours[name] ?? 0,
              'estado': workerCategories[name] ?? 'A',
            },
          )
          .toList();

      final response = await apiService
          .post('gestion_retroactiva_asistencia/', {
            'codigo_supervisor': userInfo.idSupervisor.toString(),
            'asistencias': asistencias,
            'fecha': fechaStr,
          });

      final data = jsonDecode(response.body);

      if (mounted) Navigator.of(context).pop();

      if (data['status'] != 'success') {
        logger.e(
          'Error al registrar asistencia retroactiva: ${data['message']}',
        );
        _showErrorDialog('Error al registrar asistencia. Inténtalo de nuevo.');
        return;
      }

      List<dynamic> errores = data['errores'] ?? [];
      if (errores.isNotEmpty) {
        String mensajeError = 'Errores al registrar:\n';
        for (var error in errores) {
          mensajeError +=
              '- Trabajador ID ${error['trabajador_id']}: ${error['error']}\n';
        }
        _showErrorDialog(mensajeError);
        return;
      }

      bool remainingWorkers = data['remaining_workers'] ?? false;
      int registrosCreados = data['registros_creados'] ?? 0;

      if (remainingWorkers) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(
                'Se registraron $registrosCreados trabajadores. Continuando con los restantes.',
              ),
              duration: const Duration(seconds: 3),
              backgroundColor: const Color.fromARGB(255, 180, 60, 0),
            ),
          );
        }
        await refreshWorkerList();
      } else {
        await refreshWorkerList();
        if (mounted) _showSuccessDialog();
      }
    } catch (e) {
      if (mounted) Navigator.of(context).pop();
      logger.e('Error general al registrar asistencia retroactiva: $e');
      _showErrorDialog('Error al registrar asistencia. Inténtalo de nuevo.');
    }
  }

  Future<void> refreshWorkerList() async {
    try {
      final response = await apiService.get(
        'gestion_retroactiva_asistencia/?supervisor_id=${userInfo.idSupervisor}&holding=${userInfo.holding}&fecha=$fechaStr',
      );
      final data = jsonDecode(response.body);

      if (data['acceso_asistencia'] == true && data.containsKey('workers')) {
        var workers = data['workers'] as List;
        setState(() {
          workerNames = workers.map((w) => w['nombre'] as String).toList();
          workerIds = {
            for (var w in workers) w['nombre'] as String: w['id'] as int,
          };
          workerHours = {
            for (var w in workers)
              w['nombre'] as String: (w['horas_maximas'] as num).toDouble(),
          };
          workerMaxHours = Map.from(workerHours);
          workerCategories.clear();
        });
      }
    } catch (e) {
      logger.e('Error refreshing worker list retroactivo: $e');
    }
  }

  void _showLoadingDialog() {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => Dialog(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              SizedBox(
                width: 100,
                height: 100,
                child: Lottie.asset('assets/animations/loading_blue.json'),
              ),
              const SizedBox(width: 16),
              const Text('Ingresando Asistencia...'),
            ],
          ),
        ),
      ),
    );
  }

  void _showSuccessDialog() {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (BuildContext context) {
        return PopScope(
          canPop: false,
          child: AlertDialog(
            title: const Text('Éxito'),
            content: const Text(
              'Asistencia retroactiva ingresada correctamente.',
            ),
            actions: [
              TextButton(
                child: const Text('Aceptar'),
                onPressed: () {
                  Navigator.of(context).pop();
                  navigateToScreen(context, '/Mother_Layout');
                },
              ),
            ],
          ),
        );
      },
    );
  }

  void _showErrorDialog(String message) {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: const Text('Error'),
          content: SingleChildScrollView(child: Text(message)),
          actions: [
            TextButton(
              child: const Text('Aceptar'),
              onPressed: () => Navigator.of(context).pop(),
            ),
          ],
        );
      },
    );
  }

  void cycleCategory(String workerName) {
    setState(() {
      int currentIndex = categories.indexOf(workerCategories[workerName] ?? '');
      workerCategories[workerName] =
          categories[(currentIndex + 1) % categories.length];
    });
  }

  Color _getColorForCategory(String category) {
    switch (category) {
      case 'A':
        return Colors.green;
      case 'F':
        return Colors.red;
      case 'PN':
        return Colors.blue;
      case 'PR':
        return const Color.fromARGB(255, 199, 101, 216);
      default:
        return Colors.grey;
    }
  }

  Widget _buildSelectAllButton(String category) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 4.0),
      child: ElevatedButton(
        onPressed: () {
          setState(() {
            for (var name in workerNames) {
              workerCategories[name] = category;
            }
          });
        },
        style: ElevatedButton.styleFrom(
          backgroundColor: _getColorForCategory(category),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(8),
            side: const BorderSide(color: Colors.black, width: 1),
          ),
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        ),
        child: Text(
          category,
          style: const TextStyle(
            color: Colors.black,
            fontWeight: FontWeight.w800,
          ),
        ),
      ),
    );
  }

  Widget _buildRegisterHoursButton() {
    return IconButton(
      icon: const Icon(Icons.timer, color: Colors.white),
      tooltip: 'Registrar horas máximas a todos',
      onPressed: () {
        setState(() {
          for (var name in workerNames) {
            workerHours[name] = workerMaxHours[name] ?? 9.0;
          }
        });
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: const BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            Color.fromARGB(255, 166, 120, 104),
            Color.fromARGB(255, 186, 155, 114),
          ],
        ),
      ),
      child: Scaffold(
        backgroundColor: Colors.transparent,
        appBar: PreferredSize(
          preferredSize: const Size.fromHeight(120),
          child: Column(
            children: [
              Container(
                width: double.infinity,
                color: const Color.fromARGB(255, 180, 60, 0),
                padding: const EdgeInsets.symmetric(vertical: 4),
                child: const Text(
                  'ASISTENCIA RETROACTIVA',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                    fontSize: 12,
                  ),
                ),
              ),
              Container(
                padding: const EdgeInsets.only(top: 6, bottom: 5),
                color: const Color.fromARGB(255, 6, 62, 107),
                child: Center(
                  child: Text(
                    'Fecha: $fechaDisplay',
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 22,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ),
              AppBar(
                toolbarHeight: 50,
                automaticallyImplyLeading: true,
                backgroundColor: const Color.fromARGB(255, 6, 62, 107),
                title: const Text('Asistencia Retroactiva'),
                actions: [
                  ...categories.map((c) => _buildSelectAllButton(c)),
                  _buildRegisterHoursButton(),
                ],
              ),
            ],
          ),
        ),
        body: Column(
          children: [
            Expanded(
              child: workerNames.isEmpty
                  ? const Center(
                      child: Text(
                        'No hay trabajadores pendientes para esa fecha',
                        style: TextStyle(
                          fontSize: 18,
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    )
                  : ListView.builder(
                      itemCount: workerNames.length,
                      itemBuilder: (context, index) {
                        String workerName = workerNames[index];
                        String workerCategory =
                            workerCategories[workerName] ?? '';
                        double hours = workerHours[workerName] ?? 0;
                        Map<String, int> timeDisplay = convertFromDecimal(
                          hours,
                        );

                        return Card(
                          margin: const EdgeInsets.symmetric(
                            horizontal: 8,
                            vertical: 4,
                          ),
                          elevation: 2,
                          child: ListTile(
                            leading: Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                Container(
                                  width: 30,
                                  alignment: Alignment.center,
                                  child: Text(
                                    '${index + 1}.',
                                    style: const TextStyle(
                                      fontWeight: FontWeight.bold,
                                      fontSize: 16,
                                    ),
                                  ),
                                ),
                                const SizedBox(width: 8),
                                InkWell(
                                  onTap: () => cycleCategory(workerName),
                                  child: Container(
                                    decoration: BoxDecoration(
                                      shape: BoxShape.circle,
                                      border: Border.all(
                                        color: Colors.black,
                                        width: 2,
                                      ),
                                    ),
                                    child: CircleAvatar(
                                      backgroundColor: _getColorForCategory(
                                        workerCategory,
                                      ),
                                      child: Text(
                                        workerCategory,
                                        style: const TextStyle(
                                          fontWeight: FontWeight.w700,
                                          color: Colors.black,
                                        ),
                                      ),
                                    ),
                                  ),
                                ),
                                const SizedBox(width: 8),
                                InkWell(
                                  onTap: () => updateHours(workerName),
                                  child: Container(
                                    decoration: BoxDecoration(
                                      shape: BoxShape.circle,
                                      border: Border.all(
                                        color: Colors.black,
                                        width: 2,
                                      ),
                                    ),
                                    child: CircleAvatar(
                                      backgroundColor: hours > 0
                                          ? Colors.amber
                                          : Colors.grey,
                                      child: Text(
                                        hours > 0
                                            ? '${timeDisplay['hours']}:${timeDisplay['minutes'].toString().padLeft(2, '0')}'
                                            : '0:00',
                                        style: const TextStyle(
                                          fontWeight: FontWeight.w700,
                                          fontSize: 12,
                                          color: Colors.black,
                                        ),
                                      ),
                                    ),
                                  ),
                                ),
                              ],
                            ),
                            title: Text(
                              workerName,
                              style: const TextStyle(
                                fontWeight: FontWeight.bold,
                                fontSize: 16,
                              ),
                            ),
                          ),
                        );
                      },
                    ),
            ),
            Padding(
              padding: const EdgeInsets.only(
                bottom: 0,
                right: 4,
                left: 4,
                top: 10,
              ),
              child: ElevatedButton(
                onPressed: workerNames.isEmpty ? null : submitAsistencia,
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 25,
                    vertical: 25,
                  ),
                  backgroundColor: const Color.fromARGB(255, 180, 60, 0),
                  disabledBackgroundColor: Colors.grey,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(8),
                  ),
                  minimumSize: const Size(double.infinity, 50),
                ),
                child: const Text(
                  "INGRESAR ASISTENCIA RETROACTIVA",
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                    fontSize: 16,
                  ),
                ),
              ),
            ),
            const SizedBox(height: 85),
          ],
        ),
      ),
    );
  }
}
