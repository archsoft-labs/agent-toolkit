#!/usr/bin/env python3
"""Extract main content from HTML files, removing boilerplate."""

import re
import sys
from pathlib import Path
from urllib.parse import urljoin

try:
    from bs4 import BeautifulSoup, Tag
except ImportError:
    print("ERROR: 'beautifulsoup4' not installed. Run: pip install beautifulsoup4")
    sys.exit(1)

# Add shared utilities to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "_shared"))
from html_processor import to_kebab_case
from report_generator import SkillReport


# Elements to always remove
BOILERPLATE_TAGS = [
    "script", "style", "nav", "footer", "aside", "header",
    "form", "iframe", "noscript", "template",
]

# Attributes to preserve
PRESERVE_ATTRS = {"href", "src", "alt", "title", "class", "id"}


# Minimum text length for a block to be considered main content
MIN_CONTENT_CHARS = 500


def find_main_content(soup: BeautifulSoup) -> Tag | None:
    """Identify the main content element using semantic and structural signals."""
    # Signal 1: Semantic tags
    main_tag = soup.find("main")
    if main_tag:
        return main_tag

    # <article> is only a main-content signal when it is unambiguous:
    # a single article, or multiple articles where exactly one is large enough
    # to be the main content. Pages with several small <article> blocks (FAQs,
    # cards, comments) must fall through to the structural signals below.
    articles = soup.find_all("article")
    if articles:
        large = [
            a for a in articles
            if len(a.get_text(strip=True)) >= MIN_CONTENT_CHARS
        ]
        if len(articles) == 1 and (large or len(articles[0].get_text(strip=True)) > 0):
            return articles[0]
        if len(large) == 1:
            return large[0]
        # Ambiguous or all-too-small articles: keep looking.

    # Signal 2: Common content wrappers. Start from each pattern match and
    # descend into the child that holds most of the text — outer catch-all
    # wrappers (e.g. #main-container holding nav + content + footer) lose to
    # the tightest inner wrapper that still holds the bulk of the content.
    content_patterns = re.compile(
        r"content|post|body|entry|text|main|article|story", re.IGNORECASE
    )
    matches = [
        tag for tag in soup.find_all(["div", "section"])
        if content_patterns.search(" ".join(tag.get("class", [])))
        or content_patterns.search(tag.get("id", ""))
    ]
    if matches:
        # Largest match is the starting point (guaranteed to hold the content).
        best = max(matches, key=lambda t: len(t.get_text(strip=True)))
        # Descend while a single child carries >= 80% of the text — that child
        # is a tighter wrapper around the same content. Never descend past a
        # content heading: a wrapper's own <h1>/<h2> (one not buried inside
        # nav/header/footer boilerplate) belongs to the content even if it is
        # a small share of the text.
        def has_content_heading(tag: Tag) -> bool:
            for h in tag.find_all(["h1", "h2"]):
                if not h.find_parent(["nav", "header", "footer", "aside"]):
                    return True
            return False

        current = best
        while True:
            if has_content_heading(current):
                break
            children = [
                c for c in current.find_all(recursive=False)
                if isinstance(c, Tag) and len(c.get_text(strip=True)) >= len(current.get_text(strip=True)) * 0.8
            ]
            if len(children) != 1:
                break
            current = children[0]
        # If the descent stopped at a catch-all wrapper (nav + content + footer
        # as siblings), prefer a direct child that also matches the content
        # pattern — it is the content block proper, not the chrome around it.
        inner_matches = [
            c for c in current.find_all(recursive=False)
            if isinstance(c, Tag) and c in matches
        ]
        if len(inner_matches) == 1:
            current = inner_matches[0]
        return current

    # Signal 3: Largest text block with heading
    candidates = []
    for tag in soup.find_all(["div", "section"]):
        text = tag.get_text(strip=True)
        if len(text) > MIN_CONTENT_CHARS:
            heading = tag.find(["h1", "h2"])
            score = len(text) + (500 if heading else 0)
            candidates.append((score, tag))

    if candidates:
        candidates.sort(key=lambda x: x[0], reverse=True)
        return candidates[0][1]

    return None


