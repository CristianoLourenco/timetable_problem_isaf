import 'package:flutter/material.dart';
import 'package:ghorario/core/themes/app_colors.dart';

class TabPill extends StatelessWidget {
  const TabPill({
    super.key,
    required this.label,
    required this.isActive,
    required this.onTap,
  });

  final String label;
  final bool isActive;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        decoration: BoxDecoration(
          color: isActive ? Colors.white : Colors.transparent,
          borderRadius: BorderRadius.circular(6),
          boxShadow: isActive
              ? [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.04),
                    blurRadius: 4,
                    offset: const Offset(0, 1),
                  ),
                ]
              : null,
        ),
        child: Text(
          label,
          style: TextStyle(
            color: isActive ? AppColors.blackBlue : const Color(0xFF64748B),
            fontWeight: isActive ? FontWeight.w600 : FontWeight.w500,
            fontSize: 13,
            fontFamily: 'Poppins',
          ),
        ),
      ),
    );
  }
}
