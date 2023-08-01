from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

from .validators import validate_strong_password

class UserManager(BaseUserManager):
    def create(self, **kwargs):
        user = User(
            full_name = kwargs['full_name'],
            nickname = kwargs['nickname'],
            email = kwargs['email'],
            password = kwargs['password'],
        )
        user.full_clean()

        user.set_password(kwargs['password'])
        user.save()

class User(AbstractBaseUser):
    full_name = models.CharField(max_length = 100)
    nickname = models.CharField(max_length = 25, unique = True)
    email = models.CharField(max_length = 250, unique = True)
    password = models.CharField(max_length = 100, validators = [validate_strong_password])
    created_at = models.DateTimeField(auto_now_add = True)
    # Flag that allows to remove the account in case it hasn't been verified before the defined time.
    is_verified = models.BooleanField(default = False)
    verification_token = models.CharField(max_length = 200, null = True, blank = True)

    class Meta:
        db_table = 'user'

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name', 'nickname', 'password']

    objects = UserManager()

    def __str__(self):
        return self.email