"""Tests for quick commands management."""
import pytest
import json
from pathlib import Path
from backend.quick_commands import (
    load_quick_commands,
    save_quick_commands,
    add_quick_command,
    remove_quick_command,
    update_quick_command,
    get_quick_command,
    QUICK_COMMANDS_FILE,
)
from backend.models import QuickCommand


@pytest.fixture
def temp_quick_commands_file(tmp_path, monkeypatch):
    """Use a temporary file for quick commands during tests."""
    temp_file = tmp_path / "quick_commands.json"
    monkeypatch.setattr("backend.quick_commands.QUICK_COMMANDS_FILE", temp_file)
    return temp_file


def test_ensure_quick_commands_file_creates_directory(temp_quick_commands_file):
    """Test that ensure_quick_commands_file creates the necessary directory."""
    from backend.quick_commands import ensure_quick_commands_file
    
    ensure_quick_commands_file()
    assert temp_quick_commands_file.parent.exists()
    assert temp_quick_commands_file.exists()
    assert temp_quick_commands_file.read_text() == "[]"


def test_load_empty_quick_commands(temp_quick_commands_file):
    """Test loading when file doesn't exist."""
    commands = load_quick_commands()
    assert commands == []


def test_add_quick_command(temp_quick_commands_file):
    """Test adding a new quick command."""
    cmd = QuickCommand.create(
        name="Test Command",
        adapter="shell",
        command="echo hello",
        scope="global",
    )
    
    result = add_quick_command(cmd)
    assert result is True
    
    # Verify it was saved
    commands = load_quick_commands()
    assert len(commands) == 1
    assert commands[0].name == "Test Command"
    assert commands[0].command == "echo hello"


def test_add_duplicate_quick_command(temp_quick_commands_file):
    """Test that adding duplicate command fails."""
    cmd = QuickCommand.create(
        name="Test Command",
        adapter="shell",
        command="echo hello",
    )
    
    add_quick_command(cmd)
    result = add_quick_command(cmd)  # Try to add same command again
    
    assert result is False
    commands = load_quick_commands()
    assert len(commands) == 1  # Should still only have one


def test_remove_quick_command(temp_quick_commands_file):
    """Test removing a quick command."""
    cmd = QuickCommand.create(
        name="Test Command",
        adapter="shell",
        command="echo hello",
    )
    
    add_quick_command(cmd)
    result = remove_quick_command(cmd.id)
    
    assert result is True
    commands = load_quick_commands()
    assert len(commands) == 0


def test_remove_nonexistent_command(temp_quick_commands_file):
    """Test removing a command that doesn't exist."""
    result = remove_quick_command("nonexistent_id")
    assert result is False


def test_update_quick_command(temp_quick_commands_file):
    """Test updating an existing quick command."""
    cmd = QuickCommand.create(
        name="Test Command",
        adapter="shell",
        command="echo hello",
    )
    
    add_quick_command(cmd)
    
    # Update the command
    cmd.command = "echo world"
    result = update_quick_command(cmd)
    
    assert result is True
    
    # Verify update was saved
    commands = load_quick_commands()
    assert len(commands) == 1
    assert commands[0].command == "echo world"


def test_update_nonexistent_command(temp_quick_commands_file):
    """Test updating a command that doesn't exist."""
    cmd = QuickCommand.create(
        name="Nonexistent",
        adapter="shell",
        command="echo test",
    )
    
    result = update_quick_command(cmd)
    assert result is False


def test_get_quick_command(temp_quick_commands_file):
    """Test getting a quick command by ID."""
    cmd = QuickCommand.create(
        name="Test Command",
        adapter="shell",
        command="echo hello",
    )
    
    add_quick_command(cmd)
    retrieved = get_quick_command(cmd.id)
    
    assert retrieved is not None
    assert retrieved.id == cmd.id
    assert retrieved.name == cmd.name


def test_get_nonexistent_command(temp_quick_commands_file):
    """Test getting a command that doesn't exist."""
    result = get_quick_command("nonexistent_id")
    assert result is None


def test_multiple_commands(temp_quick_commands_file):
    """Test managing multiple quick commands."""
    cmd1 = QuickCommand.create(
        name="Command 1",
        adapter="shell",
        command="echo 1",
    )
    cmd2 = QuickCommand.create(
        name="Command 2",
        adapter="npm",
        command="npm test",
    )
    
    add_quick_command(cmd1)
    add_quick_command(cmd2)
    
    commands = load_quick_commands()
    assert len(commands) == 2
    
    # Remove one
    remove_quick_command(cmd1.id)
    commands = load_quick_commands()
    assert len(commands) == 1
    assert commands[0].id == cmd2.id
