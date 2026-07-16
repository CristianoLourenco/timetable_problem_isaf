![](/media/image2.png){width="2.4479166666666665in"
height="0.8333333333333334in"}

**INSTITUTO SUPERIOR DE ADMINISTRAÇÃO E FINANÇAS**

**CURSO DE INFORMÁTICA DE GESTÃO FINANCEIRA**

**DESENVOLVIMENTO DE UM SISTEMA INTELIGENTE PARA A GERAÇÃO AUTOMÁTICA DE
HORÁRIOS ACADÉMICOS**

**CRISTIANO FRANCISCO LOURENÇO**

**Luanda, 2026**

![](/media/image2.png){width="2.4479166666666665in"
height="0.8333333333333334in"}

**INSTITUTO SUPERIOR DE ADMINISTRAÇÃO E FINANÇAS**

**CURSO DE INFORMÁTICA DE GESTÃO FINANCEIRA**

**DESENVOLVIMENTO DE UM SISTEMA INTELIGENTE PARA A GERAÇÃO AUTOMÁTICA DE
HORÁRIOS ACADÉMICOS**

**CRISTIANO FRANCISCO LOURENÇO**

> Projecto apresentado ao Instituto Superior de
>
> Administração e Finanças -- ISAF, como requisito
>
> para obtenção do grau de licenciatura em
>
> Informática de Gestão Financeira.
>
> **Orientador**: Eng. Euclides J.M. Catumbela

**Luanda, 2026**

COMPROMISSO DO AUTOR

Eu, Cristiano Francisco Lourenço, portador do documento de identidade
007643798LA044 e estudante do curso de Licenciatura em Informática de
Gestão Financeira, declaro que:

O conteúdo do presente documento é um reflexo do meu trabalho pessoal e
manifesto que, diante de qualquer notificação de plágio, cópia ou
prejuízo à fonte original, sou responsável direito legal, financeira e
administrativamente, sem afectar o orientador do trabalho, o ISAF e as
demais instituições que colaboraram neste trabalho, assumindo as
consequências derivadas de tais práticas.

E venho por meio desta, autorizar a disponibilização da versão aprovada
do meu trabalho de fim de curso, DESENVOLVIMENTO DE UM SISTEMA
INTELIGENTE PARA GERAÇÃO AUTOMÁTICA DE HORÁRIOS ACADÉMICOS, na
biblioteca do ISAF e em

outros meios de divulgação electrónica da referida Instituição.

> Assinatura:

DECLARAÇÃO DE ORIGINALIDADE

Declaro, para os devidos efeitos, que o presente trabalho é resultado da
minha investigação pessoal e autónoma, tendo sido elaborado com
observância das normas científicas e académicas aplicáveis. Todas as
fontes consultadas e utilizadas encontram-se devidamente citadas e
referenciadas. Declaro ainda que este trabalho não foi apresentado, no
todo ou em parte, para obtenção de qualquer outro grau académico.

DEDICATÓRIA

Aos meus pais, pelo apoio incondicional em cada etapa deste percurso.

À minha família, pela paciência nos momentos de ausência que este
trabalho exigiu.

A todos os que, de alguma forma, acreditaram neste projeto antes mesmo
de ele existir.

# **AGRADECIMENTOS**

Expresso os meus sinceros agradecimentos a todos os que, de forma
directa ou indirecta, contribuíram para a realização deste trabalho. Em
especial, ao meu orientador, pelo acompanhamento, pelas orientações e
pelo apoio prestado ao longo de todo o processo de investigação.
Agradeço igualmente à instituição, aos docentes, colegas, familiares e
amigos pelo incentivo, compreensão e colaboração demonstrados durante
esta caminhada académica.

RESUMO

Este trabalho aborda o desenvolvimento de um sistema inteligente para a
geração automática de horários académicos no Instituto Superior de
Administração e Finanças (ISAF). O problema de elaboração de horários
constitui uma tarefa complexa, caracterizada pela necessidade de
conciliar múltiplas restrições relacionadas com docentes, turmas,
disciplinas, salas e períodos lectivos. O estudo tem como objectivo
desenvolver uma solução computacional capaz de automatizar este
processo, reduzir conflitos de alocação e melhorar a eficiência da
gestão académica. Metodologicamente, a investigação enquadra-se como
aplicada, de abordagem mista e carácter exploratório-descritivo,
recorrendo à pesquisa bibliográfica, documental e ao estudo de caso. Em
termos tecnológicos, a solução proposta integra Flutter no
desenvolvimento da interface, FastAPI no back-end, o solver Google
OR-Tools CP-SAT no motor de optimização, PostgreSQL na camada de
persistência e Firebase Authentication na gestão de identidade e
controlo de acessos. Espera-se que o sistema contribua para a
modernização dos processos institucionais, para a optimização do uso dos
recursos disponíveis e para a melhoria da experiência de estudantes,
docentes e gestores académicos.

Palavras-chave: geração automática de horários académicos; inteligência
artificial; optimização combinatória; ensino superior; ISAF.

ABSTRACT

This study addresses the development of an intelligent system for the
automatic generation of academic timetables at the Instituto Superior de
Administração e Finanças (ISAF). Timetabling is a complex task because
it requires the simultaneous management of multiple constraints related
to lecturers, classes, courses, rooms, and time slots. The main
objective of this research is to develop a computational solution
capable of automating this process, reducing allocation conflicts, and
improving academic management efficiency. Methodologically, the study is
classified as applied research, with a mixed-methods and
exploratory-descriptive approach, supported by bibliographic research,
documentary analysis, and a case study. From a technological
perspective, the proposed solution integrates Flutter for the user
interface, FastAPI for the back-end, the Google OR-Tools CP-SAT solver
as the optimization engine, PostgreSQL as the persistence layer, and
Firebase Authentication for identity and access management. It is
expected that the system will contribute to the modernization of
institutional processes, the optimization of available resources, and
the improvement of the experience of students, lecturers, and academic
managers.

Keywords: automatic academic timetable generation; artificial
intelligence; combinatorial optimization; higher education; ISAF.

LISTA DE FIGURAS

-   Figura 1 --- Diagrama de Contexto

-   Figura 2 --- Diagrama de Casos de Uso

-   Figura 3 --- Diagrama de Classes

-   Figura 4 --- Diagrama Entidade-Relacional

LISTA DE TABELAS

-   Tabela 1 --- Glossário técnico do sistema

-   Tabela 2 --- Requisitos de negócio

-   Tabela 3 --- Requisitos Funcionais

-   Tabela 4 --- Requisitos Não Funcionais

-   Tabela 5 --- Casos de uso do sistema

-   Tabela 6 --- Cenários de Teste e Critérios de Aceitação

LISTA DE ABREVIATURAS E SIGLAS

-   API --- Application Programming Interface

-   CP --- Constraint Programming

-   CP-SAT --- Constraint Programming Satisfiability

-   CSP --- Constraint Satisfaction Problem

-   DER --- Diagrama Entidade-Relacional

-   IA --- Inteligência Artificial

-   ISAF --- Instituto Superior de Administração e Finanças

-   ITC --- International Timetabling Competition

-   MESCTI --- Ministério do Ensino Superior, Ciência, Tecnologia e
    Inovação

-   RUP --- Rational Unified Process

-   UML --- Unified Modeling Language

-   UCTP --- University Course Timetabling Problem

