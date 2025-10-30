//contratista-local
import 'package:contratista/pages/mother_layout/contratacion/contratacion.dart';
import 'package:contratista/pages/mother_layout/contratacion/pending_enrollments_screen.dart';
import 'package:contratista/pages/mother_layout/contratacion/pre_contratacion.dart';
import 'package:contratista/pages/mother_layout/contratacion/asociar_qr.dart';
import 'package:contratista/pages/mother_layout/cosecha/ingresar_produccion.dart';
import 'package:contratista/pages/mother_layout/formar_cuadrillas.dart';
import 'package:contratista/pages/mother_layout/mano_obra/asistencia.dart'; // ✅ AGREGADO
import 'package:contratista/services/contratista_api_service.dart';
import 'package:lucide_icons/lucide_icons.dart';
import 'package:flutter/material.dart';
import 'package:contratista/pages/mother_layout/inicio.dart';
import 'package:contratista/utils/globals.dart';
import 'dart:convert';

class MotherLayout extends StatefulWidget {
  const MotherLayout({super.key});

  @override
  MotherLayoutState createState() => MotherLayoutState();
}

class MotherLayoutState extends State<MotherLayout> {
  int _selectedIndex = 0;
  ApiService apiService = ApiService();

  final List<Widget> _pages = [
    const Inicio(), // _selectedIndex = 0 INICIO
    Container(), // _selectedIndex = 1 PRECONTRATACION
    const WorkerQRAssociationScreen(), // _selectedIndex = 2 ASIGNAR QR
    const WorkerProductionScreen(), // _selectedIndex = 3 INGRESAR PRODUCCION
    const AdministrarCuadrillas(), // _selectedIndex = 4 ADMINISTRAR CUADRILLAS
    const PendingEnrollmentsScreen(), // _selectedIndex = 5 ENROLAMIENTOS PENDIENTES
    Container(), // _selectedIndex = 6 ASISTENCIA ✅ AGREGADO
  ];

  @override
  void initState() {
    super.initState();
  }

  //CONTRATACION
  void goToPreContratacion() async {
    try {
      String? holding = await storage.read(key: 'holding');
      final response = await ApiService().get(
        'folio_comercial/?holding=$holding&pre_contratacion=true',
      );
      final folios = (jsonDecode(response.body) as List)
          .map((e) => e as Map<String, dynamic>)
          .toList();
      loggerGlobal.d(folios);

      if (mounted) {
        if (folios.isEmpty) {
          _showNoFoliosDialog();
        } else {
          setState(() {
            _pages[1] = PreContratacionScreen(
              folios: folios,
              onContinue: (Map<String, String?> initialData) {
                setState(() {
                  _pages[1] = ContratacionScreen(
                    initialData: initialData,
                    onBack: () {
                      goToPreContratacion();
                    },
                  );
                });
              },
            );
            _selectedIndex = 1;
          });
        }
      }
    } catch (e) {
      if (mounted) {
        _showDialogWithMessage(context, 'Error al obtener los folios: $e');
      }
    }
  }

  // ✅ NUEVA FUNCIÓN PARA ASISTENCIA
  void goToAsistencia() async {
    try {
      // Mostrar loading
      showDialog(
        context: context,
        barrierDismissible: false,
        builder: (context) => const Center(child: CircularProgressIndicator()),
      );

      // ✅ CAMBIO: Usar supervisor_id en lugar de rut
      if (userInfo.idSupervisor == null || userInfo.idSupervisor == 0) {
        if (mounted) {
          Navigator.of(context).pop();
          _showDialogWithMessage(
            context,
            'No tienes permisos de supervisor. Contacta al administrador.',
          );
        }
        return;
      }

      String? holding = await storage.read(key: 'holding');

      // ✅ CAMBIO: Enviar supervisor_id
      final response = await apiService.get(
        'gestion_asistencia/?supervisor_id=${userInfo.idSupervisor}&holding=$holding',
      );

      if (mounted) {
        Navigator.of(context).pop(); // Cerrar loading
      }

      final data = jsonDecode(response.body);

      if (mounted) {
        if (data['acceso_asistencia'] == false) {
          _showDialogWithMessage(
            context,
            'No tienes acceso a la funcionalidad de asistencia. Contacta al administrador.',
          );
        } else if (data['workers'] == null ||
            (data['workers'] as List).isEmpty) {
          _showDialogWithMessage(
            context,
            'No hay trabajadores pendientes de asistencia para el día de hoy.',
          );
        } else {
          // Procesar datos de trabajadores
          var workers = data['workers'] as List;

          List<dynamic> workerNames = workers.map((w) => w['nombre']).toList();

          Map<String, int> workerRuts = {
            for (var worker in workers)
              worker['nombre'] as String:
                  int.tryParse(worker['rut']?.toString() ?? '0') ?? 0,
          };

          Map<String, double> workerHours = {
            for (var worker in workers)
              worker['nombre'] as String:
                  (worker['horas_registradas_hoy'] as num).toDouble(),
          };

          Map<String, int> workerIds = {
            for (var worker in workers)
              worker['nombre'] as String: worker['id'] as int,
          };

          setState(() {
            _pages[6] = Asistencia(
              workerNames: workerNames,
              workerRuts: workerRuts,
              workerHours: workerHours,
              workerIds: workerIds,
            );
            _selectedIndex = 6;
          });
        }
      }
    } catch (e) {
      if (mounted) {
        Navigator.of(context).pop(); // Cerrar loading si hay error
        _showDialogWithMessage(
          context,
          'Error al obtener los trabajadores: ${e.toString()}',
        );
      }
      loggerGlobal.e('Error en goToAsistencia: $e');
    }
  }

