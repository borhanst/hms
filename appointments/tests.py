from datetime import date, time

from django.test import TestCase
from django.urls import reverse

from appointments.models import Appointment
from core.models import User
from doctors.models import Doctor
from patients.models import Patient


class AppointmentCalendarTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username="admin", password="password123", role=User.Role.ADMIN)
        self.hr = User.objects.create_user(username="hr", password="password123", role=User.Role.HR)
        self.doctor_user = User.objects.create_user(
            username="doctor",
            password="password123",
            role=User.Role.DOCTOR,
            first_name="Amina",
            last_name="Khan",
        )
        self.other_doctor_user = User.objects.create_user(
            username="other_doctor",
            password="password123",
            role=User.Role.DOCTOR,
            first_name="Rafiq",
            last_name="Hasan",
        )
        self.doctor = Doctor.objects.create(user=self.doctor_user, specialization="Cardiology")
        self.other_doctor = Doctor.objects.create(user=self.other_doctor_user, specialization="Medicine")
        self.patient = Patient.objects.create(first_name="Nadia", last_name="Rahman", gender="F", phone="01700000001")
        self.other_patient = Patient.objects.create(first_name="Omar", last_name="Ali", gender="M", phone="01700000002")

    def appointment(self, *, doctor=None, patient=None, day=None, start=time(9, 0), end=time(9, 30), status="SCHEDULED"):
        return Appointment.objects.create(
            patient=patient or self.patient,
            doctor=doctor or self.doctor,
            date=day or date(2026, 4, 28),
            start_time=start,
            end_time=end,
            status=status,
            reason="Follow up",
            created_by=self.admin,
        )

    def test_calendar_defaults_to_day_mode(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse("appointments:appointment_calendar"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["calendar_mode"], "day")
        self.assertIn("day_appointments", response.context)

    def test_day_mode_shows_selected_date_appointments_ordered_by_start_time(self):
        later = self.appointment(start=time(14, 0), end=time(14, 30))
        earlier = self.appointment(patient=self.other_patient, start=time(8, 0), end=time(8, 30))
        self.appointment(day=date(2026, 4, 29), start=time(7, 0), end=time(7, 30))

        self.client.force_login(self.admin)
        response = self.client.get(reverse("appointments:appointment_calendar"), {"mode": "day", "date": "2026-04-28"})

        self.assertEqual(response.context["selected_date"], date(2026, 4, 28))
        self.assertEqual(list(response.context["day_appointments"]), [earlier, later])
        self.assertContains(response, "Nadia Rahman")
        self.assertContains(response, "Omar Ali")

    def test_week_mode_contains_only_selected_monday_to_sunday_range(self):
        in_week = self.appointment(day=date(2026, 4, 29))
        self.appointment(day=date(2026, 5, 4))

        self.client.force_login(self.admin)
        response = self.client.get(reverse("appointments:appointment_calendar"), {"mode": "week", "week_start": "2026-04-30"})

        self.assertEqual(response.context["calendar_mode"], "week")
        self.assertEqual(response.context["start_date"], date(2026, 4, 27))
        self.assertEqual(response.context["end_date"], date(2026, 5, 3))
        self.assertIn(in_week, response.context["appointments_by_date"][date(2026, 4, 29)])

    def test_calendar_navigation_links_use_correct_day_and_week_dates(self):
        self.client.force_login(self.admin)
        day_response = self.client.get(reverse("appointments:appointment_calendar"), {"mode": "day", "date": "2026-04-28"})
        self.assertContains(day_response, "date=2026-04-27")
        self.assertContains(day_response, "date=2026-04-29")
        self.assertContains(day_response, "mode=week&week_start=2026-04-27")

        week_response = self.client.get(reverse("appointments:appointment_calendar"), {"mode": "week", "week_start": "2026-04-27"})
        self.assertContains(week_response, "week_start=2026-04-20")
        self.assertContains(week_response, "week_start=2026-05-04")
        self.assertContains(week_response, "mode=day&date=2026-04-27")

    def test_doctor_calendar_shows_only_their_appointments(self):
        own = self.appointment(doctor=self.doctor, patient=self.patient)
        self.appointment(doctor=self.other_doctor, patient=self.other_patient)

        self.client.force_login(self.doctor_user)
        response = self.client.get(reverse("appointments:appointment_calendar"), {"mode": "day", "date": "2026-04-28"})

        self.assertEqual(list(response.context["day_appointments"]), [own])
        self.assertContains(response, "Nadia Rahman")
        self.assertNotContains(response, "Omar Ali")

    def test_non_appointment_roles_are_redirected(self):
        self.client.force_login(self.hr)
        response = self.client.get(reverse("appointments:appointment_calendar"))
        self.assertRedirects(response, reverse("core:dashboard"))
