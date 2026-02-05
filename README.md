# Template Repository

A full-stack template repository with JWT authentication, user management, and dashboard routing. Built with Django REST Framework (backend) and Next.js (frontend).

This template provides a foundation for applications requiring user authentication. The auth flow redirects authenticated users to a dashboard which can be customized for any application use case.

## Features

- **JWT Authentication**: Secure token-based authentication with login/register/logout flows
- **User Management**: Custom user model with email-based authentication
- **Protected Routes**: Dashboard accessible only to authenticated users
- **Responsive UI**: Modern frontend built with Next.js and Tailwind CSS
- **API-Driven**: Clean separation between backend API and frontend consumer

## Prerequisites

- Python 3.8+
- Node.js 16+
- Make (usually pre-installed on macOS/Linux, install via `choco` or `winget` on Windows)

## Environment Configuration

This project uses environment-specific configuration files managed through symlinks:

### Setup

1. **Automatic setup** during `make install`:
   - `.env.dev` and `.env.prod` are automatically copied from `.env.example` (if they don't exist)
   - Development environment is automatically activated via toggle-env script

2. **Edit the environment files** with your specific settings (optional for development, required for production):
   - `.env.dev` - Development configuration (DEBUG=True, SQLite, etc.)
   - `.env.prod` - Production configuration (DEBUG=False, production database, etc.)
   - `.env.example` - Template file (tracked in git, do not modify for sensitive data)

3. **Switch environments** (if needed):
   ```bash
   ./scripts/toggle-env.sh dev   # Use development environment
   # or
   ./scripts/toggle-env.sh prod  # Use production environment
   ```

The script creates a `.env` symlink pointing to your chosen environment file.

### Environment Script Commands

| Command | Description |
|---------|-------------|
| `./scripts/toggle-env.sh dev` | Activate development environment |
| `./scripts/toggle-env.sh prod` | Activate production environment |
| `./scripts/toggle-env.sh current` | Show active environment |
| `./scripts/toggle-env.sh status` | Show environment files status |
| `./scripts/toggle-env.sh help` | Display script help |

> **Note**: Development environment is automatically activated during `make install`. Use these commands to switch between environments or check the current environment status.

### Initial Setup

```bash
make install
```

This will:
- Create a Python virtual environment (`.venv`)
- Automatically copy `.env.example` to `.env.dev` and `.env.prod` (if they don't exist)
- Activate the **development environment** (`.env.dev`) via the toggle-env script
- Install all backend dependencies
- Run database migrations
- Install frontend dependencies

> **Deployment Note**: The `make install` command automatically sets up a development environment. For production deployment, run `./scripts/toggle-env.sh prod` after updating `.env.prod` with production values.

## Development - Dev User

For quick testing, you can create a development user with pre-set credentials:

```bash
make dev-user
```

Login credentials:
- Email: `test@ex.com`
- Password: `Qweqwe123`

To delete the dev user:

```bash
make dev-user-delete
```

> **Warning**: These commands are for development only. Do not use in production.

### Running the Application

Start both backend and frontend servers:

```bash
make dev
```

- Backend API: `http://localhost:8000/api/`
- Frontend: `http://localhost:3000/`

Or run them separately:

```bash
make run-backend  # Django backend on port 8000
make run-frontend # Next.js frontend on port 3000
```

Stop servers:

```bash
make kill
```

### Setup & Installation

| Command | Description |
|---------|-------------|
| `make venv` | Create Python virtual environment |
| `make install` | Install dependencies and run migrations |
| `make pre-commit-install` | Setup pre-commit hooks |

### Running the Application

| Command | Description |
|---------|-------------|
| `make dev` | Start both backend and frontend servers |
| `make run-backend` | Start Django development server |
| `make run-frontend` | Start Next.js development server |
| `make kill` | Stop all running servers |

### Testing

| Command | Description |
|---------|-------------|
| `make test` | Run all tests |
| `make test-api` | Run API tests only |
| `make test-e2e` | Run end-to-end tests |
| `make test-cov` | Run tests with coverage report |

> **Note**: For `make test-e2e`, both the backend and frontend servers must be running. Start them with `make dev` before running e2e tests.

## Project Structure

```
├── api/                          # Django app
│   ├── models/                   # User model
│   ├── serializers/              # DRF serializers
│   ├── views/                    # API views and auth endpoints
│   ├── migrations/               # Database migrations
│   └── management/commands/      # Django management commands
├── core/                         # Django project settings
├── frontend/                     # Next.js application
│   ├── app/                      # Next.js app directory
│   ├── lib/                      # Frontend utilities and API client
│   └── public/                   # Static assets
├── tests/                        # Test suite
├── manage.py                     # Django entry point
├── Makefile                      # Build and task automation
└── requirements.txt              # Python dependencies
```

## Authentication Flow

1. User registers or logs in via `/login` or `/register` pages
2. Credentials are verified against the backend JWT auth endpoints
3. JWT token is stored securely in the frontend
4. Authenticated users are redirected to `/dashboard`
5. Dashboard is protected and requires valid authentication token

## API Endpoints

- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login and get JWT token
- `POST /api/auth/logout/` - Logout
- `GET /api/auth/me/` - Get current user (requires token)

## Customization

Replace the dashboard page with your application logic. The authentication and routing infrastructure is already in place and can be extended for any use case.

## Hidden Files and Directories

VS Code is configured to hide common build and cache directories to keep the file explorer clean:

- `__pycache__/` - Python cache files
- `.venv/` - Virtual environment
- `.pytest_cache/` - Pytest cache
- `.next/` - Next.js build files
- `node_modules/` - npm dependencies
- `htmlcov/` - Coverage reports
- `*.sqlite3` - Database files
- `.mypy_cache/` - MyPy cache

### Unhiding Files

To temporarily show hidden files, you can:

1. Edit `.vscode/settings.json` and remove the items from `files.exclude`
2. Or use the VS Code keyboard shortcut: `Ctrl+Shift+.` (or `Cmd+Shift+.` on Mac) to toggle hidden files
