class EntidadeNaoEncontradaError(Exception):
    """Registo não encontrado (404)."""


class IntegridadeVioladaError(Exception):
    """Violação de chave única ou de referência (409) — ex: código duplicado, curso_id inexistente."""


class TokenInvalidoError(Exception):
    """RN09 — ID Token Firebase ausente, inválido ou expirado (401)."""


class AcessoNegadoError(Exception):
    """RN10, RN11 — papel sem permissão para o recurso pedido, ou email sem correspondência (403)."""
