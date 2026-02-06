"""Browser fixtures for E2E testing."""

import pytest
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from playwright.async_api import Browser, BrowserContext

User = get_user_model()


@pytest.fixture
async def browser() -> Browser:
    """Provide a browser instance for E2E tests."""
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--use-fake-ui-for-media-stream",  # Use fake camera/mic
                "--use-fake-device-for-media-stream",  # Provide fake media devices
            ],
        )
        yield browser
        await browser.close()


@pytest.fixture
async def auth_storage_state(browser: Browser, db, test_dir, request) -> dict:
    """
    Create and save authenticated storage state for E2E tests.
    This creates a test user and sets auth tokens in localStorage.
    """
    # Create a temporary context to set up auth state
    context = await browser.new_context()
    page = await context.new_page()

    try:
        # Create test user in the database using a unique email
        # Use the test name to ensure uniqueness
        test_name = request.node.name if request else "default"
        unique_email = f"auth_user_{test_name}@example.com"

        # Clean up any existing user with this email
        await sync_to_async(User.objects.filter(email=unique_email).delete)()

        # Create the user
        await sync_to_async(User.objects.create_user)(
            email=unique_email, password="testpass123"
        )

        # Generate auth tokens directly using Django REST framework
        from rest_framework_simplejwt.tokens import RefreshToken

        user = await sync_to_async(User.objects.get)(email=unique_email)
        refresh = await sync_to_async(RefreshToken.for_user)(user)
        tokens = {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }

        # Navigate to any page first (needed for localStorage access)
        await page.goto("http://localhost:3000/login", wait_until="domcontentloaded")

        # Set tokens in localStorage
        await page.evaluate(
            f"localStorage.setItem('accessToken', '{tokens['access']}')"
        )
        await page.evaluate(
            f"localStorage.setItem('refreshToken', '{tokens['refresh']}')"
        )

        # Verify tokens were set
        stored_access = await page.evaluate("localStorage.getItem('accessToken')")
        assert (
            stored_access == tokens["access"]
        ), "Failed to set accessToken in localStorage"

        # Give storage time to persist
        await page.wait_for_timeout(200)

        # Capture and save the storage state
        state_file = test_dir / "auth_state.json"
        storage_state = await context.storage_state(path=str(state_file))

        return storage_state

    finally:
        await page.close()
        await context.close()


@pytest.fixture
async def browser_context(browser: Browser, auth_storage_state) -> BrowserContext:
    """Provide an authenticated browser context for E2E tests."""
    context = await browser.new_context(storage_state=auth_storage_state)
    yield context
    await context.close()


@pytest.fixture
async def page(browser_context: BrowserContext):
    """Provide a page instance for E2E tests with authenticated context."""
    page = await browser_context.new_page()
    yield page
    await page.close()


@pytest.fixture
async def unauthenticated_browser_context(browser: Browser) -> BrowserContext:
    """Provide an unauthenticated browser context for E2E tests."""
    context = await browser.new_context()
    yield context
    await context.close()


@pytest.fixture
async def unauthenticated_page(unauthenticated_browser_context: BrowserContext):
    """Provide a page instance for E2E tests without authentication."""
    page = await unauthenticated_browser_context.new_page()
    yield page
    await page.close()
