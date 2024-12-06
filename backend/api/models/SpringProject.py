from django.db import models


class SpringProject(models.Model):
    team_id = models.ForeignKey('Team', on_delete=models.SET_NULL, null=True, default=None)
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(default='')
    is_active = models.BooleanField(default=False)
    score = models.FloatField(default=0)
    reason = models.TextField(default='')
    date_created = models.DateTimeField(auto_now=True)
