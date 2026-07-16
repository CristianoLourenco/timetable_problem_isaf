import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_disponibilidade/data/datasource/remote/i_disponibilidade_remote.dart';
import 'package:ghorario/features/feature_disponibilidade/domain/entities/tempo_chave.dart';
import 'package:ghorario/features/feature_disponibilidade/domain/repository/i_disponibilidade_repository.dart';

class DisponibilidadeRepositoryImpl implements IDisponibilidadeRepository {
  DisponibilidadeRepositoryImpl({required this.remoteDatasource});

  final IDisponibilidadeRemote remoteDatasource;

  @override
  Future<DataState<List<TempoChave>>> obter(int professorId) {
    return remoteDatasource.obter(professorId);
  }

  @override
  Future<DataState<List<TempoChave>>> definir(int professorId, List<TempoChave> tempos) {
    return remoteDatasource.definir(professorId, tempos);
  }
}
