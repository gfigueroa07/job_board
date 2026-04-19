from django import forms
from users .models import Profile, JobListing, Review, ProfileReport, JobReport, JobApplication, ReviewReport, Conversation, Message, ConversationReport, Feedback
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm


class ProfileForm(forms.ModelForm):
    location = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Location'}),
        required=False
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Write a short bio...'}),
        required=False
    )

    class Meta:
        model = Profile
        fields = [
            'location',
            'profile_picture',
            'description',
            'skills',
            'resume',
        ]

    def clean_profile_name(self):
        profile_name = self.cleaned_data.get('profile_name')

        if not profile_name:
            return profile_name

        if Profile.objects.filter(profile_name=profile_name).exists():
            raise forms.ValidationError('This profile already exists.')

        if len(profile_name) < 5:
            raise forms.ValidationError("Title too short")

        return profile_name

class UserProfileCreationForm(UserCreationForm):
    username = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={'placeholder': 'Username'})
    )

    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'})
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'})
    )

    location = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Location'})
    )

    description = forms.CharField(
        max_length=250,
        required=False,
        widget=forms.Textarea(attrs={'placeholder': 'Short bio...', 'rows': 4})
    )

    skills = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
    )

    profile_picture = forms.ImageField(required=False)
    resume = forms.FileField(required=False)

    class Meta:
        model = User
        fields = [
            'username',
            'password1',
            'password2',
        ]

    def save(self, commit=True):
        user = super().save(commit=True)  # 🔥 UserCreationForm handles password hashing

        profile, created = Profile.objects.get_or_create(user=user)

        profile.location = self.cleaned_data.get('location')
        profile.description = self.cleaned_data.get('description')
        profile.skills = self.cleaned_data.get('skills')

        if self.cleaned_data.get('profile_picture'):
            profile.profile_picture = self.cleaned_data.get('profile_picture')

        if self.cleaned_data.get('resume'):
            profile.resume = self.cleaned_data.get('resume')

        if commit:
            profile.save()

        return user
        
class ProfileEditForm(forms.ModelForm):
    def clean_profile_name(self):
        profile_name = self.cleaned_data['profile_name']
        if Profile.objects.filter(profile_name=profile_name).exists():
            raise forms.ValidationError(
                'This profile already exists.'
            )
        if len(profile_name) < 5:
            raise ValidationError("Title too short")   
        return profile_name  
    class Meta:
        model = Profile
        fields = [
            'profile_picture',
            'description',
            'skills',
            'resume',
        ]

class ProfileReportForm(forms.ModelForm):
    class Meta:
        model = ProfileReport
        fields = [
            'reason',
            'message'
        ]
              
class JobDetailsForm(forms.ModelForm):
    class Meta:
        model = JobListing
        fields = [
            'title',
            'description',
            'due_date',
        ]
    def clean_title(self):
        title = self.cleaned_data['title']
        if len(title) < 5:
            raise ValidationError("Title too short")
        return title
    
class JobCreateForm(forms.ModelForm):
    class Meta:
        model = JobListing
        fields = [
            'price',
            'title',
            'description',
            'due_date',
            'category',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'price': forms.NumberInput(attrs={'step': 0.01}),
        }

class JobApplicationForm(forms.ModelForm):
    class Meta:
        fields = [
            'message',
        ]
        model = JobApplication

class JobReportForm(forms.ModelForm):
    class Meta:
        model = JobReport
        fields = [
            'reason',
            'message'
        ]
        
class UserReviewsForm(forms.ModelForm):
    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if rating < 1 or rating > 5:
            raise forms.ValidationError(
                'Rating must be between 1-5.'
            )
        return rating
    class Meta:
        model = Review
        fields = [
            'rating',
            'images',
            'comment',
        ]
        widgets = {
            'rating': forms.NumberInput(attrs={
                'required': True, 
                'min': 1, 
                'max': 5
            })
        }
       
class ReviewReportForm(forms.ModelForm):
    class Meta:
        model = ReviewReport
        fields = [
            'reason',
            'message'
        ]

class ConversationReportForm(forms.ModelForm):
    class Meta:
        model = ConversationReport
        fields = [
            'reason',
            'message'
        ]
class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['report_type', 'message', 'page_url']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # default: message optional
        self.fields['message'].required = False
    
    
    
# Django has built-in form validation. A form is basically a set of input fields be they text, dates, images, whatever
# These form objects need to be used for Django to run validations using your Models
from django import forms
from .models import XaropItem

class XaropItemForm(forms.ModelForm):
    class Meta:
        model = XaropItem
        fields = ["name", "description"]
        widgets = {
            "name": forms.TextInput(attrs={"required": True, "maxlength": 100}),
            "description": forms.Textarea(attrs={"maxlength": 500})
        }
