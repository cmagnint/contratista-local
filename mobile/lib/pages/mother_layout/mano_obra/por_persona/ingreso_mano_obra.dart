import 'package:contratista/services/contratista_api_service.dart';
import 'package:flutter/material.dart';
import 'package:contratista/utils/globals.dart';
import 'package:flutter/services.dart';
import 'package:lottie/lottie.dart';
import 'package:intl/intl.dart';

class IngresoManoObraScreen extends StatefulWidget {
  final List<Trabajador> trabajadores;
  final List<UnidadControl> unidadesControl;
  final String cliente;
  final String labor;
  final int laborId;
  final int folioId;

  const IngresoManoObraScreen({
    super.key,
    required this.trabajadores,
    required this.unidadesControl,
    required this.cliente,
    required this.labor,
    required this.laborId,
    required this.folioId,
  });

  @override
  IngresoManoObraScreenState createState() => IngresoManoObraScreenState();
}

class IngresoManoObraScreenState extends State<IngresoManoObraScreen> {
  ApiService apiService = ApiService();
  UnidadControl? selectedUnidadControl;
  Map<int, bool> selectedTrabajadores = {};
  List<TextEditingController> horasControllers = [];
  List<TextEditingController> produccionControllers = [];
  int? selectedUnidadControlId;

  String formatDecimalToHours(double decimal) {
    int hours = decimal.floor();
    int minutes = ((decimal - hours) * 60).round();
    return '${hours.toString().padLeft(2, '0')}:${minutes.toString().padLeft(2, '0')}';
  }

  double parseHoursToDecimal(String hoursString) {
    final parts = hoursString.split(':');
    if (parts.length != 2) return 0.0;
    final hours = int.tryParse(parts[0]) ?? 0;
    final minutes = int.tryParse(parts[1]) ?? 0;
    return hours + (minutes / 60);
  }

  @override
  void initState() {
    super.initState();
    for (var i = 0; i < widget.trabajadores.length; i++) {
      selectedTrabajadores[i] = false;
      horasControllers.add(
        TextEditingController(
          text: formatDecimalToHours(widget.trabajadores[i].horasRegistradas),
        ),
      );
      produccionControllers.add(TextEditingController(text: '0.0'));
    }
  }

