from django.db import models


class Manufacturer(models.Model):
    """
    Manufacturer model for product manufacturers.

    Available Fields:
    - id (int): Primary key, auto-generated
    - name (str): Name of the manufacturer
    """

    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
