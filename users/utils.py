import re
import jwt
from django.conf import settings
from django.core.mail import send_mail
from datetime import datetime, timedelta, timezone

from users.models import User
    
def generate_account_verification_token(data: dict):
    data['iat'] = datetime.now(tz = timezone.utc)
    data['exp'] = datetime.now(tz = timezone.utc) + (settings.EMAIL_VERIFICATION_EXP_TIME_DELTA or timedelta(hours=3))

    return jwt.encode(data, settings.SECRET_KEY, algorithm = 'HS256')

def generate_authentication_tokens(data: dict):
    access_token = dict({
        'iat': datetime.now(tz = timezone.utc),
        'exp': datetime.now(tz = timezone.utc) + settings.ACCESS_TOKEN_LIFETIME_DELTA,
        'type': 'access',
    }, **data)

    refresh_token = dict({
        'iat': datetime.now(tz = timezone.utc),
        'exp': datetime.now(tz= timezone.utc) + settings.REFRESH_TOKEN_LIFETIME_DELTA,
        'type': 'refresh',
    }, **data)

    return {
        'access_token': jwt.encode(access_token, settings.SECRET_KEY, algorithm = 'HS256'),
        'refresh_token': jwt.encode(refresh_token, settings.SECRET_KEY, algorithm = 'HS256'),
    }

def generate_and_send_email_verification_token(user_email: str):
    verification_token = generate_account_verification_token({ 'email': user_email })

    user_record = User.objects.get(email = user_email)
    user_record.verification_token = verification_token
    user_record.save()

    send_mail(
        subject = 'Welcome to Squiz!',
        message = f'Welcome to Squiz! In order to continue using your new account, please verify your email using the following link: https://squiz.com/account/verification/{verification_token}',
        recipient_list = [user_email],
        from_email = settings.EMAIL_HOST_USER
    )