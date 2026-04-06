import 'dart:async';
import 'dart:convert';
import 'dart:typed_data';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:nutribot/services/cache_service.dart';
import 'package:nutribot/utils/app_logger.dart';
import 'package:nutribot/services/image_service.dart';
import 'package:shared_preferences/shared_preferences.dart';

class FoodResult {
  final String foodItem;
  final double caloriesKcal;
  final double proteinG;
  final double carbsG;
  final double fatG;
  final double fiberG;
  final double sodiumMg;
  final double cholesterolMg;
  final double? giIndex;
  final String mealType;
  final String healthTags;
  final String vegNonveg;
  final bool didYouMean;
  final String? diseaseWarning;

  FoodResult.fromJson(Map<String, dynamic> json)
      : foodItem = json['food_item'] ?? '',
        caloriesKcal = (json['calories_kcal'] ?? 0).toDouble(),
        proteinG = (json['protein_g'] ?? 0).toDouble(),
        carbsG = (json['carbs_g'] ?? 0).toDouble(),
        fatG = (json['fat_g'] ?? 0).toDouble(),
        fiberG = (json['fiber_g'] ?? 0).toDouble(),
        sodiumMg = (json['sodium_mg'] ?? 0).toDouble(),
        cholesterolMg = (json['cholesterol_mg'] ?? 0).toDouble(),
        giIndex = json['gi_index'] != null ? (json['gi_index'] as num).toDouble() : null,
        mealType = json['meal_type'] ?? '',
        healthTags = json['health_tags'] ?? '',
        vegNonveg = json['veg_nonveg'] ?? '',
        didYouMean = json['did_you_mean'] ?? false,
        diseaseWarning = json['disease_warning'];
}

class ChatResponse {
  final String reply;
  final String intent;
  final List<FoodResult>? foods;
  final bool needsExercise;

  ChatResponse({required this.reply, required this.intent, this.foods, required this.needsExercise});

  factory ChatResponse.fromJson(Map<String, dynamic> json) {
    return ChatResponse(
      reply: json['reply'] ?? "Something went wrong. Please try again.",
      intent: json['intent'] ?? "error",
      foods: json['foods'] != null ? (json['foods'] as List).map((i) => FoodResult.fromJson(i)).toList() : null,
      needsExercise: json['needs_exercise'] ?? false,
    );
  }

  factory ChatResponse.error() {
    return ChatResponse(
      reply: "Something went wrong on my end. Please try again.",
      intent: "error",
      needsExercise: false,
    );
  }
}

class ApiService {
  static final ApiService _instance = ApiService._();
  factory ApiService() => _instance;
  ApiService._();

  // 🔥 DYNAMIC BASE URL: 
  // Use 10.0.2.2 for Android Emulator 
  // Use 192.168.0.103 for real devices on your network
  static String get baseUrl {
    if (Platform.isAndroid) {
      // 10.0.2.2 is the standard gateway for the Android Emulator to access host localhost
      return "http://10.0.2.2:8000";
    } else {
      return "http://localhost:8000";
    }
  }

  String _base = baseUrl;

  static const Duration _timeout = Duration(seconds: 15);
  static const int _maxRetries = 2;

  void setBaseUrl(String url) {
    _base = url.replaceAll(RegExp(r'/$'), '');
  }

  // 🔥 FOOD PREDICTION
  Future<Map<String, dynamic>> predictFood({
    List<int>? imageBytes,
    String? foodName,
    String? userId,
  }) async {
    final uri = Uri.parse("$_base/api/food/predict_food");

    try {
      if (imageBytes != null && imageBytes.isNotEmpty) {
        final request = http.MultipartRequest('POST', uri);
        request.fields['user_id'] = userId ?? "guest";

        request.files.add(
          http.MultipartFile.fromBytes(
            'file',
            imageBytes,
            filename: 'image.jpg',
          ),
        );

        final stream = await request.send().timeout(_timeout);
        final response = await http.Response.fromStream(stream);

        return _decode(response);
      }

      if (foodName != null && foodName.isNotEmpty) {
        final response = await http.post(
          uri,
          headers: {"Content-Type": "application/json"},
          body: jsonEncode({
            "food_name": foodName,
            "user_id": userId ?? "guest"
          }),
        ).timeout(_timeout);

        return _decode(response);
      }

      return {"error": "Provide image or foodName"};
    } catch (e) {
      AppLogger.error('API PREDICT', e);
      return {"error": e.toString()};
    }
  }


