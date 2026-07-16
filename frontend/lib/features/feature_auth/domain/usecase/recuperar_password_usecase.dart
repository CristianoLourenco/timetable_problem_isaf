import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_auth/domain/repository/i_auth_repository.dart';

/// Use case to request a password reset email (RF16/UC14).
class RecuperarPasswordUseCase implements IUseCase<void, String> {
  RecuperarPasswordUseCase(this._repository);

  final IAuthRepository _repository;

  @override
  Future<DataState<void>> call(String email) {
    return _repository.recuperarPassword(email);
  }
}
