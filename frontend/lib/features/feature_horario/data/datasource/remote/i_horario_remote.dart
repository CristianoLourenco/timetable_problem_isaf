import 'dart:typed_data';

import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_horario/data/models/horario_slot_dto.dart';
import 'package:ghorario/features/feature_horario/data/models/pendencia_dto.dart';
import 'package:ghorario/features/feature_horario/data/models/professor_qualificado_dto.dart';
import 'package:ghorario/features/feature_horario/data/models/bloco_vago_dto.dart';
import 'package:ghorario/features/feature_horario/data/models/alocacao_manual_response_dto.dart';
import 'package:ghorario/features/feature_horario/domain/entities/job_resultado.dart';

/// Abstract remote datasource interface for Horario.
abstract class IHorarioRemote {
  /// `POST /gerar-horario` — gera de uma vez o horário completo de todas as
  /// turmas do [anoLetivo]/[semestre] pedido.
  Future<DataState<String>> triggerGeneration({required int anoLetivo, required String semestre});

  /// `GET /jobs/{job_id}`.
  Future<DataState<JobResultado>> checkStatus(String jobId);

  /// `GET /horarios/turma/{turma_id}` — always the most recent DONE job for that turma.
  Future<DataState<HorarioResponseDto>> getTimetableByTurma(String turmaId);

  /// `GET /horarios/professor/{professor_id}`.
  Future<DataState<HorarioResponseDto>> getTimetableByProfessor(String professorId);

  /// `GET /horarios/turma/{turma_id}/pdf` — bytes de um único PDF.
  Future<DataState<Uint8List>> downloadHorarioTurmaPdf(String turmaId);

  /// `GET /jobs/{job_id}/exportar-pdf` — bytes de um .zip com um PDF por turma.
  Future<DataState<Uint8List>> downloadExportarTodosPdf(String jobId);

  /// `GET /jobs/{job_id}/pendencias`.
  Future<DataState<List<PendenciaDto>>> getPendencias(String jobId);

  /// `GET /turmas/{turma_id}/professores-qualificados`.
  Future<DataState<List<ProfessorQualificadoDto>>> getProfessoresQualificados(String turmaId, String disciplinaId);

  /// `GET /turmas/{turma_id}/slots-vagos`.
  Future<DataState<List<BlocoVagoDto>>> getSlotsVagos(String turmaId, String jobId);

  /// `POST /alocacoes`.
  Future<DataState<List<AlocacaoManualResponseDto>>> criarAlocacaoManual({
    required String jobId,
    required String turmaId,
    required String disciplinaId,
    required String professorId,
    required String salaId,
    required String diaSemana,
    required String turno,
    required List<int> periodos,
  });

  /// `PATCH /alocacoes/{alocacao_id}`.
  Future<DataState<AlocacaoManualResponseDto>> moverAlocacao(int alocacaoId, String diaSemana, int periodo);

  /// `DELETE /alocacoes/{alocacao_id}`.
  Future<DataState<void>> removerAlocacao(int alocacaoId);

  /// `GET /jobs?ano_letivo={ano}&semestre={semestre}`.
  Future<DataState<JobResultado?>> getJobByScope(int anoLetivo, String semestre);

  /// `DELETE /jobs/{job_id}`.
  Future<DataState<void>> deleteJob(String jobId);
}

