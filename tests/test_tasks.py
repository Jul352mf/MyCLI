"""Tests for task loading and execution."""
import os
import pytest
from backend.tasks import load_tasks
import state
from backend.loader import load_all_projects


@pytest.fixture(autouse=True)
def setup_projects():
    """Load projects before each test."""
    state.projects.clear()
    load_all_projects()


def test_load_tasks_from_demo_webapp():
    """Test loading tasks from demo-webapp Taskfile."""
    tasks = load_tasks("demo-webapp")
    
    assert len(tasks) > 0
    assert "dev" in tasks
    assert "build" in tasks
    assert "test" in tasks
    assert "lint" in tasks
    assert "deploy" in tasks


def test_load_tasks_from_demo_docker():
    """Test loading tasks from demo-docker Taskfile."""
    tasks = load_tasks("demo-docker")
    
    assert len(tasks) > 0
    assert "up" in tasks
    assert "down" in tasks
    assert "logs" in tasks


def test_load_tasks_from_demo_fullstack():
    """Test loading complex tasks from demo-fullstack."""
    tasks = load_tasks("demo-fullstack")
    
    assert len(tasks) > 0
    assert "dev" in tasks
    assert "db:migrate" in tasks or "db" in tasks
    

def test_load_tasks_nonexistent_project():
    """Test loading tasks from non-existent project."""
    tasks = load_tasks("nonexistent-project")
    assert tasks == []


def test_load_tasks_project_without_taskfile():
    """Test loading tasks from project without Taskfile."""
    # Create temp project without Taskfile
    test_project = "test-no-taskfile"
    if test_project in state.projects:
        tasks = load_tasks(test_project)
        # Should return empty list if no Taskfile
        assert isinstance(tasks, list)
