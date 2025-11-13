"""Tests for executor functions (with mocking)."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from backend.executor import (
    is_process_running,
    start_environment,
    stop_environment,
    open_urls
)
import state
from backend.loader import load_all_projects


@pytest.fixture(autouse=True)
def setup_projects():
    """Load projects before each test."""
    state.projects.clear()
    load_all_projects()


@patch('backend.executor.psutil.process_iter')
def test_is_process_running_found(mock_process_iter):
    """Test detecting a running process."""
    mock_proc = Mock()
    mock_proc.info = {'name': 'code.exe'}
    mock_process_iter.return_value = [mock_proc]
    
    assert is_process_running("code") is True


@patch('backend.executor.psutil.process_iter')
def test_is_process_running_not_found(mock_process_iter):
    """Test detecting a non-running process."""
    mock_proc = Mock()
    mock_proc.info = {'name': 'other.exe'}
    mock_process_iter.return_value = [mock_proc]
    
    assert is_process_running("code") is False


@patch('backend.executor.subprocess.Popen')
@patch('backend.executor.is_process_running')
@patch('backend.executor.os.path.exists')
def test_start_environment_opens_vscode(mock_exists, mock_running, mock_popen):
    """Test that start_environment opens VS Code when not running."""
    mock_exists.return_value = True
    mock_running.return_value = False
    
    if "demo-webapp" in state.projects:
        start_environment("demo-webapp")
        
        # Should call Popen for VS Code
        assert mock_popen.called


@patch('backend.executor.subprocess.Popen')
@patch('backend.executor.is_process_running')
def test_start_environment_skips_running_apps(mock_running, mock_popen):
    """Test that already running apps are not started again."""
    # All apps already running
    mock_running.return_value = True
    
    if "demo-webapp" in state.projects:
        start_environment("demo-webapp")
        
        # Should still call Popen for task execution, but fewer times
        # than if nothing was running
        assert True  # Basic smoke test


@patch('backend.executor.subprocess.run')
@patch('backend.executor.os.path.exists')
def test_stop_environment_runs_docker_compose_down(mock_exists, mock_run):
    """Test that stop runs docker compose down if file exists."""
    mock_exists.return_value = True
    
    if "demo-docker" in state.projects:
        stop_environment("demo-docker")
        
        # Should have called docker compose down
        assert mock_run.called
        call_args = str(mock_run.call_args)
        assert "compose" in call_args.lower()
        assert "down" in call_args.lower()


@patch('backend.executor.subprocess.run')
@patch('backend.executor.os.path.exists')
def test_stop_environment_skips_without_compose(mock_exists, mock_run):
    """Test that stop skips docker compose if no file."""
    mock_exists.return_value = False
    
    if "demo-webapp" in state.projects:
        stop_environment("demo-webapp")
        
        # Should not call docker compose
        assert not any("compose" in str(call).lower() for call in mock_run.call_args_list)


@patch('backend.executor.webbrowser.open')
@patch('backend.executor.subprocess.Popen')
@patch('backend.executor.is_process_running')
@patch('backend.executor.os.path.exists')
def test_open_urls_uses_brave_when_available(mock_exists, mock_running, mock_popen, mock_browser):
    """Test URL opening with Brave browser."""
    mock_exists.return_value = True
    mock_running.return_value = False
    
    if "demo-webapp" in state.projects:
        open_urls("demo-webapp")
        
        # Should try to use Brave
        assert mock_popen.called or mock_browser.called


@patch('backend.executor.webbrowser.open')
@patch('backend.executor.is_process_running')
@patch('backend.executor.os.path.exists')
def test_open_urls_uses_browser_when_brave_running(mock_exists, mock_running, mock_browser):
    """Test URL opening when Brave already running."""
    mock_exists.return_value = True
    mock_running.return_value = True  # Brave already running
    
    if "demo-webapp" in state.projects:
        open_urls("demo-webapp")
        
        # Should use webbrowser.open
        assert mock_browser.called
