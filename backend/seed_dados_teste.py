"""Popula a base de dados com dados fictícios (mas realistas) para demonstração e
capturas de ecrã — NUNCA usar em produção. Não semeia Alocacao (o horário é gerado
pelo utilizador via POST /gerar-horario depois de correr este script).

Cursos, disciplinas e grelha curricular do 1º ano de Informática de Gestão
Financeira inspirados na grelha curricular pública do ISAF (isaf.co.ao); as
restantes disciplinas/anos são extensões plausíveis, não uma cópia exata do
currículo oficial.

Cria também contas de teste reais no Firebase Authentication (via a mesma REST API
que o backend já usa em core/firebase_rest.py) para que seja possível iniciar
sessão como Gestor e como Professor:

  Gestor:     gestor.teste@isaf.co.ao      / Isaf@2026
  Professor:  ricardo.manuel@isaf.co.ao    / Isaf@2026  (Programação)
  Professor:  domingos.kiala@isaf.co.ao    / Isaf@2026  (Contabilidade)
  Professor:  ana.ferreira@isaf.co.ao      / Isaf@2026  (Língua Inglesa)

Uso: python seed_dados_teste.py
"""

import random

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

CURSOS = [
    {"codigo": "IGF", "nome": "Informática de Gestão Financeira"},
    {"codigo": "CF", "nome": "Contabilidade e Finanças"},
    {"codigo": "GBS", "nome": "Gestão Bancária e de Seguros"},
]

# codigo -> (nome, carga_horaria_semanal por omissão)
DISCIPLINAS = {
    "COM101": ("Comunicação Pessoal e Empresarial", 3),
    "ING101": ("Língua Inglesa I", 3),
    "ING102": ("Língua Inglesa II", 3),
    "MET101": ("Métodos de Investigação", 3),
    "MAT101": ("Matemática I", 4),
    "MAT102": ("Matemática II", 4),
    "INT101": ("Introdução às Organizações e à Gestão", 3),
    "EST101": ("Estatística", 4),
    "DIR101": ("Direito Comercial", 3),
    "ETI101": ("Ética e Deontologia Profissional", 2),
    "CTB101": ("Contabilidade Geral I", 5),
    "CTB102": ("Contabilidade Geral II", 5),
    "FSI101": ("Fundamentos de Sistemas de Informação", 4),
    "ARQ101": ("Arquitetura de Computadores", 4),
    "PRG101": ("Programação I", 5),
    "PRG102": ("Programação II", 5),
    "SDG101": ("Sistemas Digitais", 3),
    "BDD101": ("Bases de Dados", 4),
    "RDC101": ("Redes de Computadores", 3),
    "ESW101": ("Engenharia de Software", 4),
    "COF101": ("Cálculo e Operações Financeiras", 4),
    "CTC101": ("Contabilidade de Custos", 4),
    "FIS101": ("Fiscalidade", 3),
    "AUD101": ("Auditoria", 3),
    "ORC101": ("Orçamento e Controlo de Gestão", 3),
    "GBC101": ("Gestão Bancária", 4),
    "SEG101": ("Seguros e Resseguros", 3),
    "MFN101": ("Mercados Financeiros", 4),
    "AIN101": ("Análise de Investimentos", 4),
    "RSK101": ("Gestão de Risco", 3),
}

# curso_codigo -> ano -> semestre -> [codigo_disciplina]
GRADE = {
    "IGF": {
        1: {
            "1": ["COM101", "ING101", "MET101", "FSI101", "MAT101", "CTB101"],
            "2": ["ING102", "INT101", "ARQ101", "MAT102", "EST101"],
        },
        2: {
            "1": ["CTB102", "PRG101", "SDG101", "COF101", "DIR101"],
            "2": ["PRG102", "BDD101", "RDC101", "ESW101", "ETI101"],
        },
    },
    "CF": {
        1: {
            "1": ["COM101", "ING101", "MET101", "MAT101", "CTB101", "INT101"],
            "2": ["ING102", "MAT102", "EST101", "DIR101"],
        },
        2: {
            "1": ["CTB102", "CTC101", "FIS101", "ETI101"],
            "2": ["AUD101", "ORC101", "MFN101", "AIN101"],
        },
    },
    "GBS": {
        1: {
            "1": ["COM101", "ING101", "MET101", "MAT101", "CTB101", "INT101"],
            "2": ["ING102", "MAT102", "EST101", "DIR101"],
        },
        2: {
            "1": ["GBC101", "SEG101", "MFN101", "ETI101"],
            "2": ["AIN101", "RSK101", "CTB102", "FIS101"],
        },
    },
}

