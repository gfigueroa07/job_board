from django import forms
from users .models import Profile, JobListing

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'user',
            'profile_picture',
            'description',
            'skills',
            'resume',
        ]

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'profile_picture',
            'description',
            'skills',
            'resume',
        ]

class JobList(forms.ModelForm):
    class Meta:
        model = JobListing
        fields = [
            'title',
            'description',
            'images',
        ]
        
        
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