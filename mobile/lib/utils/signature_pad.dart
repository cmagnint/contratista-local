import 'package:flutter/material.dart';
import 'package:signature/signature.dart';
import 'dart:typed_data';

class SignatureWidget extends StatefulWidget {
  final Function(Uint8List) onSignatureCapture;
  const SignatureWidget({super.key, required this.onSignatureCapture});

  @override
  SignatureWidgetState createState() => SignatureWidgetState();
}

class SignatureWidgetState extends State<SignatureWidget> {
  late SignatureController _controller;

  @override
  void initState() {
    super.initState();
    _controller = SignatureController(
      penStrokeWidth: 3,
      penColor: Colors.blue,
      exportBackgroundColor: Colors.transparent,
      exportPenColor: Colors.blue,
    );
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: <Widget>[
        Expanded(
          child: Container(
            width: double.infinity,
            decoration: BoxDecoration(
              border: Border.all(color: Colors.grey[400]!, width: 1),
              borderRadius: BorderRadius.circular(4),
            ),
            child: Signature(
              controller: _controller,
              backgroundColor: Colors.white,
            ),
          ),
        ),
        const SizedBox(height: 8),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          alignment: WrapAlignment.spaceEvenly,
          children: <Widget>[
            ElevatedButton.icon(
              icon: const Icon(Icons.clear, size: 18),
              label: const Text('Limpiar'),
              onPressed: () => setState(() => _controller.clear()),
            ),
            ElevatedButton.icon(
              icon: const Icon(Icons.close, size: 18),
              label: const Text('Cancelar'),
              style: ElevatedButton.styleFrom(backgroundColor: Colors.grey),
              onPressed: () => Navigator.of(context).pop(),
            ),
            ElevatedButton.icon(
              icon: const Icon(Icons.check, size: 18),
              label: const Text('Guardar'),
              onPressed: () async {
                if (_controller.isNotEmpty) {
                  final Uint8List? data = await _controller.toPngBytes();
                  if (data != null) widget.onSignatureCapture(data);
                }
              },
            ),
          ],
        ),
      ],
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }
}
