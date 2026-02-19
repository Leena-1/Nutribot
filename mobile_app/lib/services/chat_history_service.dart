import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';

/// Service to store and retrieve chat history
class ChatHistoryService {
  static const String _historyKey = 'chat_history';

  /// Save a chat message to history
  Future<void> saveMessage({
    required String query,
    required String response,
    required DateTime timestamp,
  }) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final historyJson = prefs.getString(_historyKey);
      final List<Map<String, dynamic>> history = historyJson != null
          ? List<Map<String, dynamic>>.from(jsonDecode(historyJson))
          : [];

      history.add({
        'query': query,
        'response': response,
        'timestamp': timestamp.toIso8601String(),
      });

      // Keep only last 100 messages
      if (history.length > 100) {
        history.removeRange(0, history.length - 100);
      }

      await prefs.setString(_historyKey, jsonEncode(history));
    } catch (e) {
      print('Error saving chat history: $e');
    }
  }

  /// Get all chat history
  Future<List<Map<String, dynamic>>> getHistory() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final historyJson = prefs.getString(_historyKey);
      if (historyJson == null) return [];

      final List<dynamic> decoded = jsonDecode(historyJson);
      return decoded.map((e) => Map<String, dynamic>.from(e)).toList();
    } catch (e) {
      print('Error loading chat history: $e');
      return [];
    }
  }

  /// Clear chat history
  Future<void> clearHistory() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.remove(_historyKey);
    } catch (e) {
      print('Error clearing chat history: $e');
    }
  }

  /// Get recent chat history (last N messages)
  Future<List<Map<String, dynamic>>> getRecentHistory({int limit = 20}) async {
    final history = await getHistory();
    if (history.length <= limit) return history;
    return history.sublist(history.length - limit);
  }
}
