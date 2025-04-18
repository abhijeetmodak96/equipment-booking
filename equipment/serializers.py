from rest_framework import serializers
from django.db import models  
from .models import Equipment

class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipment
        fields = ['id', 'name', 'type', 'location', 'total_quantity', 'is_available']
        read_only_fields = ['id']