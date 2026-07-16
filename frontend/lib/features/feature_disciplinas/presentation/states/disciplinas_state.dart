import 'package:ghorario/features/feature_disciplinas/domain/entities/disciplina.dart';

const Object _sentinel = Object();

/// State class for the Disciplinas feature.
class DisciplinasState {
  const DisciplinasState({
    this.disciplinas = const <Disciplina>[],
    this.isLoading = false,
    this.errorMessage,
  });

  final List<Disciplina> disciplinas;
  final bool isLoading;
  final String? errorMessage;

  DisciplinasState copyWith({
    List<Disciplina>? disciplinas,
    bool? isLoading,
    Object? errorMessage = _sentinel,
  }) {
    return DisciplinasState(
      disciplinas: disciplinas ?? this.disciplinas,
      isLoading: isLoading ?? this.isLoading,
      errorMessage: errorMessage == _sentinel
          ? this.errorMessage
          : (errorMessage as String?),
    );
  }
}
