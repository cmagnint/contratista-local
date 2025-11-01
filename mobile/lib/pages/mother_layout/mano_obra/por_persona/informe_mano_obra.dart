import 'dart:convert';
import 'package:contratista/services/contratista_api_service.dart';
import 'package:flutter/material.dart';
import 'package:contratista/utils/globals.dart';
import 'package:intl/intl.dart';

class InformeManoObraScreen extends StatefulWidget {
  const InformeManoObraScreen({super.key});

  @override
  InformeManoObraScreenState createState() => InformeManoObraScreenState();
}

class InformeManoObraScreenState extends State<InformeManoObraScreen> {
  ApiService apiService = ApiService();
  Map<String, dynamic> dataManoObra = {};
  String? selectedTipo;
  String? selectedLabor;
  List<String> laboresList = [];
  final TextEditingController rankingController = TextEditingController();

  List<Map<String, dynamic>> todosRendimientos = [];
  List<Map<String, dynamic>> mejorRendimiento = [];
  List<Map<String, dynamic>> peorRendimiento = [];

  DateTimeRange? selectedDateRange;
  bool isLoading = false;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      fetchData();
    });
  }

  void _showLoadingDialog() {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => const Center(child: CircularProgressIndicator()),
    );
  }

  Future<void> fetchData() async {
    setState(() => isLoading = true);
    _showLoadingDialog();

    try {
      String? holding = await storage.read(key: 'holding');
      String url =
          'informe_mano_obra/?supervisor_id=${userInfo.idSupervisor}&holding=$holding';

      if (selectedDateRange != null) {
        String fechaInicio = DateFormat(
          'yyyy-MM-dd',
        ).format(selectedDateRange!.start);
        String fechaFin = DateFormat(
          'yyyy-MM-dd',
        ).format(selectedDateRange!.end);
        url += '&fecha_inicio=$fechaInicio&fecha_fin=$fechaFin';
      }

      loggerGlobal.d('Fetching: $url');
      final response = await apiService.get(url);
      if (mounted) Navigator.of(context).pop();

      final data = jsonDecode(response.body);
      if (data['registros'] != null) {
        processData(data);
      } else {
        throw Exception('Formato de respuesta inesperado');
      }

      setState(() => isLoading = false);
    } catch (e) {
      loggerGlobal.e('Error fetching data: $e');
      if (mounted) {
        Navigator.of(context).pop();
        _showDialogWithMessage(context, 'Error: ${e.toString()}');
      }
      setState(() => isLoading = false);
    }
  }

  void processData(Map<String, dynamic> response) {
    Map<String, dynamic> processedData = {};

    for (var registro in response['registros']) {
      String laborNombre = registro['nombre_labor'];

      if (!processedData.containsKey(laborNombre)) {
        processedData[laborNombre] = {
          'supervisores': {},
          'centros_costos': {},
          'unidad_control':
              registro['unidad_control'] ?? 'Sin Unidad de Control',
        };
      }

      String supervisorNombre =
          registro['nombre_supervisor'] ?? 'Sin Supervisor';
      if (!processedData[laborNombre]['supervisores'].containsKey(
        supervisorNombre,
      )) {
        processedData[laborNombre]['supervisores'][supervisorNombre] = {
          'total_horas': 0.0,
          'total_produccion': 0.0,
          'trabajadores': [],
        };
      }

      processedData[laborNombre]['supervisores'][supervisorNombre]['total_horas'] +=
          registro['horas_trabajadas'];
      processedData[laborNombre]['supervisores'][supervisorNombre]['total_produccion'] +=
          registro['produccion'];
      processedData[laborNombre]['supervisores'][supervisorNombre]['trabajadores']
          .add({
            'nombre': registro['nombre_trabajador'],
            'produccion': registro['produccion'],
          });

      String centroCostoNombre = registro['nombre_centro_costo'];
      if (!processedData[laborNombre]['centros_costos'].containsKey(
        centroCostoNombre,
      )) {
        processedData[laborNombre]['centros_costos'][centroCostoNombre] = {
          'total_horas': 0.0,
          'total_produccion': 0.0,
          'trabajadores': [],
        };
      }

      processedData[laborNombre]['centros_costos'][centroCostoNombre]['total_horas'] +=
          registro['horas_trabajadas'];
      processedData[laborNombre]['centros_costos'][centroCostoNombre]['total_produccion'] +=
          registro['produccion'];
      processedData[laborNombre]['centros_costos'][centroCostoNombre]['trabajadores']
          .add({
            'nombre': registro['nombre_trabajador'],
            'horas_trabajadas': registro['horas_trabajadas'],
            'produccion': registro['produccion'],
          });
    }

    setState(() {
      dataManoObra = processedData;
      updateLaboresList();
    });
  }

  void updateLaboresList() {
    laboresList.clear();
    for (var k in dataManoObra.keys) {
      laboresList.add(k);
    }
    if (laboresList.isNotEmpty) {
      selectedLabor = laboresList.first;
      mostrarTodosRendimientos();
    }
  }

  void mostrarTodosRendimientos() {
    if (selectedLabor == null || selectedTipo == null) return;

    final List<Map<String, dynamic>> trabajadores = [];

    if (selectedTipo == "POR SUPERVISOR") {
      dataManoObra[selectedLabor]['supervisores'].forEach((_, supervisorData) {
        final List<dynamic> workersList =
            supervisorData['trabajadores'] as List<dynamic>;
        trabajadores.addAll(workersList.map((w) => w as Map<String, dynamic>));
      });
    } else if (selectedTipo == "POR CENTRO DE COSTOS") {
      dataManoObra[selectedLabor]['centros_costos'].forEach((
        _,
        costCenterData,
      ) {
        final List<dynamic> workersList =
            costCenterData['trabajadores'] as List<dynamic>;
        trabajadores.addAll(workersList.map((w) => w as Map<String, dynamic>));
      });
    }

    trabajadores.sort((a, b) => b['produccion'].compareTo(a['produccion']));

    final List<Map<String, dynamic>> trabajadoresUnicos = [];
    final Set<String> nombresUnicos = {};
    for (var trabajador in trabajadores) {
      if (nombresUnicos.add(trabajador['nombre'])) {
        trabajadoresUnicos.add(trabajador);
      }
    }

    final List<Map<String, dynamic>> trabajadoresConInfo = trabajadoresUnicos
        .map((trabajador) {
          var supervisor = encontrarSupervisorParaTrabajador(
            trabajador,
            dataManoObra,
          );
          var unidadControl = dataManoObra[selectedLabor]['unidad_control'];
          return {
            ...trabajador,
            'supervisor': supervisor,
            'unidad_control': unidadControl,
          };
        })
        .toList();

    setState(() {
      todosRendimientos = trabajadoresConInfo;
    });
  }

  void calcularRanking() {
    final int rankingSize = int.tryParse(rankingController.text) ?? 0;
    if (todosRendimientos.isEmpty) return;

    final int maxRankingSize = (todosRendimientos.length / 2).truncate();

    if (rankingSize <= 0 || rankingSize > maxRankingSize) {
      _showDialogWithMessage(
        context,
        'Ingrese un número entre 1 y $maxRankingSize (máximo: ${todosRendimientos.length ~/ 2})',
      );
      return;
    }

    setState(() {
      mejorRendimiento = todosRendimientos.take(rankingSize).toList();
      peorRendimiento = todosRendimientos.reversed.take(rankingSize).toList();
    });
  }

  Future<void> _selectDateRange(BuildContext context) async {
    final DateTimeRange? picked = await showDateRangePicker(
      context: context,
      firstDate: DateTime(2020),
      lastDate: DateTime.now().add(const Duration(days: 365)),
      initialDateRange:
          selectedDateRange ??
          DateTimeRange(
            start: DateTime.now().subtract(const Duration(days: 7)),
            end: DateTime.now(),
          ),
    );

    if (picked != null) {
      setState(() {
        selectedDateRange = picked;
      });
      fetchData();
    }
  }

  String encontrarSupervisorParaTrabajador(
    Map<String, dynamic> trabajador,
    Map<String, dynamic> data,
  ) {
    String supervisorNombre = 'Sin Supervisor';
    for (var labor in data.keys) {
      for (var sup in data[labor]['supervisores'].keys) {
        var trabajadores = data[labor]['supervisores'][sup]['trabajadores'];
        if (trabajadores.any((t) => t['nombre'] == trabajador['nombre'])) {
          supervisorNombre = sup;
          break;
        }
      }
    }
    return supervisorNombre;
  }

  void _showDialogWithMessage(BuildContext context, String message) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Aviso'),
        content: Text(message),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }

  Color _getColorForRank(int index, int total) {
    final double tercio = total / 3;
    if (index < tercio) return Colors.green;
    if (index < tercio * 2) return Colors.orange;
    return Colors.red;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        automaticallyImplyLeading: true,
        backgroundColor: Colors.greenAccent.shade200,
        title: const Text(
          "INFORME MANO DE OBRA",
          style: TextStyle(fontWeight: FontWeight.w900),
        ),
      ),
      body: isLoading
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              child: Center(
                child: Column(
                  children: [
                    Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: ElevatedButton.icon(
                        onPressed: () => _selectDateRange(context),
                        icon: const Icon(Icons.calendar_today),
                        label: Text(
                          selectedDateRange == null
                              ? 'SELECCIONAR RANGO DE FECHAS'
                              : '${DateFormat('dd/MM/yyyy').format(selectedDateRange!.start)} - ${DateFormat('dd/MM/yyyy').format(selectedDateRange!.end)}',
                        ),
                        style: ElevatedButton.styleFrom(
                          foregroundColor: Colors.white,
                          backgroundColor: const Color.fromARGB(
                            255,
                            23,
                            160,
                            160,
                          ),
                          padding: const EdgeInsets.symmetric(
                            horizontal: 20,
                            vertical: 15,
                          ),
                        ),
                      ),
                    ),
                    DropdownButton<String>(
                      value: selectedTipo,
                      hint: const Text("Selecciona tipo"),
                      items: ['POR SUPERVISOR', 'POR CENTRO DE COSTOS'].map((
                        String value,
                      ) {
                        return DropdownMenuItem<String>(
                          value: value,
                          child: Text(value),
                        );
                      }).toList(),
                      onChanged: (newValue) {
                        setState(() {
                          selectedTipo = newValue!;
                          mostrarTodosRendimientos();
                        });
                      },
                    ),
                    if (selectedTipo != null)
                      DropdownButton<String>(
                        value: selectedLabor,
                        hint: const Text("Selecciona Labor"),
                        items: laboresList.map((String value) {
                          return DropdownMenuItem<String>(
                            value: value,
                            child: Text(value),
                          );
                        }).toList(),
                        onChanged: (newValue) {
                          setState(() {
                            selectedLabor = newValue;
                            mostrarTodosRendimientos();
                          });
                        },
                      ),
                    if (selectedTipo != null && selectedLabor != null)
                      buildDataTable(),
                    if (todosRendimientos.isNotEmpty)
                      Column(
                        children: [
                          const Padding(
                            padding: EdgeInsets.all(16.0),
                            child: Text(
                              'TODOS LOS RENDIMIENTOS',
                              style: TextStyle(
                                fontSize: 20,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                          buildRankingCompleto(),
                        ],
                      ),
                    if (laboresList.isNotEmpty)
                      Column(
                        children: [
                          SizedBox(
                            width: 300,
                            child: TextField(
                              controller: rankingController,
                              keyboardType: TextInputType.number,
                              decoration: InputDecoration(
                                labelText:
                                    'Número para ranking (max: ${todosRendimientos.length ~/ 2})',
                              ),
                            ),
                          ),
                          Padding(
                            padding: const EdgeInsets.only(bottom: 110.0),
                            child: ElevatedButton(
                              onPressed: calcularRanking,
                              style: ElevatedButton.styleFrom(
                                foregroundColor: Colors.black,
                                backgroundColor: const Color.fromARGB(
                                  255,
                                  23,
                                  160,
                                  160,
                                ),
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(30),
                                ),
                                padding: const EdgeInsets.symmetric(
                                  horizontal: 50,
                                  vertical: 20,
                                ),
                              ),
                              child: const Text(
                                'CALCULAR RANKING',
                                style: TextStyle(fontWeight: FontWeight.bold),
                              ),
                            ),
                          ),
                          if (mejorRendimiento.isNotEmpty)
                            buildRankingList(
                              mejorRendimiento,
                              'Mejores Rendimientos',
                            ),
                          if (peorRendimiento.isNotEmpty)
                            Padding(
                              padding: const EdgeInsets.only(bottom: 120.0),
                              child: buildRankingList(
                                peorRendimiento,
                                'Peores Rendimientos',
                              ),
                            ),
                        ],
                      ),
                  ],
                ),
              ),
            ),
    );
  }

  Widget buildRankingCompleto() {
    return Padding(
      padding: const EdgeInsets.only(bottom: 60.0),
      child: SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Padding(
              padding: const EdgeInsets.only(top: 56.0),
              child: Column(
                children: List.generate(
                  todosRendimientos.length,
                  (index) => Container(
                    width: 18,
                    height: 48,
                    color: _getColorForRank(index, todosRendimientos.length),
                  ),
                ),
              ),
            ),
            const SizedBox(width: 4),
            DataTable(
              columns: const <DataColumn>[
                DataColumn(label: Text('#')),
                DataColumn(label: Text('Nombre')),
                DataColumn(label: Text('U.Control')),
                DataColumn(label: Text('Producción')),
                DataColumn(label: Text('Supervisor')),
              ],
              rows: List<DataRow>.generate(todosRendimientos.length, (index) {
                final trabajador = todosRendimientos[index];
                final bool esMejor = index == 0;
                final bool esPeor = index == todosRendimientos.length - 1;

                return DataRow(
                  color: MaterialStateProperty.resolveWith<Color?>((
                    Set<MaterialState> states,
                  ) {
                    if (esMejor) return Colors.green.withOpacity(0.3);
                    if (esPeor) return Colors.red.withOpacity(0.3);
                    return null;
                  }),
                  cells: <DataCell>[
                    DataCell(
                      Text(
                        '${index + 1}', // ← CAMBIAR DE: todosRendimientos.length - index
                        style: TextStyle(
                          fontWeight: (esMejor || esPeor)
                              ? FontWeight.bold
                              : FontWeight.normal,
                        ),
                      ),
                    ),
                    DataCell(
                      Text(
                        trabajador['nombre'],
                        style: TextStyle(
                          fontWeight: (esMejor || esPeor)
                              ? FontWeight.bold
                              : FontWeight.normal,
                        ),
                      ),
                    ),
                    DataCell(Text(trabajador['unidad_control'])),
                    DataCell(
                      Text(
                        '${trabajador['produccion']}',
                        style: TextStyle(
                          fontWeight: (esMejor || esPeor)
                              ? FontWeight.bold
                              : FontWeight.normal,
                        ),
                      ),
                    ),
                    DataCell(Text(trabajador['supervisor'])),
                  ],
                );
              }),
            ),
          ],
        ),
      ),
    );
  }

  Widget buildRankingList(List<Map<String, dynamic>> ranking, String title) {
    final bool esMejor = title.contains('Mejores');

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.all(8.0),
          child: Text(
            title,
            style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),
        ),
        SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          child: DataTable(
            columns: const <DataColumn>[
              DataColumn(label: Text('#')),
              DataColumn(label: Text('Nombre')),
              DataColumn(label: Text('U.Control')),
              DataColumn(label: Text('Producción')),
              DataColumn(label: Text('Supervisor')),
            ],
            rows: List<DataRow>.generate(
              ranking.length,
              (index) => DataRow(
                cells: <DataCell>[
                  DataCell(
                    Text(
                      esMejor
                          ? '${index + 1}' // Mejores: 1, 2, 3...
                          : '${todosRendimientos.length - ranking.length + index + 1}', // Peores: 8, 9, 10...
                    ),
                  ),
                  DataCell(Text(ranking[index]['nombre'])),
                  DataCell(Text(ranking[index]['unidad_control'])),
                  DataCell(Text('${ranking[index]['produccion']}')),
                  DataCell(Text(ranking[index]['supervisor'])),
                ],
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget buildDataTable() {
    String firstColumnName = selectedTipo == "POR SUPERVISOR"
        ? 'Supervisor'
        : 'Centro de costos';
    var columnNames = [
      firstColumnName,
      'JH',
      'U.Control',
      'Producción',
      'Rendimiento',
    ];
    List<DataRow> rows = [];

    if (selectedTipo == "POR SUPERVISOR") {
      dataManoObra[selectedLabor]['supervisores'].forEach((
        supervisorName,
        supervisorData,
      ) {
        double totalHoras = supervisorData['total_horas'] ?? 0;
        double produccion = supervisorData['total_produccion'] ?? 0;
        double jh = totalHoras / 7.5;
        double rendimiento = jh > 0 ? produccion / jh : 0;

        rows.add(
          DataRow(
            cells: [
              DataCell(Text(supervisorName)),
              DataCell(Text(NumberFormat("0.00").format(jh))),
              DataCell(Text(dataManoObra[selectedLabor]['unidad_control'])),
              DataCell(Text(NumberFormat("0").format(produccion))),
              DataCell(Text(NumberFormat("0.00").format(rendimiento))),
            ],
          ),
        );
      });
    } else if (selectedTipo == "POR CENTRO DE COSTOS") {
      dataManoObra[selectedLabor]['centros_costos'].forEach((
        costCenterName,
        costCenterData,
      ) {
        double totalHoras = costCenterData['total_horas'] ?? 0;
        double produccion = costCenterData['total_produccion'] ?? 0;
        double jh = totalHoras / 7.5;
        double rendimiento = jh > 0 ? produccion / jh : 0;

        rows.add(
          DataRow(
            cells: [
              DataCell(Text(costCenterName)),
              DataCell(Text(NumberFormat("0.00").format(jh))),
              DataCell(Text(dataManoObra[selectedLabor]['unidad_control'])),
              DataCell(Text(NumberFormat("0").format(produccion))),
              DataCell(Text(NumberFormat("0.00").format(rendimiento))),
            ],
          ),
        );
      });
    }

    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: DataTable(
        columns: columnNames
            .map((name) => DataColumn(label: Text(name)))
            .toList(),
        rows: rows,
      ),
    );
  }

  @override
  void dispose() {
    rankingController.dispose();
    super.dispose();
  }
}
