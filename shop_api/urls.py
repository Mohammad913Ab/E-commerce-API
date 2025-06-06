from django.contrib import admin
from django.urls import path, include

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Apps
    path('api/', include('accounts.urls')),
    
    #SCHEMA
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger'),
    path('api/docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc')
]
