"""Tests for TaskfilePlugin discovery flow."""
from pathlib import Path
import tempfile

from backend.discovery.plugins.taskfile import TaskfilePlugin
from backend.discovery.engine import DiscoveryEngine
from backend.discovery.plugins import TaskfilePlugin as ExportedTaskfile
from backend.models import Origin


def _write_taskfile(dir_path: Path):
    (dir_path / "Taskfile.yml").write_text(
        """version: '3'
vars: {}
tasks:
  build:
    desc: Build the project
    cmd: echo building
  test:
    desc: Run tests
    cmd: echo testing
""",
        encoding="utf-8",
    )


def test_taskfile_plugin_discovers_tasks():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write_taskfile(root)
        plugin = TaskfilePlugin()
        engine = DiscoveryEngine([plugin])
        result = engine.run(root)
        # Should produce two commands
        assert len(result.commands) == 2
        names = sorted(c.name for c in result.commands)
        assert names == ["build", "test"]
        for c in result.commands:
            assert c.origin == Origin.TASKFILE
            assert c.id and len(c.id) == 16  # truncated hash length


def test_exports_match():
    # Ensure exported symbol is same class (public API integrity)
    assert TaskfilePlugin is ExportedTaskfile
