from django.urls import path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi





schema_views = get_schema_view(
    openapi.Info(
        title="Django Menu",
        default_version='v1',
        description='Product management',
        license=openapi.License(name ="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny], 
)

urlpatterns = [
    path('swagger(?P<format>\.json|\.yaml)',schema_views.without_ui(cache_timeout=0),name='schema-json'),
    path('swagger/',schema_views.with_ui('swagger', cache_timeout=0),name='schema-swagger-ui'),
    path('redoc/',schema_views.with_ui('redoc', cache_timeout=0),name='schema-redoc'),]
