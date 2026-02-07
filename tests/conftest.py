"""
Pytest configuration file.

This file sets up Django and imports all fixtures from the fixtures module.
"""

import os

import django
import pytest

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()


# ============================================================================
# Configuration
# ============================================================================

DJANGO_HOST = os.getenv("DJANGO_TEST_HOST", "http://localhost:8000")
FRONTEND_HOST = os.getenv("FRONTEND_TEST_HOST", "http://localhost:3000")


# ============================================================================
# Import all fixtures
# ============================================================================

from .fixtures.browser import (  # noqa: E402, F401
    auth_storage_state,
    authenticated_page,
    browser,
    browser_context,
    unauthenticated_browser_context,
    unauthenticated_page,
)
from .fixtures.database import db_reset  # noqa: E402, F401
from .fixtures.http import authenticated_client, http_client  # noqa: E402, F401
from .fixtures.users import (  # noqa: E402, F401
    invalid_user_data,
    test_user,
    test_user_data,
)
from .fixtures.utils import (  # noqa: E402, F401
    assert_user_created,
    assert_user_not_created,
    test_dir,
)

# ============================================================================
# Pytest Hooks
# ============================================================================


def _check_server_available(host: str, port: int, timeout: int = 2) -> bool:
    """Check if a server is available by attempting an HTTP request."""
    import urllib.error
    import urllib.request

    url = f"http://{host}:{port}/"

    try:
        # Try HTTP request (more reliable for checking actual service)
        response = urllib.request.urlopen(url, timeout=timeout)
        response.close()
        return True
    except (
        urllib.error.URLError,
        urllib.error.HTTPError,
        TimeoutError,
        Exception,
    ):
        # Server not responding
        return False


def pytest_configure(config):
    """Configure pytest and set up markers for skipping e2e tests if needed."""
    # Check server availability
    frontend_parts = (
        FRONTEND_HOST.replace("http://", "").replace("https://", "").split(":")
    )
    frontend_port = int(frontend_parts[-1]) if len(frontend_parts) > 1 else 3000
    frontend_available = _check_server_available(
        frontend_parts[0], frontend_port, timeout=1
    )

    config._frontend_available = frontend_available


def pytest_collection_modifyitems(config, items):
    """Skip E2E tests if frontend server is not available."""
    if not hasattr(config, "_frontend_available") or config._frontend_available:
        return

    # Frontend not available, skip e2e tests
    skip_marker = pytest.mark.skip(
        reason="Frontend server not available. Run: make run-frontend"
    )

    e2e_tests = [item for item in items if "e2e" in item.nodeid]

    for item in e2e_tests:
        item.add_marker(skip_marker)
