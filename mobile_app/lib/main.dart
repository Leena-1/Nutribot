import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import 'package:firebase_core/firebase_core.dart';

import 'package:nutribot/providers/auth_provider.dart';
import 'package:nutribot/providers/usage_provider.dart';
import 'package:nutribot/screens/splash_screen.dart';
import 'package:nutribot/screens/welcome_screen.dart';
import 'package:nutribot/screens/login_screen.dart';
import 'package:nutribot/screens/signup_screen.dart';
import 'package:nutribot/screens/home_screen.dart';
import 'package:nutribot/screens/subscription_screen.dart';
import 'package:nutribot/screens/result_detail_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // 🔥 Firebase init (CRITICAL)
  await Firebase.initializeApp();

  runApp(const NutribotApp());
}

class NutribotApp extends StatelessWidget {
  const NutribotApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) {
          final auth = AuthProvider();
          WidgetsBinding.instance.addPostFrameCallback((_) => auth.initialize());
          return auth;
        }),
        ChangeNotifierProvider(create: (_) {
          final usage = UsageProvider();
          WidgetsBinding.instance.addPostFrameCallback((_) => usage.loadUsage());
          return usage;
        }),
      ],
      child: MaterialApp(
        title: 'Nutribot',
        debugShowCheckedModeBanner: false,
        theme: ThemeData(
          useMaterial3: true,
          colorScheme: ColorScheme.fromSeed(
            seedColor: Colors.green,
            brightness: Brightness.light,
          ),
          textTheme: GoogleFonts.poppinsTextTheme(),
        ),
        darkTheme: ThemeData(
          useMaterial3: true,
          colorScheme: ColorScheme.fromSeed(
            seedColor: Colors.green,
            brightness: Brightness.dark,
          ),
          textTheme: GoogleFonts.poppinsTextTheme(
            ThemeData.dark().textTheme,
          ),
        ),
        themeMode: ThemeMode.system,
        initialRoute: '/',
        routes: {
          '/': (context) => const SplashScreen(),
          '/welcome': (context) => const WelcomeScreen(),
          '/login': (context) => const LoginScreen(),
          '/signup': (context) => const SignupScreen(),
          '/home': (context) => const HomeScreen(),
          '/subscription': (context) => const SubscriptionScreen(),
        },
        onGenerateRoute: (settings) {
          if (settings.name == '/result') {
            final args = settings.arguments as Map<String, dynamic>;
            return MaterialPageRoute(
              builder: (context) => ResultDetailScreen(data: args),
            );
          }
          return null;
        },
      ),
    );
  }
}
