# mycli v2 Product Requirements Document (PRD)

## 1. Summary
Version 2 of `mycli` evolves the MVP Textual TUI into a developer productivity cockpit for heterogeneous polyglot repos (initial target: JAGI monorepo). Core pillars:
- Project autodiscovery (add a directory → automatic harvesting of runnable tasks, scripts, agent graphs, Docker targets, health metrics).
- Unified command registry with typed/ranged parameters and interactive dialogs.
- Extensible parsing engine (plugin architecture) + opinionated template annotations to increase structured extraction quality over time.
- "X-ray" repository intelligence module (fast structural + statistical scan: files, lines, languages, tree, health index).
- Foundation for v3 (LLM-assisted enrichment, environment provisioning, debugging) via normalized artifact schema.

## 2. Objectives
1. Discover and surface actionable development commands within seconds after adding a project.
2. Provide structured parameter schemas enabling guided execution (validation, defaults, ranges, enums).
3. Offer rich repo insight (X-ray) under 2 seconds for medium repo (~5k files) and < 10s for large repos (~50k files) on typical dev laptop.
4. Minimize manual configuration: templates are optional accelerators, autodiscovery must work with existing JAGI files.
5. Prepare internal APIs (artifacts/models) to be ingestible by LLM augmentation in v3.

## 3. Scope (In)
- Textual UI enhancements (Project List, Dashboard, Command Palette, Command Detail Dialog, X-ray View, Health Bar/Footer).
- Parsers for: Taskfile.yml, package.json scripts, pnpm workspace, pyproject.toml, requirements.txt, setup.cfg, Makefile, shell (.sh), PowerShell (.ps1), Dockerfile & docker-compose, LangGraph config (langgraph.json), Python agent graph modules, Node tool scripts, Markdown command templates with front matter, custom template files in `templates/`.
- Parameter extraction heuristics (comments, docstrings, decorators, structured blocks).
- Template specification & examples (authoring guidelines) for future adoption.
- Repo X-ray statistics + rendering (Rich in plain CLI mode and Textual view inside TUI).
- Health metrics (CPU, RAM, open ports relevant to project processes) for dashboard.

## 4. Non-Goals (v2)
- LLM autonomous command synthesis.
- Remote orchestration (multi-host cluster management).
- Secure secret management / vault integration.
- Deployment pipelines or CI integration beyond listing commands.
- Full debugging / trace introspection.

## 5. User Personas
- Core Maintainer: Needs quick access to all tasks/scripts and system health while iterating.
- New Contributor: Wants immediate orientation (X-ray) + safe guided command execution.
- Automation Engineer: Wants normalized artifact inventory for later automation (v3).

## 6. UX High-Level Flows
1. Add Project Flow: User hits "Add Project" → chooses directory → parser engine runs → Project appears in sidebar with aggregated commands count + health indicator.
2. Command Execution Flow: User selects project → opens Command Palette (keybind) → filters list → selects command → dialog auto-populates parameters → user adjusts → run → live status pane updates.
3. X-ray Flow: Within project dashboard, presses key (e.g., F6) → X-ray overlay with summary tables & tree → can export JSON/Markdown.
4. Template Authoring Flow: User opens built-in sample template file → copies to their repo → enriched metadata improves parser extraction next run.

## 7. Functional Requirements
### 7.1 Project Management
- Add project directory (absolute path). Persist to local state (JSON or SQLite later).
- Remove project & purge associated artifacts.
- Refresh (manual & scheduled) discovery (debounced to avoid thrash).

### 7.2 Autodiscovery Engine
- Pluggable scanners with ordered phases (Scan → Classify → Extract → Normalize → Registry Build).
- Respect .gitignore & ignore patterns (pathspec).
- Detect package manager: presence of `pnpm-lock.yaml`, `package-lock.json`, `poetry.lock`, `requirements.txt`, `uv.lock`.
- Detect runnable tasks: Taskfile tasks, package.json scripts, Makefile targets, Python entrypoints (`if __name__ == "__main__"`), PowerShell scripts with `.# PARAM` blocks, shell scripts with `#!/bin/bash` and function export comments, LangGraph runnable graphs (graph module patterns), Docker targets (build, compose services).

