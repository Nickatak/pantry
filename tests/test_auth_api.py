"""
API-level end-to-end tests for authentication endpoints.

Tests cover:
- User registration
- User login
- Profile retrieval
- Profile updates
- Invalid credentials
- Protected endpoints
"""

import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


# ============================================================================
# Registration Tests
# ============================================================================


@pytest.mark.auth
@pytest.mark.registration
class TestRegistration:
    """Tests for the user registration endpoint."""

    def test_successful_registration(self, db_reset, http_client, test_user_data):
        """Test successful user registration."""
        response = http_client.post("/api/auth/register/", json=test_user_data)

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert "id" in data
        assert "password" not in data

        # Verify user was created in database
        user = User.objects.get(email=test_user_data["email"])
        assert user is not None
        assert user.email == test_user_data["email"]

    def test_registration_duplicate_email(
        self, db_reset, http_client, test_user, test_user_data
    ):
        """Test registration fails with duplicate email."""
        # Try to register with existing email
        duplicate_data = test_user_data.copy()
        duplicate_data["email"] = test_user.email

        response = http_client.post("/api/auth/register/", json=duplicate_data)

        assert response.status_code == 400
        assert "email" in response.json()

    def test_registration_password_mismatch(
        self, db_reset, http_client, test_user_data
    ):
        """Test registration fails when passwords don't match."""
        invalid_data = test_user_data.copy()
        invalid_data["password_confirm"] = "DifferentPassword123"

        response = http_client.post("/api/auth/register/", json=invalid_data)

        assert response.status_code == 400
        # The error is returned under password_confirm key
        assert "password_confirm" in response.json() or "password" in response.json()

    def test_registration_password_too_short(self, db_reset, http_client):
        """Test registration fails with password too short."""
        data = {
            "email": "test@example.com",
            "password": "short",
            "password_confirm": "short",
        }

        response = http_client.post("/api/auth/register/", json=data)

        assert response.status_code == 400
        assert "password" in response.json()

    def test_registration_invalid_email(self, db_reset, http_client):
        """Test registration fails with invalid email."""
        data = {
            "email": "invalid-email",
            "password": "ValidPass123",
            "password_confirm": "ValidPass123",
        }

        response = http_client.post("/api/auth/register/", json=data)

        assert response.status_code == 400
        assert "email" in response.json()

    def test_registration_missing_fields(self, db_reset, http_client):
        """Test registration fails with missing required fields."""
        # Missing email
        response = http_client.post(
            "/api/auth/register/",
            json={"password": "ValidPass123", "password_confirm": "ValidPass123"},
        )
        assert response.status_code == 400

        # Missing password
        response = http_client.post(
            "/api/auth/register/",
            json={"email": "test@example.com", "password_confirm": "ValidPass123"},
        )
        assert response.status_code == 400

        # Missing password_confirm
        response = http_client.post(
            "/api/auth/register/",
            json={"email": "test@example.com", "password": "ValidPass123"},
        )
        assert response.status_code == 400


# ============================================================================
# Login Tests
# ============================================================================


