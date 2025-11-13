"""Persistent command catalog for discovered commands.

This module provides utilities to:
- Discover commands for a project using the DiscoveryEngine
- Persist the normalized catalog to a JSON file under the project wrapper dir
- Load the catalog for use in the TUI (e.g., CommandDialog)

The catalog format is a list of CommandDefinition dicts (model_dump output).
"""
from __future__ import annotations

import json
import os
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List

from .discovery.engine import DiscoveryEngine
from .discovery.plugins.taskfile import TaskfilePlugin
from .discovery.plugins.npm_scripts import NpmScriptsPlugin
from .models import CommandDefinition
import state


CATALOG_FILENAME = "command_catalog.json"


def _get_paths(project_key: str) -> tuple[Path, Path]:
    """Return (wrapper_dir, dev_dir) for the project key.

    Raises KeyError if project not found in state.
    """
    wrapper_dir_str, config = state.projects[project_key]
    wrapper_dir = Path(wrapper_dir_str)
    dev_dir_str = (
        getattr(config, "dev_dir", wrapper_dir_str) or wrapper_dir_str
    )
    dev_dir = Path(dev_dir_str)
    return wrapper_dir, dev_dir


def catalog_path(project_key: str) -> Path:
    """Absolute path to the catalog JSON for a project wrapper."""
    wrapper_dir, _ = _get_paths(project_key)
    return wrapper_dir / CATALOG_FILENAME


def discover_commands(project_key: str) -> List[CommandDefinition]:
    """Run discovery for the project's dev_dir and return commands."""
    _, dev_dir = _get_paths(project_key)
    engine = DiscoveryEngine([
        TaskfilePlugin(),
        NpmScriptsPlugin(),
    ])
    result = engine.run(dev_dir)
    return result.commands


def refresh_catalog(project_key: str) -> Dict[str, Any]:
    """Rebuild and persist the catalog for the given project.

    Returns a dict: {success: bool, count: int, path: str, error?: str}
    """
    try:
        cmds = discover_commands(project_key)
        path = catalog_path(project_key)
        data = [c.model_dump() for c in cmds]
        # Ensure wrapper dir exists (should already) then write
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return {"success": True, "count": len(data), "path": str(path)}
    except Exception as e:  # pragma: no cover - defensive I/O guard
        return {"success": False, "error": str(e)}


def load_catalog(project_key: str) -> List[Dict[str, Any]]:
    """Load the catalog JSON for a project. Returns empty list if missing."""
    try:
        path = catalog_path(project_key)
        if not path.exists():
            return []
        text = path.read_text(encoding="utf-8")
        data = json.loads(text)
        if isinstance(data, list):
            return data
        return []
    except Exception:  # pragma: no cover - treat as empty on errors
        return []
