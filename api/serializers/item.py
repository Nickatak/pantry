from rest_framework import serializers

from ..models import Item


class ItemSerializer(serializers.ModelSerializer):
    """Serializer for Item model."""

    quantity = serializers.IntegerField(read_only=True)

    class Meta:
        model = Item
        fields = [
            "id",
            "barcode",
            "title",
            "alias",
            "description",
            "category",
            "quantity",
        ]
        read_only_fields = ["id"]
