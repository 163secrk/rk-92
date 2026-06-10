from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomerViewSet, SaleOrderViewSet, AuctionRecordViewSet, SalesStatsViewSet

router = DefaultRouter()
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'orders', SaleOrderViewSet, basename='sale-order')
router.register(r'auctions', AuctionRecordViewSet, basename='auction')

urlpatterns = [
    path('', include(router.urls)),
    path('stats/overview/', SalesStatsViewSet.as_view({'get': 'overview'}), name='sales-overview'),
]
