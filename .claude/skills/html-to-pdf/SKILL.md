---
name: html-to-pdf
description: >
  Converts HTML (.html) files directly to A4-formatted PDF using
  Playwright/Chromium. No intermediate Markdown conversion required.
  Use when the user wants to convert HTML directly to PDF.
  Trigger phrases: "convert html to pdf", "html to pdf", "generate pdf from html",
  "export html as pdf", "converter html para pdf", "html para pdf".
  DO NOT trigger for: Markdown to PDF (use markdown-to-pdf), or HTML to Markdown.
allowed-tools: Bash, Read, Write
---

# HTML to PDF

Converts HTML (`.html`) files directly to A4-formatted PDF using
Playwright/Chromium.

## What This Skill Does

1. Loads the HTML file in Chromium
2. Applies print styles if not already present
3. Renders to `pdf/<filename>.pdf`

## Quick Start

```bash
# Install dependencies (if not already installed)
pip install playwright
python -m playwright install chromium

# Convert a single file
python <skill-path>/scripts/convert.py path/to/file.html

# Convert multiple files
python <skill-path>/scripts/convert.py file1.html file2.html folder/*.html

# Custom output directory
python <skill-path>/scripts/convert.py file.html --output-dir ./output/
```

## Output Structure

```
project/
├── document.html
└── pdf/
    └── document.pdf
```

## PDF Specification

| Feature | Behavior |
|---------|----------|
| Generator | Playwright (`playwright.sync_api`) with bundled Chromium |
| Paper size | A4 (210mm × 297mm) |
| Margins | 20mm top/sides, 25mm bottom |
| Footer | Right-aligned "X / Y" page counter |
| Background colors | Preserved (`print_background=True`) |
| Print styles | Applied automatically if not present |

## Dependencies

- Python 3.8+
- `playwright` + Chromium: `pip install playwright && python -m playwright install chromium`

## Notes

- If HTML lacks print styles, basic A4 styles are applied automatically
- For full print style control, run `html-apply-print-styles` first
- Images with relative paths are resolved automatically
