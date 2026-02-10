from django.conf import settings
from django.db import models

from .location import Location


class Item(models.Model):
    """
    Item model for pantry items.

    Available Fields:
    - id (int): Primary key, auto-generated
    - barcode (str): Barcode/UPC identifier for the item
    - title (str): Title/name of the item
    - alias (str): Alternative name or alias for the item
    - description (str): Detailed description of the item
    - category (str): Category classification for the item
    """

    CATEGORY_CHOICES = [
        ("produce", "Produce"),
        ("dairy", "Dairy"),
        ("meat", "Meat & Poultry"),
        ("bakery", "Bakery"),
        ("canned", "Canned Goods"),
        ("frozen", "Frozen"),
        ("pantry", "Pantry Staples"),
        ("beverages", "Beverages"),
        ("snacks", "Snacks"),
        ("condiments", "Condiments & Sauces"),
        ("other", "Other"),
    ]

    barcode = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=255)
    alias = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default="other",
    )
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="UserItemQuantity",
        related_name="items",
    )

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["title"]


class UserItemQuantity(models.Model):
    """
    Adjoining model between user and item, tracks quantity per user.

    Available Fields:
    - id (int): Primary key, auto-generated
    - user (FK): User that owns the item
    - item (FK): Pantry item
    - quantity (int): Quantity owned by the user
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_items",
    )
    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        related_name="user_items",
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        related_name="user_items",
    )
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["item__title"]
        unique_together = ("user", "item", "location")

    def __str__(self):
        return f"{self.user.email}: {self.item.title} ({self.quantity})"
