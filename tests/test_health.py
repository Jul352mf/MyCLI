"""Tests for system health monitoring."""
import pytest
from unittest.mock import Mock, patch
from backend.health import get_system_health


@patch('backend.health.psutil.cpu_percent')
@patch('backend.health.psutil.virtual_memory')
@patch('backend.health.psutil.net_connections')
def test_get_system_health_returns_dict(mock_conn, mock_mem, mock_cpu):
    """Test that system health returns expected data structure."""
    mock_cpu.return_value = 45.5
    
    mock_memory = Mock()
    mock_memory.percent = 62.3
    mock_mem.return_value = mock_memory
    
    mock_conn.return_value = []
    
    health = get_system_health()
    
    assert isinstance(health, dict)
    assert "cpu_percent" in health
    assert "ram_percent" in health
    assert "listening_ports" in health


@patch('backend.health.psutil.cpu_percent')
@patch('backend.health.psutil.virtual_memory')
@patch('backend.health.psutil.net_connections')
def test_get_system_health_cpu_value(mock_conn, mock_mem, mock_cpu):
    """Test CPU percentage is captured."""
    mock_cpu.return_value = 45.5
    
    mock_memory = Mock()
    mock_memory.percent = 62.3
    mock_mem.return_value = mock_memory
    
    mock_conn.return_value = []
    
    health = get_system_health()
    
    assert health["cpu_percent"] == 45.5


@patch('backend.health.psutil.cpu_percent')
@patch('backend.health.psutil.virtual_memory')
@patch('backend.health.psutil.net_connections')
def test_get_system_health_ram_value(mock_conn, mock_mem, mock_cpu):
    """Test RAM percentage is captured."""
    mock_cpu.return_value = 45.5
    
    mock_memory = Mock()
    mock_memory.percent = 62.3
    mock_mem.return_value = mock_memory
    
    mock_conn.return_value = []
    
    health = get_system_health()
    
    assert health["ram_percent"] == 62.3


@patch('backend.health.psutil.cpu_percent')
@patch('backend.health.psutil.virtual_memory')
@patch('backend.health.psutil.net_connections')
def test_get_system_health_counts_listening_ports(mock_conn, mock_mem, mock_cpu):
    """Test listening ports are counted."""
    mock_cpu.return_value = 45.5
    
    mock_memory = Mock()
    mock_memory.percent = 62.3
    mock_mem.return_value = mock_memory
    
    # Mock 3 listening connections
    import psutil
    mock_conn1 = Mock()
    mock_conn1.status = psutil.CONN_LISTEN
    mock_conn2 = Mock()
    mock_conn2.status = psutil.CONN_LISTEN
    mock_conn3 = Mock()
    mock_conn3.status = psutil.CONN_ESTABLISHED
    
    mock_conn.return_value = [mock_conn1, mock_conn2, mock_conn3]
    
    health = get_system_health()
    
    assert health["listening_ports"] == 2


@patch('backend.health.psutil.cpu_percent')
@patch('backend.health.psutil.virtual_memory')
@patch('backend.health.psutil.net_connections')
def test_get_system_health_handles_access_denied(mock_conn, mock_mem, mock_cpu):
    """Test that AccessDenied errors are handled gracefully."""
    import psutil
    
    mock_cpu.return_value = 45.5
    
    mock_memory = Mock()
    mock_memory.percent = 62.3
    mock_mem.return_value = mock_memory
    
    # Raise AccessDenied
    mock_conn.side_effect = psutil.AccessDenied()
    
    health = get_system_health()
    
    # Should still return health data, just 0 ports
    assert "listening_ports" in health
    assert health["listening_ports"] == 0
