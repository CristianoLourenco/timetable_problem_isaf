import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_auth/domain/entities/user.dart';
import 'package:ghorario/features/feature_auth/domain/repository/i_auth_repository.dart';

/// Use case to fetch the currently authenticated user, if any.
class GetCurrentUserUseCase implements IUseCase<User?, void> {
  GetCurrentUserUseCase(this._repository);

  final IAuthRepository _repository;

  @override
  Future<DataState<User?>> call(void params) {
    return _repository.getCurrentUser();
  }
}
