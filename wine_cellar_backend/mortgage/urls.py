from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MortgageApplicationViewSet, MortgageCollateralViewSet, RepaymentScheduleViewSet, RepaymentRecordViewSet

router = DefaultRouter()
router.register(r'applications', MortgageApplicationViewSet, basename='mortgage-application')
router.register(r'collaterals', MortgageCollateralViewSet, basename='mortgage-collateral')
router.register(r'schedules', RepaymentScheduleViewSet, basename='repayment-schedule')
router.register(r'records', RepaymentRecordViewSet, basename='repayment-record')

urlpatterns = [
    path('', include(router.urls)),
    path('applications/<int:pk>/submit/', MortgageApplicationViewSet.as_view({'post': 'submit'}), name='submit-application'),
    path('applications/<int:pk>/start-review/', MortgageApplicationViewSet.as_view({'post': 'start_review'}), name='start-review'),
    path('applications/<int:pk>/approve/', MortgageApplicationViewSet.as_view({'post': 'approve'}), name='approve-application'),
    path('applications/<int:pk>/reject/', MortgageApplicationViewSet.as_view({'post': 'reject'}), name='reject-application'),
    path('applications/<int:pk>/disburse/', MortgageApplicationViewSet.as_view({'post': 'disburse'}), name='disburse-application'),
    path('applications/<int:pk>/add-collateral/', MortgageApplicationViewSet.as_view({'post': 'add_collateral'}), name='add-collateral'),
    path('applications/<int:pk>/remove-collateral/', MortgageApplicationViewSet.as_view({'post': 'remove_collateral'}), name='remove-collateral'),
    path('applications/stats/', MortgageApplicationViewSet.as_view({'get': 'stats'}), name='mortgage-stats'),
    path('collaterals/<int:pk>/release/', MortgageCollateralViewSet.as_view({'post': 'release'}), name='release-collateral'),
    path('schedules/<int:pk>/record-payment/', RepaymentScheduleViewSet.as_view({'post': 'record_payment'}), name='record-payment'),
]
