"""
End-to-end tests for the barcode scanner route.

These tests verify that:
- Barcode page requires authentication
- Camera initialization works correctly
- Barcode capture flow functions properly
- Results display works
- Retry/scan another barcode flow works
- Gemini API integration works correctly

Note: These tests require both Django (port 8000) and Next.js (port 3000)
servers to be running. They will be skipped if servers are not accessible.
Run with: make run-backend && make run-frontend (in separate terminals)
"""

import base64
import io
import json
from unittest.mock import MagicMock, patch

import pytest
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from PIL import Image

pytestmark = pytest.mark.e2e

User = get_user_model()


class TestBarcodePageAuth:
    """Test authentication requirements for barcode page."""

    @pytest.mark.asyncio
    async def test_barcode_page_redirects_to_login_when_unauthenticated(
        self, unauthenticated_page
    ):
        """Test that unauthenticated users are redirected to login."""
        # Try to access barcode page without token
        await unauthenticated_page.goto(
            "http://localhost:3000/barcode",
            wait_until="networkidle",
        )

        # Wait for redirect to happen (useEffect runs after domcontentloaded)
        try:
            await unauthenticated_page.wait_for_url(
                "http://localhost:3000/login*", timeout=3000
            )
        except Exception:
            # If redirect doesn't happen, check current URL
            pass

        # Should redirect to login
        assert "login" in unauthenticated_page.url

    @pytest.mark.asyncio
    async def test_barcode_page_accessible_when_authenticated(self, page, db):
        """Test that authenticated users can access barcode page."""
        # Navigate directly to barcode page - should succeed with authenticated context
        await page.goto("http://localhost:3000/barcode", wait_until="networkidle")

        # Should stay on barcode page (not redirected to login)
        assert "/barcode" in page.url


class TestBarcodePageUI:
    """Test barcode page UI elements and layout."""

    @pytest.mark.asyncio
    async def test_barcode_page_has_required_elements(self, page, db):
        """Test that barcode page has all required UI elements."""
        # Navigate to barcode page with authenticated context
        await page.goto("http://localhost:3000/barcode", wait_until="networkidle")

        # Check for page title
        title = await page.title()
        assert title is not None

        # Check for header
        header = await page.query_selector("h1")
        assert header is not None
        header_text = await header.text_content()
        assert "Barcode Scanner" in header_text

        # Check for description
        description = await page.query_selector("p")
        assert description is not None

        # Check for camera/scanner container or video element
        # Either html5-qrcode scanner container or BarcodeDetector video
        scanner_container = await page.query_selector("#barcode-scanner-container")
        video = await page.query_selector("video")
        assert scanner_container is not None or video is not None

    @pytest.mark.asyncio
    async def test_barcode_page_has_navigation_buttons(self, page, db):
        """Test that barcode page has navigation buttons."""
        # Navigate to barcode page with authenticated context
        await page.goto("http://localhost:3000/barcode", wait_until="networkidle")

        # Check for buttons
        buttons = await page.query_selector_all("button")
        # At least Capture and Cancel buttons
        assert len(buttons) >= 2

        # Check button text contains expected actions
        button_texts = []
        for btn in buttons:
            text = await btn.text_content()
            button_texts.append(text)

        assert any("Cancel" in text for text in button_texts)
        assert any("Capture" in text or "Processing" in text for text in button_texts)


class TestBarcodeInitialization:
    """Test barcode scanner initialization."""

    @pytest.mark.asyncio
    async def test_barcode_page_initializes_camera(self, page, db):
        """Test that barcode page attempts to initialize camera."""
        # Navigate to barcode page with authenticated context
        await page.goto("http://localhost:3000/barcode", wait_until="networkidle")

        # Check if page mentions camera access or detection method
        page_content = await page.content()
        assert (
            "camera" in page_content.lower()
            or "detection" in page_content.lower()
            or "capture" in page_content.lower()
        )


