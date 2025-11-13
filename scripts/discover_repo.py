"""CLI runner to execute the discovery engine against a repository path.

Usage (PowerShell):

  # Discover current directory and print normalized commands as JSON
  pwsh -NoLogo -NoProfile -Command "python scripts/discover_repo.py --path ."

  # Discover a specific repo (e.g., JAGI monorepo) and write results to file
        pwsh -NoLogo -NoProfile -Command \
            "python scripts/discover_repo.py --path \
             'C:\\Dev\\Projects\\JAGI\\v2\\v21\\JAGI_v21' --out results.json"

Notes:
- The runner only loads lightweight plugins (e.g., Taskfile) by default.
- Output includes both the normalized commands and raw artifacts when
    --show-raw is provided.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# Local imports
# Ensure project root is on sys.path when run as a script (not via pytest)
try:  # pragma: no cover - simple import guard for script usage
    from backend.discovery.engine import DiscoveryEngine
    from backend.discovery.plugins.taskfile import TaskfilePlugin
except ModuleNotFoundError:  # add project root and retry
    root = Path(__file__).resolve().parents[1]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    from backend.discovery.engine import DiscoveryEngine
    from backend.discovery.plugins.taskfile import TaskfilePlugin


def _build_engine() -> DiscoveryEngine:
    """Instantiate the discovery engine with the default plugin set.

    For now we enable only the Taskfile plugin. As new plugins are added,
    extend this list or make it configurable via CLI flags.
    """
    plugins = [TaskfilePlugin()]
    return DiscoveryEngine(plugins)


def _default_path(arg: str | None) -> Path:
    if arg:
        return Path(arg).resolve()
    return Path.cwd()


def _serialize_result(result: Any, include_raw: bool) -> dict[str, Any]:
    # Pydantic v2 BaseModel has model_dump(); our DiscoveryResult is a
    # dataclass with lists of BaseModel instances. Serialize explicitly for
    # stability.
    data: dict[str, Any] = {
        "commands": [c.model_dump() for c in result.commands],
    }
    if include_raw:
        data["raw_artifacts"] = [a.model_dump() for a in result.raw_artifacts]
    return data


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run mycli discovery against a repository path",
    )
    parser.add_argument(
        "--path",
        type=str,
        help="Path to repository root (defaults to current directory)",
    )
    parser.add_argument(
        "--out",
        type=str,
        help="Optional file to write JSON output to (stdout if omitted)",
    )
    parser.add_argument(
        "--show-raw",
        action="store_true",
        help="Include raw artifacts in the JSON output",
    )
    parser.add_argument(
        "--xray",
        action="store_true",
        help="Include lightweight RepoStats (X-ray) in the JSON output",
    )

    args = parser.parse_args(argv)
    repo_path = _default_path(args.path)

    if not repo_path.exists() or not repo_path.is_dir():
        print(f"[mycli] Invalid path: {repo_path}", file=sys.stderr)
        return 2

    engine = _build_engine()
    result = engine.run(repo_path)

    payload = _serialize_result(result, include_raw=args.show_raw)

    if args.xray:
        # Import lazily to avoid overhead when not requested
        from backend.xray import scan_repo  # type: ignore

        stats = scan_repo(repo_path)
        payload["xray"] = stats.model_dump()
    text = json.dumps(payload, indent=2)

    if args.out:
        out_path = Path(args.out)
        out_path.write_text(text, encoding="utf-8")
        print(f"[mycli] Wrote discovery results -> {out_path}")
    else:
        print(text)

    # Simple summary to stderr for convenience
    print(
        f"[mycli] Discovered {len(payload['commands'])} command(s)"
        + (
            f"; {len(payload.get('raw_artifacts', []))} raw"
            if args.show_raw
            else ""
        ),
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
