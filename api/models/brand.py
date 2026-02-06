from django.db import models


class Brand(models.Model):
    """
    Brand model for product brands.

    Available Fields:
    - id (int): Primary key, auto-generated
    - name (str): Name of the brand
    """

    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
