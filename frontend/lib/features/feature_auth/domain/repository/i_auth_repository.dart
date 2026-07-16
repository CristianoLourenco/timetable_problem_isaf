import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_auth/domain/entities/user.dart';

/// Abstract repository interface for authentication.
abstract class IAuthRepository {
  Future<DataState<User>> login(String email, String password);
  Future<DataState<void>> logout();

  /// Reads the locally persisted session (if any) and confirms it against
  /// `GET /auth/me`. Returns `data: null` (still `success: true`) when there
  /// is no valid session — that is not an error, just "logged out".
  Future<DataState<User?>> getCurrentUser();

  /// `POST /auth/registo-professor` — self-registration; 403 if the email
  /// doesn't match a Professor already created by the Gestor (RN10). Logs
  /// the new session in on success, same as [login].
  Future<DataState<User>> registoProfessor({
    required String email,
    required String password,
    required String contactoTelefonico,
  });

  /// `POST /auth/recuperar-password` — always succeeds from the caller's
  /// point of view (backend never reveals whether the email exists).
  Future<DataState<void>> recuperarPassword(String email);
}
