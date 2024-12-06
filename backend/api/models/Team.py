from django.db import models

class Team(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)

    CLOSE = 0
    OPEN = 1
    status_choices = (
        (OPEN, 'open'),
        (CLOSE, 'closed'),
    )
    status = models.PositiveSmallIntegerField(choices=status_choices, null=True, blank=True)

    date_created = models.DateTimeField(auto_now=True)
    date_updated = models.DateTimeField(auto_now=True)

    REQUIRED_FIELDS = ['name', 'max_members']