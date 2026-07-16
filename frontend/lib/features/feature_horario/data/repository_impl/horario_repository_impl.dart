import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_horario/data/datasource/remote/i_horario_remote.dart';
import 'package:ghorario/features/feature_horario/data/models/horario_slot_dto.dart';
import 'package:ghorario/features/feature_horario/domain/entities/horario_slot.dart';
import 'package:ghorario/features/feature_horario/domain/entities/job_resultado.dart';
import 'package:ghorario/features/feature_horario/domain/repository/i_horario_repository.dart';

/// Concrete implementation of [IHorarioRepository].
class HorarioRepositoryImpl implements IHorarioRepository {
  HorarioRepositoryImpl({required this.remoteDatasource});

  final IHorarioRemote remoteDatasource;

  @override
  Future<DataState<String>> triggerGeneration() {
    return remoteDatasource.triggerGeneration();
  }

  @override
  Future<DataState<JobResultado>> checkStatus(String jobId) {
    return remoteDatasource.checkStatus(jobId);
  }

  DataState<List<HorarioSlot>> _toEntityState(DataState<List<HorarioSlotDto>> response) {
    if (response.success && response.data != null) {
      final entities = response.data!.map((HorarioSlotDto dto) => dto.toEntity()).toList();
      return DataState<List<HorarioSlot>>(data: entities, success: true, statusCode: response.statusCode);
    }
    return DataState<List<HorarioSlot>>(
      success: false,
      error: response.error,
      statusCode: response.statusCode,
    );
  }

  @override
  Future<DataState<List<HorarioSlot>>> getTimetableByTurma(String turmaId) async {
    return _toEntityState(await remoteDatasource.getTimetableByTurma(turmaId));
  }

  @override
  Future<DataState<List<HorarioSlot>>> getTimetableByProfessor(String professorId) async {
    return _toEntityState(await remoteDatasource.getTimetableByProfessor(professorId));
  }
}
