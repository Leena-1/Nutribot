import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import 'package:nutribot/providers/auth_provider.dart';
import 'package:nutribot/providers/usage_provider.dart';
import 'package:nutribot/screens/home_screen.dart';
import 'package:nutribot/utils/app_logger.dart';

class SignupScreen extends StatefulWidget {
  const SignupScreen({super.key});

  @override
  State<SignupScreen> createState() => _SignupScreenState();
}

class _SignupScreenState extends State<SignupScreen> {
  final GlobalKey<FormState> _formKey = GlobalKey<FormState>();
  final TextEditingController _nameController = TextEditingController();
  final TextEditingController _emailController = TextEditingController();
  final TextEditingController _phoneController = TextEditingController();
  final TextEditingController _ageController = TextEditingController();
  final TextEditingController _weightController = TextEditingController(); // 🔥 ADDED
  final TextEditingController _passwordController = TextEditingController();
  final TextEditingController _confirmPasswordController = TextEditingController();

  bool _obscurePassword = true;
  bool _obscureConfirmPassword = true;
  bool _isLoading = false;
  String? _selectedGender;
  bool _hasDisease = false;
  final List<String> _selectedDiseases = [];

  static const List<String> _diseaseTypes = [
    'Kidney Disease',
    'Diabetes Type 2',
    'Celiac Disease',
    'Crohn\'s Disease',
    'Heart Disease',
    'Hypertension',
    'IBS',
  ];

  @override
  void dispose() {
    _nameController.dispose();
    _emailController.dispose();
    _phoneController.dispose();
    _ageController.dispose();
    _weightController.dispose(); // 🔥 ADDED
    _passwordController.dispose();
    _confirmPasswordController.dispose();
    super.dispose();
  }

