import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_disponibilidade/domain/entities/tempo_chave.dart';

/// Abstract remote datasource for `/professores/{id}/disponibilidade` (RF05).
abstract class IDisponibilidadeRemote {
  Future<DataState<List<TempoChave>>> obter(int professorId);
  Future<DataState<List<TempoChave>>> definir(int professorId, List<TempoChave> tempos);
}
