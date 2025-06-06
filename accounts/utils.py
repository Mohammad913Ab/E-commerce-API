from django.conf import settings

from random import randint

def random_otp() -> int:
    """
    Generate a random 4-digit OTP (One-Time Password).
    
    Returns:
        int: A random integer between 1000 and 9999 inclusive.
    """
    return randint(1000, 9999)

def send_otp(user, otp:int) -> bool:
    """
    Sends OTP based on DEBUG setting.

    In DEBUG mode, logs the OTP and returns True.
    In production, send SMS (TODO) and return False.

    Args:
        user: User instance with a mobile number.
        otp: One-Time Password to send.

    Returns:
        bool: True if logged, False if SMS should be sent.
    """
    if settings.DEBUG:
        print(f'[DEBUG] OTP for {user.mobile}: {otp}')
        return True
    else:
        # TODO: send sms 
        return False
    