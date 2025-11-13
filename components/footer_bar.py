"""Footer bar with keybind help."""
from textual.widgets import Static
from textual.containers import Container


class FooterBar(Container):
    """Footer showing available keybindings."""
    
    def compose(self):
        """Create child widgets."""
        yield Static(
                (
                    "1 Start • 2 Stop • 3 Tasks • 4 Dashboards • 5 System • "
                    "6 Create • A Add Path • R Run Cmd • F5 Refresh • ESC Back • Q Quit"
                ),
            id="footer_text",
        )
