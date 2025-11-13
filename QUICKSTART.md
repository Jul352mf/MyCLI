# Quick Start Guide - MyCLI

## 5-Minute Setup

### 1. Install & Run

```powershell
cd C:\Dev\Projects\mycli
.\.venv\Scripts\python.exe app.py
```

### 2. Create Your First Project (Press 6)

Press **6** in the TUI to open the project creation wizard:

1. Enter your project name (e.g., "My Awesome App")
2. Press **Create** or hit **Enter**
3. The project will be created automatically!

**What gets created:**

```
C:\Dev\Projects\myawesomeapp\
├── project.yaml                    # Configuration
├── Taskfile.yml                    # Task definitions
├── README.md                       # Project readme
└── myawesomeapp.code-workspace    # VS Code workspace
```

### 3. Customize Your Project

Select your new project from the sidebar, then edit the files:

#### Edit `project.yaml`

```yaml
name: My Awesome App
workspace: C:\Dev\Projects\myawesomeapp\myawesomeapp.code-workspace
dev_dir: C:\Dev\Projects\myawesomeapp
task_start: dev        # Main task to run on F1
apps:
  - code               # VS Code
  - notion             # Notion
urls:
  - http://localhost:3000
  - http://localhost:5173
```

#### Edit `Taskfile.yml`

```yaml
version: '3'

tasks:
  dev:
    desc: Start development server
    cmds:
      - npm run dev    # Change this to your actual dev command

  build:
    desc: Build the project
    cmds:
      - npm run build

  test:
    desc: Run tests
    cmds:
      - npm test
```

### 4. Start Development (Press 1)

Press **1** to start your environment:
- Opens VS Code with your workspace
- Starts Docker Desktop (if not running)
- Opens Notion (if not running)
- Runs your `dev` task in Windows Terminal
- Opens all your URLs in browser

### 5. Common Workflows

#### View All Tasks (Press 3)
- Press **3** to see all tasks from Taskfile.yml
- Press **1-6** to run any of the first 6 tasks
- Press **ESC** to return to dashboard

#### Open Dashboards (Press 4)
- Press **4** to open all URLs at once

#### Check System (Press 5)
- Press **5** to view CPU, RAM, and port usage

#### Stop Environment (Press 2)
- Press **2** to run `docker compose down`

## Example Projects

### Web App with Docker

**project.yaml:**
```yaml
name: My Web App
workspace: C:\Dev\Projects\mywebapp\mywebapp.code-workspace
dev_dir: C:\Dev\Projects\mywebapp
task_start: dev
apps:
  - code
urls:
  - http://localhost:3000
  - http://localhost:3000/api/docs
```

**Taskfile.yml:**
```yaml
version: '3'

tasks:
  dev:
    desc: Start dev with Docker
    cmds:
      - docker compose up

  down:
    desc: Stop containers
    cmds:
      - docker compose down

  logs:
    desc: View logs
    cmds:
      - docker compose logs -f
```

### Full Stack with Cloud

**project.yaml:**
```yaml
name: Full Stack App
workspace: C:\Dev\Projects\fullstack\fullstack.code-workspace
dev_dir: C:\Dev\Projects\fullstack
task_start: dev
apps:
  - code
urls:
  - http://localhost:3000
  - http://localhost:5173
  - https://vercel.com/myteam/myproject
  - https://app.supabase.com/project/abc123

vercel:
  project_slug: myproject
  team_id: team_abc123
  token: null

supabase:
  api_url: https://abc123.supabase.co
  api_health_check: /rest/v1/
```

## Tips

### Navigation
- **Arrow Keys**: Navigate between projects in sidebar
- **Tab**: Move between interactive elements
- **ESC**: Go back to dashboard from any view
- **Enter**: Select/confirm actions
- **Number Keys (1-6)**: Quick actions or run tasks (context-sensitive)

### Multiple Projects
- Create as many projects as you want with **6**
- Switch between them with arrow keys
- Each project maintains its own configuration

### Task Organization
- Name tasks clearly: `dev`, `build`, `test`, `deploy`
- Use descriptive descriptions
- Group related commands
- First 6 tasks get keyboard shortcuts in task view

### URL Management
- Add localhost URLs for local dev
- Add production URLs for quick access
- Add monitoring dashboards
- Add documentation links

### Keyboard Shortcuts
- **1**: Start environment (or run task 1 in task view)
- **2**: Stop environment (or run task 2 in task view)
- **3**: Open tasks view (or run task 3 in task view)
- **4**: Open URLs (or run task 4 in task view)
- **5**: System health (or run task 5 in task view)
- **6**: Create project (or run task 6 in task view)
- **ESC**: Return to dashboard
- **Q**: Quit anytime

## Next Steps

1. Create a project with **6**
2. Add your actual commands to `Taskfile.yml`
3. Update URLs in `project.yaml`
4. Press **1** to start development
5. Use **3** to run tasks as needed

## Need Help?

See full documentation in `README.md`

---

**Happy coding! 🚀**
