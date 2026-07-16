import 'package:ghorario/features/feature_salas/domain/entities/sala.dart';

const Object _sentinel = Object();

/// State class for the Salas feature.
class SalasState {
  const SalasState({
    this.salas = const <Sala>[],
    this.isLoading = false,
    this.errorMessage,
  });

  final List<Sala> salas;
  final bool isLoading;
  final String? errorMessage;

  SalasState copyWith({
    List<Sala>? salas,
    bool? isLoading,
    Object? errorMessage = _sentinel,
  }) {
    return SalasState(
      salas: salas ?? this.salas,
      isLoading: isLoading ?? this.isLoading,
      errorMessage: errorMessage == _sentinel
          ? this.errorMessage
          : (errorMessage as String?),
    );
  }
}
