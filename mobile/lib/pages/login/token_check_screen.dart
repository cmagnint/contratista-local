import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:contratista/services/contratista_api_service.dart';
import 'package:contratista/utils/globals.dart';

class TokenCheckScreen extends StatefulWidget {
  const TokenCheckScreen({super.key});

  @override
  TokenCheckScreenState createState() => TokenCheckScreenState();
}

class TokenCheckScreenState extends State<TokenCheckScreen> {
  final ApiService apiService = ApiService();

  @override
  void initState() {
    super.initState();
    _checkTokenAndNavigate();
  }

  Future<void> _checkTokenAndNavigate() async {
    // Pequeña pausa para mostrar la pantalla
    await Future.delayed(const Duration(milliseconds: 500));

    try {
      // Obtener token guardado
      String? token = await storage.read(key: 'jwt_token');
      logger.d('Token: $token');
      if (token == null || token.isEmpty) {
        // No hay token, ir al login
        _navigateToLogin();
        return;
      }

      // Verificar token usando el método POST existente
      final response = await apiService.post('verify_jwt/', {
        'jwt_token': token,
      });

      final data = jsonDecode(response.body);
      logger.d(data);
      if (data['valid'] == true) {
        // Token válido, cargar datos del usuario
        _loadUserDataAndNavigateHome(data);
      } else {
        // Token inválido o expirado, ir al login
        _navigateToLogin();
      }
    } catch (e) {
      loggerGlobal.e('Error checking token: $e');
      // En caso de error, ir al login
      _navigateToLogin();
    }
  }

  void _loadUserDataAndNavigateHome(Map<String, dynamic> data) async {
    // ✅ PROCESAR SOCIEDADES COMO LISTA
    List<Map<String, dynamic>> sociedadesList = [];
    if (data['sociedades'] != null) {
      sociedadesList = List<Map<String, dynamic>>.from(
        data['sociedades'].map(
          (soc) => {
            'id': soc['id'],
            'nombre': soc['nombre'],
            'rol_sociedad': soc['rol_sociedad'] ?? '',
          },
        ),
      );
    }

    // Guardar en storage
    await storage.write(
      key: 'user_id',
      value: data['user_id']?.toString() ?? '',
    );
    await storage.write(
      key: 'holding',
      value: data['holding_id']?.toString() ?? '',
    );
    await storage.write(
      key: 'sociedades',
      value: jsonEncode(sociedadesList),
    ); // ✅ GUARDAR JSON
    await storage.write(
      key: 'supervisor_id',
      value: data['supervisor_id']?.toString() ?? '',
    );
    await storage.write(
      key: 'jefe_cuadrilla_id',
      value: data['jefe_cuadrilla_id']?.toString() ?? '',
    );
    await storage.write(key: 'nombre', value: data['nombre']?.toString() ?? '');
    await storage.write(key: 'rut', value: data['rut']?.toString() ?? '');

    // Cargar en memoria
    userInfo.idUsuario = int.tryParse(data['user_id']?.toString() ?? '0') ?? 0;
    userInfo.holding = data['holding_id']?.toString() ?? '';
    userInfo.sociedades = sociedadesList; // ✅ CARGAR LISTA
    userInfo.idSupervisor = int.tryParse(
      data['supervisor_id']?.toString() ?? '0',
    );
    userInfo.idJefeCuadrilla = int.tryParse(
      data['jefe_cuadrilla_id']?.toString() ?? '0',
    );
    userInfo.name = data['nombre']?.toString() ?? '';
    userInfo.rut = data['rut']?.toString() ?? '';
    userInfo.isAdmin = data['is_admin'] ?? false;

    if (mounted) navigateToScreen(context, '/Mother_Layout');
  }

  void _navigateToLogin() {
    if (mounted) {
      navigateToScreen(context, '/Login');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              Color(0xFF00B894), // Verde esmeralda claro
              Color(0xFF00A085), // Verde esmeralda medio
              Color(0xFF2F4858), // Azul petróleo
            ],
          ),
        ),
        child: const Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.verified_user, size: 80, color: Colors.white),
              SizedBox(height: 20),
              Text(
                'Verificando sesión...',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                ),
              ),
              SizedBox(height: 20),
              CircularProgressIndicator(
                valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
