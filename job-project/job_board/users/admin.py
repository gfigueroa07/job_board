from django.contrib import admin
from .models import Profile, JobListing, Review, JobApplication, JobReport, ProfileReport, ReviewReport

# Register your models here.

admin.site.register(Profile)
admin.site.register(JobListing)
admin.site.register(Review)
admin.site.register(JobReport)
admin.site.register(JobApplication)
admin.site.register(ProfileReport)
admin.site.register(ReviewReport)