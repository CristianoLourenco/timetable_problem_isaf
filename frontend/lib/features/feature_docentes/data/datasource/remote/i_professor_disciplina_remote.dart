import 'package:ghorario/core/core.dart';

/// Abstract remote datasource for `/professores/{id}/disciplinas` (qualificação docente).
abstract class IProfessorDisciplinaRemote {
  Future<DataState<List<int>>> obter(int professorId);
  Future<DataState<List<int>>> definir(int professorId, List<int> disciplinaIds);
}
