from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiExample, OpenApiResponse
from . import serializers as sz


class EntitiesViewDoc:
    get = {
        "parameters": [
            OpenApiParameter("search", str, description="Search term"),
            OpenApiParameter("type", str, description="Entity type code"),
            OpenApiParameter("detail_code", str, description="Detail code filter"),
        ],
        "responses": sz.EntitySerializer(many=True)
    }
    post = {
        "request": sz.EntityCreateSerializer,
        "responses": {201: "Created Entity UUID"},
        "examples": [
            OpenApiExample(
                "Example payload",
                value={
                    "display_name": "SomeEntity",
                    "entity_type_code": "INSTITUTION",
                    "detail": {
                        "value": "red"
                    }
                }
            )
        ]
    }


class EntitySnapshotViewDoc:
    get = {
        "responses": sz.EntitySnapshotSerializer
    }
    patch = {
        "request": sz.EntityUpdateSerializer,
        "responses": {
            200: sz.EntitySerializer,
            404: OpenApiResponse(description="Entity not found")
        },
        "description": "Update an Entity and its details by UUID"
    }


class EntityHistoryViewDoc:
    get = {
        "responses": {
            200: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description="SCD2 history for Entity and EntityDetails",
                examples=[
                    OpenApiExample(
                        "Example response",
                        value={
                            "entity_history": [
                                {"uuid": "uuid-string", "display_name": "Entity1", "valid_from": "2025-09-27T11:42:32Z",
                                 "valid_to": None, "is_current": True}
                            ],
                            "entity_detail_history": [
                                {"detail_code": "uuid-string", "value": "red", "valid_from": "2025-09-27T11:42:32Z",
                                 "valid_to": None, "is_current": True}
                            ]
                        }
                    )
                ]
            )
        }
    }


class EntityAsOfViewDoc:
    get = {
        "parameters": [
            OpenApiParameter(
                name="as_of",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Date to fetch the snapshot for (format: YYYY-MM-DD)",
                examples=[
                    OpenApiExample(
                        name="Example date",
                        value="2025-09-01"
                    )
                ]
            )
        ],
        "description": (
            "Fetch a snapshot of all entities and their details "
            "valid as of a given date using SCD2 logic"
        ),
        "responses": {
            200: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description="Entities and EntityDetails valid at given date",
                examples=[
                    OpenApiExample(
                        "Example response",
                        value={
                            "entities": [
                                {"uuid": "uuid-string", "display_name": "Entity1", "valid_from": "2025-09-01T00:00:00Z",
                                 "valid_to": None, "is_current": True}
                            ],
                            "entity_details": [
                                {"detail_code": "uuid-string", "value": "red", "valid_from": "2025-09-01T00:00:00Z",
                                 "valid_to": None, "is_current": True}
                            ]
                        }
                    )
                ]
            )
        }
    }


class EntityDiffViewDoc:
    get = {
        "parameters": [
            OpenApiParameter(
                name="from",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Date to fetch the snapshot for (format: YYYY-MM-DD)",
                examples=[
                    OpenApiExample("Example date", value="2025-09-01")
                ]
            ),
            OpenApiParameter(
                name="to",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Date to fetch the snapshot for (format: YYYY-MM-DD)",
                examples=[
                    OpenApiExample("Example date", value="2025-09-01")
                ]
            )
        ],
        "description": "Return differences in Entities and EntityDetails between two dates using SCD2",
        "responses": {
            200: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description="Entity changes mapped by UUID",
                examples=[
                    OpenApiExample(
                        name="Example entity changes",
                        value={
                            "entity_changes": {
                                "uuid-string": {
                                    "entity_history": {
                                        "2025-09-27T11:42:32Z": [
                                            {"display_name": {"old_value": "20", "new_value": "19"}}
                                        ]
                                    },
                                    "entity_detail_history": {
                                        "2025-09-27T12:09:52Z": [
                                            {"detail_code": {"old_value": "3", "new_value": "4"}}
                                        ]
                                    }
                                }
                            }
                        }
                    )
                ],
            )
        }
    }
