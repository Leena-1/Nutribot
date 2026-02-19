import 'package:flutter/material.dart';

class ResultDetailScreen extends StatelessWidget {
  final Map<String, dynamic> data;

  const ResultDetailScreen({super.key, required this.data});

  @override
  Widget build(BuildContext context) {
    final name = data['food_name']?.toString() ?? 'Unknown';
    final nutrients = data['nutrients'] is Map ? data['nutrients'] as Map<String, dynamic> : <String, dynamic>{};
    final disease = data['disease_suitability'] is Map ? data['disease_suitability'] as Map<String, dynamic> : <String, dynamic>{};
    final String? notes = data['recommendation_notes']?.toString();

    return Scaffold(
      appBar: AppBar(title: Text(name)),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const Text('Nutrients', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          if (nutrients.isEmpty)
            const Text('No nutrient data', style: TextStyle(color: Colors.grey))
          else
            ...nutrients.entries.map((e) => Padding(
                  padding: const EdgeInsets.symmetric(vertical: 4),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(e.key),
                      Text('${e.value}'),
                    ],
                  ),
                )),
          const SizedBox(height: 24),
          const Text('Disease suitability', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          ...disease.entries.map((e) {
            final v = e.value;
            final ok = v == 1;
            return Padding(
              padding: const EdgeInsets.symmetric(vertical: 4),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(e.key),
                  Icon(ok ? Icons.check_circle : Icons.cancel, color: ok ? Colors.green : Colors.red, size: 22),
                ],
              ),
            );
          }),
          if (notes != null && notes.isNotEmpty) ...[
            const SizedBox(height: 24),
            const Text('Notes', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            Text(notes),
          ],
        ],
      ),
    );
  }
}
