## **4.5 Testes e validação**

Em conformidade com a abordagem exploratória-descritiva definida na
Secção 3, a validação do sistema seguiu uma estratégia de cenários de
teste progressivos --- do cenário mínimo controlável até um cenário à
escala real do ISAF --- complementada por dois cenários de inviabilidade
intencional, destinados a verificar especificamente o mecanismo de
diagnóstico estrutural descrito na Secção 4.3.3 (RF13, RNF03). A suite
de testes automatizados totaliza 131 testes, cobrindo o motor de
optimização e a decomposição por turno (RNF01), a validação imperativa
da alocação manual (RF13), o fluxo assíncrono de geração (RF09/RF10), a
consulta estruturada de horários (RF11/RF12), a exportação em PDF
(RF11/RF12), a importação em massa (RF06--RF08) e a camada de
autenticação e autorização (RN09--RN11, RF15/RF16, Secção 4.3.2) --- 37
destes testes cobrem especificamente a verificação de token, a
resolução de papel, o controlo de acesso por rota e o fluxo de
auto-registo de Professor (RN10); a suite completa executa em
aproximadamente 6 segundos. Adicionalmente, um script de medição
dedicado (`scripts/benchmark_isaf_real.py`, fora da suite automática por
depender da base de dados de produção e demorar vários minutos) valida o
sistema directamente contra os dados reais do ISAF (CT07).

Table: Tabela 6 --- Cenários de Teste e Critérios de Aceitação

+------+------------------------+----------------------------+----------------------------+
| ID   | Cenário                | Dimensão                   | Critério de Aceitação      |
+======+========================+============================+============================+
| CT01 | Cenário mínimo viável  | 3 turmas, 3 disciplinas, 2 | Status OPTIMAL/FEASIBLE; 6 |
|      |                        | professores, 1 sala        | alocações geradas; RN01--  |
|      |                        |                            | RN03, RN05 e RN06          |
|      |                        |                            | satisfeitas.               |
+------+------------------------+----------------------------+----------------------------+
| CT02 | Cenário de escala      | 12 turmas, 6 disciplinas,  | Status OPTIMAL/FEASIBLE em |
|      |                        | 8 professores, 5 salas     | até 10s; RN01--RN03 e RN05 |
|      |                        |                            | satisfeitas sem violação.  |
+------+------------------------+----------------------------+----------------------------+
| CT03 | Inviabilidade          | 1 turma, 1 disciplina, 1   | Status INFEASIBLE;         |
|      | estrutural intencional | professor, 1 sala, carga   | diagnóstico identifica a   |
|      |                        | semanal = 1                | causa estrutural (carga    |
|      |                        |                            | incompatível com o bloco   |
|      |                        |                            | mínimo do RN06); zero      |
|      |                        |                            | alocações.                 |
+------+------------------------+----------------------------+----------------------------+
| CT04 | Distinção entre        | Cenário de escala (CT02)   | Status INFEASIBLE;         |
|      | esgotamento de tempo e | com tempo-limite reduzido  | diagnóstico refere o       |
|      | inviabilidade genuína  | para 0,01s                 | limite de tempo, sem       |
|      |                        |                            | reportar falsamente uma    |
|      |                        |                            | causa estrutural.          |
+------+------------------------+----------------------------+----------------------------+
| CT05 | Fluxo ponta-a-ponta    | Criação de entidades via   | Job conclui com sucesso;   |
|      | (Golden Path)          | API, POST /gerar-horario,  | GET /horarios/turma/{id} e |
|      |                        | polling do Job, consulta   | /horarios/professor/{id}   |
|      |                        | por turma e por professor  | devolvem JSON estruturado  |
|      |                        |                            | por dia/slot.              |
+------+------------------------+----------------------------+----------------------------+
| CT06 | Idempotência da        | Reimportação do mesmo      | Registos já existentes são |
|      | importação Excel       | ficheiro institucional     | ignorados; nenhum registo  |
|      |                        |                            | duplicado é criado na      |
|      |                        |                            | segunda importação.        |
+------+------------------------+----------------------------+----------------------------+
| CT07 | Cenário real à escala  | 45 turmas, 104 docentes,   | Status FEASIBLE em 95,3s;  |
|      | do ISAF (dados de      | 25 salas, 1044 tempos      | 973/1044 tempos lectivos   |
|      | produção, 2025/2026)   | lectivos esperados         | alocados (93,2%); zero     |
|      |                        | (2025/2026, 1.º semestre)  | turmas com mais de uma     |
|      |                        |                            | sala no mesmo turno.       |
+------+------------------------+----------------------------+----------------------------+

O cenário CT01 corresponde ao critério mínimo de aceitação definido na
Secção 3.5.1 e foi o primeiro a ser validado, na Fase 3, antes de
qualquer dependência de framework ser introduzida. O cenário CT02,
introduzido na Fase 7, aumenta a dimensão do problema para 12 turmas
(cada uma com 30 alunos) e 8 professores --- dos quais 6 são
especialistas numa única disciplina e 2 partilham qualificação entre
duas disciplinas, testando a resolução de ambiguidade de alocação pelo
solver --- restringidos a um único turno (45 slots). Os cenários
CT01--CT06 foram executados contra uma base de dados SQLite em memória,
e não contra o PostgreSQL utilizado em produção (cf. RNF07, Secção
4.1.4).

O cenário CT07, executado directamente contra a base de dados de
produção (PostgreSQL) com os dados reais do ISAF para 2025/2026, 1.º
semestre, eleva a escala testada para 45 turmas e 104 docentes ---
próximo do limite de turmas formalmente definido pelo RNF01 (60+
turmas), embora ainda aquém do limite de docentes (100+, já
ultrapassado) considerado em conjunto com a totalidade de turmas do
requisito. O sistema produziu 973 das 1044 alocações de carga horária
semanal esperadas (93,2%) em 95,3 segundos, sem qualquer turma a
utilizar mais do que uma sala dentro do mesmo turno --- confirmando por
medição directa a decisão de modelagem de sala fixa por turma e turno
descrita na Secção 4.4.1. O défice residual de 71 tempos lectivos (25
das 45 turmas com défice parcial) reflecte o compromisso deliberado
entre tempo de resolução e optimalidade (`relative_gap_limit`, Secção
4.4.1): o CP-SAT aceita uma solução suficientemente boa dentro do
orçamento de tempo da primeira tentativa do escalonamento automático
(RF13) em vez de insistir indefinidamente em fechar a totalidade da
carga horária, ficando os tempos não alocados disponíveis para
resolução por alocação manual (RF13, UC09).

Os cenários CT03 e CT04 validam especificamente o mecanismo de
diagnóstico descrito na Secção 4.3.3. O CT03 força uma violação
estrutural do RN06 (uma disciplina com carga semanal de apenas 1 tempo
lectivo, incompatível com o tamanho mínimo de bloco de 2 tempos) e
verifica que o diagnóstico identifica correctamente essa causa. O CT04
verifica um requisito de correcção mais subtil: ao reduzir
artificialmente o tempo disponível ao solver para o cenário de escala
(CT02) para 0,01 segundos, o CP-SAT devolve um status que, sem
tratamento adequado, seria indistinguível de uma inviabilidade
estrutural genuína. O sistema distingue correctamente entre as duas
situações, evitando que um simples esgotamento do orçamento de tempo
seja reportado ao utilizador como uma revisão manual necessária.
