import 'package:flutter/foundation.dart';
import 'package:nutribot/services/api_service.dart';

class SafetyService extends ChangeNotifier {
  final ApiService _apiService = ApiService();
  
  Map<String, dynamic>? _safetyResult;
  List<dynamic> _exerciseResults = [];
  bool _showExerciseBubble = false;

  Map<String, dynamic>? get safetyResult => _safetyResult;
  List<dynamic> get exerciseResults => _exerciseResults;
  bool get showExerciseBubble => _showExerciseBubble;

  Future<void> checkSafetyAfterMeal(String userId) async {
    try {
      final result = await _apiService.checkSafety(userId);
      _safetyResult = result;
      
      final needsExercise = result['needs_exercise'] == true;
      if (needsExercise) {
        final exercises = await _apiService.recommendExercise(userId);
        _exerciseResults = exercises;
        _showExerciseBubble = true;
      } else {
        _exerciseResults = [];
        _showExerciseBubble = false;
      }
      notifyListeners();
    } catch (e) {
      _safetyResult = {'error': e.toString(), 'safety_label': 'Error', 'risk_level': 'N/A'};
      _showExerciseBubble = false;
      notifyListeners();
    }
  }

  void dismissExerciseBubble() {
    _showExerciseBubble = false;
    notifyListeners();
  }
}
