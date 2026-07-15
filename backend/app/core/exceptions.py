class EntidadeNaoEncontradaError(Exception):
    """Registo não encontrado (404)."""


class IntegridadeVioladaError(Exception):
    """Violação de chave única ou de referência (409) — ex: código duplicado, curso_id inexistente."""
