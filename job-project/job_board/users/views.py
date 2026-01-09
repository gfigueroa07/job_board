from django.shortcuts import render, redirect, get_object_or_404
from job_board .forms import ProfileForm, ProfileEditForm, UserReviewsForm, ProfileReportForm, JobReportForm, JobApplicationForm, ReviewReportForm
from job_board .funcs import filter_and_sort, get_client_ip
from users .models import Profile, Review, User, JobListing, ProfileReport, JobReport, JobApplication, ReviewReport
from django.urls import path
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.db.models import Avg, Case, When, Value, BooleanField
from django.utils import timezone
from datetime import timedelta

# Create your views here.
# def home(request):
#     return render(request, 'users/home.html')

def profile_create(request):
    if request.user.is_authenticated:
        profile = request.user.profile
        messages.error(request, "Please log out before creating a profile.")
        return redirect('profile_detail', profile_id=profile.id)
    if request.method == 'POST':
        user_form = UserCreationForm(request.POST)
        profile_form = ProfileForm(request.POST, request.FILES)  # include files for avatar
        if user_form.is_valid() and profile_form.is_valid():
            # Save the user first
            user = user_form.save()
            
            # Save the profile, link it to the new user
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.profile_name = user.username
            profile.save()

            # Log the user in immediately
            login(request, user)
            return redirect('profile_detail', profile_id=profile.id) # replace 'home' with your URL name
    else:
        user_form = UserCreationForm()
        profile_form = ProfileForm()
    context = {'user_form': user_form, 'profile_form': profile_form}
    return render(request, 'users/profile_create.html', context)

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

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

def profile_report(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id)
    if request.method == 'POST':
        form = ProfileReportForm(request.POST)
        if form.is_valid():
            reporter_profile = None
            reporter_ip = None
            if request.user.is_authenticated:
                reporter_profile = request.user.profile
                if ProfileReport.objects.filter(reported_profile=profile, reporter_profile=reporter_profile).exists():
                    messages.warning(request, "You have already reported this profile.")
                    return redirect('profile_detail', profile_id=profile.id)
            else:
                reporter_ip = get_client_ip(request)
                time_limit = timezone.now() - timedelta(hours=24)
                if ProfileReport.objects.filter(reported_profile=profile, reporter_ip=reporter_ip, created_at__gte=time_limit).exists():
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
        form = ProfileReportForm()
    return render(request, 'users/report.html', {'form': form, 'profile': profile})

def job_report(request, job_id):
    job = get_object_or_404(JobListing, id=job_id)
    if request.method == 'POST':
        form = JobReportForm(request.POST)
        if form.is_valid():
            reporter_profile = None
            reporter_ip = None
            if request.user.is_authenticated:
                reporter_profile = request.user.profile
                if JobReport.objects.filter(reported_job=job, reporter_profile=reporter_profile).exists():
                    messages.warning(request, "You have already reported this job.")
                    return redirect('job_details', job_id=job.id)
            else:
                reporter_ip = get_client_ip(request)
                time_limit = timezone.now() - timedelta(hours=24)
                if JobReport.objects.filter(reported_job=job, reporter_ip=reporter_ip, created_at__gte=time_limit).exists():
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
        form = JobReportForm()
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
            application.save()
            success = True
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
        if action == 'accepted':
            application.status = 'accepted'
            application.save()
            messages.success(request, f"{application.applicant.user.username} has been approved.")
        elif action == 'rejected':
            application.status = 'rejected'
            application.save()
            messages.success(request, f"{application.applicant.user.username} has been rejected")        
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
        form = AuthenticationForm(data=request.POST)
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
    return render(request, 'users/user_jobs.html', {'profile': profile, 'jobs': jobs})

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
        form = ReviewReportForm(request.POST)
        if form.is_valid():
            reporter_profile = None
            reporter_ip = None
            if request.user.is_authenticated:
                reporter_profile = request.user.profile
                if ReviewReport.objects.filter(reporter_review=review, reporter_profile=reporter_profile).exists():
                    messages.warning(request, "You have already reported this review.")
                    return redirect('reviews', profile_id=review.review_received.id)
            else:
                reporter_ip = get_client_ip(request)
                time_limit = timezone.now() - timedelta(hours=24)
                if ReviewReport.objects.filter(reported_review=review, reporter_ip=reporter_ip, created_at__gte=time_limit).exists():
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
        form = ReviewReportForm()
    return render(request, 'users/report.html', {'form': form, 'review': review})