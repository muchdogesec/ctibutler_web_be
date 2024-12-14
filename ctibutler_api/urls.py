from django.urls import path, include
from drf_spectacular.views import SpectacularSwaggerView

from .schema import SchemaView
from .views import (
    CtiButlerProxyView,
)

urlpatterns = [
    path("api/v1/<path:path>", CtiButlerProxyView.as_view(), name="proxy"),
    path('schema/schema-json', SchemaView.as_view(), name='schema-json'),
    path(
        "schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url="../schema-json"),
        name="swagger-ui",
    ),
]
