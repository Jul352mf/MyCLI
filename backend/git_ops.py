"""Git operations and status."""
import subprocess
import os
from typing import Dict, Any, Optional
from datetime import datetime


def get_git_status(project_dir: str) -> Optional[Dict[str, Any]]:
    """Get git status for a project directory."""
    if not os.path.exists(os.path.join(project_dir, ".git")):
        return None
    
    try:
        # Get current branch
        branch_result = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=5
        )
        branch = branch_result.stdout.strip() if branch_result.returncode == 0 else "unknown"
        
        # Get last commit info
        commit_result = subprocess.run(
            ["git", "log", "-1", "--pretty=format:%s|%ar|%h"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if commit_result.returncode == 0 and commit_result.stdout:
            parts = commit_result.stdout.split("|")
            last_commit_msg = parts[0] if len(parts) > 0 else "No commits"
            last_commit_time = parts[1] if len(parts) > 1 else ""
            last_commit_hash = parts[2] if len(parts) > 2 else ""
        else:
            last_commit_msg = "No commits"
            last_commit_time = ""
            last_commit_hash = ""
        
        # Get status (uncommitted changes)
        status_result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=5
        )
        
        status_lines = status_result.stdout.strip().split("\n") if status_result.stdout else []
        uncommitted_count = len([l for l in status_lines if l.strip()])
        
        # Get ahead/behind info
        tracking_result = subprocess.run(
            ["git", "rev-list", "--left-right", "--count", f"HEAD...@{{u}}"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=5
        )
        
        ahead, behind = 0, 0
        if tracking_result.returncode == 0 and tracking_result.stdout:
            parts = tracking_result.stdout.strip().split()
            if len(parts) == 2:
                ahead, behind = int(parts[0]), int(parts[1])
        
        return {
            "branch": branch,
            "last_commit_msg": last_commit_msg,
            "last_commit_time": last_commit_time,
            "last_commit_hash": last_commit_hash,
            "uncommitted_count": uncommitted_count,
            "ahead": ahead,
            "behind": behind,
            "has_git": True
        }
        
    except Exception:
        return None


def git_pull(project_dir: str) -> tuple[bool, str]:
    """Pull latest changes from remote."""
    try:
        result = subprocess.run(
            ["git", "pull"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode == 0, result.stdout + result.stderr
    except Exception as e:
        return False, str(e)


def git_push(project_dir: str) -> tuple[bool, str]:
    """Push commits to remote."""
    try:
        result = subprocess.run(
            ["git", "push"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode == 0, result.stdout + result.stderr
    except Exception as e:
        return False, str(e)


def git_init_and_commit(project_dir: str, initial_message: str = "Initial commit") -> bool:
    """Initialize git repo and create initial commit."""
    try:
        # Init
        subprocess.run(["git", "init"], cwd=project_dir, capture_output=True, timeout=10)
        
        # Add all
        subprocess.run(["git", "add", "."], cwd=project_dir, capture_output=True, timeout=10)
        
        # Commit
        result = subprocess.run(
            ["git", "commit", "-m", initial_message],
            cwd=project_dir,
            capture_output=True,
            timeout=10
        )
        
        return result.returncode == 0
    except Exception:
        return False
