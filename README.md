# SysEmpréstimos - Sistema de Gestão Integrada de Crédito e Cobrança

### 📝 Visão Geral
Este sistema foi desenvolvido para centralizar e automatizar a administração de carteiras de crédito. A plataforma oferece fluxos de trabalho otimizados: uma visão de **Gerente** (focada em análise de KPIs e recuperação de ativos) e uma área de **Cliente** (focada em transparência financeira). O sistema integra visualizações analíticas em tempo real e suporte nativo ao **Modo Escuro**.





https://github.com/user-attachments/assets/263728c4-373c-4e54-bdb0-8b8752feffe5


### 🎯 Objetivos do Projeto
O propósito é fornecer uma infraestrutura que simplifica operações financeiras detalhadas. Através da automação de encargos, dashboards interativos e uma régua de cobrança via WhatsApp, o projeto visa maximizar a eficiência operacional e reduzir a inadimplência, mantendo uma experiência de usuário moderna.

### 🗄️ Bases de Dados
O projeto utiliza um banco de dados relacional para persistência de usuários, cargos e configurações do sistema
*   **Sincronização Automatizada:** O sistema possui integração total entre a interface web e o banco de dados. Ao cadastrar um novo usuário pelo site, o **ID é gerado automaticamente pelo banco (Auto-increment)** e os dados são persistidos via SQLAlchemy.
*   **DBeaver:** Utilizado como cliente de banco de dados para visualização em tempo real dos registros, estruturação de tabelas e execução de queries de auditoria para validar a integridade dos cálculos financeiros.

### 🚀 Etapas do Projeto
*   **Arquitetura Backend:** Implementação de rotas otimizadas em Flask com autenticação segura por perfil.
*   **Business Intelligence (BI):** Dashboards administrativos com KPIs críticos de rentabilidade e risco.
*   **Portal do Cliente:** Experiência self-service com monitoramento de progresso, extratos dinâmicos e notificações reativas.
*   **Omnichannel de Cobrança:** Módulo integrado para acionamento via WhatsApp, agilizando a negociação de débitos.
*   **Refinamento de Interface:** UI Premium com Modo Escuro, sistema de busca global e validações dinâmicas.
*   **Governança (RBAC):** Controle de acessos baseado em funções, segmentando permissões entre diversos níveis hierárquicos.
*   **Core Financeiro:** Centralização de algoritmos para processamento de encargos e formatação monetária padronizada.

### 🛠️ Tecnologias e Bibliotecas

**Linguagens de Programação:**
*   **Python:** Lógica de backend e processamento de dados.
*   **JavaScript:** Interatividade no frontend e renderização de gráficos.
*   **HTML5 & CSS3:** Estrutura e estilização personalizada com variáveis dinâmicas.

**Frameworks e Bibliotecas Backend:**
*   **Flask:** Micro-framework web.
*   **SQLAlchemy:** ORM para manipulação do banco de dados.
*   **Jinja2:** Motor de templates para renderização de HTML dinâmico.

**Frontend e Bibliotecas JS:**
*   **Bootstrap 5:** Framework de design responsivo.
*   **Chart.js:** Biblioteca para geração de gráficos de barras, linhas e roscas.
*   **DataTables:** Manipulação e filtragem avançada de tabelas.
*   **Bootstrap Notify:** Sistema de notificações flutuantes (toasts).
*   **Font Awesome:** Biblioteca de ícones profissionais.

**APIs e Integrações:**
*   **WhatsApp Web API:** Link direto para ações rápidas de cobrança e suporte.

### 🔐 Segurança
O sistema prioriza a proteção dos dados dos usuários:
*   **Sessões Seguras:** Gerenciamento de login via Flask-Session para controle de acesso por perfil.

### 📂 Estrutura do Projeto
```text
├── sistema/
│   ├── models/          # Definição das tabelas e lógica de banco
│   ├── views/           # Rotas e controle das páginas
│   ├── templates/       # Arquivos HTML (Jinja2)
│   └── static/          # CSS, JS e Imagens
├── app.py               # Ponto de entrada da aplicação
├── config.py            # Configurações do banco de dados e chaves
└── mapeamento_roles.py  # Definição dos níveis de acesso
```

### ✅ Conclusão
O SysEmpréstimos consolida-se como uma solução completa para o mercado de crédito, unindo o controle estratégico do **Gerente** à transparência necessária para o **Cliente**. Essa distinção entre a gestão de lucros e a facilidade de acompanhamento financeiro torna a plataforma ideal para o uso real em larga escala. O foco em usabilidade, reforçado pelo **Modo Escuro** e pelos **gráficos analíticos**, garante uma ferramenta eficiente, clara e pronta para novos desafios.
