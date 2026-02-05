from django.contrib import admin

from .models.user import CustomUser

admin.site.register(CustomUser)
