## 2.2 O Problema de Escalonamento de Horários (Timetabling Problem)

### 2.2.1 Definição formal do problema

O problema de elaboração de horários insere-se numa classe mais ampla de
problemas de escalonamento. @bashab2023 estabelecem a
hierarquia conceptual deste domínio, distinguindo scheduling
(escalonamento), timetabling (elaboração de horários), sequencing
(sequenciamento) e rostering (escalonamento de recursos humanos) como
subproblemas distintos dentro da área de planeamento sujeito a
restrições. Especificamente, o timetabling é definido como a alocação,
sujeita a restrições, de recursos dados a objectos posicionados no
espaço-tempo, de forma a satisfazer o maior número possível de um
conjunto de objectivos desejáveis [Wren, 1996, como citado em @bashab2023]. No contexto universitário, o University Course Timetabling
Problem (UCTP) pode ser formalmente enunciado da seguinte forma
[@abdipoor2023]:

**Dado**:

-   Um conjunto de eventos E = {e₁, e₂, e₃, \..., e\|E\|}

-   Um conjunto de períodos de tempo T = {t₁, t₂, t₃, \..., t\|T\|} (com
    \|T\| = 45 nos conjuntos de referência --- 9 períodos por dia × 5
    dias por semana)

-   Um conjunto de salas R = {r₁, r₂, r₃, \..., r\|R\|}

-   Um conjunto de estudantes S = {s₁, s₂, s₃, \..., s\|S\|}

-   Um conjunto de características de salas F = {f₁, f₂, f₃, \...,
    f\|F\|}

-   Um conjunto de dias D = {d₁, d₂, d₃, \..., d\|D\|} (tipicamente os
    dias úteis, com \|D\| = 5)

**Encontrar**: uma atribuição (um horário) de E eventos (com S
estudantes) a R salas (com F características) e T períodos de tempo (ao
longo de D dias) que minimize as violações de restrições.

### 2.2.2 Classificação: School Timetabling vs. University Timetabling

O domínio do educational timetabling divide-se em dois ramos principais:
o escalonamento escolar (school timetabling) e o escalonamento
universitário (university timetabling). O escalonamento universitário
subdivide-se, por sua vez, em dois subproblemas distintos: o University
Course Timetabling Problem (UCTP ou UCTTP) e o University Examination
Timetabling Problem (UETP ou UETTP) [@abdipoor2023].

@bashab2023 clarificam esta distinção, definindo o course
timetabling como um problema de atribuição multidimensional no qual
estudantes e professores são alocados a disciplinas, e os eventos ---
encontros individuais entre estudantes e professores --- são atribuídos
a salas e períodos de tempo. O examination timetabling, por sua vez,
consiste na atribuição de exames a um número limitado de períodos de
tempo disponíveis, de forma a evitar conflitos ou sobreposições.

No âmbito do UCTP, a literatura identifica ainda duas variantes
principais: o Curriculum-Based Course Timetabling Problem (CB-CTP) e o
Post-Enrollment Course Timetabling Problem (PE-CTP). A principal
diferença entre ambas reside na fonte dos conflitos: no CB-CTP, os
conflitos emergem do currículo publicado pela instituição, enquanto no
PE-CTP decorrem dos dados de inscrição dos estudantes [@abdipoor2023].

@oudevrielink2019 observam ainda que a investigação em
escalonamento universitário avançou de forma mais acelerada do que a
investigação em escalonamento escolar, em grande medida porque o
primeiro beneficiou de esforços de padronização através das
International Timetabling Competitions (ITC), que permitiram a
comparação de metodologias num conjunto de referência comum.

### 2.2.3 Complexidade computacional: problemas NP-Hard

O UCTP pertence à classe dos problemas de optimização combinatória (COP
--- Combinatorial Optimization Problems), caracterizados por um espaço
de soluções que cresce exponencialmente com a dimensão do problema
[@bashab2023]. Uma vez que existem R\^E formas de alocação
possíveis no UCTP, o tempo computacional necessário aumenta de forma
exponencial com o crescimento do número de eventos, salas e períodos
considerados [@abdipoor2023].

