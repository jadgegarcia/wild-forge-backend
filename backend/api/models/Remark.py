from django.db import models

class Remark(models.Model):
    classmember_id = models.ForeignKey('ClassMember', on_delete=models.CASCADE)
    pitch_id = models.ForeignKey('Pitch', on_delete=models.CASCADE)
    meeting_id = models.ForeignKey('Meeting', on_delete=models.CASCADE)
    remark = models.TextField()
    
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True)
    