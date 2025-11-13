"""Tests for project creator."""
import os
import shutil
import pytest
from backend.creator import create_project_structure


@pytest.fixture
def cleanup_test_project():
    """Clean up test project before and after test."""
    test_dir = r"C:\Dev\Projects\test-created-project"
    testcreatedproject_dir = r"C:\Dev\Projects\testcreatedproject"
    
    # Clean up before test
    for dir_path in [test_dir, testcreatedproject_dir]:
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
    
    yield
    
    # Clean up after test
    for dir_path in [test_dir, testcreatedproject_dir]:
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)


def test_create_project_basic(cleanup_test_project):
    """Test creating a basic project."""
    result = create_project_structure("Test Created Project")
    
    assert result["success"] is True
    assert "path" in result
    assert "Test Created Project" in result["message"]
    
    # Check created files
    project_path = result["path"]
    assert os.path.exists(project_path)
    assert os.path.exists(os.path.join(project_path, "project.yaml"))
    assert os.path.exists(os.path.join(project_path, "Taskfile.yml"))
    assert os.path.exists(os.path.join(project_path, "README.md"))


def test_create_project_duplicate_fails(cleanup_test_project):
    """Test that creating duplicate project fails."""
    # Create first project
    result1 = create_project_structure("Test Created Project")
    assert result1["success"] is True
    
    # Try to create again
    result2 = create_project_structure("Test Created Project")
    assert result2["success"] is False
    assert "already exists" in result2["error"]


def test_create_project_sanitizes_name(cleanup_test_project):
    """Test that project name is sanitized for directory."""
    result = create_project_structure("Test Created Project")
    
    assert result["success"] is True
    # Should be lowercase with no spaces
    assert "test-created-project" in result["path"].lower() or "testcreatedproject" in result["path"].lower()


def test_created_project_has_valid_config(cleanup_test_project):
    """Test that created project has valid configuration."""
    import yaml
    
    result = create_project_structure("Test Created Project")
    assert result["success"] is True
    
    config_path = os.path.join(result["path"], "project.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    
    assert config["name"] == "Test Created Project"
    assert config["task_start"] == "dev"
    assert isinstance(config["apps"], list)
    assert isinstance(config["urls"], list)


def test_created_project_has_valid_taskfile(cleanup_test_project):
    """Test that created project has valid Taskfile."""
    import yaml
    
    result = create_project_structure("Test Created Project")
    assert result["success"] is True
    
    taskfile_path = os.path.join(result["path"], "Taskfile.yml")
    with open(taskfile_path, "r", encoding="utf-8") as f:
        taskfile = yaml.safe_load(f)
    
    assert "tasks" in taskfile
    assert "dev" in taskfile["tasks"]
    assert "build" in taskfile["tasks"]
    assert "test" in taskfile["tasks"]
