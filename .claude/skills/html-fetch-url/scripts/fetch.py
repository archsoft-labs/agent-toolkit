#!/usr/bin/env python3
"""Fetch HTML pages from URLs and save them locally with localized images.

Strategy: curl fast-path for public pages; escalate to browser-harness
(real Chrome via CDP) when curl returns a JS shell, an HTTP error, or a
known bot-challenge marker.
"""

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("ERROR: 'beautifulsoup4' not installed. Run: pip install beautifulsoup4")
    sys.exit(1)

# Add shared utilities to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "_shared"))
from html_processor import to_kebab_case, ensure_directory, write_html_file
from report_generator import SkillReport


USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

# Markers that indicate the page is a JS shell or a bot challenge
JS_SHELL_MARKERS = (
    "Just a moment",                # Cloudflare
    "cf-challenge",
    "cf-browser-verification",
    "Enable JavaScript",
    "Please enable JS",
    "Please turn JavaScript on",
    "Checking your browser",
    "DDoS protection",
    "__NEXT_DATA__",                # Next.js hydration shell
    "ng-app",                       # Angular root
    "data-reactroot",               # React root
    "__NUXT__",                     # Nuxt
)

# Markers of meaningful, already-rendered content. If any is present, the page
# is NOT a shell, regardless of size.
CONTENT_MARKERS = (
    "<article",
    "<main",
    "<p>",                          # a paragraph of text
    "<h1",
    "<h2",
    "<table",
    "<pre",
)

# Minimum plausible body size for a real page (bytes). Pages below this AND
# without any CONTENT_MARKERS are treated as shells.
MIN_BODY_BYTES = 1024

# Content-Type → extension fallback map
CONTENT_TYPE_TO_EXT = {
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
    "image/svg+xml": ".svg",
    "image/avif": ".avif",
    "image/x-icon": ".ico",
    "image/vnd.microsoft.icon": ".ico",
}


class FetchError(Exception):
    """Raised when a fetch step fails irrecoverably."""


def url_to_slug(url: str) -> str:
    """Derive a stable kebab-case slug from a URL.

    Uses hostname + last two path segments. Appends a short query hash when
    a query string is present so distinct URLs never collide.
    """
    parsed = urlparse(url)
    host = parsed.netloc.split(":")[0]  # strip port
    # Replace dots with dashes so example.com → example-com
    host = host.replace(".", "-")
    path_parts = [p for p in parsed.path.split("/") if p]
    tail = path_parts[-2:] if len(path_parts) >= 2 else path_parts
    base = "-".join([host] + tail) if tail else host
    slug = to_kebab_case(base) or "index"

    if parsed.query:
        digest = hashlib.sha1(parsed.query.encode("utf-8")).hexdigest()[:6]
        slug = f"{slug}-{digest}"
    return slug


