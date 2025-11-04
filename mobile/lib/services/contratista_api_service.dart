import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:contratista/utils/globals.dart';
import 'package:logger/logger.dart';

Logger logger = Logger();

class ApiService {
  final String baseUrl = 'http://192.168.100.15:8182/contratista_test_api/';
  //'http://contratista.terramobile.cl/contratista_test_api/'
  //192.168.43.122
  //192.168.100.15 = OFICINA PARRAL

  // Obtener el JWT token
  Future<String?> getJwtToken() async {
    return await storage.read(key: 'jwt_token');
  }

  // Obtener el refresh token
  Future<String?> getRefreshToken() async {
    return await storage.read(key: 'refresh_token');
  }

  // Guardar tokens después del login
  Future<void> saveTokens(String jwtToken, String refreshToken) async {
    await storage.write(key: 'jwt_token', value: jwtToken);
    await storage.write(key: 'refresh_token', value: refreshToken);
  }

  // Limpiar tokens (logout)
  Future<void> clearTokens() async {
    await storage.delete(key: 'jwt_token');
    await storage.delete(key: 'refresh_token');
  }

  // Refrescar el access token
  Future<String?> refreshAccessToken() async {
    try {
      final refreshToken = await getRefreshToken();
      if (refreshToken == null) return null;

      final response = await http
          .post(
            Uri.parse('${baseUrl}refresh-jwt/'),
            headers: {'Content-Type': 'application/json; charset=UTF-8'},
            body: jsonEncode({'refresh_token': refreshToken}),
          )
          .timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        if (data['success'] == true) {
          final newJwtToken = data['jwt_token'];
          await storage.write(key: 'jwt_token', value: newJwtToken);
          return newJwtToken;
        }
      }
      return null;
    } catch (e) {
      logger.e('Error refrescando token: $e');
      return null;
    }
  }

  // Headers básicos
  Future<Map<String, String>> _getHeaders({bool includeAuth = true}) async {
    final headers = <String, String>{
      'Content-Type': 'application/json; charset=UTF-8',
    };

    if (includeAuth) {
      final token = await getJwtToken();
      if (token != null) {
        headers['Authorization'] = 'Bearer $token';
      }
    }

    return headers;
  }

  // POST request
  Future<http.Response> post(
    String endpoint,
    Map<String, dynamic> body, {
    bool includeAuth = true,
  }) async {
    try {
      final url = Uri.parse('$baseUrl$endpoint');
      final headers = await _getHeaders(includeAuth: includeAuth);

      final response = await http
          .post(url, headers: headers, body: jsonEncode(body))
          .timeout(
            const Duration(seconds: 10),
            onTimeout: () => throw Exception(
              'La conexión ha tardado demasiado, favor intente nuevamente.',
            ),
          );

      // Si el token expiró, intentar refrescar y reintentar una vez
      if (response.statusCode == 401 && includeAuth) {
        final newToken = await refreshAccessToken();
        if (newToken != null) {
          // Reintentar con nuevo token
          final newHeaders = await _getHeaders(includeAuth: true);
          return await http
              .post(url, headers: newHeaders, body: jsonEncode(body))
              .timeout(const Duration(seconds: 10));
        }
      }

      return response;
    } catch (e) {
      logger.e('Error en POST: $e');
      rethrow;
    }
  }

  // GET request
  Future<http.Response> get(
    String endpoint, {
    bool allowNotFound = false,
  }) async {
    try {
      final url = Uri.parse('$baseUrl$endpoint');
      final headers = await _getHeaders(includeAuth: true);
      final response = await http
          .get(url, headers: headers)
          .timeout(
            const Duration(seconds: 10),
            onTimeout: () => throw Exception(
              'La conexión ha tardado demasiado, favor intente nuevamente.',
            ),
          );

      // Refrescar token si expiró
      if (response.statusCode == 401) {
        final newToken = await refreshAccessToken();
        if (newToken != null) {
          final newHeaders = await _getHeaders(includeAuth: true);
          return await http
              .get(url, headers: newHeaders)
              .timeout(const Duration(seconds: 10));
        }
      }

      // Si es 404 y está permitido, retornar la respuesta en lugar de lanzar excepción
      if (response.statusCode == 404 && allowNotFound) {
        return response;
      }

      if (response.statusCode != 200) {
        throw Exception('Error: ${response.statusCode}');
      }
      return response;
    } catch (e) {
      logger.e('Error en GET: $e');
      rethrow;
    }
  }

  // PUT request
  Future<http.Response> put(String endpoint, Map<String, dynamic> body) async {
    try {
      final url = Uri.parse('$baseUrl$endpoint');
      final headers = await _getHeaders(includeAuth: true);

      final response = await http
          .put(url, headers: headers, body: jsonEncode(body))
          .timeout(
            const Duration(seconds: 10),
            onTimeout: () => throw Exception(
              'La conexión ha tardado demasiado, favor intente nuevamente.',
            ),
          );

      // Refrescar token si expiró
      if (response.statusCode == 401) {
        final newToken = await refreshAccessToken();
        if (newToken != null) {
          final newHeaders = await _getHeaders(includeAuth: true);
          return await http
              .put(url, headers: newHeaders, body: jsonEncode(body))
              .timeout(const Duration(seconds: 10));
        }
      }

      if (response.statusCode != 200) {
        throw Exception('Error: ${response.statusCode}');
      }

      return response;
    } catch (e) {
      logger.e('Error en PUT: $e');
      rethrow;
    }
  }

  // POST Multipart
  Future<http.Response> postMultipart(
    String endpoint,
    Map<String, String> fields,
    List<MapEntry<String, File>> files,
  ) async {
    final token = await getJwtToken();
    final url = Uri.parse('$baseUrl$endpoint');
    final request = http.MultipartRequest('POST', url);

    if (token != null) {
      request.headers['Authorization'] = 'Bearer $token';
    }

    fields.forEach((key, value) {
      request.fields[key] = value;
    });

    for (var fileEntry in files) {
      request.files.add(
        await http.MultipartFile.fromPath(fileEntry.key, fileEntry.value.path),
      );
    }

    final streamResponse = await request.send();
    return await http.Response.fromStream(streamResponse);
  }
}
