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
  final ApiService _api = ApiService();

  bool _loading = false;
  String? _error;
  String _statusText = '';

  Future<void> _pickImage(ImageSource source) async {
    final authProvider = context.read<AuthProvider>();
    final usageProvider = context.read<UsageProvider>();

    if (!authProvider.isAuthenticated) {
      showDialog(context: context, builder: (_) => const AuthRequiredDialog());
      return;
    }

    final canUse = await usageProvider.canUseAnalysis();
    if (!canUse) {
      showDialog(context: context, builder: (_) => const TrialLimitDialog());
      return;
    }

    setState(() {
      _loading = true;
      _error = null;
      _statusText = "Selecting image...";
    });

    try {
      final picker = ImagePicker();
      final XFile? file = await picker.pickImage(source: source);

      if (file == null) {
        setState(() => _loading = false);
        return;
      }

      setState(() => _statusText = "Compressing image...");

      final bytes = await ImageService.compressImage(file);

      if (bytes == null || bytes.isEmpty) {
        setState(() {
          _loading = false;
          _error = "Image processing failed";
        });
        return;
      }

      setState(() => _statusText = "Uploading...");

      final result = await _api.predictFood(imageBytes: bytes);

      setState(() {
        _loading = false;
        _statusText = '';
      });

      if (result.containsKey('error')) {
        setState(() => _error = result['error'].toString());
        return;
      }

      await usageProvider.useAnalysis();

      if (!mounted) return;

      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (_) => ResultDetailScreen(data: result),
        ),
      );
    } catch (e) {
      setState(() {
        _loading = false;
        _error = e.toString();
        _statusText = '';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        children: [
          const SizedBox(height: 20),
          const Text(
            "Analyze Food",
            style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 20),

          if (_error != null)
            Text(_error!, style: const TextStyle(color: Colors.red)),

          if (_loading)
            Column(
              children: [
                const CircularProgressIndicator(),
                const SizedBox(height: 10),
                Text(_statusText),
              ],
            )
          else ...[
            ElevatedButton(
              onPressed: () => _pickImage(ImageSource.camera),
              child: const Text("Camera"),
            ),
            const SizedBox(height: 10),
            ElevatedButton(
              onPressed: () => _pickImage(ImageSource.gallery),
              child: const Text("Gallery"),
            ),
          ]
        ],
      ),
    );
  }
}
