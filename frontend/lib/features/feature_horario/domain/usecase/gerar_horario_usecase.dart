import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_horario/domain/repository/i_horario_repository.dart';

/// Params for [GerarHorarioUseCase] — âmbito da geração (RF09): o horário
/// completo de todas as turmas de um único curso/ano lectivo/semestre, de
/// uma vez. cursoId é obrigatório — gerar vários cursos em simultâneo pode
/// ser genuinamente INFEASIBLE (coortes pequenas partilham corpo docente
/// entre turmas paralelas do mesmo curso) além de não fazer sentido otimizar
/// juntos cursos que não partilham turmas/grade curricular entre si.
class GerarHorarioParams {
  const GerarHorarioParams({required this.cursoId, required this.anoLetivo, required this.semestre});

  final String cursoId;
  final int anoLetivo;
  final String semestre;
}

/// Use case to trigger the timetable generation process.
class GerarHorarioUseCase implements IUseCase<String, GerarHorarioParams> {
  GerarHorarioUseCase(this._repository);

  final IHorarioRepository _repository;

  @override
  Future<DataState<String>> call(GerarHorarioParams params) {
    return _repository.triggerGeneration(
      cursoId: params.cursoId,
      anoLetivo: params.anoLetivo,
      semestre: params.semestre,
    );
  }
}
