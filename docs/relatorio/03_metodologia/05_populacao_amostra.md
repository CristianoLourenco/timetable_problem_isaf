## 3.5 População e amostra

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
resolução de um problema concreto e identificado num contexto real [@gil2017].

### 3.5.1 Dados de referência para validação do motor de optimização

Importa distinguir dois tipos de dados institucionais recolhidos junto
do ISAF (Secção 3.6): os dados de **saída** (86 horários manuais
vigentes em 2025/2026, recolhidos por análise documental e reproduzidos
no Anexo A) e os dados de **entrada estruturados** que o motor de
optimização exige como parâmetros formais --- disponibilidade semanal
por docente, capacidade e tipologia de cada sala, grade curricular
formalizada por curso/ano/semestre e qualificação docente por
disciplina. Os primeiros foram efectivamente disponibilizados pela
instituição; os segundos não estavam, à data do desenvolvimento,
formalizados em nenhum sistema de informação --- existiam apenas de
forma implícita no critério dos responsáveis pela elaboração manual dos
horários, não sendo por isso extraíveis directamente dos horários finais
em formato PDF/imagem.

Nesta fase inicial de desenvolvimento e validação matemática do sistema, o
sistema foi por isso testado com conjuntos de dados sintéticos
controlados, de dimensão crescente (Secção 4.5, CT01--CT06), delineados
segundo a mesma lógica de escalonamento por complexidade utilizada nas
International Timetabling Competitions (ITC), referência global para a
comparação de algoritmos de escalonamento académico [@abdipoor2023;
@bashab2023]. Numa fase posterior, foi extraído manualmente, a partir da
grade curricular oficial do ISAF (2025/2026), um conjunto de dados de
entrada estruturado e correspondente a instâncias reais da instituição
--- 45 turmas do 1.º semestre, 104 docentes e respectivas qualificações
--- permitindo validar o sistema directamente contra os dados de produção
do ISAF (Secção 4.5, CT07), embora sem ainda cobrir a totalidade dos
86 horários recolhidos nem constituir, por si só, a comparação de
desempenho descrita na Secção 3.7 (cf. limitações, Secção 5.1).
