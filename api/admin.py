from django.contrib import admin

from .models import Brand, CustomUser, Item, Location, Manufacturer, UserItemQuantity

admin.site.register(CustomUser)
admin.site.register(Item)
admin.site.register(UserItemQuantity)
admin.site.register(Location)
admin.site.register(Brand)
admin.site.register(Manufacturer)
