"""
Pytest configuration and shared fixtures for authentication tests.
"""

import os

import django
import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from playwright.async_api import Browser, BrowserContext, async_playwright

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

User = get_user_model()


# ============================================================================
# Configuration
# ============================================================================

DJANGO_HOST = os.getenv("DJANGO_TEST_HOST", "http://localhost:8000")
FRONTEND_HOST = os.getenv("FRONTEND_TEST_HOST", "http://localhost:3000")


# ============================================================================
# Database Fixtures
# ============================================================================


@pytest.fixture
def db_reset(db):
    """Ensure a clean database for each test."""
    User.objects.all().delete()
    yield db
    User.objects.all().delete()


# ============================================================================
# HTTP Client Fixtures
# ============================================================================


class APITestClient:
    """Wrapper around Django test client for API testing."""

    def __init__(self, client: Client):
        self.client = client
        self.headers = {}

    def _make_request(self, method: str, path: str, json_data=None, **kwargs):
        """Make a request and return a response-like object."""
        import json as json_module

        headers = {
            "Content-Type": "application/json",
            **self.headers,
            **kwargs.get("headers", {}),
        }

        # Prepare request kwargs
        request_kwargs = {
            k: v for k, v in kwargs.items() if k not in ["headers", "json"]
        }
        request_kwargs["headers"] = headers

        # Serialize JSON data if provided
        if json_data is not None:
            request_kwargs["data"] = json_module.dumps(json_data)
            request_kwargs["content_type"] = "application/json"

        if method.lower() == "get":
            response = self.client.get(path, **request_kwargs)
        elif method.lower() == "post":
            response = self.client.post(path, **request_kwargs)
        elif method.lower() == "put":
            response = self.client.put(path, **request_kwargs)
        else:
            raise ValueError(f"Unsupported method: {method}")

        # Wrap response to add .json() method
        return ResponseWrapper(response)

    def get(self, path: str, **kwargs):
        return self._make_request("GET", path, **kwargs)

    def post(self, path: str, json=None, **kwargs):
        return self._make_request("POST", path, json_data=json, **kwargs)

    def put(self, path: str, json=None, **kwargs):
        return self._make_request("PUT", path, json_data=json, **kwargs)


class ResponseWrapper:
    """Wraps Django test response to provide httpx-like interface."""

    def __init__(self, response):
        self.response = response
        self.status_code = response.status_code
        self._json = None

    def json(self):
        """Parse response as JSON."""
        if self._json is None:
            try:
                import json as json_module

                self._json = json_module.loads(self.response.content.decode())
            except Exception:
                self._json = {}
        return self._json

    def __getattr__(self, name):
        """Delegate to wrapped response."""
        return getattr(self.response, name)


@pytest.fixture
def http_client(db) -> APITestClient:
    """API test client for making requests."""
    return APITestClient(Client())


# ============================================================================
# User Fixtures
# ============================================================================


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


# ============================================================================
# Browser Fixtures (for E2E tests)
# ============================================================================


@pytest.fixture
async def browser() -> Browser:
    """Provide a browser instance for E2E tests."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        yield browser
        await browser.close()


# ============================================================================
# E2E Test Collection Hook
# ============================================================================


def pytest_collection_modifyitems(config, items):
    """Skip E2E tests if servers are not available."""
    import socket

    # Check if we're collecting E2E tests
    e2e_tests = [item for item in items if "e2e" in item.keywords]

    if not e2e_tests:
        return

    # Try to connect to servers using socket (more reliable)
    def server_is_available(host: str, port: int) -> bool:
        """Check if a server is available by attempting a socket connection."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except Exception:
            return False

    # Extract host and port from URLs
    django_host = DJANGO_HOST.replace("http://", "").replace("https://", "")
    frontend_host = FRONTEND_HOST.replace("http://", "").replace("https://", "")

    # Check servers
    django_available = server_is_available(
        django_host.split(":")[0], int(django_host.split(":")[-1])
    )
    frontend_available = server_is_available(
        frontend_host.split(":")[0], int(frontend_host.split(":")[-1])
    )

    servers_available = django_available and frontend_available

    # Skip E2E tests if servers not available
    if not servers_available:
        skip_reason = (
            "E2E servers not available (run: make run-backend && make run-frontend)"
        )
        if not django_available:
            skip_reason += f"\n  - Django not running on {DJANGO_HOST}"
        if not frontend_available:
            skip_reason += f"\n  - Frontend not running on {FRONTEND_HOST}"

        skip_marker = pytest.mark.skip(reason=skip_reason)
        for item in e2e_tests:
            item.add_marker(skip_marker)


@pytest.fixture
async def browser_context(browser: Browser) -> BrowserContext:
    """Provide a browser context for E2E tests."""
    context = await browser.new_context()
    yield context
    await context.close()


@pytest.fixture
async def page(browser_context: BrowserContext):
    """Provide a page instance for E2E tests."""
    page = await browser_context.new_page()
    yield page
    await page.close()


# ============================================================================
# Authentication Fixtures
# ============================================================================


@pytest.fixture
def authenticated_client(http_client, test_user) -> APITestClient:
    """API test client with authentication headers."""
    from rest_framework_simplejwt.tokens import RefreshToken

    refresh = RefreshToken.for_user(test_user)
    client = http_client
    client.headers["Authorization"] = f"Bearer {str(refresh.access_token)}"
    return client


@pytest.fixture
def login_response(http_client, test_user):
    """Get login tokens for test user."""
    response = http_client.post(
        "/api/auth/login/",
        json={"email": "test@example.com", "password": "testpassword123"},
    )
    return response.json() if response.status_code == 200 else None


# ============================================================================
# Test Utilities
# ============================================================================


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
