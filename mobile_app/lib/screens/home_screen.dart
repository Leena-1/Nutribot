import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import 'package:nutribot/screens/scan_screen.dart';
import 'package:nutribot/screens/chat_screen.dart';
import 'package:nutribot/screens/results_screen.dart';
import 'package:nutribot/screens/profile_screen.dart';
import 'package:nutribot/providers/auth_provider.dart';
import 'package:nutribot/providers/usage_provider.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _currentIndex = 0;

  final _screens = [
    const ScanScreen(),
    const ResultsScreen(),
    const ChatScreen(),
    const ProfileScreen(),
  ];

  @override
  void initState() {
    super.initState();
    // Load usage stats when home screen loads
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<UsageProvider>().loadUsage();
    });
  }

  @override
  Widget build(BuildContext context) {
    final usageProvider = context.watch<UsageProvider>();
    
    return Scaffold(
      body: IndexedStack(
        index: _currentIndex,
        children: _screens,
      ),
      bottomNavigationBar: Container(
        decoration: BoxDecoration(
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.1),
              blurRadius: 10,
              offset: const Offset(0, -2),
            ),
          ],
        ),
        child: NavigationBar(
          selectedIndex: _currentIndex,
          onDestinationSelected: (index) => setState(() => _currentIndex = index),
          backgroundColor: Colors.white,
          elevation: 0,
          height: 70,
          labelBehavior: NavigationDestinationLabelBehavior.alwaysShow,
          destinations: [
            NavigationDestination(
              icon: const Icon(Icons.camera_alt_outlined),
              selectedIcon: const Icon(Icons.camera_alt),
              label: 'Scan',
            ),
            NavigationDestination(
              icon: const Icon(Icons.dashboard_outlined),
              selectedIcon: const Icon(Icons.dashboard),
              label: 'Results',
            ),
            NavigationDestination(
              icon: Stack(
                children: [
                  const Icon(Icons.chat_bubble_outline),
                  if (usageProvider.chatRemaining <= 2 && usageProvider.chatRemaining > 0)
                    Positioned(
                      right: 0,
                      top: 0,
                      child: Container(
                        padding: const EdgeInsets.all(2),
                        decoration: const BoxDecoration(
                          color: Colors.orange,
                          shape: BoxShape.circle,
                        ),
                        constraints: const BoxConstraints(
                          minWidth: 12,
                          minHeight: 12,
                        ),
                      ),
                    ),
                ],
              ),
              selectedIcon: const Icon(Icons.chat_bubble),
              label: 'Chat',
            ),
            NavigationDestination(
              icon: const Icon(Icons.person_outline),
              selectedIcon: const Icon(Icons.person),
              label: 'Profile',
            ),
          ],
        ),
      ),
    );
  }
}
