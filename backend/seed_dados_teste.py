"""Popula a base de dados com o currículo REAL do ISAF (Instituto Superior de
Administração e Finanças) — cursos, disciplinas, professores, turmas e turnos
extraídos diretamente dos horários oficiais em `docs/exemplar_isaf/` (1º e 2º
semestre, todos os anos, todos os cursos). Não semeia Alocacao (o horário é
gerado pelo utilizador via POST /gerar-horario depois de correr este script).

Convenção de nomenclatura de turma (igual à usada pelo ISAF, ver
`docs/exemplar_isaf/README.md`): "<letra do turno><número>", ex. "N1", "T2",
"M3" — a letra indica o turno (N=Noite, T=Tarde, M=Manhã) e o número distingue
turmas paralelas do mesmo curso/ano/semestre/turno (várias turmas do mesmo ano
podem ter aulas em turnos diferentes, ou o mesmo turno em salas diferentes).

Onde a mesma disciplina é lecionada por professores diferentes consoante o
curso (situação real, confirmada nos PDFs — ex. "Cálculo e Operações
Financeiras" tem 3 docentes diferentes consoante o curso), todos ficam
registados como qualificados (ProfessorDisciplina) — é o solver que escolhe,
nunca uma atribuição fixa no plano curricular.

Cria também contas de teste reais no Firebase Authentication (mesma REST API
que o backend já usa em core/firebase_rest.py):

  Gestor:     gestor.teste@isaf.co.ao      / Isaf@2026
  Professor:  ricardo.manuel@isaf.co.ao    / Isaf@2026  (Programação I/II)
  Professor:  domingos.kiala@isaf.co.ao    / Isaf@2026  (Contabilidade Geral I/II)
  Professor:  ana.ferreira@isaf.co.ao      / Isaf@2026  (Língua Inglesa I/II)

Uso: python seed_dados_teste.py
"""

import random
import re
import unicodedata

from sqlmodel import Session, select

from app.core import firebase_rest
from app.core.calendario import TurnoEnum
from app.core.database import engine
from app.models.curso import Curso
from app.models.disciplina import Disciplina
from app.models.disponibilidade import Disponibilidade
from app.models.plano_curricular import PlanoCurricular
from app.models.plano_curricular_disciplina import PlanoCurricularDisciplina
from app.models.professor import Professor
from app.models.professor_disciplina import ProfessorDisciplina
from app.models.sala import Sala
from app.models.turma import Turma
from app.models.utilizador import PerfilUtilizador, Utilizador

random.seed(42)

SENHA_TESTE = "Isaf@2026"
ANO_LETIVO = 2026

CURSOS = {
    "IGF": "Informática de Gestão Financeira",
    "CF": "Contabilidade e Finanças",
    "GBS": "Gestão Bancária e de Seguros",
}

_TURNO_POR_PREFIXO = {"N": TurnoEnum.NOITE, "T": TurnoEnum.TARDE, "M": TurnoEnum.MANHA}

# Salas reais observadas nos horários — capacidade estimada (não consta dos PDFs).
# As turmas paralelas de cada (curso,ano,semestre) — só uma foi amostrada dos
# PDFs — decerto usam salas físicas distintas das aqui listadas (que só cobrem
# a turma amostrada); as adicionais "S.1X"/"SC1X" preenchem essa lacuna de
# amostragem para não criar um estrangulamento artificial de salas que não
# existe na realidade (o ISAF já corre estas ~86 turmas em paralelo).
SALAS = {
    "S.01": 40, "S.02": 40, "S.03": 45, "S.06": 35, "S.08": 40, "S.09": 40,
    "S.12": 35, "S.13": 35, "S.15": 45, "SC2": 30, "SC4": 40, "SC7": 40,
    "SC21": 50, "2C2": 60,
    **{f"S.1{n}": 35 for n in range(6)},
    **{f"SC1{n}": 40 for n in range(6)},
    "ANF-A": 100, "ANF-B": 80,
}

