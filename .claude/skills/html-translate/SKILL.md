---
name: html-translate
description: >
  Translates HTML content to any target language while preserving document
  structure, formatting, and image references. Produces natural, fluent
  translations that read as if written by a native speaker.
  Use when the user wants to translate HTML files to another language.
  Trigger phrases: "translate to X", "translate this html", "translate to french",
  "translate to portuguese", "traduzir para X", "traduzir para inglês",
  "translate to pt-br", "translate to zh-CN".
  DO NOT trigger for: extracting content, renaming images, or applying styles.
allowed-tools: Bash, Read, Write, Glob
---

# HTML Translate

Translates HTML content into any target language while preserving
document structure, formatting, and image references.

## What This Skill Does

1. Parses HTML and identifies translatable text nodes
2. Translates all text content to the target language
3. Preserves HTML structure, attributes, and image paths
4. Produces natural, fluent prose (not word-for-word literal)
5. Maintains cohesive flow between sentences and paragraphs

## Quick Start

```bash
# Translate to a target language
python <skill-path>/scripts/translate.py path/to/file.html --lang pt-br

# Translate multiple files
python <skill-path>/scripts/translate.py file1.html file2.html --lang fr
```

## Language Specification

Accepts any of these forms:

| Format | Examples |
|--------|----------|
| Locale code | `pt-br`, `zh-CN`, `fr`, `ja`, `de` |
| Full name | `portuguese`, `french`, `japanese`, `german` |
| Native name | `português`, `français`, `日本語`, `deutsch` |

## Output

Each input produces one translated HTML file:
- **Location**: Same directory as source
- **Name**: `[original-name]-[language].html` (e.g., `article-pt-br.html`)
- **Content**: Fully translated, structure preserved

## Translation Quality

- Natural, fluent prose (not literal word-for-word)
- Cohesive sentence flow and logical connections
- Accessible vocabulary for non-specialists
- Preserved tone and register of the original

## Dependencies

- Python 3.8+
- `beautifulsoup4`: `pip install beautifulsoup4`
- Translation backend: Claude API (default) or local model

## Notes

- Image references (`<img src="...">`) are preserved unchanged
- Print styles are **not** applied (use `html-apply-print-styles` after)
- Content extraction is **not** performed (use `html-extract-content` first)
