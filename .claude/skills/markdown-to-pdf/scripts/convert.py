#!/usr/bin/env python3
"""Convert Markdown files to A4-formatted PDF via Playwright/Chromium."""

import argparse
import re
import sys
from pathlib import Path

try:
    import markdown
except ImportError:
    print("ERROR: 'markdown' library not installed. Run: pip install markdown")
    sys.exit(1)

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("ERROR: 'playwright' not installed. Run: pip install playwright && python -m playwright install chromium")
    sys.exit(1)

# Add shared utilities to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "_shared"))
from report_generator import SkillReport


def resolve_image_paths(html_content: str, base_dir: Path) -> str:
    """Replace relative src= paths with absolute file:// URIs."""
    def to_absolute(match):
        path = match.group(1)
        if re.match(r'^(https?://|file://|data:|#|//)', path):
            return match.group(0)
        abs_path = (base_dir / path).resolve()
        if abs_path.exists():
            return f'src="{abs_path.as_uri()}"'
        return match.group(0)

    return re.sub(r'src="([^"]*)"', to_absolute, html_content)


HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
@page {{
  size: A4;
  margin: 20mm 20mm 25mm 20mm;
}}

@page {{
  @bottom-right {{
    content: counter(page) " / " counter(pages);
    font-family: Arial, sans-serif;
    font-size: 10pt;
    font-weight: normal;
    color: #000;
  }}
}}

@media print {{
  header, .no-print {{
    display: none !important;
  }}
}}

body {{
  font-family: Arial, Helvetica, sans-serif;
  font-size: 12pt;
  line-height: 1.6;
  color: #000;
  background: #fff;
  max-width: 170mm;
  margin: 0 auto;
  padding: 10mm 0;
}}

img {{
  max-width: 100%;
  height: auto;
  display: block;
}}

pre {{
  background: #2d2d2d;
  color: #f8f8f2;
  font-family: "Courier New", Courier, monospace;
  font-size: 11px;
  padding: 14px 16px;
  border-radius: 4px;
  white-space: pre-wrap;
  word-wrap: break-word;
  word-break: break-all;
  overflow-wrap: break-word;
  page-break-inside: avoid;
  margin: 12px 0;
}}

code {{
  background: #2d2d2d;
  color: #f8f8f2;
  font-family: "Courier New", Courier, monospace;
  font-size: 11px;
  padding: 2px 5px;
  border-radius: 3px;
}}

pre code {{
  background: transparent;
  padding: 0;
  font-size: inherit;
}}

h1, h2, h3, h4, h5, h6 {{
  page-break-after: avoid;
  margin-top: 1em;
  margin-bottom: 0.4em;
}}

table {{
  border-collapse: collapse;
  width: 100%;
  max-width: 100%;
  margin: 12px 0;
  page-break-inside: avoid;
}}

th, td {{
  border: 1px solid #ccc;
  padding: 6px 10px;
  text-align: left;
}}

th {{
  background: #f0f0f0;
  font-weight: bold;
}}

blockquote {{
  border-left: 4px solid #ccc;
  margin: 12px 0;
  padding: 4px 16px;
  color: #444;
}}

hr {{
  border: none;
  border-top: 1px solid #ddd;
  margin: 16px 0;
}}
</style>
</head>
<body>
{content}
</body>
</html>
"""

HTML_TEMPLATE_NO_FOOTER = HTML_TEMPLATE.replace(
    """@page {{
  @bottom-right {{
    content: counter(page) " / " counter(pages);
    font-family: Arial, sans-serif;
    font-size: 10pt;
    font-weight: normal;
    color: #000;
  }}
}}""",
    "",
)


def md_to_html(md_path: Path, no_footer: bool = False) -> Path:
    """Convert Markdown to HTML; returns path of created HTML file."""
    if not md_path.exists():
        raise FileNotFoundError(f"Markdown file not found: {md_path}")

    html_dir = md_path.parent / ".tmp"
    html_dir.mkdir(parents=True, exist_ok=True)
    html_file = html_dir / (md_path.stem + ".html")

    md_text = md_path.read_text(encoding="utf-8")

    # Remove <br> tags at end of lines so nl2br doesn't double them
    md_text = re.sub(r'[ \t]*<br\s*/?>[ \t]*\n', '\n', md_text, flags=re.IGNORECASE)

    for ext_set in (
        ["tables", "fenced_code", "toc", "nl2br"],
        ["tables", "fenced_code"],
        [],
    ):
        try:
            html_body = markdown.markdown(md_text, extensions=ext_set)
            break
        except Exception:
            continue
    else:
        html_body = markdown.markdown(md_text)

    template = HTML_TEMPLATE_NO_FOOTER if no_footer else HTML_TEMPLATE
    full_html = template.format(title=md_path.stem, content=html_body)
    full_html = resolve_image_paths(full_html, md_path.parent)

    html_file.write_text(full_html, encoding="utf-8")
    return html_file


def html_to_pdf(html_path: Path, output_dir: Path | None = None) -> Path:
    """Convert HTML to PDF using Playwright/Chromium; returns PDF path."""
    if not html_path.exists():
        raise FileNotFoundError(f"HTML file not found: {html_path}")

    pdf_dir = output_dir or (html_path.parent.parent / "pdf")
    pdf_dir.mkdir(parents=True, exist_ok=True)
    pdf_file = pdf_dir / (html_path.stem + ".pdf")

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(html_path.as_uri(), wait_until="networkidle")
        page.pdf(
            path=str(pdf_file),
            format="A4",
            print_background=True,
            display_header_footer=False,
            margin={"top": "20mm", "bottom": "25mm", "left": "20mm", "right": "20mm"},
        )
        browser.close()

    return pdf_file


def cleanup_html(html_path: Path) -> None:
    """Delete temporary HTML file and its folder if empty."""
    try:
        html_path.unlink()
    except OSError:
        pass
    try:
        html_path.parent.rmdir()
    except OSError:
        pass


def process_file(md_path: Path, output_dir: Path | None, no_footer: bool, report: SkillReport) -> None:
    """Process a single Markdown file through the full pipeline."""
    html_path = None
    try:
        html_path = md_to_html(md_path, no_footer=no_footer)
        pdf_path = html_to_pdf(html_path, output_dir=output_dir)
        report.add_success(md_path, pdf_path)
    except Exception as exc:
        report.add_failure(md_path, str(exc))
    finally:
        if html_path:
            cleanup_html(html_path)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert Markdown files to A4-formatted PDF"
    )
    parser.add_argument("files", nargs="+", help="Markdown files to convert")
    parser.add_argument(
        "--output-dir", "-o",
        type=Path,
        default=None,
        help="Custom output directory (default: pdf/ next to source)",
    )
    parser.add_argument(
        "--no-footer",
        action="store_true",
        help="Disable page counter footer",
    )

    args = parser.parse_args()

    report = SkillReport(skill_name="markdown-to-pdf")

    for file_arg in args.files:
        md_path = Path(file_arg).resolve()
        if not md_path.exists():
            report.add_failure(md_path, "File not found")
            continue
        if md_path.suffix.lower() != ".md":
            report.add_failure(md_path, f"Not a Markdown file: {md_path.suffix}")
            continue

        process_file(md_path, args.output_dir, args.no_footer, report)

    report.print_summary()
    report.exit_with_status()


if __name__ == "__main__":
    main()
