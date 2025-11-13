# mycli v2 – Session Handover (2025-11-13)

This document captures the current state of the `mycli` project so a new chat/session can resume work without losing momentum.

---
## 1. Project Scope (v2 Focus)
Core goals for v2 as implemented so far:
- Repository autodiscovery yielding normalized `CommandDefinition` models.
- Persistent per-project command catalog used by the TUI command dialog.
- Interactive TUI onboarding: add existing project path, view dashboard, run tasks/commands.
- Execution adapters (initially Taskfile tasks, now extended with npm/pnpm scripts).
- X-ray / repo stats groundwork (metrics model in place; scanner previously implemented).

Upcoming (not yet implemented):
- Parameter input UI rendering `ParameterDefinition` forms.
- Additional execution adapters (Python module, PowerShell script, Docker, LangGraph agent triggers).
- Rich discovery: parameter/flag extraction from command strings.
- Catalog storage upgrade (SQLite option, incremental refresh, background indexing).
- Model enrichment (confidence heuristics, tagging, runtime estimation).

---
## 2. Completed Work Summary
| Area | Status | Key Files |
|------|--------|-----------|
| Core models (Pydantic v2) | DONE | `backend/models.py` |
| Stable ID hashing utility | DONE | `backend/models.py` (`stable_command_id`) |
| Discovery engine pipeline | DONE | `backend/discovery/engine.py` + plugins |
| Taskfile discovery plugin | DONE | `backend/discovery/plugins/taskfile.py` |
| NPM scripts discovery plugin | DONE (added this session) | `backend/discovery/plugins/npm_scripts.py` |
| Normalization logic | DONE (extended for npm) | `backend/discovery/normalization.py` |
| Confidence filtering scaffold | DONE | `backend/discovery/confidence.py` |
| Persistent catalog (JSON) | DONE | `backend/catalog.py` |
| Command selection dialog (TUI) | DONE | `components/command_dialog.py` |
| F5 catalog refresh action | DONE | `app.py` (action_refresh_commands) |
| NPM/Pnpm execution adapter | DONE (basic) | `backend/executor.py`, invocation path in `app.py` |
| Taskfile task execution (Windows Terminal) | DONE | `backend/tasks.py`, `backend/executor.py` |
| Project onboarding (Add Path modal) | DONE | `components/add_project_modal.py`, `backend/projects.py` |
| Project creation from templates | DONE | `components/create_modal.py`, `backend/templates.py` |
| Dashboard / status bars | DONE | multiple components under `components/` |

---
## 3. Key Architectural Concepts
- **Discovery Pipeline**: Plugins emit `RawArtifact` → filtered by confidence → global normalization → `CommandDefinition` (with adapter metadata in `invocation`).
- **Adapters**: Selected via `invocation['adapter']`. Currently supported:
  - `taskfile`: executes a Taskfile task via Windows Terminal.
  - `npm`: executes `npm run <script>` or `pnpm run <script>` based on detected manager.
- **Persistent Catalog**: One JSON file per project wrapper (`command_catalog.json`) storing a list of serialized `CommandDefinition` objects. Preferred source for the command dialog.
- **Stable Command IDs**: Hash of origin + source path + name (first 16 hex chars) to support future diffing, persistence, and enrichment updates.
- **Extensibility**: `parameters` currently empty; reserved for future extraction & UI generation.

---
## 4. Execution Flow
1. User selects project in sidebar (state: `state.selected_project`).
2. Press F5 (or run refresh) → `refresh_catalog()` triggers discovery engine with both Taskfile + npm plugins.
3. `DiscoveryEngine.run()` collects artifacts → normalizes to `CommandDefinition` list with invocation data.
4. Catalog stored at `<wrapper>/command_catalog.json`.
5. Command dialog (`Run Cmd`) loads catalog; user filters/selects.
6. `app._handle_command_choice()` inspects `invocation.adapter` and dispatches:
   - `taskfile` → executes via `execute_task()`.
   - `npm` → executes via `execute_npm_script()`.
7. Terminal tab opens and runs command, keeping session open (-NoExit).

---
## 5. How to Run (Windows PowerShell)
```powershell
# Launch TUI
python .\app.py

# Refresh command catalog (inside TUI)
# Press F5

# Run a command
# Press 'r' then select a command and press Run.

# Start environment for selected project
# Press '1'

# Stop environment
# Press '2'
```
Prerequisites:
- Python 3.12 venv active (current environment appears shared; consider creating a dedicated venv for `mycli`).
- `task` binary available if using Taskfile tasks.
- Node + npm/pnpm installed for package scripts.