class TestBarcodeCapture:
    """Test barcode capture functionality."""

    @pytest.mark.asyncio
    async def test_capture_button_exists_and_clickable(self, page, db):
        """Test that capture button exists and becomes clickable."""
        # Navigate to barcode page with authenticated context
        await page.goto("http://localhost:3000/barcode", wait_until="networkidle")

        # Wait for camera to initialize and buttons to appear
        try:
            await page.wait_for_selector("button", timeout=2000)
        except Exception:
            pass

        # Look for capture button - it might be disabled initially
        buttons = await page.query_selector_all("button")
        capture_button = None
        for btn in buttons:
            text = await btn.text_content()
            if text and ("Capture" in text or "Processing" in text):
                capture_button = btn
                break

        assert capture_button is not None

    @pytest.mark.asyncio
    async def test_cancel_button_navigates_to_dashboard(self, page, db):
        """Test that cancel button navigates back to dashboard."""
        # Create and login test user
        await sync_to_async(User.objects.create_user)(
            email="barcode_cancel@example.com", password="testpass123"
        )

        # Login
        await page.goto("http://localhost:3000/login")
        await page.fill("#email", "barcode_cancel@example.com")
        await page.fill("#password", "testpass123")
        await page.click('button[type="submit"]')
        try:
            await page.wait_for_url("http://localhost:3000/dashboard*", timeout=3000)
        except Exception:
            pass

        # Navigate to barcode page
        await page.goto(
            "http://localhost:3000/barcode",
            wait_until="networkidle",
        )

        # Wait for buttons to appear
        try:
            await page.wait_for_selector("button:has-text('Cancel')", timeout=2000)
        except Exception:
            # If selector fails, try finding by text content
            pass

        # Click cancel button
        buttons = await page.query_selector_all("button")
        cancel_button = None
        for btn in buttons:
            text = await btn.text_content()
            if text and "Cancel" in text:
                cancel_button = btn
                break

        if cancel_button:
            await cancel_button.click()
            try:
                await page.wait_for_url(
                    "http://localhost:3000/dashboard*", timeout=2000
                )
            except Exception:
                pass
            # Should be on dashboard or login
            assert "dashboard" in page.url or "login" in page.url


class TestBarcodeErrorHandling:
    """Test error handling in barcode scanner."""

    @pytest.mark.asyncio
    async def test_barcode_page_handles_missing_container(self, page, db):
        """Test that barcode page handles missing DOM elements gracefully."""
        # Navigate to barcode page with authenticated context
        await page.goto("http://localhost:3000/barcode", wait_until="networkidle")

        # Check that page didn't crash (still on barcode page)
        assert "/barcode" in page.url


class TestBarcodeImageSubmissionFlow:
    """Test the complete flow from image submission to results display."""

    @pytest.mark.asyncio
    async def test_image_submission_displays_barcode_result(
        self, page, authenticated_client
    ):
        """Test that submitting an image displays the barcode result on the page."""
        # Step 1: Grant camera permission to the page
        await page.context.grant_permissions(["camera"])

        # Step 2: Navigate to barcode page with authenticated context
        await page.goto("http://localhost:3000/barcode", wait_until="networkidle")

        # Step 3: Mock the barcode API response
        mock_barcode_code = "012345678901"

        async def handle_barcode_api(route):
            """Intercept and mock the barcode processing API call."""
            await route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps(
                    {
                        "barcode_code": mock_barcode_code,
                        "detected": True,
                    }
                ),
            )

        await page.route("**/api/barcode/process/**", handle_barcode_api)

        # Step 4: Wait for buttons to appear
        try:
            await page.wait_for_selector("button", timeout=3000)
        except Exception:
            pass

        buttons = await page.query_selector_all("button")
        request_camera_button = None
        capture_button = None

        for btn in buttons:
            text = await btn.text_content()
            if text and "Request Camera Permissions" in text:
                request_camera_button = btn
            if text and "Capture" in text:
                capture_button = btn

        # Step 5: Click the "Request Camera Permissions" button to initialize camera
        if request_camera_button:
            await request_camera_button.click()
            # Wait for camera to initialize
            await page.wait_for_timeout(2000)

        # Step 6: Click the capture button to trigger the API call
        if capture_button:
            await capture_button.click()
            # Wait for the API response to be processed by the frontend
            await page.wait_for_timeout(2000)

        # Step 7: Verify the barcode result is displayed
        page_content = await page.content()
        assert (
            mock_barcode_code in page_content
        ), f"Barcode code '{mock_barcode_code}' not found in page content"

    @pytest.mark.asyncio
    async def test_undetected_barcode_shows_error(self, page, authenticated_client):
        """Test that when Gemini cannot detect a barcode, an error is shown."""
        # Step 1: Grant camera permission to the page
        await page.context.grant_permissions(["camera"])

        # Step 2: Navigate to barcode page with authenticated context
        await page.goto("http://localhost:3000/barcode", wait_until="networkidle")

        # Step 3: Mock the barcode API to return "not detected"
        async def handle_undetected_barcode(route):
            """Mock barcode processing that cannot detect a barcode."""
            await route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps(
                    {
                        "barcode_code": "UNABLE_TO_READ",
                        "detected": False,
                    }
                ),
            )

        # Set up route interception
        await page.route(
            "**/api/barcode/process/**",
            handle_undetected_barcode,
        )

        # Step 4: Wait for buttons to appear
        try:
            await page.wait_for_selector("button", timeout=3000)
        except Exception:
            pass

        # Step 5: Find the camera permissions and capture buttons
        buttons = await page.query_selector_all("button")
        request_camera_button = None
        capture_button = None

        for btn in buttons:
            text = await btn.text_content()
            if text and "Request Camera Permissions" in text:
                request_camera_button = btn
            if text and "Capture" in text:
                capture_button = btn

        # Step 6: Click the "Request Camera Permissions" button to initialize camera
        if request_camera_button:
            await request_camera_button.click()
            # Wait for camera to initialize
            await page.wait_for_timeout(2000)

        # Step 7: Click the capture button to trigger the API call
        if capture_button:
            await capture_button.click()
            # Wait for response
            await page.wait_for_timeout(2000)

        # Step 8: Verify error message is shown
        page_content = await page.content()
        assert (
            "Could not read the barcode" in page_content
            or "error" in page_content.lower()
            or "UNABLE_TO_READ" in page_content
        ), "Error message not found when barcode detection fails"


