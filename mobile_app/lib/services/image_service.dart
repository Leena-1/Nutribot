import 'dart:io';
import 'dart:typed_data';
import 'package:flutter_image_compress/flutter_image_compress.dart';
import 'package:image_picker/image_picker.dart';

/// Service for optimizing images before upload
class ImageService {
  static const int maxWidth = 720;
  static const int maxHeight = 720;
  static const int quality = 70;

  /// Compress and resize image to optimize upload size
  static Future<Uint8List?> compressImage(XFile imageFile) async {
    try {
      final file = File(imageFile.path);
      if (!await file.exists()) {
        return null;
      }

      // Get file size
      final originalSize = await file.length();
      
      // Compress image
      final compressedData = await FlutterImageCompress.compressWithFile(
        imageFile.path,
        minWidth: maxWidth,
        minHeight: maxHeight,
        quality: quality,
        format: CompressFormat.jpeg,
        keepExif: false,
      );

      if (compressedData == null) {
        return null;
      }

      // Log compression ratio (optional, for debugging)
      final compressedSize = compressedData.length;
      final ratio = ((1 - compressedSize / originalSize) * 100).toStringAsFixed(1);
      print('Image compressed: ${originalSize} -> ${compressedSize} bytes (${ratio}% reduction)');

      return Uint8List.fromList(compressedData);
    } catch (e) {
      print('Image compression error: $e');
      return null;
    }
  }

  /// Get image file size in MB
  static Future<double> getImageSizeMB(XFile imageFile) async {
    try {
      final file = File(imageFile.path);
      if (await file.exists()) {
        return await file.length() / (1024 * 1024);
      }
    } catch (e) {
      print('Error getting image size: $e');
    }
    return 0.0;
  }
}
