from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

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
    price = models.FloatField(blank=False, default=0.0)
    title = models.TextField(max_length=200)
    description = models.CharField(max_length=800, blank=False)
    date = models.DateTimeField(auto_now_add=True)
    images = models.ImageField(upload_to='job_pics/', blank=True, null=True)
    due_date = models.TextField(max_length=20, blank=True, null=True)
    
    def __str__(self):
        return self.title

class Review(models.Model):
    review_written = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='reviews_written')
    review_received = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='reviews_received')
    images = models.ImageField(upload_to='review_pics/', blank=True, null=True)
    edited = models.BooleanField(default=False)
    rating = models.IntegerField(validators=[
        MinValueValidator(1),
        MaxValueValidator(5),
    ])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['review_received', 'review_written'],
                name='one_review_per_user_per_profile'
            )
        ]
        
    def __str__(self):
        return f"{self.review_written.user.username} -> {self.review_received.user.username}"
    
class ProfileReport(models.Model):
    reason_choice = [
        ('spam','Spam'),
        ('scam','Scam/Fraud'),
        ('fake','Fake Profile'),
        ('harassment','Harassment'),
        ('inappropriate','Inappropriate Content'),
        ('other','Other'),
    ]
    report_status = [
        ('pending','Pending'),
        ('reviewed','Reviewed'),
        ('action_taken','Action Taken'),
        ('ignored','Ignored'),
    ]
    reported_profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='reports_against')
    reporter_profile = models.ForeignKey(Profile, on_delete=models.SET_NULL, blank=True, null=True, related_name='reported_made')
    reason = models.CharField(max_length=20, choices=reason_choice)
    message = models.TextField(max_length=250, blank=True)
    status = models.CharField(max_length=20, choices=report_status, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    reporter_ip = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return f"{self.reported_profile} - {self.reason}"
    
    
class JobReport(models.Model):
    reason_choice = [
        ('spam','Spam'),
        ('scam','Scam/Fraud'),
        ('fake','Fake Job'),
        ('harassment','Harassment'),
        ('inappropriate','Inappropriate Content'),
        ('other','Other'),
    ]
    report_status = [
        ('pending','Pending'),
        ('reviewed','Reviewed'),
        ('action_taken','Action Taken'),
        ('ignored','Ignored'),
    ]
    
    reported_job = models.ForeignKey(JobListing, on_delete=models.CASCADE, related_name='reports_against')
    reporter_profile = models.ForeignKey(Profile, on_delete=models.SET_NULL, blank=True, null=True, related_name='reports_made')
    reason = models.CharField(max_length=20, choices=reason_choice)
    message = models.TextField(max_length=250, blank=True)
    status = models.CharField(max_length=20, choices=report_status, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    reporter_ip = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return f"{self.reported_job} - {self.reason}"
    
class JobApplication(models.Model):
    application_status = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    job = models.ForeignKey(JobListing, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(Profile, on_delete=models.CASCADE)
    message = models.TextField(blank=True)
    applied_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=application_status, default='pending')
    
    def __str__(self):
        return f"{self.job} - {self.applicant}"