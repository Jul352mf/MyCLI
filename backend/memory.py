"""Project memory system for context persistence."""
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime


class ProjectMemory:
    """Manages persistent memory for a project."""

    def __init__(self, project_path: str):
        """Initialize memory for a project."""
        self.project_path = Path(project_path)
        self.memory_file = self.project_path / "project.memory.json"
        self.data = self._load()

    def _load(self) -> Dict[str, Any]:
        """Load memory from file or create default."""
        if self.memory_file.exists():
            try:
                with open(self.memory_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return self._default_memory()
        return self._default_memory()

    def _default_memory(self) -> Dict[str, Any]:
        """Create default memory structure."""
        return {
            "working_on": "",
            "linked_ticket": "",
            "last_active": None,
            "recent_actions": [],
            "notes": [],
            "bookmarks": {},
            "time_spent_minutes": 0,
            "session_start": None,
        }

    def _save(self) -> None:
        """Save memory to file."""
        try:
            with open(self.memory_file, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Failed to save project memory: {e}")

    def get_working_on(self) -> str:
        """Get current task description."""
        return self.data.get("working_on", "")

    def set_working_on(self, task: str) -> None:
        """Set current task description."""
        self.data["working_on"] = task
        self._save()

    def get_linked_ticket(self) -> str:
        """Get linked ticket/issue ID."""
        return self.data.get("linked_ticket", "")

    def set_linked_ticket(self, ticket: str) -> None:
        """Set linked ticket/issue ID."""
        self.data["linked_ticket"] = ticket
        self._save()

    def update_last_active(self) -> None:
        """Update last active timestamp."""
        self.data["last_active"] = datetime.now().isoformat()
        self._save()

    def get_last_active(self) -> Optional[str]:
        """Get last active timestamp."""
        return self.data.get("last_active")

    def add_action(self, action: str) -> None:
        """Add an action to recent history."""
        timestamp = datetime.now().strftime("%H:%M")
        action_entry = {"time": timestamp, "action": action}
        
        # Keep only last 10 actions
        recent = self.data.get("recent_actions", [])
        recent.append(action_entry)
        self.data["recent_actions"] = recent[-10:]
        self._save()

    def get_recent_actions(self, limit: int = 5) -> List[Dict[str, str]]:
        """Get recent actions."""
        return self.data.get("recent_actions", [])[-limit:]

    def add_note(self, note: str) -> None:
        """Add a note."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        note_entry = {"time": timestamp, "note": note}
        
        notes = self.data.get("notes", [])
        notes.append(note_entry)
        self.data["notes"] = notes
        self._save()

    def get_notes(self) -> List[Dict[str, str]]:
        """Get all notes."""
        return self.data.get("notes", [])

    def clear_notes(self) -> None:
        """Clear all notes."""
        self.data["notes"] = []
        self._save()

    def set_bookmark(self, name: str, url: str) -> None:
        """Add or update a bookmark."""
        bookmarks = self.data.get("bookmarks", {})
        bookmarks[name] = url
        self.data["bookmarks"] = bookmarks
        self._save()

    def get_bookmarks(self) -> Dict[str, str]:
        """Get all bookmarks."""
        return self.data.get("bookmarks", {})

    def remove_bookmark(self, name: str) -> None:
        """Remove a bookmark."""
        bookmarks = self.data.get("bookmarks", {})
        if name in bookmarks:
            del bookmarks[name]
            self.data["bookmarks"] = bookmarks
            self._save()

    def start_session(self) -> None:
        """Mark session start for time tracking."""
        self.data["session_start"] = datetime.now().isoformat()
        self.update_last_active()

    def end_session(self) -> None:
        """Mark session end and update time spent."""
        if self.data.get("session_start"):
            start = datetime.fromisoformat(self.data["session_start"])
            duration = (datetime.now() - start).total_seconds() / 60
            
            total = self.data.get("time_spent_minutes", 0)
            self.data["time_spent_minutes"] = total + duration
            self.data["session_start"] = None
            self._save()

    def get_time_spent_formatted(self) -> str:
        """Get formatted time spent string."""
        minutes = self.data.get("time_spent_minutes", 0)
        hours = int(minutes // 60)
        mins = int(minutes % 60)
        
        if hours > 0:
            return f"{hours}h {mins}m"
        return f"{mins}m"

    def get_summary(self) -> Dict[str, Any]:
        """Get memory summary for display."""
        return {
            "working_on": self.get_working_on(),
            "linked_ticket": self.get_linked_ticket(),
            "last_active": self.get_last_active(),
            "recent_actions": self.get_recent_actions(3),
            "notes_count": len(self.get_notes()),
            "time_spent": self.get_time_spent_formatted(),
        }


def load_project_memory(project_path: str) -> ProjectMemory:
    """Load or create project memory."""
    return ProjectMemory(project_path)


def get_memory_for_selected() -> Optional[ProjectMemory]:
    """Get memory for currently selected project."""
    import state
    
    if not state.selected_project or state.selected_project not in state.projects:
        return None
    
    project_path, _ = state.projects[state.selected_project]
    return load_project_memory(project_path)
