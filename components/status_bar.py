"""Status notification widget."""
from textual.widgets import Static
from textual.containers import Container
from textual.reactive import reactive


class StatusBar(Container):
    """Status bar showing action feedback."""
    
    message: reactive[str] = reactive("")
    
    def compose(self):
        """Create child widgets."""
        yield Static("", id="status_message")
    
    def watch_message(self, new_message: str) -> None:
        """Update status message."""
        status = self.query_one("#status_message", Static)
        if new_message:
            status.update(f"[dim]ℹ[/dim] {new_message}")
        else:
            status.update("")
    
    def show_message(self, message: str) -> None:
        """Show a status message."""
        self.message = message
        
        # Auto-clear after a delay
        self.set_timer(3, self.clear_message)
    
    def clear_message(self) -> None:
        """Clear the status message."""
        self.message = ""
