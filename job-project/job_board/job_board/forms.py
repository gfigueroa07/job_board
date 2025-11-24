from django import forms
from users .models import Profile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'profile_picture',
            'description',
            'skills',
            'resume_upload'
        ]
