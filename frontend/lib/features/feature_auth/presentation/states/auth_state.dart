import 'package:ghorario/features/feature_auth/domain/entities/user.dart';

const Object _sentinel = Object();

/// State representation for authentication status.
class AuthState {
  const AuthState({
    this.currentUser,
    this.isLoading = false,
    this.errorMessage,
  });

  final User? currentUser;
  final bool isLoading;
  final String? errorMessage;

  AuthState copyWith({
    Object? currentUser = _sentinel,
    bool? isLoading,
    Object? errorMessage = _sentinel,
  }) {
    return AuthState(
      currentUser: currentUser == _sentinel ? this.currentUser : (currentUser as User?),
      isLoading: isLoading ?? this.isLoading,
      errorMessage: errorMessage == _sentinel ? this.errorMessage : (errorMessage as String?),
    );
  }
}
