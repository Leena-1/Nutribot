import 'dart:async';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import 'package:nutribot/providers/auth_provider.dart';
import 'package:nutribot/providers/usage_provider.dart';
import 'package:nutribot/screens/home_screen.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();

  bool _obscurePassword = true;
  bool _isLoading = false;

  final RegExp emailRegex = RegExp(r'^[^@]+@[^@]+\.[^@]+');

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _handleLogin() async {
    if (!_formKey.currentState!.validate() || _isLoading) return;

    setState(() => _isLoading = true);

    final authProvider = context.read<AuthProvider>();
    final usageProvider = context.read<UsageProvider>();

    String? error;

    try {
      error = await authProvider.signIn(
        email: _emailController.text.trim(),
        password: _passwordController.text.trim(),
      );
    } on TimeoutException {
      error = "Server is taking too long. Try again.";
    } on SocketException {
      error = "No internet connection.";
    } catch (e) {
      error = "Unexpected error occurred.";
    }

    if (!mounted) return;
    setState(() => _isLoading = false);

    if (error != null) {
      _showSnack(error, Colors.red);
      return;
    }

    // Reset usage after successful login
    usageProvider.resetUsage();

    _showSnack("Welcome back!", Colors.green);

    // Navigate AFTER snackbar trigger
    Future.delayed(const Duration(milliseconds: 300), () {
      if (!mounted) return;

      Navigator.pushAndRemoveUntil(
        context,
        MaterialPageRoute(builder: (_) => const HomeScreen()),
        (route) => false,
      );
    });
  }

  void _showSnack(String message, Color color) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message, style: GoogleFonts.poppins()),
        backgroundColor: color,
        behavior: SnackBarBehavior.floating,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            colors: [
              Colors.green.shade50,
              Colors.teal.shade50,
              Colors.blue.shade50,
            ],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
        ),
        child: SafeArea(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: Form(
              key: _formKey,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  const SizedBox(height: 40),

                  Icon(Icons.restaurant_menu,
                      size: 80, color: Colors.green.shade600),

                  const SizedBox(height: 24),

                  Text(
                    'Welcome Back',
                    textAlign: TextAlign.center,
                    style: GoogleFonts.poppins(
                      fontSize: 30,
                      fontWeight: FontWeight.bold,
                    ),
                  ),

                  const SizedBox(height: 8),

                  Text(
                    'Sign in to continue',
                    textAlign: TextAlign.center,
                    style: GoogleFonts.poppins(color: Colors.grey),
                  ),

                  const SizedBox(height: 40),

                  _buildField(
                    controller: _emailController,
                    label: "Email",
                    icon: Icons.email,
                    keyboardType: TextInputType.emailAddress,
                    validator: (v) {
                      if (v == null || v.isEmpty) {
                        return "Enter email";
                      }
                      if (!emailRegex.hasMatch(v)) {
                        return "Invalid email";
                      }
                      return null;
                    },
                  ),

                  const SizedBox(height: 20),

                  _buildField(
                    controller: _passwordController,
                    label: "Password",
                    icon: Icons.lock,
                    obscureText: _obscurePassword,
                    suffixIcon: IconButton(
                      icon: Icon(_obscurePassword
                          ? Icons.visibility
                          : Icons.visibility_off),
                      onPressed: () =>
                          setState(() => _obscurePassword = !_obscurePassword),
                    ),
                    validator: (v) {
                      if (v == null || v.isEmpty) {
                        return "Enter password";
                      }
                      if (v.length < 6) {
                        return "Minimum 6 characters";
                      }
                      return null;
                    },
                  ),

                  const SizedBox(height: 30),

                  ElevatedButton(
                    onPressed: _isLoading ? null : _handleLogin,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.green,
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(30),
                      ),
                    ),
                    child: _isLoading
                        ? const CircularProgressIndicator(color: Colors.white)
                        : Text(
                            "Sign In",
                            style: GoogleFonts.poppins(
                                color: Colors.white,
                                fontWeight: FontWeight.w600),
                          ),
                  ),

                  const SizedBox(height: 20),

                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text("Don't have an account? ",
                          style: GoogleFonts.poppins()),
                      TextButton(
                        onPressed: () =>
                            Navigator.pushNamed(context, '/signup'),
                        child: const Text("Sign Up"),
                      )
                    ],
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildField({
    required TextEditingController controller,
    required String label,
    required IconData icon,
    bool obscureText = false,
    Widget? suffixIcon,
    TextInputType? keyboardType,
    String? Function(String?)? validator,
  }) {
    return TextFormField(
      controller: controller,
      obscureText: obscureText,
      keyboardType: keyboardType,
      validator: validator,
      decoration: InputDecoration(
        labelText: label,
        prefixIcon: Icon(icon),
        suffixIcon: suffixIcon,
        filled: true,
        fillColor: Colors.white,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
        ),
      ),
    );
  }
}
