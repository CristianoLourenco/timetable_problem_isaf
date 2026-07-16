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
  });

  final String email;
  final PapelUtilizador papel;
  final int? professorId;

  bool get isGestorOuSuperadmin =>
      papel == PapelUtilizador.gestor || papel == PapelUtilizador.superadmin;
  bool get isProfessor => papel == PapelUtilizador.professor;
}
