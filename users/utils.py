from .models import Conversation, Message, Notifications, Profile, Review, JobListing, JobApplication

import resend
from django.conf import settings

def send_verification_email(email, verification_url):
    resend.api_key = settings.RESEND_API_KEY
    resend.Emails.send(
        {
            "from": "Hustlr <noreply@hustlrjobs.com>",
            "to": [email],
            "subject": "Verify your Hustlr account",
            "html": f"""
                <h2>Welcome to Hustlr!</h2>

                <p>
                Thanks for creating your account.
                Please verify your email address:
                </p>

                <a href="{verification_url}">
                    Verify Email
                </a>

                <p>
                If you did not create this account,
                ignore this email.
                </p>
            """,
        }
    )

def reopen_job(job):
    accepted_application = JobApplication.objects.filter(
        job=job,
        status='accepted'
    ).first()
    
    if accepted_application:
        accepted_application.change_status("rejected")
        
    conversation = Conversation.objects.filter(job=job).first()
    
    if conversation:
        conversation.archive()
        
    job.status = "open"
    job.save()
    
def complete_job(job):
    accepted_application = JobApplication.objects.filter(
        job=job,
        status='accepted'
    ).first()
    
    if accepted_application:
        accepted_application.change_status("completed")
    
    conversation = Conversation.objects.filter(job=job).first()
    
    if conversation:
        conversation.archive()
        
    job.status = "completed"
    job.save()
    
def close_job(job):
    applications = JobApplication.objects.filter(
        job=job,
        status="pending"
    )
    
    for application in applications:
        application.change_status("rejected")
    accepted_application = JobApplication.objects.filter(
        job=job,
        status="accepted"
    ).first()
    
    if accepted_application:
        accepted_application.change_status("rejected")
        
    conversation = Conversation.objects.filter(job=job).first()
    
    if conversation:
        conversation.archive()
    
    job.status = "closed"
    job.save()
    