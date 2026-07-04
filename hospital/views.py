from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, TemplateView
from django.views import View
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
import datetime
from .models import Doctor, Patient, Appointment, MedicalReport

class HomeView(TemplateView):
    template_name = 'hospital/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_doctors'] = Doctor.objects.filter(is_active=True).count()
        context['departments'] = Doctor.DEPARTMENTS
        context['featured_doctors'] = Doctor.objects.filter(is_active=True)[:4]
        context['total_appointments'] = Appointment.objects.count()
        return context


class DoctorListView(ListView):
    model = Doctor
    template_name = 'hospital/doctor_list.html'
    context_object_name = 'doctors'

    def get_queryset(self):
        queryset = Doctor.objects.filter(is_active=True)
        dept = self.request.GET.get('dept')
        search = self.request.GET.get('search')
        if dept and dept in dict(Doctor.DEPARTMENTS):
            queryset = queryset.filter(department=dept)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(specialization__icontains=search)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['departments'] = Doctor.DEPARTMENTS
        context['current_dept'] = self.request.GET.get('dept', 'ALL')
        context['search_query'] = self.request.GET.get('search', '')
        return context


class AppointmentCreateView(View):
    template_name = 'hospital/appointment_create.html'

    def get(self, request):
        doctors = Doctor.objects.filter(is_active=True)
        selected_doc_id = request.GET.get('doctor_id')
        time_slots = [
            "09:00 AM - 09:30 AM", "09:30 AM - 10:00 AM",
            "10:00 AM - 10:30 AM", "10:30 AM - 11:00 AM",
            "11:00 AM - 11:30 AM", "11:30 AM - 12:00 PM",
            "02:00 PM - 02:30 PM", "02:30 PM - 03:00 PM",
            "03:00 PM - 03:30 PM", "03:30 PM - 04:00 PM",
            "04:00 PM - 04:30 PM", "04:30 PM - 05:00 PM"
        ]
        context = {
            'doctors': doctors,
            'selected_doc_id': int(selected_doc_id) if selected_doc_id and selected_doc_id.isdigit() else None,
            'time_slots': time_slots,
            'today': datetime.date.today().strftime('%Y-%m-%d'),
        }
        return render(request, self.template_name, context)

    def post(self, request):
        patient_name = request.POST.get('patient_name', '').strip()
        patient_phone = request.POST.get('patient_phone', '').strip()
        doctor_id = request.POST.get('doctor')
        appointment_date = request.POST.get('appointment_date')
        time_slot = request.POST.get('time_slot')
        reason = request.POST.get('reason', '').strip()

        doctors = Doctor.objects.filter(is_active=True)
        time_slots = [
            "09:00 AM - 09:30 AM", "09:30 AM - 10:00 AM",
            "10:00 AM - 10:30 AM", "10:30 AM - 11:00 AM",
            "11:00 AM - 11:30 AM", "11:30 AM - 12:00 PM",
            "02:00 PM - 02:30 PM", "02:30 PM - 03:00 PM",
            "03:00 PM - 03:30 PM", "03:30 PM - 04:00 PM",
            "04:00 PM - 04:30 PM", "04:30 PM - 05:00 PM"
        ]

        if not (patient_name and patient_phone and doctor_id and appointment_date and time_slot):
            messages.error(request, "Please fill in all required fields and select a consultation slot.")
            return render(request, self.template_name, {
                'doctors': doctors, 'time_slots': time_slots,
                'today': datetime.date.today().strftime('%Y-%m-%d'),
                'form_data': request.POST
            })

        doctor = get_object_or_404(Doctor, id=doctor_id)

        # Double booking check
        if Appointment.objects.filter(doctor=doctor, appointment_date=appointment_date, time_slot=time_slot).exclude(status='CANCELLED').exists():
            messages.error(request, f"Dr. {doctor.name} is already booked for {time_slot} on {appointment_date}. Please select another slot.")
            return render(request, self.template_name, {
                'doctors': doctors, 'time_slots': time_slots,
                'today': datetime.date.today().strftime('%Y-%m-%d'),
                'form_data': request.POST
            })

        # Ensure Patient profile exists or update
        Patient.objects.get_or_create(
            phone=patient_phone,
            defaults={'name': patient_name}
        )

        appointment = Appointment.objects.create(
            patient_name=patient_name,
            patient_phone=patient_phone,
            doctor=doctor,
            appointment_date=appointment_date,
            time_slot=time_slot,
            reason=reason,
            status='PENDING'
        )

        messages.success(request, f"Appointment successfully booked with Dr. {doctor.name} on {appointment_date} ({time_slot})! Your confirmation reference ID is #{appointment.id}.")
        return redirect('patient_dashboard')


class PatientDashboardView(ListView):
    model = Appointment
    template_name = 'hospital/patient_dashboard.html'
    context_object_name = 'appointments'

    def get_queryset(self):
        phone = self.request.GET.get('phone', '').strip()
        if phone:
            return Appointment.objects.filter(patient_phone=phone)
        return Appointment.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        phone = self.request.GET.get('phone', '').strip()
        context['search_phone'] = phone
        today = datetime.date.today()
        qs = self.get_queryset()
        context['upcoming_appointments'] = qs.filter(appointment_date__gte=today).exclude(status='CANCELLED')
        context['past_appointments'] = qs.filter(Q(appointment_date__lt=today) | Q(status='CANCELLED') | Q(status='COMPLETED'))
        context['total_count'] = qs.count()
        return context


class AdminStatusUpdateView(View):
    template_name = 'hospital/admin_status_update.html'

    def get(self, request):
        status_filter = request.GET.get('status', 'ALL')
        dept_filter = request.GET.get('dept', 'ALL')
        appointments = Appointment.objects.all()

        if status_filter != 'ALL':
            appointments = appointments.filter(status=status_filter)
        if dept_filter != 'ALL':
            appointments = appointments.filter(doctor__department=dept_filter)

        context = {
            'appointments': appointments,
            'departments': Doctor.DEPARTMENTS,
            'status_choices': Appointment.STATUS_CHOICES,
            'current_status': status_filter,
            'current_dept': dept_filter,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        app_id = request.POST.get('appointment_id')
        new_status = request.POST.get('status')
        if app_id and new_status in dict(Appointment.STATUS_CHOICES):
            app = get_object_or_404(Appointment, id=app_id)
            app.status = new_status
            app.save()
            messages.success(request, f"Appointment #{app.id} status updated to {app.get_status_display()}.")
        else:
            messages.error(request, "Invalid status update request.")
        return redirect('admin_status_update')


def api_booked_slots(request):
    """AJAX endpoint for JavaScript calendar slot selector to check booked times"""
    doctor_id = request.GET.get('doctor_id')
    date_str = request.GET.get('date')
    if not (doctor_id and date_str):
        return JsonResponse({'booked_slots': []})
    
    booked = Appointment.objects.filter(
        doctor_id=doctor_id,
        appointment_date=date_str
    ).exclude(status='CANCELLED').values_list('time_slot', flat=True)
    
    return JsonResponse({'booked_slots': list(booked)})
