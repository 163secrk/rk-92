from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CustomerViewSet, SaleOrderViewSet, AuctionRecordViewSet, SalesStatsViewSet,
    customer_register, current_user_info
)

router = DefaultRouter()
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'orders', SaleOrderViewSet, basename='sale-order')
router.register(r'auctions', AuctionRecordViewSet, basename='auction')

urlpatterns = [
    path('', include(router.urls)),
    path('stats/overview/', SalesStatsViewSet.as_view({'get': 'overview'}), name='sales-overview'),
    path('auth/register/', customer_register, name='customer-register'),
    path('auth/me/', current_user_info, name='current-user-info'),
]
