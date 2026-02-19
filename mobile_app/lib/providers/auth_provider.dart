import 'package:flutter/foundation.dart';
import 'package:nutribot/models/user_model.dart';
import 'package:nutribot/services/auth_service.dart';

/// Authentication state provider
class AuthProvider with ChangeNotifier {
  final AuthService _authService = AuthService();
  UserModel? _user;
  bool _isLoading = false;
  bool _isInitialized = false;

  UserModel? get user => _user;
  bool get isAuthenticated => _user != null;
  bool get isLoading => _isLoading;

  /// Initialize auth state
  Future<void> initialize() async {
    if (_isInitialized) return;
    _isLoading = true;
    notifyListeners();

    try {
      final isAuth = await _authService.isAuthenticated();
      if (isAuth) {
        _user = await _authService.getCurrentUser();
      }
    } catch (e) {
      print('Auth initialization error: $e');
    } finally {
      _isLoading = false;
      _isInitialized = true;
      notifyListeners();
    }
  }

  /// Sign up
  Future<String?> signUp({
    required String email,
    required String password,
    String? displayName,
    String? phoneNumber,
    int? age,
    String? gender,
    bool hasDisease = false,
    String? diseaseType,
  }) async {
    _isLoading = true;
    notifyListeners();

    try {
      _user = await _authService.signUp(
        email: email,
        password: password,
        displayName: displayName,
        phoneNumber: phoneNumber,
        age: age,
        gender: gender,
        hasDisease: hasDisease,
        diseaseType: diseaseType,
      );
      return null; // Success
    } catch (e) {
      return e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Sign in
  Future<String?> signIn({
    required String email,
    required String password,
  }) async {
    _isLoading = true;
    notifyListeners();

    try {
      _user = await _authService.signIn(
        email: email,
        password: password,
      );
      return null; // Success
    } catch (e) {
      return e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Sign out
  Future<void> signOut() async {
    _isLoading = true;
    notifyListeners();

    try {
      await _authService.signOut();
      _user = null;
    } catch (e) {
      print('Sign out error: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
}
