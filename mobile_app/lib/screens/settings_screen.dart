import 'package:flutter/material.dart';

class SettingsScreen extends StatelessWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Settings')),
      body: const ListView(
        children: [
          ListTile(
            title: Text('API URL'),
            subtitle: Text('Change backend base URL (e.g. http://10.0.2.2:8000)'),
          ),
        ],
      ),
    );
  }
}
