/// The three class shifts a Turma can run in (`TurmaBase.turno`), also used
/// to key the weekly time grid (`periodo` restarts at 1 in each turno — see
/// backend/app/core/calendario.py). Shared across features — kept in `core`
/// alongside [DiaSemana] rather than a single feature's domain.
enum Turno {
  manha,
  tarde,
  noite;

  static const Map<Turno, String> _apiValues = {
    Turno.manha: 'manha',
    Turno.tarde: 'tarde',
    Turno.noite: 'noite',
  };

  static const Map<Turno, String> _displayNames = {
    Turno.manha: 'Manhã',
    Turno.tarde: 'Tarde',
    Turno.noite: 'Noite',
  };

  static Turno? fromApi(String? value) {
    if (value == null) return null;
    final normalized = value.toLowerCase().replaceAll('ã', 'a');
    for (final entry in _apiValues.entries) {
      if (entry.value == normalized) return entry.key;
    }
    return null;
  }

  String get apiValue => _apiValues[this]!;
  String get displayName => _displayNames[this]!;
}
