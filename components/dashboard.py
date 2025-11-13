"""Main panel dashboard component."""
from textual.widgets import Static, TabbedContent, TabPane, Button, Input, Label, ListView, ListItem
from textual.containers import Container, Vertical, Horizontal
from textual.app import ComposeResult
from backend.executor import is_process_running
from backend.git_ops import get_git_status
from backend.models import ProjectConfig
import os
import state


class Dashboard(Container):
    """Main panel showing project status and views with tabbed interface."""
    
    def compose(self) -> ComposeResult:
        """Create child widgets."""
        with TabbedContent(id="dashboard_tabs"):
            with TabPane("Overview", id="overview_tab"):
                yield Static(
                    "Select a project to view details",
                    id="dashboard_content",
                )
            
            with TabPane("Workspace", id="workspace_tab"):
                yield Static("", id="workspace_content")
            
            with TabPane("Command Center", id="command_center_tab"):
                yield Static("", id="command_center_content")
            
            with TabPane("X-Ray", id="xray_tab"):
                yield Static("", id="xray_content")
    
    def refresh_dashboard(self) -> None:
        """Update dashboard with current project info."""
        # Update all tabs
        self._refresh_overview()
        self._refresh_workspace()
        self._refresh_command_center()
        self._refresh_xray()
    
    def _refresh_overview(self) -> None:
        """Update the overview tab (original dashboard content)."""
        content = self.query_one("#dashboard_content", Static)
        
        if not state.selected_project:
            content.update("Select a project to view details")
            return
        
        project_key = state.selected_project
        if project_key not in state.projects:
            content.update("Project not found")
            return
        
        project_dir, project_config = state.projects[project_key]
        
        # Check running status
        vscode_running = is_process_running("code")
        docker_running = is_process_running("docker")
        notion_running = is_process_running("notion")
        
        # Get Git info
        git_info = get_git_status(project_dir)
        
        # Build status summary with indicators
        lines = []
        lines.append(f"[bold white]{project_config.name}[/bold white]")
        
        # Project memory context (if available)
        if project_key in state.project_memories:
            memory = state.project_memories[project_key]
            summary = memory.get_summary()
            
            if summary["working_on"]:
                lines.append(
                    f"📝 [cyan]Working on:[/cyan] {summary['working_on']}"
                )
            if summary["linked_ticket"]:
                lines.append(
                    f"🎫 [yellow]Ticket:[/yellow] {summary['linked_ticket']}"
                )
            if summary["time_spent"] != "0m":
                lines.append(
                    f"⏱️  [dim]Time spent: {summary['time_spent']}[/dim]"
                )
            lines.append("")  # Blank line
        
        # Git info line
        if git_info:
            branch_emoji = "🌿"
            ahead_behind = ""
            if git_info["ahead"] > 0 or git_info["behind"] > 0:
                ahead_str = f"↑{git_info['ahead']} ↓{git_info['behind']}"
                ahead_behind = f" [yellow]{ahead_str}[/yellow]"
            uncommitted_str = f" [red]~{git_info['uncommitted_count']}[/red]"
            uncommitted = (
                uncommitted_str if git_info["uncommitted_count"] > 0 else ""
            )
            lines.append(
                f"{branch_emoji} [cyan]{git_info['branch']}[/cyan]"
                f"{ahead_behind}{uncommitted}\n"
            )
            
            if git_info["last_commit_msg"]:
                commit_msg = git_info['last_commit_msg'][:50]
                commit_time = git_info['last_commit_time']
                lines.append(
                    f"[dim]Last: {commit_msg} ({commit_time})[/dim]\n"
                )
        else:
            lines.append("[dim]No git repository[/dim]\n")
        
        # Status section
        lines.append("[bold]Status:[/bold]")
        status_icon_on = "[green]●[/green]"
        status_icon_off = "[dim]○[/dim]"
        
        vs_str = (
            f"  {status_icon_on if vscode_running else status_icon_off} VS Code"
        )
        dock_str = (
            f"  {status_icon_on if docker_running else status_icon_off} Docker"
        )
        notion_str = (
            f"  {status_icon_on if notion_running else status_icon_off} Notion"
        )
        lines.append(vs_str)
        lines.append(dock_str)
        lines.append(notion_str)
        
        # Configuration section
        lines.append("\n[bold]Configuration:[/bold]")
        lines.append(f"  📁 {project_dir}")
        lines.append(f"  🚀 Main Task: {project_config.task_start}")
        lines.append(f"  🔗 URLs: {len(project_config.urls)}")
        lines.append(f"  📦 Apps: {len(project_config.apps)}")

        # Python environment badge (uv detection)
        try:
            dev_dir = getattr(project_config, "dev_dir", None)
            if dev_dir:
                uv_lock = os.path.join(dev_dir, "uv.lock")
                if os.path.exists(uv_lock):
                    lines.append("  🐍 Env: [green]uv-managed[/green]")
        except Exception:
            pass
        
        # Cloud providers section
        cloud_providers = []
        if project_config.vercel:
            cloud_providers.append(
                f"[cyan]Vercel[/cyan] ({project_config.vercel.project_slug})"
            )
        if project_config.supabase:
            cloud_providers.append("[green]Supabase[/green]")
        if project_config.railway:
            cloud_providers.append("[magenta]Railway[/magenta]")
        
        if cloud_providers:
            lines.append("\n[bold]Cloud Providers:[/bold]")
            for provider in cloud_providers:
                lines.append(f"  ☁️  {provider}")
        
        # Quick actions hint
        lines.append("\n[dim]1:Start 2:Stop r:Run Cmd s:Quick Cmds[/dim]")
        
        content.update("\n".join(lines))
    
    def _refresh_workspace(self) -> None:
        """Update the Workspace tab with URLs and start/stop mappings."""
        content = self.query_one("#workspace_content", Static)
        
        if not state.selected_project:
            content.update("Select a project to view workspace")
            return
        
        project_key = state.selected_project
        if project_key not in state.projects:
            content.update("Project not found")
            return
        
        project_dir, project_config = state.projects[project_key]
        
        lines = []
        lines.append(f"[bold white]Workspace: {project_config.name}[/bold white]\n")
        
        # URLs section
        lines.append("[bold]URLs:[/bold]")
        if project_config.urls:
            for i, url in enumerate(project_config.urls, 1):
                lines.append(f"  {i}. [cyan]{url}[/cyan]")
        else:
            lines.append("  [dim]No URLs configured[/dim]")
        
        lines.append("")
        
        # Start/Stop commands
        lines.append("[bold]Start/Stop Commands:[/bold]")
        lines.append(f"  Start: [green]{project_config.task_start}[/green]")
        lines.append(f"  Stop: [yellow]<not configured>[/yellow]")
        
        lines.append("")
        
        # Quick actions
        lines.append("[bold]Quick Actions:[/bold]")
        lines.append("  • Press [cyan]4[/cyan] to open all URLs")
        lines.append("  • Press [cyan]1[/cyan] to start environment")
        lines.append("  • Press [cyan]2[/cyan] to stop environment")
        
        lines.append("\n[dim]URL and command mapping management coming soon[/dim]")
        
        content.update("\n".join(lines))
    
    def _refresh_command_center(self) -> None:
        """Update the Command Center tab."""
        content = self.query_one("#command_center_content", Static)
        
        if not state.selected_project:
            content.update("Select a project to view commands")
            return
        
        lines = []
        lines.append("[bold white]Command Center[/bold white]\n")
        lines.append("Discovered commands with scope filtering\n")
        lines.append("[dim]Press [cyan]r[/cyan] to open Command Dialog[/dim]")
        lines.append("[dim]Press [cyan]F5[/cyan] to refresh command catalog[/dim]")
        
        content.update("\n".join(lines))
    
    def _refresh_xray(self) -> None:
        """Update the X-Ray tab."""
        content = self.query_one("#xray_content", Static)
        
        if not state.selected_project:
            content.update("Select a project to view X-Ray")
            return
        
        lines = []
        lines.append("[bold white]X-Ray: Repository Analysis[/bold white]\n")
        lines.append("Repository health metrics and insights\n")
        lines.append("[dim]Detailed X-Ray view coming soon[/dim]")
        
        content.update("\n".join(lines))
    
    def show_tasks_view(self) -> None:
        """Display tasks list with numeric hotkeys."""
        content = self.query_one("#dashboard_content", Static)
        
        if not state.task_list:
            content.update("No tasks found in Taskfile.yml")
            return
        
        lines = ["[bold white]Available Tasks[/bold white]\n"]
        
        for i, task_name in enumerate(state.task_list[:6], 1):
            lines.append(f"  [cyan]{i}[/cyan]  {task_name}")
        
        if len(state.task_list) > 6:
            remaining = len(state.task_list) - 6
            plural = "s" if remaining > 1 else ""
            lines.append(
                f"\n[dim]... and {remaining} more task{plural}[/dim]"
            )
        
        lines.append("\n[dim]Press 1-6 to run task • ESC to return[/dim]")
        
        content.update("\n".join(lines))
    
    def show_system_view(self) -> None:
        """Display system health snapshot."""
        content = self.query_one("#dashboard_content", Static)
        
        health = state.system_health
        
        cpu = health.get('cpu_percent', 0)
        ram = health.get('ram_percent', 0)
        ports = health.get('listening_ports', 0)
        
        # Color code based on usage
        cpu_color = "red" if cpu > 80 else "yellow" if cpu > 60 else "green"
        ram_color = "red" if ram > 80 else "yellow" if ram > 60 else "green"
        
        lines = ["[bold white]System Health[/bold white]\n"]
        lines.append(f"[{cpu_color}]● CPU:[/{cpu_color}] {cpu:.1f}%")
        lines.append(f"[{ram_color}]● RAM:[/{ram_color}] {ram:.1f}%")
        lines.append(f"[cyan]● Ports:[/cyan] {ports} listening")
        lines.append("[dim]● Docker:[/dim] 0 containers")
        
        lines.append("\n[dim]Press ESC to return • s for Quick Cmds[/dim]")
        
        content.update("\n".join(lines))

