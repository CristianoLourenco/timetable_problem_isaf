1. INTRODUÇÃO

A gestão de horários académicos constitui uma das tarefas operacionais
mais complexas e críticas no funcionamento das instituições de ensino
superior. Trata-se de um processo que exige a articulação simultânea de
múltiplas variáveis interdependentes, como disciplinas, docentes,
turmas, salas, períodos lectivos, restrições curriculares e limitações
de infraestrutura. Quando realizado manualmente, esse processo tende a
consumir tempo excessivo, gerar conflitos de alocação e comprometer a
eficiência da gestão académica.

Do ponto de vista computacional, a elaboração de horários enquadra-se na
classe dos problemas de optimização combinatória, sendo frequentemente
classificada como um problema NP-difícil ou NP-Hard na literatura de
escalonamento académico [@oudevrielink2019; @abdipoor2023; @bashab2023]. Isto significa que o número de combinações
possíveis cresce exponencialmente à medida que aumenta a dimensão da
instituição, tornando inviável a procura exaustiva de soluções óptimas
em contextos reais. Em consequência, muitas instituições enfrentam
atrasos, retrabalho e dificuldades operacionais na organização dos seus
horários.

Neste cenário, a aplicação de técnicas de Inteligência Artificial e de
optimização apresenta-se como uma alternativa promissora para
automatizar a geração de horários e melhorar a qualidade das soluções
produzidas. Assim, o presente trabalho propõe o desenvolvimento de um
sistema inteligente para a geração automática de horários académicos no
Instituto Superior de Administração e Finanças (ISAF), com o objectivo
de apoiar a gestão institucional, reduzir conflitos e optimizar a
utilização dos recursos disponíveis.

1.1 Contextualização do tema

A geração de horários académicos constitui um problema central na gestão
universitária, pois envolve a coordenação eficiente de recursos humanos,
físicos e temporais num ambiente caracterizado por múltiplas restrições
[@oudevrielink2019; @bashab2023]. No ensino superior, a
construção de horários não se limita à simples distribuição de aulas ao
longo da semana; trata-se de um processo estratégico que influencia a
organização pedagógica, a utilização das infraestruturas, a satisfação
dos docentes e a experiência académica dos estudantes. Neste contexto, a
aplicação de técnicas computacionais e de Inteligência Artificial
apresenta-se como uma alternativa robusta para enfrentar a complexidade
inerente ao problema e promover soluções mais rápidas, coerentes e
ajustadas à realidade institucional.

1.2 Justificativa

A pertinência deste trabalho articula-se em três dimensões
complementares:

1.  **Do ponto de vista académico,** o tema insere-se numa área de
    investigação activa e com significativa produção científica
    internacional, designada por Educational Timetabling. A aplicação de
    meta-heurísticas e de técnicas de optimização à resolução deste
    problema tem sido amplamente estudada na literatura. Contudo, a
    maioria dos estudos existentes foi desenvolvida em contextos
    europeus, norte-americanos ou asiáticos, revelando uma lacuna
    relevante no que respeita ao contexto africano e, em particular, ao
    contexto angolano. O presente trabalho contribui para reduzir essa
    lacuna, ao procurar adaptar abordagens computacionais ao contexto
    específico das instituições angolanas de ensino superior.

2.  **Do ponto de vista tecnológico**, a escolha da arquitectura baseada
    em Flutter, FastAPI e PostgreSQL reflecte uma aposta em tecnologias
    modernas, abertas e amplamente documentadas. Esta combinação permite
    desenvolver uma solução multiplataforma, com boa capacidade de
    integração, desempenho adequado e potencial de expansão futura.

3.  **Do ponto de vista institucional**, o sistema proposto responde a
    uma necessidade concreta identificada no ISAF. A automatização da
    geração de horários poderá reduzir significativamente o tempo
    despendido neste processo, diminuir conflitos de alocação, melhorar
    a utilização das salas disponíveis e aumentar a satisfação de
    docentes e estudantes. Para além disso, a solução poderá servir de
    referência para outras instituições angolanas com necessidades
    semelhantes, contribuindo para a modernização da gestão académica no
    ensino superior.

1.3 Problema de investigação