### 7.3 Command Registry
- Each command normalized to `CommandDefinition` with: id, name, source, category, description, parameters[], estimated_runtime (optional), tags, invocation adapter.
- Parameter validation: type (string, int, float, bool, enum, file, dir), constraints (min, max, regex), default, required flag.
- Execution environment resolution (python venv, node workspace, docker context).

### 7.4 Parameter Dialog
- Auto-generated form from parameter schema.
- Real-time validation prior to execute.
- Save last used parameter sets (history).

### 7.5 Templates System
- Provide canonical examples in `mycli/templates/` for: Python script with structured docstring block, PowerShell with comment-based help, shell script with variable metadata, Taskfile advanced annotation, Dockerfile extended labels, LangGraph graph metadata (JSON sidecar), Markdown command spec.
- Template annotation standard: YAML front matter or fenced JSON block specifying `command_meta`: version, description, parameters[], examples.

### 7.6 X-ray Module
- Fast scan with os.scandir + pathspec.
- Metrics: total files, total lines, size bytes, age stats, largest files, language breakdown (by extension), comment density (simple regex heuristics), directory tree (depth ≤ 3) with per-folder file/line counts, histograms (bucket file lengths: 0–50, 51–200, 201–500, 501–1k, 1k–5k, >5k).
- Repo health index formula (initial heuristic):
  - Documentation ratio (md lines / code lines) weight 0.2
  - Test ratio (test files / total code files) weight 0.2
  - Comment density weight 0.2
  - Median file size (lower median better) weight 0.1
  - Presence of CI/config (Taskfile/Makefile/Dockerfile) weight 0.1
  - Dependency hygiene (lock file present) weight 0.2
- Export options: JSON & Markdown.

### 7.7 Execution Layer
- Process spawn isolation; capture stdout/stderr streams into scrollable pane.
- Cancellation (SIGINT or platform equivalent).
- Basic success/failure classification.

### 7.8 Health Metrics
- CPU %, RAM %, active PIDs for recognized commands, open ports (netstat equivalent) filtered to project known ports.

### 7.9 Persistence
- Local ~/.mycli/state.json for project registry and usage history (later pluggable).

## 8. Data Models (Pydantic / Typed)
```python
class ParameterDefinition(BaseModel):
    name: str
    type: Literal['string','int','float','bool','enum','file','dir']
    description: str | None = None
    required: bool = False
    default: Any | None = None
    enum: list[str] | None = None
    min: float | int | None = None
    max: float | int | None = None
    regex: str | None = None
    examples: list[str] | None = None

class CommandDefinition(BaseModel):
    id: str  # stable hash of source path + name
    name: str
    source_path: Path
    origin: Literal['taskfile','package_script','python','powershell','shell','make','docker','langgraph','template','other']
    description: str | None
    parameters: list[ParameterDefinition] = []
    tags: list[str] = []
    estimated_runtime_seconds: int | None = None
    invocation: dict  # strategy payload (e.g. {'type':'taskfile','task':'dev:frontend'})

class ProjectConfig(BaseModel):
    id: str
    name: str
    root_path: Path
    detected_package_managers: list[str]
    environments: dict[str, str]  # e.g. {'python':'./.venv/bin/python'}
    commands: list[CommandDefinition] = []
    stats: 'RepoStats' | None = None

class RepoStats(BaseModel):
    total_files: int
    total_lines: int
    total_size_bytes: int
    language_breakdown: dict[str, int]  # lines
    largest_files: list[tuple[str,int]]
    comment_density_pct: float
    directory_tree: list[dict]  # hierarchical
    file_length_histogram: dict[str,int]
    health_index: float
```

