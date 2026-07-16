import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_disciplinas/data/datasource/remote/i_disciplina_remote.dart';
import 'package:ghorario/features/feature_disciplinas/data/models/disciplina_dto.dart';
import 'package:ghorario/features/feature_disciplinas/domain/entities/disciplina.dart';
import 'package:ghorario/features/feature_disciplinas/domain/repository/i_disciplina_repository.dart';

/// Concrete implementation of [IDisciplinaRepository].
class DisciplinaRepositoryImpl implements IDisciplinaRepository {
  DisciplinaRepositoryImpl({required this.remoteDatasource});

  final IDisciplinaRemote remoteDatasource;

  @override
  Future<DataState<List<Disciplina>>> getAll() async {
    final response = await remoteDatasource.getAll();
    if (response.success && response.data != null) {
      final entities = response.data!.map((DisciplinaDto dto) => dto.toEntity()).toList();
      return DataState<List<Disciplina>>(
        data: entities,
        success: true,
        statusCode: response.statusCode,
      );
    }
    return DataState<List<Disciplina>>(
      success: false,
      error: response.error,
      statusCode: response.statusCode,
    );
  }

  @override
  Future<DataState<Disciplina>> getById(String id) async {
    final response = await remoteDatasource.getById(id);
    if (response.success && response.data != null) {
      return DataState<Disciplina>(
        data: response.data!.toEntity(),
        success: true,
        statusCode: response.statusCode,
      );
    }
    return DataState<Disciplina>(
      success: false,
      error: response.error,
      statusCode: response.statusCode,
    );
  }

  @override
  Future<DataState<void>> create(Disciplina disciplina) async {
    return remoteDatasource.create(DisciplinaDto.fromEntity(disciplina));
  }

  @override
  Future<DataState<void>> update(Disciplina disciplina) async {
    return remoteDatasource.update(DisciplinaDto.fromEntity(disciplina));
  }

  @override
  Future<DataState<void>> delete(String id) async {
    return remoteDatasource.delete(id);
  }
}
