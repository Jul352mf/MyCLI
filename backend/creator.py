"""Project creation wizard."""
import os
import yaml
from typing import Dict, Any


def create_project_structure(project_name: str, base_path: str = r"C:\Dev\Projects") -> Dict[str, Any]:
    """Create new project directory structure and configuration files."""
    
    # Sanitize project name for directory
    dir_name = project_name.lower().replace(" ", "")
    project_path = os.path.join(base_path, dir_name)
    
    # Create project directory
    if os.path.exists(project_path):
        return {"success": False, "error": "Project directory already exists"}
    
    try:
        os.makedirs(project_path, exist_ok=True)
        
        # Create project.yaml
        project_config = {
            "name": project_name,
            "workspace": os.path.join(project_path, f"{dir_name}.code-workspace"),
            "dev_dir": project_path,
            "task_start": "dev",
            "apps": ["code", "notion"],
            "urls": ["http://localhost:3000"],
            "vercel": None,
            "supabase": None,
            "railway": None
        }
        
        with open(os.path.join(project_path, "project.yaml"), "w", encoding="utf-8") as f:
            yaml.dump(project_config, f, default_flow_style=False, sort_keys=False)
        
        # Create VS Code workspace file
        workspace_config = {
            "folders": [{"path": "."}],
            "settings": {}
        }
        
        with open(os.path.join(project_path, f"{dir_name}.code-workspace"), "w", encoding="utf-8") as f:
            yaml.dump(workspace_config, f, default_flow_style=False)
        
        # Create basic Taskfile.yml
        taskfile_config = {
            "version": "3",
            "tasks": {
                "dev": {
                    "desc": "Start development server",
                    "cmds": ["echo 'Starting development server...'"]
                },
                "build": {
                    "desc": "Build the project",
                    "cmds": ["echo 'Building project...'"]
                },
                "test": {
                    "desc": "Run tests",
                    "cmds": ["echo 'Running tests...'"]
                }
            }
        }
        
        with open(os.path.join(project_path, "Taskfile.yml"), "w", encoding="utf-8") as f:
            yaml.dump(taskfile_config, f, default_flow_style=False, sort_keys=False)
        
        # Create README.md
        readme_content = f"""# {project_name}

## Getting Started

This project was created with MyCLI.

## Available Tasks

- `task dev` - Start development server
- `task build` - Build the project
- `task test` - Run tests

## Development

Edit `Taskfile.yml` to add more tasks.
Edit `project.yaml` to configure your environment.
"""
        
        with open(os.path.join(project_path, "README.md"), "w", encoding="utf-8") as f:
            f.write(readme_content)
        
        return {
            "success": True,
            "path": project_path,
            "message": f"Project '{project_name}' created successfully!"
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}
