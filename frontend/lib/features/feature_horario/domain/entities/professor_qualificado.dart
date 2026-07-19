/// Domain entity representing a qualified teacher.
class ProfessorQualificado {
  const ProfessorQualificado({
    required this.id,
    required this.nome,
    required this.classificacao,
    required this.vinculoCasa,
  });

  final int id;
  final String nome;
  final int classificacao;
  final bool vinculoCasa;
}
