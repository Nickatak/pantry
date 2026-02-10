from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import Location
from ..serializers import LocationSerializer


class LocationViewSet(viewsets.ViewSet):
    """
    ViewSet for user locations.

    - GET /api/locations/ - List locations for current user
    - POST /api/locations/ - Create a new location for current user
    """

    permission_classes = [IsAuthenticated]

    def list(self, request):
        locations = Location.objects.filter(user=request.user).order_by("name")
        serializer = LocationSerializer(locations, many=True)
        return Response(serializer.data)

    def create(self, request):
        name = request.data.get("name", "").strip()
        if not name:
            return Response(
                {"name": "Location name is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        location, created = Location.objects.get_or_create(
            user=request.user, name=name
        )
        serializer = LocationSerializer(location)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )
