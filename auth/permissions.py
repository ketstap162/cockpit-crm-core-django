from typing import Optional

from rest_framework.permissions import BasePermission


class AccessPermission(BasePermission):
    def __init__(
            self,
            allowed_roles: Optional[list[str]] = None,
            auth_required: bool = False,
            allow_superuser: bool = False,
    ):
        if allowed_roles is None:
            allowed_roles = []
        self.allowed_roles = allowed_roles
        self.auth_required = auth_required
        self.allow_superuser = allow_superuser

    def has_permission(self, request, view):
        user = request.user

        if self.auth_required:
            if not user or not user.is_authenticated:
                return False

        if self.allow_superuser and user.is_superuser:
            return True

        for role in self.allowed_roles:
            if user.groups.filter(name=role).exists():
                return True

        return False


class AccessPermissionFactory:
    allowed_roles = []
    auth_required = False
    allow_superuser = False

    @classmethod
    def get_access_permission(cls, *, allowed_roles=None, auth_required=False, allow_superuser=False):
        cls.allowed_roles = allowed_roles or []
        cls.auth_required = auth_required
        cls.allow_superuser = allow_superuser

        class _Permission(AccessPermission):
            def __init__(self):
                super().__init__(
                    allowed_roles=cls.allowed_roles,
                    auth_required=cls.auth_required,
                    allow_superuser=cls.allow_superuser,
                )

        return _Permission


def access_permission_factory(*, allowed_roles=None, auth_required=False, allow_superuser=False):
    class _Permission(AccessPermission):
        def __init__(self):
            super().__init__(
                allowed_roles=allowed_roles,
                auth_required=auth_required,
                allow_superuser=allow_superuser,
            )
    return _Permission
