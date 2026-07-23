# Revisão do orientador — apontamentos e estado

Rastreabilidade dos 37 comentários do orientador (Euclides João Mujanga
Catumbela, 2026-07-18) sobre `docs/dist/TFC_Cristiano_Lourenco -
Revisado.docx`, extraídos directamente do `comments.xml` do ficheiro
(o Word não expõe estes comentários como texto navegável no relatório
`.md` fonte). Cada entrada regista o ID do comentário, o texto original,
o estado face à fonte actual (`docs/relatorio/`) e, quando aplicável, os
ficheiros afectados.

Muitos comentários referem-se a um estado **anterior à reorganização do
relatório** (tabelas com 2 linhas de exemplo em vez da totalidade,
"CT05" indefinido, requisitos truncados) — nesses casos o apontamento já
não se aplica à fonte actual, mas fica registado para memória.

Actualizar esta tabela sempre que um novo apontamento for recebido ou
resolvido — não apagar entradas resolvidas, apenas marcar o estado.

## Estado: resolvidos

### ID 2 — Redacção: "responsável direito legal..."

**Apontamento:** [REDACÇÃO — Importante] Erro de construção frásica:
«sou responsável direito legal, financeira e administrativamente».
Sugestão: «respondo directa, legal, financeira e administrativamente».

**Estado:** Já corrigido — o texto actual usa exactamente a formulação
sugerida ("respondo directa, legal, financeira e administrativamente").

**Ficheiro:** `00_pretextual/01_compromisso_autor.md`

---

### ID 3 — Título inconsistente entre secções

**Apontamento:** [COERÊNCIA — Melhoria] O título transcrito («... PARA
GERAÇÃO AUTOMÁTICA ...») difere do título da capa («... PARA A GERAÇÃO
AUTOMÁTICA ...»). Uniformizar.

**Estado:** Já corrigido — todas as ocorrências (capa, folha de rosto,
compromisso do autor) usam "PARA A GERAÇÃO AUTOMÁTICA".

**Ficheiros:** `00_pretextual/00_capa.md`, `00_pretextual/01_compromisso_autor.md`

---

### ID 8 — Ortografia "projecto" vs. "projeto"

**Apontamento:** [ORTOGRAFIA — Melhoria] Na grafia anterior ao AO90,
utilize «projecto» em vez de «projeto».

**Estado:** Já corrigido — nenhuma ocorrência de "projeto" (sem "c") no
relatório actual.

---

### ID 13 — Resumo em tom de expectativa

**Apontamento:** [RESULTADOS — Importante] O resumo termina em tom de
expectativa («Espera-se que...»), sem apresentar os resultados nem a
conclusão principal já existentes no Capítulo 4. Reformular no
pretérito, com metodologia, resultados e conclusão.

**Resolução (nesta conversa):** Reescrito o parágrafo final do resumo
(PT) e do abstract (EN) no pretérito, com os números reais do Capítulo 4
(CT07: 973/1044 tempos lectivos, 93,2%, 95,3s; zero conflitos por
construção; mecanismo de diagnóstico validado; limitação da comparação
com a distribuição manual assinalada).

**Ficheiro:** `00_pretextual/05_resumo_abstract.md`

---

### ID 14 — Palavras-chave redundantes com o título

**Apontamento:** [ESTRUTURA — Melhoria] As palavras-chave «geração
automática de horários académicos» e «inteligência artificial» repetem
termos do título. Substituir por descritores complementares (ex.:
«programação por restrições», «CP-SAT», «escalonamento universitário»).

**Resolução (nesta conversa):** Removidos os termos redundantes com o
título; lista final (PT): CP-SAT; Google OR-Tools; programação por
restrições (CSP); hard constraints (HC); soft constraints (SC);
escalonamento automático; optimização combinatória; ensino superior;
ISAF. Lista (EN) inclui adicionalmente UCTT.

**Ficheiro:** `00_pretextual/05_resumo_abstract.md`

---

### ID 20 — Lista de Figuras incompleta

**Apontamento:** [FIGURA/TABELA — Importante] A Lista de Figuras não
incluía as Figuras C.1–C.6 nem a Figura D.1. Gerar as listas
automaticamente e verificar correspondência exacta dos títulos.

