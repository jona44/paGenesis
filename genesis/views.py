from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum, Count, Q
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from django.conf import settings
from django.contrib.auth import logout, views as auth_views
from .models import Congregant, Activity, Contribution
from .sms_service import send_contribution_sms, send_welcome_sms
from .forms import CongregantForm, ActivityForm, ContributionForm



@login_required
def dashboard(request):
    selected_activity_id = request.GET.get('activity')
    total_congregants = Congregant.objects.filter(is_active=True).count()
    today = timezone.now().date()
    active_activities = Activity.objects.filter(
        is_active=True
    ).filter(
        Q(end_date__isnull=True) | Q(end_date__gte=today)
    )
    active_activities_count = active_activities.count()

    contributions = Contribution.objects.select_related('congregant', 'activity').filter(
        activity__is_active=True
    ).filter(
        Q(activity__end_date__isnull=True) | Q(activity__end_date__gte=today)
    )
    if selected_activity_id:
        contributions = contributions.filter(activity_id=selected_activity_id)

    recent_contributions = contributions.order_by('-payment_date', '-recorded_at')[:10]

    now = timezone.now()
    current_month = now.month
    current_year = now.year
    
    monthly_total = Contribution.objects.filter(
        activity__is_active=True,
        payment_date__month=current_month,
        payment_date__year=current_year
    ).filter(
        Q(activity__end_date__isnull=True) | Q(activity__end_date__gte=today)
    ).aggregate(total=Sum('amount_paid'))['total'] or 0

    # Data for Monthly Contributions Chart (current year) - Multi-line
    from django.db.models.functions import ExtractMonth
    chart_datasets = []
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    # Get monthly sums grouped by activity and month for current year
    monthly_stats = Contribution.objects.filter(
        activity__in=active_activities,
        payment_date__year=current_year
    ).annotate(
        month=ExtractMonth('payment_date')
    ).values('activity_id', 'activity__name', 'month').annotate(
        total=Sum('amount_paid')
    ).order_by('activity_id', 'month')

    # Organize into datasets
    stats_dict = {}
    for stat in monthly_stats:
        aid = stat['activity_id']
        if aid not in stats_dict:
            stats_dict[aid] = {
                'label': stat['activity__name'],
                'data': [0.0] * 12
            }
        stats_dict[aid]['data'][stat['month'] - 1] = float(stat['total'])
    
    chart_datasets = list(stats_dict.values())

    # Add a 'Total' dataset if we have data
    if chart_datasets:
        total_data = [0.0] * 12
        for ds in chart_datasets:
            for i, val in enumerate(ds['data']):
                total_data[i] += val
        chart_datasets.insert(0, {
            'label': 'Total (All Active)',
            'data': total_data,
            'is_total': True
        })

    context = {
        'total_congregants': total_congregants,
        'active_activities': active_activities_count,
        'monthly_total': monthly_total,
        'recent_contributions': recent_contributions,
        'activities': active_activities,
        'selected_activity_id': int(selected_activity_id) if selected_activity_id else None,
        'chart_labels': months,
        'chart_datasets': chart_datasets,
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
            selected = active_activities.filter(id=selected_activity_id).first()
            if selected:
                selected_activity_name = selected.name
        except Exception:
            selected_activity_name = None

    context['selected_activity_name'] = selected_activity_name

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
    show_closed = request.GET.get('show_closed') == 'true'
    today = timezone.now().date()
    
    activities = Activity.objects.annotate(
        total_contributed=Sum('contributions__amount_paid')
    )
    
    if not show_closed:
        activities = activities.filter(
            is_active=True
        ).filter(
            Q(end_date__isnull=True) | Q(end_date__gte=today)
        )
        
    activities = activities.order_by('-is_active', '-created_at')
    
    # Calculate progress for each activity
    today = timezone.now().date()
    for activity in activities:
        # Progress calculation
        if activity.amount and activity.amount > 0:
            total = float(activity.total_contributed or 0)
            goal = float(activity.amount)
            activity.progress_percent = min(100, round((total / goal) * 100, 1))
        else:
            activity.progress_percent = None
        
        # Expiry check
        activity.is_expired = activity.end_date and activity.end_date < today

    total_collected = activities.filter(total_contributed__isnull=False).aggregate(total=Sum('total_contributed'))['total'] or 0
    
    context = {
        'activities': activities, 
        'total_collected': total_collected,
        'show_closed': show_closed,
    }

    if request.headers.get('HX-Request'):
        return render(request, 'genesis/activity_list.html', context)

    return render(request, 'genesis/activity_list_full.html', context)

@login_required
def toggle_activity_status(request, pk):
    activity = get_object_or_404(Activity, pk=pk)
    activity.is_active = not activity.is_active
    activity.save()
    
    status = "reopened" if activity.is_active else "closed"
    messages.success(request, f"Activity '{activity.name}' has been {status}.")
    
    if request.headers.get('HX-Request'):
        return activity_list(request)
    return redirect('genesis:activity_list')

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

            if request.headers.get('HX-Request'):
                response = HttpResponse()
                response['HX-Redirect'] = reverse('genesis:dashboard')
                return response
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
        'activity_types': {a.id: a.contribution_type for a in activities},
    }
    
    if request.headers.get('HX-Request'):
        return render(request, 'genesis/record_contribution.html', context)
    return render(request, 'genesis/record_contribution_full.html', context)


