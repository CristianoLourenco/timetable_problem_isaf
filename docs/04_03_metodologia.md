3. METODOLOGIA

3.1 Conceito

Segundo [@gil2017], a metodologia científica é um procedimento racional
e sistemático que tem como objectivo fornecer respostas aos problemas
propostos, sendo requerida quando não se dispõe de informação suficiente
para responder a um problema com base apenas no conhecimento prévio.
Para [@marconilakatos2017], o método científico consiste num conjunto
de actividades sistemáticas e racionais que, com maior segurança e
economia, permite alcançar o objectivo --- conhecimentos válidos e
verdadeiros ---, traçando o caminho a ser seguido, detectando erros e
auxiliando as decisões do investigador.

3.2 Natureza da pesquisa

@gil2017 classifica as pesquisas em duas grandes categorias quanto à
sua finalidade:

1.  **Pesquisa Básica**: estudos que têm como propósito preencher uma
    lacuna no conhecimento e ampliar o saber, sem preocupação imediata
    com benefícios práticos ou de aplicação. Destina-se essencialmente
    ao avanço do conhecimento científico.

2.  **Pesquisa Aplicada**: estudos elaborados com a finalidade de
    resolver problemas identificados no âmbito das sociedades ou numa
    situação específica, orientados para a aquisição de conhecimentos
    com vista a uma aplicação ou solução prática.

O presente trabalho enquadra-se na categoria de pesquisa aplicada, dado
que visa desenvolver um sistema concreto em resposta a um problema
identificado.

3.3 Abordagem da pesquisa

Segundo [@gil2017] e Tashakkori e Creswell (2007, apud Gil, 2017), as
pesquisas distinguem-se metodologicamente pela natureza do tratamento e
análise dos dados:

1.  **Pesquisa Quantitativa**: apresenta os resultados em termos
    numéricos, baseando-se num enfoque tradicional e estruturado. É
    adequada para amostragens representativas e generalizações
    estatísticas;

2.  **Pesquisa Qualitativa**: apresenta os resultados mediante
    descrições verbais e textuais, adoptando um enfoque
    interpretativista em que a realidade deve ser entendida segundo a
    perspectiva dos actores que a vivenciam. É adequada para o estudo
    aprofundado da experiência vivida e das relações sociais;

3.  **Pesquisa de Métodos Mistos**: combina elementos de abordagens
    quantitativas e qualitativas num único estudo, com o propósito de
    ampliar e aprofundar o entendimento e a corroboração dos resultados,
    especialmente quando uma única fonte de dados se revela
    insuficiente.

O presente trabalho adopta uma abordagem **Mista**, privilegiando a
rigorosidade de modelos matemáticos e a análise descritiva dos
resultados encontrados pelo mesmo.

3.4 Classificação quanto aos objectivos

Com base em [@gil2017], as pesquisas classificam-se em:

1.  **Pesquisas exploratórias**: procuram proporcionar maior
    familiaridade com o problema, tornando-o mais explícito ou ajudando
    a construir hipóteses. Envolvem frequentemente levantamento
    bibliográfico e entrevistas com pessoas experientes no problema
    pesquisado;

2.  **Pesquisas descritivas**: têm como objectivo a descrição exacta das
    características de uma determinada população ou fenómeno, podendo
    também identificar possíveis associações ou relações entre
    variáveis;

3.  **Pesquisas explicativas**: são as que mais aprofundam o
    conhecimento, pois visam identificar os factores que determinam ou
    contribuem para a ocorrência de fenómenos, explicando as
    causalidades.

O presente estudo é de natureza exploratória e descritiva: exploratória
por aprofundar o conhecimento sobre o problema em análise; descritiva
por caracterizar os processos, requisitos e funcionamento do sistema
proposto.

3.5 População e amostra

[@marconilakatos2017] e @gil2017 definem população ou universo como
o conjunto total de seres, elementos ou factos que apresentam pelo menos
uma característica comum relevante para a delimitação da pesquisa. A
amostra, por sua vez, é definida como uma porção convenientemente
seleccionada do universo, utilizada quando a dimensão da pesquisa torna
impossível ou inviável a investigação da totalidade dos elementos. A
população deste estudo é constituída pelo conjunto de instituições de
ensino superior que enfrentam o problema de escalonamento de horários
académicos, com especial incidência no contexto angolano. Para efeitos
de desenvolvimento e validação do sistema, adopta-se como unidade de
análise principal o Instituto Superior de Administração e Finanças
(ISAF), dada a acessibilidade aos processos institucionais e a
relevância do problema identificado.

