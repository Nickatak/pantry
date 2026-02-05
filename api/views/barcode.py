import base64
import io

import google.generativeai as genai
from django.conf import settings
from PIL import Image
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


class BarcodeViewSet(viewsets.ViewSet):
    """
    ViewSet for barcode processing operations.

    Provides the following endpoints:
    - POST /api/barcode/process/ - Parse barcode image and extract numerical code
    """

    permission_classes = [IsAuthenticated]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize Gemini API
        api_key = getattr(settings, "GEMINI_API_KEY", None)
        if api_key:
            genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash")

    @action(detail=False, methods=["post"])
    def process(self, request):
        """
        Process a barcode image and extract the numerical code.

        POST /api/barcode/process/
        - image: base64 encoded image data

        Returns: { "barcode_code": "extracted_code" }
        """
        try:
            image_data = request.data.get("image")
            if not image_data:
                return Response(
                    {"error": "No image provided"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Decode base64 image
            try:
                image_bytes = base64.b64decode(image_data)
                image = Image.open(io.BytesIO(image_bytes))
            except Exception as e:
                return Response(
                    {"error": f"Invalid image format: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Send to Gemini for barcode extraction
            prompt = """Please analyze this barcode image and extract the numerical code shown in the barcode.
            Return ONLY the numerical code of the barcode, nothing else.
            If there is no barcode or the code cannot be extracted, respond with "UNABLE_TO_READ"."""

            response = self.model.generate_content([prompt, image])
            barcode_code = response.text.strip()

            # Determine if barcode was detected
            detected = barcode_code != "UNABLE_TO_READ"

            return Response(
                {
                    "barcode_code": barcode_code,
                    "detected": detected,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": f"Failed to process barcode: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
