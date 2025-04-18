from rest_framework import serializers
from django.db import models 
from .models import Booking
from datetime import timedelta 
from django.db import transaction      # for atomic rollback if any date collides

class BookingSerializer(serializers.ModelSerializer):
    # Nest some related info for convenience (optional):
    equipment_name = serializers.ReadOnlyField(source='equipment.name')
    user_username = serializers.ReadOnlyField(source='user.username')

    recurrence_interval = serializers.ChoiceField(
        choices=[("daily", "Daily"), ("weekly", "Weekly")],
        required=False, allow_null=True
    )
    recurrence_count = serializers.IntegerField(
        required=False, allow_null=True, min_value=1
    )
    
    class Meta:
        model = Booking
        fields = ['id', 'equipment', 'equipment_name', 'user', 'user_username',
                  'created_by', 'start_time', 'end_time', 'quantity', 'status', 
                  'recurrence_interval','recurrence_count']
        read_only_fields = ['id', 'status', 'created_by'] 
        # 'user' will be set automatically for employees (and managers can specify another user)
    
    def validate(self, attrs):
        """Validate booking data for time conflicts and quantity limits."""
        # Ensure end_time is after start_time
        if 'start_time' in attrs and 'end_time' in attrs:
            if attrs['end_time'] <= attrs['start_time']:
                raise serializers.ValidationError("End time must be after start time.")
        # If quantity is provided, ensure it's at least 1
        if 'quantity' in attrs:
            if attrs['quantity'] < 1:
                raise serializers.ValidationError("Quantity must be at least 1.")
        # If equipment provided, check availability
        # (We will do conflict checking in create() where we have access to all data)
        return attrs
    
    
    def create(self, validated):
        """
        Handles single and recurring bookings.
        1. Runs normal availability checks for the *first* slot.
        2. If recurrence_* present, repeats the same logic N‑1 more times,
           shifting by 1 day or 1 week each loop.
        3. All rows are inserted inside a DB transaction; any clash rolls everything back.
        """
        request_user = self.context['request'].user

        # -----------------------------------------------------------
        # 0) Decide who the booking is FOR  (same logic you had)
        booking_user = validated.pop('user', None) or request_user
        if booking_user != request_user:
            if not (request_user.is_staff or request_user.groups.filter(name='Manager').exists()):
                raise serializers.ValidationError("Employees cannot create bookings for other users.")
        validated['user'] = booking_user
        validated['created_by'] = request_user
        # -----------------------------------------------------------

        # pull out (and remove) the bonus params so they’re not saved
        recur = validated.pop("recurrence_interval", None)
        count = validated.pop("recurrence_count", 1) or 1

        equipment   = validated['equipment']
        start_dt    = validated['start_time']
        end_dt      = validated['end_time']
        qty         = validated['quantity']
        delta       = timedelta(days=1) if recur == "daily" else timedelta(weeks=1)

        # small helper for availability check
        def slot_free(start, end):
            overlapping = Booking.objects.filter(
                equipment=equipment, status="active"
            ).filter(
                models.Q(start_time__lt=end) & models.Q(end_time__gt=start)
            )
            booked = overlapping.aggregate(total=models.Sum("quantity"))["total"] or 0
            return booked + qty <= equipment.total_quantity

        if not equipment.is_available:
            raise serializers.ValidationError(f"Equipment '{equipment.name}' is currently not available for booking.")

        # ---------- ATOMIC so we don’t end up with partial series ----------
        with transaction.atomic():
            bookings = []
            for _ in range(count):
                if not slot_free(start_dt, end_dt):
                    raise serializers.ValidationError(
                        f"Time slot {start_dt:%Y‑%m‑%d %H:%M} already full for '{equipment.name}'."
                    )
                booking = Booking.objects.create(
                    equipment   = equipment,
                    user        = booking_user,
                    created_by  = request_user,
                    start_time  = start_dt,
                    end_time    = end_dt,
                    quantity    = qty,
                    status      = "active"
                )
                bookings.append(booking)
                # shift window for next occurrence
                start_dt += delta
                end_dt   += delta
            # DRF expects one instance back – return first; front‑end can ignore
            return bookings[0]