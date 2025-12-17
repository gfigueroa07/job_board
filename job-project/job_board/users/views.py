from django.shortcuts import render, redirect
from job_board .forms import ProfileForm
from users .models import Profile
from django.shortcuts import render, get_object_or_404
from job_board .forms import ProfileForm, ProfileEditForm
from django.urls import path
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

# Create your views here.
# def home(request):
#     return render(request, 'users/home.html')

def profile_create(request):
    if request.method == 'POST':
        user_form = UserCreationForm(request.POST)
        profile_form = ProfileForm(request.POST, request.FILES)  # include files for avatar

        if user_form.is_valid() and profile_form.is_valid():
            # Save the user first
            user = user_form.save()
            
            # Save the profile, link it to the new user
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()

            # Log the user in immediately
            login(request, user)
            
            return redirect('job_board/home.html')  # replace 'home' with your URL name
    else:
        user_form = UserCreationForm()
        profile_form = ProfileForm()

    context = {'user_form': user_form, 'profile_form': profile_form}
    return render(request, 'users/user_login.html', context)

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