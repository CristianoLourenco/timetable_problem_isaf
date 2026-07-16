import 'package:ghorario/features/feature_disponibilidade/domain/entities/tempo.dart';
import 'package:ghorario/features/feature_disponibilidade/domain/entities/tempo_chave.dart';

const Object _sentinel = Object();

/// State class for the Disponibilidade feature.
class DisponibilidadeState {
  const DisponibilidadeState({
    this.tempos = const <Tempo>[],
    this.selectedTempos = const <TempoChave>{},
    this.isLoading = false,
    this.isSaving = false,
    this.errorMessage,
  });

  final List<Tempo> tempos;
  final Set<TempoChave> selectedTempos;
  final bool isLoading;
  final bool isSaving;
  final String? errorMessage;

  DisponibilidadeState copyWith({
    List<Tempo>? tempos,
    Set<TempoChave>? selectedTempos,
    bool? isLoading,
    bool? isSaving,
    Object? errorMessage = _sentinel,
  }) {
    return DisponibilidadeState(
      tempos: tempos ?? this.tempos,
      selectedTempos: selectedTempos ?? this.selectedTempos,
      isLoading: isLoading ?? this.isLoading,
      isSaving: isSaving ?? this.isSaving,
      errorMessage: errorMessage == _sentinel ? this.errorMessage : (errorMessage as String?),
    );
  }
}
