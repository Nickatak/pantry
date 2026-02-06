from rest_framework import serializers

from ..models import Item


class ItemSerializer(serializers.ModelSerializer):
    """Serializer for Item model."""

    class Meta:
        model = Item
        fields = ["id", "barcode", "title", "alias", "description"]
        read_only_fields = ["id"]
