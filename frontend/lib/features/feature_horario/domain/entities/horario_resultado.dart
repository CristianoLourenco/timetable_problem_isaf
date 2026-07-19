import 'package:ghorario/features/feature_horario/domain/entities/horario_slot.dart';

/// Result of a `GET /horarios/turma|professor/{id}` fetch — the slots plus the
/// `job_id` that produced them (needed later to trigger "Exportar Todos", RF11,
/// without requiring a fresh generation in the same session).
class HorarioResultado {
  const HorarioResultado({required this.slots, required this.jobId});

  final List<HorarioSlot> slots;
  final String jobId;
}
