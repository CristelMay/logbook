# Logbook — Django Visitor Logbook System

## Overview

**Logbook** is a Django-based visitor logbook and management system designed to streamline visitor monitoring, logging, and record management. The project uses Django for the backend, PostgreSQL or SQLite for the database, and Tailwind CSS for frontend styling.

This guide provides complete instructions for setting up the project locally, installing dependencies, configuring the development environment, and running the application on both Windows and macOS/Linux systems.

---

# Features

- Visitor logging and monitoring
- Django-powered backend
- PostgreSQL or SQLite database support
- Tailwind CSS integration
- Responsive web interface
- Environment-based configuration
- Easy local development setup

---

# Tech Stack

| Technology | Purpose |
|---|---|
| Python 3.11+ | Backend programming language |
| Django | Web framework |
| PostgreSQL | Production database |
| SQLite | Lightweight local database |
| Tailwind CSS | Frontend styling |
| Node.js & npm | Frontend asset compilation |
| Git | Version control |

---

# Project Structure

```text
logbook/
│
├── manage.py
├── requirements.txt
├── .env
├── logbook/
│   ├── settings.py
│   └── ...
│
├── sql/
│   └── supabase_schema.sql
│
├── theme/
│   └── static_src/
│       ├── package.json
│       └── ...
│
└── README.md
```

---

# Prerequisites

Install the following software before setting up the project.

## 1. Python 3.11+

Download: https://www.python.org/downloads/

During installation on Windows:
- Enable **“Add Python to PATH”**

Verify installation:

```powershell
python --version
```

Expected output:

```powershell
Python 3.11.x
```

---

## 2. Git

Download: https://git-scm.com/downloads

Verify installation:

```powershell
git --version
```

---

## 3. Node.js & npm (LTS)

Required for Tailwind CSS asset compilation.

Download: https://nodejs.org/en/download/

Verify installation:

```powershell
node --version
npm --version
```

Recommended:
- Node.js v18+
- Latest npm version

---

## 4. PostgreSQL (Optional but Recommended)

Download: https://www.enterprisedb.com/downloads/postgres-postgresql-downloads

Verify installation:

```powershell
psql --version
```

---

# Database Setup

## PostgreSQL Setup

Open PowerShell or terminal:

```powershell
psql -U postgres
```

Inside PostgreSQL:

```sql
CREATE USER logbook WITH PASSWORD 'your_password';
CREATE DATABASE logbook OWNER logbook;
GRANT ALL PRIVILEGES ON DATABASE logbook TO logbook;
```

Exit PostgreSQL:

```sql
\q
```

### Example DATABASE_URL

```env
DATABASE_URL=postgres://logbook:your_password@localhost:5432/logbook
```

---

## SQLite Setup (Quick Local Development)

SQLite requires no installation.

Use this in your `.env` file:

```env
DATABASE_URL=sqlite:///db.sqlite3
```

---

# Installation Guide

## 1. Clone the Repository

```powershell
git clone <repo-url> logbook
cd logbook
```

---

## 2. Create a Virtual Environment

### Windows

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## 3. Install Python Dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

# Environment Variables

Create a `.env` file in the project root.

## Example `.env`

```env
DJANGO_SECRET_KEY=unsafe-dev-key
DJANGO_DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
```

For PostgreSQL:

```env
DATABASE_URL=postgres://logbook:your_password@localhost:5432/logbook
```

---

# Frontend Setup (Tailwind CSS)

## Option 1 — Django Tailwind

Install Tailwind dependencies:

```powershell
python manage.py tailwind install
```

Start the Tailwind watcher:

```powershell
python manage.py tailwind start
```

Keep this running in a separate terminal during development.

---

## Option 2 — Standalone Node.js Setup

If `theme/static_src/package.json` exists:

```powershell
cd theme/static_src
npm install
npm run build
cd ..\..
```

---

# Database Migration

Run migrations:

```powershell
python manage.py migrate
```

Create an admin account:

```powershell
python manage.py createsuperuser
```

---

# Running the Development Server

Start the Django server:

```powershell
python manage.py runserver
```

Open your browser:

```text
http://127.0.0.1:8000/
```

---

# Running Tests

Run the Django test suite:

```powershell
python manage.py test
```

---

# Static Files

Collect static files for production:

```powershell
python manage.py collectstatic --noinput
```

---

# Useful Commands

## Check Django Configuration

```powershell
python manage.py check
```

## Show Installed Migrations

```powershell
python manage.py showmigrations
```

## Verify Django Installation

```powershell
python -m pip show django
```

---

# Deployment Notes

For production deployment:

- Set `DJANGO_DEBUG=False`
- Use a secure `DJANGO_SECRET_KEY`
- Configure proper `ALLOWED_HOSTS`
- Use PostgreSQL instead of SQLite
- Run `collectstatic`
- Use Gunicorn/Uvicorn behind Nginx
- Store secrets using environment variables

If deploying to Render, refer to:

```text
DEPLOY_RENDER.md
```

---

# Troubleshooting

## `git` is not recognized

Restart your terminal after installing Git.

Verify:

```powershell
git --version
```

---

## `npm` is not recognized

Reinstall Node.js and ensure npm is included.

Verify:

```powershell
npm --version
```

---

## Migration Errors

Check:
- `DATABASE_URL`
- Database credentials
- PostgreSQL service status

---

## Static Files Not Updating

Run:

```powershell
python manage.py collectstatic --noinput
```

or restart the Tailwind watcher.

---

# Important Files

| File | Description |
|---|---|
| `manage.py` | Django management entry point |
| `requirements.txt` | Python dependencies |
| `logbook/settings.py` | Django settings |
| `sql/supabase_schema.sql` | Database schema |
| `theme/static_src/package.json` | Frontend dependencies |

---

# Recommended Improvements

- Add `.env.example`
- Add CI/CD pipeline
- Add Docker support
- Add deployment scripts
- Add automated testing workflow

---

# License

This project is intended for educational and development purposes.

---

# Author

Developed using:
- Django — https://www.djangoproject.com/
- PostgreSQL — https://www.postgresql.org/
- Tailwind CSS — https://tailwindcss.com/