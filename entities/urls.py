from django.urls import path, include
# from rest_framework.documentation import include_docs_urls
from rest_framework.schemas import get_schema_view
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView


urlpatterns = [
    path("openapi/", get_schema_view(
        title="Entities API",
        description="Basic DRF schema",
        version="1.0.0"
    ), name="openapi-schema"),
    path("api/v1/", include("entities.v1.urls"))
]


# Docs
urlpatterns += [
    # JSON schema OpenAPI
    path("schema/", SpectacularAPIView.as_view(), name="schema"),

    # Swagger UI
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),

    # ReDoc
    path("redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
