import 'dart:convert';
import 'dart:io';
import 'package:contratista/pages/mother_layout/contratacion/enrollment_db.dart';
import 'package:flutter/material.dart';
import 'package:contratista/services/contratista_api_service.dart';
import 'package:contratista/utils/globals.dart';
import 'package:path_provider/path_provider.dart';

class PendingEnrollmentsScreen extends StatefulWidget {
  const PendingEnrollmentsScreen({super.key});

  @override
  PendingEnrollmentsScreenState createState() =>
      PendingEnrollmentsScreenState();
}

class PendingEnrollmentsScreenState extends State<PendingEnrollmentsScreen> {
  final EnrollmentDatabase _db = EnrollmentDatabase();
  final ApiService _apiService = ApiService();
  List<Map<String, dynamic>> _pendingEnrollments = [];
  bool _isSyncing = false;

  @override
  void initState() {
    super.initState();
    _loadPendingEnrollments();
  }

  Future<void> _loadPendingEnrollments() async {
    final enrollments = await _db.getUnsyncedEnrollments();
    setState(() {
      _pendingEnrollments = enrollments;
    });
  }

  Future<void> _syncEnrollments() async {
    setState(() {
      _isSyncing = true;
    });

    try {
      int successCount = 0;
      int errorCount = 0;

      for (var enrollment in _pendingEnrollments) {
        try {
          // Reconstruir los archivos desde base64
          List<MapEntry<String, File>> files = [];
          final tempDir = await getTemporaryDirectory();

          if (enrollment['carnet_front_image'] != null) {
            final frontFile = await File(
              '${tempDir.path}/temp_front.jpg',
            ).create();
            await frontFile.writeAsBytes(
              base64Decode(enrollment['carnet_front_image']),
            );
            files.add(MapEntry('carnet_front_image', frontFile));
          }

          if (enrollment['carnet_back_image'] != null) {
            final backFile = await File(
              '${tempDir.path}/temp_back.jpg',
            ).create();
            await backFile.writeAsBytes(
              base64Decode(enrollment['carnet_back_image']),
            );
            files.add(MapEntry('carnet_back_image', backFile));
          }

          if (enrollment['firma'] != null) {
            final signatureFile = await File(
              '${tempDir.path}/temp_signature.png',
            ).create();
            await signatureFile.writeAsBytes(base64Decode(enrollment['firma']));
            files.add(MapEntry('firma', signatureFile));
          }

          // Preparar campos SOLO los que acepta el servidor
          Map<String, String> fields = {
            'holding': enrollment['holding'] ?? '',
            'sociedad': enrollment['sociedad'] ?? '',
            'codigo_supervisor': enrollment['codigo_supervisor'] ?? '',
            'folio': enrollment['folio'] ?? '',
            'fundo': enrollment['fundo'] ?? '',
            'casa': enrollment['casa'] ?? '',
            'rut': enrollment['rut'] ?? '',
            'dni': enrollment['dni'] ?? '',
            'nic': enrollment['nic'] ?? '',
            'apellidos': enrollment['apellidos'] ?? '',
            'nombres': enrollment['nombres'] ?? '',
            'nacionalidad': enrollment['nacionalidad'] ?? '',
            'sexo': enrollment['sexo'] ?? '',
            'estado_civil': enrollment['estado_civil'] ?? '',
            'telefono': enrollment['telefono'] ?? '',
            'correo': enrollment['correo'] ?? '',
            'direccion': enrollment['direccion'] ?? '',
            'fecha_nacimiento': enrollment['fecha_nacimiento'] ?? '',
            'metodo_pago': enrollment['metodo_pago'] ?? '',
            'banco': enrollment['banco'] ?? '',
            'tipo_cuenta_bancaria': enrollment['tipo_cuenta_bancaria'] ?? '',
            'numero_cuenta': enrollment['numero_cuenta'] ?? '',
            'estado': 'true',
          };

          // Solo agregar codigo_qr si existe
          if (enrollment['codigo_qr'] != null &&
              enrollment['codigo_qr'].isNotEmpty) {
            fields['codigo_qr'] = enrollment['codigo_qr'];
          }

          // Remover campos que podrían causar problemas
          fields.removeWhere(
            (key, value) => [
              'labor_id',
              'empresa_transporte_id',
              'vehiculo_id',
              'supervisor_contratador',
              'empresa_transporte',
              'vehiculo',
              'horario',
              'labor',
            ].contains(key),
          );

          final response = await _apiService.postMultipart(
            'personal_trabajadores_mobile/',
            fields,
            files,
          );

          if (response.statusCode == 201 || response.statusCode == 200) {
            await _db.markAsSynced(enrollment['id']);
            successCount++;

            // Limpiar archivos temporales
            for (var file in files) {
              await file.value.delete();
            }
          } else {
            errorCount++;
            loggerGlobal.e('Error syncing enrollment: ${response.body}');
          }
        } catch (e) {
          errorCount++;
          loggerGlobal.e('Error processing enrollment: $e');
        }
      }

      await _loadPendingEnrollments();

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              'Sincronización completada. Éxitos: $successCount, Errores: $errorCount',
            ),
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error en la sincronización: $e')),
        );
      }
    } finally {
      setState(() {
        _isSyncing = false;
      });
    }
  }

  void _showEnrollmentDetails(Map<String, dynamic> enrollment) {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return Dialog(
          insetPadding: const EdgeInsets.all(16),
          child: Container(
            width: MediaQuery.of(context).size.width * 0.9,
            padding: const EdgeInsets.all(16),
            child: SingleChildScrollView(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text(
                        'Detalles del Trabajador',
                        style: TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      IconButton(
                        icon: const Icon(Icons.close),
                        onPressed: () => Navigator.of(context).pop(),
                      ),
                    ],
                  ),
                  const Divider(),
                  _buildDetailSection('Información Personal', [
                    _buildDetailRow('Nombres', enrollment['nombres']),
                    _buildDetailRow('Apellidos', enrollment['apellidos']),
                    _buildDetailRow('RUT', enrollment['run']),
                    _buildDetailRow('DNI', enrollment['dni']),
                    _buildDetailRow('NIC', enrollment['nic']),
                    _buildDetailRow('Nacionalidad', enrollment['nacionalidad']),
                    _buildDetailRow('Sexo', enrollment['sexo']),
                    _buildDetailRow('Estado Civil', enrollment['estado_civil']),
                    _buildDetailRow(
                      'Fecha Nacimiento',
                      enrollment['fecha_nacimiento'],
                    ),
                  ]),
                  const Divider(),
                  _buildDetailSection('Información de Contacto', [
                    _buildDetailRow('Teléfono', enrollment['telefono']),
                    _buildDetailRow('Correo', enrollment['correo']),
                    _buildDetailRow('Dirección', enrollment['direccion']),
                  ]),
                  const Divider(),
                  _buildDetailSection('Información Laboral', [
                    _buildDetailRow('Folio', enrollment['folio']),
                    _buildDetailRow('Fundo', enrollment['fundo']),
                    _buildDetailRow('Labor', enrollment['labor']),
                    _buildDetailRow(
                      'Empresa Transporte',
                      enrollment['empresa_transporte'],
                    ),
                    _buildDetailRow('Vehículo', enrollment['vehiculo']),
                    _buildDetailRow('Casa', enrollment['casa']),
                  ]),
                  const Divider(),
                  _buildDetailSection('Información Bancaria', [
                    _buildDetailRow(
                      'Método de Pago',
                      enrollment['metodo_pago'],
                    ),
                    _buildDetailRow('Banco', enrollment['banco']),
                    _buildDetailRow(
                      'Tipo Cuenta',
                      enrollment['tipo_cuenta_bancaria'],
                    ),
                    _buildDetailRow(
                      'Número Cuenta',
                      enrollment['numero_cuenta'],
                    ),
                  ]),
                  if (enrollment['codigo_qr'] != null) ...[
                    const Divider(),
                    _buildDetailSection('QR', [
                      _buildDetailRow('Código QR', enrollment['codigo_qr']),
                    ]),
                  ],
                  const Divider(),
                  _buildDetailSection('Información del Sistema', [
                    _buildDetailRow('Creado', enrollment['createdAt']),
                    _buildDetailRow(
                      'Sincronizado',
                      enrollment['synced'].toString(),
                    ),
                  ]),
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  Future<void> _subirTodos() async {
    if (_pendingEnrollments.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('No hay trabajadores pendientes para subir'),
        ),
      );
      return;
    }

    // Mostrar diálogo de confirmación
    bool? confirm = await showDialog<bool>(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: const Text('Confirmar Subida'),
          content: Text(
            '¿Desea subir ${_pendingEnrollments.length} trabajadores a la nube?',
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(false),
              child: const Text('Cancelar'),
            ),
            ElevatedButton(
              onPressed: () => Navigator.of(context).pop(true),
              child: const Text('Subir'),
            ),
          ],
        );
      },
    );

    if (confirm != true) return;

    setState(() {
      _isSyncing = true;
    });

    try {
      await _syncEnrollments();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Proceso de subida completado')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text('Error en la subida: $e')));
      }
    } finally {
      setState(() {
        _isSyncing = false;
      });
    }
  }

  Widget _buildDetailSection(String title, List<Widget> children) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: const TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: Colors.blue,
          ),
        ),
        const SizedBox(height: 8),
        ...children,
        const SizedBox(height: 8),
      ],
    );
  }

  Widget _buildDetailRow(String label, String? value) {
    if (value == null || value.isEmpty) return const SizedBox.shrink();
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 120,
            child: Text(
              '$label:',
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
          ),
          Expanded(child: Text(value)),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Enrolamientos Pendientes'),
        actions: [
          if (_pendingEnrollments.isNotEmpty) ...[
            TextButton.icon(
              icon: const Icon(Icons.cloud_upload, color: Colors.white),
              label: const Text(
                'Subir Todos',
                style: TextStyle(color: Colors.white),
              ),
              onPressed: _isSyncing ? null : _syncEnrollments,
            ),
          ],
        ],
      ),
      body: _isSyncing
          ? const Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  CircularProgressIndicator(),
                  SizedBox(height: 16),
                  Text('Sincronizando enrolamientos...'),
                ],
              ),
            )
          : _pendingEnrollments.isEmpty
          ? const Center(child: Text('No hay enrolamientos pendientes'))
          : Column(
              children: [
                Expanded(
                  // Agregamos Expanded aquí
                  child: ListView.builder(
                    shrinkWrap: true,
                    itemCount: _pendingEnrollments.length,
                    itemBuilder: (context, index) {
                      final enrollment = _pendingEnrollments[index];
                      return Card(
                        margin: const EdgeInsets.symmetric(
                          horizontal: 8,
                          vertical: 4,
                        ),
                        child: ListTile(
                          onTap: () => _showEnrollmentDetails(enrollment),
                          title: Text(
                            '${enrollment['nombres']} ${enrollment['apellidos']}',
                          ),
                          subtitle: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text('Creado: ${enrollment['createdAt']}'),
                              Text(
                                enrollment['run']?.isNotEmpty == true
                                    ? 'RUT: ${enrollment['run']}'
                                    : 'DNI: ${enrollment['dni']}',
                              ),
                              Text('Folio: ${enrollment['folio']}'),
                            ],
                          ),
                          trailing: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              const Icon(
                                Icons.cloud_upload,
                                color: Colors.blue,
                              ),
                              IconButton(
                                icon: const Icon(
                                  Icons.delete,
                                  color: Colors.red,
                                ),
                                onPressed: () async {
                                  await _db.deleteEnrollment(enrollment['id']);
                                  _loadPendingEnrollments();
                                },
                              ),
                            ],
                          ),
                          isThreeLine: true,
                        ),
                      );
                    },
                  ),
                ),
                Padding(
                  padding: const EdgeInsets.only(bottom: 85),
                  child: ElevatedButton(
                    onPressed: _subirTodos,
                    style: ButtonStyle(
                      shape: WidgetStateProperty.all<RoundedRectangleBorder>(
                        RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(4.0),
                        ),
                      ),
                    ),
                    child: const Text('Subir Todos'),
                  ),
                ),
              ],
            ),
    );
  }
}
