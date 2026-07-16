import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_auth/domain/entities/user.dart';
import 'package:ghorario/features/feature_auth/domain/repository/i_auth_repository.dart';

class RegistoProfessorParams {
  const RegistoProfessorParams({
    required this.email,
    required this.password,
    required this.contactoTelefonico,
  });

  final String email;
  final String password;
  final String contactoTelefonico;
}

/// Use case for a Professor's self-registration (RF15/UC13) — 403 means the
/// Gestor hasn't created that Professor yet (RN10).
class RegistoProfessorUseCase implements IUseCase<User, RegistoProfessorParams> {
  RegistoProfessorUseCase(this._repository);

  final IAuthRepository _repository;

  @override
  Future<DataState<User>> call(RegistoProfessorParams params) {
    return _repository.registoProfessor(
      email: params.email,
      password: params.password,
      contactoTelefonico: params.contactoTelefonico,
    );
  }
}
