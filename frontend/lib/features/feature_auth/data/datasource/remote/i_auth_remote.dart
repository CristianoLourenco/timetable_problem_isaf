import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_auth/data/models/token_dto.dart';
import 'package:ghorario/features/feature_auth/data/models/user_dto.dart';

/// Abstract remote datasource interface for authentication.
abstract class IAuthRemote {
  Future<DataState<TokenDto>> login(String email, String password);
  Future<DataState<TokenDto>> refresh(String refreshToken);
  Future<DataState<UserDto>> getMe();

  /// `POST /auth/registo-professor` — 403 se o email não corresponder a um
  /// Professor já criado pelo Gestor (RN10).
  Future<DataState<TokenDto>> registoProfessor({
    required String email,
    required String password,
    required String contactoTelefonico,
  });

  /// `POST /auth/recuperar-password` — devolve sempre sucesso (204), mesmo
  /// que o email não exista, para não revelar contas registadas.
  Future<DataState<void>> recuperarPassword(String email);
}
