from .models import Conversation, Message, Notifications, Profile, Review, JobListing, JobApplication
from django.http import JsonResponse
from django.contrib import messages
from job_board.forms import ReportForm, JobApplicationForm
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

def unread_messages(request):
    if request.user.is_authenticated:
        conversations = Conversation.objects.filter(
            messages__is_read=False
        ).exclude(messages__sender=request.user).distinct()

        count = conversations.count()
    else:
        count = 0

    return {'unread_count': count}

def unread_counts(request):
    if not request.user.is_authenticated:
        return {}

    return {
        "unread_count": Message.objects.filter(
            is_read=False
        ).exclude(sender=request.user).count()
    }

def handle_report_submission(request):
    if request.method != "POST":
        return None
    
    form = ReportForm(request.POST)
    
    if not form.is_valid():
        return None
    report = form.save(commit=False)
    if request.user.is_authenticated:
        report.reporter = request.user
    ALLOWED_MODELS = {
        "profile": Profile,
        "job": JobListing,
        "review": Review,
        "conversation": Conversation,
    }
    
    model_name = request.POST.get("content_type")
    model_class = ALLOWED_MODELS.get(model_name)
    if model_class is None:
        return None
    try:
        object_id = int(request.POST.get("object_id"))
    except (TypeError, ValueError):
        return None
    if not model_class.objects.filter(pk=object_id).exists():
        return None
    report.content_type = ContentType.objects.get_for_model(model_class)
    report.object_id = object_id
    report.save()
    messages.success(request, "Report submitted.")
    return report