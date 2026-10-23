# Agent Toolkit

Um **toolkit portátil e curado para agentes de código de IA** — **skills**, **slash commands** e **definições de subagentes** reutilizáveis que ensinam qualquer agente a executar fluxos de trabalho complexos, sensíveis ou repetitivos de forma consistente.

Tudo é Markdown puro com frontmatter YAML, mais alguns pequenos scripts Python 3. A estrutura segue as convenções do [Claude Code](https://docs.claude.com/en/docs/claude-code) (`.claude/skills/`, `.claude/commands/`, `.claude/agents/`), mas o conteúdo em si é **agnóstico de agente**: qualquer agente de IA (Codex, Devin, Cursor, Copilot, Claude, etc.) pode ler os mesmos arquivos e segui-los.

> 🇺🇸 [Read in English](README.md)

---

## Por que este toolkit?

Agentes de IA são generalistas poderosos, mas algumas categorias de trabalho exigem **procedimentos repetíveis, auditáveis e passo a passo**:

- **Pipelines de documentos** — extrair → normalizar → traduzir → estilizar → PDF. Pular uma etapa ou executá-las fora de ordem produz saída quebrada.
- **Operações destrutivas** — reescrever histórico do git, apagar dados. Elas devem parar em caso de falha e pedir confirmação ao usuário.
- **Convenções de equipe** — camadas da Clean Architecture, padrões de nomenclatura, estrutura de testes. Todo agente (e todo colega) deve aplicá-las da mesma forma, sempre.
- **Revisões repetíveis** — checklists de code review com níveis de severidade para que os achados sejam consistentes e acionáveis.

Em vez de reexplicar esses procedimentos em cada prompt, você os escreve uma vez e o agente os lê sob demanda.

---

## Os três blocos de construção

Este repositório usa três primitivas complementares. Cada uma tem um papel distinto:

| Primitiva | O que é | Quando é carregada | Onde vive |
|---|---|---|---|
| **Skill** | Um conjunto reutilizável de instruções (Markdown + scripts opcionais) para uma tarefa bem definida | Carregada sob demanda quando a requisição do usuário corresponde às suas frases-gatilho | `.claude/skills/<nome>/SKILL.md` |
| **Command** | Um procedimento invocado por slash que o usuário dispara explicitamente | Executado apenas quando o usuário digita `/nome` | `.claude/commands/<grupo>/<nome>.md` |
| **Agent** | Uma persona de subagente especializada que orquestra skills | Instanciado pelo agente principal quando uma tarefa corresponde ao seu escopo | `.claude/agents/<nome>.md` |

**Como elas se compõem:**
- Uma **skill** sabe *como* fazer uma coisa (ex.: converter HTML para PDF).
- Um **command** é um *ponto de entrada disparado pelo usuário* (ex.: `/git:squash-history`).
- Um **agent** é uma *persona* que escolhe as skills certas, na ordem certa, para uma tarefa ampla (ex.: "processar este artigo HTML" → encadeia 4 skills).

---

## Estrutura do repositório

```
.
├── .claude/
│   ├── settings.json                 # Configurações do Claude Code no nível do projeto
│   ├── skills/                       # Uma pasta por skill
│   │   ├── _shared/                  # Utilitários Python compartilhados
│   │   │   ├── file_resolver.py
│   │   │   ├── html_processor.py
│   │   │   └── report_generator.py
│   │   ├── markdown-to-pdf/
│   │   │   ├── SKILL.md
│   │   │   └── scripts/convert.py
│   │   ├── html-fetch-url/
│   │   ├── html-to-pdf/
│   │   ├── html-to-markdown/
│   │   ├── html-extract-content/
│   │   ├── html-normalize-images/
│   │   ├── html-translate/
│   │   ├── html-apply-print-styles/
│   │   ├── clean-architecture-rules/
│   │   ├── architecture-layer-structure/
│   │   ├── code-quality-principles/
│   │   ├── naming-conventions/
│   │   └── test-organization/
│   ├── commands/                     # Slash commands
│   │   └── git/
│   │       └── squash-history.md
│   └── agents/                       # Definições de subagentes
│       ├── html-processor.md
│       ├── markdown-processor.md
│       └── clean-arch-reviewer.md
├── .github/
│   └── copilot-instructions.md       # Orientação para o GitHub Copilot
├── CLAUDE.md                         # Instruções para o Claude Code
├── AGENTS.md                         # Instruções para agentes compatíveis com AGENTS.md
├── README.md                         # English version
└── README.pt-br.md                   # Este arquivo
```

---

## Skills

Uma **skill** é um conjunto autocontido de instruções em um arquivo `SKILL.md` com frontmatter YAML (`name`, `description`, `allowed-tools`). Skills podem empacotar pequenos scripts Python em `scripts/` para trabalho determinístico.

### Skills de Processamento de Documentos

Primitivas de ponta a ponta para converter, limpar, traduzir e imprimir documentos HTML/Markdown.

| Skill | Propósito | Gatilhos principais |
|---|---|---|
| [`html-fetch-url`](.claude/skills/html-fetch-url/) | Baixa HTML de uma URL e localiza imagens (curl → fallback para browser-harness) | "baixar página", "salvar url", "fetch url" |
| [`markdown-to-pdf`](.claude/skills/markdown-to-pdf/) | Converte Markdown para PDF A4 via Playwright/Chromium | "converter markdown para pdf", "gerar pdf" |
| [`html-to-pdf`](.claude/skills/html-to-pdf/) | Converte HTML diretamente para PDF A4 | "converter html para pdf" |
| [`html-to-markdown`](.claude/skills/html-to-markdown/) | Converte HTML para Markdown limpo (títulos, tabelas, blocos de código) | "html para md" |
| [`html-extract-content`](.claude/skills/html-extract-content/) | Remove boilerplate de nav/sidebar/footer, mantém o conteúdo principal | "extrair conteúdo", "limpar html" |
| [`html-normalize-images`](.claude/skills/html-normalize-images/) | Renomeia imagens para `images/<pagina>-image-001.ext` em kebab-case | "normalizar imagens", "renomear imagens" |
| [`html-translate`](.claude/skills/html-translate/) | Traduz HTML para qualquer idioma, preservando a estrutura | "traduzir para X" |
| [`html-apply-print-styles`](.claude/skills/html-apply-print-styles/) | Injeta estilos de impressão A4 + rodapé de paginação | "aplicar estilos de impressão", "formatar para A4" |

**Exemplo de composição** — transformando uma página web salva em um PDF traduzido e pronto para impressão:

```
html-extract-content
  → html-normalize-images
  → html-translate
  → html-apply-print-styles
  → html-to-pdf
```

**Começando de uma URL** em vez de um arquivo salvo, prefixe com `html-fetch-url`:

```
html-fetch-url
  → html-extract-content
  → html-normalize-images
  → html-translate
  → html-apply-print-styles
  → html-to-pdf
```

Cada skill tem **entradas e saídas documentadas**, então elas se encadeiam de forma limpa.

### Skills de Arquitetura e Qualidade

Regras agnósticas de linguagem com exemplos em **Python, C#, TypeScript, Java e Go**.

| Skill | Propósito | Gatilhos principais |
|---|---|---|
| [`clean-architecture-rules`](.claude/skills/clean-architecture-rules/) | Índice de referência rápida para as quatro skills detalhadas abaixo | "clean architecture", "visão geral de arquitetura" |
| [`architecture-layer-structure`](.claude/skills/architecture-layer-structure/) | Definições de camadas, estruturas de pastas, regras de dependência | "estrutura de camadas", "estrutura do projeto" |
| [`code-quality-principles`](.claude/skills/code-quality-principles/) | SOLID, segurança de tipos, código morto, código defensivo, comentários | "qualidade de código", "princípios solid" |
| [`naming-conventions`](.claude/skills/naming-conventions/) | Nomenclatura de arquivos/tipos/funções por linguagem e por camada | "convenção de nomenclatura", "como nomear" |
| [`test-organization`](.claude/skills/test-organization/) | Layout de testes, test doubles, exclusões de cobertura | "estrutura de testes", "testes unitários" |

### Utilitários compartilhados

A pasta [`.claude/skills/_shared/`](.claude/skills/_shared/) contém helpers Python reutilizáveis importados por várias skills:

- **`html_processor.py`** — helpers de parsing de HTML, I/O de arquivos, conversão para kebab-case.
- **`file_resolver.py`** — expansão de globs, resolução de caminhos, descoberta de arquivos em lote.
- **`report_generator.py`** — formatação padronizada de relatórios de sucesso/erro.

### Anatomia de uma skill

```markdown
---
name: minha-skill
description: >
  Resumo de um parágrafo listando frases-gatilho para que o agente
  saiba quando carregar esta skill.
allowed-tools: Bash, Read, Write
---

# Minha Skill

Instruções passo a passo, exemplos de código, regras de decisão
e tratamento de falhas.
```

- **`name`** — slug único usado para referenciar a skill.
- **`description`** — o texto de *roteamento*; o agente lê isso para decidir se carrega a skill.
- **`allowed-tools`** — lista de ferramentas com privilégio mínimo que a skill pode usar.
- **Corpo** — o procedimento em si, com exemplos e casos extremos.

---

## Commands

Um **command** é um procedimento slash invocado pelo usuário, armazenado em `.claude/commands/`. Subpastas viram namespaces: `commands/git/squash-history.md` é invocado como `/git:squash-history`.

### Commands disponíveis

| Command | Descrição |
|---|---|
| [`/git:squash-history`](.claude/commands/git/squash-history.md) | Reescreve todo o histórico do repositório em um único commit e faz force push. **Destrutivo e irreversível** — o agente deve confirmar com o usuário antes de executar. |

### Anatomia de um command

```markdown
---
description: Resumo de uma linha exibido nas listagens de comandos
allowed-tools: Bash(git *)
---

# nome-do-comando

Comandos bash exatos a executar, em ordem, com regras de parada
em caso de falha e pontos de confirmação explícitos com o usuário
para etapas destrutivas.
```

- Commands são **explícitos** — o agente nunca executa um a menos que o usuário o tenha invocado.
- `allowed-tools` restringe o que o command pode fazer (privilégio mínimo para operações sensíveis).

---

## Agents

Um **agent** é uma definição de subagente especializado (persona + escopo + skills usadas), um arquivo `.md` por agente em `.claude/agents/`. O agente principal lê a definição antes de delegar uma subtarefa.

### Agents disponíveis

| Agent | Propósito | Skills orquestradas |
|---|---|---|
| [`html-processor`](.claude/agents/html-processor.md) | Pipelines HTML multi-etapas (baixar → limpar → traduzir → imprimir → PDF) a partir de arquivos ou URLs | `html-fetch-url`, `html-extract-content`, `html-normalize-images`, `html-translate`, `html-apply-print-styles`, `html-to-pdf`, `html-to-markdown` |
| [`markdown-processor`](.claude/agents/markdown-processor.md) | Pipelines de conversão de Markdown | `markdown-to-pdf` |
| [`clean-arch-reviewer`](.claude/agents/clean-arch-reviewer.md) | Code review contra Clean Architecture + regras de qualidade, com relatórios classificados por severidade | `architecture-layer-structure`, `code-quality-principles`, `naming-conventions`, `test-organization` |

### Anatomia de um agent

```markdown
---
name: meu-agent
description: Quando delegar para este agent
skills:
  - skill-um
  - skill-dois
---

# Meu Agent

A persona, os pipelines suportados, as regras de resolução de
entrada e o contrato de tratamento de falhas.
```

### Pipelines de exemplo (do `html-processor`)

```
URL  → PDF (direto):           fetch-url → extract → normalize → apply-print-styles → html-to-pdf
URL  → PDF traduzido:          fetch-url → extract → normalize → translate → apply-print-styles → html-to-pdf
HTML → HTML limpo:             extract → normalize
HTML → HTML traduzido:         extract → normalize → translate
HTML → HTML pronto p/ impressão: extract → normalize → apply-print-styles
HTML → PDF (direto):           extract → normalize → apply-print-styles → html-to-pdf
HTML → PDF (via Markdown):     extract → normalize → apply-print-styles → html-to-markdown → markdown-to-pdf
HTML → PDF traduzido:          extract → normalize → translate → apply-print-styles → html-to-pdf
```

---

## Como as três primitivas trabalham juntas

```
Usuário: "Faça um PDF deste artigo, em português"

  ┌────────────────────────────────────────────────────────┐
  │ O agente principal reconhece que a tarefa é multi-etapa│
  │ → delega para o agent `html-processor`                 │
  └────────────────────────────────────────────────────────┘
                          │
                          ▼
  ┌────────────────────────────────────────────────────────┐
  │ html-processor escolhe o pipeline                      │
  │   extract → normalize → translate → styles → to-pdf    │
  └────────────────────────────────────────────────────────┘
                          │
                          ▼
  ┌────────────────────────────────────────────────────────┐
  │ Cada etapa invoca sua skill (SKILL.md + script)        │
  │ Cada skill usa utilitários de _shared/ conforme precisa│
  └────────────────────────────────────────────────────────┘
                          │
                          ▼
                     article-pt-br.pdf
```

O usuário também poderia ter invocado uma única etapa diretamente ("apenas normalize as imagens") — a skill é carregada sob demanda sem precisar do agent.

---

## Adicionando um novo bloco de construção

### Nova skill
1. Crie `.claude/skills/<nome-kebab-case>/SKILL.md` com frontmatter YAML (`name`, `description`, `allowed-tools`).
2. Adicione scripts de apoio em `scripts/` (Python 3, relatório de erro padronizado via `_shared/report_generator.py`).
3. Liste a skill neste README, em [CLAUDE.md](CLAUDE.md), [AGENTS.md](AGENTS.md) e [.github/copilot-instructions.md](.github/copilot-instructions.md).

### Novo command
1. Crie `.claude/commands/<grupo>/<nome>.md` (a subpasta vira o namespace).
2. Adicione o frontmatter YAML (`description`, `allowed-tools`).
3. Escreva os passos exatos, com regras de parada em caso de falha e pontos de confirmação para ações destrutivas.
4. Liste-o neste README e nos arquivos de instrução acima.

### Novo agent
1. Crie `.claude/agents/<nome-kebab-case>.md` com frontmatter (`name`, `description`, `skills`).
2. Documente a persona, os pipelines suportados, as regras de resolução de entrada e o tratamento de falhas.
3. Liste-o neste README e nos arquivos de instrução.

---

## Arquivos de instrução para agentes de IA

Este repositório fornece a mesma orientação em três formatos para que diferentes agentes possam captá-la:

- **[CLAUDE.md](CLAUDE.md)** — lido pelo Claude Code no início da sessão.
- **[AGENTS.md](AGENTS.md)** — lido por agentes compatíveis com AGENTS.md (Codex, Devin, Cursor, etc.).
- **[.github/copilot-instructions.md](.github/copilot-instructions.md)** — lido pelo GitHub Copilot.

Mantenha os três em sincronia ao adicionar ou remover skills, commands ou agents.

---

## Princípios de design

- **Responsabilidade única** — cada skill faz exatamente uma coisa.
- **Composabilidade** — skills se encadeiam via entradas/saídas documentadas.
- **Privilégio mínimo** — `allowed-tools` lista o mínimo que cada peça precisa.
- **Portabilidade** — Markdown puro + Python 3, sem lock-in específico do Claude.
- **Conteúdo internacional** — todos os corpos de skill/agent/command são escritos em inglês para que qualquer agente (e qualquer colega) possa lê-los.
- **Idempotência quando possível** — scripts limpam arquivos temporários e são seguros para reexecutar.
- **Parar em caso de falha** — procedimentos multi-etapa interrompem no primeiro erro e o reportam.

---

## Licença

Veja [LICENSE](LICENSE).
