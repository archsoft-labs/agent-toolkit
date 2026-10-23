#!/usr/bin/env python3
"""File resolution utilities for handling user input patterns."""

import re
from pathlib import Path
from typing import Optional


def resolve_target_files(
    explicit_paths: Optional[list[str]] = None,
    glob_patterns: Optional[list[str]] = None,
    search_dirs: Optional[list[str]] = None,
    extension_filter: Optional[str] = None,
) -> tuple[list[Path], list[str]]:
    """
    Resolve user file specifications to concrete file paths.

    Returns:
        Tuple of (resolved_files, unresolved_patterns)
    """
    resolved: list[Path] = []
    unresolved: list[str] = []

    all_patterns = (explicit_paths or []) + (glob_patterns or [])

    for pattern in all_patterns:
        path = Path(pattern)

        # Direct file match
        if path.is_file():
            if _matches_filter(path, extension_filter):
                resolved.append(path.resolve())
            continue

        # Glob expansion
        matches = list(Path(".").glob(pattern))
        if matches:
            for match in matches:
                if match.is_file() and _matches_filter(match, extension_filter):
                    resolved.append(match.resolve())
        else:
            unresolved.append(pattern)

    # Search in additional directories if specified
    for search_dir in search_dirs or []:
        dir_path = Path(search_dir)
        if dir_path.is_dir():
            for ext in [extension_filter] if extension_filter else ["*"]:
                for match in dir_path.rglob(f"*.{ext}" if ext != "*" else "*"):
                    if match.is_file():
                        resolved.append(match.resolve())

    # Deduplicate while preserving order
    seen = set()
    unique_resolved = []
    for path in resolved:
        if path not in seen:
            seen.add(path)
            unique_resolved.append(path)

    return unique_resolved, unresolved


def _matches_filter(path: Path, extension_filter: Optional[str]) -> bool:
    """Check if file matches the extension filter."""
    if not extension_filter:
        return True
    return path.suffix.lower() == f".{extension_filter.lstrip('.')}"


def suggest_files(pattern: str, max_suggestions: int = 5) -> list[Path]:
    """Suggest similar files when a pattern doesn't match."""
    suggestions = []
    pattern_lower = pattern.lower()

    for ext in ["html", "md", "htm"]:
        for match in Path(".").rglob(f"*.{ext}"):
            if pattern_lower in match.name.lower():
                suggestions.append(match)
                if len(suggestions) >= max_suggestions:
                    return suggestions

    return suggestions
