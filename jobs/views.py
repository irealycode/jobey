from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Job, JobApplication
from .forms import JobForm, JobApplicationForm, JobSearchForm
from users.models import CustomUser

class EmployerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.user_type == 'employer'
    
    def handle_no_permission(self):
        messages.error(self.request, "Only employers can access this page.")
        return redirect('home')

class JobSeekerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.user_type == 'job_seeker'
    
    def handle_no_permission(self):
        messages.error(self.request, "Only job seekers can access this page.")
        return redirect('home')

class JobListView(ListView):
    model = Job
    template_name = 'jobs/job_list.html'
    context_object_name = 'jobs'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Job.objects.filter(is_active=True)
        form = JobSearchForm(self.request.GET)
        
        if form.is_valid():
            keyword = form.cleaned_data.get('keyword')
            location = form.cleaned_data.get('location')
            job_types = form.cleaned_data.get('job_type')
            experience_levels = form.cleaned_data.get('experience_level')
            min_salary = form.cleaned_data.get('min_salary')
            sort_by = form.cleaned_data.get('sort_by')
            
            if keyword:
                queryset = queryset.filter(
                    Q(title__icontains=keyword) | 
                    Q(description__icontains=keyword) |
                    Q(company__name__icontains=keyword)
                )
            
            if location:
                queryset = queryset.filter(location__icontains=location)
            
            if job_types:
                queryset = queryset.filter(job_type__in=job_types)
            
            if experience_levels:
                queryset = queryset.filter(experience_level__in=experience_levels)
            
            if min_salary:
                queryset = queryset.filter(salary_min__gte=min_salary)
            
            if sort_by == 'salary_high':
                queryset = queryset.order_by('-salary_max', '-salary_min')
            elif sort_by == 'salary_low':
                queryset = queryset.order_by('salary_min', 'salary_max')
            elif sort_by == 'relevant':
                queryset = queryset.order_by('-created_at')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = JobSearchForm(self.request.GET)
        return context

class JobDetailView(DetailView):
    model = Job
    template_name = 'jobs/job_detail.html'
    context_object_name = 'job'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            if self.request.user.user_type == 'job_seeker':
                context['already_applied'] = JobApplication.objects.filter(
                    job=self.object, 
                    applicant=self.request.user
                ).exists()
                
                context['application_form'] = JobApplicationForm()
            elif self.request.user.user_type == 'employer':
                if self.object.employer == self.request.user:
                    context['applications'] = self.object.applications.all()
        
        related_jobs = Job.objects.filter(
            is_active=True
        ).exclude(id=self.object.id)[:4]
        
        context['related_jobs'] = related_jobs
        return context

class JobCreateView(LoginRequiredMixin, EmployerRequiredMixin, CreateView):
    model = Job
    form_class = JobForm
    template_name = 'jobs/job_form.html'
    success_url = reverse_lazy('employer_dashboard')
    
    def form_valid(self, form):
        form.instance.employer = self.request.user
        form.instance.company = self.request.user.company
        messages.success(self.request, 'Job posted successfully!')
        return super().form_valid(form)

class JobUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Job
    form_class = JobForm
    template_name = 'jobs/job_form.html'
    success_url = reverse_lazy('employer_dashboard')
    
    def test_func(self):
        job = self.get_object()
        return self.request.user == job.employer
    
    def form_valid(self, form):
        messages.success(self.request, 'Job updated successfully!')
        return super().form_valid(form)

class JobDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Job
    template_name = 'jobs/job_confirm_delete.html'
    success_url = reverse_lazy('employer_dashboard')
    
    def test_func(self):
        job = self.get_object()
        return self.request.user == job.employer
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Job deleted successfully!')
        return super().delete(request, *args, **kwargs)

@login_required
def apply_for_job(request, pk):
    if request.user.user_type != 'job_seeker':
        messages.error(request, "Only job seekers can apply for jobs.")
        return redirect('job_detail', pk=pk)
    
    job = get_object_or_404(Job, pk=pk)
    
    if JobApplication.objects.filter(job=job, applicant=request.user).exists():
        messages.info(request, "You have already applied for this job.")
        return redirect('job_detail', pk=pk)
    
    if request.method == 'POST':
        form = JobApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.applicant = request.user
            
            if not application.resume and hasattr(request.user, 'profile') and request.user.profile.resume:
                application.resume = request.user.profile.resume
                
            application.save()
            messages.success(request, "Your application has been submitted successfully!")
            return redirect('job_seeker_dashboard')
    else:
        form = JobApplicationForm()
    
    return render(request, 'jobs/apply_form.html', {'form': form, 'job': job})

class ApplicationDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = JobApplication
    template_name = 'jobs/application_detail.html'
    context_object_name = 'application'
    
    def test_func(self):
        application = self.get_object()
        return (self.request.user == application.job.employer or 
                self.request.user == application.applicant)

@login_required
def update_application_status(request, pk, status):
    application = get_object_or_404(JobApplication, pk=pk)
    
    if request.user != application.job.employer:
        messages.error(request, "You don't have permission to update this application.")
        return redirect('employer_dashboard')
    
    application.status = status
    application.save()
    messages.success(request, f"Application status updated to {status}.")
    return redirect('application_detail', pk=pk)

@login_required
def withdraw_application(request, pk):
    application = get_object_or_404(JobApplication, pk=pk)
    
    if request.user != application.applicant:
        messages.error(request, "You don't have permission to withdraw this application.")
        return redirect('job_seeker_dashboard')
    
    application.status = 'withdrawn'
    application.save()
    messages.success(request, "Your application has been withdrawn.")
    return redirect('job_seeker_dashboard')