  void _showNoFoliosDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('No se encontraron folios disponibles'),
        actions: <Widget>[
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }

  void _showDialogWithMessage(BuildContext context, String message) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text(
          '¡Aviso!',
          style: TextStyle(fontWeight: FontWeight.w900),
        ),
        content: Text(
          message,
          style: const TextStyle(fontWeight: FontWeight.w900),
        ),
        actions: <Widget>[
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text(
              'Aceptar',
              style: TextStyle(color: Color.fromARGB(255, 2, 82, 4)),
            ),
          ),
        ],
      ),
    );
  }

  void cerrarSesion(BuildContext context) {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: const Text('¿Desea cerrar sesión?'),
          actions: [
            TextButton(
              child: const Text('Si'),
              onPressed: () async {
                UserInfo user = UserInfo();
                await storage.deleteAll();
                user.clear();

                if (context.mounted) {
                  Navigator.of(context).pop();
                  navigateToScreen(context, '/Login');
                }
              },
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
        flexibleSpace: Container(
          decoration: const BoxDecoration(
            gradient: LinearGradient(
              colors: [
                Color.fromRGBO(0, 32, 63, 1),
                Color.fromRGBO(0, 74, 105, 1),
                Color.fromRGBO(0, 119, 126, 1),
                Color.fromRGBO(29, 162, 133, 1),
                Color.fromRGBO(152, 251, 152, 1),
              ],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
          ),
        ),
        title: const Text(
          'CONTRATISTA',
          style: TextStyle(color: Colors.white, fontWeight: FontWeight.w600),
        ),
        automaticallyImplyLeading: false,
      ),
      drawer: Drawer(
        child: ListView(
          padding: EdgeInsets.zero,
          children: <Widget>[
            const DrawerHeader(
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [
                    Color.fromRGBO(0, 32, 63, 1),
                    Color.fromRGBO(0, 74, 105, 1),
                    Color.fromRGBO(0, 119, 126, 1),
                    Color.fromRGBO(29, 162, 133, 1),
                    Color.fromRGBO(152, 251, 152, 1),
                  ],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
              ),
              child: Text(
                'Menú',
                style: TextStyle(
                  color: Color.fromARGB(255, 255, 255, 255),
                  fontSize: 24,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
            ExpansionTile(
              leading: const Icon(Icons.handshake),
              title: const Text('Gestión de Trabajadores'),
              children: <Widget>[
                ListTile(
                  leading: const Icon(Icons.how_to_reg),
                  title: const Text('Enrollar Trabajador'),
                  onTap: () {
                    Navigator.pop(context);
                    goToPreContratacion();
                  },
                ),
                ListTile(
                  leading: const Icon(Icons.pending),
                  title: const Text('Enrolamientos Pendientes'),
                  onTap: () {
                    setState(() {
                      _selectedIndex = 5;
                    });
                    if (mounted) {
                      Navigator.pop(context);
                    }
                  },
                ),
                ListTile(
                  leading: const Icon(Icons.qr_code),
                  title: const Text('Asignar Codigo QR'),
                  onTap: () {
                    setState(() {
                      _selectedIndex = 2;
                    });
                    if (mounted) {
                      Navigator.pop(context);
                    }
                  },
                ),
              ],
            ),
            ListTile(
              leading: const Icon(Icons.group_work),
              title: const Text('Administrar Cuadrillas'),
              onTap: () {
                setState(() {
                  _selectedIndex = 4;
                });
                if (mounted) {
                  Navigator.pop(context);
                }
              },
            ),
            ExpansionTile(
              leading: const Icon(Icons.assignment_ind),
              title: const Text('Mano de Obra'),
              children: <Widget>[
                // ✅ AGREGADO: ListTile de Asistencia
                ListTile(
                  leading: const Icon(Icons.how_to_reg),
                  title: const Text('Asistencia'),
                  onTap: () {
                    Navigator.pop(context);
                    goToAsistencia(); // ✅ Llamar a la función
                  },
                ),
                ExpansionTile(
                  leading: const Icon(Icons.person_2),
                  title: const Text('Por Persona'),
                  children: <Widget>[
                    ListTile(
                      leading: const Icon(Icons.person_add),
                      title: const Text('Ingresar Rendimiento'),
                      onTap: () {
                        Navigator.pop(context);
                      },
                    ),
                    ListTile(
                      leading: const Icon(Icons.summarize),
                      title: const Text('Informes'),
                      onTap: () {
                        Navigator.pop(context);
                      },
                    ),
                  ],
                ),
                ExpansionTile(
                  leading: const Icon(Icons.group),
                  title: const Text('Por Cuadrilla'),
                  children: <Widget>[
                    ListTile(
                      leading: const Icon(Icons.group_add),
                      title: const Text('Ingresar Rendimiento'),
                      onTap: () {
                        Navigator.pop(context);
                      },
                    ),
                    ListTile(
                      leading: const Icon(Icons.summarize),
                      title: const Text('Informes'),
                      onTap: () {
                        Navigator.pop(context);
                      },
                    ),
                  ],
                ),
              ],
            ),
            ExpansionTile(
              leading: const Icon(LucideIcons.sprout),
              title: const Text('Cosecha'),
              children: <Widget>[
                ExpansionTile(
                  leading: const Icon(Icons.person),
                  title: const Text('Por Persona'),
                  children: <Widget>[
                    ListTile(
                      leading: const Icon(Icons.person_add),
                      title: const Text('Ingresar Rendimiento'),
                      onTap: () {
                        setState(() {
                          _selectedIndex = 3;
                        });
                        if (mounted) {
                          Navigator.pop(context);
                        }
                      },
                    ),
                    ListTile(
                      leading: const Icon(Icons.summarize),
                      title: const Text('Informes'),
                      onTap: () {
                        Navigator.pop(context);
                      },
                    ),
                  ],
                ),
                ExpansionTile(
                  leading: const Icon(Icons.group),
                  title: const Text('Por Cuadrilla'),
                  children: <Widget>[
                    ListTile(
                      leading: const Icon(Icons.group_add),
                      title: const Text('Ingresar Rendimiento'),
                      onTap: () {
                        Navigator.pop(context);
                      },
                    ),
                    ListTile(
                      leading: const Icon(Icons.summarize),
                      title: const Text('Informes'),
                      onTap: () {
                        Navigator.pop(context);
                      },
                    ),
                  ],
                ),
              ],
            ),
          ],
        ),
      ),
      body: Stack(
        children: [
          Center(child: _pages.elementAt(_selectedIndex)),
          Positioned(
            bottom: 0,
            left: 0,
            right: 0,
            child: Container(
              decoration: const BoxDecoration(
                gradient: LinearGradient(
                  colors: [
                    Color.fromRGBO(0, 32, 63, 1),
                    Color.fromRGBO(0, 74, 105, 1),
                    Color.fromRGBO(0, 119, 126, 1),
                    Color.fromRGBO(29, 162, 133, 1),
                    Color.fromRGBO(152, 251, 152, 1),
                  ],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
              ),
              child: BottomAppBar(
                color: Colors.transparent,
                shape: const CircularNotchedRectangle(),
                notchMargin: 30.0,
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: <Widget>[
                    Builder(
                      builder: (context) {
                        return IconButton(
                          icon: const Icon(
                            color: Color.fromARGB(255, 255, 255, 255),
                            Icons.menu,
                          ),
                          onPressed: () {
                            Scaffold.of(context).openDrawer();
                          },
                        );
                      },
                    ),
                    const Spacer(),
                    IconButton(
                      icon: const Icon(
                        color: Color.fromARGB(255, 10, 12, 109),
                        Icons.logout,
                      ),
                      onPressed: () {
                        cerrarSesion(context);
                      },
                    ),
                  ],
                ),
              ),
            ),
          ),
          Positioned(
            bottom: 10,
            left: MediaQuery.of(context).size.width / 2 - 28,
            child: FloatingActionButton(
              backgroundColor: const Color.fromARGB(255, 10, 12, 109),
              elevation: 50,
              onPressed: () {
                setState(() {
                  _selectedIndex = 0;
                });
              },
              child: const Icon(color: Colors.white, Icons.home),
            ),
          ),
        ],
      ),
      floatingActionButtonLocation: FloatingActionButtonLocation.centerDocked,
    );
  }
}
