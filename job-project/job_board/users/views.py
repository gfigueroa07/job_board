from django.shortcuts import render, redirect
from job_board .forms import ProfileForm


# Create your views here.


def profile_create(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            return redirect('profile_detail', profile_id=profile.id)
    else:
        form = ProfileForm()

    return render(request, 'profile_create.html', {'form': form})



