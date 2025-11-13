"""Modal dialog to add an existing project from a filesystem path."""
from textual.screen import ModalScreen
from textual.widgets import Input, Button, Label, Static
from textual.containers import Container, Vertical, Horizontal
from textual.app import ComposeResult
from textual.binding import Binding


class AddProjectModal(ModalScreen[dict]):
    """Simple modal to collect an existing path and optional name."""

    BINDINGS = [Binding("escape", "cancel", "Cancel")]

    CSS = """
    AddProjectModal { align: center middle; }
    #dialog { width: 80; height: 16; border: thick $primary; background: $surface; }
    #dialog_title { dock: top; height: 3; content-align: center middle; background: $primary; color: $text; }
    #dialog_content { padding: 1 2; height: auto; }
    Input { margin: 0 0 1 0; }
    #button_container { layout: horizontal; height: 3; align: center middle; margin: 1 0; }
    Button { margin: 0 1; }
    """

    def compose(self) -> ComposeResult:
        with Container(id="dialog"):
            yield Static("Add Existing Project", id="dialog_title")
            with Vertical(id="dialog_content"):
                yield Label("Project Path (absolute):")
                yield Input(placeholder=r"C:\\Dev\\Projects\\SomeRepo", id="input_path")
                yield Label("Display Name (optional):")
                yield Input(placeholder="Derived from folder name", id="input_name")
                with Horizontal(id="button_container"):
                    yield Button("Add", variant="primary", id="btn_add")
                    yield Button("Cancel", id="btn_cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_cancel":
            self.dismiss(None)
            return
        if event.button.id == "btn_add":
            path = self.query_one("#input_path", Input).value.strip()
            name = self.query_one("#input_name", Input).value.strip()
            if not path:
                self.query_one("#input_path", Input).placeholder = "⚠ Required"
                return
            self.dismiss({"path": path, "name": name or None})

    def action_cancel(self) -> None:
        self.dismiss(None)
