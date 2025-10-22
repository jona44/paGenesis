from abc import ABC, abstractmethod
from django.conf import settings

class SMSBackend(ABC):
    @abstractmethod
    def send_sms(self, phone_number, message):
        pass

class ConsoleSMSBackend(SMSBackend):
    """
    SMS backend that prints messages to the console (for development)
    """
    def send_sms(self, phone_number, message):
        print(f"SMS to {phone_number}: {message}")
        return True

def get_sms_backend():
    """
    Returns the configured SMS backend
    For now, returns the console backend
    In production, you would configure this to use your preferred SMS provider
    """
    return ConsoleSMSBackend()

def send_contribution_sms(contribution):
    """
    Sends an SMS notification for a contribution
    """
    message = (
        f"Thank you for your contribution of {contribution.amount} "
        f"towards {contribution.activity.name}. "
        f"God bless you! - Your Church"
    )
    
    backend = get_sms_backend()
    return backend.send_sms(contribution.congregant.phone_number, message)