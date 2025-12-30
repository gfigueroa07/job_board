from django.shortcuts import render, redirect, get_object_or_404
from job_board .forms import ProfileForm, ProfileEditForm, UserReviewsForm
from users .models import Profile, Review
from django.urls import path
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.db.models import Avg


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
    reviews = Review.objects.filter(review_written=profile)
    average_rating = Review.objects.filter(review_written=profile).aggregate(Avg('rating'))['rating__avg']
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
    print("POST REQUEST RECEIVED edit")

    if request.method == 'POST':
        profile = request.user.profile
        form = ProfileEditForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile_detail', profile_id=profile.id)
    else:
        form = ProfileEditForm(instance=profile)
    return render(request, 'users/profile_edit.html', {'form': form})

def user_login(request):
    print("POST REQUEST RECEIVED login")

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

def review_page(request, profile_id):
    # if request.method == 'POST':
    profile = get_object_or_404(Profile, id=profile_id)
    reviews = Review.objects.filter(review_written=profile)
    return render(request, 'users/review_page.html', {'profile': profile, 'reviews': reviews})

@login_required
def review_create(request, profile_id):
    reviewed_profile = get_object_or_404(Profile, id=profile_id)
    if request.user.profile == reviewed_profile:
        messages.error(request, 'Cant Review yourself')
        print("SELF REVIEW BLOCK HIT") #debug test
        return redirect('profile_detail', profile_id=profile_id)
    existing_review = Review.objects.filter(
        review_received=request.user.profile,
        review_written=reviewed_profile
    ).exists()
    if existing_review:
        messages.error(request, 'You have an  existing review')
        return redirect('profile_detail', profile_id=profile_id)
    print("POST REQUEST RECEIVED cr")
    if request.method == 'POST':
        form = UserReviewsForm(request.POST, request.FILES)
        if form.is_valid():
            review = form.save(commit=False)
            review.review_received = request.user.profile
            review.review_written = reviewed_profile
            print("SAVING REVIEW") #debug test
            review.save()
            return redirect('profile_detail', profile_id=profile_id)
    else:
        form = UserReviewsForm()
    return render(request, 'users/review_create.html', {'form': form, 'profile': reviewed_profile})
    
@login_required
def review_edit(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    if review.review_received != request.user.profile:
        return redirect('profile_detail', profile_id=review.review_written.id)
    if request.method =='POST':
        form = UserReviewsForm(request.POST, request.FILES, instance=review)
        if form.is_valid():
            form.save()
            return redirect('profile_detail', profile_id=review.review_written.id)
    else:
        form = UserReviewsForm(instance=review)
    return render(request, 'users/review_edit.html', {'form': form, 'review': review})

@login_required
def review_delete(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    if review.review_received != request.user.profile:
        return redirect('profile_detail', profile_id=review.review_written.id)
    if request.method == 'POST':
        review.delete()
        return redirect('profile_detail', profile_id=review.review_written.id)
    return render(request, 'users/review_delete.html', {'review': review})