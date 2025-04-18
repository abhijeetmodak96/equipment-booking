from django.db import models

class Equipment(models.Model):
    name = models.CharField(max_length=100, unique=True)  # Name of the equipment item
    type = models.CharField(max_length=50)                # Category/type (e.g., "Projector", "Laptop")
    location = models.CharField(max_length=100, blank=True, null=True)  # Location (optional)
    total_quantity = models.PositiveIntegerField()        # How many units available
    is_available = models.BooleanField(default=True)      # Availability status (False if under maintenance)
    created_at = models.DateTimeField(auto_now_add=True)  # Set only when created
    updated_at = models.DateTimeField(auto_now=True)      # Set on every update
    
    def __str__(self):
        return f"{self.name} ({self.type})"
    
    class Meta:
        # Example constraint: ensure quantity is non-negative (PositiveIntegerField already enforces >=0 at model level)
        # Ensure uniqueness on name (and location if needed)
        constraints = [
            models.CheckConstraint(check=models.Q(total_quantity__gte=0), name="quantity_non_negative"),
        ]
