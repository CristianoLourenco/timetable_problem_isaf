/// Domain entity representing a vacant schedule block.
class BlocoVago {
  const BlocoVago({
    required this.diaSemana,
    required this.turno,
    required this.periodos,
  });

  final String diaSemana;
  final String turno;
  final List<int> periodos;
}
