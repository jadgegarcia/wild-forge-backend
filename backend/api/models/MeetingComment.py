from django.db import models

class MeetingComment(models.Model):
    classmember_id = models.ForeignKey('ClassMember', on_delete=models.CASCADE)
    comment = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True)
    