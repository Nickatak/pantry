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
    - POST /api/items/ - Create item from UPC data
    - GET /api/items/lookup-product/{upc}/ - Lookup product data from external database
    - GET /api/items/{upc}/ - Lookup and create item from UPC (deprecated)

    Requires authentication for all endpoints.
    """

    permission_classes = [IsAuthenticated]

    def create(self, request):
        """
        Create a new item in the database.

        POST /api/items/
        - barcode: str (UPC code, required)
        - title: str (required)
        - description: str (optional)
        - alias: str (optional)

        Returns: Created item object with ID
        """
        barcode = request.data.get("barcode", "").strip()
        title = request.data.get("title", "").strip()
        description = request.data.get("description", "").strip()
        alias = request.data.get("alias", "").strip()

        # Validate required fields
        if not barcode:
            return Response(
                {"barcode": "Barcode is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not title:
            return Response(
                {"title": "Title is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Create or get the item
            item, created = Item.objects.get_or_create(
                barcode=barcode,
                defaults={
                    "title": title,
                    "description": description,
                    "alias": alias,
                },
            )

            # If item already existed, optionally update fields
            if not created:
                item.title = title
                item.description = description
                item.alias = alias
                item.save()

            serializer = ItemSerializer(item)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": f"Failed to create item: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["get"], url_path="lookup-product/(?P<upc>[^/.]+)")
    def lookup_product(self, request, upc=None):
        """
        Lookup product data from external UPC database.
        Does NOT create an item - just returns product information.

        GET /api/items/lookup-product/{upc}/

        Returns: { found: bool, product_data: {...} }
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
                # Product not found is not an error - return success with found=false
                return Response(
                    {"found": False, "product_data": None},
                    status=status.HTTP_200_OK,
                )

            return Response(
                {"found": True, "product_data": product},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            # External API error - return 500
            return Response(
                {"error": f"Failed to lookup product: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["get"], url_path="(?P<upc>[^/.]+)")
    def lookup_upc(self, request, upc=None):
        """
        Lookup an item by UPC and create it in the database.
        (Deprecated - use POST /api/items/ with lookup-product instead)

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
