from django.db import models

class ClassRoomPE(models.Model):
    peer_eval_id = models.ForeignKey('PeerEval', on_delete=models.CASCADE)
    class_id = models.ForeignKey('ClassRoom', on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now=True)
    date_updated = models.DateTimeField(auto_now=True)