  // 🔥 CHAT
  Future<ChatResponse> sendChatMessage({
    required String userId,
    required String message,
    String? intentHint,
  }) async {
    try {
      final token = await _getToken();
      final bodyData = {
        "user_id": userId,
        "message": message,
      };
      if (intentHint != null) {
        bodyData["intent_hint"] = intentHint;
      }
      
      final response = await http.post(
        Uri.parse('$_base/api/chat/message'),
        headers: {
          'Content-Type': 'application/json',
          if (token != null) 'Authorization': 'Bearer $token',
        },
        body: jsonEncode(bodyData),
      );
      
      if (response.statusCode == 401) {
        return ChatResponse.error();
      }
      
      return ChatResponse.fromJson(jsonDecode(response.body));
    } catch (e) {
      AppLogger.error('API CHAT', e);
      return ChatResponse.error();
    }
  }

  Future<String?> _getToken() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      return prefs.getString('auth_token'); // Match auth_service key
    } catch (e) {
      return null;
    }
  }

  // 🔥 SEARCH FOOD
  Future<List<dynamic>> searchFood(String foodName, String medicalCondition, String dietType) async {
    try {
      final token = await _getToken();
      final response = await http.post(
        Uri.parse('$_base/api/food/search-food'),
        headers: {
          'Content-Type': 'application/json',
          if (token != null) 'Authorization': 'Bearer $token',
        },
        body: jsonEncode({
          'food_name': foodName,
          'medical_condition': medicalCondition,
          'diet_type': dietType,
        }),
      );
      
      if (response.statusCode == 404) {
        return []; // Graceful handle
      } else if (response.statusCode == 401) {
        throw Exception("Authentication required");
      }
      
      return jsonDecode(response.body);
    } catch (e) {
      AppLogger.error('API SEARCH', e);
      return [];
    }
  }

  // 🔥 CHECK SAFETY
  Future<Map<String, dynamic>> checkSafety(String userId) async {
    try {
      final token = await _getToken();
      final response = await http.post(
        Uri.parse('$_base/api/safety/check-safety'),
        headers: {
          'Content-Type': 'application/json',
          if (token != null) 'Authorization': 'Bearer $token',
        },
        body: jsonEncode({'user_id': userId}),
      );
      
      if (response.statusCode == 401) {
        throw Exception("Authentication required");
      }
      
      return jsonDecode(response.body);
    } catch (e) {
      AppLogger.error('API SAFETY', e);
      return {'error': e.toString(), 'needs_exercise': false, 'safety_label': 'Safe', 'risk_level': 'N/A'};
    }
  }

  // 🔥 RECOMMEND EXERCISE
  Future<List<dynamic>> recommendExercise(String userId) async {
    try {
      final token = await _getToken();
      final response = await http.post(
        Uri.parse('$_base/api/exercise/recommend-exercise'), // Fixed base route prefix
        headers: {
          'Content-Type': 'application/json',
          if (token != null) 'Authorization': 'Bearer $token',
        },
        body: jsonEncode({'user_id': userId}),
      );
      
      if (response.statusCode == 401) {
        throw Exception("Authentication required");
      }
      
      return jsonDecode(response.body);
    } catch (e) {
      AppLogger.error('API EXERCISE', e);
      return [];
    }
  }

  // ✅ IMPROVED DECODER
  Map<String, dynamic> _decode(http.Response response) {
    try {
      if (response.body.isEmpty) return {"error": "Empty response from server"};
      return jsonDecode(response.body);
    } catch (e) {
      return {
        "error": "Invalid server response",
        "raw": response.body,
        "statusCode": response.statusCode
      };
    }
  }
}
