from django.db import models

class MeetingPresentor(models.Model):
    meeting_id = models.ForeignKey('Meeting', on_delete=models.CASCADE)
    team_id = models.ForeignKey('Team', on_delete=models.CASCADE, default=None, null=True, blank=True)
    pitch_id = models.ForeignKey('Pitch', on_delete=models.CASCADE, null=True, blank=True)
    is_rate_open = models.BooleanField(default=False)
