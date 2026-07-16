import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_disponibilidade/data/models/tempo_dto.dart';

abstract class ITempoRemote {
  Future<DataState<List<TempoDto>>> getAll();
}
