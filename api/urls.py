from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from .views import AuthViewSet

router = DefaultRouter()
router.register(r"auth", AuthViewSet, basename="auth")

urlpatterns = [
    # Explicit route for search-users with hyphens
    re_path(
        r"^auth/search-users/$",
        AuthViewSet.as_view({"get": "search_users"}),
        name="auth-search-users",
    ),
    path("", include(router.urls)),
]
