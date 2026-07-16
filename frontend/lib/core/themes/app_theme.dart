import 'package:flutter/material.dart';
import 'package:ghorario/core/themes/app_colors.dart';

/// Builds the application [ThemeData].
///
/// Uses Material 3 with the Poppins font family as defined in
/// the project's asset bundle.
ThemeData appTheme() {
  return ThemeData(
    fontFamily: 'Poppins',
    colorScheme: ColorScheme.fromSeed(
      seedColor: AppColors.lightBlue,
      primary: AppColors.lightBlue,
      secondary: AppColors.darkBlue,
      surface: AppColors.surface,
    ),
    scaffoldBackgroundColor: AppColors.background,
    useMaterial3: true,
    dividerTheme: const DividerThemeData(color: Colors.transparent),
  );
}
