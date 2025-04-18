from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from equipment.views import EquipmentViewSet
from bookings.views import BookingViewSet, availability_view

# DRF router for viewsets
router = routers.DefaultRouter()
router.register(r'equipment', EquipmentViewSet, basename='equipment')
router.register(r'bookings', BookingViewSet, basename='booking')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),  # include our API routes under /api/
]


# Swagger / OpenAPI documentation:
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Equipment Booking API",
        default_version='v1',
        description="API documentation for the Equipment Booking Management System",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],  # Allow anyone to view the docs
)

urlpatterns += [
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    # path('swagger.json/', schema_view.without_ui(cache_timeout=0), name='schema-json'),  # if JSON needed
]
urlpatterns += [
    path('api/availability/', availability_view, name='availability'),
]