class TestBarcodePageNavigation:
    """Test navigation flows within and from barcode page."""

    @pytest.mark.asyncio
    async def test_barcode_page_title_visible(self, page, db):
        """Test that barcode page title is visible."""
        # Create and login test user
        await sync_to_async(User.objects.create_user)(
            email="barcode_title@example.com", password="testpass123"
        )

        # Login
        await page.goto("http://localhost:3000/login")
        await page.fill("#email", "barcode_title@example.com")
        await page.fill("#password", "testpass123")
        await page.click('button[type="submit"]')
        await page.wait_for_url(
            "http://localhost:3000/**", wait_until="domcontentloaded"
        )

        # Navigate to barcode page
        await page.goto(
            "http://localhost:3000/barcode",
            wait_until="domcontentloaded",
        )

        # Check for page title
        h1 = await page.query_selector("h1")
        assert h1 is not None

        # Check title content
        title_text = await h1.text_content()
        assert "Barcode Scanner" in title_text

    @pytest.mark.asyncio
    async def test_barcode_page_subtitle_visible(self, page, db):
        """Test that barcode page subtitle/description is visible."""
        # Create and login test user
        await sync_to_async(User.objects.create_user)(
            email="barcode_subtitle@example.com", password="testpass123"
        )

        # Login
        await page.goto("http://localhost:3000/login")
        await page.fill("#email", "barcode_subtitle@example.com")
        await page.fill("#password", "testpass123")
        await page.click('button[type="submit"]')
        await page.wait_for_url(
            "http://localhost:3000/**", wait_until="domcontentloaded"
        )

        # Navigate to barcode page
        await page.goto(
            "http://localhost:3000/barcode",
            wait_until="domcontentloaded",
        )

        # Check for subtitle/description
        description = await page.query_selector("p")
        assert description is not None

        desc_text = await description.text_content()
        assert "camera" in desc_text.lower() or "barcode" in desc_text.lower()


