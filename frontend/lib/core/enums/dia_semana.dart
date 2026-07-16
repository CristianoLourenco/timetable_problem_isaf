/// The five teaching weekdays used across `HorarioItemSchema.dia_semana`,
/// `Slot.dia_semana` and the professor's weekly availability grid (RF05,
/// RF09-RF12). Shared across features — kept in `core` rather than a single
/// feature's domain.
enum DiaSemana {
  segunda,
  terca,
  quarta,
  quinta,
  sexta;

  static const Map<DiaSemana, String> _apiValues = {
    DiaSemana.segunda: 'segunda',
    DiaSemana.terca: 'terca',
    DiaSemana.quarta: 'quarta',
    DiaSemana.quinta: 'quinta',
    DiaSemana.sexta: 'sexta',
  };

  static const Map<DiaSemana, String> _displayNames = {
    DiaSemana.segunda: 'Segunda-feira',
    DiaSemana.terca: 'Terça-feira',
    DiaSemana.quarta: 'Quarta-feira',
    DiaSemana.quinta: 'Quinta-feira',
    DiaSemana.sexta: 'Sexta-feira',
  };

  static DiaSemana fromApi(String value) {
    final normalized = value.toLowerCase().replaceAll('ç', 'c').replaceAll('é', 'e');
    return _apiValues.entries
        .firstWhere(
          (e) => e.value == normalized,
          orElse: () => const MapEntry(DiaSemana.segunda, 'segunda'),
        )
        .key;
  }

  String get apiValue => _apiValues[this]!;
  String get displayName => _displayNames[this]!;

  /// 1-based order (Monday = 1) matching the grid columns used in the UI.
  int get ordem => index + 1;
}
