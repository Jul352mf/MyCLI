# MyCLI Session PRD - Development Cockpit Enhancement

## Session Date
November 10, 2025

## Executive Summary
Transform MyCLI from a basic TUI project manager into a production-ready development cockpit that saves time, preserves context, and automates repetitive tasks.

## Problem Statement
Current implementation is visually complete but lacks practical utility:
- Actions (1-6 keys) don't reliably trigger
- Project creation is shallow (empty files only)
- No workflow integration (Git, Docker, testing)
- No context preservation when switching projects
- Manual repetitive tasks remain manual

## Success Criteria
1. ✅ All action keys work reliably
2. ✅ Git operations accessible and fast (< 2 seconds)
3. ✅ Project memory persists between sessions
4. ✅ Start/Stop actually manage processes
5. ✅ Templates create production-ready projects in < 30 seconds
6. ✅ Zero manual setup for AI context files

## Target Users
- Developers managing 3-10 active projects
- Full-stack developers using Git, Docker, multiple languages
- Teams using AI assistants (Cursor, Claude, Copilot)
- Developers who context-switch frequently

## Core Features (This Session)

### 1. Reliable Action System
**Status:** Broken - keys don't trigger
**Goal:** Every keypress produces expected action
**Acceptance:** Press 1-6 on any project → action executes + notification

### 2. Git Operations Panel
**Status:** Backend exists, no UI
**Goal:** One-key access to Git commands
**Acceptance:** Press 'g' → modal with status, pull, push, branch ops
**Time Saved:** 30+ seconds per Git operation (no terminal switching)

### 3. Project Memory
**Status:** Not implemented
**Goal:** Never lose context when switching projects
**Acceptance:** 
- Stores "working on" task, last active time, notes
- Persists in project.memory.json
- Displays in dashboard header
- Updates automatically

