import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_turmas/domain/entities/turma_detalhada.dart';
import 'package:ghorario/features/feature_turmas/domain/repository/i_turma_repository.dart';

/// Parameters for [GetTurmasDetalhadasUseCase] — both optional; when both are
/// omitted, behaves like [GetAllTurmasUseCase] but with the extra fields.
class GetTurmasDetalhadasParams {
  const GetTurmasDetalhadasParams({this.anoLetivo, this.semestre});

  final int? anoLetivo;
  final String? semestre;
}

/// RF02 — turmas filtradas por âmbito (ano letivo/semestre) para ecrãs onde
/// listar TODAS as turmas (ver [GetAllTurmasUseCase]) esconderia o facto de
/// não haver Job gerado para o âmbito atual (ver HorarioScreen).
class GetTurmasDetalhadasUseCase implements IUseCase<List<TurmaDetalhada>, GetTurmasDetalhadasParams> {
  GetTurmasDetalhadasUseCase(this._repository);

  final ITurmaRepository _repository;

  @override
  Future<DataState<List<TurmaDetalhada>>> call(GetTurmasDetalhadasParams params) {
    return _repository.getDetalhadas(anoLetivo: params.anoLetivo, semestre: params.semestre);
  }
}
