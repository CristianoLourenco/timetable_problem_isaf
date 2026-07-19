import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_horario/domain/entities/professor_qualificado.dart';
import 'package:ghorario/features/feature_horario/domain/repository/i_horario_repository.dart';

class GetProfessoresQualificadosParams {
  const GetProfessoresQualificadosParams({
    required this.turmaId,
    required this.disciplinaId,
  });

  final String turmaId;
  final String disciplinaId;
}

/// Use case to fetch qualified teachers for a specific class (turma) and subject (disciplina).
class GetProfessoresQualificadosUseCase implements IUseCase<List<ProfessorQualificado>, GetProfessoresQualificadosParams> {
  GetProfessoresQualificadosUseCase(this._repository);

  final IHorarioRepository _repository;

  @override
  Future<DataState<List<ProfessorQualificado>>> call(GetProfessoresQualificadosParams params) {
    return _repository.getProfessoresQualificados(params.turmaId, params.disciplinaId);
  }
}
