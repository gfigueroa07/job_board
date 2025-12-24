from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from users .models import Profile
from job_board .forms import ProfileForm, ProfileEditForm
from django.urls import path
from django.http import HttpResponse
from .forms import JobDetailsForm, JobCreateForm
from users.models import JobListing
from django.contrib.auth.decorators import login_required


def home(request):
    return render(request, 'job_board/home.html')

def job_details(request):
    jobs = JobListing.objects.all()
    if not jobs.exists():
        return render(request, 'job_board/job_details.html', {'message' : 'no job listings. Check back later'})
    return render(request, 'job_board/job_details.html', {'jobs': jobs})


def job_list(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Login before posting a job.')
        return redirect('login')
    if request.method == 'POST':
        job_form = JobCreateForm(request.POST, request.FILES)
        job = job_form.save(commit=False)
        job.profile = request.user.profile
        job.save()
        return redirect('job_details')
    else:
        job_form = JobCreateForm()
    return render(request, 'job_board/job_list.html', {'job_form' : job_form})

# def profile(request):
#     return render(request, 'job_board/profile.html')