/// Base interface for all typed exceptions/errors in the system.
abstract class IExceptionError implements Exception {
  String get message;
  int? get statusCode;
}

/// Error representing network connectivity issues.
class NetworkError implements IExceptionError {
  const NetworkError({
    this.message = 'Sem conexão à internet. Verifique a sua rede.',
    this.statusCode,
  });

  @override
  final String message;
  @override
  final int? statusCode;
}

/// Error representing a general server failure (5xx status code, etc.).
class ServerError implements IExceptionError {
  const ServerError({
    required this.message,
    this.statusCode,
  });

  @override
  final String message;
  @override
  final int? statusCode;
}

/// Error representing resource not found (404 status code).
class NotFoundError implements IExceptionError {
  const NotFoundError({
    this.message = 'Recurso não encontrado.',
    this.statusCode = 404,
  });

  @override
  final String message;
  @override
  final int? statusCode;
}

/// Error representing connection timeout.
class TimeoutError implements IExceptionError {
  const TimeoutError({
    this.message = 'Tempo limite de ligação esgotado. Tente novamente.',
    this.statusCode,
  });

  @override
  final String message;
  @override
  final int? statusCode;
}

/// Error representing authentication/authorization issues (401/403 status code).
class UnauthorizedError implements IExceptionError {
  const UnauthorizedError({
    this.message = 'Não autorizado. Por favor, inicie sessão novamente.',
    this.statusCode = 401,
  });

  @override
  final String message;
  @override
  final int? statusCode;
}

/// Error representing too many requests (429 status code).
class ManyTriesError implements IExceptionError {
  const ManyTriesError({
    this.message = 'Demasiadas tentativas. Por favor, aguarde um momento.',
    this.statusCode = 429,
  });

  @override
  final String message;
  @override
  final int? statusCode;
}

/// Fallback error representing unknown/unhandled issues.
class UnknownError implements IExceptionError {
  const UnknownError({
    required this.message,
    this.statusCode,
  });

  @override
  final String message;
  @override
  final int? statusCode;
}
