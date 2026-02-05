# Pantry App

A modern app for easily scanning and tracking items in your kitchen—pantry, fridge, or freezer. Built with Django REST Framework (backend) and Next.js (frontend).

The Pantry App provides a low-friction way to keep your household inventory organized. Scan barcodes, add items manually, and instantly know what you have on hand. Perfect for reducing food waste and meal planning.

## Features

- **Barcode Scanning**: Quick item capture with barcode scanning
- **Multi-Location Tracking**: Organize items by storage location (pantry, fridge, freezer)
- **Item Management**: Add, remove, and track quantities of items
- **JWT Authentication**: Secure token-based authentication with login/register flows
- **User Accounts**: Personal inventory management with email-based authentication
- **Responsive UI**: Modern frontend built with Next.js and Tailwind CSS
- **API-Driven**: Clean separation between backend API and frontend consumer

## Prerequisites

- Python 3.8+
- Node.js 16+
- Make (usually pre-installed on macOS/Linux, install via `choco` or `winget` on Windows)

### Initial Setup

```bash
make install
```

This will:
- Create a Python virtual environment (`.venv`)
- Install all backend dependencies
- Run database migrations
- Install frontend dependencies

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
4. Authenticated users are redirected to `/dashboard` (inventory dashboard)
5. Dashboard is protected and requires valid authentication token

## API Endpoints

- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login and get JWT token
- `POST /api/auth/logout/` - Logout
- `GET /api/auth/me/` - Get current user (requires token)

## Customization

The core authentication infrastructure is in place. The next steps are to:
- Build out the inventory dashboard with scanning capabilities
- Create APIs for item management (add, remove, update)
- Implement storage location organization
- Add item details and quantity tracking

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
