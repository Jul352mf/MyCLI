"""NPM/PNPM package.json scripts discovery plugin.

Scans a project's package.json and emits RawArtifact entries for each script.
Determines the preferred package manager by checking for `packageManager`
field or lockfiles (pnpm-lock.yaml, package-lock.json, yarn.lock). For now we
only support `npm` and `pnpm` adapters.
"""
from __future__ import annotations

import json
from pathlib import Path
import os
from typing import Iterable, List

from ...models import RawArtifact, Origin


class NpmScriptsPlugin:
    name = "npm_scripts"
    origins = [Origin.PACKAGE_SCRIPT.value]

    def __init__(self, filename: str = "package.json"):
        self.filename = filename

    def _detect_pm(self, project_root: Path, pkg: dict) -> str:
        # Prefer explicit packageManager field if present
        pm_field = pkg.get("packageManager")
        if isinstance(pm_field, str):
            if pm_field.startswith("pnpm"):
                return "pnpm"
            if pm_field.startswith("npm"):
                return "npm"
        # Fallback to lockfiles
        if (project_root / "pnpm-lock.yaml").exists():
            return "pnpm"
        if (project_root / "package-lock.json").exists():
            return "npm"
        # Default to npm
        return "npm"

    def _load(self, file_path: Path):  # internal helper
        if not file_path.exists():
            return None
        try:
            text = file_path.read_text(encoding="utf-8")
            return json.loads(text)
        except Exception:
            return None

    def scan(self, project_root: Path) -> Iterable[RawArtifact]:
        """Scan root and subdirectories for package.json scripts.

        Skips heavy/vendor directories to keep discovery fast.
        """
        artifacts: List[RawArtifact] = []
        skip_dirs = {"node_modules", ".git", ".venv", "dist", "build"}
        for root, dirs, files in os.walk(project_root):
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            if self.filename not in files:
                continue
            file_path = Path(root) / self.filename
            pkg = self._load(file_path)
            if not pkg:
                continue
            scripts = pkg.get("scripts") or {}
            if not isinstance(scripts, dict):
                continue
            pm = self._detect_pm(Path(root), pkg)
            rel = Path(root).relative_to(project_root)
            rel_str = (
                str(rel).replace("\\", "/") if str(rel) != "." else ""
            )
            scope_tag = f"scope:{rel_str}" if rel_str else None
            for name, cmd in scripts.items():
                if not isinstance(name, str):
                    continue
                meta = {
                    "script_name": name,
                    "description": f"package script: {name}",
                    "origin": Origin.PACKAGE_SCRIPT.value,
                    "raw_cmd": cmd if isinstance(cmd, str) else None,
                    "package_manager": pm,
                    "cwd": str(root),
                }
                if scope_tag:
                    meta["tags"] = [scope_tag]
                artifacts.append(
                    RawArtifact(
                        type="package_script",
                        path=str(file_path),
                        content_snippet=(
                            cmd if isinstance(cmd, str) else None
                        ),
                        meta=meta,
                        confidence=0.6,
                    )
                )
        return artifacts

    # Pass-throughs for pipeline compatibility
    def classify(self, artifact: RawArtifact) -> RawArtifact | None:
        return artifact

    def extract(self, artifact: RawArtifact) -> RawArtifact | None:
        return artifact

    def normalize(self, artifacts: list[RawArtifact]) -> list[RawArtifact]:
        return artifacts
