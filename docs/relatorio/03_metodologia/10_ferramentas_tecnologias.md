## 3.10 Ferramentas e tecnologias utilizadas

A Tabela 7 sintetiza as ferramentas e tecnologias efectivamente
utilizadas na concepção, implementação, teste e documentação do sistema,
organizadas por camada arquitectural (cf. Secção 4.3 para a
fundamentação de cada escolha).

Table: Tabela 7 --- Ferramentas e tecnologias utilizadas

| Camada | Ferramenta/Tecnologia | Versão | Finalidade |
|---|---|---|---|
| Linguagens | Python | 3.11+ | Backend e motor de optimização |
| | Dart | \>=3.10.0 | Frontend Flutter |
| Backend | FastAPI | 0.115.6 | Framework web assíncrono, camada de integração |
| | Pydantic | 2.10.4 | Validação e serialização de dados (schemas) |
| | SQLModel | 0.0.22 | ORM (mapeamento objecto-relacional) |
| | psycopg | 3.2.3 | Driver PostgreSQL |
| | Google OR-Tools (CP-SAT) | 9.11.4210 | Motor de optimização por Programação por Restrições |
| | openpyxl | 3.1.5 | Importação em massa via ficheiros Excel (RF06--RF08) |
| | Uvicorn | 0.34.0 | Servidor ASGI |
| | pytest | 8.3.4 | Testes automatizados do backend |
| Frontend | Flutter | SDK \>=3.10.0 | Framework de interface multiplataforma |
| | Provider | ^6.0.5 | Gestão de estado global |
| | GoRouter | ^15.1.0 | Navegação/routing |
| | Dio | ^5.9.2 | Cliente HTTP |
| | file_picker | ^8.1.4 | Selecção de ficheiros (importação Excel) |
| Persistência | PostgreSQL | 16 | Sistema de gestão de base de dados relacional |
| Autenticação | Firebase Authentication | --- | Gestão de identidade e emissão de ID Tokens (RN09/RN10) |
| Infra-estrutura | Docker / Docker Compose | --- | Contentorização do PostgreSQL em ambiente de desenvolvimento |
| Controlo de versões | Git / GitHub | --- | Versionamento do código-fonte, histórico por fase (cf. Secção 3.9.2) |
| Documentação | Markdown, Pandoc, LibreOffice | --- | Redacção e compilação deste relatório para DOCX/PDF |
| | PlantUML | --- | Geração dos diagramas UML e entidade-relacional (cf. Secção 4.2) |
| Ambiente de desenvolvimento | Visual Studio Code | --- | Editor de código utilizado no desenvolvimento de ambas as camadas |
