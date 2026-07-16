import 'package:flutter/foundation.dart';
import 'package:ghorario/features/feature_auth/presentation/provider/auth_provider.dart';
import 'package:ghorario/features/feature_auth/presentation/states/auth_state.dart';

/// Local controller for handling authentication UI interactions.
class AuthController extends ValueNotifier<AuthState> {
  AuthController({
    required AuthProvider provider,
  })  : _provider = provider,
        super(const AuthState());

  final AuthProvider _provider;

  void init() {
    _hydrate();
    _provider.addListener(_onProviderChanged);
  }

  @override
  void dispose() {
    _provider.removeListener(_onProviderChanged);
    super.dispose();
  }

  void _hydrate() {
    value = value.copyWith(
      currentUser: _provider.currentUser,
      isLoading: _provider.isLoading,
      errorMessage: _provider.errorMessage,
    );
  }

  void _onProviderChanged() {
    value = value.copyWith(
      currentUser: _provider.currentUser,
      isLoading: _provider.isLoading,
      errorMessage: _provider.errorMessage,
    );
  }

  Future<bool> login(String email, String password) async {
    return _provider.login(email, password);
  }

  Future<void> logout() async {
    await _provider.logout();
  }

  Future<bool> registoProfessor({
    required String email,
    required String password,
    required String contactoTelefonico,
  }) async {
    return _provider.registoProfessor(
      email: email,
      password: password,
      contactoTelefonico: contactoTelefonico,
    );
  }

  Future<bool> recuperarPassword(String email) async {
    return _provider.recuperarPassword(email);
  }
}