**Resolução (nesta conversa):** Confirmado que gerar via
`\listoffigures`/`\listoftables` nativo do LaTeX mudaria o estilo visual
APA já adoptado (legendas manuais com `labelformat=empty`); decisão
tomada com o utilizador de manter o mecanismo manual e sincronizar a
lista. Todas as figuras (1–4, A.1, B.1, C.1–C.6) já estavam presentes;
corrigidos os títulos de 7 delas (A.1, B.1, C.1, C.3–C.6) que tinham
divergido do texto real do corpo.

**Ficheiro:** `00_pretextual/06_lista_figuras_tabelas.md`

---

### ID 19 — Figuras sem indicação de fonte (APA)

**Apontamento:** [FIGURA/TABELA — Melhoria] As legendas das Figuras 1–4
não indicam a fonte (ex.: «Nota. Elaboração própria»), exigido pela APA
7.ª edição mesmo para figuras originais do autor.

**Estado:** Já corrigido — todas as Figuras 1–4 têm "*Nota.* Criado pelo
autor (2026)." após a imagem.

**Ficheiro:** `04_analise_desenvolvimento/02_modelagem_sistema.md`

---

### ID 23 — Posição da legenda de tabela (APA)

**Apontamento:** [FIGURA/TABELA — Importante] Segundo a APA 7.ª edição,
o número e título da tabela devem ficar acima da tabela. As Tabelas 2–6
tinham a legenda depois do conteúdo; a Tabela 7 estava correcta.

**Resolução (nesta conversa):** Verificado, ao compilar o docx a partir
da fonte actual, que as 7 tabelas já têm a legenda `Table: ...`
correctamente posicionada antes do quadro (confirmado por inspecção do
XML do docx gerado). O ficheiro revisto pelo orientador era um build
anterior à reorganização do relatório. Nenhuma alteração de fonte foi
necessária.

**Ficheiro:** nenhum alterado (validação apenas).

---

### ID 28 — Ortografia "infraestrutura" vs. "infra-estrutura"

**Apontamento:** [ORTOGRAFIA — Melhoria] Na grafia anterior ao AO90,
utilize «infra-estrutura(s)» em vez de «infraestrutura(s)». Rever
globalmente.

**Resolução (nesta conversa):** Corrigidas as 5 ocorrências encontradas
por busca textual em todo o relatório.

**Ficheiros:** `01_introducao/01_contextualizacao.md` (×2),
`01_introducao/03_problema_investigacao.md`,
`04_analise_desenvolvimento/02_modelagem_sistema.md`,
`03_metodologia/10_ferramentas_tecnologias.md`

---

### ID 36 — Problemas sem evidência institucional

**Apontamento:** [PROBLEMA — Importante] Os problemas enumerados
(conflitos, sobreposições, janelas prolongadas) não estão sustentados
por evidências institucionais concretas. Fundamentar com dados do ISAF
(86 horários do Anexo A, «registos de conflitos» de 3.6); se os dados
não existirem, indicar isso expressamente. **Necessita confirmação pelo
autor.**

**Resolução (nesta conversa):** Identificada uma contradição real: a
Secção 3.6 afirmava que "registos de conflitos" tinham sido analisados,
mas as Secções 4.6/5.1 já assumiam como limitação que esse registo não
existe. **Confirmado pelo utilizador:** não existem registos
estruturados de conflitos. Corrigida a 3.6 para reflectir apenas os
dados reais (86 horários do Anexo A, relatos qualitativos de entrevista
e observação directa). Reescrita a Secção 1.3 fundamentando os problemas
com esses dados. Posteriormente enriquecida com uma estimativa verbal
concreta do Director da Área Académica sobre o tempo de distribuição
manual (ver ID 241).

**Ficheiros:** `01_introducao/03_problema_investigacao.md`,
`03_metodologia/06_tecnicas_recolha_dados.md`

---

### ID 39 — Pergunta de investigação incorpora tecnologias