Dado o carácter aplicado e delimitado da investigação, recorreu-se a uma
amostra não-probabilista intencional, seleccionada por conveniência e
relevância para os objectivos do estudo. Esta escolha justifica-se pelo
facto de a investigação não visar a generalização estatística, mas sim a
resolução de um problema concreto e identificado num contexto real ([@gil2017]).

3.5.1 Dados de referência para validação do
motor de optimização

Na fase de desenvolvimento e validação matemática do motor de
optimização, e na ausência de dados institucionais formalmente
disponibilizados, o sistema foi testado com base em conjuntos de dados
representativos derivados dos benchmarks internacionais utilizados nas
International Timetabling Competitions (ITC), referência global para a
comparação de algoritmos de escalonamento académico [@abdipoor2023; @bashab2023].

Estes conjuntos de referência correspondem a instâncias reais de
instituições europeias e internacionais, com dimensões variáveis que
permitem testar a escalabilidade do motor em diferentes cenários:
pequeno (3 turmas, 15 disciplinas, 10 docentes), médio (5 turmas, 30
disciplinas, 25 docentes), grande (20 turmas, 80 disciplinas, 60
docentes) e cenário de stress (60 turmas, 200 disciplinas, 100
docentes). Esta estratégia é consistente com a abordagem adoptada por
[@harshalatha2026] e [@elsakka2015] na validação dos seus
respectivos sistemas.

3.6 Técnicas e instrumentos de recolha de
dados

De acordo com [@marconilakatos2017] e [@gil2017], as técnicas de
recolha de dados constituem os procedimentos sistemáticos utilizados
para a obtenção de informação relevante ao problema de investigação.
Para o presente trabalho foram adoptadas as seguintes técnicas:

1.  **Análise documental**: Foram analisados documentos institucionais
    do ISAF, incluindo os horários vigentes, as grelhas curriculares por
    curso, os regulamentos académicos e os registos de conflitos de
    alocação de períodos anteriores. Esta análise permitiu formalizar as
    restrições rígidas e flexíveis específicas da instituição, que
    constituem o input do motor de optimização.

2.  **Observação directa**: Foi realizada observação assistemática do
    processo manual de elaboração de horários actualmente praticado no
    ISAF, com o objectivo de identificar os fluxos de trabalho reais, os
    pontos de falha recorrentes e os critérios tácitos utilizados pelos
    responsáveis na resolução de conflitos.

3.  **Revisão bibliográfica sistemática**: Procedeu-se à revisão da
    literatura científica internacional sobre o University Course
    Timetabling Problem, com enfoque nas abordagens de Programação por
    Restrições e no Google OR-Tools CP-SAT, conforme desenvolvido no
    Capítulo 2.

3.7 Técnicas de análise de dados

O tratamento e a análise dos dados recolhidos seguiram duas abordagens
complementares, adequadas à natureza Mista (Quantitativa e Qualitativa)
e aplicada da investigação.

**Análise de conteúdo:** Aplicada ao material recolhido nas entrevistas
e na análise documental, esta técnica permitiu identificar e categorizar
as restrições do problema de escalonamento específicas do ISAF, que
foram posteriormente formalizadas como Hard Constraints e Soft
Constraints no modelo matemático do sistema (cf. Secção 4.1).

**Análise comparativa de desempenho**: Para a avaliação do sistema
desenvolvido, foi adoptada uma estratégia de comparação directa entre os
resultados produzidos pelo motor CP-SAT e os horários gerados
manualmente pelo ISAF. Os indicadores de comparação incluem o número de
conflitos de alocação, o tempo de processamento e a qualidade das Soft
Constraints satisfeitas (nomeadamente a distribuição equilibrada de
carga horária e o agrupamento pedagógico em blocos de 90 minutos). Esta
abordagem é consistente com a metodologia adoptada por [@harshalatha2026] e [@elsakka2015].

3.8 Considerações éticas

A condução desta investigação observou os princípios éticos fundamentais
enunciados por [@gil2017], designadamente o respeito pela autonomia e
dignidade dos participantes, a ponderação rigorosa entre riscos e
benefícios, e a garantia de relevância social do trabalho desenvolvido.
Em concreto:

Os dados institucionais recolhidos --- incluindo horários e estruturas
curriculares --- foram utilizados exclusivamente para fins académicos e
de desenvolvimento do sistema, sem divulgação de informações pessoais ou
institucionalmente sensíveis;

O sistema desenvolvido não processa dados pessoais de estudantes para
além da afectação a turmas, não configurando tratamento de dados
pessoais nos termos das disposições legais aplicáveis;

O presente trabalho foi elaborado com observância das normas de
integridade académica, com citação e referenciação completas de todas as
fontes consultadas, conforme a Declaração de Originalidade que o
antecede.