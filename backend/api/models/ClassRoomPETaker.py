from django.db import models

class ClassRoomPETaker(models.Model):
    class_member_id = models.ForeignKey('ClassMember', on_delete=models.CASCADE)
    class_room_pe_id = models.ForeignKey('ClassRoomPE', on_delete=models.CASCADE)

    PENDING = 0
    COMPLETED = 1
    
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (COMPLETED, 'Completed'),
    ]

    status = models.PositiveIntegerField(choices=STATUS_CHOICES, default=PENDING)

    date_created = models.DateTimeField(auto_now=True)
    date_updated = models.DateTimeField(auto_now=True)
