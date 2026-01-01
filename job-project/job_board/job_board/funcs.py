from django.db.models import Case, When, Value, BooleanField

# helper functions to avoid reusing code




def review_sanitization(num):
    if num < 1 or num > 5:
        print('Please enter a number betwewen 1-5')
    else:
        pass
    

def filter_and_sort(queryset, filters=None, sort_by=None, user_profile=None):
    """
    Dynamic filtering and sorting for any queryset.

    Parameters:
    - queryset: initial queryset (Job.objects.all() or Review.objects.all())
    - filters: dictionary of filters, e.g., {'location': 'Scranton, PA'}
    - sort_by: string, options: 'new', 'old', 'rating', 'my_first'
    - user_profile: required if sort_by='my_first' for reviews
    """

    # Apply filters
    if filters:
        queryset = queryset.filter(**filters)

    # Apply sorting
    if sort_by == 'new':
        queryset = queryset.order_by('-created_at')
    elif sort_by == 'old':
        queryset = queryset.order_by('created_at')
    elif sort_by == 'rating':
        queryset = queryset.order_by('-rating')
    elif sort_by == 'my_first' and user_profile:
        # Custom sorting: user’s items first
        queryset = queryset.annotate(
            my_item=Case(
                When(review_written=user_profile, then=Value(True)),
                default=Value(False),
                output_field=BooleanField()
            )
        ).order_by('-my_item', '-created_at')
    
    return queryset
