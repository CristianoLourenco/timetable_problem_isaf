## 3.9 Metodologia de desenvolvimento de software

### 3.9.1 Conceito e disciplinas do RUP

O desenvolvimento do sistema seguiu os princípios do Rational Unified
Process (RUP), um processo de engenharia de software iterativo e
incremental, orientado pela gestão de riscos e organizado em quatro
fases sequenciais --- Concepção (Inception), Elaboração (Elaboration),
Construção (Construction) e Transição (Transition) --- cada uma
composta por uma ou mais iterações que produzem incrementos executáveis
e testáveis do sistema [@kruchten2003]. Ao contrário de um processo em
cascata, o RUP não exige que todos os requisitos estejam completamente
especificados antes do início da implementação; em vez disso, prioriza a
mitigação precoce dos riscos técnicos de maior impacto, permitindo que a
arquitectura seja validada e ajustada ao longo de sucessivas iterações
[@kruchten2003].

### 3.9.2 Aplicação da metodologia RUP a este projecto

O desenvolvimento do backend foi organizado em oito fases sequenciais
(Fase 0 a Fase 7, cf. Secção 4.4), cada uma delimitada por um commit
próprio e por critérios de conclusão verificáveis (testes automatizados
a passar), num mapeamento directo às fases do RUP:

- **Concepção** --- correspondeu à Fase 0 (configuração do projecto
  FastAPI, definição da stack tecnológica) e à Fase 1 (camada de dados:
  modelos SQLModel, seed dos slots temporais), em que se estabeleceu a
  visão do sistema e o âmbito do MVP descrito na Secção 1.7;

- **Elaboração** --- correspondeu à Fase 2 (CRUD e importação em massa
  via Excel, RF01--RF08), em que a arquitectura de camadas
  (router/service/repository) foi validada com funcionalidades de baixo
  risco técnico antes de se avançar para o motor de optimização;

- **Construção** --- correspondeu às Fases 3 a 6 (motor CP-SAT,
  processamento assíncrono, consulta de horários e segurança). Em
  conformidade com o princípio do RUP de mitigar primeiro os riscos de
  maior impacto, a Fase 3 (o motor de optimização, núcleo científico do
  sistema e o seu maior risco técnico) foi implementada antes das
  funcionalidades de menor risco que dela dependem;

- **Transição** --- correspondeu à Fase 7, dedicada a testes de escala e
  de integração ponta-a-ponta (cf. Secção 4.5), validando o sistema
  como um todo antes da consolidação da versão final do MVP.

O desenvolvimento da interface Flutter seguiu o mesmo padrão iterativo,
com a integração de cada funcionalidade (autenticação, gestão de
entidades, importação, disponibilidade, consulta de horário) validada
individualmente contra a API já implementada, em vez de se aguardar pela
conclusão simultânea de ambas as camadas.
