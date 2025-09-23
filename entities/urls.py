from django.urls import path, include

urlpatterns = [
    # path("api/v1/", ),
    path("api/v1/", include("entities.v1.urls"))
]
