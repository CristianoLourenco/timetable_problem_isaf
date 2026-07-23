# **RESUMO**

Este trabalho aborda o desenvolvimento de um sistema inteligente para a
geração automática de horários académicos no Instituto Superior de
Administração e Finanças (ISAF). O problema de elaboração de horários
constitui uma tarefa complexa, caracterizada pela necessidade de
conciliar múltiplas restrições relacionadas com docentes, turmas,
disciplinas, salas e períodos lectivos. O estudo tem como objectivo
desenvolver uma solução computacional capaz de automatizar este
processo, reduzir conflitos de alocação e melhorar a eficiência da
gestão académica. Metodologicamente, a investigação enquadra-se como
aplicada, de abordagem mista e carácter exploratório-descritivo,
recorrendo à pesquisa bibliográfica, documental e ao estudo de caso. Em
termos tecnológicos, a solução proposta integra Flutter no
desenvolvimento da interface, FastAPI no back-end, o solver Google
OR-Tools CP-SAT no motor de optimização, PostgreSQL na camada de
persistência e Firebase Authentication na gestão de identidade e
controlo de acessos. 

A validação foi conduzida através de sete cenários de teste progressivos, incluindo um cenário à escala real do ISAF (45 turmas, 104 docentes, 25 salas, dados de produção do 1.º semestre de 2025/2026). Em todos os cenários testados, o sistema gerou horários sem qualquer conflito de professor, turma ou sala, garantia obtida por construção do modelo CP-SAT. No cenário real, o sistema alocou 973 dos 1044 tempos lectivos esperados (93,2%) em 95,3 segundos (~1 minuto e 30 segundos), deixando o défice residual explicitamente sinalizado para resolução manual pelo Gestor, por escassez de recursos qualificados disponíveis. O mecanismo de diagnóstico estrutural foi igualmente validado, distinguindo correctamente entre inviabilidade genuína e esgotamento do tempo de resolução, eliminando falhas silenciosas. A validação obtida circunscreve-se, no entanto, à correcção matemática do sistema e à sua aplicabilidade aos dados reais do ISAF, não incluindo uma comparação directa de desempenho com a distribuição manual de horários no sistema de gestão escolar actualmente em uso na instituição.

Palavras-chave: CP-SAT; Google OR-Tools; programação por restrições (CSP); hard constraints (HC); soft constraints (SC); escalonamento automático; optimização combinatória; ensino superior; ISAF.

# **ABSTRACT**

This study addresses the development of an intelligent system for the
automatic generation of academic timetables at the Instituto Superior de
Administração e Finanças (ISAF). Timetabling is a complex task because
it requires the simultaneous management of multiple constraints related
to lecturers, classes, courses, rooms, and time slots. The main
objective of this research is to develop a computational solution
capable of automating this process, reducing allocation conflicts, and
improving academic management efficiency. Methodologically, the study is
classified as applied research, with a mixed-methods and
exploratory-descriptive approach, supported by bibliographic research,
documentary analysis, and a case study. From a technological
perspective, the proposed solution integrates Flutter for the user
interface, FastAPI for the back-end, the Google OR-Tools CP-SAT solver
as the optimization engine, PostgreSQL as the persistence layer, and
Firebase Authentication for identity and access management.

Validation was
carried out through seven progressive test scenarios, including a
real-scale scenario based on ISAF's own data (45 classes, 104 lecturers,
25 rooms, production data from the 2025/2026 first semester). Across all
tested scenarios, the system generated timetables with zero conflicts
among lecturers, classes, and rooms, a guarantee ensured by construction
of the CP-SAT model. In the real-scale scenario, the system allocated
973 of the 1044 expected weekly teaching slots (93.2%) in 95.3 seconds (approx. 1 minute and 30 seconds),
leaving the residual gap explicitly flagged for manual resolution by the
academic manager, due to a shortage of qualified available resources.
The structural diagnosis mechanism was also validated, correctly
distinguishing genuine infeasibility from solver time exhaustion and
eliminating silent failures. The validation obtained is nonetheless
limited to the mathematical correctness of the system and its
applicability to ISAF's real data, and does not include a direct
performance comparison with the manual timetable distribution carried
out within the school management system currently used by the
institution.

Keywords: CP-SAT; Google OR-Tools; constraint programming (CSP); hard
constraints; soft constraints; university course timetabling (UCTT);
combinatorial optimization; higher education; ISAF.
