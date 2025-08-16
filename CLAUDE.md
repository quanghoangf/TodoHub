# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a full-stack FastAPI template with React frontend. The project uses:
- **Backend**: FastAPI with SQLModel/SQLAlchemy, PostgreSQL, JWT auth
- **Frontend**: React with TypeScript, Chakra UI, Vite, TanStack Router
- **Database**: PostgreSQL with Alembic migrations
- **Testing**: Pytest (backend), Playwright (frontend E2E)
- **Containerization**: Docker Compose for development and deployment

## Development Commands

### Backend (Python/FastAPI)
Navigate to `backend/` directory for these commands:

**Development server:**
```bash
fastapi dev app/main.py
```

**Testing:**
```bash
# Run tests with coverage
bash scripts/test.sh

# Or manually:
coverage run --source=app -m pytest
coverage report --show-missing
```

**Linting and formatting:**
```bash
# Check code quality
bash scripts/lint.sh

# Format code
bash scripts/format.sh

# Manual commands:
mypy app                    # Type checking
ruff check app             # Linting
ruff format app            # Formatting
```

### Frontend (React/TypeScript)
Navigate to `frontend/` directory for these commands:

**Development server:**
```bash
npm run dev
```

**Build and test:**
```bash
npm run build              # TypeScript compilation + Vite build
npm run lint               # Biome linting and formatting
npm run generate-client    # Generate API client from OpenAPI
```

**End-to-end testing:**
```bash
npx playwright test
```

### Full Stack Development

**Docker Compose (recommended for full development):**
```bash
docker compose watch       # Start all services with hot reload
docker compose logs        # View logs for all services
docker compose logs backend # View specific service logs
```

**Full stack testing:**
```bash
bash scripts/test.sh       # Runs complete Docker-based test suite
```

## Architecture Overview

### Backend Structure (`backend/app/`)
- `api/` - FastAPI route handlers and dependency injection
  - `routes/` - Individual route modules (users, items, login, etc.)
  - `deps.py` - Common dependencies (auth, database sessions)
  - `main.py` - API router registration
- `core/` - Core configuration and utilities
  - `config.py` - Pydantic settings management
  - `db.py` - Database connection and session management
  - `security.py` - JWT and password utilities
- `models.py` - SQLModel database models
- `crud.py` - Database CRUD operations
- `utils.py` - Shared utility functions
- `alembic/` - Database migration files

### Frontend Structure (`frontend/src/`)
- `routes/` - TanStack Router file-based routing
- `components/` - React components organized by feature
  - `Admin/` - User management components
  - `Items/` - Item CRUD components
  - `Common/` - Shared UI components
  - `ui/` - Base UI components (Chakra UI-based)
- `client/` - Auto-generated API client from OpenAPI spec
- `hooks/` - Custom React hooks
- `theme/` - Chakra UI theme configuration

### Key Patterns
- **Authentication**: JWT-based with refresh tokens, handled in `backend/app/core/security.py`
- **Database**: SQLModel with Alembic migrations, session management in `api/deps.py`
- **API Client**: Auto-generated from FastAPI OpenAPI spec using `@hey-api/openapi-ts`
- **State Management**: TanStack Query for server state, React Context for auth
- **Styling**: Chakra UI with custom theme, dark mode support

## Configuration

- Backend settings: `backend/app/core/config.py` (uses Pydantic Settings)
- Environment variables: `.env` file in project root
- Frontend config: `frontend/vite.config.ts`
- Database migrations: `backend/alembic/` (use `alembic` CLI)

## Development Workflow

1. Use `docker compose watch` for full-stack development
2. For backend-only changes: stop Docker backend, run `fastapi dev app/main.py`
3. For frontend-only changes: stop Docker frontend, run `npm run dev`
4. Generate new API client after backend changes: `npm run generate-client`
5. Run tests before committing: `bash scripts/test.sh` (full stack) or individual test commands
6. Use pre-commit hooks for code formatting (install with `uv run pre-commit install`)

## Important Notes

- Database migrations: Create with `alembic revision --autogenerate -m "description"`
- API documentation available at: http://localhost:8000/docs (Swagger UI)
- Frontend dev server: http://localhost:5173
- Backend dev server: http://localhost:8000
- All services use consistent ports for easy local/Docker switching