  Future<void> _handleSignup() async {
    if (!_formKey.currentState!.validate()) return;
    if (_isLoading) return;

    setState(() => _isLoading = true);
    AppLogger.nav('Signup: submit pressed');

    final authProvider = context.read<AuthProvider>();
    final usageProvider = context.read<UsageProvider>();

    String? error;
    try {
      error = await authProvider.signUp(
        name: _nameController.text.trim(),
        email: _emailController.text.trim(),
        password: _passwordController.text,
        displayName: _nameController.text.trim().isEmpty ? null : _nameController.text.trim(),
        phoneNumber: _phoneController.text.trim().isEmpty ? null : _phoneController.text.trim(),
        age: int.tryParse(_ageController.text.trim()) ?? 0,
        weight: double.tryParse(_weightController.text.trim()) ?? 0.0, // 🔥 ADDED
        gender: _selectedGender,
        hasDisease: _hasDisease,
        diseaseType: _hasDisease && _selectedDiseases.isNotEmpty ? _selectedDiseases.join(', ') : null,
      );
    } catch (e, st) {
      AppLogger.error('SignupScreen', e, st);
      error = 'Something went wrong. Please try again.';
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }

    if (!mounted) return;

    if (error != null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(error!),
          backgroundColor: Colors.red,
          behavior: SnackBarBehavior.floating,
        ),
      );
      return;
    }

    // Success: reset usage in background
    usageProvider.resetUsage();

    AppLogger.nav('Signup: navigating to Home (pushAndRemoveUntil)');
    Navigator.pushAndRemoveUntil(
      context,
      MaterialPageRoute<void>(builder: (_) => const HomeScreen()),
      (route) => false,
    );

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('Account created! Welcome.', style: GoogleFonts.poppins()),
        backgroundColor: Colors.green,
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
            child: Form(
              key: _formKey,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Align(
                    alignment: Alignment.topLeft,
                    child: IconButton(
                      icon: const Icon(Icons.arrow_back),
                      onPressed: _isLoading ? null : () => Navigator.maybePop(context),
                    ),
                  ),
                  Text(
                    'Create Account',
                    style: GoogleFonts.poppins(
                      fontSize: 32,
                      fontWeight: FontWeight.bold,
                      color: Colors.grey.shade800,
                    ),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 32),
                  _buildTextField(
                    controller: _nameController,
                    label: 'Full Name *',
                    icon: Icons.person_outlined,
                  ),
                  const SizedBox(height: 16),
                  _buildTextField(
                    controller: _emailController,
                    label: 'Email *',
                    icon: Icons.email_outlined,
                    keyboardType: TextInputType.emailAddress,
                  ),
                  const SizedBox(height: 16),
                  Row(
                    children: [
                      Expanded(
                        child: _buildTextField(
                          controller: _ageController,
                          label: 'Age',
                          icon: Icons.cake_outlined,
                          keyboardType: TextInputType.number,
                        ),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: _buildTextField(
                          controller: _weightController, // 🔥 ADDED
                          label: 'Weight (kg)',
                          icon: Icons.monitor_weight_outlined,
                          keyboardType: TextInputType.number,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  DropdownButtonFormField<String>(
                    value: _selectedGender,
                    decoration: InputDecoration(
                      labelText: 'Gender',
                      prefixIcon: const Icon(Icons.person_outline),
                      border: OutlineInputBorder(borderRadius: BorderRadius.circular(16)),
                      filled: true,
                      fillColor: Colors.white,
                    ),
                    items: ['Male', 'Female', 'Other']
                        .map((g) => DropdownMenuItem(value: g.toLowerCase(), child: Text(g)))
                        .toList(),
                    onChanged: _isLoading ? null : (value) => setState(() => _selectedGender = value),
                  ),
                  const SizedBox(height: 16),
                  Card(
                    elevation: 0,
                    color: Colors.white,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                    child: CheckboxListTile(
                      title: Text('Do you have any medical condition?', style: GoogleFonts.poppins()),
                      value: _hasDisease,
                      onChanged: _isLoading ? null : (v) => setState(() => _hasDisease = v ?? false),
                      controlAffinity: ListTileControlAffinity.leading,
                    ),
                  ),
                  if (_hasDisease) ...[
                    const SizedBox(height: 8),
                    Container(
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(16),
                        border: Border.all(color: Colors.grey.shade300),
                      ),
                      child: Column(
                        children: _diseaseTypes.map((disease) {
                          return CheckboxListTile(
                            title: Text(disease, style: GoogleFonts.poppins()),
                            value: _selectedDiseases.contains(disease),
                            onChanged: _isLoading
                                ? null
                                : (bool? value) {
                                    setState(() {
                                      if (value == true) {
                                        _selectedDiseases.add(disease);
                                      } else {
                                        _selectedDiseases.remove(disease);
                                      }
                                    });
                                  },
                            controlAffinity: ListTileControlAffinity.leading,
                            dense: true,
                          );
                        }).toList(),
                      ),
                    ),
                  ],
                  const SizedBox(height: 16),
                  _buildTextField(
                    controller: _passwordController,
                    label: 'Password *',
                    icon: Icons.lock_outlined,
                    obscureText: _obscurePassword,
                    suffixIcon: IconButton(
                      icon: Icon(
                        _obscurePassword ? Icons.visibility_outlined : Icons.visibility_off_outlined,
                      ),
                      onPressed: () => setState(() => _obscurePassword = !_obscurePassword),
                    ),
                  ),
                  const SizedBox(height: 16),
                  _buildTextField(
                    controller: _confirmPasswordController,
                    label: 'Confirm Password *',
                    icon: Icons.lock_outlined,
                    obscureText: _obscureConfirmPassword,
                    suffixIcon: IconButton(
                      icon: Icon(
                        _obscureConfirmPassword ? Icons.visibility_outlined : Icons.visibility_off_outlined,
                      ),
                      onPressed: () => setState(() => _obscureConfirmPassword = !_obscureConfirmPassword),
                    ),
                  ),
                  const SizedBox(height: 32),
                  ElevatedButton(
                    onPressed: _isLoading ? null : _handleSignup,
                    style: ElevatedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(30)),
                      backgroundColor: Colors.green.shade600,
                    ),
                    child: _isLoading
                        ? const CircularProgressIndicator(color: Colors.white)
                        : Text(
                            'Sign Up',
                            style: GoogleFonts.poppins(color: Colors.white, fontWeight: FontWeight.w600, fontSize: 16),
                          ),
                  ),
                  const SizedBox(height: 24),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text("Already have an account? ", style: GoogleFonts.poppins()),
                      TextButton(
                        onPressed: _isLoading ? null : () => Navigator.maybePop(context),
                        child: Text('Sign In', style: GoogleFonts.poppins(color: Colors.green.shade600, fontWeight: FontWeight.w600)),
                      ),
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

  Widget _buildTextField({
    required TextEditingController controller,
    required String label,
    required IconData icon,
    bool obscureText = false,
    Widget? suffixIcon,
    TextInputType? keyboardType,
  }) {
    return TextFormField(
      controller: controller,
      obscureText: obscureText,
      keyboardType: keyboardType,
      decoration: InputDecoration(
        labelText: label,
        prefixIcon: Icon(icon),
        suffixIcon: suffixIcon,
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(16)),
        filled: true,
        fillColor: Colors.white,
      ),
    );
  }
}
