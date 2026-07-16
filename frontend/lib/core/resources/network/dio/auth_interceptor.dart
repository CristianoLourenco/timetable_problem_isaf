import 'package:dio/dio.dart';
import 'package:ghorario/core/constants/storage_keys.dart';
import 'package:ghorario/core/resources/storage/i_storage_methods.dart';

/// Attaches `Authorization: Bearer <id_token>` to every request (RN09) and,
/// on a 401 response, attempts a single `POST /auth/refresh` before retrying
/// the original request. If the refresh also fails, the stored session is
/// cleared and the original 401 is propagated so the UI can route to /login.
class AuthInterceptor extends Interceptor {
  AuthInterceptor(this._storage, this._dio);

  final IStorageMethods _storage;
  final Dio _dio;

  static const String _refreshPath = '/auth/refresh';

  @override
  Future<void> onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    if (!options.path.contains(_refreshPath) && !options.path.contains('/auth/login')) {
      final tokenState = await _storage.read(StorageKeys.idToken);
      final token = tokenState.data;
      if (token != null && token.isNotEmpty) {
        options.headers['Authorization'] = 'Bearer $token';
      }
    }
    handler.next(options);
  }

  @override
  Future<void> onError(
    DioException err,
    ErrorInterceptorHandler handler,
  ) async {
    final requestPath = err.requestOptions.path;
    final alreadyRetried = err.requestOptions.extra['retried'] == true;

    if (err.response?.statusCode != 401 ||
        requestPath.contains(_refreshPath) ||
        alreadyRetried) {
      handler.next(err);
      return;
    }

    final refreshTokenState = await _storage.read(StorageKeys.refreshToken);
    final refreshToken = refreshTokenState.data;
    if (refreshToken == null || refreshToken.isEmpty) {
      await _storage.clear();
      handler.next(err);
      return;
    }

    try {
      final refreshResponse = await _dio.post<Map<String, dynamic>>(
        _refreshPath,
        data: {'refresh_token': refreshToken},
      );
      final newIdToken = refreshResponse.data?['id_token'] as String?;
      final newRefreshToken = refreshResponse.data?['refresh_token'] as String?;
      if (newIdToken == null || newRefreshToken == null) {
        await _storage.clear();
        handler.next(err);
        return;
      }

      await _storage.save(StorageKeys.idToken, newIdToken);
      await _storage.save(StorageKeys.refreshToken, newRefreshToken);

      final retryOptions = err.requestOptions;
      retryOptions.headers['Authorization'] = 'Bearer $newIdToken';
      retryOptions.extra['retried'] = true;
      final retryResponse = await _dio.fetch<dynamic>(retryOptions);
      handler.resolve(retryResponse);
    } on DioException {
      await _storage.clear();
      handler.next(err);
    }
  }
}
