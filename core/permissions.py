from django.urls import reverse

from .models import User


MODULE_ACCESS = {
    "dashboard": {
        User.Role.ADMIN,
        User.Role.DOCTOR,
        User.Role.RECEPTIONIST,
        User.Role.HR,
        User.Role.NURSE,
        User.Role.PHARMACIST,
        User.Role.LABORATORIAN,
        User.Role.ACCOUNTANT,
    },
    "doctors": {User.Role.ADMIN, User.Role.DOCTOR, User.Role.RECEPTIONIST},
    "patients": {
        User.Role.ADMIN,
        User.Role.DOCTOR,
        User.Role.RECEPTIONIST,
        User.Role.NURSE,
        User.Role.LABORATORIAN,
        User.Role.ACCOUNTANT,
    },
    "appointments": {User.Role.ADMIN, User.Role.DOCTOR, User.Role.RECEPTIONIST},
    "reports": {User.Role.ADMIN, User.Role.DOCTOR, User.Role.RECEPTIONIST, User.Role.LABORATORIAN},
    "prescriptions": {User.Role.ADMIN, User.Role.DOCTOR, User.Role.RECEPTIONIST, User.Role.PHARMACIST},
    "billing": {User.Role.ADMIN, User.Role.RECEPTIONIST, User.Role.ACCOUNTANT},
    "pharmacy": {User.Role.ADMIN, User.Role.PHARMACIST},
    "beds": {User.Role.ADMIN, User.Role.NURSE},
    "nursing": {User.Role.ADMIN, User.Role.NURSE},
    "hr": {User.Role.ADMIN, User.Role.HR},
    "users": {User.Role.ADMIN},
}


SIDEBAR_SECTIONS = [
    {
        "title": "Overview",
        "items": [
            {
                "label": "Dashboard",
                "icon": "layout-dashboard",
                "url_name": "core:dashboard",
                "module": "dashboard",
                "active_app": "core",
                "active_url": "dashboard",
            },
        ],
    },
    {
        "title": "Management",
        "items": [
            {"label": "Doctors", "icon": "stethoscope", "url_name": "doctors:doctor_list", "module": "doctors", "active_app": "doctors"},
            {"label": "Patients", "icon": "users", "url_name": "patients:patient_list", "module": "patients", "active_app": "patients"},
            {"label": "Appointments", "icon": "calendar-days", "url_name": "appointments:appointment_calendar", "module": "appointments", "active_app": "appointments"},
            {"label": "Reports", "icon": "file-text", "url_name": "reports:report_list", "module": "reports", "active_app": "reports"},
            {"label": "Prescriptions", "icon": "pill", "url_name": "prescriptions:prescription_list", "module": "prescriptions", "active_app": "prescriptions"},
            {"label": "Billing", "icon": "credit-card", "url_name": "billing:billing_dashboard", "module": "billing", "active_app": "billing"},
            {
                "label": "Pharmacy",
                "icon": "flask-conical",
                "url_name": "pharmacy:pharmacy_dashboard",
                "module": "pharmacy",
                "active_app": "pharmacy",
                "children": [
                    {"label": "Dashboard", "url_name": "pharmacy:pharmacy_dashboard", "active_url": "pharmacy_dashboard"},
                    {"label": "Medicines", "url_name": "pharmacy:medicine_list", "active_url": "medicine_list"},
                    {"label": "Dispensing", "url_name": "pharmacy:dispensing_list", "active_url": "dispensing_list"},
                    {"label": "Suppliers", "url_name": "pharmacy:supplier_list", "active_url": "supplier_list"},
                    {"label": "Purchases", "url_name": "pharmacy:purchase_list", "active_url": "purchase_list"},
                    {"label": "Sales", "url_name": "pharmacy:sale_list", "active_url": "sale_list"},
                    {"label": "Stock Movements", "url_name": "pharmacy:stock_movement_list", "active_url": "stock_movement_list"},
                    {"label": "Reports", "url_name": "pharmacy:pharmacy_reports", "active_url": "pharmacy_reports"},
                ],
            },
            {"label": "Beds", "icon": "bed", "url_name": "beds:bed_dashboard", "module": "beds", "active_app": "beds"},
            {"label": "Nursing", "icon": "heart-pulse", "url_name": "nursing:nursing_dashboard", "module": "nursing", "active_app": "nursing"},
            {"label": "HR", "icon": "building-2", "url_name": "hr:hr_dashboard", "module": "hr", "active_app": "hr"},
        ],
    },
    {
        "title": "Administration",
        "items": [
            {"label": "Users", "icon": "user-cog", "url_name": "core:user_list", "module": "users", "active_app": "core", "active_url": "user_list"},
            {"label": "Admin Panel", "icon": "settings", "href": "/admin/", "module": "users", "active_app": "admin"},
        ],
    },
]


def can_access_module(user, module_key):
    if not getattr(user, "is_authenticated", False):
        return False
    if getattr(user, "is_superuser", False):
        return True
    return getattr(user, "role", None) in MODULE_ACCESS.get(module_key, set())


def get_sidebar_sections(user):
    sections = []
    for section in SIDEBAR_SECTIONS:
        items = []
        for item in section["items"]:
            if not can_access_module(user, item["module"]):
                continue
            item_data = item.copy()
            if "href" not in item_data:
                item_data["href"] = reverse(item_data["url_name"])
            if item_data.get("children"):
                item_data["children"] = [
                    {
                        **child,
                        "href": child.get("href") or reverse(child["url_name"]),
                    }
                    for child in item_data["children"]
                ]
            items.append(item_data)
        if items:
            sections.append({"title": section["title"], "items": items})
    return sections
