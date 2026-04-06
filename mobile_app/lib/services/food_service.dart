import 'package:flutter/foundation.dart';
import 'package:nutribot/services/api_service.dart';

class FoodService extends ChangeNotifier {
  final ApiService _apiService = ApiService();
  
  bool _isLoading = false;
  List<dynamic> _lastResults = [];

  bool get isLoading => _isLoading;
  List<dynamic> get lastResults => _lastResults;

  Future<void> searchFood(String foodName, String medicalCondition, String dietType) async {
    _isLoading = true;
    notifyListeners();

    try {
      final results = await _apiService.searchFood(foodName, medicalCondition, dietType);
      _lastResults = results;
    } catch (e) {
      _lastResults = [];
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  void clearResults() {
    _lastResults = [];
    notifyListeners();
  }
}
