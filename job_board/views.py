from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from job_board .forms import ProfileForm, ProfileEditForm, ReportForm
from django.urls import path
from django.http import HttpResponse
from .forms import JobDetailsForm, JobCreateForm, JobApplicationForm
from users.models import JobListing, JobApplication, Conversation, Profile, JobImage, Notifications
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator
from users.context_processors import handle_report_submission
from .models import XaropItem

def home(request):
    return render(request, 'job_board/home.html')

def job_page(request):
    jobs = JobListing.objects.all()
    query = request.GET.get('q')
    category = request.GET.get('category')
    if query:
        jobs = jobs.filter(title__icontains=query)
    if category and category.strip():  
        jobs = jobs.filter(category=category)
    jobs = jobs.order_by('-id')
    paginator = Paginator(jobs, 10)  # 10  jobs per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'job_board/job_page.html', {
        'page_obj': page_obj,
        'job_count': jobs.count(),
    })

def job_details(request, job_id):
    job = get_object_or_404(JobListing, id=job_id)
    report_form = ReportForm(initial={
        'reported_job': job.id
    })
    images = job.images.all()  # Related name used
    application = None
    conversation = None
    if request.user.is_authenticated and job.status == 'pending':
        conversation = Conversation.objects.filter(
            job=job,
            ).filter(
            Q(applicant=request.user) |
            Q(job__profile__user=request.user)
        ).first()
    if request.user.is_authenticated:
        application = JobApplication.objects.filter(
            job=job,
            applicant=request.user.profile
        ).first()
    else:
        application = None
    if handle_report_submission(request):
        return redirect(request.path)
    if request.method == "POST":
        apply_form = JobApplicationForm(request.POST)

        if apply_form.is_valid():
            if JobApplication.objects.filter(
                job=job,
                applicant=request.user.profile
            ).exists():
                messages.warning(
                    request,
                    "You already applied to this job."
                )
                return redirect('job_details', job_id=job.id)
            
            application = apply_form.save(commit=False)
            application.job = job
            application.applicant = request.user.profile
            application.save()
        Notifications.objects.create(
            user=job.profile.user,
            notification_type='application',
            message=f"{request.user} applied to your job",
            related_job=job,
            related_application=application
        )

        print("Notification created")
        
        messages.success(request, "Application submitted.")
        return redirect('job_details', job_id=job.id)
    
    else:
        apply_form = JobApplicationForm()
    return render(request, 'job_board/job_details.html', {
        'job': job,
        'application': application,
        'conversation': conversation,
        'images': images,
        'report_form': report_form,
        'apply_form': apply_form
    })

@login_required
def job_list(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Login before posting a job.')
        return redirect('login')
    if request.method == 'POST':
        form = JobCreateForm(request.POST, request.FILES)
        if form.is_valid():
            images = request.FILES.getlist('images')
            if len(images) > 3:
                messages.error(request, "Can't post more than 3 images.")
            else:
                job = form.save(commit=False)
                job.profile = request.user.profile
                job.save()
                for img in images:
                    JobImage.objects.create(job=job, image=img)
                messages.success(request, 'Job posted successfully.')
                return redirect('job_page')
    else:
        form = JobCreateForm()
    return render(request, 'job_board/job_list.html', {
        'form': form
    })
    
@login_required
def job_edit(request, job_id):
    job = get_object_or_404(JobListing, id=job_id)
    if job.profile != request.user.profile:
        return redirect('job_details')
    if request.method == 'POST':
        form = JobDetailsForm(request.POST, request.FILES, instance=job)

        # NEW uploaded images
        new_images = request.FILES.getlist('images')

        # Images selected for deletion
        delete_ids = request.POST.getlist('delete_images')

        # Delete selected images
        if delete_ids:
            JobImage.objects.filter(id__in=delete_ids, job=job).delete()

        # Count AFTER deletion
        current_count = job.images.count()
        total_images = current_count + len(new_images)

        if total_images > 3:
            messages.error(request, "Maximum 3 images allowed.")
            return redirect('job_edit', job_id=job.id)

        if form.is_valid():
            form.save()

            # Save new uploads
            for img in new_images:
                JobImage.objects.create(job=job, image=img)

            messages.success(request, "Job updated successfully.")
            return redirect('job_details', job_id=job.id)
    else:
        form = JobDetailsForm(instance=job)
    return render(request, 'job_board/job_edit.html', {
        'form': form, 
        'job': job, 
        'images': job.images.all(),
    })

@login_required
def job_delete(request, job_id):
    job = get_object_or_404(JobListing, id=job_id)
    if job.profile != request.user.profile:
        return redirect('job_details')
    if request.method == 'POST':
        job.delete()
        return redirect('job_page')
    return render(request, 'job_board/job_delete.html', {'job': job})

def privacy(request):
    return render(request, 'job_board/privacy.html')

def terms(request):
    return render(request, 'job_board/terms.html')

def contact(request):
    return render(request, 'job_board/contact.html')

def profile(request):
    return render(request, 'job_board/profile.html')

