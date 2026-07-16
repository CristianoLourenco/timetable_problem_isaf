import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_docentes/data/datasource/remote/i_docente_remote.dart';
import 'package:ghorario/features/feature_docentes/data/models/docente_dto.dart';
import 'package:ghorario/features/feature_docentes/domain/entities/docente.dart';
import 'package:ghorario/features/feature_docentes/domain/repository/i_docente_repository.dart';

/// Concrete implementation of [IDocenteRepository].
class DocenteRepositoryImpl implements IDocenteRepository {
  DocenteRepositoryImpl({required this.remoteDatasource});

  final IDocenteRemote remoteDatasource;

  @override
  Future<DataState<List<Docente>>> getAll() async {
    final response = await remoteDatasource.getAll();
    if (response.success && response.data != null) {
      final entities = response.data!.map((DocenteDto dto) => dto.toEntity()).toList();
      return DataState<List<Docente>>(
        data: entities,
        success: true,
        statusCode: response.statusCode,
      );
    }
    return DataState<List<Docente>>(
      success: false,
      error: response.error,
      statusCode: response.statusCode,
    );
  }

  @override
  Future<DataState<Docente>> getById(String id) async {
    final response = await remoteDatasource.getById(id);
    if (response.success && response.data != null) {
      return DataState<Docente>(
        data: response.data!.toEntity(),
        success: true,
        statusCode: response.statusCode,
      );
    }
    return DataState<Docente>(
      success: false,
      error: response.error,
      statusCode: response.statusCode,
    );
  }

  @override
  Future<DataState<void>> create(Docente docente) async {
    return remoteDatasource.create(DocenteDto.fromEntity(docente));
  }

  @override
  Future<DataState<void>> update(Docente docente) async {
    return remoteDatasource.update(DocenteDto.fromEntity(docente));
  }

  @override
  Future<DataState<void>> delete(String id) async {
    return remoteDatasource.delete(id);
  }
}
