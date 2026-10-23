#!/usr/bin/env python3
"""Convert HTML files to Markdown preserving formatting as faithfully as possible."""

import sys
import os
import re
from pathlib import Path

try:
    from markdownify import markdownify as md
except ImportError:
    print("ERROR: 'markdownify' library not installed. Run: pip install markdownify")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Language detection from <pre><code class="language-X"> or data attributes
# ---------------------------------------------------------------------------

_LANG_CLASS_RE = re.compile(
    r'class=["\'](?:[^"\']*\s)?(?:language-|lang-)(\w+)', re.IGNORECASE
)
_LANG_DATA_RE = re.compile(r'data-(?:code-)?lang(?:uage)?=["\'](\w+)["\']', re.IGNORECASE)


def _detect_lang(el) -> str:
    """Return a fenced-code language tag from a <pre> or its child <code> element."""
    for node in [el] + (el.find_all("code") or []):
        cls = " ".join(node.get("class") or [])
        m = _LANG_CLASS_RE.search(cls)
        if m:
            return m.group(1).lower()
        for attr in ("data-lang", "data-language", "data-code-language"):
            val = node.get(attr, "")
            if val:
                return val.strip().lower()
    return ""


# ---------------------------------------------------------------------------
# Conversion
# ---------------------------------------------------------------------------

def html_to_markdown(html: str) -> str:
    """Convert an HTML string to Markdown using markdownify with post-processing."""
    result = md(
        html,
        heading_style="ATX",
        bullets="-",
        code_language_callback=_detect_lang,
        newline_style="backslash",
        strip=["script", "style", "head", "nav", "footer", "aside"],
    ).strip()

    # Collapse 3+ consecutive blank lines to at most one blank line
    result = re.sub(r'\n{3,}', '\n\n', result)

    return result + "\n"


# ---------------------------------------------------------------------------
# File I/O
# ---------------------------------------------------------------------------

def convert_file(html_path: Path, out_dir: Path | None) -> Path:
    """Convert a single HTML file; return the path of the written .md file."""
    if not html_path.exists():
        raise FileNotFoundError(f"File not found: {html_path}")

    html = html_path.read_text(encoding="utf-8")
    markdown = html_to_markdown(html)

    dest_dir = out_dir if out_dir else html_path.parent
    dest_dir.mkdir(parents=True, exist_ok=True)
    md_path = dest_dir / (html_path.stem + ".md")
    md_path.write_text(markdown, encoding="utf-8")
    return md_path


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help"):
        print("Usage: convert.py <file1.html> [file2.html ...] [--out-dir <dir>]")
        print()
        print("Converts each .html file to a .md file with faithful Markdown formatting.")
        print("Output is written next to the source file unless --out-dir is specified.")
        sys.exit(0)

    out_dir: Path | None = None
    files: list[Path] = []

    i = 0
    while i < len(args):
        if args[i] in ("--out-dir", "-o") and i + 1 < len(args):
            out_dir = Path(args[i + 1])
            i += 2
        else:
            files.append(Path(args[i]))
            i += 1

    if not files:
        print("ERROR: No HTML files specified.", file=sys.stderr)
        sys.exit(1)

    errors: list[tuple[str, str]] = []
    for html_path in files:
        try:
            md_path = convert_file(html_path, out_dir)
            print(f"  [OK]  {html_path}  ->  {md_path}")
        except Exception as exc:
            print(f"  [ERR] {html_path}: {exc}", file=sys.stderr)
            errors.append((str(html_path), str(exc)))

    print()
    if errors:
        print(f"Finished with {len(errors)} error(s).")
        sys.exit(1)
    else:
        count = len(files)
        print(f"{'All' if count > 1 else '1'} file{'s' if count > 1 else ''} converted successfully.")


if __name__ == "__main__":
    main()
