import 'dart:typed_data';

import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_horario/data/datasource/remote/i_horario_remote.dart';
import 'package:ghorario/features/feature_horario/data/models/horario_slot_dto.dart';
import 'package:ghorario/features/feature_horario/domain/entities/horario_resultado.dart';
import 'package:ghorario/features/feature_horario/domain/entities/job_resultado.dart';
import 'package:ghorario/features/feature_horario/domain/entities/pendencia.dart';
import 'package:ghorario/features/feature_horario/domain/entities/professor_qualificado.dart';
import 'package:ghorario/features/feature_horario/domain/entities/bloco_vago.dart';
import 'package:ghorario/features/feature_horario/domain/entities/alocacao_manual_response.dart';
import 'package:ghorario/features/feature_horario/domain/repository/i_horario_repository.dart';

/// Concrete implementation of [IHorarioRepository].
class HorarioRepositoryImpl implements IHorarioRepository {
  HorarioRepositoryImpl({required this.remoteDatasource});

  final IHorarioRemote remoteDatasource;

  @override
  Future<DataState<String>> triggerGeneration({required int anoLetivo, required String semestre}) {
    return remoteDatasource.triggerGeneration(anoLetivo: anoLetivo, semestre: semestre);
  }

  @override
  Future<DataState<JobResultado>> checkStatus(String jobId) {
    return remoteDatasource.checkStatus(jobId);
  }

  DataState<HorarioResultado> _toEntityState(DataState<HorarioResponseDto> response) {
    if (response.success && response.data != null) {
      return DataState<HorarioResultado>(
        data: response.data!.toEntity(),
        success: true,
        statusCode: response.statusCode,
      );
    }
    return DataState<HorarioResultado>(
      success: false,
      error: response.error,
      statusCode: response.statusCode,
    );
  }

  @override
  Future<DataState<HorarioResultado>> getTimetableByTurma(
    String turmaId, {
    int? anoLetivo,
    String? semestre,
  }) async {
    return _toEntityState(
      await remoteDatasource.getTimetableByTurma(turmaId, anoLetivo: anoLetivo, semestre: semestre),
    );
  }

  @override
  Future<DataState<HorarioResultado>> getTimetableByProfessor(
    String professorId, {
    int? anoLetivo,
    String? semestre,
  }) async {
    return _toEntityState(
      await remoteDatasource.getTimetableByProfessor(professorId, anoLetivo: anoLetivo, semestre: semestre),
    );
  }

  @override
  Future<DataState<Uint8List>> downloadHorarioTurmaPdf(String turmaId) {
    return remoteDatasource.downloadHorarioTurmaPdf(turmaId);
  }

  @override
  Future<DataState<Uint8List>> downloadExportarTodosPdf(String jobId) {
    return remoteDatasource.downloadExportarTodosPdf(jobId);
  }

  @override
  Future<DataState<List<Pendencia>>> getPendencias(String jobId) async {
    final response = await remoteDatasource.getPendencias(jobId);
    if (response.success && response.data != null) {
      final list = response.data!.map((e) => e.toEntity()).toList();
      return DataState<List<Pendencia>>(data: list, success: true, statusCode: response.statusCode);
    }
    return DataState<List<Pendencia>>(success: false, error: response.error, statusCode: response.statusCode);
  }

  @override
  Future<DataState<List<ProfessorQualificado>>> getProfessoresQualificados(String turmaId, String disciplinaId) async {
    final response = await remoteDatasource.getProfessoresQualificados(turmaId, disciplinaId);
    if (response.success && response.data != null) {
      final list = response.data!.map((e) => e.toEntity()).toList();
      return DataState<List<ProfessorQualificado>>(data: list, success: true, statusCode: response.statusCode);
    }
    return DataState<List<ProfessorQualificado>>(success: false, error: response.error, statusCode: response.statusCode);
  }

  @override
  Future<DataState<List<BlocoVago>>> getSlotsVagos(String turmaId, String jobId) async {
    final response = await remoteDatasource.getSlotsVagos(turmaId, jobId);
    if (response.success && response.data != null) {
      final list = response.data!.map((e) => e.toEntity()).toList();
      return DataState<List<BlocoVago>>(data: list, success: true, statusCode: response.statusCode);
    }
    return DataState<List<BlocoVago>>(success: false, error: response.error, statusCode: response.statusCode);
  }

  @override
  Future<DataState<List<AlocacaoManualResponse>>> criarAlocacaoManual({
    required String jobId,
    required String turmaId,
    required String disciplinaId,
    required String professorId,
    required String salaId,
    required String diaSemana,
    required String turno,
    required List<int> periodos,
  }) async {
    final response = await remoteDatasource.criarAlocacaoManual(
      jobId: jobId,
      turmaId: turmaId,
      disciplinaId: disciplinaId,
      professorId: professorId,
      salaId: salaId,
      diaSemana: diaSemana,
      turno: turno,
      periodos: periodos,
    );
    if (response.success && response.data != null) {
      final list = response.data!.map((e) => e.toEntity()).toList();
      return DataState<List<AlocacaoManualResponse>>(data: list, success: true, statusCode: response.statusCode);
    }
    return DataState<List<AlocacaoManualResponse>>(success: false, error: response.error, statusCode: response.statusCode);
  }

  @override
  Future<DataState<AlocacaoManualResponse>> moverAlocacao(int alocacaoId, String diaSemana, int periodo) async {
    final response = await remoteDatasource.moverAlocacao(alocacaoId, diaSemana, periodo);
    if (response.success && response.data != null) {
      return DataState<AlocacaoManualResponse>(data: response.data!.toEntity(), success: true, statusCode: response.statusCode);
    }
    return DataState<AlocacaoManualResponse>(success: false, error: response.error, statusCode: response.statusCode);
  }

  @override
  Future<DataState<void>> removerAlocacao(int alocacaoId) {
    return remoteDatasource.removerAlocacao(alocacaoId);
  }

  @override
  Future<DataState<JobResultado?>> getJobByScope(int anoLetivo, String semestre) {
    return remoteDatasource.getJobByScope(anoLetivo, semestre);
  }

  @override
  Future<DataState<void>> deleteJob(String jobId) {
    return remoteDatasource.deleteJob(jobId);
  }
}

