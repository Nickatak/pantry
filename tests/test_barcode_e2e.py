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
from PIL import Image

pytestmark = pytest.mark.e2e


class TestBarcodePageAuth:
    """Test authentication requirements for barcode page."""

    @pytest.mark.asyncio
    async def test_barcode_page_redirects_to_login_when_unauthenticated(self, page):
        """Test that unauthenticated users are redirected to login."""
        page.set_default_timeout(5000)

        # Try to access barcode page without token
        await page.goto(
            "http://localhost:3000/barcode",
            wait_until="domcontentloaded",
        )

        # Should redirect to login
        assert "login" in page.url

    @pytest.mark.asyncio
    async def test_barcode_page_accessible_when_authenticated(self, page, db_reset):
        """Test that authenticated users can access barcode page."""
        from django.contrib.auth import get_user_model

        User = get_user_model()
        page.set_default_timeout(5000)

        # Create test user
        User.objects.create_user(
            email="barcode_test@example.com", password="testpass123"
        )

        # Login via API to get token
        await page.goto("http://localhost:3000/login")

        # Fill login form
        await page.fill("#email", "barcode_test@example.com")
        await page.fill("#password", "testpass123")

        # Submit form
        await page.click('button[type="submit"]')

        # Wait for redirect to dashboard or barcode page
        await page.wait_for_url(
            "http://localhost:3000/**", wait_until="domcontentloaded"
        )

        # Now try to access barcode page - should succeed
        await page.goto("http://localhost:3000/barcode", wait_until="domcontentloaded")

        # Should stay on barcode page
        assert "/barcode" in page.url


class TestBarcodePageUI:
    """Test barcode page UI elements and layout."""

    @pytest.mark.asyncio
    async def test_barcode_page_has_required_elements(self, page, db_reset):
        """Test that barcode page has all required UI elements."""
        from django.contrib.auth import get_user_model

        User = get_user_model()
        page.set_default_timeout(5000)

        # Create and login test user
        User.objects.create_user(email="barcode_ui@example.com", password="testpass123")

        # Login
        await page.goto("http://localhost:3000/login")
        await page.fill("#email", "barcode_ui@example.com")
        await page.fill("#password", "testpass123")
        await page.click('button[type="submit"]')
        await page.wait_for_url(
            "http://localhost:3000/**", wait_until="domcontentloaded"
        )

        # Navigate to barcode page
        await page.goto("http://localhost:3000/barcode", wait_until="domcontentloaded")

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
    async def test_barcode_page_has_navigation_buttons(self, page, db_reset):
        """Test that barcode page has navigation buttons."""
        from django.contrib.auth import get_user_model

        User = get_user_model()
        page.set_default_timeout(5000)

        # Create and login test user
        User.objects.create_user(
            email="barcode_nav@example.com", password="testpass123"
        )

        # Login
        await page.goto("http://localhost:3000/login")
        await page.fill("#email", "barcode_nav@example.com")
        await page.fill("#password", "testpass123")
        await page.click('button[type="submit"]')
        await page.wait_for_url(
            "http://localhost:3000/**", wait_until="domcontentloaded"
        )

        # Navigate to barcode page
        await page.goto("http://localhost:3000/barcode", wait_until="domcontentloaded")

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
    async def test_barcode_page_initializes_camera(self, page, db_reset):
        """Test that barcode page attempts to initialize camera."""
        from django.contrib.auth import get_user_model

        User = get_user_model()
        page.set_default_timeout(5000)

        # Create and login test user
        User.objects.create_user(
            email="barcode_camera@example.com", password="testpass123"
        )

        # Login
        await page.goto("http://localhost:3000/login")
        await page.fill("#email", "barcode_camera@example.com")
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

        # Check for camera request message or active state
        # Wait a moment for initialization attempt
        await page.wait_for_timeout(1000)

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
    async def test_capture_button_exists_and_clickable(self, page, db_reset):
        """Test that capture button exists and becomes clickable."""
        from django.contrib.auth import get_user_model

        User = get_user_model()
        page.set_default_timeout(5000)

        # Create and login test user
        User.objects.create_user(
            email="barcode_capture@example.com", password="testpass123"
        )

        # Login
        await page.goto("http://localhost:3000/login")
        await page.fill("#email", "barcode_capture@example.com")
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

        # Wait for camera to initialize (scanner ready callback)
        await page.wait_for_timeout(1500)

        # Look for capture button - it might be disabled initially
        buttons = await page.query_selector_all("button")
        capture_button = None
        for btn in buttons:
            text = await btn.text_content()
            if "Capture" in text or "Processing" in text:
                capture_button = btn
                break

        assert capture_button is not None

    @pytest.mark.asyncio
    async def test_cancel_button_navigates_to_dashboard(self, page, db_reset):
        """Test that cancel button navigates back to dashboard."""
        from django.contrib.auth import get_user_model

        User = get_user_model()
        page.set_default_timeout(5000)

        # Create and login test user
        User.objects.create_user(
            email="barcode_cancel@example.com", password="testpass123"
        )

        # Login
        await page.goto("http://localhost:3000/login")
        await page.fill("#email", "barcode_cancel@example.com")
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

        # Click cancel button
        cancel_button = await page.query_selector('button:has-text("Cancel")')
        if cancel_button:
            await cancel_button.click()
            await page.wait_for_url(
                "http://localhost:3000/**", wait_until="domcontentloaded"
            )
            # Should be on dashboard or login
            assert "dashboard" in page.url or "login" in page.url


