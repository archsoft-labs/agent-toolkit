#!/usr/bin/env python3
"""Convert HTML files directly to A4-formatted PDF via Playwright/Chromium."""

import argparse
import re
import sys
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("ERROR: 'playwright' not installed. Run: pip install playwright && python -m playwright install chromium")
    sys.exit(1)

# Add shared utilities to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "_shared"))
from report_generator import SkillReport


DEFAULT_PRINT_STYLES = """
@page {
  size: A4;
  margin: 20mm 20mm 25mm 20mm;

  @bottom-right {
    content: counter(page) " / " counter(pages);
    font-family: Arial, Helvetica, sans-serif;
    font-size: 10pt;
    color: #000;
  }
}

@media print {
  body {
    background: #FFFFFF !important;
    color: #000000 !important;
    max-width: 170mm;
    margin: 0 auto;
    padding: 10mm 0;
  }

  img {
    max-width: 100% !important;
    page-break-inside: avoid;
  }

  h1, h2, h3, h4, h5, h6 {
    page-break-after: avoid;
  }

  table {
    page-break-inside: avoid;
  }
}
"""


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


def has_print_styles(html: str) -> bool:
    """Check if HTML already has print styles."""
    return "@page" in html or "@media print" in html


def inject_print_styles(html: str) -> str:
    """Inject default print styles into HTML."""
    if "</head>" in html:
        return html.replace("</head>", f"<style>{DEFAULT_PRINT_STYLES}</style></head>")
    return html


def html_to_pdf(html_path: Path, output_dir: Path | None = None) -> Path:
    """Convert HTML to PDF using Playwright/Chromium; returns PDF path."""
    if not html_path.exists():
        raise FileNotFoundError(f"HTML file not found: {html_path}")

    # Read and prepare HTML
    html = html_path.read_text(encoding="utf-8")
    html = resolve_image_paths(html, html_path.parent)

    if not has_print_styles(html):
        html = inject_print_styles(html)

    # Setup output
    pdf_dir = output_dir or (html_path.parent / "pdf")
    pdf_dir.mkdir(parents=True, exist_ok=True)
    pdf_file = pdf_dir / (html_path.stem + ".pdf")

    # Create temp file with resolved paths
    tmp_dir = html_path.parent / ".tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    tmp_file = tmp_dir / html_path.name
    tmp_file.write_text(html, encoding="utf-8")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(tmp_file.as_uri(), wait_until="networkidle")
            page.pdf(
                path=str(pdf_file),
                format="A4",
                print_background=True,
                display_header_footer=False,
                margin={"top": "20mm", "bottom": "25mm", "left": "20mm", "right": "20mm"},
            )
            browser.close()
    finally:
        # Cleanup temp file
        try:
            tmp_file.unlink()
            tmp_dir.rmdir()
        except OSError:
            pass

    return pdf_file


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert HTML files directly to A4-formatted PDF"
    )
    parser.add_argument("files", nargs="+", help="HTML files to convert")
    parser.add_argument(
        "--output-dir", "-o",
        type=Path,
        default=None,
        help="Custom output directory (default: pdf/ next to source)",
    )

    args = parser.parse_args()

    report = SkillReport(skill_name="html-to-pdf")

    for file_arg in args.files:
        html_path = Path(file_arg).resolve()
        if not html_path.exists():
            report.add_failure(html_path, "File not found")
            continue
        if html_path.suffix.lower() not in (".html", ".htm"):
            report.add_failure(html_path, f"Not an HTML file: {html_path.suffix}")
            continue

        try:
            pdf_path = html_to_pdf(html_path, output_dir=args.output_dir)
            report.add_success(html_path, pdf_path)
        except Exception as exc:
            report.add_failure(html_path, str(exc))

    report.print_summary()
    report.exit_with_status()


if __name__ == "__main__":
    main()
