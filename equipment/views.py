from rest_framework import viewsets, permissions
from .models import Equipment
from .serializers import EquipmentSerializer

class EquipmentViewSet(viewsets.ModelViewSet):
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer
    permission_classes = [permissions.IsAuthenticated]  # Base permission
    
    def get_permissions(self):
        """Customize permissions: 
        - Admin users can create/update/delete.
        - Authenticated users (any role) can read/list.
        """
        if self.action in ['list', 'retrieve']:
            # Anyone logged in can view equipment list or details
            return [permissions.IsAuthenticated()]
        else:
            # Only admin (staff) can modify equipment
            return [permissions.IsAdminUser()]

