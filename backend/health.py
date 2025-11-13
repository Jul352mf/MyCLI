"""System health monitoring."""
from typing import Dict, Any
import psutil


def get_system_health() -> Dict[str, Any]:
    """Get current system health snapshot."""
    health = {}
    
    # CPU percentage
    health["cpu_percent"] = psutil.cpu_percent(interval=0.1)
    
    # RAM percentage
    memory = psutil.virtual_memory()
    health["ram_percent"] = memory.percent
    
    # Count listening ports
    listening_ports = 0
    try:
        connections = psutil.net_connections(kind='inet')
        for conn in connections:
            if conn.status == psutil.CONN_LISTEN:
                listening_ports += 1
    except (psutil.AccessDenied, psutil.NoSuchProcess):
        pass
    
    health["listening_ports"] = listening_ports
    
    return health
