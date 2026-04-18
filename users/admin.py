from django.contrib import admin
from .models import Profile, JobListing, Review, JobApplication, JobReport, ProfileReport, ReviewReport, Conversation, Message, ConversationReport, Message, Feedback
from django.utils.html import format_html

# Register your models here.

admin.site.register(Profile)
admin.site.register(JobListing)
admin.site.register(Review)
admin.site.register(JobReport)
admin.site.register(JobApplication)
admin.site.register(ProfileReport)
admin.site.register(ReviewReport)
admin.site.register(Conversation)

@admin.register(ConversationReport)
class ConversationReportAdmin(admin.ModelAdmin):
    list_display = ('reported_convo', 'created_at')
    readonly_fields = ('view_messages',)

    def view_messages(self, obj):
        messages = obj.reported_convo.messages.all().order_by('timestamp')

        if not messages:
            return "No messages"

        return format_html(
            "<br><br>".join(
                f"<strong>{m.sender.username}</strong>: {m.content} <br><small>{m.timestamp}</small>"
                for m in messages
            )
        )

    view_messages.short_description = "Conversation Messages"
    
admin.site.register(Feedback)