class TestBarcodeGeminiIntegration:
    """Test Gemini API integration for barcode processing."""

    def _create_test_image(self) -> str:
        """Create a simple test image and return as base64."""
        # Create a simple test image
        img = Image.new("RGB", (100, 100), color="red")
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="JPEG")
        img_bytes.seek(0)
        # Return base64 encoded image
        return base64.b64encode(img_bytes.getvalue()).decode("utf-8")

    def test_barcode_processing_calls_gemini_api(self, authenticated_client, db_reset):
        """Test that barcode processing makes a call to Gemini API."""
        # Create test image
        test_image_base64 = self._create_test_image()

        # Mock the Gemini API response
        mock_response = MagicMock()
        mock_response.text = "123456789"  # Mock barcode code

        with patch(
            "google.generativeai.GenerativeModel.generate_content",
            return_value=mock_response,
        ) as mock_generate:
            # Send barcode image to API
            response = authenticated_client.post(
                "/api/barcode/process/",
                json={"image": test_image_base64},
            )

            # Verify successful response
            assert response.status_code == 200
            result = response.json()
            assert result["detected"] is True
            assert result["barcode_code"] == "123456789"

            # Verify Gemini was called
            assert mock_generate.called
            # Verify generate_content was called once
            assert mock_generate.call_count == 1

    def test_barcode_processing_gemini_receives_correct_prompt(
        self, authenticated_client, db_reset
    ):
        """
        Test that Gemini API receives the correct barcode extraction prompt.
        """
        # Create test image
        test_image_base64 = self._create_test_image()

        # Mock the Gemini API response
        mock_response = MagicMock()
        mock_response.text = "987654321"

        with patch(
            "google.generativeai.GenerativeModel.generate_content",
            return_value=mock_response,
        ) as mock_generate:
            # Send barcode image
            authenticated_client.post(
                "/api/barcode/process/",
                json={"image": test_image_base64},
            )

            # Get the call arguments
            call_args = mock_generate.call_args
            assert call_args is not None

            # Verify the prompt is included in the call
            prompt_and_image = call_args[0][0]
            assert isinstance(prompt_and_image, list)
            assert len(prompt_and_image) == 2

            # First element should be the prompt
            prompt = prompt_and_image[0]
            assert "barcode" in prompt.lower()
            assert "extract" in prompt.lower() or "analyze" in prompt.lower()

    def test_barcode_processing_handles_gemini_unable_to_read(
        self, authenticated_client, db_reset
    ):
        """
        Test barcode processing when Gemini cannot read barcode.
        """
        # Create test image
        test_image_base64 = self._create_test_image()

        # Mock Gemini response indicating unable to read
        mock_response = MagicMock()
        mock_response.text = "UNABLE_TO_READ"

        with patch(
            "google.generativeai.GenerativeModel.generate_content",
            return_value=mock_response,
        ):
            # Send barcode image
            response = authenticated_client.post(
                "/api/barcode/process/",
                json={"image": test_image_base64},
            )

            # Verify response indicates barcode not detected
            assert response.status_code == 200
            result = response.json()
            assert result["detected"] is False
            assert result["barcode_code"] == "UNABLE_TO_READ"

    def test_barcode_processing_with_invalid_image_returns_error(
        self, authenticated_client, db_reset
    ):
        """Test that invalid image data is rejected before calling Gemini."""
        # Send invalid base64 image data
        response = authenticated_client.post(
            "/api/barcode/process/",
            json={"image": "not_valid_base64!!!"},
        )

        # Should return error
        assert response.status_code == 400
        result = response.json()
        assert "error" in result

    def test_barcode_processing_requires_authentication(self, http_client, db_reset):
        """Test that barcode processing endpoint requires authentication."""
        # Create test image
        test_image_base64 = self._create_test_image()

        # Try to access without authentication token
        response = http_client.post(
            "/api/barcode/process/",
            json={"image": test_image_base64},
        )

        # Should return 401 Unauthorized
        assert response.status_code == 401

    def test_barcode_processing_with_multiple_calls_to_gemini(
        self, authenticated_client, db_reset
    ):
        """
        Test that multiple barcode submissions each call Gemini independently.
        """
        # Create two test images
        test_image_1 = self._create_test_image()
        test_image_2 = self._create_test_image()

        # Mock responses for each call
        def mock_generate_side_effect(args):
            response = MagicMock()
            if args[0] == 1:
                response.text = "111111111"
            else:
                response.text = "222222222"
            return response

        mock_response_1 = MagicMock()
        mock_response_1.text = "111111111"

        mock_response_2 = MagicMock()
        mock_response_2.text = "222222222"

        with patch(
            "google.generativeai.GenerativeModel.generate_content",
            side_effect=[mock_response_1, mock_response_2],
        ) as mock_generate:
            # First request
            response_1 = authenticated_client.post(
                "/api/barcode/process/",
                json={"image": test_image_1},
            )

            assert response_1.status_code == 200
            assert response_1.json()["barcode_code"] == "111111111"

            # Second request
            response_2 = authenticated_client.post(
                "/api/barcode/process/",
                json={"image": test_image_2},
            )

            assert response_2.status_code == 200
            assert response_2.json()["barcode_code"] == "222222222"

            # Verify Gemini was called twice
            assert mock_generate.call_count == 2
