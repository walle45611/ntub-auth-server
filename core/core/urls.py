from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from rest_framework.routers import DefaultRouter
from auth.views import AuthViewSet

# Router for API version 1
router_v1 = DefaultRouter()
router_v1.register(r'auth', AuthViewSet, basename='auth')
api_v1_urls = [
    path('', include(router_v1.urls)),
    path('schema/', SpectacularAPIView.as_view(api_version='v1'), name='schema-v1'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema-v1'), name='swagger-ui-v1'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema-v1'), name='redoc-v1'),
]

router_v2 = DefaultRouter()
api_v2_urls = [
    path('', include(router_v2.urls)),
    path('schema/', SpectacularAPIView.as_view(api_version='v2'), name='schema-v2'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema-v2'), name='swagger-ui-v2'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema-v2'), name='redoc-v2'),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include((api_v1_urls, 'api-v1'), namespace='v1')),
    path('api/v2/', include((api_v2_urls, 'api-v2'), namespace='v2')),
]
