import 'dart:typed_data';

import 'package:dio/dio.dart' show ResponseType;
import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_horario/data/datasource/remote/i_horario_remote.dart';
import 'package:ghorario/features/feature_horario/data/models/horario_slot_dto.dart';
import 'package:ghorario/features/feature_horario/data/models/pendencia_dto.dart';
import 'package:ghorario/features/feature_horario/data/models/professor_qualificado_dto.dart';
import 'package:ghorario/features/feature_horario/data/models/bloco_vago_dto.dart';
import 'package:ghorario/features/feature_horario/data/models/alocacao_manual_response_dto.dart';
import 'package:ghorario/features/feature_horario/domain/entities/job_resultado.dart';
import 'package:ghorario/features/feature_horario/domain/entities/job_status.dart';

/// Concrete implementation of [IHorarioRemote] using [IHttpMethods].
class HorarioRemoteImpl implements IHorarioRemote {
  HorarioRemoteImpl(this._http);

  final IHttpMethods _http;

  @override
  Future<DataState<String>> triggerGeneration({required int anoLetivo, required String semestre}) async {
    final response = await _http.post<dynamic>(
      '/gerar-horario',
      data: {'ano_letivo': anoLetivo, 'semestre': semestre},
    );
    if (!response.success || response.data == null) {
      return DataState<String>(success: false, error: response.error, statusCode: response.statusCode);
    }
    final dataMap = response.data as Map<String, dynamic>;
    return DataState<String>(
      data: dataMap['job_id']?.toString(),
      success: true,
      statusCode: response.statusCode,
    );
  }

  @override
  Future<DataState<JobResultado>> checkStatus(String jobId) async {
    final response = await _http.get<dynamic>('/jobs/$jobId');
    if (!response.success || response.data == null) {
      return DataState<JobResultado>(success: false, error: response.error, statusCode: response.statusCode);
    }
    final dataMap = response.data as Map<String, dynamic>;
    return DataState<JobResultado>(
      data: JobResultado(
        status: JobStatus.fromApi(dataMap['status']?.toString()),
        diagnostico: dataMap['diagnostico'] as String?,
        tempoMaximoMinutos: dataMap['tempo_maximo_minutos'] as int?,
      ),
      success: true,
      statusCode: response.statusCode,
    );
  }

  Future<DataState<HorarioResponseDto>> _fetchHorario(String path) async {
    final response = await _http.get<dynamic>(path);
    if (!response.success || response.data == null) {
      return DataState<HorarioResponseDto>(
        success: false,
        error: response.error,
        statusCode: response.statusCode,
      );
    }
    try {
      final dataMap = response.data as Map<String, dynamic>;
      return DataState<HorarioResponseDto>(
        data: HorarioResponseDto.fromJson(dataMap),
        success: true,
        statusCode: response.statusCode,
      );
    } catch (e) {
      return DataState<HorarioResponseDto>(
        success: false,
        error: ServerFailure(message: 'Erro ao processar dados do horário: $e'),
      );
    }
  }

  @override
  Future<DataState<HorarioResponseDto>> getTimetableByTurma(String turmaId) {
    return _fetchHorario('/horarios/turma/$turmaId');
  }

  @override
  Future<DataState<HorarioResponseDto>> getTimetableByProfessor(String professorId) {
    return _fetchHorario('/horarios/professor/$professorId');
  }

  Future<DataState<Uint8List>> _downloadBytes(String path) async {
    final response = await _http.get<dynamic>(path, responseType: ResponseType.bytes);
    if (!response.success || response.data == null) {
      return DataState<Uint8List>(success: false, error: response.error, statusCode: response.statusCode);
    }
    return DataState<Uint8List>(
      data: Uint8List.fromList(List<int>.from(response.data as List)),
      success: true,
      statusCode: response.statusCode,
    );
  }

  @override
  Future<DataState<Uint8List>> downloadHorarioTurmaPdf(String turmaId) {
    return _downloadBytes('/horarios/turma/$turmaId/pdf');
  }

  @override
  Future<DataState<Uint8List>> downloadExportarTodosPdf(String jobId) {
    return _downloadBytes('/jobs/$jobId/exportar-pdf');
  }

  @override
  Future<DataState<List<PendenciaDto>>> getPendencias(String jobId) async {
    final response = await _http.get<dynamic>('/jobs/$jobId/pendencias');
    if (!response.success || response.data == null) {
      return DataState<List<PendenciaDto>>(success: false, error: response.error, statusCode: response.statusCode);
    }
    try {
      final list = (response.data as List)
          .map((e) => PendenciaDto.fromJson(e as Map<String, dynamic>))
          .toList();
      return DataState<List<PendenciaDto>>(data: list, success: true, statusCode: response.statusCode);
    } catch (e) {
      return DataState<List<PendenciaDto>>(success: false, error: ServerFailure(message: 'Erro ao processar pendências: $e'));
    }
  }

