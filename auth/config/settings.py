from datetime import timedelta


INSTALLED_APPS = [
    "rest_framework",
    "rest_framework_simplejwt",
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    # "DEFAULT_PERMISSION_CLASSES": (
    #     "rest_framework.permissions.IsAuthenticated",
    # ),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}


def configure_item(item, config):

    if item:
        item = item.copy()

        if isinstance(item, dict):
            for key, value in config.items():
                if key not in item:
                    item[key] = value

        elif isinstance(item, list):
            for lst_value in config:
                if lst_value not in item:
                    item.append(lst_value)
    else:
        item = config.copy()

    return item


def configure(
        installed_apps: list[str] = None,
        rest_framework: dict = None,
        simple_jwt: dict = None
):
    """
    Usage:
        INSTALLED_APPS, REST_FRAMEWORK, SIMPLE_JWT = configure(INSTALLED_APPS, REST_FRAMEWORK, SIMPLE_JWT)
    """
    apps = configure_item(installed_apps, INSTALLED_APPS)
    rest = configure_item(rest_framework, REST_FRAMEWORK)
    jwt = configure_item(simple_jwt, SIMPLE_JWT)

    return apps, rest, jwt
