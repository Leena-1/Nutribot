import 'package:flutter/foundation.dart';
import 'package:nutribot/services/usage_tracker_service.dart';

/// Usage tracking provider for free trial
class UsageProvider with ChangeNotifier {
  final UsageTrackerService _usageService = UsageTrackerService();
  
  int _chatRemaining = 5;
  int _analysisRemaining = 5;
  bool _isLoading = false;

  int get chatRemaining => _chatRemaining;
  int get analysisRemaining => _analysisRemaining;
  bool get isLoading => _isLoading;

  /// Load usage stats
  Future<void> loadUsage() async {
    _isLoading = true;
    notifyListeners();

    try {
      final stats = await _usageService.getUsageStats();
      _chatRemaining = stats['chatRemaining'] ?? 5;
      _analysisRemaining = stats['analysisRemaining'] ?? 5;
    } catch (e) {
      print('Error loading usage: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Check if chat can be used
  Future<bool> canUseChat() async {
    return await _usageService.canUseChat();
  }

  /// Check if analysis can be used
  Future<bool> canUseAnalysis() async {
    return await _usageService.canUseAnalysis();
  }

  /// Use chat prompt
  Future<void> useChat() async {
    await _usageService.incrementChatUsage();
    await loadUsage();
  }

  /// Use analysis
  Future<void> useAnalysis() async {
    await _usageService.incrementAnalysisUsage();
    await loadUsage();
  }

  /// Reset usage (after login/signup)
  Future<void> resetUsage() async {
    await _usageService.resetUsage();
    await loadUsage();
  }
}