O processo de elaboração de horários académicos no ISAF, à semelhança do
que ocorre em muitas instituições de ensino superior angolanas, é
realizado de forma predominantemente manual ou com recurso a ferramentas
não concebidas especificamente para esse fim. Este processo envolve a
gestão simultânea de várias restrições, muitas vezes contraditórias, o
que origina dificuldades operacionais e reduz a eficiência da gestão
académica. Entre os principais problemas observados, destacam-se:

-   Conflitos de disponibilidade de docentes;

-   Sobreposição de salas;

-   Concentração excessiva de aulas em determinados dias;

-   Janelas horárias prolongadas para docentes e estudantes;

-   Subutilização ou utilização ineficiente das infraestruturas
    disponíveis.

Estes problemas não são apenas operacionais, pois afectam directamente a
qualidade do processo de ensino-aprendizagem, a satisfação de docentes e
estudantes e a imagem institucional. Além disso, a natureza combinatória
do problema torna inviável a sua resolução eficiente por meios
exclusivamente manuais, sobretudo em contextos de média e grande
dimensão. Deste modo, coloca-se a necessidade de desenvolver uma solução
capaz de automatizar este processo e produzir horários consistentes,
viáveis e ajustados à realidade do ISAF.

1.4 Pergunta de investigação

Em que medida um sistema inteligente baseado em Inteligência Artificial,
desenvolvido com Flutter e FastAPI, é capaz de automatizar a geração de
horários académicos no ISAF, eliminando conflitos de alocação e
reduzindo o tempo e o esforço despendidos no processo manual?

1.5 Hipóteses de investigação

Parte-se da hipótese de que a utilização de um sistema inteligente
(capaz de distribuir uniformemente os horários) baseado em técnicas de
optimização combinatória e programação por restrições, é capaz de gerar
horários académicos com menor incidência de conflitos, melhor
aproveitamento das salas e redução significativa do tempo de elaboração,
quando comparado ao processo manual. Admite-se, igualmente, que a
integração entre tecnologias como **Flutter**, **FastAPI** e um
**algoritmo de optimização** em Python contribuirá para a criação de uma
solução tecnicamente viável, funcional e adaptada às necessidades
institucionais do ISAF.

1.6 Objectivos

1.6.1 Objectivo geral

Desenvolver, implementar e validar um sistema inteligente para a geração
automática de horários académicos no ISAF, recorrendo a técnicas de
optimização combinatória e a uma arquitectura tecnológica composta por
Python/FastAPI no back-end e Flutter na interface de utilizador.

1.6.2 Objectivos específicos

1.  Realizar o levantamento e a análise dos requisitos funcionais e não
    funcionais do sistema, identificando e formalizando as restrições do
    problema de elaboração de horários.

2.  Modelar o problema de elaboração de horários como um problema de
    optimização combinatória e implementar um motor de geração de
    horários em Python.

3.  Desenvolver uma API REST com FastAPI e estruturar a persistência dos
    dados académicos necessários ao funcionamento do sistema.

4.  Construir a interface de utilizador em Flutter para gestão das
    entidades académicas, visualização dos horários e exportação dos
    resultados.

5.  Validar o sistema por meio de testes funcionais e de desempenho,
    comparando os resultados com o processo manual.

1.7 Delimitação do estudo

O presente trabalho delimita-se ao contexto institucional do ISAF,
focando-se na geração automática de horários semanais para o ensino
superior com base nas restrições reais da instituição. Do ponto de vista
tecnológico, a solução circunscreve-se ao desenvolvimento de um sistema
funcional com interface em Flutter, motor de optimização em Python e
integração com a Google Calendar API para distribuição e sincronização
dos horários gerados.

1.8 Estrutura do trabalho

O presente trabalho encontra-se estruturado em cinco capítulos
principais. O primeiro capítulo apresenta a introdução, incluindo a
contextualização do tema, a justificativa, o problema e a pergunta de
investigação, as hipóteses, os objectivos e a delimitação do estudo. O
segundo capítulo desenvolve a fundamentação teórica, abordando os
conceitos, abordagens e tecnologias relacionadas com a geração
automática de horários. O terceiro capítulo apresenta a metodologia
adoptada na investigação e no desenvolvimento do sistema. O quarto
capítulo destina-se à análise, ao desenvolvimento e à discussão dos
resultados obtidos. Por fim, o quinto capítulo apresenta as conclusões,
as limitações do estudo e as recomendações para trabalhos futuros.