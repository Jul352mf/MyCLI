"""Git operations modal component."""
from textual.screen import ModalScreen
from textual.containers import Container, Vertical
from textual.widgets import Static, Button, ListView, ListItem, Label
from textual.binding import Binding

from backend.git_ops import (
    get_git_status,
    git_pull,
    git_push,
    git_init_and_commit,
)
import state


class GitModal(ModalScreen):
    """Modal for Git operations."""

    CSS = """
    GitModal {
        align: center middle;
    }

    #git_dialog {
        width: 80;
        height: 30;
        border: thick $primary;
        background: $surface;
    }

    #git_title {
        dock: top;
        height: 3;
        content-align: center middle;
        background: $primary;
        color: $text;
    }

    #git_status {
        height: 12;
        border: solid $primary-lighten-1;
        margin: 1 2;
        padding: 1;
    }

    #git_actions {
        height: 8;
        margin: 0 2 1 2;
    }

    .git_button {
        width: 100%;
        margin: 0 0 1 0;
    }
    """

    BINDINGS = [
        Binding("escape", "dismiss", "Close", priority=True),
        Binding("1", "git_status_action", "", show=False),
        Binding("2", "git_pull_action", "", show=False),
        Binding("3", "git_push_action", "", show=False),
        Binding("4", "git_add_action", "", show=False),
        Binding("5", "git_commit_action", "", show=False),
    ]

    def compose(self):
        """Create child widgets."""
        with Container(id="git_dialog"):
            yield Static("Git Operations", id="git_title")
            yield Static(id="git_status")
            with Vertical(id="git_actions"):
                yield Button("1) Git Status", classes="git_button", id="btn_status")
                yield Button("2) Git Pull", classes="git_button", id="btn_pull")
                yield Button("3) Git Push", classes="git_button", id="btn_push")
                yield Button("4) Git Add All", classes="git_button", id="btn_add")
                yield Button(
                    "5) Git Commit", classes="git_button", id="btn_commit"
                )

    def on_mount(self) -> None:
        """Refresh status on mount."""
        self.refresh_status()

    def refresh_status(self) -> None:
        """Refresh Git status display."""
        if not state.selected_project or state.selected_project not in state.projects:
            status_widget = self.query_one("#git_status", Static)
            status_widget.update("No project selected")
            return

        project_path, _ = state.projects[state.selected_project]
        status = get_git_status(project_path)

        if not status:
            status_widget = self.query_one("#git_status", Static)
            status_widget.update("Not a Git repository")
            return

        # Format status display
        lines = []
        if status.get("branch"):
            lines.append(f"🌿 Branch: [cyan]{status['branch']}[/cyan]")

        ahead = status.get("ahead", 0)
        behind = status.get("behind", 0)
        if ahead > 0:
            lines.append(f"↑ Ahead: [yellow]{ahead}[/yellow] commits")
        if behind > 0:
            lines.append(f"↓ Behind: [yellow]{behind}[/yellow] commits")

        uncommitted = status.get("uncommitted", 0)
        if uncommitted > 0:
            lines.append(
                f"~ Uncommitted: [red]{uncommitted}[/red] files"
            )
        else:
            lines.append("✓ No uncommitted changes")

        if status.get("last_commit"):
            lines.append(f"\n[dim]Last: {status['last_commit']}[/dim]")

        status_widget = self.query_one("#git_status", Static)
        status_widget.update("\n".join(lines))

    def action_git_status_action(self) -> None:
        """Refresh Git status."""
        self.refresh_status()
        self._show_feedback("Status refreshed")

    def action_git_pull_action(self) -> None:
        """Pull from remote."""
        if not state.selected_project:
            self._show_feedback("⚠ No project selected")
            return

        project_path, _ = state.projects[state.selected_project]
        success, message = git_pull(project_path)

        if success:
            self._show_feedback(f"✓ {message}")
            self.refresh_status()
        else:
            self._show_feedback(f"✗ {message}")

    def action_git_push_action(self) -> None:
        """Push to remote."""
        if not state.selected_project:
            self._show_feedback("⚠ No project selected")
            return

        project_path, _ = state.projects[state.selected_project]
        success, message = git_push(project_path)

        if success:
            self._show_feedback(f"✓ {message}")
            self.refresh_status()
        else:
            self._show_feedback(f"✗ {message}")

    def action_git_add_action(self) -> None:
        """Stage all changes."""
        if not state.selected_project:
            self._show_feedback("⚠ No project selected")
            return

        project_path, _ = state.projects[state.selected_project]
        # Just run git add .
        import subprocess

        try:
            subprocess.run(
                ["git", "add", "."],
                cwd=project_path,
                check=True,
                capture_output=True,
            )
            self._show_feedback("✓ All changes staged")
            self.refresh_status()
        except subprocess.CalledProcessError as e:
            self._show_feedback(f"✗ Error: {e.stderr.decode()}")

    def action_git_commit_action(self) -> None:
        """Commit staged changes (placeholder for now)."""
        self._show_feedback("ℹ Commit UI coming soon - use terminal for now")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id
        if button_id == "btn_status":
            self.action_git_status_action()
        elif button_id == "btn_pull":
            self.action_git_pull_action()
        elif button_id == "btn_push":
            self.action_git_push_action()
        elif button_id == "btn_add":
            self.action_git_add_action()
        elif button_id == "btn_commit":
            self.action_git_commit_action()

    def _show_feedback(self, message: str) -> None:
        """Show feedback in the app's status bar."""
        # Access the main app's status bar
        status_bar = self.app.query_one("StatusBar")
        status_bar.show_message(message)

    def action_dismiss(self) -> None:
        """Close the modal."""
        self.dismiss()
