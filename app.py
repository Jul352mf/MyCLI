"""Main TUI application entry point."""
from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.binding import Binding

from components.project_list import ProjectList
from components.dashboard import Dashboard
from components.footer_bar import FooterBar
from components.header_bar import HeaderBar
from components.status_bar import StatusBar
from components.create_modal import CreateProjectModal
from components.git_modal import GitModal
from components.edit_memory_modal import EditMemoryModal
from components.env_modal import EnvModal
from components.command_dialog import CommandDialog
from components.add_project_modal import AddProjectModal
from backend.loader import load_all_projects
from backend.executor import start_environment, stop_environment, open_urls
from backend.tasks import load_tasks, execute_task
from backend.health import get_system_health
from backend.projects import add_project_from_path
import state


class MyCLIApp(App):
    """Main TUI application."""
    
    CSS_PATH = "styles.tcss"
    BINDINGS = [
        Binding("1", "key_1", "Start", priority=True),
        Binding("2", "key_2", "Stop", priority=True),
        Binding("3", "key_3", "Tasks", priority=True),
        Binding("4", "key_4", "Dashboards", priority=True),
        Binding("5", "key_5", "System", priority=True),
        Binding("6", "key_6", "Create", priority=True),
        Binding("a", "add_project", "Add Path", priority=True),
        Binding("g", "git_panel", "Git", priority=True),
        Binding("r", "open_command_dialog", "Run Cmd", priority=True),
        Binding("f5", "refresh_commands", "Refresh", priority=True),
        Binding("m", "edit_memory", "Memory", priority=True),
        Binding("e", "open_env", "Env", priority=True),
        Binding("q", "quit", "Quit", priority=True),
        Binding("escape", "handle_escape", "", show=False),
    ]
    
    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield HeaderBar()
        with Horizontal():
            yield ProjectList()
            yield Dashboard()
        yield StatusBar()
        yield FooterBar()
    
    def on_mount(self) -> None:
        """Load projects on startup."""
        load_all_projects()
        project_list = self.query_one(ProjectList)
        project_list.refresh_list()
        state.current_view = "dashboard"

    def on_unmount(self) -> None:
        """Clean up when app closes."""
        # End all active sessions
        for memory in state.project_memories.values():
            memory.end_session()
    
    def action_key_1(self) -> None:
        """Key 1: Start environment or run task 1."""
        if (
            state.current_view == "tasks"
            and state.task_list
            and len(state.task_list) >= 1
        ):
            self._run_task_by_index(0)
            self.query_one(StatusBar).show_message(
                f"Running task: {state.task_list[0]}"
            )
        elif state.selected_project:
            self.query_one(StatusBar).show_message(
                "🚀 Starting environment..."
            )
            start_environment(state.selected_project)
            self.query_one(Dashboard).refresh_dashboard()
            self.query_one(HeaderBar).update_header()
            self.query_one(StatusBar).show_message(
                "✓ Environment started"
            )
        else:
            self.query_one(StatusBar).show_message(
                "⚠ No project selected"
            )
    
    def action_key_2(self) -> None:
        """Key 2: Stop environment or run task 2."""
        if (
            state.current_view == "tasks"
            and state.task_list
            and len(state.task_list) >= 2
        ):
            self._run_task_by_index(1)
            self.query_one(StatusBar).show_message(
                f"Running task: {state.task_list[1]}"
            )
        elif state.selected_project:
            self.query_one(StatusBar).show_message("🛑 Stopping...")
            results = stop_environment(state.selected_project)
            
            # Build feedback message
            stopped = []
            if results.get("dev_stopped"):
                stopped.append("dev task")
            if results.get("docker_stopped"):
                stopped.append("docker")
            
            if stopped:
                msg = f"✓ Stopped: {', '.join(stopped)}"
            else:
                msg = "ℹ No running processes found"
            
            self.query_one(StatusBar).show_message(msg)
            self.query_one(Dashboard).refresh_dashboard()
        else:
            self.query_one(StatusBar).show_message("⚠ No project selected")
    
    def action_key_3(self) -> None:
        """Key 3: Display tasks list or run task 3."""
        if (
            state.current_view == "tasks"
            and state.task_list
            and len(state.task_list) >= 3
        ):
            self._run_task_by_index(2)
            self.query_one(StatusBar).show_message(
                f"Running task: {state.task_list[2]}"
            )
        elif state.selected_project:
            tasks = load_tasks(state.selected_project)
            state.task_list = tasks
            state.current_view = "tasks"
            self.query_one(Dashboard).show_tasks_view()
            self.query_one(HeaderBar).update_header()
            self.query_one(StatusBar).show_message(
                f"Loaded {len(tasks)} tasks"
            )
        else:
            self.query_one(StatusBar).show_message("⚠ No project selected")
    
    def action_key_4(self) -> None:
        """Key 4: Open URLs or run task 4."""
        if (
            state.current_view == "tasks"
            and state.task_list
            and len(state.task_list) >= 4
        ):
            self._run_task_by_index(3)
            self.query_one(StatusBar).show_message(
                f"Running task: {state.task_list[3]}"
            )
        elif state.selected_project:
            open_urls(state.selected_project)
            if state.selected_project in state.projects:
                _, config = state.projects[state.selected_project]
                self.query_one(StatusBar).show_message(
                    f"Opening {len(config.urls)} URLs..."
                )
        else:
            self.query_one(StatusBar).show_message("⚠ No project selected")
    
    def action_key_5(self) -> None:
        """Key 5: Show system health or run task 5."""
        if (
            state.current_view == "tasks"
            and state.task_list
            and len(state.task_list) >= 5
        ):
            self._run_task_by_index(4)
            self.query_one(StatusBar).show_message(
                f"Running task: {state.task_list[4]}"
            )
        else:
            health = get_system_health()
            state.system_health = health
            state.current_view = "system"
            self.query_one(Dashboard).show_system_view()
            self.query_one(HeaderBar).update_header()
            self.query_one(StatusBar).show_message("System health refreshed")
    
    def action_key_6(self) -> None:
        """Key 6: Create new project or run task 6."""
        if (
            state.current_view == "tasks"
            and state.task_list
            and len(state.task_list) >= 6
        ):
            self._run_task_by_index(5)
            self.query_one(StatusBar).show_message(
                f"Running task: {state.task_list[5]}"
            )
        else:
            self.push_screen(
                CreateProjectModal(),
                self.handle_project_creation,
            )

    def action_add_project(self) -> None:
        """Open modal to register an existing project from a path."""
        self.push_screen(AddProjectModal(), self.handle_add_project)

    def action_open_command_dialog(self) -> None:
        """Open the command selection dialog."""
        if not state.selected_project:
            self.query_one(StatusBar).show_message("⚠ No project selected")
            return
        self.push_screen(CommandDialog(), self._handle_command_choice)

    def action_refresh_commands(self) -> None:
        """Discover and persist the command catalog for the project."""
        if not state.selected_project:
            self.query_one(StatusBar).show_message("⚠ No project selected")
            return
        # Lazy import to keep startup light
        from backend.catalog import refresh_catalog

        self.query_one(StatusBar).show_message("🔎 Discovering commands...")
        result = refresh_catalog(state.selected_project)
        if result.get("success"):
            count = result.get("count", 0)
            self.query_one(StatusBar).show_message(
                f"✓ Catalog refreshed: {count} command(s)"
            )
        else:
            err = result.get("error", "Unknown error")
            self.query_one(StatusBar).show_message(f"✗ Refresh failed: {err}")

    def action_git_panel(self) -> None:
        """Open Git operations panel."""
        if not state.selected_project:
            self.query_one(StatusBar).show_message("⚠ No project selected")
            return
        self.push_screen(GitModal())

    def action_edit_memory(self) -> None:
        """Edit project memory context."""
        if not state.selected_project:
            self.query_one(StatusBar).show_message("⚠ No project selected")
            return
        
        # Get current memory values
        memory = state.project_memories.get(state.selected_project)
        if memory:
            working_on = memory.get_working_on()
            ticket = memory.get_linked_ticket()
        else:
            working_on = ""
            ticket = ""
        
        self.push_screen(
            EditMemoryModal(working_on, ticket),
            self.handle_memory_edit
        )

    def handle_memory_edit(self, result: tuple[str, str]) -> None:
        """Handle result from memory edit modal."""
        working_on, ticket = result
        
        if state.selected_project in state.project_memories:
            memory = state.project_memories[state.selected_project]
            memory.set_working_on(working_on)
            memory.set_linked_ticket(ticket)
            memory.add_action(f"Updated context: {working_on[:30]}")
            
            # Refresh dashboard to show new context
            self.query_one(Dashboard).refresh_dashboard()
            self.query_one(StatusBar).show_message("✓ Context updated")

    def action_open_env(self) -> None:
        """Open environment viewer modal."""
        if not state.selected_project:
            self.query_one(StatusBar).show_message("⚠ No project selected")
            return
        self.push_screen(EnvModal())
    
    def action_handle_escape(self) -> None:
        """Handle escape key - return to dashboard view."""
        if state.current_view != "dashboard":
            state.current_view = "dashboard"
            if state.selected_project:
                self.query_one(Dashboard).refresh_dashboard()
            else:
                content = self.query_one(Dashboard).query_one(
                    "#dashboard_content"
                )
                content.update("Select a project to view details")
            self.query_one(HeaderBar).update_header()
            self.query_one(StatusBar).show_message("Returned to dashboard")
    
    def handle_project_creation(self, result: dict) -> None:
        """Handle result from project creation modal."""
        if not result:
            return
        
        # Extract data
        template_id = result["template_id"]
        project_name = result["project_name"]
        description = result["description"]
        author = result["author"]
        license_val = result["license"]
        
        # Create project from template
        from backend.templates import get_template_manager
        import os
        
        template_manager = get_template_manager()
        parent_dir = os.path.join(os.path.expanduser("~"), "Dev", "Projects")
        project_path = os.path.join(parent_dir, project_name)
        
        variables = {
            "project_name": project_name,
            "description": description,
            "author": author,
            "license": license_val
        }
        
        self.query_one(StatusBar).show_message(
            "Creating project from template..."
        )
        
        creation_result = template_manager.create_project_from_template(
            template_id,
            project_path,
            variables
        )
        
        if creation_result["success"]:
            # Reload projects
            load_all_projects()
            project_list = self.query_one(ProjectList)
            project_list.refresh_list()
            
            # Show success message with AI context info
            ai_files = creation_result.get("ai_context_files", [])
            ai_files_list = "\n".join(
                [f"  • {os.path.basename(f)}" for f in ai_files]
            )
            
            dashboard = self.query_one(Dashboard)
            content = dashboard.query_one("#dashboard_content")
            msg = (
                f"✓ {creation_result['message']}\n\n"
                f"Path: {creation_result['path']}\n\n"
                f"Template: {template_id}\n\n"
            )
            if ai_files:
                msg += f"AI Context Files Generated:\n{ai_files_list}\n\n"
            msg += "Select the project from the sidebar to view details."
            content.update(msg)
            success_msg = "✓ Project created with AI context files!"
            self.query_one(StatusBar).show_message(success_msg)
        else:
            # Show error message
            dashboard = self.query_one(Dashboard)
            content = dashboard.query_one("#dashboard_content")
            error_msg = creation_result.get('error', 'Unknown error')
            content.update(f"✗ Error creating project:\n\n{error_msg}")
            self.query_one(StatusBar).show_message("✗ Creation failed")

    def handle_add_project(self, result: dict | None) -> None:
        """Handle result from AddProjectModal."""
        if not result:
            return

        path = result.get("path")
        name = result.get("name")
        self.query_one(StatusBar).show_message("Registering project...")

        reg = add_project_from_path(path, name)
        dashboard = self.query_one(Dashboard)
        content = dashboard.query_one("#dashboard_content")

        if reg.get("success"):
            # Reload list
            load_all_projects()
            self.query_one(ProjectList).refresh_list()
            state.selected_project = reg.get("key")
            state.current_view = "dashboard"
            dashboard.refresh_dashboard()
            self.query_one(HeaderBar).update_header()
            self.query_one(StatusBar).show_message("✓ Project added from path")
            content.update(
                f"✓ Added project '{reg.get('key')}' from:\n{path}\n\n"
                "Tip: press 3 to load tasks; 1 to start."
            )
        else:
            err = reg.get("error", "Unknown error")
            content.update(f"✗ Failed to add project:\n\n{err}")
            self.query_one(StatusBar).show_message("✗ Add failed")

    def _handle_command_choice(self, result: dict | None) -> None:
        """Run selected command from the dialog (Taskfile for now)."""
        if not result:
            return
        name = result.get("name")
        if not name:
            return
        # If command payload exists, use its invocation metadata
        cmd_payload = (
            result.get("command") if isinstance(result, dict) else None
        )
        if cmd_payload and isinstance(cmd_payload, dict):
            inv = cmd_payload.get("invocation") or {}
            adapter = inv.get("adapter")
            if adapter == "taskfile":
                task_name = inv.get("task_name") or name
                inv_cwd = inv.get("cwd")
                args = result.get("args") or []
                # Show tasks view for context
                tasks = load_tasks(state.selected_project)
                state.task_list = tasks
                state.current_view = "tasks"
                self.query_one(Dashboard).show_tasks_view()
                self.query_one(HeaderBar).update_header()
                self.query_one(StatusBar).show_message(
                    f"Running task: {task_name}"
                )
                execute_task(
                    state.selected_project,
                    task_name,
                    inv_cwd,
                    args,
                )
                return
            if adapter == "npm":
                from backend.executor import execute_npm_script

                script = inv.get("script_name") or name
                pm = inv.get("package_manager") or "npm"
                inv_cwd = inv.get("cwd")
                args = result.get("args") or []
                self.query_one(StatusBar).show_message(
                    f"Running {pm} script: {script}"
                )
                execute_npm_script(
                    state.selected_project, script, pm, inv_cwd, args
                )
                return
            # Future adapters: npm/pnpm, python, docker, etc.
            self.query_one(StatusBar).show_message(
                f"⚠ Unsupported adapter: {adapter or 'unknown'}"
            )
            return
        # Ensure tasks are loaded and show tasks view for context
        tasks = load_tasks(state.selected_project)
        state.task_list = tasks
        state.current_view = "tasks"
        self.query_one(Dashboard).show_tasks_view()
        self.query_one(HeaderBar).update_header()
        self.query_one(StatusBar).show_message(f"Running task: {name}")
        execute_task(state.selected_project, name)

    def _run_task_by_index(self, index: int) -> None:
        """Execute task by index."""
        if (
            state.selected_project
            and state.task_list
            and index < len(state.task_list)
        ):
            task_name = state.task_list[index]
            execute_task(state.selected_project, task_name)


