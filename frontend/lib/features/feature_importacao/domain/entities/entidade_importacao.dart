/// Entities supported by `POST /upload/excel?entidade=...` (RF06/RF07/RF08).
///
/// Kept as an enum instead of raw strings so call sites can never typo the
/// `entidade` query parameter — [apiValue] is the single source of truth for
/// the wire format expected by the backend.
enum EntidadeImportacao {
  cursos,
  professores,
  disciplinas,
  salas,
  turmas,
  qualificacoes,
  gradeCurricular;

  String get apiValue {
    switch (this) {
      case EntidadeImportacao.gradeCurricular:
        return 'grade_curricular';
      default:
        return name;
    }
  }
}
