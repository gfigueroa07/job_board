from django import forms
from users .models import Profile, JobListing, Review



class ProfileForm(forms.ModelForm):
    def clean_profile_name(self):
        profile_name = self.cleaned_data['profile_name']
        if Profile.objects.filter(profile_name=profile_name).exists():
            raise forms.ValidationError(
                'This profile already exists.'
            )
        return profile_name   
    class Meta:
        model = Profile
        fields = [
            'location',
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

class JobDetailsForm(forms.ModelForm):
    class Meta:
        model = JobListing
        fields = [
            'title',
            'description',
            'images',
        ]
        
class JobCreateForm(forms.ModelForm):
    class Meta:
        model = JobListing
        fields = [
            'images',
            'title',
            'description',
            'due_date',
        ]

class UserReviewsForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = [
            'rating',
            'images',
            'comment',
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
