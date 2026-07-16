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

/// Password recovery screen (RF16/UC14) — always shows the same success
/// message, even for an email that doesn't exist (the backend never reveals
/// registered accounts).
class RecuperarPasswordScreen extends StatefulWidget {
  const RecuperarPasswordScreen({super.key});

  @override
  State<RecuperarPasswordScreen> createState() => _RecuperarPasswordScreenState();
}

class _RecuperarPasswordScreenState extends State<RecuperarPasswordScreen> {
  late final AuthController _controller;
  final _emailController = TextEditingController();
  bool _emailSent = false;

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
    super.dispose();
  }

  Future<void> _handleRecuperar() async {
    if (_emailController.text.isEmpty) return;
    await _controller.recuperarPassword(_emailController.text.trim());
    if (!mounted) return;
    // Sempre mostra sucesso — o backend nunca revela se o email existe.
    setState(() => _emailSent = true);
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
                            'Recuperar Palavra-passe',
                            style: TextStyle(fontWeight: FontWeight.bold, fontSize: 20, color: AppColors.darkBlue),
                          ),
                          const SizedBox(height: 24),
                          if (_emailSent) ...[
                            const Text(
                              'Se o email existir, receberá instruções para redefinir a palavra-passe.',
                              textAlign: TextAlign.center,
                            ),
                            const SizedBox(height: 24),
                            TextButton(
                              onPressed: () => context.go('/login'),
                              child: const Text('Voltar ao início de sessão'),
                            ),
                          ] else ...[
                            AppTextField(hintText: 'Email', labelText: 'Email', controller: _emailController),
                            const SizedBox(height: 24),
                            SizedBox(
                              width: double.infinity,
                              child: GradientButton(
                                minHeight: 50,
                                borderRadius: BorderRadius.circular(8),
                                onPressed: state.isLoading ? () {} : _handleRecuperar,
                                child: state.isLoading
                                    ? const Center(
                                        child: SizedBox(
                                          width: 20,
                                          height: 20,
                                          child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                                        ),
                                      )
                                    : const Center(
                                        child: Text('Enviar', style: TextStyle(color: Colors.white)),
                                      ),
                              ),
                            ),
                            const SizedBox(height: 12),
                            TextButton(
                              onPressed: () => context.go('/login'),
                              child: const Text('Cancelar'),
                            ),
                          ],
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