def clean_content(element: Tag) -> Tag:
    """Remove boilerplate and clean attributes from content element."""
    # Wrap in an isolated tree so boilerplate removal never touches the
    # original document, and so the wrapper element itself is preserved
    # (soup.find(element.name) would return a nested same-name tag instead).
    soup = BeautifulSoup("<container></container>", "html.parser")
    container = soup.find("container")
    container.append(BeautifulSoup(str(element), "html.parser"))
    content = container

    # Remove boilerplate tags
    for tag_name in BOILERPLATE_TAGS:
        for tag in content.find_all(tag_name):
            tag.decompose()

    # Remove HTML comments
    for comment in content.find_all(string=lambda s: isinstance(s, str) and s.strip().startswith("<!--")):
        comment.extract()

    # Clean attributes
    for tag in content.find_all(True):
        attrs_to_remove = [
            attr for attr in tag.attrs
            if attr not in PRESERVE_ATTRS and not attr.startswith("data-")
        ]
        for attr in attrs_to_remove:
            del tag[attr]

    # Unwrap the temporary <container>, returning the cleaned content element
    children = [c for c in container.find_all(recursive=False)]
    return children[0] if len(children) == 1 else container


def extract_content_styled(html_path: Path, report: SkillReport) -> None:
    """Extract main content while preserving the original document's CSS.

    Instead of moving the content into a bare skeleton (which loses all
    styling), this keeps the original <head> — inline styles and external
    stylesheets, with relative URLs resolved to absolute — and removes from
    the body everything that is not the main content: scripts, boilerplate
    chrome, and the siblings of the content wrapper. The content keeps its
    original classes, so the page renders with the site's own CSS.
    """
    html = html_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")

    main_content = find_main_content(soup)
    if not main_content:
        report.add_failure(html_path, "Could not identify main content")
        return

    # Record the content's ancestor chain up to <body> before mutating, so we
    # can keep the wrappers (they carry layout classes the CSS depends on).
    chain = []
    node = main_content
    while node and isinstance(node, Tag) and node.name != "body":
        chain.append(node)
        node = node.parent

    # Many SPAs hold content hidden until JS reveals it (e.g.
    # "html.pa-hold #content{visibility:hidden}"). Scripts are removed below,
    # so the reveal never happens and the page renders blank. Strip the
    # anti-FOUC hold class from <html> so those rules simply stop matching.
    # (Do NOT try to edit the CSS text — regex over nested @media rules is
    # unreliable and can corrupt the whole stylesheet.)
    html_tag = soup.find("html")
    if html_tag and html_tag.get("class"):
        for cls in list(html_tag["class"]):
            if "hold" in cls.lower() or cls.lower() in ("no-js", "nojs"):
                html_tag["class"].remove(cls)

    # Resolve relative stylesheet/icon URLs against the page's own location so
    # the saved file still loads the site's CSS. Local HTML files have no base
    # URL, so read it from <base>, a canonical link, or the og:url meta.
    base_url = ""
    base_tag = soup.find("base", href=True)
    if base_tag:
        base_url = base_tag["href"]
    if not base_url:
        canonical = soup.find("link", rel="canonical", href=True)
        if canonical:
            base_url = canonical["href"]
    if not base_url:
        og = soup.find("meta", property="og:url")
        if og and og.get("content"):
            base_url = og["content"]

    if base_url:
        for link in soup.find_all("link", href=True):
            link["href"] = urljoin(base_url, link["href"])

    # Lazy-loaded images keep the real URL in data-src while src holds a tiny
    # placeholder. Without the JS that swaps them, the placeholder is all that
    # renders. Promote data-src to src so the real image loads.
    for img in soup.find_all("img"):
        data_src = img.get("data-src")
        src = img.get("src") or ""
        if data_src and ("placeholder" in src or src.endswith(".gif") or not src):
            img["src"] = urljoin(base_url, data_src) if base_url else data_src

    # Remove scripts from the whole document (they are never content and can
    # break or phone home when the file is opened locally).
    for script in soup.find_all("script"):
        script.decompose()

    # Remove every body-level element that is not on the content path.
    body = soup.find("body")
    if body:
        for child in list(body.find_all(recursive=False)):
            if child not in chain:
                child.decompose()

        # Walk down the kept chain: at each level remove siblings that are
        # boilerplate chrome or carry no content. Chrome is identified by tag
        # (nav/header/footer/aside) or by id/class naming (header, nav, footer,
        # sidebar), because many pages mark chrome with a plain <div>.
        chrome_re = re.compile(
            r"header|nav|footer|sidebar|cookie|banner|breadcrumb|leftnav", re.IGNORECASE
        )

        def is_chrome(tag: Tag) -> bool:
            if tag.name in ("nav", "header", "footer", "aside", "form", "iframe"):
                return True
            ident = " ".join(tag.get("class", [])) + " " + (tag.get("id") or "")
            return bool(chrome_re.search(ident))

        for wrapper in chain:
            for child in list(wrapper.find_all(recursive=False)):
                if child in chain or child == main_content:
                    continue
                if is_chrome(child) or len(child.get_text(strip=True)) == 0:
                    child.decompose()

        # Inside the content itself, drop boilerplate chrome by tag only —
        # matching by id/class here would risk deleting real content blocks.
        for tag_name in ("nav", "header", "footer", "aside", "form", "iframe", "noscript"):
            for tag in main_content.find_all(tag_name):
                tag.decompose()

        # Catalogs and SPA content are often hidden by the site's external CSS
        # until JS reveals them (cards with display:none, [data-] gated rules).
        # Scripts are gone, so force the content and its descendants visible.
        # This override is appended last so it wins over the external sheets.
        override = soup.new_tag("style")
        # The site's CSS hides the whole catalog behind `#catalog-content
        # .hide-content a.coursebox-container{display:none !important}` and the
        # per-card description/tags with `display:none` — all meant to be
        # revealed by JS. Match that exact specificity (with !important) to
        # win it back, and force the anti-FOUC opacity/visibility holds off.
        override.string = (
            "\n/* html-extract-content: reveal content hidden for JS */\n"
            "html body #catalog-content.hide-content a.coursebox-container { display: block !important; }\n"
            "html body a.coursebox-container.course .coursebox-text-description { display: block !important; }\n"
            "html body a.coursebox-container .coursebox-tags { display: flex !important; gap: 0.5em; flex-wrap: wrap; }\n"
            "html body .coursebox-tag { margin-right: 0.75em; }\n"
            "html body .coursebox-tag[data-tag^=\"partner-home-widget\"] { display: none !important; }\n"
            "html body #main-container, html body #skilljar-content { visibility: visible !important; opacity: 1 !important; }\n"
            "html body #skilljar-content * { opacity: 1 !important; visibility: visible !important; }\n"
            "html body .coursebox-image img { max-width: 100%; height: auto !important; }\n"
        )
        if body:
            body.append(override)

    output_path = html_path.parent / f"{html_path.stem}-styled.html"
    output_path.write_text(str(soup), encoding="utf-8")

    original_text = len(BeautifulSoup(html, "html.parser").get_text(strip=True))
    extracted_text = len(soup.get_text(strip=True))
    reduction = ((original_text - extracted_text) / original_text * 100) if original_text else 0

    report.add_success(
        html_path,
        output_path,
        original_chars=original_text,
        extracted_chars=extracted_text,
        reduction_percent=f"{reduction:.1f}%",
    )


