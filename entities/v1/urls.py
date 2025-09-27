from django.urls import path
from entities.v1 import views

urlpatterns = [
    path("entities/", views.EntitiesView.as_view(), name="entity"),
    path("entities/<uuid:entity_uuid>", views.EntitySnapshotView.as_view(), name="entity-snapshot"),
    path("entities/<uuid:entity_uuid>/history", views.EntityHistoryView.as_view(), name="entity-history"),
    path("entities/entities-asof", views.EntityAsOfView.as_view(), name="entities-asof"),
    path("entities/diff", views.EntityDiffView.as_view(), name="entities-diff")
]
