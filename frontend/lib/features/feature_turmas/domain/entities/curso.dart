/// Domain entity representing a course (curso) — mirrors the backend's
/// `Curso` exactly (`CursoRead`: id, codigo, nome). It exists only as a
/// prerequisite for `Turma.cursoId`, no RF of its own.
class Curso {
  const Curso({required this.id, required this.codigo, required this.name});

  final String id;
  final String codigo;
  final String name;
}