---
## 6. Recently Added (This Session)
- Added `NpmScriptsPlugin` for package.json script discovery.
- Extended normalization to produce `invocation` metadata for npm/pnpm scripts.
- Updated catalog discovery to include both Taskfile and npm plugins.
- Implemented `execute_npm_script()` in `backend/executor.py`.
- Wired npm adapter path in `app._handle_command_choice()`.

---
## 7. Pending / Next Steps (Prioritized)
1. Parameter UI: Render interactive forms from `parameters` (define extraction heuristics first).
2. Parameter Extraction: Enhance normalization to parse flags (e.g. `--foo`, `<path>` tokens) and populate `ParameterDefinition`.
3. Additional Adapters:
   - Python: `python -m module` or script execution.
   - Docker: build/run commands for detected Dockerfiles.
   - PowerShell: `.ps1` script execution with argument mapping.
4. Incremental Discovery Refresh: Track file mtimes; only rescan changed files; store last scan metadata.
5. Catalog Enhancements: Add `version`, `generated_at`, adapter statistics; optional SQLite backend.
6. RepoStats Integration: Display X-ray metrics on dashboard (visual histograms, health index).
7. Testing Coverage: Add unit tests for npm plugin, executor script path, dialog fallback logic.
8. Error & Logging Strategy: Introduce structured logging (JSON lines) and a simple log viewer modal.
9. Security & Safety: Sandbox command execution (policy to restrict commands) and environment variable overrides.
10. Performance: Parallelize plugin scanning; add configurable confidence thresholds per origin.

---
## 8. Known Issues / Risks
- Shared venv path referencing external project (`JAGI_v21`) may cause dependency drift; create isolated venv under `mycli`.
- No parameter extraction yet limits interactive UX beyond selection.
- Discovery is full rescan each refresh; can become slow on very large repos.
- Execution assumes Windows environment (`wt.exe`); need cross-platform abstraction.
- Lack of telemetry/tracing makes profiling discovery pipeline harder.

---
## 9. Suggested Sprint Plan
| Sprint Item | Goal | Acceptance Criteria |
|-------------|------|---------------------|
| Parameter Extraction v1 | Populate `parameters` for Taskfile + npm commands | 60%+ commands show ≥1 parameter in dialog |
| Parameter Form Component | Collect & pass parameter values to execution | Form opens after selection; values injected into command line |
| Python Adapter | Run Python scripts/modules | Selecting a python command executes successfully and stays open |
| Incremental Refresh | Speed up discovery on large repos | Refresh time reduced ≥50% on >1000 file repo |
| RepoStats Dashboard | Visualize health metrics | Dashboard shows health index + top languages + largest files |
| Plugin Testing | Stabilize discovery | Tests cover Taskfile + npm plugin normal and error paths |

---
## 10. Technical Decisions Log (Recent)
- Chose truncated SHA256 (16 hex) as stable command ID for local uniqueness & portability.
- Stored catalog as JSON for simplicity before migrating to SQLite.
- Chose adapter key inside `invocation` to decouple discovery from execution layer.
- Implemented npm package manager detection via `packageManager` field or lockfile presence.

---
## 11. File Reference Index
- Models: `backend/models.py`
- Discovery Engine: `backend/discovery/engine.py`
- Confidence Filter: `backend/discovery/confidence.py`
- Normalization: `backend/discovery/normalization.py`
- Plugins: `backend/discovery/plugins/taskfile.py`, `backend/discovery/plugins/npm_scripts.py`
- Catalog: `backend/catalog.py`
- Executor: `backend/executor.py` (includes `execute_npm_script`)
- Task Parsing/Execution: `backend/tasks.py`
- TUI App: `app.py`
- Command Dialog: `components/command_dialog.py`
- Project Modals: `components/add_project_modal.py`, `components/create_modal.py`

---
## 12. Quick Start for New Session
```powershell
# (Optional) create dedicated venv
python -m venv .venv
./.venv/Scripts/Activate.ps1
pip install -r requirements.txt

# Run TUI
python .\app.py

# Add existing project path (press 'a') then F5 to discover commands.
# Open command dialog (press 'r') and run a Taskfile or npm script.
```

---
## 13. Immediate Next Action Recommendation
Implement parameter extraction for Taskfile commands (parse `cmd` strings for `--flag` and `<arg>` patterns), populate `parameters`, and create a simple parameter modal before executing.

---
## 14. Handshake Checklist
- [x] Core discovery & catalog implemented.
- [x] Two adapters (Taskfile, npm) working.
- [ ] Parameter UI pending.
- [ ] Incremental refresh pending.
- [ ] Repository health visualization pending.

> Continue from section 7 (Pending / Next Steps) in the next session.
