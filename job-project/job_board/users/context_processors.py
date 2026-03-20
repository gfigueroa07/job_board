



def unread_messages(request):
    if request.user.is_authenticated:
        count = Message.objects.filter(
            conversation__applicant=request.user,
            is_read=False
        ).exclude(sender=request.user).count()
    else:
        count = 0

    return {'unread_count': count}