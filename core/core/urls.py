from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from drf_yasg.renderers import SwaggerYAMLRenderer, SwaggerUIRenderer, ReDocRenderer
from rest_framework import (permissions, routers)
from rest_framework.routers import DefaultRouter
from auth.views import AuthViewSet


router = DefaultRouter()
router.register(r'auth', AuthViewSet, basename='auth')


schema_view = get_schema_view(
    openapi.Info(
        title="NTUB-AUTH-SERVER API",
        default_version='v1',
        description="北商大認證伺服器 API",
        contact=openapi.Contact(email="11146001@ntub.edu.tw"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0),
         name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger',
         cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc',
         cache_timeout=0), name='schema-redoc'),
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]