# nome, email_local, classificacao, vinculo_casa, [codigos_disciplina qualificadas]
PROFESSORES = [
    ("Manuel João Sithole", "manuel.sithole", 5, True, ["MAT101", "MAT102"]),
    ("Ana Paula Ferreira", "ana.ferreira", 4, True, ["ING101", "ING102"]),
    ("Domingos Sebastião Kiala", "domingos.kiala", 5, True, ["CTB101", "CTB102"]),
    ("Isabel Cristina Neto", "isabel.neto", 4, False, ["CTC101", "AUD101", "ORC101"]),
    ("Fernando Miguel Bumba", "fernando.bumba", 3, True, ["DIR101", "ETI101"]),
    ("Cesaltina Manuela Paulo", "cesaltina.paulo", 4, False, ["FIS101"]),
    ("António José Muatxinga", "antonio.muatxinga", 3, True, ["INT101", "MET101"]),
    ("Beatriz Fernanda Capemba", "beatriz.capemba", 4, True, ["COM101"]),
    ("Ricardo Alberto Manuel", "ricardo.manuel", 5, True, ["FSI101", "PRG101", "PRG102"]),
    ("Vanusa Domingas Chissano", "vanusa.chissano", 4, False, ["ARQ101", "SDG101", "RDC101"]),
    ("Jorge Paulino Massango", "jorge.massango", 3, True, ["BDD101", "ESW101"]),
    ("Márcia Luzia Kanda", "marcia.kanda", 5, True, ["COF101", "MFN101", "AIN101"]),
    ("Osvaldo Pedro Xavier", "osvaldo.xavier", 4, False, ["GBC101"]),
    ("Teresa Amélia Sumbo", "teresa.sumbo", 3, True, ["SEG101", "RSK101"]),
    ("Aires Domingos Baptista", "aires.baptista", 4, True, ["EST101"]),
    ("Lurdes Adelaide Manuel", "lurdes.manuel", 3, False, ["MAT101", "EST101"]),
    ("Sérgio Vicente Bento", "sergio.bento", 4, True, ["PRG101", "BDD101"]),
    ("Graça Isabel Domingos", "graca.domingos", 3, False, ["CTB101", "FIS101"]),
]

SALAS = [
    ("ANF-A", "Anfiteatro A", 120),
    ("ANF-B", "Anfiteatro B", 100),
    ("S101", "Sala 101", 40),
    ("S102", "Sala 102", 40),
    ("S103", "Sala 103", 35),
    ("S104", "Sala 104", 35),
    ("LAB01", "Laboratório de Informática 1", 30),
    ("LAB02", "Laboratório de Informática 2", 30),
    ("S201", "Sala 201", 45),
    ("S202", "Sala 202", 45),
]

TURNO_POR_ANO = {1: TurnoEnum.MANHA, 2: TurnoEnum.NOITE}
DIAS_SEMANA = ["segunda", "terca", "quarta", "quinta", "sexta"]
TURNO_PERIODOS = {"manha": 6, "tarde": 5, "noite": 5}


