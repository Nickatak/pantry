from django.conf import settings
from django.db import models


class Location(models.Model):
    """
    Location model for user-specific item storage locations.

    Available Fields:
    - id (int): Primary key, auto-generated
    - user (FK): Owner of the location
    - name (str): Location name (unique per user)
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="locations",
    )
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ["name"]
        unique_together = ("user", "name")

    def __str__(self):
        return f"{self.user.email}: {self.name}"
