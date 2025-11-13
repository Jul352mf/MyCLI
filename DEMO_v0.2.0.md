# MyCLI v0.2.0 Demo Script

This script demonstrates the new features implemented in v0.2.0 based on PRD_next_session.md.

## Prerequisites

- MyCLI installed and running
- At least one project configured
- ngrok installed (optional, for ngrok demo)

## Demo Flow

### 1. Launch MyCLI

```powershell
mycli
```

### 2. Explore the New Tabbed Dashboard

**Actions:**
1. Select a project from the sidebar
2. Notice the new tabbed interface in the main panel
3. Click through each tab:
   - **Overview**: Traditional dashboard view (familiar)
   - **Workspace**: URLs and start/stop commands
   - **Command Center**: Discovered commands (placeholder)
   - **X-Ray**: Repository analysis (placeholder)

**Expected Result:**
- Clean tabbed navigation
- Each tab displays relevant information
- Overview tab shows the familiar project status

### 3. System Quick Commands - Processes

**Actions:**
1. Press `S` to open System Quick Commands
2. Observe the Processes tab (should be active by default)
3. See the list of running processes with CPU and memory usage
4. Type in the filter box to search for a specific process (e.g., "python")
5. Use arrow keys to select a process
6. Press "Kill Selected" button (be careful!)

**Expected Result:**
- Modal opens with tabbed interface
- Processes listed with real-time stats
- Filter narrows down the list instantly
- Selected process can be terminated

**Demo Tip:** Don't kill critical processes! Use a test application or select carefully.

### 4. System Quick Commands - ngrok

**Actions:**
1. In the System Quick Commands modal, click the "ngrok" tab
2. Observe the ngrok availability status
   - If available: Shows green checkmark
   - If not available: Shows red X with installation message
3. Enter a port number (e.g., 3000)
4. Press "Start Tunnel" button
5. Check the "Active tunnels" section

**Expected Result:**
- Status indicator shows ngrok availability
- Port input accepts numbers
- Tunnel starts in background
- After 2 seconds, active tunnels list updates

**Demo Tip:** Make sure you have a service running on the port you're tunneling.

### 5. System Quick Commands - Quick Commands

**Actions:**
1. Click the "Quick Commands" tab
2. Observe the list of custom quick commands (empty if first run)
3. Try pressing "Add New" (shows placeholder message for now)
4. If any commands exist, select one and press "Remove Selected"

**Expected Result:**
- Empty state message if no commands
- Placeholder message for "Add New"
- Commands can be removed if present

**Demo Tip:** Quick command creation is stubbed in this version. Full CRUD coming soon.

### 6. Visual Theme Enhancements

**Actions:**
1. Close the System Quick Commands modal (press ESC)
2. Hover over items in the project list
3. Click on various buttons throughout the UI
4. Notice the color changes

**Expected Result:**
- **Hover**: Items highlight with dark vibrant orange
- **Click/Focus**: Items show dark royal blue
- **Buttons**: Different colors for primary (green), error (red), warning (yellow)

### 7. Enhanced Keyboard Navigation

**Actions:**
1. Press various keyboard shortcuts:
   - `S` - System Quick Commands
   - `R` - Run Command dialog
   - `E` - Environment variables
   - `ESC` - Close any modal
2. Notice the consistent behavior

**Expected Result:**
- All modals can be closed with ESC
- Shortcuts work from any view
- Status messages provide clear feedback

## Feature Highlights

### ✅ Completed in v0.2.0

1. **System Quick Commands**
   - Process listing and management
   - ngrok tunnel control
   - Quick commands list/remove

2. **Tabbed Dashboard**
   - 4 tabs: Overview, Workspace, Command Center, X-Ray
   - Clean separation of concerns
   - Workspace shows URLs and commands

3. **Enhanced Theme**
   - New color palette throughout
   - Semantic colors for actions
   - Better visual feedback

4. **Better UX**
   - ESC closes all modals
   - Consistent keyboard shortcuts
   - Status messages with color coding

### 🚧 Coming Soon

1. **URL CRUD Operations**
   - Add/edit/remove URLs from Workspace tab
   - Organize URLs by category

2. **Quick Command Creation**
   - Full add/edit dialog
   - Template system for common commands

3. **Command Center Enhancements**
   - Scope-based filtering
   - Search and filter commands
   - Parameter forms for complex commands

4. **X-Ray Deep Dive**
   - Full repository metrics
   - Health index visualization
   - Code quality insights

## Troubleshooting

### Process list is empty
- This might happen on some systems with restricted permissions
- Try running MyCLI as administrator

### ngrok not found
- Install ngrok: `winget install ngrok.ngrok`
- Make sure ngrok is in your PATH

### Tabs not visible
- Make sure your terminal window is large enough
- Minimum recommended: 120x35 characters

### Colors look wrong
- Ensure you're using Windows Terminal
- Check terminal color scheme settings

## Feedback

For issues, suggestions, or contributions, please visit:
https://github.com/Jul352mf/MyCLI

Enjoy exploring the new features!
