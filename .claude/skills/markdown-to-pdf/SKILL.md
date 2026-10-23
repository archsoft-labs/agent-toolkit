---
name: markdown-to-pdf
description: >
  Converts Markdown (.md) files to A4-formatted PDF using Playwright/Chromium.
  Use when the user wants to convert or export Markdown to PDF.
  Trigger phrases: "convert markdown to pdf", "generate pdf from markdown",
  "convert md to pdf", "export markdown as pdf", "md to pdf", "make a pdf",
  "converter markdown para pdf", "gerar pdf do markdown", "exportar como pdf".
  DO NOT trigger for: HTML to PDF, Word/DOCX export, or viewing markdown.
allowed-tools: Bash, Read, Write
---

# Markdown to PDF

Converts Markdown (`.md`) files to A4-formatted PDF using Playwright/Chromium.

## What This Skill Does

1. Creates a temporary `.tmp/<filename>.html` next to each `.md` file
2. Uses Playwright/Chromium to render it into `pdf/<filename>.pdf`
3. Deletes the temporary HTML file and the `.tmp/` folder

Only the final **PDF** remains. The `.tmp/` folder is an implementation detail.

## Quick Start

```bash
# Install dependencies (if not already installed)
pip install markdown playwright
python -m playwright install chromium

# Convert one or more files
python <skill-path>/scripts/convert.py path/to/file.md [path/to/other.md ...]

# Specify output directory
python <skill-path>/scripts/convert.py file.md --output-dir ./output/

# Generate without page footer
python <skill-path>/scripts/convert.py file.md --no-footer
```

## Output Structure

```
project/
├── notes.md
├── report.md
└── pdf/              # or custom --output-dir
    ├── notes.pdf
    └── report.pdf
```

## PDF Specification

| Feature | Behavior |
|---------|----------|
| Generator | Playwright (`playwright.sync_api`) with bundled Chromium |
| Paper size | A4 (210mm × 297mm) |
| Margins | 20mm top/sides, 25mm bottom |
| Footer | Right-aligned "X / Y" page counter (disable with `--no-footer`) |
| Header | None |
| Code blocks | Background `#2d2d2d`, font 11px, `white-space: pre-wrap` |
| Images | Resolved to absolute `file://` URIs |
| Background colors | Preserved (`print_background=True`) |
| Markdown extensions | `tables`, `fenced_code`, `toc`, `nl2br` |
| Encoding | UTF-8 throughout |

## Options

| Flag | Description |
|------|-------------|
| `--output-dir <dir>` | Custom output directory (default: `pdf/` next to source) |
| `--no-footer` | Disable page counter footer |

## Dependencies

- Python 3.8+
- `markdown`: `pip install markdown`
- `playwright` + Chromium: `pip install playwright && python -m playwright install chromium`

## Bundled Script

See `scripts/convert.py` — run directly, no wrapper needed.
