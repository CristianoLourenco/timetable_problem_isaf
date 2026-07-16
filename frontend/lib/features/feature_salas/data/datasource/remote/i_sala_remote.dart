import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_salas/data/models/sala_dto.dart';

/// Abstract remote datasource interface for Salas.
abstract class ISalaRemote {
  Future<DataState<List<SalaDto>>> getAll();
  Future<DataState<SalaDto>> getById(String id);
  Future<DataState<void>> create(SalaDto dto);
  Future<DataState<void>> update(SalaDto dto);
  Future<DataState<void>> delete(String id);
}
