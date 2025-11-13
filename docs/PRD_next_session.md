# MyCLI — Next Session PRD (UI/UX Elevation)

Date: 2025-11-13
Owner: Jules / Project Team
Status: Draft (for planning next session)

## 1) Problem Statement

The current TUI lets users select a project and run a few numbered actions, but many capabilities (discovery-driven commands, system tools, environment controls) aren’t easily discoverable or actionable. Users lack a coherent “system view,” a clear “project dashboard,” and CRUD surfaces to manage commands, URLs, and settings.

## 2) Goals (Next Session)

- Elevate the UX so users can: 
  - Access system-wide quick commands (processes/ports, ngrok, kill processes, custom shortcuts) from anywhere.
  - Navigate a richer project dashboard with clear sub-areas: Workspace, Command Center, X-Ray.
  - Perform basic CRUD on commands metadata, URLs, and start/stop mappings.
  - Understand what’s happening via consistent, descriptive status messages.
  - Enjoy clearer visual affordances (selection/hover/pressed states; color semantics).
  - Close modals with Escape (Env modal, others) and rely on consistent keybindings.
- Deliver an “instructions pack” prompt for coding agents to prep repos for maximum auto-discovery.

## 3) Non-Goals (for next session)

- Full settings center with GitHub OAuth, account CRUD, and advanced preferences (tracked for later).
- Deep X-Ray analytics beyond existing scanner (can stub entry points and enrich later).
- Full theming system overhaul; we limit to targeted palette adjustments.

## 4) Primary Users and Use Cases

- Individual developer working across multiple repos needing a fast control plane.
- Team member onboarding a new repo and wanting immediate auto-discovery and runnable commands.

## 5) UX Information Architecture

- Global Layer (always available):
  - System Quick Commands menu (key: `S`):
    - Processes/Ports: list, filter, kill.
    - ngrok: open tunnel on chosen port.
    - Custom Quick Commands: map any project command or ad-hoc shell command to a slot.
    - Shutdown/Restart: save browser tabs, close apps gracefully (design spike only; not fully implemented next session).
    - Settings (stub): GitHub login placeholder; no real OAuth yet.
- Project Layer:
  - Project Dashboard (default after selection):
    - Workspace tab: open URLs, start/stop mappings, open code editor, open terminals.
    - Command Center tab: lists discovered commands (from Taskfile/package.json, subdir scope included), with parameter UI and run.
    - X-Ray tab: existing repo scan presentation (minimal improvements only).

## 6) Functional Requirements (Next Session Scope)

- System Quick Commands
  - View processes and listening ports; filter by name/port; kill selected process.
  - Start ngrok on a chosen port (if ngrok present); display URL; copy to clipboard.
  - Manage Custom Quick Commands (add/edit/remove): store name, command adapter, args; show in a global list.
- Project Dashboard
  - Workspace tab: 
    - CRUD URLs (add/remove/edit labels). 
    - Map start/stop to commands (Taskfile task or npm script); invoke via keys 1/2.
  - Command Center tab:
    - Displays discovered commands with:
      - Scope tags (e.g., `scope:packages/ui`).
      - Parameter UI (already implemented) with execution from correct cwd.
    - Filter by name and scope; run with args.
- Env Modal
  - Close on Escape (implemented).
  - Continue to show Effective env and `.env`-only keys; editing deferred.
- Messaging & Theme
  - Status bar emits consistent success/info/warn/error messages.
  - Update selection/hover/pressed colors per palette: 
    - Hover: dark, subtly vibrant orange
    - Pressed: dark royal blue
    - Semantics: green=success/working, red=error, yellow=warning (each with 3 brightness levels where feasible).

## 7) Data Model/Storage

- Commands: derived from discovery; allow light metadata overlay (description, tags) persisted in `command_catalog.json`.
- Custom Quick Commands: new small JSON store (e.g., `quick_commands.json`) with fields: id, name, adapter, invocation, args, scope (global/project?), createdAt.
- URLs: persisted in project config; expose CRUD.
- Start/Stop mapping: persisted per project.

## 8) Technical Constraints & Assumptions

- Windows-first: PowerShell and Windows Terminal integrations remain primary.
- Monorepo: already supported via recursive discovery and invocation.cwd.
- Parameters: current extractor covers `--flags`, `--key=value`, `<positional>`; deeper typing later.
- ngrok: presence assumed if available in PATH; otherwise guide user.

## 9) Acceptance Criteria

- From the home screen, user can open System Quick Commands and:
  - See a list of processes/ports; kill a process; see confirmation.
  - Attempt to launch ngrok on a chosen port; see URL or error message.
  - Add a custom quick command and see it appear in the list.
- In a project, user can:
  - Navigate to Workspace, add/remove URLs; open all URLs; map start/stop.
  - Navigate to Command Center, filter by scope and name; run a command with parameters and observe correct cwd.
- Pressing Escape closes the Env modal.
- Color semantics and hover/pressed visual changes are visible in lists/buttons.

## 10) Milestones (Next Session)

1. System Quick Commands (processes/ports, kill; ngrok MVP; custom quick command CRUD).
2. Project Dashboard: Workspace tab (URLs, start/stop mapping).
3. Command Center filtering by scope, and parameter UI polish.
4. Palette tweaks and status messaging audit.
5. Fit-and-finish, docs, and a short demo script.

## 11) Risks & Mitigations

- ngrok availability: Detect and display an actionable message to install.
- Process management permissions: best-effort kills; show errors gracefully.
- Parameter typing ambiguity: stick to current heuristics; add enum/type hints when provided.

## 12) Open Questions

- Should Settings include GitHub OAuth now or remain a stub?
- Do we scope Custom Quick Commands globally or per project by default?
- Which X-Ray metrics matter most to surface on the tab?

## 13) Appendix — Repo Preparation Prompt for Coding Agents

Use this prompt in any repo to prepare it for MyCLI’s auto-discovery and great UX:

```
You are configuring this repository to work smoothly with MyCLI (a Textual-based CLI that auto-discovers runnable commands).

Do the following:

1) Command Surfaces
- If using Taskfile, ensure Taskfile.yml contains clearly named tasks under `tasks:` with `desc` and `cmd` fields. Prefer explicit `<positional>` placeholders and flags `--flag` or `--key=value` in `cmd` so parameters can be auto-extracted.
- If using Node, add scripts in package.json with descriptive names; prefer flags and `--key=value` arguments. Include `packageManager` if possible (e.g., "pnpm@x.y.z").
- For monorepos, place Taskfile.yml or package.json in each subpackage; keep names descriptive. Avoid deep vendor directories in repo root (MyCLI skips node_modules/, .git/, .venv/, dist/, build/).

2) Metadata & Descriptions
- Add short, action-oriented descriptions for tasks/scripts (Taskfile `desc`, package.json script name). Include helpful comments/readme snippets for what each command does and expected parameters.

3) Environment
- Provide a `.env.example` with required variables. Keep project `.env` out of version control (in .gitignore). MyCLI will merge shell env > `.env`.

4) Start/Stop & URLs
- Identify a default `dev` or `start` command and any `stop` procedure. Provide a list of dev URLs in a config file or Taskfile variables, so MyCLI can open them.

5) Consistency & Type Hints
- Prefer consistent flag styles (`--flag`, `--key=value`). Use `<positional>` for required inputs. Provide example values in docs.

6) Docs
- Add a short README section titled "Using with MyCLI" describing key commands and any setup steps (ngrok, package manager, Python/Node version).

Deliverables:
- Taskfile.yml and/or package.json updated with descriptive commands.
- `.env.example` added.
- README updated with "Using with MyCLI".
```
