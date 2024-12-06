from django.db import models

class Rating(models.Model):
    classmember_id = models.ForeignKey('ClassMember', on_delete=models.CASCADE)
    pitch_id = models.ForeignKey('Pitch', on_delete=models.CASCADE)
    meeting_id = models.ForeignKey('Meeting', on_delete=models.CASCADE)
    meeting_criteria_id = models.ForeignKey('MeetingCriteria', on_delete=models.CASCADE)
    rating = models.DecimalField(max_digits=3, decimal_places=2)
    
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True)