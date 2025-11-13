"""Taskfile parsing and task execution."""
import os
import subprocess
from typing import List, Optional
import yaml
import state


def load_tasks(project_key: str) -> List[str]:
    """Load tasks from Taskfile.yml for the given project.

    Prefer the configured dev_dir from ProjectConfig so projects that are
    "added from path" (where the wrapper directory under PROJECTS_ROOT does
    not contain a Taskfile.yml) still resolve tasks correctly.
    """
    if project_key not in state.projects:
        return []

    project_dir, project_config = state.projects[project_key]
    # Use dev_dir if available, fall back to project_dir
    base_dir = getattr(project_config, "dev_dir", project_dir) or project_dir
    taskfile_path = os.path.join(base_dir, "Taskfile.yml")
    
    if not os.path.exists(taskfile_path):
        return []
    
    try:
        with open(taskfile_path, "r", encoding="utf-8") as f:
            taskfile_data = yaml.safe_load(f)
        
        if not taskfile_data or "tasks" not in taskfile_data:
            return []
        
        tasks = taskfile_data["tasks"]
        return list(tasks.keys())
    except Exception:
        return []


def execute_task(
    project_key: str,
    task_name: str,
    cwd_dir: Optional[str] = None,
    args: Optional[List[str]] = None,
) -> None:
    """Execute a Taskfile task in Windows Terminal.

    If cwd_dir is provided, runs from that directory (for monorepo
    subprojects); otherwise uses the project's configured dev_dir.
    """
    if project_key not in state.projects:
        return
    
    project_dir, project_config = state.projects[project_key]
    dev_dir = cwd_dir or project_config.dev_dir
    
    extra = ""
    if args:
        extra = " " + " ".join(args)
    cmd = (
        'wt.exe -w 0 nt -d "{dev}" powershell -NoLogo -NoExit '
        '-Command task {task}{extra}'
    ).format(dev=dev_dir, task=task_name, extra=extra)
    subprocess.Popen(cmd, shell=True)
