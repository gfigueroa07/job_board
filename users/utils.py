from .models import Conversation, Message, Notifications, Profile, Review, JobListing, JobApplication
import resend
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

resend.api_key = settings.RESEND_API_KEY


def send_verification_email(email, verification_url):
    response = resend.Emails.send({
        "from": "Hustlr <noreply@hustlrjobs.com>",
        "to": [email],
        "subject": "Verify your Hustlr account",
        "html": f"""
            <h2>Welcome to Hustlr!</h2>

            <p>
                Thanks for creating your account.
            </p>

            <p>
                Click the button below to verify your email:
            </p>

            <p>
                <a href="{verification_url}"
                   style="background:#2563eb;
                          color:white;
                          padding:12px 20px;
                          text-decoration:none;
                          border-radius:6px;">
                    Verify Email
                </a>
            </p>

            <p>
                If you didn't create this account, you can safely ignore this email.
            </p>
        """
    })

    print("\n=== EMAIL VERIFICATION ===")
    print(f"Recipient: {email}")
    print(f"Verification URL: {verification_url}")
    print("==========================\n")

    print(response)

def build_verification_url(request, user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    return request.build_absolute_uri(
        reverse(
            "verify_email_token",
            kwargs={
                "uidb64": uid,
                "token": token,
            },
        )
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
    