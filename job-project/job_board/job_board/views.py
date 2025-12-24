from django.shortcuts import render, redirect
from job_board .forms import ProfileForm
from users .models import Profile
from django.shortcuts import render, get_object_or_404
from job_board .forms import ProfileForm, ProfileEditForm
from django.urls import path
from django.http import HttpResponse
from .forms import JobDetailsForm, JobCreateForm
from users.models import JobListing

def home(request):
    return render(request, 'job_board/home.html')

def job_details(request):
    jobs = JobListing.objects.all()
    if not jobs.exists():
        return render(request, 'job_board/job_details.html', {'message' : 'no job listings. Check back later'})
    return render(request, 'job_board/job_details.html', {'jobs': jobs})

def job_list(request):
    if not request.user.is_authenticated:
        return render(
            request,
            'users/user_login.html',
            {'message': 'Login before posting a job'}
        )
    if request.method == 'POST':
        job_form = JobCreateForm(request.POST, request.FILES)
        if not job_form.is_valid():
            return render(request, 'users/user_login.html', {'message' : 'Login before posting a job'})
        job = job_form.save(commit=False)
        job.profile = request.user.profile
        job.save()
            # if not job_form.is_valid():
            #     return render(request, 'users/user_login.html', {'message' : 'Login before posting a job'})
        return redirect('job_details')
    else:
        job_form = JobCreateForm()
    return render(request, 'job_board/job_list.html', {'job_form' : job_form})

# def profile(request):
#     return render(request, 'job_board/profile.html')