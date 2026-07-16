import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_docentes/data/datasource/remote/i_professor_disciplina_remote.dart';

class ProfessorDisciplinaRemoteImpl implements IProfessorDisciplinaRemote {
  ProfessorDisciplinaRemoteImpl(this._http);

  final IHttpMethods _http;

  DataState<List<int>> _parse(DataState<dynamic> response) {
    if (!response.success || response.data == null) {
      return DataState<List<int>>(success: false, error: response.error, statusCode: response.statusCode);
    }
    try {
      final dataMap = response.data as Map<String, dynamic>;
      final ids = (dataMap['disciplina_ids'] as List).cast<int>();
      return DataState<List<int>>(data: ids, success: true, statusCode: response.statusCode);
    } catch (e) {
      return DataState<List<int>>(
        success: false,
        error: ServerFailure(message: 'Erro ao processar qualificação docente: $e'),
      );
    }
  }

  @override
  Future<DataState<List<int>>> obter(int professorId) async {
    return _parse(await _http.get<dynamic>('/professores/$professorId/disciplinas'));
  }

  @override
  Future<DataState<List<int>>> definir(int professorId, List<int> disciplinaIds) async {
    return _parse(
      await _http.post<dynamic>(
        '/professores/$professorId/disciplinas',
        data: {'disciplina_ids': disciplinaIds},
      ),
    );
  }
}
