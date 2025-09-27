from core.settings import *

INSTALLED_APPS += [
    "entities",

    "drf_spectacular",
    "drf_spectacular_sidecar"
]

ROOT_URLCONF = "entities.urls"

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}
