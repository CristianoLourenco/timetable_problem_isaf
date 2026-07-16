import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_turmas/data/datasource/remote/i_curso_remote.dart';
import 'package:ghorario/features/feature_turmas/data/models/curso_dto.dart';
import 'package:ghorario/features/feature_turmas/domain/entities/curso.dart';
import 'package:ghorario/features/feature_turmas/domain/repository/i_curso_repository.dart';

/// Concrete implementation of [ICursoRepository].
class CursoRepositoryImpl implements ICursoRepository {
  CursoRepositoryImpl({required this.remoteDatasource});

  final ICursoRemote remoteDatasource;

  @override
  Future<DataState<List<Curso>>> getAll() async {
    final response = await remoteDatasource.getAll();
    if (response.success && response.data != null) {
      final entities = response.data!.map((CursoDto dto) => dto.toEntity()).toList();
      return DataState<List<Curso>>(data: entities, success: true, statusCode: response.statusCode);
    }
    return DataState<List<Curso>>(
      success: false,
      error: response.error,
      statusCode: response.statusCode,
    );
  }

  @override
  Future<DataState<void>> create(Curso curso) {
    return remoteDatasource.create(CursoDto.fromEntity(curso));
  }
}
