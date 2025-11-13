"""Project registry operations (add existing projects, etc.)."""
from __future__ import annotations

import os
from glob import glob
from typing import Dict, Any
import yaml

from .models import ProjectConfig

# Keep in sync with backend.loader.PROJECTS_ROOT
PROJECTS_ROOT = r"C:\Dev\Projects"


def _guess_workspace_path(dev_dir: str) -> str:
    """Try to find a .code-workspace in the target directory.

    If none exists, return the dev_dir path so opening the folder works.
    """
    try:
        matches = glob(os.path.join(dev_dir, "*.code-workspace"))
        if matches:
            return matches[0]
    except Exception:
        pass
    return dev_dir


def add_project_from_path(
    path: str, name: str | None = None
) -> Dict[str, Any]:
    """Register an existing project directory into MyCLI's registry.

    This creates a lightweight wrapper directory under PROJECTS_ROOT with a
    project.yaml pointing dev_dir to the provided path. It won't copy files.

    Returns a dict with {success: bool, message|error, key}.
    """
    path = os.path.abspath(path)
    if not os.path.isdir(path):
        return {"success": False, "error": f"Directory not found: {path}"}

    wrapper_name = (
        name or os.path.basename(os.path.normpath(path)) or "project"
    )
    wrapper_dir = os.path.join(PROJECTS_ROOT, wrapper_name)

    try:
        os.makedirs(wrapper_dir, exist_ok=True)

        config = ProjectConfig(
            name=wrapper_name,
            workspace=_guess_workspace_path(path),
            dev_dir=path,
            task_start="dev",
            apps=["code", "notion"],
            urls=[],
            vercel=None,
            supabase=None,
            railway=None,
        )

        config_path = os.path.join(wrapper_dir, "project.yaml")
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(config.model_dump(), f, sort_keys=False)

        return {
            "success": True,
            "message": (
                f"Registered existing project at {path} as "
                f"'{wrapper_name}'"
            ),
            "key": wrapper_name,
            "path": wrapper_dir,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
