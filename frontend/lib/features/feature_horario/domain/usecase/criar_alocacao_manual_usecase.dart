import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_horario/domain/entities/alocacao_manual_response.dart';
import 'package:ghorario/features/feature_horario/domain/repository/i_horario_repository.dart';

class CriarAlocacaoManualParams {
  const CriarAlocacaoManualParams({
    required this.jobId,
    required this.turmaId,
    required this.disciplinaId,
    required this.professorId,
    required this.salaId,
    required this.diaSemana,
    required this.turno,
    required this.periodos,
  });

  final String jobId;
  final String turmaId;
  final String disciplinaId;
  final String professorId;
  final String salaId;
  final String diaSemana;
  final String turno;
  final List<int> periodos;
}

/// Use case to submit a new manual allocation mapping.
class CriarAlocacaoManualUseCase implements IUseCase<List<AlocacaoManualResponse>, CriarAlocacaoManualParams> {
  CriarAlocacaoManualUseCase(this._repository);

  final IHorarioRepository _repository;

  @override
  Future<DataState<List<AlocacaoManualResponse>>> call(CriarAlocacaoManualParams params) {
    return _repository.criarAlocacaoManual(
      jobId: params.jobId,
      turmaId: params.turmaId,
      disciplinaId: params.disciplinaId,
      professorId: params.professorId,
      salaId: params.salaId,
      diaSemana: params.diaSemana,
      turno: params.turno,
      periodos: params.periodos,
    );
  }
}
