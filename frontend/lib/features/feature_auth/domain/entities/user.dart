import 'package:ghorario/features/feature_auth/domain/entities/papel_utilizador.dart';

/// Domain entity representing the authenticated user's session identity.
///
/// Maps to `GET /auth/me` — the only place the frontend learns the role
/// (RN09-RN11) and, for a Professor, the `professor_id` needed for
/// "my timetable" / "my availability" screens.
class User {
  const User({
    required this.email,
    required this.papel,
    this.professorId,
    this.nome,
  });

  final String email;
  final PapelUtilizador papel;
  final int? professorId;

  /// Nome do Professor (quando [papel] é professor). O Gestor não tem nome
  /// próprio no modelo actual — fica `null`.
  final String? nome;

  /// Texto de identificação a mostrar na UI: nome se existir, senão o email.
  String get nomeVisivel => nome ?? email;

  bool get isGestorOuSuperadmin =>
      papel == PapelUtilizador.gestor || papel == PapelUtilizador.superadmin;
  bool get isProfessor => papel == PapelUtilizador.professor;
}
