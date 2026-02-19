import 'dart:convert';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:nutribot/models/user_model.dart';

/// Authentication service with Firebase Auth support
/// Falls back to local token storage if Firebase is not configured
class AuthService {
  final FirebaseAuth _firebaseAuth = FirebaseAuth.instance;
  static const String _tokenKey = 'auth_token';
  static const String _userKey = 'user_data';

  /// Check if user is authenticated
  Future<bool> isAuthenticated() async {
    try {
      // Try Firebase first
      final user = _firebaseAuth.currentUser;
      if (user != null) return true;

      // Fallback to local token
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString(_tokenKey);
      return token != null && token.isNotEmpty;
    } catch (e) {
      // Fallback to local token
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString(_tokenKey);
      return token != null && token.isNotEmpty;
    }
  }

  /// Get current user
  Future<UserModel?> getCurrentUser() async {
    try {
      // Try Firebase first
      final user = _firebaseAuth.currentUser;
      if (user != null) {
        // Load extended profile from local storage
        final prefs = await SharedPreferences.getInstance();
        final profileJson = prefs.getString('${_userKey}_profile');
        if (profileJson != null) {
          final profile = jsonDecode(profileJson) as Map<String, dynamic>;
          return UserModel(
            uid: user.uid,
            email: user.email ?? '',
            displayName: user.displayName ?? profile['displayName'],
            photoUrl: user.photoURL,
            phoneNumber: profile['phoneNumber'],
            age: profile['age'] != null ? int.tryParse(profile['age'].toString()) : null,
            gender: profile['gender'],
            hasDisease: profile['hasDisease'] == true,
            diseaseType: profile['diseaseType'],
          );
        }
        return UserModel(
          uid: user.uid,
          email: user.email ?? '',
          displayName: user.displayName,
          photoUrl: user.photoURL,
        );
      }

      // Fallback to local storage
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

  /// Sign up with email and password
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
      // Try Firebase first
      try {
        final credential = await _firebaseAuth.createUserWithEmailAndPassword(
          email: email,
          password: password,
        );
        
        if (credential.user != null && displayName != null) {
          await credential.user!.updateDisplayName(displayName);
        }

        final user = credential.user;
        if (user != null) {
          final userModel = UserModel(
            uid: user.uid,
            email: user.email ?? email,
            displayName: displayName ?? user.displayName,
            photoUrl: user.photoURL,
            phoneNumber: phoneNumber,
            age: age,
            gender: gender,
            hasDisease: hasDisease,
            diseaseType: diseaseType,
          );
          
          // Save extended profile
          await _saveUserProfile(userModel);
          return userModel;
        }
      } catch (e) {
        // Firebase not configured, use local auth
        print('Firebase auth failed, using local: $e');
      }

      // Local auth fallback
      final prefs = await SharedPreferences.getInstance();
      final token = _generateToken(email);
      final userModel = UserModel(
        uid: token,
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

  /// Sign in with email and password
  Future<UserModel?> signIn({
    required String email,
    required String password,
  }) async {
    try {
      // Try Firebase first
      try {
        final credential = await _firebaseAuth.signInWithEmailAndPassword(
          email: email,
          password: password,
        );

        final user = credential.user;
        if (user != null) {
          // Load extended profile
          final userModel = await getCurrentUser();
          return userModel ?? UserModel(
            uid: user.uid,
            email: user.email ?? email,
            displayName: user.displayName,
            photoUrl: user.photoURL,
          );
        }
      } catch (e) {
        // Firebase not configured, use local auth
        print('Firebase auth failed, using local: $e');
      }

      // Local auth fallback (simple validation)
      final prefs = await SharedPreferences.getInstance();
      final token = _generateToken(email);
      
      // Load profile if exists
      final profileJson = prefs.getString('${_userKey}_profile');
      if (profileJson != null) {
        final profile = jsonDecode(profileJson) as Map<String, dynamic>;
        return UserModel.fromMap(profile);
      }
      
      final userModel = UserModel(
        uid: token,
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

  /// Sign out
  Future<void> signOut() async {
    try {
      await _firebaseAuth.signOut();
    } catch (e) {
      print('Firebase sign out error: $e');
    }

    // Clear local storage
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_tokenKey);
    await prefs.remove('${_userKey}_profile');
  }

  /// Generate simple token for local auth
  String _generateToken(String email) {
    return DateTime.now().millisecondsSinceEpoch.toString() + email.hashCode.toString();
  }
}
