from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from ..serializers import (
    CustomTokenObtainPairSerializer,
    UserRegistrationSerializer,
    UserSerializer,
)

User = get_user_model()


class AuthViewSet(viewsets.ViewSet):
    """
    ViewSet for authentication operations.

    Provides the following endpoints:
    - POST /api/auth/register/ - User registration
    - GET /api/auth/profile/ - Get current user profile
    - PUT /api/auth/profile/ - Update current user profile
    """

    def get_permissions(self):
        """
        Assign permissions based on the action.
        - register: AllowAny
        - login: AllowAny
        - profile: IsAuthenticated
        """
        if self.action in ["register", "login"]:
            return [AllowAny()]
        return [IsAuthenticated()]

    @action(detail=False, methods=["post"])
    def login(self, request):
        """
        User login endpoint.

        POST /api/auth/login/
        - email: str
        - password: str

        Returns: access and refresh tokens
        """
        email = request.data.get("email", "").strip()
        password = request.data.get("password", "")

        if not email:
            return Response(
                {"email": "Email is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        if not password:
            return Response(
                {"password": "Password is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if user exists
        user = User.objects.filter(email=email).first()
        if not user:
            return Response(
                {"detail": "Email or password is incorrect."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Try to get token using the serializer
        serializer = CustomTokenObtainPairSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)

        # If serializer fails, provide generic error message for security
        return Response(
            {"detail": "Email or password is incorrect."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    @action(detail=False, methods=["post"])
    def register(self, request):
        """
        User registration endpoint.

        POST /api/auth/register/
        - email: str (unique)
        - password: str
        - password_confirm: str
        """
        if User.objects.filter(email=request.data.get("email")).exists():
            return Response(
                {"email": "Email already exists."}, status=status.HTTP_400_BAD_REQUEST
            )

        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user_data = UserSerializer(user).data
            return Response(user_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get", "put"])
    def profile(self, request):
        """
        User profile endpoint.

        GET /api/auth/profile/ - Get current user profile
        PUT /api/auth/profile/ - Update current user profile

        Requires: Authorization header with valid JWT token
        """
        if request.method == "GET":
            serializer = UserSerializer(request.user)
            return Response(serializer.data)

        elif request.method == "PUT":
            user = request.user

            if "email" in request.data:
                if (
                    User.objects.filter(email=request.data["email"])
                    .exclude(id=user.id)
                    .exists()
                ):
                    return Response(
                        {"email": "Email already exists."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                user.email = request.data["email"]

            user.save()
            serializer = UserSerializer(user)
            return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def search_users(self, request):
        """
        Search for users by email.

        GET /api/auth/search-users/?q=email
        - q: str (search query, minimum 2 characters)

        Returns: List of matching users
        """
        query = request.query_params.get("q", "").strip()

        if len(query) < 2:
            return Response([], status=status.HTTP_200_OK)

        users = User.objects.filter(Q(email__icontains=query)).values("id", "email")[
            :10
        ]  # Limit to 10 results

        return Response(list(users), status=status.HTTP_200_OK)
