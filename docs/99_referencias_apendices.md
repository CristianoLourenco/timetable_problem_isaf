REFERÊNCIAS

Abdipoor, S., Yaakob, R., Goh, S. L., & Abdullah, S. (2023).
Meta-heuristic approaches for the University Course Timetabling Problem.
*Intelligent Systems with Applications*, 19, 200253.
<https://doi.org/10.1016/j.iswa.2023.200253>

Bashab, A., Ibrahim, A. O., Hashem, I. A. T., Aggarwal, K., Mukhlif, F.,
Ghaleb, F. A., & Abdelmaboud, A. (2023). Optimization techniques in
university timetabling problem: Constraints, methodologies, benchmarks,
and open issues. *Computers, Materials & Continua*, 74(3), 6461--6484.
<https://doi.org/10.32604/cmc.2023.034051>

Bittner, K., & Spence, I. (2002). *Use case modeling*. Addison-Wesley.

Booch, G., Rumbaugh, J., & Jacobson, I. (2005). *UML: Guia do usuário*
(2.ª ed.). Elsevier.

Chen, P. P. (1976). The entity-relationship model --- Toward a unified
view of data. *ACM Transactions on Database Systems*, 1(1), 9--36.
<https://doi.org/10.1145/320434.320440>

Cockburn, A. (2000). *Writing effective use cases*. Addison-Wesley.

Dechter, R. (2003). *Constraint processing*. Morgan Kaufmann.

Dijkstra, E. W. (1974). On the role of scientific thought.

El-Sakka, T. (2015). University course timetable using constraint
satisfaction and optimization. *International Journal of Computing
Academic Research (IJCAR)*, 4(3), 83--95.

Gil, A. C. (2017). *Como elaborar projetos de pesquisa* (6.ª ed.).
Atlas.

Guedes, G. T. A. (2011). *UML 2: Uma abordagem prática* (2.ª ed.).
Novatec.

Harshalatha, K., Harshitha, N., & Priyanka, C. M. (2026). Intelligent
timetable and workload manager using constraint programming (CP-SAT
solver). Cambridge Institute of Technology (VTU), Bengaluru, India.

IEEE. (1998). *IEEE recommended practice for software requirements
specifications* (IEEE Std 830-1998). IEEE.

ISO/IEC/IEEE. (2011). *Systems and software engineering --- Life cycle
processes --- Requirements engineering* (ISO/IEC/IEEE 29148:2011). ISO.

Kruchten, P. (2003). *Introdução ao RUP: Rational Unified Process*.
Ciência Moderna.

Lakatos, E. M., & Marconi, M. de A. (2017). *Fundamentos de metodologia
científica* (8.ª ed.). Atlas.

Martin, R. C. (2017). *Clean Architecture: A Craftsman\'s Guide to
Software Structure and Design*. Pearson.

Object Management Group. (2017). *OMG Unified Modeling Language (OMG
UML), Version 2.5.1*. <https://www.omg.org/spec/UML/2.5.1>

Oude Vrielink, R. A., Jansen, E. A., Hans, E. W., & van Hillegersberg,
J. (2019). Practices in timetabling higher education institutions: A
systematic review. *Annals of Operations Research*, 275(1), 145--160.
<https://doi.org/10.1007/s10479-017-2688-8>

Perron, L., Didier, F., & Gay, S. (2023). The CP-SAT-LP solver \[Invited
talk\]. In *Proceedings of the 29th International Conference on
Principles and Practice of Constraint Programming (CP 2023)*, LIPIcs,
Vol. 280, Article 3. <https://doi.org/10.4230/LIPIcs.CP.2023.3>

Prodanov, C. C., & Freitas, E. C. de. (2013). *Metodologia do trabalho
científico* (2.ª ed.). Feevale.

Russell, S., & Norvig, P. (2021). *Artificial intelligence: A modern
approach* (4th ed.). Pearson.

Sommerville, I. (2011). *Software engineering* (9th ed.). Pearson.

Vazquez, C. E., & Simões, G. S. (2016). *Engenharia de requisitos:
Software orientado ao negócio*. Brasport.

Wren, A. (1996). Scheduling, timetabling and rostering --- A special
relationship? In E. Burke & P. Ross (Eds.), *Practice and theory of
automated timetabling* (pp. 46--75). Springer.