**Apontamento:** [PROBLEMA — Importante] A pergunta de investigação
incorpora decisões tecnológicas (Flutter, FastAPI), que são meios, não
parte do problema científico. Sugestão de reformulação fornecida.
Notar que «eliminando conflitos... e reduzindo o tempo e o esforço»
pressupõe medição comparativa não realizada (cf. 4.6).

**Estado:** Já corrigido — a pergunta de investigação actual usa
exactamente a formulação sugerida pelo orientador ("Em que medida um
sistema baseado em técnicas de optimização combinatória e programação
por restrições é capaz de automatizar a geração de horários académicos
no ISAF, reduzindo conflitos de alocação e o tempo despendido..."), sem
menção a Flutter/FastAPI. Nesta conversa, o final da frase foi ainda
ajustado de "processo manual" para "distribuição manual de horários no
sistema de gestão escolar do ISAF" (apontamento de terminologia do
utilizador, não do orientador).

**Ficheiro:** `01_introducao/04_pergunta_investigacao.md`

---

### ID 43 — Hipótese sem código e hipóteses fundidas

**Apontamento:** [COERÊNCIA — Melhoria] A hipótese não estava
identificada com código, mas as Secções 4.6 e 5 já referem «H1».
Numerar (H1, H2, ...). O parágrafo contém, na prática, duas hipóteses
distintas (desempenho do motor de optimização e viabilidade da
integração tecnológica), que convém separar.

**Resolução (nesta conversa):** Separado o parágrafo único em H1
(desempenho do sistema vs. distribuição manual — a que 4.6/5 já se
referiam) e H2 (viabilidade técnica da integração
Flutter/FastAPI/CP-SAT). Acrescentada confirmação explícita de H2 na
Secção 4.6, que antes não tinha veredicto.

**Ficheiros:** `01_introducao/05_hipoteses_investigacao.md`,
`04_analise_desenvolvimento/06_discussao_resultados.md`

---

### ID 54 — Delimitação inclui Google Calendar API fora de âmbito

**Apontamento:** [COERÊNCIA — Crítico] A delimitação incluía a
integração com a Google Calendar API no âmbito do trabalho, mas a
Secção 4.3.3 e as Recomendações classificam-na como trabalho futuro
(RF17), não implementado.

**Estado:** Já corrigido — a delimitação actual declara explicitamente
que essa integração "fica fora do âmbito de implementação e validação
deste trabalho, identificada como trabalho futuro (RF17, Secção 4.1.3)".

**Ficheiro:** `01_introducao/07_delimitacao_estudo.md`

---

### ID 57 — Falta objecto de estudo / campo de acção

**Apontamento:** [ESTRUTURA — Melhoria] A introdução não explicita o
objecto de estudo nem o campo de acção, elementos habitualmente exigidos
na estrutura dos TFC em Angola, nem apresenta síntese metodológica antes
desta secção. Confirmar no regulamento institucional; se exigidos,
acrescentar secções próprias (ex.: objecto de estudo — o processo de
elaboração de horários académicos; campo de acção — o ISAF).

**Resolução (nesta conversa):** Confirmado no Regulamento TCC do ISAF
(`docs/exemplar_isaf/ISAF_Regulamento TCC.pdf`, Artigo 13.º, ponto 1,
alínea c) — "Relação do enquadramento teórico com o objecto de estudo")
que "objecto de estudo" é um critério formal de avaliação do TCC. O
Artigo 9.º (estrutura do corpo do documento) não exige uma secção
autónoma com esse nome; optou-se por não criar secção numerada nova, mas
por tornar o objecto de estudo e o campo de acção explícitos em texto
corrido na Introdução (parágrafo de abertura, antes da Secção 1.1).

**Ficheiro:** `01_introducao/01_contextualizacao.md`

---

### ID 62 — Ano de citação de Wren inconsistente (1995 vs. 1996)

**Apontamento:** [CITAÇÃO APA — Confirmar] Um trecho atribui a Wren o
ano de 1995, mas a mesma definição é citada adiante com o ano de 1996.
Verificar junto das fontes primárias e uniformizar. **Necessita
confirmação pelo autor.**

**Estado:** Já corrigido — ambas as ocorrências de Wren no relatório
actual usam 1996, uniformizado ("Wren, 1996, citado em @oudevrielink2019"
e "[Wren, 1996, como citado em @bashab2023]").

