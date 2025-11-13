"""Environment viewer modal (stub).

Shows effective environment (from shell + project .env) and a separate
section for .env file-only keys. No editing yet.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Dict

from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Static, Button, Label, ListView, ListItem
from textual.containers import Container, Horizontal

import state
from backend.env import parse_env_file


class EnvModal(ModalScreen[None]):
    BINDINGS = [
        ("escape", "close", "",),
    ]

    CSS = """
    EnvModal {
        align: center middle;
    }
    #wrap {
        width: 100;
        height: 34;
        border: thick $primary;
        background: $surface;
    }
    #title {
        dock: top;
        height: 3;
        content-align: center middle;
        background: $primary;
        color: $text;
    }
    #content {
        padding: 1 2;
        height: auto;
    }
    #cols {
        height: 26;
    }
    #col_left, #col_right {
        width: 1fr;
        border: solid $surface-darken-2;
    }
    #buttons {
        height: 3;
        align: center middle;
    }
    """

    def compose(self) -> ComposeResult:
        yield Container(
            Static("Environment", id="title"),
            Container(
                Label("Effective (shell + .env):"),
                ListView(id="effective"),
                Label(".env only:"),
                ListView(id="file_only"),
                id="content",
            ),
            Container(
                Horizontal(
                    Button("Close", id="btn_close"),
                ),
                id="buttons",
            ),
            id="wrap",
        )

    def on_mount(self) -> None:
        eff = self.query_one("#effective", ListView)
        fil = self.query_one("#file_only", ListView)
        eff.clear()
        fil.clear()

        dev_dir = None
        if state.selected_project and state.selected_project in state.projects:
            _, cfg = state.projects[state.selected_project]
            dev_dir = getattr(cfg, "dev_dir", None)
        file_env: Dict[str, str] = {}
        if dev_dir:
            env_path = Path(dev_dir) / ".env"
            if env_path.exists():
                file_env = parse_env_file(env_path)

        # Effective environment
        for k in sorted(os.environ.keys()):
            v = os.environ.get(k, "")
            eff.append(ListItem(Static(f"{k}={v}")))

        # File-only (keys present in .env but not set in current shell)
        for k in sorted(file_env.keys()):
            if k not in os.environ:
                v = file_env[k]
                fil.append(ListItem(Static(f"{k}={v}")))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_close":
            self.dismiss(None)
    
    def action_close(self) -> None:
        """Close the modal on Escape."""
        self.dismiss(None)
