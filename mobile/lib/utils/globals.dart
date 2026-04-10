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

//Widget para mostrar un teclado alfanumerico solo con la letra K
class RutKeyboard extends StatelessWidget {
  final TextEditingController controller;
  final VoidCallback onClose;
  final bool isRut;

  const RutKeyboard({
    super.key,
    required this.controller,
    required this.onClose,
    this.isRut = false,
  });

  String _getRaw() {
    return controller.text.replaceAll('.', '').replaceAll('-', '');
  }

  String _formatRut(String raw) {
    if (raw.isEmpty) return '';
    if (raw.length == 1) return raw;
    final dv = raw[raw.length - 1];
    final num = raw.substring(0, raw.length - 1);
    String formatted = '';
    for (int i = 0; i < num.length; i++) {
      if (i > 0 && (num.length - i) % 3 == 0) formatted += '.';
      formatted += num[i];
    }
    return '$formatted-$dv';
  }

  void _onKey(String key) {
    final raw = _getRaw() + key;
    final display = isRut ? _formatRut(raw) : raw;
    controller.value = TextEditingValue(
      text: display,
      selection: TextSelection.collapsed(offset: display.length),
    );
  }

  void _onDelete() {
    final raw = _getRaw();
    if (raw.isEmpty) return;
    final newRaw = raw.substring(0, raw.length - 1);
    final display = isRut ? _formatRut(newRaw) : newRaw;
    controller.value = TextEditingValue(
      text: display,
      selection: TextSelection.collapsed(offset: display.length),
    );
  }

  Widget _key(String label, {Color? color}) {
    return Expanded(
      child: Padding(
        padding: const EdgeInsets.all(3),
        child: ElevatedButton(
          style: ElevatedButton.styleFrom(
            backgroundColor: color ?? Colors.grey[200],
            foregroundColor: Colors.black,
            padding: const EdgeInsets.symmetric(vertical: 16),
            elevation: 1,
          ),
          onPressed: () => _onKey(label),
          child: Text(
            label,
            style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      top: false,
      child: Container(
        color: Colors.grey[300],
        padding: const EdgeInsets.fromLTRB(5, 0, 6, 80),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                TextButton(
                  onPressed: onClose,
                  child: const Text('Listo', style: TextStyle(fontSize: 16)),
                ),
              ],
            ),
            Row(children: ['1', '2', '3'].map((e) => _key(e)).toList()),
            Row(children: ['4', '5', '6'].map((e) => _key(e)).toList()),
            Row(children: ['7', '8', '9'].map((e) => _key(e)).toList()),
            Row(
              children: [
                _key('K', color: Colors.blue[100]),
                _key('0'),
                Expanded(
                  child: Padding(
                    padding: const EdgeInsets.all(3),
                    child: ElevatedButton(
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.red[200],
                        foregroundColor: Colors.black,
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        elevation: 1,
                      ),
                      onPressed: _onDelete,
                      child: const Icon(Icons.backspace_outlined),
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
