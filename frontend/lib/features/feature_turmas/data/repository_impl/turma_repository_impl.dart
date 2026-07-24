import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_turmas/data/datasource/remote/i_turma_remote.dart';
import 'package:ghorario/features/feature_turmas/data/models/turma_dto.dart';
import 'package:ghorario/features/feature_turmas/domain/entities/turma.dart';
import 'package:ghorario/features/feature_turmas/domain/entities/turma_detalhada.dart';
import 'package:ghorario/features/feature_turmas/domain/repository/i_turma_repository.dart';

/// Concrete implementation of [ITurmaRepository].
class TurmaRepositoryImpl implements ITurmaRepository {
  TurmaRepositoryImpl({required this.remoteDatasource});

  final ITurmaRemote remoteDatasource;

  @override
  Future<DataState<List<Turma>>> getAll() async {
    final response = await remoteDatasource.getAll();
    if (response.success && response.data != null) {
      final entities = response.data!.map((TurmaDto dto) => dto.toEntity()).toList();
      return DataState<List<Turma>>(
        data: entities,
        success: true,
        statusCode: response.statusCode,
      );
    }
    return DataState<List<Turma>>(
      success: false,
      error: response.error,
      statusCode: response.statusCode,
    );
  }

  @override
  Future<DataState<Turma>> getById(String id) async {
    final response = await remoteDatasource.getById(id);
    if (response.success && response.data != null) {
      return DataState<Turma>(
        data: response.data!.toEntity(),
        success: true,
        statusCode: response.statusCode,
      );
    }
    return DataState<Turma>(
      success: false,
      error: response.error,
      statusCode: response.statusCode,
    );
  }

  @override
  Future<DataState<void>> create(Turma turma) async {
    return remoteDatasource.create(TurmaDto.fromEntity(turma));
  }

  @override
  Future<DataState<void>> update(Turma turma) async {
    return remoteDatasource.update(TurmaDto.fromEntity(turma));
  }

  @override
  Future<DataState<void>> delete(String id) async {
    return remoteDatasource.delete(id);
  }

  @override
  Future<DataState<List<TurmaDetalhada>>> getDetalhadas({int? anoLetivo, String? semestre}) async {
    final response = await remoteDatasource.getDetalhadas(anoLetivo: anoLetivo, semestre: semestre);
    if (response.success && response.data != null) {
      final entities = response.data!.map((dto) => dto.toEntity()).toList();
      return DataState<List<TurmaDetalhada>>(
        data: entities,
        success: true,
        statusCode: response.statusCode,
      );
    }
    return DataState<List<TurmaDetalhada>>(
      success: false,
      error: response.error,
      statusCode: response.statusCode,
    );
  }
}
