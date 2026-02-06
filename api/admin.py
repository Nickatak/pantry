from django.contrib import admin

from .models import Brand, CustomUser, Item, Manufacturer

admin.site.register(CustomUser)
admin.site.register(Item)
admin.site.register(Brand)
admin.site.register(Manufacturer)
