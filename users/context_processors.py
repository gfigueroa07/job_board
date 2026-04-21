from .models import Conversation, Message, Notifications
from django.http import JsonResponse


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