from core.settings import *
from auth.config import settings as jwt

INSTALLED_APPS += [
    "entities",

    "drf_spectacular",
    "drf_spectacular_sidecar",
]

ROOT_URLCONF = "entities.urls"

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# Extend settings
INSTALLED_APPS, REST_FRAMEWORK, SIMPLE_JWT = jwt.configure(INSTALLED_APPS, REST_FRAMEWORK)
# for app in jwt.INSTALLED_APPS:
#     if app not in INSTALLED_APPS:
#         INSTALLED_APPS.append(app)
#
# REST_FRAMEWORK.update(jwt.REST_FRAMEWORK)
# SIMPLE_JWT = jwt.SIMPLE_JWT
