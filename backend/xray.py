"""Repository X-ray scanner producing RepoStats.

This is a lightweight, fast pass intended for local dashboards and heuristics.
It walks the filesystem (excluding common vendor/build directories), computes
basic metrics, and returns a RepoStats model with a computed health index.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Iterable, Tuple

from .models import RepoStats


EXCLUDE_DIRS = {
    ".git",
    "node_modules",
    ".venv",
    "venv",
    ".pytest_cache",
    "dist",
    "build",
    ".next",
    "__pycache__",
}


def _iter_files(root: Path) -> Iterable[Path]:
    for dirpath, dirnames, filenames in os.walk(root):
        # prune excluded directories in-place for efficiency
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        for fname in filenames:
            yield Path(dirpath) / fname


def _safe_read_lines(p: Path, limit_bytes: int = 2_000_000) -> int:
    """Return approximate line count; bail on very large files for speed."""
    try:
        if p.stat().st_size > limit_bytes:
            return 0
        with p.open("rb") as f:
            return sum(1 for _ in f)
    except Exception:
        return 0


def scan_repo(root: Path) -> RepoStats:
    root = root.resolve()
    total_files = 0
    total_lines = 0
    total_size_bytes = 0
    largest: list[Tuple[str, int]] = []  # (path, size)

    # naive language breakdown based on extension
    language_breakdown: Dict[str, int] = {}
    file_length_histogram: Dict[str, int] = {"0-100": 0, "101-500": 0, "501+": 0}

    for p in _iter_files(root):
        try:
            st = p.stat()
        except OSError:
            continue

        total_files += 1
        total_size_bytes += st.st_size

        # track largest files (top 10)
        largest.append((str(p), st.st_size))
        if len(largest) > 10:
            largest.sort(key=lambda t: t[1], reverse=True)
            largest = largest[:10]

        # line counts (approx)
        lc = _safe_read_lines(p)
        total_lines += lc
        if lc <= 100:
            file_length_histogram["0-100"] += 1
        elif lc <= 500:
            file_length_histogram["101-500"] += 1
        else:
            file_length_histogram["501+"] += 1

        # language heuristic
        ext = p.suffix.lower()
        lang = {
            ".py": "python",
            ".ts": "typescript",
            ".tsx": "tsx",
            ".js": "javascript",
            ".jsx": "jsx",
            ".json": "json",
            ".yml": "yaml",
            ".yaml": "yaml",
            ".md": "markdown",
        }.get(ext, "other")
        language_breakdown[lang] = language_breakdown.get(lang, 0) + lc

    # Compute health index with coarse inputs
    largest_bytes = largest[0][1] if largest else 0
    health = RepoStats.compute_health_index(
        total_files=total_files,
        comment_density_pct=None,  # not computed in the fast path
        largest_file_bytes=largest_bytes,
    )

    return RepoStats(
        total_files=total_files,
        total_lines=total_lines,
        total_size_bytes=total_size_bytes,
        language_breakdown=language_breakdown,
        largest_files=[{"path": p, "size": s} for p, s in sorted(largest, key=lambda t: t[1], reverse=True)],
        comment_density_pct=None,
        directory_tree={},  # reserved for future
        file_length_histogram=file_length_histogram,
        health_index=health,
    )
