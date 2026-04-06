import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import 'package:nutribot/models/user_model.dart';
import 'package:nutribot/providers/auth_provider.dart';
import 'package:nutribot/providers/usage_provider.dart';
import 'package:flutter_animate/flutter_animate.dart';

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

  Future<void> _handleLogout(BuildContext context) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: Colors.white.withOpacity(0.9),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(28)),
        title: Text('Logout', style: GoogleFonts.poppins(fontWeight: FontWeight.bold, fontSize: 22)),
        content: Text('Are you sure you want to logout from your account?', style: GoogleFonts.poppins(fontSize: 16)),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: Text('Cancel', style: GoogleFonts.poppins(color: Colors.grey.shade600, fontWeight: FontWeight.w600)),
          ),
          Container(
            margin: const EdgeInsets.only(right: 8, bottom: 8),
            child: ElevatedButton(
              onPressed: () => Navigator.pop(context, true),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.redAccent,
                foregroundColor: Colors.white,
                elevation: 0,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
              ),
              child: Text('Logout', style: GoogleFonts.poppins(fontWeight: FontWeight.bold)),
            ),
          ),
        ],
      ),
    );

    if (confirmed == true && context.mounted) {
      final authProvider = context.read<AuthProvider>();
      await authProvider.signOut();
      if (context.mounted) {
        Navigator.pushNamedAndRemoveUntil(context, '/login', (route) => false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final authProvider = context.watch<AuthProvider>();
    final usageProvider = context.watch<UsageProvider>();
    final user = authProvider.user;

    return Scaffold(
      extendBodyBehindAppBar: true,
      backgroundColor: const Color(0xFF0F172A), // Dark slate background for premium feel
      body: Stack(
        children: [
          // Background Gradient Blobs
          Positioned(
            top: -100,
            right: -100,
            child: _buildBlob(300, Colors.teal.withOpacity(0.2)),
          ),
          Positioned(
            bottom: 100,
            left: -150,
            child: _buildBlob(400, Colors.blue.withOpacity(0.15)),
          ),
          
          SingleChildScrollView(
            child: SafeArea(
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 20),
                child: Column(
                  children: [
                    const SizedBox(height: 30),
                    
                    // Profile Header Card (Glassmorphism)
                    _buildGlassCard(
                      child: Column(
                        children: [
                          _buildProfileAvatar(user),
                          const SizedBox(height: 16),
                          Text(
                            user?.displayName ?? 'Health Enthusiast',
                            style: GoogleFonts.outfit(
                              fontSize: 28,
                              fontWeight: FontWeight.bold,
                              color: Colors.white,
                              letterSpacing: -0.5,
                            ),
                          ),
                          Text(
                            user?.email ?? 'Join Nutribot Plus',
                            style: GoogleFonts.poppins(
                              fontSize: 14,
                              color: Colors.white.withOpacity(0.6),
                              fontWeight: FontWeight.w400,
                            ),
                          ),
                          const SizedBox(height: 24),
                          
                          // Bio Stats Row
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceAround,
                            children: [
                              _buildBioStat('Age', '${user?.age ?? "--"}'),
                              _buildVerticalDivider(),
                              _buildBioStat('Weight', '${user?.weight ?? "--"} kg'),
                              _buildVerticalDivider(),
                              _buildBioStat('Gender', '${user?.gender?.toUpperCase() ?? "--"}'),
                            ],
                          ),
                        ],
                      ),
                    ).animate().fadeIn(duration: 600.ms).slideY(begin: 0.1, end: 0),

                    const SizedBox(height: 24),

                    // Health Conditions Section
                    if (user?.hasDisease == true) 
                      _buildConditionSection(user?.diseaseType ?? "Managed Condition")
                      .animate().fadeIn(delay: 200.ms),

                    const SizedBox(height: 24),

                    // Usage Section Title
                    Align(
                      alignment: Alignment.centerLeft,
                      child: Text(
                        'Daily Insights',
                        style: GoogleFonts.outfit(
                          fontSize: 20,
                          fontWeight: FontWeight.w600,
                          color: Colors.white,
                        ),
                      ),
                    ).animate().fadeIn(delay: 300.ms),
                    
                    const SizedBox(height: 16),

                    // Usage Cards Row
                    Row(
                      children: [
                        Expanded(
                          child: _buildUsageSquare(
                            'Chat', 
                            usageProvider.chatRemaining, 
                            5, 
                            Icons.chat_bubble_outline_rounded,
                            Colors.blueAccent,
                          ),
                        ),
                        const SizedBox(width: 16),
                        Expanded(
                          child: _buildUsageSquare(
                            'Scan', 
                            usageProvider.analysisRemaining, 
                            5, 
                            Icons.camera_rounded,
                            Colors.greenAccent,
                          ),
                        ),
                      ],
                    ).animate().fadeIn(delay: 400.ms).slideY(begin: 0.1, end: 0),

                    const SizedBox(height: 32),

                    // Premium Upgrade Button
                    Container(
                      width: double.infinity,
                      height: 60,
                      decoration: BoxDecoration(
                        gradient: const LinearGradient(
                          colors: [Color(0xFF6366F1), Color(0xFFA855F7)],
                          begin: Alignment.centerLeft,
                          end: Alignment.centerRight,
                        ),
                        borderRadius: BorderRadius.circular(20),
                        boxShadow: [
                          BoxShadow(
                            color: const Color(0xFF6366F1).withOpacity(0.4),
                            blurRadius: 20,
                            offset: const Offset(0, 10),
                          ),
                        ],
                      ),
                      child: ElevatedButton(
                        onPressed: () => Navigator.pushNamed(context, '/subscription'),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.transparent,
                          shadowColor: Colors.transparent,
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
                        ),
                        child: Text(
                          'Unlock Nutribot Plus',
                          style: GoogleFonts.outfit(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                            color: Colors.white,
                          ),
                        ),
                      ),
                    ).animate().fadeIn(delay: 500.ms).scale(delay: 600.ms, begin: const Offset(0.9, 0.9), curve: Curves.elasticOut),

                    const SizedBox(height: 20),

                    // Logout Button
                    TextButton.icon(
                      onPressed: () => _handleLogout(context),
                      icon: const Icon(Icons.power_settings_new_rounded, color: Colors.redAccent, size: 20),
                      label: Text(
                        'Sign Out',
                        style: GoogleFonts.poppins(
                          color: Colors.redAccent,
                          fontWeight: FontWeight.w600,
                          fontSize: 15,
                        ),
                      ),
                      style: TextButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 24),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                      ),
                    ).animate().fadeIn(delay: 700.ms),
                    
                    const SizedBox(height: 40),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildBlob(double size, Color color) {
    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        color: color,
      ),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 70.0, sigmaY: 70.0),
        child: Container(color: Colors.transparent),
      ),
    );
  }

  Widget _buildGlassCard({required Widget child}) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.05),
        borderRadius: BorderRadius.circular(30),
        border: Border.all(color: Colors.white.withOpacity(0.1), width: 1.5),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.2),
            blurRadius: 40,
            offset: const Offset(0, 20),
          ),
        ],
      ),
      child: child,
    );
  }

  Widget _buildProfileAvatar(UserModel? user) {
    return Container(
      padding: const EdgeInsets.all(4),
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        gradient: const LinearGradient(
          colors: [Colors.tealAccent, Colors.blueAccent],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.tealAccent.withOpacity(0.3),
            blurRadius: 20,
            spreadRadius: 2,
          ),
        ],
      ),
      child: CircleAvatar(
        radius: 54,
        backgroundColor: const Color(0xFF1E293B),
        child: Text(
          (user?.displayName ?? 'N')[0].toUpperCase(),
          style: GoogleFonts.outfit(
            fontSize: 44,
            fontWeight: FontWeight.w800,
            color: Colors.white,
          ),
        ),
      ),
    );
  }

  Widget _buildBioStat(String label, String value) {
    return Column(
      children: [
        Text(
          value,
          style: GoogleFonts.outfit(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: Colors.white,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          label,
          style: GoogleFonts.poppins(
            fontSize: 12,
            color: Colors.white.withOpacity(0.5),
            fontWeight: FontWeight.w500,
          ),
        ),
      ],
    );
  }

  Widget _buildVerticalDivider() {
    return Container(
      height: 30,
      width: 1,
      color: Colors.white.withOpacity(0.1),
    );
  }

  Widget _buildConditionSection(String condition) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
      decoration: BoxDecoration(
        color: Colors.orangeAccent.withOpacity(0.1),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: Colors.orangeAccent.withOpacity(0.3)),
      ),
      child: Row(
        children: [
          const Icon(Icons.health_and_safety_rounded, color: Colors.orangeAccent, size: 28),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Health Focus',
                  style: GoogleFonts.poppins(
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                    color: Colors.orangeAccent.withOpacity(0.8),
                    letterSpacing: 1.2,
                  ),
                ),
                Text(
                  condition,
                  style: GoogleFonts.outfit(
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                    color: Colors.white.withOpacity(0.9),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildUsageSquare(String label, int current, int total, IconData icon, Color color) {
    final percent = current / total;
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.04),
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: Colors.white.withOpacity(0.05)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(icon, color: color, size: 24),
          ),
          const SizedBox(height: 20),
          Text(
            '$current/$total',
            style: GoogleFonts.outfit(
              fontSize: 22,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
          ),
          Text(
            '$label Tokens',
            style: GoogleFonts.poppins(
              fontSize: 13,
              color: Colors.white.withOpacity(0.5),
            ),
          ),
          const SizedBox(height: 12),
          ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: LinearProgressIndicator(
              value: percent,
              backgroundColor: Colors.white.withOpacity(0.05),
              valueColor: AlwaysStoppedAnimation<Color>(color),
              minHeight: 4,
            ),
          ),
        ],
      ),
    );
  }
}

class _HeaderClipper extends CustomClipper<Path> {
  @override
  Path getClip(Size size) {
    var path = Path();
    path.lineTo(0, size.height - 40);
    path.quadraticBezierTo(size.width / 2, size.height + 10, size.width, size.height - 40);
    path.lineTo(size.width, 0);
    path.close();
    return path;
  }

  @override
  bool shouldReclip(CustomClipper<Path> oldClipper) => false;
}
