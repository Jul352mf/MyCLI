"""Project discovery and loading."""
import os
from pathlib import Path
import yaml
from backend.models import ProjectConfig
import state


PROJECTS_ROOT = r"C:\Dev\Projects"


def load_all_projects() -> None:
    """Discover and load all projects from projects directory."""
    state.projects.clear()
    
    if not os.path.exists(PROJECTS_ROOT):
        return
    
    for folder_name in os.listdir(PROJECTS_ROOT):
        folder_path = os.path.join(PROJECTS_ROOT, folder_name)
        
        if not os.path.isdir(folder_path):
            continue
        
        config_path = os.path.join(folder_path, "project.yaml")
        
        if not os.path.exists(config_path):
            continue
        
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = yaml.safe_load(f)
            
            project_config = ProjectConfig(**config_data)
            state.projects[folder_name] = (folder_path, project_config)
        except Exception:
            # Skip invalid projects
            continue
