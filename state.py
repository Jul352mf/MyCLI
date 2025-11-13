"""Global application state."""
from typing import Dict, Tuple, List, Optional, Any

# Storage for all discovered projects
# Key: folder name, Value: (project_dir_path, ProjectConfig instance)
projects: Dict[str, Tuple[str, Any]] = {}

# Currently selected project key
selected_project: Optional[str] = None

# Task list for current project (displayed in tasks view)
task_list: List[str] = []

# System health data (displayed in system view)
system_health: Dict[str, Any] = {}

# Current view: "dashboard", "tasks", "system"
current_view: str = "dashboard"

# Running processes (name -> PID)
running_processes: Dict[str, int] = {}

# Project memories cache (project_key -> ProjectMemory)
project_memories: Dict[str, Any] = {}
