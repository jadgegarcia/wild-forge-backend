from django.db import models

class ActivityComment(models.Model):
    activity_id = models.ForeignKey('Activity', on_delete=models.CASCADE, null = True)
    user_id = models.ForeignKey('User', on_delete=models.CASCADE, null = True)  
    comment = models.TextField(max_length=10000)
    date_created = models.DateTimeField(auto_now=True)