  void updateHoras(int index) {
    final trabajador = widget.trabajadores[index];
    double maxHoras = trabajador.horasRegistradas;
    String currentHoras = horasControllers[index].text;

    showDialog(
      context: context,
      builder: (BuildContext context) {
        int hours = int.parse(currentHoras.split(':')[0]);
        int minutes = int.parse(currentHoras.split(':')[1]);

        return AlertDialog(
          title: Text('Horas para ${trabajador.nombre}'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text('Máximo: ${formatDecimalToHours(maxHoras)}'),
              Row(
                children: [
                  Expanded(
                    child: TextFormField(
                      initialValue: hours.toString(),
                      keyboardType: TextInputType.number,
                      decoration: const InputDecoration(labelText: 'Horas'),
                      inputFormatters: [FilteringTextInputFormatter.digitsOnly],
                      onChanged: (value) => hours = int.tryParse(value) ?? 0,
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: TextFormField(
                      initialValue: minutes.toString(),
                      keyboardType: TextInputType.number,
                      decoration: const InputDecoration(labelText: 'Minutos'),
                      inputFormatters: [FilteringTextInputFormatter.digitsOnly],
                      onChanged: (value) => minutes = int.tryParse(value) ?? 0,
                    ),
                  ),
                ],
              ),
            ],
          ),
          actions: [
            TextButton(
              child: const Text('Cancelar'),
              onPressed: () => Navigator.pop(context),
            ),
            TextButton(
              child: const Text('Guardar'),
              onPressed: () {
                double enteredTime = hours + (minutes / 60);
                if (enteredTime <= maxHoras && enteredTime > 0) {
                  setState(() {
                    horasControllers[index].text = formatDecimalToHours(
                      enteredTime,
                    );
                  });
                  Navigator.pop(context);
                } else {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Tiempo inválido')),
                  );
                }
              },
            ),
          ],
        );
      },
    );
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
                child: Lottie.asset('assets/animations/loading.json'),
              ),
              const SizedBox(width: 16),
              const Text('Guardando...'),
            ],
          ),
        ),
      ),
    );
  }

  Future<void> enviarRegistros() async {
    if (!validarCampos()) return;

    _showLoadingDialog();

    for (var i = 0; i < widget.trabajadores.length; i++) {
      if (selectedTrabajadores[i] ?? false) {
        var horas = parseHoursToDecimal(horasControllers[i].text);
        var produccion = double.tryParse(produccionControllers[i].text) ?? 0;

        var data = {
          'holding': userInfo.holding,
          'sociedad': widget.trabajadores[i].sociedad,
          'supervisor': userInfo.idSupervisor,
          'folio': widget.folioId,
          'labor': widget.laborId,
          'unidad_control': selectedUnidadControlId,
          'trabajador': widget.trabajadores[i].id,
          'produccion': produccion,
          'horas': horas,
        };

        try {
          await apiService.post('gestion_mano_obra_persona/', data);
          loggerGlobal.d('Registro enviado: ${widget.trabajadores[i].id}');
        } catch (e) {
          loggerGlobal.e('Error: $e');
        }
      }
    }

    if (mounted) {
      Navigator.pop(context);
      _mostrarExito();
    }
  }

  bool validarCampos() {
    if (selectedUnidadControl == null) {
      _mostrarError('Seleccione una unidad de control');
      return false;
    }

    bool haySeleccionados = false;
    for (var i = 0; i < widget.trabajadores.length; i++) {
      if (selectedTrabajadores[i] ?? false) {
        haySeleccionados = true;
        var horas = parseHoursToDecimal(horasControllers[i].text);
        var produccion = double.tryParse(produccionControllers[i].text) ?? 0;

        if (horas <= 0) {
          _mostrarError('Las horas deben ser mayores a cero');
          return false;
        }
        if (produccion <= 0) {
          _mostrarError('La producción debe ser mayor a cero');
          return false;
        }
      }
    }

    if (!haySeleccionados) {
      _mostrarError('Seleccione al menos un trabajador');
      return false;
    }

    return true;
  }

  void _mostrarError(String mensaje) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(mensaje), backgroundColor: Colors.red),
    );
  }

  void _mostrarExito() {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: const Text('Éxito'),
          content: const Text('Registros guardados correctamente'),
          actions: [
            TextButton(
              child: const Text('Cerrar'),
              onPressed: () {
                Navigator.pop(context);
                navigateToScreen(context, '/Mother_Layout');
              },
            ),
          ],
        );
      },
    );
  }

  void _showUnidadControlDialog() {
    String searchQuery = '';
    List<UnidadControl> sortedUnidades = List.from(widget.unidadesControl)
      ..sort((a, b) => a.descripcion.compareTo(b.descripcion));

    showDialog(
      context: context,
      builder: (BuildContext context) {
        return StatefulBuilder(
          builder: (BuildContext context, StateSetter setStateDialog) {
            List<UnidadControl> filteredUnidades = sortedUnidades
                .where(
                  (u) =>
                      u.descripcion.toLowerCase().contains(
                        searchQuery.toLowerCase(),
                      ) ||
                      u.id.toString().contains(searchQuery),
                )
                .toList();

            return Dialog(
              insetPadding: EdgeInsets.symmetric(
                horizontal: MediaQuery.of(context).size.width * 0.05,
                vertical: MediaQuery.of(context).size.height * 0.03,
              ),
              child: Column(
                children: [
                  AppBar(
                    title: const Text(
                      "SELECCIONE UNIDAD DE CONTROL",
                      style: TextStyle(color: Colors.white),
                    ),
                    automaticallyImplyLeading: false,
                    backgroundColor: const Color.fromARGB(255, 6, 62, 107),
                  ),
                  Padding(
                    padding: const EdgeInsets.all(8.0),
                    child: TextField(
                      decoration: const InputDecoration(
                        hintText: 'Buscar...',
                        prefixIcon: Icon(Icons.search),
                      ),
                      onChanged: (value) {
                        setStateDialog(() => searchQuery = value);
                      },
                    ),
                  ),
                  Expanded(
                    child: Column(
                      children: [
                        Container(
                          padding: const EdgeInsets.symmetric(vertical: 8.0),
                          decoration: const BoxDecoration(
                            border: Border(
                              bottom: BorderSide(color: Colors.black, width: 1),
                            ),
                          ),
                          child: Row(
                            children: [
                              Expanded(
                                flex: 1,
                                child: Container(
                                  padding: const EdgeInsets.only(left: 16.0),
                                  child: const Text(
                                    'Código',
                                    style: TextStyle(
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ),
                              ),
                              Expanded(
                                flex: 2,
                                child: Container(
                                  padding: const EdgeInsets.only(left: 16.0),
                                  child: const Text(
                                    'Descripción',
                                    style: TextStyle(
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),
                        Expanded(
                          child: ListView.builder(
                            itemCount: filteredUnidades.length,
                            itemBuilder: (context, index) {
                              final unidad = filteredUnidades[index];
                              return InkWell(
                                onTap: () {
                                  setState(() {
                                    selectedUnidadControl = unidad;
                                    selectedUnidadControlId = unidad.id;
                                  });
                                  Navigator.pop(context);
                                },
                                child: Container(
                                  decoration: const BoxDecoration(
                                    border: Border(
                                      bottom: BorderSide(
                                        color: Colors.black,
                                        width: 1,
                                      ),
                                    ),
                                  ),
                                  child: Row(
                                    children: [
                                      Expanded(
                                        flex: 1,
                                        child: Padding(
                                          padding: const EdgeInsets.symmetric(
                                            vertical: 8.0,
                                            horizontal: 16.0,
                                          ),
                                          child: Text(unidad.id.toString()),
                                        ),
                                      ),
                                      Expanded(
                                        flex: 2,
                                        child: Padding(
                                          padding: const EdgeInsets.symmetric(
                                            vertical: 8.0,
                                            horizontal: 16.0,
                                          ),
                                          child: Text(unidad.descripcion),
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                              );
                            },
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            );
          },
        );
      },
    ).then((_) => setState(() {}));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SingleChildScrollView(
        padding: EdgeInsets.only(
          bottom: MediaQuery.of(context).viewInsets.bottom,
        ),
        child: Column(
          children: [
            Padding(
              padding: const EdgeInsets.all(8.0),
              child: Text(
                'Fecha: ${DateFormat('dd-MM-yyyy').format(DateTime.now())}',
                style: const TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
            _buildInfoContainer('CLIENTE', widget.cliente),
            _buildInfoContainer('LABOR', widget.labor),
            _buildSelectionContainer(
              'UNIDAD DE CONTROL',
              selectedUnidadControl?.descripcion,
              _showUnidadControlDialog,
            ),
            _buildTableHeader(),
            _buildTableBody(),
            Padding(
              padding: const EdgeInsets.only(
                bottom: 90,
                left: 30,
                right: 30,
                top: 10,
              ),
              child: ElevatedButton(
                onPressed: enviarRegistros,
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
                  "GUARDAR REGISTROS",
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInfoContainer(String label, String value) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 15),
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      decoration: BoxDecoration(
        color: Colors.grey[200],
        borderRadius: BorderRadius.circular(4),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label, style: const TextStyle(fontSize: 12, color: Colors.grey)),
          const SizedBox(height: 4),
          Text(
            value,
            style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
          ),
        ],
      ),
    );
  }

  Widget _buildSelectionContainer(
    String placeholder,
    String? value,
    VoidCallback onTap,
  ) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 15),
        margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
        decoration: BoxDecoration(
          border: Border.all(color: Colors.black),
          borderRadius: BorderRadius.circular(4),
        ),
        child: Text(
          value ?? placeholder,
          style: TextStyle(
            fontWeight: FontWeight.w600,
            fontSize: 16,
            color: value != null ? Colors.black : Colors.grey,
          ),
        ),
      ),
    );
  }

  Widget _buildTableHeader() {
    return Container(
      color: const Color.fromARGB(255, 14, 116, 67),
      child: Row(
        children: [
          _buildHeaderCell(
            Icons.person_add_alt_1,
            isIcon: true,
            onTap: _selectAll,
          ),
          _buildHeaderCell('TRABAJADOR', flex: 4),
          _buildHeaderCell('HORAS', flex: 2),
          _buildHeaderCell('PRODUCCIÓN', flex: 2),
        ],
      ),
    );
  }

  Widget _buildTableBody() {
    return ListView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      itemCount: widget.trabajadores.length,
      itemBuilder: (context, index) {
        return Row(
          children: [
            _buildTableCell(
              Checkbox(
                value: selectedTrabajadores[index] ?? false,
                onChanged: (value) {
                  setState(() => selectedTrabajadores[index] = value ?? false);
                },
              ),
              flex: 1,
            ),
            _buildTableCell(
              Text(
                widget.trabajadores[index].nombre,
                overflow: TextOverflow.ellipsis,
              ),
              flex: 4,
            ),
            _buildTableCell(
              GestureDetector(
                onTap: () => updateHoras(index),
                child: AbsorbPointer(
                  child: _buildTextField(horasControllers[index]),
                ),
              ),
              flex: 2,
            ),
            _buildTableCell(
              _buildTextField(produccionControllers[index]),
              flex: 2,
            ),
          ],
        );
      },
    );
  }

  Widget _buildTextField(
    TextEditingController controller, {
    bool enabled = true,
  }) {
    return TextField(
      controller: controller,
      decoration: InputDecoration(
        isDense: true,
        contentPadding: const EdgeInsets.symmetric(horizontal: 4, vertical: 8),
        enabled: enabled,
      ),
      enabled: enabled,
      keyboardType: const TextInputType.numberWithOptions(decimal: true),
    );
  }

  void _selectAll() {
    setState(() {
      bool allSelected = selectedTrabajadores.values.every((s) => s);
      for (var i = 0; i < widget.trabajadores.length; i++) {
        selectedTrabajadores[i] = !allSelected;
      }
    });
  }

  Widget _buildHeaderCell(
    dynamic content, {
    int flex = 1,
    bool isIcon = false,
    VoidCallback? onTap,
  }) {
    return Expanded(
      flex: flex,
      child: InkWell(
        onTap: onTap,
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 8.0, horizontal: 4.0),
          decoration: const BoxDecoration(
            border: Border(right: BorderSide(color: Colors.white)),
          ),
          child: isIcon
              ? Icon(content as IconData, color: Colors.white)
              : Text(
                  content as String,
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                  textAlign: TextAlign.center,
                ),
        ),
      ),
    );
  }

  Widget _buildTableCell(Widget child, {int flex = 1}) {
    return Expanded(
      flex: flex,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 4.0, vertical: 8.0),
        decoration: BoxDecoration(
          border: Border(right: BorderSide(color: Colors.grey[300]!)),
        ),
        child: child,
      ),
    );
  }

  @override
  void dispose() {
    for (var c in horasControllers) c.dispose();
    for (var c in produccionControllers) c.dispose();
    super.dispose();
  }
}

class Trabajador {
  final String nombre;
  final int id;
  final double horasRegistradas;
  final String estado;
  final int? fundo;
  final int? sociedad;
  final double produccion;

  Trabajador({
    required this.nombre,
    required this.id,
    required this.horasRegistradas,
    required this.estado,
    required this.fundo,
    required this.sociedad,
    required this.produccion,
  });
}

class UnidadControl {
  final String descripcion;
  final int id;

  UnidadControl({required this.descripcion, required this.id});

  factory UnidadControl.fromJson(Map<String, dynamic> json) {
    return UnidadControl(
      descripcion: json['descripcion'], // ← El backend envía 'descripcion'
      id: json['id'],
    );
  }
}
