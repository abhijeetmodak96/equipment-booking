from rest_framework import viewsets, permissions
from rest_framework.response import Response
from .models import Booking
from .models import Equipment
from .serializers import BookingSerializer
from rest_framework.decorators import api_view
from django.db.models import Sum
from datetime import datetime, time

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]  # all actions require login
    
    def get_queryset(self):
        """Limit booking visibility based on role:
        - Admin: see all bookings.
        - Manager: see all bookings (or could be limited to their team's bookings if team concept exists).
        - Employee: see only their own bookings.
        """
        user = self.request.user
        if user.is_staff:  # Admin (staff or superuser)
            return Booking.objects.all()
        elif user.groups.filter(name='Manager').exists():
            return Booking.objects.all()
            # If we had a way to identify a manager's team, we could filter those.
            # For simplicity, managers can also see all bookings, to help avoid conflicts.
        else:
            # Employee
            return Booking.objects.filter(user=user)
    
    def perform_create(self, serializer):
        """Override to handle instance creation via serializer.
        We pass the request context for serializer to use in validating and setting fields.
        """
        serializer.save()  # serializer.create will handle setting user/created_by

    def perform_update(self, serializer):
        instance = self.get_object()
        user = self.request.user
        # employees may update only their own booking
        if (not user.is_staff and not user.groups.filter(name='Manager').exists()
                and instance.user != user):
            raise permissions.PermissionDenied("You may edit only your own bookings.")
        serializer.save()
    
    def perform_destroy(self, instance):
        """Custom delete: allow only certain roles to delete (cancel) bookings.
        Employees can only cancel their own bookings.
        Managers/Admin can cancel any booking.
        """
        user = self.request.user
        # Check permission: If user is not admin/manager and not the owner, deny deletion
        if (not user.is_staff) and (not user.groups.filter(name='Manager').exists()) and (instance.user != user):
            raise permissions.PermissionDenied("You do not have permission to cancel this booking.")
        # Otherwise, allow deletion (or we could set status to canceled instead of actual delete)
        instance.delete()

    
@api_view(['GET'])
    # @permission_classes([IsAuthenticated])   # comment this to make it public
def availability_view(request):
    start_str = request.GET.get("start")
    end_str = request.GET.get("end")

    if not (start_str and end_str):
        return Response({"detail": "start and end query params (YYYY-MM-DD) are required."}, status=400)

    try:
        start_date = datetime.strptime(start_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_str, "%Y-%m-%d")
    except ValueError:
        return Response({"detail": "Invalid date format. Use YYYY-MM-DD."}, status=400)

    # Convert to full-day datetime range
    start_datetime = datetime.combine(start_date, time.min)
    end_datetime = datetime.combine(end_date, time.max)

    data = []
    for equip in Equipment.objects.filter(is_available=True):
        overlapping = Booking.objects.filter(
            equipment=equip,
            status="active",
            start_time__lt=end_datetime,
            end_time__gt=start_datetime
        ).aggregate(total=Sum('quantity'))["total"] or 0

        data.append({
            "equipment_id": equip.id,
            "name": equip.name,
            "type": equip.type,
            "free_units": max(0, equip.total_quantity - overlapping)
        })

    return Response(data)