from django.contrib import admin
from .models import Profile, JobListing, Review

# Register your models here.

admin.site.register(Profile)
admin.site.register(JobListing)
admin.site.register(Review)