@login_required
def contribution_list(request):
    contributions = Contribution.objects.select_related('congregant', 'activity').all().order_by('-payment_date', '-recorded_at')
    
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
    contributions = Contribution.objects.filter(congregant=congregant).select_related('activity').order_by('-payment_date', '-recorded_at')
    
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

import csv
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch

@login_required
def download_receipt(request, pk):
    contribution = get_object_or_404(Contribution, pk=pk)
    
    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="receipt_{contribution.id}.pdf"'

    # Create the PDF object, using the response object as its "file."
    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    # Draw things on the PDF
    p.setFont("Helvetica-Bold", 24)
    p.drawCentredString(width/2.0, height - 1*inch, settings.CHURCH_NAME)
    
    p.setFont("Helvetica", 12)
    p.drawCentredString(width/2.0, height - 1.3*inch, "Official Contribution Receipt")
    
    p.setStrokeColor(colors.blue)
    p.line(1*inch, height - 1.5*inch, width - 1*inch, height - 1.5*inch)
    
    # Content body
    p.setFont("Helvetica-Bold", 12)
    p.drawString(1*inch, height - 2*inch, "Congregant:")
    p.setFont("Helvetica", 12)
    p.drawString(2.5*inch, height - 2*inch, f"{contribution.congregant.title} {contribution.congregant.first_name} {contribution.congregant.last_name}")
    
    p.setFont("Helvetica-Bold", 12)
    p.drawString(1*inch, height - 2.3*inch, "Activity:")
    p.setFont("Helvetica", 12)
    p.drawString(2.5*inch, height - 2.3*inch, f"{contribution.activity.name}")
    
    p.setFont("Helvetica-Bold", 12)
    p.drawString(1*inch, height - 2.6*inch, "Amount Paid:")
    p.setFont("Helvetica-Bold", 14)
    p.drawString(2.5*inch, height - 2.6*inch, f"${contribution.amount_paid}")
    
    p.setFont("Helvetica-Bold", 12)
    p.drawString(1*inch, height - 2.9*inch, "Date:")
    p.setFont("Helvetica", 12)
    p.drawString(2.5*inch, height - 2.9*inch, f"{contribution.payment_date}")
    
    p.setFont("Helvetica-Bold", 12)
    p.drawString(1*inch, height - 3.2*inch, "Payment Method:")
    p.setFont("Helvetica", 12)
    p.drawString(2.5*inch, height - 3.2*inch, f"{contribution.get_payment_method_display()}")
    
    if contribution.notes:
        p.setFont("Helvetica-Bold", 12)
        p.drawString(1*inch, height - 3.5*inch, "Notes:")
        p.setFont("Helvetica", 10)
        p.drawString(2.5*inch, height - 3.5*inch, f"{contribution.notes}")

    # Footer
    p.setFont("Helvetica-Oblique", 10)
    p.drawCentredString(width/2.0, 1*inch, "Thank you for your generous contribution. God Bless.")
    p.setFont("Helvetica", 8)
    p.drawCentredString(width/2.0, 0.8*inch, f"Receipt generated on {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()
    return response

@login_required
def export_contributions_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="contributions_{timezone.now().strftime("%Y%m%d")}.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Congregant', 'Activity', 'Amount Paid', 'Date', 'Method', 'Notes', 'Recorded By'])

    contributions = Contribution.objects.filter(activity__is_active=True).select_related('congregant', 'activity', 'recorded_by').order_by('-payment_date', '-recorded_at')
    
    # Filter by user selections if any
    activity_id = request.GET.get('activity')
    if activity_id:
        contributions = contributions.filter(activity_id=activity_id)

    for c in contributions:
        writer.writerow([
            c.id,
            f"{c.congregant.title} {c.congregant.first_name} {c.congregant.last_name}",
            c.activity.name,
            c.amount_paid,
            c.payment_date,
            c.get_payment_method_display(),
            c.notes,
            c.recorded_by.username
        ])

    return response