## 9. Architecture Overview
Layers:
1. UI (Textual): components → state queries.
2. State Manager: holds projects, selected project, handles refresh events.
3. Discovery Engine: orchestrates plugin scanners producing raw artifacts → normalizer.
4. Normalizer / Registry Builder: converts raw extracted metadata into `CommandDefinition` list.
5. Execution Layer: decides proper invocation strategy (shell, python, node, docker, task runner).
6. Analytics (X-ray): separate fast path; caches stats in memory, invalidated on manual refresh.

### 9.1 Plugin Interface
```python
class DiscoveryPlugin(Protocol):
    def scan(self, root: Path) -> list['RawArtifact']:
        ...
```
RawArtifact contains: type, path, content_snippet, meta.
Normalizer collects recognized patterns and builds parameter definitions.

### 9.2 Performance Targets
- Initial scan: ≤ 1.5s for JAGI repo subtree subset (~3–5k files) with caching (skip unchanged by mtime & size hash).
- X-ray: streaming partial results to UI; final health index after all lines counted.

## 10. Module Contracts (v2 Implementation Order)
1. `backend/models.py`: All Pydantic models.
2. `backend/loader.py`: Adds project, triggers discovery engine.
3. `backend/tasks.py`: Taskfile + Makefile + package.json script parsing.
4. `backend/executor.py`: Command execution strategies.
5. `backend/health.py`: System & port metrics.
6. `backend/parser_plugins/` (new): taskfile.py, package_scripts.py, python_entrypoints.py, powershell.py, shell.py, docker.py, langgraph.py, templates.py.
7. `components/project_list.py`: Sidebar listing with counts & status icons.
8. `state.py`: AppState, events (ProjectSelected, RefreshRequested, CommandExecuted).
9. `components/dashboard.py`: Commands summary + health snapshots.
10. `components/command_dialog.py`: Parameter UI generator (new file).
11. `components/xray_view.py`: X-ray rendering using Rich tables within Textual.
12. `components/footer_bar.py`: Keybind hints.
13. `styles.tcss`: Layout + theme.

## 11. Autodiscovery Heuristics (Initial)
- Taskfile.yml: parse YAML keys under `tasks:`; description from `desc:`; parameters from `vars:` or embedded comments.
- package.json: scripts map; attempt parameter schema by scanning sibling `scripts/*.js/ts` for yargs/commander definitions.
- Python: look for `if __name__ == "__main__"` or click/typer decorators to extract parameters.
- PowerShell: comment-based help (`<# .SYNOPSIS ... .PARAMETER Name ... #>`).
- Shell: top comment block with `@param name:type:description` lines; fallback: none.
- Dockerfile: treat `docker build` + `docker run` with discovered EXPOSE ports as commands.
- docker-compose.yml: each service start command; environment variable hints as enum candidates.
- LangGraph: `langgraph.json` list of graphs; Python `graph.py` nodes → exposed graph names (namespace as command tag).
- Templates: front matter `command_meta` block canonical source of truth.

## 12. Template Specification
### 12.1 YAML Front Matter Example (Python)
```python
"""
---
command_meta:
  name: ingest-docs
  description: Ingest documents into vector store
  parameters:
    - name: input_dir
      type: dir
      required: true
      description: Folder containing source docs
    - name: batch_size
      type: int
      min: 1
      max: 500
      default: 100
      description: Number of docs per chunk
    - name: dry_run
      type: bool
      default: false
---
"""
```
### 12.2 PowerShell
```powershell
<#
command_meta:
  name: sync-env
  description: Synchronize environment variables
  parameters:
    - name: target
      type: enum
      enum: ["dev","staging","prod"]
      required: true
#>
```
### 12.3 Shell
```bash
# command_meta:name=deploy-api;description=Deploy API service
# param env:enum(dev|staging|prod):Deployment environment
# param replicas:int:1-20:Desired replica count
```

