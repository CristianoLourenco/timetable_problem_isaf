import 'package:ghorario/features/feature_horario/domain/entities/horario_slot.dart';

const Object _sentinel = Object();

/// State class for the Horario feature.
class HorarioState {
  const HorarioState({
    this.slots = const <HorarioSlot>[],
    this.isLoading = false,
    this.isGenerating = false,
    this.errorMessage,
    this.currentJobId,
  });

  final List<HorarioSlot> slots;
  final bool isLoading;
  final bool isGenerating;
  final String? errorMessage;
  final String? currentJobId;

  HorarioState copyWith({
    List<HorarioSlot>? slots,
    bool? isLoading,
    bool? isGenerating,
    Object? errorMessage = _sentinel,
    Object? currentJobId = _sentinel,
  }) {
    return HorarioState(
      slots: slots ?? this.slots,
      isLoading: isLoading ?? this.isLoading,
      isGenerating: isGenerating ?? this.isGenerating,
      errorMessage: errorMessage == _sentinel
          ? this.errorMessage
          : (errorMessage as String?),
      currentJobId: currentJobId == _sentinel
          ? this.currentJobId
          : (currentJobId as String?),
    );
  }
}
