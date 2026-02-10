"""HTTP client fixtures for API testing."""

import pytest
from django.test import Client


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
        elif method.lower() == "patch":
            response = self.client.patch(path, **request_kwargs)
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

    def patch(self, path: str, json=None, **kwargs):
        return self._make_request("PATCH", path, json_data=json, **kwargs)


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
def http_client() -> APITestClient:
    """API test client for making requests."""
    return APITestClient(Client())


@pytest.fixture
def authenticated_client(test_user) -> APITestClient:
    """API test client authenticated with test user."""
    from rest_framework_simplejwt.tokens import RefreshToken

    # Generate token for test user
    refresh = RefreshToken.for_user(test_user)

    # Create client with authentication headers
    client = Client()
    client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {str(refresh.access_token)}"

    return APITestClient(client)
