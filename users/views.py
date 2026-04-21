from django.shortcuts import render, redirect, get_object_or_404
from job_board .forms import ProfileForm, ProfileEditForm, UserReviewsForm, JobApplicationForm, FeedbackForm, UserProfileCreationForm, ReportForm
from job_board .funcs import filter_and_sort, get_client_ip, is_job_owner
from users .models import Profile, Review, User, JobListing, JobApplication,  Message, Conversation, Notifications, Feedback, Report
from django.urls import path
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.db.models import Avg, Case, When, Value, BooleanField, Max, Q
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator
from django.contrib.contenttypes.models import ContentType


# Create your views here.
# def home(request):
#     return render(request, 'users/home.html')

def profile_create(request):
    if request.user.is_authenticated:
        profile = request.user.profile
        messages.error(request, "Please log out before creating a profile.")
        return redirect('profile_detail', profile_id=profile.id)
    if request.method == 'POST':
        form = UserProfileCreationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('login')  # or wherever you want
    else:
        form = UserProfileCreationForm()
    return render(request, 'users/profile_create.html', {'form': form})

def profile_detail(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id)
    reviews = Review.objects.filter(review_received=profile)
    average_rating = Review.objects.filter(review_received=profile).aggregate(Avg('rating'))['rating__avg']
    return render(request, 'users/profile_detail.html', {
        'profile': profile,
        'reviews': reviews,
        'average_rating': average_rating,   
    })

def profile_edit(request):
    if not request.user.is_authenticated:
        messages.error(request, 'No profile to edit. Please log in or create a profile.')
        return redirect('login')
    profile = request.user.profile
    if request.method == 'POST':
        profile = request.user.profile
        form = ProfileEditForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile_detail', profile_id=profile.id)
    else:
        form = ProfileEditForm(instance=profile)
    return render(request, 'users/profile_edit.html', {'form': form})

