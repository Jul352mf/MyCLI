"""Interactively select and execute discovered commands.

Currently supports Taskfile-derived commands by running `task <name>` in the
repository root. Intended as a simple bridge until the TUI dialog wiring is in
place.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, List


def _load_commands(repo_path: Path) -> List[dict[str, Any]]:
    # Expect the caller to have run discover_repo first; if not, run it now
    results_path = Path("discovery_results.json")
    if not results_path.exists():
        # Try to generate quickly
        from scripts.discover_repo import main as discover_main  # type: ignore

        print(
            "[mycli] No discovery_results.json found. Running discovery...",
            file=sys.stderr,
        )
        discover_main(["--path", str(repo_path), "--out", str(results_path)])

    data = json.loads(results_path.read_text(encoding="utf-8"))
    return data.get("commands", [])


def _select(commands: List[dict[str, Any]]) -> dict[str, Any] | None:
    if not commands:
        print("[mycli] No commands available.", file=sys.stderr)
        return None
    for idx, c in enumerate(commands, start=1):
        name = c.get("name", "<unnamed>")
        origin = c.get("origin", "?")
        desc = c.get("description") or ""
        print(f"{idx:3d}. [{origin}] {name} - {desc}")
    while True:
        choice = input(
            "Select a command number (or blank to cancel): "
        ).strip()
        if not choice:
            return None
        if choice.isdigit():
            i = int(choice)
            if 1 <= i <= len(commands):
                return commands[i - 1]
        print("Invalid selection. Try again.")


def _run_taskfile(repo_path: Path, task_name: str) -> int:
    # Execute `task <name>` in repo_path
    print(f"[mycli] Running: task {task_name} (cwd={repo_path})")
    try:
        # Use PowerShell on Windows; fall back otherwise
        if os.name == "nt":
            cmd = [
                "pwsh",
                "-NoLogo",
                "-NoProfile",
                "-Command",
                f"cd '{repo_path}'; task {task_name}",
            ]
        else:
            cmd = ["bash", "-lc", f"cd '{repo_path}'; task {task_name}"]
        return subprocess.call(cmd)
    except FileNotFoundError:
        print(
            "[mycli] 'task' not found. Please install go-task.",
            file=sys.stderr,
        )
        return 127


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Select and execute discovered commands"
    )
    parser.add_argument(
        "--path", type=str, required=True, help="Repository root path"
    )
    args = parser.parse_args(argv)

    repo = Path(args.path).resolve()
    cmds = _load_commands(repo)
    chosen = _select(cmds)
    if not chosen:
        print("[mycli] Cancelled.")
        return 0

    invocation = chosen.get("invocation", {})
    adapter = invocation.get("adapter")
    if adapter == "taskfile":
        task_name = invocation.get("task_name")
        if not task_name:
            print("[mycli] Missing task_name in invocation", file=sys.stderr)
            return 1
        return _run_taskfile(repo, task_name)

    print(f"[mycli] Unsupported adapter: {adapter}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
