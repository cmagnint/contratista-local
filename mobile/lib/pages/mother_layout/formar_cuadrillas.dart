import 'dart:math';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:contratista/services/contratista_api_service.dart';
import 'package:contratista/utils/globals.dart';

class AdministrarCuadrillas extends StatefulWidget {
  const AdministrarCuadrillas({super.key});

  @override
  AdministrarCuadrillasState createState() => AdministrarCuadrillasState();
}

class AdministrarCuadrillasState extends State<AdministrarCuadrillas> {
  final ApiService apiService = ApiService();
  List<dynamic> grupos = [];
  List<dynamic> cuadrillas = [];
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    loggerGlobal.d(userInfo.idUsuario);
    _cargarGrupos();
    _cargarCuadrillas();
  }

  Future<void> _cargarGrupos() async {
    try {
      final response = await apiService.get(
        'api_cuadrillas/grupos/?holding=${userInfo.holding}',
      );
      final decodedData = jsonDecode(response.body);
      setState(() {
        grupos = List<dynamic>.from(decodedData);
        isLoading = false;
      });
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text('Error al cargar grupos: $e')));
      }
      setState(() => isLoading = false);
    }
  }

  Future<void> _cargarCuadrillas() async {
    try {
      final response = await apiService.get(
        'api_cuadrillas/?holding=${userInfo.holding}',
      );
      final decodedData = jsonDecode(response.body);
      setState(() {
        cuadrillas = List<dynamic>.from(decodedData);
      });
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error al cargar cuadrillas: $e')),
        );
      }
    }
  }

  void _guardarCuadrilla(List<dynamic> trabajadoresIds) async {
    try {
      // Generar un nuevo ID para la cuadrilla
      int newId = 1;
      if (cuadrillas.isNotEmpty) {
        newId = cuadrillas.map<int>((c) => c['id']).reduce(max) + 1;
      }

      final response = await apiService.post('api_cuadrillas/', {
        'id': newId,
        'holding': userInfo.holding,
        'usuario': userInfo.idUsuario,
        'trabajadores': trabajadoresIds,
      });

      final decodedData = jsonDecode(response.body);

      if (decodedData['id'] != null) {
        setState(() {
          cuadrillas.add(decodedData);
        });
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Cuadrilla creada con éxito')),
          );
          // Recargar los grupos y cuadrillas
          _cargarGrupos();
          _cargarCuadrillas();
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error al crear la cuadrilla: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: const BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            Color.fromARGB(255, 104, 138, 166),
            Color.fromARGB(255, 114, 186, 116),
          ],
        ),
      ),
      child: Scaffold(
        backgroundColor: Colors.transparent,
        appBar: AppBar(
          automaticallyImplyLeading: true,
          backgroundColor: const Color.fromARGB(255, 6, 62, 107),
          title: const Text(
            'ADMINISTRAR CUADRILLAS',
            style: TextStyle(color: Colors.white, fontWeight: FontWeight.w600),
          ),
        ),
        body: isLoading
            ? const Center(child: CircularProgressIndicator())
            : Column(
                children: [
                  Expanded(
                    child: grupos.isEmpty
                        ? _buildEmptyGrupos()
                        : _buildGruposList(),
                  ),
                ],
              ),
      ),
    );
  }

  Widget _buildEmptyGrupos() {
    return const Center(
      child: Text(
        'No hay grupos de trabajadores disponibles.',
        style: TextStyle(fontWeight: FontWeight.w600, fontSize: 25),
      ),
    );
  }

  Widget _buildGruposList() {
    return ListView.builder(
      itemCount: grupos.length,
      itemBuilder: (context, index) {
        var grupo = grupos[index];
        return Card(
          margin: const EdgeInsets.all(8.0),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(0),
            side: const BorderSide(color: Colors.black, width: 1),
          ),
          child: ExpansionTile(
            backgroundColor: Colors.white,
            collapsedBackgroundColor: Colors.white,
            title: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Folio: ${grupo['folio_nombre']}',
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
                Text(
                  'Labor: ${grupo['labor_nombre']}',
                  style: const TextStyle(fontSize: 14),
                ),
                Text(
                  'Supervisor: ${grupo['supervisor_nombre']}',
                  style: const TextStyle(fontSize: 14),
                ),
              ],
            ),
            children: [
              Container(
                decoration: const BoxDecoration(
                  border: Border(
                    top: BorderSide(color: Colors.black, width: 1),
                  ),
                ),
                child: Column(
                  children: [
                    ...grupo['trabajadores'].map<Widget>((trabajador) {
                      return ListTile(
                        title: Text(
                          '${trabajador['nombres']} ${trabajador['apellidos']}',
                        ),
                        trailing: IconButton(
                          icon: const Icon(Icons.group_add),
                          onPressed: () => _crearCuadrilla(grupo, trabajador),
                        ),
                      );
                    }).toList(),
                  ],
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  void _crearCuadrilla(
    Map<String, dynamic> grupo,
    Map<String, dynamic> trabajador,
  ) {
    List<dynamic> selectedTrabajadores = [];

    showDialog(
      context: context,
      builder: (BuildContext context) {
        return StatefulBuilder(
          builder: (context, setState) {
            return AlertDialog(
              title: const Text('Crear Nueva Cuadrilla'),
              content: SizedBox(
                width: double.maxFinite,
                child: ListView(
                  shrinkWrap: true,
                  children: [
                    ...grupo['trabajadores'].map<Widget>((t) {
                      return CheckboxListTile(
                        title: Text('${t['nombres']} ${t['apellidos']}'),
                        value: selectedTrabajadores.contains(t['id']),
                        onChanged: (bool? value) {
                          setState(() {
                            if (value == true) {
                              selectedTrabajadores.add(t['id']);
                            } else {
                              selectedTrabajadores.remove(t['id']);
                            }
                          });
                        },
                      );
                    }).toList(),
                  ],
                ),
              ),
              actions: [
                TextButton(
                  child: const Text('Cancelar'),
                  onPressed: () => Navigator.of(context).pop(),
                ),
                ElevatedButton(
                  child: const Text('Crear Cuadrilla'),
                  onPressed: () {
                    if (selectedTrabajadores.length >= 2) {
                      _guardarCuadrilla(selectedTrabajadores);
                      Navigator.of(context).pop();
                    } else {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                          content: Text('Seleccione al menos 2 trabajadores'),
                        ),
                      );
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
}
