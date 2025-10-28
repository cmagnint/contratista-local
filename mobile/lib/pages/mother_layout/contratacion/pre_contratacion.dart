import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:contratista/utils/globals.dart';
import 'package:contratista/services/contratista_api_service.dart';

class PreContratacionScreen extends StatefulWidget {
  final List<Map<String, dynamic>> folios;
  final Function(Map<String, String?>) onContinue;

  const PreContratacionScreen({
    super.key,
    required this.folios,
    required this.onContinue,
  });

  @override
  PreContratacionScreenState createState() => PreContratacionScreenState();
}

class PreContratacionScreenState extends State<PreContratacionScreen> {
  // Variables existentes
  String? _selectedFolio;
  String? _selectedFundo;
  String? _selectedLabor;
  String? _selectedTransportista;
  String? _selectedVehiculo;
  String? _selectedCasa;
  String? _selectedSupervisor;
  String? _selectedJefeCuadrilla;
  String? _selectedHorario; // ✅ NUEVO

  // Listas existentes
  List<Map<String, dynamic>> _fundos = [];
  List<Map<String, dynamic>> _labores = [];
  List<Map<String, dynamic>> _transportistas = [];
  List<Map<String, dynamic>> _vehiculos = [];
  List<Map<String, dynamic>> _horarios = []; // ✅ NUEVO
  List<String> _casas = [];
  List<Map<String, dynamic>> _supervisores = [];
  List<Map<String, dynamic>> _jefesCuadrilla = [];

  Map<String, int> _casaMap = {};

  @override
  void initState() {
    super.initState();
    _fetchCasas();
    _fetchSupervisores();
  }

  void _updateSelections() {
    if (_selectedFolio != null) {
      final folio = widget.folios.firstWhere(
        (folio) => folio['id'].toString() == _selectedFolio,
      );

      setState(() {
        _fundos = folio['fundos'] != null
            ? List<Map<String, dynamic>>.from(folio['fundos'])
            : <Map<String, dynamic>>[];

        _labores = folio['labores'] != null
            ? List<Map<String, dynamic>>.from(folio['labores'])
            : <Map<String, dynamic>>[];

        _transportistas = folio['transportistas'] != null
            ? List<Map<String, dynamic>>.from(folio['transportistas'])
            : <Map<String, dynamic>>[];

        _horarios =
            folio['horarios'] !=
                null // ✅ NUEVO
            ? List<Map<String, dynamic>>.from(folio['horarios'])
            : <Map<String, dynamic>>[];

        // Reset selections
        _selectedFundo = null;
        _selectedLabor = null;
        _selectedTransportista = null;
        _selectedVehiculo = null;
        _selectedHorario = null; // ✅ NUEVO

        _vehiculos = [];

        // Auto-selección
        if (_fundos.length == 1) {
          _selectedFundo = _fundos[0]['id'].toString();
        }

        if (_labores.length == 1) {
          _selectedLabor = _labores[0]['id'].toString();
        }

        if (_transportistas.length == 1) {
          _selectedTransportista = _transportistas[0]['id'].toString();
          _updateVehiculos();
        }

        if (_horarios.length == 1) {
          // ✅ NUEVO
          _selectedHorario = _horarios[0]['id'].toString();
        }
      });
    } else {
      setState(() {
        _fundos = [];
        _labores = [];
        _transportistas = [];
        _vehiculos = [];
        _horarios = []; // ✅ NUEVO
        _selectedFundo = null;
        _selectedLabor = null;
        _selectedTransportista = null;
        _selectedVehiculo = null;
        _selectedHorario = null; // ✅ NUEVO
        _selectedCasa = null;
      });
    }
  }

  void _updateVehiculos() {
    if (_selectedTransportista != null) {
      final transportista = _transportistas.firstWhere(
        (t) => t['id'].toString() == _selectedTransportista,
      );
      setState(() {
        _vehiculos = transportista['vehiculos'] != null
            ? List<Map<String, dynamic>>.from(transportista['vehiculos'])
            : <Map<String, dynamic>>[];
        _selectedVehiculo = null;

        if (_vehiculos.length == 1) {
          _selectedVehiculo = _vehiculos[0]['id'].toString();
        }
      });
    } else {
      setState(() {
        _vehiculos = [];
        _selectedVehiculo = null;
      });
    }
  }

