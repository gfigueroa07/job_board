from .models import Conversation, Message, Notifications
from django.http import JsonResponse
from django.contrib import messages
from job_board.forms import ReportForm
from django.contrib.contenttypes.models import ContentType


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

    content_type = ContentType.objects.get(
        model=request.POST.get("content_type")
    )

    report.content_type = content_type
    report.object_id = int(request.POST.get("object_id"))

    report.save()

    messages.success(request, "Report submitted.")

    return report