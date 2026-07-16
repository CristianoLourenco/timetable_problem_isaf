import 'package:ghorario/core/resources/data_state.dart';

/// Base interface for all use cases.
///
/// Ensures use cases always return a [Future] wrapping a [DataState].
abstract class IUseCase<Types, Params> {
  Future<DataState<Types>> call(Params params);
}
