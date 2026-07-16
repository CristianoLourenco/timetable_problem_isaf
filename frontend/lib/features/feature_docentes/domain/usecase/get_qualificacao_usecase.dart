import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_docentes/domain/repository/i_professor_disciplina_repository.dart';

class GetQualificacaoUseCase implements IUseCase<List<int>, int> {
  GetQualificacaoUseCase(this._repository);

  final IProfessorDisciplinaRepository _repository;

  @override
  Future<DataState<List<int>>> call(int professorId) {
    return _repository.obter(professorId);
  }
}
