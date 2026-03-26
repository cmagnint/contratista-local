import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:contratista/utils/globals.dart';
import 'package:contratista/services/contratista_api_service.dart';
import 'package:intl/intl.dart';

class InformeAsistenciaScreen extends StatefulWidget {
  const InformeAsistenciaScreen({super.key});

  @override
  InformeAsistenciaScreenState createState() => InformeAsistenciaScreenState();
}

class InformeAsistenciaScreenState extends State<InformeAsistenciaScreen> {
  Map<String, dynamic> sociedades = {};
  Map<String, dynamic> fundos = {};
  Map<String, dynamic> supervisores = {};
  List<Map<String, dynamic>> informeData = [];
  ApiService apiService = ApiService();
  String? selectedEstado;
  DateTime selectedDate = DateTime.now();
  bool isLoading = false;

  Map<String, Color> estadoColores = {
    'A': const Color.fromARGB(255, 175, 220, 61),
    'F': const Color.fromARGB(255, 227, 94, 94),
    'PN': const Color.fromARGB(255, 237, 179, 70),
    'PR': const Color.fromARGB(255, 234, 234, 73),
  };

  @override
  void initState() {
    super.initState();
    buscarPorFecha(useCurrentDate: true);
  }

  String formatHorasTrabajadas(dynamic horas) {
    if (horas == null) return '0 h 00 min';
    double horasDouble = horas is int ? horas.toDouble() : horas;
    int horasEnteras = horasDouble.floor();
    int minutos = ((horasDouble - horasEnteras) * 60).round();
    return '$horasEnteras h ${minutos.toString().padLeft(2, '0')} min';
  }

