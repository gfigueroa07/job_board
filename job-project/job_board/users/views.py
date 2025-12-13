from django.shortcuts import render, redirect
from job_board .forms import ProfileForm
from users .models import Profile
from django.shortcuts import render, get_object_or_404
from job_board .forms import ProfileForm, ProfileEditForm
from django.urls import path
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required



# Create your views here.
def home(request):
    return render(request, 'users/home.html')

@login_required
def profile_create(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            return redirect('users/profile_detail', profile_id=profile.id)
    else:
        form = ProfileForm()

    return render(request, 'users/profile_create.html', {'form': form})

@login_required
def profile_detail(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id)
    reviews = profile.reviews_received.all()
    return render(request, 'users/profile_detail.html', {
        'profile': profile,
        'reviews': reviews
    })


@login_required
def profile_edit(request):
    profile = request.user.profile

    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('users/profile_detail', profile_id=profile.id)
    else:
        form = ProfileEditForm(instance=profile)

    return render(request, 'users/profile_edit.html', {'form': form})

def user_login(request):
    return render(request, 'users/user_login.html')