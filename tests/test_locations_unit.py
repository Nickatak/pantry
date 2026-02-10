import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.db import transaction

from api.models import Location
from api.serializers import LocationSerializer


User = get_user_model()


@pytest.mark.items
class TestLocationModel:
    def test_location_unique_per_user(self, db_reset):
        user = User.objects.create_user(
            email="unique-location@example.com", password="testpassword123"
        )

        pantry = Location.objects.get(user=user, name="Pantry")

        with pytest.raises(IntegrityError):
            with transaction.atomic():
                Location.objects.create(user=user, name=pantry.name)

    def test_location_name_can_repeat_across_users(self, db_reset):
        user_a = User.objects.create_user(
            email="usera@example.com", password="testpassword123"
        )
        user_b = User.objects.create_user(
            email="userb@example.com", password="testpassword123"
        )

        pantry_a = Location.objects.get(user=user_a, name="Pantry")
        pantry_b = Location.objects.get(user=user_b, name="Pantry")

        assert pantry_a.id != pantry_b.id

    def test_location_serializer_fields(self, db_reset):
        user = User.objects.create_user(
            email="serializer@example.com", password="testpassword123"
        )
        location = Location.objects.get(user=user, name="Pantry")

        serialized = LocationSerializer(location).data
        assert set(serialized.keys()) == {"id", "name"}
