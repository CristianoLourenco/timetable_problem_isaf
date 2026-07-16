import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_disponibilidade/domain/entities/tempo_chave.dart';

abstract class IDisponibilidadeRepository {
  Future<DataState<List<TempoChave>>> obter(int professorId);
  Future<DataState<List<TempoChave>>> definir(int professorId, List<TempoChave> tempos);
}
