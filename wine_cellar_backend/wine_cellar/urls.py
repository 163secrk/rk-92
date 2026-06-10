from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    return Response({
        'name': '高端私人酒窖管理系统 API',
        'version': '1.0.0',
        'endpoints': {
            'auth': '/api/auth/',
            'monitoring': '/api/monitoring/',
            'collection': '/api/collection/',
            'mortgage': '/api/mortgage/',
            'tasting': '/api/tasting/',
            'sales': '/api/sales/',
        }
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api_root),
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/monitoring/', include('monitoring.urls')),
    path('api/collection/', include('collection.urls')),
    path('api/mortgage/', include('mortgage.urls')),
    path('api/tasting/', include('tasting.urls')),
    path('api/sales/', include('sales.urls')),
]
