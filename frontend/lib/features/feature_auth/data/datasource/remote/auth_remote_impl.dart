import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_auth/data/datasource/remote/i_auth_remote.dart';
import 'package:ghorario/features/feature_auth/data/models/token_dto.dart';
import 'package:ghorario/features/feature_auth/data/models/user_dto.dart';

/// Concrete implementation of [IAuthRemote].
class AuthRemoteImpl implements IAuthRemote {
  AuthRemoteImpl(this._http);

  final IHttpMethods _http;

  @override
  Future<DataState<TokenDto>> login(String email, String password) async {
    final response = await _http.post<dynamic>(
      '/auth/login',
      data: {'email': email, 'password': password},
    );
    if (response.success && response.data != null) {
      return DataState<TokenDto>(
        data: TokenDto.fromJson(response.data as Map<String, dynamic>),
        success: true,
        statusCode: response.statusCode,
      );
    }
    return DataState<TokenDto>(
      success: false,
      error: response.error,
      statusCode: response.statusCode,
    );
  }

  @override
  Future<DataState<TokenDto>> refresh(String refreshToken) async {
    final response = await _http.post<dynamic>(
      '/auth/refresh',
      data: {'refresh_token': refreshToken},
    );
    if (response.success && response.data != null) {
      return DataState<TokenDto>(
        data: TokenDto.fromJson(response.data as Map<String, dynamic>),
        success: true,
        statusCode: response.statusCode,
      );
    }
    return DataState<TokenDto>(
      success: false,
      error: response.error,
      statusCode: response.statusCode,
    );
  }

  @override
  Future<DataState<UserDto>> getMe() async {
    final response = await _http.get<dynamic>('/auth/me');
    if (response.success && response.data != null) {
      return DataState<UserDto>(
        data: UserDto.fromJson(response.data as Map<String, dynamic>),
        success: true,
        statusCode: response.statusCode,
      );
    }
    return DataState<UserDto>(
      success: false,
      error: response.error,
      statusCode: response.statusCode,
    );
  }

  @override
  Future<DataState<TokenDto>> registoProfessor({
    required String email,
    required String password,
    required String contactoTelefonico,
  }) async {
    final response = await _http.post<dynamic>(
      '/auth/registo-professor',
      data: {'email': email, 'password': password, 'contacto_telefonico': contactoTelefonico},
    );
    if (response.success && response.data != null) {
      return DataState<TokenDto>(
        data: TokenDto.fromJson(response.data as Map<String, dynamic>),
        success: true,
        statusCode: response.statusCode,
      );
    }
    return DataState<TokenDto>(
      success: false,
      error: response.error,
      statusCode: response.statusCode,
    );
  }

  @override
  Future<DataState<void>> recuperarPassword(String email) async {
    final response = await _http.post<dynamic>('/auth/recuperar-password', data: {'email': email});
    return DataState<void>(success: response.success, error: response.error, statusCode: response.statusCode);
  }
}
