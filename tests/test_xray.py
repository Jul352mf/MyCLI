from __future__ import annotations

from pathlib import Path

from backend.xray import scan_repo


def test_scan_repo_basic(tmp_path: Path):
    # create tiny repo
    d = tmp_path / "repo"
    d.mkdir()
    (d / "a.py").write_text("print('hi')\n" * 3, encoding="utf-8")
    (d / "b.md").write_text("# title\n\ntext\n", encoding="utf-8")

    stats = scan_repo(d)
    assert stats.total_files >= 2
    assert stats.total_lines >= 3
    assert stats.total_size_bytes > 0
    assert isinstance(stats.language_breakdown, dict)
    assert stats.health_index is not None
