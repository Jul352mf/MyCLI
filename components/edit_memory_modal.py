"""Modal for editing project memory context."""
from textual.screen import ModalScreen
from textual.containers import Container, Vertical
from textual.widgets import Static, Input, Button
from textual.binding import Binding


class EditMemoryModal(ModalScreen[tuple[str, str]]):
    """Modal for editing working on task and linked ticket."""

    CSS = """
    EditMemoryModal {
        align: center middle;
    }

    #memory_dialog {
        width: 60;
        height: 20;
        border: thick $primary;
        background: $surface;
    }

    #memory_title {
        dock: top;
        height: 3;
        content-align: center middle;
        background: $primary;
        color: $text;
    }

    #memory_form {
        padding: 1 2;
        height: auto;
    }

    .field_label {
        margin: 1 0 0 0;
    }

    Input {
        margin: 0 0 1 0;
    }

    #memory_buttons {
        layout: horizontal;
        height: 3;
        align: center middle;
        margin: 1 0;
    }

    Button {
        margin: 0 1;
    }
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel", priority=True),
    ]

    def __init__(self, working_on: str = "", linked_ticket: str = ""):
        """Initialize with current values."""
        super().__init__()
        self.working_on = working_on
        self.linked_ticket = linked_ticket

    def compose(self):
        """Create child widgets."""
        with Container(id="memory_dialog"):
            yield Static("Edit Project Context", id="memory_title")
            with Vertical(id="memory_form"):
                yield Static("Working On:", classes="field_label")
                yield Input(
                    value=self.working_on,
                    placeholder="What are you working on?",
                    id="input_working_on"
                )
                yield Static("Linked Ticket:", classes="field_label")
                yield Input(
                    value=self.linked_ticket,
                    placeholder="JIRA-123, #456, etc.",
                    id="input_ticket"
                )
                with Container(id="memory_buttons"):
                    yield Button("Save", variant="primary", id="btn_save")
                    yield Button("Cancel", id="btn_cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "btn_save":
            working_on_input = self.query_one(
                "#input_working_on", Input
            )
            ticket_input = self.query_one("#input_ticket", Input)
            self.dismiss((working_on_input.value, ticket_input.value))
        else:
            self.dismiss((self.working_on, self.linked_ticket))

    def action_cancel(self) -> None:
        """Cancel without saving."""
        self.dismiss((self.working_on, self.linked_ticket))