Consequentemente, o UCTP é classificado como um problema NP-Hard
(Non-deterministic Polynomial-time hard), o que torna inviável a
aplicação de algoritmos exactos, em particular para instâncias de maior
dimensão [@abdipoor2023]. @oudevrielink2019, citando
Even (1975), reforçam que o problema de elaboração de horários é um
problema NP-hard e NP-completo, dependendo das restrições consideradas,
e que soluções viáveis, eficientes ou rápidas --- todos sinónimos de
tempo polinomial --- não se aplicam a este domínio. @bashab2023
acrescentam que as características desta classe de problemas implicam
que: (1) ainda não existe um método capaz de os resolver em tempo
razoável para qualquer instância; (2) o tempo computacional necessário
cresce exponencialmente com a dimensão do problema; e (3) a solução
exacta é apenas alcançável para instâncias modestas, sendo que a maioria
das abordagens adopta algoritmos de aproximação que, não garantindo a
solução óptima, procuram obter soluções suficientemente boas.

### 2.2.4 Hard Constraints e Soft Constraints

As restrições envolvidas no UCTP classificam-se genericamente em dois
tipos: restrições rígidas (Hard Constraints --- HC) e restrições
flexíveis (Soft Constraints --- SC) [@abdipoor2023; @bashab2023]. As restrições rígidas são condições obrigatórias que
determinam a viabilidade de uma solução --- a sua violação torna o
horário inválido. As restrições flexíveis são condicionantes opcionais
que determinam a qualidade de uma solução --- a sua satisfação é
desejável, mas não imprescindível para a validade do horário [@abdipoor2023].

@abdipoor2023 apresentam o catálogo formal das restrições
envolvidas no UCTP padrão. No que respeita às restrições rígidas,
destacam-se: nenhum estudante pode ser atribuído a mais do que uma
disciplina no mesmo período (HC1); a sala deve satisfazer as
características exigidas pela disciplina (HC2); o número de estudantes
inscritos numa disciplina não deve exceder a capacidade da sala (HC3);
não é permitida mais do que uma disciplina por período em cada sala
(HC4); uma disciplina só pode ser atribuída a determinados períodos
pré-definidos (HC5); todas as aulas de uma disciplina devem ser
escalonadas (HC7); as aulas de disciplinas pertencentes ao mesmo
currículo ou leccionadas pelo mesmo docente devem ser escalonadas em
períodos distintos (HC8); e, se o docente de uma disciplina não estiver
disponível num determinado período, nenhuma aula dessa disciplina pode
ser escalonada nesse período (HC9).

Relativamente às restrições flexíveis, os mesmos autores identificam,
entre outras: um estudante não deve ter apenas uma disciplina num
determinado dia (SC1); um estudante não deve ter mais de duas
disciplinas consecutivas (SC2); um estudante não deve ter disciplinas
escalonadas no último período do dia (SC3); as aulas de cada disciplina
devem ser distribuídas pelo número mínimo de dias estabelecido (SC5); as
aulas pertencentes a um mesmo currículo devem ser adjacentes entre si
(SC6); e todas as aulas de uma disciplina devem ser leccionadas na mesma
sala (SC7).

@bashab2023 sublinham que o objectivo da elaboração de um
horário viável consiste em satisfazer todas as restrições rígidas e,
simultaneamente, minimizar as violações das restrições flexíveis. A
função de custo de uma solução candidata S é tipicamente calculada como
a soma ponderada das violações de restrições rígidas e flexíveis: CS =
WSC × \|SC\| + WHC × \|HC\|, sendo que uma solução que viole qualquer
restrição rígida é considerada inviável e, portanto, sem valor prático
[@abdipoor2023].