def curl_get(url: str, timeout: int) -> str:
    """Fetch URL via system curl. Raises FetchError on transport or HTTP failure.

    Reads raw bytes and decodes as UTF-8 with replacement so non-text responses
    (binary images, etc.) surface a clear "not HTML" error rather than crashing
    the decoder.
    """
    if not shutil.which("curl"):
        raise FetchError(
            "curl not found on PATH. Install curl or use --via browser-harness."
        )
    cmd = [
        "curl", "-sSL",
        "--max-time", str(timeout),
        "-A", USER_AGENT,
        "-w", "\n__HTTP_STATUS__:%{http_code}",
        url,
    ]
    try:
        result = subprocess.run(
            cmd, capture_output=True, timeout=timeout + 5, check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise FetchError(f"curl timed out after {timeout}s for {url}") from exc

    if result.returncode != 0:
        stderr_text = result.stderr.decode("utf-8", errors="replace").strip()
        raise FetchError(
            f"curl exited {result.returncode}: {stderr_text or 'no stderr'}"
        )

    # Decode bytes → text (UTF-8 with replacement). Binary content yields
    # garbage characters, which `looks_like_js_shell` will then classify.
    stdout_text = result.stdout.decode("utf-8", errors="replace")

    # Split status marker from body
    body, _, status_line = stdout_text.rpartition("__HTTP_STATUS__:")
    status = status_line.strip() if status_line else ""
    if status and status != "200":
        # 3xx are usually resolved by -L; any other non-200 is suspicious
        if not status.startswith("2"):
            raise FetchError(f"HTTP {status} for {url}")

    # Refuse obvious binary payloads early
    stripped = body.lstrip().lower()
    if body and not stripped.startswith(("<!doctype", "<html", "<?xml")) and not stripped.startswith("<"):
        raise FetchError(
            f"URL does not look like HTML (first 40 bytes: {body[:40]!r}). "
            "This skill fetches HTML pages only."
        )

    return body


def looks_like_js_shell(html: str) -> bool:
    """Heuristic: does this HTML look like a JS-rendered shell with no content?

    Order matters:
      1. Explicit bot-challenge markers always escalate.
      2. Pages with visible content markers never escalate (small pages like
         example.com are real content, not shells).
      3. SPA framework markers escalate only when the page is also small —
         a large page with `data-reactroot` may be a fully SSR'd React app.
      4. Very small pages with no content markers escalate.
    """
    if not html:
        return True

    lowered = html.lower()

    # 1. Explicit challenge markers → always shell
    for marker in ("just a moment", "cf-challenge", "cf-browser-verification",
                   "checking your browser", "ddos protection",
                   "please enable js", "please turn javascript on"):
        if marker in lowered:
            return True

    # 2. Real content markers → not a shell
    for marker in CONTENT_MARKERS:
        if marker in lowered:
            return False

    # 3. SPA framework markers + small page → likely shell
    spa_markers = ("__next_data__", "ng-app", "data-reactroot", "__nuxt__",
                   "enable javascript")
    has_spa_marker = any(m in lowered for m in spa_markers)
    if has_spa_marker and len(html) < MIN_BODY_BYTES * 4:
        return True

    # 4. Tiny page with no content markers → suspicious
    if len(html) < MIN_BODY_BYTES:
        return True

    return False


def browser_harness_get(url: str, timeout: int) -> tuple[str, list[str]]:
    """Render URL via browser-harness CLI; return (html, image_urls)."""
    if not shutil.which("browser-harness"):
        raise FetchError(
            "browser-harness CLI not found on PATH. "
            "Install it (see https://github.com/browser-use/browser-harness) "
            "or use --via curl."
        )

    snippet = f"""
import json
new_tab({json.dumps(url)})
wait_for_load()
html = js("document.documentElement.outerHTML")
imgs = js("Array.from(document.images).map(i => i.src)")
print("__BH_JSON_START__")
print(json.dumps({{"html": html, "images": imgs}}))
print("__BH_JSON_END__")
"""

    try:
        result = subprocess.run(
            ["browser-harness"],
            input=snippet,
            capture_output=True,
            text=True,
            timeout=timeout + 30,  # extra headroom for browser launch
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise FetchError(
            f"browser-harness timed out after {timeout + 30}s for {url}"
        ) from exc

    if result.returncode != 0:
        raise FetchError(
            f"browser-harness exited {result.returncode}: "
            f"{result.stderr.strip() or 'no stderr'}. "
            f"Run 'browser-harness --doctor' to diagnose."
        )

    # Extract JSON payload between markers
    match = re.search(
        r"__BH_JSON_START__\s*(\{.*?\})\s*__BH_JSON_END__",
        result.stdout,
        re.DOTALL,
    )
    if not match:
        raise FetchError(
            "browser-harness did not return a JSON payload. "
            f"Raw stdout (first 500 chars): {result.stdout[:500]}"
        )

    try:
        payload = json.loads(match.group(1))
    except json.JSONDecodeError as exc:
        raise FetchError(f"Failed to parse browser-harness JSON: {exc}") from exc

    html = payload.get("html", "")
    images = payload.get("images", []) or []
    if not html:
        raise FetchError("browser-harness returned empty HTML")
    return html, images


def fetch_html(url: str, via: str, timeout: int) -> tuple[str, str, list[str]]:
    """Return (html, method_used, image_urls_from_browser).

    `image_urls_from_browser` is non-empty only when browser-harness was used;
    it captures images added by JS that may not appear in the raw HTML.

    Escalation rules in `auto` mode:
      - HTTP 4xx/5xx → escalate (may be a bot wall that a real browser passes)
      - Network/timeout → escalate (browser may retry with real TLS/cookies)
      - JS-shell heuristic → escalate (that's the whole point)
      - "Not HTML" / curl missing → DO NOT escalate (deterministic, won't
        be solved by a browser)
    """
    if via in ("auto", "curl"):
        try:
            html = curl_get(url, timeout)
            if via == "curl":
                return html, "curl", []
            if not looks_like_js_shell(html):
                return html, "curl", []
            # JS shell detected → fall through to browser-harness
        except FetchError as exc:
            if via == "curl":
                raise
            # In auto mode, decide based on the error kind
            msg = str(exc).lower()
            non_escalatable = (
                "does not look like html",
                "curl not found",
            )
            if any(marker in msg for marker in non_escalatable):
                raise
            # HTTP errors, timeouts, DNS, TLS → try browser-harness

    html, images = browser_harness_get(url, timeout)
    return html, "browser-harness", images


def extension_from_response(url_path: str, content_type: Optional[str]) -> str:
    """Pick an image extension from URL path, falling back to Content-Type."""
    suffix = Path(url_path).suffix.lower()
    if suffix in {".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg", ".avif", ".ico"}:
        return ".jpg" if suffix == ".jpeg" else suffix
    if content_type:
        ct = content_type.split(";")[0].strip().lower()
        if ct in CONTENT_TYPE_TO_EXT:
            return CONTENT_TYPE_TO_EXT[ct]
    return ".bin"


def download_image(url: str, dest: Path, timeout: int) -> Optional[str]:
    """Download one image. Returns the final extension on success, None on failure."""
    req = Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(req, timeout=timeout) as resp:
            content_type = resp.headers.get("Content-Type")
            data = resp.read()
    except (HTTPError, URLError, TimeoutError, OSError):
        return None

    ext = extension_from_response(urlparse(url).path, content_type)
    final_path = dest.with_suffix(ext)
    final_path.write_bytes(data)
    return ext


def localize_images(
    html: str,
    page_url: str,
    out_dir: Path,
    slug: str,
    timeout: int,
    pre_fetched_urls: Optional[list[str]] = None,
) -> tuple[str, int, list[str]]:
    """Download <img> sources into images/ and rewrite src attributes.

    Returns (updated_html, images_downloaded, failed_urls).
    """
    soup = BeautifulSoup(html, "html.parser")
    img_tags = soup.find_all("img")
    if not img_tags and not pre_fetched_urls:
        return html, 0, []

    images_dir = ensure_directory(out_dir / "images")

    # Collect candidate URLs from <img src> plus any JS-added images
    candidates: list[str] = []
    for img in img_tags:
        src = (img.get("src") or "").strip()
        if not src or src.startswith(("data:", "blob:", "#")):
            continue
        absolute = urljoin(page_url, src)
        candidates.append(absolute)
    for u in pre_fetched_urls or []:
        if u and not u.startswith(("data:", "blob:")):
            candidates.append(u)

    # Dedupe preserving order
    seen: set[str] = set()
    unique_urls: list[str] = []
    for u in candidates:
        if u not in seen:
            seen.add(u)
            unique_urls.append(u)

    if not unique_urls:
        return str(soup), 0, []

    url_to_local: dict[str, str] = {}
    failed: list[str] = []
    counter = 1

    for src_url in unique_urls:
        base_name = f"{slug}-image-{counter:03d}"
        dest = images_dir / base_name
        ext = download_image(src_url, dest, timeout)
        if ext is None:
            failed.append(src_url)
            continue
        url_to_local[src_url] = f"images/{base_name}{ext}"
        counter += 1

    # Rewrite <img src> for the ones we successfully localized
    for img in img_tags:
        src = (img.get("src") or "").strip()
        if not src:
            continue
        absolute = urljoin(page_url, src)
        if absolute in url_to_local:
            img["src"] = url_to_local[absolute]

    return str(soup), len(url_to_local), failed


def fetch_url(
    url: str,
    output_root: Path,
    via: str,
    no_images: bool,
    timeout: int,
    report: SkillReport,
) -> None:
    """Fetch one URL end-to-end and record the result."""
    slug = url_to_slug(url)
    out_dir = ensure_directory(output_root / slug)
    html_path = out_dir / f"{slug}.html"

    try:
        html, method, browser_images = fetch_html(url, via, timeout)
    except FetchError as exc:
        # Use a symbolic Path for the source so the report stays consistent
        report.add_failure(Path(urlparse(url).netloc or url), str(exc))
        return

    n_images = 0
    failed_images: list[str] = []
    if not no_images:
        try:
            html, n_images, failed_images = localize_images(
                html, url, out_dir, slug, timeout,
                pre_fetched_urls=browser_images,
            )
        except Exception as exc:
            # Image failure is non-fatal: keep the HTML, report as a detail
            failed_images = failed_images + [f"<localize_images error: {exc}>"]

    write_html_file(html_path, html)
    report.add_success(
        html_path,
        html_path,
        url=url,
        method=method,
        images_localized=n_images,
        images_failed=len(failed_images),
    )
    if failed_images:
        # Surface failures without failing the whole fetch
        for f in failed_images:
            print(f"  [warn] image not localized: {f}", file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Fetch HTML pages from URLs and save them locally with localized "
            "images. Defaults to curl; escalates to browser-harness when the "
            "page looks like a JS shell or a bot challenge."
        )
    )
    parser.add_argument("urls", nargs="+", help="One or more http(s) URLs")
    parser.add_argument(
        "--output-dir", "-o",
        type=Path,
        default=Path("."),
        help="Parent directory for the <slug>/ output folder (default: cwd)",
    )
    parser.add_argument(
        "--via",
        choices=("auto", "curl", "browser-harness"),
        default="auto",
        help="Fetch strategy (default: auto = curl first, escalate on JS shell)",
    )
    parser.add_argument(
        "--no-images",
        action="store_true",
        help="Skip image download; <img src> keeps remote URLs",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="HTTP/browser timeout in seconds (default: 30)",
    )

    args = parser.parse_args()

    report = SkillReport(skill_name="html-fetch-url")
    output_root = args.output_dir.resolve()
    ensure_directory(output_root)

    for url in args.urls:
        if not url.lower().startswith(("http://", "https://")):
            report.add_failure(Path(url), "Not an http(s) URL")
            continue
        fetch_url(url, output_root, args.via, args.no_images, args.timeout, report)

    report.print_summary()
    report.exit_with_status()


if __name__ == "__main__":
    main()
