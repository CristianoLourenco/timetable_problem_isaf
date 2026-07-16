import 'package:ghorario/features/feature_turmas/domain/entities/curso.dart';

const Object _sentinel = Object();

/// State class for the Cursos feature.
class CursosState {
  const CursosState({
    this.cursos = const <Curso>[],
    this.isLoading = false,
    this.errorMessage,
  });

  final List<Curso> cursos;
  final bool isLoading;
  final String? errorMessage;

  CursosState copyWith({
    List<Curso>? cursos,
    bool? isLoading,
    Object? errorMessage = _sentinel,
  }) {
    return CursosState(
      cursos: cursos ?? this.cursos,
      isLoading: isLoading ?? this.isLoading,
      errorMessage: errorMessage == _sentinel ? this.errorMessage : (errorMessage as String?),
    );
  }
}
