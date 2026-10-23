#!/usr/bin/env python3
"""Translate HTML content to a target language while preserving structure."""

import re
import sys
from pathlib import Path

try:
    from bs4 import BeautifulSoup, NavigableString
except ImportError:
    print("ERROR: 'beautifulsoup4' not installed. Run: pip install beautifulsoup4")
    sys.exit(1)

# Add shared utilities to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "_shared"))
from html_processor import to_kebab_case
from report_generator import SkillReport


# Language name to locale mapping
LANGUAGE_MAP = {
    "portuguese": "pt-br", "português": "pt-br", "portugues": "pt-br",
    "english": "en", "inglês": "en", "ingles": "en",
    "french": "fr", "français": "fr", "frances": "fr",
    "spanish": "es", "espanhol": "es", "espanol": "es",
    "german": "de", "alemão": "de", "alemao": "de",
    "japanese": "ja", "japonês": "ja", "japones": "ja",
    "chinese": "zh-cn", "chinês": "zh-cn", "chines": "zh-cn",
    "korean": "ko", "coreano": "ko",
    "italian": "it", "italiano": "it",
    "russian": "ru", "russo": "ru",
    "arabic": "ar", "árabe": "ar", "arabe": "ar",
    "hindi": "hi",
    "dutch": "nl", "holandês": "nl", "holandes": "nl",
    "swedish": "sv", "sueco": "sv",
    "polish": "pl", "polonês": "pl", "polones": "pl",
    "turkish": "tr", "turco": "tr",
    "vietnamese": "vi", "vietnamita": "vi",
    "thai": "th", "tailandês": "th", "tailandes": "th",
    "indonesian": "id", "indonésio": "id", "indonesio": "id",
}


def normalize_language(lang: str) -> str:
    """Normalize language input to lowercase locale code."""
    lang_lower = lang.lower().strip()

    # Direct locale code
    if re.match(r"^[a-z]{2}(-[a-z]{2,4})?$", lang_lower):
        return lang_lower

    # Map from name
    if lang_lower in LANGUAGE_MAP:
        return LANGUAGE_MAP[lang_lower]

    # Try partial match
    for name, code in LANGUAGE_MAP.items():
        if lang_lower in name or name in lang_lower:
            return code

    return lang_lower


def translate_text(text: str, target_lang: str) -> str:
    """
    Translate text to target language.

    NOTE: This is a placeholder implementation. In production, integrate with:
    - Claude API (recommended for quality)
    - Google Translate API
    - DeepL API
    - Local LLM via Ollama

    For now, returns text unchanged with a marker. Replace with actual API call.
    """
    # TODO: Integrate actual translation API
    # Example with Claude API:
    # response = anthropic.messages.create(
    #     model="claude-3-5-sonnet-20241022",
    #     messages=[{"role": "user", "content": f"Translate to {target_lang}: {text}"}]
    # )
    # return response.content[0].text

    return text  # Placeholder: return unchanged


def translate_html(html_path: Path, target_lang: str, report: SkillReport) -> None:
    """Translate HTML file to target language."""
    html = html_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")

    # Find all translatable text nodes
    text_nodes = []
    for element in soup.find_all(string=True):
        if isinstance(element, NavigableString):
            parent = element.parent
            if parent and parent.name not in ("script", "style", "head"):
                text = element.strip()
                if text and len(text) > 1:  # Skip whitespace-only and single chars
                    text_nodes.append((element, text))

    # Translate each text node
    translated_count = 0
    for element, original_text in text_nodes:
        translated = translate_text(original_text, target_lang)
        if translated != original_text:
            element.replace_with(translated)
            translated_count += 1

    # Update html lang attribute
    html_tag = soup.find("html")
    if html_tag:
        html_tag["lang"] = target_lang

    # Write output
    output_path = html_path.parent / f"{html_path.stem}-{target_lang}.html"
    output_path.write_text(str(soup), encoding="utf-8")

    report.add_success(
        html_path,
        output_path,
        target_language=target_lang,
        text_nodes_translated=translated_count,
        total_text_nodes=len(text_nodes),
    )


def main() -> None:
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help"):
        print("Usage: translate.py <file1.html> [file2.html ...] --lang <target>")
        print("\nTranslates HTML files to the target language.")
        print("\nExamples:")
        print("  translate.py article.html --lang pt-br")
        print("  translate.py docs/*.html --lang french")
        sys.exit(0)

    # Parse arguments
    files: list[Path] = []
    target_lang: str | None = None

    i = 0
    while i < len(args):
        if args[i] == "--lang" and i + 1 < len(args):
            target_lang = normalize_language(args[i + 1])
            i += 2
        else:
            files.append(Path(args[i]))
            i += 1

    if not files:
        print("ERROR: No HTML files specified.", file=sys.stderr)
        sys.exit(1)

    if not target_lang:
        print("ERROR: Target language not specified. Use --lang <language>", file=sys.stderr)
        sys.exit(1)

    report = SkillReport(skill_name="html-translate")

    for path in files:
        if not path.exists():
            report.add_failure(path, "File not found")
            continue
        if path.suffix.lower() not in (".html", ".htm"):
            report.add_failure(path, f"Not an HTML file: {path.suffix}")
            continue

        try:
            translate_html(path.resolve(), target_lang, report)
        except Exception as exc:
            report.add_failure(path, str(exc))

    report.print_summary()
    report.exit_with_status()


if __name__ == "__main__":
    main()
