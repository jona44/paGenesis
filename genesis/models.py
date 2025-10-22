from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.urls import reverse
from django.utils import timezone

class Congregant(models.Model):
    title      = models.CharField(max_length=10, blank=True,choices=[('Madzibaba', 'Madzibaba'), ('Madzimai', 'Madzimai')])
    first_name = models.CharField(max_length=100)
    last_name    = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    email        = models.EmailField(blank=True, null=True)
    date_joined  = models.DateField(default=timezone.now)
    is_active    = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} {self.first_name} "

    class Meta:
        ordering = ['first_name']



class Activity(models.Model):
    CONTRIBUTION_TYPES = [
        ('one_time', 'One-time Payment'),
        ('monthly', 'Monthly Contribution'),
        ('installment', 'Installment Plan'),
    ]
    
    name        = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    contribution_type = models.CharField( max_length=20,choices=CONTRIBUTION_TYPES,default='one_time')  
    amount      = models.DecimalField( max_digits=10,decimal_places=2,null=True, blank=True,validators=[MinValueValidator(0)],help_text="Amount for one-time or monthly payments" )
    start_date  = models.DateField(default=timezone.now)
    end_date    = models.DateField(null=True, blank=True)
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
            return self.name

    def get_absolute_url(self):
        return reverse('genesis:activity_detail', kwargs={'pk': self.pk})

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Activities"


class Contribution(models.Model):
    PAYMENT_TYPES = [
        ('full', 'Full Payment'),
        ('deposit', 'Deposit'),
        ('installment', 'Installment'),
        ('monthly', 'Monthly'),
    ]
    congregant     = models.ForeignKey(Congregant, on_delete=models.CASCADE, related_name='contributions')
    activity           = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='contributions')
    payment_type       = models.CharField(max_length=20, choices=PAYMENT_TYPES, default='full')
    amount_paid        = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    installment_number = models.PositiveIntegerField(null=True, blank=True)
    payment_date       = models.DateField(default=timezone.now)
    payment_method     = models.CharField(max_length=50, choices=[
        ('cash', 'Cash'),
        ('mobile_money', 'Mobile Money'),
        ('bank_transfer', 'Bank Transfer'),
        ('check', 'Check')
    ], default='cash')
    recorded_by       = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    recorded_at       = models.DateTimeField(auto_now_add=True)
    notes             = models.TextField(blank=True)
    sms_sent          = models.BooleanField(default=False)
    sms_status        = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ['-payment_date', '-recorded_at']

    def __str__(self):
        return f"{self.congregant} - {self.activity} - ${self.amount_paid}"

    @property
    def payment_description(self):
        """Generate human-readable payment description"""
        if self.payment_type == 'deposit':
            return "Deposit"
        elif self.payment_type == 'installment' and self.installment_number:
            return f"Installment {self.installment_number}"
        elif self.payment_type == 'monthly':
            return "Monthly"
        else:
            return "Full Payment"
        
    