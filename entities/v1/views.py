from datetime import datetime, timezone

from django.db import transaction
from django.db.models import OuterRef, Exists, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import exceptions as drf_exc
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models.scd2.changes import map_by_field, fill_dict_with_changes
from core.utils.orm import get_one_or_fail, get_one_or_none
from entities.models import Entity, EntityDetail
from . import docs
from . import serializers as sz


def index(request):
    mro = Entity.__mro__

    lst = []
    for x in mro:
        lst.append(str(x))

    resp = "".join(lst[:-3])
    return HttpResponse(mro[1].__class__.__name__)


class EntitiesView(APIView):
    @extend_schema(**docs.EntitiesViewDoc.get)
    def get(self, request):
        search_term = request.query_params.get("search")
        type_code = request.query_params.get("type")
        detail_code = request.query_params.get("detail_code")

        entities = Entity.objects.current()

        if search_term:
            entities = entities.filter(display_name__icontains=search_term)
        if type_code:
            entities = entities.filter(entity_type__code=type_code)

        if detail_code:
            entity_details = EntityDetail.objects.current().filter(detail_code=detail_code)
            entities = (
                entities
                .annotate(has_detail=Exists(
                    entity_details.filter(entity_uuid=OuterRef('uuid')))
                )
                .filter(has_detail=True)
            )

        serializer = sz.EntitySerializer(entities, many=True)
        return Response(serializer.data)

    @extend_schema(**docs.EntitiesViewDoc.post)
    def post(self, request):
        serializer = sz.EntityCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        display_name = serializer.validated_data["display_name"]
        entity_type = serializer.validated_data["entity_type_code"]
        details_data = serializer.validated_data.get("detail", {})

        with transaction.atomic():
            # Create entity
            entity = Entity(display_name=display_name, entity_type=entity_type)
            entity.ingest(rest=True)

            # Create details
            if details_data:
                EntityDetail(
                    entity_uuid=entity.uuid,
                    **details_data
                ).ingest()

        return Response({"uuid": str(entity.uuid)}, status=status.HTTP_201_CREATED)


class EntitySnapshotView(APIView):
    """
    GET /api/v1/entities/{entity_uuid}
    Return the current snapshot of an Entity and its details.
    """
    def get(self, request, entity_uuid):
        entity = get_object_or_404(
            Entity.objects.current(),
            uuid=entity_uuid
        )

        details_qs = get_one_or_fail(
            EntityDetail.objects.current().filter(entity_uuid=entity.uuid),
            rest=True,
        )

        serializer = sz.EntitySnapshotSerializer(entity)
        data = serializer.data
        data["detail"] = sz.EntityDetailSerializer(details_qs, many=False).data

        return Response(data, status=status.HTTP_200_OK)

    @extend_schema(**docs.EntitySnapshotViewDoc.patch)
    def patch(self, request, entity_uuid):
        save_list = []  # Order makes sense

        # Entity flow: process entity data only after ensuring it exists
        entity: Entity = get_one_or_fail(
            Entity.objects.current().filter(uuid=entity_uuid),
            rest=True,
        )

        entity_data = dict(request.data)
        entity_data.pop("detail", None)

        if entity.check_fields_change(entity_data):
            entity_nv, entity_ov = entity.new_version(**entity_data, save=False)
            save_list.append(entity_ov)  # Close old version first
            save_list.append(entity_nv)

            entity = entity_nv

        # Detail flow: only fetch entity detail if detail data is provided
        detail_data = request.data.get("detail", [])

        if detail_data:
            entity_detail: EntityDetail = get_one_or_none(
                EntityDetail.objects.current().filter(entity_uuid=entity_uuid),
                rest=True,
            )

            if entity_detail:
                if entity_detail.check_fields_change(detail_data):
                    detail_nv, detail_ov = entity_detail.new_version(**detail_data)
                    save_list.append(detail_ov)  # Close old version first
                    save_list.append(detail_nv)
            else:
                entity_detail = EntityDetail(
                    entity_uuid=entity_uuid,
                    **detail_data
                )
                # entity_detail.save()
                save_list.append(entity_detail)

        # Commit
        with transaction.atomic():
            for instance in save_list:
                instance.save()

        entity_serialized = sz.EntitySerializer(entity).data
        entity_detail_serialized = sz.EntityDetailSerializer(
            EntityDetail.objects.current().filter(entity_uuid=entity_uuid),
            many=True
        ).data

        return Response({
            "entity": entity_serialized,
            "detail": entity_detail_serialized
        }, status=status.HTTP_200_OK)


