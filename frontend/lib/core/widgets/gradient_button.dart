import 'package:flutter/material.dart';
import 'package:ghorario/core/widgets/gradient_container.dart';

/// An [ElevatedButton] whose background is a [GradientContainer].
class GradientButton extends StatelessWidget {
  const GradientButton({
    super.key,
    required this.onPressed,
    required this.child,
    this.minHeight = 40,
    this.borderRadius = BorderRadius.zero,
    this.elevation,
  });

  final double minHeight;
  final BorderRadiusGeometry borderRadius;
  final void Function()? onPressed;
  final Widget? child;
  final double? elevation;

  @override
  Widget build(BuildContext context) {
    return ElevatedButton(
      clipBehavior: Clip.antiAlias,
      style: ElevatedButton.styleFrom(
        elevation: elevation,
        padding: const EdgeInsets.all(0),
        shape: RoundedRectangleBorder(borderRadius: borderRadius),
      ),
      onPressed: onPressed,
      child: SizedBox(
        height: minHeight,
        width: double.maxFinite,
        child: GradientContainer(child: child),
      ),
    );
  }
}