### 4. Process Management (Start/Stop)
**Status:** Superficial (doesn't track PIDs)
**Goal:** One-key start/stop of dev environment
**Acceptance:**
- Start: Runs Taskfile, tracks PIDs, shows progress
- Stop: Kills processes gracefully, offers to commit
- Persistent: Survives MyCLI restart

### 5. Project Templates
**Status:** Creates empty files
**Goal:** Production-ready scaffolding in seconds
**Acceptance:**
- 3+ templates (FastAPI, Next.js, Node API)
- Includes: tests/, docs/, CI/CD, Docker, .gitignore
- Generates AI context files (.cursorrules, .claude-project.md)
- Optional GitHub repo creation

## Technical Scope

### In Scope (This Session)
- ✅ Fix action key bindings and state management
- ✅ Git panel UI (status, pull, push, branch, checkout)
- ✅ Project memory system (persist + restore)
- ✅ Enhanced Start/Stop with PID tracking
- ✅ Template system foundation (3 templates minimum)
- ✅ Template selection modal
- ✅ AI context file generation
- ✅ GitHub repo creation integration

### Out of Scope (Future)
- ❌ GitHub Actions/CI status display
- ❌ Team activity feeds
- ❌ Issue tracker integration (Jira, Linear)
- ❌ Deployment status monitoring
- ❌ Advanced Docker orchestration (Kubernetes)
- ❌ Multi-user collaboration features

## Architecture Decisions

### File Structure
```
mycli/
├── app.py                          # Main TUI app
├── state.py                        # Global state management
├── components/
│   ├── dashboard.py                # Main view (enhanced)
│   ├── project_list.py             # Sidebar (fixed)
│   ├── header_bar.py               # Context display
│   ├── status_bar.py               # Notifications
│   ├── create_modal.py             # Template selector (enhanced)
│   ├── git_modal.py                # NEW: Git operations
│   ├── docker_modal.py             # NEW: Container management
│   └── test_modal.py               # NEW: Test results
├── backend/
│   ├── loader.py                   # Project discovery
│   ├── models.py                   # Data models
│   ├── executor.py                 # Process execution
│   ├── tasks.py                    # Taskfile parsing
│   ├── health.py                   # System health
│   ├── creator.py                  # Project creation (basic)
│   ├── git_ops.py                  # Git commands (exists)
│   ├── memory.py                   # NEW: Project memory
│   ├── templates.py                # NEW: Template management
│   ├── github_ops.py               # NEW: GitHub API
│   ├── docker_ops.py               # NEW: Docker operations
│   └── test_runner.py              # NEW: Test execution
└── templates/
    ├── python-fastapi.yaml         # NEW: FastAPI template
    ├── nextjs-app.yaml             # NEW: Next.js template
    └── nodejs-api.yaml             # NEW: Node API template
```

### Key Technologies
- **TUI:** Textual v6.5.0 (reactive components)
- **Config:** YAML (project.yaml, Taskfile.yml)
- **Git:** subprocess + gitpython (if needed)
- **GitHub:** requests or PyGithub
- **Docker:** subprocess (docker compose)
- **Process:** psutil (PID tracking, process health)

### State Management Strategy
```python
# state.py additions needed:
class AppState:
    selected_project: Optional[ProjectConfig]  # Already exists
    running_processes: Dict[str, int]          # NEW: name -> PID
    project_memories: Dict[str, ProjectMemory] # NEW: path -> memory
    last_test_results: Optional[TestResults]   # NEW: cached results
```

## Implementation Phases

### Phase 1: Foundation (Tasks 1-4) - ~2 hours
**Goal:** Fix bugs, add Git panel, memory, better Start/Stop
**Deliverable:** Stable app with Git operations and context preservation

### Phase 2: Templates (Tasks 5-8) - ~3 hours
**Goal:** Real project scaffolding with AI context
**Deliverable:** Create production-ready projects in 30 seconds

### Phase 3: Advanced (Tasks 9-12) - ~3 hours
**Goal:** Docker, tests, context switching, logging
**Deliverable:** Full-featured development cockpit

## Quality Gates

### Must Pass Before Moving to Next Task:
1. ✅ Code runs without errors
2. ✅ New feature has basic error handling
3. ✅ Status bar shows feedback for operations
4. ✅ State persists correctly (if applicable)
5. ✅ Quick manual test confirms feature works

### No Blockers:
- Skip tests for now (focus on functionality)
- UI polish can wait (functional > pretty)
- Documentation can be added later

## Non-Functional Requirements

### Performance
- Actions respond in < 500ms
- Git operations complete in < 3s
- Template generation in < 30s
- App startup in < 2s

### Usability
- Every action shows feedback (status bar)
- Errors display user-friendly messages
- No silent failures
- Keyboard shortcuts discoverable (footer hints)

### Reliability
- No crashes on invalid input
- Graceful degradation (Git not available? Show message)
- State corruption prevention (validate before save)

## Risk Mitigation

### Known Risks:
1. **Git operations block UI** → Use background threads
2. **Template generation complex** → Start with 1 simple template
3. **GitHub API rate limits** → Cache, show limits to user
4. **Docker not installed** → Detect, disable features gracefully
5. **Subprocess hangs** → Add timeouts, kill switches

### Fallback Plans:
- If GitHub API fails → Manual repo creation instructions
- If Docker unavailable → Hide Docker features
- If Git missing → Show warning, disable Git panel

## Definition of Done (Session)

### Must Have:
- [x] All 12 todos completed
- [ ] App runs without errors
- [ ] Can create project from template
- [ ] Git panel functional (status, pull, push)
- [ ] Start/Stop manage processes
- [ ] Project memory persists

### Nice to Have:
- [ ] Docker panel working
- [ ] Test runner integrated
- [ ] Context switching automated
- [ ] Comprehensive logging

### Out of Scope:
- Full test coverage (29 tests already exist)
- Documentation updates
- Performance optimization
- UI/UX polish

## Success Metrics

### Quantitative:
- Time to start project: < 30 seconds (was: 5+ minutes manual)
- Git operations: < 3 seconds (was: 15+ seconds with terminal)
- Context switch time: < 5 seconds (was: 2+ minutes remembering state)

### Qualitative:
- "I actually want to use this daily"
- "This saves me from terminal gymnastics"
- "I never lose context anymore"

## Next Session Priorities
1. GitHub Actions status integration
2. Issue tracker integration (Jira, Linear)
3. Team activity feed
4. Deployment monitoring
5. Advanced Docker orchestration

---

## Development Notes

### Current Status
- **Last Working:** Git status display in dashboard
- **Last Bug:** Selection AttributeError (FIXED: .renderable → str())
- **Next Up:** Task 1 - Fix action keys

### Known Issues
- Action keys 1-6 may not trigger (state.selected_project not set?)
- Create modal shallow (empty files)
- No error handling for subprocess failures

### Environment
- Python 3.11+
- Windows (PowerShell)
- VS Code workspace: c:\Dev\Projects\mycli
- Virtual env: .venv

---

**This PRD is a living document. Update as we discover blockers or change priorities.**