  Future<void> buscarPorFecha({bool useCurrentDate = false}) async {
    if (!useCurrentDate) {
      final DateTime? pickedDate = await showDatePicker(
        context: context,
        initialDate: selectedDate,
        firstDate: DateTime(2000),
        lastDate: DateTime(2101),
      );

      if (pickedDate == null) return;
      selectedDate = pickedDate;
    }

    if (!mounted) return;

    setState(() {
      isLoading = true;
    });

    String formattedDate = DateFormat('yyyy-MM-dd').format(selectedDate);

    try {
      String url =
          'informe_asistencia/?fecha=$formattedDate&is_admin=${userInfo.isAdmin}';

      if (!userInfo.isAdmin) {
        final supervisorId = userInfo.idSupervisor;
        url += '&supervisor_id=$supervisorId';
      }

      var response = await apiService.get(url);

      final data = jsonDecode(response.body);
      if (!mounted) return;

      setState(() {
        sociedades = Map<String, dynamic>.from(data['sociedades'] ?? {});
        fundos = Map<String, dynamic>.from(data['fundos'] ?? {});
        supervisores = Map<String, dynamic>.from(data['supervisores'] ?? {});
        informeData = List<Map<String, dynamic>>.from(
          data['reporte_detallado'] ?? [],
        );
        isLoading = false;
      });

      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Informe actualizado para la fecha: $formattedDate'),
          backgroundColor: Colors.green,
        ),
      );
    } catch (e) {
      if (!mounted) return;

      setState(() {
        isLoading = false;
      });

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error al obtener el informe: $e'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  void _showDetalleEstados(String nombre, Map<String, dynamic> detalle) {
    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: Text(nombre, style: const TextStyle(fontSize: 16)),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: detalle.entries.map((entry) {
              return ListTile(
                leading: Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 8,
                    vertical: 4,
                  ),
                  decoration: BoxDecoration(
                    color: estadoColores[entry.key] ?? Colors.grey,
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Text(
                    entry.key,
                    style: const TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                title: Text(formatHorasTrabajadas(entry.value)),
              );
            }).toList(),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('Cerrar'),
            ),
          ],
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'INFORME DE ASISTENCIAS',
          style: TextStyle(color: Colors.white, fontWeight: FontWeight.w600),
        ),
        backgroundColor: const Color.fromARGB(255, 6, 62, 107),
      ),
      body: isLoading
          ? const Center(child: CircularProgressIndicator())
          : ListView(
              children: [
                Padding(
                  padding: const EdgeInsets.all(8.0),
                  child: Text(
                    'Fecha: ${DateFormat('dd/MM/yyyy').format(selectedDate)}',
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                    textAlign: TextAlign.center,
                  ),
                ),
                _buildOptionTile('INFORME POR SOCIEDAD', 'sociedad'),
                _buildOptionTile('INFORME POR FUNDO', 'fundo'),
                _buildOptionTile('INFORME POR SUPERVISOR', 'supervisor'),
                const SizedBox(height: 300),
                Padding(
                  padding: const EdgeInsets.only(
                    bottom: 0.0,
                    right: 4,
                    left: 4,
                    top: 10,
                  ),
                  child: ElevatedButton(
                    onPressed: () => buscarPorFecha(),
                    style: ElevatedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 25,
                        vertical: 25,
                      ),
                      backgroundColor: const Color.fromARGB(255, 6, 62, 107),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8),
                      ),
                      minimumSize: const Size(double.infinity, 50),
                    ),
                    child: const Text(
                      "BUSCAR POR FECHA",
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                    ),
                  ),
                ),
              ],
            ),
    );
  }

  Widget _buildOptionTile(String title, String tipo) {
    return Container(
      decoration: BoxDecoration(
        color: const Color.fromARGB(255, 6, 62, 107),
        border: Border.all(color: const Color.fromARGB(255, 0, 0, 0)),
        borderRadius: BorderRadius.circular(8),
      ),
      margin: const EdgeInsets.all(8),
      child: ListTile(
        title: Text(
          title,
          style: const TextStyle(
            color: Colors.white,
            fontWeight: FontWeight.w600,
          ),
        ),
        onTap: () => _showInformeDialog(tipo),
      ),
    );
  }

  void _showInformeDialog(String tipo) {
    String? localSelectedEstado = selectedEstado;

    showDialog(
      context: context,
      builder: (BuildContext context) {
        return StatefulBuilder(
          builder: (context, setState) {
            Map<String, dynamic> dataOriginal;
            String title;
            switch (tipo) {
              case 'sociedad':
                dataOriginal = sociedades;
                title = 'Informe por Sociedad';
                break;
              case 'fundo':
                dataOriginal = fundos;
                title = 'Informe por Fundo';
                break;
              case 'supervisor':
                dataOriginal = supervisores;
                title = 'Informe por Supervisor';
                break;
              default:
                dataOriginal = {};
                title = '';
            }

            // Recalcular conteos si hay filtro activo
            Map<String, dynamic> data;
            if (localSelectedEstado != null) {
              data = {};
              for (var trab in informeData) {
                Map<String, dynamic> detalle = Map<String, dynamic>.from(
                  trab['detalle_estados'] ?? {},
                );
                if (!detalle.containsKey(localSelectedEstado)) continue;

                String keyValue;
                switch (tipo) {
                  case 'sociedad':
                    keyValue = trab['sociedad'] ?? '';
                    break;
                  case 'fundo':
                    keyValue = trab['fundo'] ?? '';
                    break;
                  case 'supervisor':
                    keyValue = trab['supervisor'] ?? '';
                    break;
                  default:
                    keyValue = '';
                }
                data[keyValue] = (data[keyValue] ?? 0) + 1;
              }
            } else {
              data = dataOriginal;
            }

            return AlertDialog(
              title: Text(title),
              content: SizedBox(
                width: double.maxFinite,
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    _buildEstadosFilter(localSelectedEstado, (newState) {
                      setState(() {
                        localSelectedEstado = newState;
                      });
                    }),
                    Expanded(
                      child: data.isEmpty
                          ? const Center(
                              child: Text('No hay datos disponibles'),
                            )
                          : ListView.builder(
                              itemCount: data.length,
                              itemBuilder: (context, index) {
                                String key = data.keys.elementAt(index);
                                dynamic value = data[key];
                                return Container(
                                  decoration: BoxDecoration(
                                    border: Border.all(color: Colors.grey),
                                    borderRadius: BorderRadius.circular(8),
                                  ),
                                  margin: const EdgeInsets.symmetric(
                                    vertical: 4,
                                  ),
                                  child: ListTile(
                                    title: Text(key),
                                    trailing: Text(
                                      '${value.toString()} Trabajador(es)',
                                    ),
                                    onTap: () => _showTrabajadoresDialog(
                                      tipo,
                                      key,
                                      localSelectedEstado,
                                    ),
                                  ),
                                );
                              },
                            ),
                    ),
                  ],
                ),
              ),
            );
          },
        );
      },
    );
  }

  Widget _buildEstadosFilter(
    String? currentSelectedEstado,
    Function(String?) onStateChanged,
  ) {
    return Wrap(
      spacing: 8.0,
      children: ['A', 'F', 'PN', 'PR'].map((estado) {
        return ChoiceChip(
          label: Text(estado),
          selected: currentSelectedEstado == estado,
          onSelected: (bool selected) {
            onStateChanged(selected ? estado : null);
          },
          backgroundColor: estadoColores[estado],
          selectedColor: estadoColores[estado]?.withValues(alpha: 0.7),
        );
      }).toList(),
    );
  }

  void _showTrabajadoresDialog(
    String tipo,
    String key,
    String? initialSelectedEstado,
  ) {
    String? localSelectedEstado = initialSelectedEstado;

    showDialog(
      context: context,
      builder: (BuildContext context) {
        return StatefulBuilder(
          builder: (BuildContext context, StateSetter setState) {
            List trabajadoresFiltrados = _filtrarTrabajadores(
              tipo,
              key,
              localSelectedEstado,
            );

            double totalHoras = trabajadoresFiltrados.fold(0.0, (
              sum,
              trabajador,
            ) {
              Map<String, dynamic> detalle = Map<String, dynamic>.from(
                trabajador['detalle_estados'] ?? {},
              );
              if (localSelectedEstado != null &&
                  detalle.containsKey(localSelectedEstado)) {
                return sum + (detalle[localSelectedEstado] ?? 0);
              }
              return sum + (trabajador['horas_registradas'] ?? 0);
            });

            return AlertDialog(
              title: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Trabajadores de $key'),
                  Text('Total trabajadores: ${trabajadoresFiltrados.length}'),
                  Text('Total horas: ${formatHorasTrabajadas(totalHoras)}'),
                ],
              ),
              content: SizedBox(
                width: double.maxFinite,
                child: Column(
                  children: [
                    _buildEstadosFilter(localSelectedEstado, (newState) {
                      setState(() {
                        localSelectedEstado = newState;
                      });
                    }),
                    Expanded(
                      child: trabajadoresFiltrados.isEmpty
                          ? const Center(child: Text('No hay trabajadores'))
                          : ListView.builder(
                              itemCount: trabajadoresFiltrados.length,
                              itemBuilder: (context, index) {
                                var trabajador = trabajadoresFiltrados[index];
                                Map<String, dynamic> detalleEstados =
                                    Map<String, dynamic>.from(
                                      trabajador['detalle_estados'] ?? {},
                                    );

                                double horasMostrar;
                                List<String> estadosMostrar;

                                if (localSelectedEstado != null &&
                                    detalleEstados.containsKey(
                                      localSelectedEstado,
                                    )) {
                                  horasMostrar =
                                      (detalleEstados[localSelectedEstado] ?? 0)
                                          .toDouble();
                                  estadosMostrar = [localSelectedEstado!];
                                } else {
                                  horasMostrar =
                                      (trabajador['horas_registradas'] ?? 0)
                                          .toDouble();
                                  estadosMostrar =
                                      (trabajador['estado'] as String).split(
                                        ', ',
                                      );
                                }

                                return Container(
                                  decoration: BoxDecoration(
                                    border: Border.all(color: Colors.grey),
                                    borderRadius: BorderRadius.circular(8),
                                  ),
                                  margin: const EdgeInsets.symmetric(
                                    vertical: 4,
                                  ),
                                  child: ListTile(
                                    title: Text(
                                      trabajador['nombretrabajador'] ?? '',
                                    ),
                                    subtitle: Text(
                                      'Horas: ${formatHorasTrabajadas(horasMostrar)}',
                                    ),
                                    trailing: Wrap(
                                      spacing: 4,
                                      children: estadosMostrar.map((estado) {
                                        return Container(
                                          padding: const EdgeInsets.symmetric(
                                            horizontal: 6,
                                            vertical: 4,
                                          ),
                                          decoration: BoxDecoration(
                                            color:
                                                estadoColores[estado] ??
                                                Colors.grey,
                                            borderRadius: BorderRadius.circular(
                                              4,
                                            ),
                                          ),
                                          child: Text(
                                            estado,
                                            style: const TextStyle(
                                              color: Colors.white,
                                              fontWeight: FontWeight.bold,
                                              fontSize: 12,
                                            ),
                                          ),
                                        );
                                      }).toList(),
                                    ),
                                    onTap: detalleEstados.length > 1
                                        ? () => _showDetalleEstados(
                                            trabajador['nombretrabajador'],
                                            detalleEstados,
                                          )
                                        : null,
                                  ),
                                );
                              },
                            ),
                    ),
                  ],
                ),
              ),
            );
          },
        );
      },
    );
  }

  List _filtrarTrabajadores(
    String tipo,
    String key,
    String? currentSelectedEstado,
  ) {
    return informeData.where((trabajador) {
      bool condicionTipo = tipo == 'sociedad'
          ? trabajador['sociedad'] == key
          : tipo == 'fundo'
          ? trabajador['fundo'] == key
          : trabajador['supervisor'] == key;
      bool condicionEstado =
          currentSelectedEstado == null ||
          (Map<String, dynamic>.from(
            trabajador['detalle_estados'] ?? {},
          )).containsKey(currentSelectedEstado);
      return condicionTipo && condicionEstado;
    }).toList();
  }
}