def seed() -> None:
    with Session(engine) as session:
        # --- Curso ---
        cursos_por_codigo: dict[str, Curso] = {}
        for c in CURSOS:
            curso = Curso(**c)
            session.add(curso)
            cursos_por_codigo[c["codigo"]] = curso
        session.flush()

        # --- Disciplina ---
        disciplinas_por_codigo: dict[str, Disciplina] = {}
        for codigo, (nome, _carga) in DISCIPLINAS.items():
            disciplina = Disciplina(codigo=codigo, nome=nome)
            session.add(disciplina)
            disciplinas_por_codigo[codigo] = disciplina
        session.flush()

        # --- PlanoCurricular + PlanoCurricularDisciplina ---
        planos: dict[tuple[str, int, str], PlanoCurricular] = {}
        for curso_codigo, anos in GRADE.items():
            for ano, semestres in anos.items():
                for semestre, codigos_disciplina in semestres.items():
                    plano = PlanoCurricular(
                        curso_id=cursos_por_codigo[curso_codigo].id, ano=ano, semestre=semestre
                    )
                    session.add(plano)
                    session.flush()
                    planos[(curso_codigo, ano, semestre)] = plano
                    for codigo_disc in codigos_disciplina:
                        _nome, carga_base = DISCIPLINAS[codigo_disc]
                        carga = carga_base + random.choice([-1, 0, 0, 1])
                        carga = max(2, carga)
                        session.add(
                            PlanoCurricularDisciplina(
                                plano_curricular_id=plano.id,
                                disciplina_id=disciplinas_por_codigo[codigo_disc].id,
                                carga_horaria_semanal=carga,
                            )
                        )
        session.flush()

        # --- Professor + ProfessorDisciplina ---
        professores_por_email: dict[str, Professor] = {}
        for nome, email_local, classificacao, vinculo_casa, codigos_qualificacao in PROFESSORES:
            email = f"{email_local}@isaf.co.ao"
            professor = Professor(
                nome=nome, email=email, classificacao=classificacao, vinculo_casa=vinculo_casa
            )
            session.add(professor)
            session.flush()
            professores_por_email[email] = professor
            for codigo_disc in codigos_qualificacao:
                session.add(
                    ProfessorDisciplina(
                        professor_id=professor.id, disciplina_id=disciplinas_por_codigo[codigo_disc].id
                    )
                )
        session.flush()

        # --- Sala ---
        for codigo, nome, capacidade in SALAS:
            session.add(Sala(codigo=codigo, nome=nome, capacidade=capacidade))

        # --- Turma (uma por PlanoCurricular) ---
        for (curso_codigo, ano, semestre), plano in planos.items():
            turno = TURNO_POR_ANO[ano]
            numero_alunos = random.randint(25, 45)
            codigo = f"{curso_codigo}{ano}S{semestre}-26"
            nome = f"{cursos_por_codigo[curso_codigo].nome} — {ano}º Ano, {semestre}º Semestre"
            session.add(
                Turma(
                    codigo=codigo,
                    nome=nome,
                    ano_letivo=2026,
                    turno=turno,
                    numero_alunos=numero_alunos,
                    plano_curricular_id=plano.id,
                )
            )
        session.flush()

        # --- Disponibilidade (metade dos professores; a outra metade cai no
        # fallback RN07 = totalmente disponível) ---
        professores_lista = list(professores_por_email.values())
        for professor in professores_lista[: len(professores_lista) // 2]:
            turno = random.choice(list(TURNO_PERIODOS))
            dias_escolhidos = random.sample(DIAS_SEMANA, k=3)
            for dia in dias_escolhidos:
                for periodo in range(1, TURNO_PERIODOS[turno] + 1):
                    session.add(
                        Disponibilidade(
                            professor_id=professor.id, dia_semana=dia, turno=turno, periodo=periodo
                        )
                    )

        session.commit()

        print(f"Cursos: {len(CURSOS)}")
        print(f"Disciplinas: {len(DISCIPLINAS)}")
        print(f"Planos curriculares: {len(planos)}")
        print(f"Professores: {len(PROFESSORES)}")
        print(f"Salas: {len(SALAS)}")
        print(f"Turmas: {len(planos)}")

    # --- Utilizador (Gestor + 3 Professores) — cria também a conta Firebase real,
    # via a mesma REST API que o backend usa (core/firebase_rest.py) ---
    with Session(engine) as session:
        contas = [
            ("gestor.teste@isaf.co.ao", PerfilUtilizador.GESTOR, None),
            ("ricardo.manuel@isaf.co.ao", PerfilUtilizador.PROFESSOR, "ricardo.manuel@isaf.co.ao"),
            ("domingos.kiala@isaf.co.ao", PerfilUtilizador.PROFESSOR, "domingos.kiala@isaf.co.ao"),
            ("ana.ferreira@isaf.co.ao", PerfilUtilizador.PROFESSOR, "ana.ferreira@isaf.co.ao"),
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
                # Conta Firebase já existe de uma seed anterior (a BD local foi
                # recriada, mas o Firebase Authentication é externo e não é
                # afetado) — a senha continua a ser SENHA_TESTE; só falta
                # recriar a linha Utilizador correspondente.
                print(f"Conta Firebase já existe, a recriar apenas a linha Utilizador: {email}")
            professor_id = professores_por_email[professor_email].id if professor_email else None
            session.add(
                Utilizador(
                    email=email, contacto_telefonico="900000000", perfil=perfil, professor_id=professor_id
                )
            )
            session.commit()
            print(f"Conta criada: {email} / {SENHA_TESTE} ({perfil.value})")


if __name__ == "__main__":
    seed()
    print("\nDados de teste semeados com sucesso.")
