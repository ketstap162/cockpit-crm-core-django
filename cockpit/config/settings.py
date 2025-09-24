from core.settings import *

INSTALLED_APPS += [
    # CRM module
    "cockpit",

    # Other modules
    "entities",
]

ROOT_URLCONF = "cockpit.urls"
