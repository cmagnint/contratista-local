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
      penStrokeWidth: 5,
      penColor: Colors.black,
      exportBackgroundColor: Colors.white,
    );
  }

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final isLandscape = constraints.maxWidth > constraints.maxHeight;
        final signatureWidth =
            isLandscape ? constraints.maxWidth * 0.8 : constraints.maxWidth;
        final signatureHeight = isLandscape
            ? constraints.maxHeight * 0.7
            : constraints.maxHeight * 0.6;

        return Column(
          mainAxisSize: MainAxisSize.min,
          children: <Widget>[
            Container(
              width: signatureWidth,
              height: signatureHeight,
              decoration: BoxDecoration(
                border: Border.all(color: Colors.grey),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Signature(
                controller: _controller,
                backgroundColor: Colors.grey[200]!,
              ),
            ),
            SizedBox(height: isLandscape ? 10 : 20),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: <Widget>[
                ElevatedButton(
                  child: const Text('Limpiar'),
                  onPressed: () {
                    setState(() => _controller.clear());
                  },
                ),
                ElevatedButton(
                  child: const Text('Guardar'),
                  onPressed: () async {
                    if (_controller.isNotEmpty) {
                      final Uint8List? data = await _controller.toPngBytes();
                      if (data != null) {
                        widget.onSignatureCapture(data);
                      }
                    }
                  },
                ),
              ],
            ),
          ],
        );
      },
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }
}
