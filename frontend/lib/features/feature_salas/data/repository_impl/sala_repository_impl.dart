import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_salas/data/datasource/remote/i_sala_remote.dart';
import 'package:ghorario/features/feature_salas/data/models/sala_dto.dart';
import 'package:ghorario/features/feature_salas/domain/entities/sala.dart';
import 'package:ghorario/features/feature_salas/domain/repository/i_sala_repository.dart';

/// Concrete implementation of [ISalaRepository].
class SalaRepositoryImpl implements ISalaRepository {
  SalaRepositoryImpl({required this.remoteDatasource});

  final ISalaRemote remoteDatasource;

  @override
  Future<DataState<List<Sala>>> getAll() async {
    final response = await remoteDatasource.getAll();
    if (response.success && response.data != null) {
      final entities = response.data!.map((SalaDto dto) => dto.toEntity()).toList();
      return DataState<List<Sala>>(
        data: entities,
        success: true,
        statusCode: response.statusCode,
      );
    }
    return DataState<List<Sala>>(
      success: false,
      error: response.error,
      statusCode: response.statusCode,
    );
  }

  @override
  Future<DataState<Sala>> getById(String id) async {
    final response = await remoteDatasource.getById(id);
    if (response.success && response.data != null) {
      return DataState<Sala>(
        data: response.data!.toEntity(),
        success: true,
        statusCode: response.statusCode,
      );
    }
    return DataState<Sala>(
      success: false,
      error: response.error,
      statusCode: response.statusCode,
    );
  }

  @override
  Future<DataState<void>> create(Sala sala) async {
    return remoteDatasource.create(SalaDto.fromEntity(sala));
  }

  @override
  Future<DataState<void>> update(Sala sala) async {
    return remoteDatasource.update(SalaDto.fromEntity(sala));
  }

  @override
  Future<DataState<void>> delete(String id) async {
    return remoteDatasource.delete(id);
  }
}
