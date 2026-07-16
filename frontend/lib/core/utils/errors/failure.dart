import 'package:ghorario/core/utils/errors/i_exception_error.dart';

/// Base class for structured failure representation, implementing [IExceptionError].
abstract class Failure implements IExceptionError {
  const Failure({required this.message, this.statusCode});

  @override
  final String message;

  @override
  final int? statusCode;

  @override
  String toString() => '$runtimeType: $message';
}

/// Failure originating from remote server (API / Firebase).
class ServerFailure extends Failure {
  const ServerFailure({required super.message, super.statusCode});
}

/// Failure originating from local cache or storage.
class CacheFailure extends Failure {
  const CacheFailure({required super.message});
}

/// Failure due to invalid user input or business rule violation.
class ValidationFailure extends Failure {
  const ValidationFailure({required super.message});
}
