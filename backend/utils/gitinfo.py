"""
Lightweight helpers to read Git repository metadata without external deps.

Functions provided:
- get_repo_slug(repo_dir): Returns "owner/repo" based on remote.origin.url
- parse_remote_url(url): Extracts (owner, repo) from common GitHub URL forms
- get_current_branch(repo_dir): Reads .git/HEAD to infer current branch

No network calls. Supports HTTPS and SSH URL forms and strips trailing .git.
"""
from __future__ import annotations

from configparser import ConfigParser
from pathlib import Path
from typing import Optional, Tuple
import re


_GITHUB_HOST_RE = re.compile(r"github\.com[:/]", re.IGNORECASE)


def parse_remote_url(url: str) -> Optional[Tuple[str, str]]:
    """
    Parse a Git remote URL and return (owner, repo) if it looks like GitHub.

    Supported forms:
    - https://github.com/owner/repo.git
    - https://github.com/owner/repo
    - git@github.com:owner/repo.git
    - ssh://git@github.com/owner/repo.git

    Returns None if it cannot confidently determine an owner/repo.
    """
    if not url:
        return None

    # Normalize and quickly check host
    if not _GITHUB_HOST_RE.search(url):
        # Not a GitHub URL; we won't try to infer foreign hosting patterns
        return None

    # Strip protocol and host prefix variations
    # Keep the path-ish portion after github.com[:/]
    path_part = _GITHUB_HOST_RE.split(url, maxsplit=1)[-1]

    # Remove any leading slashes/colons that may remain
    path_part = path_part.lstrip(":/")

    # Trim possible query/fragment (rare for remote URLs)
    path_part = path_part.split("?")[0].split("#")[0]

    # Now expect something like "owner/repo(.git)?/..."
    segments = [seg for seg in path_part.split("/") if seg]
    if len(segments) < 2:
        return None

    owner, repo = segments[0], segments[1]

    # Drop trailing .git
    if repo.endswith(".git"):
        repo = repo[:-4]

    # Basic sanity: owner and repo should be non-empty and alphanumeric-ish
    name_re = re.compile(r"^[A-Za-z0-9._-]+$")
    if not (name_re.match(owner) and name_re.match(repo)):
        return None

    return owner, repo


def get_repo_slug(repo_dir: str | Path = ".") -> Optional[str]:
    """
    Return "owner/repo" for the given repo directory by reading .git/config.
    If the directory is not a git repo or origin URL isn't set/parsable, None.
    """
    repo_path = Path(repo_dir)
    git_config = repo_path / ".git" / "config"
    if not git_config.is_file():
        return None

    parser = ConfigParser()
    try:
        parser.read(git_config, encoding="utf-8")
    except Exception:
        return None

    # Prefer the "origin" remote
    section = 'remote "origin"'
    if not parser.has_section(section):
        # Fall back to any remote section if origin doesn't exist
        remote_sections = [s for s in parser.sections() if s.startswith("remote ")]
        if not remote_sections:
            return None
        section = remote_sections[0]

    url = parser.get(section, "url", fallback=None)
    if not url:
        return None

    parsed = parse_remote_url(url)
    if not parsed:
        return None

    owner, repo = parsed
    return f"{owner}/{repo}"


def get_current_branch(repo_dir: str | Path = ".") -> Optional[str]:
    """
    Read .git/HEAD to determine the current branch name if available.
    Returns None when in detached HEAD or data isn't present.
    """
    head_file = Path(repo_dir) / ".git" / "HEAD"
    try:
        data = head_file.read_text(encoding="utf-8").strip()
    except Exception:
        return None

    # Common format: "ref: refs/heads/main"
    if data.startswith("ref:"):
        ref = data.split(None, 1)[-1]
        parts = ref.split("/")
        if parts:
            return parts[-1]
        return None

    # If it's a commit hash, we're in detached HEAD - return None
    return None
