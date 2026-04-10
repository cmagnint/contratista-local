import 'dart:convert';
import 'dart:io';
import 'dart:math';
import 'dart:ui';
import 'package:contratista/pages/mother_layout/contratacion/asociar_qr.dart';
import 'package:contratista/pages/mother_layout/contratacion/enrollment_db.dart';
import 'package:contratista/services/contratista_api_service.dart';
import 'package:contratista/services/worker_sinc_service.dart';
import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import 'package:flutter/services.dart';
import 'dart:async';
import 'package:google_mlkit_text_recognition/google_mlkit_text_recognition.dart';
import 'package:logger/logger.dart';
import 'package:image_picker/image_picker.dart';
import 'package:lottie/lottie.dart';
import 'package:image/image.dart' as img;
import 'package:contratista/utils/globals.dart';
import 'package:contratista/utils/signature_pad.dart';
import 'package:mobile_scanner/mobile_scanner.dart';
import 'package:path_provider/path_provider.dart';
import 'package:sembast/sembast_io.dart';
import 'package:path/path.dart' as p;
import 'package:contratista/services/finterprint_service.dart';

class ContratacionScreen extends StatefulWidget {
  final Map<String, String?> initialData;
  final VoidCallback onBack;

  const ContratacionScreen({
    super.key,
    required this.initialData,
    required this.onBack,
  });

  @override
  ContratacionScreenState createState() => ContratacionScreenState();
}

class ContratacionScreenState extends State<ContratacionScreen> {
  Logger logger = Logger();
  double _rotationAngle = 0;
  bool _isLoading = false;
  final List<String?> _imagePaths = [null, null];
  final _formKey = GlobalKey<FormState>();
  final Map<String, TextEditingController> _controllers = {
    'RUN': TextEditingController(),
    'APELLIDOS': TextEditingController(),
    'NOMBRES': TextEditingController(),
    'NACIONALIDAD': TextEditingController(),
    'TELEFONO': TextEditingController(),
    'CORREO': TextEditingController(),
    'DIRECCION': TextEditingController(),
  };

  final Map<String, FocusNode> _focusNodes = {};
  bool _isCameraInitialized = false;

  String _estadoCivil = 'Soltero(a)';
  String? _sexo;
  String _selectedDia = '01';
  String _selectedMes = '01';
  String _selectedAnio = '2000';
  String _metodoPago = 'Efectivo';
  String _banco = '';
  String _tipoCuenta = '';
  String _numeroCuenta = '';
  List<Map<String, dynamic>> _bancos = [];
  Map<String, int> _bancoMap = {};
  String? _selectedBancoNombre;
  final ImagePicker _picker = ImagePicker();
  final TextEditingController _numeroCuentaController = TextEditingController();
  CameraDescription? _camera;
  CameraController? _cameraController;
  String _tipoDocumento = 'Cédula Chilena';
  String _dni = '';
  final TextEditingController _dniController = TextEditingController();

  Uint8List? _signatureImage;
  String? _associatedQR;
  bool _isDisposing = false;
  final FingerPrintService _fingerprintService = FingerPrintService();
  String? huellaDigital;
  final TextEditingController _nicController = TextEditingController();

  // ── NUEVOS: prefijo telefónico y dominio de correo ──
  String _phonePrefix = '+56';
  String _emailDomain = '@gmail.com';
  bool _showRutKeyboard = false;
  TextEditingController? _activeRutController;

  static const List<Map<String, String>> _countryPrefixes = [
    {'label': '🇨🇱 +56', 'value': '+56'},
    {'label': '🇦🇷 +54', 'value': '+54'},
    {'label': '🇧🇴 +591', 'value': '+591'},
    {'label': '🇧🇷 +55', 'value': '+55'},
    {'label': '🇨🇴 +57', 'value': '+57'},
    {'label': '🇪🇨 +593', 'value': '+593'},
    {'label': '🇲🇽 +52', 'value': '+52'},
    {'label': '🇵🇾 +595', 'value': '+595'},
    {'label': '🇵🇪 +51', 'value': '+51'},
    {'label': '🇺🇾 +598', 'value': '+598'},
    {'label': '🇻🇪 +58', 'value': '+58'},
    {'label': '🇪🇸 +34', 'value': '+34'},
    {'label': '🇺🇸 +1', 'value': '+1'},
  ];

  static const List<String> _emailDomains = [
    '@gmail.com',
    '@outlook.com',
    '@hotmail.com',
    '@yahoo.com',
    '@icloud.com',
    '@live.com',
  ];

  @override
  void initState() {
    super.initState();
    _initializeCamera();
    _numeroCuentaController.text = _numeroCuenta;
    _dniController.text = _dni;
    _fetchBancos();

    for (var key in _controllers.keys) {
      _focusNodes[key] = FocusNode();
      if (key != 'RUN') {
        // RUN abre teclado custom, su propio listener lo cierra
        _focusNodes[key]!.addListener(() {
          if (_focusNodes[key]!.hasFocus && _showRutKeyboard) {
            setState(() => _showRutKeyboard = false);
          }
        });
      }
    }

    loggerGlobal.d('holding: ${userInfo.holding}');
  }

  @override
  void dispose() {
    _isDisposing = true;
    _numeroCuentaController.dispose();
    _dniController.dispose();
    _nicController.dispose();

    _focusNodes.forEach((key, node) {
      node.dispose();
    });

    _disposeCameraAsync();
    super.dispose();
  }

  Future<void> capturarHuellaDigital() async {
    try {
      // PASO 1: Instrucciones para conectar
      bool? continuar = await showDialog<bool>(
        context: context,
        barrierDismissible: false,
        builder: (context) => AlertDialog(
          title: const Text('Conectar Escáner'),
          content: const Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(Icons.usb, size: 48, color: Colors.blue),
              SizedBox(height: 16),
              Text(
                '1. Conecta el escáner Grow R102A al puerto USB\n'
                '2. Acepta el diálogo de permisos\n'
                '3. Marca "Usar por defecto"\n'
                '4. Presiona CONTINUAR',
                textAlign: TextAlign.left,
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context, false),
              child: const Text('Cancelar'),
            ),
            TextButton(
              onPressed: () => Navigator.pop(context, true),
              child: const Text('CONTINUAR'),
            ),
          ],
        ),
      );

