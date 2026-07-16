import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_horario/domain/entities/horario_slot.dart';
import 'package:ghorario/features/feature_horario/domain/entities/job_resultado.dart';

/// Abstract repository interface for Horario.
abstract class IHorarioRepository {
  Future<DataState<String>> triggerGeneration();
  Future<DataState<JobResultado>> checkStatus(String jobId);
  Future<DataState<List<HorarioSlot>>> getTimetableByTurma(String turmaId);
  Future<DataState<List<HorarioSlot>>> getTimetableByProfessor(String professorId);
}
