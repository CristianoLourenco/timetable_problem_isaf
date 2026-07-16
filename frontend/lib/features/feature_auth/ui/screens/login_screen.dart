import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

import 'package:ghorario/core/constants/app_assets.dart';
import 'package:ghorario/core/constants/app_strings.dart';
import 'package:ghorario/core/themes/app_colors.dart';
import 'package:ghorario/core/widgets/gradient_container.dart';
import 'package:ghorario/features/feature_auth/presentation/controller/auth_controller.dart';
import 'package:ghorario/features/feature_auth/presentation/provider/auth_provider.dart';
import 'package:ghorario/features/feature_auth/presentation/states/auth_state.dart';
import 'package:ghorario/features/feature_auth/ui/components/login_screen_components/login_card.dart';

/// Login screen — Scaffold only, visual logic lives in [LoginCard].
class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  late final AuthController _controller;
  late final TextEditingController _usernameController;
  late final TextEditingController _passwordController;

  @override
  void initState() {
    super.initState();
    _controller = AuthController(provider: context.read<AuthProvider>());
    _controller.init();
    _usernameController = TextEditingController();
    _passwordController = TextEditingController();
  }

  @override
  void dispose() {
    _controller.dispose();
    _usernameController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  void _handleLogin() async {
    final username = _usernameController.text.trim();
    final password = _passwordController.text.trim();

    if (username.isEmpty || password.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Por favor, preencha todos os campos.'),
        ),
      );
      return;
    }

    showDialog<void>(
      context: context,
      barrierDismissible: false,
      builder: (BuildContext context) => const Center(child: CircularProgressIndicator()),
    );

    final success = await _controller.login(username, password);

    if (mounted) {
      Navigator.pop(context); // Dismiss loading dialog
    }

    if (success) {
      if (mounted) {
        context.go('/dashboard');
      }
    } else {
      if (mounted) {
        final errorMsg = _controller.value.errorMessage ?? 'Erro de autenticação.';
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(errorMsg),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final size = MediaQuery.of(context).size;

    return Scaffold(
      body: Stack(
        children: <Widget>[
          Image.asset(
            AppAssets.backgroundLogin,
            fit: BoxFit.cover,
            width: size.width,
            height: size.height,
          ),
          GradientContainer(
            colors: <Color>[
              AppColors.lightBlue.withValues(alpha: 0.3),
              AppColors.darkBlue.withValues(alpha: 0.8),
            ],
          ),
          Row(
            children: <Widget>[
              const Expanded(
                child: Center(
                  child: Text(
                    AppStrings.appBrand,
                    textAlign: TextAlign.center,
                    textScaler: TextScaler.linear(5),
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      color: AppColors.white,
                    ),
                  ),
                ),
              ),
              Expanded(
                child: ValueListenableBuilder<AuthState>(
                  valueListenable: _controller,
                  builder: (BuildContext context, AuthState state, Widget? child) {
                    return LoginCard(
                      size: size,
                      usernameController: _usernameController,
                      passwordController: _passwordController,
                      onPressed: state.isLoading ? () {} : _handleLogin,
                      onRegistoProfessorPressed: () => context.go('/registo-professor'),
                      onRecuperarPasswordPressed: () => context.go('/recuperar-password'),
                    );
                  },
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

