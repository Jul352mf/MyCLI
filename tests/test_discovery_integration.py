"""Optional integration test for discovery against a real repository.

This test is SKIPPED by default. Enable by setting the environment variable
MYCLI_DISCOVERY_REPO to an absolute path.
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest

from backend.discovery.engine import DiscoveryEngine
from backend.discovery.plugins.taskfile import TaskfilePlugin


REPO_ENV = "MYCLI_DISCOVERY_REPO"


def _target_path() -> Path | None:
    p = os.environ.get(REPO_ENV)
    if not p:
        return None
    path = Path(p)
    return path if path.exists() and path.is_dir() else None


@pytest.mark.integration
def test_discovery_runs_against_target_repo():
    repo = _target_path()
    if repo is None:
        pytest.skip(f"Set {REPO_ENV} to enable this integration test")

    engine = DiscoveryEngine([TaskfilePlugin()])
    result = engine.run(repo)

    # Basic sanity assertions: types and non-crashing execution
    assert isinstance(result.commands, list)
    assert isinstance(result.raw_artifacts, list)
    # Do not assert non-empty: repositories may lack Taskfile.yml
    # But if commands exist, ensure they look like CommandDefinition models
    for c in result.commands:
        assert hasattr(c, "name") and hasattr(c, "source_path")
