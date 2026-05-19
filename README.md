# MediCore - Hospital Management System

A comprehensive, production-grade Hospital Management System built with Django, HTMX, and Alpine.js.

## Features

- **User Management** — 8 role-based access levels (Admin, Doctor, Receptionist, HR, Nurse, Pharmacist, Laboratorian, Accountant)
- **Doctor Management** — Profiles, weekly schedules, break times, patient limits
- **Patient Records** — Medical history, allergies, vital signs with auto-calculated BMI and BP alerts
- **Appointments** — Booking, calendar view, conflict detection
- **Prescriptions** — Status tracking, medicine line items
- **Billing & Invoicing** — Auto-numbered invoices, PDF print, revenue dashboard
- **Pharmacy** — Medicine catalog, stock tracking, low-stock alerts, supplier management
- **Bed/Ward Management** — Admission/discharge workflow
- **Nursing** — Notes with priority levels, medication administration log
- **HR Module** — Employee profiles, attendance tracking, leave management
- **Diagnostic Reports** — Lab reports with status tracking
- **Audit Logging** — All CRUD operations tracked
- **Dark/Light Theme** — 60+ CSS custom properties, dual-accent (teal/violet) design system

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.11+, Django 5.2+, django-htmx |
| **Frontend** | Django Templates, HTMX 2.0, Alpine.js 3.14, Chart.js, Lucide Icons |
| **Database** | SQLite (dev), PostgreSQL/MySQL (production) |
| **Scraper** | Scrapy 2.15+ (medicine data import) |
| **Video Demo** | React 19, Remotion 4.x, TypeScript |
| **Package Manager** | uv (Python), npm (Node.js) |

## Prerequisites

- Python 3.11+
- Node.js 18+
- [uv](https://docs.astral.sh/uv/) (Python package manager)

## Quick Start

### 1. Install Python Dependencies

```bash
uv sync
```

### 2. Apply Database Migrations

```bash
uv run python manage.py migrate
```

### 3. Seed Demo Data

```bash
uv run python populate_demo_data.py
```

This creates demo users, doctors, patients, and sample data across all modules.

### 4. Start Development Server

```bash
uv run python manage.py runserver
```

Visit `http://localhost:8000` in your browser.

### Default Credentials

| Username | Role | Password |
|---|---|---|
| `admin` | Admin (superuser) | `password123` |
| `doctor_john` | Doctor | `password123` |
| `receptionist1` | Receptionist | `password123` |
| `nurse1` | Nurse | `password123` |
| `pharmacist1` | Pharmacist | `password123` |
| `accountant1` | Accountant | `password123` |
| `hr1` | HR Manager | `password123` |
| `laboratorian1` | Laboratorian | `password123` |

## Project Structure

```
HMS/
├── hms/              # Django project settings
├── core/             # User model, auth, dashboard, audit logging, permissions
├── doctors/          # Doctor profiles, weekly schedules
├── patients/         # Patient records, medical history, vital signs
├── appointments/     # Appointment booking, calendar
├── prescriptions/    # Prescriptions with medicine line items
├── billing/          # Invoicing, PDF print, revenue dashboard
├── pharmacy/         # Medicine catalog, stock, suppliers
├── beds/             # Wards, beds, admission/discharge
├── nursing/          # Nursing notes, medication administration
├── hr/               # Employee profiles, attendance, leave
├── reports/          # Diagnostic/lab reports
├── scraper/          # Scrapy spider for medicine data
├── src/              # Remotion demo video (React/TypeScript)
├── templates/        # Django HTML templates + reusable components
├── static/css/       # "Clinical Elegance" design system
└── media/            # User uploads (avatars, etc.)
```

## Available Commands

### Django/Python

```bash
uv run python manage.py migrate          # Apply migrations
uv run python manage.py runserver        # Start dev server
uv run python manage.py createsuperuser  # Create admin user
uv run python manage.py collectstatic    # Collect static files
uv run python manage.py shell            # Interactive Django shell
uv run python manage.py check            # System checks
uv run python populate_demo_data.py      # Seed demo data
```

### Demo Video (Remotion)

```bash
npm run dev        # Open Remotion Studio (interactive preview)
npm run build      # Render video to out/demo.mp4
./rebuild_video.sh # Re-render demo video via shell
```

### Medicine Scraper

```bash
cd scraper && scrapy crawl <spider_name>  # Run medicine data scraper
```

## Configuration

The project currently uses hardcoded development settings. For production:

1. Create a `.env` file with:
   - `SECRET_KEY` (generate a new secure key)
   - `DEBUG=False`
   - `ALLOWED_HOSTS` (restrict to your domain)
   - Database credentials (PostgreSQL/MySQL)

2. Update `hms/settings.py` to read from environment variables

3. Replace SQLite with PostgreSQL or MySQL

## Design System

The UI uses a custom "Clinical Elegance" design system featuring:
- Dark/light theme toggle
- 60+ CSS custom properties
- Dual-accent color scheme (teal/violet)
- Typography: IBM Plex Sans, Sora (Google Fonts)
- Lucide Icons (emoji-free)
- Skeleton loading states
- Toast notifications (Alpine.js)
- Modal dialog system
- 10 reusable Django template components

## License

MIT
