## **4.4 Implementação do sistema**

A implementação seguiu uma abordagem incremental e iterativa inspirada
no Rational Unified Process (RUP), com o desenvolvimento organizado em
módulos independentes e testáveis, por ordem de prioridade técnica e de
dependência entre componentes [@kruchten2003].

### **4.4.1 Módulo 1 --- Motor de Optimização (Core)**

O módulo central foi desenvolvido em primeiro lugar, de forma isolada,
para validar a lógica matemática sem dependências de framework.
Implementa a modelagem esparsa do CSP com Google OR-Tools CP-SAT, a
gestão das Hard Constraints puras (RN01, RN02 e RN03), a regra híbrida
de agrupamento em blocos (RN06), a penalização das Soft Constraints
(RN04 e RN08) e do défice residual de RN05 na função objectivo (cf.
Secção 4.1.2), e o mecanismo de diagnóstico estrutural para
inviabilidade (RF13, cf. Secção 4.3.3). A arquitectura do modelo foi
preparada para suportar, em iterações futuras, o congelamento de
alocações necessário à reoptimização incremental (RF14, classificado
como trabalho futuro). O código deste módulo encontra-se disponível no
repositório do projecto (cf. Apêndice A).

### **4.4.2 Módulo 2 --- API REST (FastAPI)**

O segundo módulo implementa a camada de integração HTTP, expondo os
endpoints definidos no contrato de API: POST /gerar-horario (accciona o
solver para o âmbito ano lectivo/semestre pedido), GET /jobs/{job\_id}
(consulta o estado de uma tarefa assíncrona) e GET
/horarios/turma/{id} e /horarios/professor/{id} (obtêm o horário
resultante em JSON estruturado por dia e tempo, sempre a partir do Job
concluído mais recente do âmbito correspondente). A validação dos
payloads de entrada utiliza modelos Pydantic, garantindo a integridade
dos dados antes da sua passagem ao motor de optimização.

### **4.4.3 Módulo 3 --- Interface Flutter**

A interface de utilizador foi implementada em Flutter com Clean
Architecture, disponibilizando os seguintes ecrãs principais:
autenticação de utilizadores (Firebase Authentication, RF15/RF16),
gestão de entidades académicas (docentes, turmas, disciplinas, salas),
registo de disponibilidade docente, visualização do horário gerado em
formato de grelha semanal, consulta do relatório de inviabilidade quando
aplicável, e exportação do horário em PDF. As capturas de ecrã do
sistema encontram-se no Apêndice C.
