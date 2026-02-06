"""Database fixtures."""

import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def db_reset(db):
    """Ensure a clean database for each test."""
    User.objects.all().delete()
    yield db
    User.objects.all().delete()
