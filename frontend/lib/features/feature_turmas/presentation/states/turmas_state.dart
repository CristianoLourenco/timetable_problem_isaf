import 'package:ghorario/features/feature_turmas/domain/entities/turma.dart';

const Object _sentinel = Object();

/// State class for the Turmas feature.
class TurmasState {
  const TurmasState({
    this.turmas = const <Turma>[],
    this.isLoading = false,
    this.errorMessage,
  });

  final List<Turma> turmas;
  final bool isLoading;
  final String? errorMessage;

  TurmasState copyWith({
    List<Turma>? turmas,
    bool? isLoading,
    Object? errorMessage = _sentinel,
  }) {
    return TurmasState(
      turmas: turmas ?? this.turmas,
      isLoading: isLoading ?? this.isLoading,
      errorMessage: errorMessage == _sentinel
          ? this.errorMessage
          : (errorMessage as String?),
    );
  }
}
