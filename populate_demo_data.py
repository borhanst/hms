import os
import django
from datetime import date, timedelta
import random

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hms.settings")
django.setup()

from core.models import User
from doctors.models import Doctor
from patients.models import Patient
from reports.models import DiagnosticReport
from prescriptions.models import Prescription, PrescriptionItem

DEMO_PASSWORD = "password123"


def ensure_demo_admin():
    admin, _ = User.objects.get_or_create(
        username="admin",
        defaults={
            "first_name": "Admin",
            "last_name": "User",
            "email": "admin@hms.local",
            "role": User.Role.ADMIN,
            "is_staff": True,
            "is_superuser": True,
        },
    )
    admin.first_name = admin.first_name or "Admin"
    admin.last_name = admin.last_name or "User"
    admin.email = admin.email or "admin@hms.local"
    admin.role = User.Role.ADMIN
    admin.is_staff = True
    admin.is_superuser = True
    admin.is_active = True
    admin.set_password(DEMO_PASSWORD)
    admin.save()
    return admin


def create_demo_data():
    print("Clearing old data...")
    # Keep admin, delete others
    User.objects.exclude(username="admin").delete()
    Patient.objects.all().delete()

    print("Ensuring admin demo account...")
    ensure_demo_admin()

    print("Creating doctors...")
    doc_users = [
        {"username": "doctor_john", "first_name": "John", "last_name": "Smith", "role": "DOCTOR"},
        {"username": "doctor_sarah", "first_name": "Sarah", "last_name": "Connor", "role": "DOCTOR"},
        {"username": "doctor_ali", "first_name": "Ali", "last_name": "Khan", "role": "DOCTOR"},
    ]

    doctors = []
    specializations = [
        ("Cardiology", "CARDIOLOGY"), 
        ("Neurology", "NEUROLOGY"), 
        ("General Medicine", "GENERAL")
    ]
    
    for i, ud in enumerate(doc_users):
        u = User.objects.create_user(
            username=ud["username"],
            password=DEMO_PASSWORD,
            first_name=ud["first_name"],
            last_name=ud["last_name"],
            email=f"{ud['username']}@hms.local",
            role=ud["role"]
        )
        spec, dept = specializations[i]
        doc = Doctor.objects.create(
            user=u,
            specialization=spec,
            department=dept,
            phone=f"+8801700{random.randint(100000, 999999)}",
            bio=f"Experienced {spec} specialist with 10+ years of experience.",
            consultation_fee=1000 + (i * 200)
        )
        doctors.append(doc)

    print("Creating Receptionist...")
    User.objects.create_user(
        username="receptionist1",
        password=DEMO_PASSWORD,
        first_name="Alice",
        last_name="Johnson",
        role="RECEPTIONIST"
    )

    print("Creating other staff...")
    extra_staff = [
        ("nurse1", "Nurse", "Nightingale", "NURSE"),
        ("pharmacist1", "Pharma", "Care", "PHARMACIST"),
        ("laboratorian1", "Lab", "Tech", "LABORATORIAN"),
        ("accountant1", "Money", "Manager", "ACCOUNTANT"),
        ("hr1", "HR", "Director", "HR"),
    ]
    for un, fn, ln, r in extra_staff:
        User.objects.create_user(
            username=un, password=DEMO_PASSWORD, first_name=fn, last_name=ln, role=r
        )

    print("Creating patients...")
    p_names = [
        ("Kamal", "Hossain", "M"), ("Rina", "Akter", "F"), ("Rahim", "Uddin", "M"), 
        ("Fatema", "Begum", "F"), ("Sajib", "Hasan", "M"), ("Nadia", "Islam", "F")
    ]
    
    patients = []
    blood_groups = ["A+", "B+", "O+", "O-", "AB+"]
    for first, last, gender in p_names:
        p = Patient.objects.create(
            first_name=first,
            last_name=last,
            gender=gender,
            date_of_birth=date(1990 - random.randint(0, 30), random.randint(1, 12), random.randint(1, 28)),
            age=random.randint(20, 60),
            phone=f"+8801800{random.randint(100000, 999999)}",
            blood_group=random.choice(blood_groups),
            address=f"House {random.randint(1, 100)}, Road {random.randint(1, 20)}, Dhaka",
            assigned_doctor=random.choice(doctors)
        )
        patients.append(p)

    print("Creating reports...")
    tests = [
        ("Complete Blood Count", "BLOOD"), ("Chest X-Ray", "XRAY"), 
        ("Urine Routine", "URINE"), ("Lipid Profile", "BLOOD"), 
        ("Brain MRI", "MRI"), ("Abdomen Ultrasound", "ULTRASOUND")
    ]
    statuses = ["COMPLETED", "IN_PROGRESS", "PENDING"]
    
    for i in range(10):
        test_name, category = random.choice(tests)
        status = random.choice(statuses)
        DiagnosticReport.objects.create(
            patient=random.choice(patients),
            doctor=random.choice(doctors),
            test_name=test_name,
            test_category=category,
            status=status,
            result="Results indicate normal values." if status == "COMPLETED" else "",
            notes="Sample collected."
        )

    print("Creating prescriptions...")
    medicines = [
        ("Paracetamol 500mg", "1 tablet", "TDS"), 
        ("Amoxicillin 500mg", "1 capsule", "BD"), 
        ("Omeprazole 20mg", "1 capsule", "OD"), 
        ("Cetirizine 10mg", "1 tablet", "OD"), 
        ("Ibuprofen 400mg", "1 tablet", "SOS")
    ]
    
    for i in range(8):
        patient = random.choice(patients)
        doctor = patient.assigned_doctor
        rx = Prescription.objects.create(
            patient=patient,
            doctor=doctor,
            diagnosis=random.choice(["Viral Fever", "Hypertension", "Migraine", "Gastric Ulcer", "Common Cold"]),
            notes="Take rest and drink plenty of water.",
            follow_up_date=date.today() + timedelta(days=7)
        )
        
        # Add 1-3 medicines
        for _ in range(random.randint(1, 3)):
            med, dos, freq = random.choice(medicines)
            PrescriptionItem.objects.create(
                prescription=rx,
                medicine_name=med,
                dosage=dos,
                frequency=freq,
                duration=f"{random.randint(3, 10)} days",
                instructions="After meal" if random.choice([True, False]) else "Before meal"
            )

    print("Done!")

if __name__ == "__main__":
    create_demo_data()
