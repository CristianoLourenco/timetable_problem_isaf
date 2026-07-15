# Análise de Requisitos — Sistema Inteligente de Geração de Horários (ISAF)
> Documento vivo de trabalho. Última atualização: 15/07. Serve de base para o Capítulo 4 do TFC.
> **Fonte de verdade única** — todos os diagramas e o relatório derivam deste documento.

---

## 1. Atores / Stakeholders

| Ator | Natureza | Papel |
|---|---|---|
| **Utilizador** | Actor pai (generalização UML) | Agrega o comportamento comum de autenticação partilhado pelos dois actores humanos |
| **Gestor Académico / Secretaria** | Actor humano — herda Utilizador | Gere dados mestre, importa ficheiros, dispara geração, consulta e exporta horários |
| **Professor** | Actor humano — herda Utilizador | Gere a própria disponibilidade, consulta e exporta o seu horário |
| **Firebase Authentication** | Entidade externa não-humana | Emite e valida tokens de identidade; gere login email/senha e Google Sign-In |
| **Motor CP-SAT** | Componente interno do sistema | Consome dados validados e produz o horário optimizado |

**Decisões confirmadas:**
- 15/07: Modelo de generalização de actores adoptado (Utilizador → Gestor / Professor)
- 15/07: Login via email/senha **e** Google Sign-In (ambos Firebase nativos)
- 15/07: Professor cria a própria conta Firebase — validação de email vs. registo do Gestor feita internamente (RN10)

---

## 2. Requisitos Funcionais (RF)

### Gestão de Dados Mestre
| ID | Nome | Ator | Descrição |
|---|---|---|---|
| RF01 | Gerir Professores (CRUD) | Gestor | Criar, consultar, actualizar e eliminar registos de docentes, incluindo email institucional |
| RF02 | Gerir Turmas (CRUD) | Gestor | Gestão completa das turmas da instituição |
| RF03 | Gerir Disciplinas (CRUD) | Gestor | Catálogo de disciplinas com cargas horárias semanais |
| RF04 | Gerir Salas (CRUD) | Gestor | Salas físicas com capacidade e recursos |
| RF05 | Gerir Disponibilidade (CRUD) | Professor | Professor gere os próprios slots de disponibilidade/preferência |

### Importação de Dados
| ID | Nome | Ator | Descrição |
|---|---|---|---|
| RF06 | Importar Dados via Excel | Gestor | Importação em massa por entidade a partir de ficheiros .xlsx institucionais |
| RF07 | Validar Dados Importados | Sistema (interno) | Validação de estrutura e integridade antes da gravação; incluído obrigatoriamente por RF06 |
| RF08 | Idempotência na Importação | Sistema (interno) | Reimportação ignora registos já existentes com base em chave institucional única |

### Geração de Horário
| ID | Nome | Ator | Descrição |
|---|---|---|---|
| RF09 | Disparar Geração de Horário | Gestor | Dispara processamento assíncrono do motor CP-SAT |
| RF10 | Consultar Estado de Processamento | Gestor | Polling do estado do Job (Em Processamento / Concluído / Falhado) |
| RF11 | Consultar Horário por Turma | Gestor | Grelha semanal filtrada por turma |
| RF12 | Consultar Horário por Professor | Gestor, Professor | Agenda semanal por docente — controlo de acesso por perfil (RN10/UC15) |
| RF13 | Notificar Cenário Sem Solução | Sistema (interno) | Relatório explícito de conflitos quando solver retorna INFEASIBLE |

### Exportação de Horários (novo — 15/07)
| ID | Nome | Ator | Descrição |
|---|---|---|---|
| RF18 | Exportar Horário (PDF/Excel) | Gestor, Professor | Exportação do horário em PDF e/ou Excel — controlo de acesso por perfil: Gestor exporta qualquer horário, Professor só exporta o seu |

