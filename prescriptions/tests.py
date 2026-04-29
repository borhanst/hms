from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from core.models import User
from doctors.models import Doctor
from patients.models import Patient
from pharmacy.models import Medicine

from .forms import PrescriptionItemForm
from .models import Prescription, PrescriptionItem


class PrescriptionMedicineSelectorTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="doctor",
            password="password123",
            role=User.Role.DOCTOR,
            first_name="Ibrahim",
            last_name="Khan",
        )
        self.doctor = Doctor.objects.create(
            user=self.user,
            specialization="Medicine",
            department="GENERAL",
            consultation_fee=Decimal("500.00"),
        )
        self.patient = Patient.objects.create(
            first_name="Ayesha",
            last_name="Rahman",
            gender="F",
            phone="01700000000",
            age=32,
        )
        self.medicine = Medicine.objects.create(
            name="Napa Extra",
            generic_name="Paracetamol",
            category="TABLET",
            manufacturer="Beximco",
            stock=100,
            unit_price=Decimal("12.50"),
            reorder_level=10,
        )

    def login(self):
        self.client.force_login(self.user)

    def test_prescription_item_form_defaults_quantity_to_one(self):
        form = PrescriptionItemForm()

        self.assertEqual(form.fields["quantity"].initial, 1)

    def test_medicine_search_returns_matching_medicines_with_prices(self):
        Medicine.objects.create(
            name="Napa",
            generic_name="Paracetamol",
            category="TABLET",
            manufacturer="Beximco",
            stock=50,
            unit_price=Decimal("5.00"),
            reorder_level=10,
        )
        self.login()

        response = self.client.get(reverse("prescriptions:medicine_search"), {"q": "napa"})

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertGreaterEqual(len(payload), 2)
        self.assertEqual(payload[0]["name"], "Napa")
        self.assertEqual(payload[0]["unit_price"], "5.00")

    def test_prescription_create_page_renders_medicine_search_ui(self):
        self.login()

        response = self.client.get(reverse("prescriptions:prescription_create"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-medicine-search-url=')
        self.assertContains(response, 'data-role="medicine-search"')
        self.assertContains(response, 'data-role="medicine-unit-price"')
        self.assertContains(response, 'data-role="medicine-total"')

    def test_prescription_create_saves_selected_medicine_quantity_and_total(self):
        self.login()

        response = self.client.post(
            reverse("prescriptions:prescription_create"),
            {
                "patient": self.patient.pk,
                "doctor": self.doctor.pk,
                "diagnosis": "Fever",
                "status": "ACTIVE",
                "notes": "",
                "follow_up_date": "",
                "items-TOTAL_FORMS": "1",
                "items-INITIAL_FORMS": "0",
                "items-MIN_NUM_FORMS": "0",
                "items-MAX_NUM_FORMS": "1000",
                "items-0-medicine": self.medicine.pk,
                "items-0-medicine_search": self.medicine.name,
                "items-0-dosage": "500 mg",
                "items-0-quantity": "3",
                "items-0-unit_price": "12.50",
                "items-0-frequency": "OD",
                "items-0-duration": "5 days",
                "items-0-instructions": "After meals",
            },
        )

        prescription = Prescription.objects.get()
        self.assertRedirects(response, reverse("prescriptions:prescription_detail", args=[prescription.pk]))
        item = PrescriptionItem.objects.get(prescription=prescription)
        self.assertEqual(item.medicine, self.medicine)
        self.assertEqual(item.medicine_name, "Napa Extra")
        self.assertEqual(item.quantity, 3)
        self.assertEqual(item.unit_price, Decimal("12.50"))
        self.assertEqual(item.total, Decimal("37.50"))

    def test_legacy_item_keeps_display_name_without_medicine_relation(self):
        prescription = Prescription.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            diagnosis="Legacy entry",
        )
        item = PrescriptionItem.objects.create(
            prescription=prescription,
            medicine_name="Legacy Medicine",
            dosage="1 tablet",
            quantity=2,
            unit_price=Decimal("8.00"),
            frequency="OD",
            duration="3 days",
            instructions="",
        )

        self.assertIsNone(item.medicine)
        self.assertEqual(item.display_medicine_name, "Legacy Medicine")
        self.assertEqual(item.total, Decimal("16.00"))
