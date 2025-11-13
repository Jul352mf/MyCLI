"""Environment loading and merging utilities.

Loads a simple .env file (KEY=VALUE pairs, # comments) from a project
directory and merges into the current process environment with the
specified precedence rules:

Priority (highest first):
1. Existing OS environment variables (shell user launched mycli from)
2. Project .env file values (only fill if not already defined)

This ensures user/session overrides are respected while still providing
project defaults.
"""
from __future__ import annotations

from pathlib import Path
import os


def parse_env_file(path: Path) -> dict[str, str]:
    """Parse a minimal .env file into a dict.

    Supports lines of form KEY=VALUE. Leading/trailing whitespace around
    keys/values is trimmed. Lines starting with '#' or empty lines are
    ignored. Does not support export statements or variable expansion.
    """
    data: dict[str, str] = {}
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return data
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.strip()
        v = v.strip()
        if k:
            data[k] = v
    return data


def merge_project_env(dev_dir: str) -> dict[str, str]:
    """Load .env under dev_dir and merge into os.environ.

    Returns a dict of keys added (those not previously present).
    """
    env_path = Path(dev_dir) / ".env"
    if not env_path.exists():
        return {}
    parsed = parse_env_file(env_path)
    added: dict[str, str] = {}
    for key, value in parsed.items():
        if key not in os.environ:
            os.environ[key] = value
            added[key] = value
    return added
