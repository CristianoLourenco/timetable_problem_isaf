import 'package:ghorario/core/utils/errors/i_exception_error.dart';

/// Generic response wrapper for data transactions.
///
/// Encapsulates either the success data or the error details.
class DataState<T> implements IExceptionError {
  DataState({
    this.data,
    this.error,
    String? message,
    this.statusCode,
    required this.success,
  }) : message = message ?? error?.message ?? '';

  final T? data;
  final bool success;
  final IExceptionError? error;

  @override
  final String message;

  @override
  final int? statusCode;
}
