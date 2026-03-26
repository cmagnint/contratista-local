// pre_contratacion.dart
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
  String? _selectedSociedad;
  List<Map<String, dynamic>> _sociedadesDisponibles = [];

  String? _selectedFolio;
  String? _selectedFundo;
  String? _selectedLabor;
  String? _selectedTransportista;
  String? _selectedVehiculo;
  String? _selectedCasa;
  String? _selectedSupervisor;
  String? _selectedHorario;
  String? _selectedArea;
  String? _selectedCargo;

  List<Map<String, dynamic>> _fundos = [];
  List<Map<String, dynamic>> _labores = [];
  List<Map<String, dynamic>> _transportistas = [];
  List<Map<String, dynamic>> _vehiculos = [];
  List<Map<String, dynamic>> _horarios = [];
  List<String> _casas = [];
  List<Map<String, dynamic>> _supervisores = [];
  List<Map<String, dynamic>> _areas = [];
  List<Map<String, dynamic>> _cargos = [];
  bool _isLoadingSociedades = true;

  Map<String, int> _casaMap = {};

  @override
  void initState() {
    super.initState();
    _loadSociedades();
    _fetchCasas();
    _fetchSupervisores();
    _fetchAreas();
  }

  Future<void> _loadSociedades() async {
    try {
      setState(() {
        _isLoadingSociedades = true;
      });

      loggerGlobal.d('=== CARGANDO SOCIEDADES ===');
      loggerGlobal.d('Sociedades en userInfo: ${userInfo.sociedades}');

      if (userInfo.sociedades.isEmpty) {
        loggerGlobal.w('No hay sociedades disponibles para el usuario');
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('No hay sociedades disponibles para este usuario'),
            ),
          );
        }
        setState(() {
          _isLoadingSociedades = false;
        });
        return;
      }

      setState(() {
        _sociedadesDisponibles = userInfo.sociedades;
        _isLoadingSociedades = false;
      });

      loggerGlobal.d(
        'Total sociedades cargadas: ${_sociedadesDisponibles.length}',
      );

      if (_sociedadesDisponibles.length == 1) {
        setState(() {
          _selectedSociedad = _sociedadesDisponibles[0]['id'].toString();
          userInfo.sociedadSeleccionada = _selectedSociedad!;
        });
        loggerGlobal.d('Auto-seleccionada única sociedad: $_selectedSociedad');
      }
    } catch (e) {
      loggerGlobal.e('Error cargando sociedades: $e');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error al cargar sociedades: $e')),
        );
      }
      setState(() {
        _isLoadingSociedades = false;
      });
    }
  }

  Future<void> _fetchAreas() async {
    try {
      ApiService apiService = ApiService();
      String? holding = await storage.read(key: 'holding');
      final response = await apiService.get(
        'api_areas_administracion/?holding=$holding',
      );

      if (response.statusCode == 200) {
        final List<dynamic> responseData = jsonDecode(response.body);
        setState(() {
          _areas = List<Map<String, dynamic>>.from(responseData);

          final operaciones = _areas
              .where(
                (a) => a['nombre'].toString().toUpperCase() == 'OPERACIONES',
              )
              .toList();
          if (operaciones.isNotEmpty) {
            _selectedArea = operaciones[0]['id'].toString();
          } else if (_areas.length == 1) {
            _selectedArea = _areas[0]['id'].toString();
          }
          if (_selectedArea != null) {
            _fetchCargos(_selectedArea!);
          }
        });
        loggerGlobal.d('Áreas cargadas: ${_areas.length}');
      } else {
        loggerGlobal.e('Error al cargar áreas: ${response.statusCode}');
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Error al cargar áreas: ${response.reasonPhrase}'),
            ),
          );
        }
      }
    } catch (e) {
      loggerGlobal.e('Error en _fetchAreas: $e');
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text('Error al cargar áreas: $e')));
      }
    }
  }

  Future<void> _fetchCargos(String areaId) async {
    try {
      ApiService apiService = ApiService();
      String? holding = await storage.read(key: 'holding');
      final response = await apiService.get(
        'api_cargos_administracion/?holding=$holding',
      );

      if (response.statusCode == 200) {
        final List<dynamic> responseData = jsonDecode(response.body);
        final List<Map<String, dynamic>> allCargos =
            List<Map<String, dynamic>>.from(responseData);

        setState(() {
          _cargos = allCargos
              .where((cargo) => cargo['area'].toString() == areaId)
              .toList();
          _selectedCargo = null;

          final temporero = _cargos
              .where((c) => c['nombre'].toString().toUpperCase() == 'TEMPORERO')
              .toList();
          if (temporero.isNotEmpty) {
            _selectedCargo = temporero[0]['id'].toString();
          } else if (_cargos.length == 1) {
            _selectedCargo = _cargos[0]['id'].toString();
          }
        });
        loggerGlobal.d('Cargos cargados para área $areaId: ${_cargos.length}');
      } else {
        loggerGlobal.e('Error al cargar cargos: ${response.statusCode}');
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Error al cargar cargos: ${response.reasonPhrase}'),
            ),
          );
        }
      }
    } catch (e) {
      loggerGlobal.e('Error en _fetchCargos: $e');
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text('Error al cargar cargos: $e')));
      }
    }
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

        _horarios = folio['horarios'] != null
            ? List<Map<String, dynamic>>.from(folio['horarios'])
            : <Map<String, dynamic>>[];

        _selectedFundo = null;
        _selectedLabor = null;
        _selectedTransportista = null;
        _selectedVehiculo = null;
        _selectedHorario = null;

        _vehiculos = [];

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
          _selectedHorario = _horarios[0]['id'].toString();
        }
      });
    } else {
      setState(() {
        _fundos = [];
        _labores = [];
        _transportistas = [];
        _vehiculos = [];
        _horarios = [];
        _selectedFundo = null;
        _selectedLabor = null;
        _selectedTransportista = null;
        _selectedVehiculo = null;
        _selectedHorario = null;
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

  void _navigateToContratacionScreen() {
    if (_selectedSociedad == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Por favor, seleccione una sociedad')),
      );
      return;
    }

    if (_selectedArea == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Por favor, seleccione un área')),
      );
      return;
    }

    if (_selectedCargo == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Por favor, seleccione un cargo')),
      );
      return;
    }

    if (_selectedFolio != null &&
        _selectedFundo != null &&
        _selectedLabor != null &&
        _selectedTransportista != null &&
        _selectedVehiculo != null &&
        _selectedCasa != null &&
        _selectedHorario != null &&
        _selectedSupervisor != null) {
      userInfo.sociedadSeleccionada = _selectedSociedad!;

      loggerGlobal.d('=== DATOS DE PRE-CONTRATACIÓN ===');
      loggerGlobal.d('Sociedad seleccionada: $_selectedSociedad');
      loggerGlobal.d('Área seleccionada: $_selectedArea');
      loggerGlobal.d('Cargo seleccionado: $_selectedCargo');

      widget.onContinue({
        'sociedad': _selectedSociedad,
        'folio': _selectedFolio,
        'fundo': _selectedFundo,
        'labor': _selectedLabor,
        'transportista': _selectedTransportista,
        'vehiculo': _selectedVehiculo,
        'casa': _casaMap[_selectedCasa].toString(),
        'supervisor': _selectedSupervisor,
        'horario': _selectedHorario,
        'area': _selectedArea,
        'cargo': _selectedCargo,
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
              const Text(
                'Sociedad *',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: Colors.black87,
                ),
              ),
              const SizedBox(height: 8),
              _isLoadingSociedades
                  ? const Center(
                      child: Padding(
                        padding: EdgeInsets.all(16.0),
                        child: CircularProgressIndicator(),
                      ),
                    )
                  : DropdownButton<String>(
                      value: _selectedSociedad,
                      hint: const Text('Seleccione una sociedad (Obligatorio)'),
                      isExpanded: true,
                      items: _sociedadesDisponibles.map((sociedad) {
                        return DropdownMenuItem<String>(
                          value: sociedad['id']?.toString(),
                          child: Text(
                            (sociedad['rol_sociedad']?.toString().isNotEmpty ??
                                    false)
                                ? '${sociedad['nombre']} '
                                : sociedad['nombre']?.toString() ??
                                      'Sociedad sin nombre',
                            style: const TextStyle(fontSize: 14),
                          ),
                        );
                      }).toList(),
                      onChanged: (String? newValue) {
                        setState(() {
                          _selectedSociedad = newValue;
                          if (newValue != null) {
                            userInfo.sociedadSeleccionada = newValue;
                            final sociedadSeleccionada = _sociedadesDisponibles
                                .firstWhere(
                                  (s) => s['id']?.toString() == newValue,
                                );
                            loggerGlobal.d(
                              'Sociedad seleccionada: ${sociedadSeleccionada['nombre']} (ID: $newValue)',
                            );
                          }
                        });
                      },
                    ),
              const SizedBox(height: 30),

              const Text(
                'Área *',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: Colors.black87,
                ),
              ),
              const SizedBox(height: 8),
              DropdownButton<String>(
                value: _selectedArea,
                hint: const Text('Seleccione un área'),
                isExpanded: true,
                items: _areas.map((area) {
                  return DropdownMenuItem<String>(
                    value: area['id'].toString(),
                    child: Text(area['nombre']),
                  );
                }).toList(),
                onChanged: (String? newValue) {
                  setState(() {
                    _selectedArea = newValue;
                    _selectedCargo = null;
                    _cargos = [];
                    if (newValue != null) {
                      _fetchCargos(newValue);
                    }
                  });
                },
              ),
              const SizedBox(height: 30),

              const Text(
                'Cargo *',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: Colors.black87,
                ),
              ),
              const SizedBox(height: 8),
              DropdownButton<String>(
                value: _selectedCargo,
                hint: Text(
                  _selectedArea == null
                      ? 'Primero seleccione un área'
                      : _cargos.isEmpty
                      ? 'No hay cargos disponibles'
                      : 'Seleccione un cargo',
                  style: TextStyle(
                    color: _selectedArea == null || _cargos.isEmpty
                        ? Colors.grey
                        : null,
                  ),
                ),
                isExpanded: true,
                items: _cargos.isEmpty
                    ? null
                    : _cargos.map((cargo) {
                        return DropdownMenuItem<String>(
                          value: cargo['id'].toString(),
                          child: Text(cargo['nombre']),
                        );
                      }).toList(),
                onChanged: _cargos.isEmpty
                    ? null
                    : (String? newValue) {
                        setState(() {
                          _selectedCargo = newValue;
                        });
                      },
              ),
              const SizedBox(height: 30),

              const Text(
                'Folio Comercial *',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: Colors.black87,
                ),
              ),
              const SizedBox(height: 8),
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

              const Text(
                'Fundo *',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: Colors.black87,
                ),
              ),
              const SizedBox(height: 8),
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

              const Text(
                'Labor *',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: Colors.black87,
                ),
              ),
              const SizedBox(height: 8),
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

              const Text(
                'Horario *',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: Colors.black87,
                ),
              ),
              const SizedBox(height: 8),
              DropdownButton<String>(
                value: _selectedHorario,
                hint: const Text('Seleccione Horario'),
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

              const Text(
                'Empresa de Transporte *',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: Colors.black87,
                ),
              ),
              const SizedBox(height: 8),
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

              const Text(
                'Vehículo *',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: Colors.black87,
                ),
              ),
              const SizedBox(height: 8),
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

              const Text(
                'Casa *',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: Colors.black87,
                ),
              ),
              const SizedBox(height: 8),
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

              const Text(
                'Supervisor *',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: Colors.black87,
                ),
              ),
              const SizedBox(height: 8),
              DropdownButton<String>(
                value: _selectedSupervisor,
                hint: const Text('Seleccione Supervisor'),
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
                  });
                },
              ),
              const SizedBox(height: 30),

              if (_selectedSupervisor != null) ...[
                const Text(
                  'Jefe de Cuadrilla (Opcional)',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: Colors.black87,
                  ),
                ),
                const SizedBox(height: 8),

                const SizedBox(height: 30),
              ],

              Padding(
                padding: const EdgeInsets.only(bottom: 85.0),
                child: ElevatedButton(
                  onPressed: _navigateToContratacionScreen,
                  style: ElevatedButton.styleFrom(
                    minimumSize: const Size(double.infinity, 50),
                  ),
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
