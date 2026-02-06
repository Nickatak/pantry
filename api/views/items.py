import upcdatabase
from decouple import config
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import Brand, Item
from ..serializers import ItemSerializer


class ItemViewSet(viewsets.ViewSet):
    """
    ViewSet for item operations.

    Provides the following endpoints:
    - GET /api/items/{upc}/ - Lookup and create item from UPC

    Requires authentication for all endpoints.
    """

    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["get"], url_path="(?P<upc>[^/.]+)")
    def lookup_upc(self, request, upc=None):
        """
        Lookup an item by UPC and create it in the database.

        GET /api/items/{upc}/

        Returns: created or existing item
        """
        if not upc:
            return Response(
                {"error": "UPC code is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Get API key from environment
            api_key = config("UPCDATABASE_API_KEY", default="")
            if not api_key:
                return Response(
                    {"error": "UPCDATABASE_API_KEY environment variable not set"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            # Create UPCDatabase instance and lookup the UPC
            db = upcdatabase.UPCDatabase(api_key)
            product = db.lookup(upc)

            if not product:
                return Response(
                    {"error": f"No product found for UPC: {upc}"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            print(f"UPC Lookup Result: {product}")

            # Extract product information
            title = product.get("title", "Unknown")
            brand_name = product.get("brand", "")
            description = product.get("description", "")

            # Create or get brand
            brand = None
            if brand_name:
                brand, _ = Brand.objects.get_or_create(name=brand_name)

            # Create or get item
            item, created = Item.objects.get_or_create(
                barcode=upc,
                defaults={"title": title, "description": description, "alias": ""},
            )

            if created:
                print(f"Created new item: {item}")
            else:
                print(f"Item already exists: {item}")

            serializer = ItemSerializer(item)
            return Response(
                {"created": created, "item": serializer.data, "product_data": product},
                status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
            )

        except Exception as e:
            print(f"Error looking up UPC {upc}: {str(e)}")
            return Response(
                {"error": f"Failed to lookup UPC: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
