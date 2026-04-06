import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:nutribot/models/user_model.dart';

/// Authentication service using local storage only (no Firebase).
class AuthService {
  static const String _tokenKey = 'auth_token';
  static const String _userKey = 'user_data';

  /// Check if user is authenticated
  Future<bool> isAuthenticated() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString(_tokenKey);
      return token != null && token.isNotEmpty;
    } catch (e) {
      return false;
    }
  }

  /// Get current user from local storage
  Future<UserModel?> getCurrentUser() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final profileJson = prefs.getString('${_userKey}_profile');
      if (profileJson != null) {
        final profile = jsonDecode(profileJson) as Map<String, dynamic>;
        return UserModel.fromMap(profile);
      }
    } catch (e) {
      print('Error getting current user: $e');
    }
    return null;
  }

  /// Sign up with email and password (local storage only)
  Future<UserModel?> signUp({
    required String email,
    required String password,
    String? displayName,
    String? phoneNumber,
    int? age,
    String? gender,
    bool hasDisease = false,
    String? diseaseType,
  }) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = _generateToken(email);
      final userModel = UserModel(
        id: token,
        email: email,
        displayName: displayName,
        phoneNumber: phoneNumber,
        age: age,
        gender: gender,
        hasDisease: hasDisease,
        diseaseType: diseaseType,
      );

      await prefs.setString(_tokenKey, token);
      await _saveUserProfile(userModel);

      return userModel;
    } catch (e) {
      print('Sign up error: $e');
      rethrow;
    }
  }

  /// Sign in with email and password (local storage only)
  Future<UserModel?> signIn({
    required String email,
    required String password,
  }) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = _generateToken(email);

      // Load profile if exists (user signed up before)
      final profileJson = prefs.getString('${_userKey}_profile');
      if (profileJson != null) {
        final profile = jsonDecode(profileJson) as Map<String, dynamic>;
        final user = UserModel.fromMap(profile);
        // Update token so session is valid
        await prefs.setString(_tokenKey, token);
        return user;
      }

      // New login (no profile yet) - create minimal user
      final userModel = UserModel(
        id: token,
        email: email,
      );

      await prefs.setString(_tokenKey, token);
      await _saveUserProfile(userModel);

      return userModel;
    } catch (e) {
      print('Sign in error: $e');
      rethrow;
    }
  }

  /// Save user profile to local storage
  Future<void> _saveUserProfile(UserModel user) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('${_userKey}_profile', jsonEncode(user.toMap()));
    } catch (e) {
      print('Error saving user profile: $e');
    }
  }

  /// Sign out - clear local storage
  Future<void> signOut() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.remove(_tokenKey);
      await prefs.remove('${_userKey}_profile');
    } catch (e) {
      print('Sign out error: $e');
    }
  }

  String _generateToken(String email) {
    return DateTime.now().millisecondsSinceEpoch.toString() + email.hashCode.toString();
  }
}
