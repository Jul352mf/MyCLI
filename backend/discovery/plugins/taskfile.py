"""Taskfile.yml discovery plugin.

Parses Taskfile.yml (common task runner format) to extract tasks as commands.
This is intentionally lightweight for early scaffolding: parameter inference is
minimal. Later iterations will examine command strings for flag patterns.
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, List
import os
import yaml

from ...models import RawArtifact, Origin
from ..base import DiscoveryPlugin  # noqa: F401


class TaskfilePlugin:
    name = "taskfile"
    origins = [Origin.TASKFILE.value]

    def __init__(self, filename: str = "Taskfile.yml"):
        self.filename = filename

    def _load(self, file_path: Path):  # internal helper
        if not file_path.exists():
            return None
        try:
            with file_path.open("r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception:  # pragma: no cover - graceful failure
            return None

    def scan(self, project_root: Path) -> Iterable[RawArtifact]:
        """Scan root and subdirectories for Taskfile.yml.

        Skips heavy/vendor directories to keep discovery fast.
        """
        artifacts: List[RawArtifact] = []
        skip_dirs = {"node_modules", ".git", ".venv", "dist", "build"}
        for root, dirs, files in os.walk(project_root):
            # prune skip dirs in-place
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            if self.filename not in files:
                continue
            file_path = Path(root) / self.filename
            data = self._load(file_path)
            if not data:
                continue
            tasks = data.get("tasks", {})
            # compute cwd and tag if not at project root
            rel = Path(root).relative_to(project_root)
            rel_str = str(rel).replace("\\", "/") if str(rel) != "." else ""
            scope_tag = f"scope:{rel_str}" if rel_str else None
            for name, spec in tasks.items():
                if not isinstance(spec, dict):
                    continue
                desc = spec.get("desc") or spec.get("description")
                cmd = spec.get("cmd") or spec.get("run")
                meta = {
                    "task_name": name,
                    "description": desc,
                    "origin": Origin.TASKFILE.value,
                    "raw_cmd": cmd,
                    "cwd": str(root),
                }
                if scope_tag:
                    meta["tags"] = [scope_tag]
                artifacts.append(
                    RawArtifact(
                        type="task",
                        path=str(file_path),
                        content_snippet=(
                            cmd if isinstance(cmd, str) else None
                        ),
                        meta=meta,
                        confidence=0.6,
                    )
                )
        return artifacts

    # Provide pass-through implementations to satisfy engine expectations
    def classify(self, artifact: RawArtifact) -> RawArtifact | None:
        return artifact

    def extract(self, artifact: RawArtifact) -> RawArtifact | None:
        return artifact

    def normalize(self, artifacts: list[RawArtifact]) -> list[RawArtifact]:
        return artifacts