@login_required
def profile_delete(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if user.id != request.user.id:
        return redirect('profile_detail', user_id=user.id)
    if request.method == 'POST':
        user.delete()
        return redirect('login')
    return render(request, 'users/profile_delete.html', {'user': user})

def profile_report(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id)
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            reporter_profile = None
            reporter_ip = None
            if request.user.is_authenticated:
                reporter_profile = request.user.profile
                if Report.objects.filter(reported_profile=profile, reporter_profile=reporter_profile).exists():
                    messages.warning(request, "You have already reported this profile.")
                    return redirect('profile_detail', profile_id=profile.id)
            else:
                reporter_ip = get_client_ip(request)
                time_limit = timezone.now() - timedelta(hours=24)
                if Report.objects.filter(reported_profile=profile, reporter_ip=reporter_ip, created_at__gte=time_limit).exists():
                    messages.warning(request, "You have already reported this profile in the last 24 hours.")
                    return redirect('profile_detail', profile_id=profile.id)
            report = form.save(commit=False)
            report.reported_profile = profile
            report.reporter_profile = reporter_profile
            report.reporter_ip = reporter_ip
            report.save()
            messages.success(request, "Thank you for your report.")
            return redirect('profile_detail', profile_id=profile.id)
    else:
        form = ReportForm()
    return render(request, 'users/report.html', {'form': form, 'profile': profile})

def job_report(request, job_id):
    job = get_object_or_404(JobListing, id=job_id)
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            reporter_profile = None
            reporter_ip = None
            if request.user.is_authenticated:
                reporter_profile = request.user.profile
                if Report.objects.filter(reported_job=job, reporter_profile=reporter_profile).exists():
                    messages.warning(request, "You have already reported this job.")
                    return redirect('job_details', job_id=job.id)
            else:
                reporter_ip = get_client_ip(request)
                time_limit = timezone.now() - timedelta(hours=24)
                if Report.objects.filter(reported_job=job, reporter_ip=reporter_ip, created_at__gte=time_limit).exists():
                    messages.warning(request, "You have already reported this job in the last 24 hours.")
                    return redirect('job_details', job_id=job.id)
            report = form.save(commit=False)
            report.reported_job = job
            report.reporter_profile = reporter_profile
            report.reporter_ip = reporter_ip
            report.save()
            messages.success(request, "Thank you for your report.")
            return redirect('job_details', job_id=job.id)
    else:
        form = ReportForm()
    return render(request, 'users/report.html', {'form': form, 'job': job})

@login_required
def job_application(request, job_id):
    job =  get_object_or_404(JobListing, id=job_id)
    if request.user.profile == job.profile:
        messages.error(request, "Can't apply to a job owned by you.")
        return redirect('job_details', job_id=job.id)
    already_applied = False
    if JobApplication.objects.filter(job=job, applicant=request.user.profile).exists():
        success = False  
        already_applied = True
        messages.warning(request, "You have already applied to this job.")
        return redirect('job_details', job_id=job.id)
    if request.method == 'POST':
        form = JobApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.applicant = request.user.profile
            if JobApplication.objects.filter(job=job, applicant=request.user.profile).exists():
                success = False  
                already_applied = True
                messages.warning(request, "You have already applied to this job.")
                return redirect('job_details', job_id=job.id)
            Notifications.objects.create(
                user=job.profile.user,
                notification_type='application',
                message=f"{request.user} applied to your job",
                related_job=job
            )
            application.save()
            success = True
            return redirect('job_details', job_id=job.id)
        else:
            success = False
    else:
        form = JobApplicationForm()
        success = False
    return render(request, 'users/user_apply.html', {'form': form, 'job': job, 'success': success, 'already_applied': already_applied})

def job_applicants(request, job_id):
    job = get_object_or_404(JobListing, id=job_id)
    if request.user.profile.id != job.profile.id: 
        messages.error(request, "You are not allowed to view this job's applicants.")
        return redirect('job_page')
    applications = JobApplication.objects.filter(job=job).order_by('-applied_at')
    if request.method == 'POST':
        application_id = request.POST.get('application_id')
        action = request.POST.get('action')
        application = get_object_or_404(JobApplication, id=application_id, job=job)
        job = application.job
        if JobApplication.objects.filter(job=job, status="accepted").exists():
            messages.error(request, 'Job already has an accepted applicant.')
            return redirect('job_applicants', job_id=job.id)
        if action == 'accepted':
            application.status = 'accepted'
            application.save()
            job.status = 'pending'
            job.save()
            Conversation.objects.get_or_create(job=job, applicant=application.applicant.user)
            messages.success(request, f"{application.applicant.user.username} has been approved.")
        elif action == 'rejected':
            application.status = 'rejected'
            messages.success(request, f"{application.applicant.user.username} has been rejected")   
        Notifications.objects.create(
            user=application.applicant.user,
            notification_type='status_update',
            message=f"Your application was {application.status}",
            related_application=application
            )
        application.save()
        return redirect('job_applicants', job.id)     
    return render(request, 'users/job_applicants.html', {
        'job': job,
        'applications': applications,
    })
    
def user_login(request):
    if request.user.is_authenticated:
        profile = request.user.profile
        messages.error(request, "You are already logged in.")
        return redirect('profile_detail', profile_id=profile.id)
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            profile = request.user.profile
            return redirect('profile_detail', profile_id=profile.id)
    else:
        form = AuthenticationForm()
    return render(request, 'users/user_login.html', {'form': form})

@require_POST
def user_logout(request):
    print("POST REQUEST RECEIVED logout")
    if request.method == 'POST':
        logout(request)
        return redirect('login') 
    
def user_jobs(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id)
    jobs = JobListing.objects.filter(profile=profile)
    query = request.GET.get('q')
    category = request.GET.get('category')
    if query:
        jobs = jobs.filter(title__icontains=query)
    if category and category.strip():  
        jobs = jobs.filter(category=category)
    paginator = Paginator(jobs, 10)  # 10 jobs per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'users/user_jobs.html', {
        'page_obj': page_obj,
        'job_count': jobs.count(),
    })

@login_required
def user_jobs_applied(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id)
    application = JobApplication.objects.filter(applicant=profile)
    jobs = JobListing.objects.filter(id__in=application.values_list('job', flat=True))
    query = request.GET.get('q')
    category = request.GET.get('category')
    if query:
        jobs = jobs.filter(title__icontains=query)
    if category and category.strip():  
        jobs = jobs.filter(category=category)
    paginator = Paginator(jobs, 10)  # 10 jobs per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'users/jobs_applied.html', {
        'page_obj': page_obj,
        'job_count': jobs.count(),
    })

    
def review_page(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id)
    reviews = Review.objects.filter(review_received=profile)
    return render(request, 'users/review_page.html', {'profile': profile, 'reviews': reviews})

