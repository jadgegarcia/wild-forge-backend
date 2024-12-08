from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)

    ADMIN = 0
    MODERATOR = 1
    BASIC = 2
    role_choices = (
        (ADMIN, 'Admin'),
        (MODERATOR, 'Moderator'),
        (BASIC, 'Basic'),
    )
    role = models.PositiveSmallIntegerField(choices=role_choices, null=True, blank=True)

    date_created = models.DateTimeField(auto_now=True)
    date_updated = models.DateTimeField(auto_now=True)

    # Disable username field
    username = None
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'password']
    