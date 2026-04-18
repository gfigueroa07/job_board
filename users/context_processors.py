from .models import Conversation

def unread_messages(request):
    if request.user.is_authenticated:
        conversations = Conversation.objects.filter(
            messages__is_read=False
        ).exclude(messages__sender=request.user).distinct()

        count = conversations.count()
    else:
        count = 0

    return {'unread_count': count}