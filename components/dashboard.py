"""Main panel dashboard component."""
from textual.widgets import Static
from textual.containers import Container
from backend.executor import is_process_running
from backend.git_ops import get_git_status
import os
import state


class Dashboard(Container):
    """Main panel showing project status and views."""
    
    def compose(self):
        """Create child widgets."""
        yield Static(
            "Select a project to view details",
            id="dashboard_content",
        )
    
    def refresh_dashboard(self) -> None:
        """Update dashboard with current project info."""
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
        lines.append("\n[dim]1:Start 2:Stop 3:Tasks 4:URLs 5:System[/dim]")
        
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
        
        lines.append("\n[dim]Press ESC to return • 5 to refresh[/dim]")
        
        content.update("\n".join(lines))
