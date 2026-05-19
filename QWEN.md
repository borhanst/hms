# Hospital Management System (HMS)

## Project Overview

A **comprehensive Django-based Hospital Management System** with 13 apps covering doctors, patients, appointments, billing, pharmacy, beds, nursing, HR, and more. Features role-based access control for 8 user roles, HTMX-powered dynamic UI, Chart.js analytics, and a polished dark-theme responsive frontend.

### Tech Stack
- **Backend:** Python 3.11+, Django 5.2+
- **Frontend:** HTML templates, Custom CSS (dark theme), HTMX 2.x, Alpine.js 3.x, Chart.js 4.x
- **Database:** SQLite (development)
- **Package Manager:** `uv`
- **Image Handling:** Pillow

### Apps & Architecture (13 Django Apps)

| App | Purpose | Key Models |
|-----|---------|------------|
| `core` | Custom User (8 roles), auth, dashboard, user management, audit logging | `User`, `AuditLog` |
| `doctors` | Doctor profiles, weekly schedules | `Doctor`, `DoctorSchedule` |
| `patients` | Patient records, allergies, medical history, vital signs | `Patient`, `VitalSign` |
| `appointments` | Appointment booking, calendar view, conflict detection | `Appointment` |
| `reports` | Diagnostic/lab reports with status tracking | `DiagnosticReport` |
| `prescriptions` | Prescriptions with status, medicine line items | `Prescription`, `PrescriptionItem` |
| `billing` | Invoicing, line items, PDF print, revenue dashboard | `Invoice`, `InvoiceItem` |
| `pharmacy` | Medicine catalog, stock tracking, dispensing, low-stock alerts | `Medicine`, `DispensingRecord` |
| `beds` | Wards, beds, admission/discharge workflow | `Ward`, `Bed`, `Admission` |
| `nursing` | Nursing notes, medication administration | `NursingNote`, `MedicationAdministration` |
| `hr` | Employee profiles, attendance, leave management | `EmployeeProfile`, `Attendance`, `LeaveRequest` |

### User Roles
Admin, Doctor, Receptionist, HR Manager, Nurse, Pharmacist, Laboratorian, Accountant

### Key Features
- ✅ **Pagination** on all list views (10-20 items/page)
- ✅ **Vital Signs** tracking with auto-calculated BMI and BP alerts
- ✅ **Prescription Status** (Active, Completed, Discontinued)
- ✅ **Doctor Schedules** (weekly, with breaks, max patients)
- ✅ **Appointments** with conflict detection and weekly calendar view
- ✅ **Billing** with auto-numbered invoices, PDF print, revenue charts
- ✅ **Pharmacy** with stock management, dispensing, low-stock alerts
- ✅ **Bed/Ward Management** with admission/discharge workflow
- ✅ **Nursing** notes with priority levels, medication administration log
- ✅ **HR** employee profiles, attendance tracking, leave request/approval
- ✅ **Chart.js Dashboard** — patient trends, report categories, revenue, payment methods
- ✅ **Audit Logging** — tracks all CRUD operations
- ✅ **Role-based access** — every view respects user roles
- ✅ **HTMX** — dynamic partial page updates without full reloads

## Building and Running

```bash
# Install dependencies
uv sync

# Run migrations
uv run python manage.py migrate

# Populate demo data
uv run python populate_demo_data.py

# Start development server
uv run python manage.py runserver
```

### Default Credentials (after populate_demo_data.py)
- **Doctors:** `doctor_john`, `doctor_sarah`, `doctor_ali` — password: `password123`
- **Receptionist:** `receptionist1` — password: `password123`
- **Staff:** `nurse1`, `pharmacist1`, `laboratorian1`, `accountant1`, `hr1` — password: `password123`

### Common Commands
```bash
uv run python manage.py migrate          # Apply migrations
uv run python manage.py createsuperuser  # Create admin
uv run python manage.py collectstatic    # Collect static files
uv run python manage.py shell            # Django shell
uv run python manage.py check            # System checks
```

## Development Conventions

- **Custom User Model:** `AUTH_USER_MODEL = "core.User"`
- **Role Decorators:** `@admin_required`, `@doctor_required`, `@staff_required` in `core/decorators.py`
- **HTMX:** Views check `request.htmx` for partial template returns
- **Pagination:** `Paginator(queryset, 10)` with `page_obj` context
- **Templates:** Per-app under `templates/<app_name>/`, shared `base.html` with `{% block extra_js %}`
- **Static Files:** `static/css/styles.css` — dark theme with CSS custom properties
- **Timezone:** `Asia/Dhaka`

## Project Structure

```
HMS/
├── core/              # User, auth, dashboard, audit log, user management
├── doctors/           # Doctor profiles, schedules
├── patients/          # Patient records, vital signs
├── appointments/      # Appointments, calendar, conflict detection
├── reports/           # Diagnostic/lab reports
├── prescriptions/     # Prescriptions with status
├── billing/           # Invoices, PDF, revenue dashboard
├── pharmacy/          # Medicine catalog, dispensing, stock
├── beds/              # Wards, beds, admission/discharge
├── nursing/           # Nursing notes, medication administration
├── hr/                # Employee profiles, attendance, leave
├── hms/               # Settings, URLs, WSGI/ASGI
├── templates/         # Per-app HTML templates
├── static/css/        # Dark theme CSS
├── media/             # User uploads
├── manage.py
├── populate_demo_data.py
├── pyproject.toml
└── db.sqlite3
```
