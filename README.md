# 🚀 Flutter App Creator (FAC)
**A ferramenta de linha de comando mais completa para criar aplicativos Flutter profissionais**

---

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Flutter](https://img.shields.io/badge/Flutter-3.0+-blue.svg)](https://flutter.dev)
[![Firebase](https://img.shields.io/badge/Firebase-Ready-orange.svg)](https://firebase.google.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-1.2.0-red.svg)](CHANGELOG.md)

*Gere aplicativos Flutter completos, escaláveis e prontos para produção em minutos*

[Instalação](#instalação) • [Uso Rápido](#uso-rápido) • [Documentação](#documentação) • [Exemplos](#exemplos) • [Contribuir](#contribuir)

</div>

---

## 📋 Índice

- [Sobre o FAC](#sobre-o-fac)
- [✨ Funcionalidades](#-funcionalidades)
- [📦 Instalação](#-instalação)
- [🚀 Uso Rápido](#-uso-rápido)
- [📝 Configuração YAML](#-configuração-yaml)
- [🏗️ Arquitetura](#-arquitetura)
- [🔧 CLI Commands](#-cli-commands)
- [📱 Apps Gerados](#-apps-gerados)
- [🔥 Funcionalidades Avançadas](#-funcionalidades-avançadas)
- [📊 Dashboard e Analytics](#-dashboard-e-analytics)
- [🛡️ Segurança e Autenticação](#-segurança-e-autenticação)
- [📁 Estrutura do Projeto](#-estrutura-do-projeto)
- [🌍 Roadmap](#-roadmap)
- [📄 Licença](#-licença)

---

## 🎯 Sobre o FAC

O **Flutter App Creator (FAC)** é uma ferramenta revolucionária que automatiza a criação de aplicativos Flutter completos e profissionais. Com uma única configuração YAML, você pode gerar:

- 📱 **Apps multiplataforma** (Android, iOS, Web, Windows, macOS, Linux)
- 🏗️ **Arquitetura Clean** com separação de responsabilidades
- 🔐 **Autenticação completa** (Firebase, Local, Social)
- 💾 **Persistência híbrida** (Firebase + SQLite sincronizado)
- 📊 **Dashboard interativo** com gráficos e KPIs
- 🔍 **Sistema de filtros** dinâmicos e exportação
- 📋 **CRUD automático** para todos os módulos
- 🎨 **UI/UX profissional** com Material Design 3
- 🧪 **Testes automatizados** (Unit, Widget, Integration)
- 🚀 **Deploy automático** para todas as plataformas

---

## ✨ Funcionalidades

### 🔥 Core Features

| Funcionalidade | Status | Descrição |
|---|---|---|
| **Geração de Apps** | ✅ **Disponível** | Criação completa de apps Flutter |
| **Módulos CRUD** | ✅ **Disponível** | Operações Create, Read, Update, Delete automáticas |
| **Autenticação** | ✅ **Disponível** | Firebase Auth, SQLite local, Social Login |
| **Persistência Híbrida** | 🚧 **Em desenvolvimento** | Firebase + SQLite com sincronização automática |
| **Módulos Aninhados** | 🚧 **Em desenvolvimento** | Hierarquia de módulos (Pedidos > Itens) |
| **Sistema de Filtros** | 🚧 **Em desenvolvimento** | Filtros dinâmicos configuráveis via YAML |
| **Import/Export** | 🚧 **Em desenvolvimento** | Importação CSV/XLSX com mapeamento visual |
| **Tours Interativos** | 🚧 **Em desenvolvimento** | Guias passo-a-passo configuráveis |
| **Geração de Ícones** | 🚧 **Em desenvolvimento** | Ícones automáticos para todas as plataformas |

### 📊 Advanced Features

- **Dashboard Customizável**: Gráficos, KPIs e widgets configuráveis
- **Relacionamentos Complexos**: 1:1, 1:N, N:N entre entidades
- **Permissões Granulares**: Sistema de roles e permissões por módulo
- **Soft Delete**: Exclusão lógica configurável
- **Validações Avançadas**: Validação de campos em tempo real
- **Notificações Push**: Firebase Cloud Messaging integrado
- **Internacionalização**: Suporte multi-idioma automático
- **Temas Dinâmicos**: Material Design 3 com cores personalizáveis
- **PWA Ready**: Progressive Web App com service workers
- **CI/CD Integration**: GitHub Actions, GitLab CI configurados

---

## 📦 Instalação

### Pré-requisitos

- **Python 3.8+** instalado
- **Flutter SDK 3.0+** configurado
- **Firebase CLI** (opcional, para integração Firebase)
- **Git** para controle de versão

### Instalação via PyPI

```bash
pip install flutter-app-creator
```

### Instalação via Código Fonte

```bash
git clone https://github.com/avnt-sistemas/fac.git
cd fac
pip install -e .
```

### Verificar Instalação

```bash
fac --version
fac doctor  # Verifica dependências
```

---

## 🚀 Uso Rápido

### 1. Criar Novo Projeto

```bash
# Criar com configuração interativa
fac new meu-app --interactive

# Criar com arquivo de configuração
fac new meu-app --config config.yaml

# Criar com template pré-definido
fac new meu-app --template ecommerce
```

### 2. Adicionar Módulos

```bash
# Adicionar módulo simples
fac generate module --name Produto --fields "nome:String,preco:double"

# Adicionar módulo com relacionamentos
fac generate module --name Pedido --config pedido.yaml

# Adicionar módulo aninhado
fac generate module --name ItemPedido --parent Pedido
```

### 3. Configurar Firebase

```bash
# Setup automático do Firebase
fac firebase setup --auto

# Configurar projeto existente
fac firebase setup --project meu-projeto-123
```

### 4. Executar o App

```bash
cd meu-app
flutter run
```

---

## 📝 Configuração YAML

### Exemplo Completo

```yaml
# config.yaml
app:
  name: "Minha Loja Virtual"
  package: "com.minhaempresa.loja"
  description: "E-commerce completo com Flutter"
  version: "1.0.0"
  
  # 🎨 Configuração visual
  logo: "assets/logo.png"  # Será redimensionado automaticamente
  theme:
    primary_color: "#1976D2"
    secondary_color: "#424242"
    accent_color: "#FF4081"
    font_family: "Roboto"
    dark_mode: true

# 🔐 Autenticação
auth:
  enabled: true
  provider: "firebase"  # firebase, local, hybrid
  social_login:
    google: true
    apple: true
    facebook: true
  features:
    email_verification: true
    password_reset: true
    two_factor: true

# 💾 Persistência
persistence:
  enabled: true
  provider: "hybrid"  # firebase, sqlite, hybrid
  offline_first: true
  sync_interval: 30  # segundos
  
# 📱 Módulos
modules:
  # Módulo principal
  - name: "Categoria"
    icon: "category"
    show_in_menu: true
    fields:
      - name: "nome"
        type: "String"
        required: true
        unique: true
      - name: "descricao"
        type: "String"
      - name: "imagem"
        type: "image"
        max_size: "2MB"
    
    # 🔍 Filtros configuráveis
    filters:
      - name: "status"
        type: "select"
        options: ["ativo", "inativo"]
        label: "Status da Categoria"
      - name: "data_criacao"
        type: "date_range"
        label: "Período de Criação"
    
    # 📤 Configurações de export
    export:
      csv: true
      xlsx: true
      pdf: true
      
    # 🎯 Tour da tela
    tour:
      enabled: true
      steps:
        - target: "add_button"
          title: "Nova Categoria"
          content: "Clique aqui para adicionar uma nova categoria de produtos"
        - target: "filter_panel"
          title: "Filtros"
          content: "Use os filtros para encontrar categorias específicas"

  # Módulo com relacionamento
  - name: "Produto"
    icon: "shopping_bag"
    show_in_menu: true
    fields:
      - name: "nome"
        type: "String"
        required: true
      - name: "descricao"
        type: "String"
        max_length: 500
      - name: "preco"
        type: "double"
        required: true
        min_value: 0.01
        format: "currency"
      - name: "categoria"
        type: "reference"
        reference: "Categoria"
        required: true
      - name: "imagens"
        type: "List<image>"
        max_count: 5
      - name: "ativo"
        type: "bool"
        default: true
      - name: "tags"
        type: "List<String>"
    
    # Relacionamentos
    relationships:
      - type: "1:N"
        with: "ItemPedido"
        inverse: "produto"
    
    # Permissões por role
    permissions:
      create: ["admin", "gerente"]
      read: ["*"]
      update: ["admin", "gerente"]
      delete: ["admin"]
    
    soft_delete: true
    
    # Filtros avançados
    filters:
      - name: "categoria"
        type: "reference"
        reference: "Categoria"
      - name: "preco"
        type: "range"
        min: 0
        max: 10000
        format: "currency"
      - name: "ativo"
        type: "boolean"
      - name: "tags"
        type: "multi_select"
        source: "dynamic"  # Busca tags existentes

  # Módulo aninhado
  - name: "Pedido"
    icon: "receipt"
    show_in_menu: true
    fields:
      - name: "numero"
        type: "String"
        auto_generate: true
        pattern: "PED-{YYYY}{MM}{DD}-{###}"
      - name: "cliente"
        type: "reference"
        reference: "Usuario"
      - name: "data_pedido"
        type: "DateTime"
        default: "now"
      - name: "status"
        type: "enum"
        options: ["pendente", "confirmado", "enviado", "entregue", "cancelado"]
        default: "pendente"
      - name: "valor_total"
        type: "double"
        calculated: true
        formula: "SUM(itens.valor_total)"
    
    # Módulo filho
    children:
      - name: "ItemPedido"
        show_in_menu: false
        icon: "shopping_cart"
        fields:
          - name: "produto"
            type: "reference"
            reference: "Produto"
            required: true
          - name: "quantidade"
            type: "int"
            required: true
            min_value: 1
          - name: "preco_unitario"
            type: "double"
            auto_fill: "produto.preco"
          - name: "valor_total"
            type: "double"
            calculated: true
            formula: "quantidade * preco_unitario"

# 📊 Dashboard
dashboard:
  enabled: true
  auto_refresh: 60  # segundos
  widgets:
    - type: "kpi"
      title: "Total de Produtos"
      data_source: "Produto"
      operation: "count"
      filter: "ativo = true"
      size: "small"
      
    - type: "kpi"
      title: "Vendas do Mês"
      data_source: "Pedido"
      operation: "sum"
      field: "valor_total"
      filter: "data_pedido >= startOfMonth"
      format: "currency"
      size: "medium"
      
    - type: "line_chart"
      title: "Vendas por Dia"
      data_source: "Pedido"
      x_axis: "data_pedido"
      y_axis: "valor_total"
      group_by: "day"
      period: "last_30_days"
      
    - type: "bar_chart"
      title: "Produtos por Categoria"
      data_source: "Produto"
      group_by: "categoria.nome"
      operation: "count"
      
    - type: "pie_chart"
      title: "Status dos Pedidos"
      data_source: "Pedido"
      group_by: "status"
      operation: "count"

# 🔔 Notificações
notifications:
  enabled: true
  provider: "firebase"  # firebase, local
  types:
    - name: "novo_pedido"
      title: "Novo Pedido"
      body: "Pedido #{numero} recebido"
      trigger: "Pedido.created"
      recipients: ["admin", "gerente"]
    - name: "produto_estoque_baixo"
      title: "Estoque Baixo"
      body: "Produto {nome} com estoque baixo"
      trigger: "Produto.estoque < 5"

# 🌍 Configurações globais
settings:
  internationalization:
    enabled: true
    default_locale: "pt_BR"
    supported_locales: ["pt_BR", "en_US", "es_ES"]
  
  offline_mode:
    enabled: true
    cache_duration: 24  # horas
    
  analytics:
    enabled: true
    provider: "firebase"  # firebase, google_analytics
    
  crash_reporting:
    enabled: true
    provider: "firebase"  # firebase, sentry
```

---

## 🏗️ Arquitetura

O FAC gera apps seguindo **Clean Architecture** com as seguintes camadas:

```
lib/
├── 🎯 app/                    # Configuração do app
├── 🏢 core/                   # Núcleo compartilhado
├── 💾 data/                   # Camada de dados
├── 🎯 domain/                 # Regras de negócio
└── 🎨 features/               # Features do app
    ├── auth/                  # Autenticação
    ├── dashboard/             # Dashboard
    └── [módulos]/             # Módulos gerados
        ├── data/              # Repositórios, DataSources
        ├── domain/            # Entidades, UseCases
        └── presentation/      # UI, Controllers
```

### 🔧 Tecnologias Utilizadas

- **State Management**: BLoC + Provider
- **Dependency Injection**: GetIt
- **HTTP Client**: Dio com interceptors
- **Local Storage**: Hive + Shared Preferences
- **Firebase**: Auth, Firestore, Storage, Analytics
- **Charts**: FL Chart
- **Forms**: Reactive Forms
- **Testing**: Mockito, Bloc Test

---

## 🔧 CLI Commands

### Comandos Principais

```bash
# 📱 Projeto
fac new <nome>                 # Criar novo projeto
fac generate module <nome>     # Adicionar módulo
fac generate screen <tipo>     # Gerar tela customizada
fac generate test <módulo>     # Gerar testes

# 🔥 Firebase
fac firebase setup             # Configurar Firebase
fac firebase deploy            # Deploy para Firebase Hosting
fac firebase functions         # Deploy Cloud Functions

# 🔧 Utilitários
fac doctor                     # Verificar dependências
fac clean                      # Limpar caches
fac analyze                    # Análise de código
fac build                      # Build para produção

# 📊 Analytics
fac stats                      # Estatísticas do projeto
fac dependencies               # Analisar dependências
fac unused                     # Código não utilizado
```

### Opções Avançadas

```bash
# Templates personalizados
fac new meu-app --template ecommerce
fac new meu-app --template saas
fac new meu-app --template social

# Configurações específicas
fac new meu-app --auth firebase --db hybrid --theme dark

# Geradores específicos
fac generate module Produto --with-api --with-tests
fac generate crud Categoria --fields nome,descricao
fac generate form Pedido --validation
```

---

## 📱 Apps Gerados

### 📱 Estrutura das Telas

Cada módulo gera automaticamente:

| Tela | Funcionalidades |
|---|---|
| **📋 Listagem** | Busca, filtros, ordenação, paginação, export |
| **➕ Cadastro** | Formulário validado, upload de imagens |
| **✏️ Edição** | Formulário pré-preenchido, validações |
| **👁️ Visualização** | Dados detalhados, ações rápidas |
| **🔍 Filtros** | Filtros dinâmicos baseados no YAML |

### 🎨 Componentes UI

- **Cards responsivos** com design moderno
- **Formulários inteligentes** com validação em tempo real
- **Componentes de upload** com preview
- **Diálogos padronizados** para confirmações
- **Snackbars** para feedback
- **Loading states** em todas as operações
- **Error handling** robusto
- **Temas dark/light** automáticos

---

## 🔥 Funcionalidades Avançadas

### 💾 Persistência Híbrida

```yaml
persistence:
  provider: "hybrid"
  offline_first: true
  sync_strategy: "smart"  # smart, immediate, manual
  conflict_resolution: "client_wins"  # client_wins, server_wins, merge
```

**Como funciona:**
- 📱 **SQLite local**: Para dados offline e performance
- ☁️ **Firebase**: Para sincronização e backup
- 🔄 **Sync automático**: Quando conexão estiver disponível
- ⚡ **Smart caching**: Cache inteligente baseado em uso

### 🔍 Sistema de Filtros

```yaml
filters:
  - name: "data_periodo"
    type: "date_range"
    label: "Período"
    default: "last_30_days"
    
  - name: "status"
    type: "multi_select"
    options: ["ativo", "inativo", "pendente"]
    
  - name: "categoria"
    type: "reference"
    reference: "Categoria"
    multiple: true
    
  - name: "preco"
    type: "range"
    min: 0
    max: 1000
    step: 10
    format: "currency"
```

### 📤 Import/Export Avançado

**Export Features:**
- 📊 **CSV, XLSX, PDF** com formatação
- 🔍 **Baseado em filtros** ativos
- 📈 **Gráficos inclusos** no PDF
- 📱 **Agendamento** de exports

**Import Features:**
- 📁 **Upload** de CSV/XLSX
- 🗺️ **Mapeamento visual** de colunas
- ✅ **Validação** em tempo real
- 📊 **Preview** antes da importação
- 📋 **Relatório** detalhado pós-import
- 💾 **Histórico** de importações

### 🎯 Tours Interativos

```yaml
tour:
  enabled: true
  auto_start: "first_visit"  # first_visit, manual, never
  steps:
    - target: "#add-button"
      title: "Adicionar Registro"
      content: "Clique aqui para adicionar um novo item"
      position: "bottom"
      
    - target: ".filter-panel"
      title: "Filtros"
      content: "Use os filtros para encontrar itens específicos"
      position: "left"
      
    - target: "[data-export]"
      title: "Exportar Dados"
      content: "Exporte seus dados para Excel ou PDF"
      position: "top"
```

---

## 📊 Dashboard e Analytics

### 📈 Widgets Disponíveis

| Widget | Descrição | Configuração |
|---|---|---|
| **KPI** | Métricas principais | `operation: count/sum/avg/min/max` |
| **Line Chart** | Gráfico de linhas temporal | `x_axis, y_axis, group_by` |
| **Bar Chart** | Gráfico de barras | `group_by, operation` |
| **Pie Chart** | Gráfico de pizza | `group_by, operation` |
| **Donut Chart** | Gráfico de rosca | `group_by, operation, inner_radius` |
| **Table** | Tabela de dados | `fields, filters, limit` |
| **Map** | Mapa com marcadores | `lat_field, lng_field, popup_fields` |

### 📊 Analytics Automático

- 📱 **Screen tracking** automático
- 👆 **Event tracking** em botões importantes
- ⏱️ **Performance monitoring**
- 💥 **Crash reporting**
- 👥 **User analytics** (com consentimento)

---

## 🛡️ Segurança e Autenticação

### 🔐 Providers de Auth

| Provider | Features | Status |
|---|---|---|
| **Firebase** | Social login, 2FA, Email verification | ✅ |
| **Local** | SQLite, Biometrics, Pin code | ✅ |
| **Hybrid** | Firebase + Local fallback | 🚧 |

### 🔒 Sistema de Permissões

```yaml
permissions:
  roles:
    admin:
      - "*.create"
      - "*.read"
      - "*.update"
      - "*.delete"
      - "dashboard.admin"
      
    manager:
      - "produtos.*"
      - "categorias.*"
      - "pedidos.read"
      - "dashboard.sales"
      
    user:
      - "produtos.read"
      - "categorias.read"
      - "perfil.*"

modules:
  - name: "Produto"
    permissions:
      create: ["admin", "manager"]
      read: ["*"]
      update: ["admin", "manager"]
      delete: ["admin"]
```

### 🔐 Segurança

- 🔒 **Encryption**: Dados sensíveis criptografados
- 🔑 **JWT**: Tokens seguros com expiração
- 🛡️ **Input validation**: Sanitização automática
- 🚫 **Rate limiting**: Proteção contra spam
- 📝 **Audit logs**: Log de todas as operações

---

## 📁 Estrutura do Projeto

```
flutter_app_creator/
├── 📁 cli/                    # Interface CLI
│   ├── commands/              # Comandos disponíveis
│   ├── validators/            # Validadores de entrada
│   └── interactive/           # Modo interativo
├── 📁 config/                 # Configurações
│   ├── default_config.yaml    # Config padrão
│   ├── schema.json           # Schema de validação
│   └── templates/            # Templates de config
├── 📁 generators/             # Geradores de código
│   ├── app_generator.py      # Gerador principal
│   ├── auth_generator.py     # Autenticação
│   ├── crud_generator.py     # CRUD automático
│   ├── dashboard_generator.py # Dashboard
│   ├── filter_generator.py   # Sistema de filtros
│   ├── import_generator.py   # Import/Export
│   ├── tour_generator.py     # Tours interativos
│   └── icon_generator.py     # Geração de ícones
├── 📁 templates/              # Templates Jinja2
│   ├── app/                  # App base
│   ├── auth/                 # Autenticação
│   ├── core/                 # Classes base
│   ├── crud/                 # Templates CRUD
│   ├── dashboard/            # Dashboard
│   ├── filters/              # Filtros
│   ├── forms/                # Formulários
│   └── widgets/              # Widgets reutilizáveis
├── 📁 utils/                  # Utilitários
│   ├── case_converter.py     # Conversão de naming
│   ├── file_manager.py       # Gerenciamento de arquivos
│   ├── flutter_cli.py        # Wrapper Flutter CLI
│   ├── firebase_cli.py       # Wrapper Firebase CLI
│   ├── image_processor.py    # Processamento de imagens
│   └── code_analyzer.py      # Análise de código
├── 📁 tests/                  # Testes do FAC
├── 📁 docs/                   # Documentação
├── 📁 examples/               # Exemplos de uso
├── requirements.txt           # Dependências Python
├── setup.py                  # Setup do pacote
└── README.md                 # Este arquivo
```

---

## 🌍 Roadmap

### 🚧 Em Desenvolvimento (v2.0)

- [ ] **Persistência Híbrida** - Firebase + SQLite sincronizado
- [ ] **Módulos Aninhados** - Hierarquia de módulos
- [ ] **Sistema de Filtros** - Filtros dinâmicos configuráveis
- [ ] **Import/Export Avançado** - Com mapeamento visual
- [ ] **Tours Interativos** - Guias passo-a-passo
- [ ] **Geração de Ícones** - Para todas as plataformas
- [ ] **Templates Customizáveis** - Sistema de templates


### 🔮 Futuro (v3.0)

- [ ] **Visual Editor** - Editor drag-and-drop
- [ ] **Cloud IDE** - Desenvolvimento na nuvem
- [ ] **Team Collaboration** - Colaboração em tempo real
- [ ] **Marketplace** - Store de plugins e templates
- [ ] **Enterprise Features** - Recursos empresariais
- [ ] **Multi-tenant** - Aplicações multi-inquilino

---

### 📚 Recursos

- 📋 **Changelog**: [CHANGELOG.md](CHANGELOG.md)

## 📄 Licença

Este projeto está licenciado sob a **MIT License** - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

<div align="center">

[🔝 Voltar ao topo](#-flutter-app-creator-fac)

</div>