## 13. CLI / TUI Interactions
Keybind proposals:
- F1: Help / Key map
- F2: Command Palette
- F3: Refresh Project
- F4: Health Overlay
- F5: Command History
- F6: X-ray View
- F10: Toggle Themes
Sidebar navigation: Up/Down, Enter selects project. Dashboard lists categories (Build, Dev, Test, Deploy, Misc).
Command Dialog: Tab cycle fields, Enter run, Esc cancel.

## 14. Telemetry & Logging
- Structured logger (JSON lines) for command execution events (future ingestion).
- Basic error classification (ParserError, ExecutionError, ValidationError).

## 15. Security & Safety Considerations
- No automatic execution upon discovery.
- Show clear command source path.
- Warn before running scripts outside project root.
- Parameter sanitation (no shell injection if user edits values – use subprocess list form).

## 16. Performance Strategies
- Cache file metadata (path, size, mtime) to skip unchanged parsing.
- Multi-threaded line counting for X-ray (constrained by GIL → use multiprocessing if needed for large repos).
- Early rendering: show partial stats progressively.

## 17. Error Handling Patterns
- Parser plugin returns RawArtifact or raises PluginWarning (non-fatal) stored in diagnostics panel.
- Execution errors captured and displayed with last N lines of stderr.

## 18. Roadmap
### v2 (This PRD)
- Core discovery engine + essential plugins.
- Command registry + dialogs.
- X-ray insights + export.
- Health + system integration.
- Template library + docs.

### v2.x Enhancements
- Incremental refresh (watch mode).
- Plugin enable/disable toggles.
- Basic dependency graph (commands referencing each other).

### v3 Vision (Future)
- LLM-assisted enrichment: infer missing parameter types, propose new commands.
- Intelligent troubleshooting: parse failure logs, suggest remediation.
- Environment provisioning (create venv, install dependencies, generate missing template blocks).
- Cross-project orchestration & scenario scripts.
- Auto-generated dashboards (HTML export) & historical statistics.

## 19. Risks & Mitigations
| Risk | Impact | Mitigation |
|------|--------|------------|
| Parser false positives | Confusing commands | Confidence score + hide low-confidence by default |
| Large repo performance | Slow UX | Caching + progressive render |
| Parameter extraction inconsistency | Dialog friction | Encourage template adoption; fallback to freeform input |
| Diverse scripting styles | Missed commands | Plugin heuristics + iterative user feedback loop |
| Security of arbitrary scripts | Accidental harmful run | Explicit confirmation for elevated operations (detected by keywords) |

## 20. Acceptance Criteria
- Adding JAGI root directory lists ≥ 90% of Taskfile tasks and package.json scripts as commands.
- Python scripts with template front matter produce typed parameter dialogs (at least 3 types: enum, int range, bool).
- X-ray completes on JAGI repo subset (apps + docs) < 3s with all core sections rendered.
- Export of X-ray JSON & Markdown works.
- Dashboard shows live CPU/RAM and at least one recognized open port.
- Removing a project cleans registry with no stale entries.

## 21. Open Questions
- Persist command run history length & retention policy? (Default 50 in-memory for v2.)
- Provide per-project custom ignore patterns? (Maybe v2.x.)
- How to surface plugin diagnostics elegantly? (Mini panel vs overlay.)

## 22. Documentation Deliverables
- `docs/TEMPLATES.md`: authoring guide.
- `docs/ARCHITECTURE.md`: summarized layered view.
- `docs/XRAY.md`: metric definitions & health index formula.

## 23. Initial Task Breakdown (Seed)
1. Models & data layer.
2. Discovery plugin framework + Taskfile/Package.json parsers.
3. State manager & project add/remove persistence.
4. Command registry + dialog generation.
5. X-ray scanner + renderer.
6. Health metrics provider.
7. Additional parsers (Python, PowerShell, shell, Docker, LangGraph).
8. Template examples & documentation.
9. UI components wiring & keybindings.
10. Testing & performance validation.

---
Prepared for implementation. This PRD is the authoritative reference for v2 development.
