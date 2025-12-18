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
            'profile_name',
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