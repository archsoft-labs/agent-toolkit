---
name: html-fetch-url
description: >
  Fetches HTML pages from URLs and saves them as local files with
  localized images. Uses curl for public pages and escalates to
  browser-harness (real Chrome via CDP) for JS-rendered, login-walled,
  or bot-protected pages. Produces a local .html file ready for
  downstream skills (extract, normalize, translate, PDF).
  Use when the user provides a URL (http/https) instead of a file path.
  Trigger phrases: "fetch url", "download page", "save webpage",
  "get html from url", "process this link", "capture this page",
  "baixar página", "salvar url", "capturar html da url",
  "extrair desta url", "processar este link".
  DO NOT trigger for: local file paths (use the target skill directly),
  fetching non-HTML content (PDFs, images, JSON APIs), or interactive
  browsing sessions that need clicking/typing (use browser-harness directly).
allowed-tools: Bash, Read, Write
---

# HTML Fetch URL

Downloads HTML pages from URLs and saves them as local files with images
localized to an `images/` folder, producing a self-contained snapshot ready
for the rest of the HTML pipeline (`html-extract-content`,
`html-normalize-images`, `html-translate`, `html-apply-print-styles`,
`html-to-pdf`, `html-to-markdown`).

## What This Skill Does

1. **Fetches** the page HTML using `curl` (fast path for public pages)
2. **Escalates to `browser-harness`** automatically when curl returns a
   JavaScript shell, an HTTP error, or a known bot-challenge marker
3. **Localizes images**: downloads every `<img src>` to `images/` and
   rewrites the attribute to the relative local path
4. **Writes** the final HTML to `<output-dir>/<slug>/<slug>.html`

## Fetch Strategy

| Mode | When used | Cost | Requirement |
|------|-----------|------|-------------|
| `curl` (default) | Public, server-rendered pages | Milliseconds, no deps | `curl` on PATH (built into Windows 10+, macOS, Linux) |
| `browser-harness` (auto-fallback or `--via browser-harness`) | SPAs, JS-rendered DOM, Cloudflare/anti-bot, login walls | Real Chrome instance + CDP daemon | `browser-harness` CLI installed and Chrome running with remote debugging |

The default mode is `auto`: curl first, escalate to `browser-harness` only
when curl's output looks like a shell page. Force a specific mode with
`--via curl` or `--via browser-harness`.

### Escalation Heuristics (auto mode)

Curl output escalates to `browser-harness` when any of these is true:

- HTTP status ≥ 400 (403, 503, etc.)
- HTML body is < 2 KB **and** contains no `<article>` or `<main>` tag
- HTML contains known challenge markers:
  - `Just a moment` (Cloudflare)
  - `Enable JavaScript` / `Please enable JS`
  - `cf-challenge` / `cf-browser-verification`
  - `__NEXT_DATA__` present but the rendered body is empty

## Quick Start

```bash
# Fetch a public page (curl fast path)
python <skill-path>/scripts/fetch.py https://example.com/article

# Fetch with explicit browser rendering (SPA / login wall)
python <skill-path>/scripts/fetch.py https://app.example.com/dashboard --via browser-harness

# Fetch multiple pages into a custom directory
python <skill-path>/scripts/fetch.py https://a.com/p1 https://b.com/p2 --output-dir ./captures/

# Skip image localization (HTML keeps remote URLs)
python <skill-path>/scripts/fetch.py https://example.com/article --no-images

# Custom timeout (default 30s)
python <skill-path>/scripts/fetch.py https://slow-site.com --timeout 60
```

## Output Structure

Each URL produces one self-contained directory:

```
<cwd or --output-dir>/
└── <slug>/                       # slug derived from hostname + path
    ├── <slug>.html               # the page HTML, img src rewritten to local
    └── images/                   # omitted if --no-images or page has no <img>
        ├── <slug>-image-001.jpg
        ├── <slug>-image-002.png
        └── ...
```

**Slug rules:** hostname + last two path segments, kebab-case. A short query
hash is appended when the URL has a query string (`?p=1` → `-a1b2c3`) so
distinct URLs never collide.

## Options

