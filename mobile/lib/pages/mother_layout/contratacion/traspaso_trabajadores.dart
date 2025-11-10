import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:contratista/services/contratista_api_service.dart';
import 'package:contratista/utils/globals.dart';

class TraspasoTrabajadoresScreen extends StatefulWidget {
  const TraspasoTrabajadoresScreen({super.key});

  @override
  TraspasoTrabajadoresScreenState createState() =>
      TraspasoTrabajadoresScreenState();
}

class TraspasoTrabajadoresScreenState
    extends State<TraspasoTrabajadoresScreen> {
  final ApiService apiService = ApiService();

  bool _isLoading = true;
  bool _isSupervisor = false;
  bool _isJefeCuadrilla = false;

  List<dynamic> _misTrabajadores = [];
  List<dynamic> _misJefesCuadrilla = [];
  List<dynamic> _otrosSupervisores = [];
  List<dynamic> _otrosJefesCuadrilla = [];
  List<dynamic> _solicitudesPendientes = [];

  Set<int> _trabajadoresSeleccionados = {};
  String? _destinoSeleccionado;
  String? _tipoDestino;

  @override
  void initState() {
    super.initState();
    _cargarDatos();
  }

  Future<void> _cargarDatos() async {
    setState(() => _isLoading = true);

    try {
      String? holding = await storage.read(key: 'holding');

      _isSupervisor =
          userInfo.idSupervisor != null && userInfo.idSupervisor! > 0;
      _isJefeCuadrilla =
          userInfo.idJefeCuadrilla != null && userInfo.idJefeCuadrilla! > 0;

      String endpoint;
      Map<String, String> params = {'holding': holding!};

      if (_isSupervisor) {
        endpoint = 'traspaso_trabajadores/';
        params['supervisor_id'] = userInfo.idSupervisor.toString();
      } else if (_isJefeCuadrilla) {
        endpoint = 'traspaso_trabajadores/';
        params['jefe_cuadrilla_id'] = userInfo.idJefeCuadrilla.toString();
      } else {
        throw Exception(
          'Usuario no tiene perfil de Supervisor o Jefe de Cuadrilla',
        );
      }

      final queryString = params.entries
          .map((e) => '${e.key}=${e.value}')
          .join('&');
      final response = await apiService.get('$endpoint?$queryString');

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);

        setState(() {
          _misTrabajadores = data['mis_trabajadores'] ?? [];
          _misJefesCuadrilla = data['mis_jefes_cuadrilla'] ?? [];
          _otrosSupervisores = data['otros_supervisores'] ?? [];
          _otrosJefesCuadrilla = data['otros_jefes_cuadrilla'] ?? [];
          _solicitudesPendientes = data['solicitudes_pendientes'] ?? [];
          _isLoading = false;
        });
      } else {
        throw Exception('Error al cargar datos: ${response.statusCode}');
      }
    } catch (e) {
      if (mounted) {
        _mostrarError('Error al cargar datos: $e');
      }
      setState(() => _isLoading = false);
    }
  }

  void _mostrarError(String mensaje) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Error'),
        content: Text(mensaje),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }

  void _mostrarExito(String mensaje) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(mensaje),
        backgroundColor: Colors.green,
        duration: const Duration(seconds: 3),
      ),
    );
  }

  Future<void> _realizarTraspaso() async {
    if (_trabajadoresSeleccionados.isEmpty) {
      _mostrarError('Debe seleccionar al menos un trabajador');
      return;
    }

    if (_destinoSeleccionado == null) {
      _mostrarError('Debe seleccionar un destino');
      return;
    }

    try {
      showDialog(
        context: context,
        barrierDismissible: false,
        builder: (context) => const Center(child: CircularProgressIndicator()),
      );

      String? holding = await storage.read(key: 'holding');

      Map<String, dynamic> requestData = {
        'holding': holding,
        'trabajadores_ids': _trabajadoresSeleccionados.toList(),
      };

      // Caso especial: recuperar al supervisor
      if (_destinoSeleccionado == 'recuperar_supervisor') {
        requestData['recuperar'] = true;
        requestData['supervisor_id'] = userInfo.idSupervisor;
      } else {
        // Traspaso normal
        final destinoId = int.parse(_destinoSeleccionado!.split('_')[1]);
        requestData['destino_id'] = destinoId;
        requestData['tipo_destino'] = _tipoDestino;

        if (_isSupervisor) {
          requestData['supervisor_id'] = userInfo.idSupervisor;
        } else if (_isJefeCuadrilla) {
          requestData['jefe_cuadrilla_id'] = userInfo.idJefeCuadrilla;
        }
      }

      final response = await apiService.post(
        'traspaso_trabajadores/',
        requestData,
      );

      if (mounted) Navigator.pop(context);

      if (response.statusCode == 200 || response.statusCode == 201) {
        final data = jsonDecode(response.body);
        _mostrarExito(data['mensaje'] ?? 'Operación exitosa');

        setState(() {
          _trabajadoresSeleccionados.clear();
          _destinoSeleccionado = null;
          _tipoDestino = null;
        });

        await _cargarDatos();
      } else {
        final data = jsonDecode(response.body);
        _mostrarError(data['error'] ?? 'Error en la operación');
      }
    } catch (e) {
      if (mounted) Navigator.pop(context);
      _mostrarError('Error: $e');
    }
  }

  Future<void> _responderSolicitud(int solicitudId, bool aprobar) async {
    try {
      showDialog(
        context: context,
        barrierDismissible: false,
        builder: (context) => const Center(child: CircularProgressIndicator()),
      );

      final response = await apiService.post('responder_traspaso/', {
        'solicitud_id': solicitudId,
        'aprobar': aprobar,
        'supervisor_id': userInfo.idSupervisor,
      });

      if (mounted) Navigator.pop(context);

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        _mostrarExito(data['mensaje'] ?? 'Solicitud procesada');
        await _cargarDatos();
      } else {
        final data = jsonDecode(response.body);
        _mostrarError(data['error'] ?? 'Error al procesar');
      }
    } catch (e) {
      if (mounted) Navigator.pop(context);
      _mostrarError('Error: $e');
    }
  }

  Widget _buildTrabajadorItem(dynamic trabajador) {
    final trabajadorId = trabajador['id'];
    final isSelected = _trabajadoresSeleccionados.contains(trabajadorId);

    return CheckboxListTile(
      title: Text(
        trabajador['nombre'],
        style: const TextStyle(fontWeight: FontWeight.bold),
      ),
      subtitle: Text('RUT: ${trabajador['rut']}'),
      value: isSelected,
      onChanged: (bool? value) {
        setState(() {
          if (value == true) {
            _trabajadoresSeleccionados.add(trabajadorId);
          } else {
            _trabajadoresSeleccionados.remove(trabajadorId);
          }
        });
      },
      activeColor: const Color(0xFF00B894),
    );
  }

  Widget _buildJefesCuadrillaDisponibles() {
    if (_misJefesCuadrilla.isEmpty) {
      return const SizedBox.shrink();
    }

    return Card(
      elevation: 2,
      margin: const EdgeInsets.all(8),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.groups, color: Color(0xFF00B894)),
                const SizedBox(width: 8),
                Text(
                  'Jefes de Cuadrilla (${_misJefesCuadrilla.length})',
                  style: const TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const Divider(height: 24),
            ..._misJefesCuadrilla.map((jefe) {
              final trabajadores = jefe['trabajadores'] ?? [];

              return Card(
                elevation: 1,
                margin: const EdgeInsets.symmetric(vertical: 4),
                child: Theme(
                  data: Theme.of(
                    context,
                  ).copyWith(dividerColor: Colors.transparent),
                  child: ExpansionTile(
                    leading: CircleAvatar(
                      backgroundColor: const Color(0xFF00B894),
                      child: Text(
                        '${trabajadores.length}',
                        style: const TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                    title: Text(
                      jefe['nombre'],
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                    subtitle: Text('RUT: ${jefe['rut']}'),
                    children: trabajadores.isEmpty
                        ? [
                            const Padding(
                              padding: EdgeInsets.all(16),
                              child: Text(
                                'Sin trabajadores',
                                style: TextStyle(color: Colors.grey),
                              ),
                            ),
                          ]
                        : trabajadores.map<Widget>((t) {
                            return _buildTrabajadorItem(t);
                          }).toList(),
                  ),
                ),
              );
            }).toList(),
          ],
        ),
      ),
    );
  }

  Widget _buildDestinoSelector() {
    List<DropdownMenuItem<String>> items = [];

    if (_isSupervisor) {
      items.add(
        const DropdownMenuItem(
          value: 'recuperar_supervisor',
          child: Text('🔙 Recuperar para mí'),
        ),
      );

      for (var jefe in _misJefesCuadrilla) {
        items.add(
          DropdownMenuItem(
            value: 'jefe_${jefe['id']}',
            child: Text('Jefe: ${jefe['nombre']}'),
          ),
        );
      }

      for (var supervisor in _otrosSupervisores) {
        items.add(
          DropdownMenuItem(
            value: 'supervisor_${supervisor['id']}',
            child: Text('Supervisor: ${supervisor['nombre']}'),
          ),
        );
      }
    } else if (_isJefeCuadrilla) {
      if (_misTrabajadores.isNotEmpty) {
        final supervisorId = _misTrabajadores[0]['supervisor_id'];
        final supervisorNombre = _misTrabajadores[0]['supervisor_nombre'];
        items.add(
          DropdownMenuItem(
            value: 'supervisor_$supervisorId',
            child: Text('Devolver: $supervisorNombre'),
          ),
        );
      }

      for (var jefe in _otrosJefesCuadrilla) {
        items.add(
          DropdownMenuItem(
            value: 'jefe_${jefe['id']}',
            child: Text('Jefe: ${jefe['nombre']}'),
          ),
        );
      }
    }

    return Card(
      elevation: 2,
      margin: const EdgeInsets.all(8),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Destino',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            DropdownButtonFormField<String>(
              decoration: const InputDecoration(
                border: OutlineInputBorder(),
                labelText: 'Seleccionar',
              ),
              value: _destinoSeleccionado,
              items: items,
              onChanged: (value) {
                setState(() {
                  _destinoSeleccionado = value;
                  if (value != null) {
                    if (value == 'recuperar_supervisor') {
                      _tipoDestino = 'recuperar_supervisor';
                    } else if (value.startsWith('jefe_')) {
                      _tipoDestino = 'jefe_cuadrilla';
                    } else if (value.startsWith('supervisor_')) {
                      _tipoDestino = 'supervisor';
                    }
                  }
                });
              },
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSolicitudesPendientes() {
    if (_solicitudesPendientes.isEmpty) {
      return const SizedBox.shrink();
    }

    return Card(
      elevation: 4,
      margin: const EdgeInsets.all(8),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.pending_actions, color: Color(0xFF00B894)),
                const SizedBox(width: 8),
                Text(
                  'Solicitudes (${_solicitudesPendientes.length})',
                  style: const TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const Divider(height: 24),
            ..._solicitudesPendientes.map((solicitud) {
              return Card(
                elevation: 1,
                margin: const EdgeInsets.symmetric(vertical: 8),
                child: Padding(
                  padding: const EdgeInsets.all(12),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'De: ${solicitud['solicitante_nombre']}',
                        style: const TextStyle(fontWeight: FontWeight.bold),
                      ),
                      const SizedBox(height: 4),
                      Text('Trabajadores: ${solicitud['trabajadores_count']}'),
                      Text('Tipo: ${solicitud['tipo_traspaso']}'),
                      const SizedBox(height: 12),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.end,
                        children: [
                          TextButton.icon(
                            onPressed: () =>
                                _responderSolicitud(solicitud['id'], false),
                            icon: const Icon(Icons.cancel, color: Colors.red),
                            label: const Text('Rechazar'),
                          ),
                          const SizedBox(width: 8),
                          ElevatedButton.icon(
                            onPressed: () =>
                                _responderSolicitud(solicitud['id'], true),
                            icon: const Icon(Icons.check_circle),
                            label: const Text('Aprobar'),
                            style: ElevatedButton.styleFrom(
                              backgroundColor: const Color(0xFF00B894),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              );
            }).toList(),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return Scaffold(
        appBar: AppBar(
          title: const Text('Traspaso de Trabajadores'),
          backgroundColor: const Color(0xFF00B894),
        ),
        body: const Center(child: CircularProgressIndicator()),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('Traspaso de Trabajadores'),
        backgroundColor: const Color(0xFF00B894),
        foregroundColor: Colors.white,
      ),
      body: RefreshIndicator(
        onRefresh: _cargarDatos,
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          child: Padding(
            padding: const EdgeInsets.fromLTRB(8, 8, 8, 80),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Card(
                  color: const Color(0xFF00B894).withOpacity(0.1),
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Row(
                      children: [
                        Icon(
                          _isSupervisor
                              ? Icons.supervisor_account
                              : Icons.person,
                          color: const Color(0xFF00B894),
                          size: 32,
                        ),
                        const SizedBox(width: 12),
                        Text(
                          _isSupervisor ? 'Supervisor' : 'Jefe de Cuadrilla',
                          style: const TextStyle(
                            fontSize: 20,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),

                const SizedBox(height: 16),

                if (_isSupervisor) _buildSolicitudesPendientes(),

                const SizedBox(height: 16),

                if (_isSupervisor) _buildJefesCuadrillaDisponibles(),

                const SizedBox(height: 16),

                Card(
                  elevation: 2,
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            const Icon(Icons.people, color: Color(0xFF00B894)),
                            const SizedBox(width: 8),
                            Text(
                              'Mis Trabajadores (${_misTrabajadores.length})',
                              style: const TextStyle(
                                fontSize: 18,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ],
                        ),
                        const Divider(height: 24),
                        if (_misTrabajadores.isEmpty)
                          const Padding(
                            padding: EdgeInsets.all(16),
                            child: Center(
                              child: Text(
                                'No tienes trabajadores asignados',
                                style: TextStyle(color: Colors.grey),
                              ),
                            ),
                          )
                        else
                          ..._misTrabajadores
                              .map(_buildTrabajadorItem)
                              .toList(),
                      ],
                    ),
                  ),
                ),

                const SizedBox(height: 16),

                if (_trabajadoresSeleccionados.isNotEmpty)
                  _buildDestinoSelector(),

                const SizedBox(height: 16),

                if (_trabajadoresSeleccionados.isNotEmpty)
                  Padding(
                    padding: const EdgeInsets.all(8),
                    child: SizedBox(
                      width: double.infinity,
                      child: ElevatedButton.icon(
                        onPressed: _realizarTraspaso,
                        icon: const Icon(Icons.swap_horiz),
                        label: Text(
                          _destinoSeleccionado == 'recuperar_supervisor'
                              ? 'Recuperar'
                              : (_isSupervisor &&
                                        _tipoDestino == 'jefe_cuadrilla'
                                    ? 'Traspasar'
                                    : 'Solicitar'),
                          style: const TextStyle(fontSize: 16),
                        ),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFF00B894),
                          foregroundColor: Colors.white,
                          padding: const EdgeInsets.symmetric(vertical: 16),
                        ),
                      ),
                    ),
                  ),

                const SizedBox(height: 24),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
