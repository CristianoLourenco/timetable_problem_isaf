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

Após a realização de testes utilizando dados reais do ISAF, conseguimos provar uma melhora aignificativa na redução do tempo para geração dos horários académicos com a duração de ~2 minutos, o sistema foi capaz de gerar 70% dos horários de forma autônoma, sem conflitos, deixando o remanescente a mercê de intervenção por parte do Gestor através do próprio sistema, devido a escassez de recursos necessários para o processo.

Palavras-chave: programação por restrições (CP); hard constraints (HC); soft constraints (SC); escalonamento automático; optimização combinatória; ensino superior; ISAF.

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
Firebase Authentication for identity and access management. It is
expected that the system will contribute to the modernization of
institutional processes, the optimization of available resources, and
the improvement of the experience of students, lecturers, and academic
managers.

Keywords: automatic academic timetable generation; artificial
intelligence; combinatorial optimization; higher education; ISAF.
