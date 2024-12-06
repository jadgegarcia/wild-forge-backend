from django.db import models

class Message(models.Model):
    ROLE_CHOICES = (
        ('system', 'System'),
        ('assistant', 'Assistant'),
        ('user', 'User'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
