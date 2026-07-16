import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_horario/data/models/horario_slot_dto.dart';
import 'package:ghorario/features/feature_horario/domain/entities/job_resultado.dart';

/// Abstract remote datasource interface for Horario.
abstract class IHorarioRemote {
  Future<DataState<String>> triggerGeneration();

  /// `GET /jobs/{job_id}`.
  Future<DataState<JobResultado>> checkStatus(String jobId);

  /// `GET /horarios/turma/{turma_id}` — always the most recent DONE job for that turma.
  Future<DataState<List<HorarioSlotDto>>> getTimetableByTurma(String turmaId);

  /// `GET /horarios/professor/{professor_id}`.
  Future<DataState<List<HorarioSlotDto>>> getTimetableByProfessor(String professorId);
}
