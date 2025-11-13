"""Project template management system."""
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import yaml
from datetime import datetime


@dataclass
class ProjectTemplate:
    """Structure for a project template."""
    id: str
    name: str
    description: str
    language: str
    files: Dict[str, str]  # path -> content
    directories: List[str]
    required_fields: List[str]
    optional_fields: List[str]


class TemplateManager:
    """Manages project templates."""

    def __init__(self):
        """Initialize template manager."""
        self.templates_dir = Path(__file__).parent.parent / "templates"
        self.templates: Dict[str, ProjectTemplate] = {}
        self._load_templates()

    def _load_templates(self) -> None:
        """Load all templates from templates directory."""
        if not self.templates_dir.exists():
            self.templates_dir.mkdir(exist_ok=True)
            return

        for template_file in self.templates_dir.glob("*.yaml"):
            try:
                with open(template_file, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    template = self._parse_template(data)
                    self.templates[template.id] = template
            except Exception as e:
                print(f"Failed to load template {template_file}: {e}")

    def _parse_template(self, data: Dict[str, Any]) -> ProjectTemplate:
        """Parse template data into ProjectTemplate."""
        return ProjectTemplate(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            language=data["language"],
            files=data.get("files", {}),
            directories=data.get("directories", []),
            required_fields=data.get("required_fields", []),
            optional_fields=data.get("optional_fields", [])
        )

    def get_template(self, template_id: str) -> Optional[ProjectTemplate]:
        """Get template by ID."""
        return self.templates.get(template_id)

    def list_templates(self) -> List[Dict[str, str]]:
        """List all available templates."""
        return [
            {
                "id": t.id,
                "name": t.name,
                "description": t.description,
                "language": t.language
            }
            for t in self.templates.values()
        ]

    def create_project_from_template(
        self,
        template_id: str,
        project_path: str,
        variables: Dict[str, str]
    ) -> Dict[str, Any]:
        """Create a new project from template."""
        template = self.get_template(template_id)
        if not template:
            return {
                "success": False,
                "error": f"Template '{template_id}' not found"
            }

        project_path = Path(project_path)

        # Create project directory
        if project_path.exists():
            return {
                "success": False,
                "error": f"Directory '{project_path}' already exists"
            }

        try:
            project_path.mkdir(parents=True)

            # Create directories
            for directory in template.directories:
                dir_path = project_path / directory
                dir_path.mkdir(parents=True, exist_ok=True)

            # Create files with variable substitution
            for file_path, content in template.files.items():
                # Substitute variables in path
                rendered_path = self._render_template(file_path, variables)
                full_path = project_path / rendered_path

                # Ensure parent directory exists
                full_path.parent.mkdir(parents=True, exist_ok=True)

                # Substitute variables in content
                rendered_content = self._render_template(content, variables)

                # Write file
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(rendered_content)

            # Generate AI context files
            ai_files = generate_ai_context_files(
                str(project_path),
                template_id,
                variables
            )

            return {
                "success": True,
                "message": f"Project created from {template.name}",
                "path": str(project_path),
                "ai_context_files": ai_files
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create project: {str(e)}"
            }

    def _render_template(
        self,
        template_str: str,
        variables: Dict[str, str]
    ) -> str:
        """Render template string with variables."""
        result = template_str
        for key, value in variables.items():
            result = result.replace(f"{{{{{key}}}}}", value)
        return result


# AI Context Templates
AI_CONTEXT_TEMPLATES = {
    "python-fastapi": {
        ".cursorrules": """# Python FastAPI Project Rules

## Code Style
- Use Python 3.11+ features
- Follow PEP 8 style guide
- Use type hints for all functions
- Prefer async/await over sync code
- Keep functions focused and small

## Architecture
- Follow repository pattern for data access
- Use dependency injection for services
- Keep business logic in service layer
- Models in `src/models/`
- API routes in `src/api/`
- Business logic in `src/services/`

## Testing
- Write tests for all endpoints
- Use pytest fixtures for common setup
- Mock external dependencies
- Aim for >80% coverage

## FastAPI Patterns
- Use Pydantic models for request/response
- Implement proper exception handlers
- Use background tasks for async operations
- Document all endpoints with docstrings

## Dependencies
- Keep requirements.txt minimal
- Pin major versions only
- Separate dev dependencies
""",
        ".claude-project.md": """# {project_name} - Claude Project Context

## Project Overview
{description}

## Architecture Decisions
- **Framework**: FastAPI for high-performance async API
- **Validation**: Pydantic v2 for data validation
- **Testing**: Pytest with async support
- **Deployment**: Docker with uvicorn

## File Structure
```
src/
├── main.py          # FastAPI app entry point
├── api/             # API route handlers
├── models/          # Pydantic models
└── services/        # Business logic

tests/
├── api/             # API endpoint tests
└── conftest.py      # Test fixtures
```

## Development Workflow
1. Create Pydantic models for data structures
2. Implement service layer with business logic
3. Create API routes using FastAPI
4. Write tests for each endpoint
5. Run tests with: `pytest`
6. Start dev server: `task dev`

## Key Commands
- `task dev` - Start development server
- `task test` - Run test suite
- `task lint` - Run code linters

## Important Notes
- All endpoints should have proper error handling
- Use dependency injection for database/services
- Keep routes thin, logic in services
- Document complex business logic
""",
        ".github/copilot-instructions.md": """# GitHub Copilot Instructions

## Project: {project_name}

### Code Generation Preferences
- Use async/await for all I/O operations
- Include type hints in all function signatures
- Follow FastAPI best practices
- Write docstrings for all public functions

### Testing Conventions
- Use pytest-asyncio for async tests
- Mock external dependencies with pytest-mock
- Test both success and error cases
- Include edge cases in tests

### API Endpoint Pattern
```python
@router.get("/resource/{{id}}")
async def get_resource(
    resource_id: int,
    service: ResourceService = Depends()
) -> ResourceResponse:
    \"\"\"Get resource by ID.\"\"\"
    resource = await service.get_resource(resource_id)
    if not resource:
        raise HTTPException(404, "Resource not found")
    return ResourceResponse.from_orm(resource)
```

### Error Handling
- Use HTTPException for API errors
- Create custom exception classes for business logic
- Always include meaningful error messages
"""
    },
    "nextjs-app": {
        ".cursorrules": """# Next.js + TypeScript Project Rules

## Code Style
- Use TypeScript strict mode
- Prefer functional components with hooks
- Use arrow functions for components
- Keep components under 200 lines
- Extract complex logic into custom hooks

## Architecture
- Use App Router (not Pages Router)
- Server Components by default
- Client Components only when needed
- API routes in `app/api/`
- Components in `components/`
- Utilities in `lib/`

## Component Patterns
- One component per file
- Props interface above component
- Export component as default
- Use named exports for types

## Styling
- Use Tailwind CSS utility classes
- Keep custom CSS minimal
- Use CSS modules for complex styles
- Prefer composition over inheritance

## State Management
- Use useState for local state
- Use Context for shared state
- Consider Zustand for complex state
- Avoid prop drilling

## Testing
- Test user interactions, not implementation
- Use Testing Library queries
- Mock API calls
- Test accessibility

## Performance
- Use React.memo() sparingly
- Optimize images with next/image
- Lazy load heavy components
- Use dynamic imports wisely
""",
        ".claude-project.md": """# {project_name} - Claude Project Context

## Project Overview
{description}

## Architecture Decisions
- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript with strict mode
- **Styling**: Tailwind CSS
- **Testing**: Jest + React Testing Library
- **Deployment**: Vercel (recommended)

## File Structure
```
app/
├── layout.tsx       # Root layout
├── page.tsx         # Home page
└── api/             # API routes

components/
└── [feature]/       # Feature components

lib/
└── utils.ts         # Utility functions
```

## Development Workflow
1. Create component with TypeScript interface
2. Style with Tailwind CSS
3. Write tests for user interactions
4. Check types: `npm run build`
5. Run dev server: `npm run dev`

## Key Commands
- `npm run dev` - Start development server
- `npm test` - Run test suite
- `npm run build` - Build for production
- `npm run lint` - Run ESLint

## Important Notes
- Use Server Components by default
- Add 'use client' only when needed
- Always define TypeScript interfaces
- Optimize images with next/image
""",
        ".github/copilot-instructions.md": """# GitHub Copilot Instructions

## Project: {project_name}

### Component Generation Pattern
```typescript
interface ComponentProps {
  // Define props here
}

export default function Component({ ...props }: ComponentProps) {
  return (
    <div className="...">
      {/* Component JSX */}
    </div>
  )
}
```

### Server Component Pattern
- Use async functions
- Fetch data directly in component
- No useState or useEffect

### Client Component Pattern
- Add 'use client' directive
- Use hooks for interactivity
- Handle user events

### API Route Pattern
```typescript
import { NextResponse } from 'next/server'

export async function GET(request: Request) {
  // Handle GET request
  return NextResponse.json({ data })
}
```

### Testing Pattern
- Test user behavior, not implementation
- Use screen queries from Testing Library
- Mock network requests
- Test accessibility
"""
    },
    "nodejs-api": {
        ".cursorrules": """# Node.js + TypeScript API Rules

## Code Style
- Use TypeScript strict mode
- Prefer async/await over callbacks
- Use arrow functions
- Keep functions under 50 lines
- One export per file

## Architecture
- Follow MVC pattern
- Routes in `src/routes/`
- Controllers in `src/controllers/`
- Services in `src/services/`
- Models in `src/models/`
- Middleware in `src/middleware/`

## Express Patterns
- Use Router for route grouping
- Validate input with middleware
- Use async error handling
- Return consistent response format

## Error Handling
- Create custom error classes
- Use error handling middleware
- Always log errors
- Return appropriate HTTP status codes

## Security
- Validate all inputs
- Sanitize user data
- Use helmet for headers
- Implement rate limiting
- Never expose stack traces in production

## Testing
- Test all routes
- Mock external services
- Test error cases
- Use supertest for API tests

## Database
- Use connection pooling
- Parameterize queries
- Handle connection errors
- Close connections properly
""",
        ".claude-project.md": """# {project_name} - Claude Project Context

## Project Overview
{description}

## Architecture Decisions
- **Framework**: Express.js
- **Language**: TypeScript
- **Testing**: Jest + Supertest
- **Logging**: Winston
- **Security**: Helmet + CORS

## File Structure
```
src/
├── index.ts         # App entry point
├── routes/          # Route definitions
├── controllers/     # Request handlers
├── services/        # Business logic
├── middleware/      # Custom middleware
└── models/          # Data models

tests/
└── *.test.ts        # Test files
```

## Development Workflow
1. Define route in routes/
2. Create controller function
3. Implement business logic in service
4. Add middleware if needed
5. Write tests
6. Run tests: `npm test`
7. Start dev: `npm run dev`

## Key Commands
- `npm run dev` - Start with hot reload
- `npm test` - Run test suite
- `npm run build` - Compile TypeScript
- `npm start` - Start production server

## Important Notes
- All routes should have error handling
- Use middleware for cross-cutting concerns
- Keep controllers thin, logic in services
- Log all errors with Winston
""",
        ".github/copilot-instructions.md": """# GitHub Copilot Instructions

## Project: {project_name}

### Route Handler Pattern
```typescript
export const getResource = async (
  req: Request,
  res: Response,
  next: NextFunction
) => {
  try {
    const data = await resourceService.get(req.params.id)
    res.json({ success: true, data })
  } catch (error) {
    next(error)
  }
}
```

### Service Pattern
```typescript
export class ResourceService {
  async get(id: string): Promise<Resource> {
    // Business logic here
  }
}
```

### Error Handling
- Use try/catch in async handlers
- Pass errors to next() middleware
- Create custom error classes
- Always return proper status codes

### Testing
- Test all endpoints
- Mock external dependencies
- Test error cases
- Use supertest for requests
"""
    }
}


def generate_ai_context_files(
    project_path: str,
    template_id: str,
    variables: Dict[str, str]
) -> List[str]:
    """Generate AI context files for a project.
    
    Returns list of created file paths.
    """
    if template_id not in AI_CONTEXT_TEMPLATES:
        return []
    
    created_files = []
    context_files = AI_CONTEXT_TEMPLATES[template_id]
    project_path_obj = Path(project_path)
    
    for filename, content in context_files.items():
        # Render content with variables
        rendered_content = content
        for key, value in variables.items():
            rendered_content = rendered_content.replace(
                f"{{{key}}}",
                value
            )
        
        # Determine file path
        if filename.startswith('.github/'):
            file_path = project_path_obj / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
        else:
            file_path = project_path_obj / filename
        
        # Write file
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(rendered_content)
            created_files.append(str(file_path))
        except Exception as e:
            print(f"Failed to create {filename}: {e}")
    
    return created_files


# Global template manager instance
_template_manager: Optional[TemplateManager] = None


def get_template_manager() -> TemplateManager:
    """Get or create global template manager."""
    global _template_manager
    if _template_manager is None:
        _template_manager = TemplateManager()
    return _template_manager
