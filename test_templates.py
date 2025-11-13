"""Test template loading."""
from backend.templates import get_template_manager

# Test loading
manager = get_template_manager()

print("Templates loaded:")
for template in manager.list_templates():
    print(f"  - {template['id']}: {template['name']}")
    print(f"    Language: {template['language']}")
    print(f"    Description: {template['description']}")
    print()

# Test getting a specific template
fastapi_template = manager.get_template("python-fastapi")
if fastapi_template:
    print(f"FastAPI template has {len(fastapi_template.files)} files")
    print(f"Directories: {fastapi_template.directories}")
