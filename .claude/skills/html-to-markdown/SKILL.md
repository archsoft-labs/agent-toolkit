---
name: html-to-markdown
description: >
  Converts HTML (.html) files to Markdown (.md) preserving formatting:
  headings, bold, italic, inline code, fenced code blocks with language
  detection, tables, links, lists, blockquotes, and horizontal rules.
  Use when the user wants to convert HTML to Markdown.
  Trigger phrases: "convert html to markdown", "html to md", "generate markdown",
  "transform html into markdown", "converter html para markdown", "html para md".
  DO NOT trigger for: translating HTML, converting to PDF, or editing HTML.
allowed-tools: Bash, Read, Write, Glob
---

# HTML to Markdown

Converts HTML (`.html`) files to Markdown (`.md`), preserving original
formatting as faithfully as possible.

## What This Skill Does

1. Parses HTML structure and content
2. Converts elements to Markdown equivalents
3. Preserves code block language tags
4. Maintains table structure
5. Outputs clean, readable Markdown

## Conversion Rules

| HTML | Markdown |
|------|----------|
| `<h1>`…`<h6>` | `#` through `######` |
| `<strong>`, `<b>` | `**bold**` |
| `<em>`, `<i>` | `*italic*` |
| `<code>` (inline) | `` `backtick` `` |
| `<pre><code class="language-X">` | ```` ```X ```` fenced block |
| `<a href="url">` | `[text](url)` |
| `<ul>` / `<ol>` | `-` / `1.` lists |
| `<table>` | GFM pipe table |
| `<blockquote>` | `> ` prefixed lines |
| `<hr>` | `---` |
| `<img>` | `![alt](src)` |
| `<br>` | Two trailing spaces |

## Quick Start

```bash
# Install dependency
pip install markdownify

# Convert single file
python <skill-path>/scripts/convert.py path/to/file.html

# Convert multiple files
python <skill-path>/scripts/convert.py file1.html file2.html folder/*.html

# Custom output directory
python <skill-path>/scripts/convert.py file.html --out-dir ./output/
```

## Output

- **Default**: Same directory as source, `.md` extension
- **With `--out-dir`**: Specified directory, same base name
- Existing `.md` files are overwritten without prompting

## Dependencies

- Python 3.8+
- `markdownify`: `pip install markdownify`

## Bundled Script

See `scripts/convert.py` — run directly, no wrapper needed.
