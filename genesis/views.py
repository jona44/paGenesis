from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum, Count
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from .models import Congregant, Activity, Contribution
from .sms_service import send_contribution_sms, send_welcome_sms
from django.contrib.auth import logout
from .forms import CongregantForm, ActivityForm, ContributionForm
from django.contrib.auth import views as auth_views
from django.shortcuts import render
from django.db.models import Sum
from django.utils import timezone
from .models import Congregant, Activity, Contribution



@login_required
def dashboard(request):
    selected_activity_id = request.GET.get('activity')
    total_congregants = Congregant.objects.filter(is_active=True).count()
    active_activities = Activity.objects.filter(is_active=True)
    active_activities_count = active_activities.count()

    contributions = Contribution.objects.select_related('congregant', 'activity')
    if selected_activity_id:
        contributions = contributions.filter(activity_id=selected_activity_id)

    recent_contributions = contributions.order_by('-payment_date')[:10]

    current_month = timezone.now().month
    current_year = timezone.now().year
    monthly_total = Contribution.objects.filter(
        payment_date__month=current_month,
        payment_date__year=current_year
    ).aggregate(total=Sum('amount_paid'))['total'] or 0

    context = {
        'total_congregants': total_congregants,
        'active_activities': active_activities_count,
        'monthly_total': monthly_total,
        'recent_contributions': recent_contributions,
        'activities': active_activities,
        'selected_activity_id': int(selected_activity_id) if selected_activity_id else None,
    }

    # Calculate total for the selected activity if one is selected
    total_for_selected_activity = 0
    if selected_activity_id:
        total_for_selected_activity = contributions.aggregate(total=Sum('amount_paid'))['total'] or 0
    context['total_for_selected_activity'] = total_for_selected_activity

    # Determine the selected activity name (safe for templates)
    selected_activity_name = None
    if selected_activity_id:
        try:
            # active_activities is a queryset of active activities
            selected = active_activities.filter(id=selected_activity_id).first()
            if selected:
                selected_activity_name = selected.name
        except Exception:
            selected_activity_name = None

    # add the name to the context so templates can render it without method calls
    context['selected_activity_name'] = selected_activity_name

    # If request is from HTMX, render the wrapper partial that includes the
    # contributions table so responses contain the `#contributions-table`
    # element (required when using hx-swap="outerHTML").
    if request.headers.get('HX-Request'):
        return render(request, 'genesis/_contributions_table_wrapper.html', context)

    return render(request, 'genesis/dashboard.html', context)


@login_required
def congregant_list(request):
    congregants = Congregant.objects.filter(is_active=True)
    context = {'congregants': congregants}

    # If request is from HTMX, return the partial so it can be swapped into
    # the existing `#genesis` container. For normal requests (regular
    # browser navigation or redirects), render a full-page template that
    # includes the partial so the page has the base layout.
    if request.headers.get('HX-Request'):
        return render(request, 'genesis/congregants_list.html', context)

    return render(request, 'genesis/congregants_list_full.html', context)

@login_required
def add_congregant(request):
    if request.method == 'POST':
        form = CongregantForm(request.POST)
        if form.is_valid():
            congregant = form.save()
            
            # Send welcome SMS
            sms_success = send_welcome_sms(congregant)

            if sms_success:
                messages.success(request, f'Successfully added {congregant.title} {congregant.first_name}. A welcome SMS has been sent.')
            else:
                messages.warning(request, f'Successfully added {congregant.title} {congregant.first_name}, but the welcome SMS could not be sent.')

            # If this is an HTMX request, set HX-Redirect so the client navigates.
            if request.headers.get('HX-Request'):
                response = HttpResponse()
                response['HX-Redirect'] = reverse('genesis:congregant_list')
                return response

            # For normal (non-HTMX) requests, use a standard redirect so Django
            # returns a proper HTTP redirect response instead of an empty page.
            return redirect('genesis:congregant_list')
    else:
        form = CongregantForm()
    
    context= {
        'form': form
    }
    return render(request, 'genesis/add_congregant.html', context)




class HtmxLoginView(auth_views.LoginView):
    """
    Subclass of Django's LoginView that returns an HX-Redirect header
    when the request comes from HTMX so the client navigates instead of
    replacing a fragment with the login response.
    """
    def form_valid(self, form):
        response = super().form_valid(form)
        # If this was an HTMX request, set HX-Redirect to the success URL
        if self.request.headers.get('HX-Request'):
            try:
                redirect_url = self.get_success_url()
            except Exception:
                redirect_url = '/'
            response['HX-Redirect'] = redirect_url
        return response





def activity_list(request):
    activities = Activity.objects.annotate(
        total_contributed=Sum('contributions__amount_paid')
    ).order_by('-is_active', '-created_at')
    total_collected = activities.filter(total_contributed__isnull=False).aggregate(total=Sum('total_contributed'))['total'] or 0
    
    context = {
        'activities': activities, 
        'total_collected': total_collected
    }

    if request.headers.get('HX-Request'):
        return render(request, 'genesis/activity_list.html', context)

    return render(request, 'genesis/activity_list_full.html', context)


@login_required
def activity_create(request):
    if request.method == 'POST':
        form = ActivityForm(request.POST)
        if form.is_valid():
            activity = form.save()
            messages.success(request, f'Successfully created activity: {activity.name}.')
            
            if request.headers.get('HX-Request'):
                response = HttpResponse()
                response['HX-Redirect'] = reverse('genesis:activity_list')
                return response
            
            return redirect('genesis:activity_list')
    else:
        form = ActivityForm()
    
    context = {'form': form}
    return render(request, 'genesis/activity_create.html', context)



