from django import forms
from .models import Congregant, Activity, Contribution

class CongregantForm(forms.ModelForm):
    class Meta:
        model = Congregant
        fields = [
            'title', 'first_name', 'last_name', 'phone_number', 
            'email', 'date_joined'
        ]
        widgets = {
            'date_joined': forms.DateInput(attrs={'type': 'date'}),
        }


class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ['name', 'description', 'contribution_type', 'amount', 'start_date', 'end_date']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'amount': forms.NumberInput(attrs={'step': '0.01'}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set helpful labels and placeholders
        self.fields['amount'].label = "Target Amount"
        self.fields['amount'].help_text = "The expected amount for this activity"


class ContributionForm(forms.ModelForm):
    class Meta:
        model = Contribution
        fields = [
            'congregant', 'activity', 'payment_type', 'amount_paid',
            'installment_number', 'payment_date', 'payment_method', 'notes'
        ]
        widgets = {
            'amount_paid': forms.NumberInput(attrs={'step': '0.01', 'placeholder': '0.00'}),
            'payment_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'installment_number': forms.NumberInput(attrs={'placeholder': 'e.g., 1, 2, 3...'}),
        }
    
    def __init__(self, *args, **kwargs):
        # Pop the user argument before calling super, as it's not expected.
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filter querysets to only active congregants and active/unexpired activities
        from django.db.models import Q
        from django.utils import timezone
        today = timezone.now().date()
        
        self.fields['congregant'].queryset = self.fields['congregant'].queryset.filter(is_active=True) # type: ignore
        self.fields['activity'].queryset = self.fields['activity'].queryset.filter(
            is_active=True
        ).filter(
            Q(end_date__isnull=True) | Q(end_date__gte=today)
        ) # type: ignore
        
        # Set initial payment date to today
        self.fields['payment_date'].initial = forms.utils.timezone.now().date() # type: ignore
        
        # Customize labels and help texts
        self.fields['payment_type'].label = "Payment Type"
        self.fields['installment_number'].label = "Installment Number"
        self.fields['installment_number'].help_text = "Required for installment payments"
        self.fields['amount_paid'].label = "Amount Paid"
        
        # Make payment_type and installment_number not required initially
        # We handle their validation and defaults in the clean() method based on activity type
        self.fields['payment_type'].required = False
        self.fields['installment_number'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        payment_type = cleaned_data.get('payment_type')
        installment_number = cleaned_data.get('installment_number')
        amount_paid = cleaned_data.get('amount_paid')
        activity = cleaned_data.get('activity')
        
        if activity and activity.contribution_type == 'monthly':
            # For monthly activities, we don't use installments & payment type is always 'full'
            cleaned_data['payment_type'] = 'full'
            cleaned_data['installment_number'] = None
        else:
            # Validate installment number for non-monthly installment payments
            if payment_type == 'installment' and not installment_number:
                self.add_error('installment_number', 'Installment number is required for installment payments.')
            
            if payment_type == 'installment' and installment_number and installment_number < 1:
                self.add_error('installment_number', 'Installment number must be at least 1.')
        
        # Validate amount
        if amount_paid and amount_paid <= 0:
            self.add_error('amount_paid', 'Amount paid must be greater than 0.')
        
        return cleaned_data