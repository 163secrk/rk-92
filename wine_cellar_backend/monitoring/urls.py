from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WineCellarViewSet, SensorReadingViewSet, AlertViewSet

router = DefaultRouter()
router.register(r'cellars', WineCellarViewSet, basename='cellar')
router.register(r'readings', SensorReadingViewSet, basename='reading')
router.register(r'alerts', AlertViewSet, basename='alert')

urlpatterns = [
    path('', include(router.urls)),
]
