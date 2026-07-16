import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_disponibilidade/domain/entities/tempo.dart';

abstract class ITempoRepository {
  Future<DataState<List<Tempo>>> getAll();
}
