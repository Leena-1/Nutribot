import 'package:shared_preferences/shared_preferences.dart';

/// Service to track free trial usage
class UsageTrackerService {
  static const String _chatUsageKey = 'chat_usage_count';
  static const String _analysisUsageKey = 'analysis_usage_count';
  static const int _freeLimit = 5;

  /// Get remaining chat prompts
  Future<int> getRemainingChatPrompts() async {
    final prefs = await SharedPreferences.getInstance();
    final used = prefs.getInt(_chatUsageKey) ?? 0;
    return (_freeLimit - used).clamp(0, _freeLimit);
  }

  /// Get remaining analysis attempts
  Future<int> getRemainingAnalysisAttempts() async {
    final prefs = await SharedPreferences.getInstance();
    final used = prefs.getInt(_analysisUsageKey) ?? 0;
    return (_freeLimit - used).clamp(0, _freeLimit);
  }

  /// Check if chat is available
  Future<bool> canUseChat() async {
    final remaining = await getRemainingChatPrompts();
    return remaining > 0;
  }

  /// Check if analysis is available
  Future<bool> canUseAnalysis() async {
    final remaining = await getRemainingAnalysisAttempts();
    return remaining > 0;
  }

  /// Increment chat usage
  Future<void> incrementChatUsage() async {
    final prefs = await SharedPreferences.getInstance();
    final current = prefs.getInt(_chatUsageKey) ?? 0;
    await prefs.setInt(_chatUsageKey, current + 1);
  }

  /// Increment analysis usage
  Future<void> incrementAnalysisUsage() async {
    final prefs = await SharedPreferences.getInstance();
    final current = prefs.getInt(_analysisUsageKey) ?? 0;
    await prefs.setInt(_analysisUsageKey, current + 1);
  }

  /// Reset usage counts (called after login/signup)
  Future<void> resetUsage() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_chatUsageKey);
    await prefs.remove(_analysisUsageKey);
  }

  /// Get total usage
  Future<Map<String, int>> getUsageStats() async {
    final prefs = await SharedPreferences.getInstance();
    return {
      'chatUsed': prefs.getInt(_chatUsageKey) ?? 0,
      'analysisUsed': prefs.getInt(_analysisUsageKey) ?? 0,
      'chatRemaining': await getRemainingChatPrompts(),
      'analysisRemaining': await getRemainingAnalysisAttempts(),
    };
  }
}
