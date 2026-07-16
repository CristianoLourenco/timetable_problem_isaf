import 'package:flutter/material.dart';

/// Application color palette.
///
/// All colors used across the app are defined here to maintain a single
/// source of truth. Avoid hardcoding Color values elsewhere.
class AppColors {
  AppColors._();

  // Primary blues
  static const Color lightBlue = Color(0xFF05A1FF);
  static const Color darkBlue = Color(0xFF004D7B);
  static const Color blackBlue = Color(0xFF00395E);

  // Neutrals
  static const Color white = Color(0xFFFFFFFF);
  static const Color background = Color(0xFFF5F7FA);
  static const Color surface = Color(0xFFFFFFFF);
  static const Color textPrimary = Color(0xFF1A1A2E);
  static const Color textSecondary = Color(0xFF6B7280);

  // Feedback
  static const Color success = Color(0xFF10B981);
  static const Color error = Color(0xFFEF4444);
  static const Color warning = Color(0xFFF59E0B);

  /// Standard gradient used in sidebar and buttons.
  static const List<Color> primaryGradient = [lightBlue, darkBlue];
}
