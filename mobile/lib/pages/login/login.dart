import 'dart:async';
import 'dart:convert';
import 'package:device_info_plus/device_info_plus.dart';
import 'package:flutter/material.dart';
import 'package:logger/logger.dart';
import 'package:contratista/utils/globals.dart';
import 'package:contratista/services/contratista_api_service.dart';
import 'package:permission_handler/permission_handler.dart';
import 'dart:io';
import 'package:lottie/lottie.dart';

Logger logger = Logger();

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});
  @override
  LoginScreenState createState() => LoginScreenState();
}

class LoginScreenState extends State<LoginScreen>
    with TickerProviderStateMixin {
  final TextEditingController rutController = TextEditingController();
  final TextEditingController passwordController = TextEditingController();
  final ApiService _apiService = ApiService();

  bool _isRutValid = true;
  double _opacity = 0.0;
  bool obscureText = true;
  final GlobalKey<NavigatorState> navigatorKey = globalnavigatorKey;
  List<TextEditingController> rutControllers = List.generate(
    12,
    (index) => TextEditingController(),
  );
  FocusNode focusNode = FocusNode();

  Color _borderColor = Colors.transparent;
  Timer? _borderTimer;

  // Colores del tema
  static const Color _primaryColor = Color(0xFF1A237E); // Azul oscuro elegante
  static const Color _cardColor = Colors.white;
  static const Color _textMuted = Color(0xFF6B7280);

  @override
  void initState() {
    super.initState();
    checkAndRequestStoragePermission();

    rutController.addListener(() {
      final text = rutController.text;
      rutController.value = rutController.value.copyWith(
        text: formatRut(text),
        selection: TextSelection.collapsed(offset: formatRut(text).length),
      );
    });
  }

  void _toggleBorderBlinking(bool isFocused) {
    if (isFocused) {
      _borderTimer = Timer.periodic(const Duration(seconds: 2), (_) {
        setState(() {
          _borderColor = _borderColor == _primaryColor
              ? Colors.transparent
              : _primaryColor;
        });
      });
    } else {
      _borderTimer?.cancel();
      setState(() {
        _borderColor = Colors.transparent;
      });
    }
  }

  Future<void> token() async {
    String? token = await storage.read(key: 'jwt_token');
    loggerGlobal.d(token);
  }

  Future _showEmailNotSentDialog(BuildContext context) {
    return showDialog(
      context: context,
      barrierDismissible: true,
      builder: (BuildContext context) {
        return Dialog(
          elevation: 5.0,
          backgroundColor: Colors.transparent,
          child: Container(
            width: MediaQuery.of(context).size.width * 0.8,
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(8.0),
              color: Colors.white,
              boxShadow: const [
                BoxShadow(
                  color: Colors.black26,
                  offset: Offset(0.0, 3.0),
                  blurRadius: 5.0,
                ),
              ],
            ),
            child: Padding(
              padding: const EdgeInsets.all(20.0),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                children: [
                  Expanded(
                    flex: 2,
                    child: Lottie.asset(
                      'assets/animations/invalid.json',
                      repeat: true,
                      animate: true,
                    ),
                  ),
                  const Expanded(
                    flex: 2,
                    child: Text(
                      "¡El correo no fue enviado! \nRut invalido \nPor favor intente nuevamente",
                      style: TextStyle(
                        fontSize: 15,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  Future<bool> generarCodigo(String rut) async {
    try {
      final response = await _apiService.post('password-reset/', {
        'rut': rut,
        'action': 'generate_code',
      }, includeAuth: false);

      if (response.statusCode == 200) {
        var jsonResponse = jsonDecode(response.body);
        if (jsonResponse['status'] == 'success') {
          return true;
        } else if (jsonResponse['status'] == 'error') {
          logger.d(jsonResponse['message']);
          return false;
        }
      }
      return false;
    } catch (e) {
      if (mounted && e.toString().contains('tardado demasiado')) {
        Navigator.of(context).pop();
        _showDialogWithMessage(
          context,
          'La conexión ha tardado demasiado, favor intente nuevamente.',
        );
      }
      logger.d(e.toString());
      return false;
    }
  }

  Future<bool> verificarCodigo(String rut, String codigo) async {
    try {
      String rutNumber = rutController.text;
      loggerGlobal.d('el rut a enviar es: $rutNumber');

      final response = await _apiService.post('password-reset/', {
        'rut': rutNumber.toString(),
        'codigo': codigo,
        'action': 'verify_code',
      }, includeAuth: false);

      if (response.statusCode == 200) {
        final Map<String, dynamic> responseBody = json.decode(response.body);
        if (responseBody['status'] == 'success') {
          return true;
        }
      }
      return false;
    } catch (e) {
      logger.d('Error en verificarCodigo: $e');
      return false;
    }
  }

  Future _showEmailSentDialog(BuildContext context) {
    return showDialog(
      context: context,
      barrierDismissible: true,
      builder: (BuildContext context) {
        return Dialog(
          elevation: 5.0,
          backgroundColor: Colors.transparent,
          child: Container(
            width: MediaQuery.of(context).size.width * 0.8,
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(8.0),
              color: Colors.white,
              boxShadow: const [
                BoxShadow(
                  color: Colors.black26,
                  offset: Offset(0.0, 3.0),
                  blurRadius: 5.0,
                ),
              ],
            ),
            child: Padding(
              padding: const EdgeInsets.all(20.0),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                children: [
                  Expanded(
                    flex: 2,
                    child: Lottie.asset(
                      'assets/animations/email_send.json',
                      repeat: true,
                      animate: true,
                    ),
                  ),
                  Expanded(
                    flex: 3,
                    child: Text(
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 16,
                      ),
                      "¡Hola ${userInfo.name}, el codigo fue enviado al correo con exito! Revise su bandeja \n (Revise tambien Spam)",
                    ),
                  ),
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  Future<void> sendCodePressed(BuildContext context) async {
    String rutNumber = rutController.text;
    userInfo.rut = rutNumber;
    loggerGlobal.d(userInfo.rut);

    try {
      final String rut = formatCharRut(rutNumber.toString());
      loggerGlobal.d(rut);
      if (rut != "") {
        final hasInternet = await isConnected();
        if (!hasInternet) {
          if (context.mounted) {
            _showDialogWithMessage(context, 'No hay conexión a Internet.');
            return;
          }
        }

        if (context.mounted) {
          _showProgressDialog(context);
        }

        globalState.hasResponse = false;
        bool isSuccessful = await generarCodigo(rut);

        if (context.mounted) {
          Navigator.of(context).pop();
        }

        if (isSuccessful && context.mounted) {
          _showEmailSentDialog(context).then((_) {
            if (context.mounted) {
              _showRecoveryDialog();
            }
          });
        } else {
          if (context.mounted) {
            _showEmailNotSentDialog(context);
          }
        }
      } else {
        if (context.mounted) {
          _showDialogWithMessage(
            context,
            '¡Debe poner un rut para hacer la consulta!',
          );
        }
      }
    } catch (e) {
      logger.d('Error: $e');
    }
  }

  // ignore: unused_element
  void _showTimeoutDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: const Text(
            'La conexion ha tardado demasiado, favor intente nuevamente',
          ),
          actions: [
            TextButton(
              child: const Text('OK'),
              onPressed: () {
                Navigator.of(context).pop();
              },
            ),
          ],
        );
      },
    );
  }

  Future _showProgressDialog(BuildContext context) {
    return showDialog(
      context: context,
      barrierDismissible: false,
      builder: (BuildContext context) {
        return Dialog(
          elevation: 5.0,
          backgroundColor: Colors.transparent,
          child: Container(
            width: MediaQuery.of(context).size.width * 0.8,
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(8.0),
              color: Colors.white,
              boxShadow: const [
                BoxShadow(
                  color: Colors.black26,
                  offset: Offset(0.0, 3.0),
                  blurRadius: 5.0,
                ),
              ],
            ),
            child: Padding(
              padding: const EdgeInsets.all(20.0),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                children: [
                  Expanded(
                    flex: 2,
                    child: Lottie.asset(
                      'assets/animations/request_code.json',
                      repeat: true,
                      animate: true,
                    ),
                  ),
                  const Expanded(
                    flex: 3,
                    child: Text(
                      "Solicitando código...",
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 18.0,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  void _showInvalidRutDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: const Text('¡Rut y/o contraseña invalido/a!'),
          actions: [
            TextButton(
              child: const Text('OK'),
              onPressed: () {
                Navigator.of(context).pop();
              },
            ),
          ],
        );
      },
    );
  }

  Future<void> checkAndRequestStoragePermission() async {
    if (Platform.isAndroid) {
      var androidInfo = await DeviceInfoPlugin().androidInfo;
      if (androidInfo.version.sdkInt < 30) {
        var status = await Permission.storage.status;
        if (!status.isGranted) {
          status = await Permission.storage.request();
        }
      }
    }
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
              const Text('Iniciando Sesión'),
            ],
          ),
        ),
      ),
    );
  }

  Future<void> loginButtonPressed(BuildContext context) async {
    _showLoadingDialog();

    String rutNumber = rutController.text.replaceAll(RegExp(r'[^\dKk]'), '');
    userInfo.rut = rutNumber;
    userInfo.password = passwordController.text;

    try {
      final hasInternet = await isConnected();
      if (!hasInternet) {
        if (context.mounted) {
          Navigator.of(context).pop();
          _showDialogWithMessage(context, 'No hay conexión a Internet.');
        }
        return;
      }

      if (userInfo.password.isEmpty || rutNumber.isEmpty || !_isRutValid) {
        if (context.mounted) {
          Navigator.of(context).pop();
          _showInvalidRutDialog(context);
        }
        return;
      }

      final response = await _apiService.post('api_login/', {
        'rut': rutNumber,
        'password': passwordController.text,
        'origin': 'MOVIL',
        'version': '1.2.0',
      }, includeAuth: false);

      final responseData = jsonDecode(response.body);
      logger.d('Respuesta login: $responseData');

      if (context.mounted) {
        Navigator.of(context).pop();
      }

      if (response.statusCode == 200 && responseData['autorizado'] == true) {
        await _apiService.saveTokens(
          responseData['jwt_token'],
          responseData['refresh_token'],
        );

        List<Map<String, dynamic>> sociedadesList = [];
        if (responseData['sociedades'] != null) {
          sociedadesList = List<Map<String, dynamic>>.from(
            responseData['sociedades'].map(
              (soc) => {
                'id': soc['id'],
                'nombre': soc['nombre'],
                'rol_sociedad': soc['rol_sociedad'] ?? '',
              },
            ),
          );
        }

        userInfo.idUsuario =
            int.tryParse(responseData['user_id']?.toString() ?? '0') ?? 0;
        userInfo.holding = responseData['holding_id']?.toString() ?? '';
        userInfo.sociedades = sociedadesList;
        userInfo.idSupervisor = int.tryParse(
          responseData['supervisor_id']?.toString() ?? '0',
        );

        userInfo.name = responseData['nombre']?.toString() ?? '';
        userInfo.rut = responseData['rut']?.toString() ?? '';
        userInfo.isAdmin = responseData['is_admin'] ?? false;

        await storage.write(
          key: 'user_id',
          value: responseData['user_id'].toString(),
        );
        await storage.write(
          key: 'holding',
          value: responseData['holding_id']?.toString() ?? '',
        );
        await storage.write(
          key: 'sociedades',
          value: jsonEncode(sociedadesList),
        );
        await storage.write(
          key: 'supervisor_id',
          value: responseData['supervisor_id']?.toString() ?? '',
        );
        await storage.write(
          key: 'nombre',
          value: responseData['nombre']?.toString() ?? '',
        );
        await storage.write(key: 'rut', value: rutNumber);
        await storage.write(
          key: 'is_admin',
          value: responseData['is_admin']?.toString() ?? 'false',
        );

        logger.i('Login exitoso - Sociedades: ${sociedadesList.length}');

        if (context.mounted) {
          navigateToScreen(context, '/Mother_Layout');
        }
      } else {
        if (context.mounted) {
          _showDialogWithMessage(
            context,
            responseData['mensaje'] ?? 'Acceso no autorizado',
          );
        }
      }
    } catch (e) {
      logger.e('Error en login: $e');
      if (context.mounted) {
        Navigator.of(context).pop();
        _showDialogWithMessage(
          context,
          e.toString().contains('tardado')
              ? 'La conexión ha tardado demasiado'
              : 'Error al iniciar sesión',
        );
      }
    }
  }

  void _showDialogWithMessage(BuildContext context, String message) {
    if (globalnavigatorKey.currentState != null) {
      showDialog(
        context: globalnavigatorKey.currentContext!,
        builder: (context) => AlertDialog(
          title: const Text(
            style: TextStyle(fontWeight: FontWeight.w900),
            '¡Aviso!',
          ),
          content: Text(
            style: const TextStyle(fontWeight: FontWeight.w900),
            message,
          ),
          actions: <Widget>[
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text(
                style: TextStyle(color: Color.fromARGB(255, 2, 82, 4)),
                'Aceptar',
              ),
            ),
          ],
        ),
      );
    }
  }

  void _showRecoveryDialog() {
    int intentos = 3;
    String mensajeError = "";

    final TextEditingController codigoController = TextEditingController();

    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) {
        return StatefulBuilder(
          builder: (BuildContext context, StateSetter setState) {
            return AlertDialog(
              title: const Text('Ingrese el código recibido'),
              content: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  TextField(
                    controller: codigoController,
                    decoration: const InputDecoration(labelText: 'Código'),
                  ),
                  Padding(
                    padding: const EdgeInsets.only(top: 10.0),
                    child: Text(
                      mensajeError,
                      style: const TextStyle(color: Colors.red),
                    ),
                  ),
                ],
              ),
              actions: <Widget>[
                TextButton(
                  onPressed: () {
                    Navigator.of(context).pop();
                  },
                  child: const Text('Cancelar'),
                ),
                ElevatedButton(
                  onPressed: () async {
                    String rut = userInfo.rut;
                    final String codigo = codigoController.text;

                    final bool esCorrecto = await verificarCodigo(rut, codigo);

                    if ((esCorrecto) && (context.mounted)) {
                      Navigator.of(context).pop();
                      navigateToScreen(context, '/ChangePassScreen');
                    } else {
                      intentos--;

                      if ((intentos <= 0) && (context.mounted)) {
                        Navigator.of(context).pop();
                      } else {
                        setState(() {
                          mensajeError =
                              "Código incorrecto, te quedan $intentos intentos.";
                        });
                      }
                    }
                  },
                  child: const Text('Validar Código'),
                ),
              ],
            );
          },
        );
      },
    );
  }

  String formatCharRut(String rut) {
    return rut.replaceAll(RegExp(r'[^\dKk]'), '').toUpperCase();
  }

  String formatRut(String rut) {
    rut = rut.replaceAll(RegExp(r'[^0-9kK]'), '').toUpperCase();

    if (rut.length > 1) {
      String dv = rut.substring(rut.length - 1);
      String numbers = rut
          .substring(0, rut.length - 1)
          .replaceAll(RegExp(r'\B(?=(\d{3})+(?!\d))'), '.');
      return '$numbers-$dv';
    }

    return rut;
  }

  String calculateDV(String rut) {
    int multiplier = 2;
    int sum = 0;

    for (int i = rut.length - 1; i >= 0; i--) {
      sum += int.parse(rut[i]) * multiplier;
      multiplier = multiplier == 7 ? 2 : multiplier + 1;
    }

    int remainder = sum % 11;
    int result = 11 - remainder;

    if (result == 11) {
      return '0';
    } else if (result == 10) {
      return 'K';
    } else {
      return result.toString();
    }
  }

  bool validateRut(String rut) {
    rut = rut.replaceAll(RegExp(r'[^0-9kK]'), '').toUpperCase();
    if (rut.length < 2) return false;

    String numbers = rut.substring(0, rut.length - 1);
    String givenDV = rut.substring(rut.length - 1).toUpperCase();
    String calculatedDV = calculateDV(numbers);

    return givenDV == calculatedDV;
  }

  void _startBlinking() {
    Timer.periodic(const Duration(seconds: 1), (timer) {
      if (!mounted) {
        timer.cancel();
        return;
      }
      setState(() {
        _opacity = _opacity == 1.0 ? 0.0 : 1.0;
      });
      if (_isRutValid || rutController.text.isEmpty) {
        timer.cancel();
      }
    });
  }

  @override
  void dispose() {
    _borderTimer?.cancel();
    super.dispose();
  }

  InputDecoration _inputDecoration({
    required String hint,
    required IconData prefixIcon,
    Widget? suffixIcon,
  }) {
    return InputDecoration(
      hintText: hint,
      hintStyle: TextStyle(
        color: Colors.grey.shade400,
        fontWeight: FontWeight.w400,
        fontSize: 14,
      ),
      prefixIcon: Icon(prefixIcon, color: _primaryColor, size: 20),
      suffixIcon: suffixIcon,
      filled: true,
      fillColor: Colors.white,
      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: BorderSide(color: Colors.grey.shade300),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: BorderSide(color: Colors.grey.shade300),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: const BorderSide(color: _primaryColor, width: 1.5),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color.fromARGB(255, 189, 245, 186),
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            child: Column(
              children: [
                // ── Logo arriba solo ──
                const SizedBox(height: 20),
                Container(
                  width: 100,
                  height: 100,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: const Color.fromARGB(255, 255, 255, 255),
                    boxShadow: [
                      BoxShadow(
                        color: const Color.fromARGB(
                          255,
                          255,
                          255,
                          255,
                        ).withOpacity(0.3),
                        blurRadius: 20,
                        offset: const Offset(0, 8),
                      ),
                    ],
                  ),
                  child: ClipOval(
                    child: Image.asset('assets/login.png', fit: BoxFit.cover),
                  ),
                ),

                const SizedBox(height: 32),

                // ── Tarjeta principal ──
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 24),
                  child: Container(
                    width: double.infinity,
                    padding: const EdgeInsets.symmetric(
                      horizontal: 28,
                      vertical: 36,
                    ),
                    decoration: BoxDecoration(
                      color: _cardColor,
                      borderRadius: BorderRadius.circular(20),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.black.withOpacity(0.06),
                          blurRadius: 24,
                          offset: const Offset(0, 8),
                        ),
                      ],
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        // Título
                        const Center(
                          child: Text(
                            'Iniciar Sesión',
                            style: TextStyle(
                              fontSize: 24,
                              fontWeight: FontWeight.w700,
                              color: Color(0xFF1F2937),
                              letterSpacing: -0.5,
                            ),
                          ),
                        ),
                        const SizedBox(height: 6),
                        Center(
                          child: Text(
                            'Ingresa tus credenciales para continuar',
                            style: TextStyle(fontSize: 13, color: _textMuted),
                          ),
                        ),

                        const SizedBox(height: 32),

                        // Label RUT
                        const Text(
                          'RUT',
                          style: TextStyle(
                            fontSize: 13,
                            fontWeight: FontWeight.w600,
                            color: Color(0xFF374151),
                          ),
                        ),
                        const SizedBox(height: 8),

                        // Campo RUT
                        Focus(
                          onFocusChange: (hasFocus) {
                            setState(() {
                              _isRutValid =
                                  rutController.text.isEmpty ||
                                  validateRut(rutController.text);
                              _toggleBorderBlinking(hasFocus);
                              if (!_isRutValid) {
                                _startBlinking();
                              }
                            });
                          },
                          child: Container(
                            decoration: BoxDecoration(
                              border: Border.all(
                                color: _borderColor,
                                width: _borderColor == Colors.transparent
                                    ? 0
                                    : 1.5,
                              ),
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: TextField(
                              style: const TextStyle(
                                fontWeight: FontWeight.w500,
                                fontSize: 14,
                              ),
                              keyboardType: TextInputType.number,
                              controller: rutController,
                              decoration: _inputDecoration(
                                hint: 'Ingresa tu RUT',
                                prefixIcon: Icons.person_outline_rounded,
                              ),
                            ),
                          ),
                        ),

                        // Mensaje RUT inválido
                        if (!_isRutValid)
                          AnimatedOpacity(
                            opacity: _opacity,
                            duration: const Duration(seconds: 1),
                            child: const Padding(
                              padding: EdgeInsets.only(top: 8),
                              child: Text(
                                "El RUT ingresado no es válido",
                                style: TextStyle(
                                  color: Color(0xFFEF4444),
                                  fontSize: 12,
                                  fontWeight: FontWeight.w500,
                                ),
                              ),
                            ),
                          ),

                        const SizedBox(height: 20),

                        // Label Contraseña
                        const Text(
                          'Contraseña',
                          style: TextStyle(
                            fontSize: 13,
                            fontWeight: FontWeight.w600,
                            color: Color(0xFF374151),
                          ),
                        ),
                        const SizedBox(height: 8),

                        // Campo Contraseña
                        TextField(
                          style: const TextStyle(
                            fontWeight: FontWeight.w500,
                            fontSize: 14,
                          ),
                          controller: passwordController,
                          obscureText: obscureText,
                          decoration: _inputDecoration(
                            hint: 'Ingresa tu contraseña',
                            prefixIcon: Icons.lock_outline_rounded,
                            suffixIcon: GestureDetector(
                              onTap: () {
                                setState(() {
                                  obscureText = !obscureText;
                                });
                              },
                              child: Icon(
                                obscureText
                                    ? Icons.visibility_outlined
                                    : Icons.visibility_off_outlined,
                                color: Colors.grey.shade500,
                                size: 20,
                              ),
                            ),
                          ),
                        ),

                        // Olvidó contraseña
                        Align(
                          alignment: Alignment.centerRight,
                          child: TextButton(
                            onPressed: () {
                              sendCodePressed(context);
                            },
                            style: TextButton.styleFrom(
                              padding: const EdgeInsets.only(top: 12),
                              minimumSize: Size.zero,
                              tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                            ),
                            child: const Text(
                              '¿Olvidó su contraseña?',
                              style: TextStyle(
                                color: _primaryColor,
                                fontWeight: FontWeight.w600,
                                fontSize: 13,
                              ),
                            ),
                          ),
                        ),

                        const SizedBox(height: 28),

                        // Botón ENTRAR
                        SizedBox(
                          width: double.infinity,
                          height: 52,
                          child: ElevatedButton(
                            onPressed: () {
                              loginButtonPressed(context);
                            },
                            style: ElevatedButton.styleFrom(
                              backgroundColor: _primaryColor,
                              foregroundColor: Colors.white,
                              elevation: 0,
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(12),
                              ),
                            ),
                            child: const Text(
                              'ENTRAR',
                              style: TextStyle(
                                fontWeight: FontWeight.w700,
                                fontSize: 15,
                                letterSpacing: 1.2,
                              ),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),

                const SizedBox(height: 32),

                // Footer
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Container(
                      width: 40,
                      height: 0.5,
                      color: Colors.grey.shade400,
                    ),
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 12),
                      child: Text(
                        'by ®Terrasoft',
                        style: TextStyle(
                          fontWeight: FontWeight.w500,
                          color: Colors.grey.shade500,
                          fontSize: 13,
                        ),
                      ),
                    ),
                    Container(
                      width: 40,
                      height: 0.5,
                      color: Colors.grey.shade400,
                    ),
                  ],
                ),
                const SizedBox(height: 4),
                Text(
                  'v. 1.0.0',
                  style: TextStyle(color: Colors.grey.shade400, fontSize: 11),
                ),
                const SizedBox(height: 20),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
