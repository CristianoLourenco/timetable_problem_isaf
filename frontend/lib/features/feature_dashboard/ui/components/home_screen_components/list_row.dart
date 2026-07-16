import 'package:flutter/material.dart';
import 'package:ghorario/core/themes/app_colors.dart';

class HomeListRow extends StatelessWidget {
  const HomeListRow({
    super.key,
    required this.title,
    required this.subtitle,
    required this.onViewPressed,
    this.onDownloadPressed,
  });

  final String title;
  final String subtitle;
  final VoidCallback onViewPressed;
  final VoidCallback? onDownloadPressed;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                title,
                style: const TextStyle(
                  fontSize: 15,
                  fontWeight: FontWeight.bold,
                  color: AppColors.blackBlue,
                  fontFamily: 'Poppins',
                ),
              ),
              const SizedBox(height: 2),
              Text(
                subtitle,
                style: const TextStyle(
                  fontSize: 13,
                  color: Color(0xFF64748B),
                  fontFamily: 'Poppins',
                ),
              ),
            ],
          ),
          Row(
            children: [
              const Text(
                '0 aulas',
                style: TextStyle(
                  fontSize: 13,
                  color: Color(0xFF94A3B8),
                  fontFamily: 'Poppins',
                ),
              ),
              const SizedBox(width: 24),
              OutlinedButton.icon(
                onPressed: onViewPressed,
                icon: const Icon(Icons.visibility_outlined, size: 14, color: AppColors.blackBlue),
                label: const Text(
                  'Ver',
                  style: TextStyle(
                    fontSize: 12,
                    color: AppColors.blackBlue,
                    fontWeight: FontWeight.bold,
                    fontFamily: 'Poppins',
                  ),
                ),
                style: OutlinedButton.styleFrom(
                  side: const BorderSide(color: Color(0xFFE2E8F0)),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(6),
                  ),
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                ),
              ),
              const SizedBox(width: 8),
              IconButton(
                icon: const Icon(Icons.download_rounded, size: 18, color: Color(0xFF94A3B8)),
                onPressed: onDownloadPressed ?? () {},
              ),
            ],
          ),
        ],
      ),
    );
  }
}
