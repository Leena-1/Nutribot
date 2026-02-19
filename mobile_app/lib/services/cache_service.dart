import 'dart:convert';
import 'package:crypto/crypto.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// Service for caching API responses to reduce redundant calls
class CacheService {
  static const String _cachePrefix = 'nutribot_cache_';
  static const Duration _cacheExpiry = Duration(hours: 24);

  /// Generate cache key from image bytes or food name
  static String _generateKey(dynamic input) {
    final bytes = input is List<int> 
        ? input 
        : utf8.encode(input.toString());
    final hash = sha256.convert(bytes);
    return '$_cachePrefix${hash.toString()}';
  }

  /// Store cached result
  static Future<void> setCache(String key, Map<String, dynamic> data) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final cacheData = {
        'data': data,
        'timestamp': DateTime.now().millisecondsSinceEpoch,
      };
      await prefs.setString(key, jsonEncode(cacheData));
    } catch (e) {
      print('Cache write error: $e');
    }
  }

  /// Get cached result if exists and not expired
  static Future<Map<String, dynamic>?> getCache(String key) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final cached = prefs.getString(key);
      if (cached == null) return null;

      final cacheData = jsonDecode(cached) as Map<String, dynamic>;
      final timestamp = cacheData['timestamp'] as int;
      final age = DateTime.now().millisecondsSinceEpoch - timestamp;

      if (age > _cacheExpiry.inMilliseconds) {
        await prefs.remove(key); // Expired, remove it
        return null;
      }

      return cacheData['data'] as Map<String, dynamic>;
    } catch (e) {
      print('Cache read error: $e');
      return null;
    }
  }

  /// Get cache key for image bytes
  static String getImageCacheKey(List<int> imageBytes) {
    return _generateKey(imageBytes);
  }

  /// Get cache key for food name
  static String getFoodNameCacheKey(String foodName) {
    return _generateKey(foodName.toLowerCase().trim());
  }

  /// Clear all cache
  static Future<void> clearCache() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final keys = prefs.getKeys().where((k) => k.startsWith(_cachePrefix));
      for (final key in keys) {
        await prefs.remove(key);
      }
    } catch (e) {
      print('Cache clear error: $e');
    }
  }
}