  Future<void> _fetchCasas() async {
    ApiService apiService = ApiService();
    String? holding = await storage.read(key: 'holding');
    final response = await apiService.get(
      'api_casas_trabajadores/?holding=$holding',
    );
    if (response.statusCode == 200) {
      final List<dynamic> responseData = jsonDecode(response.body);
      final List<String> casasData = responseData
          .map((casa) => casa['nombre'].toString())
          .toList();
      setState(() {
        _casas = casasData;
        _casaMap = Map.fromIterables(
          _casas,
          responseData.map((casa) => casa['id'] as int).toList(),
        );

        if (_casas.length == 1) {
          _selectedCasa = _casas[0];
        }
      });
    } else {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              'Error al cargar las casas: ${response.reasonPhrase}',
            ),
          ),
        );
      }
    }
  }

  Future<void> _fetchSupervisores() async {
    ApiService apiService = ApiService();
    String? holding = await storage.read(key: 'holding');
    final response = await apiService.get('api_supervisores/$holding/');

    if (response.statusCode == 200) {
      final List<dynamic> responseData = jsonDecode(response.body);
      setState(() {
        _supervisores = List<Map<String, dynamic>>.from(responseData);

        if (_supervisores.length == 1) {
          _selectedSupervisor = _supervisores[0]['id'].toString();
          _fetchJefesCuadrilla(_selectedSupervisor!);
        }
      });
    } else {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              'Error al cargar supervisores: ${response.reasonPhrase}',
            ),
          ),
        );
      }
    }
  }

  Future<void> _fetchJefesCuadrilla(String supervisorId) async {
    try {
      ApiService apiService = ApiService();
      String? holding = await storage.read(key: 'holding');
      final response = await apiService.get(
        'api_jefes_cuadrilla/$holding/?supervisor=$supervisorId',
        allowNotFound: true,
      );

      if (response.statusCode == 200) {
        final List<dynamic> responseData = jsonDecode(response.body);
        setState(() {
          _jefesCuadrilla = List<Map<String, dynamic>>.from(responseData);
          _selectedJefeCuadrilla = null;

          if (_jefesCuadrilla.length == 1) {
            _selectedJefeCuadrilla = _jefesCuadrilla[0]['id'].toString();
          }
        });
      } else {
        setState(() {
          _jefesCuadrilla = [];
          _selectedJefeCuadrilla = null;
        });
      }
    } catch (e) {
      setState(() {
        _jefesCuadrilla = [];
        _selectedJefeCuadrilla = null;
      });
    }
  }

  void _navigateToContratacionScreen() {
    if (_selectedFolio != null &&
        _selectedFundo != null &&
        _selectedLabor != null &&
        _selectedTransportista != null &&
        _selectedVehiculo != null &&
        _selectedCasa != null &&
        _selectedSupervisor != null &&
        _selectedHorario != null) {
      // ✅ NUEVO - Validación obligatoria
      widget.onContinue({
        'folio': _selectedFolio,
        'fundo': _selectedFundo,
        'labor': _selectedLabor,
        'transportista': _selectedTransportista,
        'vehiculo': _selectedVehiculo,
        'casa': _casaMap[_selectedCasa].toString(),
        'supervisor': _selectedSupervisor,
        'jefe_cuadrilla': _selectedJefeCuadrilla,
        'horario': _selectedHorario, // ✅ NUEVO
      });
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Por favor, complete todos los campos obligatorios.'),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Pre-Contratación')),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Dropdown de Folio
              DropdownButton<String>(
                value: _selectedFolio,
                hint: const Text('Selecciona un folio'),
                isExpanded: true,
                items: widget.folios.map((folio) {
                  return DropdownMenuItem<String>(
                    value: folio['id'].toString(),
                    child: Text(
                      'Folio: ${folio['id']} - ${folio['nombre_cliente']}',
                    ),
                  );
                }).toList(),
                onChanged: (String? newValue) {
                  setState(() {
                    _selectedFolio = newValue;
                    _updateSelections();
                  });
                },
              ),
              const SizedBox(height: 30),

              // Dropdown de Fundo
              DropdownButton<String>(
                value: _selectedFundo,
                hint: const Text('Seleccione Fundo'),
                isExpanded: true,
                items: _fundos.map((fundo) {
                  return DropdownMenuItem<String>(
                    value: fundo['id'].toString(),
                    child: Text(fundo['nombre']),
                  );
                }).toList(),
                onChanged: (String? newValue) {
                  setState(() {
                    _selectedFundo = newValue;
                  });
                },
              ),
              const SizedBox(height: 30),

              // Dropdown de Labor
              DropdownButton<String>(
                value: _selectedLabor,
                hint: const Text('Seleccione Labor'),
                isExpanded: true,
                items: _labores.map((labor) {
                  return DropdownMenuItem<String>(
                    value: labor['id'].toString(),
                    child: Text(labor['nombre']),
                  );
                }).toList(),
                onChanged: (String? newValue) {
                  setState(() {
                    _selectedLabor = newValue;
                  });
                },
              ),
              const SizedBox(height: 30),

              // ✅ NUEVO - Dropdown de Horario
              DropdownButton<String>(
                value: _selectedHorario,
                hint: const Text('Seleccione Horario (Obligatorio)'),
                isExpanded: true,
                items: _horarios.map((horario) {
                  return DropdownMenuItem<String>(
                    value: horario['id'].toString(),
                    child: Text(
                      '${horario['nombre']} (${horario['jornada']} hrs)',
                    ),
                  );
                }).toList(),
                onChanged: (String? newValue) {
                  setState(() {
                    _selectedHorario = newValue;
                  });
                },
              ),
              const SizedBox(height: 30),

              // Dropdown de Transportista
              DropdownButton<String>(
                value: _selectedTransportista,
                hint: const Text('Seleccione Empresa de Transporte'),
                isExpanded: true,
                items: _transportistas.map((transportistas) {
                  return DropdownMenuItem<String>(
                    value: transportistas['id'].toString(),
                    child: Text(transportistas['nombre']),
                  );
                }).toList(),
                onChanged: (String? newValue) {
                  setState(() {
                    _selectedTransportista = newValue;
                    _updateVehiculos();
                  });
                },
              ),
              const SizedBox(height: 30),

              // Dropdown de Vehículo
              DropdownButton<String>(
                value: _selectedVehiculo,
                hint: const Text('Seleccione Vehículo'),
                isExpanded: true,
                items: _vehiculos.map((vehiculos) {
                  return DropdownMenuItem<String>(
                    value: vehiculos['id'].toString(),
                    child: Text(
                      vehiculos['patente'] ??
                          vehiculos['modelo'] ??
                          'Sin nombre',
                    ),
                  );
                }).toList(),
                onChanged: (String? newValue) {
                  setState(() {
                    _selectedVehiculo = newValue;
                  });
                },
              ),
              const SizedBox(height: 30),

              // Dropdown de Casa
              DropdownButton<String>(
                value: _selectedCasa,
                hint: const Text('Seleccione Casa'),
                isExpanded: true,
                items: _casas.map((casa) {
                  return DropdownMenuItem<String>(
                    value: casa,
                    child: Text(casa),
                  );
                }).toList(),
                onChanged: (String? newValue) {
                  setState(() {
                    _selectedCasa = newValue;
                  });
                },
              ),
              const SizedBox(height: 30),

              // Dropdown de Supervisor
              DropdownButton<String>(
                value: _selectedSupervisor,
                hint: const Text('Seleccione Supervisor (Obligatorio)'),
                isExpanded: true,
                items: _supervisores.map((supervisor) {
                  return DropdownMenuItem<String>(
                    value: supervisor['id'].toString(),
                    child: Text(
                      '${supervisor['usuario_nombre']} - ${supervisor['usuario_rut']}',
                    ),
                  );
                }).toList(),
                onChanged: (String? newValue) {
                  setState(() {
                    _selectedSupervisor = newValue;
                    if (newValue != null) {
                      _fetchJefesCuadrilla(newValue);
                    } else {
                      _jefesCuadrilla = [];
                      _selectedJefeCuadrilla = null;
                    }
                  });
                },
              ),
              const SizedBox(height: 30),

              // Dropdown de Jefe de Cuadrilla
              if (_selectedSupervisor != null) ...[
                DropdownButton<String>(
                  value: _selectedJefeCuadrilla,
                  hint: Text(
                    _jefesCuadrilla.isEmpty
                        ? 'No hay jefes de cuadrilla disponibles'
                        : 'Seleccione Jefe de Cuadrilla (Opcional)',
                    style: TextStyle(
                      color: _jefesCuadrilla.isEmpty ? Colors.grey : null,
                      fontSize: _jefesCuadrilla.isEmpty ? 14 : null,
                    ),
                  ),
                  isExpanded: true,
                  items: _jefesCuadrilla.isEmpty
                      ? [
                          const DropdownMenuItem<String>(
                            value: null,
                            enabled: false,
                            child: Text(
                              'Sin jefes de cuadrilla registrados',
                              style: TextStyle(
                                color: Colors.grey,
                                fontStyle: FontStyle.italic,
                              ),
                            ),
                          ),
                        ]
                      : [
                          const DropdownMenuItem<String>(
                            value: '',
                            child: Text('Sin Jefe de Cuadrilla'),
                          ),
                          ..._jefesCuadrilla.map((jefe) {
                            return DropdownMenuItem<String>(
                              value: jefe['id'].toString(),
                              child: Text(
                                '${jefe['usuario_nombre']} - ${jefe['usuario_rut']}',
                              ),
                            );
                          }),
                        ],
                  onChanged: _jefesCuadrilla.isEmpty
                      ? null
                      : (String? newValue) {
                          setState(() {
                            _selectedJefeCuadrilla = newValue == ''
                                ? null
                                : newValue;
                          });
                        },
                ),
                const SizedBox(height: 30),
              ],

              // Botón de Continuar
              Padding(
                padding: const EdgeInsets.only(bottom: 85.0),
                child: ElevatedButton(
                  onPressed: _navigateToContratacionScreen,
                  child: const Text('Continuar'),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
