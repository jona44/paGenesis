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
            'title': forms.Select(attrs={
                'class': 'mt-1 block w-full '
                'px-3 py-3 '
                'rounded-md '
                'border '
                'border-blue-300 '
                'hover:border-blue-300 '
                'hover:border-4 '
                'focus:ring-blue-300 '
                'focus:border-blue-300 '
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'mt-1 block w-full '
                'px-3 py-3 '
                'rounded-md '
                'border '
                'border-blue-300 '
                'hover:border-blue-300 '
                'hover:border-4 '
                'focus:ring-blue-300 '
                'focus:border-blue-300 '
                }),
            'last_name': forms.TextInput(attrs={
                'class': 'mt-1 block w-full '
                'px-3 py-3 '
                'rounded-md '
                'border '
                'border-blue-300 '
                'hover:border-blue-300 '
                'hover:border-4 '
                'focus:ring-blue-300 '
                'focus:border-blue-300 '
                }),
            'phone_number': forms.TextInput(attrs={
                'class': 'mt-1 block w-full '
                'px-3 py-3 '
                'rounded-md '
                'border '
                'border-blue-300 '
                'hover:border-blue-300 '
                'hover:border-4 '
                'focus:ring-blue-300 '
                'focus:border-blue-300 '
                }),
            'email': forms.EmailInput(attrs={
                'class': 'mt-1 block w-full '
                'px-3 py-3 '
                'border '
                'border-blue-300 '
                'hover:border-blue-300 '
                'hover:border-4 '
                'focus:ring-blue-300 '
                'focus:border-blue-300 '
                }),
            'date_joined': forms.DateInput(attrs={
                'type': 'date',
                'class': 'mt-1 block w-full '
                'px-3 py-3 '
                'border '
                'border-blue-300 '
                'hover:border-blue-300 '
                'hover:border-4 '
                'focus:ring-blue-300 '
                'focus:border-blue-300 '
                
                }),
        }


