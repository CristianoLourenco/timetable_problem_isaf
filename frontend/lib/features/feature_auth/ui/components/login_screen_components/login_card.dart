import 'package:flutter/material.dart';

import 'package:ghorario/core/constants/app_strings.dart';
import 'package:ghorario/core/themes/app_colors.dart';
import 'package:ghorario/core/widgets/gradient_button.dart';
import 'package:ghorario/core/widgets/app_text_field.dart';

/// The login card displayed on the [LoginScreen].
///
/// Receives [size] and [onPressed] as parameters —
/// no direct Provider access.
class LoginCard extends StatelessWidget {
  const LoginCard({
    super.key,
    required this.size,
    required this.onPressed,
    required this.usernameController,
    required this.passwordController,
    required this.onRegistoProfessorPressed,
    required this.onRecuperarPasswordPressed,
  });

  final Size size;
  final void Function() onPressed;
  final TextEditingController usernameController;
  final TextEditingController passwordController;
  final void Function() onRegistoProfessorPressed;
  final void Function() onRecuperarPasswordPressed;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: SizedBox(
        height: size.height * .5,
        width: size.width * .22,
        child: Card(
          elevation: 10,
          child: Padding(
            padding: const EdgeInsets.symmetric(
              vertical: 18,
              horizontal: 38,
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              mainAxisAlignment: MainAxisAlignment.center,
              children: <Widget>[
                const Spacer(),
                const Text(
                  AppStrings.login,
                  textScaler: TextScaler.linear(1.3),
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    color: AppColors.darkBlue,
                  ),
                ),
                const Spacer(),
                AppTextField(
                  hintText: AppStrings.username,
                  labelText: AppStrings.username,
                  controller: usernameController,
                ),
                const Divider(),
                AppTextField(
                  hintText: AppStrings.password,
                  labelText: AppStrings.password,
                  obscureText: true,
                  controller: passwordController,
                ),
                const Spacer(),
                Row(
                  children: <Widget>[
                    Expanded(
                      child: GradientButton(
                        elevation: 10,
                        minHeight: 50,
                        borderRadius: BorderRadius.circular(8),
                        onPressed: onPressed,
                        child: const Center(
                          child: Text(
                            AppStrings.login,
                            textAlign: TextAlign.center,
                            style: TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.normal,
                            ),
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                TextButton(
                  onPressed: onRecuperarPasswordPressed,
                  child: const Text('Esqueceu a palavra-passe?'),
                ),
                TextButton(
                  onPressed: onRegistoProfessorPressed,
                  child: const Text('Sou Professor e ainda não tenho conta'),
                ),
                const Spacer(),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

