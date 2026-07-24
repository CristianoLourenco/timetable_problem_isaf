# Implementa: RF03 — nome curto de Disciplina (ver app/core/abreviacoes.py)
from app.core.abreviacoes import gerar_nome_curto
from app.models.disciplina import Disciplina


def test_gerar_nome_curto_varias_palavras_usa_iniciais():
    assert gerar_nome_curto("Comunicação Pessoal e Empresarial") == "CPE"
    assert gerar_nome_curto("Contabilidade Geral I") == "CG I"


def test_gerar_nome_curto_ignora_preposicoes_e_artigos():
    assert gerar_nome_curto("Introdução às Organizações e à Gestão") == "IOG"
    assert gerar_nome_curto("Base de Dados I") == "BD I"


def test_gerar_nome_curto_uma_so_palavra_significativa_usa_prefixo_nao_inicial():
    """Bug real evitado: Macroeconomia/Marketing/Matemática/Microeconomia I
    geravam todas 'MI' (mesma inicial + numeral) — colisão real entre
    disciplinas distintas do currículo do ISAF."""
    assert gerar_nome_curto("Macroeconomia I") == "MACRO I"
    assert gerar_nome_curto("Marketing I") == "MARKE I"
    assert gerar_nome_curto("Matemática I") == "MATEM I"
    assert gerar_nome_curto("Microeconomia I") == "MICRO I"

    curtos = {
        gerar_nome_curto(n)
        for n in ["Macroeconomia I", "Marketing I", "Matemática I", "Microeconomia I"]
    }
    assert len(curtos) == 4  # nenhuma colisão


def test_gerar_nome_curto_numeral_romano_nao_se_funde_com_a_sigla():
    """Bug real evitado: sem separador, 'Língua Inglesa III' virava 'LIIII'
    (o 'I' de "Inglesa" fundido com o numeral III) — ilegível."""
    assert gerar_nome_curto("Língua Inglesa I") == "LI I"
    assert gerar_nome_curto("Língua Inglesa II") == "LI II"
    assert gerar_nome_curto("Língua Inglesa III") == "LI III"
    assert gerar_nome_curto("Língua Inglesa IV") == "LI IV"


def test_gerar_nome_curto_respeita_tamanho_maximo():
    resultado = gerar_nome_curto("Gestão de Activos, Passivos e Fundos de Pensões", tamanho_maximo=12)
    assert len(resultado) <= 12


def test_disciplina_gera_nome_curto_automaticamente_quando_omitido():
    disciplina = Disciplina(codigo="MAT001", nome="Matemática I")
    assert disciplina.nome_curto == "MATEM I"


def test_disciplina_respeita_nome_curto_fornecido_manualmente():
    """Gestor pode substituir o valor automático quando ficar confuso."""
    disciplina = Disciplina(codigo="MAT002", nome="Matemática II", nome_curto="M2")
    assert disciplina.nome_curto == "M2"
