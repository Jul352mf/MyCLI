"""Command selection dialog.

Prefers the persistent discovery catalog (backend.catalog). Falls back to
Taskfile tasks when no catalog is present.
"""
from textual.screen import ModalScreen
from textual.widgets import (
    Input,
    Button,
    Label,
    ListView,
    ListItem,
    Static,
    Checkbox,
)
from textual.containers import Container, Vertical, Horizontal
from textual.app import ComposeResult
from textual.binding import Binding

from backend.tasks import load_tasks
from backend.catalog import load_catalog
import state


class CommandDialog(ModalScreen[dict | None]):
    """Modal that lists available commands and lets user run one."""

    BINDINGS = [Binding("escape", "cancel", "Cancel")]

    CSS = """
    CommandDialog { align: center middle; }
                #dialog {
                    width: 90;
                    height: 28;
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
    #dialog_content { padding: 1 2; height: auto; }
    #filter { margin: 0 0 1 0; }
    #list { height: 16; border: solid $primary-lighten-1; }
    #params_title { margin: 1 0 0 0; }
    #params_area { height: 5; border: solid $surface-darken-2; padding: 0 1; }
                #button_row {
                    layout: horizontal;
                    height: 3;
                    align: center middle;
                    margin: 1 0;
                }
    Button { margin: 0 1; }
    """

    def __init__(self) -> None:
        super().__init__()
        self._all: list[str] = []  # display names
        self._filtered: list[str] = []
        # name -> command payload (when loaded from catalog)
        self._by_name: dict[str, dict] = {}

    def compose(self) -> ComposeResult:
        with Container(id="dialog"):
            yield Static("Run Command", id="dialog_title")
            with Vertical(id="dialog_content"):
                yield Label("Filter:")
                yield Input(placeholder="type to filter...", id="filter")
                yield ListView(id="list")
                yield Label("Parameters", id="params_title")
                yield Vertical(id="params_area")
                with Horizontal(id="button_row"):
                    yield Button("Run", variant="primary", id="btn_run")
                    yield Button("Cancel", id="btn_cancel")

    def on_mount(self) -> None:
        listview = self.query_one("#list", ListView)
        listview.clear()

        if not state.selected_project:
            listview.append(ListItem(Label("No project selected")))
            return

        # Source preference: discovery catalog, then Taskfile tasks
        catalog = load_catalog(state.selected_project)
        if catalog:
            # Build name list and mapping (dedupe by name by last-write wins)
            self._by_name = {
                c.get("name", ""): c for c in catalog if c.get("name")
            }
            self._all = sorted(self._by_name.keys())
        else:
            self._all = load_tasks(state.selected_project) or []
            self._by_name = {}
        self._filtered = list(self._all)
        for name in self._filtered:
            listview.append(ListItem(Label(name)))
        # Initialize params for first item (if any)
        if self._filtered:
            self._render_params(self._filtered[0])

    def _apply_filter(self) -> None:
        text = self.query_one("#filter", Input).value.strip().lower()
        listview = self.query_one("#list", ListView)
        listview.clear()
        if not text:
            self._filtered = list(self._all)
        else:
            self._filtered = [n for n in self._all if text in n.lower()]
        for name in self._filtered:
            listview.append(ListItem(Label(name)))

    def on_input_changed(self, event: Input.Changed) -> None:  # noqa: D401
        """Update results when filter changes."""
        if event.input.id == "filter":
            self._apply_filter()

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        listview = self.query_one("#list", ListView)
        if listview.index is None or not self._filtered:
            return
        idx = max(0, min(listview.index, len(self._filtered) - 1))
        name = self._filtered[idx]
        self._render_params(name)

    def _render_params(self, name: str) -> None:
        area = self.query_one("#params_area", Vertical)
        area.remove_children()
        payload = self._by_name.get(name)
        if not payload:
            area.mount(Label("(no parameters)"))
            return
        params = payload.get("parameters") or []
        if not params:
            area.mount(Label("(no parameters)"))
            return
        for p in params:
            pname = p.get("name")
            ptype = p.get("type")
            preq = bool(p.get("required"))
            pdef = p.get("default")
            label_text = f"{pname} ({ptype}{', required' if preq else ''})"
            area.mount(Label(label_text))
            wid = f"param_{pname}"
            if ptype == "boolean":
                cb = Checkbox(id=wid)
                try:
                    cb.value = bool(pdef)
                except Exception:
                    cb.value = False
                area.mount(cb)
            else:
                # string/enum/other types use Input for now
                ph = str(pdef) if pdef is not None else ""
                inp = Input(id=wid, placeholder=ph)
                area.mount(inp)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_cancel":
            self.dismiss(None)
            return
        if event.button.id == "btn_run":
            listview = self.query_one("#list", ListView)
            if listview.index is None or not self._filtered:
                return
            idx = max(0, min(listview.index, len(self._filtered) - 1))
            name = self._filtered[idx]
            payload: dict | None = self._by_name.get(name)
            result = {"name": name}
            if payload:
                result["command"] = payload
                # Collect parameter values and build CLI args
                args: list[str] = []
                params = payload.get("parameters") or []
                for p in params:
                    pname = p.get("name")
                    ptype = p.get("type")
                    meta = p.get("meta") or {}
                    wid = f"param_{pname}"
                    val: str | None = None
                    if ptype == "boolean":
                        try:
                            cb = self.query_one(f"#{wid}", Checkbox)
                            if cb.value:
                                flag = pname.replace("_", "-")
                                args.append(f"--{flag}")
                        except Exception:
                            pass
                    else:
                        try:
                            inp = self.query_one(f"#{wid}", Input)
                            val = inp.value.strip()
                        except Exception:
                            val = None
                        if val:
                            if meta.get("positional"):
                                args.append(val)
                            else:
                                key = pname.replace("_", "-")
                                args.append(f"--{key}={val}")
                if args:
                    result["args"] = args
            self.dismiss(result)

    def action_cancel(self) -> None:
        self.dismiss(None)
