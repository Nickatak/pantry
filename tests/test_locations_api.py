import pytest
from django.contrib.auth import get_user_model

from api.models import Item, Location, UserItemQuantity


User = get_user_model()


@pytest.mark.items
class TestLocations:
    def test_default_locations_created_on_user_creation(self, db_reset):
        user = User.objects.create_user(
            email="locations@example.com", password="testpassword123"
        )

        names = list(user.locations.order_by("name").values_list("name", flat=True))
        assert names == ["Freezer", "Fridge", "Kitchen Counter", "Pantry"]

    def test_add_to_user_defaults_to_pantry_and_increments(
        self, db_reset, authenticated_client, test_user
    ):
        item = Item.objects.create(
            barcode="4445556667771",
            title="Peanut Butter",
            description="Crunchy",
            alias="PB",
        )

        response = authenticated_client.post(
            f"/api/items/{item.id}/add-to-user/", json={}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["quantity"] == 1

        response = authenticated_client.post(
            f"/api/items/{item.id}/add-to-user/", json={}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["quantity"] == 2

        pantry = Location.objects.get(user=test_user, name="Pantry")
        user_item = UserItemQuantity.objects.get(
            user=test_user, item=item, location=pantry
        )
        assert user_item.quantity == 2

    def test_list_sums_quantities_across_locations(
        self, db_reset, authenticated_client, test_user
    ):
        item = Item.objects.create(
            barcode="8889990001112",
            title="Frozen Pizza",
            description="Pepperoni",
            alias="Pizza",
        )
        freezer = Location.objects.get(user=test_user, name="Freezer")
        pantry = Location.objects.get(user=test_user, name="Pantry")

        UserItemQuantity.objects.create(
            user=test_user, item=item, location=freezer, quantity=2
        )
        UserItemQuantity.objects.create(
            user=test_user, item=item, location=pantry, quantity=3
        )

        response = authenticated_client.get("/api/items/")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert data["results"][0]["id"] == item.id
        assert data["results"][0]["quantity"] == 5

    def test_update_quantity_with_location(
        self, db_reset, authenticated_client, test_user
    ):
        item = Item.objects.create(
            barcode="2223334445556",
            title="Ice Cream",
            description="Vanilla",
            alias="Dessert",
        )
        freezer = Location.objects.get(user=test_user, name="Freezer")

        UserItemQuantity.objects.create(
            user=test_user, item=item, location=freezer, quantity=1
        )

        response = authenticated_client.patch(
            f"/api/items/{item.id}/quantity/",
            json={"quantity": 4, "location_id": freezer.id},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["quantity"] == 4

        updated = UserItemQuantity.objects.get(
            user=test_user, item=item, location=freezer
        )
        assert updated.quantity == 4

    def test_locations_list_and_create(self, db_reset, authenticated_client, test_user):
        response = authenticated_client.get("/api/locations/")
        assert response.status_code == 200
        data = response.json()
        assert any(location["name"] == "Pantry" for location in data)

        response = authenticated_client.post(
            "/api/locations/", json={"name": "Basement"}
        )
        assert response.status_code == 201
        created = response.json()
        assert created["name"] == "Basement"

        response = authenticated_client.get("/api/locations/")
        data = response.json()
        assert any(location["name"] == "Basement" for location in data)
