import pytest
from django.contrib.auth.models import User, Group
from rest_framework.test import APIClient
from entities.models import Entity, EntityType, EntityDetail
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


@pytest.fixture
def create_user():
    def _create(username, groups=None, is_superuser=False):
        user = User.objects.create_user(username=username, password="password", is_superuser=is_superuser)
        if groups:
            for group_name in groups:
                group, _ = Group.objects.get_or_create(name=group_name)
                user.groups.add(group)
        user.save()
        return user
    return _create


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def entity_type():
    return EntityType.objects.create(code="INSTITUTION", name="Institution")


@pytest.fixture
def entity(entity_type):
    return Entity.objects.create(display_name="MyEntity", entity_type=entity_type)


@pytest.fixture
def entity_detail(entity):
    return EntityDetail.objects.create(entity_uuid=entity.uuid, value="InitialValue")


@pytest.fixture
def users():
    """Створює словник користувачів різного типу."""
    anon = None

    authenticated = User.objects.create_user(username="auth_user", password="password")

    cockpit_group, _ = Group.objects.get_or_create(name="cockpit_admin")
    cockpit_admin = User.objects.create_user(username="cockpit_admin_user", password="password")
    cockpit_admin.groups.add(cockpit_group)
    cockpit_admin.save()

    entity_group, _ = Group.objects.get_or_create(name="entity_admin")
    entity_admin = User.objects.create_user(username="entity_admin_user", password="password")
    entity_admin.groups.add(entity_group)
    entity_admin.save()

    superuser = User.objects.create_superuser(username="superuser", password="password")

    return {
        "anon": anon,
        "authenticated": authenticated,
        "cockpit_admin": cockpit_admin,
        "entity_admin": entity_admin,
        "superuser": superuser,
    }


def _authenticate_user(self, api_client, users, user_key, force_auth):
    """Форсує авторизацію для конкретного користувача, або None для anon"""
    api_client.force_authenticate(user=None)  # скидаємо попередню автентифікацію
    user = users[user_key]
    if force_auth and user:
        api_client.force_authenticate(user=user)


@pytest.mark.parametrize(
    "user_key, force_auth, expected_status_get, expected_status_post, expected_status_patch",
    [
        ("anon", False, status.HTTP_401_UNAUTHORIZED, status.HTTP_401_UNAUTHORIZED, status.HTTP_401_UNAUTHORIZED),
        ("authenticated", True, status.HTTP_403_FORBIDDEN, status.HTTP_403_FORBIDDEN, status.HTTP_403_FORBIDDEN),
        ("cockpit_admin", True, status.HTTP_200_OK, status.HTTP_201_CREATED, status.HTTP_200_OK),
        ("entity_admin", True, status.HTTP_200_OK, status.HTTP_201_CREATED, status.HTTP_200_OK),
        ("superuser", True, status.HTTP_200_OK, status.HTTP_201_CREATED, status.HTTP_200_OK),
    ]
)
class TestEntitiesAPI:
    def _authenticate_user(self, api_client, users, user_key, force_auth):
        user = users[user_key]
        if force_auth and user:
            api_client.force_authenticate(user=user)
        else:
            api_client.force_authenticate(user=None)

    def test_list_entities(self, api_client, users, entity, user_key, force_auth, expected_status_get, expected_status_post, expected_status_patch):
        self._authenticate_user(api_client, users, user_key, force_auth)
        url = reverse("entity")
        response = api_client.get(url)
        assert response.status_code == expected_status_get

    def test_filter_entities_by_search(self, api_client, users, entity, user_key, force_auth, expected_status_get, expected_status_post, expected_status_patch):
        self._authenticate_user(api_client, users, user_key, force_auth)
        url = reverse("entity")
        response = api_client.get(url, {"search": "My"})
        assert response.status_code == expected_status_get
        if expected_status_get == status.HTTP_200_OK:
            assert len(response.data) == 1

        response_empty = api_client.get(url, {"search": "XYZ"})
        assert response_empty.status_code == expected_status_get
        if expected_status_get == status.HTTP_200_OK:
            assert len(response_empty.data) == 0

    def test_create_entity(self, api_client, users, entity_type, user_key, force_auth, expected_status_get, expected_status_post, expected_status_patch):
        self._authenticate_user(api_client, users, user_key, force_auth)
        url = reverse("entity")
        payload = {
            "display_name": "NewEntity",
            "entity_type_code": entity_type.code,
            "detail": {"value": "Red"}
        }
        response = api_client.post(url, payload, format="json")
        assert response.status_code == expected_status_post

    def test_get_entity_snapshot(
            self, api_client, users, entity, entity_detail, user_key,
            force_auth, expected_status_get, expected_status_post, expected_status_patch):
        self._authenticate_user(api_client, users, user_key, force_auth)
        url = reverse("entity-snapshot", args=[entity.uuid])
        response = api_client.get(url)
        assert response.status_code == expected_status_get
        if expected_status_get == status.HTTP_200_OK:
            assert response.data["uuid"] == str(entity.uuid)
            assert response.data["detail"]["value"] == entity_detail.value

    def test_patch_entity_and_create_new_version(
            self, api_client, users, entity, entity_detail, user_key, force_auth,
            expected_status_get, expected_status_post, expected_status_patch
    ):
        self._authenticate_user(api_client, users, user_key, force_auth)
        url = reverse("entity-snapshot", args=[entity.uuid])
        payload = {"display_name": "UpdatedEntity", "detail": {"value": "UpdatedValue"}}
        response = api_client.patch(url, payload, format="json")
        assert response.status_code == expected_status_patch