| Flag | Description |
|------|-------------|
| `--output-dir <dir>` | Parent directory for the `<slug>/` folder (default: current directory) |
| `--via {auto,curl,browser-harness}` | Force a fetch strategy (default: `auto`) |
| `--no-images` | Skip image download; `<img src>` keeps remote URLs |
| `--timeout <seconds>` | HTTP/browser timeout in seconds (default: 30) |

## Browser-Harness Integration

When escalation is needed, the script invokes the `browser-harness` CLI via
`subprocess`, sending a small Python snippet on stdin:

```python
new_tab(url)
wait_for_load()
html = js("document.documentElement.outerHTML")
imgs = js("Array.from(document.images).map(i => i.src)")
```

The snippet returns a JSON payload with the rendered HTML plus the live list
of image URLs (which may include images added by JavaScript that a static
curl fetch would miss). The outer script then downloads those image URLs
with `urllib`.

### Requirements for browser-harness fallback

- `browser-harness` CLI on PATH (`pip install browser-harness` or see
  https://github.com/browser-use/browser-harness/blob/main/install.md)
- Chrome/Chromium running with remote debugging enabled
- **Windows / macOS**: Chrome may show an *"Allow remote debugging?"* prompt
  the first time. The script prints a notice; the user clicks **Allow** and
  the fetch resumes automatically. Do not retry the command — the click
  completes the handshake.
- If `browser-harness` is missing or fails, the script reports a clear error
  suggesting `browser-harness --doctor` and the curl result is preserved for
  inspection.

## Image Localization

For each `<img>` tag in the fetched HTML:

1. Skip if `src` is empty, `data:`, `blob:`, or `#`
2. Resolve to an absolute URL with `urllib.parse.urljoin(page_url, src)`
   (handles relative, protocol-relative `//`, and absolute sources)
3. Dedupe by normalized URL — same source gets the same filename
4. Extension comes from the URL path; fallback to `Content-Type` header
   (`image/jpeg` → `.jpg`, `image/png` → `.png`, `image/webp` → `.webp`,
   `image/gif` → `.gif`, `image/svg+xml` → `.svg`)
5. Download to `images/<slug>-image-NNN.<ext>` (same naming convention as
   `html-normalize-images`)
6. Rewrite `<img src>` to `images/<slug>-image-NNN.<ext>`

### Known limitation: authenticated images

Images that require the user's logged-in session (cookies) are still
downloaded with a plain HTTP GET, even when the page itself was fetched via
`browser-harness`. If an image fails with 401/403, the script logs a warning
and keeps the remote `src` for that image. For fully offline captures of
authenticated pages, save the page manually from the browser instead.

## Dependencies

- Python 3.8+
- `beautifulsoup4`: `pip install beautifulsoup4`
- `curl` (system binary; bundled with Windows 10+, macOS, most Linux distros)
- **Optional** — `browser-harness` CLI: only needed for JS-rendered or
  protected pages, or when `--via browser-harness` is used explicitly

## Integration with the HTML Pipeline

This skill is the **entry point** when the user provides a URL. Once the
page is saved locally, downstream skills operate on the file unchanged:

```
html-fetch-url
  → html-extract-content
  → html-normalize-images   (renames again — see note below)
  → html-translate
  → html-apply-print-styles
  → html-to-pdf
```

The `html-processor` agent detects URLs in user input and invokes this skill
automatically as step zero.

### Note on `html-normalize-images` after `html-fetch-url`

`html-fetch-url` already names images as `images/<slug>-image-NNN.ext`. When
`html-normalize-images` runs on the cleaned file (e.g. `<slug>-clean.html`),
it uses **its own** file stem as the base name, producing
`images/<slug>-clean-image-NNN.ext` and copying the files again. The end
result is consistent and correct — just expect a second pass of renaming
with the new base name. The older `<slug>-image-NNN.ext` files remain on
disk and can be cleaned up manually if disk usage matters; the pipeline
always references the latest names.

## Bundled Script

See `scripts/fetch.py` — run directly, no wrapper needed.

## Notes

- **Idempotent**: re-running with the same URL overwrites the same `<slug>/`
  folder. Safe to retry after a failure.
- **Stop on failure**: if any step fails for a URL, that URL is marked
  `[ERR]` in the report and the script moves to the next one; the exit code
  reflects whether any URL failed.
- **No retry loop**: transient network errors are reported, not retried.
  Re-run the command to retry.
