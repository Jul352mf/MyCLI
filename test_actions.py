"""Quick test to verify action keys work."""
import state
from backend.loader import load_all_projects

# Load projects
load_all_projects()

print(f"Loaded {len(state.projects)} projects:")
for key in state.projects.keys():
    print(f"  - {key}")

# Simulate selection
if state.projects:
    first_project = list(state.projects.keys())[0]
    state.selected_project = first_project
    print(f"\nSelected project: {state.selected_project}")
    print(f"Project exists in dict: {state.selected_project in state.projects}")
    
    # Check if we can access it
    if state.selected_project in state.projects:
        project_path, config = state.projects[state.selected_project]
        print(f"Project path: {project_path}")
        print(f"Project name: {config.name}")
        print("\n✅ State management working correctly!")
    else:
        print("\n❌ State management broken!")
