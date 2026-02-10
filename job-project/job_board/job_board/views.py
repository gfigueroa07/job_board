from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from users .models import Profile
from job_board .forms import ProfileForm, ProfileEditForm
from django.urls import path
from django.http import HttpResponse
from .forms import JobDetailsForm, JobCreateForm
from users.models import JobListing, JobApplication
from django.contrib.auth.decorators import login_required

from .models import XaropItem

def home(request):
    return render(request, 'job_board/home.html')

def job_page(request):
    jobs = JobListing.objects.all()
    if not jobs.exists():
        return render(request, 'job_board/job_page.html', {'message' : 'no job listings. Check back later'})
    return render(request, 'job_board/job_page.html', {'jobs': jobs})

def job_details(request, job_id):
    job = get_object_or_404(JobListing, id=job_id)
    application = None
    if request.user.is_authenticated and hasattr(request.user, 'profile'):
        application = JobApplication.objects.filter(
        job=job,
        applicant=request.user.profile).first()
    return render(request, 'job_board/job_details.html', {'job': job, 'application': application})
    
def job_list(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Login before posting a job.')
        return redirect('login')
    if request.method == 'POST':
        job_form = JobCreateForm(request.POST, request.FILES)
        job = job_form.save(commit=False)
        job.profile = request.user.profile
        job.save()
        return redirect('job_page')
    else:
        job_form = JobCreateForm()
    return render(request, 'job_board/job_list.html', {'job_form' : job_form})

@login_required
def job_edit(request, job_id):
    job = get_object_or_404(JobListing, id=job_id)
    if job.profile != request.user.profile:
        return redirect('job_details')
    if request.method == 'POST':
        form = JobDetailsForm(request.POST, request.FILES, instance=job)
        if form.is_valid():
            form.save()
            return redirect('job_details')
    else:
        form = JobDetailsForm(instance=job)
    return render(request, 'job_board/job_edit.html', {'form': form, 'job': job})

@login_required
def job_delete(request, job_id):
    job = get_object_or_404(JobListing, id=job_id)
    if job.profile != request.user.profile:
        return redirect('job_details')
    if request.method == 'POST':
        job.delete()
        return redirect('job_details')
    return render(request, 'job_board/job_delete.html', {'job': job})
    
    
    pass

def profile(request):
    return render(request, 'job_board/profile.html')



# This is an example of a class-based view. 
# You make a class that takes a type of View as parameter and then have methods for the HTTP verbs
from django.views import View
from django.shortcuts import render, redirect
from .forms import XaropItemForm
from .models import XaropItem

class XaropItemsView(View):
    template_name = "job_board/xarop_items.html"

    # Gets the existing items and fills the template with them and the form fields.
    def get(self, request, primary_key = None):
        # Get all items from DB
        items = XaropItem.objects.all()
        
        # Decide, based on if primary_key of an item was given or not, if we are creating or editing an item
        if primary_key:
            item = get_object_or_404(XaropItem, pk=primary_key)
            form = XaropItemForm(instance = item) # loads found XaropItem for editing
        else:
            item = None
            form = XaropItemForm() # new XaropItem
            
        return render(
            request, 
            self.template_name, 
            {
                "form": form # Form object bound to XaropItem model
                ,"items": items # all XaropItems's in DB
                ,"selected_item": item # XaropItem found with given PK, or empty if none found
            }
        )

    # Submits data from the open form. Usually done by a Submit/Create/etc button
    def post(self, request, primary_key = None):
        # Update existing XaropItem
        if primary_key:
            # Get item with specified PK from database
            item = get_object_or_404(XaropItem, pk = primary_key)
    
            # Get the form (that has been filled by the user) object from the HTTP request and binds it to the XaropItem from the DB
            # This means that the form object now has the "original" item and the item with the changes made by the user
            form = XaropItemForm(request.POST, instance = item)
        else:
            # Create new
            form = XaropItemForm(request.POST)
            item = None

        # The next line runs validation checks on the data as per the rules you set in the model
        # For example the min_length, max_length, required, etc
        if form.is_valid():
            # Creates or updates a XaropItem, depending on how form was created above (if it has an instance of an item or not)
            saved_item = form.save()
            # Take user back to items list. PRG pattern dictates we should use redirect to avoid a double POST. A redirect is always to a URL defined in urls.py, not directly to an HTML page
            # Giving it the pk of the saved item makes it so the page loads with the form filled with what was just edited/saved.
            return redirect("xarop_items_edit", primary_key = saved_item.pk)
        else:
            # If form is not valid, re-render the page with the error but this might seem strange because... where are the errors!
            # Django fills in form.errors with the existing errors so all you have to do is check for form.errors in the template and put them in your page where you want
            items = XaropItem.objects.all()
            return render(request, self.template_name, {"form": form, "items": items})
