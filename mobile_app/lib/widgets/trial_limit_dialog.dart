import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

/// Dialog shown when free trial limit is reached
class TrialLimitDialog extends StatelessWidget {
  const TrialLimitDialog({super.key});

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(20),
      ),
      title: Row(
        children: [
          Icon(Icons.star_outline, color: Colors.amber.shade600),
          const SizedBox(width: 12),
          Text(
            'Free Trial Completed',
            style: GoogleFonts.poppins(
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'You\'ve used all your free prompts!',
            style: GoogleFonts.poppins(),
          ),
          const SizedBox(height: 12),
          Text(
            'Sign up to continue with unlimited access.',
            style: GoogleFonts.poppins(
              color: Colors.grey.shade600,
            ),
          ),
        ],
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: Text(
            'Maybe Later',
            style: GoogleFonts.poppins(
              color: Colors.grey.shade600,
            ),
          ),
        ),
        ElevatedButton(
          onPressed: () {
            Navigator.pop(context);
            Navigator.pushNamed(context, '/signup');
          },
          style: ElevatedButton.styleFrom(
            backgroundColor: Colors.green.shade600,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
          ),
          child: Text(
            'Sign Up',
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
