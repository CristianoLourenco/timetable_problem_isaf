import 'package:flutter/material.dart';
import 'package:ghorario/core/themes/app_colors.dart';

/// A container that renders a [LinearGradient] as its background.
///
/// Defaults to the primary brand gradient ([AppColors.primaryGradient]).
class GradientContainer extends StatelessWidget {
  const GradientContainer({
    super.key,
    this.child,
    this.colors = AppColors.primaryGradient,
    this.begin = Alignment.centerLeft,
    this.end = Alignment.centerRight,
  });

  final List<Color> colors;
  final Widget? child;
  final AlignmentGeometry begin;
  final AlignmentGeometry end;

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: begin,
          end: end,
          colors: colors,
        ),
      ),
      child: child,
    );
  }
}
