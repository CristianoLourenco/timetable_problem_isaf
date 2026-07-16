import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_docentes/data/datasource/remote/i_professor_disciplina_remote.dart';
import 'package:ghorario/features/feature_docentes/domain/repository/i_professor_disciplina_repository.dart';

class ProfessorDisciplinaRepositoryImpl implements IProfessorDisciplinaRepository {
  ProfessorDisciplinaRepositoryImpl({required this.remoteDatasource});

  final IProfessorDisciplinaRemote remoteDatasource;

  @override
  Future<DataState<List<int>>> obter(int professorId) {
    return remoteDatasource.obter(professorId);
  }

  @override
  Future<DataState<List<int>>> definir(int professorId, List<int> disciplinaIds) {
    return remoteDatasource.definir(professorId, disciplinaIds);
  }
}