      if (continuar != true) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Captura cancelada'),
              backgroundColor: Colors.orange,
            ),
          );
        }
        return;
      }

      // PASO 2: Intentar conectar con reintentos
      if (mounted) {
        showDialog(
          context: context,
          barrierDismissible: false,
          builder: (context) => const AlertDialog(
            content: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                CircularProgressIndicator(),
                SizedBox(height: 16),
                Text('Detectando escáner...'),
              ],
            ),
          ),
        );
      }

      bool conectado = false;
      int intentos = 0;

      while (!conectado && intentos < 5) {
        await Future.delayed(Duration(seconds: 1));
        conectado = await _fingerprintService.conectarDispositivo();
        intentos++;
        loggerGlobal.d('Intento $intentos: conectado=$conectado');
      }

      if (mounted) {
        Navigator.of(context, rootNavigator: true).pop();
      }

      if (!conectado) {
        if (mounted) {
          bool? reintentar = await showDialog<bool>(
            context: context,
            builder: (context) => AlertDialog(
              title: const Text('Escáner No Detectado'),
              content: const Text(
                'Verifica:\n'
                '• Scanner conectado al USB\n'
                '• Cable OTG funcionando\n'
                '• Permisos USB aceptados\n'
                '• LED verde encendido',
              ),
              actions: [
                TextButton(
                  onPressed: () => Navigator.pop(context, false),
                  child: const Text('Continuar Sin Huella'),
                ),
                TextButton(
                  onPressed: () => Navigator.pop(context, true),
                  child: const Text('Reintentar'),
                ),
              ],
            ),
          );

          if (reintentar == true) {
            await capturarHuellaDigital();
          }
        }
        return;
      }

      // PASO 3: Capturar huella
      if (mounted) {
        showDialog(
          context: context,
          barrierDismissible: false,
          builder: (context) => const AlertDialog(
            content: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                CircularProgressIndicator(),
                SizedBox(height: 16),
                Text('Coloca tu dedo en el escáner...'),
              ],
            ),
          ),
        );
      }

      final huellaData = await _fingerprintService.capturarHuella();

      if (mounted) {
        Navigator.of(context, rootNavigator: true).pop();
      }

      if (huellaData != null) {
        setState(() {
          huellaDigital = base64Encode(huellaData);
        });

        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Huella capturada exitosamente'),
              backgroundColor: Colors.green,
            ),
          );
        }
      } else {
        if (mounted) {
          bool? reintentar = await showDialog<bool>(
            context: context,
            builder: (context) => AlertDialog(
              title: const Text('Huella No Capturada'),
              content: const Text(
                'No se detectó el dedo.\n'
                '• Limpia el sensor\n'
                '• Presiona firmemente\n'
                '• Mantén 3-5 segundos',
              ),
              actions: [
                TextButton(
                  onPressed: () => Navigator.pop(context, false),
                  child: const Text('Continuar Sin Huella'),
                ),
                TextButton(
                  onPressed: () => Navigator.pop(context, true),
                  child: const Text('Reintentar'),
                ),
              ],
            ),
          );

          if (reintentar == true) {
            await capturarHuellaDigital();
          }
        }
      }

      await _fingerprintService.desconectar();
    } catch (e) {
      loggerGlobal.e('Error: $e');

      if (mounted) {
        Navigator.of(context, rootNavigator: true).pop();

        await showDialog(
          context: context,
          builder: (context) => AlertDialog(
            title: const Text('Error'),
            content: Text('$e'),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(context),
                child: const Text('OK'),
              ),
            ],
          ),
        );
      }
    }
  }

  Future<void> _disposeCameraAsync() async {
    if (_cameraController != null && _cameraController!.value.isInitialized) {
      try {
        await _cameraController!.dispose();
      } catch (e) {
        loggerGlobal.w('Error al liberar cámara: $e');
      }
    }
  }

  Future<void> _fetchBancos() async {
    try {
      ApiService apiService = ApiService();
      final response = await apiService.get('api_bancos/');

      if (response.statusCode == 200) {
        final List<dynamic> responseData = jsonDecode(response.body);
        setState(() {
          _bancos = List<Map<String, dynamic>>.from(responseData);
          _bancoMap = Map.fromIterables(
            responseData.map((banco) => banco['nombre'].toString()).toList(),
            responseData.map((banco) => banco['id'] as int).toList(),
          );
        });
        loggerGlobal.d('Bancos cargados: ${_bancos.length}');
      } else {
        loggerGlobal.e('Error al cargar bancos: ${response.statusCode}');
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Error al cargar bancos: ${response.reasonPhrase}'),
            ),
          );
        }
      }
    } catch (e) {
      loggerGlobal.e('Error en _fetchBancos: $e');
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text('Error al cargar bancos: $e')));
      }
    }
  }

  void _openSignaturePad({bool autoPromptFingerprint = true}) {
    // CAPTURAR EL CONTEXTO DEL STATE ANTES DE ABRIR EL DIÁLOGO
    final screenContext = context;

    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (BuildContext dialogContext) {
        return OrientationBuilder(
          builder: (context, orientation) {
            final isLandscape = orientation == Orientation.landscape;
            return Dialog(
              insetPadding: const EdgeInsets.all(8),
              child: Container(
                width: MediaQuery.of(context).size.width * 0.95,
                height:
                    MediaQuery.of(context).size.height *
                    (isLandscape ? 0.9 : 0.7),
                padding: const EdgeInsets.all(8.0),
                child: Column(
                  children: [
                    Text(
                      'Firma del trabajador',
                      style: TextStyle(
                        fontSize: isLandscape ? 18 : 16,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Expanded(
                      child: SignatureWidget(
                        onSignatureCapture: (Uint8List signature) async {
                          // 1. Guardar firma
                          setState(() {
                            _signatureImage = signature;
                          });

                          // 2. Cerrar diálogo de firma USANDO SU PROPIO CONTEXTO
                          Navigator.of(dialogContext).pop();

                          // 3. Esperar a que se cierre completamente
                          await Future.delayed(
                            const Duration(milliseconds: 500),
                          );

                          // 4. Mostrar SnackBar USANDO EL CONTEXTO DE LA PANTALLA
                          if (mounted) {
                            ScaffoldMessenger.of(screenContext).showSnackBar(
                              const SnackBar(
                                content: Text('Firma capturada exitosamente'),
                                backgroundColor: Colors.green,
                                duration: Duration(seconds: 2),
                              ),
                            );
                          }

                          // 5. Esperar un poco más
                          await Future.delayed(
                            const Duration(milliseconds: 700),
                          );

                          // 6. MOSTRAR DIÁLOGO DE HUELLA USANDO EL CONTEXTO DE LA PANTALLA
                          if (autoPromptFingerprint && mounted) {
                            final capturar = await showDialog<bool>(
                              context:
                                  screenContext, // USAR CONTEXTO DE LA PANTALLA, NO DEL DIÁLOGO
                              barrierDismissible: false,
                              builder: (BuildContext ctx) => AlertDialog(
                                title: const Text('Capturar Huella'),
                                content: const Text(
                                  '¿Deseas capturar la huella digital ahora?\n\n'
                                  'También puedes hacerlo después usando el botón "Huella".',
                                ),
                                actions: [
                                  TextButton(
                                    onPressed: () =>
                                        Navigator.of(ctx).pop(false),
                                    child: const Text('Después'),
                                  ),
                                  TextButton(
                                    onPressed: () =>
                                        Navigator.of(ctx).pop(true),
                                    child: const Text('Sí, Capturar'),
                                  ),
                                ],
                              ),
                            );

                            // 7. Si acepta, capturar huella
                            if (capturar == true && mounted) {
                              await capturarHuellaDigital();
                            }
                          }
                        },
                      ),
                    ),
                  ],
                ),
              ),
            );
          },
        );
      },
    );
  }

  Future<bool> asociarQR() async {
    try {
      String? scannedCode = await Navigator.push<String>(
        context,
        MaterialPageRoute(builder: (context) => const QRScannerScreen()),
      );

      if (scannedCode == null || scannedCode.isEmpty) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('No se escaneó ningún código QR válido'),
            ),
          );
        }
        return false;
      }

      setState(() {
        _associatedQR = scannedCode;
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Código QR asociado temporalmente')),
        );
      }
      return true;
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error al escanear el código QR: $e')),
        );
      }
      return false;
    }
  }

  void _rotateImage(StateSetter setState) {
    setState(() {
      _rotationAngle += pi / 2;
      if (_rotationAngle >= 2 * pi) {
        _rotationAngle -= 2 * pi;
      }
    });
  }

  Future<bool> _confirmPhoto(String imagePath, bool isFront) async {
    _rotationAngle = 0;
    return await showDialog<bool>(
          context: context,
          builder: (context) => StatefulBuilder(
            builder: (BuildContext context, StateSetter setState) {
              return AlertDialog(
                title: const Text('¿Usar esta foto?'),
                content: SingleChildScrollView(
                  child: Center(
                    child: Transform.rotate(
                      angle: _rotationAngle,
                      child: Image.file(
                        File(imagePath),
                        fit: BoxFit.contain,
                        width: 200,
                        height: 300,
                      ),
                    ),
                  ),
                ),
                actions: <Widget>[
                  TextButton(
                    onPressed: () => _rotateImage(setState),
                    child: const Text('Rotar'),
                  ),
                  TextButton(
                    onPressed: () => Navigator.of(context).pop(false),
                    child: const Text('No, volver a tomar'),
                  ),
                  TextButton(
                    onPressed: () async {
                      Navigator.of(context).pop(true);
                      if (isFront) {
                        await Future.delayed(const Duration(milliseconds: 100));
                        _showLoadingOverlay();
                      }
                    },
                    child: const Text('Sí, usar esta'),
                  ),
                ],
              );
            },
          ),
        ) ??
        false;
  }

  String _monthStringToNumber(String month) {
    switch (month.toLowerCase()) {
      case 'jan':
      case 'ene':
        return '01';
      case 'feb':
        return '02';
      case 'mar':
        return '03';
      case 'apr':
      case 'abr':
        return '04';
      case 'may':
        return '05';
      case 'jun':
        return '06';
      case 'jul':
        return '07';
      case 'aug':
      case 'ago':
        return '08';
      case 'sep':
        return '09';
      case 'oct':
        return '10';
      case 'nov':
        return '11';
      case 'dec':
      case 'dic':
        return '12';
      default:
        return '01';
    }
  }

  Future<String> _rotateAndSaveImage(String imagePath, double angle) async {
    final originalFile = File(imagePath);
    final originalImage = img.decodeImage(await originalFile.readAsBytes());

    if (originalImage == null) {
      return imagePath;
    }

    final rotatedImage = img.copyRotate(originalImage, angle: angle * 180 / pi);
    final newPath =
        '${originalFile.parent.path}/rotated_${originalFile.uri.pathSegments.last}';
    File(newPath).writeAsBytesSync(img.encodeJpg(rotatedImage));
    return newPath;
  }

  void _pickImageFromGallery(bool isFront) async {
    final pickedFile = await _picker.pickImage(source: ImageSource.gallery);
    if (pickedFile != null) {
      _confirmPictureAndRecognizeText(pickedFile.path, isFront);
    }
  }

  Future<void> _initializeCamera() async {
    if (_isDisposing) return;

    try {
      final cameras = await availableCameras();
      if (_isDisposing) return;

      CameraDescription? backCamera;
      try {
        backCamera = cameras.firstWhere(
          (camera) => camera.lensDirection == CameraLensDirection.back,
        );
      } catch (e) {
        if (cameras.isNotEmpty) {
          backCamera = cameras.first;
          loggerGlobal.w(
            'Cámara trasera no encontrada, usando: ${cameras.first.name}',
          );
        }
      }

      if (backCamera != null && !_isDisposing) {
        final controller = CameraController(
          backCamera,
          ResolutionPreset.veryHigh,
          enableAudio: false,
        );

        await controller.initialize();

        if (_isDisposing) {
          await controller.dispose();
          return;
        }

        if (mounted) {
          setState(() {
            _camera = backCamera;
            _cameraController = controller;
            _isCameraInitialized = true;
          });
        } else {
          await controller.dispose();
        }
      }
    } catch (e) {
      loggerGlobal.e('Error inicializando cámara: $e');
      if (mounted && !_isDisposing) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error al inicializar cámara: $e')),
        );
      }
    }
  }

  void _takePictureAndRecognizeText(bool isFront) async {
    if (!_isCameraInitialized || _camera == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text(
            'La cámara aún se está inicializando, por favor espera...',
          ),
        ),
      );
      return;
    }

    try {
      final imagePath = await Navigator.push<String>(
        context,
        MaterialPageRoute(builder: (context) => CameraScreen(camera: _camera!)),
      );

      if (imagePath != null) {
        _confirmPictureAndRecognizeText(imagePath, isFront);
      }
    } catch (e) {
      loggerGlobal.e('Error al tomar foto: $e');
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text('Error al tomar foto: $e')));
      }
    }
  }

  // FLUJO AUTOMÁTICO RESTAURADO
  void _confirmPictureAndRecognizeText(String imagePath, bool isFront) async {
    final confirm = await _confirmPhoto(imagePath, isFront);

    if (confirm == true) {
      final rotatedImage = await _rotateAndSaveImage(imagePath, _rotationAngle);
      setState(() {
        if (isFront) {
          _imagePaths[0] = rotatedImage;
        } else {
          _imagePaths[1] = rotatedImage;
        }
      });

      if (_tipoDocumento == 'Cédula Chilena') {
        if (isFront) {
          _showLoadingOverlay();
          final text = await readTextFromImageChilena(rotatedImage);
          setState(() {
            for (var field in _controllers.keys) {
              _controllers[field]!.text = text[field] ?? '';
            }
            if (text['SEXO'] != null) {
              _sexo = text['SEXO'];
            }
            if (text['FECHA_NACIMIENTO'] != null) {
              final fechaParts = text['FECHA_NACIMIENTO']!.split(' ');
              if (fechaParts.length == 3) {
                _selectedDia = fechaParts[0].padLeft(2, '0');
                _selectedMes = _monthStringToNumber(fechaParts[1]);
                _selectedAnio = fechaParts[2];
              }
            }
            _estadoCivil = 'Soltero(a)';
          });
          _hideLoadingOverlay();

          // AUTOMÁTICAMENTE IR A LA FOTO TRASERA
          await Future.delayed(const Duration(milliseconds: 500));
          if (mounted) {
            _takePictureAndRecognizeText(false);
          }
        } else {
          // DESPUÉS DE LA FOTO TRASERA, IR AUTOMÁTICAMENTE A LA FIRMA
          await Future.delayed(const Duration(milliseconds: 500));
          if (mounted) {
            _openSignaturePad(autoPromptFingerprint: true); // Flujo automático
          }
        }
      } else if (_tipoDocumento == 'Cédula Extranjera') {
        _showLoadingOverlay();
        if (isFront) {
          final extractedData = await readDNIFromImageExtranjera(rotatedImage);
          setState(() {
            _dni = extractedData['DNI'] ?? '';
            _dniController.text = _dni;
            _controllers['NACIONALIDAD']!.text =
                extractedData['NACIONALIDAD'] ?? '';
            loggerGlobal.d('DNI capturado: $_dni');
            loggerGlobal.d(
              'Nacionalidad capturada: ${_controllers['NACIONALIDAD']!.text}',
            );
          });
          _hideLoadingOverlay();

          // AUTOMÁTICAMENTE IR A LA FOTO TRASERA
          await Future.delayed(const Duration(milliseconds: 500));
          if (mounted) {
            _takePictureAndRecognizeText(false);
          }
        } else {
          final backData = await readBackTextFromImageExtranjera(rotatedImage);
          setState(() {
            _controllers['NOMBRES']!.text = backData['NOMBRES'] ?? '';
            _controllers['APELLIDOS']!.text = backData['APELLIDOS'] ?? '';
            if (backData['SEXO'] != null) {
              _sexo = backData['SEXO'];
            }
            _estadoCivil = normalizeEstadoCivil(
              backData['ESTADO_CIVIL'] ?? 'Soltero(a)',
            );

            if (backData['FECHA_NACIMIENTO'] != null) {
              final fechaParts = backData['FECHA_NACIMIENTO']!.split(' ');
              if (fechaParts.length == 5) {
                _selectedDia = fechaParts[0].padLeft(2, '0');
                _selectedMes = _monthStringToNumber(fechaParts[2]);
                _selectedAnio = fechaParts[4];
              }
            }

            loggerGlobal.d('Datos del reverso procesados');
          });
          _hideLoadingOverlay();

          // DESPUÉS DE LA FOTO TRASERA, IR AUTOMÁTICAMENTE A LA FIRMA
          await Future.delayed(const Duration(milliseconds: 500));
          if (mounted) {
            _openSignaturePad(autoPromptFingerprint: true); // Flujo automático
          }
        }
      }
    }
  }

  String normalizeEstadoCivil(String estadoCivil) {
    const validEstados = {
      'Soltero(a)',
      'Casado(a)',
      'Conviviente civil',
      'Separado(a) judicialmente',
      'Divorciado(a)',
      'Viudo(a)',
    };

    String normalizedEstado = estadoCivil.trim().toLowerCase();

    for (var estado in validEstados) {
      if (estado.toLowerCase().startsWith(normalizedEstado)) {
        return estado;
      }
    }

    return 'Soltero(a)';
  }

  Future<Map<String, String>> readTextFromImageChilena(String imagePath) async {
    final inputImage = InputImage.fromFilePath(imagePath);
    final textRecognizer = TextRecognizer(script: TextRecognitionScript.latin);
    final RecognizedText recognizedText = await textRecognizer.processImage(
      inputImage,
    );
    Map<String, String> cardData = {};

    final runPattern = RegExp(
      r'run\s*(\d{1,3}(?:\.\d{3})*-[\dkK])',
      caseSensitive: false,
    );
    final apellidosPattern = RegExp(
      r'apellidos\s*([\p{L}\s]+)(?=\s*nombres)',
      unicode: true,
      caseSensitive: false,
    );
    final nombresPattern = RegExp(
      r'nombres\s*([\p{L}\s]+)(?=\s*nacionalidad)',
      unicode: true,
      caseSensitive: false,
    );
    final nacionalidadPattern = RegExp(
      r'nacionalidad\s*([\p{L}]+)',
      unicode: true,
      caseSensitive: false,
    );
    final sexoPattern = RegExp(
      r'sexo\s*(\p{L})',
      unicode: true,
      caseSensitive: false,
    );
    final numDocPattern = RegExp(
      r'número\s*documento\s*(\d+)(?=\s*fecha de emisión|fecha de vencimiento)',
      caseSensitive: false,
    );
    final fechaNacimientoPattern = RegExp(
      r'(\d{2} [A-Z]{3} \d{4})',
      caseSensitive: false,
    );

    String combinedText = recognizedText.blocks
        .map((block) => block.text)
        .join('\n');
    logger.d('Texto combinado para regex: $combinedText');

    var runMatch = runPattern.firstMatch(combinedText);
    var apellidosMatch = apellidosPattern.firstMatch(combinedText);
    var nombresMatch = nombresPattern.firstMatch(combinedText);
    var nacionalidadMatch = nacionalidadPattern.firstMatch(combinedText);
    var sexoMatch = sexoPattern.firstMatch(combinedText);
    var numDocMatch = numDocPattern.firstMatch(combinedText);
    var fechaNacimientoMatch = fechaNacimientoPattern.firstMatch(combinedText);

    if (runMatch != null) cardData['RUN'] = runMatch.group(1)!;
    if (apellidosMatch != null) {
      cardData['APELLIDOS'] = apellidosMatch
          .group(1)!
          .trim()
          .replaceAll('\n', ' ');
    }
    if (nombresMatch != null) {
      cardData['NOMBRES'] = nombresMatch.group(1)!.trim();
    }
    if (nacionalidadMatch != null) {
      cardData['NACIONALIDAD'] = nacionalidadMatch.group(1)!;
    }
    if (sexoMatch != null) {
      String sexoDetectado = sexoMatch.group(1)!.toUpperCase();
      cardData['SEXO'] = (sexoDetectado == 'M' || sexoDetectado == 'F')
          ? sexoDetectado
          : 'M';
    }
    if (numDocMatch != null) {
      cardData['NUMERO DOCUMENTO'] = numDocMatch.group(1)!;
    }
    if (fechaNacimientoMatch != null) {
      cardData['FECHA_NACIMIENTO'] = fechaNacimientoMatch.group(1)!;
    }

    if (cardData['SEXO'] == 'P') {
      final sexoNearPattern = RegExp(r'sexo\s*([MF])', caseSensitive: false);
      final sexoNearMatch = sexoNearPattern.firstMatch(combinedText);
      if (sexoNearMatch != null) {
        String sexoDetectado = sexoNearMatch.group(1)!.toUpperCase();
        cardData['SEXO'] = (sexoDetectado == 'M' || sexoDetectado == 'F')
            ? sexoDetectado
            : 'M';
      }
    }

    textRecognizer.close();

    cardData = cardData.map((key, value) {
      return MapEntry(key, normalizeTextFrontalChilena(value));
    });

    cardData.forEach((key, value) => logger.d('Dato: $key, Valor: $value'));

    return cardData;
  }

  String normalizeTextFrontalChilena(String text) {
    text = text
        .replaceAll('Á', 'A')
        .replaceAll('É', 'E')
        .replaceAll('Í', 'I')
        .replaceAll('Ó', 'O')
        .replaceAll('Ú', 'U');
    text = text
        .replaceAll('á', 'a')
        .replaceAll('é', 'e')
        .replaceAll('í', 'i')
        .replaceAll('ó', 'o')
        .replaceAll('ú', 'u');
    text = text.replaceAll('Ñ', 'N').replaceAll('ñ', 'n');
    text = text.replaceAll(RegExp(r'[^\p{L}\p{N}\s]', unicode: true), '');
    text = text.replaceAll(RegExp(r'\s+'), ' ').trim();
    return text;
  }

  Future<Map<String, String>> readBackTextFromImageExtranjera(
    String imagePath,
  ) async {
    final inputImage = InputImage.fromFilePath(imagePath);
    final textRecognizer = TextRecognizer(script: TextRecognitionScript.latin);
    final RecognizedText recognizedText = await textRecognizer.processImage(
      inputImage,
    );
    Map<String, String> cardData = {};

    String combinedText = recognizedText.blocks
        .map((block) => block.text)
        .join('\n');
    loggerGlobal.d('Texto combinado (reverso): $combinedText');

    final nombrePattern = RegExp(
      r'A:\s*([\p{L}\s]+)(?:\n|$|Nacido)',
      unicode: true,
      dotAll: true,
    );
    final fechaNacimientoPattern = RegExp(
      r'Nacido el\s*(\d{1,2}\s+de\s+\w+\s+de\s+\d{4})',
      caseSensitive: false,
    );
    final nacionalidadPattern = RegExp(
      r'Nacionalidad\s*([\p{L}]+)',
      unicode: true,
    );
    final estadoCivilPattern = RegExp(
      r'Estado Civil\s*([\p{L}]+)',
      unicode: true,
    );
    final sexoPattern = RegExp(r'Sexo\s*([MF])', caseSensitive: false);

    var nombreMatch = nombrePattern.firstMatch(combinedText);
    if (nombreMatch != null) {
      String nombreCompleto = nombreMatch.group(1)!.trim();
      List<String> palabras = nombreCompleto.split(' ');

      String nombres = '';
      String apellidos = '';

      if (palabras.length == 2) {
        nombres = palabras[0];
        apellidos = palabras[1];
      } else if (palabras.length == 3) {
        nombres = palabras[0];
        apellidos = '${palabras[1]} ${palabras[2]}';
      } else if (palabras.length >= 4) {
        nombres = '${palabras[0]} ${palabras[1]}';
        apellidos = '${palabras[2]} ${palabras[3]}';
      }

      cardData['NOMBRES'] = nombres;
      cardData['APELLIDOS'] = apellidos;
      loggerGlobal.d('Nombres encontrados: ${cardData['NOMBRES']}');
      loggerGlobal.d('Apellidos encontrados: ${cardData['APELLIDOS']}');
    } else {
      loggerGlobal.d('Nombre completo no encontrado');
    }

    var fechaNacimientoMatch = fechaNacimientoPattern.firstMatch(combinedText);
    if (fechaNacimientoMatch != null) {
      cardData['FECHA_NACIMIENTO'] = fechaNacimientoMatch.group(1)!;
      loggerGlobal.d(
        'Fecha de nacimiento encontrada: ${cardData['FECHA_NACIMIENTO']}',
      );
    }

    var nacionalidadMatch = nacionalidadPattern.firstMatch(combinedText);
    if (nacionalidadMatch != null) {
      cardData['NACIONALIDAD'] = nacionalidadMatch.group(1)!;
      loggerGlobal.d('Nacionalidad encontrada: ${cardData['NACIONALIDAD']}');
    }

    var estadoCivilMatch = estadoCivilPattern.firstMatch(combinedText);
    if (estadoCivilMatch != null) {
      cardData['ESTADO_CIVIL'] = estadoCivilMatch.group(1)!;
      loggerGlobal.d('Estado civil encontrado: ${cardData['ESTADO_CIVIL']}');
    }

    var sexoMatch = sexoPattern.firstMatch(combinedText);
    if (sexoMatch != null) {
      String sexoDetectado = sexoMatch.group(1)!.toUpperCase();
      cardData['SEXO'] = (sexoDetectado == 'M' || sexoDetectado == 'F')
          ? sexoDetectado
          : 'M';
      loggerGlobal.d('Sexo encontrado: ${cardData['SEXO']}');
    }

    textRecognizer.close();

    cardData = cardData.map(
      (key, value) =>
          MapEntry(key, normalizeTextTraseraBolivianoFormatoUno(value)),
    );
    loggerGlobal.d('Datos capturados (reverso): $cardData');

    return cardData;
  }

  String normalizeTextTraseraBolivianoFormatoUno(String text) {
    text = text
        .replaceAll('Á', 'A')
        .replaceAll('É', 'E')
        .replaceAll('Í', 'I')
        .replaceAll('Ó', 'O')
        .replaceAll('Ú', 'U')
        .replaceAll('á', 'a')
        .replaceAll('é', 'e')
        .replaceAll('í', 'i')
        .replaceAll('ó', 'o')
        .replaceAll('ú', 'u')
        .replaceAll('Ñ', 'N')
        .replaceAll('ñ', 'n');
    text = text.replaceAll(RegExp(r'[^\p{L}\p{N}\s]', unicode: true), '');
    return text.replaceAll(RegExp(r'\s+'), ' ').trim();
  }

  Future<Map<String, String>> readDNIFromImageExtranjera(
    String imagePath,
  ) async {
    final inputImage = InputImage.fromFilePath(imagePath);
    final textRecognizer = TextRecognizer(script: TextRecognitionScript.latin);
    final RecognizedText recognizedText = await textRecognizer.processImage(
      inputImage,
    );

    String combinedText = recognizedText.blocks
        .map((block) => block.text)
        .join('\n');
    loggerGlobal.d('Texto combinado (frontal): $combinedText');

    Map<String, String> extractedData = {};

    final dniPattern = RegExp(r'\b(\d{7,8})\b');
    final boliviaPattern = RegExp(
      r'ESTADO PLURINACIONAL DE BOLIVIA',
      caseSensitive: false,
    );

    var dniMatches = dniPattern.allMatches(combinedText);
    if (dniMatches.isNotEmpty) {
      extractedData['DNI'] = dniMatches.first.group(1)!;
      loggerGlobal.d('DNI encontrado: ${extractedData['DNI']}');
    } else {
      loggerGlobal.d('DNI no encontrado');
    }

    if (boliviaPattern.hasMatch(combinedText)) {
      extractedData['NACIONALIDAD'] = 'BOLIVIANA';
      loggerGlobal.d(
        'Nacionalidad encontrada: ${extractedData['NACIONALIDAD']}',
      );
    } else {
      loggerGlobal.d('Nacionalidad no encontrada');
    }

    textRecognizer.close();

    return extractedData;
  }

  bool _validateFieldsFormat(Map<String, String> fields) {
    loggerGlobal.d('=== VALIDANDO FORMATO DE CAMPOS ===');

    try {
      final requiredFields = ['nombres', 'apellidos'];
      for (String field in requiredFields) {
        if (fields[field] == null || fields[field]!.isEmpty) {
          loggerGlobal.e('Campo requerido vacío: $field');
          return false;
        }
        if (fields[field]!.trim().isEmpty) {
          loggerGlobal.e('Campo requerido solo espacios: $field');
          return false;
        }
      }

      if (fields['fecha_nacimiento'] != null) {
        try {
          DateTime.parse(fields['fecha_nacimiento']!);
          loggerGlobal.d(
            'Fecha de nacimiento válida: ${fields['fecha_nacimiento']}',
          );
        } catch (e) {
          loggerGlobal.e(
            'Formato de fecha inválido: ${fields['fecha_nacimiento']} - Error: $e',
          );
          return false;
        }
      }

      if (fields['holding'] == null || fields['holding']!.isEmpty) {
        loggerGlobal.e('Holding vacío o nulo');
        return false;
      }

      if (fields['codigo_supervisor'] == null ||
          fields['codigo_supervisor']!.isEmpty) {
        loggerGlobal.e('Código supervisor vacío o nulo');
        return false;
      }

      bool hasRut = fields['rut'] != null && fields['rut']!.isNotEmpty;
      bool hasDni = fields['dni'] != null && fields['dni']!.isNotEmpty;

      if (!hasRut && !hasDni) {
        loggerGlobal.e('Ni RUT ni DNI proporcionados');
        return false;
      }

      final textFields = ['nombres', 'apellidos', 'nacionalidad'];
      for (String field in textFields) {
        if (fields[field] != null && fields[field]!.isNotEmpty) {
          String value = fields[field]!;
          if (value.contains('\n') ||
              value.contains('\r') ||
              value.contains('\t')) {
            loggerGlobal.w(
              'Campo $field contiene caracteres de control - limpiando',
            );
            fields[field] = value.replaceAll(RegExp(r'[\n\r\t]'), ' ').trim();
          }
        }
      }

      loggerGlobal.d('Validación de formato exitosa');
      return true;
    } catch (e) {
      loggerGlobal.e('Error durante validación de formato: $e');
      return false;
    }
  }

  bool _validateFiles(List<MapEntry<String, File>> files) {
    loggerGlobal.d('=== VALIDANDO ARCHIVOS ===');

    try {
      for (var fileEntry in files) {
        loggerGlobal.d('Validando archivo: ${fileEntry.key}');

        if (!fileEntry.value.existsSync()) {
          loggerGlobal.e('Archivo no existe: ${fileEntry.value.path}');
          return false;
        }

        int fileSize = fileEntry.value.lengthSync();
        loggerGlobal.d('Tamaño del archivo ${fileEntry.key}: $fileSize bytes');

        if (fileSize == 0) {
          loggerGlobal.e('Archivo vacío: ${fileEntry.key}');
          return false;
        }

        if (fileSize > 10 * 1024 * 1024) {
          loggerGlobal.e(
            'Archivo demasiado grande: ${fileEntry.key} - $fileSize bytes',
          );
          return false;
        }

        String path = fileEntry.value.path.toLowerCase();
        if (fileEntry.key.contains('image') || fileEntry.key == 'firma') {
          if (!path.endsWith('.png') &&
              !path.endsWith('.jpg') &&
              !path.endsWith('.jpeg')) {
            loggerGlobal.w(
              'Archivo ${fileEntry.key} no es imagen estándar: $path',
            );
          }
        }
      }

      loggerGlobal.d('Validación de archivos exitosa');
      return true;
    } catch (e) {
      loggerGlobal.e('Error durante validación de archivos: $e');
      return false;
    }
  }

  Future<void> _submitData() async {
    final EnrollmentDatabase _db = EnrollmentDatabase();

    loggerGlobal.d('=== INICIO DE _submitData ===');

    if (_formKey.currentState!.validate()) {
      loggerGlobal.d('Formulario válido');

      if (_signatureImage == null) {
        loggerGlobal.w('Error: Firma faltante');
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text(
              'La firma es obligatoria para todos los trabajadores.',
            ),
          ),
        );
        return;
      }
      loggerGlobal.d('Firma presente');

      // LA HUELLA AHORA ES OPCIONAL
      if (huellaDigital == null || huellaDigital!.isEmpty) {
        loggerGlobal.w('Advertencia: Huella digital no capturada (opcional)');
      } else {
        loggerGlobal.d('Huella digital presente');
      }

      if (_tipoDocumento == 'Cédula Chilena' &&
          (_controllers['RUN']!.text.isEmpty ||
              _controllers['NOMBRES']!.text.isEmpty ||
              _controllers['APELLIDOS']!.text.isEmpty)) {
        loggerGlobal.w('Error: Campos requeridos para chileno faltantes');
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text(
              'Para trabajadores chilenos, se requiere RUT, nombres, apellidos',
            ),
          ),
        );
        return;
      } else if (_tipoDocumento == 'Cédula Extranjera' &&
          (_dni.isEmpty ||
              _controllers['NOMBRES']!.text.isEmpty ||
              _controllers['APELLIDOS']!.text.isEmpty)) {
        loggerGlobal.w('Error: Campos requeridos para extranjero faltantes');
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text(
              'Para trabajadores extranjeros, se requiere DNI, nombres, apellidos',
            ),
          ),
        );
        return;
      }
      loggerGlobal.d('Validación de campos requeridos pasada');

      try {
        loggerGlobal.d('=== PREPARANDO DATOS ===');

        String? holding = await storage.read(key: 'holding');
        loggerGlobal.d('Holding obtenido del storage: $holding');

        String fechaNacimiento = '$_selectedAnio-$_selectedMes-$_selectedDia';
        loggerGlobal.d('Fecha de nacimiento calculada: $fechaNacimiento');

        // Combinar prefijo + número de teléfono
        final String telefonoCombinado =
            '$_phonePrefix${_controllers['TELEFONO']!.text}';

        // Combinar usuario + dominio de correo
        final String correoCombinado =
            '${_controllers['CORREO']!.text.toLowerCase()}$_emailDomain';

        final Map<String, String> fields = {
          'holding': holding ?? '',
          'sociedad': userInfo.sociedadSeleccionada,
          'fecha_ingreso': DateTime.now().toIso8601String().split('T')[0],
          'codigo_supervisor': widget.initialData['supervisor'] ?? '',
          'folio': widget.initialData['folio'] ?? '',
          'fundo': widget.initialData['fundo'] ?? '',
          'labor': widget.initialData['labor'] ?? '',
          'transportista': widget.initialData['transportista'] ?? '',
          'casa': widget.initialData['casa'] ?? '',
          'area': widget.initialData['area'] ?? '',
          'cargo': widget.initialData['cargo'] ?? '',
          'rut': _tipoDocumento == 'Cédula Chilena'
              ? _controllers['RUN']!.text
                    .replaceAll('.', '')
                    .replaceAll('-', '')
                    .toUpperCase()
              : '',
          'dni': _tipoDocumento == 'Cédula Extranjera'
              ? _dni.toUpperCase()
              : '',
          'nic': _nicController.text
              .replaceAll('.', '')
              .replaceAll('-', '')
              .toUpperCase(),
          'apellidos': _controllers['APELLIDOS']!.text.toUpperCase(),
          'nombres': _controllers['NOMBRES']!.text.toUpperCase(),
          'nacionalidad': _controllers['NACIONALIDAD']!.text.toUpperCase(),
          'sexo': _sexo ?? '',
          'estado_civil': _estadoCivil.toUpperCase(),
          'telefono': telefonoCombinado.toUpperCase(),
          'correo': correoCombinado,
          'direccion': _controllers['DIRECCION']!.text.toUpperCase(),
          'fecha_nacimiento': fechaNacimiento,
          'metodo_pago': _metodoPago.toUpperCase(),
          'banco': _banco,
          'tipo_cuenta_bancaria': _tipoCuenta.toUpperCase(),
          'numero_cuenta': _numeroCuenta,
          'estado': 'true',
        };

        loggerGlobal.d('=== SOCIEDAD ENVIADA ===');
        loggerGlobal.d('Sociedad ID: ${userInfo.sociedadSeleccionada}');
        loggerGlobal.d('=== CAMPOS PREPARADOS ===');
        fields.forEach((key, value) {
          loggerGlobal.d('  $key: $value');
        });

        if (_associatedQR != null) {
          fields['codigo_qr'] = _associatedQR!;
          loggerGlobal.d('Código QR agregado: $_associatedQR');
        }

        loggerGlobal.d('=== PREPARANDO ARCHIVOS ===');
        List<MapEntry<String, File>> files = [];

        if (_imagePaths[0] != null) {
          loggerGlobal.d('Preparando imagen frontal: ${_imagePaths[0]}');
          try {
            File frontFile = File(_imagePaths[0]!);
            if (await frontFile.exists()) {
              files.add(MapEntry('carnet_front_image', frontFile));
              loggerGlobal.d(
                'Imagen frontal agregada - Tamaño: ${await frontFile.length()} bytes',
              );
            } else {
              loggerGlobal.w(
                'Archivo de imagen frontal no existe: ${_imagePaths[0]}',
              );
            }
          } catch (e) {
            loggerGlobal.e('Error procesando imagen frontal: $e');
          }
        }

        if (_imagePaths[1] != null) {
          loggerGlobal.d('Preparando imagen trasera: ${_imagePaths[1]}');
          try {
            File backFile = File(_imagePaths[1]!);
            if (await backFile.exists()) {
              files.add(MapEntry('carnet_back_image', backFile));
              loggerGlobal.d(
                'Imagen trasera agregada - Tamaño: ${await backFile.length()} bytes',
              );
            } else {
              loggerGlobal.w(
                'Archivo de imagen trasera no existe: ${_imagePaths[1]}',
              );
            }
          } catch (e) {
            loggerGlobal.e('Error procesando imagen trasera: $e');
          }
        }

        if (_signatureImage != null) {
          loggerGlobal.d(
            'Preparando firma - Tamaño: ${_signatureImage!.length} bytes',
          );
          try {
            final tempDir = await getTemporaryDirectory();
            String fileName = _tipoDocumento == 'Cédula Chilena'
                ? 'firma_${_controllers['RUN']!.text.replaceAll('.', '').replaceAll('-', '')}.png'
                : 'firma_$_dni.png';

            loggerGlobal.d('Nombre de archivo de firma: $fileName');
            loggerGlobal.d('Directorio temporal: ${tempDir.path}');

            final file = await File('${tempDir.path}/$fileName').create();
            await file.writeAsBytes(_signatureImage!);
            files.add(MapEntry('firma', file));
            loggerGlobal.d(
              'Firma guardada y agregada - Tamaño final: ${await file.length()} bytes',
            );
          } catch (e) {
            loggerGlobal.e('Error procesando firma: $e');
            throw Exception('Error al procesar la firma: $e');
          }
        }

        // AGREGAR HUELLA SOLO SI ESTÁ PRESENTE
        if (huellaDigital != null && huellaDigital!.isNotEmpty) {
          loggerGlobal.d('Preparando huella digital');
          try {
            final tempDir = await getTemporaryDirectory();
            String fileName = _tipoDocumento == 'Cédula Chilena'
                ? 'huella_${_controllers['RUN']!.text.replaceAll('.', '').replaceAll('-', '')}.png'
                : 'huella_$_dni.png';

            loggerGlobal.d('Nombre de archivo de huella: $fileName');

            final huellaBytes = base64Decode(huellaDigital!);
            final file = await File('${tempDir.path}/$fileName').create();
            await file.writeAsBytes(huellaBytes);
            files.add(MapEntry('huella_digital', file));
            loggerGlobal.d(
              'Huella guardada y agregada - Tamaño final: ${await file.length()} bytes',
            );
          } catch (e) {
            loggerGlobal.e('Error procesando huella digital: $e');
            throw Exception('Error al procesar la huella digital: $e');
          }
        } else {
          loggerGlobal.d('Huella digital no proporcionada (opcional)');
        }

        loggerGlobal.d('Total de archivos preparados: ${files.length}');

        if (!_validateFiles(files)) {
          throw FormatException('Error en validación de archivos');
        }

        loggerGlobal.d('=== PREPARANDO CAMPOS LOCALES ===');
        Map<String, String> localFields = Map.from(fields);

        Map<String, String> additionalFields = {
          'labor_id': widget.initialData['labor'] ?? '',
          'empresa_transporte_id': widget.initialData['transportista'] ?? '',
          'vehiculo_id': widget.initialData['vehiculo'] ?? '',
          'horario': widget.initialData['horario'] ?? '',
          'codigo_supervisor': widget.initialData['supervisor'] ?? '',
        };

        loggerGlobal.d('Campos adicionales para BD local:');
        additionalFields.forEach((key, value) {
          loggerGlobal.d('  $key: $value');
        });

        localFields.addAll(additionalFields);

        loggerGlobal.d('=== TOTAL CAMPOS PARA BD LOCAL ===');
        loggerGlobal.d('Total de campos: ${localFields.length}');

        if (!_validateFieldsFormat(localFields)) {
          throw FormatException('Error en validación de formato de campos');
        }

        loggerGlobal.d('=== GUARDANDO EN BD LOCAL ===');
        await _db.saveEnrollment(localFields, files);
        loggerGlobal.d('Guardado en BD local exitoso');

        loggerGlobal.d('=== PROGRAMANDO SINCRONIZACIÓN ===');
        await WorkerSyncService.scheduleSync();
        loggerGlobal.d('Sincronización programada');

        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text(
                'Trabajador guardado localmente. Se sincronizará en breve.',
              ),
            ),
          );
        }

        if (_associatedQR != null) {
          loggerGlobal.d('=== GUARDANDO QR LOCAL ===');
          await _saveWorkerQRToLocal(fields, _associatedQR!);
          loggerGlobal.d('QR guardado localmente');
        }

        loggerGlobal.d('=== RESETEANDO FORMULARIO ===');
        _resetForm();

        loggerGlobal.d('=== LIMPIANDO ARCHIVOS TEMPORALES ===');
        for (var file in files) {
          try {
            if (await file.value.exists()) {
              await file.value.delete();
              loggerGlobal.d('Archivo temporal eliminado: ${file.value.path}');
            }
          } catch (e) {
            loggerGlobal.w(
              'Error eliminando archivo temporal ${file.value.path}: $e',
            );
          }
        }

        loggerGlobal.d('=== _submitData COMPLETADO EXITOSAMENTE ===');
      } catch (e, stackTrace) {
        loggerGlobal.e('=== ERROR EN _submitData ===');
        loggerGlobal.e('Error: $e');
        loggerGlobal.e('StackTrace: $stackTrace');

        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Error al guardar localmente: $e')),
          );
        }
      }
    } else {
      loggerGlobal.w('Formulario no válido');
    }
  }

  Future<void> _saveWorkerQRToLocal(
    Map<String, String> workerData,
    String qrCode,
  ) async {
    try {
      loggerGlobal.d('=== INICIO _saveWorkerQRToLocal ===');
      loggerGlobal.d('workerData recibido: $workerData');
      loggerGlobal.d('qrCode: $qrCode');

      final appDocumentDir = await getApplicationDocumentsDirectory();
      final dbPath = p.join(appDocumentDir.path, 'worker_data.db');
      final Database db = await databaseFactoryIo.openDatabase(dbPath);
      final store = intMapStoreFactory.store('workers');

      String idString = '';

      if (workerData['rut'] != null && workerData['rut']!.isNotEmpty) {
        idString = workerData['rut']!;
        loggerGlobal.d('Usando RUT como ID: $idString');
      } else if (workerData['dni'] != null && workerData['dni']!.isNotEmpty) {
        idString = workerData['dni']!;
        loggerGlobal.d('Usando DNI como ID: $idString');
      } else {
        loggerGlobal.w('Ni RUT ni DNI disponibles, usando ID por defecto');
        idString = '0';
      }

      idString = idString.replaceAll('.', '').replaceAll('-', '');

      if (idString.length > 1 &&
          (idString.contains('k') || idString.contains('K'))) {
        idString = idString.substring(0, idString.length - 1);
      }

      int workerId;
      try {
        workerId = int.parse(idString);
        loggerGlobal.d('ID parseado exitosamente: $workerId');
      } catch (e) {
        loggerGlobal.e('Error parseando ID "$idString": $e');
        workerId = DateTime.now().millisecondsSinceEpoch;
        loggerGlobal.w('Usando timestamp como ID fallback: $workerId');
      }

      final worker = Worker(
        id: workerId,
        name: '${workerData['nombres'] ?? ''} ${workerData['apellidos'] ?? ''}'
            .trim(),
        qrCode: qrCode,
        production: 0.0,
        cantidadUnidadControl: 0.0,
      );

      loggerGlobal.d('Worker creado: ${worker.toMap()}');

      await store.record(worker.id).put(db, worker.toMap());
      await db.close();

      loggerGlobal.d('Worker guardado exitosamente en BD local');
    } catch (e, stackTrace) {
      loggerGlobal.e('Error en _saveWorkerQRToLocal: $e');
      loggerGlobal.e('StackTrace: $stackTrace');
      rethrow;
    }
  }

  void _showLoadingOverlay() {
    setState(() {
      _isLoading = true;
    });
  }

  void _hideLoadingOverlay() {
    setState(() {
      _isLoading = false;
    });
  }

  void _showFullImage(dynamic image) {
    showDialog(
      context: context,
      builder: (context) {
        return Dialog(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              if (image is File)
                Image.file(image)
              else if (image is Uint8List)
                Image.memory(image),
              TextButton(
                onPressed: () => Navigator.of(context).pop(),
                child: const Text('Cerrar'),
              ),
            ],
          ),
        );
      },
    );
  }

  List<String> _getDays() {
    return List<String>.generate(31, (i) => (i + 1).toString().padLeft(2, '0'));
  }

  List<String> _getMonths() {
    return List<String>.generate(12, (i) => (i + 1).toString().padLeft(2, '0'));
  }

  List<String> _getYears() {
    int currentYear = DateTime.now().year;
    return List<String>.generate(100, (i) => (currentYear - i).toString());
  }

  String _getRutWithoutFormatting(String run) {
    String cleanRun = run.replaceAll(RegExp(r'[.\-]'), '');
    if (cleanRun.length > 1) {
      cleanRun = cleanRun.substring(0, cleanRun.length - 1);
    }
    return cleanRun;
  }

  void _updateNumeroCuenta(String value) {
    setState(() {
      _numeroCuenta = value;
    });
  }

  void _resetForm() {
    setState(() {
      _controllers.forEach((key, controller) => controller.clear());
      _imagePaths[0] = null;
      _imagePaths[1] = null;
      _estadoCivil = 'Soltero(a)';
      _sexo = null;
      _selectedDia = '01';
      _selectedMes = '01';
      _selectedAnio = '2000';
      _metodoPago = 'Efectivo';
      _banco = '';
      _selectedBancoNombre = null;
      _tipoCuenta = '';
      _numeroCuenta = '';
      _numeroCuentaController.clear();
      _dni = '';
      _dniController.clear();
      _tipoDocumento = 'Cédula Chilena';
      _signatureImage = null;
      huellaDigital = null;
      _nicController.clear();
      // Resetear prefijo y dominio
      _phonePrefix = '+56';
      _emailDomain = '@gmail.com';
    });
  }

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        GestureDetector(
          onTap: () {
            if (_showRutKeyboard) setState(() => _showRutKeyboard = false);
          },
          child: Scaffold(
            body: SingleChildScrollView(
              child: Form(
                key: _formKey,
                child: Column(
                  children: <Widget>[
                    Padding(
                      padding: const EdgeInsets.all(8.0),
                      child: DropdownButtonFormField<String>(
                        value: _tipoDocumento,
                        onChanged: (String? newValue) {
                          setState(() {
                            _resetForm();
                            _tipoDocumento = newValue!;
                          });
                        },
                        decoration: const InputDecoration(
                          labelText: 'Tipo de Documento',
                          border: OutlineInputBorder(),
                        ),
                        items: <String>['Cédula Chilena', 'Cédula Extranjera']
                            .map<DropdownMenuItem<String>>((String value) {
                              return DropdownMenuItem<String>(
                                value: value,
                                child: Text(value),
                              );
                            })
                            .toList(),
                      ),
                    ),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Expanded(
                          child: Stack(
                            children: [
                              Container(
                                decoration: BoxDecoration(
                                  border: Border.all(color: Colors.grey),
                                  borderRadius: BorderRadius.circular(8),
                                ),
                                padding: const EdgeInsets.all(16),
                                margin: const EdgeInsets.symmetric(
                                  vertical: 20,
                                ),
                                child: Column(
                                  children: [
                                    Row(
                                      mainAxisAlignment:
                                          MainAxisAlignment.center,
                                      children: [
                                        IconButton(
                                          icon: const Icon(Icons.photo_library),
                                          onPressed: () =>
                                              _pickImageFromGallery(true),
                                        ),
                                        IconButton(
                                          icon: const Icon(Icons.camera_alt),
                                          onPressed: () =>
                                              _takePictureAndRecognizeText(
                                                true,
                                              ),
                                        ),
                                      ],
                                    ),
                                  ],
                                ),
                              ),
                              Positioned(
                                left: 16,
                                right: 16,
                                top: 0,
                                child: Container(
                                  color: Colors.white,
                                  padding: const EdgeInsets.symmetric(
                                    horizontal: 8,
                                  ),
                                  child: const Text(
                                    'Carnet Frontal',
                                    style: TextStyle(
                                      fontSize: 16,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),
                        const SizedBox(width: 20),
                        Expanded(
                          child: Stack(
                            children: [
                              Container(
                                decoration: BoxDecoration(
                                  border: Border.all(color: Colors.grey),
                                  borderRadius: BorderRadius.circular(8),
                                ),
                                padding: const EdgeInsets.all(16),
                                margin: const EdgeInsets.symmetric(
                                  vertical: 20,
                                ),
                                child: Column(
                                  children: [
                                    Row(
                                      mainAxisAlignment:
                                          MainAxisAlignment.center,
                                      children: [
                                        IconButton(
                                          icon: const Icon(Icons.photo_library),
                                          onPressed: () =>
                                              _pickImageFromGallery(false),
                                        ),
                                        IconButton(
                                          icon: const Icon(Icons.camera_alt),
                                          onPressed: () =>
                                              _takePictureAndRecognizeText(
                                                false,
                                              ),
                                        ),
                                      ],
                                    ),
                                  ],
                                ),
                              ),
                              Positioned(
                                left: 16,
                                right: 16,
                                top: 0,
                                child: Container(
                                  color: Colors.white,
                                  padding: const EdgeInsets.symmetric(
                                    horizontal: 8,
                                  ),
                                  child: const Text(
                                    'Carnet Trasero',
                                    style: TextStyle(
                                      fontSize: 16,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        ElevatedButton(
                          onPressed: asociarQR,
                          child: const Text('Asociar QR'),
                        ),
                        const SizedBox(width: 12),
                        ElevatedButton.icon(
                          onPressed: () =>
                              _openSignaturePad(autoPromptFingerprint: false),
                          icon: const Icon(Icons.draw),
                          label: const Text('Firmar'),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: _signatureImage != null
                                ? Colors.green
                                : null,
                          ),
                        ),
                        const SizedBox(width: 12),
                        ElevatedButton.icon(
                          onPressed: capturarHuellaDigital,
                          icon: const Icon(Icons.fingerprint),
                          label: const Text('Huella'),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: huellaDigital != null
                                ? Colors.green
                                : null,
                          ),
                        ),
                      ],
                    ),
                    if (_tipoDocumento == 'Cédula Chilena')
                      Padding(
                        padding: const EdgeInsets.all(8.0),
                        child: TextFormField(
                          controller: _controllers['RUN'],
                          focusNode: _focusNodes['RUN'],
                          readOnly: true,
                          showCursor: true,
                          onTap: () {
                            setState(() {
                              _showRutKeyboard = true;
                              _activeRutController = _controllers['RUN'];
                            });
                          },
                          decoration: const InputDecoration(
                            labelText: 'RUT *',
                            border: OutlineInputBorder(),
                          ),
                          validator: (value) {
                            if (value == null || value.isEmpty) {
                              return 'RUT es requerido para trabajadores chilenos';
                            }
                            return null;
                          },
                        ),
                      ),
                    if (_tipoDocumento == 'Cédula Extranjera') ...[
                      Padding(
                        padding: const EdgeInsets.all(8.0),
                        child: TextFormField(
                          textCapitalization: TextCapitalization.characters,
                          decoration: const InputDecoration(
                            labelText: 'DNI *',
                            border: OutlineInputBorder(),
                          ),
                          controller: _dniController,
                          onChanged: (value) {
                            _dni = value;
                          },
                          validator: (value) {
                            if (value == null || value.isEmpty) {
                              return 'DNI es requerido para trabajadores extranjeros';
                            }
                            return null;
                          },
                        ),
                      ),
                      Padding(
                        padding: const EdgeInsets.all(8.0),
                        child: TextFormField(
                          decoration: const InputDecoration(
                            labelText: 'NIC',
                            border: OutlineInputBorder(),
                          ),
                          controller: _nicController,
                          readOnly: true,
                          showCursor: true,
                          onTap: () {
                            setState(() {
                              _showRutKeyboard = true;
                              _activeRutController = _nicController;
                            });
                          },
                        ),
                      ),
                    ],
                    Padding(
                      padding: const EdgeInsets.all(8.0),
                      child: TextFormField(
                        textCapitalization: TextCapitalization.characters,
                        controller: _controllers['NOMBRES'],
                        focusNode: _focusNodes['NOMBRES'],
                        decoration: const InputDecoration(
                          labelText: 'Nombres *',
                          border: OutlineInputBorder(),
                        ),
                        validator: (value) {
                          if (value == null || value.isEmpty) {
                            return 'Nombres son requeridos';
                          }
                          return null;
                        },
                      ),
                    ),
                    Padding(
                      padding: const EdgeInsets.all(8.0),
                      child: TextFormField(
                        textCapitalization: TextCapitalization.characters,
                        controller: _controllers['APELLIDOS'],
                        focusNode: _focusNodes['APELLIDOS'],
                        decoration: const InputDecoration(
                          labelText: 'Apellidos *',
                          border: OutlineInputBorder(),
                        ),
                        validator: (value) {
                          if (value == null || value.isEmpty) {
                            return 'Apellidos son requeridos';
                          }
                          return null;
                        },
                      ),
                    ),
                    Padding(
                      padding: const EdgeInsets.all(8.0),
                      child: DropdownButtonFormField<String>(
                        value: _controllers['NACIONALIDAD']!.text.isNotEmpty
                            ? _controllers['NACIONALIDAD']!.text
                            : null,
                        decoration: const InputDecoration(
                          labelText: 'NACIONALIDAD',
                          border: OutlineInputBorder(),
                        ),
                        onChanged: (String? newValue) {
                          setState(() {
                            _controllers['NACIONALIDAD']!.text = newValue ?? '';
                          });
                        },
                        items:
                            <Map<String, String>>[
                              {'label': '🇨🇱 CHILENA', 'value': 'CHILENA'},
                              {'label': '🇧🇴 BOLIVIANA', 'value': 'BOLIVIANA'},
                              {'label': '🇵🇪 PERUANA', 'value': 'PERUANA'},
                              {
                                'label': '🇻🇪 VENEZOLANA',
                                'value': 'VENEZOLANA',
                              },
                              {
                                'label': '🇨🇴 COLOMBIANA',
                                'value': 'COLOMBIANA',
                              },
                              {'label': '🇦🇷 ARGENTINA', 'value': 'ARGENTINA'},
                              {
                                'label': '🇪🇨 ECUATORIANA',
                                'value': 'ECUATORIANA',
                              },
                              {'label': '🇵🇾 PARAGUAYA', 'value': 'PARAGUAYA'},
                              {'label': '🇺🇾 URUGUAYA', 'value': 'URUGUAYA'},
                              {'label': '🇧🇷 BRASILEÑA', 'value': 'BRASILEÑA'},
                              {'label': '🌐 OTRA', 'value': 'OTRA'},
                            ].map<DropdownMenuItem<String>>((item) {
                              return DropdownMenuItem<String>(
                                value: item['value'],
                                child: Text(item['label']!),
                              );
                            }).toList(),
                      ),
                    ),
                    Padding(
                      padding: const EdgeInsets.all(8.0),
                      child: TextFormField(
                        textCapitalization: TextCapitalization.characters,
                        controller: _controllers['DIRECCION'],
                        focusNode: _focusNodes['DIRECCION'],
                        decoration: const InputDecoration(
                          labelText: 'DIRECCION',
                          border: OutlineInputBorder(),
                        ),
                      ),
                    ),
                    Padding(
                      padding: const EdgeInsets.all(8.0),
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Container(
                            decoration: BoxDecoration(
                              border: Border.all(color: Colors.grey),
                              borderRadius: BorderRadius.circular(4),
                            ),
                            padding: const EdgeInsets.symmetric(horizontal: 8),
                            height: 56,
                            child: DropdownButtonHideUnderline(
                              child: DropdownButton<String>(
                                value: _phonePrefix,
                                onChanged: (String? newValue) {
                                  setState(() {
                                    _phonePrefix = newValue!;
                                  });
                                },
                                items: _countryPrefixes
                                    .map<DropdownMenuItem<String>>((item) {
                                      return DropdownMenuItem<String>(
                                        value: item['value'],
                                        child: Text(item['label']!),
                                      );
                                    })
                                    .toList(),
                              ),
                            ),
                          ),
                          const SizedBox(width: 8),
                          Expanded(
                            child: TextFormField(
                              controller: _controllers['TELEFONO'],
                              focusNode: _focusNodes['TELEFONO'],
                              keyboardType: TextInputType.phone,
                              inputFormatters: [
                                FilteringTextInputFormatter.digitsOnly,
                              ],
                              decoration: const InputDecoration(
                                labelText: 'TELEFONO',
                                border: OutlineInputBorder(),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                    Padding(
                      padding: const EdgeInsets.all(8.0),
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Expanded(
                            child: TextFormField(
                              controller: _controllers['CORREO'],
                              focusNode: _focusNodes['CORREO'],
                              keyboardType: TextInputType.emailAddress,
                              decoration: const InputDecoration(
                                labelText: 'CORREO',
                                border: OutlineInputBorder(),
                              ),
                            ),
                          ),
                          const SizedBox(width: 8),
                          Container(
                            decoration: BoxDecoration(
                              border: Border.all(color: Colors.grey),
                              borderRadius: BorderRadius.circular(4),
                            ),
                            padding: const EdgeInsets.symmetric(horizontal: 8),
                            height: 56,
                            child: DropdownButtonHideUnderline(
                              child: DropdownButton<String>(
                                value: _emailDomain,
                                onChanged: (String? newValue) {
                                  setState(() {
                                    _emailDomain = newValue!;
                                  });
                                },
                                items: _emailDomains
                                    .map<DropdownMenuItem<String>>((domain) {
                                      return DropdownMenuItem<String>(
                                        value: domain,
                                        child: Text(domain),
                                      );
                                    })
                                    .toList(),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                    Padding(
                      padding: const EdgeInsets.all(8.0),
                      child: DropdownButtonFormField<String>(
                        value: _sexo,
                        onChanged: (String? newValue) {
                          setState(() {
                            _sexo = newValue;
                          });
                        },
                        decoration: const InputDecoration(
                          labelText: 'SEXO *',
                          border: OutlineInputBorder(),
                        ),
                        items: <String>['F', 'M'].map<DropdownMenuItem<String>>(
                          (String value) {
                            return DropdownMenuItem<String>(
                              value: value,
                              child: Text(value),
                            );
                          },
                        ).toList(),
                        validator: (value) {
                          if (value == null || value.isEmpty)
                            return 'Sexo es requerido';
                          return null;
                        },
                      ),
                    ),
                    Padding(
                      padding: const EdgeInsets.all(8.0),
                      child: DropdownButtonFormField<String>(
                        value: _estadoCivil,
                        onChanged: (String? newValue) {
                          setState(() {
                            _estadoCivil = newValue!;
                          });
                        },
                        decoration: const InputDecoration(
                          labelText: 'Estado Civil',
                          border: OutlineInputBorder(),
                        ),
                        items:
                            <String>[
                              'Soltero(a)',
                              'Casado(a)',
                              'Conviviente civil',
                              'Separado(a) judicialmente',
                              'Divorciado(a)',
                              'Viudo(a)',
                            ].map<DropdownMenuItem<String>>((String value) {
                              return DropdownMenuItem<String>(
                                value: value,
                                child: Text(value),
                              );
                            }).toList(),
                      ),
                    ),
                    Padding(
                      padding: const EdgeInsets.all(8.0),
                      child: Container(
                        decoration: BoxDecoration(
                          border: Border.all(color: Colors.grey),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        padding: const EdgeInsets.all(8.0),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text(
                              'Fecha de nacimiento',
                              style: TextStyle(
                                fontSize: 16,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            const SizedBox(height: 8.0),
                            Row(
                              children: [
                                Expanded(
                                  child: DropdownButtonFormField<String>(
                                    value: _selectedDia,
                                    onChanged: (String? newValue) {
                                      setState(() => _selectedDia = newValue!);
                                    },
                                    decoration: const InputDecoration(
                                      labelText: 'Día',
                                      border: OutlineInputBorder(),
                                    ),
                                    items: _getDays()
                                        .map<DropdownMenuItem<String>>((
                                          String value,
                                        ) {
                                          return DropdownMenuItem<String>(
                                            value: value,
                                            child: Text(value),
                                          );
                                        })
                                        .toList(),
                                  ),
                                ),
                                const SizedBox(width: 8.0),
                                Expanded(
                                  child: DropdownButtonFormField<String>(
                                    value: _selectedMes,
                                    onChanged: (String? newValue) {
                                      setState(() => _selectedMes = newValue!);
                                    },
                                    decoration: const InputDecoration(
                                      labelText: 'Mes',
                                      border: OutlineInputBorder(),
                                    ),
                                    items: _getMonths()
                                        .map<DropdownMenuItem<String>>((
                                          String value,
                                        ) {
                                          return DropdownMenuItem<String>(
                                            value: value,
                                            child: Text(value),
                                          );
                                        })
                                        .toList(),
                                  ),
                                ),
                                const SizedBox(width: 8.0),
                                Expanded(
                                  child: DropdownButtonFormField<String>(
                                    value: _selectedAnio,
                                    onChanged: (String? newValue) {
                                      setState(() => _selectedAnio = newValue!);
                                    },
                                    decoration: const InputDecoration(
                                      labelText: 'Año',
                                      border: OutlineInputBorder(),
                                    ),
                                    items: _getYears()
                                        .map<DropdownMenuItem<String>>((
                                          String value,
                                        ) {
                                          return DropdownMenuItem<String>(
                                            value: value,
                                            child: Text(value),
                                          );
                                        })
                                        .toList(),
                                  ),
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                    ),
                    Padding(
                      padding: const EdgeInsets.all(8.0),
                      child: DropdownButtonFormField<String>(
                        value: _metodoPago,
                        onChanged: (String? newValue) {
                          setState(() {
                            _metodoPago = newValue!;
                            if (_metodoPago == 'Efectivo') {
                              _banco = '';
                              _selectedBancoNombre = null;
                              _tipoCuenta = '';
                              _numeroCuenta = '';
                              _numeroCuentaController.clear();
                            } else if (_metodoPago == 'Transferencia') {
                              final bancoEstado = _bancos.firstWhere(
                                (b) => b['nombre']
                                    .toString()
                                    .toLowerCase()
                                    .contains('estado'),
                                orElse: () => {},
                              );
                              if (bancoEstado.isNotEmpty) {
                                _selectedBancoNombre = bancoEstado['nombre']
                                    .toString();
                                _banco = bancoEstado['id'].toString();
                              }
                              _tipoCuenta = 'CUENTA RUT';
                              if (_controllers['RUN']!.text.isNotEmpty) {
                                _numeroCuenta = _getRutWithoutFormatting(
                                  _controllers['RUN']!.text,
                                );
                                _numeroCuentaController.text = _numeroCuenta;
                              }
                            }
                          });
                        },
                        decoration: const InputDecoration(
                          labelText: 'Método de Pago',
                          border: OutlineInputBorder(),
                        ),
                        items: <String>['Efectivo', 'Transferencia']
                            .map<DropdownMenuItem<String>>((String value) {
                              return DropdownMenuItem<String>(
                                value: value,
                                child: Text(value),
                              );
                            })
                            .toList(),
                      ),
                    ),
                    if (_metodoPago == 'Transferencia') ...[
                      Padding(
                        padding: const EdgeInsets.all(8.0),
                        child: DropdownButtonFormField<String>(
                          value: _selectedBancoNombre,
                          hint: const Text('Seleccione un banco'),
                          onChanged: (String? newValue) {
                            setState(() {
                              _selectedBancoNombre = newValue;
                              _banco = _bancoMap[newValue]?.toString() ?? '';
                            });
                            loggerGlobal.d(
                              'Banco seleccionado: $newValue (ID: $_banco)',
                            );
                          },
                          decoration: const InputDecoration(
                            labelText: 'Banco',
                            border: OutlineInputBorder(),
                          ),
                          items: _bancos.map((banco) {
                            return DropdownMenuItem<String>(
                              value: banco['nombre'].toString(),
                              child: Text(banco['nombre'].toString()),
                            );
                          }).toList(),
                        ),
                      ),
                      Padding(
                        padding: const EdgeInsets.all(8.0),
                        child: DropdownButtonFormField<String>(
                          value: _tipoCuenta.isNotEmpty ? _tipoCuenta : null,
                          onChanged: (String? newValue) {
                            setState(() {
                              _tipoCuenta = newValue!;
                              if (_tipoCuenta == 'CUENTA RUT' &&
                                  _controllers['RUN'] != null) {
                                _numeroCuenta = _getRutWithoutFormatting(
                                  _controllers['RUN']!.text,
                                );
                                _numeroCuentaController.text = _numeroCuenta;
                              } else {
                                _numeroCuenta = '';
                                _numeroCuentaController.clear();
                              }
                            });
                          },
                          decoration: const InputDecoration(
                            labelText: 'TIPO DE CUENTA',
                            border: OutlineInputBorder(),
                          ),
                          items:
                              <String>[
                                'CUENTA RUT',
                                'VISTA/CHEQUERA ELECTRÓNICA',
                                'CUENTA DE AHORRO',
                                'CUENTA CORRIENTE',
                              ].map<DropdownMenuItem<String>>((String value) {
                                return DropdownMenuItem<String>(
                                  value: value,
                                  child: Text(value),
                                );
                              }).toList(),
                        ),
                      ),
                      Padding(
                        padding: const EdgeInsets.all(8.0),
                        child: TextFormField(
                          textCapitalization: TextCapitalization.characters,
                          controller: _numeroCuentaController,
                          onChanged: _updateNumeroCuenta,
                          keyboardType: TextInputType.number,
                          inputFormatters: <TextInputFormatter>[
                            FilteringTextInputFormatter.digitsOnly,
                          ],
                          decoration: const InputDecoration(
                            labelText: 'Número de Cuenta',
                            border: OutlineInputBorder(),
                          ),
                        ),
                      ),
                    ],
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        if (_imagePaths[0] != null)
                          Expanded(
                            child: Padding(
                              padding: const EdgeInsets.all(8.0),
                              child: Column(
                                children: [
                                  GestureDetector(
                                    onTap: () =>
                                        _showFullImage(File(_imagePaths[0]!)),
                                    child: Image.file(
                                      File(_imagePaths[0]!),
                                      fit: BoxFit.cover,
                                      width: 100,
                                      height: 100,
                                    ),
                                  ),
                                  const SizedBox(height: 4),
                                  const Text(
                                    'Carnet Frontal',
                                    style: TextStyle(
                                      fontSize: 10,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ),
                        if (_imagePaths[1] != null)
                          Expanded(
                            child: Padding(
                              padding: const EdgeInsets.all(8.0),
                              child: Column(
                                children: [
                                  GestureDetector(
                                    onTap: () =>
                                        _showFullImage(File(_imagePaths[1]!)),
                                    child: Image.file(
                                      File(_imagePaths[1]!),
                                      fit: BoxFit.cover,
                                      width: 100,
                                      height: 100,
                                    ),
                                  ),
                                  const SizedBox(height: 4),
                                  const Text(
                                    'Carnet Trasero',
                                    style: TextStyle(
                                      fontSize: 10,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ),
                        if (_signatureImage != null)
                          Expanded(
                            child: Padding(
                              padding: const EdgeInsets.all(8.0),
                              child: Column(
                                children: [
                                  GestureDetector(
                                    onTap: () =>
                                        _showFullImage(_signatureImage!),
                                    child: Image.memory(
                                      _signatureImage!,
                                      fit: BoxFit.cover,
                                      width: 100,
                                      height: 100,
                                    ),
                                  ),
                                  const SizedBox(height: 4),
                                  const Text(
                                    'Firma',
                                    style: TextStyle(
                                      fontSize: 10,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ),
                        if (huellaDigital != null)
                          Expanded(
                            child: Padding(
                              padding: const EdgeInsets.all(8.0),
                              child: Column(
                                children: [
                                  GestureDetector(
                                    onTap: () => _showFullImage(
                                      base64Decode(huellaDigital!),
                                    ),
                                    child: Image.memory(
                                      base64Decode(huellaDigital!),
                                      fit: BoxFit.cover,
                                      width: 100,
                                      height: 100,
                                    ),
                                  ),
                                  const SizedBox(height: 4),
                                  const Text(
                                    'Huella Digital',
                                    style: TextStyle(
                                      fontSize: 10,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ),
                      ],
                    ),
                    Padding(
                      padding: const EdgeInsets.only(bottom: 85),
                      child: ElevatedButton(
                        onPressed: _submitData,
                        style: ButtonStyle(
                          shape:
                              WidgetStateProperty.all<RoundedRectangleBorder>(
                                RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(4.0),
                                ),
                              ),
                        ),
                        child: const Text('Contratar Trabajador'),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
        if (_isLoading)
          Stack(
            children: [
              BackdropFilter(
                filter: ImageFilter.blur(sigmaX: 5, sigmaY: 5),
                child: Container(color: Colors.black.withValues(alpha: 0.5)),
              ),
              Center(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Lottie.asset(
                      'assets/animations/loading_blue.json',
                      repeat: true,
                    ),
                    const SizedBox(height: 20),
                    _LoadingText(),
                  ],
                ),
              ),
            ],
          ),
        if (_showRutKeyboard && _activeRutController != null)
          Positioned(
            bottom: 0,
            left: 0,
            right: 0,
            child: GestureDetector(
              onTap: () {},
              child: RutKeyboard(
                controller: _activeRutController!,
                onClose: () => setState(() => _showRutKeyboard = false),
                isRut: _activeRutController == _controllers['RUN'],
              ),
            ),
          ),
      ],
    );
  }
}

class _LoadingText extends StatefulWidget {
  @override
  __LoadingTextState createState() => __LoadingTextState();
}

class __LoadingTextState extends State<_LoadingText> {
  String _loadingText = 'Cargando datos';
  late Timer _timer;
  int _dotCount = 0;

  @override
  void initState() {
    super.initState();
    _timer = Timer.periodic(const Duration(milliseconds: 500), (timer) {
      setState(() {
        _dotCount = (_dotCount + 1) % 4;
        _loadingText = 'Cargando datos${'.' * _dotCount}';
      });
    });
  }

  @override
  void dispose() {
    _timer.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Text(
      _loadingText,
      style: const TextStyle(
        fontWeight: FontWeight.bold,
        decoration: TextDecoration.none,
        fontSize: 18.0,
        color: Colors.white,
      ),
    );
  }
}

class CameraScreen extends StatefulWidget {
  final CameraDescription camera;

  const CameraScreen({super.key, required this.camera});

  @override
  CameraScreenState createState() => CameraScreenState();
}

class CameraScreenState extends State<CameraScreen> {
  late CameraController _controller;
  late Future<void> _initializeControllerFuture;
  bool _isFlashOn = false;

  @override
  void initState() {
    super.initState();
    _controller = CameraController(widget.camera, ResolutionPreset.veryHigh);
    _initializeControllerFuture = _controller.initialize();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _toggleFlash() {
    setState(() {
      _isFlashOn = !_isFlashOn;
      _controller.setFlashMode(_isFlashOn ? FlashMode.torch : FlashMode.off);
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: FutureBuilder<void>(
        future: _initializeControllerFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.done) {
            return Stack(
              fit: StackFit.expand,
              children: [
                CameraPreview(_controller),
                Positioned(
                  bottom: 16.0,
                  left: 0,
                  right: 0,
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                    children: [
                      IconButton(
                        icon: Icon(
                          _isFlashOn ? Icons.flash_off : Icons.flash_on,
                        ),
                        color: Colors.white,
                        onPressed: _toggleFlash,
                      ),
                      FloatingActionButton(
                        child: const Icon(Icons.camera_alt),
                        onPressed: () async {
                          try {
                            await _initializeControllerFuture;
                            final image = await _controller.takePicture();
                            if (!mounted) return;
                            if (context.mounted) {
                              Navigator.of(context).pop(image.path);
                            }
                          } catch (e) {
                            loggerGlobal.d(e);
                          }
                        },
                      ),
                    ],
                  ),
                ),
              ],
            );
          } else {
            return const Center(child: CircularProgressIndicator());
          }
        },
      ),
    );
  }
}

class QRScannerScreen extends StatelessWidget {
  const QRScannerScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Escanear Código QR')),
      body: MobileScanner(
        onDetect: (capture) {
          final List<Barcode> barcodes = capture.barcodes;
          if (barcodes.isNotEmpty) {
            final String? code = barcodes.first.rawValue;
            if (code != null && code.isNotEmpty) {
              Navigator.of(context).pop(code);
            }
          }
        },
      ),
    );
  }
}
