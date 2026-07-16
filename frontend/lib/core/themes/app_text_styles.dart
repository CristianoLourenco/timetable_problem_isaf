import 'package:flutter/material.dart';
import 'package:ghorario/core/themes/app_colors.dart';

/// Reusable text styles used across the application.
///
/// All styles reference [AppColors] for consistency.
class AppTextStyles {
  AppTextStyles._();

  static const TextStyle heading1 = TextStyle(
    fontSize: 28,
    fontWeight: FontWeight.bold,
    color: AppColors.textPrimary,
  );

  static const TextStyle heading2 = TextStyle(
    fontSize: 22,
    fontWeight: FontWeight.w600,
    color: AppColors.textPrimary,
  );

  static const TextStyle heading3 = TextStyle(
    fontSize: 18,
    fontWeight: FontWeight.w500,
    color: AppColors.textPrimary,
  );

  static const TextStyle body = TextStyle(
    fontSize: 14,
    fontWeight: FontWeight.normal,
    color: AppColors.textPrimary,
  );

  static const TextStyle bodySmall = TextStyle(
    fontSize: 12,
    fontWeight: FontWeight.normal,
    color: AppColors.textSecondary,
  );

  static const TextStyle button = TextStyle(
    fontSize: 14,
    fontWeight: FontWeight.w500,
    color: AppColors.white,
  );

  static const TextStyle menuItem = TextStyle(
    fontWeight: FontWeight.normal,
    color: AppColors.white,
  );

  static const TextStyle menuItemActive = TextStyle(
    fontWeight: FontWeight.w500,
    color: AppColors.white,
  );

  static const TextStyle label = TextStyle(
    fontSize: 14,
    color: AppColors.blackBlue,
    fontWeight: FontWeight.w800,
    fontFamily: 'Lato',
  );
}
