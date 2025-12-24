from django.shortcuts import render, redirect, get_object_or_404
from job_board .forms import ProfileForm, ProfileEditForm
from users .models import Profile, Review
from django.urls import path
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout

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

@login_required
def profile_detail(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id)
    # reviews = profile.Review.all()
    return render(request, 'users/profile_detail.html', {
        'profile': profile,
        # 'reviews': reviews
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
    if request.method == 'POST':
        logout(request)
        return redirect('login')
    return HttpResponse('ligma')