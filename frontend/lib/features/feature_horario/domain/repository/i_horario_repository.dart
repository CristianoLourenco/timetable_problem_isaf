import 'dart:typed_data';

import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_horario/domain/entities/horario_resultado.dart';
import 'package:ghorario/features/feature_horario/domain/entities/job_resultado.dart';
import 'package:ghorario/features/feature_horario/domain/entities/pendencia.dart';
import 'package:ghorario/features/feature_horario/domain/entities/professor_qualificado.dart';
import 'package:ghorario/features/feature_horario/domain/entities/bloco_vago.dart';
import 'package:ghorario/features/feature_horario/domain/entities/alocacao_manual_response.dart';

/// Abstract repository interface for Horario.
abstract class IHorarioRepository {
  Future<DataState<String>> triggerGeneration({required int anoLetivo, required String semestre});
  Future<DataState<JobResultado>> checkStatus(String jobId);
  Future<DataState<HorarioResultado>> getTimetableByTurma(String turmaId, {int? anoLetivo, String? semestre});
  Future<DataState<HorarioResultado>> getTimetableByProfessor(String professorId, {int? anoLetivo, String? semestre});
  Future<DataState<Uint8List>> downloadHorarioTurmaPdf(String turmaId);
  Future<DataState<Uint8List>> downloadExportarTodosPdf(String jobId);
  Future<DataState<List<Pendencia>>> getPendencias(String jobId);
  Future<DataState<List<ProfessorQualificado>>> getProfessoresQualificados(String turmaId, String disciplinaId);
  Future<DataState<List<BlocoVago>>> getSlotsVagos(String turmaId, String jobId);
  Future<DataState<List<AlocacaoManualResponse>>> criarAlocacaoManual({
    required String jobId,
    required String turmaId,
    required String disciplinaId,
    required String professorId,
    required String salaId,
    required String diaSemana,
    required String turno,
    required List<int> periodos,
  });
  Future<DataState<AlocacaoManualResponse>> moverAlocacao(int alocacaoId, String diaSemana, int periodo);
  Future<DataState<void>> removerAlocacao(int alocacaoId);
  Future<DataState<JobResultado?>> getJobByScope(int anoLetivo, String semestre);
  Future<DataState<void>> deleteJob(String jobId);
}

