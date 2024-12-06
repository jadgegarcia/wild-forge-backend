from django.db import models

class Feedback(models.Model):
    pitch_id = models.ForeignKey('Pitch', on_delete=models.CASCADE)
    meeting_id = models.ForeignKey('Meeting', on_delete=models.CASCADE)
    feedback = models.TextField()
    
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True)
    