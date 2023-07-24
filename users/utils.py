import re
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