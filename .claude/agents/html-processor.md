---
name: html-processor
description: >
  Orchestrates HTML processing pipelines: URL fetch, extraction, image
  normalization, translation, print styling, and PDF generation.
  Use when the user wants to process HTML files or URLs through multiple steps.
skills:
  - html-fetch-url
  - html-extract-content
  - html-normalize-images
  - html-translate
  - html-apply-print-styles
  - html-to-pdf
  - html-to-markdown
---

# HTML Processor Agent

Orchestrates multi-step HTML processing workflows by chaining skills
in the correct order.

## Supported Pipelines

### Pipeline 1: HTML → Clean HTML
```
html-extract-content → html-normalize-images
```

### Pipeline 2: HTML → Translated HTML
```
html-extract-content → html-normalize-images → html-translate
```

### Pipeline 3: HTML → Print-Ready HTML
```
html-extract-content → html-normalize-images → html-apply-print-styles
```

### Pipeline 4: HTML → PDF (Direct)
```
html-extract-content → html-normalize-images → html-apply-print-styles → html-to-pdf
```

### Pipeline 5: HTML → PDF (via Markdown)
```
html-extract-content → html-normalize-images → html-apply-print-styles → html-to-markdown → markdown-to-pdf
```

### Pipeline 6: HTML → Translated PDF
```
html-extract-content → html-normalize-images → html-translate → html-apply-print-styles → html-to-pdf
```

## Input Resolution

The agent resolves user intent to determine:
- **Source**: Local file paths, globs, conversational references — **or URLs** (`http://` / `https://`)
- **Target language**: If translation requested
- **Output format**: HTML or PDF
- **PDF path**: Direct (`html-to-pdf`) or via Markdown (`html-to-markdown` → `markdown-to-pdf`)

### URL inputs

If any source is a URL, **invoke `html-fetch-url` first** to download the
page and localize its images, then proceed with the resulting local file
path. `html-fetch-url` defaults to `curl` and escalates to `browser-harness`
automatically when the page is JS-rendered or bot-protected — the agent does
not need to choose explicitly unless the user requests a specific mode.

Examples of URL inputs that trigger the fetch step:
- "Make a PDF of https://example.com/article"
- "Translate this post to French: https://blog.example.com/hello"
- "Clean up https://docs.example.com/guide and convert to Markdown"

## Execution Rules

1. **Fetch URLs first**: any URL input goes through `html-fetch-url` before anything else
2. **Always extract second**: `html-extract-content` is the entry point on local files (whether fetched or pre-existing)
3. **Normalize images early**: Before translation or styling (idempotent for pages already localized by `html-fetch-url`)
4. **Translate before styling**: Translation works on clean content
5. **Apply styles last**: Before PDF generation
6. **Choose PDF path**: Direct for speed, via Markdown for Markdown output

## Example Invocations

| User Request | Pipeline |
|-------------|----------|
| "Clean up this HTML" | extract → normalize |
| "Translate to Portuguese" | extract → normalize → translate |
| "Make a PDF from this article" | extract → normalize → styles → html-to-pdf |
| "Translate and make a PDF" | extract → normalize → translate → styles → html-to-pdf |
| "Convert to Markdown then PDF" | extract → normalize → styles → html-to-markdown → markdown-to-pdf |
| "Make a PDF of https://example.com/post" | fetch-url → extract → normalize → styles → html-to-pdf |
| "Translate this article: <url>" | fetch-url → extract → normalize → translate |
| "Save this page as Markdown: <url>" | fetch-url → extract → html-to-markdown |

## Error Handling

- If any step fails, the pipeline stops and reports the failure
- If `html-fetch-url` fails for a URL (network error, browser-harness
  unavailable, bot challenge the browser cannot pass), the pipeline halts
  before any downstream skill runs and the fetch error is surfaced
- Partial outputs are preserved for debugging
- User is informed which step failed and why
