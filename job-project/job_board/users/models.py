from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_name = models.CharField(max_length=30, unique=False, blank=True, null=False)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    location = models.TextField(blank=False)
    description = models.TextField(blank=True)
    avg_review_score = models.FloatField(default=0.0)
    skills = models.TextField(blank=True)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)

    def __str__(self):
        return self.user.username
    
class JobListing(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    title = models.TextField(max_length=200)
    description = models.CharField(max_length=800, blank=False)
    date = models.DateTimeField(auto_now_add=True)
    images = models.ImageField(upload_to='job_pics/', blank=False, null=True)
    due_date = models.TextField(max_length=20, blank=True, null=True)
    
    def __str__(self):
        return self.title

class Review(models.Model):
    review_by_profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='reviews_written')
    review_to_profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='reviews_received')
    rating = models.FloatField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.review_by_profile.user.username} -> {self.review_to_profile.user.username}"