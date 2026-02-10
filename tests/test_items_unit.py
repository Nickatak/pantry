import pytest
from django.contrib.auth import get_user_model

from api.models import Location
from api.views.items import ItemViewSet


User = get_user_model()


@pytest.mark.items
class TestItemViewSetDefaults:
    def test_default_location_helper_creates_pantry(self, db_reset):
        user = User.objects.create_user(
            email="default-location@example.com", password="testpassword123"
        )
        Location.objects.filter(user=user).delete()

        viewset = ItemViewSet()
        location = viewset._get_default_location(user)

        assert location.name == "Pantry"
        assert Location.objects.filter(user=user, name="Pantry").exists()
