HOSPITAL PORTAL

Dark Mode and light mode with multiple webpages in one and sections all 

🏥 Capstone Project 1: Hospital & Patient Appointment Management Portal
📌 1. Project Overview & Scenario
In modern healthcare, hospitals require streamlined systems to manage doctor schedules, patient appointments, and consultation records. Students will build a responsive Hospital Appointment Management Portal where patients can browse available doctors by specialization, book time slots, and view medical consultation status, while administrators and doctors manage schedules.

🎯 2. Core Functional Requirements
Frontend Requirements (HTML, CSS, JS, Bootstrap 5)
Responsive UI: Built with Bootstrap 5 (Cards, Modals, Badges, and Alerts).
Dynamic Doctor Filter: JavaScript-powered instant filtering of doctors by department (Cardiology, Pediatrics, Orthopedics, Neurology) without reloading the page.
Interactive Appointment Slot Selector: A JavaScript calendar/time-picker that highlights booked vs. available consultation slots.
Status Badges: Visual status indicators using Bootstrap color classes (badge bg-warning for Pending, bg-success for Confirmed, bg-secondary for Completed).
Backend Requirements (Django MVT & ORM)
Models: Doctor, Patient, Appointment, and MedicalReport.
Views:
DoctorListView: Displays all doctors with search and department filtering.
AppointmentCreateView: Handles booking form submissions with validation (preventing double-booking).
PatientDashboardView: Shows the patient's upcoming and past appointments.
AdminStatusUpdateView: Allows staff to confirm or cancel appointments.
Security: Form validation, session management, and {% csrf_token %} protection.
🛢️ 3. Database Schema & Starter Models (models.py)
from django.db import models
from django.contrib.auth.models import User

class Doctor(models.Model):
    DEPARTMENTS = [
        ('CARDIO', 'Cardiology'),
        ('PEDIA', 'Pediatrics'),
        ('ORTHO', 'Orthopedics'),
        ('NEURO', 'Neurology'),
    ]
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=10, choices=DEPARTMENTS)
    specialization = models.CharField(max_length=150)
    consultation_fee = models.DecimalField(max_digits=8, decimal_places=2)
    available_days = models.CharField(max_length=100, default="Mon - Fri")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Dr. {self.name} ({self.get_department_display()})"

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending Confirmation'),
        ('CONFIRMED', 'Confirmed'),
        ('COMPLETED', 'Consultation Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    patient_name = models.CharField(max_length=100)
    patient_phone = models.CharField(max_length=15)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    appointment_date = models.DateField()
    time_slot = models.CharField(max_length=20, help_text="e.g. 10:00 AM - 10:30 AM")
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['doctor', 'appointment_date', 'time_slot']

    def __str__(self):
        return f"{self.patient_name} with Dr. {self.doctor.name} on {self.appointment_date}"
⚡ 4. Render Cloud Deployment Guide (Under 512MB Limit)
To ensure this application deploys smoothly on Render's Free Tier (512MB RAM & Ephemeral Storage), follow these exact configurations:

1️⃣ Production settings.py Setup
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-dev-key')
DEBUG = os.environ.get('RENDER', 'False') == 'True'

ALLOWED_HOSTS = ['*']
CSRF_TRUSTED_ORIGINS = ['https://*.onrender.com']

# Static Files via WhiteNoise (Zero memory bloat)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Place right after SecurityMiddleware
    # ... other middlewares ...
]
2️⃣ Blueprint (render.yaml)
Create this file in your root folder for 1-click deployment:

services:
  - type: web
    name: hospital-portal-demo
    runtime: python
    rootDir: .
    buildCommand: "pip install -r requirements.txt && python manage.py collectstatic --no-input && python manage.py migrate && python create_superuser.py"
    startCommand: "python manage.py migrate && python create_superuser.py && gunicorn myproject.wsgi:application"
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: WEB_CONCURRENCY
        value: 2  # IMPORTANT: Caps Gunicorn workers at 2 to stay under 512MB RAM!
👤 5. Automatic Superuser Creation (create_superuser.py)
Because Render Free Tier containers reset ephemeral SQLite storage when they restart, and interactive SSH terminal access is restricted, include this script in your project root:

# create_superuser.py
import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

try:
    import django
    django.setup()
    from django.contrib.auth import get_user_model
except Exception as e:
    print(f"[-] Django setup failed: {e}")
    sys.exit(1)

def create_admin():
    User = get_user_model()
    username = os.environ.get('ADMIN_USERNAME', 'admin')
    email = os.environ.get('ADMIN_EMAIL', 'admin@hospital.com')
    password = os.environ.get('ADMIN_PASSWORD', 'admin123')

    print("[*] Checking / Creating Automatic Admin Superuser...")
    try:
        # Using db_manager to correctly handle manager calls in ORM
        if not User.objects.db_manager('default').filter(username=username).exists():
            User.objects.db_manager('default').create_superuser(username=username, email=email, password=password)
            print(f"[+] Superuser '{username}' created successfully! (Password: {password})")
        else:
            print(f"[*] Superuser '{username}' already exists.")
    except Exception as e:
        print(f"[-] Error creating superuser: {e}")

if __name__ == '__main__':
    create_admin()