def _ensure_cwd_onboarded_and_select() -> str | None:
    """Ensure current working dir is registered and selected.

    Returns the selected project key or None.
    """
    import os
    from backend.catalog import refresh_catalog

    # Load current registry
    load_all_projects()

    cwd = os.path.abspath(os.getcwd())

    def _is_path_under(base: str, path: str) -> bool:
        base_abs = os.path.abspath(base)
        path_abs = os.path.abspath(path)
        if path_abs == base_abs:
            return True
        base_norm = (
            base_abs if base_abs.endswith(os.sep) else base_abs + os.sep
        )
        return path_abs.startswith(base_norm)

    # Already covered?
    for key, (_wrapper, cfg) in state.projects.items():
        dev_dir = getattr(cfg, "dev_dir", None)
        if dev_dir and _is_path_under(dev_dir, cwd):
            return key

    # Register CWD
    reg = add_project_from_path(cwd, None)
    if not reg.get("success"):
        return None

    # Reload and discover
    load_all_projects()
    selected = reg.get("key")
    try:
        refresh_catalog(selected)
    except Exception:
        pass
    return selected


def main() -> None:
    """Console entry point for `mycli`.

    Spawns a new Windows Terminal session by default for full-screen UX.
    Use --in-place or env MYCLI_FORCE_IN_PLACE=1 to run in current shell.
    """
    import argparse
    import os
    import shutil
    import subprocess
    import sys

    parser = argparse.ArgumentParser(prog="mycli", add_help=True)
    parser.add_argument(
        "--in-place",
        action="store_true",
        help="Run TUI in current terminal (disable new window spawn)",
    )
    args, _ = parser.parse_known_args()

    # New window logic (only on Windows)
    force_in_place = os.environ.get("MYCLI_FORCE_IN_PLACE") == "1"
    if os.name == "nt" and not args.in_place and not force_in_place:
        # Avoid recursion: if already marked in-place, we skip spawning
        wt = shutil.which("wt.exe")
        # Build a PowerShell-friendly command that runs this Python
        cmdline = f'& "{sys.executable}" -m mycli --in-place'
        if wt:
            try:
                subprocess.Popen(
                    [
                        wt,
                        "-w",
                        "0",
                        "powershell",
                        "-NoExit",
                        "-Command",
                        cmdline,
                    ],
                    cwd=os.getcwd(),
                )
                return
            except Exception:
                pass
        # Fallback: open a new console via cmd start
        try:
            subprocess.Popen(
                [
                    "cmd",
                    "/c",
                    "start",
                    "mycli",
                    "powershell",
                    "-NoExit",
                    "-Command",
                    cmdline,
                ],
                cwd=os.getcwd(),
            )
            return
        except Exception:
            # If spawn fails, continue in-place
            pass

    selected = _ensure_cwd_onboarded_and_select()
    if selected:
        state.selected_project = selected

    # Merge .env defaults (shell overrides remain)
    try:
        if selected:
            from backend.env import merge_project_env
            wrapper, cfg = state.projects.get(selected, (None, None))
            dev_dir = getattr(cfg, "dev_dir", None)
            if dev_dir:
                merge_project_env(dev_dir)
    except Exception:
        # Non-fatal if env loading fails
        pass

    if os.environ.get("MYCLI_NO_UI") == "1":
        return

    app = MyCLIApp()
    app.run()


if __name__ == "__main__":
    main()
