import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:provider/provider.dart';
import 'package:nutribot/services/api_service.dart';
import 'package:nutribot/services/image_service.dart';
import 'package:nutribot/screens/result_detail_screen.dart';
import 'package:nutribot/providers/auth_provider.dart';
import 'package:nutribot/providers/usage_provider.dart';
import 'package:nutribot/widgets/auth_required_dialog.dart';
import 'package:nutribot/widgets/trial_limit_dialog.dart';

class ScanScreen extends StatefulWidget {
  const ScanScreen({super.key});

  @override
  State<ScanScreen> createState() => _ScanScreenState();
}

class _ScanScreenState extends State<ScanScreen> {
  final _api = ApiService();
  bool _loading = false;
  String? _error;
  String _statusText = '';

  Future<void> _pickImage(ImageSource source) async {
    final authProvider = context.read<AuthProvider>();
    final usageProvider = context.read<UsageProvider>();

    // Check authentication
    if (!authProvider.isAuthenticated) {
      if (mounted) {
        showDialog(
          context: context,
          builder: (context) => const AuthRequiredDialog(),
        );
      }
      return;
    }

    // Check usage limit
    final canUse = await usageProvider.canUseAnalysis();
    if (!canUse) {
      if (mounted) {
        showDialog(
          context: context,
          builder: (context) => const TrialLimitDialog(),
        );
      }
      return;
    }

    setState(() {
      _loading = true;
      _error = null;
      _statusText = 'Selecting image...';
    });

    try {
      final picker = ImagePicker();
      final xfile = await picker.pickImage(source: source);
      
      if (xfile == null || !mounted) {
        setState(() => _loading = false);
        return;
      }

      // Show compression status
      setState(() => _statusText = 'Compressing image...');
      
      // Compress image before upload
      final compressedBytes = await ImageService.compressImage(xfile);
      
      if (compressedBytes == null || compressedBytes.isEmpty) {
        if (mounted) {
          setState(() {
            _loading = false;
            _error = 'Failed to process image';
          });
        }
        return;
      }

      // Show upload status
      setState(() => _statusText = 'Uploading image...');

      // Upload compressed image
      final result = await _api.predictFood(
        imageBytes: compressedBytes,
        useCache: true,
      );

      if (!mounted) return;

      setState(() {
        _loading = false;
        _statusText = '';
      });

      if (result.containsKey('error')) {
        setState(() => _error = result['error']?.toString() ?? 'Request failed');
        return;
      }

      // Show analysis status
      setState(() {
        _loading = true;
        _statusText = 'Analyzing nutrients...';
      });

      // Small delay to show status (actual analysis happens on backend)
      await Future.delayed(const Duration(milliseconds: 300));

      if (!mounted) return;

      // Increment usage
      await usageProvider.useAnalysis();

      setState(() {
        _loading = false;
        _statusText = '';
      });

      Navigator.of(context).push(
        MaterialPageRoute(
          builder: (_) => ResultDetailScreen(data: result),
        ),
      );
    } catch (e) {
      if (mounted) {
        setState(() {
          _loading = false;
          _error = 'Error: ${e.toString()}';
          _statusText = '';
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const SizedBox(height: 24),
          const Text(
            'Analyze food',
            style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 8),
          const Text(
            'Take a photo or choose from gallery to get nutrients and disease suitability.',
            style: TextStyle(color: Colors.grey),
          ),
          const SizedBox(height: 32),
          if (_error != null)
            Container(
              padding: const EdgeInsets.all(12),
              margin: const EdgeInsets.only(bottom: 16),
              decoration: BoxDecoration(
                color: Colors.red.shade50,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.red.shade200),
              ),
              child: Row(
                children: [
                  Icon(Icons.error_outline, color: Colors.red.shade700, size: 20),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      _error!,
                      style: TextStyle(color: Colors.red.shade700, fontSize: 13),
                    ),
                  ),
                ],
              ),
            ),
          if (_loading)
            Container(
              padding: const EdgeInsets.all(24),
              child: Column(
                children: [
                  const CircularProgressIndicator(),
                  const SizedBox(height: 16),
                  if (_statusText.isNotEmpty)
                    Text(
                      _statusText,
                      style: TextStyle(
                        color: Colors.grey.shade600,
                        fontSize: 14,
                      ),
                      textAlign: TextAlign.center,
                    ),
                ],
              ),
            )
          else ...[
            ElevatedButton.icon(
              onPressed: () => _pickImage(ImageSource.camera),
              icon: const Icon(Icons.camera_alt),
              label: const Text('Take photo'),
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 16),
              ),
            ),
            const SizedBox(height: 12),
            OutlinedButton.icon(
              onPressed: () => _pickImage(ImageSource.gallery),
              icon: const Icon(Icons.photo_library),
              label: const Text('Choose from gallery'),
              style: OutlinedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 16),
              ),
            ),
          ],
        ],
      ),
    );
  }
}
