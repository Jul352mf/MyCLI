"""System-wide commands for process management, ngrok, etc.

Provides functionality for:
- Listing and filtering processes
- Killing processes
- Managing ngrok tunnels
"""
import psutil
import subprocess
import shutil
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ProcessInfo:
    """Information about a running process."""
    pid: int
    name: str
    cmdline: str
    cpu_percent: float
    memory_mb: float
    status: str


@dataclass
class PortInfo:
    """Information about a listening port."""
    port: int
    pid: int
    process_name: str


def get_all_processes() -> List[ProcessInfo]:
    """Get list of all running processes with details."""
    processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'status']):
        try:
            pinfo = proc.info
            pid = pinfo['pid']
            name = pinfo['name']
            cmdline = ' '.join(pinfo.get('cmdline', []) or [])
            status = pinfo.get('status', 'unknown')
            
            # Get CPU and memory (may fail for some processes)
            try:
                cpu = proc.cpu_percent(interval=0.1)
                mem = proc.memory_info().rss / (1024 * 1024)  # MB
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                cpu = 0.0
                mem = 0.0
            
            processes.append(ProcessInfo(
                pid=pid,
                name=name,
                cmdline=cmdline[:100],  # Truncate long command lines
                cpu_percent=cpu,
                memory_mb=mem,
                status=status
            ))
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    
    return processes


def filter_processes(
    processes: List[ProcessInfo],
    name_filter: str = "",
    port_filter: Optional[int] = None
) -> List[ProcessInfo]:
    """Filter processes by name or port."""
    filtered = processes
    
    if name_filter:
        name_lower = name_filter.lower()
        filtered = [
            p for p in filtered
            if name_lower in p.name.lower() or name_lower in p.cmdline.lower()
        ]
    
    if port_filter is not None:
        # Get processes listening on specific port
        port_pids = {conn.pid for conn in psutil.net_connections()
                     if conn.status == 'LISTEN' and conn.laddr.port == port_filter}
        filtered = [p for p in filtered if p.pid in port_pids]
    
    return filtered


def get_listening_ports() -> List[PortInfo]:
    """Get all listening ports with process information."""
    ports = []
    
    try:
        connections = psutil.net_connections(kind='inet')
        for conn in connections:
            if conn.status == 'LISTEN' and conn.laddr:
                try:
                    proc = psutil.Process(conn.pid) if conn.pid else None
                    process_name = proc.name() if proc else "unknown"
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    process_name = "unknown"
                
                ports.append(PortInfo(
                    port=conn.laddr.port,
                    pid=conn.pid or 0,
                    process_name=process_name
                ))
        
        # Sort by port number
        ports.sort(key=lambda x: x.port)
    except (psutil.AccessDenied, PermissionError):
        # May need elevated privileges on some systems
        pass
    
    return ports


def kill_process(pid: int) -> Tuple[bool, str]:
    """Kill a process by PID.
    
    Returns:
        Tuple of (success, message)
    """
    try:
        process = psutil.Process(pid)
        process_name = process.name()
        
        # Try graceful termination first
        process.terminate()
        
        try:
            process.wait(timeout=5)
            return True, f"Successfully terminated {process_name} (PID: {pid})"
        except psutil.TimeoutExpired:
            # Force kill if graceful termination failed
            process.kill()
            return True, f"Force killed {process_name} (PID: {pid})"
            
    except psutil.NoSuchProcess:
        return False, f"Process {pid} not found"
    except psutil.AccessDenied:
        return False, f"Access denied to kill process {pid} (try running as admin)"
    except Exception as e:
        return False, f"Failed to kill process {pid}: {str(e)}"


def is_ngrok_available() -> bool:
    """Check if ngrok is available in PATH."""
    return shutil.which("ngrok") is not None


def start_ngrok_tunnel(port: int, protocol: str = "http") -> Tuple[bool, str, Optional[str]]:
    """Start an ngrok tunnel on the specified port.
    
    Args:
        port: Local port to tunnel
        protocol: Protocol (http or tcp)
    
    Returns:
        Tuple of (success, message, tunnel_url)
    """
    if not is_ngrok_available():
        return False, "ngrok not found in PATH. Please install ngrok.", None
    
    try:
        # Start ngrok in background
        # Note: This is a simple implementation. Production code might want to:
        # 1. Track ngrok processes
        # 2. Parse ngrok API for tunnel URL
        # 3. Handle ngrok authentication
        
        cmd = ["ngrok", protocol, str(port)]
        
        # On Windows, use CREATE_NEW_CONSOLE to run in new window
        if subprocess.sys.platform == "win32":
            subprocess.Popen(
                cmd,
                creationflags=subprocess.CREATE_NEW_CONSOLE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        else:
            subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        
        # For now, return a message that user should check ngrok window
        # Future: Could query ngrok API at localhost:4040/api/tunnels
        return True, f"ngrok tunnel starting on port {port}", None
        
    except Exception as e:
        return False, f"Failed to start ngrok: {str(e)}", None


def get_ngrok_tunnels() -> List[Dict]:
    """Get active ngrok tunnels by querying the ngrok API.
    
    Returns:
        List of tunnel information dictionaries
    """
    import urllib.request
    import json
    
    try:
        # ngrok exposes an API at localhost:4040 by default
        with urllib.request.urlopen("http://localhost:4040/api/tunnels", timeout=2) as response:
            data = json.loads(response.read().decode())
            return data.get("tunnels", [])
    except Exception:
        # ngrok not running or API not accessible
        return []
