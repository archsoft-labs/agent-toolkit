#!/usr/bin/env python3
"""Standardized reporting for skill execution results."""

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class FileResult:
    """Result of processing a single file."""
    source: Path
    output: Optional[Path] = None
    success: bool = True
    error: Optional[str] = None
    details: dict = field(default_factory=dict)


@dataclass
class SkillReport:
    """Aggregated report for a skill execution."""
    skill_name: str
    results: list[FileResult] = field(default_factory=list)

    @property
    def succeeded(self) -> list[FileResult]:
        return [r for r in self.results if r.success]

    @property
    def failed(self) -> list[FileResult]:
        return [r for r in self.results if not r.success]

    def add_success(self, source: Path, output: Path, **details) -> None:
        self.results.append(FileResult(source=source, output=output, success=True, details=details))

    def add_failure(self, source: Path, error: str) -> None:
        self.results.append(FileResult(source=source, success=False, error=error))

    def print_summary(self) -> None:
        """Print human-readable summary to stdout."""
        print(f"\n{'='*60}")
        print(f"Skill: {self.skill_name}")
        print(f"{'='*60}")

        for result in self.results:
            if result.success:
                print(f"  [OK] {result.source}")
                if result.output:
                    print(f"       -> {result.output}")
                for key, value in result.details.items():
                    print(f"       {key}: {value}")
            else:
                print(f"  [ERR] {result.source}: {result.error}", file=sys.stderr)

        print(f"\n{'-'*60}")
        print(f"Total: {len(self.results)} | "
              f"Succeeded: {len(self.succeeded)} | "
              f"Failed: {len(self.failed)}")
        print(f"{'='*60}\n")

    def exit_with_status(self) -> None:
        """Exit with appropriate status code."""
        sys.exit(1 if self.failed else 0)