# curso -> ano -> semestre -> {"turmas": [...codigos], "disciplinas": [(nome, carga, [profs])]}
# Dados extraídos de docs/exemplar_isaf/ (uma turma amostrada por (curso,ano,semestre);
# grade curricular partilhada por todas as turmas paralelas desse mesmo âmbito).
CURRICULO = {
    "IGF": {
        1: {
            "1": {
                "turmas": ["N1", "T1", "T2", "T3"],
                "disciplinas": [
                    ("Comunicação Pessoal e Empresarial", 4, ["MSc. Artur Santos", "MSc. Youran Mandonga", "MSc. Mateus Halaiwa"]),
                    ("Matemática I", 6, ["Dr. Benedito Pinheiro", "MSc. Jaime Jerónimo"]),
                    ("Fundamentos de Sistemas de Informação", 6, ["MSc. Bernardo António", "Eng. Luís Henriques Fernandes", "MSc. Euclides Catumbela"]),
                    ("Língua Inglesa I", 4, ["MSc. António Vueba", "Dr. Manuel Pedro", "Dr. Ava Pinto", "Dr. Anibal Pululo"]),
                    ("Métodos de Investigação Científica", 4, ["Professora Doutora Martha Nyanungo", "Doutor Dácia Joaquim", "Doutor Alice Costa"]),
                ],
            },
            "2": {
                "turmas": ["N1", "T1", "T2", "T3"],
                "disciplinas": [
                    ("Introdução às Organizações e à Gestão", 4, ["MSc. Bernardo António", "Eng. Luís Henriques Fernandes"]),
                    ("Arquitetura de Computadores", 4, ["Eng. Odeir Fortunato", "Eng. Eduardo Chiquete"]),
                    ("Contabilidade Geral I", 6, ["MSc. Cláudio Voza", "MSc. Joaquim Baltazar", "Dr. Isabel Almeida"]),
                    ("Matemática II", 6, ["Dr. Benedito Pinheiro", "MSc. Jaime Jerónimo"]),
                    ("Língua Inglesa II", 4, ["MSc. António Vueba", "Dr. Manuel Pedro", "Dr. Francisco Cachivalela", "Dr. Anibal Pululo"]),
                ],
            },
        },
        2: {
            "1": {
                "turmas": ["N1", "T1", "T2"],
                "disciplinas": [
                    ("Cálculo e Operações Financeiras", 4, ["Dr. Vander Nascimento", "MSc. Deolinda Cahando", "Dr. Flávio Mendes"]),
                    ("Introdução à Economia", 4, ["MSc. Miguel Troco"]),
                    ("Sistemas Digitais", 4, ["Eng. Odeir Fortunato", "Dr. Wilson Paiva"]),
                    ("Programação I", 6, ["Dr. Edson Tomás", "Dr. Lukau Garcia"]),
                    ("Contabilidade Geral II", 6, ["MSc. Cláudio Voza", "Dr. Isabel Almeida", "MSc. Catarina Júlio"]),
                ],
            },
            "2": {
                "turmas": ["N1", "T1"],
                "disciplinas": [
                    ("Probabilidades e Estatística", 4, ["MSc. Singa Mateus"]),
                    ("Base de Dados I", 4, ["MSc. Lírio Ramalheira"]),
                    ("Programação II", 6, ["Dr. Edson Tomás", "Engª. Bernardo Dala"]),
                    ("Comportamento Organizacional", 4, ["Dr. Érica Viegas", "MSc. Dominicana Monteiro"]),
                    ("Contabilidade Analítica", 6, ["Dr. António Francisco", "Dr. Israel Abias"]),
                ],
            },
        },
        3: {
            "1": {
                "turmas": ["N1", "T1"],
                "disciplinas": [
                    ("Redes de Computadores", 6, ["Eng. Joaquim de Almeida"]),
                    ("Finanças Empresariais", 4, ["Dr. Manuel Martins", "MSc. Manuel Castó"]),
                    ("Sistemas Operativos I", 4, ["Eng. Joaquim de Almeida"]),
                    ("Base de Dados II", 4, ["MSc. Lírio Ramalheira"]),
                    ("Metodologias de Desenvolvimento de Sistemas de Informação", 6, ["MSc. Bernardo António"]),
                ],
            },
            "2": {
                "turmas": ["N1", "T1"],
                "disciplinas": [
                    ("Qualidade de Sistemas de Informação", 4, ["Eng. Odeir Fortunato", "MSc. Bernardo António"]),
                    ("Gestão de Redes Informáticas", 4, ["Eng. Silvano Rosa"]),
                    ("Linguagens e Tecnologias Web", 6, ["MSc. Nanitamo Pedro António", "Engª. Bernardo Dala"]),
                    ("Sistemas Operativos II", 4, ["Eng. Silvano Rosa", "MSc. Lírio Ramalheira"]),
                    ("Desenvolvimento de Software", 6, ["Dr. Edson Tomás", "MSc. Nanitamo Pedro António"]),
                ],
            },
        },
        4: {
            "1": {
                "turmas": ["N1"],
                "disciplinas": [
                    ("Tecnologias Multimédia", 4, ["MSc. Nanitamo Pedro António"]),
                    ("Segurança Informática em Redes de Sistemas", 4, ["Dr. Edson Tomás"]),
                    ("Direito Informático", 4, ["Dr. Divaldo Sousa"]),
                    ("Fiscalidade", 4, ["Dr. Cristina Silvestre"]),
                ],
            },
            "2": {
                "turmas": ["N1"],
                "disciplinas": [
                    ("Marketing Digital", 4, ["Dr. Mário Chuva"]),
                    ("Gestão de Recursos Humanos", 5, ["Dra. Teresa Vunge"]),
                    ("Comércio Electrónico", 4, ["MSc. Euclides Catumbela"]),
                    ("Auditoria Informática", 6, ["Dr. Wilson Paiva"]),
                ],
            },
        },
    },
    "CF": {
        1: {
            "1": {
                "turmas": ["N1", "T1", "T2", "T3", "T4", "T5", "T6"],
                "disciplinas": [
                    ("Métodos de Investigação Científica", 4, ["Doutor Dácia Joaquim", "Dra. Luísa David", "Doutor João Jovita", "Doutor Alice Costa"]),
                    ("Língua Inglesa I", 4, ["MSc. António Vueba", "Dr. Nuno Alves", "Dr. Anibal Pululo", "Dr. Manuel Pedro", "Dr. Ava Pinto"]),
                    ("Comunicação Pessoal e Empresarial", 4, ["MSc. Artur Santos", "MSc. Eliseu Ernesto", "MSc. Mateus Halaiwa"]),
                    ("Introdução à Informática", 6, ["Dr. Divaldo Sousa", "Eng. Eduardo Chiquete", "Dr. Bernardo Dala", "Eng. Luciano Gonçalves"]),
                    ("Matemática I", 6, ["Dr. Benedito Pinheiro", "MSc. Augusto Carlos Sanson", "MSc. Humberto Filipe", "MSc. Singa Mateus"]),
                ],
            },
            "2": {
                "turmas": ["N1", "T1", "T2", "T3", "T4", "T5", "T6"],
                "disciplinas": [
                    ("Introdução às Organizações e à Gestão", 4, ["MSc. Kavungo João", "Doutor Dácia Joaquim", "MSc. Dominicana Monteiro", "MSc. Laurinda Sacala"]),
                    ("Matemática II", 6, ["Dr. Benedito Pinheiro", "MSc. Augusto Carlos Sanson", "MSc. Humberto Filipe", "MSc. Singa Mateus"]),
                    ("Contabilidade Geral I", 6, ["MSc. Cláudio Voza", "MSc. Sebastião Rocha", "Dr. António dos Santos", "MSc. Catarina Júlio", "Dr. António Caetano"]),
                    ("Comunicação Pessoal e Empresarial", 4, ["MSc. Artur Santos", "MSc. Eliseu Ernesto", "MSc. Mateus Halaiwa"]),
                    ("Língua Inglesa II", 4, ["MSc. António Vueba", "Dr. Francisco Cachivalela", "Dr. Aníbal Pululo", "Dr. Manuel Pedro", "Doutor Gabriel Albino"]),
                ],
            },
        },
        2: {
            "1": {
                "turmas": ["M1", "M2", "M3", "M4", "M5", "N1"],
                "disciplinas": [
                    ("Língua Inglesa III", 4, ["MSc. Jonas Mateus", "Dr. Ava Pinto", "MSc. Agostinho Neto"]),
                    ("Contabilidade Geral II", 6, ["MSc. Sandra da Costa", "Dr. Isabel Almeida", "MSc. Catarina Júlio", "MSc. Sebastião Rocha"]),
                    ("Estatística I", 4, ["MSc. António Oliveira", "MSc. Singa Mateus", "Doutor Victor da Silva"]),
                    ("Microeconomia I", 4, ["Dr. Álvaro Castelo", "MSc. Juliana André"]),
                    ("Cálculo e Operações Financeiras", 6, ["Dr. António dos Santos", "Dr. Flávio Mendes", "MSc. Nelito António", "MSc. Deolinda Cahando", "Dr. Vander Nascimento"]),
                ],
            },
            "2": {
                "turmas": ["M1", "M2", "M3", "M4", "M5", "N1"],
                "disciplinas": [
                    ("Microeconomia II", 4, ["MSc. Juliana André", "Dr. Álvaro Castelo"]),
                    ("Contabilidade Analítica", 6, ["Professor Doutor Capela Tepa", "Dr. Israel Abias", "MSc. Sebastião Rocha", "Dr. António Francisco"]),
                    ("Estatística II", 6, ["MSc. António Oliveira", "MSc. Singa Mateus", "Doutor Victor da Silva"]),
                    ("Direito das Empresas", 4, ["MSc. Yara Vilombo", "Dr. Nelson Marcos", "MSc. Adilson Rodrigues"]),
                    ("Língua Inglesa IV", 4, ["Dr. Ava Pinto", "MSc. Jonas Mateus", "Doutor Gabriel Albino", "MSc. Agostinho Neto"]),
                ],
            },
        },
        3: {
            "1": {
                "turmas": ["M1", "M2", "M3", "M4", "N1"],
                "disciplinas": [
                    ("Direito Comercial", 4, ["Dr. Nelson Marcos", "MSc. Yara Vilombo", "MSc. Adilson Rodrigues"]),
                    ("Contabilidade, Planeamento e Controlo Orçamental", 6, ["Dr. Félix Inácio", "Dr. António dos Santos", "Dr. António Francisco"]),
                    ("Macroeconomia I", 4, ["MSc. João Pinho", "MSc. Eduardo da Silva"]),
                    ("Marketing I", 4, ["MSc. Adão Chitxiami", "Dr. Osmerivaldo Ramos"]),
                    ("Finanças I", 6, ["MSc. Manuel Castó", "Dr. Davidson Manuel"]),
                ],
            },
            "2": {
                "turmas": ["M1", "M2", "M3", "N1"],
                "disciplinas": [
                    ("Macroeconomia II", 4, ["MSc. Deolinda Cahando", "MSc. Eduardo da Silva", "MSc. João Pinho"]),
                    ("Estratégia e Planeamento da Empresa", 6, ["MSc. Miguel Troco", "Dr. Flávio Mendes"]),
                    ("Finanças II", 6, ["MSc. Manuel Castó", "Dr. Davidson Manuel", "Dr. Manuel Martins"]),
                    ("Marketing II", 4, ["MSc. Adão Chitxiami", "Dr. Osmerivaldo Ramos"]),
                    ("Fiscalidade", 4, ["Dr. Flávio Mendes", "Dr. Cristina Silvestre"]),
                ],
            },
        },
        4: {
            "1": {
                "turmas": ["M1", "M2", "M3", "N1"],
                "disciplinas": [
                    ("Mercados e Produtos Financeiros", 6, ["Dr. Pedro Pitta Groz", "MSc. Kavungo João"]),
                    ("Gestão de Recursos Humanos", 4, ["MSc. Miguel Troco", "MSc. Etelvina Carlos", "Dr. Hildebrando Sala"]),
                    ("Contabilidade Analítica Avançada", 6, ["Professor Doutor Capela Tepa", "Dr. António Francisco"]),
                    ("História Económica", 4, ["MSc. Cidália de Castro", "Dra. Helena Miguel"]),
                ],
            },
            "2": {
                "turmas": ["M1", "M2", "M3", "N1"],
                "disciplinas": [
                    ("Análise Económico-Financeira", 6, ["Dr. Davidson Manuel", "MSc. Nelito António", "Dr. Pedro Pitta Groz"]),
                    ("Economia e Comércio Internacionais", 4, ["Dra. Helena Miguel", "MSc. João Pinho"]),
                    ("Auditoria", 6, ["MSc. Cidália de Castro", "Doutor Carla Negrão", "MSc. Marthe Kimfumu"]),
                    ("Sistemas de Controlo de Gestão", 4, ["Doutor Carla Negrão", "Dr. António dos Santos"]),
                ],
            },
        },
    },
    "GBS": {
        1: {
            "1": {
                "turmas": ["N1", "T1", "T2", "T3", "T4"],
                "disciplinas": [
                    ("Introdução à Informática", 6, ["Dr. Divaldo Sousa", "Dr. Joaquim Piedade", "Eng. Luciano Gonçalves", "MSc. Euclides Catumbela"]),
                    ("Matemática I", 6, ["Dr. Benedito Pinheiro", "MSc. Margarida Covilhã", "MSc. Augusto Carlos Sanson"]),
                    ("Comunicação Pessoal e Empresarial", 4, ["MSc. Artur Santos", "MSc. Eliseu Ernesto", "MSc. Mateus Halaiwa", "MSc. Youran Mandonga"]),
                    ("Língua Inglesa I", 4, ["MSc. António Vueba", "Dr. Anibal Pululo", "Dr. Ava Pinto"]),
                    ("Métodos de Investigação Científica", 4, ["Doutor Dácia Joaquim", "Professora Doutora Martha Nyanungo", "Dra. Luísa David", "Doutor Alice Costa"]),
                ],
            },
            "2": {
                "turmas": ["N1", "T1", "T2", "T3", "T4"],
                "disciplinas": [
                    ("Matemática II", 6, ["Dr. Benedito Pinheiro", "MSc. Margarida Covilhã", "MSc. Ana Paula Fonseca"]),
                    ("Contabilidade Geral I", 6, ["MSc. Cláudio Voza", "MSc. Catarina Júlio", "MSc. Sandra da Costa"]),
                    ("Introdução às Organizações e à Gestão", 4, ["MSc. Kavungo João", "MSc. Laurinda Sacala"]),
                    ("Comunicação Pessoal e Empresarial", 4, ["MSc. Artur Santos", "MSc. Eliseu Ernesto", "MSc. Mateus Halaiwa", "MSc. Youran Mandonga"]),
                    ("Língua Inglesa II", 4, ["MSc. António Vueba", "Dr. Anibal Pululo", "Dr. Francisco Cachivalela"]),
                ],
            },
        },
        2: {
            "1": {
                "turmas": ["M1", "M2", "N1"],
                "disciplinas": [
                    ("Contabilidade Geral II", 6, ["MSc. Sandra da Costa", "Dr. Isabel Almeida", "MSc. Cláudio Voza"]),
                    ("Estatística", 6, ["MSc. Singa Mateus", "MSc. António Oliveira"]),
                    ("Cálculo e Operações Financeiras", 4, ["MSc. Deolinda Cahando", "MSc. Nelito António", "Dr. Vander Nascimento"]),
                    ("Tecnologias e Sistemas de Informação", 4, ["Eng. Edilson Cruz", "Eng. Odeir Fortunato"]),
                    ("Língua Inglesa III", 4, ["MSc. Jonas Mateus", "Dr. Ava Pinto", "MSc. Agostinho Neto"]),
                ],
            },
            "2": {
                "turmas": ["M1", "N1"],
                "disciplinas": [
                    ("Introdução ao Risco e Seguro", 6, ["Dr. Júlio Matias", "Dr. Silva e Rocha"]),
                    ("Contabilidade Analítica", 6, ["Professor Doutor Capela Tepa", "Dr. António Francisco"]),
                    ("Comportamento Organizacional", 4, ["MSc. Victória da Silva", "Dr. Érica Viegas"]),
                    ("Mercados e Produtos Financeiros", 4, ["Dr. Pedro Pitta Groz", "MSc. Kavungo João"]),
                    ("Língua Inglesa IV", 4, ["Dr. Ava Pinto", "MSc. Agostinho Neto"]),
                ],
            },
        },
        3: {
            "1": {
                "turmas": ["M1", "N1"],
                "disciplinas": [
                    ("Financiamento e Crédito Bancário", 6, ["Dr. Adélsio dos Santos", "Dr. Artur Camuefo"]),
                    ("Contabilidade, Planeamento e Controlo Orçamental", 6, ["Dr. António dos Santos", "Dr. António Francisco"]),
                    ("Finanças Empresariais", 4, ["Dr. Davidson Manuel", "Dr. Manuel Martins"]),
                    ("Análise e Gestão de Risco", 4, ["Dr. Pedro Pitta Groz", "MSc. Dorivaldo Adão"]),
                    ("Direito na Actividade Bancária", 4, ["Dr. Nelson Marcos", "Dr. Teixeira Cumbi"]),
                ],
            },
            "2": {
                "turmas": ["M1", "N1"],
                "disciplinas": [
                    ("Análise Económico-Financeira", 6, ["MSc. Manuel Castó", "Dr. Pedro Pitta Groz"]),
                    ("Seguros de Vida, Saúde e Acidentes", 6, ["Dr. Pascoal Diogo", "Dr. Silva e Rocha"]),
                    ("Direito na Actividade Seguradora", 4, ["MSc. Yara Vilombo", "Dr. Nelson Marcos"]),
                    ("Fiscalidade de Produtos Financeiros", 4, ["Dr. Isabel Almeida", "Dr. António Francisco"]),
                    ("Operações e Prática Bancária", 4, ["Dr. Adélsio dos Santos", "Dr. Pedro Narciso"]),
                ],
            },
        },
        4: {
            "1": {
                "turmas": ["M1", "N1", "N2"],
                "disciplinas": [
                    ("Gestão de Recursos Humanos", 6, ["MSc. Ana da Silva", "Dra. Teresa Vunge"]),
                    ("Seguros de Propriedade e Não-Vida", 6, ["Dr. Júlio Matias", "Dr. Silva e Rocha"]),
                    ("Economia Angolana e Internacional", 4, ["MSc. João Pinho"]),
                    ("Operações e Prática Seguradora", 4, ["Dr. Passos Reis"]),
                ],
            },
            "2": {
                "turmas": ["M1", "N1"],
                "disciplinas": [
                    ("Gestão de Activos, Passivos e Fundos de Pensões", 6, ["MSc. Carlos Almeida", "Dr. Lídia Pierre"]),
                    ("Auditoria Financeira Banca e Seguros", 6, ["Dr. Nelson Marcos", "MSc. Marthe Kimfumu"]),
                    ("Marketing de Serviços Financeiros", 4, ["Dr. Osmerivaldo Ramos"]),
                    ("Sistemas de Controlo de Gestão", 4, ["Doutor Carla Negrão"]),
                ],
            },
        },
    },
}