class EntityHistoryView(APIView):
    """
    GET /api/v1/entities/{entity_uuid}/history
    Return full SCD2 history for Entity and its EntityDetails.
    """
    def get(self, request, entity_uuid):
        get_object_or_404(Entity.objects.current(), uuid=entity_uuid)

        entity_history = Entity.objects.filter(uuid=entity_uuid).order_by("-valid_from")
        entity_history = sz.EntityHistorySerializer(entity_history, many=True).data

        entity_detail_history = EntityDetail.objects.filter(entity_uuid=entity_uuid).order_by("-valid_from")
        entity_detail_history = sz.EntityDetailHistorySerializer(entity_detail_history, many=True).data

        return Response(
            {
                "entity_history": entity_history,
                "entity_detail_history": entity_detail_history
            }
        )


class EntityAsOfView(APIView):
    """
    GET /api/v1/entities-asof?as_of=YYYY-MM-DD
    Returns a snapshot of all Entities and their Details valid at the specified date. Uses SCD2 logic.
    """
    @extend_schema(**docs.EntityAsOfViewDoc.get)
    def get(self, request):
        as_of_date_str = request.query_params.get("as_of")

        try:
            as_of_date = datetime.strptime(as_of_date_str, "%Y-%m-%d").date()
        except ValueError:
            raise drf_exc.ValidationError({"as_of": "Invalid date format. Use YYYY-MM-DD."})

        as_of_datetime = datetime.combine(as_of_date, datetime.min.time(), tzinfo=timezone.utc)

        filter_kwargs = {
            "valid_from__lte": as_of_datetime,
            "valid_to__gt": as_of_datetime,
        }
        filter_q = Q(**filter_kwargs) | Q(valid_from__lte=as_of_datetime, valid_to__isnull=True)

        entities = Entity.objects.filter(filter_q)
        entities = sz.EntityHistorySerializer(entities, many=True).data

        entity_details = EntityDetail.objects.filter(filter_q)
        entity_details = sz.EntityDetailHistorySerializer(entity_details, many=True).data

        return Response(
            {
                "entities": entities,
                "entity_details": entity_details
            }
        )


class EntityDiffView(APIView):
    @extend_schema(**docs.EntityDiffViewDoc.get)
    def get(self, request):
        from_date = request.query_params.get("from")
        to_date = request.query_params.get("to")

        try:
            from_date = datetime.strptime(from_date, "%Y-%m-%d").date()
        except ValueError:
            raise drf_exc.ValidationError({"from_date": "Invalid date format. Use YYYY-MM-DD."})

        try:
            to_date = datetime.strptime(to_date, "%Y-%m-%d").date()
        except ValueError:
            raise drf_exc.ValidationError({"from_date": "Invalid date format. Use YYYY-MM-DD."})

        from_dt = datetime.combine(from_date, datetime.min.time(), tzinfo=timezone.utc)
        to_dt = datetime.combine(to_date, datetime.max.time(), tzinfo=timezone.utc)

        filter_q = Q(valid_from__lte=to_dt) & (Q(valid_to__gte=from_dt) | Q(valid_to__isnull=True))

        entity_history = Entity.objects.filter(filter_q).order_by("-valid_from")
        entity_detail_history = EntityDetail.objects.filter(filter_q).order_by("-valid_from")

        response = {}

        entity_versions_by_uuid = map_by_field(entity_history, "uuid")
        detail_versions_by_uuid = map_by_field(entity_detail_history, "entity_uuid")

        entity_changes: dict = {}
        fill_dict_with_changes(entity_changes, entity_versions_by_uuid, "entity_history")
        fill_dict_with_changes(entity_changes, detail_versions_by_uuid, "entity_detail_history")

        response["entity_changes"] = entity_changes

        return Response(
            response
        )
