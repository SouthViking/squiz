import re
import jwt
from django.conf import settings
from datetime import datetime, timedelta, timezone
from django.core.exceptions import ValidationError

def validate_strong_password(password: str):
    # Regular expression that checks whether a password is strong or not based on the following rules:
    # 1. It needs to have more or equal than 8 characters and less or equal than 30.
    # 2. At least one uppercase English letter.
    # 3. At least one lowercase English letter.
    # 4. At least one digit.
    # 5. At least one special character.
    strong_password_regex = '^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,30}$'

    if re.match(strong_password_regex, password) is None:
        raise ValidationError('The provided password is not strong enough.')
    
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