# Professores fictícios extra — mantidos com as credenciais de teste já
# documentadas ao utilizador; qualificados para disciplinas reais e recorrentes.
PROFESSORES_TESTE_LOGIN = [
    ("Ricardo Alberto Manuel", "ricardo.manuel@isaf.co.ao", ["Programação I", "Programação II"]),
    ("Domingos Sebastião Kiala", "domingos.kiala@isaf.co.ao", ["Contabilidade Geral I", "Contabilidade Geral II"]),
    ("Ana Paula Ferreira", "ana.ferreira@isaf.co.ao", ["Língua Inglesa I", "Língua Inglesa II"]),
]


def _slug_email(nome: str) -> str:
    """"Dr. Benedito Pinheiro" -> "benedito.pinheiro@isaf.co.ao" — remove títulos
    académicos e acentos para gerar um email plausível e estável."""
    nome_sem_titulo = re.sub(
        r"^(Dr\.|Dra\.|MSc\.|Eng\.|Doutor|Doutora|Professor Doutor|Professora Doutora|Professor|Professora)\s+",
        "",
        nome,
    )
    normalizado = unicodedata.normalize("NFKD", nome_sem_titulo).encode("ascii", "ignore").decode()
    partes = [p.lower() for p in re.findall(r"[A-Za-z]+", normalizado)]
    primeiro, ultimo = partes[0], partes[-1]
    return f"{primeiro}.{ultimo}@isaf.co.ao"


