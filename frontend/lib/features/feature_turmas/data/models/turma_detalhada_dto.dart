import 'package:ghorario/features/feature_turmas/data/models/turma_dto.dart';
import 'package:ghorario/features/feature_turmas/domain/entities/turma_detalhada.dart';

/// DTO for `TurmaDetalhadaSchema` (`GET /turmas-detalhadas`): all [TurmaDto]
/// fields plus curso_codigo, curso_nome, ano_curricular, semestre.
class TurmaDetalhadaDto {
  const TurmaDetalhadaDto({
    required this.turma,
    required this.cursoCodigo,
    required this.cursoNome,
    required this.anoCurricular,
    required this.semestre,
  });

  final TurmaDto turma;
  final String cursoCodigo;
  final String cursoNome;
  final int anoCurricular;
  final String semestre;

  factory TurmaDetalhadaDto.fromJson(Map<String, dynamic> json) {
    return TurmaDetalhadaDto(
      turma: TurmaDto.fromJson(json),
      cursoCodigo: json['curso_codigo'] as String? ?? '',
      cursoNome: json['curso_nome'] as String? ?? '',
      anoCurricular: json['ano_curricular'] as int? ?? 0,
      semestre: json['semestre'] as String? ?? '',
    );
  }

  TurmaDetalhada toEntity() {
    return TurmaDetalhada(
      turma: turma.toEntity(),
      cursoCodigo: cursoCodigo,
      cursoNome: cursoNome,
      anoCurricular: anoCurricular,
      semestre: semestre,
    );
  }
}