**Ficheiros:** `02_fundamentacao_teorica/01_processo_elaboracao_horarios.md`,
`02_fundamentacao_teorica/02_timetabling_problem.md`

---

### ID 72 — Citação narrativa com parênteses indevidos (Oude Vrielink)

**Apontamento:** [CITAÇÃO APA — Melhoria] Formato pouco convencional:
apelido entre parênteses mas verbo na 3.ª pessoa do plural concordando
com sujeito narrativo. Para citação narrativa, escrever sem parênteses.

**Estado:** Já corrigido — o texto actual usa "@oudevrielink2019,
citando Even (1975), reforçam que..." (formato narrativo correcto, sem
parênteses no apelido principal).

**Ficheiro:** `02_fundamentacao_teorica/02_timetabling_problem.md`

---

### ID 100, 101, 123 — Citações narrativas com parênteses indevidos (padrão geral)

**Apontamento:** [CITAÇÃO APA — Importante/Melhoria] Uso indevido de
parênteses em citações narrativas introduzidas por «segundo», «para»,
«com base em», «de acordo com», «enunciados por». Recomenda-se revisão
global.

**Estado:** Parcialmente corrigido em sessão anterior, com falso negativo
na validação — a verificação por `"Segundo ("` (parêntese literal) não
detectava o padrão real, que é `Segundo [@chave]` (colchetes do pandoc,
que renderizam como citação parentética mesmo em posição narrativa: "Segundo
(Gil, 2017)"). Detectado durante a revisão do PDF LaTeX completo (não
visível na validação anterior, feita só por grep de texto). Corrigidas
as 7 ocorrências reais: `Segundo [@gil2017]`, `Para [@marconilakatos2017]`,
`Com base em [@gil2017]`, `De acordo com [@marconilakatos2017] e [@gil2017]`,
`Conforme assinala [@sommerville2011]`, `Tal como destaca [@sommerville2011]`
— todas convertidas para `@chave` sem colchetes (formato narrativo correcto
do pandoc-citeproc).

**Ficheiros:** `03_metodologia/01_conceito.md`,
`03_metodologia/03_abordagem_pesquisa.md`,
`03_metodologia/04_classificacao_objectivos.md`,
`03_metodologia/06_tecnicas_recolha_dados.md`,
`04_analise_desenvolvimento/01_levantamento_requisitos.md`

---

### ID 111 — Amostra de entrevistas genérica

**Apontamento:** [METODOLOGIA — Crítico] Não se indica o número de
participantes nas entrevistas nem critérios de selecção (cargos,
quantos gestores/docentes, datas). **Necessita confirmação pelo autor.**

**Estado:** Já corrigido — a Secção 3.6 indica "dois elementos da
instituição, em Maio de 2026: o Director da Área Académica e um
Professor".

**Ficheiro:** `03_metodologia/06_tecnicas_recolha_dados.md`

---

### ID 117 — Observação directa sem datas/consentimento

**Apontamento:** [METODOLOGIA — Importante] Não é indicado o período da
observação directa, nº de sessões, nem se houve consentimento formal.
Exigível para a Secção 3.8 (considerações éticas).

