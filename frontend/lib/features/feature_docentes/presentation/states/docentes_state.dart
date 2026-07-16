import 'package:ghorario/features/feature_docentes/domain/entities/docente.dart';

const Object _sentinel = Object();

/// State class for the Docentes feature.
///
/// Immutable class employing the Sentinel Pattern to handle nullable fields correctly.
class DocentesState {
  const DocentesState({
    this.docentes = const <Docente>[],
    this.isLoading = false,
    this.errorMessage,
  });

  final List<Docente> docentes;
  final bool isLoading;
  final String? errorMessage;

  DocentesState copyWith({
    List<Docente>? docentes,
    bool? isLoading,
    Object? errorMessage = _sentinel,
  }) {
    return DocentesState(
      docentes: docentes ?? this.docentes,
      isLoading: isLoading ?? this.isLoading,
      errorMessage: errorMessage == _sentinel
          ? this.errorMessage
          : (errorMessage as String?),
    );
  }
}
