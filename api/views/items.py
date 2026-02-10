try:
    import upcdatabase
except ModuleNotFoundError:
    class _MissingUPCDB:
        def __init__(self, *args, **kwargs):
            raise ModuleNotFoundError(
                "upcdatabase is not installed. Install it to use UPC lookup."
            )

    class _UPCDBModule:
        UPCDatabase = _MissingUPCDB

    upcdatabase = _UPCDBModule()
from decouple import config
from django.db import models
from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import Brand, Item, Location, UserItemQuantity
from ..serializers import ItemSerializer


class ItemPagination(PageNumberPagination):
    """Pagination for item list endpoint."""

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class ItemViewSet(viewsets.ViewSet):
    """
    ViewSet for item operations.

    Provides the following endpoints:
    - GET /api/items/ - List all items with pagination and search
    - POST /api/items/ - Create item from UPC data
    - GET /api/items/lookup-product/{upc}/ - Lookup product data from external database
    - GET /api/items/{upc}/ - Lookup and create item from UPC (deprecated)
    - DELETE /api/items/{id}/ - Delete an item
    - PUT /api/items/{id}/ - Update an item

    Requires authentication for all endpoints.
    """

    permission_classes = [IsAuthenticated]

    def _get_default_location(self, user):
        return Location.objects.get_or_create(user=user, name="Pantry")[0]

    def list(self, request):
        """
        Get paginated list of items with optional search.

        GET /api/items/
        Query parameters:
        - search: str (searches in title, description, alias)
        - page: int (page number, default 1)
        - page_size: int (items per page, default 20, max 100)

        Returns: paginated list of items
        """
        queryset = (
            Item.objects.filter(user_items__user=request.user)
            .annotate(quantity=models.Sum("user_items__quantity"))
            .distinct()
            .order_by("title")
        )

        # Handle search
        search_query = request.query_params.get("search", "").strip()
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query)
                | Q(description__icontains=search_query)
                | Q(alias__icontains=search_query)
                | Q(barcode__icontains=search_query)
            )

        # Apply pagination
        paginator = ItemPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = ItemSerializer(paginated_queryset, many=True)

        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        Get a single item by ID.

        GET /api/items/{id}/

        Returns: item object
        """
        try:
            item = (
                Item.objects.filter(user_items__user=request.user, pk=pk)
                .annotate(quantity=models.Sum("user_items__quantity"))
                .get()
            )
        except Item.DoesNotExist:
            return Response(
                {"error": "Item not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = ItemSerializer(item)
        return Response(serializer.data)

    def update(self, request, pk=None):
        """
        Update an item by ID.

        PUT /api/items/{id}/
        - title: str (optional)
        - description: str (optional)
        - alias: str (optional)
        - category: str (optional)
        - quantity: int (optional, per-user)
        - location_id: int (optional, for quantity updates)

        Returns: updated item object
        """
        try:
            item = Item.objects.get(pk=pk)
            if not UserItemQuantity.objects.filter(user=request.user, item=item).exists():
                raise Item.DoesNotExist
        except Item.DoesNotExist:
            return Response(
                {"error": "Item not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Update fields if provided
        if "title" in request.data:
            item.title = request.data.get("title", "").strip()
        if "description" in request.data:
            item.description = request.data.get("description", "").strip()
        if "alias" in request.data:
            item.alias = request.data.get("alias", "").strip()
        if "category" in request.data:
            item.category = request.data.get("category", "").strip() or "other"
        if "quantity" in request.data:
            try:
                quantity_value = int(request.data.get("quantity", 1))
            except (TypeError, ValueError):
                return Response(
                    {"error": "Quantity must be a valid integer"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if quantity_value < 1:
                return Response(
                    {"error": "Quantity must be at least 1"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            location_id = request.data.get("location_id")
            if location_id:
                try:
                    location = Location.objects.get(pk=location_id, user=request.user)
                except Location.DoesNotExist:
                    return Response(
                        {"error": "Location not found"},
                        status=status.HTTP_404_NOT_FOUND,
                    )
            else:
                location = self._get_default_location(request.user)

            user_item, _ = UserItemQuantity.objects.get_or_create(
                user=request.user,
                item=item,
                location=location,
                defaults={"quantity": quantity_value},
            )
            user_item.quantity = quantity_value
            user_item.save()

        try:
            item.save()
            item.quantity = UserItemQuantity.objects.filter(
                user=request.user, item=item
            ).aggregate(total=models.Sum("quantity"))["total"] or 0
            serializer = ItemSerializer(item)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"error": f"Failed to update item: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def destroy(self, request, pk=None):
        """
        Delete an item by ID.

        DELETE /api/items/{id}/

        Returns: success message
        """
        try:
            item = Item.objects.get(pk=pk)
        except Item.DoesNotExist:
            return Response(
                {"error": "Item not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        UserItemQuantity.objects.filter(user=request.user, item=item).delete()

        if not UserItemQuantity.objects.filter(item=item).exists():
            item.delete()

        return Response(
            {"message": "Item deleted successfully"},
            status=status.HTTP_204_NO_CONTENT,
        )

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
        Lookup product data by checking database first, then external UPC database.
        Does NOT create an item - just returns product information.

        GET /api/items/lookup-product/{upc}/

        Returns: { found: bool, from_database: bool, product_data: {...} }
        """
        if not upc:
            return Response(
                {"error": "UPC code is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        # First, check if item exists in database
        try:
            item = Item.objects.get(barcode=upc)
            # Item found in database - return existing data
            return Response(
                {
                    "found": True,
                    "from_database": True,
                    "product_data": {
                        "title": item.title,
                        "description": item.description,
                        "alias": item.alias,
                    },
                },
                status=status.HTTP_200_OK,
            )
        except Item.DoesNotExist:
            # Item not in database, proceed to external API lookup
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
                        {
                            "found": False,
                            "from_database": False,
                            "product_data": None,
                        },
                        status=status.HTTP_200_OK,
                    )

                return Response(
                    {
                        "found": True,
                        "from_database": False,
                        "product_data": product,
                    },
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

    @action(detail=True, methods=["post"], url_path="add-to-user")
    def add_to_user(self, request, pk=None):
        """
        Add an item to the current user.

        I have purposely decided to use the PK instead of UPC here, as a temporary
        workaround to avoid dealing with duplicate UPC's for now.  Although, at some
        point this will have to be addressed during the item creation process.

        POST /api/items/{id}/add-to-user/
        - Increments quantity by 1 if record exists
        - Creates a new record with quantity=1 otherwise
        """
        try:
            item = Item.objects.get(pk=pk)
        except Item.DoesNotExist:
            return Response(
                {"error": "Item not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        location_id = request.data.get("location_id")
        if location_id:
            try:
                location = Location.objects.get(pk=location_id, user=request.user)
            except Location.DoesNotExist:
                return Response(
                    {"error": "Location not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            location = self._get_default_location(request.user)

        user_item, created = UserItemQuantity.objects.get_or_create(
            user=request.user,
            item=item,
            location=location,
            defaults={"quantity": 1},
        )
        if not created:
            user_item.quantity += 1
            user_item.save()

        item.quantity = UserItemQuantity.objects.filter(
            user=request.user, item=item
        ).aggregate(total=models.Sum("quantity"))["total"] or 0
        serializer = ItemSerializer(item)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["patch"], url_path="quantity")
    def update_quantity(self, request, pk=None):
        """
        Update quantity for a user-owned item.

        PATCH /api/items/{id}/quantity/
        - quantity: int (required, >= 1)
        - location_id: int (optional, defaults to Pantry)
        """
        location_id = request.data.get("location_id")
        if location_id:
            try:
                location = Location.objects.get(pk=location_id, user=request.user)
            except Location.DoesNotExist:
                return Response(
                    {"error": "Location not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            location = self._get_default_location(request.user)

        try:
            user_item = UserItemQuantity.objects.select_related("item").get(
                user=request.user, item_id=pk, location=location
            )
        except UserItemQuantity.DoesNotExist:
            return Response(
                {"error": "Item not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            quantity_value = int(request.data.get("quantity", 0))
        except (TypeError, ValueError):
            return Response(
                {"error": "Quantity must be a valid integer"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if quantity_value < 1:
            return Response(
                {"error": "Quantity must be at least 1"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_item.quantity = quantity_value
        user_item.save()

        item = user_item.item
        item.quantity = UserItemQuantity.objects.filter(
            user=request.user, item=item
        ).aggregate(total=models.Sum("quantity"))["total"] or 0
        serializer = ItemSerializer(item)
        return Response(serializer.data, status=status.HTTP_200_OK)
