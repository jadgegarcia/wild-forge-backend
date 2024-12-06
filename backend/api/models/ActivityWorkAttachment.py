from django.db import models

from api.models import Activity

class ActivityWorkAttachment(models.Model):
    activity_id = models.ForeignKey('Activity', on_delete=models.CASCADE, null=True)
    description = models.TextField(max_length=100)
    file_attachment = models.FileField(upload_to='activity_work_submissions/', blank=True)
    date_created = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.description