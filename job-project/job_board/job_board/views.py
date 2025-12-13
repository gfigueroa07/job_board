from django.shortcuts import render, redirect
from job_board .forms import ProfileForm
from users .models import Profile
from django.shortcuts import render, get_object_or_404
from job_board .forms import ProfileForm, ProfileEditForm
from django.urls import path
from django.http import HttpResponse
from .forms import JobList
from users.models import JobListing

def home(request):
    return render(request, 'job_board/home.html')

def job_details(request):
    jobs = JobListing.objects.all()
    if not jobs.exists():
        return render(request, 'job_board/job_details.html', {'message' : 'no job listings. Check back later'})
    return render(request, 'job_board/job_details.html', {'jobs': jobs})

def job_list(request):
    return render(request, 'job_board/job_list.html')

def profile(request):
    return render(request, 'job_board/profile.html')