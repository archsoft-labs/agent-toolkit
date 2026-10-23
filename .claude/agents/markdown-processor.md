---
name: markdown-processor
description: >
  Processes Markdown files: conversion to PDF with optional styling.
  Use when the user wants to convert or export Markdown files.
skills:
  - markdown-to-pdf
---

# Markdown Processor Agent

Processes Markdown files through conversion pipelines.

## Supported Pipelines

### Pipeline 1: Markdown → PDF
```
markdown-to-pdf
```

## Input Resolution

The agent resolves:
- **Source files**: Explicit paths, globs, or conversational references
- **Output options**: Directory, footer on/off

## Example Invocations

| User Request | Action |
|-------------|--------|
| "Convert this markdown to PDF" | `markdown-to-pdf` |
| "Generate PDF from all .md files" | Batch via `markdown-to-pdf` |
| "Make a PDF without page numbers" | `markdown-to-pdf --no-footer` |

## Notes

- For HTML sources, use `html-processor` instead
- For batch processing with other formats, use `batch-converter`
