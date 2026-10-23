#!/usr/bin/env python3
"""Shared HTML processing utilities for document skills."""

import re
from pathlib import Path
from typing import Optional


def resolve_file_patterns(patterns: list[str]) -> list[Path]:
    """Resolve glob patterns and file paths to a concrete list of existing files."""
    resolved: list[Path] = []
    for pattern in patterns:
        path = Path(pattern)
        if path.exists():
            resolved.append(path.resolve())
        else:
            # Try glob expansion
            for match in Path(".").glob(pattern):
                if match.is_file():
                    resolved.append(match.resolve())
    return resolved


def to_kebab_case(text: str) -> str:
    """Convert text to kebab-case: lowercase, spaces to hyphens, remove special chars."""
    # Replace spaces and underscores with hyphens
    result = re.sub(r"[\s_]+", "-", text)
    # Remove non-alphanumeric except hyphens
    result = re.sub(r"[^a-z0-9\-]", "", result.lower())
    # Collapse multiple hyphens
    result = re.sub(r"-+", "-", result)
    # Strip leading/trailing hyphens
    return result.strip("-")


def ensure_directory(path: Path) -> Path:
    """Ensure directory exists, create if necessary."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def read_html_file(path: Path) -> str:
    """Read HTML file with UTF-8 encoding."""
    return path.read_text(encoding="utf-8")


def write_html_file(path: Path, content: str) -> None:
    """Write HTML file with UTF-8 encoding."""
    path.write_text(content, encoding="utf-8")
