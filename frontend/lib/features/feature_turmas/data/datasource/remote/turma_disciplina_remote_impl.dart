import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_turmas/data/datasource/remote/i_turma_disciplina_remote.dart';
import 'package:ghorario/features/feature_turmas/data/models/item_grade_curricular_dto.dart';

class TurmaDisciplinaRemoteImpl implements ITurmaDisciplinaRemote {
  TurmaDisciplinaRemoteImpl(this._http);

  final IHttpMethods _http;

  DataState<List<ItemGradeCurricularDto>> _parse(DataState<dynamic> response) {
    if (!response.success || response.data == null) {
      return DataState<List<ItemGradeCurricularDto>>(
        success: false,
        error: response.error,
        statusCode: response.statusCode,
      );
    }
    try {
      final dataMap = response.data as Map<String, dynamic>;
      final itens = (dataMap['itens'] as List)
          .map((dynamic e) => ItemGradeCurricularDto.fromJson(e as Map<String, dynamic>))
          .toList();
      return DataState<List<ItemGradeCurricularDto>>(data: itens, success: true, statusCode: response.statusCode);
    } catch (e) {
      return DataState<List<ItemGradeCurricularDto>>(
        success: false,
        error: ServerFailure(message: 'Erro ao processar grade curricular: $e'),
      );
    }
  }

  @override
  Future<DataState<List<ItemGradeCurricularDto>>> obter(int planoCurricularId) async {
    return _parse(await _http.get<dynamic>('/planos-curriculares/$planoCurricularId/disciplinas'));
  }

  @override
  Future<DataState<List<ItemGradeCurricularDto>>> definir(
    int planoCurricularId,
    List<ItemGradeCurricularDto> itens,
  ) async {
    return _parse(
      await _http.post<dynamic>(
        '/planos-curriculares/$planoCurricularId/disciplinas',
        data: {'itens': itens.map((i) => i.toJson()).toList()},
      ),
    );
  }
}
