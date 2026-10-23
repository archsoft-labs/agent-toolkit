#!/usr/bin/env python3
"""Normalize image references in HTML files: rename to kebab-case and organize into images/ folder."""

import re
import shutil
import sys
from pathlib import Path

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("ERROR: 'beautifulsoup4' not installed. Run: pip install beautifulsoup4")
    sys.exit(1)

# Add shared utilities to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "_shared"))
from html_processor import to_kebab_case, ensure_directory
from report_generator import SkillReport


def normalize_images(html_path: Path, report: SkillReport) -> None:
    """Process a single HTML file: rename images and update references."""
    html = html_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")

    images = soup.find_all("img")
    if not images:
        report.add_success(html_path, html_path, images_found=0, note="No images to normalize")
        return

    # Setup images directory
    images_dir = ensure_directory(html_path.parent / "images")
    base_name = to_kebab_case(html_path.stem)

    # Track renames for deduplication
    src_to_new_name: dict[str, str] = {}
    counter = 1

    for img in images:
        src = img.get("src", "")
        if not src or src.startswith(("http://", "https://", "data:", "//")):
            continue

        # Resolve source path
        src_path = (html_path.parent / src).resolve()
        if not src_path.exists():
            continue

        # Deduplicate: same source gets same target name
        src_key = str(src_path)
        if src_key in src_to_new_name:
            new_name = src_to_new_name[src_key]
        else:
            ext = src_path.suffix.lower()
            new_name = f"{base_name}-image-{counter:03d}{ext}"
            counter += 1
            src_to_new_name[src_key] = new_name

            # Copy to images folder
            dest_path = images_dir / new_name
            shutil.copy2(src_path, dest_path)

        # Update reference
        img["src"] = f"images/{new_name}"

    # Write updated HTML
    html_path.write_text(str(soup), encoding="utf-8")
    report.add_success(
        html_path,
        html_path,
        images_found=len(images),
        images_normalized=len(src_to_new_name),
        images_dir=str(images_dir),
    )


def main() -> None:
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help"):
        print("Usage: normalize.py <file1.html> [file2.html ...]")
        print("\nRenames images to kebab-case and organizes into images/ folder.")
        sys.exit(0)

    report = SkillReport(skill_name="html-normalize-images")

    for arg in args:
        path = Path(arg)
        if not path.exists():
            report.add_failure(path, "File not found")
            continue
        if path.suffix.lower() not in (".html", ".htm"):
            report.add_failure(path, f"Not an HTML file: {path.suffix}")
            continue

        try:
            normalize_images(path.resolve(), report)
        except Exception as exc:
            report.add_failure(path, str(exc))

    report.print_summary()
    report.exit_with_status()


if __name__ == "__main__":
    main()
