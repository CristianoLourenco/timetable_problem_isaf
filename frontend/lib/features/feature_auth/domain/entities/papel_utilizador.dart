/// The three roles returned by `GET /auth/me` (RN09-RN11).
enum PapelUtilizador {
  superadmin,
  gestor,
  professor;

  static PapelUtilizador fromApi(String value) {
    return PapelUtilizador.values.firstWhere(
      (p) => p.apiValue == value,
      orElse: () => PapelUtilizador.professor,
    );
  }

  String get apiValue => name.toUpperCase();

  String get rotulo => switch (this) {
        PapelUtilizador.superadmin => 'Superadmin',
        PapelUtilizador.gestor => 'Gestor',
        PapelUtilizador.professor => 'Professor',
      };
}
