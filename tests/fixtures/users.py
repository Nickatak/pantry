"""User fixtures."""

import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def test_user(db_reset):
    """Create a test user."""
    return User.objects.create_user(
        email="test@example.com", password="testpassword123"
    )


@pytest.fixture
def test_user_data():
    """Test user credentials."""
    return {
        "email": "newuser@example.com",
        "password": "SecurePass123",
        "password_confirm": "SecurePass123",
    }


@pytest.fixture
def invalid_user_data():
    """Invalid test user data."""
    return {
        "email": "invalid@example.com",
        "password": "short",
        "password_confirm": "different",
    }
