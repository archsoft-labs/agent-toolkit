---
name: html-apply-print-styles
description: >
  Applies A4 print styles, pagination footer, and high-contrast formatting
  to HTML files for print-ready output. Preserves existing content styles
  while adding print-specific rules.
  Use when the user wants to prepare HTML for printing or PDF conversion.
  Trigger phrases: "apply print styles", "format for A4", "prepare for print",
  "add print footer", "make print-ready", "preparar para impressão", "formatar para A4".
  DO NOT trigger for: extracting content, translating, or converting to PDF directly.
allowed-tools: Bash, Read, Write
---

# HTML Apply Print Styles

Transforms HTML files into print-ready documents with A4 formatting,
pagination footer, and high-contrast styling.

## What This Skill Does

1. Adds `@page` rule for A4 paper size (210mm × 297mm)
2. Adds `@media print` styles for print optimization
3. Injects CSS-driven pagination footer: `[current] / [total]`
4. Forces white background and high text contrast
5. Preserves existing content styles (fonts, colors, spacing)

## Quick Start

```bash
# Apply print styles to a file
python <skill-path>/scripts/apply_styles.py path/to/file.html

# Process multiple files
python <skill-path>/scripts/apply_styles.py file1.html file2.html
```

## Print Specification

| Feature | Value |
|---------|-------|
| Paper size | A4 (210mm × 297mm) |
| Margins | 20mm top/sides, 25mm bottom |
| Footer | Right-aligned page counter |
| Background | White (`#FFFFFF`) |
| Text contrast | High (dark on light) |

## Dependencies

- Python 3.8+
- `beautifulsoup4`: `pip install beautifulsoup4`

## Notes

- Existing `<style>` blocks are preserved; print styles are appended
- If `@page` already exists, it is updated to A4
- Footer uses CSS counters (no JavaScript required)
- Safe to run multiple times (idempotent)
