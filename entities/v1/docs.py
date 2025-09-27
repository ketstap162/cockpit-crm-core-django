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
                    "entity_type_code": "TYPE1",
                    "detail": {
                        "detail_code": "color",
                        "value": "red"
                    }
                }
            )
        ]
    }


class EntitySnapshotViewDoc:
    patch = {
        "request": sz.EntityUpdateSerializer,
        "responses": {
            200: sz.EntitySerializer,
            404: None
        },
        "description": "Update an Entity and its details by UUID"
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
        )
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
        "description": "",
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
