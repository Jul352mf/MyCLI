from pathlib import Path
import tempfile

from backend.utils.gitinfo import (
    parse_remote_url,
    get_repo_slug,
    get_current_branch,
)


def write_git_config(tmp: Path, url: str):
    git = tmp / ".git"
    git.mkdir(parents=True, exist_ok=True)
    (git / "config").write_text(
        f"""
[core]
    repositoryformatversion = 0
[remote "origin"]
    url = {url}
    fetch = +refs/heads/*:refs/remotes/origin/*
""".strip(),
        encoding="utf-8",
    )


def test_parse_remote_url_https():
    owner_repo = parse_remote_url("https://github.com/Jul352mf/JAGI.git")
    assert owner_repo == ("Jul352mf", "JAGI")


def test_parse_remote_url_ssh():
    owner_repo = parse_remote_url("git@github.com:owner/repo.git")
    assert owner_repo == ("owner", "repo")


def test_parse_remote_url_invalid():
    assert parse_remote_url("https://gitlab.com/owner/repo.git") is None
    assert parse_remote_url("") is None


def test_get_repo_slug_from_config_https():
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        write_git_config(tmp, "https://github.com/owner/repo.git")
        assert get_repo_slug(tmp) == "owner/repo"


def test_get_repo_slug_from_config_ssh():
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        write_git_config(tmp, "git@github.com:owner/repo.git")
        assert get_repo_slug(tmp) == "owner/repo"


def test_get_current_branch_from_head():
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        git = tmp / ".git"
        git.mkdir(parents=True, exist_ok=True)
        (git / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
        assert get_current_branch(tmp) == "main"
