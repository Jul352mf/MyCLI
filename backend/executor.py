"""Process execution and environment control."""
import subprocess
import os
import webbrowser
from typing import Optional, Dict
import psutil
import state
from backend.tasks import load_tasks


def is_process_running(name_substring: str) -> bool:
    """Check if a process with name containing substring is running."""
    for proc in psutil.process_iter(['name']):
        try:
            if name_substring.lower() in proc.info['name'].lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False


def kill_process_by_pid(pid: int) -> bool:
    """Kill a process by PID gracefully.

    Be defensive about pid types during testing/mocking where pid may be a
    MagicMock or string; attempt to coerce to int and fail gracefully.
    """
    try:
        if not isinstance(pid, int):
            try:
                pid = int(pid)  # type: ignore[arg-type]
            except Exception:
                return False
        process = psutil.Process(pid)
        process.terminate()  # Try graceful shutdown first
        try:
            process.wait(timeout=5)  # Wait up to 5 seconds
        except psutil.TimeoutExpired:
            process.kill()  # Force kill if didn't terminate
        return True
    except (psutil.NoSuchProcess, psutil.AccessDenied, TypeError, ValueError):
        return False


def start_dev_task(project_key: str) -> Optional[int]:
    """Start the main dev task and return PID."""
    if project_key not in state.projects:
        return None
    
    project_dir, project_config = state.projects[project_key]
    dev_dir = project_config.dev_dir
    
    # Check if Taskfile exists
    taskfile_path = os.path.join(dev_dir, "Taskfile.yml")
    if not os.path.exists(taskfile_path):
        return None
    
    # Load tasks and find 'dev' or 'start' task
    tasks = load_tasks(project_key)
    dev_task = None
    
    if "dev" in tasks:
        dev_task = "dev"
    elif "start" in tasks:
        dev_task = "start"
    elif tasks:
        dev_task = tasks[0]  # Use first task as fallback
    
    if not dev_task:
        return None
    
    # Start task in background and capture PID
    try:
        # Use PowerShell to run task in new window
        cmd = f'task {dev_task}'
        process = subprocess.Popen(
            cmd,
            cwd=dev_dir,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        
        # Track in state
        state.running_processes[f"{project_key}_dev"] = process.pid
        
        # Add to memory
        if project_key in state.project_memories:
            memory = state.project_memories[project_key]
            memory.add_action(f"Started {dev_task} task")
        
        return process.pid
    except Exception as e:
        print(f"Failed to start dev task: {e}")
        return None


def start_environment(project_key: str) -> None:
    """Start project environment (Key 1)."""
    if project_key not in state.projects:
        return
    
    project_dir, project_config = state.projects[project_key]
    
    # Start dev task with PID tracking
    start_dev_task(project_key)
    
    # Open VS Code if not running
    if not is_process_running("code"):
        workspace_path = project_config.workspace
        if os.path.exists(workspace_path):
            subprocess.Popen(["code", workspace_path], shell=True)
    
    # Open URLs
    open_urls(project_key)


def stop_environment(project_key: str) -> Dict[str, bool]:
    """Stop project environment (Key 2)."""
    results = {"dev_stopped": False, "docker_stopped": False}
    
    if project_key not in state.projects:
        return results
    
    project_dir, project_config = state.projects[project_key]
    dev_dir = project_config.dev_dir
    
    # Stop tracked dev process
    dev_key = f"{project_key}_dev"
    if dev_key in state.running_processes:
        pid = state.running_processes[dev_key]
        if kill_process_by_pid(pid):
            results["dev_stopped"] = True
            del state.running_processes[dev_key]
            
            # Add to memory
            if project_key in state.project_memories:
                memory = state.project_memories[project_key]
                memory.add_action("Stopped dev task")
    
    # Check for docker-compose.yml
    docker_compose_path = os.path.join(dev_dir, "docker-compose.yml")
    
    if os.path.exists(docker_compose_path):
        try:
            subprocess.run(
                ["docker", "compose", "down"],
                cwd=dev_dir,
                shell=True,
                capture_output=True,
                timeout=30
            )
            results["docker_stopped"] = True
        except (subprocess.TimeoutExpired, Exception):
            pass
    
    return results


def open_urls(project_key: str) -> None:
    """Open project URLs in browser (F4)."""
    if project_key not in state.projects:
        return
    
    project_dir, project_config = state.projects[project_key]
    urls = project_config.urls
    
    if not urls:
        return
    
    brave_path = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
    
    # Check if brave.exe exists
    if os.path.exists(brave_path):
        if not is_process_running("brave"):
            # Launch Brave with all URLs
            subprocess.Popen([brave_path] + urls, shell=True)
        else:
            # Brave already running, use webbrowser
            for url in urls:
                webbrowser.open(url)
    else:
        # Brave not found, use default browser
        for url in urls:
            webbrowser.open(url)


def execute_npm_script(
    project_key: str,
    script_name: str,
    package_manager: str = "npm",
    cwd_dir: Optional[str] = None,
    args: Optional[list[str]] = None,
) -> None:
    """Execute an npm/pnpm script in Windows Terminal.

    Opens a new tab in the current Windows Terminal window, changes to the
    project's dev_dir, and runs the given script with the selected package
    manager, leaving the terminal open.
    """
    if project_key not in state.projects:
        return

    _, project_config = state.projects[project_key]
    dev_dir = cwd_dir or project_config.dev_dir

    pm = package_manager.lower().strip() if package_manager else "npm"
    if pm not in ("npm", "pnpm"):
        pm = "npm"

    # Use -NoExit to keep the tab open after completion
    extra = ""
    if args:
        extra = " -- " + " ".join(args)
    cmd = (
        'wt.exe -w 0 nt -d "{dev}" powershell -NoLogo -NoExit '
        '-Command {pm} run {script}{extra}'
    ).format(dev=dev_dir, pm=pm, script=script_name, extra=extra)
    try:
        subprocess.Popen(cmd, shell=True)
    except Exception:
        # Best-effort execution; errors are non-fatal for the TUI
        pass
