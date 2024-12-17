from django.urls import path, include
from drf_spectacular.views import SpectacularSwaggerView

from .schema import AdminSchemaView, SchemaView
from .views import (
    CtiButlerProxyView,
    AdminCtiButlerProxyView,
)

urlpatterns = [
    path("api/v1/<path:path>", CtiButlerProxyView.as_view(), name="proxy"),
    path("admin/api/v1/<path:path>", AdminCtiButlerProxyView.as_view(), name="admin-proxy"),
    path('schema/schema-json', SchemaView.as_view(), name='schema-json'),
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url="../schema-json"),
        name="swagger-ui",
    ),
    path('api/schema/schema-json', SchemaView.as_view(), name='schema-json'),
    path('admin/schema/schema-json', AdminSchemaView.as_view(), name='admin-schema-json'),
    path(
        "admin/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url="../schema-json"),
        name="swagger-ui",
    ),
]