APÊNDICES

Apêndice A --- Código-fonte do Motor de
Optimização

**\[PLACEHOLDER --- Inserir excertos comentados do módulo CP-SAT após
conclusão da implementação do backend\]**

Apêndice B --- Especificação Textual dos Casos
de Uso

UC06 --- Importar Dados em Massa via Excel

**Ator Principal:** Gestor Académico/Secretaria

**Pré-condições:** Gestor autenticado (UC13); ficheiro Excel no formato
institucional esperado.

**Gatilho:** O Gestor selecciona \"Importar Dados\" e escolhe a
entidade-alvo.

**Fluxo Principal:** 1. O Gestor selecciona a entidade e carrega o
ficheiro Excel. 2. O sistema invoca UC07 --- Validar Dados Importados
(\<\<include\>\>). 3. O sistema apresenta o resultado da validação
(registos válidos, inválidos, duplicados) para confirmação. 4. O Gestor
confirma a gravação. 5. O sistema aplica a regra de idempotência (RF08).
6. O sistema grava os registos novos e apresenta o relatório final.

**Fluxo Alternativo A1:** Cancelamento antes da confirmação --- nenhum
dado é gravado.

**Fluxo de Excepção E1:** Ficheiro em formato inválido --- o sistema
rejeita e informa o formato esperado.

**Garantia de Sucesso:** Registos válidos e não duplicados persistidos
na base de dados.

**Garantia Mínima:** Nenhum registo parcialmente importado --- operação
transaccional.

UC08 --- Disparar Geração de Horário

**Ator Principal:** Gestor Académico/Secretaria

**Pré-condições:** Dados, mestre, completos e disponibilidades
registadas; Gestor autenticado (UC13).

**Gatilho:** O Gestor selecciona \"Gerar Horário\".

**Fluxo Principal:** 1. O Gestor solicita a geração. 2. O sistema cria
um Job assíncrono e devolve um Job ID (RNF02). 3. O sistema executa o
motor CP-SAT em segundo plano, aplicando RN01--RN09 e a função
objectivo. 4. O motor devolve uma solução óptima ou quase-óptima \[Ponto
de Extensão: \"Sem Solução Viável\"\]. 5. O sistema associa o resultado
ao Job ID e marca o estado como concluído.

**Extensão condicional (passo 4):** Se o solver não conseguir satisfazer
as restrições após relaxamento das soft constraints, invoca UC09
(\<\<extend\>\>).

**Garantia de Sucesso:** Horário completo persistido e disponível para
consulta (UC11, UC12).

**Garantia Mínima:** Mesmo em INFEASIBLE, o Job é marcado como Falhado
com o motivo registado --- o sistema nunca falha silenciosamente
(RNF03).

UC13 --- Autenticar-se

**Atores:** Gestor Académico/Secretaria; Professor

**Pré-condição:** O actor possui conta registada no Firebase
Authentication.

**Fluxo Principal:** 1. O actor submete email e password. 2. A aplicação
Flutter envia as credenciais ao Firebase Authentication (SDK nativo). 3.
O Firebase valida e devolve um ID Token. 4. A aplicação Flutter anexa o
ID Token a cada pedido subsequente ao backend FastAPI. 5. O backend
valida o ID Token através do Firebase Admin SDK antes de processar
qualquer pedido (RN09).

**Fluxo de Excepção E1:** Credenciais inválidas --- mensagem de erro
genérica, sem indicar qual campo falhou.

**Fluxo de Excepção E2:** Token expirado --- backend devolve HTTP 401; o
SDK tenta renovação silenciosa; novo login só é exigido se essa
renovação falhar.

**Garantia Mínima:** Nenhuma sessão é criada sem validação bem-sucedida
da identidade.

Apêndice C --- Capturas de Ecrã do Sistema

**\[PLACEHOLDER --- Inserir capturas de ecrã da interface Flutter
(autenticação, gestão de entidades, grelha de horário) e da documentação
Swagger da API após conclusão do frontend\]**

ANEXOS

**\[PLACEHOLDER --- Inserir, caso aplicável, documentos institucionais
de suporte, como o modelo de horário manual actualmente em uso no
ISAF.**
