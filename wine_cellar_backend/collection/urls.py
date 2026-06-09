from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from .views import WineViewSet, ValuationHistoryViewSet, CollectionStatsViewSet

router = DefaultRouter()
router.register(r'wines', WineViewSet, basename='wine')
router.register(r'valuations', ValuationHistoryViewSet, basename='valuation')

stats_router = routers.NestedSimpleRouter(router, r'wines', lookup='wine')
stats_router.register(r'history', ValuationHistoryViewSet, basename='wine-valuations')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(stats_router.urls)),
    path('stats/overview/', CollectionStatsViewSet.as_view({'get': 'overview'}), name='collection-overview'),
    path('stats/valuation-trend/', CollectionStatsViewSet.as_view({'get': 'valuation_trend'}), name='valuation-trend'),
    path('stats/maturity-distribution/', CollectionStatsViewSet.as_view({'get': 'maturity_distribution'}), name='maturity-distribution'),
    path('stats/expiry-alerts/', CollectionStatsViewSet.as_view({'get': 'expiry_alerts'}), name='expiry-alerts'),
]
