import 'dart:convert';
import 'dart:io';
import 'dart:ui';
import 'package:contratista/services/contratista_api_service.dart';
import 'package:contratista/services/finterprint_service.dart';
import 'package:contratista/utils/globals.dart';
import 'package:contratista/utils/signature_pad.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:http/http.dart' as http;
import 'package:lottie/lottie.dart';
import 'package:path_provider/path_provider.dart';

class HuellaFirmaScreen extends StatefulWidget {
  const HuellaFirmaScreen({super.key});

  @override
  HuellaFirmaScreenState createState() => HuellaFirmaScreenState();
}

class HuellaFirmaScreenState extends State<HuellaFirmaScreen> {
  final ApiService _apiService = ApiService();
  final FingerPrintService _fingerprintService = FingerPrintService();

  bool _isLoading = false;
  List<Map<String, dynamic>> _workers = [];
  List<Map<String, dynamic>> _filteredWorkers = [];
  Map<String, dynamic>? _selectedWorker;

  Uint8List? _signatureImage;
  String? _huellaBase64;

  final TextEditingController _searchController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _fetchWorkers();
    _searchController.addListener(_onSearchChanged);
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  // ─── Workers ──────────────────────────────────────────────────────────────

  void _onSearchChanged() {
    final q = _searchController.text.toLowerCase();
    setState(() {
      _filteredWorkers = _workers.where((w) {
        return (w['apellidos'] ?? '').toString().toLowerCase().contains(q) ||
            (w['nombres'] ?? '').toString().toLowerCase().contains(q) ||
            (w['rut'] ?? '').toString().toLowerCase().contains(q) ||
            (w['dni'] ?? '').toString().toLowerCase().contains(q);
      }).toList();
    });
  }

  Future<void> _fetchWorkers() async {
    setState(() => _isLoading = true);
    try {
      final response = await _apiService.get(
        'api_firma_huella/?holding=${userInfo.holding}',
      );
      if (response.statusCode == 200) {
        final List<dynamic> data = jsonDecode(response.body);
        final workers = List<Map<String, dynamic>>.from(data);
        setState(() {
          _workers = workers;
          _filteredWorkers = workers;
        });
      } else {
        _showSnack('Error al cargar trabajadores: ${response.statusCode}');
      }
    } catch (e) {
      _showSnack('Error: $e');
    } finally {
      setState(() => _isLoading = false);
    }
  }

  // ─── Selección ────────────────────────────────────────────────────────────

  void _onWorkerSelected(Map<String, dynamic> worker) {
    setState(() {
      _selectedWorker = worker;
      _signatureImage = null;
      _huellaBase64 = null;
    });
    _showCaptureOptionDialog();
  }

