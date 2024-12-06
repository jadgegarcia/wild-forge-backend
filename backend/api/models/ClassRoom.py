from django.db import models

class ClassRoom(models.Model):
    class_code = models.CharField(max_length=8, unique=True)
    course_name = models.CharField(max_length=100)
    sections = models.CharField(max_length=100)
    schedule = models.CharField(max_length=100)
    max_teams_members = models.IntegerField(default=5)
    date_created = models.DateTimeField(auto_now=True)
    date_updated = models.DateTimeField(auto_now=True)

    REQUIRED_FIELDS = ['name', 'sections', 'schedule']

    invited_users = models.ManyToManyField('User', blank=True)
