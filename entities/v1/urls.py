from django.urls import path
from entities.v1.views import index

urlpatterns = [
    path("index/", index),
]
