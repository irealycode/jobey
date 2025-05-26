from django.urls import path
from . import views

urlpatterns = [
    path('', views.JobListView.as_view(), name='job_list'),
    path('<int:pk>/', views.JobDetailView.as_view(), name='job_detail'),
    path('create/', views.JobCreateView.as_view(), name='job_create'),
    path('<int:pk>/edit/', views.JobUpdateView.as_view(), name='job_edit'),
    path('<int:pk>/delete/', views.JobDeleteView.as_view(), name='job_delete'),
    path('<int:pk>/apply/', views.apply_for_job, name='apply_for_job'),
    path('application/<int:pk>/', views.ApplicationDetailView.as_view(), name='application_detail'),
    path('application/<int:pk>/status/<str:status>/', views.update_application_status, name='update_application_status'),
    path('application/<int:pk>/withdraw/', views.withdraw_application, name='withdraw_application'),
]