# Implementa: RF03 — nome curto de Disciplina para a grelha de horário (espaço
# reduzido nas células), gerado automaticamente mas editável pelo Gestor.
#
# Regra: iniciais das palavras significativas (ignora artigos/preposições
# curtas: de, da, do, das, dos, e, à, ao, em, na, no, para, com), preservando
# numeração romana/algarismo no fim (ex: "Contabilidade Geral I" -> "CGI",
# "Introdução à Economia" -> "IE"). Consistente e determinística — nunca
# copia abreviaturas dos exemplares reais do ISAF, que variam por curso.
import re
import unicodedata

_PALAVRAS_IGNORADAS = {
    "de", "da", "do", "das", "dos", "e", "a", "as", "ao", "aos", "em", "na",
    "no", "nas", "nos", "para", "com",
}
_NUMERAIS_ROMANOS = {"i", "ii", "iii", "iv", "v"}


def _sem_acentos(texto: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn")


def gerar_nome_curto(nome: str, tamanho_maximo: int = 12) -> str:
    """Gera um nome curto determinístico a partir do nome completo da disciplina.

    Só uma palavra significativa (ex: "Matemática I", "Macroeconomia I") — as
    iniciais colidiriam entre disciplinas distintas (Macroeconomia/Marketing/
    Matemática/Microeconomia I geravam todas "MI") — usa um prefixo de 3-5
    letras dessa palavra em vez de uma única inicial. Duas ou mais palavras
    significativas continuam a usar iniciais (ex: "Contabilidade Geral I" ->
    "CGI"), onde a colisão é rara."""
    palavras = re.findall(r"[A-Za-zÀ-ÿ]+", nome)
    if not palavras:
        return nome[:tamanho_maximo]

    numerais: list[str] = []
    significativas: list[str] = []
    for palavra in palavras:
        minuscula = _sem_acentos(palavra.lower())
        if minuscula in _NUMERAIS_ROMANOS or palavra.isdigit():
            numerais.append(palavra.upper())
        elif minuscula not in _PALAVRAS_IGNORADAS:
            significativas.append(palavra)

    sufixo_numeral = f" {' '.join(numerais)}" if numerais else ""  # espaço separa sigla do numeral
    # sem isto, "Língua Inglesa III" virava "LIIII" (I da palavra + III do
    # numeral fundidos, ilegível) — mesmo problema em qualquer disciplina cuja
    # última inicial coincida com "I"/"V".
    if len(significativas) == 1:
        palavra = significativas[0]
        tamanho_prefixo = min(5, max(3, tamanho_maximo - len(sufixo_numeral)))
        resultado = _sem_acentos(palavra)[:tamanho_prefixo].upper() + sufixo_numeral
    else:
        resultado = "".join(p[0].upper() for p in significativas) + sufixo_numeral

    return resultado[:tamanho_maximo] if resultado else nome[:tamanho_maximo]
