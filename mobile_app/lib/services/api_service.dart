import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:nutribot/services/cache_service.dart';

/// Base URL of the Nutribot backend. Change for your machine/emulator.
const String baseUrl = 'http://192.168.0.103:8000'; // Android emulator localhost
// Use http://localhost:8000 for iOS simulator or web.
// For physical device: use your PC's IP (e.g., http://192.168.1.23:8000)

class ApiService {
  static final ApiService _instance = ApiService._();
  factory ApiService() => _instance;
  ApiService._();

  String _base = baseUrl;
  static const Duration _timeout = Duration(seconds: 30);
  static const int _maxRetries = 2;

  void setBaseUrl(String url) {
    _base = url.replaceAll(RegExp(r'/$'), '');
  }

  /// Create HTTP client with timeout
  http.Client _getClient() {
    return http.Client();
  }

  /// Retry mechanism for network calls
  Future<http.Response> _retryRequest(
    Future<http.Response> Function() requestFn,
    {int retries = _maxRetries}
  ) async {
    int attempts = 0;
    while (attempts <= retries) {
      try {
        final response = await requestFn().timeout(_timeout);
        if (response.statusCode < 500 || attempts == retries) {
          return response;
        }
      } catch (e) {
        if (attempts == retries) {
          rethrow;
        }
        await Future.delayed(Duration(milliseconds: 500 * (attempts + 1)));
      }
      attempts++;
    }
    throw Exception('Request failed after ${retries + 1} attempts');
  }

  /// POST /api/predict_food with image file or food_name
  /// Includes caching and retry logic
  Future<Map<String, dynamic>> predictFood({
    List<int>? imageBytes,
    String? foodName,
    bool useCache = true,
  }) async {
    // Check cache first
    if (useCache) {
      String cacheKey;
      if (imageBytes != null && imageBytes.isNotEmpty) {
        cacheKey = CacheService.getImageCacheKey(imageBytes);
      } else if (foodName != null && foodName.isNotEmpty) {
        cacheKey = CacheService.getFoodNameCacheKey(foodName);
      } else {
        return {'message': 'Provide image or food_name'};
      }

      final cached = await CacheService.getCache(cacheKey);
      if (cached != null) {
        print('Cache hit for predict_food');
        return cached;
      }
    }

    final uri = Uri.parse('$_base/api/predict_food');
    
    try {
      if (imageBytes != null && imageBytes.isNotEmpty) {
        final request = http.MultipartRequest('POST', uri);
        request.files.add(http.MultipartFile.fromBytes(
          'file',
          imageBytes,
          filename: 'image.jpg',
        ));
        
        final response = await _retryRequest(() async {
          final stream = await request.send();
          return await http.Response.fromStream(stream);
        });
        
        final result = _decode(response);
        
        // Cache successful response
        if (useCache && !result.containsKey('error')) {
          final cacheKey = CacheService.getImageCacheKey(imageBytes);
          await CacheService.setCache(cacheKey, result);
        }
        
        return result;
      }
      
      if (foodName != null && foodName.isNotEmpty) {
        final response = await _retryRequest(() async {
          return await http.post(
            uri,
            headers: {'Content-Type': 'application/x-www-form-urlencoded'},
            body: 'food_name=${Uri.encodeComponent(foodName)}',
          ).timeout(_timeout);
        });
        
        final result = _decode(response);
        
        // Cache successful response
        if (useCache && !result.containsKey('error')) {
          final cacheKey = CacheService.getFoodNameCacheKey(foodName);
          await CacheService.setCache(cacheKey, result);
        }
        
        return result;
      }
      
      return {'message': 'Provide image or food_name'};
    } on SocketException {
      return {'error': 'Network error: Unable to connect to server. Check your connection.'};
    } on HttpException {
      return {'error': 'HTTP error: Server returned an error response.'};
    } catch (e) {
      return {'error': 'Request failed: ${e.toString()}'};
    }
  }

  /// POST /api/predict_food with form data (multipart for file)
  /// DEPRECATED: Use predictFood with compressed imageBytes instead
  Future<Map<String, dynamic>> predictFoodMultipart({
    required String filePath,
    bool useCache = true,
  }) async {
    final file = File(filePath);
    if (!await file.exists()) {
      return {'error': 'File not found'};
    }

    // Check cache
    if (useCache) {
      final imageBytes = await file.readAsBytes();
      final cacheKey = CacheService.getImageCacheKey(imageBytes);
      final cached = await CacheService.getCache(cacheKey);
      if (cached != null) {
        print('Cache hit for predictFoodMultipart');
        return cached;
      }
    }

    final uri = Uri.parse('$_base/api/predict_food');
    
    try {
      final request = http.MultipartRequest('POST', uri);
      request.files.add(await http.MultipartFile.fromPath('file', filePath));
      
      final response = await _retryRequest(() async {
        final stream = await request.send();
        return await http.Response.fromStream(stream);
      });
      
      final result = _decode(response);
      
      // Cache successful response
      if (useCache && !result.containsKey('error')) {
        final imageBytes = await file.readAsBytes();
        final cacheKey = CacheService.getImageCacheKey(imageBytes);
        await CacheService.setCache(cacheKey, result);
      }
      
      return result;
    } on SocketException {
      return {'error': 'Network error: Unable to connect to server. Check your connection.'};
    } catch (e) {
      return {'error': 'Request failed: ${e.toString()}'};
    }
  }

  /// POST /api/chat_query with retry logic and user context
  Future<Map<String, dynamic>> chatQuery(String query, {String? userContext}) async {
    final uri = Uri.parse('$_base/api/chat_query');
    
    try {
      final response = await _retryRequest(() async {
        return await http.post(
          uri,
          headers: {'Content-Type': 'application/json'},
          body: jsonEncode({
            'query': query,
            if (userContext != null && userContext.isNotEmpty) 'user_context': userContext,
          }),
        ).timeout(_timeout);
      });
      
      return _decode(response);
    } on SocketException {
      return {'error': 'Network error: Unable to connect to server. Check your connection.'};
    } on HttpException {
      return {'error': 'HTTP error: Server returned an error response.'};
    } catch (e) {
      return {'error': 'Request failed: ${e.toString()}'};
    }
  }

  static Map<String, dynamic> _decode(http.Response response) {
    if (response.statusCode >= 200 && response.statusCode < 300) {
      return jsonDecode(response.body) as Map<String, dynamic>? ?? {};
    }
    return {'error': response.body, 'statusCode': response.statusCode};
  }
}
