"""System Quick Commands Modal.

Provides a tabbed interface for:
- Processes/Ports: List, filter, and kill processes
- ngrok: Start tunnels on ports
- Custom Quick Commands: CRUD interface for user-defined commands
"""
from textual.screen import ModalScreen
from textual.widgets import (
    TabbedContent,
    TabPane,
    DataTable,
    Input,
    Button,
    Label,
    Static,
    ListView,
    ListItem,
)
from textual.containers import Container, Vertical, Horizontal
from textual.app import ComposeResult
from textual.binding import Binding
from textual.reactive import reactive

from backend.system_commands import (
    get_all_processes,
    filter_processes,
    get_listening_ports,
    kill_process,
    is_ngrok_available,
    start_ngrok_tunnel,
    get_ngrok_tunnels,
)
from backend.quick_commands import (
    load_quick_commands,
    add_quick_command,
    remove_quick_command,
)
from backend.models import QuickCommand


class SystemQuickCommandsModal(ModalScreen[None]):
    """Modal for system-wide quick commands and utilities."""

    BINDINGS = [
        Binding("escape", "cancel", "Close"),
        Binding("r", "refresh", "Refresh", show=True),
    ]

    CSS = """
    SystemQuickCommandsModal {
        align: center middle;
    }
    
    #dialog {
        width: 95;
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
    
    #content {
        padding: 1 2;
        height: 100%;
    }
    
    TabbedContent {
        height: 100%;
    }
    
    TabPane {
        padding: 1;
    }
    
    #process_filter {
        margin: 0 0 1 0;
    }
    
    #process_table {
        height: 20;
        margin: 0 0 1 0;
    }
    
    #ngrok_status {
        margin: 0 0 1 0;
        padding: 1;
        background: $surface-darken-1;
        border: solid $primary-lighten-1;
    }
    
    #ngrok_port_input {
        width: 20;
        margin: 0 1 0 0;
    }
    
    #tunnels_list {
        height: 15;
        margin: 1 0;
        border: solid $primary-lighten-1;
    }
    
    #quick_commands_list {
        height: 18;
        margin: 0 0 1 0;
        border: solid $primary-lighten-1;
    }
    
    #quick_command_form {
        padding: 1;
        background: $surface-darken-1;
        border: solid $primary-lighten-1;
    }
    
    .form_row {
        layout: horizontal;
        height: 3;
        margin: 0 0 1 0;
    }
    
    .form_label {
        width: 15;
        padding: 0 1 0 0;
    }
    
    .form_input {
        width: 1fr;
    }
    
    Button {
        margin: 0 1 0 0;
    }
    
    #status_message {
        dock: bottom;
        height: 1;
        background: $surface-darken-2;
        padding: 0 1;
    }
    """

    filter_text: reactive[str] = reactive("")
    status_message: reactive[str] = reactive("")

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        with Container(id="dialog"):
            yield Static("System Quick Commands", id="dialog_title")
            with Vertical(id="content"):
                with TabbedContent():
                    with TabPane("Processes", id="processes_tab"):
                        yield Label("Filter by name or port:")
                        yield Input(
                            placeholder="Filter processes...",
                            id="process_filter",
                        )
                        yield DataTable(id="process_table")
                        with Horizontal():
                            yield Button(
                                "Kill Selected",
                                variant="error",
                                id="btn_kill_process",
                            )
                            yield Button("Refresh", id="btn_refresh_processes")

                    with TabPane("ngrok", id="ngrok_tab"):
                        yield Static("", id="ngrok_status")
                        yield Label("Start tunnel on port:")
                        with Horizontal():
                            yield Input(
                                placeholder="3000",
                                id="ngrok_port_input",
                                type="integer",
                            )
                            yield Button(
                                "Start Tunnel",
                                variant="primary",
                                id="btn_start_ngrok",
                            )
                        yield Label("Active tunnels:", classes="section_label")
                        yield ListView(id="tunnels_list")

                    with TabPane("Quick Commands", id="quick_commands_tab"):
                        yield Label("Your custom quick commands:")
                        yield ListView(id="quick_commands_list")
                        with Horizontal():
                            yield Button(
                                "Add New",
                                variant="primary",
                                id="btn_add_quick_command",
                            )
                            yield Button(
                                "Remove Selected",
                                variant="error",
                                id="btn_remove_quick_command",
                            )

            yield Static("", id="status_message")

    def on_mount(self) -> None:
        """Initialize the modal."""
        self._refresh_processes()
        self._refresh_ngrok_status()
        self._refresh_quick_commands()

    def _refresh_processes(self) -> None:
        """Refresh the process list."""
        table = self.query_one("#process_table", DataTable)
        table.clear(columns=True)

        # Add columns
        table.add_columns("PID", "Name", "CPU %", "Memory MB", "Status")

        # Get and filter processes
        all_processes = get_all_processes()
        filter_val = self.query_one("#process_filter", Input).value
        filtered = filter_processes(all_processes, name_filter=filter_val)

        # Add rows (limit to top 50 by CPU usage)
        filtered.sort(key=lambda p: p.cpu_percent, reverse=True)
        for proc in filtered[:50]:
            table.add_row(
                str(proc.pid),
                proc.name,
                f"{proc.cpu_percent:.1f}",
                f"{proc.memory_mb:.1f}",
                proc.status,
                key=str(proc.pid),
            )

        self._show_status(f"Showing {len(filtered[:50])} processes")

    def _refresh_ngrok_status(self) -> None:
        """Refresh ngrok availability status."""
        status_widget = self.query_one("#ngrok_status", Static)

        if is_ngrok_available():
            status_widget.update(
                "[green]✓[/green] ngrok is available and ready to use"
            )
        else:
            status_widget.update(
                "[red]✗[/red] ngrok not found in PATH. Please install ngrok to use this feature."
            )

        # Refresh active tunnels
        self._refresh_tunnels()

    def _refresh_tunnels(self) -> None:
        """Refresh the list of active ngrok tunnels."""
        listview = self.query_one("#tunnels_list", ListView)
        listview.clear()

        tunnels = get_ngrok_tunnels()

        if not tunnels:
            listview.append(ListItem(Label("[dim]No active tunnels[/dim]")))
        else:
            for tunnel in tunnels:
                url = tunnel.get("public_url", "Unknown")
                proto = tunnel.get("proto", "")
                config = tunnel.get("config", {})
                addr = config.get("addr", "")
                listview.append(
                    ListItem(Label(f"[cyan]{url}[/cyan] → {addr} ({proto})"))
                )

    def _refresh_quick_commands(self) -> None:
        """Refresh the quick commands list."""
        listview = self.query_one("#quick_commands_list", ListView)
        listview.clear()

        commands = load_quick_commands()

        if not commands:
            listview.append(ListItem(Label("[dim]No quick commands yet[/dim]")))
        else:
            for cmd in commands:
                scope_badge = (
                    "[blue]global[/blue]"
                    if cmd.scope == "global"
                    else "[yellow]project[/yellow]"
                )
                listview.append(
                    ListItem(
                        Label(
                            f"{scope_badge} [bold]{cmd.name}[/bold]: {cmd.command}"
                        ),
                        name=cmd.id,
                    )
                )

    def _show_status(self, message: str) -> None:
        """Show a status message."""
        self.status_message = message
        status = self.query_one("#status_message", Static)
        status.update(message)

    def action_cancel(self) -> None:
        """Close the modal."""
        self.dismiss()

    def action_refresh(self) -> None:
        """Refresh all tabs."""
        self._refresh_processes()
        self._refresh_ngrok_status()
        self._refresh_quick_commands()
        self._show_status("Refreshed")

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle input changes for filtering."""
        if event.input.id == "process_filter":
            self._refresh_processes()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id

        if button_id == "btn_kill_process":
            self._kill_selected_process()
        elif button_id == "btn_refresh_processes":
            self._refresh_processes()
        elif button_id == "btn_start_ngrok":
            self._start_ngrok_tunnel()
        elif button_id == "btn_add_quick_command":
            self._add_quick_command()
        elif button_id == "btn_remove_quick_command":
            self._remove_selected_quick_command()

    def _kill_selected_process(self) -> None:
        """Kill the currently selected process."""
        table = self.query_one("#process_table", DataTable)

        if table.cursor_row is None:
            self._show_status("⚠ No process selected")
            return

        # Get the PID from the selected row
        row_key = table.get_row_key_at(table.cursor_row)
        if row_key is None:
            return

        pid = int(str(row_key))

        # Confirm and kill
        success, message = kill_process(pid)

        if success:
            self._show_status(f"✓ {message}")
            self._refresh_processes()
        else:
            self._show_status(f"✗ {message}")

    def _start_ngrok_tunnel(self) -> None:
        """Start an ngrok tunnel."""
        port_input = self.query_one("#ngrok_port_input", Input)

        try:
            port = int(port_input.value or "3000")
        except ValueError:
            self._show_status("⚠ Invalid port number")
            return

        if not (1 <= port <= 65535):
            self._show_status("⚠ Port must be between 1 and 65535")
            return

        success, message, url = start_ngrok_tunnel(port)

        if success:
            self._show_status(f"✓ {message}")
            # Refresh tunnels after a short delay to allow ngrok to start
            self.set_timer(2.0, self._refresh_tunnels)
        else:
            self._show_status(f"✗ {message}")

    def _add_quick_command(self) -> None:
        """Open dialog to add a new quick command."""
        # For now, just show a placeholder message
        # In a full implementation, this would open a new modal
        self._show_status(
            "💡 Quick command creation dialog coming soon. Use the quick_commands.py API for now."
        )

    def _remove_selected_quick_command(self) -> None:
        """Remove the selected quick command."""
        listview = self.query_one("#quick_commands_list", ListView)

        if not listview.highlighted_child:
            self._show_status("⚠ No command selected")
            return

        # Get the command ID from the list item
        item = listview.highlighted_child
        if hasattr(item, "name") and item.name:
            success = remove_quick_command(item.name)
            if success:
                self._show_status("✓ Quick command removed")
                self._refresh_quick_commands()
            else:
                self._show_status("✗ Failed to remove command")
        else:
            self._show_status("⚠ No command selected")
