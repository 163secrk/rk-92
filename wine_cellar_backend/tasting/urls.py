from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TastingEventViewSet, TastingAttendeeViewSet, TastingNoteViewSet, TastingStatsViewSet

router = DefaultRouter()
router.register(r'events', TastingEventViewSet, basename='tasting-event')
router.register(r'attendees', TastingAttendeeViewSet, basename='tasting-attendee')
router.register(r'notes', TastingNoteViewSet, basename='tasting-note')

urlpatterns = [
    path('', include(router.urls)),
    path('stats/overview/', TastingStatsViewSet.as_view({'get': 'overview'}), name='tasting-overview'),
]
