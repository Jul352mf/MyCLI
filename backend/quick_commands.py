"""Quick commands management and storage.

Provides CRUD operations for custom quick commands that can be invoked
globally or per-project.
"""
from pathlib import Path
from typing import List, Optional
import json
from backend.models import QuickCommand


QUICK_COMMANDS_FILE = Path.home() / ".mycli" / "quick_commands.json"


def ensure_quick_commands_file() -> None:
    """Ensure the quick commands file exists."""
    QUICK_COMMANDS_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not QUICK_COMMANDS_FILE.exists():
        QUICK_COMMANDS_FILE.write_text("[]")


def load_quick_commands() -> List[QuickCommand]:
    """Load all quick commands from storage."""
    ensure_quick_commands_file()
    try:
        data = json.loads(QUICK_COMMANDS_FILE.read_text())
        return [QuickCommand(**item) for item in data]
    except (json.JSONDecodeError, ValueError):
        return []


def save_quick_commands(commands: List[QuickCommand]) -> None:
    """Save quick commands to storage."""
    ensure_quick_commands_file()
    data = [cmd.model_dump() for cmd in commands]
    QUICK_COMMANDS_FILE.write_text(json.dumps(data, indent=2))


def add_quick_command(command: QuickCommand) -> bool:
    """Add a new quick command."""
    commands = load_quick_commands()
    
    # Check for duplicate ID
    if any(cmd.id == command.id for cmd in commands):
        return False
    
    commands.append(command)
    save_quick_commands(commands)
    return True


def remove_quick_command(command_id: str) -> bool:
    """Remove a quick command by ID."""
    commands = load_quick_commands()
    original_count = len(commands)
    commands = [cmd for cmd in commands if cmd.id != command_id]
    
    if len(commands) < original_count:
        save_quick_commands(commands)
        return True
    return False


def update_quick_command(command: QuickCommand) -> bool:
    """Update an existing quick command."""
    commands = load_quick_commands()
    
    for i, cmd in enumerate(commands):
        if cmd.id == command.id:
            commands[i] = command
            save_quick_commands(commands)
            return True
    
    return False


def get_quick_command(command_id: str) -> Optional[QuickCommand]:
    """Get a quick command by ID."""
    commands = load_quick_commands()
    for cmd in commands:
        if cmd.id == command_id:
            return cmd
    return None
