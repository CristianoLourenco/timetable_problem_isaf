import 'package:flutter/foundation.dart';
import 'package:ghorario/features/feature_auth/domain/entities/user.dart';
import 'package:ghorario/features/feature_auth/domain/usecase/login_usecase.dart';
import 'package:ghorario/features/feature_auth/domain/usecase/logout_usecase.dart';
import 'package:ghorario/features/feature_auth/domain/usecase/get_current_user_usecase.dart';
import 'package:ghorario/features/feature_auth/domain/usecase/recuperar_password_usecase.dart';
import 'package:ghorario/features/feature_auth/domain/usecase/registo_professor_usecase.dart';

/// Provider that maintains global authentication state.
class AuthProvider extends ChangeNotifier {
  AuthProvider({
    required LoginUseCase loginUseCase,
    required LogoutUseCase logoutUseCase,
    required GetCurrentUserUseCase getCurrentUserUseCase,
    required RegistoProfessorUseCase registoProfessorUseCase,
    required RecuperarPasswordUseCase recuperarPasswordUseCase,
  })  : _loginUseCase = loginUseCase,
        _logoutUseCase = logoutUseCase,
        _getCurrentUserUseCase = getCurrentUserUseCase,
        _registoProfessorUseCase = registoProfessorUseCase,
        _recuperarPasswordUseCase = recuperarPasswordUseCase;

  final LoginUseCase _loginUseCase;
  final LogoutUseCase _logoutUseCase;
  final GetCurrentUserUseCase _getCurrentUserUseCase;
  final RegistoProfessorUseCase _registoProfessorUseCase;
  final RecuperarPasswordUseCase _recuperarPasswordUseCase;

  User? _currentUser;
  User? get currentUser => _currentUser;

  bool _isLoading = false;
  bool get isLoading => _isLoading;

  String? _errorMessage;
  String? get errorMessage => _errorMessage;

  Future<bool> login(String email, String password) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    final result = await _loginUseCase(LoginParams(email: email, password: password));
    bool success = false;
    if (result.success && result.data != null) {
      _currentUser = result.data;
      success = true;
    } else {
      _errorMessage = result.message;
    }

    _isLoading = false;
    notifyListeners();
    return success;
  }

  Future<void> logout() async {
    _isLoading = true;
    notifyListeners();

    await _logoutUseCase(null);
    _currentUser = null;

    _isLoading = false;
    notifyListeners();
  }

  Future<void> checkCurrentUser() async {
    final result = await _getCurrentUserUseCase(null);
    if (result.success) {
      _currentUser = result.data;
      notifyListeners();
    }
  }

  Future<bool> registoProfessor({
    required String email,
    required String password,
    required String contactoTelefonico,
  }) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    final result = await _registoProfessorUseCase(
      RegistoProfessorParams(email: email, password: password, contactoTelefonico: contactoTelefonico),
    );
    bool success = false;
    if (result.success && result.data != null) {
      _currentUser = result.data;
      success = true;
    } else {
      _errorMessage = result.message;
    }

    _isLoading = false;
    notifyListeners();
    return success;
  }

  Future<bool> recuperarPassword(String email) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    final result = await _recuperarPasswordUseCase(email);

    _isLoading = false;
    if (!result.success) _errorMessage = result.message;
    notifyListeners();
    return result.success;
  }
}
