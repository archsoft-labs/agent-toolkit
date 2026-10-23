# Agent Toolkit

A curated, **portable toolkit for AI coding agents** — reusable **skills**, **slash commands**, and **subagent definitions** that teach any agent how to execute complex, sensitive, or repetitive workflows consistently.

Everything is plain Markdown with YAML frontmatter, plus a few small Python 3 scripts. The layout follows the [Claude Code](https://docs.claude.com/en/docs/claude-code) conventions (`.claude/skills/`, `.claude/commands/`, `.claude/agents/`), but the content itself is **agent-agnostic**: any AI agent (Codex, Devin, Cursor, Copilot, Claude, etc.) can read the same files and follow them.

> 🇧🇷 [Ler em português](README.pt-br.md)

---

## Why this toolkit?

AI agents are powerful generalists, but some categories of work demand **repeatable, audited, step-by-step procedures**:

- **Document pipelines** — extract → normalize → translate → style → PDF. Skipping a step or running them out of order produces broken output.
- **Destructive operations** — rewriting git history, dropping data. These must stop on failure and confirm with the user.
- **Team conventions** — Clean Architecture layering, naming standards, test structure. Every agent (and every teammate) should apply them the same way, every time.
- **Repeatable reviews** — code review checklists with severity levels so findings are consistent and actionable.

Instead of re-explaining these procedures in every prompt, you write them once and the agent reads them on demand.

---

## The three building blocks

This repository uses three complementary primitives. Each plays a distinct role:

| Primitive | What it is | When it loads | Where it lives |
|---|---|---|---|
| **Skill** | A reusable instruction set (Markdown + optional scripts) for one well-defined task | Loaded on demand when the user's request matches its trigger phrases | `.claude/skills/<name>/SKILL.md` |
| **Command** | A slash-invoked procedure the user triggers explicitly | Runs only when the user types `/name` | `.claude/commands/<group>/<name>.md` |
| **Agent** | A specialized subagent persona that orchestrates skills | Spawned by the main agent when a task matches its scope | `.claude/agents/<name>.md` |

**How they compose:**
- A **skill** knows *how* to do one thing (e.g. convert HTML to PDF).
- A **command** is a *user-triggered* entry point (e.g. `/git:squash-history`).
- An **agent** is a *persona* that picks the right skills, in the right order, for a broad task (e.g. "process this HTML article" → chains 4 skills).

---

## Repository layout

```
.
├── .claude/
│   ├── settings.json                 # Project-level Claude Code settings
│   ├── skills/                       # One folder per skill
│   │   ├── _shared/                  # Shared Python utilities
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
│   └── agents/                       # Subagent definitions
│       ├── html-processor.md
│       ├── markdown-processor.md
│       └── clean-arch-reviewer.md
├── .github/
│   └── copilot-instructions.md       # GitHub Copilot guidance
├── CLAUDE.md                         # Instructions for Claude Code
├── AGENTS.md                         # Instructions for AGENTS.md-compatible agents
├── README.md                         # This file (English)
└── README.pt-br.md                   # Versão em português
```

---

## Skills

A **skill** is a self-contained instruction set in a `SKILL.md` file with YAML frontmatter (`name`, `description`, `allowed-tools`). Skills may bundle small Python scripts under `scripts/` for deterministic work.

### Document Processing Skills

End-to-end primitives for converting, cleaning, translating, and printing HTML/Markdown documents.

| Skill | Purpose | Key Triggers |
|---|---|---|
| [`html-fetch-url`](.claude/skills/html-fetch-url/) | Download HTML from a URL and localize images (curl → browser-harness fallback) | "fetch url", "download page", "baixar página" |
| [`markdown-to-pdf`](.claude/skills/markdown-to-pdf/) | Convert Markdown to A4 PDF via Playwright/Chromium | "convert markdown to pdf", "generate pdf" |
| [`html-to-pdf`](.claude/skills/html-to-pdf/) | Convert HTML directly to A4 PDF | "convert html to pdf" |
| [`html-to-markdown`](.claude/skills/html-to-markdown/) | Convert HTML to clean Markdown (headings, tables, code blocks) | "html to md" |
| [`html-extract-content`](.claude/skills/html-extract-content/) | Strip nav/sidebar/footer boilerplate, keep main content | "extract content", "clean html" |
| [`html-normalize-images`](.claude/skills/html-normalize-images/) | Rename images to `images/<page>-image-001.ext` kebab-case | "normalize images" |
| [`html-translate`](.claude/skills/html-translate/) | Translate HTML to any language, preserving structure | "translate to X" |
| [`html-apply-print-styles`](.claude/skills/html-apply-print-styles/) | Inject A4 print styles + pagination footer | "apply print styles", "format for A4" |

**Composability example** — turning a raw saved web page into a translated, print-ready PDF:

```
html-extract-content
  → html-normalize-images
  → html-translate
  → html-apply-print-styles
  → html-to-pdf
```

**Starting from a URL** instead of a saved file, prepend `html-fetch-url`:

```
html-fetch-url
  → html-extract-content
  → html-normalize-images
  → html-translate
  → html-apply-print-styles
  → html-to-pdf
```

Each skill has **documented inputs and outputs**, so they chain cleanly.

### Architecture & Quality Skills

Language-agnostic rules with examples in **Python, C#, TypeScript, Java, and Go**.

| Skill | Purpose | Key Triggers |
|---|---|---|
| [`clean-architecture-rules`](.claude/skills/clean-architecture-rules/) | Quick-reference index into the four detailed skills below | "clean architecture", "architecture overview" |
| [`architecture-layer-structure`](.claude/skills/architecture-layer-structure/) | Layer definitions, folder structures, dependency rules | "layer structure", "project structure" |
| [`code-quality-principles`](.claude/skills/code-quality-principles/) | SOLID, type safety, dead code, defensive code, comments | "code quality", "solid principles" |
| [`naming-conventions`](.claude/skills/naming-conventions/) | File/type/function naming per language and per layer | "naming convention", "how to name" |
| [`test-organization`](.claude/skills/test-organization/) | Test layout, test doubles, coverage exclusions | "test structure", "unit tests" |

### Shared utilities

The [`.claude/skills/_shared/`](.claude/skills/_shared/) folder holds reusable Python helpers imported by multiple skills:

- **`html_processor.py`** — HTML parsing helpers, file I/O, kebab-case conversion.
- **`file_resolver.py`** — Glob expansion, path resolution, batch file discovery.
- **`report_generator.py`** — Standardized success/error report formatting.

### Anatomy of a skill

```markdown
---
name: my-skill
description: >
  One-paragraph summary listing trigger phrases so the agent
  knows when to load this skill.
allowed-tools: Bash, Read, Write
---

# My Skill

Step-by-step instructions, code samples, decision rules,
and failure handling.
```

- **`name`** — unique slug used to reference the skill.
- **`description`** — the *routing* text; the agent reads this to decide whether to load the skill.
- **`allowed-tools`** — least-privilege tool list the skill may use.
- **Body** — the actual procedure, with examples and edge cases.

---

## Commands

A **command** is a user-invoked slash procedure stored under `.claude/commands/`. Subfolders become namespaces: `commands/git/squash-history.md` is invoked as `/git:squash-history`.

### Available commands

| Command | Description |
|---|---|
| [`/git:squash-history`](.claude/commands/git/squash-history.md) | Rewrites the entire repository history into a single commit and force-pushes. **Destructive and irreversible** — the agent must confirm with the user before running. |

### Anatomy of a command

```markdown
---
description: One-line summary shown in command listings
allowed-tools: Bash(git *)
---

# command-name

Exact bash commands to run, in order, with stop-on-failure rules
and explicit user-confirmation gates for destructive steps.
```

- Commands are **explicit** — the agent never runs one unless the user invoked it.
- `allowed-tools` restricts what the command may do (least privilege for sensitive operations).

---

## Agents

An **agent** is a specialized subagent definition (persona + scope + skills used), one `.md` file per agent in `.claude/agents/`. The main agent reads the definition before delegating a subtask.

### Available agents

| Agent | Purpose | Skills Orchestrated |
|---|---|---|
| [`html-processor`](.claude/agents/html-processor.md) | Multi-step HTML pipelines (fetch → clean → translate → print → PDF) from files or URLs | `html-fetch-url`, `html-extract-content`, `html-normalize-images`, `html-translate`, `html-apply-print-styles`, `html-to-pdf`, `html-to-markdown` |
| [`markdown-processor`](.claude/agents/markdown-processor.md) | Markdown conversion pipelines | `markdown-to-pdf` |
| [`clean-arch-reviewer`](.claude/agents/clean-arch-reviewer.md) | Code review against Clean Architecture + quality rules, with severity-rated reports | `architecture-layer-structure`, `code-quality-principles`, `naming-conventions`, `test-organization` |

### Anatomy of an agent

```markdown
---
name: my-agent
description: When to delegate to this agent
skills:
  - skill-one
  - skill-two
---

# My Agent

The persona, the supported pipelines, the input-resolution rules,
and the failure-handling contract.
```

### Example pipelines (from `html-processor`)

```
URL  → PDF (direct):          fetch-url → extract → normalize → apply-print-styles → html-to-pdf
URL  → Translated PDF:        fetch-url → extract → normalize → translate → apply-print-styles → html-to-pdf
HTML → Clean HTML:            extract → normalize
HTML → Translated HTML:       extract → normalize → translate
HTML → Print-ready HTML:      extract → normalize → apply-print-styles
HTML → PDF (direct):          extract → normalize → apply-print-styles → html-to-pdf
HTML → PDF (via Markdown):    extract → normalize → apply-print-styles → html-to-markdown → markdown-to-pdf
HTML → Translated PDF:        extract → normalize → translate → apply-print-styles → html-to-pdf
```

---

## How the three primitives work together

```
User: "Make a PDF of this article, in Portuguese"

  ┌────────────────────────────────────────────────────────┐
  │ Main agent recognizes the task is multi-step           │
  │ → delegates to the `html-processor` agent              │
  └────────────────────────────────────────────────────────┘
                          │
                          ▼
  ┌────────────────────────────────────────────────────────┐
  │ html-processor picks the pipeline                      │
  │   extract → normalize → translate → styles → to-pdf    │
  └────────────────────────────────────────────────────────┘
                          │
                          ▼
  ┌────────────────────────────────────────────────────────┐
  │ Each step invokes its skill (SKILL.md + script)        │
  │ Each skill uses _shared/ utilities as needed           │
  └────────────────────────────────────────────────────────┘
                          │
                          ▼
                     article-pt-br.pdf
```

The user could also have invoked a single step directly ("just normalize the images") — the skill is loaded on demand without needing the agent.

---

## Adding a new building block

### New skill
1. Create `.claude/skills/<kebab-case-name>/SKILL.md` with YAML frontmatter (`name`, `description`, `allowed-tools`).
2. Add any supporting scripts under `scripts/` (Python 3, standard error reporting via `_shared/report_generator.py`).
3. List the skill in this README, in [CLAUDE.md](CLAUDE.md), [AGENTS.md](AGENTS.md), and [.github/copilot-instructions.md](.github/copilot-instructions.md).

### New command
1. Create `.claude/commands/<group>/<name>.md` (the subfolder becomes the namespace).
2. Add YAML frontmatter (`description`, `allowed-tools`).
3. Write the exact steps, with stop-on-failure rules and confirmation gates for destructive actions.
4. List it in this README and the instruction files above.

### New agent
1. Create `.claude/agents/<kebab-case-name>.md` with frontmatter (`name`, `description`, `skills`).
2. Document the persona, supported pipelines, input-resolution rules, and failure handling.
3. List it in this README and the instruction files.

---

## Instruction files for AI agents

This repository ships the same guidance in three formats so different agents can pick it up:

- **[CLAUDE.md](CLAUDE.md)** — read by Claude Code on session start.
- **[AGENTS.md](AGENTS.md)** — read by AGENTS.md-compatible agents (Codex, Devin, Cursor, etc.).
- **[.github/copilot-instructions.md](.github/copilot-instructions.md)** — read by GitHub Copilot.

Keep all three in sync when adding or removing skills, commands, or agents.

---

## Design principles

- **Single responsibility** — each skill does exactly one thing.
- **Composability** — skills chain via documented inputs/outputs.
- **Least privilege** — `allowed-tools` lists the minimum each piece needs.
- **Portability** — pure Markdown + Python 3, no Claude-specific lock-in.
- **International content** — all skill/agent/command bodies are written in English so any agent (and any teammate) can read them.
- **Idempotency where possible** — scripts clean up temporary files and are safe to re-run.
- **Stop on failure** — multi-step procedures halt on the first error and report it.

---

## License

See [LICENSE](LICENSE).
