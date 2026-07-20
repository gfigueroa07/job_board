from .models import Conversation, Message, Notifications, Profile, Review, JobListing, JobApplication

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
    