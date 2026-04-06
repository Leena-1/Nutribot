import 'package:flutter/material.dart';

class ResultDetailScreen extends StatelessWidget {
  final Map<String, dynamic> data;

  const ResultDetailScreen({super.key, required this.data});

  double? _asDouble(dynamic v) {
    if (v == null) return null;
    if (v is num) return v.toDouble();
    return double.tryParse(v.toString());
  }

  Widget _riskGauge(String title, dynamic riskObj) {
    if (riskObj is! Map) return const SizedBox.shrink();
    final prob = _asDouble(riskObj['probability']);
    if (prob == null) return const SizedBox.shrink();

    final clamped = prob.clamp(0.0, 1.0);
    final color = clamped >= 0.7
        ? Colors.red
        : (clamped >= 0.4 ? Colors.orange : Colors.green);

    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        border: Border.all(color: Colors.grey.shade200),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          SizedBox(
            width: 48,
            height: 48,
            child: Stack(
              alignment: Alignment.center,
              children: [
                CircularProgressIndicator(
                  value: clamped,
                  strokeWidth: 6,
                  backgroundColor: Colors.grey.shade200,
                  valueColor: AlwaysStoppedAnimation<Color>(color),
                ),
                Text('${(clamped * 100).round()}%', style: const TextStyle(fontSize: 11)),
              ],
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: const TextStyle(fontWeight: FontWeight.w600)),
                const SizedBox(height: 4),
                Text(
                  clamped >= 0.7
                      ? 'Higher risk'
                      : (clamped >= 0.4 ? 'Moderate risk' : 'Lower risk'),
                  style: TextStyle(color: color, fontSize: 12),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _macroBar({
    required String label,
    required double value,
    required double max,
    required Color color,
    required String unit,
  }) {
    final pct = max <= 0 ? 0.0 : (value / max).clamp(0.0, 1.0);
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(label, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w500)),
              Text('${value.toStringAsFixed(1)} $unit', style: TextStyle(color: Colors.grey.shade700, fontSize: 12)),
            ],
          ),
          const SizedBox(height: 6),
          ClipRRect(
            borderRadius: BorderRadius.circular(999),
            child: LinearProgressIndicator(
              value: pct,
              minHeight: 10,
              backgroundColor: Colors.grey.shade200,
              valueColor: AlwaysStoppedAnimation<Color>(color),
            ),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final name = data['food_name']?.toString() ?? 'Unknown';
    final nutrients = data['nutrients'] is Map ? data['nutrients'] as Map<String, dynamic> : <String, dynamic>{};
    final disease = data['disease_suitability'] is Map ? data['disease_suitability'] as Map<String, dynamic> : <String, dynamic>{};
    final String? notes = data['recommendation_notes']?.toString();
    final String? dietType = data['diet_type']?.toString();

    final calories = _asDouble(nutrients['energy_kcal']) ?? 0.0;
    final protein = _asDouble(nutrients['protein_g']) ?? 0.0;
    final carbs = _asDouble(nutrients['carbohydrates_g']) ?? 0.0;
    final fat = _asDouble(nutrients['total_fat_g']) ?? 0.0;
    final maxMacro = [protein, carbs, fat].reduce((a, b) => a > b ? a : b);

    return Scaffold(
      appBar: AppBar(title: Text(name)),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.blueGrey.shade50,
              borderRadius: BorderRadius.circular(14),
              border: Border.all(color: Colors.blueGrey.shade100),
            ),
            child: Row(
              children: [
                const Icon(Icons.local_fire_department, color: Colors.deepOrange),
                const SizedBox(width: 10),
                Text(
                  '${calories.toStringAsFixed(0)} kcal',
                  style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                const Spacer(),
                if (dietType != null && dietType.isNotEmpty)
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(999),
                      border: Border.all(color: Colors.blueGrey.shade200),
                    ),
                    child: Text(dietType, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600)),
                  ),
              ],
            ),
          ),
          const SizedBox(height: 16),

          const Text('Macro breakdown', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          _macroBar(label: 'Protein', value: protein, max: maxMacro, color: Colors.green, unit: 'g'),
          _macroBar(label: 'Carbs', value: carbs, max: maxMacro, color: Colors.blue, unit: 'g'),
          _macroBar(label: 'Fat', value: fat, max: maxMacro, color: Colors.purple, unit: 'g'),
          const SizedBox(height: 20),

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
          const Text('Risk indicators', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          _riskGauge('Diabetes', disease['diabetes_risk']),
          const SizedBox(height: 10),
          _riskGauge('Blood pressure', disease['blood_pressure_risk']),
          const SizedBox(height: 10),
          _riskGauge('Heart health', disease['heart_risk']),
          const SizedBox(height: 20),

          const Text('Disease suitability', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          if (disease.isEmpty)
            const Text('No suitability data', style: TextStyle(color: Colors.grey))
          else
            ...disease.entries
                .where((e) => e.value is num && (e.key.startsWith('suitable_')))
                .map((e) {
              final v = e.value;
              final ok = v == 1;
              final unknown = v == -1;
              return Padding(
                padding: const EdgeInsets.symmetric(vertical: 4),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(e.key.replaceAll('suitable_', '').replaceAll('_', ' ')),
                    if (unknown)
                      const Icon(Icons.help_outline, color: Colors.grey, size: 22)
                    else
                      Icon(ok ? Icons.check_circle : Icons.cancel,
                          color: ok ? Colors.green : Colors.red, size: 22),
                  ],
                ),
              );
            }),
          if (notes != null && notes.isNotEmpty) ...[
            const SizedBox(height: 24),
            const Text('Diet recommendations', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            Text(notes),
          ],
        ],
      ),
    );
  }
}
