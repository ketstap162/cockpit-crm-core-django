from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView


urlpatterns = [
    path("api/auth/", include("auth.urls")),
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
