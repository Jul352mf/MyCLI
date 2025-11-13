"""Sidebar project list component."""
from textual.widgets import ListView, ListItem, Label
from textual.containers import Container
import state
from backend.memory import load_project_memory


class ProjectList(Container):
    """Sidebar showing all discovered projects."""
    
    def compose(self):
        """Create child widgets."""
        yield Label("Projects", classes="header")
        yield ListView(id="project_listview")
    
    def refresh_list(self) -> None:
        """Populate list with discovered projects."""
        listview = self.query_one("#project_listview", ListView)
        listview.clear()
        
        for project_key in sorted(state.projects.keys()):
            listview.append(ListItem(Label(project_key)))
    
    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle project selection."""
        if event.item:
            label = event.item.query_one(Label)
            # Get the text content from the label
            if hasattr(label, 'renderable'):
                project_key = str(label.renderable)
            else:
                project_key = str(label.render())
            
            state.selected_project = project_key
            state.current_view = "dashboard"
            
            # Load project memory and start session
            if project_key in state.projects:
                project_path, _ = state.projects[project_key]
                memory = load_project_memory(project_path)
                memory.start_session()
                state.project_memories[project_key] = memory
            
            # Refresh dashboard and header
            dashboard = self.app.query_one("Dashboard")
            dashboard.refresh_dashboard()
            
            header = self.app.query_one("HeaderBar")
            header.update_header()
