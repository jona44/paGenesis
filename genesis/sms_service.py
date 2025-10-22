import os
from django.conf import settings
from django.utils import timezone
import logging

# Import Twilio client if available; otherwise set to None and use mock functions
logger = logging.getLogger(__name__)

# Dynamically import Twilio client to avoid static analysis errors when package is not installed
try:
    import importlib
    _twilio_rest = importlib.import_module('twilio.rest')
    Client = getattr(_twilio_rest, 'Client', None)
except Exception:
    Client = None

def send_contribution_sms(contribution):
    """
    Send SMS notification for contribution using Twilio
    """
    # If Twilio client isn't available in this environment, use the mock
    if Client is None:
        return send_contribution_sms_mock(contribution)

    try:
        # Initialize Twilio client
        account_sid = settings.TWILIO_ACCOUNT_SID
        auth_token = settings.TWILIO_AUTH_TOKEN
        twilio_phone = settings.TWILIO_PHONE_NUMBER

        if not all([account_sid, auth_token, twilio_phone]):
            logger.error("Twilio settings (SID, AUTH_TOKEN, or PHONE_NUMBER) are not configured.")
            return False
            
        client = Client(account_sid, auth_token)
        
        # Format message
        message = f"""
        Hello {contribution.congregant.first_name},
        
        Thank you for your contribution of ${contribution.amount_paid} 
        towards {contribution.activity.name}.
        
        Date: {contribution.payment_date}
        Payment Method: {contribution.get_payment_method_display()}
        
        Blessings,
        {settings.CHURCH_NAME}
        """
        
        # Send SMS
        message = client.messages.create(
            body=message,
            from_=twilio_phone,
            to=contribution.congregant.phone_number
        )
        
        # Update contribution record
        contribution.sms_sent = True
        contribution.sms_status = message.status
        contribution.save()
        
        return True
        
    except Exception as e: # Catch specific Twilio exceptions for better error handling
        logger.error(f"SMS sending failed for congregant {contribution.congregant.pk}: {e}")
        contribution.sms_status = f"Failed: {str(e)}"
        contribution.save()
        return False

# Alternative: For testing without Twilio
def send_contribution_sms_mock(contribution):
    """ 
    Mock SMS service for development/testing when Twilio is not configured.
    """
    print(f"Mock SMS to {contribution.congregant.phone_number}:")
    print(f"Thank you for your contribution of ${contribution.amount_paid} towards {contribution.activity.name}")
    
    contribution.sms_sent = True
    contribution.sms_status = "Mock sent"
    contribution.save()
    
    return True

def send_welcome_sms(congregant):
    """
    Sends a welcome SMS to a new congregant.
    """ 
    if not congregant.phone_number:
        print(f"No phone number for {congregant.title} {congregant.first_name}, skipping welcome SMS.")
        return False
    # If Twilio isn't installed, use mock to avoid breaking during development/tests
    if Client is None:
        return send_welcome_sms_mock(congregant)

    try:
        # Initialize Twilio client
        account_sid = settings.TWILIO_ACCOUNT_SID
        auth_token = settings.TWILIO_AUTH_TOKEN
        twilio_phone = settings.TWILIO_PHONE_NUMBER

        if not all([account_sid, auth_token, twilio_phone]):
            logger.error("Twilio settings (SID, AUTH_TOKEN, or PHONE_NUMBER) are not configured.")
            return False

        client = Client(account_sid, auth_token)

        message_body = f"Welcome to {settings.CHURCH_NAME}, {congregant.title} {congregant.first_name}! We are so glad to have you join our community. Blessings!"

        # Send SMS
        client.messages.create(
            body=message_body,
            from_=twilio_phone,
            to=congregant.phone_number
        ) 
        logger.info(f"Welcome SMS sent to {congregant.title} {congregant.first_name}")
        return True
    
    except Exception as e: # Catch specific Twilio exceptions for better error handling
        logger.error(f"Welcome SMS sending failed for {congregant.title} {congregant.first_name}: {e}")
        return False


def send_welcome_sms_mock(congregant):
    """
    Mock welcome SMS service for development
    """
    if not congregant.phone_number:
        return False
    print(f"Mock Welcome SMS to {congregant.phone_number}:")
    print(f"Welcome to the church, {congregant.first_name}!")
    return True