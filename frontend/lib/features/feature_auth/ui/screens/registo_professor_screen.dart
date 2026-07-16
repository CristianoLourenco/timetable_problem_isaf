import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

import 'package:ghorario/core/constants/app_assets.dart';
import 'package:ghorario/core/themes/app_colors.dart';
import 'package:ghorario/core/widgets/app_text_field.dart';
import 'package:ghorario/core/widgets/gradient_button.dart';
import 'package:ghorario/core/widgets/gradient_container.dart';
import 'package:ghorario/features/feature_auth/presentation/controller/auth_controller.dart';
import 'package:ghorario/features/feature_auth/presentation/provider/auth_provider.dart';
import 'package:ghorario/features/feature_auth/presentation/states/auth_state.dart';

/// Self-registration screen for a Professor (RF15/UC13) — the Gestor must
/// have already created the Professor record; 403 otherwise (RN10).
class RegistoProfessorScreen extends StatefulWidget {
  const RegistoProfessorScreen({super.key});

  @override
  State<RegistoProfessorScreen> createState() => _RegistoProfessorScreenState();
}

class _RegistoProfessorScreenState extends State<RegistoProfessorScreen> {
  late final AuthController _controller;
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _contactoController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _controller = AuthController(provider: context.read<AuthProvider>());
    _controller.init();
  }

  @override
  void dispose() {
    _controller.dispose();
    _emailController.dispose();
    _passwordController.dispose();
    _contactoController.dispose();
    super.dispose();
  }

  Future<void> _handleRegisto() async {
    if (_emailController.text.isEmpty || _passwordController.text.isEmpty || _contactoController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Por favor, preencha todos os campos.')),
      );
      return;
    }

    final success = await _controller.registoProfessor(
      email: _emailController.text.trim(),
      password: _passwordController.text.trim(),
      contactoTelefonico: _contactoController.text.trim(),
    );

    if (!mounted) return;
    if (success) {
      context.go('/dashboard');
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(_controller.value.errorMessage ?? 'Erro ao registar.'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final size = MediaQuery.of(context).size;

    return Scaffold(
      body: Stack(
        children: [
          Image.asset(AppAssets.backgroundLogin, fit: BoxFit.cover, width: size.width, height: size.height),
          GradientContainer(
            colors: [AppColors.lightBlue.withValues(alpha: 0.3), AppColors.darkBlue.withValues(alpha: 0.8)],
          ),
          Center(
            child: ValueListenableBuilder<AuthState>(
              valueListenable: _controller,
              builder: (context, state, child) {
                return SizedBox(
                  width: 420,
                  child: Card(
                    elevation: 10,
                    child: Padding(
                      padding: const EdgeInsets.all(32),
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          const Text(
                            'Registo de Professor',
                            style: TextStyle(fontWeight: FontWeight.bold, fontSize: 20, color: AppColors.darkBlue),
                          ),
                          const SizedBox(height: 8),
                          const Text(
                            'O Gestor tem de já ter criado o seu registo de Professor.',
                            textAlign: TextAlign.center,
                            style: TextStyle(fontSize: 12, color: Colors.grey),
                          ),
                          const SizedBox(height: 24),
                          AppTextField(hintText: 'Email', labelText: 'Email', controller: _emailController),
                          const SizedBox(height: 12),
                          AppTextField(
                            hintText: 'Palavra-passe',
                            labelText: 'Palavra-passe',
                            obscureText: true,
                            controller: _passwordController,
                          ),
                          const SizedBox(height: 12),
                          AppTextField(
                            hintText: 'Contacto Telefónico',
                            labelText: 'Contacto Telefónico',
                            controller: _contactoController,
                          ),
                          const SizedBox(height: 24),
                          SizedBox(
                            width: double.infinity,
                            child: GradientButton(
                              minHeight: 50,
                              borderRadius: BorderRadius.circular(8),
                              onPressed: state.isLoading ? () {} : _handleRegisto,
                              child: state.isLoading
                                  ? const Center(
                                      child: SizedBox(
                                        width: 20,
                                        height: 20,
                                        child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                                      ),
                                    )
                                  : const Center(
                                      child: Text('Registar', style: TextStyle(color: Colors.white)),
                                    ),
                            ),
                          ),
                          const SizedBox(height: 12),
                          TextButton(
                            onPressed: () => context.go('/login'),
                            child: const Text('Já tem conta? Iniciar sessão'),
                          ),
                        ],
                      ),
                    ),
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}
