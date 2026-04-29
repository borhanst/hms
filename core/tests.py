from django.contrib.messages import get_messages
from django.contrib.auth import authenticate
from django.test import TestCase
from django.urls import reverse

from core.models import User
from populate_demo_data import DEMO_PASSWORD, ensure_demo_admin


class RoleBasedAccessTests(TestCase):
    user_counter = 0

    def make_user(self, role, username=None, is_superuser=False):
        self.user_counter += 1
        return User.objects.create_user(
            username=username or f"{role.lower()}_{self.user_counter}",
            password="password123",
            role=role,
            is_superuser=is_superuser,
            is_staff=is_superuser,
        )

    def login_as(self, role, username=None, is_superuser=False):
        user = self.make_user(role, username=username, is_superuser=is_superuser)
        self.client.force_login(user)
        return user

    MENU_URLS = {
        "Dashboard": "/",
        "Doctors": "/doctors/",
        "Patients": "/patients/",
        "Appointments": "/appointments/calendar/",
        "Reports": "/reports/",
        "Prescriptions": "/prescriptions/",
        "Billing": "/billing/",
        "Pharmacy": "/pharmacy/",
        "Beds": "/beds/",
        "Nursing": "/nursing/",
        "HR": "/hr/",
        "Users": "/users/",
        "Admin Panel": "/admin/",
    }

    def assert_menu_contains(self, role, expected_labels):
        self.login_as(role)
        response = self.client.get(reverse("core:dashboard"))
        self.assertEqual(response.status_code, 200)
        html = self.sidebar_html(response)
        for label in expected_labels:
            self.assertIn(f'href="{self.MENU_URLS[label]}"', html)

    def assert_menu_omits(self, role, omitted_labels):
        self.login_as(role)
        response = self.client.get(reverse("core:dashboard"))
        self.assertEqual(response.status_code, 200)
        html = self.sidebar_html(response)
        for label in omitted_labels:
            self.assertNotIn(f'href="{self.MENU_URLS[label]}"', html)

    def sidebar_html(self, response):
        html = response.content.decode()
        start = html.index('<nav class="sidebar-nav">')
        end = html.index("</nav>", start)
        return html[start:end]

    def assert_denied_to_dashboard(self, role, url_name):
        self.login_as(role)
        response = self.client.get(reverse(url_name))
        self.assertRedirects(response, reverse("core:dashboard"))
        messages = [str(message) for message in get_messages(response.wsgi_request)]
        self.assertIn("You don't have permission to access this page.", messages)

    def test_receptionist_sidebar_shows_assigned_modules_only(self):
        self.assert_menu_contains(
            User.Role.RECEPTIONIST,
            ["Dashboard", "Doctors", "Patients", "Appointments", "Reports", "Prescriptions", "Billing"],
        )
        self.assert_menu_omits(
            User.Role.RECEPTIONIST,
            ["Pharmacy", "Beds", "Nursing", "HR", "Users", "Admin Panel"],
        )

    def test_pharmacist_sidebar_shows_pharmacy_and_prescriptions_only(self):
        self.assert_menu_contains(User.Role.PHARMACIST, ["Dashboard", "Prescriptions", "Pharmacy"])
        self.assert_menu_omits(
            User.Role.PHARMACIST,
            ["Doctors", "Patients", "Appointments", "Reports", "Billing", "Beds", "Nursing", "HR", "Users"],
        )

    def test_pharmacy_menu_is_collapsed_until_toggled(self):
        self.login_as(User.Role.ADMIN)
        response = self.client.get(reverse("core:dashboard"))
        html = self.sidebar_html(response)

        self.assertIn('x-data="{ open: false }"', html)
        self.assertIn('aria-controls="pharmacy-submenu"', html)
        self.assertNotIn('class="nav-menu-group open"', html)

    def test_pharmacy_menu_expands_on_active_pharmacy_page(self):
        self.login_as(User.Role.ADMIN)
        response = self.client.get(reverse("pharmacy:pharmacy_dashboard"))
        html = self.sidebar_html(response)

        self.assertIn('x-data="{ open: true }"', html)
        self.assertIn('class="nav-menu-group"', html)
        self.assertIn('class="nav-submenu-link active"', html)

    def test_hr_sidebar_shows_hr_only(self):
        self.assert_menu_contains(User.Role.HR, ["Dashboard", "HR"])
        self.assert_menu_omits(
            User.Role.HR,
            ["Doctors", "Patients", "Appointments", "Reports", "Prescriptions", "Billing", "Pharmacy", "Beds", "Nursing", "Users"],
        )

    def test_admin_sidebar_shows_every_module_and_admin_tools(self):
        self.assert_menu_contains(
            User.Role.ADMIN,
            [
                "Dashboard",
                "Doctors",
                "Patients",
                "Appointments",
                "Reports",
                "Prescriptions",
                "Billing",
                "Pharmacy",
                "Beds",
                "Nursing",
                "HR",
                "Users",
                "Admin Panel",
            ],
        )

    def test_non_assigned_module_landing_pages_redirect_to_dashboard(self):
        denied_cases = [
            (User.Role.HR, "patients:patient_list"),
            (User.Role.HR, "billing:billing_dashboard"),
            (User.Role.PHARMACIST, "reports:report_list"),
            (User.Role.ACCOUNTANT, "pharmacy:pharmacy_dashboard"),
            (User.Role.LABORATORIAN, "billing:billing_dashboard"),
            (User.Role.NURSE, "pharmacy:pharmacy_dashboard"),
        ]
        for role, url_name in denied_cases:
            with self.subTest(role=role, url_name=url_name):
                self.client.logout()
                self.assert_denied_to_dashboard(role, url_name)

    def test_admin_can_access_every_module_landing_page(self):
        self.login_as(User.Role.ADMIN)
        url_names = [
            "doctors:doctor_list",
            "patients:patient_list",
            "appointments:appointment_list",
            "reports:report_list",
            "prescriptions:prescription_list",
            "billing:billing_dashboard",
            "pharmacy:pharmacy_dashboard",
            "beds:bed_dashboard",
            "nursing:nursing_dashboard",
            "hr:hr_dashboard",
            "core:user_list",
        ]
        for url_name in url_names:
            with self.subTest(url_name=url_name):
                response = self.client.get(reverse(url_name))
                self.assertEqual(response.status_code, 200)

    def test_laboratorian_can_view_patients_but_cannot_create_them(self):
        self.login_as(User.Role.LABORATORIAN)
        self.assertEqual(self.client.get(reverse("patients:patient_list")).status_code, 200)
        response = self.client.get(reverse("patients:patient_create"))
        self.assertRedirects(response, reverse("core:dashboard"))

    def test_pharmacist_can_view_prescriptions_but_cannot_access_billing(self):
        self.login_as(User.Role.PHARMACIST)
        self.assertEqual(self.client.get(reverse("prescriptions:prescription_list")).status_code, 200)
        response = self.client.get(reverse("billing:billing_dashboard"))
        self.assertRedirects(response, reverse("core:dashboard"))


class DemoAdminAccountTests(TestCase):
    def test_ensure_demo_admin_repairs_login_credentials(self):
        admin = User.objects.create_user(
            username="admin",
            password="wrong-password",
            role=User.Role.RECEPTIONIST,
            is_staff=False,
            is_superuser=False,
            is_active=False,
        )

        ensure_demo_admin()
        admin.refresh_from_db()

        self.assertEqual(admin.role, User.Role.ADMIN)
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.is_active)
        self.assertEqual(authenticate(username="admin", password=DEMO_PASSWORD), admin)
