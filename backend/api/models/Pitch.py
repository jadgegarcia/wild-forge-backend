from django.db import models

class Pitch(models.Model):
    team_id = models.ForeignKey('Team', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True)
    