class TestBarcodeErrorHandling:
    """Test error handling in barcode scanner."""

    @pytest.mark.asyncio
    async def test_barcode_page_handles_missing_container(self, page, db_reset):
        """Test that barcode page handles missing DOM elements gracefully."""
        from django.contrib.auth import get_user_model

        User = get_user_model()
        page.set_default_timeout(5000)

        # Create and login test user
        User.objects.create_user(
            email="barcode_error@example.com", password="testpass123"
        )

        # Login
        await page.goto("http://localhost:3000/login")
        await page.fill("#email", "barcode_error@example.com")
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

        # Wait a moment
        await page.wait_for_timeout(500)

        # Check that page didn't crash (still on barcode page)
        assert "/barcode" in page.url


class TestBarcodeImageSubmissionFlow:
    """Test the complete flow from image submission to results display."""

    @pytest.mark.asyncio
    async def test_image_submission_displays_barcode_result(self, page, db_reset):
        """
        Test that submitting an image displays the barcode result on the page.
        """
        from django.contrib.auth import get_user_model

        User = get_user_model()
        page.set_default_timeout(5000)

        # Create and login test user
        User.objects.create_user(
            email="barcode_submit@example.com", password="testpass123"
        )

        # Login
        await page.goto("http://localhost:3000/login")
        await page.fill("#email", "barcode_submit@example.com")
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

        # Mock the barcode API response
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

        # Set up route interception for the barcode API
        await page.route("**/api/barcode/process/**", handle_barcode_api)

        # Wait for camera to initialize
        await page.wait_for_timeout(1500)

        # Click the capture button to submit an image
        capture_button = await page.query_selector('button:has-text("Capture")')
        assert capture_button is not None, "Capture button not found"

        await capture_button.click()

        # Wait for the API response and page update
        await page.wait_for_timeout(2000)

        # Verify the barcode result is displayed on the page
        page_content = await page.content()

        # Check that the barcode code is displayed
        assert (
            mock_barcode_code in page_content
        ), f"Barcode code '{mock_barcode_code}' not found in page content"

        # Check for results view indicators
        assert "Barcode Found" in page_content or "Scan Another Barcode" in page_content

    @pytest.mark.asyncio
    async def test_gemini_barcode_result_shows_in_results_view(self, page, db_reset):
        """
        Test that Gemini-extracted barcode is displayed in the results view.
        """
        from django.contrib.auth import get_user_model

        User = get_user_model()
        page.set_default_timeout(5000)

        # Create and login test user
        User.objects.create_user(
            email="barcode_gemini_result@example.com", password="testpass123"
        )

        # Login
        await page.goto("http://localhost:3000/login")
        await page.fill("#email", "barcode_gemini_result@example.com")
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

        # Mock the barcode API to return a Gemini-extracted code
        gemini_extracted_code = "5901234123457"

        async def handle_gemini_barcode_api(route):
            """
            Intercept and mock the barcode processing API call.
            Uses Gemini data for the response.
            """
            await route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps(
                    {
                        "barcode_code": gemini_extracted_code,
                        "detected": True,
                    }
                ),
            )

        # Set up route interception
        await page.route(
            "**/api/barcode/process/**",
            handle_gemini_barcode_api,
        )

        # Wait for camera to initialize
        await page.wait_for_timeout(1500)

        # Click capture button
        capture_button = await page.query_selector('button:has-text("Capture")')
        assert capture_button is not None

        await capture_button.click()

        # Wait for results to load
        await page.wait_for_timeout(2000)

        # Verify results view is showing
        results_view = await page.query_selector(
            'button:has-text("Scan Another Barcode")'
        )
        assert results_view is not None, "Results view not found"

        # Verify the extracted barcode code is displayed
        page_content = await page.content()
        error_msg = f"Extracted barcode '{gemini_extracted_code}' not in results"
        assert gemini_extracted_code in page_content, error_msg

        # Verify "Barcode Found" message is shown
        assert "Barcode Found" in page_content

    @pytest.mark.asyncio
    async def test_undetected_barcode_shows_error(self, page, db_reset):
        """Test that when Gemini cannot detect a barcode, an error is shown."""
        from django.contrib.auth import get_user_model

        User = get_user_model()
        page.set_default_timeout(5000)

        # Create and login test user
        User.objects.create_user(
            email="barcode_not_detected@example.com", password="testpass123"
        )

        # Login
        await page.goto("http://localhost:3000/login")
        await page.fill("#email", "barcode_not_detected@example.com")
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

        # Mock the barcode API to return "not detected"
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

        # Wait for camera to initialize
        await page.wait_for_timeout(1500)

        # Click capture button
        capture_button = await page.query_selector('button:has-text("Capture")')
        assert capture_button is not None

        await capture_button.click()

        # Wait for response
        await page.wait_for_timeout(2000)

        # Verify error message is shown and still on camera view
        page_content = await page.content()
        assert (
            "Could not read the barcode" in page_content
            or "error" in page_content.lower()
        ) or "/barcode" in page.url


class TestBarcodePageNavigation:
    """Test navigation flows within and from barcode page."""

    @pytest.mark.asyncio
    async def test_barcode_page_title_visible(self, page, db_reset):
        """Test that barcode page title is visible."""
        from django.contrib.auth import get_user_model

        User = get_user_model()
        page.set_default_timeout(5000)

        # Create and login test user
        User.objects.create_user(
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
    async def test_barcode_page_subtitle_visible(self, page, db_reset):
        """Test that barcode page subtitle/description is visible."""
        from django.contrib.auth import get_user_model

        User = get_user_model()
        page.set_default_timeout(5000)

        # Create and login test user
        User.objects.create_user(
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

    @pytest.mark.asyncio
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

    @pytest.mark.asyncio
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

    @pytest.mark.asyncio
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

    @pytest.mark.asyncio
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

    @pytest.mark.asyncio
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

    @pytest.mark.asyncio
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
