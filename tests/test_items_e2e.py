"""
API-level end-to-end tests for item endpoints.

Tests cover:
- UPC lookup and item creation
- Handling of existing items
- Error cases (missing UPC, API failures)
"""

from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model

from api.models import Item

User = get_user_model()


# ============================================================================
# Test Data
# ============================================================================

TEST_UPC = "0111222333446"

EXPECTED_UPC_RESPONSE = {
    "added_time": "2011-06-03 19:45:37",
    "modified_time": "2020-03-17 14:59:12",
    "title": "UPC Database Testing Code",
    "alias": "Testing Code",
    "description": "http://upcdatabase.org/code/0111222333446",
    "brand": "",
    "manufacturer": "",
    "msrp": "123.45",
    "ASIN": "",
    "category": "",
    "categories": "",
    "stores": [],
    "barcode": "0111222333446",
    "success": True,
    "timestamp": 1770332489,
    "images": [],
    "metadata": {"msrp": "123.45", "unit": "1 code"},
    "metanutrition": None,
}


# ============================================================================
# UPC Lookup Tests
# ============================================================================


@pytest.mark.items
class TestItemsUPCLookup:
    """Tests for the items UPC lookup endpoint."""

    @patch("api.views.items.upcdatabase.UPCDatabase")
    def test_lookup_upc_creates_new_item(
        self, mock_upc_db_class, db_reset, authenticated_client
    ):
        """Test successful UPC lookup creates a new item."""
        # Setup mock
        mock_db_instance = mock_upc_db_class.return_value
        mock_db_instance.lookup.return_value = EXPECTED_UPC_RESPONSE

        # Ensure item doesn't exist
        assert not Item.objects.filter(barcode=TEST_UPC).exists()

        # Make request
        response = authenticated_client.get(f"/api/items/{TEST_UPC}/")

        # Verify response status
        assert response.status_code == 201
        data = response.json()

        # Verify response structure
        assert "created" in data
        assert "item" in data
        assert "product_data" in data

        # Verify item was created
        assert data["created"] is True
        assert data["item"]["barcode"] == TEST_UPC
        assert data["item"]["title"] == "UPC Database Testing Code"

        # Verify product data matches expected response
        assert data["product_data"]["barcode"] == TEST_UPC
        assert data["product_data"]["title"] == "UPC Database Testing Code"

        # Verify item exists in database
        item = Item.objects.get(barcode=TEST_UPC)
        assert item.title == "UPC Database Testing Code"
        assert item.barcode == TEST_UPC

    @patch("api.views.items.upcdatabase.UPCDatabase")
    def test_lookup_upc_returns_existing_item(
        self, mock_upc_db_class, db_reset, authenticated_client
    ):
        """Test UPC lookup returns existing item without creating duplicate."""
        # Setup mock
        mock_db_instance = mock_upc_db_class.return_value
        mock_db_instance.lookup.return_value = EXPECTED_UPC_RESPONSE

        # Create item first
        existing_item = Item.objects.create(
            barcode=TEST_UPC,
            title="UPC Database Testing Code",
            description="http://upcdatabase.org/code/0111222333446",
            alias="",
        )

        # Make request
        response = authenticated_client.get(f"/api/items/{TEST_UPC}/")

        # Verify response status is 200 (not created)
        assert response.status_code == 200
        data = response.json()

        # Verify item was not created again
        assert data["created"] is False
        assert data["item"]["id"] == existing_item.id
        assert data["item"]["barcode"] == TEST_UPC

        # Verify only one item exists in database
        assert Item.objects.filter(barcode=TEST_UPC).count() == 1

    def test_lookup_upc_without_upc_param(self, db_reset, http_client):
        """Test UPC lookup fails when UPC is not provided."""
        response = http_client.get("/api/items/")

        # Should get 404 because of router pattern
        assert response.status_code == 404

    @patch("api.views.items.upcdatabase.UPCDatabase")
    def test_lookup_upc_not_found_in_database(
        self, mock_upc_db_class, db_reset, authenticated_client
    ):
        """Test UPC lookup fails when product not found in UPC database."""
        # Setup mock to return None
        mock_db_instance = mock_upc_db_class.return_value
        mock_db_instance.lookup.return_value = None

        # Make request
        response = authenticated_client.get(f"/api/items/{TEST_UPC}/")

        # Verify response status
        assert response.status_code == 404
        data = response.json()

        # Verify error message
        assert "error" in data
        assert f"No product found for UPC: {TEST_UPC}" in data["error"]

        # Verify item was not created
        assert not Item.objects.filter(barcode=TEST_UPC).exists()

    @patch("api.views.items.upcdatabase.UPCDatabase")
    def test_lookup_upc_api_error(
        self, mock_upc_db_class, db_reset, authenticated_client
    ):
        """Test UPC lookup handles API errors gracefully."""
        # Setup mock to raise exception
        mock_db_instance = mock_upc_db_class.return_value
        mock_db_instance.lookup.side_effect = Exception("API connection failed")

        # Make request
        response = authenticated_client.get(f"/api/items/{TEST_UPC}/")

        # Verify response status
        assert response.status_code == 500
        data = response.json()

        # Verify error message
        assert "error" in data
        assert "Failed to lookup UPC" in data["error"]
        assert "API connection failed" in data["error"]

    @patch("api.views.items.upcdatabase.UPCDatabase")
    def test_lookup_upc_missing_api_key(
        self, mock_upc_db_class, db_reset, authenticated_client
    ):
        """Test UPC lookup fails when API key is not configured."""
        with patch("api.views.items.config") as mock_config:
            # Mock config to return empty API key
            mock_config.return_value = ""

            # Make request
            response = authenticated_client.get(f"/api/items/{TEST_UPC}/")

            # Verify response status
            assert response.status_code == 500
            data = response.json()

            # Verify error message
            assert "error" in data
            assert "UPCDATABASE_API_KEY environment variable not set" in data["error"]

    @patch("api.views.items.upcdatabase.UPCDatabase")
    def test_lookup_upc_response_structure(
        self, mock_upc_db_class, db_reset, authenticated_client
    ):
        """Test UPC lookup response contains all required fields."""
        # Setup mock
        mock_db_instance = mock_upc_db_class.return_value
        mock_db_instance.lookup.return_value = EXPECTED_UPC_RESPONSE

        # Make request
        response = authenticated_client.get(f"/api/items/{TEST_UPC}/")

        # Verify response structure
        assert response.status_code == 201
        data = response.json()

        # Verify top-level fields
        assert "created" in data
        assert "item" in data
        assert "product_data" in data

        # Verify item serialization includes expected fields
        item = data["item"]
        assert "id" in item
        assert "barcode" in item
        assert "title" in item
        assert "description" in item
        assert "alias" in item

        # Verify product_data matches expected response
        product_data = data["product_data"]
        assert product_data["barcode"] == TEST_UPC
        assert product_data["title"] == EXPECTED_UPC_RESPONSE["title"]
        assert product_data["success"] is True