@login_required
def review_create(request, profile_id):
    reviewed_profile = get_object_or_404(Profile, id=profile_id)
    if request.user.profile == reviewed_profile:
        messages.error(request, 'Cant Review yourself')
        return redirect('profile_detail', profile_id=profile_id)
    existing_review = Review.objects.filter(
        review_written=request.user.profile,
        review_received=reviewed_profile
    ).exists()
    if existing_review:
        messages.error(request, 'You have an  existing review')
        return redirect('profile_detail', profile_id=profile_id)
    if request.method == 'POST':
        form = UserReviewsForm(request.POST, request.FILES)
        if form.is_valid():
            review = form.save(commit=False)
            review.review_written = request.user.profile
            review.review_received = reviewed_profile
            print("SAVING REVIEW") #debug test
            Notifications.objects.create(
            user=review.review_received.user,
            notification_type='review',
            message=f"You received a new review.",
            )
            review.save()
            return redirect('profile_detail', profile_id=profile_id)
    else:
        form = UserReviewsForm()
    return render(request, 'users/review_create.html', {'form': form, 'profile': reviewed_profile})
    
@login_required
def review_edit(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    if review.review_written != request.user.profile:
        return redirect('profile_detail', profile_id=review.review_written.id)
    if request.method =='POST':
        form = UserReviewsForm(request.POST, request.FILES, instance=review)
        if form.is_valid():
            review.edited = True
            form.save()
            return redirect('profile_detail', profile_id=review.review_received.id)
    else:
        form = UserReviewsForm(instance=review)
    return render(request, 'users/review_edit.html', {'form': form, 'review': review})

@login_required
def review_delete(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    if review.review_written != request.user.profile:
        return redirect('profile_detail', review_id=review.review_written.id)
    if request.method == 'POST':
        review.delete()
        return redirect('review_edit', profile_id=review.review_written.id)
    return render(request, 'users/review_delete.html', {'review': review})

def review_report(request, review_id):
    review  = get_object_or_404(Review, id=review_id)
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            reporter_profile = None
            reporter_ip = None
            if request.user.is_authenticated:
                reporter_profile = request.user.profile
                if Report.objects.filter(reporter_review=review, reporter_profile=reporter_profile).exists():
                    messages.warning(request, "You have already reported this review.")
                    return redirect('reviews', profile_id=review.review_received.id)
            else:
                reporter_ip = get_client_ip(request)
                time_limit = timezone.now() - timedelta(hours=24)
                if Report.objects.filter(reported_review=review, reporter_ip=reporter_ip, created_at__gte=time_limit).exists():
                    messages.warning(request, "You have already reported this review in the last 24 hours.")
                    return redirect('reviews', profile_id=review.review_received.id)
            report = form.save(commit=False)
            report.reported_review = review
            report.reporter_profile = reporter_profile
            report.reporter_ip = reporter_ip
            report.save()
            messages.success(request, "Thank you for your report.")
            return redirect('reviews', profile_id=review.review_received.id)
    else:
        form = ReportForm()
    return render(request, 'users/report.html', {'form': form, 'review': review})

@login_required
def conversation_detail(request, convo_id):

    conversation = get_object_or_404(Conversation, id=convo_id)

    if request.user != conversation.applicant and request.user != conversation.job.profile.user:
        return redirect('job_details', conversation.job.id)

    # define other_user
    if request.user == conversation.applicant:
        other_user = conversation.job.profile.user
    else:
        other_user = conversation.applicant

    conversation.other_user = other_user

    if request.method == 'POST':
        content = request.POST.get('content')
        if content and content.strip():
            Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=content
            )
            return redirect("conversation_details", convo_id=convo_id)

    convo_messages = conversation.messages.all().order_by('timestamp')

    convo_messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

    return render(request, 'users/conversation.html', {
        'conversation': conversation,
        'convo_messages': convo_messages,
    })
    
def conversation_report(request, convo_id):
    conversation  = get_object_or_404(Conversation, id=convo_id)
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            reporter_profile = None
            reporter_ip = None
            if request.user.is_authenticated:
                reporter_profile = request.user.profile
                if Report.objects.filter(reported_convo=conversation, reporter_profile=reporter_profile).exists():
                    messages.warning(request, "You have already reported this conversation.")
                    return redirect('conversation_details', convo_id=conversation.id)
            else:
                reporter_ip = get_client_ip(request)
                time_limit = timezone.now() - timedelta(hours=24)
                if Report.objects.filter(reported_convo=conversation, reporter_ip=reporter_ip, created_at__gte=time_limit).exists():
                    messages.warning(request, "You have already reported this conversation in the last 24 hours.")
                    return redirect('conversation_details', convo_id=conversation.id)
            report = form.save(commit=False)
            report.reported_convo = conversation
            report.reporter_profile = reporter_profile
            report.reporter_ip = reporter_ip
            report.save()
            messages.success(request, "Thank you for your report.")
            return redirect('conversation_details', convo_id=conversation.id)
    else:
        form = ReportForm()
    return render(request, 'users/report.html', {'form': form, 'conversation': conversation})

@login_required
def inbox(request):

    user = request.user

    conversations = Conversation.objects.filter(
        Q(applicant=user) |
        Q(job__profile__user=user)
    ).annotate(
        last_message_time=Max('messages__created_at')
    ).order_by('-last_message_time')

    convo_data = []

    for convo in conversations:

        last_message = convo.messages.order_by('-created_at').first()

        has_unread = convo.messages.filter(
            is_read=False
        ).exclude(sender=request.user).exists()

        # FIX: compute other_profile HERE
        if user == convo.applicant:
            other_user = convo.job.profile
        else:
            other_user = convo.applicant

        convo_data.append({
            'conversation': convo,
            'last_message': last_message,
            'has_unread': has_unread,
            'other_user': other_user
        })

    return render(request, 'users/inbox.html', {
        'convo_data': convo_data
    })

@login_required
def notifications(request):
    notifications = request.user.notifications.order_by('-created_at')
    return render(request, 'users/notifications.html', {'notifications': notifications})

@login_required
def notification_count(request):
    count = request.user.notifications.filter(is_read=False).count()
    return JsonResponse({'count': count})

@login_required
def submit_report(request):
    form = FeedbackForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            report_type = form.cleaned_data['report_type']
            message = form.cleaned_data['message']

            # Make message required for bugs
            if report_type == 'bug' and not message:
                return render(request, 'users/feedback.html', {
                    'form': form,
                    'error': 'Please describe the bug in the message field.'
                })
            # 24-hour limit check
            last_report = Feedback.objects.filter(user=request.user).order_by('-created_at').first()
            if last_report and timezone.now() - last_report.created_at < timedelta(hours=24):
                return render(request, 'users/feedback.html', {
                    'form': form,
                    'error': 'You can only submit one report every 24 hours.'
                })
            # Save report
            report = form.save(commit=False)
            report.user = request.user
            report.save()
            return redirect('home')
    return render(request, 'users/feedback.html', {'form': form})

def unread_count(request):
    if not request.user.is_authenticated:
        return JsonResponse({"count": 0})

    message_count = Message.objects.filter(
        is_read=False
    ).exclude(sender=request.user).count()

    notification_count = Notifications.objects.filter(
        user=request.user,
        is_read=False
    ).count()

    return JsonResponse({
        "messages": message_count,
        "notifications": notification_count,
        "total": message_count + notification_count
    })

def mark_messages_read(request):
    if not request.user.is_authenticated:
        return JsonResponse({"status": "unauthorized"})

    Message.objects.filter(
        is_read=False
    ).exclude(sender=request.user).update(is_read=True)

    return JsonResponse({"status": "ok"})

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')


def report_create(request, model_name, object_id):
    """
    Generic report view:
    - model_name: 'job', 'profile', 'conversation', 'review'
    - object_id: id of the object being reported
    """
    # Map URL string → actual model
    MODEL_MAP = {
        'job': 'users.JobListing',
        'profile': 'users.Profile',
        'conversation': 'users.Conversation',
        'review': 'users.Review',
    }
    if model_name not in MODEL_MAP:
        return redirect('/')
    app_label, model_class = MODEL_MAP[model_name].split('.')
    # get the actual model class dynamically
    from django.apps import apps
    Model = apps.get_model(app_label, model_class)
    # fetch object safely
    obj = get_object_or_404(Model, id=object_id)
    next_url = request.GET.get('next', '/')
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            # attach reporter (or anonymous)
            if request.user.is_authenticated:
                report.reporter = request.user
            else:
                report.reporter = None
                report.ip_address = get_client_ip(request)
            # GenericForeignKey assignment
            report.content_type = ContentType.objects.get_for_model(Model)
            report.object_id = obj.id
            report.save()
            return redirect(next_url)
    else:
        form = ReportForm()
    return render(request, 'users/report.html', {
        'form': form,
        'reported_object': obj,
        'model_name': model_name,
        'next': next_url
    })