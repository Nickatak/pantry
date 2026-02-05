# Template Repository

A full-stack template repository with JWT authentication, user management, and dashboard routing. Built with Django REST Framework (backend) and Next.js (frontend).

This template provides a foundation for applications requiring user authentication. The auth flow redirects authenticated users to a dashboard which can be customized for any application use case.

## Features

- **JWT Authentication**: Secure token-based authentication with login/register/logout flows
- **User Management**: Custom user model with email-based authentication
- **Protected Routes**: Dashboard accessible only to authenticated users
- **Responsive UI**: Modern frontend built with Next.js and Tailwind CSS
- **API-Driven**: Clean separation between backend API and frontend consumer

## Quick Start

### Backend Setup

#### Install dependencies

```bash
pip install -r requirements.txt
```

#### Run migrations

```bash
python manage.py migrate
```

#### Start development server

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/`

### Frontend Setup

#### Install dependencies

```bash
cd frontend
npm install
```

#### Start development server

```bash
npm run dev
```

The frontend will be available at `http://localhost:3000/`

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
