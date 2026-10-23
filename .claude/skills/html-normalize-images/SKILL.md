---
name: html-normalize-images
description: >
  Renames and organizes images referenced in HTML files into a standardized
  images/ folder with kebab-case naming. Updates all <img> src attributes
  to point to the renamed files.
  Use when the user wants to standardize image naming in HTML files.
  Trigger phrases: "normalize images", "rename images", "organize images",
  "standardize image names", "fix image paths", "arrumar imagens", "renomear imagens".
  DO NOT trigger for: extracting content, translating, or applying styles.
allowed-tools: Bash, Read, Write, Glob
---

# HTML Normalize Images

Standardizes image references in HTML files by renaming images to a consistent
kebab-case pattern and organizing them into an `images/` folder.

## What This Skill Does

1. Scans HTML for all `<img>` tags
2. Copies referenced images to an `images/` folder next to the HTML file
3. Renames images using pattern: `{html-filename}-image-{number:03d}.{ext}`
4. Updates all `<img src="...">` attributes to point to the new paths

## Quick Start

```bash
# Install dependencies (if not already installed)
pip install beautifulsoup4

# Normalize images in a single file
python <skill-path>/scripts/normalize.py path/to/file.html

# Process multiple files
python <skill-path>/scripts/normalize.py file1.html file2.html folder/*.html
```

## Naming Pattern

| Input | Output |
|-------|--------|
| `My Page.html` + `photo.jpg` | `images/my-page-image-001.jpg` |
| `article.html` + `diagram.png` | `images/article-image-001.png` |

## Output Structure

```
project/
├── document.html
└── images/
    ├── document-image-001.png
    ├── document-image-002.jpg
    └── document-image-003.gif
```

## Dependencies

- Python 3.8+
- `beautifulsoup4`: `pip install beautifulsoup4`

## Notes

- Original images are **copied**, not moved (source files preserved)
- Existing `images/` folder is reused if present
- Duplicate image references are deduplicated (same source = same target)
- External URLs (`http://`, `https://`) are left unchanged
