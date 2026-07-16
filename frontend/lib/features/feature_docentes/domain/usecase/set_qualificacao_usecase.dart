import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_docentes/domain/repository/i_professor_disciplina_repository.dart';

class SetQualificacaoParams {
  const SetQualificacaoParams({required this.professorId, required this.disciplinaIds});

  final int professorId;
  final List<int> disciplinaIds;
}

class SetQualificacaoUseCase implements IUseCase<List<int>, SetQualificacaoParams> {
  SetQualificacaoUseCase(this._repository);

  final IProfessorDisciplinaRepository _repository;

  @override
  Future<DataState<List<int>>> call(SetQualificacaoParams params) {
    return _repository.definir(params.professorId, params.disciplinaIds);
  }
}
