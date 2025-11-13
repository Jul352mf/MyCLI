✅ FINAL IMPLEMENTATION INSTRUCTIONS FOR CLAUDE

Claude — your role:
You are to translate these specifications directly into code.
You are not to design, decide, restructure, simplify, or reinterpret anything.
Your task is to mechanically implement the architecture described below.

Before writing any code:
You must confirm understanding of the instructions with a short acknowledgment.

1) Project Goal

Create a persistent full-screen Textual-based TUI application that serves as a project cockpit / development environment launcher and monitor.
The user interacts entirely via arrow keys, F-keys, and enter — meaning no commands must be remembered.

The TUI acts as a control panel for all development projects located in a specific directory on the local machine.

2) Technology Requirements

You must use the following without substitution:

Purpose	Library / Tool
TUI interface framework	Textual (latest version)
Config + Taskfile parsing	PyYAML
Process and system state inspection	psutil
Structured config schema	pydantic
Launching external processes	Python subprocess
OS:	Windows 11 environment (assume available: wt.exe, powershell.exe, brave.exe)

You may not replace these with alternatives.

3) Directory Structure (Mandatory)

You must generate exactly this structure:

mycli/
  app.py
  state.py
  styles.tcss
  components/
    project_list.py
    dashboard.py
    footer_bar.py
  backend/
    loader.py
    models.py
    executor.py
    tasks.py
    health.py


No file should be renamed.
No additional files should be created unless explicitly instructed later.

4) Project Discovery Logic

Projects exist under:

C:\Dev\Projects


A project is recognized only if it contains:

project.yaml

Load rule:

For each project folder:

key = folder_name
(project_dir_path, ProjectConfig instance)


This must populate:

state.projects: Dict[str, Tuple[str, ProjectConfig]]


Where ProjectConfig has the following fields:

Field	Type	Purpose
name	str	Human-readable display title
workspace	str	Path to VS Code .code-workspace
dev_dir	str	Directory where dev tasks execute
task_start	str	Primary dev task (string name)
apps	List[str]	List of applications to open when starting environment
urls	List[str]	Links to dashboards / monitoring / local frontends

Additionally, cloud metadata must be included:

vercel:
  project_slug: string
  team_id: optional string (nullable)
  token: null (placeholder; tokens will come from environment variables later)

supabase:
  api_url: string
  api_health_check: string (path used for HEAD/GET check)

railway:
  project_id: string (UUID)
  environment_id: string (UUID)
  token: null (placeholder; tokens come from environment variables later)


Claude is not to implement cloud calls yet.
These fields must simply be parsed and stored in the ProjectConfig model.

5) UI Layout

The TUI layout must consist of:

┌─────────────────────────────┬──────────────────────────────────────┐
│ Sidebar (Project List)      │ Main Panel (Dashboard / Views)       │
│ Fixed width ~34 chars       │ Expands to fill space                │
├─────────────────────────────┴──────────────────────────────────────┤
│ Footer (Keybind Help)                                             │
└───────────────────────────────────────────────────────────────────┘

Sidebar behavior:

Shows all discovered project keys.

Selecting a project updates global state.

Dashboard updates when selection changes.

Main Panel behavior:

Displays the project’s status summary by default.

Footer behavior:

Must show exactly:

F1 Start • F2 Stop • F3 Tasks • F4 Dashboards • F5 System • Q Quit

6) Key Bindings (Required)
Key	Function Name	Behavior
F1	start_env	Start environment
F2	stop_env	Stop environment
F3	open_tasks	Display tasks list in main panel
F4	open_urls	Open URLs in browser
F5	show_system_panel	Show system health snapshot
Q	quit	Exit TUI

Claude must bind these in App.BINDINGS.

7) Environment Start Logic (F1)

When starting a project environment:

Open VS Code with the project workspace.

Only if no code process is already running.

Start Docker Desktop.

Only if no docker-desktop-related process is running.

Start Notion.

Only if no Notion process is running.

Execute the project’s main task using Windows Terminal new tab:

wt.exe -w 0 nt -d <dev_dir> powershell -NoLogo -NoExit -Command task <task_start>


Open all project URLs:

If brave.exe exists and is not running → launch once with all URLs.

If brave.exe is already running → open URLs using webbrowser.open.

Idempotence Requirement

Multiple presses of F1 must not spawn duplicates.

Use psutil process matching by substring to detect running apps.

8) Environment Stop Logic (F2)

When stopping the environment:

If <dev_dir>/docker-compose.yml exists → run:

docker compose down


Do not close VS Code or Notion.

Do not kill unrelated processes.

After stopping, refresh dashboard.

9) Task List (F3)

Parse Taskfile.yml in the project directory.

Extract list of tasks (top-level task keys).

Display them in the main panel.

Assign numeric hotkeys:

"1" runs the first task
"2" runs the second
...
up to "9"


Running a task:

Opens a new Windows Terminal tab, same as main dev task.

10) Dashboards / External URLs (F4)

Opens all URLs listed in urls: config.

Same process rules as environment start.

11) System Panel (F5)

Displayed in main panel:

CPU % (psutil)

RAM % (psutil)

Count of listening ports (psutil)

Placeholder:

Docker containers: 0


No auto-refresh.
Refresh only occurs upon panel display or F5 re-press.

12) Cloud Integration (Locked, but deferred)

Cloud checks are not implemented yet.
Only metadata storage is implemented now.

Cloud priority order for future phases:

Vercel — preview and production deployment summaries.

Supabase — basic API reachability + latency.

Railway — service status & restart loops.

Claude must not attempt network calls or cloud fetches at this stage.

13) Styling Rules (Minimalist Swiss)

Dark neutral background.

Light neutral text.

No neon.

No gradients.

Only minimal borders.

Bold only for section headers.

14) Claude Instructions Before Coding

Before generating code, Claude must reply with:

I confirm I will not design or change anything. 
I will only translate the specification into code exactly as written.
I understand that no cloud calls are implemented in this phase.
I am ready to begin implementation.


Claude must wait for the message:

Begin implementation phase.


before writing any code.

✅ End of Instructions