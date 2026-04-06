import 'package:flutter/foundation.dart';

/// Centralized debug logging. Only prints in debug mode.
class AppLogger {
  static void auth(String message, [Object? detail]) {
    if (kDebugMode) {
      final detailStr = detail != null ? ' | $detail' : '';
      debugPrint('[AUTH] $message$detailStr');
    }
  }

  static void api(String message, [Object? detail]) {
    if (kDebugMode) {
      final detailStr = detail != null ? ' | $detail' : '';
      debugPrint('[API] $message$detailStr');
    }
  }

  static void nav(String message) {
    if (kDebugMode) {
      debugPrint('[NAV] $message');
    }
  }

  static void error(String tag, Object error, [StackTrace? stack]) {
    if (kDebugMode) {
      debugPrint('[$tag] ERROR: $error');
      if (stack != null) debugPrint(stack.toString());
    }
  }

  static void timing(String label, Duration duration) {
    if (kDebugMode) {
      debugPrint('[TIMING] $label: ${duration.inMilliseconds}ms');
    }
  }
}