  @override
  Future<DataState<List<ProfessorQualificadoDto>>> getProfessoresQualificados(String turmaId, String disciplinaId) async {
    final response = await _http.get<dynamic>(
      '/turmas/$turmaId/professores-qualificados',
      queryParameters: {'disciplina_id': int.tryParse(disciplinaId) ?? 0},
    );
    if (!response.success || response.data == null) {
      return DataState<List<ProfessorQualificadoDto>>(success: false, error: response.error, statusCode: response.statusCode);
    }
    try {
      final list = (response.data as List)
          .map((e) => ProfessorQualificadoDto.fromJson(e as Map<String, dynamic>))
          .toList();
      return DataState<List<ProfessorQualificadoDto>>(data: list, success: true, statusCode: response.statusCode);
    } catch (e) {
      return DataState<List<ProfessorQualificadoDto>>(success: false, error: ServerFailure(message: 'Erro ao processar professores qualificados: $e'));
    }
  }

  @override
  Future<DataState<List<BlocoVagoDto>>> getSlotsVagos(String turmaId, String jobId) async {
    final response = await _http.get<dynamic>(
      '/turmas/$turmaId/slots-vagos',
      queryParameters: {'job_id': jobId},
    );
    if (!response.success || response.data == null) {
      return DataState<List<BlocoVagoDto>>(success: false, error: response.error, statusCode: response.statusCode);
    }
    try {
      final list = (response.data as List)
          .map((e) => BlocoVagoDto.fromJson(e as Map<String, dynamic>))
          .toList();
      return DataState<List<BlocoVagoDto>>(data: list, success: true, statusCode: response.statusCode);
    } catch (e) {
      return DataState<List<BlocoVagoDto>>(success: false, error: ServerFailure(message: 'Erro ao processar slots vagos: $e'));
    }
  }

  @override
  Future<DataState<List<AlocacaoManualResponseDto>>> criarAlocacaoManual({
    required String jobId,
    required String turmaId,
    required String disciplinaId,
    required String professorId,
    required String salaId,
    required String diaSemana,
    required String turno,
    required List<int> periodos,
  }) async {
    final response = await _http.post<dynamic>(
      '/alocacoes',
      data: {
        'job_id': jobId,
        'turma_id': int.tryParse(turmaId) ?? 0,
        'disciplina_id': int.tryParse(disciplinaId) ?? 0,
        'professor_id': int.tryParse(professorId) ?? 0,
        'sala_id': int.tryParse(salaId) ?? 0,
        'dia_semana': diaSemana,
        'turno': turno,
        'periodos': periodos,
      },
    );
    if (!response.success || response.data == null) {
      return DataState<List<AlocacaoManualResponseDto>>(success: false, error: response.error, statusCode: response.statusCode);
    }
    try {
      final list = (response.data as List)
          .map((e) => AlocacaoManualResponseDto.fromJson(e as Map<String, dynamic>))
          .toList();
      return DataState<List<AlocacaoManualResponseDto>>(data: list, success: true, statusCode: response.statusCode);
    } catch (e) {
      return DataState<List<AlocacaoManualResponseDto>>(success: false, error: ServerFailure(message: 'Erro ao processar alocação manual: $e'));
    }
  }

  @override
  Future<DataState<AlocacaoManualResponseDto>> moverAlocacao(int alocacaoId, String diaSemana, int periodo) async {
    final response = await _http.patch<dynamic>(
      '/alocacoes/$alocacaoId',
      data: {
        'dia_semana': diaSemana,
        'periodo': periodo,
      },
    );
    if (!response.success || response.data == null) {
      return DataState<AlocacaoManualResponseDto>(success: false, error: response.error, statusCode: response.statusCode);
    }
    try {
      final data = AlocacaoManualResponseDto.fromJson(response.data as Map<String, dynamic>);
      return DataState<AlocacaoManualResponseDto>(data: data, success: true, statusCode: response.statusCode);
    } catch (e) {
      return DataState<AlocacaoManualResponseDto>(success: false, error: ServerFailure(message: 'Erro ao processar movimento: $e'));
    }
  }

  @override
  Future<DataState<void>> removerAlocacao(int alocacaoId) async {
    final response = await _http.delete<dynamic>('/alocacoes/$alocacaoId');
    if (!response.success) {
      return DataState<void>(success: false, error: response.error, statusCode: response.statusCode);
    }
    return DataState<void>(success: true, statusCode: response.statusCode);
  }
}