@login_required
def record_contribution(request):
    if request.method == 'POST':
        form = ContributionForm(request.POST, user=request.user)
        if form.is_valid():
            contribution = form.save(commit=False)
            contribution.recorded_by = request.user
            contribution.save()
            
            # Send SMS notification
            sms_success = send_contribution_sms(contribution)
            
            if sms_success:
                messages.success(request, f'Contribution recorded and SMS sent to {contribution.congregant.title} {contribution.congregant.first_name}')
            else:
                messages.warning(request, f'Contribution recorded but SMS failed to send to {contribution.congregant.title} {contribution.congregant.first_name}')

            return redirect('genesis:dashboard')
    else:
        form = ContributionForm(
            user=request.user, 
            initial={'payment_date': timezone.now().date()}
        )
    activities = Activity.objects.filter(is_active=True)
    congregants = Congregant.objects.filter(is_active=True)
    
    context = {
        'form': form,
        'activities': activities,
        'congregants': congregants,
    }
    return render(request, 'genesis/record_contribution.html', context)


@login_required
def contribution_list(request):
    contributions = Contribution.objects.select_related('congregant', 'activity').all()
    
    # Filtering
    activity_filter = request.GET.get('activity')
    if activity_filter:
        contributions = contributions.filter(activity_id=activity_filter)
    
    congregant_filter = request.GET.get('congregant')
    if congregant_filter:
        contributions = contributions.filter(congregant_id=congregant_filter)
    
    context = {
        'contributions': contributions,
        'activities': Activity.objects.all(),
        'congregants': Congregant.objects.filter(is_active=True)
    }
    return render(request, 'genesis/contributions.html', context)


@login_required
def get_congregant_contributions(request, congregant_id):
    congregant = get_object_or_404(Congregant, id=congregant_id)
    contributions = Contribution.objects.filter(congregant=congregant).select_related('activity')
    
    total_contributions = contributions.aggregate(total=Sum('amount_paid'))['total'] or 0
    
    data = {
        'congregant': {
            'name': congregant.title + ' ' + congregant.first_name,
            'phone': congregant.phone_number,
            'email': congregant.email
        },
        'contributions': [
            {
                'activity': contrib.activity.name,
                'amount': float(contrib.amount_paid),
                'date': contrib.payment_date.strftime('%Y-%m-%d'),
                
            }
            for contrib in contributions
        ],
        'total_contributions': float(total_contributions)
    }
    
    return JsonResponse(data)


@login_required
def congregant_detail(request, pk):
    congregant = get_object_or_404(Congregant, pk=pk)
    
    selected_activity_id = request.GET.get('activity')
    
    # Base queryset for contributions
    contributions = Contribution.objects.filter(congregant=congregant).select_related('activity').order_by('-payment_date')
    
    # Get unique activities this congregant has contributed to for filter buttons
    contributed_activities_ids = contributions.values_list('activity_id', flat=True).distinct()
    contributed_activities = Activity.objects.filter(id__in=contributed_activities_ids)
    
    # Filter contributions if an activity is selected
    if selected_activity_id:
        contributions = contributions.filter(activity_id=selected_activity_id)
    
    # Calculate totals
    total_contributions = contributions.aggregate(total=Sum('amount_paid'))['total'] or 0
    
    # Get selected activity name for display
    selected_activity_name = None
    if selected_activity_id:
        selected_activity = contributed_activities.filter(id=selected_activity_id).first()
        if selected_activity:
            selected_activity_name = selected_activity.name
    
    context = {
        'congregant': congregant,
        'contributions': contributions,
        'total_contributions': total_contributions,
        'contributed_activities': contributed_activities,
        'selected_activity_id': int(selected_activity_id) if selected_activity_id else None,
        'selected_activity_name': selected_activity_name,
    }

    # For HTMX requests, return only the contributions table partial
    if request.headers.get('HX-Request'):
        return render(request, 'genesis/partials/_congregant_contributions_wrapper.html', context)
        
    return render(request, 'genesis/congregant_detail.html', context)


@login_required
def congregant_edit(request, pk):
    congregant = get_object_or_404(Congregant, pk=pk)
    if request.method == 'POST':
        form = CongregantForm(request.POST, instance=congregant)
        if form.is_valid():
            form.save()
            messages.success(request, f'Updated {congregant.title} {congregant.first_name}.')
            return redirect('genesis:congregant_detail', pk=congregant.pk)
    else:
        form = CongregantForm(instance=congregant)

    return render(request, 'genesis/congregant_edit.html', {'form': form, 'congregant': congregant})


@login_required
def congregant_delete(request, pk):
    congregant = get_object_or_404(Congregant, pk=pk)
    if request.method == 'POST':
        # Soft-delete by marking inactive
        congregant.is_active = False
        congregant.save()
        messages.success(request, f'{congregant.title} {congregant.first_name} has been removed.')
        return redirect('genesis:congregant_list')

    return render(request, 'genesis/congregant_confirm_delete.html', {'congregant': congregant})


@login_required
def get_activity_details(request):
    activity_id = request.GET.get('activity')
    if not activity_id:
        # Return an empty div with a message if no activity is selected
        return render(request, 'genesis/partials/_activity_payment_details.html')

    activity = get_object_or_404(Activity, pk=activity_id)
    context = {'activity': activity}
    return render(request, 'genesis/partials/_activity_payment_details.html', context)

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect('login')
