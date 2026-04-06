import 'dart:async';
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:nutribot/models/user_model.dart';
import 'package:nutribot/utils/app_logger.dart';
import 'package:nutribot/services/api_service.dart';

class AuthProvider with ChangeNotifier {
  UserModel? _user;
  bool _isLoading = false;
  bool _isInitialized = false;

  static const Duration _authTimeout = Duration(seconds: 20);

  UserModel? get user => _user;
  bool get isAuthenticated => _user != null;
  bool get isLoading => _isLoading;

  // ================= INIT =================
  Future<void> initialize() async {
    if (_isInitialized) return;
    _isInitialized = true;
  }

  // ================= HELPERS (ERROR PARSING) =================
  String _parseError(http.Response response) {
    AppLogger.error('AUTH ERROR', 'Status: ${response.statusCode}, Body: ${response.body}');
    
    try {
      final data = jsonDecode(response.body);
      
      // 1. Check for standard FastAPI "detail"
      if (data["detail"] != null) {
        if (data["detail"] is String) {
          return data["detail"];
        } else if (data["detail"] is List && data["detail"].isNotEmpty) {
          // Pydantic validation error
          return data["detail"][0]["msg"]?.toString() ?? "Validation error";
        }
      }
      
      // 2. Check for custom "error" object from AppError
      if (data["error"] != null && data["error"]["message"] != null) {
        return data["error"]["message"];
      }
      
      return "Request failed (Status: ${response.statusCode})";
    } catch (e) {
      return "Server error: ${response.statusCode}";
    }
  }

  // ================= SIGN UP =================
  Future<String?> signUp({
    required String email,
    required String password,
    String? displayName,
    String? phoneNumber,
    int? age,
    double? weight,
    String? gender,
    bool? hasDisease,
    String? diseaseType,
    required String name,
  }) async {
    _isLoading = true;
    notifyListeners();

    try {
      final response = await http
          .post(
            Uri.parse("${ApiService.baseUrl}/api/signup"),
            headers: {"Content-Type": "application/json"},
            body: jsonEncode({
              "full_name": name,
              "email": email,
              "password": password,
              "age": age ?? 0,
              "weight": weight ?? 0.0,
              "gender": gender ?? "Other",
              "diseases": (diseaseType != null && diseaseType.isNotEmpty) 
                  ? diseaseType.split(', ').map((d) => d.trim()).toList() 
                  : [],
            }),
          )
          .timeout(_authTimeout);

      if (response.statusCode == 200 || response.statusCode == 201) {
        return null; // success
      } else {
        return _parseError(response);
      }
    } on TimeoutException {
      return "Connection timeout. Check your connection or IP (${ApiService.baseUrl})";
    } on Exception catch (e) {
      AppLogger.error('AUTH SIGNUP', e);
      return "Connectivity error. Ensure server is reachable.";
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  // ================= SIGN IN =================
  Future<String?> signIn({
    required String email,
    required String password,
  }) async {
    _isLoading = true;
    notifyListeners();

    try {
      final response = await http
          .post(
            Uri.parse("${ApiService.baseUrl}/api/login"),
            headers: {"Content-Type": "application/json"},
            body: jsonEncode({
              "email": email,
              "password": password,
            }),
          )
          .timeout(_authTimeout);

      if (response.statusCode != 200) {
        return _parseError(response);
      }

      final data = jsonDecode(response.body);

      if (data["user_id"] == null) {
        return "Invalid server response";
      }

      // ✅ SUCCESS → CREATE USER WITH FULL PROFILE
      _user = UserModel.fromMap(data);
      
      // Update usage if needed (optional)
      notifyListeners();
      return null;
    } on TimeoutException {
      return "Server timeout. Try again.";
    } catch (e, st) {
      AppLogger.error('AUTH SIGNIN', e, st);
      return "Something went wrong";
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  // ================= SIGN OUT =================
  Future<void> signOut() async {
    _user = null;
    notifyListeners();
  }
}
