from django import forms
from django.conf import settings
from users .models import Profile, JobListing, Review, JobApplication, Conversation, Message, Feedback, Report, ContactMessage
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm, SetPasswordForm
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberPrefixWidget
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string

import resend
import re


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
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Email"
            }
        )
    )

    username = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
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
            'email',
            'password1',
            'password2',
        ]

    def save(self, commit=True):
        user = super().save(commit=False)

        email = self.cleaned_data["email"].lower()

        user.email = email

        # Username exists internally
        user.username = email

        if commit:
            user.save()
        
        profile, created = Profile.objects.get_or_create(user=user)

        profile.description = self.cleaned_data.get("description")
        profile.skills = self.cleaned_data.get("skills")

        if self.cleaned_data.get("profile_picture"):
            profile.profile_picture = self.cleaned_data["profile_picture"]

        if self.cleaned_data.get("resume"):
            profile.resume = self.cleaned_data["resume"]

        if commit:
            profile.save()

        return profile
    
    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "An account already exists with this email."
            )

        return email
    
class LoginForm(AuthenticationForm):
    def clean_email(self):
        return self.cleaned_data['email'].strip().lower()

class CompleteProfileForm(forms.Form):
    def validate_name(value):
            if not re.match(r"^[a-zA-ZÀ-ÿ' -]+$", value):
                raise ValidationError(
                    "Names can only contain letters, spaces, apostrophes, and hyphens."
                )

    first_name = forms.CharField(
        max_length=50,
        validators=[validate_name]
    )

    last_name = forms.CharField(
        max_length=50,
        validators=[validate_name]
    )
    phone_number = PhoneNumberField(
        required=False,
    )
                        
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
        fields = ['feedback_type', 'message']

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

def send_password_reset_email(email, reset_url):

    resend.api_key = settings.RESEND_API_KEY

    response = resend.Emails.send(
        {
            "from": "Hustlr <noreply@hustlrjobs.com>",
            "to": [email],
            "subject": "Reset your Hustlr password",

            "html": f"""
                <h2>Password Reset Request</h2>

                <p>
                    We received a request to reset your Hustlr password.
                </p>

                <p>
                    Click the button below to create a new password:
                </p>

                <p>
                    <a href="{reset_url}"
                    style="
                    background:#2563eb;
                    color:white;
                    padding:12px 20px;
                    text-decoration:none;
                    border-radius:6px;">
                        Reset Password
                    </a>
                </p>

                <p>
                    If you did not request this,
                    you can safely ignore this email.
                </p>
            """
        }
    )

    resend.api_key = settings.RESEND_API_KEY


class CustomPasswordResetForm(PasswordResetForm):

    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Enter your email",
                "class": "form-control",
            }
        )
    )

    def save(
        self,
        domain_override=None,
        subject_template_name=None,
        email_template_name=None,
        use_https=False,
        token_generator=default_token_generator,
        from_email=None,
        request=None,
        html_email_template_name=None,
        extra_email_context=None,
    ):

        email = self.cleaned_data["email"]

        users = self.get_users(email)

        for user in users:

            uid = urlsafe_base64_encode(
                force_bytes(user.pk)
            )

            token = token_generator.make_token(user)

            reset_url = request.build_absolute_uri(
                reverse(
                    "password_reset_confirm",
                    kwargs={
                        "uidb64": uid,
                        "token": token,
                    },
                )
            )

class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "New Password",
                "class": "form-control",
            }
        )
    )

    new_password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Confirm New Password",
                "class": "form-control",
            }
        )
    )