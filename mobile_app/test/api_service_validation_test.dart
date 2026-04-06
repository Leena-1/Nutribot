import 'package:flutter_test/flutter_test.dart';
import 'package:nutribot/services/api_service.dart';
import 'dart:typed_data';

void main() {
  group('ApiService logic tests', () {
    final api = ApiService();

    test('predictFood validation - empty inputs', () async {
      final result = await api.predictFood(imageBytes: [], foodName: '');
      expect(result.containsKey('error'), isTrue);
      expect(result['error'], contains('Provide either an image or a food name'));
    });

    test('predictFood validation - small image', () async {
      final result = await api.predictFood(imageBytes: Uint8List(10)); // 10 bytes
      expect(result.containsKey('error'), isTrue);
      expect(result['error'], contains('Invalid image data (too small)'));
    });
  });
}
