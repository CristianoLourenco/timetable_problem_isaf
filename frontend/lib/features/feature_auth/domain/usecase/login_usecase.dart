import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_auth/domain/entities/user.dart';
import 'package:ghorario/features/feature_auth/domain/repository/i_auth_repository.dart';

/// Parameters required to login.
class LoginParams {
  const LoginParams({required this.email, required this.password});
  final String email;
  final String password;
}

/// Use case to log in a user.
class LoginUseCase implements IUseCase<User, LoginParams> {
  LoginUseCase(this._repository);

  final IAuthRepository _repository;

  @override
  Future<DataState<User>> call(LoginParams params) {
    return _repository.login(params.email, params.password);
  }
}
