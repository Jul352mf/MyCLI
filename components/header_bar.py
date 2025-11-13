"""Header bar showing current context."""
from textual.widgets import Static
from textual.containers import Container
import state


class HeaderBar(Container):
    """Header showing current project and view."""
    
    def compose(self):
        """Create child widgets."""
        yield Static("MyCLI - Development Cockpit", id="header_text", classes="header")
    
    def update_header(self) -> None:
        """Update header with current context."""
        header = self.query_one("#header_text", Static)
        
        if not state.selected_project:
            header.update("MyCLI - Development Cockpit")
            return
        
        project_key = state.selected_project
        view_name = state.current_view.title()
        
        if project_key in state.projects:
            _, config = state.projects[project_key]
            header.update(f"[bold]{config.name}[/bold] • {view_name} View")
        else:
            header.update(f"MyCLI - {view_name} View")
