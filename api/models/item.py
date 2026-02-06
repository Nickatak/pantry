from django.db import models


class Item(models.Model):
    """
    Item model for pantry items.

    Available Fields:
    - id (int): Primary key, auto-generated
    - barcode (str): Barcode/UPC identifier for the item
    - title (str): Title/name of the item
    - alias (str): Alternative name or alias for the item
    - description (str): Detailed description of the item
    """

    barcode = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=255)
    alias = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["title"]