class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ['name', 'description', 'contribution_type', 'amount', 'start_date', 'end_date']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'mt-1 block '
                'w-full px-3 py-3 '
                'rounded-md '
                'border '
                'border-blue-300 '
                'hover:border-blue-300 '
                'hover:border-4 '
                'focus:ring-blue-300 '
                'focus:border-blue-300 '
                
            }),
            'description': forms.Textarea(attrs={
                'rows': 4,
                'class': 'w-full px-3 '
                'py-2 border '
                'border '
                'border-blue-300 '
                'hover:border-blue-300 '
                'hover:border-4 '
                'focus:ring-blue-300 '
                'focus:border-blue-300 '
                
            }),
            'contribution_type': forms.Select(attrs={
                'class': 'mt-1 block '
                'w-full '
                'px-3 py-3 '
                'rounded-md '
                'border '
                'border-blue-300 '
                'hover:border-blue-300 '
                'hover:border-4 '
                'focus:ring-blue-300 '
                'focus:border-blue-300 '
                
            }),
            'amount': forms.NumberInput(attrs={
                'step': '0.01',
                'class': 'mt-1 block '
                'w-full '
                'px-3 py-3 '
                'rounded-md '
                'border '
                'border-blue-300 '
                'hover:border-blue-300 '
                'hover:border-4 '
                'focus:ring-blue-300 '
                'focus:border-blue-300 '
            }),
            'start_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'mt-1 block w-full '
                'px-3 py-3 '
                'rounded-md '
                'border '
                'border-blue-300 '
                'hover:border-blue-300 '
                'hover:border-4 '
                'focus:ring-blue-300 '
                'focus:border-blue-300 '
            }),
            'start_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'mt-1 block w-full '
                'px-3 py-3 '
                'rounded-md '
                'border '
                'border-blue-300 '
                'hover:border-blue-300 '
                'hover:border-4 '
                'focus:ring-blue-300 '
                'focus:border-blue-300 '
            }),
            'end_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'mt-1 block '
                'w-full '
                'px-3 py-3 '
                'rounded-md '
                'border '
                'border-blue-300 '
                'hover:border-blue-300 '
                'hover:border-4 '
                'focus:ring-blue-300 '
                'focus:border-blue-300 '
            }),
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
            'congregant': forms.Select(attrs={
                'class': 'mt-1 block w-full '
                'px-3 py-3 '
                'rounded-md '
                'border '
                'border-blue-300 '
                'shadow-sm '
                'hover:border-blue-300 '
                'hover:border-4 '
                'focus:ring-blue-300 '
                'focus:border-blue-300',
                
            }),
            'activity': forms.Select(attrs={
                'class': 'mt-1 '
                'block w-full '
                'px-3 py-3 '
                'rounded-md '
                'border '
                'border-blue-300 '
                'shadow-sm '
                'hover:border-blue-300300 '
                'hover:border-4 '
                'focus:ring-blue-300300 '
                'focus:border-blue-300300',
            }),
            'payment_type': forms.Select(attrs={
                'class': 'mt-1 block w-full '
                    'px-3 py-3 '
                    'rounded-md '
                    'border '
                    'border-blue-300 '
                    'shadow-sm '
                    'hover:border-blue-300 '
                    'hover:border-4 '
                    'focus:ring-blue-300 '
                    'focus:border-blue-300',
            }),
            'payment_type': forms.Select(attrs={
                'class': 'mt-1 block w-full '
                    'px-3 py-3 '
                    'rounded-md '
                    'border '
                    'border-blue-300 '
                    'shadow-sm '
                    'hover:border-blue-300 '
                    'hover:border-4 '
                    'focus:ring-blue-300 '
                    'focus:border-blue-300',
            }),
            'payment_type': forms.RadioSelect(attrs={
                'class': 'mt-2 space-y-2 '
                    'px-3 py-3 '
                    'rounded-md '
                    'border '
                    'border-blue-300 '
                    'shadow-sm '
                    'hover:border-blue-300 '
                    'hover:border-4 '
                    'focus:ring-blue-300 '
                    'focus:border-blue-300',
            }),
            'amount_paid': forms.NumberInput(attrs={
                'step': '100.00',
                'class': 'mt-1 block w-full '
                'px-3 py-3 '
                'rounded-md '
                'border '
                'border-blue-300 '
                'shadow-sm '
                'hover:border-blue-300 '
                'hover:border-4 '
                'focus:ring-blue-300 '
                'focus:border-blue-300',
                'min': '100.00',
                'placeholder': '0.00'
            }),
            'installment_number': forms.NumberInput(attrs={
                'class': 'mt-1 block '
                'w-full '
                'px-3 py-3 '
                'rounded-md '
                'border '
                'border-blue-300 '
                'shadow-sm '
                'hover:border-blue-300 '
                'hover:border-4 '
                'focus:ring-blue-300 '
                'focus:border-ray-300 '
                'focus:ring-blue-300 '
                'focus:border-blue-300',
                'placeholder': 'e.g., 1, 2, 3...'
            }),
            'payment_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'mt-1 '
                'block w-full '
                'px-3 py-3 '
                'rounded-md '
                'border '
                'border-blue-300 '
                'shadow-sm '
                'hover:border-blue-300 '
                'hover:border-4 '
                'focus:ring-blue-300 '
                'focus:border-blue-300'
            }),
            'payment_method': forms.Select(attrs={
                'class': 'mt-1 block w-full '
                'px-3 py-3 '
                'rounded-md '
                'border '
                'border-blue-300 '
                'shadow-sm '
                'hover:border-blue-300 '
                'hover:border-4 '
                'focus:ring-blue-300 '
                'focus:border-blue-300'
            }),
            'notes': forms.Textarea(attrs={
                'rows': 3,
                'class': 'mt-1 block '
                'w-full '
                'px-3 py-2 '
                'rounded-md '
                'border '
                'border-blue-300 '
                'shadow-sm '
                'hover:border-blue-300 '
                'hover:border-4 '
                'focus:ring-blue-300 '
                'focus:border-blue-300',
                'placeholder': 'Any additional notes about this payment...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        # Pop the user argument before calling super, as it's not expected.
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filter querysets to only active congregants and activities
        self.fields['congregant'].queryset = self.fields['congregant'].queryset.filter(is_active=True) # type: ignore
        self.fields['activity'].queryset = self.fields['activity'].queryset.filter(is_active=True) # type: ignore
        
        # Set initial payment date to today
        self.fields['payment_date'].initial = forms.utils.timezone.now().date() # type: ignore
        
        # Customize labels and help texts
        self.fields['payment_type'].label = "Payment Type"
        self.fields['installment_number'].label = "Installment Number"
        self.fields['installment_number'].help_text = "Required for installment payments"
        self.fields['amount_paid'].label = "Amount Paid"
        
        # Make installment_number not required initially
        self.fields['installment_number'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        payment_type = cleaned_data.get('payment_type')
        installment_number = cleaned_data.get('installment_number')
        amount_paid = cleaned_data.get('amount_paid')
        activity = cleaned_data.get('activity')
        
        # Validate installment number for installment payments
        if payment_type == 'installment' and not installment_number:
            self.add_error('installment_number', 'Installment number is required for installment payments.')
        
        if payment_type == 'installment' and installment_number and installment_number < 1:
            self.add_error('installment_number', 'Installment number must be at least 1.')
        
        # Validate amount
        if amount_paid and amount_paid <= 0:
            self.add_error('amount_paid', 'Amount paid must be greater than 0.')
        
        return cleaned_data