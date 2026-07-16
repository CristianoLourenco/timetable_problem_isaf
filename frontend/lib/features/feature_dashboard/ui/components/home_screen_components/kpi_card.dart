import 'package:flutter/material.dart';
import 'package:ghorario/core/themes/app_colors.dart';

class KpiCard extends StatelessWidget {
  const KpiCard({
    super.key,
    required this.icon,
    required this.value,
    required this.title,
    required this.subtitle,
    required this.iconColor,
    this.onTapLink,
  });

  final IconData icon;
  final String value;
  final String title;
  final String subtitle;
  final Color iconColor;
  final VoidCallback? onTapLink;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 210,
      height: 150,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFFE8EEF5), width: 1.2),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.015),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Stack(
        children: [
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              // Circular/Rounded Icon container
              Container(
                width: 38,
                height: 38,
                decoration: BoxDecoration(
                  color: iconColor.withOpacity(0.08),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(icon, color: iconColor, size: 20),
              ),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    value,
                    style: const TextStyle(
                      fontSize: 28,
                      fontWeight: FontWeight.bold,
                      color: AppColors.blackBlue,
                      fontFamily: 'Poppins',
                      height: 1.1,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    title,
                    style: const TextStyle(
                      fontSize: 13,
                      fontWeight: FontWeight.w500,
                      color: Color(0xFF64748B),
                      fontFamily: 'Poppins',
                    ),
                  ),
                  Text(
                    subtitle,
                    style: const TextStyle(
                      fontSize: 11,
                      color: Color(0xFF94A3B8),
                      fontFamily: 'Poppins',
                    ),
                  ),
                ],
              ),
            ],
          ),
          if (onTapLink != null)
            Positioned(
              top: 0,
              right: 0,
              child: InkWell(
                onTap: onTapLink,
                borderRadius: BorderRadius.circular(4),
                child: const Padding(
                  padding: EdgeInsets.all(4.0),
                  child: Icon(
                    Icons.arrow_outward_rounded,
                    color: Color(0xFF94A3B8),
                    size: 18,
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }
}
