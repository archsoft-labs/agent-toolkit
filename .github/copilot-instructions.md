# Copilot instructions for this repository

## What this repository is

**Agent Toolkit** is a portable collection of **skills**, **slash commands**, and **subagent definitions** for AI coding agents. Everything is plain Markdown with YAML frontmatter, plus a few small Python 3 scripts. The layout follows Claude Code conventions (`.claude/skills/`, `.claude/commands/`, `.claude/agents/`), but the content is agent-agnostic — read the matching file and follow it.

## The three building blocks

| Primitive | What it is | Where it lives |
|---|---|---|
| **Skill** | Reusable instruction set for one well-defined task | `.claude/skills/<name>/SKILL.md` |
| **Command** | Slash-invoked procedure the user triggers explicitly | `.claude/commands/<group>/<name>.md` |
| **Agent** | Specialized subagent persona that orchestrates skills | `.claude/agents/<name>.md` |

## Project Skills

Skills are reusable specialized instructions, one per folder, defined in `SKILL.md` files with YAML frontmatter (`name`, `description`, `allowed-tools`). Read the `description` field to decide whether the skill applies, then load the full `SKILL.md` before executing the task.

### Document Processing Skills

| Skill | Purpose |
|-------|---------|
| [`html-fetch-url`](../.claude/skills/html-fetch-url/) | Download HTML from a URL and localize images (curl → browser-harness fallback) |
| [`markdown-to-pdf`](../.claude/skills/markdown-to-pdf/) | Convert Markdown to A4 PDF via Playwright/Chromium |
| [`html-to-pdf`](../.claude/skills/html-to-pdf/) | Convert HTML directly to A4 PDF |
| [`html-to-markdown`](../.claude/skills/html-to-markdown/) | Convert HTML to clean Markdown |
| [`html-extract-content`](../.claude/skills/html-extract-content/) | Strip nav/sidebar/footer boilerplate, keep main content |
| [`html-normalize-images`](../.claude/skills/html-normalize-images/) | Rename images to kebab-case `images/<page>-image-001.ext` |
| [`html-translate`](../.claude/skills/html-translate/) | Translate HTML to any language, preserving structure |
| [`html-apply-print-styles`](../.claude/skills/html-apply-print-styles/) | Inject A4 print styles + pagination footer |

**Typical composition** — turning a raw saved web page into a translated, print-ready PDF:

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

### Architecture & Quality Skills

Language-agnostic rules with examples in **Python, C#, TypeScript, Java, and Go**.

| Skill | Purpose |
|-------|---------|
| [`clean-architecture-rules`](../.claude/skills/clean-architecture-rules/) | Quick reference index into the four skills below |
| [`architecture-layer-structure`](../.claude/skills/architecture-layer-structure/) | Layer definitions, folder structures, dependency rules |
| [`code-quality-principles`](../.claude/skills/code-quality-principles/) | SOLID, type safety, dead code, defensive code, comments |
| [`naming-conventions`](../.claude/skills/naming-conventions/) | File/type/function naming per language and per layer |
| [`test-organization`](../.claude/skills/test-organization/) | Test layout, test doubles, coverage exclusions |

### Shared Utilities

The `.claude/skills/_shared/` folder contains common Python utilities used by multiple skills:

- `html_processor.py` — HTML parsing, file I/O, kebab-case conversion
- `file_resolver.py` — Glob expansion, file resolution
- `report_generator.py` — Standardized success/error reporting

## Project Commands

Commands are reusable command definitions, one `.md` file per command in the `.claude/commands/` folder, with YAML frontmatter (`description`, `allowed-tools`). Subfolders become namespaces (`commands/<group>/<name>.md` → `/<group>:<name>`). Read the file and follow its steps directly.

### Available Commands

| Command | Purpose |
|---------|---------|
| [`/git:squash-history`](../.claude/commands/git/squash-history.md) | Rewrite repository history to a single commit and force-push. **Destructive and irreversible** — always confirm with the user first. |

## Project Agents

Agents are specialized subagent definitions (a persona + scope + instructions), one `.md` file per agent in the `.claude/agents/` folder. Before delegating a subtask to a specialized agent, read the corresponding definition.

### Available Agents

| Agent | Purpose | Skills Used |
|-------|---------|-------------|
| [`html-processor`](../.claude/agents/html-processor.md) | Multi-step HTML pipelines (fetch → clean → translate → print → PDF) from files or URLs | `html-fetch-url`, `html-extract-content`, `html-normalize-images`, `html-translate`, `html-apply-print-styles`, `html-to-pdf`, `html-to-markdown` |
| [`markdown-processor`](../.claude/agents/markdown-processor.md) | Markdown conversion pipelines | `markdown-to-pdf` |
| [`clean-arch-reviewer`](../.claude/agents/clean-arch-reviewer.md) | Code review against Clean Architecture + quality rules, with severity-rated reports | `architecture-layer-structure`, `code-quality-principles`, `naming-conventions`, `test-organization` |

## Working in this repository

When the user asks you to **add a new skill, command, or agent**:

1. Create the file in the right folder with proper YAML frontmatter.
2. Bundle any supporting scripts under `scripts/` (Python 3, using `_shared/` helpers).
3. Update all four documentation files in sync:
   - `README.md` (English)
   - `README.pt-br.md` (Portuguese)
   - `CLAUDE.md`
   - `AGENTS.md`
   - `.github/copilot-instructions.md` (this file)

## Design principles

- All skills follow **single responsibility** principle
- Skills are **composable** — chain via documented inputs/outputs
- All content in **English** (international audience)
- Architecture skills provide examples in **Python, C#, TypeScript, Java, and Go**
- Scripts use **Python 3** with standardized error reporting via `_shared/report_generator.py`
- Temporary files are cleaned up automatically
- **Stop on failure** — multi-step procedures halt on the first error and report it
- **Least privilege** — `allowed-tools` lists the minimum each piece needs
