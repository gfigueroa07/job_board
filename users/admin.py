from django.contrib import admin
from .models import Profile, JobListing, Review, JobApplication, Conversation, Feedback, Report, ContactMessage
from django.utils.html import format_html
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
# Register your models here.

admin.site.register(Profile)
admin.site.register(JobListing)
admin.site.register(Review)
admin.site.register(JobApplication)
admin.site.register(Conversation)

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'report_type_display', 'object_preview', 'reporter', 'created_at')
    readonly_fields = ('object_preview', 'full_details')

    def report_type_display(self, obj):
        return obj.content_type.model
    report_type_display.short_description = "Type"

    def object_preview(self, obj):
        target = obj.content_object

        if isinstance(target, JobListing):
            return f"Job: {target.title}"

        if isinstance(target, Profile):
            return f"Profile: {target.profile_name or target.user.username}"

        if isinstance(target, Conversation):
            return f"Conversation (Job: {target.job.title})"

        if isinstance(target, Review):
            return f"Review: {target.rating}⭐"

        return str(target)

    object_preview.short_description = "Preview"

    def full_details(self, obj):
        target = obj.content_object

        # JOB
        if isinstance(target, JobListing):
            return format_html(
                "<b>Title:</b> {}<br><b>Description:</b> {}",
                target.title,
                target.description
            )

        # PROFILE
        if isinstance(target, Profile):
            return format_html(
                "<b>Name:</b> {}<br><b>Description:</b> {}<br><b>Location:</b> {}",
                target.profile_name,
                target.description,
                target.location
            )

        # CONVERSATION + MESSAGES
        if isinstance(target, Conversation):
            messages = target.messages.all().order_by('timestamp')
            return format_html(
                "<br><br>".join(
                    f"<b>{m.sender.username}</b>: {m.content} <small>({m.timestamp})</small>"
                    for m in messages
                )
            )

        # REVIEW
        if isinstance(target, Review):
            return format_html(
                "<b>Rating:</b> {}⭐<br><b>Comment:</b> {}",
                target.rating,
                target.comment
            )

        return "No details available"

    full_details.short_description = "Full Content"
    
@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "email",
        "created_at",
    )

    search_fields = (
        "full_name",
        "email",
    )

    ordering = ("-created_at",)
    
@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = (
        "display_user",
        "feedback_type",
        "message",
        "created_at",
    )
    search_fields = (
        "user__username",
        "message",
    )
    ordering = ("-created_at",)
    def display_user(self, obj):
        if obj.user:
            return obj.user.username
        return "Anonymous"
    display_user.short_description = "User"