from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import UpdateView, DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CustomUser, Company, Profile
from .forms import CompanyForm, ProfileForm

class EmployerDashboardView(LoginRequiredMixin, DetailView):
    model = CustomUser
    template_name = 'users/employer_dashboard.html'
    context_object_name = 'user'
    
    def get_object(self):
        return self.request.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['jobs'] = self.request.user.jobs.all()
        return context

class JobSeekerDashboardView(LoginRequiredMixin, DetailView):
    model = CustomUser
    template_name = 'users/job_seeker_dashboard.html'
    context_object_name = 'user'
    
    def get_object(self):
        return self.request.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['applications'] = self.request.user.applications.all()
        return context

@login_required
def dashboard(request):
    if request.user.user_type == 'employer':
        return redirect('employer_dashboard')
    else:
        return redirect('job_seeker_dashboard')

class CompanyUpdateView(LoginRequiredMixin, UpdateView):
    model = Company
    form_class = CompanyForm
    template_name = 'users/company_form.html'
    success_url = reverse_lazy('employer_dashboard')
    
    def get_object(self):
        return self.request.user.company
    
    def form_valid(self, form):
        messages.success(self.request, 'Company information updated successfully!')
        return super().form_valid(form)

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = 'users/profile_form.html'
    success_url = reverse_lazy('job_seeker_dashboard')
    
    def get_object(self):
        return self.request.user.profile
    
    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)

class PublicProfileView(DetailView):
    model = CustomUser
    template_name = 'users/public_profile.html'
    context_object_name = 'profile_user'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        if user.user_type == 'employer':
            context['company'] = user.company
        else:
            context['profile'] = user.profile
        return context

class CompanyDetailView(DetailView):
    model = Company
    template_name = 'users/company_detail.html'
    context_object_name = 'company'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['jobs'] = self.object.user.jobs.all()
        return context