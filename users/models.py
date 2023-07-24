from django.db import models
from django.contrib.auth.models import AbstractBaseUser

class User(AbstractBaseUser):
    full_name = models.CharField(max_length = 100)
    nickname = models.CharField(max_length = 25, unique = True)
    email = models.CharField(max_length = 250, unique = True)
    password = models.CharField(max_length = 100)
    created_at = models.DateTimeField(auto_now_add = True)

    class Meta:
        db_table = 'user'

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name', 'nickname', 'password']

    def __str__(self):
        return self.email