def extract_content(html_path: Path, report: SkillReport) -> None:
    """Extract main content from a single HTML file into a bare skeleton."""
    html = html_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")

    # Find main content
    main_content = find_main_content(soup)
    if not main_content:
        report.add_failure(html_path, "Could not identify main content")
        return

    # Clean the content
    cleaned = clean_content(main_content)

    # Build output HTML
    output_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html_path.stem}</title>
</head>
<body>
{cleaned.prettify()}
</body>
</html>
"""

    # Write output
    output_path = html_path.parent / f"{html_path.stem}-clean.html"
    output_path.write_text(output_html, encoding="utf-8")

    # Stats
    original_text = len(soup.get_text(strip=True))
    extracted_text = len(cleaned.get_text(strip=True))
    reduction = ((original_text - extracted_text) / original_text * 100) if original_text else 0

    report.add_success(
        html_path,
        output_path,
        original_chars=original_text,
        extracted_chars=extracted_text,
        reduction_percent=f"{reduction:.1f}%",
    )


def main() -> None:
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help"):
        print("Usage: extract.py [--keep-styles] <file1.html> [file2.html ...]")
        print("\nExtracts main content from HTML files, removing boilerplate.")
        print("\nModes:")
        print("  (default)       Move the content into a bare semantic skeleton.")
        print("  --keep-styles   Keep the original document and its CSS; remove only")
        print("                  non-content chrome (scripts, nav, header, footer).")
        sys.exit(0)

    keep_styles = False
    if args and args[0] == "--keep-styles":
        keep_styles = True
        args = args[1:]

    if not args:
        print("ERROR: no input files given.", file=sys.stderr)
        sys.exit(1)

    report = SkillReport(skill_name="html-extract-content")

    for arg in args:
        path = Path(arg)
        if not path.exists():
            report.add_failure(path, "File not found")
            continue
        if path.suffix.lower() not in (".html", ".htm"):
            report.add_failure(path, f"Not an HTML file: {path.suffix}")
            continue

        try:
            if keep_styles:
                extract_content_styled(path.resolve(), report)
            else:
                extract_content(path.resolve(), report)
        except Exception as exc:
            report.add_failure(path, str(exc))

    report.print_summary()
    report.exit_with_status()


if __name__ == "__main__":
    main()
