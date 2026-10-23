---
name: html-extract-content
description: >
  Extracts the main content from HTML files, removing navigation, sidebars,
  footers, ads, and other boilerplate. Produces clean semantic HTML with
  preserved content structure.
  Use when the user wants to extract or clean HTML content.
  Trigger phrases: "extract content", "clean html", "remove boilerplate",
  "get main content", "strip navigation", "extrair conteúdo", "limpar html".
  DO NOT trigger for: renaming images, translating, or applying print styles.
allowed-tools: Bash, Read, Write, Glob
---

# HTML Extract Content

Extracts the primary content from HTML files, discarding navigation,
sidebars, footers, banners, cookie notices, and advertisements.

## What This Skill Does

1. Analyzes HTML structure to identify main content
2. Isolates the content heading and body
3. Discards all boilerplate elements
4. Preserves content-internal structure (headings, paragraphs, lists, tables, code)
5. Outputs clean semantic HTML

## Content Identification Signals

The skill uses these signals, in order of reliability:

1. **Semantic tags**: `<main>`; `<article>` only when unambiguous (a single
   article, or exactly one article large enough to be main content — several
   small `<article>` blocks, e.g. FAQ items, are treated as boilerplate)
2. **Wrapper patterns**: `id`/`class` containing `content`, `post`, `body`,
   `entry`, `text`, `main` — starts from the largest match and descends to the
   tightest inner wrapper holding the bulk of the text, so catch-all
   containers (nav + content + footer) lose to the content block proper
3. **Content patterns**: Largest contiguous text-heavy block with `<h1>`/`<h2>`
4. **Structural clues**: High text-to-markup ratio, no link-heavy navigation

## Quick Start

```bash
# Extract content from a single file
python <skill-path>/scripts/extract.py path/to/file.html

# Process multiple files
python <skill-path>/scripts/extract.py file1.html file2.html folder/*.html
```

## Output

Each input produces one clean HTML file:
- **Location**: Same directory as source
- **Name**: `[original-name]-clean.html`
- **Content**: Semantic HTML with preserved structure

## Ambiguity Handling

Ambiguous cases are resolved deterministically, never by guessing the first
match: multiple small `<article>` blocks (FAQs, cards) are skipped in favor of
structural signals, and nested content wrappers are unwrapped to the tightest
block that still holds the bulk of the text. If no signal identifies content,
the script reports a failure instead of producing an empty extraction.

## Dependencies

- Python 3.8+
- `beautifulsoup4`: `pip install beautifulsoup4`
- `lxml`: `pip install lxml` (optional, faster parsing)

## Notes

- Images are **not** renamed or moved by this skill (use `html-normalize-images`)
- Print styles are **not** applied (use `html-apply-print-styles`)
- Translation is **not** performed (use `html-translate`)
