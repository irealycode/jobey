from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('employer/dashboard/', views.EmployerDashboardView.as_view(), name='employer_dashboard'),
    path('job-seeker/dashboard/', views.JobSeekerDashboardView.as_view(), name='job_seeker_dashboard'),
    path('company/edit/', views.CompanyUpdateView.as_view(), name='edit_company'),
    path('profile/edit/', views.ProfileUpdateView.as_view(), name='edit_profile'),
    path('profile/<int:pk>/', views.PublicProfileView.as_view(), name='public_profile'),
    path('company/<int:pk>/', views.CompanyDetailView.as_view(), name='company_detail'),
]