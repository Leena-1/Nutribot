import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

/// Dialog shown when user tries to access features without login
class AuthRequiredDialog extends StatelessWidget {
  const AuthRequiredDialog({super.key});

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(20),
      ),
      title: Row(
        children: [
          Icon(Icons.lock_outlined, color: Colors.green.shade600),
          const SizedBox(width: 12),
          Text(
            'Login Required',
            style: GoogleFonts.poppins(
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
      content: Text(
        'Please sign in to continue using this feature.',
        style: GoogleFonts.poppins(),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: Text(
            'Cancel',
            style: GoogleFonts.poppins(
              color: Colors.grey.shade600,
            ),
          ),
        ),
        ElevatedButton(
          onPressed: () {
            Navigator.pop(context);
            Navigator.pushNamed(context, '/login');
          },
          style: ElevatedButton.styleFrom(
            backgroundColor: Colors.green.shade600,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
          ),
          child: Text(
            'Sign In',
            style: GoogleFonts.poppins(
              color: Colors.white,
              fontWeight: FontWeight.w600,
            ),
          ),
        ),
      ],
    );
  }
}
