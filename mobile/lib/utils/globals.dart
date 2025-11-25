import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:logger/logger.dart';
import 'package:flutter/material.dart';
import 'package:connectivity_plus/connectivity_plus.dart';

Logger loggerGlobal = Logger();
final GlobalKey<NavigatorState> globalnavigatorKey =
    GlobalKey<NavigatorState>();

const storage = FlutterSecureStorage();
bool hasFetchedData = false;
final UserInfo userInfo = UserInfo();
final GlobalState globalState = GlobalState();

// Class to manage user information
class UserInfo {
  String rut = '';
  String dv = '';
  String name = '';
  String password = '';
  String email = '';
  String holding = '';
  List<Map<String, dynamic>> sociedades = []; // ✅ CAMBIAR a List
  String sociedadSeleccionada = '';
  int idUsuario = 0;
  String selectedHolding = '';
  bool isAdmin = false;
  bool fetchData = false;
  bool trueToken = false;
  bool bodega = false;
  bool maquinaria = false;
  bool manoObra = false;
  //PERFIL
  int idPerfil = 0;
  String nombrePerfil = '';
  //SUPERVISOR O JEFE DE CUADRILLA
  bool isSupervisorOrJefe = false;
  int? idSupervisor = 0;
  int? idJefeCuadrilla = 0;

  void clear() {
    rut = '';
    dv = '';
    name = '';
    password = '';
    email = '';
    holding = '';
    sociedades = []; // ✅ LIMPIAR LISTA
    sociedadSeleccionada = '';
    idUsuario = 0;
    selectedHolding = '';
    isAdmin = false;
    fetchData = false;
    trueToken = false;
    bodega = false;
    maquinaria = false;
    manoObra = false;
    idSupervisor = 0;
    idJefeCuadrilla = 0;
  }
}

class GlobalState {
  bool alreadyDownloaded = false;
  bool hasResponse = false;
}

Future<bool> isConnected() async {
  var connectivityResult = await (Connectivity().checkConnectivity());
  if (connectivityResult == ConnectivityResult.none) {
    return false;
  }
  return true;
}

void navigateToScreen(BuildContext context, String routeName) {
  Navigator.pushReplacementNamed(context, routeName);
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
                navigateToScreen(context, '/LoginScreen');
              }
            },
          ),
        ],
      );
    },
  );
}
