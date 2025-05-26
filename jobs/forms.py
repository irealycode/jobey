from django import forms
from .models import Job, JobApplication

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ('title', 'job_type', 'experience_level', 'location', 
                 'salary_min', 'salary_max', 'description', 'requirements', 
                 'benefits', 'application_instructions', 'application_url', 
                 'is_active', 'expiry_date')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 6}),
            'requirements': forms.Textarea(attrs={'rows': 6}),
            'benefits': forms.Textarea(attrs={'rows': 4}),
            'application_instructions': forms.Textarea(attrs={'rows': 4}),
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
        }

class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ('resume', 'cover_letter')
        widgets = {
            'cover_letter': forms.Textarea(attrs={
                'rows': 6, 
                'placeholder': 'Introduce yourself and explain why you are a good fit for this position...'
            }),
        }

class JobSearchForm(forms.Form):
    SORT_CHOICES = (
        ('recent', 'Most Recent'),
        ('relevant', 'Most Relevant'),
        ('salary_high', 'Salary (High to Low)'),
        ('salary_low', 'Salary (Low to High)'),
    )
    
    keyword = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Job title, keywords, or company',
        'class': 'form-control'
    }))
    
    location = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'City, state, or zip code',
        'class': 'form-control'
    }))
    
    
    
    job_type = forms.MultipleChoiceField(
        choices=Job.JOB_TYPE_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple
    )
    
    experience_level = forms.MultipleChoiceField(
        choices=Job.EXPERIENCE_LEVEL_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple
    )
    
    min_salary = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Min Salary'})
    )
    
    sort_by = forms.ChoiceField(
        choices=SORT_CHOICES,
        required=False,
        initial='recent',
        widget=forms.Select(attrs={'class': 'form-select'})
    )