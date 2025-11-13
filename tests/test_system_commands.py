"""Tests for system commands module."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from backend.system_commands import (
    get_all_processes,
    filter_processes,
    get_listening_ports,
    kill_process,
    is_ngrok_available,
    start_ngrok_tunnel,
    ProcessInfo,
    PortInfo,
)


def test_get_all_processes():
    """Test getting all processes returns a list."""
    processes = get_all_processes()
    
    # Should return a list (even if empty in some test environments)
    assert isinstance(processes, list)
    
    # If processes exist, check structure
    if processes:
        assert isinstance(processes[0], ProcessInfo)
        assert hasattr(processes[0], 'pid')
        assert hasattr(processes[0], 'name')


def test_filter_processes_by_name():
    """Test filtering processes by name."""
    # Create mock processes
    mock_processes = [
        ProcessInfo(pid=1, name="python", cmdline="python app.py", 
                   cpu_percent=0.5, memory_mb=100.0, status="running"),
        ProcessInfo(pid=2, name="node", cmdline="node server.js",
                   cpu_percent=1.0, memory_mb=200.0, status="running"),
        ProcessInfo(pid=3, name="chrome", cmdline="chrome.exe",
                   cpu_percent=2.0, memory_mb=500.0, status="running"),
    ]
    
    # Filter by name
    filtered = filter_processes(mock_processes, name_filter="python")
    assert len(filtered) == 1
    assert filtered[0].name == "python"
    
    # Filter by partial name
    filtered = filter_processes(mock_processes, name_filter="py")
    assert len(filtered) == 1
    
    # Filter returning multiple results
    filtered = filter_processes(mock_processes, name_filter="")
    assert len(filtered) == 3


def test_filter_processes_by_cmdline():
    """Test filtering processes by command line content."""
    mock_processes = [
        ProcessInfo(pid=1, name="python", cmdline="python app.py",
                   cpu_percent=0.5, memory_mb=100.0, status="running"),
        ProcessInfo(pid=2, name="python", cmdline="python test.py",
                   cpu_percent=1.0, memory_mb=200.0, status="running"),
    ]
    
    filtered = filter_processes(mock_processes, name_filter="app.py")
    assert len(filtered) == 1
    assert "app.py" in filtered[0].cmdline


@patch('backend.system_commands.psutil.Process')
def test_kill_process_success(mock_process_class):
    """Test successfully killing a process."""
    mock_proc = Mock()
    mock_proc.name.return_value = "test_process"
    mock_proc.wait.return_value = None
    mock_process_class.return_value = mock_proc
    
    success, message = kill_process(1234)
    
    assert success is True
    assert "Successfully terminated" in message
    assert "test_process" in message
    mock_proc.terminate.assert_called_once()


@patch('backend.system_commands.psutil.Process')
def test_kill_process_not_found(mock_process_class):
    """Test killing a non-existent process."""
    import psutil
    mock_process_class.side_effect = psutil.NoSuchProcess(1234)
    
    success, message = kill_process(1234)
    
    assert success is False
    assert "not found" in message.lower()


@patch('backend.system_commands.psutil.Process')
def test_kill_process_access_denied(mock_process_class):
    """Test killing a process without permission."""
    import psutil
    mock_process_class.side_effect = psutil.AccessDenied()
    
    success, message = kill_process(1234)
    
    assert success is False
    assert "access denied" in message.lower()


@patch('backend.system_commands.shutil.which')
def test_is_ngrok_available(mock_which):
    """Test checking if ngrok is available."""
    mock_which.return_value = "/usr/bin/ngrok"
    assert is_ngrok_available() is True
    
    mock_which.return_value = None
    assert is_ngrok_available() is False


@patch('backend.system_commands.subprocess.Popen')
@patch('backend.system_commands.is_ngrok_available')
def test_start_ngrok_tunnel_success(mock_available, mock_popen):
    """Test starting an ngrok tunnel successfully."""
    mock_available.return_value = True
    mock_popen.return_value = Mock()
    
    success, message, url = start_ngrok_tunnel(3000)
    
    assert success is True
    assert "starting" in message.lower()
    mock_popen.assert_called_once()


@patch('backend.system_commands.is_ngrok_available')
def test_start_ngrok_tunnel_not_available(mock_available):
    """Test starting ngrok when it's not installed."""
    mock_available.return_value = False
    
    success, message, url = start_ngrok_tunnel(3000)
    
    assert success is False
    assert "not found" in message.lower()
    assert url is None


def test_get_listening_ports():
    """Test getting listening ports."""
    # This is a basic test that just checks the function runs
    # In a real environment, it would return actual ports
    ports = get_listening_ports()
    
    assert isinstance(ports, list)
    # If ports exist, check structure
    if ports:
        assert isinstance(ports[0], PortInfo)
        assert hasattr(ports[0], 'port')
        assert hasattr(ports[0], 'pid')


def test_process_info_dataclass():
    """Test ProcessInfo dataclass creation."""
    proc = ProcessInfo(
        pid=1234,
        name="test",
        cmdline="test command",
        cpu_percent=1.5,
        memory_mb=100.0,
        status="running"
    )
    
    assert proc.pid == 1234
    assert proc.name == "test"
    assert proc.cpu_percent == 1.5


def test_port_info_dataclass():
    """Test PortInfo dataclass creation."""
    port = PortInfo(
        port=8080,
        pid=1234,
        process_name="node"
    )
    
    assert port.port == 8080
    assert port.pid == 1234
    assert port.process_name == "node"