@pytest.mark.auth
@pytest.mark.login
class TestLogin:
    """Tests for the user login endpoint."""

    def test_successful_login(self, db_reset, http_client, test_user):
        """Test successful user login."""
        response = http_client.post(
            "/api/auth/login/",
            json={"email": "test@example.com", "password": "testpassword123"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "access" in data
        assert "refresh" in data

    def test_login_invalid_email(self, db_reset, http_client, test_user):
        """Test login fails with non-existent email."""
        response = http_client.post(
            "/api/auth/login/",
            json={"email": "nonexistent@example.com", "password": "testpassword123"},
        )

        assert response.status_code == 401
        # Should not reveal if email exists or not
        assert "Email or password is incorrect" in response.json()["detail"]

    def test_login_invalid_password(self, db_reset, http_client, test_user):
        """Test login fails with incorrect password."""
        response = http_client.post(
            "/api/auth/login/",
            json={"email": "test@example.com", "password": "wrongpassword"},
        )

        assert response.status_code == 401
        # Check for either error message from JWT or custom auth error
        data = response.json()
        assert "detail" in data or "non_field_errors" in data

    def test_login_empty_email(self, db_reset, http_client):
        """Test login fails with empty email."""
        response = http_client.post(
            "/api/auth/login/", json={"email": "", "password": "testpassword123"}
        )

        assert response.status_code == 400
        assert "email" in response.json()

    def test_login_empty_password(self, db_reset, http_client, test_user):
        """Test login fails with empty password."""
        response = http_client.post(
            "/api/auth/login/", json={"email": "test@example.com", "password": ""}
        )

        assert response.status_code == 400
        assert "password" in response.json()

    def test_login_missing_fields(self, db_reset, http_client):
        """Test login fails with missing required fields."""
        # Missing email
        response = http_client.post(
            "/api/auth/login/", json={"password": "testpassword123"}
        )
        assert response.status_code == 400

        # Missing password
        response = http_client.post(
            "/api/auth/login/", json={"email": "test@example.com"}
        )
        assert response.status_code == 400


# ============================================================================
# Profile Tests
# ============================================================================


@pytest.mark.auth
@pytest.mark.profile
class TestProfile:
    """Tests for the user profile endpoint."""

    def test_get_profile_authenticated(self, db_reset, authenticated_client, test_user):
        """Test getting user profile when authenticated."""
        response = authenticated_client.get("/api/auth/profile/")

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
        assert data["id"] == test_user.id

    def test_get_profile_unauthenticated(self, db_reset, http_client):
        """Test getting profile fails without authentication."""
        response = http_client.get("/api/auth/profile/")

        assert response.status_code == 401

    def test_update_profile_email(self, db_reset, authenticated_client, test_user):
        """Test updating user email."""
        new_email = "newemail@example.com"
        response = authenticated_client.put(
            "/api/auth/profile/", json={"email": new_email}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == new_email

        # Verify email was updated in database
        test_user.refresh_from_db()
        assert test_user.email == new_email

    def test_update_profile_duplicate_email(self, db_reset, http_client, db):
        """Test updating profile fails with duplicate email."""
        # Create two users
        user1 = User.objects.create_user(
            email="user1@example.com", password="pass123456"
        )
        user2 = User.objects.create_user(
            email="user2@example.com", password="pass123456"
        )

        # Authenticate as user1
        from rest_framework_simplejwt.tokens import RefreshToken

        refresh = RefreshToken.for_user(user1)
        http_client.headers["Authorization"] = f"Bearer {str(refresh.access_token)}"

        # Try to update user1's email to user2's email
        response = http_client.put("/api/auth/profile/", json={"email": user2.email})

        assert response.status_code == 400
        assert "email" in response.json()

    def test_update_profile_same_email(self, db_reset, authenticated_client, test_user):
        """Test updating profile with same email succeeds."""
        response = authenticated_client.put(
            "/api/auth/profile/", json={"email": test_user.email}
        )

        assert response.status_code == 200
        assert response.json()["email"] == test_user.email

    def test_update_profile_unauthenticated(self, db_reset, http_client):
        """Test updating profile fails without authentication."""
        response = http_client.put(
            "/api/auth/profile/", json={"email": "newemail@example.com"}
        )

        assert response.status_code == 401


# ============================================================================
# Token Tests
# ============================================================================


@pytest.mark.auth
class TestTokens:
    """Tests for JWT token handling."""

    def test_token_payload(self, db_reset, http_client, test_user):
        """Test that token contains expected claims."""
        import jwt

        response = http_client.post(
            "/api/auth/login/",
            json={"email": "test@example.com", "password": "testpassword123"},
        )

        assert response.status_code == 200
        tokens = response.json()
        access_token = tokens["access"]

        # Decode token (without verification for testing)
        decoded = jwt.decode(access_token, options={"verify_signature": False})
        # user_id might be string in token, so compare appropriately
        assert int(decoded["user_id"]) == test_user.id

    def test_invalid_token(self, db_reset, http_client):
        """Test that invalid token is rejected."""
        http_client.headers["Authorization"] = "Bearer invalid.token.here"

        response = http_client.get("/api/auth/profile/")
        assert response.status_code == 401

    def test_expired_token_behavior(self, db_reset, http_client, test_user):
        """Test behavior with malformed authorization header."""
        http_client.headers["Authorization"] = "InvalidFormat token"

        response = http_client.get("/api/auth/profile/")
        assert response.status_code == 401


# ============================================================================
# User Search Tests
# ============================================================================


@pytest.mark.auth
class TestUserSearch:
    """Tests for the user search endpoint."""

    def test_search_users_authenticated(
        self, db_reset, authenticated_client, test_user, db
    ):
        """Test searching users when authenticated."""
        # Create another user
        User.objects.create_user(email="search@example.com", password="pass123456")

        response = authenticated_client.get("/api/auth/search-users/?q=search")

        assert response.status_code == 200
        results = response.json()
        assert len(results) > 0
        assert any(user["email"] == "search@example.com" for user in results)

    def test_search_users_minimum_length(self, db_reset, authenticated_client):
        """Test that search requires minimum 2 characters."""
        response = authenticated_client.get("/api/auth/search-users/?q=a")

        assert response.status_code == 200
        assert response.json() == []

    def test_search_users_case_insensitive(self, db_reset, authenticated_client, db):
        """Test that search is case insensitive."""
        User.objects.create_user(email="TestUser@example.com", password="pass123456")

        response = authenticated_client.get("/api/auth/search-users/?q=test")

        assert response.status_code == 200
        results = response.json()
        assert any(user["email"].lower() == "testuser@example.com" for user in results)

    def test_search_users_limit(self, db_reset, authenticated_client, db):
        """Test that search results are limited to 10."""
        # Create 15 users
        for i in range(15):
            User.objects.create_user(
                email=f"testuser{i:02d}@example.com", password="pass123456"
            )

        response = authenticated_client.get("/api/auth/search-users/?q=testuser")

        assert response.status_code == 200
        results = response.json()
        assert len(results) <= 10


# ============================================================================
# Integration Tests
# ============================================================================


@pytest.mark.auth
@pytest.mark.integration
class TestAuthenticationFlow:
    """Integration tests for complete authentication flows."""

    def test_full_registration_and_login_flow(
        self, db_reset, http_client, test_user_data
    ):
        """Test complete flow: register, login, access profile."""
        # Register
        register_response = http_client.post("/api/auth/register/", json=test_user_data)
        assert register_response.status_code == 201

        # Login
        login_response = http_client.post(
            "/api/auth/login/",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"],
            },
        )
        assert login_response.status_code == 200
        tokens = login_response.json()

        # Access profile with token
        headers = {"Authorization": f"Bearer {tokens['access']}"}
        profile_response = http_client.get("/api/auth/profile/", headers=headers)
        assert profile_response.status_code == 200
        assert profile_response.json()["email"] == test_user_data["email"]

    def test_update_profile_flow(self, db_reset, http_client, test_user):
        """Test flow: login, then update profile."""
        # Login
        login_response = http_client.post(
            "/api/auth/login/",
            json={"email": "test@example.com", "password": "testpassword123"},
        )
        assert login_response.status_code == 200
        tokens = login_response.json()

        # Update profile
        headers = {"Authorization": f"Bearer {tokens['access']}"}
        new_email = "updated@example.com"
        update_response = http_client.put(
            "/api/auth/profile/", json={"email": new_email}, headers=headers
        )
        assert update_response.status_code == 200
        assert update_response.json()["email"] == new_email

        # Verify profile updated
        profile_response = http_client.get("/api/auth/profile/", headers=headers)
        assert profile_response.json()["email"] == new_email
