"""Enhanced project creation modal with template selection."""
from textual.screen import ModalScreen
from textual.widgets import (
    Input,
    Button,
    Label,
    Static,
    ListView,
    ListItem,
    Select
)
from textual.containers import Container, Vertical, Horizontal
from textual.app import ComposeResult
from textual.binding import Binding

from backend.templates import get_template_manager


class CreateProjectModal(ModalScreen[dict]):
    """Modal dialog for creating new projects with template selection."""
    
    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]
    
    CSS = """
    CreateProjectModal {
        align: center middle;
    }
    
    #dialog {
        width: 80;
        height: 35;
        border: thick $primary;
        background: $surface;
    }
    
    #dialog_title {
        dock: top;
        height: 3;
        content-align: center middle;
        background: $primary;
        color: $text;
    }
    
    #dialog_content {
        padding: 1 2;
        height: auto;
    }
    
    .field_label {
        margin: 1 0 0 0;
    }
    
    Input, Select {
        margin: 0 0 1 0;
    }
    
    #template_list {
        height: 8;
        border: solid $primary-lighten-1;
        margin: 0 0 1 0;
    }
    
    #button_container {
        layout: horizontal;
        height: 3;
        align: center middle;
        margin: 1 0;
    }
    
    Button {
        margin: 0 1;
    }
    """
    
    def __init__(self):
        """Initialize modal."""
        super().__init__()
        self.template_manager = get_template_manager()
        self.selected_template_id = None
    
    def compose(self) -> ComposeResult:
        """Create modal widgets."""
        with Container(id="dialog"):
            yield Static("Create New Project", id="dialog_title")
            with Vertical(id="dialog_content"):
                # Template selection
                yield Static(
                    "Select Template:",
                    classes="field_label"
                )
                yield ListView(id="template_list")
                
                # Project details
                yield Static("Project Name:", classes="field_label")
                yield Input(
                    placeholder="my-awesome-project",
                    id="input_project_name"
                )
                
                yield Static("Description:", classes="field_label")
                yield Input(
                    placeholder="A brief description",
                    id="input_description"
                )
                
                yield Static("Author:", classes="field_label")
                yield Input(
                    placeholder="Your Name",
                    id="input_author"
                )
                
                yield Static("License (optional):", classes="field_label")
                yield Input(
                    placeholder="MIT",
                    id="input_license",
                    value="MIT"
                )
                
                with Horizontal(id="button_container"):
                    yield Button("Create", variant="primary", id="btn_create")
                    yield Button("Cancel", id="btn_cancel")
    
    def on_mount(self) -> None:
        """Populate template list on mount."""
        template_list = self.query_one("#template_list", ListView)
        
        for template_info in self.template_manager.list_templates():
            item = ListItem(
                Label(
                    f"{template_info['name']} "
                    f"[dim]({template_info['language']})[/dim]"
                )
            )
            item.metadata = template_info['id']
            template_list.append(item)
        
        # Select first template by default
        if len(template_list.children) > 0:
            template_list.index = 0
            self.selected_template_id = template_list.children[0].metadata
    
    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle template selection."""
        if event.item and hasattr(event.item, 'metadata'):
            self.selected_template_id = event.item.metadata
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks."""
        if event.button.id == "btn_cancel":
            self.dismiss(None)
        elif event.button.id == "btn_create":
            # Collect all form data
            project_name = self.query_one(
                "#input_project_name", Input
            ).value.strip()
            description = self.query_one(
                "#input_description", Input
            ).value.strip()
            author = self.query_one("#input_author", Input).value.strip()
            license_val = self.query_one(
                "#input_license", Input
            ).value.strip()
            
            # Validation
            if not project_name:
                self.query_one("#input_project_name", Input).placeholder = (
                    "⚠ Required!"
                )
                return
            
            if not description:
                self.query_one("#input_description", Input).placeholder = (
                    "⚠ Required!"
                )
                return
            
            if not author:
                self.query_one("#input_author", Input).placeholder = (
                    "⚠ Required!"
                )
                return
            
            if not self.selected_template_id:
                return
            
            # Return all data
            self.dismiss({
                "template_id": self.selected_template_id,
                "project_name": project_name,
                "description": description,
                "author": author,
                "license": license_val
            })
    
    def action_cancel(self) -> None:
        """Handle escape key."""
        self.dismiss(None)
