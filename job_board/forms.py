from django import forms
from users .models import Profile, JobListing, Review, JobApplication, Conversation, Message, Feedback, Report, ContactMessage
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm


class ProfileForm(forms.ModelForm):
    # location = forms.CharField(
    #     widget=forms.TextInput(attrs={'placeholder': 'Location'}),
    #     required=False
    # )
    description = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Write a short bio...'}),
        required=False
    )

    class Meta:
        model = Profile
        fields = [
            # 'location',
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

    description = forms.CharField(
        max_length=250,
        required=False,
        widget=forms.Textarea(attrs={'placeholder': 'Short bio...', 'rows': 4})
    )

    skills = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
    )

    profile_picture = forms.ImageField(
        required=False, 
        help_text="Upload a profile image"
    )
    resume = forms.FileField(
        required=False,
        label="Upload Resume"
    )

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

        # profile.location = self.cleaned_data.get('location')
        profile.description = self.cleaned_data.get('description')
        profile.skills = self.cleaned_data.get('skills')

        if self.cleaned_data.get('profile_picture'):
            profile.profile_picture = self.cleaned_data.get('profile_picture')

        if self.cleaned_data.get('resume'):
            profile.resume = self.cleaned_data.get('resume')

        if commit:
            profile.save()

        return profile
    
    def clean_username(self):
        username = self.cleaned_data['username'].strip().lower()
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username
    
class LoginForm(AuthenticationForm):
    def clean_username(self):
        return self.cleaned_data['username'].strip().lower()
                                     
class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'profile_picture',
            'description',
            'skills',
            'resume',
        ]
        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 4,
                'maxlength': 250,
                'class': 'auto-resize',
            }),
        }   
          
class JobDetailsForm(forms.ModelForm):
    class Meta:
        model = JobListing
        fields = [
            'title',
            'description',
            'price',
        ]
        widgets = {
            'title': forms.TextInput(),
            'description': forms.Textarea(attrs={'rows': 4}),
            'price': forms.NumberInput(attrs={'step': 0.01}),
        }
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
            # 'due_date',
            'category'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'maxlength': 50,
                'placeholder': 'Need lawn mowing',
            }),
            
            'description': forms.Textarea(attrs={
                'rows': 4,
                'maxlength': 800,
                'placeholder': 'Describe the job, tools needed, etc.'
            }),
            
            'price': forms.NumberInput(attrs={
                'step': 0.01,
                'placeholder': '50.00',
                'min': 1,
            }),
        }

class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = [
            'message',
        ]
        widgets = {
            'message': forms.Textarea(attrs={
                'rows': 4,
                'maxlength': 250,
                'placeholder': 'Optional details...'
            })
        }
        
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
            # 'images',
            'comment',
        ]
        widgets = {
            'rating': forms.NumberInput(attrs={
                'required': True, 
                'min': 1, 
                'max': 5,
                'placeholder': '1-5',
            }),
            'comment': forms.Textarea(attrs={
                'placeholder': 'Share your experience with this user...',
            })
        }
             
class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['report_type', 'message', 'page_url']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # default: message optional
        self.fields['message'].required = False

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['reason', 'description']

        widgets = {
            'reason': forms.Select(choices=[
                ('spam', 'Spam'),
                ('abuse', 'Abusive Content'),
                ('fake', 'Fake Content'),
                ('other', 'Other'),
            ]),
            'description': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Optional details...'
            }),
        }
        
class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = [
            'full_name',
            'email',
            'phone_number',
            'subject',
            'message'
        ]
        labels = {
            'full_name': 'FULL NAME',
            'email': 'EMAIL',
            'phone_number': 'PHONE NUMBER',
            'subject': 'SUBJECT',
            'message': 'MESSAGE'
        }