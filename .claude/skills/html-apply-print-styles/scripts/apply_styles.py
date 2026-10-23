#!/usr/bin/env python3
"""Apply A4 print styles and pagination footer to HTML files."""

import sys
from pathlib import Path

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("ERROR: 'beautifulsoup4' not installed. Run: pip install beautifulsoup4")
    sys.exit(1)

# Add shared utilities to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "_shared"))
from report_generator import SkillReport


PRINT_STYLES = """
/* Print styles injected by html-apply-print-styles */
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

  a {
    color: #000000 !important;
    text-decoration: underline;
  }

  pre, code {
    background: #f5f5f5 !important;
    color: #000000 !important;
    border: 1px solid #ddd;
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


def apply_print_styles(html_path: Path, report: SkillReport) -> None:
    """Apply print styles to a single HTML file."""
    html = html_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")

    # Ensure <head> exists
    head = soup.find("head")
    if not head:
        head = soup.new_tag("head")
        if soup.html:
            soup.html.insert(0, head)
        else:
            soup.insert(0, head)

    # Check if print styles already applied
    existing_style = head.find("style", string=lambda s: s and "Print styles injected" in s)
    if existing_style:
        report.add_success(html_path, html_path, note="Print styles already applied, skipped")
        return

    # Create or append to style tag
    style_tag = head.find("style")
    if style_tag:
        style_tag.string = (style_tag.string or "") + "\n" + PRINT_STYLES
    else:
        style_tag = soup.new_tag("style")
        style_tag.string = PRINT_STYLES
        head.append(style_tag)

    # Ensure body has white background
    body = soup.find("body")
    if body:
        current_style = body.get("style", "")
        if "background" not in current_style.lower():
            body["style"] = f"{current_style}; background-color: #FFFFFF;".strip("; ")

    html_path.write_text(str(soup), encoding="utf-8")
    report.add_success(html_path, html_path, note="Print styles applied")


def main() -> None:
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help"):
        print("Usage: apply_styles.py <file1.html> [file2.html ...]")
        print("\nApplies A4 print styles and pagination footer to HTML files.")
        sys.exit(0)

    report = SkillReport(skill_name="html-apply-print-styles")

    for arg in args:
        path = Path(arg)
        if not path.exists():
            report.add_failure(path, "File not found")
            continue
        if path.suffix.lower() not in (".html", ".htm"):
            report.add_failure(path, f"Not an HTML file: {path.suffix}")
            continue

        try:
            apply_print_styles(path.resolve(), report)
        except Exception as exc:
            report.add_failure(path, str(exc))

    report.print_summary()
    report.exit_with_status()


if __name__ == "__main__":
    main()
