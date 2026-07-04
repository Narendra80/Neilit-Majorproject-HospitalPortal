from django.core.management.base import BaseCommand
from django.utils import timezone
import datetime
from hospital.models import Doctor, Patient, Appointment, MedicalReport

class Command(BaseCommand):
    help = 'Seeds initial realistic hospital data for demonstration'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE("Checking existing sample data..."))
        if Doctor.objects.exists():
            self.stdout.write(self.style.SUCCESS("Doctors already exist. Skipping seed."))
            return

        doctors_data = [
            {
                'name': 'Sarah Jenkins',
                'department': 'CARDIO',
                'specialization': 'Interventional Cardiology & Heart Failure Specialist',
                'consultation_fee': 120.00,
                'available_days': 'Mon, Wed, Fri',
                'experience_years': 15,
                'room_number': 'Suite 302-C'
            },
            {
                'name': 'Michael Chen',
                'department': 'CARDIO',
                'specialization': 'Electrophysiology & Echocardiography',
                'consultation_fee': 110.00,
                'available_days': 'Tue, Thu, Sat',
                'experience_years': 11,
                'room_number': 'Suite 304-C'
            },
            {
                'name': 'Emily Rodriguez',
                'department': 'PEDIA',
                'specialization': 'General Pediatrics & Neonatal Care',
                'consultation_fee': 90.00,
                'available_days': 'Mon - Fri',
                'experience_years': 8,
                'room_number': 'Wing A-102'
            },
            {
                'name': 'David Oconnor',
                'department': 'PEDIA',
                'specialization': 'Pediatric Allergy & Immunology',
                'consultation_fee': 95.00,
                'available_days': 'Mon, Tue, Thu',
                'experience_years': 12,
                'room_number': 'Wing A-105'
            },
            {
                'name': 'James Miller',
                'department': 'ORTHO',
                'specialization': 'Joint Replacement & Sports Medicine Surgery',
                'consultation_fee': 150.00,
                'available_days': 'Mon, Wed, Thu',
                'experience_years': 18,
                'room_number': 'Ortho Center 401'
            },
            {
                'name': 'Lisa Thorne',
                'department': 'ORTHO',
                'specialization': 'Spine Surgery & Pediatric Orthopedics',
                'consultation_fee': 140.00,
                'available_days': 'Tue, Fri, Sat',
                'experience_years': 14,
                'room_number': 'Ortho Center 405'
            },
            {
                'name': 'Robert Vance',
                'department': 'NEURO',
                'specialization': 'Neuromuscular Disorders & Stroke Rehabilitation',
                'consultation_fee': 160.00,
                'available_days': 'Mon, Tue, Wed, Fri',
                'experience_years': 20,
                'room_number': 'Neuro Lab 502'
            },
            {
                'name': 'Priya Sharma',
                'department': 'NEURO',
                'specialization': 'Clinical Neurophysiology & Epilepsy Care',
                'consultation_fee': 145.00,
                'available_days': 'Wed, Thu, Sat',
                'experience_years': 10,
                'room_number': 'Neuro Lab 508'
            },
        ]

        created_doctors = []
        for d in doctors_data:
            doc = Doctor.objects.create(**d)
            created_doctors.append(doc)

        self.stdout.write(self.style.SUCCESS(f"Created {len(created_doctors)} doctors across all departments!"))

        # Create sample Patients
        p1 = Patient.objects.create(
            name="Johnathan Tyler",
            phone="9876543210",
            email="j.tyler@example.com",
            age=34,
            gender="M",
            blood_group="A+",
            medical_history="Mild hypertension, allergic to penicillin"
        )
        p2 = Patient.objects.create(
            name="Elena Rostova",
            phone="9812345678",
            email="elena.r@example.com",
            age=28,
            gender="F",
            blood_group="O-",
            medical_history="No chronic conditions. Regular annual physical checkup."
        )

        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(days=1)
        yesterday = today - datetime.timedelta(days=1)

        # Create Sample Appointments
        app1 = Appointment.objects.create(
            patient_name=p1.name,
            patient_phone=p1.phone,
            doctor=created_doctors[0], # Dr. Sarah Jenkins (Cardio)
            appointment_date=tomorrow,
            time_slot="10:00 AM - 10:30 AM",
            reason="Routine cardiac evaluation and ECG review",
            status="CONFIRMED"
        )

        app2 = Appointment.objects.create(
            patient_name=p2.name,
            patient_phone=p2.phone,
            doctor=created_doctors[6], # Dr. Robert Vance (Neuro)
            appointment_date=tomorrow,
            time_slot="11:30 AM - 12:00 PM",
            reason="Frequent chronic migraines and dizziness consultation",
            status="PENDING"
        )

        app3 = Appointment.objects.create(
            patient_name="Alex Mercer",
            patient_phone="9551122334",
            doctor=created_doctors[4], # Dr. James Miller (Ortho)
            appointment_date=yesterday,
            time_slot="02:00 PM - 02:30 PM",
            reason="Post-workout right knee swelling and stiffness",
            status="COMPLETED"
        )

        # Create sample Medical Report for the completed appointment
        MedicalReport.objects.create(
            appointment=app3,
            patient_name="Alex Mercer",
            doctor=created_doctors[4],
            diagnosis="Grade 1 Meniscal Strain",
            prescription="1. Ibuprofen 400mg TID for 5 days\n2. Ice compress 20 mins twice daily\n3. Knee support brace during physical activity",
            recommended_tests="MRI Right Knee if pain persists after 2 weeks",
            doctor_notes="Patient advised to avoid high-impact running or squatting for at least 14 days."
        )

        self.stdout.write(self.style.SUCCESS("Successfully seeded sample patients, appointments, and medical reports!"))