### Autenticação e Segurança
| ID | Nome | Ator | Descrição |
|---|---|---|---|
| RF15 | Autenticar-se | Utilizador | Login via email/senha ou Google Sign-In, ambos via Firebase Authentication |
| RF16 | Recuperar Password | Utilizador | Reset self-service via link de email (Firebase nativo — só aplicável a contas email/senha) |

### Trabalho Futuro (fora do escopo MVP)
| ID | Nome | Descrição |
|---|---|---|
| RF14 | Reotimização Manual | Alteração de alocação sem recalcular horário completo |
| RF17 | Sincronização Google Calendar | Exportação automática para calendários dos docentes |

---

## 3. Requisitos Não-Funcionais (RNF)

| ID | Categoria | Descrição |
|---|---|---|
| RNF01 | Desempenho | Escalar para 100+ professores / 60+ turmas com modelagem esparsa |
| RNF02 | Usabilidade | Resposta assíncrona — Job ID + polling (RF09/RF10) |
| RNF03 | Confiabilidade | Nunca falhar silenciosamente; minimizar INFEASIBLE |
| RNF04 | Manutenibilidade | Motor CP-SAT isolado da camada de API FastAPI |
| RNF05 | Portabilidade de Dados | Entrada via Excel .xlsx institucional |
| RNF06 | Segurança | Firebase Authentication — email/senha + Google Sign-In; 2 perfis (Gestor, Professor); backend valida ID Token em cada pedido (RN09) |
| RNF07 | Persistência | PostgreSQL via SQLModel — suporte a escrita concorrente e hosting estável |

---

## 4. Regras de Negócio

| ID | Regra | Tipo |
|---|---|---|
| RN01 | Professor sem dupla alocação no mesmo slot | Hard |
| RN02 | Turma sem duas disciplinas no mesmo slot | Hard |
| RN03 | Sala sem duas turmas no mesmo slot | Hard |
| RN04 | Alocação mais próxima da disponibilidade do Professor | Soft (penalização alta) |
| RN05 | Carga horária semanal da Disciplina cumprida integralmente | Hard |
| RN06 | Aulas agrupadas em blocos — sem tempos isolados | Hard (tamanho do bloco decidido pelo solver) |
| RN07 | Professor sem disponibilidade registada = totalmente disponível | Lógica de fallback |
| RN08 | Sala com capacidade adequada preferencial | Soft (penalização muito alta) |
| RN09 | ID Token Firebase válido obrigatório em todos os pedidos excepto RF15/RF16 | Hard — HTTP 401 se ausente/expirado |
| RN10 | Email da conta Firebase do Professor deve corresponder a registo criado pelo Gestor (RF01) | Hard — HTTP 403 se não corresponder |
| RN11 | Gestor exporta/consulta horários de qualquer entidade; Professor exporta/consulta apenas o seu próprio | Hard — validação interna (UC15) |

---

## 5. Casos de Uso (UC) — versão final 15/07

### Actores
- **Utilizador** (actor pai): UC13, UC14
- **Gestor** (herda Utilizador): UC01–UC04, UC06, UC08–UC12, UC16
- **Professor** (herda Utilizador): UC05, UC12, UC16

### Tabela completa

| UC | Nome | RF | Ator(es) | Relação |
|---|---|---|---|---|
| UC01 | Gerir Professores (CRUD) | RF01 | Gestor | — |
| UC02 | Gerir Turmas (CRUD) | RF02 | Gestor | — |
| UC03 | Gerir Disciplinas (CRUD) | RF03 | Gestor | — |
| UC04 | Gerir Salas (CRUD) | RF04 | Gestor | — |
| UC05 | Gerir Disponibilidade (CRUD) | RF05 | Professor | — |
| UC06 | Importar Dados via Excel | RF06 | Gestor | `<<include>>` UC07 |
| UC07 | Validar Dados Importados | RF07 | Sistema (interno) | incluído por UC06 |
| UC08 | Disparar Geração de Horário | RF09 | Gestor | `<<extend>>` UC09 |
| UC09 | Notificar Sem Solução Viável | RF13 | Sistema (interno) | estende UC08 |
| UC10 | Consultar Estado de Processamento | RF10 | Gestor | — |
| UC11 | Consultar Horário por Turma | RF11 | Gestor | — |
| UC12 | Consultar Horário por Professor | RF12 | Gestor, Professor | `<<include>>` UC15 |
| UC13 | Autenticar-se | RF15 | Utilizador | — (pré-condição de todos os outros) |
| UC14 | Recuperar Password | RF16 | Utilizador | — |
| UC15 | Verificar Permissão de Acesso | RN11 | Sistema (interno) | incluído por UC12, UC16 |
| UC16 | Exportar Horário (PDF/Excel) | RF18 | Gestor, Professor | `<<include>>` UC15 |

