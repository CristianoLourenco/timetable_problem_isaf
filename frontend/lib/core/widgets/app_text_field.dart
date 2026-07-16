import 'package:flutter/material.dart';
import 'package:ghorario/core/themes/app_colors.dart';
import 'package:ghorario/core/themes/app_text_styles.dart';

/// A styled text field with a top label and bottom divider.
///
/// Receives all configuration through constructor parameters —
/// no direct Provider access.
class AppTextField extends StatelessWidget {
  const AppTextField({
    super.key,
    this.obscureText = false,
    this.labelText = '',
    this.hintText = '',
    this.controller,
  });

  final bool obscureText;
  final String labelText;
  final String hintText;
  final TextEditingController? controller;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 70,
      child: Column(
        children: <Widget>[
          Align(
            alignment: Alignment.centerLeft,
            child: Text(labelText, style: AppTextStyles.label),
          ),
          Expanded(
            flex: 2,
            child: TextField(
              controller: controller,
              obscureText: obscureText,
              decoration: InputDecoration(
                hintText: hintText,
                border: InputBorder.none,
              ),
            ),
          ),
          const Divider(
            color: AppColors.blackBlue,
            thickness: 1.2,
          ),
        ],
      ),
    );
  }
}
