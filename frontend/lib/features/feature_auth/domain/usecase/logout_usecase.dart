import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_auth/domain/repository/i_auth_repository.dart';

/// Use case to log out the current user.
class LogoutUseCase implements IUseCase<void, void> {
  LogoutUseCase(this._repository);

  final IAuthRepository _repository;

  @override
  Future<DataState<void>> call(void params) {
    return _repository.logout();
  }
}
