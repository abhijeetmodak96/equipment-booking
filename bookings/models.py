from django.db import models
from django.conf import settings  # to get AUTH_USER_MODEL
from equipment.models import Equipment

class Booking(models.Model):
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name="bookings")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookings")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_bookings")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    quantity = models.PositiveIntegerField()  # number of equipment units booked
    status = models.CharField(max_length=20, default="active")  # "active" or "canceled"
    
    def __str__(self):
        return f"{self.equipment.name} booking by {self.user} from {self.start_time} to {self.end_time}"
    
    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(end_time__gt=models.F('start_time')), name="end_after_start"),
            # Optional: you could add an exclusion constraint for no overlapping booking:
            # This requires psycopg2 and PostgreSQL with btree_gist extension.
            # Example (not active by default):
            # models.ExclusionConstraint(
            #     name='no_overlap_booking',
            #     expressions=[
            #         ('equipment', models.EXACT), 
            #         (models.Func(models.F('start_time'), models.F('end_time'), function='TSTZRANGE'), models.Overlap)
            #     ],
            #     condition=models.Q(status="active")
            # )
        ]
