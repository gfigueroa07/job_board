from django import forms
from users .models import Profile, JobListing, Review, ProfileReport, JobReport, JobApplication, ReviewReport, Conversation, Message, ConversationReport, Feedback
from django.core.exceptions import ValidationError


class ProfileForm(forms.ModelForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Username'})
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Username'})
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Username'})
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Username'})
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Username'})
    )
    
    class Meta:
        model = Profile
        fields = [
            'profile_name',      # Include if it's a model field
            'location',
            'profile_picture',
            'description',
            'skills',
            'resume',
        ]
    def clean_profile_name(self):
        profile_name = self.cleaned_data.get('profile_name')
        if Profile.objects.filter(profile_name=profile_name).exists():
            raise forms.ValidationError('This profile already exists.')
        if len(profile_name) < 5:
            raise forms.ValidationError("Title too short")   
        return profile_name

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
            'images',
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
            'images',
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
