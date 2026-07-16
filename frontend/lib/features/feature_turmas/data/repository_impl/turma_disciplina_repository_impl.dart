import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_turmas/data/datasource/remote/i_turma_disciplina_remote.dart';
import 'package:ghorario/features/feature_turmas/data/models/item_grade_curricular_dto.dart';
import 'package:ghorario/features/feature_turmas/domain/entities/item_grade_curricular.dart';
import 'package:ghorario/features/feature_turmas/domain/repository/i_turma_disciplina_repository.dart';

class TurmaDisciplinaRepositoryImpl implements ITurmaDisciplinaRepository {
  TurmaDisciplinaRepositoryImpl({required this.remoteDatasource});

  final ITurmaDisciplinaRemote remoteDatasource;

  DataState<List<ItemGradeCurricular>> _toEntityState(DataState<List<ItemGradeCurricularDto>> response) {
    if (response.success && response.data != null) {
      final entities = response.data!.map((ItemGradeCurricularDto dto) => dto.toEntity()).toList();
      return DataState<List<ItemGradeCurricular>>(data: entities, success: true, statusCode: response.statusCode);
    }
    return DataState<List<ItemGradeCurricular>>(
      success: false,
      error: response.error,
      statusCode: response.statusCode,
    );
  }

  @override
  Future<DataState<List<ItemGradeCurricular>>> obter(int turmaId) async {
    return _toEntityState(await remoteDatasource.obter(turmaId));
  }

  @override
  Future<DataState<List<ItemGradeCurricular>>> definir(int turmaId, List<ItemGradeCurricular> itens) async {
    final dtos = itens.map((i) => ItemGradeCurricularDto.fromEntity(i)).toList();
    return _toEntityState(await remoteDatasource.definir(turmaId, dtos));
  }
}
