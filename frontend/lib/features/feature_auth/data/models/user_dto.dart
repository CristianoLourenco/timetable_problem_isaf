import 'package:ghorario/features/feature_auth/domain/entities/papel_utilizador.dart';
import 'package:ghorario/features/feature_auth/domain/entities/user.dart';

/// DTO for the `GET /auth/me` response (`MeResponseSchema`).
class UserDto {
  const UserDto({
    required this.email,
    required this.papel,
    this.professorId,
  });

  final String email;
  final PapelUtilizador papel;
  final int? professorId;

  factory UserDto.fromJson(Map<String, dynamic> json) {
    return UserDto(
      email: json['email'] as String? ?? '',
      papel: PapelUtilizador.fromApi(json['papel'] as String? ?? ''),
      professorId: json['professor_id'] as int?,
    );
  }

  User toEntity() {
    return User(email: email, papel: papel, professorId: professorId);
  }
}
