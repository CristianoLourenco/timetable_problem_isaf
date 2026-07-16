import 'package:ghorario/core/core.dart';
import 'package:ghorario/core/enums/dia_semana.dart';
import 'package:ghorario/core/enums/turno.dart';
import 'package:ghorario/features/feature_disponibilidade/data/datasource/remote/i_disponibilidade_remote.dart';
import 'package:ghorario/features/feature_disponibilidade/domain/entities/tempo_chave.dart';

class DisponibilidadeRemoteImpl implements IDisponibilidadeRemote {
  DisponibilidadeRemoteImpl(this._http);

  final IHttpMethods _http;

  Map<String, dynamic> _toJson(TempoChave tempo) => {
        'dia_semana': tempo.diaSemana.apiValue,
        'turno': tempo.turno.apiValue,
        'periodo': tempo.periodo,
      };

  TempoChave _fromJson(Map<String, dynamic> json) => TempoChave(
        diaSemana: DiaSemana.fromApi(json['dia_semana'] as String? ?? ''),
        turno: Turno.fromApi(json['turno'] as String?) ?? Turno.manha,
        periodo: json['periodo'] as int? ?? 0,
      );

  DataState<List<TempoChave>> _parse(DataState<dynamic> response) {
    if (!response.success || response.data == null) {
      return DataState<List<TempoChave>>(success: false, error: response.error, statusCode: response.statusCode);
    }
    try {
      final dataMap = response.data as Map<String, dynamic>;
      final tempos = (dataMap['tempos'] as List)
          .map((dynamic e) => _fromJson(e as Map<String, dynamic>))
          .toList();
      return DataState<List<TempoChave>>(data: tempos, success: true, statusCode: response.statusCode);
    } catch (e) {
      return DataState<List<TempoChave>>(
        success: false,
        error: ServerFailure(message: 'Erro ao processar disponibilidade: $e'),
      );
    }
  }

  @override
  Future<DataState<List<TempoChave>>> obter(int professorId) async {
    return _parse(await _http.get<dynamic>('/professores/$professorId/disponibilidade'));
  }

  @override
  Future<DataState<List<TempoChave>>> definir(int professorId, List<TempoChave> tempos) async {
    return _parse(
      await _http.post<dynamic>(
        '/professores/$professorId/disponibilidade',
        data: {'tempos': tempos.map(_toJson).toList()},
      ),
    );
  }
}