def seed() -> None:
    with Session(engine) as session:
        # --- Curso ---
        cursos_por_codigo = {}
        for codigo, nome in CURSOS.items():
            curso = Curso(codigo=codigo, nome=nome)
            session.add(curso)
            cursos_por_codigo[codigo] = curso
        session.flush()

        # --- Sala ---
        for codigo, capacidade in SALAS.items():
            session.add(Sala(codigo=codigo, nome=f"Sala {codigo}", capacidade=capacidade))

        # --- Disciplina (catálogo global, dedup por nome) + Professor (dedup por nome) ---
        disciplinas_por_nome: dict[str, Disciplina] = {}
        professores_por_nome: dict[str, Professor] = {}
        contador_disciplina = 0

        def obter_ou_criar_disciplina(nome: str) -> Disciplina:
            nonlocal contador_disciplina
            if nome in disciplinas_por_nome:
                return disciplinas_por_nome[nome]
            contador_disciplina += 1
            iniciais = "".join(w[0] for w in re.findall(r"[A-Za-zÀ-ÿ]+", nome) if w[0].isupper())[:4] or "DIS"
            codigo = f"{iniciais}{contador_disciplina:03d}"
            disciplina = Disciplina(codigo=codigo, nome=nome)
            session.add(disciplina)
            session.flush()
            disciplinas_por_nome[nome] = disciplina
            return disciplina

        def obter_ou_criar_professor(nome: str) -> Professor:
            if nome in professores_por_nome:
                return professores_por_nome[nome]
            email = _slug_email(nome)
            professor = Professor(
                nome=nome,
                email=email,
                classificacao=random.randint(2, 5),
                vinculo_casa=random.random() < 0.6,
            )
            session.add(professor)
            session.flush()
            professores_por_nome[nome] = professor
            return professor

        # --- PlanoCurricular + PlanoCurricularDisciplina + Turma + qualificações ---
        total_turmas = 0
        total_planos = 0
        for curso_codigo, anos in CURRICULO.items():
            for ano, semestres in anos.items():
                for semestre, dados in semestres.items():
                    plano = PlanoCurricular(curso_id=cursos_por_codigo[curso_codigo].id, ano=ano, semestre=semestre)
                    session.add(plano)
                    session.flush()
                    total_planos += 1

                    for nome_disciplina, carga, nomes_professores in dados["disciplinas"]:
                        disciplina = obter_ou_criar_disciplina(nome_disciplina)
                        # Uma disciplina pode já ter sido associada a este plano
                        # (não deve acontecer nos dados extraídos, mas protege
                        # contra duplicados no PK composto).
                        ja_associada = session.exec(
                            select(PlanoCurricularDisciplina).where(
                                PlanoCurricularDisciplina.plano_curricular_id == plano.id,
                                PlanoCurricularDisciplina.disciplina_id == disciplina.id,
                            )
                        ).first()
                        if ja_associada is None:
                            session.add(
                                PlanoCurricularDisciplina(
                                    plano_curricular_id=plano.id,
                                    disciplina_id=disciplina.id,
                                    carga_horaria_semanal=carga,
                                )
                            )
                        for nome_professor in nomes_professores:
                            professor = obter_ou_criar_professor(nome_professor)
                            ja_qualificado = session.exec(
                                select(ProfessorDisciplina).where(
                                    ProfessorDisciplina.professor_id == professor.id,
                                    ProfessorDisciplina.disciplina_id == disciplina.id,
                                )
                            ).first()
                            if ja_qualificado is None:
                                session.add(
                                    ProfessorDisciplina(professor_id=professor.id, disciplina_id=disciplina.id)
                                )

                    for turma_codigo in dados["turmas"]:
                        turno = _TURNO_POR_PREFIXO[turma_codigo[0]]
                        codigo_global = f"{curso_codigo}{ano}S{semestre}-{turma_codigo}"
                        nome_turma = f"{cursos_por_codigo[curso_codigo].nome} — {ano}º Ano, {semestre}º Semestre ({turma_codigo})"
                        session.add(
                            Turma(
                                codigo=codigo_global,
                                nome=nome_turma,
                                ano_letivo=ANO_LETIVO,
                                turno=turno,
                                numero_alunos=random.randint(25, 45),
                                plano_curricular_id=plano.id,
                            )
                        )
                        total_turmas += 1
        session.flush()

        # --- Professores de teste (credenciais de login já documentadas) ---
        for nome, email, nomes_disciplinas_qualificacao in PROFESSORES_TESTE_LOGIN:
            professor = session.exec(select(Professor).where(Professor.email == email)).first()
            if professor is None:
                professor = Professor(nome=nome, email=email, classificacao=random.randint(3, 5), vinculo_casa=True)
                session.add(professor)
                session.flush()
            professores_por_nome[nome] = professor
            for nome_disciplina in nomes_disciplinas_qualificacao:
                disciplina = disciplinas_por_nome.get(nome_disciplina)
                if disciplina is None:
                    continue
                ja_qualificado = session.exec(
                    select(ProfessorDisciplina).where(
                        ProfessorDisciplina.professor_id == professor.id,
                        ProfessorDisciplina.disciplina_id == disciplina.id,
                    )
                ).first()
                if ja_qualificado is None:
                    session.add(ProfessorDisciplina(professor_id=professor.id, disciplina_id=disciplina.id))

        # --- Disponibilidade (metade dos professores; a outra metade cai no
        # fallback RN07 = totalmente disponível) ---
        dias_semana = ["segunda", "terca", "quarta", "quinta", "sexta"]
        turno_periodos = {"manha": 6, "tarde": 5, "noite": 5}
        todos_professores = list(professores_por_nome.values())
        for professor in todos_professores[: len(todos_professores) // 2]:
            turno = random.choice(list(turno_periodos))
            for dia in random.sample(dias_semana, k=3):
                for periodo in range(1, turno_periodos[turno] + 1):
                    session.add(
                        Disponibilidade(professor_id=professor.id, dia_semana=dia, turno=turno, periodo=periodo)
                    )

        session.commit()

        print(f"Cursos: {len(CURSOS)}")
        print(f"Disciplinas: {len(disciplinas_por_nome)}")
        print(f"Planos curriculares: {total_planos}")
        print(f"Professores: {len(professores_por_nome)}")
        print(f"Salas: {len(SALAS)}")
        print(f"Turmas: {total_turmas}")

    # --- Utilizador (Gestor + 3 Professores) — cria também a conta Firebase real ---
    with Session(engine) as session:
        contas = [
            ("gestor.teste@isaf.co.ao", PerfilUtilizador.GESTOR, None),
            *[(email, PerfilUtilizador.PROFESSOR, email) for _n, email, _d in PROFESSORES_TESTE_LOGIN],
        ]
        professores_por_email = {p.email: p for p in session.exec(select(Professor)).all()}

        for email, perfil, professor_email in contas:
            existente = session.exec(select(Utilizador).where(Utilizador.email == email)).first()
            if existente is not None:
                print(f"Utilizador já existe, a saltar: {email}")
                continue
            try:
                firebase_rest.criar_conta_com_password(email, SENHA_TESTE)
            except firebase_rest.FirebaseAuthError as exc:
                if exc.codigo != "EMAIL_EXISTS":
                    print(f"AVISO: não foi possível criar a conta Firebase de {email}: {exc}")
                    continue
                print(f"Conta Firebase já existe, a recriar apenas a linha Utilizador: {email}")
            professor_id = professores_por_email[professor_email].id if professor_email else None
            session.add(
                Utilizador(email=email, contacto_telefonico="900000000", perfil=perfil, professor_id=professor_id)
            )
            session.commit()
            print(f"Conta pronta: {email} / {SENHA_TESTE} ({perfil.value})")


if __name__ == "__main__":
    seed()
    print("\nDados de teste (currículo real do ISAF) semeados com sucesso.")