  Future<void> _showCaptureOptionDialog() async {
    final nombre =
        '${_selectedWorker!['nombres']} ${_selectedWorker!['apellidos'] ?? ''}'
            .trim();

    final result = await showDialog<String>(
      context: context,
      barrierDismissible: false,
      builder: (ctx) => AlertDialog(
        title: Text(
          nombre,
          style: const TextStyle(fontSize: 15, fontWeight: FontWeight.bold),
        ),
        content: const Text('¿Qué deseas capturar?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, 'firma'),
            child: const Text('Solo Firma'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(ctx, 'huella'),
            child: const Text('Solo Huella'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(ctx, 'ambas'),
            child: const Text('Ambas'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(ctx, null),
            child: const Text('Cancelar', style: TextStyle(color: Colors.grey)),
          ),
        ],
      ),
    );

    if (result == null) {
      setState(() => _selectedWorker = null);
      return;
    }

    if (result == 'firma') {
      _openSignaturePad();
    } else if (result == 'huella') {
      await _capturarHuella();
    } else {
      _openSignaturePad(
        onDone: () async {
          await Future.delayed(const Duration(milliseconds: 700));
          if (mounted) await _capturarHuella();
        },
      );
    }
  }

  // ─── Firma ────────────────────────────────────────────────────────────────

  void _openSignaturePad({Future<void> Function()? onDone}) {
    final screenCtx = context;
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (dialogCtx) => OrientationBuilder(
        builder: (ctx, orientation) {
          final isLandscape = orientation == Orientation.landscape;
          return Dialog(
            insetPadding: const EdgeInsets.all(8),
            child: SizedBox(
              width: MediaQuery.of(ctx).size.width * 0.95,
              height:
                  MediaQuery.of(ctx).size.height * (isLandscape ? 0.9 : 0.7),
              child: Padding(
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
                          setState(() => _signatureImage = signature);
                          Navigator.of(dialogCtx).pop();
                          await Future.delayed(
                            const Duration(milliseconds: 400),
                          );
                          if (mounted) {
                            ScaffoldMessenger.of(screenCtx).showSnackBar(
                              const SnackBar(
                                content: Text('Firma capturada exitosamente'),
                                backgroundColor: Colors.green,
                                duration: Duration(seconds: 2),
                              ),
                            );
                          }
                          if (onDone != null && mounted) await onDone();
                        },
                      ),
                    ),
                  ],
                ),
              ),
            ),
          );
        },
      ),
    );
  }

  // ─── Huella ───────────────────────────────────────────────────────────────

  Future<void> _capturarHuella() async {
    try {
      final continuar = await showDialog<bool>(
        context: context,
        barrierDismissible: false,
        builder: (ctx) => AlertDialog(
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
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(ctx, false),
              child: const Text('Cancelar'),
            ),
            TextButton(
              onPressed: () => Navigator.pop(ctx, true),
              child: const Text('CONTINUAR'),
            ),
          ],
        ),
      );

      if (continuar != true) {
        _showSnack('Captura cancelada', color: Colors.orange);
        return;
      }

      _showProgressDialog('Detectando escáner...');
      bool conectado = false;
      for (int i = 0; i < 5 && !conectado; i++) {
        await Future.delayed(const Duration(seconds: 1));
        conectado = await _fingerprintService.conectarDispositivo();
      }
      _closeDialog();

      if (!conectado) {
        final reintentar = await showDialog<bool>(
          context: context,
          builder: (ctx) => AlertDialog(
            title: const Text('Escáner No Detectado'),
            content: const Text(
              '• Scanner conectado al USB\n'
              '• Cable OTG funcionando\n'
              '• Permisos USB aceptados\n'
              '• LED verde encendido',
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(ctx, false),
                child: const Text('Omitir'),
              ),
              TextButton(
                onPressed: () => Navigator.pop(ctx, true),
                child: const Text('Reintentar'),
              ),
            ],
          ),
        );
        if (reintentar == true) await _capturarHuella();
        return;
      }

      _showProgressDialog('Coloca tu dedo en el escáner...');
      final huellaData = await _fingerprintService.capturarHuella();
      _closeDialog();

      if (huellaData != null) {
        setState(() => _huellaBase64 = base64Encode(huellaData));
        _showSnack('Huella capturada exitosamente', color: Colors.green);
      } else {
        final reintentar = await showDialog<bool>(
          context: context,
          builder: (ctx) => AlertDialog(
            title: const Text('Huella No Capturada'),
            content: const Text(
              '• Limpia el sensor\n'
              '• Presiona firmemente\n'
              '• Mantén 3-5 segundos',
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(ctx, false),
                child: const Text('Omitir'),
              ),
              TextButton(
                onPressed: () => Navigator.pop(ctx, true),
                child: const Text('Reintentar'),
              ),
            ],
          ),
        );
        if (reintentar == true) await _capturarHuella();
      }

      await _fingerprintService.desconectar();
    } catch (e) {
      loggerGlobal.e('Error huella: $e');
      _closeDialog();
      _showSnack('Error: $e');
    }
  }

  void _showProgressDialog(String msg) {
    if (!mounted) return;
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (ctx) => AlertDialog(
        content: Row(
          children: [
            const CircularProgressIndicator(),
            const SizedBox(width: 16),
            Expanded(child: Text(msg)),
          ],
        ),
      ),
    );
  }

  void _closeDialog() {
    if (mounted) Navigator.of(context, rootNavigator: true).pop();
  }

  // ─── Enviar ───────────────────────────────────────────────────────────────

  Future<void> _submit() async {
    if (_selectedWorker == null) return;
    if (_signatureImage == null && _huellaBase64 == null) {
      _showSnack('No hay firma ni huella capturada');
      return;
    }

    setState(() => _isLoading = true);

    try {
      final trabajadorId = _selectedWorker!['id'];
      final token = await _apiService.getJwtToken();
      final url = Uri.parse(
        '${_apiService.baseUrl}api_firma_huella/$trabajadorId/',
      );

      final request = http.MultipartRequest('PATCH', url);
      if (token != null) {
        request.headers['Authorization'] = 'Bearer $token';
      }

      final tempDir = await getTemporaryDirectory();
      final identifier =
          (_selectedWorker!['rut'] ?? _selectedWorker!['dni'] ?? 'worker')
              .toString()
              .replaceAll('.', '')
              .replaceAll('-', '');

      if (_signatureImage != null) {
        final f = File('${tempDir.path}/firma_$identifier.png');
        await f.writeAsBytes(_signatureImage!);
        request.files.add(await http.MultipartFile.fromPath('firma', f.path));
      }

      if (_huellaBase64 != null) {
        final f = File('${tempDir.path}/huella_$identifier.png');
        await f.writeAsBytes(base64Decode(_huellaBase64!));
        request.files.add(
          await http.MultipartFile.fromPath('huella_digital', f.path),
        );
      }

      final streamed = await request.send();
      final response = await http.Response.fromStream(streamed);

      if (response.statusCode == 200) {
        _showSnack('Guardado exitosamente', color: Colors.green);
        setState(() {
          _selectedWorker = null;
          _signatureImage = null;
          _huellaBase64 = null;
        });
      } else {
        loggerGlobal.e('Error: ${response.statusCode} ${response.body}');
        _showSnack('Error al guardar: ${response.statusCode}');
      }
    } catch (e) {
      loggerGlobal.e('Error en _submit: $e');
      _showSnack('Error: $e');
    } finally {
      setState(() => _isLoading = false);
    }
  }

  // ─── Helpers ──────────────────────────────────────────────────────────────

  void _showSnack(String msg, {Color color = Colors.red}) {
    if (!mounted) return;
    ScaffoldMessenger.of(
      context,
    ).showSnackBar(SnackBar(content: Text(msg), backgroundColor: color));
  }

  void _showFullImage(Uint8List bytes) {
    showDialog(
      context: context,
      builder: (ctx) => Dialog(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Image.memory(bytes),
            TextButton(
              onPressed: () => Navigator.pop(ctx),
              child: const Text('Cerrar'),
            ),
          ],
        ),
      ),
    );
  }

  // ─── Build ────────────────────────────────────────────────────────────────

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        Scaffold(
          appBar: AppBar(title: const Text('Huella y Firma')),
          body: Column(
            children: [
              Padding(
                padding: const EdgeInsets.all(8.0),
                child: TextField(
                  controller: _searchController,
                  decoration: const InputDecoration(
                    labelText: 'Buscar por apellido, nombre o RUT/DNI',
                    prefixIcon: Icon(Icons.search),
                    border: OutlineInputBorder(),
                  ),
                ),
              ),
              Expanded(
                child: _isLoading
                    ? const Center(child: CircularProgressIndicator())
                    : _filteredWorkers.isEmpty
                    ? const Center(child: Text('Sin resultados'))
                    : ListView.builder(
                        itemCount: _filteredWorkers.length,
                        itemBuilder: (context, i) {
                          final w = _filteredWorkers[i];
                          final isSelected =
                              _selectedWorker != null &&
                              _selectedWorker!['id'] == w['id'];
                          return ListTile(
                            leading: CircleAvatar(
                              backgroundColor: isSelected
                                  ? Colors.green
                                  : Colors.blueGrey,
                              child: Text(
                                (w['apellidos'] ?? 'W')
                                    .toString()
                                    .substring(0, 1)
                                    .toUpperCase(),
                                style: const TextStyle(color: Colors.white),
                              ),
                            ),
                            title: Text(
                              '${w['apellidos'] ?? ''}, ${w['nombres'] ?? ''}',
                              style: TextStyle(
                                fontWeight: isSelected
                                    ? FontWeight.bold
                                    : FontWeight.normal,
                              ),
                            ),
                            subtitle: Text(w['rut'] ?? w['dni'] ?? ''),
                            onTap: () => _onWorkerSelected(w),
                          );
                        },
                      ),
              ),
              if (_selectedWorker != null) _buildBottomPanel(),
            ],
          ),
        ),
        if (_isLoading)
          BackdropFilter(
            filter: ImageFilter.blur(sigmaX: 5, sigmaY: 5),
            child: Container(
              color: Colors.black.withValues(alpha: 0.5),
              child: Center(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Lottie.asset(
                      'assets/animations/loading_blue.json',
                      repeat: true,
                    ),
                    const SizedBox(height: 16),
                    const Text(
                      'Procesando...',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        decoration: TextDecoration.none,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
      ],
    );
  }

  Widget _buildBottomPanel() {
    return Container(
      color: Colors.grey[100],
      padding: const EdgeInsets.fromLTRB(8, 8, 8, 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Divider(height: 1),
          const SizedBox(height: 8),
          Text(
            '${_selectedWorker!['nombres']} ${_selectedWorker!['apellidos'] ?? ''}',
            style: const TextStyle(fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 8),

          // Previews
          if (_signatureImage != null || _huellaBase64 != null)
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                if (_signatureImage != null)
                  Expanded(
                    child: _PreviewTile(
                      label: 'Firma',
                      bytes: _signatureImage!,
                      onTap: () => _showFullImage(_signatureImage!),
                      onRedo: _openSignaturePad,
                    ),
                  ),
                if (_huellaBase64 != null)
                  Expanded(
                    child: _PreviewTile(
                      label: 'Huella',
                      bytes: base64Decode(_huellaBase64!),
                      onTap: () => _showFullImage(base64Decode(_huellaBase64!)),
                      onRedo: _capturarHuella,
                    ),
                  ),
              ],
            ),

          const SizedBox(height: 8),

          // Botones de captura
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: [
              ElevatedButton.icon(
                onPressed: _openSignaturePad,
                icon: const Icon(Icons.draw),
                label: Text(_signatureImage != null ? 'Re-Firmar' : 'Firma'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: _signatureImage != null
                      ? Colors.green
                      : null,
                ),
              ),
              ElevatedButton.icon(
                onPressed: _capturarHuella,
                icon: const Icon(Icons.fingerprint),
                label: Text(_huellaBase64 != null ? 'Re-Huella' : 'Huella'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: _huellaBase64 != null ? Colors.green : null,
                ),
              ),
            ],
          ),

          const SizedBox(height: 8),

          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: (_signatureImage != null || _huellaBase64 != null)
                  ? _submit
                  : null,
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.teal,
                foregroundColor: Colors.white,
              ),
              child: const Text('Guardar y Enviar'),
            ),
          ),

          const SizedBox(height: 20),
          Center(
            child: TextButton(
              onPressed: () => setState(() {
                _selectedWorker = null;
                _signatureImage = null;
                _huellaBase64 = null;
              }),
              child: const Text(
                'Cancelar selección',
                style: TextStyle(color: Colors.grey),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

// ─── Widget auxiliar ─────────────────────────────────────────────────────────

class _PreviewTile extends StatelessWidget {
  final String label;
  final Uint8List bytes;
  final VoidCallback onTap;
  final VoidCallback onRedo;

  const _PreviewTile({
    required this.label,
    required this.bytes,
    required this.onTap,
    required this.onRedo,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        GestureDetector(
          onTap: onTap,
          child: Image.memory(
            bytes,
            width: 100,
            height: 100,
            fit: BoxFit.cover,
          ),
        ),
        const SizedBox(height: 2),
        Text(
          label,
          style: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold),
        ),
        TextButton(
          onPressed: onRedo,
          style: TextButton.styleFrom(
            minimumSize: Size.zero,
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
            tapTargetSize: MaterialTapTargetSize.shrinkWrap,
          ),
          child: const Text('Repetir', style: TextStyle(fontSize: 11)),
        ),
      ],
    );
  }
}
