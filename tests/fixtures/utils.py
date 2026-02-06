"""Utility fixtures."""

import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def test_dir(tmp_path):
    """Provide a temporary directory for test artifacts."""
    return tmp_path


@pytest.fixture
def assert_user_created():
    """Helper to assert a user was created."""

    def _assert(email: str) -> User:
        user = User.objects.get(email=email)
        assert user is not None
        return user

    return _assert


@pytest.fixture
def assert_user_not_created():
    """Helper to assert a user was not created."""

    def _assert(email: str):
        assert not User.objects.filter(email=email).exists()

    return _assert
