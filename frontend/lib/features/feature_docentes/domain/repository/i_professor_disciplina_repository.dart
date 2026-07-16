import 'package:ghorario/core/core.dart';

abstract class IProfessorDisciplinaRepository {
  Future<DataState<List<int>>> obter(int professorId);
  Future<DataState<List<int>>> definir(int professorId, List<int> disciplinaIds);
}
