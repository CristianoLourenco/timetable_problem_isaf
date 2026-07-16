import 'package:ghorario/core/constants/storage_keys.dart';
import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_auth/data/datasource/remote/i_auth_remote.dart';
import 'package:ghorario/features/feature_auth/data/models/token_dto.dart';
import 'package:ghorario/features/feature_auth/domain/entities/user.dart';
import 'package:ghorario/features/feature_auth/domain/repository/i_auth_repository.dart';

/// Concrete implementation of [IAuthRepository].
class AuthRepositoryImpl implements IAuthRepository {
  AuthRepositoryImpl({
    required this.remoteDatasource,
    required this.storage,
  });

  final IAuthRemote remoteDatasource;
  final IStorageMethods storage;

  Future<DataState<User>> _persistSessionAndFetchUser(TokenDto token) async {
    await storage.save(StorageKeys.idToken, token.idToken);
    await storage.save(StorageKeys.refreshToken, token.refreshToken);

    final meResponse = await remoteDatasource.getMe();
    if (!meResponse.success || meResponse.data == null) {
      await storage.clear();
      return DataState<User>(
        success: false,
        error: meResponse.error,
        statusCode: meResponse.statusCode,
      );
    }

    return DataState<User>(
      data: meResponse.data!.toEntity(),
      success: true,
      statusCode: meResponse.statusCode,
    );
  }

  @override
  Future<DataState<User>> login(String email, String password) async {
    final tokenResponse = await remoteDatasource.login(email, password);
    if (!tokenResponse.success || tokenResponse.data == null) {
      return DataState<User>(
        success: false,
        error: tokenResponse.error,
        statusCode: tokenResponse.statusCode,
      );
    }
    return _persistSessionAndFetchUser(tokenResponse.data!);
  }

  @override
  Future<DataState<void>> logout() async {
    await storage.clear();
    return DataState<void>(data: null, success: true);
  }

  @override
  Future<DataState<User?>> getCurrentUser() async {
    final tokenState = await storage.read(StorageKeys.idToken);
    if (tokenState.data == null || tokenState.data!.isEmpty) {
      return DataState<User?>(success: true, data: null);
    }

    final meResponse = await remoteDatasource.getMe();
    if (meResponse.success && meResponse.data != null) {
      return DataState<User?>(success: true, data: meResponse.data!.toEntity());
    }

    // Interceptor already attempted a refresh transparently; a 401 here
    // means the session is truly gone — treat as "logged out", not an error.
    await storage.clear();
    return DataState<User?>(success: true, data: null);
  }

  @override
  Future<DataState<User>> registoProfessor({
    required String email,
    required String password,
    required String contactoTelefonico,
  }) async {
    final tokenResponse = await remoteDatasource.registoProfessor(
      email: email,
      password: password,
      contactoTelefonico: contactoTelefonico,
    );
    if (!tokenResponse.success || tokenResponse.data == null) {
      return DataState<User>(
        success: false,
        error: tokenResponse.error,
        statusCode: tokenResponse.statusCode,
      );
    }
    return _persistSessionAndFetchUser(tokenResponse.data!);
  }

  @override
  Future<DataState<void>> recuperarPassword(String email) {
    return remoteDatasource.recuperarPassword(email);
  }
}
