from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from allauth.account.forms import SignupForm
from .models import CustomUser, Company, Profile
import logging
logger = logging.getLogger(__name__)

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'user_type')

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'user_type', 'bio', 'location')

class CustomSignupForm(SignupForm):
    user_type = forms.ChoiceField(
        choices=CustomUser.USER_TYPE_CHOICES,
        widget=forms.RadioSelect
    )
    
    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        user.user_type = self.cleaned_data['user_type']
        user.save()

        print('test test')
        # print("Saving form with data:", self.cleaned_data)

        # print("User Type selected: %s", self.cleaned_data.get('user_type'))
        # print(user.user_type)

        
        if user.user_type == 'job_seeker':
            Profile.objects.create(user=user)
        elif user.user_type == 'employer':
            Company.objects.create(
                user=user,
                name=user.username, 
                description="Company description"
            )
        
        return user

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ('name', 'logo', 'website', 'description', 'industry', 'size', 'founded_year')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('resume', 'skills', 'experience', 'education', 'phone_number', 'website')
        widgets = {
            'skills': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Separate skills with commas'}),
            'experience': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe your work experience'}),
            'education': forms.Textarea(attrs={'rows': 3, 'placeholder': 'List your educational background'}),
        }