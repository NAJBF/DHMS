# DHMS API - Dorm and Hostel Management System

A Django REST Framework API for managing university dormitory operations.

## Features

- 🔐 **JWT Authentication** - Secure login with role-based access
- 🏠 **Dorm Management** - Track dorms, rooms, and occupancy
- 👨‍🎓 **Student Portal** - Dashboard, maintenance, laundry forms
- 👨‍💼 **Proctor Dashboard** - Approve requests, assign rooms, manage penalties
- 🔧 **Staff Operations** - Accept and complete maintenance jobs
- 🛡️ **Security Gate** - Verify laundry with QR scanning

## Quick Start

```bash
# Install dependencies
uv sync

# Apply migrations
uv run python manage.py migrate

# Create superuser
uv run python manage.py createsuperuser

# Run server
uv run python manage.py runserver
```

## API Endpoints

| Base URL | Description |
|----------|-------------|
| `/api/auth/` | Authentication (login, register, logout) |
| `/api/students/` | Student operations |
| `/api/proctors/` | Proctor operations |
| `/api/staff/` | Staff operations |
| `/api/security/` | Security operations |
| `/api/dorms/` | Dorm listing |
| `/api/docs/` | Swagger UI |
| `/api/redoc/` | ReDoc |

## User Roles

| Role | Access |
|------|--------|
| `student` | View room, submit maintenance/laundry |
| `proctor` | Approve requests, assign rooms, penalties |
| `staff` | Handle maintenance jobs |
| `security` | Verify laundry at gate |
| `admin` | Full access |

## Environment Variables

Create a `.env` file:

```env
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=postgresql://user:pass@host/db
```

## Tech Stack

- Django 5.x
- Django REST Framework
- PostgreSQL (Neon)
- SimpleJWT
- DRF Spectacular
