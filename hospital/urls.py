from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('doctors/', views.DoctorListView.as_view(), name='doctor_list'),
    path('book/', views.AppointmentCreateView.as_view(), name='appointment_create'),
    path('dashboard/', views.PatientDashboardView.as_view(), name='patient_dashboard'),
    path('staff/status/', views.AdminStatusUpdateView.as_view(), name='admin_status_update'),
    path('api/booked-slots/', views.api_booked_slots, name='api_booked_slots'),
]
