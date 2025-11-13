"""Tests for project loader."""
import os
import pytest
from backend.loader import load_all_projects
import state


def test_load_all_projects_finds_demo_projects():
    """Test that loader discovers demo projects."""
    state.projects.clear()
    load_all_projects()
    
    # Should find at least the demo projects
    assert len(state.projects) >= 4
    assert "demo-webapp" in state.projects
    assert "demo-api" in state.projects
    assert "demo-docker" in state.projects
    assert "demo-fullstack" in state.projects


def test_loaded_project_structure():
    """Test that loaded projects have correct structure."""
    state.projects.clear()
    load_all_projects()
    
    if "demo-webapp" in state.projects:
        project_dir, config = state.projects["demo-webapp"]
        
        # Check directory path
        assert "demo-webapp" in project_dir
        assert os.path.exists(project_dir)
        
        # Check config fields
        assert config.name == "Demo Web App"
        assert config.task_start == "dev"
        assert "code" in config.apps
        assert len(config.urls) > 0


def test_project_with_vercel_config():
    """Test project with Vercel configuration."""
    state.projects.clear()
    load_all_projects()
    
    if "demo-webapp" in state.projects:
        _, config = state.projects["demo-webapp"]
        assert config.vercel is not None
        assert config.vercel.project_slug == "demo-webapp"


def test_project_with_supabase_config():
    """Test project with Supabase configuration."""
    state.projects.clear()
    load_all_projects()
    
    if "demo-api" in state.projects:
        _, config = state.projects["demo-api"]
        assert config.supabase is not None
        assert "supabase.co" in config.supabase.api_url


def test_project_with_railway_config():
    """Test project with Railway configuration."""
    state.projects.clear()
    load_all_projects()
    
    if "demo-fullstack" in state.projects:
        _, config = state.projects["demo-fullstack"]
        assert config.railway is not None
        assert config.railway.project_id is not None


def test_project_without_yaml_ignored():
    """Test that folders without project.yaml are ignored."""
    state.projects.clear()
    load_all_projects()
    
    # mycli itself should not be loaded as a project
    assert "mycli" not in state.projects
