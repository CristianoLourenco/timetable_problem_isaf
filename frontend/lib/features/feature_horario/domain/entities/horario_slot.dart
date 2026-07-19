/// Domain entity representing a single timetable assignment slot.
class HorarioSlot {
  const HorarioSlot({
    required this.id,
    required this.docenteName,
    required this.turmaName,
    required this.disciplinaName,
    required this.salaName,
    required this.dayOfWeek,
    required this.timeSlot,
    required this.turno,
    required this.periodo,
    required this.disciplinaId,
    required this.professorId,
    required this.salaId,
    this.alocacaoId,
  });

  final String id;
  final String docenteName;
  final String turmaName;
  final String disciplinaName;
  final String salaName;
  final int dayOfWeek; // 1 to 5 for Mon-Fri
  final String timeSlot; // e.g., "08:00-09:30"
  final String turno;
  final int periodo;
  final int disciplinaId;
  final int professorId;
  final int salaId;
  final int? alocacaoId;
}

