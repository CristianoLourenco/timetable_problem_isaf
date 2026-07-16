import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_salas/domain/entities/sala.dart';

/// Abstract repository interface for the Salas feature.
abstract class ISalaRepository {
  Future<DataState<List<Sala>>> getAll();
  Future<DataState<Sala>> getById(String id);
  Future<DataState<void>> create(Sala sala);
  Future<DataState<void>> update(Sala sala);
  Future<DataState<void>> delete(String id);
}
