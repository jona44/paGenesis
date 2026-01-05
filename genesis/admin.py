from django.contrib import admin
from .models import Congregant, Activity, Contribution

@admin.register(Congregant)
class CongregantAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'phone_number', 'email', 'is_active']
    list_filter = ['is_active']
    search_fields = ['first_name', 'last_name', 'phone_number']

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ['name', 'amount', 'start_date', 'end_date', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']

@admin.register(Contribution)
class ContributionAdmin(admin.ModelAdmin):
    list_display = ['congregant', 'activity', 'amount_paid', 'payment_date', 'payment_method', 'sms_sent']
    list_filter = ['payment_date', 'activity', 'payment_method', 'sms_sent']
    search_fields = ['congregant__first_name', 'congregant__last_name']