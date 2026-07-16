import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_horario/data/datasource/remote/i_horario_remote.dart';
import 'package:ghorario/features/feature_horario/data/models/horario_slot_dto.dart';
import 'package:ghorario/features/feature_horario/domain/entities/job_resultado.dart';
import 'package:ghorario/features/feature_horario/domain/entities/job_status.dart';

/// Concrete implementation of [IHorarioRemote] using [IHttpMethods].
class HorarioRemoteImpl implements IHorarioRemote {
  HorarioRemoteImpl(this._http);

  final IHttpMethods _http;

  @override
  Future<DataState<String>> triggerGeneration() async {
    final response = await _http.post<dynamic>('/gerar-horario');
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
      ),
      success: true,
      statusCode: response.statusCode,
    );
  }

  Future<DataState<List<HorarioSlotDto>>> _fetchHorario(String path) async {
    final response = await _http.get<dynamic>(path);
    if (!response.success || response.data == null) {
      return DataState<List<HorarioSlotDto>>(
        success: false,
        error: response.error,
        statusCode: response.statusCode,
      );
    }
    try {
      final dataMap = response.data as Map<String, dynamic>;
      final dias = dataMap['dias'] as List;
      final slots = <HorarioSlotDto>[];
      for (final dia in dias) {
        final diaMap = dia as Map<String, dynamic>;
        final diaSemana = diaMap['dia_semana']?.toString() ?? '';
        final tempos = diaMap['tempos'] as List;
        for (final tempo in tempos) {
          slots.add(HorarioSlotDto.fromJson(tempo as Map<String, dynamic>, diaSemana));
        }
      }
      return DataState<List<HorarioSlotDto>>(data: slots, success: true, statusCode: response.statusCode);
    } catch (e) {
      return DataState<List<HorarioSlotDto>>(
        success: false,
        error: ServerFailure(message: 'Erro ao processar dados do horário: $e'),
      );
    }
  }

  @override
  Future<DataState<List<HorarioSlotDto>>> getTimetableByTurma(String turmaId) {
    return _fetchHorario('/horarios/turma/$turmaId');
  }

  @override
  Future<DataState<List<HorarioSlotDto>>> getTimetableByProfessor(String professorId) {
    return _fetchHorario('/horarios/professor/$professorId');
  }
}