**Estado:** Já corrigido — a Secção 3.6 indica o período ("no mesmo
período, Maio de 2026"); a Secção 3.8 trata explicitamente do
consentimento, assumindo como limitação que "o consentimento verbal
explícito... foi obtido apenas junto de um dos dois entrevistados, não
tendo sido formalmente solicitado ao segundo".

**Ficheiros:** `03_metodologia/06_tecnicas_recolha_dados.md`,
`03_metodologia/08_consideracoes_eticas.md`

---

### ID 132 — Tabela 7 incompleta (só Python/Dart)

**Apontamento:** [FORMATAÇÃO — Crítico] A Tabela 7 apresentava apenas
duas linhas (Python, Dart), mas o corpo cita FastAPI, PostgreSQL,
SQLModel, Pydantic, Firebase Authentication, OR-Tools/CP-SAT como
efectivamente utilizadas.

**Estado:** Já corrigido — a Tabela 7 actual tem 24 linhas, cobrindo
todas as camadas (linguagens, backend, frontend, persistência,
autenticação, infra-estrutura, controlo de versões, documentação,
ambiente de desenvolvimento).

**Ficheiro:** `03_metodologia/10_ferramentas_tecnologias.md`

---

### ID 139 — Glossário técnico incompleto

**Apontamento:** [FORMATAÇÃO — Importante] O Glossário (Tabela 1)
definia apenas dois termos (CB-CTT, CP-SAT Solver), mas o trabalho usa
dezenas de siglas não glossadas (UCTP, CSP, CP, HC, SC, RUP, MVP, DER,
DFD, RN, RF, RNF...).

**Estado:** Já corrigido — a Tabela 1 actual tem 9 termos (CB-CTT,
CP-SAT Solver, Hard Constraint, Soft Constraint, Modelagem Esparsa,
Variável de Folga, Tempo Lectivo, Job ID). Nesta conversa foi ainda
validada/corrigida separadamente a Lista de Abreviaturas e Siglas
(`07_lista_abreviaturas.md`), que cobre as restantes siglas gerais
(API, CP, CP-SAT, CSP, DER, IA, ISAF, ITC, RUP, UML, UCTP + HTTP, CRUD,
REST, JSON, PDF, MVP, NP, IEEE, MIP acrescentadas nesta conversa).

**Ficheiros:** `04_analise_desenvolvimento/01_levantamento_requisitos.md`,
`00_pretextual/07_lista_abreviaturas.md`

---

### ID 143 — Tabela 2 incompleta (RN01–RN02 apenas)

**Apontamento:** [REQUISITOS — Crítico] A Tabela 2 apresentava apenas
RN01–RN02, mas a Conclusão afirma «onze regras de negócio rastreáveis»
(RN03–RN11 citadas dispersamente).

**Estado:** Já corrigido — a Tabela 2 actual cobre RN01–RN12 (doze
regras; a Conclusão actual refere "doze regras de negócio
rastreáveis", coerente com a tabela).

**Ficheiro:** `04_analise_desenvolvimento/01_levantamento_requisitos.md`

---

### ID 146 — Tabela 3 incompleta (RF01–RF02 apenas)

**Apontamento:** [REQUISITOS — Crítico] A Tabela 3 apresentava apenas
RF01–RF02, mas a Conclusão refere «dezassete requisitos funcionais»
(RF03–RF17 citados no corpo).

**Estado:** Já corrigido — a Tabela 3 actual cobre RF01–RF17 na
íntegra.

**Ficheiro:** `04_analise_desenvolvimento/01_levantamento_requisitos.md`

---

### ID 149 — Tabela 4 incompleta (RNF01–RNF02 apenas)

**Apontamento:** [REQUISITOS — Crítico] A Tabela 4 apresentava apenas
RNF01–RNF02, mas a Conclusão refere «sete» requisitos não funcionais.

**Estado:** Já corrigido — a Tabela 4 actual cobre RNF01–RNF07 na
íntegra.

**Ficheiro:** `04_analise_desenvolvimento/01_levantamento_requisitos.md`

---

### ID 156 — Tabela 5 incompleta (UC01–UC02 apenas)

**Apontamento:** [DIAGRAMA — Crítico] A Tabela 5 apresentava apenas
UC01–UC02, mas o Capítulo 4 e o Apêndice B referem UC06–UC15.

**Estado:** Já corrigido — a Tabela 5 actual cobre UC01–UC15 na
íntegra.

**Ficheiro:** `04_analise_desenvolvimento/02_modelagem_sistema.md`

---

### ID 179 — Tabela 6 incompleta e "CT05" indefinido

**Apontamento:** [TESTES — Crítico] A Tabela 6 apresentava apenas
CT01–CT02; CT03/CT04 só estavam descritos em texto corrido. A Secção
4.6 refere um cenário «CT05» nunca definido em lado nenhum — possível
erro de digitação. **Necessita confirmação pelo autor.**

**Estado:** Já corrigido — a Tabela 6 actual cobre CT01–CT07 na
íntegra, incluindo CT05 (fluxo ponta-a-ponta / Golden Path) já
formalmente definido.

**Ficheiro:** `04_analise_desenvolvimento/05_testes_validacao.md`

---

### ID 182 — "CT05" citado nos resultados sem definição (repetição do 179)

**Apontamento:** [RESULTADOS — Crítico] Repetição do erro de CT05 sem
definição. **Necessita confirmação pelo autor.**

**Estado:** Já corrigido — CT05 está definido na Tabela 6 (ver ID 179).

**Ficheiro:** `04_analise_desenvolvimento/06_discussao_resultados.md`

---

### ID 220 — Repositório do projecto sem URL

**Apontamento:** [FORMATAÇÃO — Melhoria] É referido um «repositório do
projecto» como local de consulta do código-fonte, mas nunca se indica a
URL. Adicionar a referência (ou nota de rodapé/apêndice).

**Resolução (nesta conversa):** Acrescentada a URL
(`https://github.com/CristianoLourenco/timetable_problem_isaf`,
confirmada pelo utilizador) nas duas menções autónomas ao repositório
(Apêndice A e Anexo A). As restantes duas menções
(`05_conclusao/01_limitacoes_estudo.md` e
`04_analise_desenvolvimento/04_implementacao_sistema.md`) já remetiam
explicitamente para "cf. Apêndice A" / "referenciado no Apêndice A", pelo
que não necessitam de repetir a URL.

**Ficheiros:** `06_referencias_apendices/01_apendices.md`,
`06_referencias_apendices/02_anexos.md`

---

### ID 241 — Contradição entre objectivo 5 e Secção 4.6 (comparação não realizada)

**Apontamento:** [COERÊNCIA — Crítico] Uma afirmação (provavelmente no
objectivo específico 5 ou na Conclusão, na versão revista) contradizia
directamente a Secção 4.6, que reconhece que a comparação com os
horários manuais não foi realizada. Se não foi realizada, reformular
para «base de referência para uma futura comparação»; se foi realizada,
apresentar os resultados no Capítulo 4.

**Resolução (nesta conversa):** Para além da formulação já correcta do
objectivo 5 ("estabelecendo a base para uma futura comparação directa"),
foi incorporada uma nova evidência: uma estimativa verbal do Director da
Área Académica (menos de 10 minutos por turma, distribuição manual, sem
disponibilidades docentes por resolver — Secção 3.6). Esta estimativa
foi projectada de forma indicativa para a escala de CT07 (45 turmas:
~7,5 horas), e incorporada com ressalvas explícitas — "não constitui uma
medição documentada nem validada" — nas Secções 1.3, 3.6, 3.7, 4.6 e
5.1, todas declarando claramente a ausência de uma comparação
documentada rigorosa, eliminando qualquer leitura de que a comparação
tivesse sido realizada.

**Ficheiros:** `01_introducao/03_problema_investigacao.md`,
`03_metodologia/06_tecnicas_recolha_dados.md`,
`03_metodologia/07_tecnicas_analise_dados.md`,
`04_analise_desenvolvimento/06_discussao_resultados.md`,
`05_conclusao/01_limitacoes_estudo.md`

---

### ID 242 — Figura "D.1" sem "Anexo D" correspondente

**Apontamento:** [FORMATAÇÃO — Importante] A legenda identificava a
imagem como «Figura D.1», mas não existe «Anexo D» no documento; deveria
ser «Figura A.1» (por estar no Anexo A).

**Estado:** Já corrigido — a figura no Anexo A chama-se actualmente
"Figura A.1" no corpo e na lista.

**Ficheiro:** `06_referencias_apendices/02_anexos.md`

---

### ID 48 e 51 — Objectivo geral e objectivo específico 5

**ID 48** — [OBJECTIVO — Importante] Três verbos acumulados no
objectivo geral. **Já corrigido** — `01_introducao/06_objectivos.md` usa
um único verbo nuclear ("Desenvolver"); a formulação antiga
("desenvolver, implementar e validar") só sobrevivia na abertura do
Capítulo 5, corrigida nesta conversa.

**ID 51** — [OBJECTIVO — Crítico] "Este objectivo específico não foi
demonstrado no corpo do trabalho" — refere-se ao objectivo 5 (validação
comparativa). **Estado:** o objectivo 5 já foi reformulado para
"estabelecendo a base para uma futura comparação directa", exactamente
como o apontamento pede como alternativa à execução da comparação antes
da entrega. **Considerar resolvido**, salvo se o orientador exigir a
comparação efectiva em vez da reformulação (essa é uma opção que o
apontamento deixa em aberto: "reformule... ou execute a comparação
antes da entrega" — a decisão tomada foi reformular, não executar).

**Ficheiro:** `01_introducao/06_objectivos.md`, `05_conclusao/01_limitacoes_estudo.md`

---

### ID 142 — Paráfrase próxima de Vazquez e Simões (2016), grafia "objetivos"

**Apontamento:** [REDACÇÃO — Crítico] O parágrafo sobre requisitos de
negócio parece parafrasear (ou citar sem aspas) Vazquez e Simões (2016)
quase literalmente, e usa a grafia «objetivos» (sem "c"), inconsistente
com a grafia pré-AO90 do resto do documento. Se for citação directa,
delimitar com aspas e página; se for paráfrase, reescrever com
vocabulário próprio e ortografia adaptada.

**Resolução (nesta conversa):** Confirmado pelo utilizador tratar-se de
citação directa. Localizado o trecho exacto na fonte original
(`Engenharia de Requisitos: Software orientado ao negócio`, Vazquez &
Simões, 2016, p. 125, Secção 5.2 "Requisitos (ou necessidades) de
negócio") — página confirmada pelo utilizador a partir do PDF original.
O parágrafo foi reformulado como citação directa em bloco, delimitada
por aspas, com a grafia original da fonte preservada dentro das aspas
("objetivos", "projeto" — grafia PT-BR/AO90 do livro, correcta em
citação directa por não se alterar o texto citado) e a referência
"Vazquez & Simões (2016, p. 125)" antes da citação (formato narrativo,
verificado por compilação real com pandoc-citeproc/apa.csl). A frase
final do parágrafo (fora das aspas, em português europeu pré-AO90) liga
o conceito à Tabela 2 de regras de negócio do trabalho.

**Ficheiro:** `04_analise_desenvolvimento/01_levantamento_requisitos.md`

## Estado: já não se aplica (fonte reorganizada)

### ID 203 — Referência Harshalatha, Harshitha & Priyanka (2026) incompleta

**Apontamento:** [REFERÊNCIA APA — Crítico] A referência, citada como
suporte central da comparação CP-SAT vs. meta-heurísticas, estava
incompleta (falta periódico, DOI, etc.). **Necessita confirmação pelo
autor.**

**Estado:** Esta citação/referência já não existe em nenhum ficheiro do
relatório actual nem em `referencias.bib` — o trecho que a usava foi
removido ou reescrito com outras fontes na reorganização. Nada a
corrigir; documentado para memória, caso a referência tenha sido
substituída por outra que mereça a mesma verificação de completude.

## Resumo por estado

| Estado | Quantidade | IDs |
|---|---|---|
| Resolvido (nesta conversa) | 10 | 13, 14, 23, 28, 36, 43, 57, 142, 220, 241 |
| Já estava corrigido (fonte actual, fora desta conversa) | 26 | 2, 3, 8, 19, 20, 39, 54, 62, 72, 100, 101, 111, 117, 123, 132, 139, 143, 146, 149, 156, 179, 182, 242, 48, 51 |
| Já não se aplica (fonte reorganizada) | 1 | 203 |
| Pendente | 0 | — |

**Nota sobre "confirmação pelo autor":** os apontamentos IDs 36, 62,
111, 179, 182 e 203 tinham a marca «Necessita de confirmação pelo
autor/gestor» no documento original. Onde a resolução dependeu de uma
confirmação factual, essa confirmação foi registada explicitamente na
entrada correspondente (ex.: ID 36 — confirmado pelo utilizador que não
existem registos estruturados de conflitos). Nenhuma confirmação
institucional externa (ex.: junto do ISAF) foi obtida neste processo,
excepto a estimativa verbal do Director da Área Académica que já
constava do relato do próprio utilizador (ver ID 241).
