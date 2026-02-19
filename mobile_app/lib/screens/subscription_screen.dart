import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:flutter_animate/flutter_animate.dart';

class SubscriptionScreen extends StatelessWidget {
  const SubscriptionScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(
          'Upgrade to Premium',
          style: GoogleFonts.poppins(fontWeight: FontWeight.bold),
        ),
        elevation: 0,
      ),
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              Colors.green.shade50,
              Colors.teal.shade50,
              Colors.blue.shade50,
            ],
          ),
        ),
        child: SafeArea(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: Column(
              children: [
                // Premium badge
                Container(
                  padding: const EdgeInsets.all(24),
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      colors: [
                        Colors.amber.shade400,
                        Colors.orange.shade600,
                      ],
                    ),
                    borderRadius: BorderRadius.circular(20),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.amber.withOpacity(0.3),
                        blurRadius: 20,
                        offset: const Offset(0, 10),
                      ),
                    ],
                  ),
                  child: Column(
                    children: [
                      Icon(
                        Icons.star,
                        size: 60,
                        color: Colors.white,
                      )
                          .animate()
                          .scale(delay: 200.ms, duration: 600.ms)
                          .fadeIn(delay: 200.ms, duration: 600.ms),
                      const SizedBox(height: 16),
                      Text(
                        'Premium',
                        style: GoogleFonts.poppins(
                          fontSize: 32,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                        ),
                      )
                          .animate()
                          .fadeIn(delay: 400.ms, duration: 600.ms)
                          .slideY(begin: 0.2, end: 0, delay: 400.ms, duration: 600.ms),
                    ],
                  ),
                ),

                const SizedBox(height: 32),

                // Features
                _buildFeature(
                  icon: Icons.all_inclusive,
                  title: 'Unlimited Analysis',
                  description: 'Analyze unlimited food images',
                )
                    .animate()
                    .fadeIn(delay: 600.ms, duration: 600.ms)
                    .slideX(begin: -0.2, end: 0, delay: 600.ms, duration: 600.ms),

                const SizedBox(height: 16),

                _buildFeature(
                  icon: Icons.chat_bubble_outline,
                  title: 'Unlimited Chat',
                  description: 'Ask unlimited questions to AI',
                )
                    .animate()
                    .fadeIn(delay: 700.ms, duration: 600.ms)
                    .slideX(begin: -0.2, end: 0, delay: 700.ms, duration: 600.ms),

                const SizedBox(height: 16),

                _buildFeature(
                  icon: Icons.speed,
                  title: 'Priority Processing',
                  description: 'Faster response times',
                )
                    .animate()
                    .fadeIn(delay: 800.ms, duration: 600.ms)
                    .slideX(begin: -0.2, end: 0, delay: 800.ms, duration: 600.ms),

                const SizedBox(height: 16),

                _buildFeature(
                  icon: Icons.cloud_download,
                  title: 'Export Reports',
                  description: 'Download nutrition reports',
                )
                    .animate()
                    .fadeIn(delay: 900.ms, duration: 600.ms)
                    .slideX(begin: -0.2, end: 0, delay: 900.ms, duration: 600.ms),

                const SizedBox(height: 40),

                // Pricing
                Container(
                  padding: const EdgeInsets.all(24),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(20),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.1),
                        blurRadius: 20,
                        offset: const Offset(0, 10),
                      ),
                    ],
                  ),
                  child: Column(
                    children: [
                      Text(
                        '\$9.99',
                        style: GoogleFonts.poppins(
                          fontSize: 48,
                          fontWeight: FontWeight.bold,
                          color: Colors.green.shade600,
                        ),
                      ),
                      Text(
                        'per month',
                        style: GoogleFonts.poppins(
                          fontSize: 16,
                          color: Colors.grey.shade600,
                        ),
                      ),
                    ],
                  ),
                )
                    .animate()
                    .fadeIn(delay: 1000.ms, duration: 600.ms)
                    .scale(delay: 1000.ms, duration: 600.ms),

                const SizedBox(height: 32),

                // Subscribe button
                ElevatedButton(
                  onPressed: () {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Text(
                          'Premium subscription coming soon!',
                          style: GoogleFonts.poppins(),
                        ),
                        backgroundColor: Colors.green.shade600,
                        behavior: SnackBarBehavior.floating,
                      ),
                    );
                  },
                  style: ElevatedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 18),
                    backgroundColor: Colors.green.shade600,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(30),
                    ),
                    elevation: 4,
                  ),
                  child: SizedBox(
                    width: double.infinity,
                    child: Text(
                      'Subscribe Now',
                      style: GoogleFonts.poppins(
                        color: Colors.white,
                        fontWeight: FontWeight.w600,
                        fontSize: 18,
                      ),
                      textAlign: TextAlign.center,
                    ),
                  ),
                )
                    .animate()
                    .fadeIn(delay: 1100.ms, duration: 600.ms)
                    .slideY(begin: 0.2, end: 0, delay: 1100.ms, duration: 600.ms),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildFeature({
    required IconData icon,
    required String title,
    required String description,
  }) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.green.shade50,
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(icon, color: Colors.green.shade600, size: 24),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: GoogleFonts.poppins(
                    fontWeight: FontWeight.w600,
                    color: Colors.grey.shade800,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  description,
                  style: GoogleFonts.poppins(
                    fontSize: 14,
                    color: Colors.grey.shade600,
                  ),
                ),
              ],
            ),
          ),
          Icon(Icons.check_circle, color: Colors.green.shade600),
        ],
      ),
    );
  }
}
