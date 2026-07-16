import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_disponibilidade/data/datasource/remote/i_tempo_remote.dart';
import 'package:ghorario/features/feature_disponibilidade/data/models/tempo_dto.dart';
import 'package:ghorario/features/feature_disponibilidade/domain/entities/tempo.dart';
import 'package:ghorario/features/feature_disponibilidade/domain/repository/i_tempo_repository.dart';

class TempoRepositoryImpl implements ITempoRepository {
  TempoRepositoryImpl({required this.remoteDatasource});

  final ITempoRemote remoteDatasource;

  @override
  Future<DataState<List<Tempo>>> getAll() async {
    final response = await remoteDatasource.getAll();
    if (response.success && response.data != null) {
      final entities = response.data!.map((TempoDto dto) => dto.toEntity()).toList();
      return DataState<List<Tempo>>(data: entities, success: true, statusCode: response.statusCode);
    }
    return DataState<List<Tempo>>(success: false, error: response.error, statusCode: response.statusCode);
  }
}