### Relações estruturais
```
UC06 ──<<include>>──→ UC07  (validação obrigatória na importação)
UC08 ←──<<extend>>── UC09  (notificação condicional — só se INFEASIBLE)
UC12 ──<<include>>──→ UC15  (verificação de permissão obrigatória)
UC16 ──<<include>>──→ UC15  (verificação de permissão obrigatória)
```

### Generalização de actores
```
        Utilizador
        /         \
  Gestor         Professor
```
Utilizador associa-se a UC13 e UC14. Os actores filhos herdam este comportamento sem repetição de setas no diagrama.

---

## 6. Os Três Cenários Concorrentes

- **Cenário A** — Período fixo por Turma (Hard)
- **Cenário B** — Período fixo por Professor (Hard)
- **Cenário C** — Preferência institucional de período (Soft)

**Regra de resolução (07/07):**
1. Turma tem prioridade estrutural sobre Professor
2. Solver aloca primeiro os professores de maior prioridade nos tempos fixos das turmas
3. Restantes distribuídos o mais próximo possível da disponibilidade registada
4. INFEASIBLE minimizado via soft constraints — nunca falha silenciosamente
5. Intervenção humana é o último recurso (fora do sistema)

### Função objectivo do CP-SAT
```
minimizar: (peso_A × penalização_disponibilidade_RN04) + (peso_B × variância_distribuição_diária)
```

### Agrupamento em blocos (RN06)
- Sem tempo isolado (1 slot sozinho) — proibido (Hard)
- Sem limite máximo de bloco — decisão do solver
- Carga ímpar → blocos par + ímpar (ex: 5 = 2+3)
- Objectivo: minimizar dias de deslocação do docente

---

## 7. Fórmula de Prioridade Docente

| Factor | Papel | Peso |
|---|---|---|
| Classificação institucional (1–5) | Prioridade de fixação | 50% |
| Vínculo (professor de casa) | Prioridade de fixação | 30% |
| Escassez de disponibilidade (menos slots = mais prioritário) | Prioridade de fixação | 20% |
| Quantidade de aulas | Objectivo de equidade separado (função objectivo) | — |

---

## 8. Stack Tecnológica Fechada

| Camada | Tecnologia | Decisão |
|---|---|---|
| Frontend | Flutter (Clean Architecture, GoRouter, Provider, Hive) | Stack original |
| Backend | Python / FastAPI | Stack original |
| Motor de Optimização | Google OR-Tools CP-SAT | Stack original |
| Persistência | PostgreSQL + SQLModel | Decidido 15/07 (substituiu SQLite) |
| Autenticação | Firebase Authentication (email/senha + Google Sign-In) | Decidido 13/07 |
| IDE | Antigravity (fork VS Code, Google) | Ambiente de desenvolvimento |
| Modelação | Visual Paradigm | Diagramas UML definitivos |
| Versionamento | Git / GitHub | Repositório monorepo |

---

## 9. Perguntas em Aberto

- [ ] Resultado do OR-Tools — estrutura exacta do JSON de saída (a analisar na fase de backend)
- [ ] Chave de idempotência da importação Excel — confirmar com ficheiros reais do ISAF
- [ ] Estrutura das entidades no frontend (já existe parcialmente) — alinhar com Diagrama de Classes
